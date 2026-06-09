"""Source-contract test for the spell-check F7 flow fix (issue #129).

wxPython cannot be imported headlessly, so (as with the other dialog a11y tests)
this reads the UI source and pins the behaviour: a single misspelling goes
straight to its corrections, and the multi-word chooser's action button clearly
leads to corrections rather than a vague "Review Word".
"""

from __future__ import annotations

from pathlib import Path


def _main_frame_source() -> str:
    return Path("quill/ui/main_frame.py").read_text(encoding="utf-8")


def _spell_dialog_body() -> str:
    source = _main_frame_source()
    start = source.index("def open_spell_check_dialog")
    end = source.index("def _misspelling_context_text")
    return source[start:end]


def test_single_misspelling_skips_the_chooser() -> None:
    body = _spell_dialog_body()
    # F7 on one typo (the reported "This is a bligtest" case) jumps straight to
    # the word so its corrections are shown without a one-item chooser first.
    assert "if len(misspellings) == 1:" in body
    assert "item = misspellings[0]" in body


def test_multi_word_chooser_button_names_the_corrections_action() -> None:
    body = _spell_dialog_body()
    assert 'label="Show Corrections..."' in body
    assert 'label="Review Word"' not in body
