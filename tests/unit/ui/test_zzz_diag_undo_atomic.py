"""TEMPORARY diagnostic for the macOS test_main_frame_undo_atomic.py failure.

Not a real test suite file -- run once via CI, read the printed diagnostics,
then delete. Named zzz_ so it sorts/runs late (after the real tests) and is
trivially greppable/removable.
"""

from __future__ import annotations

import sys

import pytest

wx = pytest.importorskip("wx")

from quill.ui.main_frame import MainFrame  # noqa: E402


@pytest.fixture(scope="module")
def wx_app():
    app = wx.App()
    yield app
    app.Destroy()


class _Holder:
    def __init__(self, editor) -> None:
        self.editor = editor

    _atomic_replace = MainFrame._atomic_replace


def _dump(label: str, ctrl: "wx.TextCtrl") -> None:
    print(  # noqa: T201
        f"[DIAG] {label}: value={ctrl.GetValue()!r} CanUndo={ctrl.CanUndo()} "
        f"CanRedo={ctrl.CanRedo()} IsModified={ctrl.IsModified()}"
    )


def test_zzz_diag_unshown_vs_shown(wx_app) -> None:
    print(f"[DIAG] platform={sys.platform} wx.version={wx.version()}")  # noqa: T201

    # Scenario A: never Show()n (matches the real failing test exactly).
    frame_a = wx.Frame(None)
    try:
        ctrl = wx.TextCtrl(frame_a, style=wx.TE_MULTILINE)
        ctrl.SetValue("hello world this is a test")
        holder = _Holder(ctrl)
        _dump("A after SetValue", ctrl)
        text = ctrl.GetValue()
        holder._atomic_replace(0, len(text), text.upper())
        _dump("A after atomic_replace", ctrl)
        ctrl.Undo()
        _dump("A after 1st Undo", ctrl)
        if ctrl.GetValue() != text:
            ctrl.Undo()
            _dump("A after 2nd Undo", ctrl)
    finally:
        frame_a.Destroy()

    # Scenario B: Show()n frame -- tests the "unshown/non-key window" hypothesis.
    frame_b = wx.Frame(None)
    try:
        frame_b.Show()
        wx_app.ProcessPendingEvents()
        ctrl = wx.TextCtrl(frame_b, style=wx.TE_MULTILINE)
        ctrl.SetValue("hello world this is a test")
        holder = _Holder(ctrl)
        wx_app.ProcessPendingEvents()
        _dump("B after SetValue+Show", ctrl)
        text = ctrl.GetValue()
        holder._atomic_replace(0, len(text), text.upper())
        wx_app.ProcessPendingEvents()
        _dump("B after atomic_replace", ctrl)
        ctrl.Undo()
        wx_app.ProcessPendingEvents()
        _dump("B after 1st Undo", ctrl)
        if ctrl.GetValue() != text:
            ctrl.Undo()
            wx_app.ProcessPendingEvents()
            _dump("B after 2nd Undo", ctrl)
    finally:
        frame_b.Destroy()

    # Scenario C: raw Replace() (the pre-#131 approach) for comparison -- does
    # THIS also corrupt on macOS, or is select+WriteText uniquely broken here?
    frame_c = wx.Frame(None)
    try:
        ctrl = wx.TextCtrl(frame_c, style=wx.TE_MULTILINE)
        ctrl.SetValue("hello world this is a test")
        _dump("C after SetValue", ctrl)
        text = ctrl.GetValue()
        ctrl.Replace(0, len(text), text.upper())
        _dump("C after raw Replace", ctrl)
        ctrl.Undo()
        _dump("C after 1st Undo", ctrl)
        if ctrl.GetValue() != text:
            ctrl.Undo()
            _dump("C after 2nd Undo", ctrl)
    finally:
        frame_c.Destroy()

    # Scenario D: SetSelection+WriteText but with an explicit SetFocus() first
    # -- maybe Cocoa's NSTextView only records selection-replace as undoable
    # when it is (or has been) first responder at least once.
    frame_d = wx.Frame(None)
    try:
        ctrl = wx.TextCtrl(frame_d, style=wx.TE_MULTILINE)
        ctrl.SetValue("hello world this is a test")
        ctrl.SetFocus()
        holder = _Holder(ctrl)
        _dump("D after SetValue+SetFocus", ctrl)
        text = ctrl.GetValue()
        holder._atomic_replace(0, len(text), text.upper())
        _dump("D after atomic_replace", ctrl)
        ctrl.Undo()
        _dump("D after 1st Undo", ctrl)
        if ctrl.GetValue() != text:
            ctrl.Undo()
            _dump("D after 2nd Undo", ctrl)
    finally:
        frame_d.Destroy()

    # Scenario E: seed with ChangeValue() (matches the real document-load path
    # -- main_frame.py always uses ChangeValue, never SetValue, specifically
    # because ChangeValue does not generate an event or mark modified) instead
    # of SetValue(). If A/B/C/D's "empty after 1 undo" is really SetValue()
    # itself getting coalesced into the same undo group as the next edit,
    # this should NOT reproduce.
    frame_e = wx.Frame(None)
    try:
        ctrl = wx.TextCtrl(frame_e, style=wx.TE_MULTILINE)
        ctrl.ChangeValue("hello world this is a test")
        holder = _Holder(ctrl)
        _dump("E after ChangeValue", ctrl)
        text = ctrl.GetValue()
        holder._atomic_replace(0, len(text), text.upper())
        _dump("E after atomic_replace", ctrl)
        ctrl.Undo()
        _dump("E after 1st Undo", ctrl)
        if ctrl.GetValue() != text:
            ctrl.Undo()
            _dump("E after 2nd Undo", ctrl)
    finally:
        frame_e.Destroy()

    assert True  # this file only exists to print diagnostics
