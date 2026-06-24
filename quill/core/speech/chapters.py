"""MP3/ID3 chapter markers for batch document-to-speech (§4.8.4).

wx-free, strict-typed. Computes chapter boundaries from per-section durations and
writes ID3v2.3 CHAP + CTOC frames (the format Apple Podcasts, Overcast, VLC,
foobar2000, … navigate). The CHAP/CTOC writer is borrowed from the sibling BITS
project **ChapterForge** (``d:\\code99\\forum``, MIT) — ``core.Chapter`` /
``core.compute_chapters`` / ``core.write_tags_and_chapters`` — with two
deliberate fixes over the borrowed logic (see ``docs/planning`` §4.8.4 notes):

1. Chapters are **contiguous**: with an inter-article gap, the gap silence is the
   trailing part of the article it follows (``end_ms`` of chapter i equals
   ``start_ms`` of chapter i+1), so every millisecond belongs to a chapter.
   ChapterForge's ``_chapters_with_gaps`` leaves the gap un-chaptered.
2. Writing **loads existing ID3 tags** and only replaces the chapter frames,
   instead of building a fresh ``ID3()`` that discards other metadata.

Requires ``mutagen`` (the ``quill[mp3]`` extra); imported lazily so this module
loads without it and ``write_mp3_chapters`` raises a clear error if it is absent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Chapter:
    """A computed chapter boundary (ms), mirroring ChapterForge's ``Chapter``."""

    index: int
    title: str
    start_ms: int
    end_ms: int

    @property
    def duration_ms(self) -> int:
        return self.end_ms - self.start_ms


@dataclass(slots=True)
class ChapterSection:
    """One source section to be chaptered: a heading title and its audio length."""

    title: str
    duration_ms: int


def compute_chapters(sections: list[ChapterSection], gap_ms: int = 0) -> list[Chapter]:
    """Cumulative chapter boundaries from section durations, contiguous with gaps.

    ``gap_ms`` of silence is inserted between articles (never after the last). The
    gap is counted as the **trailing** part of the preceding chapter, so chapters
    are contiguous (``chapters[i].end_ms == chapters[i+1].start_ms``) and the whole
    timeline is covered — the fix over ChapterForge's gap handling.
    """
    chapters: list[Chapter] = []
    cursor = 0
    last = len(sections) - 1
    for i, section in enumerate(sections):
        start = cursor
        trailing_gap = max(0, gap_ms) if i < last else 0
        end = start + max(0, section.duration_ms) + trailing_gap
        chapters.append(Chapter(index=i, title=section.title, start_ms=start, end_ms=end))
        cursor = end
    return chapters


def write_mp3_chapters(path: Path, chapters: list[Chapter], *, toc_title: str = "Chapters") -> None:
    """Write ID3v2.3 CHAP + CTOC frames onto ``path`` (existing tags preserved).

    Idempotent: any existing CHAP/CTOC frames are removed first so re-running does
    not duplicate chapters. Raises ``RuntimeError`` when mutagen is unavailable.
    """
    try:
        from mutagen.id3 import CHAP, CTOC, ID3, TIT2, CTOCFlags, ID3NoHeaderError
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise RuntimeError(
            "MP3 chapter markers require the 'mutagen' package (quill[mp3])."
        ) from exc

    try:
        tags = ID3(str(path))
    except ID3NoHeaderError:
        tags = ID3()

    tags.delall("CHAP")
    tags.delall("CTOC")

    element_ids: list[str] = []
    for chapter in chapters:
        element_id = f"chp{chapter.index:04d}"
        element_ids.append(element_id)
        tags.add(
            CHAP(
                element_id=element_id,
                start_time=int(chapter.start_ms),
                end_time=int(chapter.end_ms),
                start_offset=0xFFFFFFFF,  # 0xFFFFFFFF = "use time, ignore byte offset"
                end_offset=0xFFFFFFFF,
                sub_frames=[TIT2(encoding=3, text=[chapter.title])],
            )
        )
    if element_ids:
        tags.add(
            CTOC(
                element_id="toc",
                flags=CTOCFlags.TOP_LEVEL | CTOCFlags.ORDERED,
                child_element_ids=element_ids,
                sub_frames=[TIT2(encoding=3, text=[toc_title])],
            )
        )
    tags.save(str(path), v2_version=3)


def read_mp3_chapters(path: Path) -> list[Chapter]:
    """Read CHAP frames back from ``path`` (ordered by start time). For verification."""
    from mutagen.id3 import ID3

    tags = ID3(str(path))
    frames = sorted(tags.getall("CHAP"), key=lambda f: f.start_time)
    chapters: list[Chapter] = []
    for index, frame in enumerate(frames):
        title = ""
        title_frame = frame.sub_frames.get("TIT2")
        if title_frame is not None and title_frame.text:
            title = str(title_frame.text[0])
        chapters.append(
            Chapter(
                index=index,
                title=title,
                start_ms=int(frame.start_time),
                end_ms=int(frame.end_time),
            )
        )
    return chapters


@dataclass(slots=True)
class ChapterSettings:
    """Resolved batch chapterization settings (§4.8.8); see core.settings for storage."""

    mode: str = "none"  # none | single | separate
    sound_enabled: bool = False
    sound_id: str = ""
    sound_volume: int = 100  # 0–100
    article_gap_ms: int = 1200
    intro_section_title: str = "Introduction"
    extra: dict[str, str] = field(default_factory=dict)
