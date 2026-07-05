"""Tests for the book-metadata lookup parsers (pure parts; no network)."""

from __future__ import annotations

from quill.core.metadata_lookup import (
    LookupResult,
    _lucene_escape,
    results_from_musicbrainz,
    results_from_open_library,
)


def test_lucene_escape_backslash_then_quote() -> None:
    assert _lucene_escape('He said "hi" \\ bye') == 'He said \\"hi\\" \\\\ bye'


def test_results_from_open_library_parses_and_scores() -> None:
    data = {
        "docs": [
            {
                "title": "My Book",
                "author_name": ["Jane Doe"],
                "first_publish_year": 2001,
                "subject": ["Fiction", "Adventure"],
                "series": ["The Saga"],
            },
            {"title": "Another", "author_name": []},
            "junk",
        ]
    }
    results = results_from_open_library(data, "my book")
    assert results[0].title == "My Book"
    assert results[0].author == "Jane Doe"
    assert results[0].genre == "Fiction"
    assert results[0].year == "2001"
    assert results[0].series_title == "The Saga"
    assert results[0].score == 95  # exact title match
    assert results[1].score == 75
    assert len(results) == 2  # junk entry skipped


def test_results_from_musicbrainz_parses() -> None:
    data = {
        "releases": [
            {
                "title": "My Album",
                "score": 88,
                "date": "1999-05-01",
                "artist-credit": [{"name": "The Band"}],
            }
        ]
    }
    results = results_from_musicbrainz(data)
    assert results == [
        LookupResult(
            title="My Album", author="The Band", year="1999", source="MusicBrainz", score=88
        )
    ]


def test_results_tolerate_empty_payloads() -> None:
    assert results_from_open_library({}, "x") == []
    assert results_from_musicbrainz({"releases": "nope"}) == []


def test_display_reads_as_one_sentence() -> None:
    result = LookupResult(title="My Book", author="Jane", year="2001", source="Open Library")
    assert result.display == "My Book by Jane (2001) — Open Library"


def test_search_merges_best_first(monkeypatch) -> None:
    import quill.core.metadata_lookup as lookup

    monkeypatch.setattr(
        lookup,
        "search_open_library",
        lambda t, a="": [LookupResult(title="Book", author="", source="Open Library", score=95)],
    )
    monkeypatch.setattr(
        lookup,
        "search_musicbrainz",
        lambda t, a="": [LookupResult(title="Album", author="", source="MusicBrainz", score=99)],
    )
    results = lookup.search("x")
    assert [r.title for r in results] == ["Album", "Book"]
