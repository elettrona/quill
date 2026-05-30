from __future__ import annotations

from pathlib import Path

import pytest

from quill.core.paths import app_data_dir
from quill.core.storage_mode import load_storage_mode, save_storage_mode


def test_storage_mode_uses_portable_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_PORTABLE_ROOT", str(tmp_path / "portable"))
    assert load_storage_mode() is None

    save_storage_mode("portable")

    assert load_storage_mode() == "portable"
    assert app_data_dir() == (tmp_path / "portable").resolve()


def test_storage_mode_can_prefer_appdata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_PORTABLE_ROOT", str(tmp_path / "portable"))
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    save_storage_mode("appdata")

    assert load_storage_mode() == "appdata"
    assert app_data_dir() == (tmp_path / "appdata" / "Quill").resolve()


def test_storage_mode_falls_back_when_portable_path_is_not_writable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("QUILL_PORTABLE_ROOT", str(tmp_path / "portable"))
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    monkeypatch.setattr("quill.core.storage_mode.os.access", lambda *_args: False)

    save_storage_mode("appdata")

    fallback_path = tmp_path / "appdata" / "Quill" / "storage-mode.json"
    assert fallback_path.exists()
    assert not (tmp_path / "portable" / "storage-mode.json").exists()
    assert load_storage_mode() == "appdata"

    stale_portable_path = tmp_path / "portable" / "storage-mode.json"
    stale_portable_path.parent.mkdir(parents=True, exist_ok=True)
    stale_portable_path.write_text('{"mode":"portable"}', encoding="utf-8")
    assert load_storage_mode() == "appdata"
