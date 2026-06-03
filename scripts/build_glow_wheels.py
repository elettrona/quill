"""Rebuild the vendored GLOW wheels in a drive-independent way.

Quill consumes the GLOW document-accessibility engine through two first-party,
pure-Python (``py3-none-any``) packages:

* ``quill-glow-core`` — the thin, stable audit/fix/convert service contract Quill
  imports directly.
* ``acb-large-print`` — the GLOW backend that ``quill-glow-core[glow]`` pulls in.

The built wheels live under ``vendor/wheels/`` and are referenced by name from
``pyproject.toml`` (never by a drive path), so installation is portable across
machines and drive letters::

    pip install --find-links vendor/wheels "quill-glow-core[glow]"

Building the wheels, however, needs the GLOW *source* repos, which live outside
the Quill checkout and at different locations on different machines. This helper
finds them without hardcoding any drive letter, in priority order:

1. ``--core-src`` / ``--backend-src`` command-line arguments.
2. ``QUILL_GLOW_CORE_SRC`` / ``QUILL_GLOW_BACKEND_SRC`` environment variables.
3. Auto-discovery: a sibling ``quill-glow-core`` checkout and a sibling
   ``glow/desktop`` checkout next to the Quill repo, then under a sibling
   ``code/`` directory.

Usage examples::

    # Auto-discover sibling GLOW checkouts.
    python scripts/build_glow_wheels.py

    # Point at explicit source locations (any drive).
    python scripts/build_glow_wheels.py --core-src X:/src/quill-glow-core \
        --backend-src X:/src/glow/desktop
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENDOR_WHEELS = REPO_ROOT / "vendor" / "wheels"

# Marker files that confirm a candidate directory is the right source checkout.
_CORE_MARKER = "pyproject.toml"
_BACKEND_MARKER = "pyproject.toml"


def _candidate_roots() -> list[Path]:
    """Directories to search for sibling GLOW checkouts, drive-independently."""
    parent = REPO_ROOT.parent
    roots = [parent, parent / "code", parent.parent, parent.parent / "code"]
    # De-duplicate while preserving order.
    seen: set[Path] = set()
    unique: list[Path] = []
    for root in roots:
        if root not in seen:
            seen.add(root)
            unique.append(root)
    return unique


def _discover(relative_parts: tuple[str, ...], marker: str) -> Path | None:
    for root in _candidate_roots():
        candidate = root.joinpath(*relative_parts)
        if (candidate / marker).is_file():
            return candidate
    return None


def _resolve_source(
    cli_value: str | None,
    env_var: str,
    relative_parts: tuple[str, ...],
    marker: str,
    label: str,
) -> Path:
    if cli_value:
        path = Path(cli_value).expanduser().resolve()
        if not (path / marker).is_file():
            raise SystemExit(f"{label} source {path} has no {marker}")
        return path

    env_value = os.environ.get(env_var)
    if env_value:
        path = Path(env_value).expanduser().resolve()
        if not (path / marker).is_file():
            raise SystemExit(f"{label} source {path} (from {env_var}) has no {marker}")
        return path

    discovered = _discover(relative_parts, marker)
    if discovered is not None:
        return discovered

    raise SystemExit(
        f"Could not locate the {label} source. Pass it explicitly, e.g.\n"
        f"  python scripts/build_glow_wheels.py --core-src <path> --backend-src <path>\n"
        f"or set {env_var}."
    )


def _build_wheel(source: Path, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"Building wheel from {source} -> {outdir}")
    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(outdir), str(source)],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--core-src",
        help="Path to the quill-glow-core source checkout (overrides env/auto-discovery).",
    )
    parser.add_argument(
        "--backend-src",
        help="Path to the acb-large-print source checkout (glow/desktop).",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=VENDOR_WHEELS,
        help="Where to write the wheels (default: vendor/wheels).",
    )
    args = parser.parse_args()

    core_src = _resolve_source(
        args.core_src,
        "QUILL_GLOW_CORE_SRC",
        ("quill-glow-core",),
        _CORE_MARKER,
        "quill-glow-core",
    )
    backend_src = _resolve_source(
        args.backend_src,
        "QUILL_GLOW_BACKEND_SRC",
        ("glow", "desktop"),
        _BACKEND_MARKER,
        "acb-large-print",
    )

    _build_wheel(core_src, args.outdir)
    _build_wheel(backend_src, args.outdir)

    print("\nVendored GLOW wheels:")
    for wheel in sorted(args.outdir.glob("*.whl")):
        print(f"  {wheel.relative_to(REPO_ROOT)}")
    print(
        "\nInstall (drive-independent):\n"
        '  pip install --find-links vendor/wheels "quill-glow-core[glow]"'
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
