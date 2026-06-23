"""Optional in-app install of the Faster Whisper speech engine (#669 follow-up).

QUILL bundles the whisper.cpp and Vosk engines. The higher-throughput Faster
Whisper engine (CTranslate2-based, GPU-capable) pulls in ~110 MB of binary
dependencies (CTranslate2, ONNX Runtime, PyAV, tokenizers), so it is not shipped
in the installer. For users who want it, this installs the engine **on demand**
into a user-writable folder -- no admin, not in the installer payload -- using the
runtime's own pip with **binary wheels only** (no arbitrary build steps).

The packages land in ``<app data>/engine-packs/faster-whisper`` and that folder is
added to ``sys.path`` (see :func:`activate_engine_packs`, called once at startup),
so ``importlib.util.find_spec('faster_whisper')`` then lights the engine up in the
speech registry exactly as a source install would.

Safety mirrors the model / ffmpeg download paths: blocked in Safe Mode, on an
explicit user action only, wheel-only, and the only network touch is the runtime
pip reaching PyPI (documented in the network-egress audit as a subprocess egress).
wx-free.
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from quill.core.speech import models

ProgressCallback = Callable[[float, str], None]

#: Subdirectory under the app-data dir that holds downloadable engine packs.
ENGINE_PACKS_SUBDIR = "engine-packs"

#: The Faster Whisper pack's folder name and import name.
_FASTER_WHISPER_PACK = "faster-whisper"
_FASTER_WHISPER_MODULE = "faster_whisper"

# Kept in sync with the ``[fasterwhisper]`` extra in pyproject.toml. Wheel-only
# (``--only-binary=:all:``) so no build backend is needed at install time.
_FASTER_WHISPER_REQUIREMENTS: tuple[str, ...] = (
    "faster-whisper>=1.0",
    "huggingface_hub>=0.20",
)

_INSTALL_TIMEOUT_S = 1800.0


class EngineInstallError(Exception):
    """Raised when the optional speech-engine download/install fails."""


def engine_packs_dir() -> Path:
    """The root folder holding downloadable engine packs (user-writable)."""
    return models.app_data_dir() / ENGINE_PACKS_SUBDIR


def faster_whisper_pack_dir() -> Path:
    """The folder a downloaded Faster Whisper engine is installed into."""
    return engine_packs_dir() / _FASTER_WHISPER_PACK


def _known_pack_dirs() -> tuple[Path, ...]:
    return (faster_whisper_pack_dir(),)


def activate_engine_packs() -> None:
    """Prepend any installed engine-pack folders to ``sys.path`` (idempotent).

    Called once early in startup so an engine the user installed on demand is
    importable for the rest of the session. Light and safe to call when no pack
    exists -- it only touches ``sys.path`` for folders that are present.
    """
    changed = False
    for pack in _known_pack_dirs():
        try:
            if not pack.is_dir() or not any(pack.iterdir()):
                continue
        except OSError:
            continue
        entry = str(pack)
        if entry not in sys.path:
            sys.path.insert(0, entry)
            changed = True
    if changed:
        importlib.invalidate_caches()


def faster_whisper_install_supported() -> bool:
    """True when QUILL can install Faster Whisper on demand.

    Requires pip to be importable in the running runtime (the shipped build keeps
    pip for exactly this; setuptools/wheel are not needed for a wheel-only install).
    """
    return importlib.util.find_spec("pip") is not None


def is_faster_whisper_available() -> bool:
    """True when the ``faster_whisper`` module is importable (after activation)."""
    return importlib.util.find_spec(_FASTER_WHISPER_MODULE) is not None


def _pip_command(dest: Path, requirements: Sequence[str], python_executable: str) -> list[str]:
    return [
        python_executable,
        "-m",
        "pip",
        "install",
        "--no-input",
        "--disable-pip-version-check",
        "--only-binary=:all:",
        "--no-warn-script-location",
        "--upgrade",
        "--target",
        str(dest),
        *requirements,
    ]


def install_faster_whisper(
    progress: ProgressCallback | None = None,
    *,
    dest_dir: Path | None = None,
    requirements: Sequence[str] | None = None,
    python_executable: str | None = None,
    timeout_seconds: float = _INSTALL_TIMEOUT_S,
    runner: Callable[..., object] | None = None,
) -> Path:
    """Download and install the Faster Whisper engine, returning its pack folder.

    Installs wheel-only into a user-writable engine-pack folder and activates it on
    ``sys.path`` so the engine is immediately importable. Raises
    :class:`EngineInstallError` on Safe Mode, an unsupported runtime, a non-zero
    pip exit, or if the engine still cannot be imported afterward.

    ``runner`` defaults to :func:`quill.stability.safe_subprocess.run_subprocess_safely`
    (injectable for tests); it must return an object with ``returncode``,
    ``stdout``, and ``stderr`` attributes.
    """
    if os.environ.get("QUILL_SAFE_MODE") == "1":
        raise EngineInstallError("Downloading speech engines is disabled in Safe Mode.")
    if not faster_whisper_install_supported():
        raise EngineInstallError(
            "This build cannot install Faster Whisper automatically (pip is "
            'unavailable). Install it from source with: pip install -e ".[fasterwhisper]".'
        )

    dest = Path(dest_dir) if dest_dir is not None else faster_whisper_pack_dir()
    dest.mkdir(parents=True, exist_ok=True)
    reqs = tuple(requirements) if requirements is not None else _FASTER_WHISPER_REQUIREMENTS
    python_exe = python_executable or sys.executable
    if not python_exe:
        raise EngineInstallError("Could not locate the Python runtime to install into.")

    if progress is not None:
        progress(0.05, "Preparing to install Faster Whisper...")
    command = _pip_command(dest, reqs, python_exe)
    run = runner if runner is not None else _default_runner
    if progress is not None:
        progress(0.15, "Downloading Faster Whisper (this can take a few minutes)...")

    try:
        result = run(command, timeout_seconds=timeout_seconds)
    except Exception as exc:  # noqa: BLE001 - surface a clean message
        raise EngineInstallError(f"Could not run the installer: {exc}") from exc

    returncode = int(getattr(result, "returncode", 1))
    if returncode != 0:
        detail = _tail(getattr(result, "stderr", "") or getattr(result, "stdout", ""))
        raise EngineInstallError(
            f"Faster Whisper installation failed (pip exit {returncode}). {detail}"
        )

    if progress is not None:
        progress(0.9, "Finishing up...")
    if str(dest) not in sys.path:
        sys.path.insert(0, str(dest))
    importlib.invalidate_caches()
    if not is_faster_whisper_available():
        raise EngineInstallError(
            "Faster Whisper was installed but could not be imported. Try restarting QUILL."
        )
    if progress is not None:
        progress(1.0, "Done.")
    return dest


def _default_runner(command: Sequence[str], *, timeout_seconds: float) -> object:
    from quill.stability.safe_subprocess import run_subprocess_safely

    return run_subprocess_safely(command, timeout_seconds=timeout_seconds)


def _tail(text: str, *, limit: int = 400) -> str:
    text = (text or "").strip()
    return text[-limit:] if len(text) > limit else text
