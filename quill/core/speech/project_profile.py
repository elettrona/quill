"""Project-remembered speech settings — ``<project>/.quill/speech-project.json`` (§4.10).

wx-free, strict-typed. A *project* is a folder of documents; this module persists
that folder's whole speech profile so the user configures **once per project**:
the synthesizer (engine + voice + rate/speed), the output format, the chapter
options, the text-normalization options, and which pronunciation dictionaries
(and their formats) are active.

The on-disk format is documented in ``docs/planning/speech-project-format.md`` and
schema-described in ``quill/core/schemas/speech_project.json``. The dataclasses
here are the in-memory mirror, with ``to_dict`` / ``from_dict`` (tolerant of
missing keys and old versions) and ``load_profile`` / ``save_profile`` for the
atomic JSON file. Convenience converters (:func:`to_batch_options`,
:func:`to_chapter_options`) turn a profile into the runtime option objects so the
batch pipeline can be driven straight from a project file — including headlessly
in tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from quill.core.storage import read_json, write_json_atomic

PROJECT_DIRNAME = ".quill"
PROFILE_FILENAME = "speech-project.json"
PROFILE_VERSION = 1

_VALID_ENGINES = {"sapi5", "dectalk", "piper", "kokoro", "espeak"}
_VALID_FORMATS = {"wav", "mp3"}
_VALID_CHAPTER_MODES = {"none", "single", "separate"}
_VALID_SCOPES = {"global", "project"}
# Dictionary file formats we know how to read. "quill-json" is the native
# PronunciationDictionary schema; others are reserved for future importers.
_VALID_DICT_FORMATS = {"quill-json", "sapi-lexicon", "csv"}


def _clamp_int(value: Any, default: int, lo: int, hi: int) -> int:
    try:
        return max(lo, min(hi, int(value)))
    except (TypeError, ValueError):
        return default


def _as_float(value: Any, default: float, lo: float, hi: float) -> float:
    try:
        return max(lo, min(hi, float(value)))
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class SynthesizerProfile:
    """The chosen engine and its voice/pace. ``extra`` holds engine-specific keys."""

    engine: str = "sapi5"
    voice: str = ""
    rate: int = 200  # words-per-minute style rate (SAPI/eSpeak/DECtalk)
    volume: float = 1.0  # 0.0-1.0
    speed: float = 1.0  # multiplier engines that use one (Kokoro)
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": self.engine,
            "voice": self.voice,
            "rate": self.rate,
            "volume": self.volume,
            "speed": self.speed,
            "extra": dict(self.extra),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SynthesizerProfile:
        engine = str(data.get("engine", "sapi5")).strip().lower()
        if engine not in _VALID_ENGINES:
            engine = "sapi5"
        extra = data.get("extra")
        return cls(
            engine=engine,
            voice=str(data.get("voice", "")),
            rate=_clamp_int(data.get("rate", 200), 200, 50, 800),
            volume=_as_float(data.get("volume", 1.0), 1.0, 0.0, 1.0),
            speed=_as_float(data.get("speed", 1.0), 1.0, 0.25, 4.0),
            extra=dict(extra) if isinstance(extra, dict) else {},
        )


@dataclass(slots=True)
class OutputProfile:
    """How the audio is written."""

    format: str = "wav"  # wav | mp3
    skip_existing: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"format": self.format, "skip_existing": self.skip_existing}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OutputProfile:
        fmt = str(data.get("format", "wav")).strip().lower()
        if fmt not in _VALID_FORMATS:
            fmt = "wav"
        return cls(format=fmt, skip_existing=bool(data.get("skip_existing", False)))


@dataclass(slots=True)
class ChapterProfile:
    """Chapterization options (§4.8.8), mirrored from the app settings."""

    mode: str = "none"  # none | single | separate
    sound_enabled: bool = False
    sound_id: str = ""  # sound-pack id; "" = bundled placeholder chime
    sound_volume: int = 100  # 0-100
    article_gap_ms: int = 1200  # 0-10000
    sentence_gap_ms: int = 0  # 0-10000; silence between sentences within a section (opt-in)
    tail_padding_ms: int = 300  # 0-10000; trailing silence per section (anti-clipping default)
    intro_section_title: str = "Introduction"

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "sound_enabled": self.sound_enabled,
            "sound_id": self.sound_id,
            "sound_volume": self.sound_volume,
            "article_gap_ms": self.article_gap_ms,
            "sentence_gap_ms": self.sentence_gap_ms,
            "tail_padding_ms": self.tail_padding_ms,
            "intro_section_title": self.intro_section_title,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChapterProfile:
        mode = str(data.get("mode", "none")).strip().lower()
        if mode not in _VALID_CHAPTER_MODES:
            mode = "none"
        title = str(data.get("intro_section_title", "Introduction")).strip() or "Introduction"
        return cls(
            mode=mode,
            sound_enabled=bool(data.get("sound_enabled", False)),
            sound_id=str(data.get("sound_id", "")).strip(),
            sound_volume=_clamp_int(data.get("sound_volume", 100), 100, 0, 100),
            article_gap_ms=_clamp_int(data.get("article_gap_ms", 1200), 1200, 0, 10000),
            sentence_gap_ms=_clamp_int(data.get("sentence_gap_ms", 0), 0, 0, 10000),
            tail_padding_ms=_clamp_int(data.get("tail_padding_ms", 300), 300, 0, 10000),
            intro_section_title=title,
        )


@dataclass(slots=True)
class DictionaryRef:
    """A reference to one pronunciation dictionary the project uses (§4.7)."""

    id: str
    scope: str = "global"  # global | project
    format: str = "quill-json"
    path: str = ""  # for project scope: path relative to the project root; "" = by id

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "scope": self.scope, "format": self.format, "path": self.path}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DictionaryRef:
        scope = str(data.get("scope", "global")).strip().lower()
        if scope not in _VALID_SCOPES:
            scope = "global"
        fmt = str(data.get("format", "quill-json")).strip().lower()
        if fmt not in _VALID_DICT_FORMATS:
            fmt = "quill-json"
        return cls(
            id=str(data.get("id", "")).strip(),
            scope=scope,
            format=fmt,
            path=str(data.get("path", "")).strip(),
        )


@dataclass(slots=True)
class PronunciationProfile:
    """Which pronunciation dictionaries (and formats) are active for the project."""

    enabled: bool = True
    dictionaries: list[DictionaryRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "dictionaries": [d.to_dict() for d in self.dictionaries],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PronunciationProfile:
        raw = data.get("dictionaries")
        dicts = (
            [DictionaryRef.from_dict(d) for d in raw if isinstance(d, dict) and d.get("id")]
            if isinstance(raw, list)
            else []
        )
        return cls(enabled=bool(data.get("enabled", True)), dictionaries=dicts)


@dataclass(slots=True)
class SpeechProjectProfile:
    """The complete remembered speech profile for one project folder (§4.10)."""

    version: int = PROFILE_VERSION
    synthesizer: SynthesizerProfile = field(default_factory=SynthesizerProfile)
    output: OutputProfile = field(default_factory=OutputProfile)
    chapters: ChapterProfile = field(default_factory=ChapterProfile)
    # Serialized TextNormalizationOptions (empty = recommended defaults).
    normalization: dict[str, Any] = field(default_factory=dict)
    pronunciation: PronunciationProfile = field(default_factory=PronunciationProfile)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "synthesizer": self.synthesizer.to_dict(),
            "output": self.output.to_dict(),
            "chapters": self.chapters.to_dict(),
            "normalization": dict(self.normalization),
            "pronunciation": self.pronunciation.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpeechProjectProfile:
        if not isinstance(data, dict):
            return cls()
        norm = data.get("normalization")
        return cls(
            version=_clamp_int(data.get("version", PROFILE_VERSION), PROFILE_VERSION, 1, 1000),
            synthesizer=SynthesizerProfile.from_dict(_sub(data, "synthesizer")),
            output=OutputProfile.from_dict(_sub(data, "output")),
            chapters=ChapterProfile.from_dict(_sub(data, "chapters")),
            normalization=dict(norm) if isinstance(norm, dict) else {},
            pronunciation=PronunciationProfile.from_dict(_sub(data, "pronunciation")),
        )


def _sub(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    return value if isinstance(value, dict) else {}


def profile_path(project_dir: Path) -> Path:
    """Path to the project's speech profile file (may not exist yet)."""
    return project_dir / PROJECT_DIRNAME / PROFILE_FILENAME


