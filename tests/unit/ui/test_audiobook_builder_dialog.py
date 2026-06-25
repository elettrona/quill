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


def _make(wx_app, tmp_path):
    frame = wx.Frame(None)
    dlg = AudiobookBuilderDialog(
        frame, defaults=_defaults(tmp_path), on_scan=lambda folder, recursive: (3, "")
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
