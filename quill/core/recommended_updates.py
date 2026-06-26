"""Force-once updates to important defaults (e.g. restoring Find to Ctrl+F).

The delta-based stores (settings, keymap, features) make *unset* defaults flow
forward automatically: a user who never customized a field always tracks its
current default. But sometimes we change a default that users have already
*overridden*, and the change matters enough to push anyway -- the canonical
case being Find, which some pre-release builds bound to a QUILL-key chord and
which we want back on the conventional Ctrl+F for everyone.

A *recommended update* is how we push such a change safely and scalably:

* Each update has a stable ``id``. It is applied **at most once per user** --
  once applied, the id is remembered and the binding is never force-touched
  again, so the user stays free to rebind afterward.
* The whole mechanism is opt-out: users who would rather keep their own choices
  set ``apply_recommended_keymap_updates`` to False in Settings, and nothing is
  forced.

Shipping a new important default change is then a one-liner: append a
:class:`RecommendedKeymapUpdate` with a fresh id. The id is what makes it fire
exactly once. Pure model code -- no ``wx`` imports.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class RecommendedKeymapUpdate:
    """One important keymap default we push to existing users, once.

    ``id`` is the stable, unique fire-once key (never reuse it). ``command_id``
    and ``binding`` are the chord to force; ``reason`` is a short human note for
    docs/changelog and any future "what changed" surfacing.
    """

    id: str
    command_id: str
    binding: str
    reason: str


#: Ordered registry. Append a new entry (with a brand-new ``id``) whenever an
#: important default change should reach users who have already customized that
#: binding. Never edit or remove an existing id -- that is what guarantees each
#: update fires exactly once per user.
RECOMMENDED_KEYMAP_UPDATES: tuple[RecommendedKeymapUpdate, ...] = (
    RecommendedKeymapUpdate(
        id="edit.find-ctrl-f-2026-06",
        command_id="edit.find",
        binding="Ctrl+F",
        reason="Find returns to the conventional Ctrl+F (some pre-release builds "
        "defaulted it to a QUILL-key chord).",
    ),
)


def apply_recommended_keymap_updates(
    keymap: dict[str, str],
    applied_ids: Iterable[str],
    *,
    enabled: bool,
    valid_command_ids: frozenset[str] | None = None,
) -> tuple[dict[str, str], set[str]]:
    """Apply not-yet-applied recommended keymap updates to a copy of ``keymap``.

    Returns ``(updated_keymap, newly_applied_ids)``. ``updated_keymap`` is a new
    dict (the input is never mutated); ``newly_applied_ids`` are the update ids
    that fired this call and should be recorded so they never fire again.

    * When ``enabled`` is False (the user opted out), nothing is changed and no
      ids are returned -- and crucially nothing is marked applied, so turning the
      setting back on later still offers the current recommendations.
    * An update whose id is already in ``applied_ids`` is skipped (fire-once).
    * ``valid_command_ids``, when given, guards against an update referencing a
      command that no longer ships, so a stale registry entry cannot inject an
      unknown binding.
    """
    if not enabled:
        return dict(keymap), set()
    already = set(applied_ids)
    updated = dict(keymap)
    newly: set[str] = set()
    for update in RECOMMENDED_KEYMAP_UPDATES:
        if update.id in already:
            continue
        if valid_command_ids is not None and update.command_id not in valid_command_ids:
            continue
        updated[update.command_id] = update.binding
        newly.add(update.id)
    return updated, newly


__all__ = [
    "RECOMMENDED_KEYMAP_UPDATES",
    "RecommendedKeymapUpdate",
    "apply_recommended_keymap_updates",
]
