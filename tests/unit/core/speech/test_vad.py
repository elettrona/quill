"""Tests for voice-activity end-of-turn detection (Hey QUILL refinement)."""

from __future__ import annotations

import struct

from quill.core.speech.vad import SilenceDetector, rms


def _pcm(amplitude: int, ms: int, sample_rate: int = 16000) -> bytes:
    n = sample_rate * ms // 1000
    return struct.pack(f"<{n}h", *([amplitude] * n))


def test_rms_of_silence_is_zero_and_loud_is_high() -> None:
    assert rms(_pcm(0, 100)) == 0.0
    assert rms(_pcm(8000, 100)) > 1000.0


def test_turn_ends_after_speech_then_silence() -> None:
    d = SilenceDetector(sample_rate=16000, silence_ms=1000, min_speech_ms=200)
    # 400 ms of speech: not enough silence yet.
    assert d.feed(_pcm(6000, 400)) is False
    assert d.heard_speech is True
    # 600 ms of silence: still short of the 1000 ms window.
    assert d.feed(_pcm(0, 600)) is False
    # Another 500 ms of silence crosses the window -> turn ends.
    assert d.feed(_pcm(0, 500)) is True


def test_silence_before_any_speech_never_ends_the_turn() -> None:
    d = SilenceDetector(silence_ms=500, min_speech_ms=200)
    for _ in range(10):
        assert d.feed(_pcm(0, 300)) is False
    assert d.heard_speech is False


def test_brief_blip_below_min_speech_does_not_arm() -> None:
    d = SilenceDetector(silence_ms=500, min_speech_ms=300)
    d.feed(_pcm(6000, 100))  # a 100 ms click, under the 300 ms floor
    assert d.heard_speech is False
    assert d.feed(_pcm(0, 1000)) is False  # trailing silence cannot end an empty turn


def test_silence_run_resets_when_speech_resumes() -> None:
    d = SilenceDetector(silence_ms=1000, min_speech_ms=200)
    d.feed(_pcm(6000, 300))  # speech
    d.feed(_pcm(0, 800))  # nearly enough silence
    d.feed(_pcm(6000, 200))  # spoke again -> silence run resets
    assert d.feed(_pcm(0, 800)) is False  # 800 < 1000, not yet


def test_zero_silence_window_disables_detection() -> None:
    d = SilenceDetector(silence_ms=0)
    for _ in range(20):
        assert d.feed(_pcm(0, 500)) is False


def test_reset_clears_state() -> None:
    d = SilenceDetector(silence_ms=500, min_speech_ms=100)
    d.feed(_pcm(6000, 300))
    d.reset()
    assert d.heard_speech is False
