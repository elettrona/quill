"""#617 Speech S2 UI: the SpeechCommandsMixin resolves the offline provider."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

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


class _FakeDialog:
    def __init__(self, *_a: object, **_k: object) -> None:
        self._sel = 0

    def __enter__(self) -> _FakeDialog:
        return self

    def __exit__(self, *_a: object) -> bool:
        return False

    def SetSelection(self, index: int) -> None:
        self._sel = index

    def GetSelection(self) -> int:
        return self._sel


class _FakeWx:
    ID_OK = 5100

    def SingleChoiceDialog(self, *_a: object, **_k: object) -> _FakeDialog:
        return _FakeDialog()


def _host_with_two_engines(modal_result: int) -> tuple[_Host, object, object]:
    host = _Host()
    host.frame = object()  # type: ignore[attr-defined]  # dialog parent, unused by the fake
    host.settings = SimpleNamespace(speech_whisper_path="", speech_provider="")
    p1 = SimpleNamespace(id="whispercpp", display_name="whisper.cpp")
    p2 = SimpleNamespace(id="fasterwhisper", display_name="Faster Whisper")
    host._speech_registry = lambda: SimpleNamespace(  # type: ignore[method-assign]
        available=lambda: [p1, p2], get=lambda _i: None
    )
    host._wx = _FakeWx()  # type: ignore[assignment]
    host._show_modal_dialog = lambda _dialog, _title: modal_result  # type: ignore[assignment]
    host._announce = lambda *_a, **_k: None  # type: ignore[assignment]
    return host, p1, p2


def test_choose_speech_engine_cancel_returns_cancelled_not_default() -> None:
    # Escape/Cancel on the engine chooser must report cancellation so the caller
    # returns to the editor instead of opening the default engine's models (#8).
    host, _p1, _p2 = _host_with_two_engines(_FakeWx.ID_OK - 1)
    cancelled, provider = host._choose_speech_engine()
    assert cancelled is True
    assert provider is None


def test_choose_speech_engine_ok_selects_and_persists(monkeypatch: pytest.MonkeyPatch) -> None:
    import quill.core.settings as settings_module

    monkeypatch.setattr(settings_module, "save_settings", lambda _s: None)
    host, p1, _p2 = _host_with_two_engines(_FakeWx.ID_OK)
    cancelled, provider = host._choose_speech_engine()
    assert cancelled is False
    assert provider is p1
    assert host.settings.speech_provider == "whispercpp"
