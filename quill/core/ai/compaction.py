"""Graceful context compaction for long assistant sessions (AI-23).

A long writing-and-editing conversation eventually exceeds the model's context
window. Rather than silently truncating the oldest turns (which loses earlier
decisions), this module compacts: it keeps the most recent turns verbatim and
replaces the older head of the conversation with a single, clearly labelled
summary turn produced by the model. The caller announces when this happens, so
the user always knows the thread was condensed rather than dropped.

The logic is pure and UI-agnostic. Token counts use a conservative character
heuristic so no tokenizer dependency is required; the caller supplies the
summarizer (normally the on-device assistant) and the budget.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

# Conservative average of characters per token for English prose. Real
# tokenizers vary, so we deliberately under-estimate capacity (treat text as
# slightly larger than it is) to leave headroom for the prompt and reply.
_CHARS_PER_TOKEN = 4
SUMMARY_SPEAKER = "Summary"


@dataclass(frozen=True, slots=True)
class Message:
    """One conversation turn: who spoke and what they said."""

    speaker: str
    text: str


@dataclass(frozen=True, slots=True)
class CompactionResult:
    """The outcome of a compaction pass."""

    messages: tuple[Message, ...]
    compacted: bool
    summarized_count: int = 0


def estimate_tokens(text: str) -> int:
    """Estimate the token count of ``text`` (conservative, tokenizer-free)."""
    if not text:
        return 0
    return max(1, (len(text) + _CHARS_PER_TOKEN - 1) // _CHARS_PER_TOKEN)


def conversation_tokens(messages: Sequence[Message]) -> int:
    """Estimate the total token count of a conversation."""
    return sum(estimate_tokens(message.text) for message in messages)


def needs_compaction(messages: Sequence[Message], *, token_budget: int) -> bool:
    """Return True when the conversation exceeds the token budget."""
    return conversation_tokens(messages) > token_budget


def _summary_prompt(messages: Sequence[Message]) -> str:
    lines = [f"{message.speaker}: {message.text}" for message in messages]
    return (
        "Summarize the earlier part of this writing conversation into a brief, "
        "factual recap that preserves decisions, constraints, and unfinished "
        "threads. Be concise; this replaces the messages to save context.\n\n" + "\n".join(lines)
    )


def compact_conversation(
    messages: Sequence[Message],
    *,
    token_budget: int,
    summarize: Callable[[str], str],
    keep_recent: int = 4,
) -> CompactionResult:
    """Compact a conversation to fit within ``token_budget`` (pure logic).

    Keeps the most recent ``keep_recent`` turns verbatim and replaces the older
    head with one summary turn produced by ``summarize``. When the conversation
    already fits, or there is nothing old enough to summarize, the conversation
    is returned unchanged with ``compacted=False``. A summarizer that fails or
    returns blank leaves the conversation untouched rather than losing content.
    """
    items = list(messages)
    if keep_recent < 0:
        keep_recent = 0
    if not needs_compaction(items, token_budget=token_budget):
        return CompactionResult(tuple(items), compacted=False)
    if len(items) <= keep_recent + 1:
        # Too few old turns to gain anything by summarizing.
        return CompactionResult(tuple(items), compacted=False)

    head = items[: len(items) - keep_recent] if keep_recent else items
    tail = items[len(items) - keep_recent :] if keep_recent else []
    try:
        summary_text = summarize(_summary_prompt(head)).strip()
    except Exception:  # noqa: BLE001 - a failed summary must not drop the thread
        return CompactionResult(tuple(items), compacted=False)
    if not summary_text:
        return CompactionResult(tuple(items), compacted=False)

    summary_message = Message(SUMMARY_SPEAKER, f"(Earlier conversation summarized)\n{summary_text}")
    return CompactionResult((summary_message, *tail), compacted=True, summarized_count=len(head))
