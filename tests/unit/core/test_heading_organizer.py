from __future__ import annotations

from dataclasses import replace

from quill.core.heading_organizer import (
    HeadingBlock,
    apply_heading_organizer_edits,
    heading_context_at,
    parse_heading_blocks,
    validate_heading_sequence,
)


def test_parse_markdown_heading_blocks_tracks_sections() -> None:
    text = "# Top\nParagraph\n## Child\nMore\n"
    blocks = parse_heading_blocks(text, "markdown")
    assert [block.level for block in blocks] == [1, 2]
    assert blocks[0].section_start == 0
    assert blocks[0].section_end == blocks[1].start


def test_apply_heading_organizer_edits_reorders_markdown_sections() -> None:
    text = "# First\nA\n## Second\nB\n"
    blocks = parse_heading_blocks(text, "markdown")
    first = blocks[0]
    second = blocks[1]
    updated = [
        replace(second, title="Second Updated", level=1),
        replace(first, title="First Updated", level=2),
    ]
    rendered = apply_heading_organizer_edits(text, "markdown", updated)
    assert rendered.startswith("# Second Updated\nB\n## First Updated\nA\n")


def test_apply_heading_organizer_edits_rewrites_html_heading_attributes() -> None:
    text = '<h2 id="a">Alpha</h2><p>a</p><h3 class="x">Beta</h3><p>b</p>'
    blocks = parse_heading_blocks(text, "html")
    updated = [
        replace(blocks[0], level=1, title="Alpha Prime"),
        replace(blocks[1], level=2, title="Beta Prime"),
    ]
    rendered = apply_heading_organizer_edits(text, "html", updated)
    assert '<h1 id="a">Alpha Prime</h1>' in rendered
    assert '<h2 class="x">Beta Prime</h2>' in rendered


def test_heading_context_at_reports_level_ordinal_and_total() -> None:
    text = "# Top\nIntro\n## Child\nBody\n### Grandchild\nMore\n"
    blocks = parse_heading_blocks(text, "markdown")

    first = heading_context_at(text, blocks[0].start, "markdown")
    assert first is not None
    assert (first.level, first.ordinal, first.total, first.title) == (1, 1, 3, "Top")

    second = heading_context_at(text, blocks[1].start, "markdown")
    assert second is not None
    assert (second.level, second.ordinal, second.total, second.title) == (2, 2, 3, "Child")

    third = heading_context_at(text, blocks[2].start, "markdown")
    assert third is not None
    assert (third.level, third.ordinal) == (3, 3)


def test_heading_context_at_matches_by_line_with_leading_whitespace() -> None:
    text = "Intro paragraph\n## Spaced\nBody\n"
    target = text.index("##")
    context = heading_context_at(text, target, "markdown")
    assert context is not None
    assert context.level == 2
    assert context.title == "Spaced"


def test_heading_context_at_returns_none_off_heading() -> None:
    text = "# Top\nParagraph body line\n"
    body = text.index("Paragraph")
    assert heading_context_at(text, body, "markdown") is None


def test_heading_context_at_handles_html() -> None:
    text = "<h1>Alpha</h1><p>a</p>\n<h2>Beta</h2><p>b</p>"
    blocks = parse_heading_blocks(text, "html")
    beta = heading_context_at(text, blocks[1].start, "html")
    assert beta is not None
    assert (beta.level, beta.ordinal, beta.total, beta.title) == (2, 2, 2, "Beta")


def test_validate_heading_sequence_reports_issues() -> None:
    blocks = [
        HeadingBlock(0, 2, "Top", 0, 0, 0, 0),
        HeadingBlock(1, 4, "", 0, 0, 0, 0),
    ]
    issues = validate_heading_sequence(blocks, require_single_h1=True)
    assert any("start at H1" in issue for issue in issues)
    assert any("skipped" in issue for issue in issues)
    assert any("empty" in issue for issue in issues)


# --- Fence-aware markdown parsing -----------------------------------------


def test_parse_markdown_heading_blocks_skips_fenced_backticks() -> None:
    """A line beginning with ``#`` inside a ``` fence must not be parsed
    as a heading, even though the regex would match it on its own."""
    text = (
        "# Real Heading\n"
        "Paragraph line.\n"
        "```python\n"
        "# not a heading\n"
        "def f():\n"
        "    # also not\n"
        "```\n"
        "## After Fence\n"
        "Body\n"
    )
    blocks = parse_heading_blocks(text, "markdown")
    assert [block.title for block in blocks] == ["Real Heading", "After Fence"]
    assert [block.level for block in blocks] == [1, 2]


def test_parse_markdown_heading_blocks_skips_fenced_tildes() -> None:
    """Tilde fences (~~~) must be recognised with the same fidelity as
    backtick fences."""
    text = "# Real\n~~~text\n# not a heading\n~~~ \n## After\n"
    blocks = parse_heading_blocks(text, "markdown")
    assert [block.title for block in blocks] == ["Real", "After"]


def test_parse_markdown_heading_blocks_handles_unclosed_fence() -> None:
    """If the document ends inside an open fence, every line from the
    opening fence to EOF must be treated as code (no headings found after
    the opening fence)."""
    text = "# Real\n```\n# not closed\n# still not\n"
    blocks = parse_heading_blocks(text, "markdown")
    assert [block.title for block in blocks] == ["Real"]


def test_parse_markdown_heading_blocks_resets_fence_on_close() -> None:
    """A heading on the line *after* the closing fence is recognised again."""
    text = "# A\n```\n# fenced\n```\n# back outside\n"
    blocks = parse_heading_blocks(text, "markdown")
    assert [block.title for block in blocks] == ["A", "back outside"]


def test_parse_markdown_heading_blocks_section_end_after_fenced_heading() -> None:
    """The section_end of a real heading must skip over any fenced code
    block (the fenced content belongs to the preceding section, not to the
    heading after it)."""
    text = "# Top\nPara\n```\n# fake\n```\n## After\nBody\n"
    blocks = parse_heading_blocks(text, "markdown")
    assert len(blocks) == 2
    top, after = blocks
    assert top.title == "Top"
    assert after.title == "After"
    # Top's section must include the fenced block.
    assert top.section_end == after.start


def test_parse_markdown_heading_blocks_indented_fence_close() -> None:
    """CommonMark allows a closing fence with up to three spaces of indent.
    A heading inside a fence that closes with leading whitespace must still
    be excluded."""
    text = "# Real\n```\n# inside\n   ```\n## After\n"
    blocks = parse_heading_blocks(text, "markdown")
    assert [block.title for block in blocks] == ["Real", "After"]


def test_parse_markdown_heading_blocks_html_path_unchanged() -> None:
    """HTML parsing must not regress on the fence-aware refactor."""
    text = "<h1>A</h1><h2>B</h2>"
    blocks = parse_heading_blocks(text, "html")
    assert [block.level for block in blocks] == [1, 2]  # type: ignore[misc]
