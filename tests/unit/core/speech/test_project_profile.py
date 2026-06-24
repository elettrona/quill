"""Unit tests for the speech project profile (batch-document-to-speech §4.10)."""

from __future__ import annotations

from pathlib import Path

from quill.core.speech.project_profile import (
    ChapterProfile,
    DictionaryRef,
    OutputProfile,
    PronunciationProfile,
    SpeechProjectProfile,
    SynthesizerProfile,
    load_profile,
    profile_path,
    save_profile,
    to_batch_options,
    to_chapter_options,
)


def _full_profile() -> SpeechProjectProfile:
    return SpeechProjectProfile(
        synthesizer=SynthesizerProfile(
            engine="piper",
            voice="en_US-amy",
            rate=210,
            extra={"piper_model": "C:/m/amy.onnx", "piper_executable": "C:/p/piper.exe"},
        ),
        output=OutputProfile(format="mp3", skip_existing=True),
        chapters=ChapterProfile(
            mode="single", sound_enabled=True, sound_volume=80, article_gap_ms=1500
        ),
        normalization={"dash_mode": "words"},
        pronunciation=PronunciationProfile(
            enabled=True,
            dictionaries=[
                DictionaryRef(id="news", scope="project", path=".quill/pronunciation/news.json"),
                DictionaryRef(id="tech", scope="global"),
            ],
        ),
    )


def test_round_trips_through_dict() -> None:
    p = _full_profile()
    assert SpeechProjectProfile.from_dict(p.to_dict()) == p


def test_save_and_load(tmp_path: Path) -> None:
    p = _full_profile()
    path = save_profile(p, tmp_path)
    assert path == profile_path(tmp_path)
    assert path.is_file()
    assert path.parent.name == ".quill"
    assert load_profile(tmp_path) == p


def test_load_missing_returns_none(tmp_path: Path) -> None:
    assert load_profile(tmp_path) is None


def test_defaults_are_sane() -> None:
    p = SpeechProjectProfile()
    assert p.version == 1
    assert p.synthesizer.engine == "sapi5"
    assert p.output.format == "wav"
    assert p.chapters.mode == "none"
    assert p.pronunciation.enabled is True
    assert p.pronunciation.dictionaries == []


def test_from_dict_clamps_and_falls_back() -> None:
    p = SpeechProjectProfile.from_dict({
        "version": 1,
        "synthesizer": {"engine": "bogus", "rate": 99999, "volume": 5, "speed": -1},
        "output": {"format": "flac"},
        "chapters": {"mode": "weird", "sound_volume": 500, "article_gap_ms": -10},
        "pronunciation": {
            "dictionaries": [
                {"scope": "x", "format": "y"},  # no id -> dropped
                {"id": "ok", "scope": "x", "format": "y"},  # bad scope/format -> defaults
            ]
        },
    })
    assert p.synthesizer.engine == "sapi5"
    assert p.synthesizer.rate == 800  # clamped
    assert p.synthesizer.volume == 1.0  # clamped
    assert p.synthesizer.speed == 0.25  # clamped
    assert p.output.format == "wav"
    assert p.chapters.mode == "none"
    assert p.chapters.sound_volume == 100
    assert p.chapters.article_gap_ms == 0
    assert [d.id for d in p.pronunciation.dictionaries] == ["ok"]
    assert p.pronunciation.dictionaries[0].scope == "global"
    assert p.pronunciation.dictionaries[0].format == "quill-json"


def test_from_dict_tolerates_garbage() -> None:
    assert SpeechProjectProfile.from_dict({}) == SpeechProjectProfile()
    # Non-dict sub-objects are ignored, not fatal.
    p = SpeechProjectProfile.from_dict({"synthesizer": "nope", "chapters": 5})
    assert p.synthesizer.engine == "sapi5"
    assert p.chapters.mode == "none"


def test_to_batch_options_piper(tmp_path: Path) -> None:
    opts = to_batch_options(_full_profile(), tmp_path / "src", tmp_path / "out")
    assert opts.engine == "piper"
    assert opts.output_format == "mp3"
    assert opts.skip_existing is True
    assert opts.piper_model == Path("C:/m/amy.onnx")
    assert opts.piper_executable == Path("C:/p/piper.exe")


def test_to_batch_options_sapi5(tmp_path: Path) -> None:
    profile = SpeechProjectProfile(
        synthesizer=SynthesizerProfile(engine="sapi5", voice="David", rate=180, volume=0.8)
    )
    opts = to_batch_options(profile, tmp_path / "s", tmp_path / "o")
    assert opts.engine == "sapi5"
    assert opts.sapi5_voice == "David"
    assert opts.sapi5_rate == 180
    assert opts.sapi5_volume == 0.8


def test_to_chapter_options() -> None:
    co = to_chapter_options(_full_profile())
    assert co.article_gap_ms == 1500
    assert co.sound_enabled is True
    assert co.sound_volume == 80
    assert co.output_format == "mp3"
