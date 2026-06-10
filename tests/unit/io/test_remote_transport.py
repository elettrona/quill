"""Unit tests for the shared transport helpers."""

from __future__ import annotations

from io import BytesIO

import pytest

from quill.io.remote_transport import (
    DownloadResult,
    RemoteAuthError,
    RemoteEntry,
    RemoteNotFoundError,
    RemoteTransportError,
    chunked_copy,
    merge_headers,
)


def test_remote_entry_to_display_brackets_dirs() -> None:
    assert RemoteEntry(name="sub", is_dir=True).to_display() == "[sub]"
    assert RemoteEntry(name="note.md", is_dir=False).to_display() == "note.md"


def test_merge_headers_skips_blank_names() -> None:
    out = merge_headers([("", "ignored"), ("X-OK", "yes"), ("X-N", "n")])
    assert out == {"X-OK": "yes", "X-N": "n"}


def test_merge_headers_coerces_to_strings() -> None:
    out = merge_headers([("X-Int", 1)])  # type: ignore[list-item]
    assert out == {"X-Int": "1"}


def test_chunked_copy_streams_entire_buffer() -> None:
    src = BytesIO(b"abcdefghij")
    dest = BytesIO()
    written = chunked_copy(src, dest, total=10)
    assert written == 10
    assert dest.getvalue() == b"abcdefghij"


def test_chunked_copy_emits_progress() -> None:
    src = BytesIO(b"abc")
    dest = BytesIO()
    calls: list[tuple[int, int | None]] = []

    def _progress(written: int, total: int | None) -> None:
        calls.append((written, total))

    chunked_copy(src, dest, total=3, progress=_progress, chunk_size=1)
    # Three 1-byte chunks; the final progress event reports the full count.
    assert calls[-1] == (3, 3)


def test_chunked_copy_handles_none_total() -> None:
    src = BytesIO(b"x")
    dest = BytesIO()
    written = chunked_copy(src, dest, total=None)
    assert written == 1


def test_remote_transport_error_hierarchy() -> None:
    assert issubclass(RemoteAuthError, RemoteTransportError)
    assert issubclass(RemoteNotFoundError, RemoteTransportError)
    with pytest.raises(RemoteTransportError):
        raise RemoteAuthError("nope")


def test_download_result_defaults() -> None:
    result = DownloadResult(path="x", size=10)
    assert result.path == "x"
    assert result.size == 10
    assert result.mime_type == ""
    assert result.elapsed_ms == 0
    assert result.headers == {}