def load_profile(project_dir: Path) -> SpeechProjectProfile | None:
    """Load the project's speech profile, or ``None`` when the folder has none."""
    path = profile_path(project_dir)
    if not path.is_file():
        return None
    raw = read_json(path, default=None)
    if not isinstance(raw, dict):
        return None
    return SpeechProjectProfile.from_dict(raw)


def save_profile(profile: SpeechProjectProfile, project_dir: Path) -> Path:
    """Write *profile* to ``<project_dir>/.quill/speech-project.json`` atomically."""
    path = profile_path(project_dir)
    write_json_atomic(path, profile.to_dict())
    return path


# --- Profile -> runtime options (drives the batch pipeline from a project) --- #


def to_chapter_options(profile: SpeechProjectProfile) -> Any:
    """Build a :class:`ChapterAssembleOptions` from a profile (lazy import)."""
    from quill.core.speech.chapter_assemble import ChapterAssembleOptions

    ch = profile.chapters
    return ChapterAssembleOptions(
        article_gap_ms=ch.article_gap_ms,
        sound_enabled=ch.sound_enabled,
        sound_path=None,  # sound_id resolution to a real file is a UI/sound-pack concern
        sound_volume=ch.sound_volume,
        intro_section_title=ch.intro_section_title,
        output_format=profile.output.format,
        sentence_gap_ms=ch.sentence_gap_ms,
        tail_padding_ms=ch.tail_padding_ms,
    )


