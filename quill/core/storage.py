from __future__ import annotations

import errno
import json
import os
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

# On Windows os.replace can transiently fail with PermissionError when another
# process (an antivirus scanner, a backup agent, or a screen reader's file hook)
# briefly holds the destination open. Retry a few times with a short backoff
# before giving up so a normal save is not lost to a momentary lock.
_REPLACE_MAX_ATTEMPTS = 5
_REPLACE_RETRY_DELAY = 0.05


class PathEscapeError(ValueError):
    """Raised when a write target resolves outside its permitted base directory."""


def resolve_within(base: Path, candidate: Path) -> Path:
    """Resolve ``candidate`` and confirm it stays inside ``base``.

    Returns the resolved candidate path. Raises :class:`PathEscapeError` when the
    candidate would escape ``base`` (for example through a ``..`` segment or an
    absolute path), so persistence writers can never be tricked into writing
    outside the application data area.
    """

    base_resolved = base.resolve()
    candidate_resolved = candidate.resolve()
    if candidate_resolved != base_resolved and base_resolved not in candidate_resolved.parents:
        raise PathEscapeError(f"Refusing to write outside {base_resolved}: {candidate_resolved}")
    return candidate_resolved


def _atomic_replace(temp_path: Path, path: Path) -> None:
    """Replace ``path`` with ``temp_path``, retrying transient Windows locks.

    On Windows the destination can be briefly held open by an antivirus
    scanner, a backup agent, or a screen reader's file hook. We retry on
    ``PermissionError`` and on ``OSError`` with the transient sharing-
    violation / lock-violation errnos (ERROR_SHARING_VIOLATION,
    ERROR_LOCK_VIOLATION) so a normal save is not lost to a momentary lock.
    """

    _TRANSIENT_ERRNOS = frozenset({
        errno.EACCES,
        errno.EAGAIN,
        errno.EBUSY,
        getattr(errno, "EWOULDBLOCK", errno.EAGAIN),
    })
    last_error: OSError | None = None
    for attempt in range(_REPLACE_MAX_ATTEMPTS):
        try:
            temp_path.replace(path)
            return
        except OSError as error:
            if not isinstance(error, PermissionError) and error.errno not in _TRANSIENT_ERRNOS:
                raise
            last_error = error
            if attempt + 1 < _REPLACE_MAX_ATTEMPTS:
                time.sleep(_REPLACE_RETRY_DELAY)
    assert last_error is not None
    raise last_error


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def write_json_atomic(path: Path, data: Any, *, base: Path | None = None) -> None:
    if base is not None:
        resolve_within(base, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Use a UUID-named temp file in the same directory so concurrent writers
    # cannot collide on a fixed name like path.suffix + ".tmp".
    fd, raw_temp = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=f".{uuid.uuid4().hex}.tmp",
        dir=path.parent,
    )
    temp_path = Path(raw_temp)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file_handle:
            json.dump(data, file_handle, indent=2, sort_keys=True, ensure_ascii=False)
            file_handle.write("\n")
            file_handle.flush()
            os.fsync(file_handle.fileno())
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise
    try:
        _atomic_replace(temp_path, path)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise
