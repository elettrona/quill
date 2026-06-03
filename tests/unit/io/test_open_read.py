from __future__ import annotations

from pathlib import Path

from quill.io.open_read import (
    LIGHT_STRUCTURED_SUFFIXES,
    OFFICE_STREAM_SUFFIXES,
    read_open_document,
)


def test_read_open_document_reads_plain_text(tmp_path: Path) -> None:
    target = tmp_path / "note.txt"
    target.write_text("hello world\n", encoding="utf-8")

    loaded, epub_book = read_open_document(target, ".txt")

    assert "hello world" in loaded.text
    assert epub_book is None


def test_read_open_document_tags_csv_grid_metadata(tmp_path: Path) -> None:
    target = tmp_path / "data.csv"
    target.write_text("a,b\n1,2\n", encoding="utf-8")

    loaded, epub_book = read_open_document(target, ".csv", csv_mode="grid")

    assert loaded.source_metadata["csv_open_mode"] == "grid"
    assert loaded.source_metadata["engine"] == "csv grid"
    assert epub_book is None


def test_read_open_document_tags_csv_text_metadata(tmp_path: Path) -> None:
    target = tmp_path / "data.csv"
    target.write_text("a,b\n1,2\n", encoding="utf-8")

    loaded, _ = read_open_document(target, ".csv", csv_mode="text")

    assert loaded.source_metadata["csv_open_mode"] == "text"
    assert loaded.source_metadata["engine"] == "csv text"


def test_read_open_document_applies_word_open_mode(tmp_path: Path, monkeypatch) -> None:
    from quill.core.document import Document

    target = tmp_path / "sample.docx"
    target.write_bytes(b"PK\x03\x04")

    def _fake_read(path: Path) -> Document:
        return Document(text="word body\n", path=path, source_metadata={})

    monkeypatch.setattr("quill.io.structured.read_structured_document", _fake_read)

    loaded, epub_book = read_open_document(target, ".docx", word_mode="structured")

    assert loaded.source_metadata["word_open_mode"] == "structured"
    assert epub_book is None


def test_read_open_document_returns_epub_book(tmp_path: Path) -> None:
    import zipfile

    target = tmp_path / "sample.epub"
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("OEBPS/chapter1.xhtml", "<html><body><p>Hi EPUB</p></body></html>")

    loaded, epub_book = read_open_document(target, ".epub")

    assert "Hi EPUB" in loaded.text
    # An EPUB book object is parsed and handed back for the UI thread to install.
    assert epub_book is not None


def test_office_and_light_suffix_sets_are_disjoint() -> None:
    assert OFFICE_STREAM_SUFFIXES.isdisjoint(LIGHT_STRUCTURED_SUFFIXES)
    assert ".docx" in OFFICE_STREAM_SUFFIXES
    assert ".pptx" in OFFICE_STREAM_SUFFIXES
    assert ".pdf" in OFFICE_STREAM_SUFFIXES
