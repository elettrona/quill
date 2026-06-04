from quill.io.rtf_model import (
    InlineSpan,
    RichDocument,
    RichParagraph,
    analyze_markdown,
    format_at_markdown_offset,
    markdown_offset_to_plain_offset,
    markdown_to_rich,
    plain_offset_to_markdown_offset,
    rich_to_markdown,
    rich_to_rtf,
    rtf_to_rich,
    scan_rtf_features,
)


def test_markdown_to_rich_paragraph_styles() -> None:
    doc = markdown_to_rich("# Title\n- item\nplain line")
    assert [p.style for p in doc.paragraphs] == ["heading", "bullet", "paragraph"]
    assert doc.paragraphs[0].level == 1
    assert doc.paragraphs[0].text() == "Title"
    assert doc.paragraphs[1].text() == "item"


def test_markdown_to_rich_inline_runs() -> None:
    doc = markdown_to_rich("A **bold** and *italic* word")
    spans = doc.paragraphs[0].spans
    bold = [s for s in spans if s.bold]
    italic = [s for s in spans if s.italic]
    assert bold and bold[0].text == "bold"
    assert italic and italic[0].text == "italic"


def test_markdown_to_rich_link_span() -> None:
    doc = markdown_to_rich("see [QUILL](https://example.com) now")
    link = [s for s in doc.paragraphs[0].spans if s.href]
    assert link and link[0].text == "QUILL"
    assert link[0].href == "https://example.com"


def test_nested_bold_italic() -> None:
    doc = markdown_to_rich("**bold *both* end**")
    spans = doc.paragraphs[0].spans
    both = [s for s in spans if s.bold and s.italic]
    assert both and both[0].text == "both"


def test_rich_to_markdown_round_trip() -> None:
    markdown = "# Heading\n- first\nbody with **bold** and *italic* and [x](u)"
    assert rich_to_markdown(markdown_to_rich(markdown)) == markdown


def test_rich_to_markdown_merges_adjacent_runs() -> None:
    doc = RichDocument(
        paragraphs=[
            RichParagraph(
                spans=[InlineSpan("a", bold=True), InlineSpan("b", bold=True)],
            )
        ]
    )
    assert rich_to_markdown(doc) == "**ab**"


def test_plain_text_excludes_structure() -> None:
    doc = markdown_to_rich("# Title\n- item\nbody")
    assert doc.plain_text() == "Title\nitem\nbody"


def test_rtf_round_trip_through_rich() -> None:
    markdown = "# Heading One\n\nA **bold** word.\n- one\n- two"
    rtf = rich_to_rtf(markdown_to_rich(markdown))
    assert rtf.startswith("{\\rtf1\\ansi")
    restored = rich_to_markdown(rtf_to_rich(rtf))
    assert restored == markdown


def test_analyze_plain_text_matches_model() -> None:
    markdown = "# Title\n**bold** plain"
    analysis = analyze_markdown(markdown)
    assert analysis.plain_text == "Title\nbold plain"


def test_md_to_plain_length_covers_caret_at_end() -> None:
    markdown = "**bold**"
    analysis = analyze_markdown(markdown)
    assert len(analysis.md_to_plain) == len(markdown) + 1
    # Caret after the closing ** lands at the end of the visible word.
    assert analysis.md_to_plain[len(markdown)] == len("bold")


def test_markdown_offset_to_plain_inside_bold() -> None:
    markdown = "x **bold** y"
    # The 'b' of bold is at md offset 4; visible offset should be 2 ("x b").
    assert markdown_offset_to_plain_offset(markdown, 4) == 2


def test_plain_offset_round_trips_to_markdown() -> None:
    markdown = "x **bold** y"
    plain = markdown_offset_to_plain_offset(markdown, 4)
    assert plain_offset_to_markdown_offset(markdown, plain) == 4


def test_heading_prefix_maps_to_first_visible_char() -> None:
    markdown = "## Big"
    # Caret anywhere in "## " maps to the first visible char of "Big".
    assert markdown_offset_to_plain_offset(markdown, 0) == 0
    assert markdown_offset_to_plain_offset(markdown, 2) == 0


def test_format_at_offset_reports_bold() -> None:
    markdown = "a **bold** b"
    fmt = format_at_markdown_offset(markdown, 6)
    assert fmt.bold is True
    assert fmt.italic is False


def test_format_at_offset_reports_heading_level() -> None:
    fmt = format_at_markdown_offset("### Deep", 6)
    assert fmt.heading_level == 3


def test_format_at_offset_reports_link() -> None:
    markdown = "go [here](http://x) now"
    fmt = format_at_markdown_offset(markdown, 5)
    assert fmt.href == "http://x"


def test_format_at_offset_plain_is_empty() -> None:
    fmt = format_at_markdown_offset("plain text", 3)
    assert fmt.bold is False and fmt.italic is False and fmt.href is None
    assert fmt.heading_level == 0 and fmt.bullet is False


def test_scan_rtf_features_flags_tables_and_images() -> None:
    rtf = r"{\rtf1\ansi \trowd \cell \pict\pngblip ffff}"
    found = scan_rtf_features(rtf)
    assert "tables" in found
    assert "images" in found


def test_scan_rtf_features_clean_subset_is_empty() -> None:
    rtf = r"{\rtf1\ansi\pard {\b bold} text\par}"
    assert scan_rtf_features(rtf) == []
