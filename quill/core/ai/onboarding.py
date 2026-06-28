"""AI onboarding model — a magical, frictionless first run for QUILL's AI (wx-free).

This is the brain of the AI Setup Wizard: the welcome, the one real decision (how
should AI run?), the friendly provider choices, the celebration of what just became
possible, and the persisted state (was setup done, and is the user in the gentle
**Basic** experience mode). It holds no wx — the wizard dialog drives it and applies
the chosen configuration through the existing settings/provider functions, so the
whole flow is unit-testable and the copy lives in one reviewable place.

Design promises: no jargon, no dead ends, no broken configurations. Every path can be
finished or skipped in seconds; the on-device path verifies a usable local Ollama
before it commits (``ollama_status``) so the user is never left "configured but not
working"; and the wizard's "keep it simple" checkbox puts a newcomer in Basic mode.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "EXPERIENCE_BASIC",
    "EXPERIENCE_ADVANCED",
    "OnboardingPath",
    "CloudProviderOption",
    "ONBOARDING_PATHS",
    "CLOUD_PROVIDER_OPTIONS",
    "WELCOME_TITLE",
    "WELCOME_BODY",
    "cloud_provider_option",
    "onboarding_path",
    "load_experience_mode",
    "save_experience_mode",
    "is_basic_mode",
    "onboarding_complete",
    "mark_onboarding_complete",
    "reset_onboarding",
    "ai_needs_setup",
    "celebration_lines",
    "apply_cloud_setup",
    "apply_on_device_setup",
    "ollama_status",
]

EXPERIENCE_BASIC = "basic"
EXPERIENCE_ADVANCED = "advanced"
_VALID_MODES = (EXPERIENCE_BASIC, EXPERIENCE_ADVANCED)

WELCOME_TITLE = "Meet QUILL's AI"
WELCOME_BODY = (
    "QUILL has a friendly AI that helps you write, fix, summarize, and turn recordings "
    "into finished documents — only when you ask, always with a preview, and never "
    "sending your work anywhere unless you choose to.\n\n"
    "Let's set it up in a few seconds. You can change anything later, and you can stop "
    "at any point."
)


@dataclass(frozen=True, slots=True)
class OnboardingPath:
    """One way AI can run. The user picks exactly one (or skips)."""

    id: str  # "on_device" | "cloud" | "skip"
    title: str
    summary: str  # one line shown in the choice list
    detail: str  # the reassuring paragraph shown when focused


ONBOARDING_PATHS: tuple[OnboardingPath, ...] = (
    OnboardingPath(
        id="on_device",
        title="On your device with Ollama — private and free",
        summary="Runs on your computer with Ollama. No account or key; stays on your machine.",
        detail=(
            "Run AI entirely on your own computer with Ollama — completely private and free, "
            "your writing never leaves your machine. If you already have Ollama running, QUILL "
            "connects to it now. If not, it is a quick one-time install from ollama.com, then "
            "come back here. Best if privacy matters most and you don't mind a one-time setup."
        ),
    ),
    OnboardingPath(
        id="cloud",
        title="Use an AI account — most capable",
        summary="Connect an account you already have (or a free one) for the strongest results.",
        detail=(
            "Connect an AI provider — Claude, OpenAI, Gemini, OpenRouter, or Ollama Cloud — "
            "with a key you paste once and QUILL stores securely on this device. This gives "
            "you the most capable models. Your document text is sent only to the provider "
            "you choose, only when you run an AI action, and always after a preview you "
            "approve."
        ),
    ),
    OnboardingPath(
        id="skip",
        title="Not right now",
        summary="Keep AI off for now. You can set it up any time from the AI menu.",
        detail=(
            "No problem — QUILL works beautifully without AI. You can turn it on whenever "
            "you like from AI > Set Up AI, with no pressure and nothing lost."
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class CloudProviderOption:
    """One cloud provider the user can connect during onboarding."""

    id: str  # matches assistant_ai provider ids
    name: str
    blurb: str
    key_hint: str  # where to get a key, in plain language
    signup_url: str


CLOUD_PROVIDER_OPTIONS: tuple[CloudProviderOption, ...] = (
    CloudProviderOption(
        id="claude",
        name="Claude (Anthropic)",
        blurb="Excellent, careful writing help. A great default.",
        key_hint="Get a key from console.anthropic.com under API Keys.",
        signup_url="https://console.anthropic.com/",
    ),
    CloudProviderOption(
        id="openai",
        name="OpenAI",
        blurb="GPT models — widely used and reliable.",
        key_hint="Get a key from platform.openai.com under API keys.",
        signup_url="https://platform.openai.com/api-keys",
    ),
    CloudProviderOption(
        id="gemini",
        name="Google Gemini",
        blurb="Fast and capable, with a generous free tier.",
        key_hint="Get a key from aistudio.google.com under Get API key.",
        signup_url="https://aistudio.google.com/app/apikey",
    ),
    CloudProviderOption(
        id="openrouter",
        name="OpenRouter",
        blurb="One key, many models — handy if you like to switch.",
        key_hint="Get a key from openrouter.ai under Keys.",
        signup_url="https://openrouter.ai/keys",
    ),
    CloudProviderOption(
        id="ollama_cloud",
        name="Ollama Cloud",
        blurb="Hosted open models with one key.",
        key_hint="Get a key from ollama.com after signing in.",
        signup_url="https://ollama.com/",
    ),
)


def onboarding_path(path_id: str) -> OnboardingPath | None:
    return next((p for p in ONBOARDING_PATHS if p.id == path_id), None)


def cloud_provider_option(provider_id: str) -> CloudProviderOption | None:
    target = provider_id.strip().lower()
    return next((p for p in CLOUD_PROVIDER_OPTIONS if p.id == target), None)


def celebration_lines(path_id: str, *, provider_name: str = "") -> list[str]:
    """The 'you're all set' lines shown at the end, tailored to what was set up."""
    head = {
        "on_device": "Your private, on-device AI (Ollama) is connected.",
        "cloud": f"Connected to {provider_name or 'your AI provider'}. You're all set.",
        "skip": "No problem — AI is off for now.",
    }.get(path_id, "You're all set.")
    if path_id == "skip":
        return [head, "Turn it on any time from AI > Set Up AI."]
    return [
        head,
        "Here's what you can do now:",
        "- Ask Quill (Alt+Q): chat about your document, ask anything.",
        "- Turn a recording into minutes, action items, or notes (AI > Transcribe Audio).",
        "- Build your own AI actions in plain language (AI > AI Library > Build Action).",
        "Everything previews before it changes your work, and one keystroke undoes it.",
    ]


