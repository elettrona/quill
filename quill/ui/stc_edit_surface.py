"""Scintilla editor surface -- the "Notepad++ experiment" (Experimental tab).

Hosts ``wx.stc.StyledTextCtrl`` (Win32 window class "Scintilla", the engine
behind Notepad++) as an experimental editor surface. Scintilla is the only
alternative surface that natively provides multi-level undo AND redo while
remaining a real windowed control that screen readers can address; NVDA
supports it well (it drives Notepad++ daily), JAWS support is partial. The
full risk analysis lives in edit.md at the repository root ("stc" section).

StyledTextCtrl implements the wx.TextCtrl-compatible API QUILL relies on
(value, caret, selection tuples, Replace/GetRange, PositionToXY, undo/redo),
verified by probe. Four contract gaps remain, all shimmed here:

* ``wx.EVT_TEXT`` never fires natively -- only ``EVT_STC_CHANGE`` -- so dirty
  tracking, word count, and the Reveal Codes sync would go dead. The wrapper
  forwards each change as a ``wxEVT_TEXT`` command event.
* ``ChangeValue`` fires change notifications and leaves the buffer reported
  as modified; QUILL loads documents through ``ChangeValue`` and must not see
  a fresh document as dirty. The wrapper suppresses forwarding and sets the
  Scintilla save point (and empties the undo buffer, matching a load).
* ``SetInsertionPoint`` moves the caret but leaves the selection anchor
  behind, so a later ``WriteText`` replaces the dragged selection. The
  wrapper uses ``GotoPos``, which collapses the selection like wx.TextCtrl.
* Line endings pass through unconverted; QUILL's buffer is LF-only. The
  wrapper pins ``STC_EOL_LF``, converts on load, and converts pasted text.
* wx's Scintilla port paints its own caret and never touches the Windows
  system caret -- the one signal JAWS and NVDA use for caret tracking -- so
  pressing Enter moved the buffer but the screen reader stayed on the old
  line. Real Scintilla (ScintillaWin, what Notepad++ ships) mirrors an
  invisible system caret on every update; :class:`_SystemCaretMirror`
  replicates that with ctypes (no pywin32 dependency).

Mirrors the rtf/win32 defensive pattern: on any failure the factory returns
a stock ``wx.TextCtrl`` so selecting this surface can never brick the editor.
"""

from __future__ import annotations

import sys
from typing import Any

try:
    import wx
    import wx.stc as _stc

    _SCINTILLA = True
except Exception:  # noqa: BLE001 - wx.stc absent/broken: surface unavailable
    _SCINTILLA = False


