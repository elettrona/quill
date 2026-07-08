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
    # Grouped radio (RadioBox with a group label) + self-describing labels
    # so the trade-off is announced on focus.
    assert 'label="Speech engine"' in src
    assert "_engine_label(" in src
    # Renders wx-free data; no engine/model logic baked into the UI.
    assert "from quill.core.speech.guided_setup import" in src


def test_guided_speech_dialog_returns_engine_and_model_selection() -> None:
    src = _src("guided_speech_dialog.py")
    # The dialog yields (engine_id, model_id) for the caller to install.
    assert "tuple[str, str] | None" in src
    assert "data.default_model(" in src  # preselects the smallest model


def test_hub_offline_speech_row_opens_the_guided_picker() -> None:
    src = _src("main_frame_speech.py")
    # The hub's offline-speech row opens the guided picker, not the bare download.
    assert '"whispercpp": self.open_guided_offline_speech' in src
    assert "def open_guided_offline_speech" in src
    assert "show_guided_speech_setup(" in src


def test_guided_install_does_engine_then_model_and_returns_to_hub() -> None:
    src = _src("main_frame_speech.py")
    assert "def _install_offline_speech" in src
    assert "def _ensure_offline_engine" in src
    assert "provider.download_model(" in src  # install engine (if needed) then model
    assert "on_ok=self.open_optional_components" in src  # returns to the hub, stays put


def test_speech_menu_consolidated_the_separate_download_items() -> None:
    src = _src("main_frame_menu.py")
    # These three moved into Download Optional Components / the guided picker.
    assert "tools.speech_offline_engine" not in src
    assert "tools.speech_engine_download" not in src
    assert "Download &FFmpeg" not in src


def test_hub_offers_mp3_support_download() -> None:
    src = _src("main_frame_speech.py")
    assert '"mp3": self.download_mp3_support' in src
    assert "def download_mp3_support" in src
    assert "install_mp3_support(" in src  # on-demand mutagen install
