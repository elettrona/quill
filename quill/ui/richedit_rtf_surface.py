"""Native Microsoft Rich Edit surface for the experimental "richedit_rtf" option.

Selected on the Experimental tab (``experimental_editor_surface = "richedit_rtf"``).
Backed by the *same* native Windows Rich Edit control QUILL already ships as its
default (``RICHEDIT50W`` from msftedit.dll, created as a ``wx.TextCtrl`` with
``TE_RICH2``). Because the inner control is that proven native control, the whole
``EditorSurface`` contract (value / caret / selection / undo / events) comes for
free and unchanged.

**Phase 0** established the surface, its ``surface_kind``, and the
:class:`QuillRichEdit` wrapper. **Phase 1 (this file)** adds the thing the
default surface cannot do through wx: real **RTF load/save** by driving the
native control's ``EM_STREAMIN`` / ``EM_STREAMOUT`` messages with an
``EDITSTREAM`` callback, over the control's own ``HWND``. That is what turns the
surface from a clone of the default into a lightweight RTF editor.

Still to come: formatting commands (``CHARFORMAT2`` / ``PARAFORMAT2``, Phase 2)
and the braille instrument (the Rich Edit TOM via ``EM_GETOLEINTERFACE`` plus
``EM_SETEDITSTYLE``, Phase 3) that will drive the fixes for the cell-2 (#616) and
dots-7-8-on-selection (#813) braille bugs on the real HWND -- not the
generic-window bridge that failed for the Scintilla surface.

Design: the byte-pump seams (:class:`_StreamInPump`, :class:`_StreamOutSink`) are
pure and unit-tested cross-platform; the ``ctypes`` Win32 glue is guarded so the
module imports everywhere, and every path falls back or raises a clear error --
selecting the surface can never brick the editor. See
``docs/planning/editor-surface-experiments.md`` §8.
"""

from __future__ import annotations

import sys
from typing import Any

SURFACE_KIND = "richedit_rtf"

# Rich Edit stream messages and format flags (Win32 richedit.h).
_WM_USER = 0x0400
_EM_STREAMIN = _WM_USER + 73
_EM_STREAMOUT = _WM_USER + 74
_SF_TEXT = 0x0001
_SF_RTF = 0x0002


class RichEditRtfError(RuntimeError):
    """A native RTF stream operation failed (bad handle, EDITSTREAM error, I/O).

    A plain ``RuntimeError`` subclass, not a ``CodedError``: this is UI-layer glue
    (``quill/ui``), outside the error-code audit's ``core``/``io``/``stability``
    scope, and the caller degrades to a clear on-screen message + the plain-text
    fallback rather than surfacing a code.
    """


class RichEditRtfUnavailableError(NotImplementedError):
    """A QuillRichEdit capability scheduled for a later phase (e.g. formatting).

    Raised by the Phase 2 formatting methods so callers get a clear, catchable
    signal rather than a silent no-op. RTF load/save no longer raise this -- they
    are implemented in Phase 1.
    """


# --------------------------------------------------------------------------- #
# Pure byte-pump seams (platform-independent, unit-tested directly)
# --------------------------------------------------------------------------- #


class _StreamInPump:
    """Hands a byte string to a Rich Edit stream in ``EM_STREAMIN`` chunks.

    The native callback asks for up to ``count`` bytes at a time and stops when a
    read returns fewer than requested (0 = EOF). Pure so the chunking logic is
    tested without a live control.
    """

    def __init__(self, data: bytes) -> None:
        self._data = bytes(data)
        self._pos = 0

    def read(self, count: int) -> bytes:
        if count <= 0:
            return b""
        chunk = self._data[self._pos : self._pos + count]
        self._pos += len(chunk)
        return chunk

    @property
    def done(self) -> bool:
        return self._pos >= len(self._data)


class _StreamOutSink:
    """Accumulates the bytes a Rich Edit control streams out via ``EM_STREAMOUT``."""

    def __init__(self) -> None:
        self._chunks: list[bytes] = []

    def write(self, chunk: bytes) -> None:
        if chunk:
            self._chunks.append(bytes(chunk))

    def getvalue(self) -> bytes:
        return b"".join(self._chunks)


# --------------------------------------------------------------------------- #
# Win32 EDITSTREAM glue (guarded so the module imports on every platform)
# --------------------------------------------------------------------------- #

_WIN32_STREAMING = False

