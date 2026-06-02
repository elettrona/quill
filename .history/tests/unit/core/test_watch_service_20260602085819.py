"""Tests for the WatchService facade (WATCH-1 through WATCH-7)."""

from __future__ import annotations

import time
from pathlib import Path

from quill.core.watch_profiles import WatchProfile
from quill.core.watch_service import WATCH_FEATURE_ID, WatchService


def _service(tmp_path: Path, **kwargs) -> WatchService:
    return WatchService(data_dir=tmp_path, **kwargs)


def test_start_respects_disabled_feature(tmp_path: Path) -> None:
    service = _service(tmp_path, feature_enabled=lambda _fid: False)
    service.add_profile(WatchProfile(name="Inbox", folder_path=str(tmp_path)))
    assert service.start() == []
    assert service.is_running is False
    service.stop()


def test_feature_flag_check_uses_watch_id(tmp_path: Path) -> None:
    seen: list[str] = []

    def gate(fid: str) -> bool:
        seen.append(fid)
        return True

    service = _service(tmp_path, feature_enabled=gate)
    service.is_feature_enabled()
    assert seen == [WATCH_FEATURE_ID]


def test_start_launches_enabled_profiles(tmp_path: Path) -> None:
    watch_dir = tmp_path / "drop"
    watch_dir.mkdir()
    service = _service(tmp_path)
    added = service.add_profile(
        WatchProfile(name="Inbox", folder_path=str(watch_dir), enabled=True)
    )
    started = service.start()
    try:
        assert added.profile_id in started
        assert service.is_running is True
    finally:
        service.stop()
    assert service.is_running is False


def test_open_action_processes_dropped_file(tmp_path: Path) -> None:
    watch_dir = tmp_path / "drop"
    watch_dir.mkdir()
    opened: list[Path] = []
    service = _service(tmp_path, on_open=opened.append)
    service.add_profile(
        WatchProfile(
            name="Inbox",
            folder_path=str(watch_dir),
            enabled=True,
            process_existing=True,
            action_id="open",
            poll_interval_seconds=2,
        )
    )
    service.start()
    try:
        (watch_dir / "note.txt").write_text("hello", encoding="utf-8")
        deadline = time.time() + 5.0
        while time.time() < deadline and not opened:
            time.sleep(0.05)
    finally:
        service.stop()
    assert any(p.name == "note.txt" for p in opened)


def test_profiles_persist_across_instances(tmp_path: Path) -> None:
    first = _service(tmp_path)
    first.add_profile(WatchProfile(name="Inbox", folder_path=str(tmp_path)))
    second = _service(tmp_path)
    assert [p.name for p in second.profiles()] == ["Inbox"]


def test_queue_passthroughs(tmp_path: Path) -> None:
    service = _service(tmp_path)
    assert sum(service.queue_counts().values()) == 0
    assert service.queue_items() == []
    service.pause()
    service.resume()
    assert service.clear_finished() == 0
