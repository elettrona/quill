from __future__ import annotations

from types import SimpleNamespace

from quill.core.accessibility_agent import build_plan
from quill.ui.assistant_tools import (
    AccessibilityAgentDialog,
    AgentCenterDialog,
    PromptStudioDialog,
)


class _TextCtrl:
    def __init__(self, value: str) -> None:
        self._value = value

    def GetValue(self) -> str:
        return self._value


class _Status:
    def __init__(self) -> None:
        self.label = ""

    def SetLabel(self, value: str) -> None:
        self.label = value


class _Dialog:
    def __init__(self) -> None:
        self.ended_with: int | None = None

    def EndModal(self, result: int) -> None:
        self.ended_with = result


def test_prompt_studio_use_prompt_routes_to_callback() -> None:
    used: list[str] = []
    announcements: list[str] = []

    dialog = PromptStudioDialog.__new__(PromptStudioDialog)
    dialog._wx = SimpleNamespace(ID_OK=1)
    dialog.template_text = _TextCtrl("Rewrite: {selection}")
    dialog.status = _Status()
    dialog._render_prompt = lambda template: template.replace("{selection}", "alpha")
    dialog._use_prompt_callback = lambda value: used.append(value)
    dialog._announce = lambda message: announcements.append(message)
    dialog.dialog = _Dialog()

    dialog._on_use_prompt_clicked(object())

    assert used == ["Rewrite: alpha"]
    assert announcements == ["Loaded prompt into Writing Assistant"]
    assert dialog.dialog.ended_with == 1


def test_agent_center_use_prompt_generates_then_routes_to_callback() -> None:
    used: list[str] = []
    announcements: list[str] = []

    dialog = AgentCenterDialog.__new__(AgentCenterDialog)
    dialog._wx = SimpleNamespace(ID_OK=1)
    dialog._current_prompt = ""
    dialog.status = _Status()
    dialog.dialog = _Dialog()
    dialog._announce = lambda message: announcements.append(message)
    dialog._use_prompt_callback = lambda value: used.append(value)
    dialog._on_generate_prompt = lambda _event: setattr(dialog, "_current_prompt", "Generated")

    dialog._on_use_prompt_clicked(object())

    assert used == ["Generated"]
    assert announcements == ["Loaded agent prompt into Writing Assistant"]
    assert dialog.dialog.ended_with == 1


class _CheckListBox:
    def __init__(self, checked: set[int]) -> None:
        self._checked = checked

    def IsChecked(self, index: int) -> bool:
        return index in self._checked


def _make_accessibility_dialog(
    text: str, checked: set[int]
) -> tuple[AccessibilityAgentDialog, list, list[str]]:
    plan = build_plan("doc.md", text, "markdown", "current document")
    dialog = AccessibilityAgentDialog.__new__(AccessibilityAgentDialog)
    dialog._wx = SimpleNamespace(ID_OK=1)
    dialog.plan = plan
    dialog._document_text = text
    dialog.applied = False
    dialog.status = _Status()
    dialog.dialog = _Dialog()
    dialog.step_list = _CheckListBox(checked)
    applied: list = []
    announcements: list[str] = []
    dialog._on_apply = lambda result: applied.append(result)
    dialog._announce = lambda message: announcements.append(message)
    return dialog, applied, announcements


def test_accessibility_agent_apply_routes_checked_steps() -> None:
    text = "#Title\nUtilize the tool in order to begin.\n"
    dialog, applied, announcements = _make_accessibility_dialog(text, checked=set(range(len(text))))

    dialog._on_apply_clicked(object())

    assert dialog.applied is True
    assert len(applied) == 1
    assert applied[0].changed is True
    assert applied[0].text != text
    assert dialog.dialog.ended_with == 1
    assert announcements and "applied" in announcements[0]


def test_accessibility_agent_apply_with_nothing_checked_makes_no_change() -> None:
    text = "#Title\nUtilize the tool in order to begin.\n"
    dialog, applied, announcements = _make_accessibility_dialog(text, checked=set())

    dialog._on_apply_clicked(object())

    assert dialog.applied is False
    assert applied == []
    assert dialog.dialog.ended_with is None
    assert announcements and "no automatic changes" in announcements[0].lower()
