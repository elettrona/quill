"""Unit test for the List Studio settings dialog's pure option matcher.

The dialog itself is a thin wx shell over the tested core (presets and
StructuredListSettings.to_dict/from_dict); only the option-index helper is pure,
and a regression there would mis-select a control on open.
"""

from __future__ import annotations

from quill.ui.list_studio_settings_dialog import _index_of


def test_index_of_finds_match() -> None:
    options = [("Alpha", "a"), ("Beta", "b"), ("Gamma", "c")]
    assert _index_of(options, "b", 0) == 1


def test_index_of_returns_default_when_absent() -> None:
    options = [("Alpha", "a"), ("Beta", "b")]
    assert _index_of(options, "missing", 0) == 0