# ---------------------------------------------------------------------------
# Persisted state: experience mode + "setup was offered/completed".
# ---------------------------------------------------------------------------

_STATE_FILE = "onboarding.json"


def onboarding_state_path() -> Path:
    from quill.core.paths import app_data_dir

    return app_data_dir() / "ai" / _STATE_FILE


def _load_state() -> dict[str, object]:
    from quill.core.storage import read_json

    data = read_json(onboarding_state_path(), default={})
    return data if isinstance(data, dict) else {}


def _save_state(state: dict[str, object]) -> None:
    from quill.core.storage import write_json_atomic

    path = onboarding_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(path, state)


def load_experience_mode() -> str:
    """The current AI experience mode: 'basic' (gentle) or 'advanced' (everything).

    Defaults to **advanced** when the user has never chosen — so nothing is ever
    hidden from someone who did not opt into Basic (e.g. an existing user who has not
    run the wizard). The AI Setup Wizard's "keep it simple" checkbox is what puts a
    newcomer into Basic.
    """
    mode = str(_load_state().get("experience_mode", EXPERIENCE_ADVANCED)).strip().lower()
    return mode if mode in _VALID_MODES else EXPERIENCE_ADVANCED


def save_experience_mode(mode: str) -> None:
    normalized = mode.strip().lower()
    if normalized not in _VALID_MODES:
        normalized = EXPERIENCE_ADVANCED
    state = _load_state()
    state["experience_mode"] = normalized
    _save_state(state)


def is_basic_mode() -> bool:
    """True when the AI surface should stay simple (advanced controls hidden)."""
    return load_experience_mode() == EXPERIENCE_BASIC


