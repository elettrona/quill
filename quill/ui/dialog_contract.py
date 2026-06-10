from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence

# Control classes that should receive initial keyboard focus when a custom
# dialog opens, in priority order. These are the "content" controls a user came
# to interact with — lists, trees, text fields, choices. Buttons (OK/Cancel)
# are deliberately excluded: a dialog that focuses its OK button on open hides
# the actual content from screen-reader and keyboard users, who then cannot tell
# what the dialog is for without hunting with Tab. Progress gauges and static
# text are excluded because they are not interactive.
_PREFERRED_FOCUS_CLASSES: tuple[str, ...] = (
    "CheckListBox",
    "ListBox",
    "ListCtrl",
    "ListView",
    "TreeCtrl",
    "TreeListCtrl",
    "DataViewCtrl",
    "DataViewListCtrl",
    "DataViewTreeCtrl",
    "EditableListBox",
    "TextCtrl",
    "SearchCtrl",
    "ComboBox",
    "BitmapComboBox",
    "Choice",
    "SpinCtrl",
    "SpinCtrlDouble",
    "RadioBox",
    "CheckBox",
    "Slider",
)


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


def _iter_descendant_controls(widget: object) -> Iterable[object]:
    """Yield a widget's descendants in creation (tab) order, depth-first."""
    get_children = getattr(widget, "GetChildren", None)
    if not callable(get_children):
        return
    try:
        children = list(get_children())
    except Exception:
        return
    for child in children:
        yield child
        yield from _iter_descendant_controls(child)


def _is_focusable(control: object) -> bool:
    is_enabled = getattr(control, "IsEnabled", None)
    is_shown = getattr(control, "IsShown", None)
    can_focus = getattr(control, "CanAcceptFocus", None)
    try:
        if callable(is_enabled) and not is_enabled():
            return False
        if callable(is_shown) and not is_shown():
            return False
        if callable(can_focus) and not can_focus():
            return False
    except Exception:
        return False
    return callable(getattr(control, "SetFocus", None))


def _has_explicit_focus(dialog: object) -> bool:
    """Return True if a *content* control already holds focus, or the dialog
    opted out of auto-focus.

    A construction-time ``content.SetFocus()`` is reflected by ``HasFocus()``
    even before the dialog is shown, so honouring it lets dialogs that
    deliberately target a specific field keep their intended initial focus.
    A focused *button*, by contrast, is the platform's default auto-park (the
    very bug this helper fixes) and is therefore not treated as explicit.

    A dialog may force its initial focus to be kept — even on a button — by
    setting a truthy ``_quill_keep_initial_focus`` attribute (used by the rare
    dialog whose primary action button should hold focus, e.g. crash recovery).
    """
    if getattr(dialog, "_quill_keep_initial_focus", False):
        return True
    preferred_set = set(_PREFERRED_FOCUS_CLASSES)
    for control in _iter_descendant_controls(dialog):
        has_focus = getattr(control, "HasFocus", None)
        if not callable(has_focus):
            continue
        try:
            focused = has_focus()
        except Exception:
            continue
        if focused and type(control).__name__ in preferred_set:
            return True
    return False


def find_primary_focus_target(
    dialog: object,
    *,
    preferred: Sequence[str] = _PREFERRED_FOCUS_CLASSES,
) -> object | None:
    """Return the first preferred, focusable content control inside *dialog*.

    Walks the dialog's descendants in tab order and returns the first control
    whose class name matches *preferred* and that can currently accept focus.
    Returns ``None`` when no such control exists (e.g. a button-only dialog),
    leaving the platform's default focus untouched.
    """
    preferred_set = set(preferred)
    for control in _iter_descendant_controls(dialog):
        if type(control).__name__ in preferred_set and _is_focusable(control):
            return control
    return None


def focus_primary_control(
    dialog: object,
    *,
    preferred: Sequence[str] = _PREFERRED_FOCUS_CLASSES,
) -> object | None:
    """Move initial focus to the dialog's first content control, if any.

    Honours an explicit initial focus already set during construction (so
    dialogs that deliberately target a specific control are left untouched).
    Otherwise moves focus to the first content control, keeping custom dialogs
    from opening with focus parked on their OK button — which hides the
    dialog's purpose from keyboard and screen-reader users. Idempotent and
    side-effect-free when no suitable control is found.
    """
    if _has_explicit_focus(dialog):
        return None
    target = find_primary_focus_target(dialog, preferred=preferred)
    if target is None:
        return None
    set_focus = getattr(target, "SetFocus", None)
    if callable(set_focus):
        try:
            set_focus()
        except Exception:
            return None
    return target


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


def show_message_box(
    message: str,
    caption: str,
    style: int,
    parent: object = None,
    *,
    announce: Callable[[str], None] | None = None,
) -> int:
    """Show a wx.MessageBox with enter/exit announcements.

    Drop-in replacement for raw ``wx.MessageBox`` calls that ensures screen
    readers hear a region-entry cue before the dialog appears and an exit cue
    after it closes.
    """
    import wx

    if announce is not None:
        announce(f"Entered {caption} dialog")
    try:
        result = wx.MessageBox(message, caption, style, parent)
    finally:
        if announce is not None:
            announce(f"Exited {caption} dialog")
    return result
