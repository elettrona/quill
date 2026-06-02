from pathlib import Path

import pytest

from quill.core.document import Document
from quill.io.text import read_text_document, write_text_document


def test_read_text_document(tmp_path: Path) -> None:
    target = tmp_path / "example.txt"
    target.write_text("hello\nworld\n", encoding="utf-8")

    document = read_text_document(target)
    assert document.text == "hello\nworld\n"
    assert document.path == target
    assert document.modified is False


def test_write_text_document(tmp_path: Path) -> None:
    target = tmp_path / "save.txt"
    document = Document(text="line1\nline2", line_ending="\r\n")

    write_text_document(document, target)
    assert target.read_text(encoding="utf-8") == "line1\nline2"
    assert document.path == target
    assert document.modified is False


def test_write_text_document_requires_path() -> None:
    document = Document(text="x")
    with pytest.raises(ValueError):
        write_text_document(document)


def test_read_markdown_document_preserves_source_verbatim(tmp_path: Path) -> None:
    target = tmp_path / "notes.md"
    markdown = "# Title\n\n- one\n- two\n\n**bold** and `code`\n"
    target.write_text(markdown, encoding="utf-8")

    document = read_text_document(target)

    # Markdown is edited as plain text, so the reader keeps it byte-for-byte.
    assert document.text == markdown
    assert document.source_metadata["source_kind"] == "text"
    assert document.modified is False


def test_read_html_document_preserves_markup(tmp_path: Path) -> None:
    target = tmp_path / "page.html"
    html = "<html>\n  <body>\n    <p>Hello &amp; welcome</p>\n  </body>\n</html>\n"
    target.write_text(html, encoding="utf-8")

    document = read_text_document(target)

    # HTML opens as plain text; entities and tags are left untouched.
    assert document.text == html
    assert "<p>Hello &amp; welcome</p>" in document.text


def test_markdown_roundtrip_through_writer(tmp_path: Path) -> None:
    source = tmp_path / "in.md"
    source.write_text("# Heading\n\nBody line\n", encoding="utf-8")
    document = read_text_document(source)

    destination = tmp_path / "out.md"
    write_text_document(document, destination)

    assert destination.read_text(encoding="utf-8") == "# Heading\n\nBody line\n"
