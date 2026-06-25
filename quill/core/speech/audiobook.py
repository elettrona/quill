"""Build one chaptered audiobook/podcast master from a folder of audio files.

The ChapterForge-aligned surface (design source: ``D:\\code99\\forum``, MIT):
point QUILL at a folder of audio files and combine them into a single chaptered
**MP3** or **M4B** master that an audiobook/podcast player navigates track by
track. Each source file becomes a chapter (its title derived from the filename),
a cover image found in the folder is picked up, and the book's tags
(title/author/narrator/genre/year) are written.

wx-free, strict-typed. All ffmpeg work goes through
:mod:`quill.core.speech.ffmpeg`; chapter timing reuses
:func:`quill.core.speech.chapters.compute_chapters`. Only the surfaces that fit
QUILL's current audiobook vision are ported here — ChapterForge's Auphonic, RSS
feed, SFTP-publish, and metadata-lookup features are intentionally left out.
"""

from __future__ import annotations

import re
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from quill.core.speech.ffmpeg import AudioMetadata, TranscodeError

# Source audio formats accepted as chapter files, and cover-image discovery.
AUDIO_EXTENSIONS: tuple[str, ...] = (
    ".mp3",
    ".m4a",
    ".m4b",
    ".wav",
    ".flac",
    ".ogg",
    ".opus",
    ".aac",
)
# Output formats that carry navigable chapters: MP3 (ID3 CHAP via mutagen) and
# M4B (native MP4 chapter atoms). These are the only meaningful audiobook outputs —
# FLAC/Opus cannot carry the chapter markers an audiobook needs, so they are not
# offered as output (they are still accepted as source chapter files).
OUTPUT_FORMATS: tuple[str, ...] = ("mp3", "m4b")
_COVER_STEMS: tuple[str, ...] = ("cover", "folder", "front", "albumart", "album", "artwork")
_COVER_EXTENSIONS: tuple[str, ...] = (".jpg", ".jpeg", ".png")

_NUM_RE = re.compile(r"(\d+)")
# A leading track-number prefix: "01 - ", "02_", "03.", "4) ", or a bare "01 "
# before a word. \d{1,3} leaves four-digit years like "1984" alone.
_TRACK_PREFIX_RE = re.compile(r"^\s*\d{1,3}\s*(?:[-._)]+\s*|\s+(?=[^\W\d]))", re.UNICODE)


def natural_key(text: str) -> list[object]:
    """Natural sort key so "track2" precedes "track10" (digits compared as ints)."""
    return [int(part) if part.isdigit() else part.lower() for part in _NUM_RE.split(text)]


def title_from_filename(path: Path) -> str:
    """Derive a chapter title from a filename, stripping a leading track prefix.

    Returns "" when nothing meaningful remains (e.g. ``01.mp3``) so the caller can
    substitute a generated "Chapter N".
    """
    stem = path.stem
    cleaned = _TRACK_PREFIX_RE.sub("", stem).replace("_", " ").strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    # A purely numeric name (e.g. "01") has no real title; let the caller add one.
    return "" if cleaned.isdigit() else cleaned


def find_cover(folder: Path) -> Path | None:
    """Return a likely cover image in *folder* (preferred names first), or None."""
    images = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in _COVER_EXTENSIONS]
    for stem in _COVER_STEMS:
        for image in images:
            if image.stem.lower() == stem:
                return image
    return images[0] if images else None


@dataclass(slots=True)
class AudiobookChapter:
    """One chapter: a primary file, display title, duration, and any merged files.

    A chapter is normally one source file (``extra_paths`` empty). When the user
    **merges** adjacent files in the builder, the trailing files land in
    ``extra_paths`` — they play as part of this chapter (in order, after ``path``)
    but get no chapter marker of their own. ``duration_ms`` is the sum of all parts.
    """

    path: Path
    title: str
    duration_ms: int
    extra_paths: list[Path] = field(default_factory=list)

    @property
    def all_paths(self) -> list[Path]:
        """The chapter's files in play order: the primary file then any merged ones."""
        return [self.path, *self.extra_paths]


