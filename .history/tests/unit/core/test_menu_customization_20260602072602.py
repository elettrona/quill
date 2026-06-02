from __future__ import annotations

from pathlib import Path

import pytest

from quill.core.menu_customization import (
    CONTEXT_MENU_KEY,
    MenuCustomization,
    load_menu_customization,
    save_menu_customization,
)

DEFAULT_TOP = ["file", "edit", "view", "insert", "ai", "help"]
DEFAULT_EDIT_ITEMS = ["edit.undo", "edit.redo", "edit.cut", "edit.copy", "edit.paste"]


def test_defaults_are_identity() -> None:
    custom = MenuCustomization()
    assert custom.is_customized() is False
    assert custom.ordered_top_keys(DEFAULT_TOP) == DEFAULT_TOP
    assert custom.visible_top_keys(DEFAULT_TOP) == DEFAULT_TOP
    assert custom.ordered_item_keys("edit", DEFAULT_EDIT_ITEMS) == DEFAULT_EDIT_ITEMS
    assert custom.top_label("edit", "Edit") == "Edit"
    assert custom.item_label("edit.cut", "Cut") == "Cut"


def test_reorder_top_keeps_unlisted_in_default_order() -> None:
    custom = MenuCustomization()
    custom.set_top_order(["help", "edit"])
    # help, edit first (saved order), then the rest in default order.
    assert custom.ordered_top_keys(DEFAULT_TOP) == [
        "help",
        "edit",
        "file",
        "view",
        "insert",
        "ai",
    ]
    assert custom.is_customized() is True


def test_hidden_top_removed_from_visible_but_kept_in_ordered() -> None:
    custom = MenuCustomization()
    custom.set_top_hidden("ai", True)
    assert "ai" in custom.ordered_top_keys(DEFAULT_TOP)
    assert "ai" not in custom.visible_top_keys(DEFAULT_TOP)
    custom.set_top_hidden("ai", False)
    assert "ai" in custom.visible_top_keys(DEFAULT_TOP)


def test_item_reorder_and_hide() -> None:
    custom = MenuCustomization()
    custom.set_item_order("edit", ["edit.paste", "edit.copy"])
    assert custom.ordered_item_keys("edit", DEFAULT_EDIT_ITEMS) == [
        "edit.paste",
        "edit.copy",
        "edit.undo",
        "edit.redo",
        "edit.cut",
    ]
    custom.set_item_hidden("edit.cut", True)
    assert "edit.cut" not in custom.visible_item_keys("edit", DEFAULT_EDIT_ITEMS)


def test_rename_and_clear() -> None:
    custom = MenuCustomization()
    custom.rename_top("edit", "Editing")
    custom.rename_item("edit.cut", "Snip")
    assert custom.top_label("edit", "Edit") == "Editing"
    assert custom.item_label("edit.cut", "Cut") == "Snip"
    # Empty / whitespace rename clears the override.
    custom.rename_top("edit", "   ")
    custom.rename_item("edit.cut", "")
    assert custom.top_label("edit", "Edit") == "Edit"
    assert custom.item_label("edit.cut", "Cut") == "Cut"


def test_reset_returns_to_factory() -> None:
    custom = MenuCustomization()
    custom.set_top_order(["help", "file"])
    custom.set_top_hidden("ai", True)
    custom.rename_item("edit.cut", "Snip")
    assert custom.is_customized() is True
    custom.reset()
    assert custom.is_customized() is False
    assert custom.ordered_top_keys(DEFAULT_TOP) == DEFAULT_TOP


def test_reconcile_drops_stale_keys() -> None:
    custom = MenuCustomization()
    custom.set_top_order(["file", "gone_menu"])
    custom.set_top_hidden("gone_menu", True)
    custom.rename_top("gone_menu", "Ghost")
    custom.set_item_order("edit", ["edit.cut", "edit.gone"])
    custom.set_item_hidden("edit.gone", True)
    custom.rename_item("edit.gone", "Ghost item")
    custom.reconcile(
        known_top_keys={"file", "edit"},
        known_item_keys={"edit.cut", "edit.copy"},
    )
    assert custom.top_order == ["file"]
    assert custom.hidden_top == []
    assert "gone_menu" not in custom.top_labels
    assert custom.item_order["edit"] == ["edit.cut"]
    assert custom.hidden_items == []
    assert "edit.gone" not in custom.item_labels


def test_reconcile_keeps_context_menu_key() -> None:
    custom = MenuCustomization()
    custom.set_item_order(CONTEXT_MENU_KEY, ["edit.copy", "edit.cut"])
    custom.reconcile(
        known_top_keys={"edit"},
        known_item_keys={"edit.copy", "edit.cut"},
    )
    assert custom.item_order[CONTEXT_MENU_KEY] == ["edit.copy", "edit.cut"]


def test_from_dict_tolerates_garbage() -> None:
    assert MenuCustomization.from_dict(None).is_customized() is False
    assert MenuCustomization.from_dict([1, 2, 3]).is_customized() is False
    salvaged = MenuCustomization.from_dict(
        {
            "top_order": ["file", 42, "file", "edit"],
            "hidden_top": "not-a-list",
            "top_labels": {"edit": "", "file": "Documents", 7: "bad"},
            "item_order": {"edit": ["a", "a", "b"], "bad": 5},
            "hidden_items": ["x"],
            "item_labels": {"k": "  Label  "},
        }
    )
    assert salvaged.top_order == ["file", "edit"]
    assert salvaged.hidden_top == []
    assert salvaged.top_labels == {"file": "Documents"}
    assert salvaged.item_order == {"edit": ["a", "b"]}
    assert salvaged.hidden_items == ["x"]
    assert salvaged.item_labels == {"k": "  Label  "}


def test_round_trip_persistence(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    custom = MenuCustomization()
    custom.set_top_order(["help", "file"])
    custom.set_top_hidden("ai", True)
    custom.rename_top("edit", "Editing")
    custom.set_item_order("edit", ["edit.paste", "edit.copy"])
    custom.set_item_hidden("edit.cut", True)
    custom.rename_item("edit.copy", "Duplicate")
    save_menu_customization(custom)

    loaded = load_menu_customization()
    assert loaded.to_dict() == custom.to_dict()


def test_load_missing_returns_defaults(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    assert load_menu_customization().is_customized() is False
