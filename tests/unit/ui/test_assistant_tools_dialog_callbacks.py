from __future__ import annotations

from types import SimpleNamespace

from quill.ui.assistant_tools import AgentCenterDialog, PromptStudioDialog


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
