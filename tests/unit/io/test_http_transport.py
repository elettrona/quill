"""Unit tests for the HTTP/HTTPS transport (issue #155)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import pytest

from quill.io import http_transport
from quill.io.http_transport import HttpDownload, download_url
from quill.io.remote_transport import (
    RemoteAuthError,
    RemoteNotFoundError,
    RemoteTransportError,
)


class _FakeResponse:
    def __init__(
        self,
        body: bytes,
        *,
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._body = body
        self._offset = 0
        self.status = status
        self.headers = headers or {}

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            chunk = self._body[self._offset :]
            self._offset = len(self._body)
            return chunk
        chunk = self._body[self._offset : self._offset + n]
        self._offset += len(chunk)
        return chunk

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_exc: object) -> None:
        return None


class _FakeOpener:
    def __init__(self, responses: list[_FakeResponse]) -> None:
        self._responses = list(responses)
        self.calls: list[str] = []

    def __call__(self, request: Any, timeout: float, context: object) -> _FakeResponse:
        url = request.full_url if hasattr(request, "full_url") else str(request)
        self.calls.append(url)
        if not self._responses:
            raise AssertionError(f"Unexpected request: {url}")
        return self._responses.pop(0)


def test_download_url_writes_body_to_disk(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    out_path = tmp_path / "download.bin"
    response = _FakeResponse(
        b"hello world",
        headers={"Content-Type": "text/plain", "Content-Length": "11"},
    )
    monkeypatch.setattr(http_transport.urllib.request, "urlopen", _FakeOpener([response]))
    result = download_url("https://example.com/file.bin")
    assert isinstance(result, HttpDownload)
    assert Path(result.local_path).read_bytes() == b"hello world"
    assert result.size == 11
    assert result.mime_type == "text/plain"
    assert result.filename == "file.bin"
    _ = out_path  # tmp_path is not used directly; keeps the fixture live for consistency.


def test_download_url_follows_redirects(monkeypatch: pytest.MonkeyPatch) -> None:
    redirect = _FakeResponse(
        b"",
        status=302,
        headers={"Location": "https://other.example.com/asset.txt"},
    )
    body = _FakeResponse(b"ok", headers={"Content-Type": "text/plain"})
    opener = _FakeOpener([redirect, body])
    monkeypatch.setattr(http_transport.urllib.request, "urlopen", opener)
    result = download_url("https://example.com/start")
    assert result.final_url == "https://other.example.com/asset.txt"
    assert result.size == 2


def test_download_url_raises_on_404(monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import HTTPError

    def _raise(_request: Any, **_kwargs: Any) -> _FakeResponse:
        raise HTTPError("https://example.com/missing", 404, "Not Found", {}, BytesIO())

    monkeypatch.setattr(http_transport.urllib.request, "urlopen", _raise)
    with pytest.raises(RemoteNotFoundError):
        download_url("https://example.com/missing")


def test_download_url_raises_on_auth_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    from urllib.error import HTTPError

    def _raise(_request: Any, **_kwargs: Any) -> _FakeResponse:
        raise HTTPError("https://example.com/secret", 401, "Unauthorized", {}, BytesIO())

    monkeypatch.setattr(http_transport.urllib.request, "urlopen", _raise)
    with pytest.raises(RemoteAuthError):
        download_url("https://example.com/secret")


def test_download_url_rejects_too_many_redirects(monkeypatch: pytest.MonkeyPatch) -> None:
    chain = [
        _FakeResponse(b"", status=302, headers={"Location": f"https://example.com/n{i}"})
        for i in range(http_transport._MAX_REDIRECTS + 2)
    ]
    monkeypatch.setattr(http_transport.urllib.request, "urlopen", _FakeOpener(chain))
    with pytest.raises(RemoteTransportError):
        download_url("https://example.com/start")


def test_infer_filename_prefers_content_disposition() -> None:
    headers = {"Content-Disposition": "attachment; filename=example.md"}
    assert http_transport._infer_filename("https://example.com/", headers) == "example.md"


def test_infer_filename_falls_back_to_url_path() -> None:
    name = http_transport._infer_filename("https://example.com/dir/notes.md", {})
    assert name == "notes.md"


def test_infer_filename_returns_untitled_when_unknown() -> None:
    assert http_transport._infer_filename("https://example.com/", {}) == "untitled"
