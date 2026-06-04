from quill.core.format_speech import describe_format_transition, describe_inline_format


def test_plain_text_is_silent() -> None:
    assert describe_inline_format() == ""


def test_bold_only() -> None:
    assert describe_inline_format(bold=True) == "bold"


def test_bold_italic_combined() -> None:
    assert describe_inline_format(bold=True, italic=True) == "bold italic"


def test_link() -> None:
    assert describe_inline_format(href="http://x") == "link"


def test_heading_level() -> None:
    assert describe_inline_format(heading_level=2) == "heading level 2"


def test_heading_with_inline() -> None:
    assert describe_inline_format(heading_level=1, bold=True) == "heading level 1, bold"


def test_bullet_with_inline() -> None:
    assert describe_inline_format(bullet=True, italic=True) == "bullet, italic"


def test_transition_enter_bold() -> None:
    assert describe_format_transition("", "bold") == "bold"


def test_transition_leave_to_plain() -> None:
    assert describe_format_transition("bold", "") == "plain"


def test_transition_no_change_is_silent() -> None:
    assert describe_format_transition("bold", "bold") == ""
