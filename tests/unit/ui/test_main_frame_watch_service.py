from __future__ import annotations

from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[3] / "quill" / "ui" / "main_frame.py").read_text(
    encoding="utf-8"
)


def test_main_frame_uses_watch_service_not_legacy_watcher() -> None:
    assert "from quill.core.watch_service import WatchService" in SOURCE
    assert "self._watch_service = WatchService(" in SOURCE
    # The legacy single-folder watcher must be fully removed.
    assert "WatchFolderService" not in SOURCE
    assert "WatchFolderConfig" not in SOURCE
    assert "_watch_folder_config" not in SOURCE


def test_watch_service_wiring_passes_engine_callbacks() -> None:
    assert "on_open=lambda path: self._wx.CallAfter(self._on_watch_file_opened, path)" in SOURCE
    assert "queue_listener=lambda event, item: self._wx.CallAfter(" in SOURCE
    assert "def _on_watch_file_opened(self, path: Path) -> None:" in SOURCE
    assert "def _on_watch_queue_event(self, event: str, item: object) -> None:" in SOURCE


def test_apply_watch_folder_menu_state_uses_service_running() -> None:
    # Method name preserved for accessibility tests that monkeypatch it.
    assert "def _apply_watch_folder_menu_state(self) -> None:" in SOURCE
    assert "item.Check(self._watch_service.is_running)" in SOURCE


def test_watch_profile_manager_dialog_is_accessible() -> None:
    assert "def open_watch_folder_settings(self) -> None:" in SOURCE
    assert 'title="Watch Folder Profiles"' in SOURCE
    assert "panel = wx.Panel(dialog)" in SOURCE
    assert 'listbox.SetName("Watch folder profile list")' in SOURCE
    assert "def _edit_watch_profile(self, profile: WatchProfile | None)" in SOURCE


def test_watch_queue_monitor_dialog_is_accessible() -> None:
    assert "def show_watch_folder_status(self) -> None:" in SOURCE
    assert 'title="Watch Queue Monitor"' in SOURCE
    assert "def _refresh_watch_queue_monitor(self) -> None:" in SOURCE
    assert "self._watch_service.retry_item(item.item_id)" in SOURCE
    assert "self._watch_service.clear_finished()" in SOURCE


def test_watch_profile_editor_uses_registry_actions() -> None:
    assert "self._watch_service.registry.available_actions()" in SOURCE
    assert 'action_options["destination"] = destination' in SOURCE
    assert "post_values = [POST_LEAVE, POST_MOVE, POST_DELETE]" in SOURCE
