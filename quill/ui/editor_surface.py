"""The editor-surface protocol (rtf.md Part One, Stage 1).

QUILL's main frame talks to its editor through a small, duck-typed surface. The
default plain-text surface is a stock ``wx.TextCtrl``; alternative surfaces
(``CsvGridSurface``, ``WordDocumentSurface`` and now ``RichTextSurface``) wrap
other controls and expose the same shape so the rest of ``main_frame`` does not
care which control is active.

This module makes that contract explicit. It is deliberately thin: it documents the
methods the application relies on as a :class:`~typing.Protocol`, and offers
:func:`surface_kind` so command code can branch on the active surface when a
formatting command genuinely means something different on a rich surface than on a
plain one. It does **not** force a refactor of the existing controls; a plain
``wx.TextCtrl`` already satisfies the protocol, and the wrappers add the optional
``bind_editor_events`` / ``surface_kind`` hooks.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["EditorSurface", "surface_kind", "PLAIN", "RICH"]

PLAIN = "plain"
RICH = "rich"


@runtime_checkable
class EditorSurface(Protocol):
    """The contract every editor control in the writing path satisfies.

    These are the members ``main_frame`` calls on ``self.editor``. A stock
    ``wx.TextCtrl`` provides all of them natively; wrappers implement them over
    their inner control. Optional members (``bind_editor_events``, ``surface_kind``,
    ``caret_format_description``) are detected with ``getattr`` and are not required.
    """

    def GetValue(self) -> str:  # noqa: N802 - wx naming
        """Return the canonical document text (QUILL markup)."""

    def ChangeValue(self, value: str) -> None:  # noqa: N802
        """Replace the document text without firing a change event."""

    def GetInsertionPoint(self) -> int:  # noqa: N802
        ...

    def SetInsertionPoint(self, position: int) -> None:  # noqa: N802
        ...

    def GetSelection(self) -> tuple[int, int]:  # noqa: N802
        ...

    def SetSelection(self, start: int, end: int) -> None:  # noqa: N802
        ...

    def SetFocus(self) -> None:  # noqa: N802
        ...


def surface_kind(editor: object) -> str:
    """Return the kind of an editor surface: ``"plain"``, ``"rich"`` or other.

    A surface may advertise its kind via a ``surface_kind`` attribute (string) or a
    ``surface_kind()`` method. Anything that does not is treated as the default
    plain-text surface, so existing ``wx.TextCtrl`` editors report ``"plain"``.
    """
    advertised = getattr(editor, "surface_kind", None)
    if callable(advertised):
        try:
            value = advertised()
        except TypeError:
            value = None
        if isinstance(value, str) and value:
            return value
    if isinstance(advertised, str) and advertised:
        return advertised
    return PLAIN
