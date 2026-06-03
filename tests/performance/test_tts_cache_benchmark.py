"""Benchmark: cached TTS sentences avoid expensive re-synthesis (PERF-3/PERF-10).

These tests do not touch a real audio engine. They model the cost of synthesis
with a deliberate delay and assert that an identical sentence served from the
on-disk cache is dramatically faster than re-rendering, and that a long document
full of repeated sentences only pays the synthesis cost once per unique line.
"""

from __future__ import annotations

from pathlib import Path
from time import perf_counter, sleep

from quill.core.tts_cache import TtsCache, cached_sentence_generator

_RENDER_DELAY = 0.05  # Models a slow synthesis step.


def _make_renderer(counter: list[int]):
    def render(sentence: str, out: Path) -> None:
        counter[0] += 1
        sleep(_RENDER_DELAY)
        out.write_bytes(b"RIFF" + sentence.encode("utf-8"))

    return render


def test_repeated_sentence_is_served_from_cache_quickly(tmp_path: Path) -> None:
    cache = TtsCache(tmp_path / "cache")
    counter = [0]
    gen = cached_sentence_generator(("piper", "voiceA"), _make_renderer(counter), cache=cache)

    first_start = perf_counter()
    gen("The same heading repeats.", tmp_path / "a.wav")
    first_elapsed = perf_counter() - first_start

    second_start = perf_counter()
    gen("The same heading repeats.", tmp_path / "b.wav")
    second_elapsed = perf_counter() - second_start

    assert counter[0] == 1  # Only the first call synthesized.
    assert first_elapsed >= _RENDER_DELAY
    # The cache hit must be far cheaper than re-rendering.
    assert second_elapsed < _RENDER_DELAY / 2


def test_long_document_only_renders_unique_sentences(tmp_path: Path) -> None:
    cache = TtsCache(tmp_path / "cache", max_entries=10_000, max_bytes=10**9)
    counter = [0]
    gen = cached_sentence_generator(("piper", "voiceA"), _make_renderer(counter), cache=cache)

    unique = [f"Sentence number {i}." for i in range(5)]
    # A 100-sentence document built from only 5 distinct sentences.
    document = [unique[i % len(unique)] for i in range(100)]

    for index, sentence in enumerate(document):
        gen(sentence, tmp_path / f"out_{index}.wav")

    assert counter[0] == len(unique)
