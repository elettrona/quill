from __future__ import annotations

from pathlib import Path

import pytest

import quill.core.assistant_ai as assistant_ai


def test_assistant_connection_settings_round_trip(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))

    assistant_ai.save_assistant_connection_settings(
        assistant_ai.AssistantConnectionSettings(
            provider="custom",
            host="http://127.0.0.1:11434",
            model="qwen2.5",
        )
    )

    loaded = assistant_ai.load_assistant_connection_settings()

    assert loaded.provider == "custom"
    assert loaded.host == "http://127.0.0.1:11434"
    assert loaded.model == "qwen2.5"


def test_assistant_api_key_is_protected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(assistant_ai, "protect_secret", lambda secret: f"enc:{secret}")
    monkeypatch.setattr(
        assistant_ai,
        "unprotect_secret",
        lambda secret: secret.removeprefix("enc:"),
    )

    assistant_ai.save_assistant_api_key("secret-value")

    assert assistant_ai.load_assistant_api_key() == "secret-value"
