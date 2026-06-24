"""Import interpretation: text -> list items / definition entries (§5, §6, §17, §18).

Turning a selection, pasted text, or file contents into model items is where the
"excellent defaults, no silent data loss" promise lives. The functions here are
deliberately conservative: they detect consistently-used markers, treat blank
lines as paragraph separators without inventing blank items, and — crucially for
definition lists — refuse to silently pick a term/definition separator when more
than one is plausible (§18.2), surfacing the ambiguity for the preview instead.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

from quill.core.lists.model import DefinitionEntry, DefinitionList
from quill.core.lists.settings import StructuredListSettings

# Marker shapes for import detection (§6.2). Ordered allows "." or ")".
_BULLET_RE = re.compile(r"^[ \t]*([-+*])[ \t]+(.*)$")
_ORDERED_RE = re.compile(r"^[ \t]*\d+[.)][ \t]+(.*)$")
_TASK_RE = re.compile(r"^[ \t]*[-+*][ \t]+\[([ xX])\][ \t]+(.*)$")


class SelectionMode(Enum):
    AUTO = "auto"
    PARAGRAPH = "paragraph"
    NONBLANK_LINE = "nonblank_line"
    EVERY_LINE = "every_line"


def strip_marker(line: str) -> tuple[str, str, bool]:
    """Return ``(content, kind, checked)`` after removing any list marker.

    ``kind`` is one of ``"task"``, ``"ordered"``, ``"bullet"``, or ``""`` when the
    line carries no recognizable marker. Task markers are checked *before* bullet
    markers because a task line is also a bullet line.
    """
    task = _TASK_RE.match(line)
    if task is not None:
        return task.group(2), "task", task.group(1).lower() == "x"
    ordered = _ORDERED_RE.match(line)
    if ordered is not None:
        return ordered.group(1), "ordered", False
    bullet = _BULLET_RE.match(line)
    if bullet is not None:
        return bullet.group(2), "bullet", False
    return line, "", False


def _trim(text: str, settings: StructuredListSettings) -> str:
    if settings.trim_leading:
        text = text.lstrip(" \t")
    if settings.trim_trailing:
        text = text.rstrip(" \t")
    if settings.collapse_internal_spaces:
        text = re.sub(r"[ \t]{2,}", " ", text)
    return text


def _resolve_mode(text: str, settings: StructuredListSettings) -> SelectionMode:
    configured = settings.selection_mode
    if configured == "paragraph":
        return SelectionMode.PARAGRAPH
    if configured == "nonblank_line":
        return SelectionMode.NONBLANK_LINE
    if configured == "every_line":
        return SelectionMode.EVERY_LINE
    # AUTO (§5.1 recommended): blank-line-separated content reads as paragraphs;
    # otherwise each non-blank line is its own item.
    has_blank_separator = bool(re.search(r"\n[ \t]*\n", text))
    return SelectionMode.PARAGRAPH if has_blank_separator else SelectionMode.NONBLANK_LINE


def interpret_selection(
    text: str, settings: StructuredListSettings | None = None
) -> list[tuple[str, str, bool]]:
    """Interpret ``text`` into ``(content, marker_kind, checked)`` item tuples.

    Honors the configured selection mode (auto/paragraph/line), blank-line policy,
    whitespace trimming, and marker detection. Returns one tuple per item; an
    empty selection yields no items.
    """
    cfg = settings if settings is not None else StructuredListSettings()
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.strip():
        return []
    mode = _resolve_mode(normalized, cfg)
    lines = normalized.split("\n")

    raw_items: list[str] = []
    if mode is SelectionMode.PARAGRAPH:
        paragraph: list[str] = []
        for line in lines:
            if line.strip() == "":
                if paragraph:
                    raw_items.append(_join_paragraph(paragraph, cfg))
                    paragraph = []
                elif cfg.create_blank_items and not cfg.blank_lines_as_separators:
                    raw_items.append("")
            else:
                paragraph.append(line)
        if paragraph:
            raw_items.append(_join_paragraph(paragraph, cfg))
    else:
        for line in lines:
            if line.strip() == "":
                if mode is SelectionMode.EVERY_LINE or cfg.create_blank_items:
                    raw_items.append("")
                continue
            raw_items.append(line)

    items: list[tuple[str, str, bool]] = []
    for raw in raw_items:
        content, kind, checked = (raw, "", False)
        if cfg.detect_existing_markers:
            content, kind, checked = strip_marker(raw)
        items.append((_trim(content, cfg), kind, checked))
    return items


def _join_paragraph(lines: list[str], settings: StructuredListSettings) -> str:
    if settings.preserve_internal_breaks:
        return "\n".join(lines)
    return " ".join(line.strip() for line in lines)


# -- definition-list interpretation (§17, §18) ----------------------------- #

# Ordered most-to-least specific. A tab is the least ambiguous; a bare colon is
# the most (it appears in URLs and prose), so it is only chosen when it divides
# the lines consistently and nothing more specific applies.
_SEPARATORS: list[tuple[str, str]] = [
    ("tab", "\t"),
    ("dash", " - "),
    ("equals", "="),
    ("colon", ":"),
]


@dataclass(slots=True)
class DefinitionInterpretation:
    """A proposed reading of pasted/selected content as definition entries (§18.2)."""

    separator: str  # label: tab|dash|equals|colon|alternating_lines|alternating_paragraphs
    entries: list[tuple[str, str]] = field(default_factory=list)
    ambiguous: bool = False
    candidates: list[str] = field(default_factory=list)
    incomplete_indices: list[int] = field(default_factory=list)


def _split_on(line: str, sep: str) -> tuple[str, str] | None:
    idx = line.find(sep)
    if idx < 0:
        return None
    return line[:idx].strip(), line[idx + len(sep) :].strip()


def detect_definition_separator(text: str) -> DefinitionInterpretation:
    """Pick the best term/definition reading, flagging ambiguity (§18.1, §18.2).

    Tries inline separators (tab, " - ", "=", ":") and the alternating-lines
    pattern. A separator "fits" when it splits the majority of non-blank lines.
    When two or more readings fit comparably the result is marked ``ambiguous``
    so the caller shows a preview rather than guessing (no silent conversion).
    """
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln for ln in normalized.split("\n") if ln.strip()]
    if not lines:
        return DefinitionInterpretation(separator="colon", entries=[])

    fitting: list[str] = []
    best: DefinitionInterpretation | None = None
    for label, sep in _SEPARATORS:
        pairs = [_split_on(ln, sep) for ln in lines]
        hits = sum(1 for p in pairs if p is not None and p[0])
        if hits >= max(1, (len(lines) + 1) // 2):  # splits at least half the lines
            fitting.append(label)
            interp = _build_interpretation(label, lines, sep)
            if best is None:
                best = interp

    # Alternating lines: an even number of lines with no consistent inline sep.
    if not fitting and len(lines) % 2 == 0:
        entries = [(lines[i].strip(), lines[i + 1].strip()) for i in range(0, len(lines), 2)]
        return DefinitionInterpretation(
            separator="alternating_lines",
            entries=entries,
            ambiguous=False,
            candidates=["alternating_lines"],
        )

    if best is None:
        # No separator divides the content; treat each line as a term with a
        # blank definition (the caller's preview lets the user correct this).
        entries = [(ln.strip(), "") for ln in lines]
        return DefinitionInterpretation(
            separator="none", entries=entries, ambiguous=False, candidates=[]
        )

    best.candidates = fitting
    best.ambiguous = len(fitting) > 1
    return best


def _build_interpretation(label: str, lines: list[str], sep: str) -> DefinitionInterpretation:
    entries: list[tuple[str, str]] = []
    incomplete: list[int] = []
    for index, line in enumerate(lines):
        split = _split_on(line, sep)
        if split is None:
            entries.append((line.strip(), ""))
            incomplete.append(index)
        else:
            term, definition = split
            entries.append((term, definition))
            if not term or not definition:
                incomplete.append(index)
    return DefinitionInterpretation(separator=label, entries=entries, incomplete_indices=incomplete)


def interpret_definition_entries(text: str, *, separator: str) -> DefinitionList:
    """Build a :class:`DefinitionList` using an explicitly chosen ``separator``.

    ``separator`` is a label from :class:`DefinitionInterpretation`
    (``tab``/``dash``/``equals``/``colon``/``alternating_lines``/
    ``alternating_paragraphs``) or a literal custom string. The caller picks it
    from the preview, so this function does not re-guess.
    """
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if separator == "alternating_paragraphs":
        return _entries_from_alternating_paragraphs(normalized)
    lines = [ln for ln in normalized.split("\n") if ln.strip()]
    if separator == "alternating_lines":
        pairs = [
            (lines[i].strip(), lines[i + 1].strip() if i + 1 < len(lines) else "")
            for i in range(0, len(lines), 2)
        ]
        return _list_from_pairs(pairs)
    sep = {"tab": "\t", "dash": " - ", "equals": "=", "colon": ":"}.get(separator, separator)
    pairs = []
    for line in lines:
        split = _split_on(line, sep) if sep else None
        pairs.append(split if split is not None else (line.strip(), ""))
    return _list_from_pairs(pairs)


def _entries_from_alternating_paragraphs(text: str) -> DefinitionList:
    paragraphs = [p.strip() for p in re.split(r"\n[ \t]*\n", text) if p.strip()]
    pairs = [
        (paragraphs[i], paragraphs[i + 1] if i + 1 < len(paragraphs) else "")
        for i in range(0, len(paragraphs), 2)
    ]
    return _list_from_pairs(pairs)


def _list_from_pairs(pairs: list[tuple[str, str]]) -> DefinitionList:
    entries = [
        DefinitionEntry(terms=[term], definitions=[definition]) for term, definition in pairs
    ]
    return DefinitionList(entries=entries)
