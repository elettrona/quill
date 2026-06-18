from __future__ import annotations

from quill.ui.dialog_contract import (
    apply_modal_ids,
    find_primary_focus_target,
    focus_primary_control,
    show_modal_dialog,
)


class _DialogWithIds:
    def __init__(self, result: int = 0) -> None:
        self._result = result
        self.affirmative_id: int | None = None
        self.escape_id: int | None = None

    def SetAffirmativeId(self, value: int) -> None:
        self.affirmative_id = value

    def SetEscapeId(self, value: int) -> None:
        self.escape_id = value

    def ShowModal(self) -> int:
        return self._result


class _DialogWithoutIds:
    def __init__(self, result: int = 0) -> None:
        self._result = result

    def ShowModal(self) -> int:
        return self._result


def test_apply_modal_ids_sets_supported_ids() -> None:
    dialog = _DialogWithIds()

    apply_modal_ids(dialog, affirmative_id=101, escape_id=202)

    assert dialog.affirmative_id == 101
    assert dialog.escape_id == 202


def test_apply_modal_ids_ignores_unsupported_dialogs() -> None:
    dialog = _DialogWithoutIds(result=5)

    apply_modal_ids(dialog, affirmative_id=11, escape_id=22)

    assert dialog.ShowModal() == 5


def test_show_modal_dialog_calls_accessibility_hooks_in_order() -> None:
    events: list[str] = []

    def enter_region(label: str) -> None:
        events.append(f"enter:{label}")

    def exit_region(label: str) -> None:
        events.append(f"exit:{label}")

    def announce(message: str) -> None:
        events.append(f"announce:{message}")

    def is_verbosity_speech_enabled() -> bool:
        return True

    dialog = _DialogWithIds(result=9)

    result = show_modal_dialog(
        dialog,
        "Find",
        announce=announce,
        enter_region=enter_region,
        exit_region=exit_region,
    )

    assert result == 9
    assert events == [
        "enter:Find",
        "announce:Entered Find dialog",
        "announce:Exited Find dialog",
        "exit:Find",
    ]


class _FakeControl:
    """Minimal wx-like control for focus-helper tests.

    The class name (set per-instance via ``_make_control``) drives the
    preferred-content matching, mirroring how the real helper inspects
    ``type(control).__name__``.
    """

    def __init__(
        self,
        *,
        children: list[_FakeControl] | None = None,
        focused: bool = False,
        enabled: bool = True,
        shown: bool = True,
        can_focus: bool = True,
    ) -> None:
        self._children = children or []
        self._focused = focused
        self._enabled = enabled
        self._shown = shown
        self._can_focus = can_focus

    def GetChildren(self) -> list[_FakeControl]:
        return self._children

    def HasFocus(self) -> bool:
        return self._focused

    def IsEnabled(self) -> bool:
        return self._enabled

    def IsShown(self) -> bool:
        return self._shown

    def CanAcceptFocus(self) -> bool:
        return self._can_focus

    def SetFocus(self) -> None:
        self._focused = True


def _make_control(class_name: str, **kwargs: object) -> _FakeControl:
    cls = type(class_name, (_FakeControl,), {})
    return cls(**kwargs)  # type: ignore[arg-type]


class _FakeDialog:
    def __init__(self, children: list[_FakeControl]) -> None:
        self._children = children

    def GetChildren(self) -> list[_FakeControl]:
        return self._children


def test_find_primary_focus_target_picks_first_content_control() -> None:
    static = _make_control("StaticText")
    listbox = _make_control("ListBox")
    textctrl = _make_control("TextCtrl")
    dialog = _FakeDialog([static, listbox, textctrl])

    assert find_primary_focus_target(dialog) is listbox


def test_find_primary_focus_target_returns_none_when_only_buttons() -> None:
    dialog = _FakeDialog([_make_control("StaticText"), _make_control("Button")])

    assert find_primary_focus_target(dialog) is None


def test_focus_primary_control_redirects_from_button_autopark() -> None:
    button = _make_control("Button", focused=True)
    listbox = _make_control("ListBox")
    dialog = _FakeDialog([listbox, button])

    target = focus_primary_control(dialog)

    assert target is listbox
    assert listbox.HasFocus() is True


def test_focus_primary_control_respects_explicit_content_focus() -> None:
    textctrl = _make_control("TextCtrl")
    listbox = _make_control("ListBox", focused=True)
    dialog = _FakeDialog([textctrl, listbox])

    target = focus_primary_control(dialog)

    assert target is None
    assert textctrl.HasFocus() is False
    assert listbox.HasFocus() is True


def test_focus_primary_control_honours_keep_initial_focus_optout() -> None:
    listbox = _make_control("ListBox")
    button = _make_control("Button", focused=True)
    dialog = _FakeDialog([listbox, button])
    dialog._quill_keep_initial_focus = True  # type: ignore[attr-defined]

    target = focus_primary_control(dialog)

    assert target is None
    assert listbox.HasFocus() is False
    assert button.HasFocus() is True


def test_focus_primary_control_noop_when_no_content_control() -> None:
    dialog = _FakeDialog([_make_control("StaticText"), _make_control("Button")])

    assert focus_primary_control(dialog) is None


def test_focus_primary_control_skips_disabled_or_hidden_controls() -> None:
    disabled = _make_control("ListBox", enabled=False)
    hidden = _make_control("TextCtrl", shown=False)
    usable = _make_control("ComboBox")
    dialog = _FakeDialog([disabled, hidden, usable])

    assert focus_primary_control(dialog) is usable
