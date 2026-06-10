"""Named bookmark helpers (wx-free domain logic).

Kept as a separate module so the pure dict operations can be unit-tested
without importing wx. The UI layer (MainFrame) owns the bookmark dict and
calls these helpers directly.
"""

from __future__ import annotations


def set_bookmark(bookmarks: dict[str, int], name: str, position: int) -> dict[str, int]:
    normalized_name = name.strip()
    if not normalized_name:
        return bookmarks
    updated = dict(bookmarks)
    updated[normalized_name] = max(0, position)
    return updated


def bookmark_names(bookmarks: dict[str, int]) -> list[str]:
    return sorted(bookmarks.keys(), key=lambda value: value.lower())


def bookmark_position(bookmarks: dict[str, int], name: str) -> int | None:
    return bookmarks.get(name)
