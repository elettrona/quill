"""Pronunciation dictionaries for all QUILL speech (batch + live Read Aloud).

wx-free, strict-typed. A *dictionary* is a named, ordered set of *entries*, each
mapping a term to how it should be spoken. Scope is two-dimensional
(``batch-document-to-speech-plan.md`` §4.7.1):

* **location** — ``global`` (under ``app_data_dir()/speech/pronunciation/``,
  available everywhere) or ``project`` (under ``<project>/.quill/pronunciation/``,
  active only while that folder of files is open and travelling with it);
* **engine** — ``None`` (all engines, applied as pre-synthesis text substitution)
  or one synthesizer id (applied only when that engine is active).

:func:`apply_pronunciations` is the single substitution stage both the batch and
live paths call, so a fix made once is heard everywhere. Conflict precedence,
most specific first: project+engine > project+all > global+engine > global+all.

Respelling substitution is fully implemented here. Phoneme/SSML entries degrade
to their ``plain_fallback`` for now (native SSML rendering is the plan's Phase 6);
they never emit raw markup into spoken text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from quill.core.paths import app_data_dir
from quill.core.storage import read_json, write_json_atomic

ENGINES: frozenset[str] = frozenset({"sapi5", "dectalk", "piper", "kokoro", "espeak"})
_MODES: frozenset[str] = frozenset({"respelling", "phoneme", "ssml"})
_SCOPES: frozenset[str] = frozenset({"global", "project"})


@dataclass(slots=True)
class PronunciationEntry:
    """One term → spoken-form mapping (§4.7.2)."""

    term: str = ""
    replacement: str = ""
    mode: str = "respelling"  # respelling | phoneme | ssml
    plain_fallback: str = ""  # used when the engine cannot honour mode (required for ssml/phoneme)
    whole_word: bool = True
    case_sensitive: bool = False
    regex: bool = False
    enabled: bool = True
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "term": self.term,
            "replacement": self.replacement,
            "mode": self.mode if self.mode in _MODES else "respelling",
            "plain_fallback": self.plain_fallback,
            "whole_word": self.whole_word,
            "case_sensitive": self.case_sensitive,
            "regex": self.regex,
            "enabled": self.enabled,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: Any) -> PronunciationEntry:
        if not isinstance(data, dict):
            return cls()
        mode = str(data.get("mode", "respelling"))
        return cls(
            term=str(data.get("term", "")),
            replacement=str(data.get("replacement", "")),
            mode=mode if mode in _MODES else "respelling",
            plain_fallback=str(data.get("plain_fallback", "")),
            whole_word=bool(data.get("whole_word", True)),
            case_sensitive=bool(data.get("case_sensitive", False)),
            regex=bool(data.get("regex", False)),
            enabled=bool(data.get("enabled", True)),
            note=str(data.get("note", "")),
        )


@dataclass(slots=True)
class PronunciationDictionary:
    """A named, scoped collection of entries (§4.7.1)."""

    id: str
    name: str = ""
    scope: str = "global"  # global | project (the storage location)
    engine: str | None = None  # None = all engines; else a synthesizer id
    enabled: bool = True
    entries: list[PronunciationEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "scope": self.scope if self.scope in _SCOPES else "global",
            "engine": self.engine if self.engine in ENGINES else None,
            "enabled": self.enabled,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: Any) -> PronunciationDictionary:
        if not isinstance(data, dict):
            return cls(id="")
        scope = str(data.get("scope", "global"))
        engine = data.get("engine")
        raw_entries = data.get("entries")
        entries = (
            [PronunciationEntry.from_dict(item) for item in raw_entries]
            if isinstance(raw_entries, list)
            else []
        )
        return cls(
            id=str(data.get("id", "")),
            name=str(data.get("name", "")),
            scope=scope if scope in _SCOPES else "global",
            engine=engine if engine in ENGINES else None,
            enabled=bool(data.get("enabled", True)),
            entries=entries,
        )

    def specificity(self) -> int:
        """Higher = more specific (project+engine 3 … global+all 0)."""
        return (2 if self.scope == "project" else 0) + (1 if self.engine is not None else 0)


@dataclass(slots=True)
class PronunciationResult:
    """Output of :func:`apply_pronunciations`."""

    text: str
    is_ssml: bool = False
    applied: dict[str, int] = field(default_factory=dict)  # entry term → times fired

    @property
    def total_applied(self) -> int:
        return sum(self.applied.values())


# ----------------------------------------------------------------------------
# Storage
# ----------------------------------------------------------------------------


def global_dir() -> Path:
    return app_data_dir() / "speech" / "pronunciation"


def project_dir_for(project_dir: Path) -> Path:
    return Path(project_dir) / ".quill" / "pronunciation"


def _load_from(folder: Path, scope: str) -> list[PronunciationDictionary]:
    out: list[PronunciationDictionary] = []
    try:
        paths = sorted(folder.glob("*.json"))
    except OSError:
        return out
    for path in paths:
        try:
            data = read_json(path, None)
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        dictionary = PronunciationDictionary.from_dict(data)
        dictionary.scope = scope  # the location it was found in is authoritative
        if not dictionary.id:
            dictionary.id = path.stem
        out.append(dictionary)
    return out


def load_dictionaries(project_dir: Path | None = None) -> list[PronunciationDictionary]:
    """All stored dictionaries: globals always, plus the project's when given."""
    dictionaries = _load_from(global_dir(), "global")
    if project_dir is not None:
        dictionaries.extend(_load_from(project_dir_for(project_dir), "project"))
    return dictionaries


