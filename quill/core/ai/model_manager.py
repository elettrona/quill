"""Automatic, RAM-tiered model download for the llama.cpp backend.

On first use, if no GGUF model is present, Quill downloads one sized to the
machine's RAM (per issue #40):
  - under 8 GB RAM  -> Llama 3.2 1B Instruct (Q4)  (~0.8 GB)
  - 8 GB or more    -> Phi-4-mini Instruct (Q4)    (~2.5 GB)

Resolution order: QUILL_LLAMA_MODEL env -> first *.gguf in <app data>/models ->
download the tiered model. Standard library only (urllib).
"""
from __future__ import annotations

import os
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from quill.core.paths import app_data_dir


@dataclass(frozen=True, slots=True)
class ModelSpec:
    name: str
    filename: str
    url: str


_LOW_END = ModelSpec(
    "Llama 3.2 1B Instruct (Q4_K_M)",
    "Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/"
    "Llama-3.2-1B-Instruct-Q4_K_M.gguf",
)
_DEFAULT = ModelSpec(
    "Phi-4-mini Instruct (Q4_K_M)",
    "Phi-4-mini-instruct-Q4_K_M.gguf",
    "https://huggingface.co/bartowski/Phi-4-mini-instruct-GGUF/resolve/main/"
    "Phi-4-mini-instruct-Q4_K_M.gguf",
)

_LOW_RAM_THRESHOLD_GB = 8.0


def total_ram_gb() -> float:
    # POSIX (Linux, macOS)
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / (1024**3)
    except (ValueError, AttributeError, OSError):
        pass
    # Windows
    if sys.platform.startswith("win"):
        import ctypes

        class _MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = _MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        return stat.ullTotalPhys / (1024**3)
    return _LOW_RAM_THRESHOLD_GB  # safe default


def choose_model_spec() -> ModelSpec:
    return _LOW_END if total_ram_gb() < _LOW_RAM_THRESHOLD_GB else _DEFAULT


def models_dir() -> Path:
    return app_data_dir() / "models"


def existing_model() -> str | None:
    override = os.environ.get("QUILL_LLAMA_MODEL")
    if override and Path(override).expanduser().exists():
        return str(Path(override).expanduser())
    folder = models_dir()
    if folder.exists():
        for candidate in sorted(folder.glob("*.gguf")):
            return str(candidate)
    return None


def ensure_model(progress=None) -> str:
    """Return a local GGUF path, downloading the RAM-appropriate model if needed.

    ``progress`` is an optional callable(downloaded_bytes, total_bytes).
    """
    found = existing_model()
    if found:
        return found
    spec = choose_model_spec()
    folder = models_dir()
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / spec.filename
    _download(spec.url, target, progress)
    return str(target)


def _download(url: str, target: Path, progress=None) -> None:
    part = target.with_name(target.name + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "Quill"})
    with urllib.request.urlopen(request) as response, open(part, "wb") as out:
        total = int(response.headers.get("Content-Length", 0))
        done = 0
        while True:
            chunk = response.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)
            if progress is not None:
                progress(done, total)
    part.replace(target)
