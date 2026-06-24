"""Batch TTS export: folder-scan → text-extract → synthesize → WAV files.

wx-free; all synthesis calls block the caller's thread.  The UI layer
wraps :func:`run_batch_export` in its own thread and uses ``wx.CallAfter``
for progress updates.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from quill.core.speech.pronunciation import PronunciationDictionary, apply_pronunciations
from quill.core.speech.text_polish import UnsupportedFormatError, extract_text, polish_for_tts

__all__ = [
    "BatchExportOptions",
    "BatchFileResult",
    "discover_files",
    "run_batch_export",
    "SUPPORTED_EXTENSIONS",
]

SUPPORTED_EXTENSIONS: tuple[str, ...] = (".md", ".html", ".htm", ".docx")

BatchStatus = Literal["pending", "processing", "done", "error", "skipped"]


@dataclass
class BatchExportOptions:
    source_folder: Path
    output_folder: Path
    engine: str = "sapi5"
    extensions: list[str] = field(default_factory=lambda: [".md", ".html", ".docx"])
    recursive: bool = True
    # SAPI 5 (Windows system voice)
    sapi5_voice: str = ""
    sapi5_rate: int = 200
    sapi5_volume: float = 1.0
    # DECtalk
    dectalk_executable: Path | None = None
    dectalk_voice: str = "paul"
    dectalk_rate: int = 180
    dectalk_dictionary: Path | None = None
    # Piper
    piper_executable: Path | None = None
    piper_model: Path | None = None
    # Kokoro
    kokoro_voice: str = "af_heart"
    kokoro_speed: float = 1.0
    # eSpeak-NG
    espeak_executable: Path | None = None
    espeak_voice: str = "en"
    espeak_rate: int = 175
    # Pronunciation dictionaries (§4.7): the resolved active set for this engine
    # and (the source folder as) project. Applied as a silent text transform before
    # synthesis — batch writes audio files to disk and never reads aloud.
    pronunciation_dictionaries: list[PronunciationDictionary] = field(default_factory=list)


@dataclass
class BatchFileResult:
    source_path: Path
    output_path: Path | None = None
    status: BatchStatus = "pending"
    error: str | None = None
    duration_s: float | None = None
    pronunciation_applied: int = 0  # §4.7.10 per-file substitution count


ProgressFn = Callable[[int, int, "BatchFileResult"], None]
"""Called after each file: (done_count, total_count, updated_result)."""


def discover_files(
    folder: Path,
    extensions: list[str],
    recursive: bool,
) -> list[Path]:
    """Return source files matching *extensions* under *folder*."""
    exts = {e.lower() for e in extensions}
    glob = "**/*" if recursive else "*"
    found: list[Path] = []
    for ext in exts:
        found.extend(folder.glob(f"{glob}{ext}"))
    found.sort()
    return found


def _output_path_for(source: Path, source_root: Path, output_root: Path) -> Path:
    """Mirror the relative path of *source* under *output_root*, with .wav suffix."""
    try:
        rel = source.relative_to(source_root)
    except ValueError:
        rel = Path(source.name)
    return (output_root / rel).with_suffix(".wav")


def _synthesize_one(text: str, output_path: Path, opts: BatchExportOptions) -> None:
    """Call the appropriate synthesis function for the configured engine."""
    from quill.core.read_aloud import (
        ReadAloudUnavailableError,
        synthesize_to_file_with_dectalk,
        synthesize_to_file_with_sapi5,
        synthesize_with_espeak,
        synthesize_with_kokoro,
        synthesize_with_piper,
    )

    engine = opts.engine.strip().lower()
    if engine == "pyttsx3":  # migrate the retired engine id
        engine = "sapi5"

    if engine == "sapi5":
        synthesize_to_file_with_sapi5(
            text,
            output_path,
            voice=opts.sapi5_voice,
            rate=opts.sapi5_rate,
            volume=opts.sapi5_volume,
        )
    elif engine == "dectalk":
        if opts.dectalk_executable is None:
            raise ReadAloudUnavailableError("DECtalk executable not configured")
        synthesize_to_file_with_dectalk(
            text,
            output_path,
            executable_path=opts.dectalk_executable,
            voice=opts.dectalk_voice,
            rate=opts.dectalk_rate,
            dictionary_path=opts.dectalk_dictionary,
        )
    elif engine == "piper":
        if opts.piper_executable is None:
            raise ReadAloudUnavailableError("Piper executable not configured")
        if opts.piper_model is None:
            raise ReadAloudUnavailableError("Piper model not configured")
        synthesize_with_piper(
            text,
            output_path,
            executable_path=opts.piper_executable,
            model_path=opts.piper_model,
        )
    elif engine == "kokoro":
        synthesize_with_kokoro(
            text,
            output_path,
            voice=opts.kokoro_voice,
            speed=opts.kokoro_speed,
        )
    elif engine == "espeak":
        if opts.espeak_executable is None:
            raise ReadAloudUnavailableError("eSpeak-NG executable not configured")
        synthesize_with_espeak(
            text,
            output_path,
            executable_path=opts.espeak_executable,
            voice=opts.espeak_voice,
            rate=opts.espeak_rate,
        )
    else:
        raise ReadAloudUnavailableError(f"Unknown engine: {engine!r}")


def run_batch_export(
    options: BatchExportOptions,
    results: list[BatchFileResult],
    on_progress: ProgressFn,
    cancel_event: threading.Event,
) -> None:
    """Process every file in *results* in order.

    *results* must be pre-populated (e.g. from :func:`discover_files`) with
    ``status="pending"``.  Updates each entry in-place and calls *on_progress*
    after every file so the UI can refresh.
    """
    total = len(results)
    done = 0

    for res in results:
        if cancel_event.is_set():
            res.status = "skipped"
            on_progress(done, total, res)
            continue

        res.status = "processing"
        on_progress(done, total, res)

        t0 = time.monotonic()
        try:
            text = extract_text(res.source_path)
            # §4.7.4: pronunciation correction runs before polishing, as a silent
            # text transform (no audio) — the same stage the live path uses.
            if options.pronunciation_dictionaries:
                applied = apply_pronunciations(
                    text, options.engine, options.pronunciation_dictionaries
                )
                text = applied.text
                res.pronunciation_applied = applied.total_applied
            text = polish_for_tts(text)
            if not text.strip():
                res.status = "skipped"
                res.error = "No speakable text"
                done += 1
                on_progress(done, total, res)
                continue

            out = _output_path_for(res.source_path, options.source_folder, options.output_folder)
            out.parent.mkdir(parents=True, exist_ok=True)
            res.output_path = out

            _synthesize_one(text, out, options)

            res.status = "done"
            res.duration_s = time.monotonic() - t0
        except UnsupportedFormatError as exc:
            res.status = "skipped"
            res.error = str(exc)
        except Exception as exc:  # noqa: BLE001
            res.status = "error"
            res.error = str(exc)

        done += 1
        on_progress(done, total, res)
