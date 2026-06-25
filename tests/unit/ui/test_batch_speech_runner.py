"""Headless tests for batch_speech_runner helpers (no wx app needed)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from quill.ui.batch_speech_runner import _resolve_chapter_sound_path


def _frame(sound_id: str, pack_path: str = "") -> SimpleNamespace:
    return SimpleNamespace(
        settings=SimpleNamespace(batch_speech_chapter_sound_id=sound_id, sound_pack_path=pack_path)
    )


def test_resolve_chapter_sound_from_bundled_ink(tmp_path: Path) -> None:
    # An event id present in the bundled Ink pack resolves to a real WAV on disk.
    out = _resolve_chapter_sound_path(_frame("transcription_started"), tmp_path)
    assert out is not None
    assert out.exists() and out.suffix == ".wav"
    assert out.stat().st_size > 0


def test_resolve_chapter_sound_none_when_unset(tmp_path: Path) -> None:
    assert _resolve_chapter_sound_path(_frame(""), tmp_path) is None


def test_resolve_chapter_sound_none_for_unknown_id(tmp_path: Path) -> None:
    assert _resolve_chapter_sound_path(_frame("no_such_event_id"), tmp_path) is None


def _req(folder: Path, **overrides: object):
    from quill.ui.batch_speech_export_dialog import BatchSpeechRequest

    base = dict(
        source_folder=folder,
        recursive=False,
        extensions=(".md",),
        engine="sapi5",
        voice="",
        rate=200,
        speed=1.0,
        output_format="mp3",
        sound_enabled=False,
        sound_volume=100,
        article_gap_ms=1200,
        sentence_gap_ms=0,
        tail_padding_ms=300,
        speak_headings=True,
        skip_existing=False,
    )
    base.update(overrides)
    return BatchSpeechRequest(**base)  # type: ignore[arg-type]


def test_project_profile_save_then_apply_round_trips(tmp_path: Path) -> None:
    from quill.ui.batch_speech_runner import _apply_project_profile, _save_project_profile

    chosen = _req(
        tmp_path,
        engine="kokoro",
        voice="am_liam",
        rate=190,
        speed=1.1,
        output_format="m4b",
        sound_enabled=True,
        sound_volume=70,
        article_gap_ms=900,
        chapter_mode="separate",
        combine_headings=True,
        round_robin_voices=("am_liam", "af_heart"),
    )
    _save_project_profile(SimpleNamespace(), chosen)  # writes <tmp_path>/.quill/speech-project.json
    assert (tmp_path / ".quill" / "speech-project.json").is_file()

    # A frame whose active document lives in tmp_path pre-fills from that profile.
    frame = SimpleNamespace(_active_document_path=lambda: str(tmp_path / "doc.md"))
    applied = _apply_project_profile(frame, _req(tmp_path))  # global defaults overlaid
    assert applied.engine == "kokoro" and applied.voice == "am_liam"
    assert applied.output_format == "m4b" and applied.chapter_mode == "separate"
    assert applied.sound_enabled is True and applied.article_gap_ms == 900
    assert applied.combine_headings is True
    assert applied.round_robin_voices == ("am_liam", "af_heart")


def test_apply_project_profile_no_profile_keeps_defaults(tmp_path: Path) -> None:
    from quill.ui.batch_speech_runner import _apply_project_profile

    frame = SimpleNamespace(_active_document_path=lambda: str(tmp_path / "doc.md"))
    defaults = _req(tmp_path, engine="sapi5", output_format="mp3")
    applied = _apply_project_profile(frame, defaults)
    assert applied.engine == "sapi5" and applied.output_format == "mp3"
