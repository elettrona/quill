from __future__ import annotations

from pathlib import Path

import pytest

from quill.core import storage_mode
from quill.core.paths import app_data_dir
from quill.core.storage_mode import custom_path, load_storage_mode, save_storage_mode


def _make_portable_bundle(tmp_path: Path) -> Path:
    """Create a minimal portable-bundle layout: a run-quill.cmd at the root.

    Mirrors what scripts/build_windows_distribution.py actually ships, and
    is the structural evidence portable_root_dir() requires -- a bare env
    var value is never trusted on its own (L-9).
    """
    root = tmp_path / "QuillPortable"
    root.mkdir()
    (root / "run-quill.cmd").write_text("@echo off\r\n", encoding="utf-8")
    return root


def _pin_executable_away_from_any_real_bundle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Make the sys.executable fallback chain deterministic in tests.

    Without this, portable_root_dir()'s fallback (walking up from
    sys.executable) would check the real dev machine's Python install
    location, which happens to lack run-quill.cmd today but is not a
    guarantee a test should depend on.
    """
    fake_exe_dir = tmp_path / "fake-python" / "bin"
    fake_exe_dir.mkdir(parents=True)
    monkeypatch.setattr(storage_mode.sys, "executable", str(fake_exe_dir / "python.exe"))


def test_portable_root_requires_run_quill_cmd_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """L-9: a bare QUILL_APP_ROOT value is not enough on its own."""
    _pin_executable_away_from_any_real_bundle(monkeypatch, tmp_path)
    bare_dir = tmp_path / "not-a-real-bundle"
    bare_dir.mkdir()
    monkeypatch.setenv("QUILL_APP_ROOT", str(bare_dir))
    assert storage_mode.portable_root_dir() is None


def test_portable_root_resolves_with_verified_bundle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = _make_portable_bundle(tmp_path)
    monkeypatch.setenv("QUILL_APP_ROOT", str(root))
    resolved = storage_mode.portable_root_dir()
    assert resolved == (root / "data").resolve()
    # The data folder need not exist yet -- created on demand when chosen.
    assert not resolved.exists()


def test_storage_mode_uses_portable_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = _make_portable_bundle(tmp_path)
    monkeypatch.setenv("QUILL_APP_ROOT", str(root))
    assert load_storage_mode() is None

    save_storage_mode("portable")

    assert load_storage_mode() == "portable"
    assert app_data_dir() == (root / "data").resolve()


def test_storage_mode_can_prefer_appdata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = _make_portable_bundle(tmp_path)
    monkeypatch.setenv("QUILL_APP_ROOT", str(root))
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    save_storage_mode("appdata")

    assert load_storage_mode() == "appdata"
    assert app_data_dir() == (tmp_path / "appdata" / "Quill").resolve()


def test_custom_mode_works_without_a_portable_bundle(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """#615: non-portable users can also redirect their data folder."""
    _pin_executable_away_from_any_real_bundle(monkeypatch, tmp_path)
    monkeypatch.delenv("QUILL_APP_ROOT", raising=False)
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    target = tmp_path / "MyQuillData"

    save_storage_mode("custom", path=target)

    assert load_storage_mode() == "custom"
    assert custom_path() == target.resolve()
    assert app_data_dir() == target.resolve()


def test_save_storage_mode_custom_requires_a_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _pin_executable_away_from_any_real_bundle(monkeypatch, tmp_path)
    monkeypatch.delenv("QUILL_APP_ROOT", raising=False)
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    with pytest.raises(ValueError, match="requires a path"):
        save_storage_mode("custom")


def test_arbitrary_quill_app_root_alone_does_not_redirect_data(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """L-9 (carried forward): setting QUILL_APP_ROOT to an attacker-chosen

    directory with no run-quill.cmd there must not be treated as portable.
    """
    _pin_executable_away_from_any_real_bundle(monkeypatch, tmp_path)
    monkeypatch.setenv("QUILL_APP_ROOT", str(tmp_path / "attacker-controlled"))
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    monkeypatch.delenv("QUILL_DATA_DIR", raising=False)
    assert storage_mode.portable_root_dir() is None
    assert app_data_dir() == (tmp_path / "appdata" / "Quill").resolve()


def test_storage_mode_falls_back_when_portable_path_is_not_writable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = _make_portable_bundle(tmp_path)
    monkeypatch.setenv("QUILL_APP_ROOT", str(root))
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    monkeypatch.setattr("quill.core.storage_mode.os.access", lambda *_args: False)

    save_storage_mode("appdata")

    fallback_path = tmp_path / "appdata" / "Quill" / "storage-mode.json"
    assert fallback_path.exists()
    assert not (root / "data" / "storage-mode.json").exists()
    assert load_storage_mode() == "appdata"

    stale_portable_path = root / "data" / "storage-mode.json"
    stale_portable_path.parent.mkdir(parents=True, exist_ok=True)
    stale_portable_path.write_text('{"mode":"portable"}', encoding="utf-8")
    assert load_storage_mode() == "appdata"
