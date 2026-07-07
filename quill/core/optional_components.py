"""Optional, downloadable components — a single status model (wx-free).

QUILL ships a small base installer and fetches several large or redistributable
components on demand (PRD 10.2.x): the offline speech engine, neural voices,
classic voices, optional tools, and non-English spell-check dictionaries. Each had
its own scattered download entry point; this module gives a *single* status model
so a "Download Optional Components" dialog (Help menu) can show, in one place, what
is present versus what is available — the touch point the footprint plan asked for
(§10.2.5).

Pure logic, no ``wx``: it only *reports* status by asking each component's existing
detector. The download actions themselves stay in the UI (they need progress and
consent), keyed by :attr:`OptionalComponent.component_id`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Categories (also the dialog's grouping labels).
SPEECH_ENGINE = "Speech engine"
VOICES = "Voices"
DICTIONARY = "Spell-check dictionary"
TOOL = "Tool"


@dataclass(frozen=True, slots=True)
class OptionalComponent:
    """One optional component and whether it is installed right now."""

    component_id: str  # stable key the UI maps to a download action
    name: str
    description: str
    category: str
    installed: bool
    size_hint: str  # human "~8 MB" etc.; "" when unknown
    # A note shown when a component is present for a reason other than a download
    # (e.g. an upgrader's bundled copy, or a system-provided tool).
    note: str = ""
    # Display priority: lower sorts higher in the dialog (importance order).
    # Left at the default for dictionaries, which are grouped and sorted by name.
    priority: int = 500

    @property
    def status_label(self) -> str:
        return "Installed" if self.installed else "Available to download"


# Read Aloud engine id a voice component provides, so removing it can reset the
# active engine to the always-present SAPI 5 floor (the UI does the reset +
# menu refresh; see the design's "remove closes the loop" decision).
_ENGINE_BY_COMPONENT: dict[str, str] = {
    "kokoro": "kokoro",
    "piper": "piper",
    "espeak": "espeak",
    "dectalk": "dectalk",
}


def read_aloud_engine_for_component(component_id: str) -> str | None:
    """The ``settings.read_aloud_engine`` value this component provides, or None."""
    return _ENGINE_BY_COMPONENT.get(component_id)


def _app_data_root() -> Path:
    from quill.core.paths import app_data_dir

    return app_data_dir()


def _candidate_removable_path(component_id: str) -> Path | None:
    """The on-disk copy Remove would delete for *component_id*, before safety
    checks. None when QUILL has no managed-dir helper for it (e.g. dectalk,
    mathcat, spell dictionaries — no Remove offered there yet)."""
    try:
        if component_id == "kokoro":
            return _app_data_root() / "kokoro-models"
        if component_id == "whispercpp":
            return _app_data_root() / "speech-engine"
        if component_id == "piper":
            from quill.core.speech.piper_install import managed_piper_dir

            return managed_piper_dir()
        if component_id == "espeak":
            from quill.core.speech.espeak_install import managed_espeak_dir

            return managed_espeak_dir()
        if component_id == "node":
            from quill.core.node_install import managed_node_dir

            return managed_node_dir()
        if component_id == "ffmpeg":
            from quill.core.speech.ffmpeg_install import managed_ffmpeg_dir

            return managed_ffmpeg_dir()
        if component_id == "braille":
            from quill.core.braille_pack import managed_braille_dir

            return managed_braille_dir()
        if component_id == "pandoc":
            from quill.core.pandoc_install import managed_pandoc_dir

            return managed_pandoc_dir()
        if component_id == "vosk":
            from quill.core.speech.engine_install import vosk_pack_dir

            return vosk_pack_dir()
        if component_id == "libmpv":
            from quill.core.speech.engine_install import engine_packs_dir

            return engine_packs_dir() / "mpv"
    except Exception:  # noqa: BLE001 - a missing helper just means "not removable"
        return None
    return None


def removable_path(component_id: str) -> Path | None:
    """Return the QUILL-downloaded copy Remove may delete, or None.

    Returns a path only when it exists **and** lives under the active data dir
    (``app_data_dir()``, which is the portable data folder in portable mode). A
    system tool on PATH, an upgrader's ``{app}`` copy, or a component with no
    managed-dir helper returns None, so no Remove is offered for those.
    """
    path = _candidate_removable_path(component_id)
    if path is None:
        return None
    try:
        root = _app_data_root().resolve()
        resolved = path.resolve()
    except Exception:  # noqa: BLE001
        return None
    if not path.exists():
        return None
    # Safety: only ever delete inside the active (portable-aware) data dir.
    if resolved != root and root not in resolved.parents:
        return None
    return path


def remove_component(component_id: str) -> bool:
    """Delete QUILL's downloaded copy of *component_id* and clear caches.

    Returns True when something was removed, False when there was nothing QUILL
    can safely remove (see :func:`removable_path`). Never raises.
    """
    import shutil

    path = removable_path(component_id)
    if path is None:
        return False
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    except OSError:
        return False
    if component_id == "kokoro":
        try:
            from quill.core.read_aloud import clear_kokoro_cache

            clear_kokoro_cache()
        except Exception:  # noqa: BLE001 - cache clear is best-effort
            pass
    return True


def _safe(predicate) -> bool:  # type: ignore[no-untyped-def]
    """Run a detector, treating any failure as 'not installed'."""
    try:
        return bool(predicate())
    except Exception:  # noqa: BLE001 - a broken detector must never crash the list
        return False


def _whisper_installed() -> bool:
    from quill.core.speech.providers.whispercpp import resolve_whisper_executable

    return resolve_whisper_executable() is not None


def _vosk_installed() -> bool:
    from quill.core.speech.engine_install import is_vosk_available

    return is_vosk_available()


def _kokoro_installed() -> bool:
    from quill.core.read_aloud import kokoro_engine_ready

    return kokoro_engine_ready()


def _piper_installed() -> bool:
    from quill.core.read_aloud import discover_piper_executable

    return discover_piper_executable() is not None


def _node_installed() -> bool:
    from quill.core.node_install import is_node_available

    return is_node_available()


def _espeak_installed() -> bool:
    from quill.core.read_aloud import discover_espeak_executable

    return discover_espeak_executable() is not None


def _dectalk_installed() -> bool:
    from quill.core.read_aloud import discover_dectalk_executable

    return discover_dectalk_executable() is not None


def _ffmpeg_installed() -> bool:
    from quill.core.speech.ffmpeg import ffmpeg_available

    return ffmpeg_available()


def _braille_pack_installed() -> bool:
    from quill.core.braille_pack import is_braille_pack_installed

    return is_braille_pack_installed()


def _libmpv_installed() -> bool:
    from quill.core.speech.engine_install import engine_packs_dir

    pack = engine_packs_dir() / "mpv"
    return any((pack / name).is_file() for name in ("libmpv-2.dll", "mpv-2.dll", "libmpv.dll"))


def _pandoc_installed() -> bool:
    from quill.core.external_tools import get_external_tool_status

    return get_external_tool_status("pandoc").installed


def _mathcat_installed() -> bool:
    from quill.core.math import mathcat_engine

    return mathcat_engine.is_available()


def gather_optional_components() -> list[OptionalComponent]:
    """Return every optional component with its current installed status.

    Sorted by ``priority`` (importance order: Pandoc and the braille pack first,
    then engines/voices/tools), with the spell-check dictionaries last, grouped
    and alphabetical, so the dialog reads predictably.
    """
    out: list[OptionalComponent] = [
        OptionalComponent(
            "pandoc",
            "Pandoc (document conversion)",
            "Imports and exports Word, ODT, EPUB, RTF, and many other formats. "
            "Plain-text and Markdown editing work without it. On Windows QUILL "
            "fetches the official build the first time a conversion needs it; "
            "on macOS install Pandoc yourself (for example via Homebrew) and "
            "QUILL finds it on the PATH.",
            TOOL,
            _safe(_pandoc_installed),
            "~45 MB",
            note="Provided by Pandoc (jgm/pandoc); QUILL fetches the official, pinned build.",
            priority=10,
        ),
        OptionalComponent(
            "braille",
            "Braille pack (translation and BRF export)",
            "liblouis translation tables and BRF profiles that power the Translation "
            "submenu and BRF/embossing export. Reading with a braille display works "
            "without it (that is your screen reader); this adds QUILL's own "
            "translation and embossing.",
            TOOL,
            _safe(_braille_pack_installed),
            "~9 MB",
            note="QUILL braille pack (liblouis, LGPL-3.0/GPL-3.0); fetched from QUILL's "
            "pinned release.",
            priority=20,
        ),
        OptionalComponent(
            "whispercpp",
            "Offline speech engine (whisper.cpp)",
            "Powers private, on-device dictation and transcription. SAPI 5 dictation "
            "works without it; this adds the offline Whisper engine.",
            SPEECH_ENGINE,
            _safe(_whisper_installed),
            "~8 MB",
            priority=30,
        ),
        OptionalComponent(
            "kokoro",
            "Kokoro neural voices",
            "High-quality offline neural Read Aloud voices.",
            VOICES,
            _safe(_kokoro_installed),
            "~120 MB",
            priority=40,
        ),
        OptionalComponent(
            "piper",
            "Piper neural voices",
            "Fast, local, high-quality neural Read Aloud voices (dozens of English "
            "voices). A small engine download, then pick voices in Manage Voices.",
            VOICES,
            _safe(_piper_installed),
            "~22 MB",
            note="Piper (MIT, rhasspy/piper); downloaded on demand and SHA-256 verified.",
            priority=50,
        ),
        OptionalComponent(
            "espeak",
            "eSpeak NG voices",
            "Compact offline Read Aloud engine covering many languages.",
            VOICES,
            _safe(_espeak_installed),
            "~40 MB",
            priority=60,
        ),
        OptionalComponent(
            "dectalk",
            "DECtalk voices",
            "The classic DECtalk Read Aloud voices.",
            VOICES,
            _safe(_dectalk_installed),
            "~2 MB",
            priority=70,
        ),
        OptionalComponent(
            "ffmpeg",
            "FFmpeg (audio export helper)",
            "Lets QUILL export speech audio as MP3, M4A/M4B, OGG, Opus, or FLAC. "
            "WAV export works without it.",
            TOOL,
            _safe(_ffmpeg_installed),
            "~90 MB",
            note="Provided by FFmpeg; QUILL helps you fetch the official build.",
            priority=80,
        ),
        OptionalComponent(
            "node",
            "Node.js runtime",
            "Runs Node (JavaScript/TypeScript) Quillins and the Developer Console's "
            "TypeScript interface. Python Quillins and the rest of QUILL work without it.",
            TOOL,
            _safe(_node_installed),
            "~30 MB",
            note="Provided by the OpenJS Foundation; QUILL fetches the official build.",
            priority=85,
        ),
        OptionalComponent(
            "libmpv",
            "mpv player engine (Audio Studio playback)",
            "A higher-fidelity playback engine for the Audio Studio's player: "
            "gapless audio, exact seeking, and instant chapter jumps on long "
            "books. Playback works without it on the built-in Windows engine.",
            TOOL,
            _safe(_libmpv_installed),
            "~44 MB",
            note="mpv playback library (GPL; the download carries its licenses and a "
            "source offer); fetched from QUILL's pinned release.",
            priority=90,
        ),
        OptionalComponent(
            "mathcat",
            "MathCAT math speech engine",
            "Real natural-language speech for equations — used by Insert > Explore "
            'Equation Structure...\'s "Read this part aloud". Equations are still '
            "readable without it, via a simpler built-in template reading.",
            SPEECH_ENGINE,
            _safe(_mathcat_installed),
            "~3 MB",
            note="MathCAT (MIT, daisy/MathCATForC); fetched from QUILL's pinned release.",
            priority=100,
        ),
        OptionalComponent(
            "vosk",
            "Vosk speech engine (very low resource)",
            "A tiny offline dictation/transcription engine for old or low-memory "
            "machines with no GPU. whisper.cpp is the default; this is the lightweight "
            "fallback.",
            SPEECH_ENGINE,
            _safe(_vosk_installed),
            "~51 MB",
            priority=110,
        ),
    ]
    out.extend(_dictionary_components())
    out.sort(key=lambda c: (c.priority, c.name))
    return out


def _dictionary_components() -> list[OptionalComponent]:
    """One entry per downloadable spell-check language, plus the installed ones."""
    try:
        from quill.core import spellcheck
    except Exception:  # noqa: BLE001
        return []
    installed = set(_safe_list(spellcheck.installed_languages))
    available = set(_safe_list(spellcheck.installable_languages))
    # English ships inside pyenchant and is never a separate download; omit it.
    installed.discard("en_US")
    langs = sorted(installed | available)
    rows: list[OptionalComponent] = []
    for lang in langs:
        try:
            display = spellcheck.language_display_name(lang)
        except Exception:  # noqa: BLE001
            display = lang
        rows.append(
            OptionalComponent(
                f"spell-{lang}",
                f"Spell-check dictionary: {display}",
                "A Hunspell dictionary so the spell checker can validate this language.",
                DICTIONARY,
                lang in installed,
                # A representative estimate: Hunspell language packs are a few MB.
                # (Exact per-language sizes are a future refinement, see the design.)
                "~4 MB",
            )
        )
    return rows


def describe_component(component: OptionalComponent) -> str:
    """A rich, human description of *component* for the dialog's detail box.

    Combines what it enables, its size, its license/source note, and its current
    state with a next-step hint. Wx-free and pure so it can be unit-tested.
    """
    lines: list[str] = [component.name, ""]
    if component.description:
        lines.append(component.description)
    if component.note:
        lines.append(component.note)
    size = component.size_hint or "size varies"
    if component.installed:
        lines.append("")
        lines.append(
            f"Status: Installed ({size}). Use Test to confirm it works, or Remove "
            "to delete QUILL's downloaded copy and turn its features back off."
        )
    else:
        lines.append("")
        lines.append(
            f"Status: Not installed. Download ({size}) to enable it — everything "
            "here is optional and the base app works without it."
        )
    return "\n".join(lines)


def _safe_list(getter) -> list:  # type: ignore[no-untyped-def]
    try:
        return list(getter())
    except Exception:  # noqa: BLE001
        return []
