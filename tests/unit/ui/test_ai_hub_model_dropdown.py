"""AI Hub Provider tab: the Model field is an editable dropdown, not a text box.

The Hub used a bare text field for the model while the Setup Wizard offered a
combo with recommended (now free-first) suggestions and a model list. These tests
pin the control type at the source level and exercise the pure populate/list
helpers on a light stub (no full wx dialog needed).
"""

from __future__ import annotations

import re
from pathlib import Path

from quill.ui.ai_hub_dialog import AIHubDialog


def _hub_source() -> str:
    ui = Path(__file__).resolve().parents[3] / "quill" / "ui"
    return (ui / "ai_hub_dialog.py").read_text(encoding="utf-8")


def test_model_control_is_a_combobox() -> None:
    src = _hub_source()
    assert re.search(r"self\._model_ctrl\s*=\s*wx\.ComboBox\(", src), (
        "AI Hub Model field must be an editable wx.ComboBox, not a TextCtrl"
    )


class _FakeCombo:
    def __init__(self) -> None:
        self._items: list[str] = []
        self._value = ""

    def Set(self, items: list[str]) -> None:
        self._items = list(items)

    def SetValue(self, value: str) -> None:
        self._value = value

    def GetValue(self) -> str:
        return self._value

    def GetStrings(self) -> list[str]:
        return list(self._items)


class _FakeLabel:
    def __init__(self) -> None:
        self.text = ""

    def SetLabel(self, text: str) -> None:
        self.text = text


class _FakeButton:
    def __init__(self) -> None:
        self.enabled = True

    def Enable(self, value: bool) -> None:
        self.enabled = value


class _Stub:
    def __init__(self) -> None:
        self._model_ctrl = _FakeCombo()
        self._test_label = _FakeLabel()
        self._list_models_btn = _FakeButton()


def test_populate_hub_models_prefers_free_for_openrouter() -> None:
    from quill.core.ai.free_models import best_free_writing_model

    stub = _Stub()
    AIHubDialog._populate_hub_models(stub, "openrouter")
    assert stub._model_ctrl.GetValue() == best_free_writing_model("openrouter")
    assert stub._model_ctrl.GetValue().endswith(":free")


def test_populate_hub_models_keeps_explicit_selection() -> None:
    stub = _Stub()
    AIHubDialog._populate_hub_models(stub, "openai", select="gpt-4.1")
    assert stub._model_ctrl.GetValue() == "gpt-4.1"


def test_hub_models_listed_loads_and_selects() -> None:
    stub = _Stub()
    AIHubDialog._on_hub_models_listed(stub, ["a", "b", "c"], "")
    assert stub._model_ctrl.GetStrings() == ["a", "b", "c"]
    assert stub._model_ctrl.GetValue() == "a"
    assert stub._list_models_btn.enabled is True
    assert "3 models" in stub._test_label.text


def test_hub_models_listed_surfaces_error() -> None:
    stub = _Stub()
    AIHubDialog._on_hub_models_listed(stub, [], "connection refused")
    assert "refused" in stub._test_label.text
    assert stub._list_models_btn.enabled is True
