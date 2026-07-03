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

Mirrors the rtf/win32 defensive pattern: on any failure the factory returns
a stock ``wx.TextCtrl`` so selecting this surface can never brick the editor.
"""

from __future__ import annotations

from typing import Any

try:
    import wx
    import wx.stc as _stc

    _SCINTILLA = True
except Exception:  # noqa: BLE001 - wx.stc absent/broken: surface unavailable
    _SCINTILLA = False


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

        def surface_kind(self) -> str:
            return "stc"

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
