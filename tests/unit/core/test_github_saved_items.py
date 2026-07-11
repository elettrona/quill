"""Pinned repositories + favorites store (GHManage parity, QUILL conventions)."""

from __future__ import annotations

from pathlib import Path

from quill.core.github.saved_items import FavoriteItem, GitHubSavedItems


def _store(tmp_path: Path) -> GitHubSavedItems:
    return GitHubSavedItems.load(tmp_path / "github_saved_items.json")


def test_pin_unpin_round_trip_with_case_insensitive_dedup(tmp_path: Path) -> None:
    store = _store(tmp_path)
    assert store.pin_repo("Community-Access/QUILL") is True
    assert store.pin_repo("community-access/quill") is False  # dedup
    assert store.pin_repo("no-slash") is False  # not owner/repo shaped
    assert store.is_pinned("COMMUNITY-ACCESS/QUILL") is True

    reloaded = _store(tmp_path)
    assert reloaded.pinned == ["Community-Access/QUILL"]
    assert reloaded.unpin_repo("community-access/QUILL") is True
    assert reloaded.unpin_repo("community-access/QUILL") is False
    assert _store(tmp_path).pinned == []


def test_favorites_round_trip_dedup_and_timestamp(tmp_path: Path) -> None:
    store = _store(tmp_path)
    entry = FavoriteItem(
        repo="o/r", item_type="issue", url="https://github.com/o/r/issues/1", title="#1 Bug"
    )
    assert store.add_favorite(entry) is True
    assert store.add_favorite(entry) is False  # dedup by repo+type+url
    assert store.add_favorite(FavoriteItem(repo="", item_type="issue", url="x", title="")) is False

    reloaded = _store(tmp_path)
    assert len(reloaded.favorites) == 1
    saved = reloaded.favorites[0]
    assert saved.title == "#1 Bug"
    assert saved.added_at  # stamped at add time
    assert reloaded.remove_favorite(saved.key) is True
    assert _store(tmp_path).favorites == []


def test_corrupt_store_degrades_to_empty(tmp_path: Path) -> None:
    target = tmp_path / "github_saved_items.json"
    target.write_text("not json at all", encoding="utf-8")
    store = GitHubSavedItems.load(target)
    assert store.pinned == [] and store.favorites == []
