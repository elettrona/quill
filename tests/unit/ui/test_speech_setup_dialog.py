"""Unit tests for SpeechSetupDialog pure helpers (#8 model-manager).

Covers the engine-chooser label, which must keep a registered-but-not-installed
engine (e.g. whisper.cpp with no binary) visible and clearly marked rather than
hiding it. The helper is a staticmethod, so it is exercised without constructing
the wx dialog.
"""

from __future__ import annotations

from quill.ui.speech_setup_dialog import SpeechSetupDialog, build_engine_descriptors


class _IdProvider:
    def __init__(self, pid: str, display_name: str) -> None:
        self.id = pid
        self.display_name = display_name


def test_engine_descriptors_always_lists_three_dictation_engines() -> None:
    rows = build_engine_descriptors(
        [_IdProvider("whispercpp", "Whisper.cpp")],
        whispercpp_ok=True,
        faster_whisper_ok=False,
        vosk_ok=False,
    )
    labels = [r["label"] for r in rows]
    assert any("Whisper (built in)" in label for label in labels)
    assert any("Faster Whisper" in label for label in labels)
    assert any("Vosk" in label for label in labels)


def test_engine_descriptors_mark_not_installed_with_install_action() -> None:
    rows = build_engine_descriptors(
        [_IdProvider("whispercpp", "Whisper.cpp")],
        whispercpp_ok=True,
        faster_whisper_ok=False,
        vosk_ok=False,
    )
    by_action = {r["install_action"]: r for r in rows}
    # Faster Whisper / Vosk are not installed here, so they carry an install action
    # and no provider yet — selecting them installs the engine.
    assert by_action["engine"]["installed"] is False
    assert by_action["engine"]["provider"] is None
    assert by_action["vosk"]["installed"] is False


def test_engine_descriptors_append_other_registered_providers() -> None:
    cloud = _IdProvider("cloud-stt", "Cloud STT")
    rows = build_engine_descriptors(
        [_IdProvider("whispercpp", "Whisper.cpp"), cloud],
        whispercpp_ok=True,
        faster_whisper_ok=False,
        vosk_ok=False,
    )
    cloud_rows = [r for r in rows if r["provider"] is cloud]
    assert len(cloud_rows) == 1
    assert cloud_rows[0]["installed"] is True
    assert cloud_rows[0]["install_action"] is None


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
