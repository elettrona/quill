from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from quill.core.paths import app_data_dir
from quill.core.storage import read_json, write_json_atomic
from quill.platform.windows.dpapi import protect_secret, unprotect_secret

_ASSISTANT_CONNECTION_FILE = "assistant-connection.json"
_ASSISTANT_SECRET_FILE = "assistant-secret.json"


@dataclass(slots=True)
class AssistantConnectionSettings:
    provider: str = "ollama"
    host: str = "http://localhost:11434"
    model: str = "llama3.1"

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> AssistantConnectionSettings:
        provider = str(data.get("provider", "ollama")).strip().lower()
        if provider not in {"off", "ollama", "custom"}:
            provider = "ollama"
        host = str(data.get("host", "http://localhost:11434")).strip() or "http://localhost:11434"
        model = str(data.get("model", "llama3.1")).strip() or "llama3.1"
        return cls(provider=provider, host=host, model=model)


def assistant_connection_path() -> Path:
    return app_data_dir() / _ASSISTANT_CONNECTION_FILE


def assistant_secret_path() -> Path:
    return app_data_dir() / _ASSISTANT_SECRET_FILE


def load_assistant_connection_settings() -> AssistantConnectionSettings:
    raw = read_json(assistant_connection_path(), default={})
    if not isinstance(raw, dict):
        return AssistantConnectionSettings()
    return AssistantConnectionSettings.from_dict(raw)


def save_assistant_connection_settings(settings: AssistantConnectionSettings) -> None:
    write_json_atomic(assistant_connection_path(), asdict(settings))


def load_assistant_api_key() -> str:
    raw = read_json(assistant_secret_path(), default={})
    if not isinstance(raw, dict):
        return ""
    encrypted = str(raw.get("protected_secret", "")).strip()
    if not encrypted:
        return ""
    return unprotect_secret(encrypted)


def save_assistant_api_key(api_key: str) -> None:
    secret = api_key.strip()
    path = assistant_secret_path()
    if not secret:
        if path.exists():
            path.unlink()
        return
    write_json_atomic(path, {"protected_secret": protect_secret(secret)})
