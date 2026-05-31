"""Regression tests for the macOS self-voicing bug.

On macOS the announcement engine must hand text to VoiceOver via the
accessibility API and must NEVER fall back to pyttsx3 (the system voice), which
would talk over VoiceOver. See the darwin branch in AnnouncementEngine.announce.
"""
from __future__ import annotations

import quill.platform.macos.announce as macos_announce
import quill.platform.windows.prism_bridge as prism_bridge


def _engine_without_backend() -> prism_bridge.AnnouncementEngine:
    engine = prism_bridge.AnnouncementEngine("auto")
    # Force the no-Prism fallback path deterministically (machine may or may not
    # have a Prism runtime installed).
    engine._runtime_backend = None
    return engine


def test_macos_announce_routes_to_voiceover(monkeypatch) -> None:
    received: list[str] = []
    monkeypatch.setattr(macos_announce, "announce", lambda m: received.append(m) or True)
    monkeypatch.setattr(prism_bridge.sys, "platform", "darwin")

    engine = _engine_without_backend()
    result = engine.announce("hello voiceover")

    assert result is None
    assert received == ["hello voiceover"]


def test_macos_never_self_voices_with_pyttsx3(monkeypatch) -> None:
    monkeypatch.setattr(macos_announce, "announce", lambda m: True)
    monkeypatch.setattr(prism_bridge.sys, "platform", "darwin")

    class _Tripwire:
        def init(self, *args, **kwargs):
            raise AssertionError("pyttsx3 was used on macOS — it talks over VoiceOver")

    monkeypatch.setattr(prism_bridge, "pyttsx3", _Tripwire())

    engine = _engine_without_backend()
    # Must not raise: the darwin branch returns before any pyttsx3 use.
    assert engine.announce("anything") is None


def test_macos_announce_swallows_voiceover_errors(monkeypatch) -> None:
    def _boom(_message: str) -> bool:
        raise RuntimeError("AppKit not available")

    monkeypatch.setattr(macos_announce, "announce", _boom)
    monkeypatch.setattr(prism_bridge.sys, "platform", "darwin")

    engine = _engine_without_backend()
    # A VoiceOver dispatch failure must not crash the app.
    assert engine.announce("hi") is None
