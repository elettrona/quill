"""Tests for opening and saving existing chaptered audiobooks (MP3 path)."""

from __future__ import annotations

from pathlib import Path

import pytest

mutagen = pytest.importorskip("mutagen")

from quill.core.speech.book_file import (  # noqa: E402
    BookFile,
    BookReadError,
    build_m4b_remux_command,
    read_book,
    save_mp3_book,
)
from quill.core.speech.chapters import Chapter, write_mp3_chapters  # noqa: E402
from quill.core.speech.ffmpeg import AudioMetadata  # noqa: E402


@pytest.fixture
def silent_mp3(tmp_path: Path) -> Path:
    """A minimal valid MP3 (silent frames) to tag in place."""
    path = tmp_path / "book.mp3"
    frame = b"\xff\xfb\x90\x00" + b"\x00" * 413
    path.write_bytes(frame * 4)
    return path


def _chapters() -> list[Chapter]:
    return [
        Chapter(index=0, title="Intro", start_ms=0, end_ms=60_000),
        Chapter(index=1, title="Body", start_ms=60_000, end_ms=180_000),
    ]


def test_read_book_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(BookReadError):
        read_book(tmp_path / "nope.mp3")


def test_mp3_book_round_trip(silent_mp3: Path) -> None:
    write_mp3_chapters(silent_mp3, _chapters())
    book = read_book(silent_mp3)
    assert [c.title for c in book.chapters] == ["Intro", "Body"]
    assert book.kind == "mp3"

    # Edit: rename a chapter, set tags, save in place, read back.
    book.chapters[1].title = "The Long Road"
    book.tags = AudioMetadata(
        album="My Book", artist="Jane Doe", album_artist="Sam Reader", genre="Fiction", year="2026"
    )
    save_mp3_book(book)
    again = read_book(silent_mp3)
    assert [c.title for c in again.chapters] == ["Intro", "The Long Road"]
    assert again.tags.album == "My Book"
    assert again.tags.artist == "Jane Doe"
    assert again.tags.album_artist == "Sam Reader"
    assert again.tags.genre == "Fiction"
    assert again.tags.year == "2026"


def test_mp3_without_chapters_opens_as_single_chapter(silent_mp3: Path, monkeypatch) -> None:
    # No CHAP frames and no ffprobe: duration comes from the chapter fallback.
    import quill.core.speech.book_file as book_file

    monkeypatch.setattr("quill.core.speech.ffmpeg.probe_duration_ms", lambda _p, **_k: 120_000)
    book = book_file.read_book(silent_mp3)
    assert len(book.chapters) == 1
    assert book.chapters[0].start_ms == 0
    assert book.chapters[0].end_ms == 120_000
    assert book.chapters[0].title == "book"


def test_m4b_remux_command_is_lossless_copy() -> None:
    args = build_m4b_remux_command("ffmpeg", Path("in.m4b"), Path("meta.ffmeta"), Path("out.m4b"))
    assert args[args.index("-c") + 1] == "copy"
    assert "-map_chapters" in args and "-map_metadata" in args
    assert args[args.index("-f") + 1] == "ipod"
    assert args[-1] == "out.m4b"


def test_save_m4b_refuses_same_path(tmp_path: Path, monkeypatch) -> None:
    from quill.core.speech.book_file import save_m4b_book_as
    from quill.core.speech.ffmpeg import TranscodeError

    src = tmp_path / "book.m4b"
    src.write_bytes(b"stub")
    book = BookFile(path=src, tags=AudioMetadata(), chapters=_chapters(), total_ms=180_000)
    monkeypatch.setattr("quill.core.speech.book_file.find_ffmpeg", lambda: "ffmpeg")
    with pytest.raises(TranscodeError):
        save_m4b_book_as(book, src)
