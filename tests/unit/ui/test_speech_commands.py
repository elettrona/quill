"""#617 Speech S2 UI: the SpeechCommandsMixin resolves the offline provider."""

from __future__ import annotations

from types import SimpleNamespace

from quill.ui.main_frame_speech import SpeechCommandsMixin


class _Host(SpeechCommandsMixin):
    def __init__(self) -> None:
        self.settings = SimpleNamespace(speech_whisper_path="")


def test_speech_provider_is_whispercpp() -> None:
    provider = _Host()._speech_provider()
    assert provider is not None
    assert provider.id == "whispercpp"
    # The provider exposes the model catalog without needing the binary installed.
    assert any(m.id == "small" for m in provider.list_supported_models())
