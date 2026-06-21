from __future__ import annotations

from pathlib import Path

import pytest

from quill.core import data_location, storage_mode
from quill.core.paths import app_data_dir


@pytest.fixture
def current_data_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """The data dir app_data_dir() resolves to by default (mode unset).

    Deliberately does NOT use QUILL_DATA_DIR: that dev override short-
    circuits app_data_dir() before it ever consults storage_mode, which
    would make it impossible to observe a storage-mode-driven move.
    """
    monkeypatch.delenv("QUILL_DATA_DIR", raising=False)
    monkeypatch.delenv("QUILL_APP_ROOT", raising=False)
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    current = tmp_path / "appdata" / "Quill"
    current.mkdir(parents=True)
    return current


def test_request_change_to_current_location_saves_immediately_with_no_marker(
    current_data_dir: Path,
) -> None:
    target = data_location.request_data_location_change("appdata")
    assert target == current_data_dir.resolve()
    assert storage_mode.load_storage_mode() == "appdata"
    assert not (current_data_dir / "pending-data-location.json").exists()


def test_request_change_to_new_location_queues_a_marker_without_moving_anything(
    current_data_dir: Path, tmp_path: Path
) -> None:
    (current_data_dir / "settings.json").write_text("{}", encoding="utf-8")
    new_location = tmp_path / "new-data-home"

    target = data_location.request_data_location_change("custom", new_location)

    assert target == new_location.resolve()
    # Nothing moved yet -- only applied on next launch.
    assert (current_data_dir / "settings.json").exists()
    assert not new_location.exists() or not any(new_location.iterdir())
    marker = current_data_dir / "pending-data-location.json"
    assert marker.exists()


def test_apply_pending_migration_moves_files_and_updates_storage_mode(
    current_data_dir: Path, tmp_path: Path
) -> None:
    (current_data_dir / "settings.json").write_text('{"theme": "dark"}', encoding="utf-8")
    (current_data_dir / "logs").mkdir()
    (current_data_dir / "logs" / "quill.log").write_text("hello", encoding="utf-8")
    new_location = tmp_path / "new-data-home"

    data_location.request_data_location_change("custom", new_location)
    data_location.apply_pending_data_location_migration()

    assert (new_location / "settings.json").read_text(encoding="utf-8") == '{"theme": "dark"}'
    assert (new_location / "logs" / "quill.log").read_text(encoding="utf-8") == "hello"
    assert storage_mode.load_storage_mode() == "custom"
    assert storage_mode.custom_path() == new_location.resolve()
    assert app_data_dir() == new_location.resolve()


def test_apply_pending_migration_writes_a_success_notice_at_the_new_location(
    current_data_dir: Path, tmp_path: Path
) -> None:
    new_location = tmp_path / "new-data-home"
    data_location.request_data_location_change("custom", new_location)
    data_location.apply_pending_data_location_migration()

    import json

    notice_path = new_location / "data-location-migration-notice.json"
    assert notice_path.exists()
    notice = json.loads(notice_path.read_text(encoding="utf-8"))
    assert str(new_location) in notice["message"]


def test_pop_pending_migration_notice_reads_and_clears_once(
    current_data_dir: Path, tmp_path: Path
) -> None:
    new_location = tmp_path / "new-data-home"
    data_location.request_data_location_change("custom", new_location)
    data_location.apply_pending_data_location_migration()

    # app_data_dir() now resolves to new_location, since storage-mode.json
    # was written there by apply_pending_data_location_migration().
    assert app_data_dir() == new_location.resolve()

    message = data_location.pop_pending_migration_notice()
    assert message is not None
    assert "now stored at" in message
    assert data_location.pop_pending_migration_notice() is None


def test_apply_pending_migration_is_a_no_op_when_no_marker_exists(
    current_data_dir: Path,
) -> None:
    data_location.apply_pending_data_location_migration()
    assert data_location.pop_pending_migration_notice() is None


def test_apply_pending_migration_failure_leaves_old_location_intact(
    current_data_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (current_data_dir / "settings.json").write_text('{"theme": "dark"}', encoding="utf-8")
    new_location = tmp_path / "new-data-home"
    data_location.request_data_location_change("custom", new_location)

    def _boom(*_args: object, **_kwargs: object) -> None:
        raise OSError("simulated transient lock")

    monkeypatch.setattr(data_location.shutil, "move", _boom)
    data_location.apply_pending_data_location_migration()

    # Old location is untouched; storage mode was never switched.
    assert (current_data_dir / "settings.json").exists()
    assert storage_mode.load_storage_mode() is None
    notice_path = current_data_dir / "data-location-migration-notice.json"
    assert notice_path.exists()
    assert "Could not move" in notice_path.read_text(encoding="utf-8")


def test_resolve_target_rejects_unknown_mode(current_data_dir: Path) -> None:
    with pytest.raises(ValueError, match="Unknown storage mode"):
        data_location.resolve_target("bogus")


def test_resolve_target_requires_custom_path_for_custom_mode(current_data_dir: Path) -> None:
    with pytest.raises(ValueError, match="requires a path"):
        data_location.resolve_target("custom")


def test_resolve_target_rejects_portable_without_a_bundle(
    current_data_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_exe_dir = tmp_path / "fake-python" / "bin"
    fake_exe_dir.mkdir(parents=True)
    monkeypatch.setattr(storage_mode.sys, "executable", str(fake_exe_dir / "python.exe"))
    with pytest.raises(ValueError, match="Portable mode is not available"):
        data_location.resolve_target("portable")
