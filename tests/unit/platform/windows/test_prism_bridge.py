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
