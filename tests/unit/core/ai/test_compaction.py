"""Tests for graceful context compaction (AI-23)."""

from __future__ import annotations

from quill.core.ai.compaction import (
    SUMMARY_SPEAKER,
    Message,
    compact_conversation,
    conversation_tokens,
    estimate_tokens,
    needs_compaction,
)


def _msg(speaker: str, text: str) -> Message:
    return Message(speaker, text)


def test_estimate_tokens_is_conservative() -> None:
    assert estimate_tokens("") == 0
    assert estimate_tokens("a") == 1
    # 8 chars -> 2 tokens at 4 chars/token.
    assert estimate_tokens("12345678") == 2


def test_needs_compaction_only_over_budget() -> None:
    messages = [_msg("You", "x" * 40)]  # ~10 tokens
    assert needs_compaction(messages, token_budget=100) is False
    assert needs_compaction(messages, token_budget=5) is True


def test_short_conversation_is_unchanged() -> None:
    messages = [_msg("You", "hi"), _msg("Quill", "hello")]
    result = compact_conversation(messages, token_budget=1000, summarize=lambda _p: "SUMMARY")
    assert result.compacted is False
    assert result.messages == tuple(messages)


def test_long_conversation_is_compacted() -> None:
    messages = [_msg("You" if i % 2 == 0 else "Quill", "word " * 50) for i in range(12)]
    calls: list[str] = []

    def summarize(prompt: str) -> str:
        calls.append(prompt)
        return "Earlier we agreed on tone and audience."

    result = compact_conversation(messages, token_budget=50, summarize=summarize, keep_recent=4)

    assert result.compacted is True
    assert result.summarized_count == 8  # 12 - 4 recent kept
    assert result.messages[0].speaker == SUMMARY_SPEAKER
    assert "agreed on tone" in result.messages[0].text
    # The four most recent turns are preserved verbatim after the summary.
    assert result.messages[1:] == tuple(messages[-4:])
    assert len(calls) == 1


def test_compaction_preserves_recent_turns_count() -> None:
    messages = [_msg("You", "x" * 100) for _ in range(10)]
    result = compact_conversation(
        messages, token_budget=10, summarize=lambda _p: "recap", keep_recent=3
    )
    assert result.compacted is True
    # one summary + three recent
    assert len(result.messages) == 4
    assert result.messages[1:] == tuple(messages[-3:])


def test_failed_summarizer_leaves_thread_intact() -> None:
    messages = [_msg("You", "x" * 100) for _ in range(10)]

    def boom(_prompt: str) -> str:
        raise RuntimeError("model down")

    result = compact_conversation(messages, token_budget=10, summarize=boom)
    assert result.compacted is False
    assert result.messages == tuple(messages)


def test_blank_summary_leaves_thread_intact() -> None:
    messages = [_msg("You", "x" * 100) for _ in range(10)]
    result = compact_conversation(messages, token_budget=10, summarize=lambda _p: "   ")
    assert result.compacted is False
    assert result.messages == tuple(messages)


def test_too_few_old_turns_not_compacted() -> None:
    # Over budget, but only the recent turns plus one — nothing to gain.
    messages = [_msg("You", "x" * 100) for _ in range(4)]
    result = compact_conversation(
        messages, token_budget=1, summarize=lambda _p: "recap", keep_recent=4
    )
    assert result.compacted is False


def test_conversation_tokens_sums_messages() -> None:
    messages = [_msg("You", "12345678"), _msg("Quill", "1234")]
    assert conversation_tokens(messages) == 3  # 2 + 1
