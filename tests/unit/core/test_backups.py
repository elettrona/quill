from __future__ import annotations

from pathlib import Path

import pytest

from quill.core.backups import backup_document, list_backups
from quill.core.document import Document


def test_backup_document_creates_snapshot(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "work.txt"
    document = Document(text="hello", path=target)

    snapshot = backup_document(document)
    assert snapshot.exists()
    assert snapshot.suffix == ".bak"
    assert snapshot.read_text(encoding="utf-8") == "hello"


def test_list_backups_returns_newest_first(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "work.txt"
    document = Document(text="one", path=target)
    first = backup_document(document)
    document.set_text("two")
    second = backup_document(document)

    items = list_backups(target)
    assert items[0] == second
    assert items[1] == first


def test_backup_document_disambiguates_identical_timestamps(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    target = tmp_path / "work.txt"
    document = Document(text="one", path=target)

    class _FrozenDatetime:
        @staticmethod
        def now(_tz: object) -> object:
            class _Stamp:
                @staticmethod
                def strftime(_fmt: str) -> str:
                    return "20260529T210000000000Z"

            return _Stamp()

    monkeypatch.setattr("quill.core.backups.datetime", _FrozenDatetime)

    first = backup_document(document)
    document.set_text("two")
    second = backup_document(document)

    assert first.name == "20260529T210000000000Z.bak"
    assert second.name == "20260529T210000000000Z-1.bak"
    assert second.read_text(encoding="utf-8") == "two"
