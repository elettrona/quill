"""Speech service facade (#617).

A thin, testable seam between the UI and the providers: builds the default
registry (lazily registering the whisper.cpp provider) and turns a provider's
model list into accessible, ready-to-display rows. Keeping this logic here (not
in the wx dialog) means the model-manager content is unit-testable.
"""

from __future__ import annotations

from dataclasses import dataclass

from quill.core.speech.provider import SpeechToTextProvider
from quill.core.speech.registry import SpeechProviderRegistry

DEFAULT_PROVIDER_ID = "whispercpp"


def default_registry(executable_path: str | None = None) -> SpeechProviderRegistry:
    """Return a registry with the built-in providers registered (lazy import)."""
    registry = SpeechProviderRegistry()
    from quill.core.speech.providers.whispercpp import WhisperCppProvider

    registry.register(WhisperCppProvider(executable_path))
    return registry


@dataclass(frozen=True, slots=True)
class ModelRow:
    """One accessible row for the model-manager list."""

    id: str
    installed: bool
    label: str


def _size_text(mb: int) -> str:
    if mb >= 1000:
        return f"{mb / 1000:.1f} GB"
    return f"{mb} MB"


def describe_models(provider: SpeechToTextProvider) -> list[ModelRow]:
    """Build accessible model rows (installed status first, then size/accuracy)."""
    installed_ids = {m.id for m in provider.list_installed_models()}
    rows: list[ModelRow] = []
    for info in provider.list_supported_models():
        installed = info.id in installed_ids
        state = "Installed" if installed else "Not installed"
        label = (
            f"{info.display_name} — {state} — {_size_text(info.approximate_size_mb)} "
            f"download — {info.accuracy_tier} accuracy, {info.speed_tier} speed. "
            f"{info.recommended_use}"
        )
        rows.append(ModelRow(id=info.id, installed=installed, label=label))
    return rows
