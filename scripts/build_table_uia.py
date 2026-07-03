"""Build the optional Table Studio native UIA provider (`_quill_table_uia.pyd`).

Wraps the CMake build in ``quill/native/table_uia``. Windows-only; requires
MSVC (Visual Studio 2022), the Windows 10 SDK (10.0.19041+), pybind11
(``pip install pybind11``), and CMake 3.20+.

On success the built ``_quill_table_uia.pyd`` is staged in
``quill/native/table_uia/`` and reported. The build is entirely optional: QUILL
runs with the MSAA fallback when the module is absent, so this script exits 0
with a clear message when the toolchain is missing rather than failing a build.

Usage::

    python scripts/build_table_uia.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

_NATIVE_DIR = Path(__file__).resolve().parent.parent / "quill" / "native" / "table_uia"


def _have(tool: str) -> bool:
    return shutil.which(tool) is not None


def main() -> int:
    if sys.platform != "win32":
        print("The Table Studio UIA provider is Windows-only; nothing to build here.")
        return 0
    if not _have("cmake"):
        print("cmake not found on PATH; skipping the native UIA provider (MSAA fallback ships).")
        return 0
    build_dir = _NATIVE_DIR / "build"
    try:
        subprocess.run(
            ["cmake", "-B", str(build_dir), "-G", "Visual Studio 17 2022", "-A", "x64"],
            cwd=_NATIVE_DIR,
            check=True,
        )
        subprocess.run(
            ["cmake", "--build", str(build_dir), "--config", "Release"],
            cwd=_NATIVE_DIR,
            check=True,
        )
        subprocess.run(
            ["cmake", "--install", str(build_dir), "--config", "Release"],
            cwd=_NATIVE_DIR,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        print(
            f"Native UIA provider build failed ({error}); QUILL will ship with the "
            "MSAA fallback. Install pybind11 and the Windows 10 SDK to enable it."
        )
        return 0
    pyd = next(_NATIVE_DIR.glob("_quill_table_uia*.pyd"), None)
    if pyd is None:
        print("Build reported success but no .pyd was produced; using the MSAA fallback.")
        return 0
    print(f"Built native UIA provider: {pyd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
