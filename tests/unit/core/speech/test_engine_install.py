"""Tests for the on-demand Faster Whisper engine installer (#669 follow-up)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from quill.core.speech import engine_install as ei


class _FakeResult:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


@pytest.fixture(autouse=True)
def _restore_sys_path():
    before = list(sys.path)
    yield
    sys.path[:] = before


def _make_runner(captured: dict, result: _FakeResult | None = None):
    def runner(command, *, timeout_seconds):
        captured["command"] = list(command)
        captured["timeout"] = timeout_seconds
        return result if result is not None else _FakeResult()

    return runner


def test_install_builds_wheel_only_target_command(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(ei, "is_faster_whisper_available", lambda: True)
    captured: dict = {}
    dest = tmp_path / "fw"
    out = ei.install_faster_whisper(
        dest_dir=dest,
        requirements=("faster-whisper>=1.0",),
        python_executable="py.exe",
        runner=_make_runner(captured),
    )
    cmd = captured["command"]
    assert out == dest and dest.is_dir()
    assert cmd[0] == "py.exe"
    assert cmd[1:4] == ["-m", "pip", "install"]
    assert "--only-binary=:all:" in cmd
    assert "--target" in cmd and cmd[cmd.index("--target") + 1] == str(dest)
    assert "faster-whisper>=1.0" in cmd
    assert str(dest) in sys.path  # activated on success


def test_install_blocked_in_safe_mode(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_SAFE_MODE", "1")
    with pytest.raises(ei.EngineInstallError, match="Safe Mode"):
        ei.install_faster_whisper(dest_dir=tmp_path / "fw", runner=_make_runner({}))


def test_install_unsupported_runtime_raises(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(ei, "faster_whisper_install_supported", lambda: False)
    with pytest.raises(ei.EngineInstallError, match="pip is"):
        ei.install_faster_whisper(dest_dir=tmp_path / "fw", runner=_make_runner({}))


def test_install_nonzero_exit_surfaces_pip_output(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(ei, "is_faster_whisper_available", lambda: True)
    runner = _make_runner({}, _FakeResult(returncode=1, stderr="No matching distribution"))
    with pytest.raises(ei.EngineInstallError, match="No matching distribution"):
        ei.install_faster_whisper(dest_dir=tmp_path / "fw", runner=runner)


def test_install_succeeds_but_not_importable_raises(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(ei, "is_faster_whisper_available", lambda: False)
    with pytest.raises(ei.EngineInstallError, match="could not be imported"):
        ei.install_faster_whisper(dest_dir=tmp_path / "fw", runner=_make_runner({}))


def test_install_wraps_runner_exception(monkeypatch, tmp_path: Path) -> None:
    def boom(command, *, timeout_seconds):
        raise OSError("launch failed")

    with pytest.raises(ei.EngineInstallError, match="Could not run the installer"):
        ei.install_faster_whisper(dest_dir=tmp_path / "fw", runner=boom)


def test_activate_engine_packs_adds_nonempty_dir(monkeypatch, tmp_path: Path) -> None:
    pack = tmp_path / "fw"
    pack.mkdir()
    (pack / "marker.txt").write_text("x", encoding="utf-8")
    monkeypatch.setattr(ei, "faster_whisper_pack_dir", lambda: pack)
    ei.activate_engine_packs()
    assert str(pack) in sys.path
    # Idempotent: a second call does not duplicate the entry.
    ei.activate_engine_packs()
    assert sys.path.count(str(pack)) == 1


def test_activate_engine_packs_skips_missing_or_empty(monkeypatch, tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(ei, "faster_whisper_pack_dir", lambda: empty)
    ei.activate_engine_packs()
    assert str(empty) not in sys.path
    missing = tmp_path / "missing"
    monkeypatch.setattr(ei, "faster_whisper_pack_dir", lambda: missing)
    ei.activate_engine_packs()
    assert str(missing) not in sys.path
