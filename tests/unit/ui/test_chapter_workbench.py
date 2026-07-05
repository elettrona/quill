"""Tests for the Chapter Workbench dialog (split/retime/merge over a real plan).

Playback itself is not exercised (no media backend in CI); the playhead is
stubbed so the surgery operations can be driven exactly as the buttons do.
"""

from __future__ import annotations

from pathlib import Path

import pytest  # type: ignore[import-not-found]

wx = pytest.importorskip("wx")

from quill.core.speech.book_file import BookFile  # noqa: E402
from quill.core.speech.chapters import Chapter  # noqa: E402
from quill.core.speech.ffmpeg import AudioMetadata  # noqa: E402
from quill.ui.audio_studio.chapter_workbench import ChapterWorkbenchDialog  # noqa: E402


@pytest.fixture(scope="module")
def wx_app():
    app = wx.App()
    yield app
    app.Destroy()


def _book(tmp_path: Path) -> BookFile:
    path = tmp_path / "book.mp3"
    path.write_bytes(b"\xff\xfb\x90\x00" + b"\x00" * 413)
    return BookFile(
        path=path,
        tags=AudioMetadata(album="My Book", artist="Jane"),
        chapters=[
            Chapter(index=0, title="One", start_ms=0, end_ms=60_000),
            Chapter(index=1, title="Two", start_ms=60_000, end_ms=120_000),
        ],
        total_ms=120_000,
    )


def _make(wx_app, tmp_path, announces=None):
    frame = wx.Frame(None)
    dlg = ChapterWorkbenchDialog(
        frame,
        _book(tmp_path),
        announce=(announces.append if announces is not None else None),
    )
    return frame, dlg


def test_list_shows_times_and_titles(wx_app, tmp_path):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        items = [dlg._chapter_list.GetString(i) for i in range(dlg._chapter_list.GetCount())]
        assert items[0] == "1. One — starts 0:00, runs 1:00"
        assert items[1] == "2. Two — starts 1:00, runs 1:00"
    finally:
        dlg.Destroy()
        frame.Destroy()


def test_split_at_playhead(wx_app, tmp_path):
    announces: list[str] = []
    frame, dlg = _make(wx_app, tmp_path, announces)
    try:
        dlg.player.playhead_ms = lambda: 30_000  # stub the transport
        dlg._on_split()
        titles = [c.title for c in dlg._book.chapters]
        assert titles == ["One", "New chapter", "Two"]
        assert dlg._book.chapters[1].start_ms == 30_000
        assert any("Split at 0:30" in a for a in announces)
        assert dlg._dirty
    finally:
        dlg.Destroy()
        frame.Destroy()


def test_retime_selected_chapter_to_playhead(wx_app, tmp_path):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        dlg._chapter_list.SetSelection(1)
        dlg.player.playhead_ms = lambda: 45_000
        dlg._on_retime()
        assert dlg._book.chapters[0].end_ms == 45_000
        assert dlg._book.chapters[1].start_ms == 45_000
    finally:
        dlg.Destroy()
        frame.Destroy()


def test_bad_split_is_spoken_not_crash(wx_app, tmp_path, monkeypatch):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        errors: list[str] = []
        monkeypatch.setattr(dlg, "_error", errors.append)
        dlg.player.playhead_ms = lambda: 0  # not inside any chapter interior
        dlg._on_split()
        assert errors and len(dlg._book.chapters) == 2
    finally:
        dlg.Destroy()
        frame.Destroy()


def test_merge_and_restore(wx_app, tmp_path):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        dlg._chapter_list.SetSelection(1)
        dlg._on_merge()
        assert [c.title for c in dlg._book.chapters] == ["One"]
        assert dlg._book.chapters[0].end_ms == 120_000
        dlg._on_restore()
        assert [c.title for c in dlg._book.chapters] == ["One", "Two"]
        assert not dlg._dirty
    finally:
        dlg.Destroy()
        frame.Destroy()


def test_rename_updates_plan(wx_app, tmp_path):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        dlg._chapter_list.SetSelection(0)
        dlg._title_edit.SetValue("Prologue")
        dlg._on_rename()
        assert dlg._book.chapters[0].title == "Prologue"
    finally:
        dlg.Destroy()
        frame.Destroy()


def test_m4b_disables_in_place_save(wx_app, tmp_path):
    frame = wx.Frame(None)
    book = _book(tmp_path)
    book.path = book.path.with_suffix(".m4b")
    book.path.write_bytes(b"stub")
    dlg = ChapterWorkbenchDialog(frame, book, announce=None)
    try:
        assert dlg._save_btn.IsThisEnabled() is False
    finally:
        dlg.Destroy()
        frame.Destroy()
