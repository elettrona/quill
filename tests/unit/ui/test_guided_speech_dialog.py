from __future__ import annotations

from pathlib import Path

_UI = Path(__file__).resolve().parents[3] / "quill" / "ui"


def _src(name: str) -> str:
    return (_UI / name).read_text(encoding="utf-8")


def test_guided_speech_dialog_follows_contract_and_is_accessible() -> None:
    src = _src("guided_speech_dialog.py")
    # Dialog contract: modal ids + affirmative/escape.
    assert "apply_modal_ids(" in src
    assert "wx.ID_OK" in src and "wx.ID_CANCEL" in src
    # Accessible engine choice (RadioBox) + model list, not free-form widgets.
    assert "wx.RadioBox(" in src
    assert "wx.ListBox(" in src
    # Focus lands on a real control, never a button (screen-reader contract).
    assert "engine_box.SetFocus()" in src
    # Renders wx-free data; no engine/model logic baked into the UI.
    assert "from quill.core.speech.guided_setup import" in src


def test_guided_speech_dialog_returns_engine_and_model_selection() -> None:
    src = _src("guided_speech_dialog.py")
    # The dialog yields (engine_id, model_id) for the caller to install.
    assert "tuple[str, str] | None" in src
    assert "data.default_model(" in src  # preselects the smallest model
