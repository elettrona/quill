from __future__ import annotations

from pathlib import Path

import pytest

from quill.core.undo_store import clear_undo_history, load_undo_history, save_undo_history


def test_save_and_load_undo_history(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "note.md"
    target.write_text("x", encoding="utf-8")
    save_undo_history(target, ["a", "b", "c"])
    assert load_undo_history(target) == ["a", "b", "c"]


def test_save_undo_history_honors_limit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "note.md"
    target.write_text("x", encoding="utf-8")
    save_undo_history(target, ["1", "2", "3", "4"], limit=2)
    assert load_undo_history(target) == ["3", "4"]


def test_clear_undo_history(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "note.md"
    target.write_text("x", encoding="utf-8")
    save_undo_history(target, ["one"])
    clear_undo_history(target)
    assert load_undo_history(target) == []


def test_load_missing_history_returns_empty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "never-saved.md"
    assert load_undo_history(target) == []


def test_clear_missing_history_is_a_noop(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "never-saved.md"
    # Clearing a history that was never written must not raise.
    clear_undo_history(target)
    assert load_undo_history(target) == []


def test_load_filters_non_string_entries(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "note.md"
    # Persistence accepts only string snapshots; corrupt entries are dropped.
    save_undo_history(target, ["good", "also-good"])
    raw_path = next((Path(tmp_path) / "undo").glob("*.json"))
    raw_path.write_text('["keep", 5, null, "stay", true]', encoding="utf-8")
    assert load_undo_history(target) == ["keep", "stay"]


def test_load_non_list_payload_returns_empty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "note.md"
    save_undo_history(target, ["seed"])
    raw_path = next((Path(tmp_path) / "undo").glob("*.json"))
    raw_path.write_text('{"not": "a list"}', encoding="utf-8")
    assert load_undo_history(target) == []


def test_save_returns_bounded_history(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "note.md"
    returned = save_undo_history(target, ["1", "2", "3", "4", "5"], limit=3)
    assert returned == ["3", "4", "5"]
    assert load_undo_history(target) == ["3", "4", "5"]


def test_save_limit_below_one_keeps_a_single_entry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "note.md"
    # A non-positive limit is coerced to keep the most recent entry, never zero.
    save_undo_history(target, ["old", "new"], limit=0)
    assert load_undo_history(target) == ["new"]


def test_history_survives_repeated_save_load_cycles(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "note.md"
    # Simulate undo snapshots accumulating across edits, then a reload.
    save_undo_history(target, ["v1"])
    save_undo_history(target, ["v1", "v2"])
    save_undo_history(target, ["v1", "v2", "v3"])
    assert load_undo_history(target) == ["v1", "v2", "v3"]


def test_histories_for_distinct_paths_do_not_collide(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    save_undo_history(first, ["a", "b"])
    save_undo_history(second, ["x", "y"])
    assert load_undo_history(first) == ["a", "b"]
    assert load_undo_history(second) == ["x", "y"]
