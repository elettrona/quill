"""PERF-1 / PERF-2: background preload warms the lexical caches.

These tests verify that ``spellcheck.preload()`` and ``thesaurus.preload()``:

* populate their module cache so the *first* real lookup pays no file-load
  cost (the "first check does not stall" acceptance), and
* are idempotent and cheap to call repeatedly (safe to fire from a startup
  daemon thread).

The caches are module-global, so each test resets them to a cold state first
to make the warm-up measurable regardless of test ordering.
"""

from __future__ import annotations

import threading
from time import perf_counter

from quill.core import spellcheck, thesaurus


def _reset_spellcheck_cache() -> None:
    spellcheck._WORDLIST_CACHE = None
    spellcheck._ENCHANT_DICT = None
    spellcheck._ENCHANT_TRIED = False


def _reset_thesaurus_cache() -> None:
    thesaurus._INDEX = None
    thesaurus._LOAD_ERROR = None


def test_spellcheck_preload_warms_cache_and_first_check_is_fast() -> None:
    _reset_spellcheck_cache()
    try:
        spellcheck.preload()
        # After preload, either enchant resolved or the wordlist is in memory;
        # in both cases a backend is selected without a further file load.
        assert spellcheck._ENCHANT_TRIED or spellcheck._WORDLIST_CACHE is not None

        start = perf_counter()
        spellcheck.is_known_word("document")
        elapsed = perf_counter() - start
        # No file I/O on the hot path -> the first check is essentially free.
        assert elapsed < 0.05
    finally:
        _reset_spellcheck_cache()


def test_spellcheck_preload_is_idempotent() -> None:
    _reset_spellcheck_cache()
    try:
        spellcheck.preload()
        warmed = spellcheck._WORDLIST_CACHE
        start = perf_counter()
        spellcheck.preload()
        elapsed = perf_counter() - start
        # Second call must not reload anything.
        assert spellcheck._WORDLIST_CACHE is warmed
        assert elapsed < 0.01
    finally:
        _reset_spellcheck_cache()


def test_thesaurus_preload_warms_index_and_first_lookup_is_fast() -> None:
    _reset_thesaurus_cache()
    try:
        thesaurus.preload()
        assert thesaurus._INDEX is not None

        start = perf_counter()
        thesaurus.lookup("happy")
        elapsed = perf_counter() - start
        assert elapsed < 0.05
    finally:
        _reset_thesaurus_cache()


def test_thesaurus_preload_is_idempotent() -> None:
    _reset_thesaurus_cache()
    try:
        thesaurus.preload()
        warmed = thesaurus._INDEX
        start = perf_counter()
        thesaurus.preload()
        elapsed = perf_counter() - start
        assert thesaurus._INDEX is warmed
        assert elapsed < 0.01
    finally:
        _reset_thesaurus_cache()


def test_preload_is_safe_from_a_background_thread() -> None:
    _reset_spellcheck_cache()
    _reset_thesaurus_cache()
    errors: list[BaseException] = []

    def worker() -> None:
        try:
            spellcheck.preload()
            thesaurus.preload()
        except BaseException as exc:  # noqa: BLE001 - record any failure
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    try:
        assert errors == []
        assert spellcheck._WORDLIST_CACHE is not None or spellcheck._ENCHANT_TRIED
        assert thesaurus._INDEX is not None
    finally:
        _reset_spellcheck_cache()
        _reset_thesaurus_cache()


def test_start_lexical_preload_is_importable_and_warms_caches() -> None:
    # Regression guard: main_frame imports ``start_lexical_preload`` by this
    # exact name, so a rename here would raise ImportError at app startup.
    from quill.core.lexical_preload import start_lexical_preload

    _reset_spellcheck_cache()
    _reset_thesaurus_cache()
    try:
        thread = start_lexical_preload()
        thread.join(timeout=30)
        assert not thread.is_alive()
        assert spellcheck._WORDLIST_CACHE is not None or spellcheck._ENCHANT_TRIED
        assert thesaurus._INDEX is not None
    finally:
        _reset_spellcheck_cache()
        _reset_thesaurus_cache()
