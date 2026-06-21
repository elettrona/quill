"""Curated whisper.cpp model catalog (#617 section 5.2).

Data-driven model tiers with approximate sizes and accessible speed/accuracy/use
descriptions. URLs and hashes are intentionally left for the provider/release
pipeline to fill in (kept data-driven per #617 section 17); this module is the
single place the model manager reads its menu of models from.
"""

from __future__ import annotations

from quill.core.speech.provider import SpeechModelInfo

RECOMMENDED_MODEL_ID = "small"
# A model that supports whisper.cpp tinydiarize (-tdrz) speaker-turn detection.
DIARIZATION_MODEL_ID = "small.en-tdrz"

# whisper.cpp GGML models are published on Hugging Face. URLs are data-driven so
# a release/mirror can override them; sha256 is left None until the pipeline pins
# verified hashes (download verifies only when a hash is present — #617 section 8).
_HF_BASE = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"


def _ggml_url(name: str) -> str:
    return f"{_HF_BASE}/ggml-{name}.bin"


WHISPER_CPP_MODELS: tuple[SpeechModelInfo, ...] = (
    SpeechModelInfo(
        id="tiny",
        display_name="Tiny",
        language_mode="multilingual",
        approximate_size_mb=75,
        accuracy_tier="low",
        speed_tier="fast",
        recommended_use="Smallest download. Good for testing and simple voice commands.",
        download_url=_ggml_url("tiny"),
        license_name="MIT",
    ),
    SpeechModelInfo(
        id="base",
        display_name="Base",
        language_mode="multilingual",
        approximate_size_mb=145,
        accuracy_tier="low",
        speed_tier="fast",
        recommended_use="Small download. Better than Tiny; good for quick notes.",
        download_url=_ggml_url("base"),
        license_name="MIT",
    ),
    SpeechModelInfo(
        id="small",
        display_name="Small",
        language_mode="multilingual",
        approximate_size_mb=465,
        accuracy_tier="medium",
        speed_tier="medium",
        recommended_use="Recommended starting point: solid transcription without a huge download.",
        download_url=_ggml_url("small"),
        license_name="MIT",
    ),
    SpeechModelInfo(
        id="small.en-tdrz",
        display_name="Small English with speaker detection",
        language_mode="english",
        approximate_size_mb=465,
        accuracy_tier="medium",
        speed_tier="medium",
        recommended_use=(
            "English only, and marks who is speaking when (speaker turns) in transcripts."
        ),
        download_url=_ggml_url("small.en-tdrz"),
        license_name="MIT",
    ),
    SpeechModelInfo(
        id="medium",
        display_name="Medium",
        language_mode="multilingual",
        approximate_size_mb=1500,
        accuracy_tier="high",
        speed_tier="slow",
        recommended_use="Higher accuracy. Larger download and slower on older computers.",
        download_url=_ggml_url("medium"),
        license_name="MIT",
    ),
    SpeechModelInfo(
        id="large-v3",
        display_name="Large (v3)",
        language_mode="multilingual",
        approximate_size_mb=3100,
        accuracy_tier="highest",
        speed_tier="slow",
        recommended_use="Best local quality. Very large download and storage requirement.",
        download_url=_ggml_url("large-v3"),
        license_name="MIT",
    ),
)


def model_by_id(model_id: str) -> SpeechModelInfo | None:
    """Look up a catalog model by id."""
    for model in WHISPER_CPP_MODELS:
        if model.id == model_id:
            return model
    return None


# --------------------------------------------------------------------------- #
# Faster Whisper (CTranslate2) models — S4
#
# Faster Whisper loads CTranslate2 model *repositories* from the Hugging Face
# Hub, not single GGML files. We store the Hub repo id in ``download_url`` (the
# provider passes it to huggingface_hub.snapshot_download). Sizes are the
# approximate on-disk footprint of the CT2 weights.
# --------------------------------------------------------------------------- #

FASTER_WHISPER_RECOMMENDED_MODEL_ID = "small"


def _ct2_repo(name: str) -> str:
    return f"Systran/faster-whisper-{name}"


FASTER_WHISPER_MODELS: tuple[SpeechModelInfo, ...] = (
    SpeechModelInfo(
        id="tiny",
        display_name="Tiny (Faster Whisper)",
        language_mode="multilingual",
        approximate_size_mb=75,
        accuracy_tier="low",
        speed_tier="fast",
        recommended_use="Smallest download. Fastest, lowest accuracy.",
        download_url=_ct2_repo("tiny"),
        license_name="MIT",
    ),
    SpeechModelInfo(
        id="base",
        display_name="Base (Faster Whisper)",
        language_mode="multilingual",
        approximate_size_mb=145,
        accuracy_tier="low",
        speed_tier="fast",
        recommended_use="Small and quick; good for short notes.",
        download_url=_ct2_repo("base"),
        license_name="MIT",
    ),
    SpeechModelInfo(
        id="small",
        display_name="Small (Faster Whisper)",
        language_mode="multilingual",
        approximate_size_mb=465,
        accuracy_tier="medium",
        speed_tier="fast",
        recommended_use="Recommended: solid accuracy and fast, especially with a GPU.",
        download_url=_ct2_repo("small"),
        license_name="MIT",
    ),
    SpeechModelInfo(
        id="medium",
        display_name="Medium (Faster Whisper)",
        language_mode="multilingual",
        approximate_size_mb=1500,
        accuracy_tier="high",
        speed_tier="medium",
        recommended_use="Higher accuracy; comfortable on a GPU or a fast CPU.",
        download_url=_ct2_repo("medium"),
        license_name="MIT",
    ),
    SpeechModelInfo(
        id="large-v3",
        display_name="Large v3 (Faster Whisper)",
        language_mode="multilingual",
        approximate_size_mb=3100,
        accuracy_tier="highest",
        speed_tier="medium",
        recommended_use="Best quality. Large download; a GPU is recommended.",
        download_url=_ct2_repo("large-v3"),
        license_name="MIT",
    ),
    SpeechModelInfo(
        id="distil-large-v3",
        display_name="Distil-Large v3 (Faster Whisper, English)",
        language_mode="english",
        approximate_size_mb=1500,
        accuracy_tier="high",
        speed_tier="fast",
        recommended_use=(
            "English-only, near-Large accuracy at roughly half the size and twice the speed."
        ),
        download_url="Systran/faster-distil-whisper-large-v3",
        license_name="MIT",
    ),
)


def fw_model_by_id(model_id: str) -> SpeechModelInfo | None:
    """Look up a Faster Whisper catalog model by id."""
    for model in FASTER_WHISPER_MODELS:
        if model.id == model_id:
            return model
    return None


def is_diarization_model(model_id: str) -> bool:
    """True when a model supports speaker-turn detection (whisper.cpp tinydiarize)."""
    return model_id.endswith("-tdrz")


def recommended_model() -> SpeechModelInfo:
    """The model QUILL recommends for a first download."""
    found = model_by_id(RECOMMENDED_MODEL_ID)
    if found is None:  # pragma: no cover - RECOMMENDED_MODEL_ID is always present
        return WHISPER_CPP_MODELS[0]
    return found