if sys.platform == "win32":  # pragma: no cover - exercised only on Windows with a real HWND
    try:
        import ctypes
        from ctypes import wintypes

        # DWORD CALLBACK EditStreamCallback(DWORD_PTR cookie, LPBYTE buf, LONG cb, LONG *pcb)
        _EDITSTREAMCALLBACK = ctypes.WINFUNCTYPE(
            wintypes.DWORD,
            ctypes.c_size_t,  # DWORD_PTR dwCookie (pointer-sized; unused, we close over state)
            ctypes.POINTER(ctypes.c_byte),  # LPBYTE pbBuff
            wintypes.LONG,  # LONG cb (buffer size on in, bytes available on out)
            ctypes.POINTER(wintypes.LONG),  # LONG *pcb (bytes actually read/written)
        )

        class _EDITSTREAM(ctypes.Structure):
            _fields_ = (
                ("dwCookie", ctypes.c_size_t),
                ("dwError", wintypes.DWORD),
                ("pfnCallback", _EDITSTREAMCALLBACK),
            )

        _SendMessageW = ctypes.windll.user32.SendMessageW
        _SendMessageW.argtypes = (
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,  # lParam is an EDITSTREAM* here (passed as its address)
        )
        _SendMessageW.restype = ctypes.c_ssize_t  # LRESULT
        _WIN32_STREAMING = True
    except Exception:  # noqa: BLE001 - any setup failure disables native streaming
        _WIN32_STREAMING = False


# ------------------------------------------------------------------------- #
# On-device finding (2026-07-08): the ctypes EDITSTREAM callback approach below
# HARD-CRASHES msftedit.dll (RICHEDIT50W) with an access violation the moment the
# control invokes the callback -- reproduced for EM_STREAMOUT *and* EM_STREAMIN,
# SF_TEXT *and* SF_RTF, on a wx.TextCtrl(TE_RICH2) *and* a raw CreateWindowExW
# RICHEDIT50W, shown or not, with WINFUNCTYPE *and* CFUNCTYPE. The thunk is
# provably valid (callable directly from Python; the EDITSTREAM struct holds the
# correct 24-byte layout and callback address), and ctypes callbacks work here
# with other guarded system APIs (EnumWindows visits 746 windows fine) -- so this
# is specific to msftedit's EM_STREAM dispatch, not a general callback problem.
# Conclusion: pure-ctypes EM_STREAM is not viable; native RTF I/O needs the
# callback to live in compiled C -- a small native helper .pyd (the
# _quill_table_uia precedent, scripts/build_table_uia.py) -- or the TOM
# ITextDocument::Save/Open path (file/IStream based, no Python callback). Until
# one of those lands, streaming is GATED OFF so it can never crash QUILL. The
# _stream_in/_stream_out below are kept as the reference implementation for the
# native-helper port. See docs/planning/editor-surface-experiments.md §8.
_NATIVE_STREAM_CALLBACK_BLOCKED = True
_STREAM_BLOCKED_MESSAGE = (
    "Native RTF streaming is not available yet: the EM_STREAMIN/EM_STREAMOUT "
    "ctypes callback crashes the native Rich Edit control (msftedit), so it is "
    "disabled pending a compiled-C helper. See the QuillRichEdit Phase 1 notes."
)


def _stream_in(hwnd: int, data: bytes, fmt: int) -> None:
    """Push *data* into the Rich Edit *hwnd* via EM_STREAMIN (replaces content).

    Reference implementation only -- see _NATIVE_STREAM_CALLBACK_BLOCKED above;
    this path is gated off because it crashes msftedit from a ctypes callback.
    """
    if not (_WIN32_STREAMING and hwnd):
        raise RichEditRtfError("Native RTF streaming is unavailable on this control.")
    pump = _StreamInPump(data)

    def _callback(_cookie: int, buf: Any, cb: int, pcb: Any) -> int:
        try:
            chunk = pump.read(int(cb))
            if chunk:
                ctypes.memmove(buf, chunk, len(chunk))
            pcb[0] = len(chunk)
            return 0
        except Exception:  # noqa: BLE001 - signal the control to stop, don't crash it
            return 1

    callback = _EDITSTREAMCALLBACK(_callback)
    stream = _EDITSTREAM(0, 0, callback)
    _SendMessageW(hwnd, _EM_STREAMIN, fmt, ctypes.addressof(stream))
    if stream.dwError:
        raise RichEditRtfError(f"EM_STREAMIN failed (dwError={stream.dwError}).")


