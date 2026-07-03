"""Remote feature kill switch — local persistence and enforcement state (wx-free).

Signed feature advisories ride inside the update manifest
(:mod:`quill.core.updates`). This module turns the advisories that apply to the
running version into a locked set, persists it atomically in the app data dir so
a kill switch **survives offline and across restarts** (a lock you can only
reach while online would be useless during an incident), and exposes the small
state object the UI consults in ``_feature_enabled``.

Design guarantees:

- **Fail-safe, one direction.** A lock can only make a feature *unavailable*; it
  never enables or runs anything. Enforcement is a plain membership test.
- **Persistent once received.** The locked set is cached locally and honored on
  the next launch even with no network. It clears only when a later verified
  manifest no longer lists the feature (or the escape hatch below is used).
- **Local escape hatch.** Setting ``QUILL_IGNORE_FEATURE_LOCKS=1`` disables all
  remote locks for that run — for an administrator who must use a feature the
  advisory disabled, or to recover if an advisory is ever wrong.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

_STATE_FILE = "feature_locks.json"
_IGNORE_ENV = "QUILL_IGNORE_FEATURE_LOCKS"


def locks_ignored() -> bool:
    """True when the local escape hatch (``QUILL_IGNORE_FEATURE_LOCKS``) is set."""
    return os.getenv(_IGNORE_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class FeatureLockState:
    """The set of remotely-locked features and why (feature_id -> spoken reason)."""

    locked: dict[str, str] = field(default_factory=dict)

    def is_locked(self, feature_id: str) -> bool:
        if locks_ignored():
            return False
        return feature_id in self.locked

    def reason(self, feature_id: str) -> str:
        return self.locked.get(feature_id, "")

    def active(self) -> dict[str, str]:
        """The effective locks (empty when the escape hatch is set)."""
        return {} if locks_ignored() else dict(self.locked)


def _state_path() -> Path:
    from quill.core.paths import app_data_dir

    return app_data_dir() / "safety" / _STATE_FILE


def load_feature_locks() -> FeatureLockState:
    """Load the cached locked set; an empty/absent/corrupt cache means no locks."""
    try:
        import json

        path = _state_path()
        if not path.is_file():
            return FeatureLockState()
        data = json.loads(path.read_text(encoding="utf-8"))
        locked = data.get("locked") if isinstance(data, dict) else None
        if not isinstance(locked, dict):
            return FeatureLockState()
        return FeatureLockState(locked={str(k): str(v) for k, v in locked.items()})
    except Exception:  # noqa: BLE001 - a bad cache must never break startup
        return FeatureLockState()


def save_feature_locks(locked: dict[str, str]) -> None:
    """Persist the locked set atomically (best-effort; never raises)."""
    try:
        from quill.core.storage import write_json_atomic

        path = _state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json_atomic(path, {"locked": locked})
    except Exception:  # noqa: BLE001 - persistence failure must not break the app
        pass


def apply_manifest_locks(manifest: object, current_version: str) -> FeatureLockState:
    """Resolve a manifest's advisories for ``current_version``, persist, and return.

    ``manifest`` is an :class:`quill.core.updates.UpdateManifest`. A manifest
    with no advisories clears any previously-cached locks — that is how a fixed
    build lifts a kill switch.
    """
    from quill.core.updates import active_feature_locks

    locked = active_feature_locks(manifest, current_version)  # type: ignore[arg-type]
    save_feature_locks(locked)
    return FeatureLockState(locked=locked)


__all__ = [
    "FeatureLockState",
    "apply_manifest_locks",
    "load_feature_locks",
    "locks_ignored",
    "save_feature_locks",
]
