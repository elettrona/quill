"""TEMPORARY diagnostic for the macOS voice_browser_dialog IsEnabled() failure.

Not a real test suite file -- run once via CI, read the printed diagnostics,
then delete.
"""

from __future__ import annotations

import sys

import pytest
import wx

from quill.ui.voice_browser_dialog import VoiceBrowserDialog


@pytest.fixture(scope="module")
def wx_app():
    app = wx.App()
    yield app
    app.Destroy()


def _make_dialog(frame, *, preview_fn, preview_stop_fn=None):
    dlg = VoiceBrowserDialog(
        frame,
        engine_options=[("SAPI 5", "sapi5")],
        current_engine="sapi5",
        piper_model_dir=__import__("pathlib").Path("."),
        settings=type(
            "S", (), {"read_aloud_rate": 200, "read_aloud_volume": 100, "read_aloud_pitch": 0}
        )(),
        preview_fn=preview_fn,
        preview_stop_fn=preview_stop_fn,
    )
    dlg._all_voices = [type("V", (), {"id": "v1", "name": "Voice 1", "installed": True})()]
    dlg._displayed_voices = dlg._all_voices
    dlg._voice_lb.Append("Voice 1")
    dlg._voice_lb.SetSelection(0)
    return dlg


def _dump(label: str, btn: "wx.Button") -> None:
    print(  # noqa: T201
        f"[DIAG] {label}: IsEnabled={btn.IsEnabled()} IsThisEnabled={btn.IsThisEnabled()} "
        f"IsShown={btn.IsShown()} ParentIsEnabled={btn.GetParent().IsEnabled()} "
        f"TopLevelShown={wx.GetTopLevelParent(btn).IsShown() if wx.GetTopLevelParent(btn) else None}"
    )


def test_zzz_diag_voice_browser_button_state(wx_app) -> None:
    print(f"[DIAG] platform={sys.platform} wx.version={wx.version()}")  # noqa: T201

    def fake_preview(engine, voice_id, *, live=False, on_state_change=None):
        if on_state_change is not None:
            on_state_change("playing")

    # Scenario A: never Show()n (matches the real failing test exactly).
    frame_a = wx.Frame(None)
    try:
        dlg = _make_dialog(frame_a, preview_fn=fake_preview)
        _dump("A right after construction", dlg._preview_btn)
        dlg._do_preview()
        _dump("A after _do_preview", dlg._preview_btn)
    finally:
        frame_a.Destroy()

    # Scenario B: Show() the frame (not the dialog itself, which is a
    # separate top-level window parented to frame) before interacting.
    frame_b = wx.Frame(None)
    try:
        frame_b.Show()
        wx_app.ProcessPendingEvents()
        dlg = _make_dialog(frame_b, preview_fn=fake_preview)
        _dump("B right after construction", dlg._preview_btn)
        wx_app.ProcessPendingEvents()
        _dump("B after ProcessPendingEvents", dlg._preview_btn)
        dlg._do_preview()
        wx_app.ProcessPendingEvents()
        _dump("B after _do_preview", dlg._preview_btn)
    finally:
        frame_b.Destroy()

    # Scenario C: Show() the dialog itself (dlg.dialog, the actual top-level
    # window the button lives in -- frame is just its parent, not necessarily
    # shown itself either way).
    frame_c = wx.Frame(None)
    try:
        dlg = _make_dialog(frame_c, preview_fn=fake_preview)
        _dump("C right after construction", dlg._preview_btn)
        dialog_window = wx.GetTopLevelParent(dlg._preview_btn)
        print(f"[DIAG] C dialog_window={dialog_window!r}")  # noqa: T201
        if dialog_window is not None:
            dialog_window.Show()
            wx_app.ProcessPendingEvents()
        _dump("C after Show()ing top-level + ProcessPendingEvents", dlg._preview_btn)
        dlg._do_preview()
        wx_app.ProcessPendingEvents()
        _dump("C after _do_preview", dlg._preview_btn)
    finally:
        frame_c.Destroy()

    assert True  # this file only exists to print diagnostics
