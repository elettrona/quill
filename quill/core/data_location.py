"""Configurable data-location support (issue #615).

Moving the data directory while QUILL is running is not safe: the
in-memory ``Settings`` object is loaded once at startup and never reloaded
on demand, ``CopyTray`` caches its data directory at construction, and
there is no atomic move primitive for an entire directory tree under
Windows' transient file locks. So a location change is recorded as a
*pending* migration (``request_data_location_change``) and applied once,
very early in ``quill.__main__.main()`` -- before ``ensure_app_directories()``
or anything else resolves :func:`quill.core.paths.app_data_dir` -- by
:func:`apply_pending_data_location_migration`.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from quill.core import storage_mode
from quill.core.paths import app_data_dir
from quill.core.storage import read_json, retry_on_transient_lock, write_json_atomic

_PENDING_MARKER_NAME = "pending-data-location.json"
_MIGRATION_NOTICE_NAME = "data-location-migration-notice.json"

_VALID_MODES = {"appdata", "portable", "custom"}


def _appdata_target() -> Path:
    """Mirror paths.py::app_data_dir()'s appdata branch, for resolving a move target."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "Quill"
    return Path.home() / ".quill"


def resolve_target(mode: str, custom_path: Path | None = None) -> Path:
    """Return the directory ``mode`` (and ``custom_path``, if any) resolves to."""
    if mode not in _VALID_MODES:
        raise ValueError(f"Unknown storage mode: {mode}")
    if mode == "custom":
        if custom_path is None:
            raise ValueError("Custom storage mode requires a path")
        return Path(custom_path).expanduser().resolve()
    if mode == "portable":
        root = storage_mode.portable_root_dir()
        if root is None:
            raise ValueError("Portable mode is not available -- not running from a portable bundle")
        return root
    return _appdata_target()


def request_data_location_change(mode: str, custom_path: Path | None = None) -> Path:
    """Record an intent to move the data directory; applied on next launch.

    Returns the resolved target directory, for the caller's confirmation
    message. If the target is already the current data directory, the
    storage-mode choice is saved immediately and no migration is queued.
    """
    target = resolve_target(mode, custom_path)
    current = app_data_dir().resolve()

    if target == current:
        storage_mode.save_storage_mode(mode, path=target if mode == "custom" else None)
        (current / _PENDING_MARKER_NAME).unlink(missing_ok=True)
        return target

    document: dict[str, object] = {"mode": mode, "target": str(target)}
    if mode == "custom":
        document["custom_path"] = str(target)
    write_json_atomic(current / _PENDING_MARKER_NAME, document)
    return target


def apply_pending_data_location_migration() -> None:
    """Apply a pending data-location move recorded by Preferences, if any.

    Must run before ``ensure_app_directories()``/``load_settings()`` so it
    reads the marker from the *current* (pre-move) location. Writes a
    one-line notice (success or failure) at whichever location the app
    will actually use afterwards, for :func:`pop_pending_migration_notice`
    to surface once the UI exists.
    """
    current = app_data_dir()
    marker = current / _PENDING_MARKER_NAME
    if not marker.exists():
        return

    document = read_json(marker, default={})
    marker.unlink(missing_ok=True)
    if not isinstance(document, dict):
        return

    mode = document.get("mode")
    target_raw = document.get("target")
    if not isinstance(mode, str) or mode not in _VALID_MODES or not isinstance(target_raw, str):
        return
    target = Path(target_raw)

    try:
        _move_directory_contents(current, target)
    except OSError as error:
        _write_migration_notice(
            current, f"Could not move Quill's data to {target}: {error}. Staying at {current}."
        )
        return

    custom_value = document.get("custom_path")
    custom_path = Path(str(custom_value)) if mode == "custom" and custom_value else None
    storage_mode.save_storage_mode(mode, path=custom_path)
    _write_migration_notice(target, f"Quill's data is now stored at {target}.")


def pop_pending_migration_notice() -> str | None:
    """Read and clear the one-time migration status message, or return None.

    Mirrors ``paths.py::new_install_marker_path()``'s consume-once pattern:
    call from the UI layer once a frame exists (see
    ``main_frame.py::_maybe_run_first_run_onboarding``) so the message can
    be announced/shown, rather than threading it through ``run_app()``.
    """
    marker = app_data_dir() / _MIGRATION_NOTICE_NAME
    if not marker.exists():
        return None
    document = read_json(marker, default={})
    marker.unlink(missing_ok=True)
    if not isinstance(document, dict):
        return None
    message = document.get("message")
    return message if isinstance(message, str) else None


def _write_migration_notice(location: Path, message: str) -> None:
    write_json_atomic(location / _MIGRATION_NOTICE_NAME, {"message": message})


def _move_directory_contents(source: Path, destination: Path) -> None:
    """Move every entry in ``source`` into ``destination``, retrying transient locks.

    Moves per top-level entry (not a single directory rename) so it works
    whether or not the destination already exists, and so a partial
    failure leaves both ends in a recoverable state rather than a
    half-renamed directory. Never overwrites an existing destination entry
    -- skips it instead, so a retry after a partial failure does not lose
    data that already made it across.
    """
    destination.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        return
    for entry in source.iterdir():
        target_entry = destination / entry.name
        if target_entry.exists():
            continue

        def _do_move(_entry: Path = entry, _target: Path = target_entry) -> None:
            shutil.move(str(_entry), str(_target))

        retry_on_transient_lock(_do_move)


__all__ = [
    "apply_pending_data_location_migration",
    "pop_pending_migration_notice",
    "request_data_location_change",
    "resolve_target",
]
