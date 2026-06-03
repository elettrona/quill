"""Document reading for the editor's open flow.

This module centralizes how a path is turned into a :class:`Document` when the
user opens a file. It is deliberately wx-free so the heavy office and PDF reads
can run on a worker thread (PERF-12) without touching the UI toolkit.

The single public entry point, :func:`read_open_document`, returns the loaded
document together with any parsed EPUB book so the caller can install both on the
UI thread.
"""

from __future__ import annotations

from pathlib import Path

from quill.core.document import Document
from quill.io.text import read_text_document

# PERF-12: heavy office and PDF formats are parsed off the UI thread.
OFFICE_STREAM_SUFFIXES: frozenset[str] = frozenset({
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xlsx",
    ".xls",
    ".pdf",
    ".odt",
    ".rtf",
    ".epub",
    ".pages",
})

# Light structured formats are cheap enough to read on the UI thread.
LIGHT_STRUCTURED_SUFFIXES: frozenset[str] = frozenset({
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
    ".ipynb",
    ".sqlite",
    ".db",
})

_CSV_SUFFIXES: frozenset[str] = frozenset({".csv", ".tsv"})


def read_open_document(
    selected_path: Path,
    suffix: str,
    *,
    word_mode: str | None = None,
    csv_mode: str | None = None,
) -> tuple[Document, object]:
    """Read ``selected_path`` into a document for the open flow.

    Returns the loaded :class:`Document` and any parsed EPUB book (``None`` for
    non-EPUB inputs). ``word_mode`` and ``csv_mode`` carry UI choices that must be
    resolved before calling this function so it never needs the UI toolkit.
    """
    if suffix in _CSV_SUFFIXES:
        loaded = read_text_document(selected_path)
        engine = "csv grid" if csv_mode == "grid" else "csv text"
        mode = "grid" if csv_mode == "grid" else "text"
        loaded.source_metadata = {
            "source_kind": suffix.lstrip("."),
            "engine": engine,
            "quality_score": 100,
            "csv_open_mode": mode,
        }
        return loaded, None

    if suffix in OFFICE_STREAM_SUFFIXES:
        from quill.io.structured import read_structured_document

        loaded = read_structured_document(selected_path)
        if word_mode is not None:
            loaded.source_metadata["word_open_mode"] = word_mode
        epub_book: object = None
        if suffix == ".epub":
            from quill.core.epub import load_epub_book

            epub_book = load_epub_book(selected_path)
        return loaded, epub_book

    if suffix in LIGHT_STRUCTURED_SUFFIXES:
        from quill.io.structured import read_structured_document

        return read_structured_document(selected_path), None

    return read_text_document(selected_path), None
