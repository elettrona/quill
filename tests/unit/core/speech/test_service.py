from __future__ import annotations

from pathlib import Path

from quill.core.speech import service
from quill.core.speech.provider import InstalledSpeechModel, SpeechModelInfo


class _Provider:
    id = "whispercpp"

    def __init__(self, installed: list[str]) -> None:
        self._installed = installed

    def list_supported_models(self) -> list[SpeechModelInfo]:
        return [
            SpeechModelInfo(
                id="small",
                display_name="Small",
                language_mode="multilingual",
                approximate_size_mb=465,
                accuracy_tier="medium",
                speed_tier="medium",
                recommended_use="Recommended starting point.",
            ),
            SpeechModelInfo(
                id="large-v3",
                display_name="Large (v3)",
                language_mode="multilingual",
                approximate_size_mb=3100,
                accuracy_tier="highest",
                speed_tier="slow",
                recommended_use="Best local quality.",
            ),
        ]

    def list_installed_models(self) -> list[InstalledSpeechModel]:
        return [
            InstalledSpeechModel(
                id=m, display_name=m, path=Path(m), size_mb=0, provider_id="whispercpp"
            )
            for m in self._installed
        ]


def test_default_registry_has_whispercpp() -> None:
    registry = service.default_registry()
    assert registry.get(service.DEFAULT_PROVIDER_ID) is not None


def test_describe_models_marks_installed_and_sizes() -> None:
    rows = service.describe_models(_Provider(installed=["small"]))
    by_id = {r.id: r for r in rows}
    assert by_id["small"].installed is True
    assert "Installed" in by_id["small"].label
    assert "465 MB download" in by_id["small"].label
    assert by_id["large-v3"].installed is False
    assert "Not installed" in by_id["large-v3"].label
    assert "3.1 GB download" in by_id["large-v3"].label
