"""Tweak the Windows RichEdit control that backs the editor.

QUILL's editor is a RichEdit (``TE_RICH2`` / ``TE_RICH``) rather than a plain
EDIT control, because a plain multiline control reports a broken accessible value
to screen readers on Windows (#616). RichEdit, however, ships with a small
internal left/right margin. On a braille display some screen readers — notably
JAWS, which drives RichEdit through the same rich-document path it used for
Microsoft Word — mirror that gutter as a leading blank cell, so a line's first
character lands in cell two instead of cell one.

:func:`zero_richedit_margins` removes that internal gutter via ``EM_SETMARGINS``.
It is Windows-only and defensive: any failure (non-Windows, missing handle, API
quirk) is a silent no-op that returns ``False`` so editor creation never breaks.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

#: EM_SETMARGINS and its flags (winuser.h). lParam 0 sets a literal zero margin
#: (as opposed to ``EC_USEFONTINFO`` = 0xFFFF, which asks the font to decide).
_EM_SETMARGINS = 0x00D3
_EC_LEFTMARGIN = 0x0001
_EC_RIGHTMARGIN = 0x0002


def zero_richedit_margins(hwnd: int | None) -> bool:
    """Set the RichEdit ``hwnd``'s left and right inner margins to zero.

    Returns ``True`` when the message was sent, ``False`` on any guard
    (falsy handle, non-Windows, or an unexpected ctypes failure).
    """
    if not hwnd:
        return False
    try:
        user32 = ctypes.windll.user32  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        return False
    try:
        send = user32.SendMessageW
        send.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        send.restype = wintypes.LPARAM
        send(hwnd, _EM_SETMARGINS, _EC_LEFTMARGIN | _EC_RIGHTMARGIN, 0)
    except Exception:
        return False
    return True
