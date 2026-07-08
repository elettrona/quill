"""Packaging-dependency invariants.

These guard a class of "green tests, broken build" bugs where a package that a
*default* feature needs at runtime is declared only in an optional extra (or the
dev extra). Dev and CI install those extras, so import-based tests pass -- but the
shipped runtime, which installs only the base dependencies, is missing the package
and the feature fails at first use. See the beta-2 speech-engine fixes:

- huggingface_hub: the default whisper.cpp speech-to-text engine downloads its
  GGML models via huggingface_hub.hf_hub_download, so it must be a base dep.
- Babel: the Kokoro ONNX voice chain (kokoro-onnx -> phonemizer -> segments ->
  csvw -> babel.numbers) needs it; it must ride with the [kokoro] extra, not only
  [dev].
"""

from __future__ import annotations

import pathlib
import tomllib

import pytest

_PYPROJECT = pathlib.Path(__file__).resolve().parents[2] / "pyproject.toml"


@pytest.fixture(scope="module")
def project() -> dict:
    return tomllib.loads(_PYPROJECT.read_text("utf-8"))["project"]


def _names(requirements: list[str]) -> set[str]:
    """Distribution names from PEP 508 requirement strings, lowercased.

    Normalizes '-'/'_' so 'huggingface_hub' and 'huggingface-hub' compare equal.
    """
    out: set[str] = set()
    for req in requirements:
        head = req.split(";", 1)[0].strip()
        for sep in ("==", ">=", "<=", "~=", ">", "<", "!=", "[", " "):
            head = head.split(sep, 1)[0]
        out.add(head.strip().lower().replace("_", "-"))
    return out


def test_huggingface_hub_is_a_base_runtime_dependency(project: dict) -> None:
    """The default whisper.cpp downloader needs huggingface_hub on a clean install.

    It must be in [project].dependencies -- not only the optional [fasterwhisper]
    extra -- so speech-to-text model downloads work without opting into Faster
    Whisper. Regression guard for QUILL-SPEECH-PROVIDER-FAILED "needs the
    'huggingface_hub' package" on a fresh install.
    """
    assert "huggingface-hub" in _names(project["dependencies"])


def test_babel_rides_with_the_kokoro_extra(project: dict) -> None:
    """The Kokoro ONNX voice chain imports babel.numbers transitively via csvw.

    Declaring Babel in the [kokoro] extra keeps that runtime chain self-contained
    so a pruned/partial install can't leave the ONNX voice path failing with
    ModuleNotFoundError: No module named 'babel'.
    """
    assert "babel" in _names(project["optional-dependencies"]["kokoro"])
