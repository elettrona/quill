"""ACX loudness measurement and one-click normalization (§1.5 audiobook).

Audiobook platforms (ACX / Audible) require each delivered file to sit in a narrow
loudness window: integrated **RMS between -23 dB and -18 dB**, **peak no higher than
-3 dB**, and a noise floor below -60 dB RMS. This module measures a finished master
with ffmpeg's ``volumedetect`` filter and reports whether it meets the ACX window;
the one-click fix re-encodes through ffmpeg's ``loudnorm`` filter (applied during the
audiobook build) to pull RMS and true-peak into range in a single pass.

wx-free, strict-typed. Only the RMS and peak constraints are evaluated and fixed
automatically — the noise-floor requirement depends on the source recording quality
and is left to the author's judgement.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# ACX delivery window, in decibels relative to full scale.
ACX_RMS_MIN = -23.0
ACX_RMS_MAX = -18.0
ACX_PEAK_MAX = -3.0
# The one-click fix aims for the middle of the RMS window with true-peak just under
# the ceiling. ``loudnorm`` works in LUFS / dBTP, a close proxy for ACX's RMS/peak.
ACX_TARGET_RMS = -20.0
ACX_TARGET_TP = -3.1
ACX_TARGET_LRA = 11.0

_MEAN_RE = re.compile(r"mean_volume:\s*(-?\d+(?:\.\d+)?)\s*dB")
_MAX_RE = re.compile(r"max_volume:\s*(-?\d+(?:\.\d+)?)\s*dB")


@dataclass(slots=True)
class LoudnessStats:
    """Measured integrated RMS (``mean_db``) and peak (``max_db``) of one file."""

    mean_db: float
    max_db: float

    @property
    def rms_ok(self) -> bool:
        return ACX_RMS_MIN <= self.mean_db <= ACX_RMS_MAX

    @property
    def peak_ok(self) -> bool:
        return self.max_db <= ACX_PEAK_MAX

    @property
    def acx_compliant(self) -> bool:
        return self.rms_ok and self.peak_ok

    def summary(self) -> str:
        """A one-line, speakable verdict for the status bar / a screen reader."""
        rms = f"RMS {self.mean_db:.1f} dB"
        peak = f"peak {self.max_db:.1f} dB"
        if self.acx_compliant:
            return f"Output is within ACX loudness range ({rms}, {peak})."
        problems: list[str] = []
        if not self.rms_ok:
            problems.append(f"{rms} is outside ACX's -23 to -18 dB")
        if not self.peak_ok:
            problems.append(f"{peak} exceeds the -3 dB ceiling")
        tail = " — rebuild with Normalize to ACX loudness enabled."
        return "; ".join(problems) + tail


def loudnorm_filter() -> str:
    """The ffmpeg ``loudnorm`` filter string that targets the ACX window."""
    return f"loudnorm=I={ACX_TARGET_RMS}:TP={ACX_TARGET_TP}:LRA={ACX_TARGET_LRA}"


def build_volumedetect_command(ffmpeg: str, path: Path) -> list[str]:
    """ffmpeg argv that prints a file's mean/max volume (to stderr), decoding to null."""
    return [
        ffmpeg,
        "-hide_banner",
        "-nostats",
        "-i",
        str(path),
        "-vn",
        "-af",
        "volumedetect",
        "-f",
        "null",
        "-",
    ]


def parse_volumedetect(stderr: str) -> LoudnessStats | None:
    """Parse ``mean_volume`` / ``max_volume`` from ffmpeg ``volumedetect`` output."""
    mean = _MEAN_RE.search(stderr or "")
    peak = _MAX_RE.search(stderr or "")
    if not mean or not peak:
        return None
    return LoudnessStats(mean_db=float(mean.group(1)), max_db=float(peak.group(1)))


def measure_loudness(path: Path, *, timeout_seconds: float = 600.0) -> LoudnessStats | None:
    """Measure *path*'s loudness via ffmpeg ``volumedetect`` (None when unavailable).

    Decodes the whole file, so callers run it on the background task pool, never on
    the UI thread. Returns ``None`` if ffmpeg is missing, the file is absent, or the
    output could not be parsed.
    """
    from quill.core.speech.ffmpeg import find_ffmpeg
    from quill.stability.safe_subprocess import run_subprocess_safely

    ffmpeg = find_ffmpeg()
    if ffmpeg is None or not path.is_file():
        return None
    try:
        completed = run_subprocess_safely(
            build_volumedetect_command(ffmpeg, path), timeout_seconds=timeout_seconds
        )
    except OSError:
        return None
    # volumedetect prints its histogram to stderr; safe_subprocess captures it.
    return parse_volumedetect(completed.stderr or "")
