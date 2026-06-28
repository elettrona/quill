"""Tests for the wx-free AI onboarding model."""

from __future__ import annotations

import quill.core.ai.onboarding as ob


def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(ob, "onboarding_state_path", lambda: tmp_path / "ai" / "onboarding.json")


def test_paths_and_providers_are_well_formed() -> None:
    ids = {p.id for p in ob.ONBOARDING_PATHS}
    assert ids == {"on_device", "cloud", "skip"}
    assert all(p.title and p.summary and p.detail for p in ob.ONBOARDING_PATHS)
    assert ob.onboarding_path("cloud").id == "cloud"
    assert ob.onboarding_path("nope") is None
    # Every cloud option maps to a real assistant_ai provider id.
    from quill.core.ai.providers import provider_requires_api_key

    for opt in ob.CLOUD_PROVIDER_OPTIONS:
        assert opt.name and opt.blurb and opt.key_hint and opt.signup_url
        assert provider_requires_api_key(opt.id)
    assert ob.cloud_provider_option("Claude").name.startswith("Claude")  # case-insensitive
    assert ob.cloud_provider_option("nope") is None


def test_celebration_lines_are_tailored() -> None:
    on_device = ob.celebration_lines("on_device")
    assert any("connected" in line.lower() for line in on_device)
    assert any("Ask Quill" in line for line in on_device)
    cloud = ob.celebration_lines("cloud", provider_name="Claude")
    assert any("Claude" in line for line in cloud)
    skip = ob.celebration_lines("skip")
    assert any("off for now" in line.lower() for line in skip)
    assert not any("Ask Quill" in line for line in skip)


def test_experience_mode_defaults_to_advanced_and_persists(tmp_path, monkeypatch) -> None:
    _isolate(tmp_path, monkeypatch)
    # Default is advanced so nothing is hidden from users who never opted into Basic.
    assert ob.load_experience_mode() == ob.EXPERIENCE_ADVANCED
    assert ob.is_basic_mode() is False
    ob.save_experience_mode(ob.EXPERIENCE_BASIC)
    assert ob.load_experience_mode() == ob.EXPERIENCE_BASIC
    assert ob.is_basic_mode() is True
    # Garbage falls back to advanced.
    ob.save_experience_mode("nonsense")
    assert ob.load_experience_mode() == ob.EXPERIENCE_ADVANCED


def test_completion_state_persists_and_resets(tmp_path, monkeypatch) -> None:
    _isolate(tmp_path, monkeypatch)
    assert ob.onboarding_complete() is False
    ob.mark_onboarding_complete()
    assert ob.onboarding_complete() is True
    ob.reset_onboarding()
    assert ob.onboarding_complete() is False


def test_ollama_status_classifies_reachability(monkeypatch) -> None:
    import quill.core.assistant_ai as aa

    # Reachable with models -> ok, returns a real installed model.
    monkeypatch.setattr(aa, "list_assistant_models", lambda *a, **k: (["gemma3:4b", "x"], None))
    ok, msg, model = ob.ollama_status()
    assert ok is True and msg == "" and model == "gemma3:4b"

    # Not running (error) -> not ok, friendly guidance, no model.
    monkeypatch.setattr(aa, "list_assistant_models", lambda *a, **k: ([], "connection refused"))
    ok, msg, model = ob.ollama_status()
    assert ok is False and "ollama.com" in msg.lower() and model == ""

    # Running but no models -> not ok, guidance to pull a model.
    monkeypatch.setattr(aa, "list_assistant_models", lambda *a, **k: ([], None))
    ok, msg, _model = ob.ollama_status()
    assert ok is False and "pull" in msg.lower()


def test_apply_cloud_setup_configures_provider_key_and_enables(monkeypatch) -> None:
    import quill.core.ai.model_manager as mm
    import quill.core.assistant_ai as aa

    saved: dict[str, object] = {}
    monkeypatch.setattr(
        aa, "save_assistant_connection_settings", lambda s: saved.update(settings=s)
    )
    monkeypatch.setattr(aa, "save_provider_api_key", lambda p, k: saved.update(key=(p, k)))
    monkeypatch.setattr(aa, "save_provider_model", lambda p, m: saved.update(model=(p, m)))
    monkeypatch.setattr(mm, "save_ai_enabled", lambda v: saved.update(enabled=v))

    ob.apply_cloud_setup("claude", "sk-test")
    assert saved["settings"].provider == "claude"
    assert saved["key"] == ("claude", "sk-test")
    assert saved["enabled"] is True
    assert saved["settings"].model  # a default model was filled in


def test_apply_on_device_setup_points_at_ollama_and_enables(monkeypatch) -> None:
    import quill.core.ai.model_manager as mm
    import quill.core.assistant_ai as aa

    saved: dict[str, object] = {}
    monkeypatch.setattr(
        aa, "save_assistant_connection_settings", lambda s: saved.update(settings=s)
    )
    monkeypatch.setattr(mm, "save_ai_enabled", lambda v: saved.update(enabled=v))

    ob.apply_on_device_setup()
    assert saved["settings"].provider == "ollama"
    assert "localhost" in saved["settings"].host
    assert saved["enabled"] is True


def test_needs_setup_only_when_incomplete_and_ai_off(tmp_path, monkeypatch) -> None:
    _isolate(tmp_path, monkeypatch)
    import quill.core.ai.model_manager as mm

    # Fresh + AI off -> offer it.
    monkeypatch.setattr(mm, "load_ai_enabled", lambda: False)
    assert ob.ai_needs_setup() is True
    # AI already on -> never nag.
    monkeypatch.setattr(mm, "load_ai_enabled", lambda: True)
    assert ob.ai_needs_setup() is False
    # Completed -> never nag, even with AI off.
    monkeypatch.setattr(mm, "load_ai_enabled", lambda: False)
    ob.mark_onboarding_complete()
    assert ob.ai_needs_setup() is False
