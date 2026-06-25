"""Tests for the Build Audiobook dialog's option collection (no real ffmpeg)."""

from __future__ import annotations

from pathlib import Path

import pytest  # type: ignore[import-not-found]

wx = pytest.importorskip("wx")

from quill.ui.audiobook_builder_dialog import (  # noqa: E402
    AudiobookBuilderDialog,
    AudiobookRequest,
)


@pytest.fixture(scope="module")
def wx_app():
    app = wx.App()
    yield app
    app.Destroy()


def _defaults(tmp_path: Path) -> AudiobookRequest:
    return AudiobookRequest(
        source_folder=tmp_path,
        recursive=False,
        output_path=tmp_path / "book.m4b",
        output_format="m4b",
        album="My Book",
        author="Jeff",
        narrator="",
        genre="Audiobook",
        year="2026",
        cover_path="",
    )


_ROWS = [
    ("/a/01 - Intro.mp3", "Intro"),
    ("/a/02 - Middle.mp3", "Middle"),
    ("/a/03 - End.mp3", "End"),
]


def _make(wx_app, tmp_path, rows=_ROWS):
    frame = wx.Frame(None)
    dlg = AudiobookBuilderDialog(
        frame, defaults=_defaults(tmp_path), on_scan=lambda folder, recursive: (list(rows), "")
    )
    return frame, dlg


def test_collect_round_trips_defaults(wx_app, tmp_path):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        req = dlg._collect()
        assert req.output_format == "m4b"
        assert req.album == "My Book"
        assert req.author == "Jeff"
        assert req.genre == "Audiobook"
        assert req.year == "2026"
    finally:
        dlg.dialog.Destroy()
        frame.Destroy()


def test_format_choice_switches_to_mp3(wx_app, tmp_path):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        dlg._format.SetSelection(1)  # MP3
        assert dlg._current_format() == "mp3"
        assert dlg._collect().output_format == "mp3"
    finally:
        dlg.dialog.Destroy()
        frame.Destroy()


def test_scan_populates_chapter_plan(wx_app, tmp_path):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        plan = dlg._collect().chapter_plan
        assert plan == [
            ("Intro", ["/a/01 - Intro.mp3"]),
            ("Middle", ["/a/02 - Middle.mp3"]),
            ("End", ["/a/03 - End.mp3"]),
        ]
    finally:
        dlg.dialog.Destroy()
        frame.Destroy()


def test_rename_reorder_and_merge_chapters(wx_app, tmp_path):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        # Rename chapter 1.
        dlg._chapter_list.SetSelection(0)
        dlg._on_chapter_selected()
        dlg._title_edit.SetValue("Prologue")
        dlg._on_rename()
        assert dlg._chapters[0].title == "Prologue"

        # Move "End" (index 2) up to index 1.
        dlg._chapter_list.SetSelection(2)
        dlg._on_move(-1)
        assert [c.title for c in dlg._chapters] == ["Prologue", "End", "Middle"]

        # Merge "Middle" (now index 2) into the previous chapter "End".
        dlg._chapter_list.SetSelection(2)
        dlg._on_merge_up()
        assert len(dlg._chapters) == 2
        merged = dlg._chapters[1]
        assert merged.title == "End"
        assert merged.paths == ["/a/03 - End.mp3", "/a/02 - Middle.mp3"]
        assert "2 files" in merged.label()

        plan = dlg._collect().chapter_plan
        assert plan == [
            ("Prologue", ["/a/01 - Intro.mp3"]),
            ("End", ["/a/03 - End.mp3", "/a/02 - Middle.mp3"]),
        ]
    finally:
        dlg.dialog.Destroy()
        frame.Destroy()


def test_acx_checkbox_flows_into_request(wx_app, tmp_path):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        assert dlg._collect().acx_normalize is False
        dlg._acx.SetValue(True)
        assert dlg._collect().acx_normalize is True
    finally:
        dlg.dialog.Destroy()
        frame.Destroy()
