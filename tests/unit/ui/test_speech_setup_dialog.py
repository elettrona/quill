"""Unit tests for SpeechSetupDialog pure helpers (#8 model-manager).

Covers the engine-chooser label, which must keep a registered-but-not-installed
engine (e.g. whisper.cpp with no binary) visible and clearly marked rather than
hiding it. The helper is a staticmethod, so it is exercised without constructing
the wx dialog.
"""

from __future__ import annotations

from quill.ui.speech_setup_dialog import SpeechSetupDialog


class _FakeProvider:
    def __init__(self, display_name: str, *, available: bool, raises: bool = False) -> None:
        self.display_name = display_name
        self._available = available
        self._raises = raises

    def is_available(self) -> bool:
        if self._raises:
            raise RuntimeError("boom")
        return self._available


def test_provider_label_plain_when_available() -> None:
    provider = _FakeProvider("Whisper.cpp", available=True)
    assert SpeechSetupDialog._provider_label(provider) == "Whisper.cpp"


def test_provider_label_marks_uninstalled_engine() -> None:
    provider = _FakeProvider("Whisper.cpp", available=False)
    assert SpeechSetupDialog._provider_label(provider) == "Whisper.cpp (not installed)"


def test_provider_label_treats_broken_provider_as_not_installed() -> None:
    provider = _FakeProvider("Vosk", available=True, raises=True)
    assert SpeechSetupDialog._provider_label(provider) == "Vosk (not installed)"


def test_provider_label_falls_back_when_name_missing() -> None:
    assert SpeechSetupDialog._provider_label(object()) == "Engine (not installed)"
