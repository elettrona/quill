"""Native Microsoft Rich Edit surface for the experimental "richedit_rtf" option.

Selected on the Experimental tab (``experimental_editor_surface = "richedit_rtf"``).
This is **Phase 0** of the QuillRichEdit proposal (see
``docs/planning/editor-surface-experiments.md`` §8): it establishes a
distinct, gated surface backed by the *same* native Windows Rich Edit control
QUILL already ships as its default (``RICHEDIT50W`` from msftedit.dll, created
as a ``wx.TextCtrl`` with ``TE_RICH2``). Because the inner control is that
proven native control, the whole ``EditorSurface`` contract (value / caret /
selection / undo / events) comes for free and unchanged -- Phase 0 adds no risk.

What Phase 0 deliberately does NOT do yet:

* Real RTF load/save. The native path is ``EM_STREAMIN`` / ``EM_STREAMOUT`` with
  an ``EDITSTREAM`` callback; :meth:`QuillRichEdit.load_rtf` / :meth:`save_rtf`
  are declared so callers can feature-detect, but they raise until Phase 1 so
  nothing silently half-works.
* Formatting commands (``CHARFORMAT2`` / ``PARAFORMAT2``) -- Phase 2.
* The braille instrument (TOM selection dump, ``EM_SETEDITSTYLE``) -- Phase 3.

What it DOES give testers now: a selectable surface that is a real Rich Edit
control with its own ``surface_kind`` and a read-only diagnostic that confirms
the underlying Win32 class name -- the first, safe rung of the ladder that later
resolves the cell-2 (#616) and dots-7-8-on-selection (#813) braille bugs.

Mirrors the ``rtf_edit_surface`` / ``stc_edit_surface`` defensive pattern: on any
failure the factory returns a stock ``wx.TextCtrl`` so selecting this surface can
never brick the editor.
"""

from __future__ import annotations

import sys
from typing import Any

# Phase 0 is native RichEdit only; RTF streaming and formatting arrive in later
# phases. This id is the surface_kind and the settings value.
SURFACE_KIND = "richedit_rtf"


class RichEditRtfUnavailableError(NotImplementedError):
    """A QuillRichEdit capability that is scheduled for a later phase.

    Raised by RTF load/save in Phase 0 so callers get a clear, catchable signal
    rather than a silent no-op. Not a :class:`CodedError`: it is a build-time
    "not wired yet" marker, never surfaced to end users.
    """


def _window_class_name(hwnd: int) -> str:
    """Best-effort Win32 window class name for *hwnd* (empty off-Windows/failure).

    Read-only and document-content-free: used only to confirm the surface really
    is a native Rich Edit control (``RICHEDIT50W``), the distinction that made the
    generic-window Scintilla bridge fail for JAWS.
    """
    if sys.platform != "win32" or not hwnd:
        return ""
    try:
        import ctypes

        buffer = ctypes.create_unicode_buffer(256)
        length = ctypes.windll.user32.GetClassNameW(int(hwnd), buffer, 256)
        return buffer.value if length else ""
    except Exception:  # noqa: BLE001 - diagnostics must never raise
        return ""


class QuillRichEdit:
    """Thin, replaceable wrapper API over the native Rich Edit control.

    Phase 0 wires only the pieces that are safe without a device: identity,
    the native window handle, capability reporting, and a read-only diagnostic.
    The RTF/formatting/braille methods are declared so the rest of QUILL can
    feature-detect them, and raise :class:`RichEditRtfUnavailableError` until
    their phase lands. ``surface`` is the live ``wx.TextCtrl`` (TE_RICH2).
    """

    def __init__(self, surface: Any) -> None:
        self._surface = surface

    def hwnd(self) -> int:
        """The native HWND of the Rich Edit control (0 off-Windows/on failure).

        The foundation for every later phase (streaming, TOM, edit-style); safe
        to call now via wx's own ``GetHandle``.
        """
        try:
            return int(self._surface.GetHandle())
        except Exception:  # noqa: BLE001 - handle access is best-effort
            return 0

    def rtf_streaming_available(self) -> bool:
        """Whether native RTF load/save is wired (False in Phase 0)."""
        return False

    def load_rtf(self, path: str) -> None:
        """Load an RTF file via EM_STREAMIN (Phase 1 -- not yet wired)."""
        raise RichEditRtfUnavailableError(
            "Native RTF load (EM_STREAMIN) lands in Phase 1 of the QuillRichEdit "
            "surface; Phase 0 is the native Rich Edit control only."
        )

    def save_rtf(self, path: str) -> None:
        """Save to an RTF file via EM_STREAMOUT (Phase 1 -- not yet wired)."""
        raise RichEditRtfUnavailableError(
            "Native RTF save (EM_STREAMOUT) lands in Phase 1 of the QuillRichEdit "
            "surface; Phase 0 is the native Rich Edit control only."
        )

    def capabilities(self) -> dict[str, Any]:
        """A wx-free report of what this surface can do right now.

        Honest capability reporting is a house rule: the surface says plainly
        that it is Phase 0 (native control, no RTF I/O yet) so callers never
        assume RTF fidelity that is not there.
        """
        return {
            "surface_kind": SURFACE_KIND,
            "phase": 0,
            "native_control": True,
            "rtf_load": False,
            "rtf_save": False,
            "formatting_commands": False,
            "notes": (
                "Phase 0: the native Windows Rich Edit control (RICHEDIT50W). RTF "
                "load/save (Phase 1), formatting (Phase 2), and the braille "
                "instrument (Phase 3) are not wired yet."
            ),
        }

    def accessibility_diagnostic_summary(self) -> str:
        """A short, read-only summary for Copy Diagnostic Summary.

        Reports the underlying Win32 class name so a tester can confirm the
        surface is a genuine Rich Edit control (the property JAWS keys its
        dedicated support off, and the reason the generic-window bridge failed).
        Deliberately carries NO document content.
        """
        class_name = _window_class_name(self.hwnd()) or "(unavailable)"
        return (
            "QuillRichEdit surface (Phase 0)\n"
            f"Win32 class name: {class_name}\n"
            "RTF streaming: not wired (Phase 1)\n"
            "Document content included: no"
        )


def create_richedit_rtf(wx_module: Any, parent: Any, style: int) -> Any:
    """Build the native Rich Edit surface, or a stock ``wx.TextCtrl`` fallback.

    The surface is a ``wx.TextCtrl`` with ``TE_RICH2 | TE_NOHIDESEL`` (the same
    RICHEDIT50W the default editor uses), tagged with ``surface_kind`` and a
    :class:`QuillRichEdit` wrapper on ``quill_richedit`` for later phases. Any
    failure -- including off-Windows, where TE_RICH2 is a no-op -- returns a
    plain multiline control so selecting this surface can never brick the editor.
    """
    try:
        rich_style = style | wx_module.TE_RICH2 | wx_module.TE_NOHIDESEL
        surface = wx_module.TextCtrl(parent, style=rich_style)
    except Exception:  # noqa: BLE001 - hosting is best-effort; fall back to wx
        return wx_module.TextCtrl(parent, style=style)
    # Tag the live control so editor_surface.surface_kind() reports "richedit_rtf"
    # and command code that branches plain-vs-rich treats it as a rich surface.
    try:
        surface.surface_kind = SURFACE_KIND  # type: ignore[attr-defined]
        surface.quill_richedit = QuillRichEdit(surface)  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001 - tagging is best-effort; the control still works
        pass
    return surface
