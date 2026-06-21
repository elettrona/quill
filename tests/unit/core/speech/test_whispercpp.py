from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from quill.core.speech import models
from quill.core.speech.provider import SpeechError, TranscriptionRequest
from quill.core.speech.providers import whispercpp

_SAMPLE_JSON = json.dumps({
    "result": {"language": "en"},
    "transcription": [
        {"offsets": {"from": 0, "to": 2500}, "text": " Hello world"},
        {"offsets": {"from": 2500, "to": 4000}, "text": " second line"},
    ],
})


@pytest.fixture(autouse=True)
def _isolated_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(models, "app_data_dir", lambda: tmp_path)


# --- pure helpers ---------------------------------------------------------- #


def test_parse_whisper_json() -> None:
    result = whispercpp.parse_whisper_json(_SAMPLE_JSON)
    assert result.full_text == "Hello world second line"
    assert result.language == "en"
    assert len(result.segments) == 2
    assert result.segments[0].start_seconds == 0.0
    assert result.segments[0].end_seconds == 2.5
    assert result.duration_seconds == 4.0


def test_parse_whisper_json_bad_input_raises() -> None:
    with pytest.raises(SpeechError):
        whispercpp.parse_whisper_json("{ not json")


def test_build_whisper_command_includes_flags(tmp_path: Path) -> None:
    request = TranscriptionRequest(
        source_path=tmp_path / "a.wav",
        model_id="small",
        language="en",
        translate_to_english=True,
    )
    args = whispercpp.build_whisper_command(
        "whisper-cli", tmp_path / "ggml-small.bin", tmp_path / "a.wav", tmp_path / "out", request
    )
    assert args[0] == "whisper-cli"
    assert "-oj" in args
    assert args[args.index("-l") + 1] == "en"
    assert "-tr" in args


def test_resolve_executable_honors_allowed_configured(tmp_path: Path) -> None:
    exe = tmp_path / "whisper-cli"
    exe.write_text("", encoding="utf-8")
    assert whispercpp.resolve_whisper_executable(str(exe)) == str(exe)


def test_resolve_executable_rejects_disallowed_basename(tmp_path: Path) -> None:
    evil = tmp_path / "rm-rf"
    evil.write_text("", encoding="utf-8")
    assert whispercpp.resolve_whisper_executable(str(evil)) is None


def test_resolve_executable_finds_bundled_under_app_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(whispercpp.shutil, "which", lambda _name: None)
    bundled = tmp_path / "app" / "tools" / "speech" / "whispercpp"
    bundled.mkdir(parents=True)
    exe = bundled / "whisper-cli.exe"
    exe.write_text("", encoding="utf-8")
    monkeypatch.setenv("QUILL_APP_ROOT", str(tmp_path / "app"))
    assert whispercpp.resolve_whisper_executable() == str(exe)


def test_resolve_executable_finds_downloaded_engine(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(whispercpp.shutil, "which", lambda _name: None)
    monkeypatch.delenv("QUILL_APP_ROOT", raising=False)
    engine_dir = tmp_path / "speech-engine"
    engine_dir.mkdir(parents=True)
    exe = engine_dir / "whisper-cli"
    exe.write_text("", encoding="utf-8")
    assert whispercpp.resolve_whisper_executable() == str(exe)


def test_resolve_executable_uses_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        whispercpp.shutil,
        "which",
        lambda name: "/usr/bin/whisper-cli" if name == "whisper-cli" else None,
    )
    assert whispercpp.resolve_whisper_executable() == "/usr/bin/whisper-cli"


# --- provider behavior ----------------------------------------------------- #


def test_get_install_status_when_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(whispercpp.shutil, "which", lambda _name: None)
    provider = whispercpp.WhisperCppProvider()
    assert provider.is_available() is False
    assert provider.get_install_status().installed is False


def test_download_blocked_in_safe_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QUILL_SAFE_MODE", "1")
    provider = whispercpp.WhisperCppProvider()
    with pytest.raises(SpeechError, match="Safe Mode"):
        provider.download_model("small")


def test_download_records_model(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("QUILL_SAFE_MODE", raising=False)

    def _fake_download(info, target, progress):
        Path(target).write_bytes(b"FAKEMODEL")

    monkeypatch.setattr(whispercpp, "_download_to_file", _fake_download)
    provider = whispercpp.WhisperCppProvider()
    installed = provider.download_model("small")
    assert installed.id == "small"
    assert installed.path.exists()
    assert provider.list_installed_models()[0].id == "small"


def test_transcribe_requires_installed_model(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(whispercpp.shutil, "which", lambda _name: "/usr/bin/whisper-cli")
    provider = whispercpp.WhisperCppProvider()
    audio = tmp_path / "a.wav"
    audio.write_bytes(b"RIFF")
    with pytest.raises(SpeechError, match="not installed"):
        provider.transcribe_file(TranscriptionRequest(source_path=audio, model_id="small"))


def test_transcribe_runs_and_parses(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(whispercpp.shutil, "which", lambda _name: "/usr/bin/whisper-cli")
    # Install a fake model file.
    model_path = whispercpp._model_path("small")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_bytes(b"FAKE")
    audio = tmp_path / "a.wav"
    audio.write_bytes(b"RIFF")

    def _fake_run(args, *, timeout_seconds=0.0, cwd=None):
        # whisper writes <output_base>.json; -of is the arg after the flag.
        out_base = Path(args[args.index("-of") + 1])
        out_base.with_suffix(".json").write_text(_SAMPLE_JSON, encoding="utf-8")
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    import quill.stability.safe_subprocess as ssp

    monkeypatch.setattr(ssp, "run_subprocess_safely", _fake_run)

    provider = whispercpp.WhisperCppProvider()
    result = provider.transcribe_file(TranscriptionRequest(source_path=audio, model_id="small"))
    assert result.full_text == "Hello world second line"
    assert result.model_id == "small"
