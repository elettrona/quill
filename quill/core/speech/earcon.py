"""Transition earcons ("sounders") and PCM silence for chaptered speech (§4.8.5).

wx-free, strict-typed, stdlib-only (``wave`` + ``math`` + ``struct``). Produces a
short, pleasant **placeholder chime** to mark article/chapter boundaries in the
"with-tones" output variant, plus matching PCM silence for the inter-article gap.

The bundled chime is intentionally a *placeholder* the user can replace: a real
sound file dropped into a sound pack, or any WAV chosen in the batch dialog, can
override it. The generator is parameterised by sample rate / channels / sample
width so the earcon and silence always match the format of the speech WAVs they
are spliced between (the assembler reads the first section's format and passes it
through — see :mod:`quill.core.speech.chapter_assemble`).

No playback happens here — everything writes PCM to disk, consistent with the
silent batch pipeline (§silent-batch).
"""

from __future__ import annotations

import math
import struct
import wave
from dataclasses import dataclass
from pathlib import Path

# A sensible default speech-WAV format. SAPI 5, Piper, eSpeak, and Kokoro all
# emit 16-bit mono; 22.05 kHz is the most common TTS rate. The assembler
# overrides these from the first real section WAV so splices line up exactly.
DEFAULT_SAMPLE_RATE = 22050
DEFAULT_CHANNELS = 1
DEFAULT_SAMPWIDTH = 2  # bytes per sample (16-bit PCM)


@dataclass(slots=True, frozen=True)
class PcmFormat:
    """The PCM parameters that silence and earcons must match to splice cleanly."""

    sample_rate: int = DEFAULT_SAMPLE_RATE
    channels: int = DEFAULT_CHANNELS
    sampwidth: int = DEFAULT_SAMPWIDTH

    @classmethod
    def from_wav(cls, path: Path) -> PcmFormat:
        """Read the PCM format of an existing WAV (the canonical section format)."""
        with wave.open(str(path), "rb") as w:
            return cls(
                sample_rate=w.getframerate(),
                channels=w.getnchannels(),
                sampwidth=w.getsampwidth(),
            )


def _max_amplitude(sampwidth: int) -> int:
    """Largest positive sample value for a given byte width (16-bit -> 32767)."""
    return (1 << (8 * sampwidth - 1)) - 1


def _tone_samples(
    fmt: PcmFormat,
    *,
    freq_hz: float,
    duration_ms: int,
    volume: float,
    fade_ms: int = 8,
) -> list[int]:
    """A single sine tone as a list of integer samples (mono), with a short fade.

    The fade in/out avoids clicks at the tone edges — important for screen-reader
    users who would otherwise hear a hard pop at every chapter boundary.
    """
    n = max(0, int(fmt.sample_rate * duration_ms / 1000))
    if n == 0:
        return []
    amp = _max_amplitude(fmt.sampwidth) * max(0.0, min(1.0, volume))
    fade = min(int(fmt.sample_rate * fade_ms / 1000), n // 2)
    samples: list[int] = []
    for i in range(n):
        env = 1.0
        if fade > 0:
            if i < fade:
                env = i / fade
            elif i >= n - fade:
                env = (n - i) / fade
        value = amp * env * math.sin(2.0 * math.pi * freq_hz * (i / fmt.sample_rate))
        samples.append(int(value))
    return samples


def _write_wav(path: Path, fmt: PcmFormat, mono_samples: list[int]) -> None:
    """Write mono integer samples to a PCM WAV, duplicating across channels."""
    clip = _max_amplitude(fmt.sampwidth)
    frames = bytearray()
    for s in mono_samples:
        s = max(-clip - 1, min(clip, s))
        packed = struct.pack("<h", s) if fmt.sampwidth == 2 else struct.pack("<i", s)
        frames += packed * fmt.channels
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(fmt.channels)
        w.setsampwidth(fmt.sampwidth)
        w.setframerate(fmt.sample_rate)
        w.writeframes(bytes(frames))


def silence_frames(fmt: PcmFormat, duration_ms: int) -> bytes:
    """Raw PCM silence (all-zero frames) of ``duration_ms`` in ``fmt``."""
    n = max(0, int(fmt.sample_rate * duration_ms / 1000))
    return b"\x00" * (n * fmt.sampwidth * fmt.channels)


def write_silence_wav(path: Path, fmt: PcmFormat, duration_ms: int) -> Path:
    """Write a silent WAV of ``duration_ms`` (used for the inter-article gap)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(fmt.channels)
        w.setsampwidth(fmt.sampwidth)
        w.setframerate(fmt.sample_rate)
        w.writeframes(silence_frames(fmt, duration_ms))
    return path


def default_sounder_samples(fmt: PcmFormat, *, volume: float = 1.0) -> list[int]:
    """The placeholder chime as mono samples: a rising two-note 'ding-dong'.

    Two short sine tones (a perfect fourth apart, ~A5 then D6) with a tiny gap —
    a friendly, unobtrusive boundary cue. Swap the frequencies/durations to taste,
    or replace the whole thing with a user-chosen sound later.
    """
    first = _tone_samples(fmt, freq_hz=880.0, duration_ms=110, volume=volume)
    middle = [0] * int(fmt.sample_rate * 0.02)  # 20 ms gap between the two notes
    second = _tone_samples(fmt, freq_hz=1174.7, duration_ms=150, volume=volume)
    return first + middle + second


def write_default_sounder(
    path: Path,
    fmt: PcmFormat | None = None,
    *,
    volume: float = 1.0,
) -> Path:
    """Write the placeholder transition chime to ``path`` as a PCM WAV.

    ``fmt`` defaults to the standard speech-WAV format; pass the section format so
    the chime splices cleanly. ``volume`` is 0.0–1.0 (map a 0–100 setting by /100).
    """
    fmt = fmt or PcmFormat()
    _write_wav(path, fmt, default_sounder_samples(fmt, volume=volume))
    return path


def sounder_duration_ms(fmt: PcmFormat) -> int:
    """Length of the default chime in ms, for chapter-offset accounting."""
    return len(default_sounder_samples(fmt)) * 1000 // fmt.sample_rate