def _stream_out(hwnd: int, fmt: int) -> bytes:
    """Read the whole document out of Rich Edit *hwnd* via EM_STREAMOUT."""
    if not (_WIN32_STREAMING and hwnd):
        raise RichEditRtfError("Native RTF streaming is unavailable on this control.")
    sink = _StreamOutSink()

    def _callback(_cookie: int, buf: Any, cb: int, pcb: Any) -> int:
        try:
            count = int(cb)
            if count > 0:
                sink.write(ctypes.string_at(buf, count))
            pcb[0] = count
            return 0
        except Exception:  # noqa: BLE001 - stop the stream cleanly
            return 1

    callback = _EDITSTREAMCALLBACK(_callback)
    stream = _EDITSTREAM(0, 0, callback)
    _SendMessageW(hwnd, _EM_STREAMOUT, fmt, ctypes.addressof(stream))
    if stream.dwError:
        raise RichEditRtfError(f"EM_STREAMOUT failed (dwError={stream.dwError}).")
    return sink.getvalue()


def _window_class_name(hwnd: int) -> str:
    """Best-effort Win32 window class name for *hwnd* (empty off-Windows/failure).

    Read-only and content-free: confirms the surface is a genuine Rich Edit
    control (``RICHEDIT50W``) -- the distinction that made the generic-window
    Scintilla bridge fail for JAWS.
    """
    if sys.platform != "win32" or not hwnd:
        return ""
    try:
        buffer = ctypes.create_unicode_buffer(256)
        length = ctypes.windll.user32.GetClassNameW(int(hwnd), buffer, 256)
        return buffer.value if length else ""
    except Exception:  # noqa: BLE001 - diagnostics must never raise
        return ""


