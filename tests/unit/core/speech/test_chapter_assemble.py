"""Unit tests for chaptered audio assembly (batch-document-to-speech §4.8.5-§4.8.6).

These run fully headless: a fake synthesizer writes silent WAVs of a controlled
length, so the concat / gap / earcon / chapter-tagging wiring is proven without
any TTS engine or ffmpeg. WAV output is used so no transcode is needed.
"""

from __future__ import annotations

import wave
from pathlib import Path

import pytest

from quill.core.speech.chapter_assemble import (
    AssembleError,
    ChapterAssembleOptions,
    assemble_chaptered_audio,
)
from quill.core.speech.earcon import DEFAULT_SAMPLE_RATE, PcmFormat, sounder_duration_ms
from quill.core.speech.text_polish import DocumentSection

_FMT = PcmFormat()


def make_fake_synth(ms_per_word: int = 200, min_ms: int = 200):
    """A synth that writes silence proportional to the word count of the text."""

    def _synth(text: str, out: Path) -> None:
        ms = max(min_ms, len(text.split()) * ms_per_word)
        n = int(_FMT.sample_rate * ms / 1000)
        out.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out), "wb") as w:
            w.setnchannels(_FMT.channels)
            w.setsampwidth(_FMT.sampwidth)
            w.setframerate(_FMT.sample_rate)
            w.writeframes(b"\x00" * (n * _FMT.sampwidth * _FMT.channels))

    return _synth


def _wav_ms(path: Path) -> int:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() * 1000 // w.getframerate()


def _sections() -> list[DocumentSection]:
    return [
        DocumentSection("", "lead in words here"),  # 4 words -> 800 ms
        DocumentSection("Article One", "one two three"),  # 3 -> 600 ms
        DocumentSection("Article Two", "a b c d e"),  # 5 -> 1000 ms
    ]


def test_clean_chapter_offsets_no_sound(tmp_path: Path) -> None:
    opts = ChapterAssembleOptions(article_gap_ms=500, sound_enabled=False, output_format="wav")
    r = assemble_chaptered_audio(
        _sections(), tmp_path / "out.wav", make_fake_synth(), opts, work_dir=tmp_path / "w"
    )
    assert r.section_count == 3
    assert r.with_tones_path is None
    assert [(c.title, c.start_ms, c.end_ms) for c in r.chapters] == [
        ("Introduction", 0, 1300),  # 800 + 500 gap
        ("Article One", 1300, 2400),  # 600 + 500 gap
        ("Article Two", 2400, 3400),  # 1000, no trailing gap
    ]
    assert _wav_ms(r.output_path) == 3400


def test_empty_heading_uses_intro_title(tmp_path: Path) -> None:
    opts = ChapterAssembleOptions(
        article_gap_ms=0, sound_enabled=False, output_format="wav", intro_section_title="Front Page"
    )
    r = assemble_chaptered_audio(
        _sections(), tmp_path / "o.wav", make_fake_synth(), opts, work_dir=tmp_path / "w"
    )
    assert r.chapters[0].title == "Front Page"


def test_with_tones_variant_has_identical_timing(tmp_path: Path) -> None:
    opts = ChapterAssembleOptions(
        article_gap_ms=500, sound_enabled=True, sound_volume=80, output_format="wav"
    )
    r = assemble_chaptered_audio(
        _sections(), tmp_path / "out.wav", make_fake_synth(), opts, work_dir=tmp_path / "w"
    )
    assert r.with_tones_path is not None
    assert r.with_tones_path.name == "out (with chapter tones).wav"
    # clean and with-tones must be byte-for-byte the same length
    assert _wav_ms(r.output_path) == _wav_ms(r.with_tones_path)
    # effective gap folds in the earcon length
    earcon = sounder_duration_ms(_FMT)
    assert r.chapters[0].end_ms == 800 + 500 + earcon


def test_chapters_are_contiguous(tmp_path: Path) -> None:
    opts = ChapterAssembleOptions(article_gap_ms=750, sound_enabled=True, output_format="wav")
    r = assemble_chaptered_audio(
        _sections(), tmp_path / "o.wav", make_fake_synth(), opts, work_dir=tmp_path / "w"
    )
    for prev, nxt in zip(r.chapters, r.chapters[1:], strict=False):
        assert prev.end_ms == nxt.start_ms
    # The last chapter ends at (approximately) the end of the audio. Per-section
    # millisecond floor-rounding can accumulate a few ms vs the whole-file length;
    # markers within that tolerance are frame-accurate for navigation.
    assert 0 <= _wav_ms(r.output_path) - r.chapters[-1].end_ms <= len(r.chapters)


def test_wav_output_writes_chapter_sidecar(tmp_path: Path) -> None:
    opts = ChapterAssembleOptions(article_gap_ms=300, output_format="wav")
    r = assemble_chaptered_audio(
        _sections(), tmp_path / "o.wav", make_fake_synth(), opts, work_dir=tmp_path / "w"
    )
    sidecar = r.output_path.with_suffix(".chapters.txt")
    assert sidecar.is_file()
    lines = sidecar.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    assert lines[0].split("\t")[2] == "Introduction"


def test_heading_only_section_speaks_its_title(tmp_path: Path) -> None:
    secs = [DocumentSection("Chapter With No Body", "")]
    opts = ChapterAssembleOptions(article_gap_ms=0, output_format="wav")
    r = assemble_chaptered_audio(
        secs, tmp_path / "o.wav", make_fake_synth(), opts, work_dir=tmp_path / "w"
    )
    assert r.chapters[0].title == "Chapter With No Body"
    assert _wav_ms(r.output_path) > 0  # the title was spoken, so there is audio


def test_empty_sections_raises(tmp_path: Path) -> None:
    with pytest.raises(AssembleError):
        assemble_chaptered_audio(
            [], tmp_path / "o.wav", make_fake_synth(), ChapterAssembleOptions(), work_dir=tmp_path
        )


def test_mismatched_section_format_raises(tmp_path: Path) -> None:
    def bad_synth(text: str, out: Path) -> None:
        # second section at a different sample rate than the first
        rate = DEFAULT_SAMPLE_RATE if "one" in text else 8000
        out.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(b"\x00" * (rate // 2 * 2))

    secs = [DocumentSection("One", "one"), DocumentSection("Two", "two")]
    with pytest.raises(AssembleError):
        assemble_chaptered_audio(
            secs, tmp_path / "o.wav", bad_synth, ChapterAssembleOptions(), work_dir=tmp_path / "w"
        )