@dataclass(slots=True)
class AudiobookResult:
    """What a build produced."""

    output_path: Path
    chapter_count: int
    notes: list[str] = field(default_factory=list)


def scan_audio_folder(folder: Path, *, recursive: bool = False) -> list[Path]:
    """Return the audio files under *folder*, natural-sorted by name."""
    from quill.core.speech.batch_discovery import discover_files

    found = discover_files(folder, list(AUDIO_EXTENSIONS), recursive)
    return sorted(found, key=lambda p: natural_key(p.name))


def build_chapter_list(paths: list[Path]) -> list[AudiobookChapter]:
    """Probe each file's duration and derive its chapter title ("Chapter N" fallback)."""
    from quill.core.speech.ffmpeg import probe_duration_ms

    chapters: list[AudiobookChapter] = []
    for index, path in enumerate(paths, start=1):
        title = title_from_filename(path) or f"Chapter {index}"
        duration = probe_duration_ms(path)
        chapters.append(AudiobookChapter(path=path, title=title, duration_ms=duration))
    return chapters


def chapters_from_plan(plan: list[tuple[str, list[Path]]]) -> list[AudiobookChapter]:
    """Build chapters from an edited ``(title, [files])`` plan, probing durations.

    Each entry is one chapter; entries with more than one file are merged chapters
    (the first file is primary, the rest go to ``extra_paths``). Used by the builder
    when the user has renamed / reordered / merged chapters before building.
    """
    from quill.core.speech.ffmpeg import probe_duration_ms

    chapters: list[AudiobookChapter] = []
    for index, (title, files) in enumerate(plan, start=1):
        if not files:
            continue
        parts = [Path(f) for f in files]
        duration = sum(probe_duration_ms(p) for p in parts)
        chapters.append(
            AudiobookChapter(
                path=parts[0],
                title=title.strip() or f"Chapter {index}",
                duration_ms=duration,
                extra_paths=parts[1:],
            )
        )
    return chapters


def _ffconcat_quote(path: Path) -> str:
    """Quote a path for the ffmpeg concat demuxer (single quotes are escaped)."""
    return "'" + str(path).replace("'", "'\\''") + "'"


def build_concat_list(paths: list[Path]) -> str:
    """Build the ffmpeg concat-demuxer list document for *paths*."""
    return "\n".join(f"file {_ffconcat_quote(p)}" for p in paths) + "\n"


def build_audiobook_command(
    ffmpeg: str,
    concat_list: Path,
    out_path: Path,
    fmt: str,
    *,
    ffmetadata: Path | None = None,
    cover: Path | None = None,
    map_chapters: bool = False,
    acx_normalize: bool = False,
) -> list[str]:
    """Build the ffmpeg argv that concatenates the chapter files into *out_path*.

    Inputs are ordered: the concat list, then (optional) the FFMETADATA document,
    then (optional) the cover image. Tags/chapters come from the metadata input;
    the cover is mapped as an attached picture. When *acx_normalize* is set the
    audio is run through the ``loudnorm`` filter to bring it into ACX loudness range
    during the (already re-encoding) build. Pure and unit-tested.
    """
    args = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list),
    ]
    next_index = 1
    meta_index = cover_index = -1
    if ffmetadata is not None:
        args.extend(["-i", str(ffmetadata)])
        meta_index = next_index
        next_index += 1
    if cover is not None:
        args.extend(["-i", str(cover)])
        cover_index = next_index
        next_index += 1
    args.extend(["-map", "0:a"])
    if cover is not None:
        args.extend(["-map", f"{cover_index}:v", "-disposition:v:0", "attached_pic"])
    if meta_index >= 0:
        args.extend(["-map_metadata", str(meta_index)])
        if map_chapters:
            args.extend(["-map_chapters", str(meta_index)])
    if acx_normalize:
        from quill.core.speech.loudness import loudnorm_filter

        args.extend(["-af", loudnorm_filter()])
    if fmt == "m4b":
        args.extend(["-c:a", "aac", "-b:a", "96k", "-c:v", "copy", "-f", "ipod"])
    else:  # mp3
        args.extend(["-c:a", "libmp3lame", "-q:a", "4", "-c:v", "copy"])
    args.extend(["-y", str(out_path)])
    return args


