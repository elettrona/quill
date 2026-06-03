"""Consistent, screen-reader-friendly AI availability reporting (AI-6).

Every AI feature must announce clearly when a model is unavailable or an API key
is missing, and must never block the editor. This module is the single, wx-free
place that turns the three facts a caller has — whether the master AI toggle is
on, whether the active backend reports itself available, and the backend's
reason string — into one clear sentence the UI can speak.

Keeping the wording here (instead of scattered f-strings across the UI) means
the chat, the inline writing actions, the watch-folder actions, and the AI
status badge all describe the same problem the same way.
"""

from __future__ import annotations

from dataclasses import dataclass

# Master-switch wording, shared by every entry point that guards on the toggle.
AI_DISABLED_MESSAGE = "AI is turned off. Enable 'Use Artificial Intelligence' in the AI menu."

# Phrases a backend uses in its unavailable reason when the real problem is a
# missing or unusable API key — detected so we can flag it for a louder cue.
_KEY_PHRASES = (
    "api key",
    "no key",
    "needs key",
    "could not be unlocked",
    "add one in ai settings",
)


@dataclass(frozen=True, slots=True)
class AIAvailability:
    """The result of resolving whether an AI feature can run right now.

    ``ok`` is True only when AI is enabled and the backend is available. When it
    is False, ``message`` is a complete, speakable sentence explaining what to do
    and ``needs_key`` marks the missing-API-key case so callers can show a
    dedicated "Needs key" cue. ``blocks_editor`` is always False — surfacing AI
    status must never stop the user from typing.
    """

    ok: bool
    message: str
    needs_key: bool = False
    blocks_editor: bool = False


def _looks_like_key_problem(reason: str | None) -> bool:
    low = (reason or "").lower()
    return any(phrase in low for phrase in _KEY_PHRASES)


def describe_ai_availability(
    *,
    enabled: bool,
    available: bool,
    reason: str | None = None,
    feature: str | None = None,
) -> AIAvailability:
    """Resolve AI availability into one clear, speakable result.

    ``enabled`` is the master AI toggle, ``available`` and ``reason`` come from
    the active backend's ``is_available()``. ``feature`` (e.g. "Rewrite") is
    woven into the unavailable message so the announcement names what the user
    was trying to do. The editor is never blocked regardless of the outcome.
    """
    if not enabled:
        return AIAvailability(ok=False, message=AI_DISABLED_MESSAGE)
    if available:
        return AIAvailability(ok=True, message="AI is ready.")

    detail = (reason or "").strip() or "The AI model is unavailable right now."
    needs_key = _looks_like_key_problem(detail)
    if feature:
        message = f"{feature} is unavailable: {detail}"
    else:
        message = detail
    return AIAvailability(ok=False, message=message, needs_key=needs_key)
