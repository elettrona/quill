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
        assert opt.tagline  # short trade-off spoken in the radio label
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


def test_models_for_engine_lists_catalog_with_a_recommendation() -> None:
    cpp = gs.models_for_engine("whispercpp")
    fw = gs.models_for_engine("faster-whisper")
    assert cpp and fw
    # Smallest first, and exactly one best-fit recommendation each.
    assert cpp[0].model_id == gs.default_model_id("whispercpp")
    assert sum(1 for m in cpp if m.recommended) == 1
    for m in cpp:
        assert m.display_name and m.size_text and m.summary
    # The two engines have distinct catalogs.
    assert {m.model_id for m in cpp} != {m.model_id for m in fw}


def test_default_model_is_the_smallest_for_a_fast_start() -> None:
    # "default to tiny so they're going immediately" -- the first (smallest) model.
    assert gs.default_model_id("whispercpp") == "tiny"


def test_models_for_engine_never_crashes_on_detection_failure(monkeypatch) -> None:
    from quill.core.speech import service

    monkeypatch.setattr(
        service, "detect_total_ram_gb", lambda: (_ for _ in ()).throw(RuntimeError())
    )
    models = gs.models_for_engine("whispercpp")  # must not raise
    assert models and sum(1 for m in models if m.recommended) == 1
