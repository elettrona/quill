"""Backend-tier fallback tests for the spell-check engine (CQ-11, partial).

The engine selects one of three tiers at runtime: native ``enchant``, the
bundled English wordlist, or a tiny built-in stub. These tests pin each tier by
seeding the module-level caches directly, then confirm that ``backend_info`` and
``is_known_word`` honour the active tier.

Note: CQ-11 also calls for a *background preload* test, but no preload API
exists yet, so only the tier-fallback half is covered here.
"""

from __future__ import annotations

import pytest

from quill.core import spellcheck


@pytest.fixture(autouse=True)
def _isolate_backend_caches(monkeypatch: pytest.MonkeyPatch) -> None:
    """Give each test a clean, fully controllable backend cache."""
    monkeypatch.setattr(spellcheck, "_ENCHANT_TRIED", True, raising=False)
    monkeypatch.setattr(spellcheck, "_ENCHANT_DICT", None, raising=False)
    monkeypatch.setattr(spellcheck, "_WORDLIST_CACHE", None, raising=False)


class _FakeEnchantDict:
    """Minimal stand-in for an enchant dictionary object."""

    tag = "en_GB"

    class provider:  # noqa: N801 - mirrors enchant's attribute shape
        name = "hunspell"

    def __init__(self, known: set[str]) -> None:
        self._known = known

    def check(self, word: str) -> bool:
        return word in self._known


def test_enchant_tier_is_selected_when_a_dictionary_is_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        spellcheck, "_ENCHANT_DICT", _FakeEnchantDict({"colour"}), raising=False
    )

    info = spellcheck.backend_info()

    assert info.name == "enchant"
    assert "en_GB" in info.detail
    assert "hunspell" in info.detail
    assert info.word_count == 0
    # is_known_word must defer to the enchant dictionary.
    assert spellcheck.is_known_word("colour") is True
    assert spellcheck.is_known_word("zzzznope") is False


def test_wordlist_tier_is_selected_when_enchant_is_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        spellcheck, "_WORDLIST_CACHE", frozenset({"quill", "editor"}), raising=False
    )

    info = spellcheck.backend_info()

    assert info.name == "wordlist"
    assert info.word_count == 2
    assert "2" in info.detail
    # is_known_word validates against the bundled wordlist (case-insensitive).
    assert spellcheck.is_known_word("Quill") is True
    assert spellcheck.is_known_word("notinlist") is False


def test_stub_tier_is_the_last_resort_when_no_data_is_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(spellcheck, "_WORDLIST_CACHE", frozenset(), raising=False)

    info = spellcheck.backend_info()

    assert info.name == "stub"
    assert info.word_count == len(spellcheck._STUB_WORDS)
    # Stub words still validate; anything outside the tiny corpus does not.
    assert spellcheck.is_known_word("document") is True
    assert spellcheck.is_known_word("supercalifragilistic") is False


def test_personal_dictionary_overrides_active_tier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(spellcheck, "_WORDLIST_CACHE", frozenset(), raising=False)

    # A word unknown to the stub tier is accepted when supplied as extra.
    assert spellcheck.is_known_word("Quillington", extra={"quillington"}) is True