def to_batch_options(
    profile: SpeechProjectProfile,
    source_folder: Path,
    output_folder: Path,
    *,
    pronunciation_dictionaries: list[Any] | None = None,
) -> Any:
    """Build a :class:`BatchExportOptions` from a profile and source/output folders.

    Engine-specific fields are filled from the synthesizer profile (with ``extra``
    supplying per-engine keys like ``piper_model`` or ``dectalk_executable``). The
    resolved active pronunciation dictionaries are passed through unchanged.
    """
    from quill.core.speech.batch_export import BatchExportOptions

    s = profile.synthesizer
    extra = s.extra
    opts = BatchExportOptions(
        source_folder=source_folder,
        output_folder=output_folder,
        engine=s.engine,
        output_format=profile.output.format,  # type: ignore[arg-type]
        skip_existing=profile.output.skip_existing,
        pronunciation_dictionaries=pronunciation_dictionaries or [],
    )
    # Engine-specific wiring from the flat profile + extra bag.
    if s.engine == "sapi5":
        opts.sapi5_voice = s.voice
        opts.sapi5_rate = s.rate
        opts.sapi5_volume = s.volume
    elif s.engine == "dectalk":
        opts.dectalk_voice = s.voice or "paul"
        opts.dectalk_rate = s.rate
        if extra.get("dectalk_executable"):
            opts.dectalk_executable = Path(str(extra["dectalk_executable"]))
        if extra.get("dectalk_dictionary"):
            opts.dectalk_dictionary = Path(str(extra["dectalk_dictionary"]))
    elif s.engine == "piper":
        if extra.get("piper_executable"):
            opts.piper_executable = Path(str(extra["piper_executable"]))
        if extra.get("piper_model"):
            opts.piper_model = Path(str(extra["piper_model"]))
    elif s.engine == "kokoro":
        opts.kokoro_voice = s.voice or "af_heart"
        opts.kokoro_speed = s.speed
    elif s.engine == "espeak":
        opts.espeak_voice = s.voice or "en"
        opts.espeak_rate = s.rate
        if extra.get("espeak_executable"):
            opts.espeak_executable = Path(str(extra["espeak_executable"]))
    return opts
