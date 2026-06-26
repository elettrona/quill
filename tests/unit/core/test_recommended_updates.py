from __future__ import annotations

from quill.core.keymap import DEFAULT_KEYMAP
from quill.core.recommended_updates import (
    RECOMMENDED_KEYMAP_UPDATES,
    apply_recommended_keymap_updates,
)

_FIND = next(u for u in RECOMMENDED_KEYMAP_UPDATES if u.command_id == "edit.find")


def test_apply_forces_the_binding_and_reports_the_id_when_enabled() -> None:
    keymap = dict(DEFAULT_KEYMAP)
    keymap["edit.find"] = "Ctrl+Shift+Grave, Z"  # a stale override to overwrite
    updated, newly = apply_recommended_keymap_updates(keymap, [], enabled=True)
    assert updated["edit.find"] == _FIND.binding == "Ctrl+F"
    assert _FIND.id in newly
    # Input is not mutated.
    assert keymap["edit.find"] == "Ctrl+Shift+Grave, Z"


def test_already_applied_update_does_not_fire_again() -> None:
    keymap = dict(DEFAULT_KEYMAP)
    keymap["edit.find"] = "Ctrl+Alt+F"  # user rebound it after the update applied
    updated, newly = apply_recommended_keymap_updates(keymap, [_FIND.id], enabled=True)
    assert newly == set()
    assert updated["edit.find"] == "Ctrl+Alt+F"  # their choice is respected


def test_disabled_changes_nothing_and_marks_nothing() -> None:
    keymap = dict(DEFAULT_KEYMAP)
    keymap["edit.find"] = "Ctrl+Shift+Grave, Z"
    updated, newly = apply_recommended_keymap_updates(keymap, [], enabled=False)
    assert newly == set()
    assert updated["edit.find"] == "Ctrl+Shift+Grave, Z"


def test_update_for_unknown_command_is_skipped() -> None:
    # A stale registry entry referencing a dropped command must not inject it.
    keymap = dict(DEFAULT_KEYMAP)
    _, newly = apply_recommended_keymap_updates(
        keymap, [], enabled=True, valid_command_ids=frozenset()
    )
    assert newly == set()
