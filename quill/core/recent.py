from __future__ import annotations

import sys
from pathlib import Path

from quill.core.paths import app_data_dir
from quill.core.storage import read_json, write_json_atomic

# Win32 GetDriveType return code for a fixed/internal drive.
_DRIVE_FIXED = 3


def recent_path() -> Path:
    return app_data_dir() / "recent.json"


def load_recent_files() -> list[Path]:
    raw = read_json(recent_path(), default=[])
    if not isinstance(raw, list):
        return []
    results: list[Path] = []
    for item in raw:
        if isinstance(item, str):
            results.append(Path(item))
    return results


def save_recent_files(paths: list[Path]) -> None:
    write_json_atomic(recent_path(), [str(entry) for entry in paths], base=app_data_dir())


def add_recent_file(path: Path, limit: int) -> list[Path]:
    normalized = path.resolve()
    existing = [entry.resolve() for entry in load_recent_files()]
    deduped = [entry for entry in existing if entry != normalized]
    updated = [normalized, *deduped][:limit]
    save_recent_files(updated)
    return updated


def clear_recent_files() -> None:
    save_recent_files([])


def _is_fixed_drive(path: Path) -> bool:
    """True only when *path* can be positively confirmed to live on a fixed,
    internal drive.

    Deliberately conservative: anything we cannot confirm is fixed -- a
    removable/USB drive, a network share, a RAM disk, an unknown type, or any
    non-Windows platform -- returns False. Callers use this to decide whether a
    missing file may be auto-dropped; a False result means "keep it", because a
    file that is 'missing' on a detached USB or network drive usually means the
    drive is gone, not that the file was deleted (#14)."""
    if sys.platform != "win32":
        return False
    anchor = path.anchor  # e.g. "C:\\"; empty for a relative or UNC-less path
    if not anchor:
        return False
    try:
        import ctypes

        drive_type = ctypes.windll.kernel32.GetDriveTypeW(anchor)  # type: ignore[attr-defined]
    except (OSError, AttributeError, ValueError):
        return False
    return int(drive_type) == _DRIVE_FIXED


def prune_missing_recent_files(
    paths: list[Path], *, enabled: bool
) -> tuple[list[Path], list[Path]]:
    """Split *paths* into (kept, removed).

    When *enabled*, an entry is removed only when it both (a) no longer exists
    on disk and (b) sits on a confirmed fixed/internal drive. Entries on
    removable/network/unknown drives are never probed and always kept, so a
    detached USB or offline share doesn't wipe its recent files (#14). When
    *enabled* is False this is a no-op and nothing is removed."""
    if not enabled:
        return list(paths), []
    kept: list[Path] = []
    removed: list[Path] = []
    for path in paths:
        # Check drive type first so removable/network paths are never probed
        # (their existence check can be slow or hang on a detached drive).
        if not _is_fixed_drive(path):
            kept.append(path)
            continue
        try:
            exists = path.exists()
        except OSError:
            exists = True  # keep on any access error rather than risk a wrong drop
        (kept if exists else removed).append(path)
    return kept, removed
