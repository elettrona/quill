from __future__ import annotations

from quill.ui.dialog_contract import apply_modal_ids, show_modal_dialog


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
