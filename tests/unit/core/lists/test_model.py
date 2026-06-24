"""Unit tests for structured-list model helpers."""

from __future__ import annotations

from quill.core.lists.model import DefinitionEntry


def test_terms_text_joins_one_per_line() -> None:
    entry = DefinitionEntry(terms=["alpha", "beta"])
    assert entry.terms_text() == "alpha\nbeta"


def test_set_terms_text_splits_non_blank_lines() -> None:
    entry = DefinitionEntry()
    entry.set_terms_text("alpha\n  beta  \n\ngamma\n")
    assert entry.terms == ["alpha", "beta", "gamma"]


def test_set_terms_text_all_blank_keeps_single_empty_term() -> None:
    entry = DefinitionEntry(terms=["alpha"])
    entry.set_terms_text("   \n\n")
    assert entry.terms == [""]  # never collapses to zero terms
    assert entry.primary_term == ""


def test_terms_text_round_trips_through_set() -> None:
    entry = DefinitionEntry(terms=["one", "two", "three"])
    clone = DefinitionEntry()
    clone.set_terms_text(entry.terms_text())
    assert clone.terms == entry.terms
