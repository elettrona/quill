from quill.core.browser_preview import render_preview_body, render_preview_html


def test_render_preview_body_light_has_no_dark_style() -> None:
    body = render_preview_body("# Title\n\nHello", "markdown")
    assert "background:#1e1e1e" not in body
    assert "<h1" in body


def test_render_preview_body_dark_injects_dark_stylesheet() -> None:
    # Issue #83: in dark mode the preview WebView must render dark too, so the
    # split view is not half dark, half bright.
    body = render_preview_body("# Title\n\nHello", "markdown", dark=True)
    assert "background:#1e1e1e" in body
    assert "color:#e6e6e6" in body
    # The rendered content still follows the injected style.
    assert "<h1" in body


def test_render_preview_body_dark_applies_to_html_and_plain() -> None:
    html_body = render_preview_body("<h1>Hi</h1>", "html", dark=True)
    assert "background:#1e1e1e" in html_body
    plain_body = render_preview_body("just text", "plain", dark=True)
    assert "background:#1e1e1e" in plain_body
    assert "<pre>" in plain_body


def test_render_preview_html_adapts_links_for_dark_browsers() -> None:
    # Issue #126: the standalone browser preview must follow the OS colour
    # scheme so links are not the default blue (which fails contrast) on a dark
    # background.
    page = render_preview_html("Doc", "[link](https://x)", "markdown")
    assert "color-scheme:light dark" in page
    assert "@media (prefers-color-scheme: dark)" in page
    # A light-blue link colour, not the default #0000ee, on dark backgrounds.
    assert "a{color:#6cb6ff;}" in page


def test_render_preview_html_has_no_refresh_tag_by_default() -> None:
    # Issue #46: one-shot pages (the User Guide, keyboard reference, etc.)
    # must not get the live-preview auto-refresh tag, or they reload forever.
    page = render_preview_html("Doc", "hello", "markdown")
    assert "http-equiv" not in page


def test_render_preview_html_live_includes_refresh_tag() -> None:
    # The live browser preview still needs to poll so an open tab tracks edits.
    page = render_preview_html("Doc", "hello", "markdown", live=True)
    assert '<meta http-equiv="refresh" content="1">' in page