class _SystemCaretMirror:
    """Mirror Scintilla's drawn caret to an invisible Windows system caret.

    JAWS and NVDA follow the system caret through win events
    (EVENT_OBJECT_LOCATIONCHANGE on OBJID_CARET). ScintillaWin creates a
    caret from an all-zero monochrome bitmap -- XOR with zeros paints
    nothing, so the user never sees a second blinking caret -- and moves it
    on every caret update. wx's port skips all of this; without it the
    screen reader reports the caret frozen on its old line.

    Every call is wrapped: a failure here degrades to the previous behavior
    (no tracking), never to a crash.
    """

    def __init__(self, ctrl: Any) -> None:
        self._ctrl = ctrl
        self._active = False
        self._bitmap = None

    def activate(self) -> None:
        if sys.platform != "win32" or self._active:
            return
        try:
            import ctypes

            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            width = max(1, int(self._ctrl.GetCaretWidth() or 1))
            height = max(2, int(self._ctrl.TextHeight(self._ctrl.GetCurrentLine())))
            # Monochrome scanlines are word-aligned; all zeros = invisible.
            stride = ((width + 15) // 16) * 2
            bits = ctypes.create_string_buffer(stride * height)
            self._bitmap = gdi32.CreateBitmap(width, height, 1, 1, bits)
            hwnd = int(self._ctrl.GetHandle())
            user32.CreateCaret(hwnd, self._bitmap, width, height)
            user32.ShowCaret(hwnd)
            self._active = True
            self.update()
        except Exception:  # noqa: BLE001 - tracking is best-effort
            self._active = False

    def update(self) -> None:
        if not self._active:
            return
        try:
            import ctypes

            point = self._ctrl.PointFromPosition(self._ctrl.GetCurrentPos())
            ctypes.windll.user32.SetCaretPos(int(point.x), int(point.y))
        except Exception:  # noqa: BLE001
            pass

    def deactivate(self) -> None:
        if not self._active:
            return
        try:
            import ctypes

            ctypes.windll.user32.DestroyCaret()
            if self._bitmap:
                ctypes.windll.gdi32.DeleteObject(self._bitmap)
        except Exception:  # noqa: BLE001
            pass
        self._bitmap = None
        self._active = False


if _SCINTILLA:

    class StcEditorSurface(_stc.StyledTextCtrl):  # type: ignore[misc]
        """StyledTextCtrl configured to honor the wx.TextCtrl editor contract."""

        def __init__(self, parent: Any, style: int = 0) -> None:
            super().__init__(parent, style=style)
            self._suppress_text_events = 0
            # LF-only buffer so caret offsets match GetValue() string indices,
            # including for text pasted with CRLF endings.
            self.SetEOLMode(_stc.STC_EOL_LF)
            self.SetPasteConvertEndings(True)
            # A clean text surface: no line-number/fold/symbol margins.
            for margin in range(5):
                self.SetMarginWidth(margin, 0)
            # Match the default wx.TextCtrl word wrap.
            self.SetWrapMode(_stc.STC_WRAP_WORD)
            self.Bind(_stc.EVT_STC_CHANGE, self._forward_text_event)
            # Screen-reader caret tracking: create the invisible system caret
            # while focused and move it on every caret/scroll update.
            self._caret_mirror = _SystemCaretMirror(self)
            self.Bind(wx.EVT_SET_FOCUS, self._on_focus_gained)
            self.Bind(wx.EVT_KILL_FOCUS, self._on_focus_lost)
            self.Bind(_stc.EVT_STC_UPDATEUI, self._on_update_ui)

        def surface_kind(self) -> str:
            return "stc"

        def _on_focus_gained(self, event: Any) -> None:
            event.Skip()
            self._caret_mirror.activate()

        def _on_focus_lost(self, event: Any) -> None:
            event.Skip()
            self._caret_mirror.deactivate()

        def _on_update_ui(self, event: Any) -> None:
            event.Skip()
            self._caret_mirror.update()

        def _forward_text_event(self, event: Any) -> None:
            event.Skip()
            if self._suppress_text_events:
                return
            text_event = wx.CommandEvent(wx.wxEVT_TEXT, self.GetId())
            text_event.SetEventObject(self)
            wx.PostEvent(self.GetEventHandler(), text_event)

        def _release_text_events(self) -> None:
            if self._suppress_text_events:
                self._suppress_text_events -= 1

        def ChangeValue(self, value: str) -> None:  # noqa: N802 - wx API
            self._suppress_text_events += 1
            try:
                self.SetText(value or "")
                self.ConvertEOLs(_stc.STC_EOL_LF)
                self.EmptyUndoBuffer()
                self.SetSavePoint()
            finally:
                # Change notifications may arrive queued as well as inline;
                # lift the suppression only after the queue has drained.
                wx.CallAfter(self._release_text_events)

        def SetValue(self, value: str) -> None:  # noqa: N802 - wx API
            # Same normalization as ChangeValue, but the change event fires
            # (wx.TextCtrl.SetValue semantics).
            self.SetText(value or "")
            self.ConvertEOLs(_stc.STC_EOL_LF)
            self.EmptyUndoBuffer()
            self.SetSavePoint()

        def SetInsertionPoint(self, pos: int) -> None:  # noqa: N802 - wx API
            # GotoPos moves caret AND anchor; the inherited implementation
            # leaves the anchor behind, silently dragging a selection.
            self.GotoPos(int(pos))


def create_stc_editor(wx_module: Any, parent: Any, style: int) -> Any:
    """Build the Scintilla surface, or a stock ``wx.TextCtrl`` fallback."""
    if _SCINTILLA:
        try:
            return StcEditorSurface(parent, style=style)
        except Exception:  # noqa: BLE001 - hosting is best-effort; fall back to wx
            pass
    return wx_module.TextCtrl(parent, style=style)
