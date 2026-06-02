from __future__ import annotations

from pathlib import Path

import pytest

from quill.core.storage import (
    PathEscapeError,
    read_json,
    resolve_within,
    write_json_atomic,
)


def test_write_and_read_json(tmp_path: Path) -> None:
    target = tmp_path / "state.json"
    payload = {"a": 1, "b": ["x", "y"]}
    write_json_atomic(target, payload)
    loaded = read_json(target, default={})
    assert loaded == payload


def test_read_json_returns_default_for_missing_file(tmp_path: Path) -> None:
    target = tmp_path / "missing.json"
    loaded = read_json(target, default={"ok": True})
    assert loaded == {"ok": True}


def test_resolve_within_allows_nested_paths(tmp_path: Path) -> None:
    target = tmp_path / "sub" / "state.json"
    resolved = resolve_within(tmp_path, target)
    assert resolved == target.resolve()


def test_resolve_within_rejects_parent_traversal(tmp_path: Path) -> None:
    base = tmp_path / "appdata"
    base.mkdir()
    escape = base / ".." / ".." / "evil.json"
    with pytest.raises(PathEscapeError):
        resolve_within(base, escape)


def test_write_json_atomic_guard_blocks_traversal(tmp_path: Path) -> None:
    base = tmp_path / "appdata"
    base.mkdir()
    escape = base / ".." / "outside.json"
    with pytest.raises(PathEscapeError):
        write_json_atomic(escape, {"k": "v"}, base=base)
    assert not (tmp_path / "outside.json").exists()


def test_write_json_atomic_guard_allows_in_base(tmp_path: Path) -> None:
    base = tmp_path / "appdata"
    base.mkdir()
    target = base / "nested" / "state.json"
    write_json_atomic(target, {"k": "v"}, base=base)
    assert read_json(target, default={}) == {"k": "v"}