class QuillRichEdit:
    """Thin, replaceable wrapper API over the native Rich Edit control.

    Phase 1 implemented native RTF load/save over ``EM_STREAMIN``/``EM_STREAMOUT``,
    but on-device testing found the ctypes EDITSTREAM callback hard-crashes
    msftedit (see ``_NATIVE_STREAM_CALLBACK_BLOCKED``). So RTF I/O is **gated off**
    -- ``get_rtf``/``set_rtf``/``load_rtf``/``save_rtf`` raise a clear
    :class:`RichEditRtfUnavailableError` instead of crashing, pending a compiled-C
    helper or the TOM path. ``get_plain_text`` returns the control's plain value
    so QUILL's offset-anchored features (search, spell, AI, read aloud, braille)
    keep working unchanged. ``surface`` is the live ``wx.TextCtrl`` (TE_RICH2).
    """

    def __init__(self, surface: Any) -> None:
        self._surface = surface

    # -- identity / handle -------------------------------------------------- #

    def hwnd(self) -> int:
        try:
            return int(self._surface.GetHandle())
        except Exception:  # noqa: BLE001 - handle access is best-effort
            return 0

    def rtf_streaming_available(self) -> bool:
        """True when native RTF load/save can actually run.

        False while ``_NATIVE_STREAM_CALLBACK_BLOCKED`` -- the ctypes EDITSTREAM
        callback crashes msftedit, so streaming is gated off even though the
        Windows glue and a real HWND are present.
        """
        return bool(_WIN32_STREAMING and self.hwnd() and not _NATIVE_STREAM_CALLBACK_BLOCKED)

    # -- RTF I/O (implemented, but gated off pending a safe callback) -------- #

    def get_rtf(self) -> bytes:
        """Return the document as RTF bytes (EM_STREAMOUT) -- gated off, see notes."""
        if not self.rtf_streaming_available():
            raise RichEditRtfUnavailableError(_STREAM_BLOCKED_MESSAGE)
        return _stream_out(self.hwnd(), _SF_RTF)  # reference path; unreached while blocked

    def set_rtf(self, data: bytes) -> None:
        """Replace the document with RTF bytes (EM_STREAMIN) -- gated off, see notes."""
        if not self.rtf_streaming_available():
            raise RichEditRtfUnavailableError(_STREAM_BLOCKED_MESSAGE)
        _stream_in(self.hwnd(), data, _SF_RTF)  # reference path; unreached while blocked

    def load_rtf(self, path: str) -> None:
        """Load an RTF file into the control via native streaming."""
        try:
            with open(path, "rb") as handle:
                data = handle.read()
        except OSError as exc:
            raise RichEditRtfError(f"Could not read RTF file: {exc}") from exc
        self.set_rtf(data)

    def save_rtf(self, path: str) -> None:
        """Save the control's content to an RTF file via native streaming."""
        data = self.get_rtf()
        try:
            with open(path, "wb") as handle:
                handle.write(data)
        except OSError as exc:
            raise RichEditRtfError(f"Could not write RTF file: {exc}") from exc

    def get_plain_text(self) -> str:
        """The control's plain text -- what search/spell/AI/read-aloud consume."""
        try:
            return str(self._surface.GetValue())
        except Exception:  # noqa: BLE001 - never break the plain-text contract
            return ""

    # -- formatting (Phase 2 -- not yet wired) ------------------------------ #

    def apply_bold(self) -> None:
        raise RichEditRtfUnavailableError(
            "Formatting commands (CHARFORMAT2) land in Phase 2 of the QuillRichEdit surface."
        )

    # -- reporting ---------------------------------------------------------- #

    def capabilities(self) -> dict[str, Any]:
        """A wx-free report of what this surface can do right now (honest by rule)."""
        rtf = self.rtf_streaming_available()
        return {
            "surface_kind": SURFACE_KIND,
            "phase": 1,
            "native_control": True,
            "rtf_load": rtf,
            "rtf_save": rtf,
            "formatting_commands": False,
            "notes": (
                "Native Windows Rich Edit (RICHEDIT50W). RTF load/save is "
                "implemented over EM_STREAMIN/EM_STREAMOUT but GATED OFF: the "
                "ctypes EDITSTREAM callback crashes msftedit, so it awaits a "
                "compiled-C helper (or the TOM ITextDocument path). Formatting "
                "and the braille instrument are later phases."
            ),
        }

    def self_test_rtf_roundtrip(self) -> tuple[bool, str]:
        """Push a known RTF snippet in and read it back -- a tester's one-click check.

        Verifiable on the device (this environment has no real HWND). Returns
        ``(ok, detail)`` and never raises, so it is safe to wire to a menu/hotkey.
        """
        sample = (
            rb"{\rtf1\ansi\deff0{\fonttbl{\f0 Segoe UI;}}"
            rb"\f0 QuillRichEdit round-trip test.\par}"
        )
        try:
            self.set_rtf(sample)
            out = self.get_rtf()
            text = self.get_plain_text()
            ok = "round-trip test" in text
            return ok, (
                f"RTF set/get {'OK' if ok else 'MISMATCH'}: read back "
                f"{len(out)} RTF bytes; plain text = {text.strip()!r}"
            )
        except Exception as exc:  # noqa: BLE001 - a self-test must report, not raise
            return False, f"RTF round-trip failed: {exc}"

    def _rtf_out_probe(self) -> str:
        """A safe, read-only EM_STREAMOUT check for the diagnostic (no content).

        Streams the current document out as RTF and reports only its size and
        whether it carries the RTF signature -- enough to confirm EM_STREAMOUT
        works on the device, with zero document text included and no mutation.
        """
        if not self.rtf_streaming_available():
            if _NATIVE_STREAM_CALLBACK_BLOCKED:
                return "gated off (EDITSTREAM callback crashes msftedit; awaiting native helper)"
            return "not run (no native handle)"
        try:
            data = self.get_rtf()
        except (RichEditRtfError, RichEditRtfUnavailableError) as exc:
            return f"failed ({exc})"
        signed = data[:6].startswith(b"{\\rtf")
        return f"{len(data)} bytes, RTF signature: {'yes' if signed else 'no'}"

    def accessibility_diagnostic_summary(self) -> str:
        """A short, read-only summary for Copy Diagnostic Summary (no document content)."""
        class_name = _window_class_name(self.hwnd()) or "(unavailable)"
        return (
            "QuillRichEdit surface (Phase 1)\n"
            f"Win32 class name: {class_name}\n"
            f"RTF streaming: {'available' if self.rtf_streaming_available() else 'unavailable'}\n"
            f"RTF stream-out probe: {self._rtf_out_probe()}\n"
            "Document content included: no"
        )


def create_richedit_rtf(wx_module: Any, parent: Any, style: int) -> Any:
    """Build the native Rich Edit surface, or a stock ``wx.TextCtrl`` fallback.

    The surface is a ``wx.TextCtrl`` with ``TE_RICH2 | TE_NOHIDESEL`` (the same
    RICHEDIT50W the default editor uses), tagged with ``surface_kind`` and a
    :class:`QuillRichEdit` wrapper on ``quill_richedit`` for RTF I/O + later
    phases. Any failure -- including off-Windows, where TE_RICH2 is a no-op --
    returns a plain multiline control so selecting this surface can never brick
    the editor.
    """
    try:
        rich_style = style | wx_module.TE_RICH2 | wx_module.TE_NOHIDESEL
        surface = wx_module.TextCtrl(parent, style=rich_style)
    except Exception:  # noqa: BLE001 - hosting is best-effort; fall back to wx
        return wx_module.TextCtrl(parent, style=style)
    try:
        surface.surface_kind = SURFACE_KIND  # type: ignore[attr-defined]
        surface.quill_richedit = QuillRichEdit(surface)  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001 - tagging is best-effort; the control still works
        pass
    return surface
