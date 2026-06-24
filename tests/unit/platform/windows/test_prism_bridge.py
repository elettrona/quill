from __future__ import annotations

import types

from quill.platform.windows.prism_bridge import AnnouncementEngine


class _FakeFeatures:
    def __init__(self, *, runtime: bool = True) -> None:
        self.is_supported_at_runtime = runtime


class _FakeBackend:
    def __init__(self, *, runtime: bool = True) -> None:
        self.features = _FakeFeatures(runtime=runtime)
        self.name = "Fake Prism"
        self.messages: list[str] = []

    def speak(self, message: str, interrupt: bool = False) -> None:
        _ = interrupt
        self.messages.append(message)


class _FakeContext:
    def __init__(self, backend: _FakeBackend) -> None:
        self._backend = backend

    def acquire_best(self) -> _FakeBackend:
        return self._backend


def test_announcement_engine_uses_prism_backend_when_available(monkeypatch) -> None:
    backend = _FakeBackend(runtime=True)
    prism_module = types.SimpleNamespace(Context=lambda: _FakeContext(backend))
    monkeypatch.setattr(
        "quill.platform.windows.prism_bridge.import_module",
        lambda name: prism_module if name == "prism" else None,
    )
    engine = AnnouncementEngine("auto")

    state = engine.state()
    assert state.active_backend == "prism"
    assert state.prism_runtime_ready is True
    assert engine.announce("hello") is None
    assert backend.messages == ["hello"]


def test_announcement_engine_falls_back_to_status_when_prism_missing(monkeypatch) -> None:
    def fail_import(_name: str) -> object:
        raise ImportError

    monkeypatch.setattr("quill.platform.windows.prism_bridge.import_module", fail_import)
    engine = AnnouncementEngine("prism")

    state = engine.state()
    assert state.requested_backend == "prism"
    assert state.active_backend == "status_only"
    assert "not installed" in state.last_error.lower()


class _FakeVoice:
    """Stand-in SAPI SpVoice that records what was spoken."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def Speak(self, message: str, flags: int = 0) -> None:  # noqa: N802 - SAPI API name
        _ = flags
        self.messages.append(message)


def test_announcement_engine_uses_system_speech_when_prism_is_missing(monkeypatch) -> None:
    voice = _FakeVoice()
    build_calls = {"n": 0}

    def _build():
        build_calls["n"] += 1
        return voice

    # The SAPI fallback is the Windows path; on macOS announcements go to
    # VoiceOver instead. Pin a non-darwin platform so this exercises the TTS
    # fallback regardless of the host OS the tests run on.
    monkeypatch.setattr("quill.platform.windows.prism_bridge.sys.platform", "win32")
    monkeypatch.setattr("quill.platform.windows.prism_bridge._build_tts_voice", _build)
    monkeypatch.setattr(
        "quill.platform.windows.prism_bridge.import_module",
        lambda _name: (_ for _ in ()).throw(ImportError),
    )
    monkeypatch.setattr(
        "quill.platform.windows.prism_bridge._screen_reader_active",
        lambda: False,
    )
    # The SAPI SpVoice is a process-wide singleton built once on the worker
    # thread, so many announcements must build it exactly once after a reset.
    from quill.platform.windows import prism_bridge

    prism_bridge.reset_tts_engine_for_tests()

    engine = AnnouncementEngine("auto")
    assert engine.announce("hello") is None
    assert engine.announce("world") is None
    prism_bridge.flush_tts_for_tests()
    assert voice.messages == ["hello", "world"]
    assert build_calls["n"] == 1
    assert engine.state().active_backend == "speech"


def test_force_speech_bypasses_screen_reader_suppression(monkeypatch) -> None:
    # The QUILL key prefix/browse-mode chord has no focus or control change for
    # a screen reader to pick up on its own, so callers narrating that
    # internal-only state pass force_speech=True to still get spoken even
    # while JAWS/NVDA/Narrator is running and no Prism backend is active.
    voice = _FakeVoice()
    monkeypatch.setattr("quill.platform.windows.prism_bridge.sys.platform", "win32")
    monkeypatch.setattr("quill.platform.windows.prism_bridge._build_tts_voice", lambda: voice)
    monkeypatch.setattr(
        "quill.platform.windows.prism_bridge.import_module",
        lambda _name: (_ for _ in ()).throw(ImportError),
    )
    monkeypatch.setattr(
        "quill.platform.windows.prism_bridge._screen_reader_active",
        lambda: True,
    )
    from quill.platform.windows import prism_bridge

    prism_bridge.reset_tts_engine_for_tests()

    engine = AnnouncementEngine("auto")
    assert engine.announce("quiet while screen reader runs") is None
    prism_bridge.flush_tts_for_tests()
    assert voice.messages == []

    assert engine.announce("QUILL key", force_speech=True) is None
    prism_bridge.flush_tts_for_tests()
    assert voice.messages == ["QUILL key"]


def test_macos_announce_error_logged(monkeypatch, caplog) -> None:
    """H-4-platform: a VoiceOver announce failure is logged, not silently swallowed."""
    import logging

    monkeypatch.setattr("quill.platform.windows.prism_bridge.sys.platform", "darwin")
    monkeypatch.setattr(
        "quill.platform.windows.prism_bridge.import_module",
        lambda _name: (_ for _ in ()).throw(ImportError),
    )

    def _boom(_msg: str) -> None:
        raise RuntimeError("VoiceOver not available")

    monkeypatch.setattr(
        "quill.platform.macos.announce.announce",
        _boom,
        raising=False,
    )

    engine = AnnouncementEngine("auto")
    with caplog.at_level(logging.WARNING, logger="quill.platform.windows.prism_bridge"):
        result = engine.announce("test message")

    assert result is None
    assert any("VoiceOver" in r.message for r in caplog.records)
