"""Tests for ACX loudness measurement/parsing and the loudnorm filter (§1.5)."""

from __future__ import annotations

from quill.core.speech.loudness import (
    ACX_PEAK_MAX,
    ACX_RMS_MAX,
    ACX_RMS_MIN,
    LoudnessStats,
    build_volumedetect_command,
    loudnorm_filter,
    parse_volumedetect,
)

_SAMPLE = """
[Parsed_volumedetect_0 @ 0x55] n_samples: 123456
[Parsed_volumedetect_0 @ 0x55] mean_volume: -20.4 dB
[Parsed_volumedetect_0 @ 0x55] max_volume: -3.6 dB
[Parsed_volumedetect_0 @ 0x55] histogram_0db: 1
"""


def test_parse_volumedetect_reads_mean_and_peak() -> None:
    stats = parse_volumedetect(_SAMPLE)
    assert stats is not None
    assert stats.mean_db == -20.4
    assert stats.max_db == -3.6
    assert stats.acx_compliant  # -20.4 in [-23,-18], -3.6 <= -3


def test_parse_volumedetect_none_when_absent() -> None:
    assert parse_volumedetect("no volume data here") is None


def test_loudness_stats_flags_out_of_range() -> None:
    # Too loud: RMS above the -18 ceiling and peak above -3.
    loud = LoudnessStats(mean_db=-12.0, max_db=-1.0)
    assert not loud.rms_ok and not loud.peak_ok and not loud.acx_compliant
    assert "exceeds" in loud.summary() and "Normalize to ACX" in loud.summary()

    # In range.
    ok = LoudnessStats(mean_db=ACX_RMS_MIN + 1.0, max_db=ACX_PEAK_MAX - 1.0)
    assert ok.acx_compliant and "within acx" in ok.summary().lower()

    # Edge values are inclusive.
    edge = LoudnessStats(mean_db=ACX_RMS_MAX, max_db=ACX_PEAK_MAX)
    assert edge.acx_compliant


def test_volumedetect_command_shape() -> None:
    from pathlib import Path

    cmd = build_volumedetect_command("ffmpeg", Path("book.m4b"))
    assert cmd[0] == "ffmpeg"
    assert "volumedetect" in cmd
    assert cmd[-2:] == ["-f", "null"] or cmd[-1] == "-"
    assert "book.m4b" in cmd


def test_loudnorm_filter_targets_acx_window() -> None:
    flt = loudnorm_filter()
    assert flt.startswith("loudnorm=")
    # Target RMS sits inside the ACX window and true-peak under the ceiling.
    assert "I=-20.0" in flt
    assert "TP=-3.1" in flt
    assert ACX_RMS_MIN < -20.0 < ACX_RMS_MAX
