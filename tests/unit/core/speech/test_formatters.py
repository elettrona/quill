from __future__ import annotations

import json

from quill.core.speech import formatters
from quill.core.speech.provider import TranscriptionResult, TranscriptionSegment

_SEGMENTS = (
    TranscriptionSegment(0.0, 2.5, "Hello world"),
    TranscriptionSegment(2.5, 3661.789, "Much later"),
)
_RESULT = TranscriptionResult(
    full_text="Hello world Much later",
    segments=_SEGMENTS,
    provider_id="whispercpp",
    model_id="small",
    language="en",
    duration_seconds=3661.789,
)


def test_plain_text_strips_and_adds_newline() -> None:
    result = TranscriptionResult(full_text="  hi there  ")
    assert formatters.to_plain_text(result) == "hi there\n"


def test_srt_indices_and_comma_timestamps() -> None:
    srt = formatters.to_srt(_SEGMENTS)
    assert srt.startswith("1\n00:00:00,000 --> 00:00:02,500\nHello world\n")
    assert "2\n00:00:02,500 --> 01:01:01,789\nMuch later\n" in srt


def test_vtt_header_and_dot_timestamps() -> None:
    vtt = formatters.to_vtt(_SEGMENTS)
    assert vtt.startswith("WEBVTT\n")
    assert "00:00:00.000 --> 00:00:02.500" in vtt
    assert "01:01:01.789" in vtt


def test_json_is_structured_and_round_trips() -> None:
    payload = json.loads(formatters.to_json(_RESULT))
    assert payload["model_id"] == "small"
    assert payload["language"] == "en"
    assert payload["full_text"] == "Hello world Much later"
    assert payload["segments"][0] == {
        "start_seconds": 0.0,
        "end_seconds": 2.5,
        "text": "Hello world",
    }


def test_negative_time_clamps_to_zero() -> None:
    srt = formatters.to_srt((TranscriptionSegment(-1.0, 1.0, "x"),))
    assert "00:00:00,000 --> 00:00:01,000" in srt
