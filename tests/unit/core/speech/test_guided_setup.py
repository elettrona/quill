from __future__ import annotations

import quill.core.speech.guided_setup as gs


def test_offline_speech_engine_options_lists_both_recommended_first() -> None:
    opts = gs.offline_speech_engine_options()
    ids = [o.engine_id for o in opts]
    assert ids == ["whispercpp", "faster-whisper"]
    # whisper.cpp is the friendly default and always installable (release asset).
    whispercpp = opts[0]
    assert whispercpp.recommended is True
    assert whispercpp.install_supported is True
    # Every option carries a plain-language explanation for the picker.
    for opt in opts:
        assert opt.name
        assert len(opt.summary) > 20


def test_engine_options_never_crash_on_detector_failure(monkeypatch) -> None:
    def boom() -> bool:
        raise RuntimeError("detector exploded")

    monkeypatch.setattr(gs, "_whispercpp_installed", boom)
    monkeypatch.setattr(gs, "_faster_whisper_installed", boom)
    opts = gs.offline_speech_engine_options()  # must not raise
    assert all(o.installed is False for o in opts)


def test_recommended_engine_prefers_an_installed_one_else_whispercpp(monkeypatch) -> None:
    # Nothing installed -> the friendly default.
    monkeypatch.setattr(gs, "_whispercpp_installed", lambda: False)
    monkeypatch.setattr(gs, "_faster_whisper_installed", lambda: False)
    assert gs.recommended_engine_id() == "whispercpp"

    # Faster Whisper already installed -> keep the user on what they have.
    monkeypatch.setattr(gs, "_faster_whisper_installed", lambda: True)
    assert gs.recommended_engine_id() == "faster-whisper"
