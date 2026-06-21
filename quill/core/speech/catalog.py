"""Curated whisper.cpp model catalog (#617 section 5.2).

Data-driven model tiers with approximate sizes and accessible speed/accuracy/use
descriptions. URLs and hashes are intentionally left for the provider/release
pipeline to fill in (kept data-driven per #617 section 17); this module is the
single place the model manager reads its menu of models from.
"""

from __future__ import annotations

from quill.core.speech.provider import SpeechModelInfo

RECOMMENDED_MODEL_ID = "small"

WHISPER_CPP_MODELS: tuple[SpeechModelInfo, ...] = (
    SpeechModelInfo(
        id="tiny",
        display_name="Tiny",
        language_mode="multilingual",
        approximate_size_mb=75,
        accuracy_tier="low",
        speed_tier="fast",
        recommended_use="Smallest download. Good for testing and simple voice commands.",
    ),
    SpeechModelInfo(
        id="base",
        display_name="Base",
        language_mode="multilingual",
        approximate_size_mb=145,
        accuracy_tier="low",
        speed_tier="fast",
        recommended_use="Small download. Better than Tiny; good for quick notes.",
    ),
    SpeechModelInfo(
        id="small",
        display_name="Small",
        language_mode="multilingual",
        approximate_size_mb=465,
        accuracy_tier="medium",
        speed_tier="medium",
        recommended_use="Recommended starting point: solid transcription without a huge download.",
    ),
    SpeechModelInfo(
        id="medium",
        display_name="Medium",
        language_mode="multilingual",
        approximate_size_mb=1500,
        accuracy_tier="high",
        speed_tier="slow",
        recommended_use="Higher accuracy. Larger download and slower on older computers.",
    ),
    SpeechModelInfo(
        id="large-v3",
        display_name="Large (v3)",
        language_mode="multilingual",
        approximate_size_mb=3100,
        accuracy_tier="highest",
        speed_tier="slow",
        recommended_use="Best local quality. Very large download and storage requirement.",
    ),
)


def model_by_id(model_id: str) -> SpeechModelInfo | None:
    """Look up a catalog model by id."""
    for model in WHISPER_CPP_MODELS:
        if model.id == model_id:
            return model
    return None


def recommended_model() -> SpeechModelInfo:
    """The model QUILL recommends for a first download."""
    found = model_by_id(RECOMMENDED_MODEL_ID)
    if found is None:  # pragma: no cover - RECOMMENDED_MODEL_ID is always present
        return WHISPER_CPP_MODELS[0]
    return found