def save_dictionary(dictionary: PronunciationDictionary, project_dir: Path | None = None) -> Path:
    """Write ``dictionary`` to its scope's location and return the path."""
    if dictionary.scope == "project":
        if project_dir is None:
            raise ValueError("a project-scoped dictionary needs a project_dir to save")
        folder = project_dir_for(project_dir)
    else:
        folder = global_dir()
    path = folder / f"{dictionary.id}.json"
    write_json_atomic(path, dictionary.to_dict())
    return path


def delete_dictionary(dictionary: PronunciationDictionary, project_dir: Path | None = None) -> None:
    folder = (
        project_dir_for(project_dir)
        if dictionary.scope == "project" and project_dir is not None
        else global_dir()
    )
    (folder / f"{dictionary.id}.json").unlink(missing_ok=True)


def active_dictionaries(
    engine: str,
    *,
    project_dir: Path | None = None,
    enabled_ids: set[str] | None = None,
) -> list[PronunciationDictionary]:
    """Enabled, in-scope dictionaries for ``(engine, project)``, most specific first.

    A dictionary participates when its engine is ``None`` or matches ``engine``,
    and when it is enabled. ``enabled_ids`` (the per-user selection from settings)
    is authoritative when given; otherwise the dictionary's own ``enabled`` flag
    is used.
    """
    out: list[PronunciationDictionary] = []
    for dictionary in load_dictionaries(project_dir):
        if dictionary.engine is not None and dictionary.engine != engine:
            continue
        is_on = (dictionary.id in enabled_ids) if enabled_ids is not None else dictionary.enabled
        if not is_on:
            continue
        out.append(dictionary)
    out.sort(key=lambda d: d.specificity(), reverse=True)
    return out


# ----------------------------------------------------------------------------
# Substitution
# ----------------------------------------------------------------------------


def _spoken_form(entry: PronunciationEntry) -> str | None:
    """The text to substitute, or None to skip (e.g. markup with no fallback).

    Respelling substitutes its replacement directly. Phoneme/SSML entries degrade
    to ``plain_fallback`` so raw markup is never read aloud (native rendering is
    Phase 6); without a fallback they are skipped rather than spoken literally.
    """
    if entry.mode == "respelling":
        return entry.replacement
    return entry.plain_fallback or None


def _compile(entry: PronunciationEntry) -> re.Pattern[str] | None:
    flags = 0 if entry.case_sensitive else re.IGNORECASE
    pattern = entry.term if entry.regex else re.escape(entry.term)
    if entry.whole_word and not entry.regex:
        pattern = rf"\b{pattern}\b"
    try:
        return re.compile(pattern, flags)
    except re.error:
        return None


def apply_pronunciations(
    text: str, engine: str, dictionaries: list[PronunciationDictionary]
) -> PronunciationResult:
    """Apply ``dictionaries`` (active set) to ``text`` for ``engine`` (§4.7.3).

    ``dictionaries`` should be the resolved active set (e.g. from
    :func:`active_dictionaries`); it is treated as ordered most-specific-first.
    On a term conflict the most specific dictionary wins; ties keep earlier
    entries. Matching is longest-term-first so a longer phrase wins over a
    shorter contained one.
    """
    if not text:
        return PronunciationResult(text=text)

    # Collect enabled entries, deduping by (case-folded) term so the most specific
    # dictionary's entry for a term wins. ``dictionaries`` is most-specific-first.
    chosen: dict[str, PronunciationEntry] = {}
    for dictionary in dictionaries:
        for entry in dictionary.entries:
            if not entry.enabled or not entry.term.strip():
                continue
            key = entry.term if entry.case_sensitive else entry.term.casefold()
            chosen.setdefault(key, entry)

    # Collect every match span against the ORIGINAL text (never re-scanning a
    # substituted replacement — that is the "New York" → "noo york" → "noo yorrk"
    # trap), then resolve overlaps greedily left-to-right, longest match first at a
    # tie. This yields longest-term-first semantics deterministically.
    matches: list[tuple[int, int, str, str]] = []
    for entry in chosen.values():
        spoken = _spoken_form(entry)
        if spoken is None:
            continue
        pattern = _compile(entry)
        if pattern is None:
            continue
        for found in pattern.finditer(text):
            if found.end() > found.start():  # skip zero-width matches
                matches.append((found.start(), found.end(), spoken, entry.term))

    matches.sort(key=lambda m: (m[0], -(m[1] - m[0])))
    parts: list[str] = []
    applied: dict[str, int] = {}
    cursor = 0
    for start, end, spoken, term in matches:
        if start < cursor:
            continue  # overlaps an already-applied match
        parts.append(text[cursor:start])
        parts.append(spoken)
        applied[term] = applied.get(term, 0) + 1
        cursor = end
    parts.append(text[cursor:])

    return PronunciationResult(text="".join(parts), is_ssml=False, applied=applied)
