"""Transcription output formatters: TXT, SRT, VTT, JSON (#617 section 6.2).

Pure functions that turn a :class:`TranscriptionResult` (or its segments) into
the standard caption/transcript formats. No I/O, no wx — the UI decides where to
write the returned string.
"""

from __future__ import annotations

import json

from quill.core.speech.provider import TranscriptionResult, TranscriptionSegment


def to_plain_text(result: TranscriptionResult) -> str:
    """The transcript as plain text (one trailing newline)."""
    return result.full_text.strip() + "\n"


def to_srt(segments: tuple[TranscriptionSegment, ...]) -> str:
    """SubRip (.srt) captions. Indices are 1-based; times use a comma."""
    blocks: list[str] = []
    for index, segment in enumerate(segments, start=1):
        blocks.append(
            f"{index}\n"
            f"{_srt_timestamp(segment.start_seconds)} --> {_srt_timestamp(segment.end_seconds)}\n"
            f"{segment.text.strip()}\n"
        )
    return "\n".join(blocks)


def to_vtt(segments: tuple[TranscriptionSegment, ...]) -> str:
    """WebVTT (.vtt) captions. Header + dot-separated times."""
    parts = ["WEBVTT", ""]
    for segment in segments:
        parts.append(
            f"{_vtt_timestamp(segment.start_seconds)} --> {_vtt_timestamp(segment.end_seconds)}"
        )
        parts.append(segment.text.strip())
        parts.append("")
    return "\n".join(parts)


def to_json(result: TranscriptionResult) -> str:
    """A structured JSON transcript (stable keys, 2-space indent)."""
    payload = {
        "provider_id": result.provider_id,
        "model_id": result.model_id,
        "language": result.language,
        "duration_seconds": result.duration_seconds,
        "full_text": result.full_text,
        "segments": [
            {
                "start_seconds": round(seg.start_seconds, 3),
                "end_seconds": round(seg.end_seconds, 3),
                "text": seg.text,
            }
            for seg in result.segments
        ],
        "warnings": list(result.warnings),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _clamp(seconds: float) -> float:
    return seconds if seconds > 0 else 0.0


def _split_hms_ms(seconds: float) -> tuple[int, int, int, int]:
    total_ms = int(round(_clamp(seconds) * 1000))
    hours, total_ms = divmod(total_ms, 3_600_000)
    minutes, total_ms = divmod(total_ms, 60_000)
    secs, millis = divmod(total_ms, 1000)
    return hours, minutes, secs, millis


def _srt_timestamp(seconds: float) -> str:
    h, m, s, ms = _split_hms_ms(seconds)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _vtt_timestamp(seconds: float) -> str:
    h, m, s, ms = _split_hms_ms(seconds)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
