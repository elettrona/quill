"""Wiring tests for ListStudioDialog that do not need a live wx control tree.

The full control behavior is exercised by hand with a screen reader; here we guard
the seam between the dialog and ``quill.core.lists`` — that the dialog renders the
model it was given through the right renderer and reports an accurate summary — so
a regression in that wiring is caught without a wx display.
"""

from __future__ import annotations

from quill.core.lists import (
    DefinitionEntry,
    DefinitionList,
    FlatList,
    ListItem,
    ListType,
)
from quill.core.lists.settings import DefinitionMarkdownProfile, StructuredListSettings
from quill.ui.list_studio_dialog import ListStudioDialog


def _studio(**kwargs: object) -> ListStudioDialog:
    # __init__ only stores its arguments; no wx objects are constructed until
    # populate(), so a placeholder wx module is fine for these seam tests.
    return ListStudioDialog(wx=object(), **kwargs)  # type: ignore[arg-type]


def test_renders_flat_markdown_by_default() -> None:
    studio = _studio(flat=FlatList(items=[ListItem("apples"), ListItem("oranges")]))
    assert studio._render() == "- apples\n- oranges"
    assert studio.summary == "Bulleted list, 2 items."


def test_renders_flat_html_when_format_is_html() -> None:
    studio = _studio(flat=FlatList(items=[ListItem("a")]), target_format="html")
    assert studio._render() == "<ul>\n  <li>a</li>\n</ul>"


def test_definition_model_selects_definition_type() -> None:
    dl = DefinitionList(entries=[DefinitionEntry(terms=["Term"], definitions=["Def"])])
    studio = _studio(
        definition=dl,
        settings=StructuredListSettings(
            definition_markdown_profile=DefinitionMarkdownProfile.PANDOC
        ),
    )
    assert studio._is_definition()
    assert "Term\n: Def" in studio._render()


def test_checklist_render_reflects_checked_state() -> None:
    studio = _studio(
        flat=FlatList(
            list_type=ListType.CHECKLIST,
            items=[ListItem("done", checked=True), ListItem("todo")],
        )
    )
    assert studio._render() == "- [x] done\n- [ ] todo"


def test_multiple_terms_render_as_multiple_dt() -> None:
    # One entry with two synonymous terms (§15.3) emits two <dt> in HTML.
    dl = DefinitionList(
        entries=[
            DefinitionEntry(
                terms=["HTTP", "HyperText Transfer Protocol"],
                definitions=["A protocol"],
            )
        ]
    )
    studio = _studio(definition=dl, target_format="html")
    rendered = studio._render()
    assert "<dt>HTTP</dt>" in rendered
    assert "<dt>HyperText Transfer Protocol</dt>" in rendered
    assert "<dd>A protocol</dd>" in rendered


def test_multiple_definitions_render_as_multiple_dd() -> None:
    # One entry with two definitions (§15.4) emits two <dd> in HTML.
    dl = DefinitionList(
        entries=[
            DefinitionEntry(
                terms=["bank"],
                definitions=["A financial institution", "The side of a river"],
            )
        ]
    )
    studio = _studio(definition=dl, target_format="html")
    rendered = studio._render()
    assert "<dd>A financial institution</dd>" in rendered
    assert "<dd>The side of a river</dd>" in rendered
