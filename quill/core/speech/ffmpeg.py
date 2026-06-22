"""ffmpeg-based audio preparation for offline speech (#617 follow-up).

whisper.cpp's command-line tool only reliably reads **16 kHz mono PCM WAV**, so
any other input (mp3, m4a, mp4, flac, ogg, or a stereo / 48 kHz WAV) has to be
converted first. This module locates an ``ffmpeg`` executable — preferring a
QUILL-managed copy, then the system ``PATH`` — and transcodes a source file to a
temporary WAV that whisper.cpp can read.

Design notes:

- **Resolution** mirrors ChapterForge's bundled-first ``_find_tool``: look in
  QUILL-managed tool folders, then fall back to ``PATH``; cache the result. The
  basename must be on a narrow allowlist, so QUILL only ever launches a known
  ``ffmpeg`` / ``ffprobe`` binary.
- **Safety**: runs go through :func:`run_subprocess_safely`, which sets
  ``CREATE_NO_WINDOW`` so no console window flashes (important for screen-reader
  users) and bounds every call with a timeout.
- **Licensing**: ffmpeg is GPL/LGPL. QUILL does **not** bundle or redistribute
  it — it uses an ffmpeg already on the system (or a QUILL-managed copy the user
  installs), the same non-redistributor stance ChapterForge takes. This keeps
  QUILL free of ffmpeg's source-distribution obligations.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path

from quill.core.speech import models

# (fraction 0.0-1.0, human message) — same shape as the speech ProgressCallback.
ProgressCallback = Callable[[float, str], None]

TARGET_SAMPLE_RATE = 16000
TARGET_CHANNELS = 1

# whisper.cpp loads these container/codecs natively only as 16 kHz mono WAV.
_ALLOWED_FFMPEG = frozenset({"ffmpeg", "ffmpeg.exe"})
_ALLOWED_FFPROBE = frozenset({"ffprobe", "ffprobe.exe"})

# How to obtain ffmpeg, surfaced in the "not installed" message (no bundling).
INSTALL_HINT = "Install ffmpeg (for example: winget install Gyan.FFmpeg) and try again."


class TranscodeError(Exception):
    """Raised when audio could not be prepared for transcription."""


def ffmpeg_search_dirs() -> list[Path]:
    """QUILL-managed locations to check for ffmpeg/ffprobe before the PATH.

    1. ``{QUILL_APP_ROOT}/tools/ffmpeg`` — a copy shipped beside a portable build
       or dropped in by the user (mirrors the whisper.cpp engine layout).
    2. ``<data>/tools/ffmpeg`` — a copy a future "Download FFmpeg" action installs.
    """
    dirs: list[Path] = []
    app_root = os.environ.get("QUILL_APP_ROOT", "").strip()
    if app_root:
        dirs.append(Path(app_root) / "tools" / "ffmpeg")
    dirs.append(models.app_data_dir() / "tools" / "ffmpeg")
    return dirs


def _resolve_tool(name: str, allowed: frozenset[str]) -> str | None:
    exe = name + (".exe" if os.name == "nt" else "")
    for directory in ffmpeg_search_dirs():
        candidate = directory / exe
        if candidate.is_file() and candidate.name.lower() in allowed:
            return str(candidate)
    found = shutil.which(name)
    if found and Path(found).name.lower() in allowed:
        return found
    return None


@lru_cache(maxsize=1)
def find_ffmpeg() -> str | None:
    """Path to an allowed ffmpeg executable, or None if not installed."""
    return _resolve_tool("ffmpeg", _ALLOWED_FFMPEG)


@lru_cache(maxsize=1)
def find_ffprobe() -> str | None:
    """Path to an allowed ffprobe executable, or None if not installed."""
    return _resolve_tool("ffprobe", _ALLOWED_FFPROBE)


def ffmpeg_available() -> bool:
    """True when QUILL can convert arbitrary audio/video for transcription."""
    return find_ffmpeg() is not None


def build_transcode_command(ffmpeg: str, source: Path, out_wav: Path) -> list[str]:
    """Build the ffmpeg argv that converts ``source`` to a 16 kHz mono PCM WAV.

    Pure and unit-tested: the audio path is a controlled, on-disk file (never
    untrusted document content), so this is safe to hand to a subprocess.
    """
    return [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(source),
        "-vn",  # drop any video stream
        "-ac",
        str(TARGET_CHANNELS),
        "-ar",
        str(TARGET_SAMPLE_RATE),
        "-acodec",
        "pcm_s16le",
        "-y",  # overwrite the temp file
        str(out_wav),
    ]


def transcode_to_wav(
    source: Path,
    *,
    out_dir: Path | None = None,
    progress: ProgressCallback | None = None,
    timeout_seconds: float = 600.0,
) -> Path:
    """Convert ``source`` to a 16 kHz mono WAV whisper.cpp can read.

    Returns the path to the new WAV. When ``out_dir`` is given the file is written
    there (so the caller's temp dir handles cleanup); otherwise a temp file is
    created. Raises :class:`TranscodeError` if ffmpeg is missing or fails.
    """
    from quill.stability.safe_subprocess import run_subprocess_safely

    ffmpeg = find_ffmpeg()
    if ffmpeg is None:
        raise TranscodeError(f"ffmpeg is not installed. {INSTALL_HINT}")
    if not source.is_file():
        raise TranscodeError(f"The audio file was not found: {source}")

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_wav = out_dir / f"{source.stem}.transcode.wav"
    else:
        import tempfile

        fd, raw = tempfile.mkstemp(prefix="quill_transcode_", suffix=".wav")
        os.close(fd)
        out_wav = Path(raw)

    if progress is not None:
        progress(0.0, "Preparing audio...")
    args = build_transcode_command(ffmpeg, source, out_wav)
    try:
        completed = run_subprocess_safely(args, timeout_seconds=timeout_seconds)
    except OSError as exc:
        raise TranscodeError(f"Could not run ffmpeg: {exc}") from exc
    if completed.returncode != 0:
        detail = (completed.stderr or "").strip()[:300]
        out_wav.unlink(missing_ok=True)
        raise TranscodeError(f"ffmpeg could not convert the audio. {detail}".strip())
    if not out_wav.is_file():
        raise TranscodeError("ffmpeg produced no output.")
    if progress is not None:
        progress(0.05, "Audio ready.")
    return out_wav
