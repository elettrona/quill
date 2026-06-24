"""Structured List Studio core (wx-free).

The pure-domain half of the Structured List Studio feature described in
``docs/planning/quill-structured-list-studio-prd.md``: a neutral list/definition
model, import interpretation (turning selected text, lines, or pasted content into
items or term/definition entries), Markdown/HTML source generation that lets the
user work with concepts instead of raw ``-``/``1.``/``<dl>`` syntax, and
conversions between list types with information-loss detection.

Everything here is wx-free and unit-tested so the wx dialog stays a thin shell
that builds a model, asks this package to render it, and previews the result.
"""

from __future__ import annotations

from quill.core.lists.announce import (
    checklist_toggle_announcement,
    definition_entry_announcement,
    flat_item_announcement,
    list_summary,
)
from quill.core.lists.convert import (
    ConversionLoss,
    definition_to_flat,
    flat_to_definition,
)
from quill.core.lists.model import (
    DefinitionEntry,
    DefinitionList,
    FlatList,
    ListItem,
    ListType,
)
from quill.core.lists.parse import (
    DefinitionInterpretation,
    SelectionMode,
    detect_definition_separator,
    interpret_definition_entries,
    interpret_selection,
    strip_marker,
)
from quill.core.lists.render import render_html, render_markdown
from quill.core.lists.settings import (
    DefinitionMarkdownProfile,
    StructuredListSettings,
)

__all__ = [
    "ConversionLoss",
    "DefinitionEntry",
    "DefinitionInterpretation",
    "DefinitionList",
    "DefinitionMarkdownProfile",
    "FlatList",
    "ListItem",
    "ListType",
    "SelectionMode",
    "StructuredListSettings",
    "checklist_toggle_announcement",
    "definition_entry_announcement",
    "definition_to_flat",
    "detect_definition_separator",
    "flat_item_announcement",
    "flat_to_definition",
    "interpret_definition_entries",
    "interpret_selection",
    "list_summary",
    "render_html",
    "render_markdown",
    "strip_marker",
]