def build_audiobook(
    chapters: list[AudiobookChapter],
    output_path: Path,
    *,
    output_format: str = "m4b",
    metadata: AudioMetadata | None = None,
    cover: Path | None = None,
    acx_normalize: bool = False,
    on_progress: Callable[[str], None] | None = None,
    cancel_event: threading.Event | None = None,
) -> AudiobookResult:
    """Concatenate *chapters* into one chaptered audiobook master at *output_path*.

    Returns an :class:`AudiobookResult`. Raises :class:`TranscodeError` when ffmpeg
    is unavailable or the build fails, and :class:`ValueError` on empty input.
    """
    import tempfile

    from quill.core.speech.chapters import (
        ChapterSection,
        compute_chapters,
        write_mp3_chapters,
    )
    from quill.core.speech.ffmpeg import build_ffmetadata, find_ffmpeg
    from quill.stability.safe_subprocess import run_subprocess_safely

    fmt = output_format.strip().lower()
    if fmt not in OUTPUT_FORMATS:
        raise ValueError(f"Unsupported audiobook format: {output_format!r}")
    speakable = [c for c in chapters if c.path.is_file()]
    if not speakable:
        raise ValueError("No audio files to build an audiobook from.")
    if cancel_event is not None and cancel_event.is_set():
        raise TranscodeError("Audiobook build cancelled.")

    ffmpeg = find_ffmpeg()
    if ffmpeg is None:
        from quill.core.speech.ffmpeg import INSTALL_HINT

        raise TranscodeError(f"ffmpeg is not installed. {INSTALL_HINT}")

    computed = compute_chapters(
        [ChapterSection(title=c.title, duration_ms=c.duration_ms) for c in speakable], gap_ms=0
    )
    notes: list[str] = []
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if on_progress is not None:
        on_progress("Combining chapters...")

    with tempfile.TemporaryDirectory(prefix="quill_audiobook_") as tmp:
        tmp_dir = Path(tmp)
        list_path = tmp_dir / "chapters.txt"
        # A merged chapter contributes all of its files (primary + merged) to the
        # concat list, in order, but still emits a single chapter marker.
        concat_paths = [p for c in speakable for p in c.all_paths if p.is_file()]
        list_path.write_text(build_concat_list(concat_paths), encoding="utf-8")
        meta_path = tmp_dir / "meta.ffmeta"
        # M4B carries chapters natively; MP3 gets tags from ffmpeg and chapters from
        # mutagen afterwards (ffmpeg does not write ID3 CHAP frames reliably).
        chapter_tuples = [(c.title, c.start_ms, c.end_ms) for c in computed] if fmt == "m4b" else []
        meta_path.write_text(build_ffmetadata(chapter_tuples, metadata), encoding="utf-8")
        args = build_audiobook_command(
            ffmpeg,
            list_path,
            output_path,
            fmt,
            ffmetadata=meta_path,
            cover=cover if (cover and cover.is_file()) else None,
            map_chapters=(fmt == "m4b"),
            acx_normalize=acx_normalize,
        )
        try:
            completed = run_subprocess_safely(args, timeout_seconds=1800.0)
        except OSError as exc:
            raise TranscodeError(f"Could not run ffmpeg: {exc}") from exc

    if completed.returncode != 0:
        detail = (completed.stderr or "").strip()[:300]
        output_path.unlink(missing_ok=True)
        raise TranscodeError(f"ffmpeg could not build the audiobook. {detail}".strip())
    if not output_path.is_file():
        raise TranscodeError("ffmpeg produced no output.")

    if fmt == "mp3":
        if on_progress is not None:
            on_progress("Writing chapter markers...")
        try:
            write_mp3_chapters(output_path, computed)
        except RuntimeError as exc:  # mutagen missing
            notes.append(f"Chapter markers not written ({exc}).")

    return AudiobookResult(output_path=output_path, chapter_count=len(speakable), notes=notes)