def onboarding_complete() -> bool:
    return bool(_load_state().get("completed", False))


def mark_onboarding_complete() -> None:
    state = _load_state()
    state["completed"] = True
    _save_state(state)


def reset_onboarding() -> None:
    """Forget that setup was done (so the wizard offers itself again). For tests/support."""
    state = _load_state()
    state["completed"] = False
    _save_state(state)


def apply_cloud_setup(provider_id: str, api_key: str, *, model: str = "") -> None:
    """Configure a cloud provider and turn AI on. Stores the key on this device only.

    Mirrors what the AI Hub does, in one call: set the connection (provider, default
    host, model), save the API key to the OS secure store, and enable AI.
    """
    from quill.core.ai.model_manager import save_ai_enabled
    from quill.core.ai.providers import default_host_for_provider, default_model_for_provider
    from quill.core.assistant_ai import (
        AssistantConnectionSettings,
        save_assistant_connection_settings,
        save_provider_api_key,
        save_provider_model,
    )

    chosen_model = model.strip() or default_model_for_provider(provider_id)
    save_assistant_connection_settings(
        AssistantConnectionSettings(
            provider=provider_id,
            host=default_host_for_provider(provider_id),
            model=chosen_model,
        )
    )
    if api_key.strip():
        save_provider_api_key(provider_id, api_key.strip())
    save_provider_model(provider_id, chosen_model)
    save_ai_enabled(True)


def ollama_status(host: str = "http://localhost:11434") -> tuple[bool, str, str]:
    """Check whether a usable local Ollama is present. Returns ``(ok, message, model)``.

    Used by the on-device setup path so QUILL never "configures" Ollama before it is
    actually there to talk to. On success, ``model`` is a model that is genuinely
    installed (so we never point the user at a model they don't have); on failure,
    ``message`` is plain-language guidance to fix it. Fast-fails (short timeout, single
    attempt) — a missing Ollama refuses the connection immediately.
    """
    from quill.core.ai.providers import default_model_for_provider
    from quill.core.assistant_ai import AssistantConnectionSettings, list_assistant_models

    settings = AssistantConnectionSettings(
        provider="ollama", host=host, model=default_model_for_provider("ollama")
    )
    try:
        models, error = list_assistant_models(settings, "", timeout_seconds=3.0, max_attempts=1)
    except Exception:  # noqa: BLE001 - any failure means "not reachable", with guidance
        return (
            False,
            "Could not reach Ollama on this computer. Install it free from ollama.com, "
            "then try again — or choose 'Use an AI account' instead.",
            "",
        )
    if error or not models:
        if error:
            return (
                False,
                "Ollama isn't running on this computer. Install it free from ollama.com "
                "and start it, then try again — or choose 'Use an AI account' instead.",
                "",
            )
        return (
            False,
            "Ollama is running but has no models yet. In a terminal run, for example, "
            "'ollama pull llama3.2', then try again.",
            "",
        )
    return True, "", models[0]


def apply_on_device_setup(*, host: str = "http://localhost:11434", model: str = "") -> None:
    """Point QUILL at a local Ollama server and turn AI on (private, no key)."""
    from quill.core.ai.model_manager import save_ai_enabled
    from quill.core.ai.providers import default_model_for_provider
    from quill.core.assistant_ai import (
        AssistantConnectionSettings,
        save_assistant_connection_settings,
    )

    chosen_model = model.strip() or default_model_for_provider("ollama")
    save_assistant_connection_settings(
        AssistantConnectionSettings(provider="ollama", host=host, model=chosen_model)
    )
    save_ai_enabled(True)


def ai_needs_setup() -> bool:
    """True when it's kind to offer the AI Setup Wizard.

    Offered once: when the user has not been through setup and AI is still off. If they
    have already turned AI on, or already completed (or skipped) setup, QUILL never
    nags — the wizard stays one click away in the AI menu.
    """
    from quill.core.ai.model_manager import load_ai_enabled

    if onboarding_complete():
        return False
    try:
        return not load_ai_enabled()
    except Exception:  # noqa: BLE001 - never let a setup check break startup
        return False
