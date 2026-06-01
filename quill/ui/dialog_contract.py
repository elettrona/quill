from __future__ import annotations

from collections.abc import Callable


def apply_modal_ids(
    dialog: object,
    *,
    affirmative_id: int | None = None,
    escape_id: int | None = None,
) -> None:
    """Apply modal affirmative/escape ids when supported by the dialog."""
    if affirmative_id is not None and hasattr(dialog, "SetAffirmativeId"):
        dialog.SetAffirmativeId(affirmative_id)
    if escape_id is not None and hasattr(dialog, "SetEscapeId"):
        dialog.SetEscapeId(escape_id)


def show_modal_dialog(
    dialog: object,
    label: str,
    *,
    announce: Callable[[str], None] | None = None,
    enter_region: Callable[[str], None] | None = None,
    exit_region: Callable[[str], None] | None = None,
) -> int:
    """Show a modal dialog with optional region and announcement hooks."""
    if enter_region is not None:
        enter_region(label)
    if announce is not None:
        announce(f"Entered {label} dialog")
    try:
        result = dialog.ShowModal()
    finally:
        if announce is not None:
            announce(f"Exited {label} dialog")
        if exit_region is not None:
            exit_region(label)
    return result