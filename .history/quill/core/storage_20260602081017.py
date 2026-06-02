from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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
        raise PathEscapeError(
            f"Refusing to write outside {base_resolved}: {candidate_resolved}"
        )
    return candidate_resolved


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def write_json_atomic(path: Path, data: Any, *, base: Path | None = None) -> None:
    if base is not None:
        resolve_within(base, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8", newline="\n") as file_handle:
        json.dump(data, file_handle, indent=2, sort_keys=True, ensure_ascii=False)
        file_handle.write("\n")
    temp_path.replace(path)
