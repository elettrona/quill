"""Tests for the Batch Speech Export dialog's option collection (no real engine).

Constructs the dialog under a module-scoped ``wx.App`` and exercises the pure
option-collection logic: extension grouping (HTML implies HTM), engine switching
reloading the voice list, format mapping, and that the gap/pause controls round
-trip into the returned :class:`BatchSpeechRequest`.
"""

from __future__ import annotations

from pathlib import Path

import pytest  # type: ignore[import-not-found]

wx = pytest.importorskip("wx")

from quill.ui.batch_speech_export_dialog import (  # noqa: E402
    BatchSpeechExportDialog,
    BatchSpeechRequest,
)


@pytest.fixture(scope="module")
def wx_app():
    app = wx.App()
    yield app
    app.Destroy()


_VOICES = {
    "kokoro": [("Liam", "am_liam"), ("Heart", "af_heart")],
    "sapi5": [("David", "David"), ("Zira", "Zira")],
}


def _defaults(tmp_path: Path) -> BatchSpeechRequest:
    return BatchSpeechRequest(
        source_folder=tmp_path,
        recursive=False,
        extensions=(".docx", ".html", ".htm"),
        engine="kokoro",
        voice="am_liam",
        rate=190,
        speed=1.1,
        output_format="mp3",
        sound_enabled=True,
        sound_volume=80,
        article_gap_ms=1200,
        sentence_gap_ms=250,
        tail_padding_ms=300,
        speak_headings=True,
        skip_existing=False,
    )


def _make(wx_app, tmp_path):
    frame = wx.Frame(None)
    dlg = BatchSpeechExportDialog(
        frame,
        engine_options=[("Windows (SAPI 5)", "sapi5"), ("Kokoro (neural, offline)", "kokoro")],
        engine_available={"sapi5": True, "kokoro": True},
        voices_for=lambda e: _VOICES.get(e, []),
        on_preview=lambda req: None,
        defaults=_defaults(tmp_path),
    )
    return frame, dlg


def test_collect_round_trips_defaults(wx_app, tmp_path):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        req = dlg._collect(preview=False)
        assert req.engine == "kokoro"
        assert req.voice == "am_liam"
        assert req.output_format == "mp3"
        assert req.rate == 190
        assert abs(req.speed - 1.1) < 1e-6
        assert req.sentence_gap_ms == 250
        assert req.tail_padding_ms == 300
        assert req.sound_volume == 80
        # HTML default is checked and expands to both .html and .htm.
        assert ".html" in req.extensions and ".htm" in req.extensions
    finally:
        dlg.dialog.Destroy()
        frame.Destroy()


def test_switching_engine_reloads_voices(wx_app, tmp_path):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        dlg._select_engine("sapi5")
        dlg._reload_voices()
        assert [vid for _lbl, vid in dlg._voice_pairs] == ["David", "Zira"]
        dlg._voice.SetSelection(1)
        assert dlg._current_voice_id() == "Zira"
    finally:
        dlg.dialog.Destroy()
        frame.Destroy()


def test_format_choice_maps_each_option(wx_app, tmp_path):
    frame, dlg = _make(wx_app, tmp_path)
    try:
        dlg._format.SetSelection(0)
        assert dlg._collect(preview=False).output_format == "mp3"
        dlg._format.SetSelection(1)
        assert dlg._collect(preview=False).output_format == "m4b"
        dlg._format.SetSelection(2)
        assert dlg._collect(preview=False).output_format == "wav"
    finally:
        dlg.dialog.Destroy()
        frame.Destroy()
