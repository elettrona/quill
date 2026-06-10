"""Unit tests for the WebDAV transport's PROPFIND parser (issue #156)."""

from __future__ import annotations

import base64
from io import BytesIO

import pytest

from quill.core.remote_sites import RemoteSite
from quill.io import webdav_transport
from quill.io.remote_transport import RemoteTransportError


def test_parse_propfind_extracts_files_and_dirs() -> None:
    body = b"""<?xml version='1.0' encoding='utf-8'?>
<d:multistatus xmlns:d='DAV:'>
  <d:response>
    <d:href>/dav/</d:href>
    <d:propstat>
      <d:prop>
        <d:resourcetype><d:collection/></d:resourcetype>
        <d:getcontentlength>0</d:getcontentlength>
        <d:getlastmodified>Tue, 02 Jan 2024 03:04:05 GMT</d:getlastmodified>
      </d:prop>
      <d:status>HTTP/1.1 200 OK</d:status>
    </d:propstat>
  </d:response>
  <d:response>
    <d:href>/dav/notes.md</d:href>
    <d:propstat>
      <d:prop>
        <d:resourcetype/>
        <d:getcontentlength>42</d:getcontentlength>
        <d:getlastmodified>Wed, 03 Jan 2024 11:22:33 GMT</d:getlastmodified>
      </d:prop>
      <d:status>HTTP/1.1 200 OK</d:status>
    </d:propstat>
  </d:response>
  <d:response>
    <d:href>/dav/sub/</d:href>
    <d:propstat>
      <d:prop>
        <d:resourcetype><d:collection/></d:resourcetype>
        <d:getcontentlength>0</d:getcontentlength>
      </d:prop>
      <d:status>HTTP/1.1 200 OK</d:status>
    </d:propstat>
  </d:response>
</d:multistatus>
"""
    entries = webdav_transport._parse_propfind(
        body, base_url="https://example.com/dav/", current="/dav/"
    )
    names = {(entry.name, entry.is_dir) for entry in entries}
    # The collection itself is skipped; only the notes file and the sub
    # directory are returned.
    assert ("notes.md", False) in names
    assert ("sub", True) in names
    files = [entry for entry in entries if entry.name == "notes.md"]
    assert files[0].size == 42


def test_parse_propfind_handles_empty_body() -> None:
    assert webdav_transport._parse_propfind(b"", base_url="x", current="y") == []


def test_parse_propfind_rejects_malformed_xml() -> None:
    with pytest.raises(webdav_transport.RemoteTransportError):
        webdav_transport._parse_propfind(b"<unclosed", base_url="x", current="y")


def test_parse_propfind_rejects_unsafe_xml() -> None:
    body = (
        b"<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>"
        b"<d:multistatus xmlns:d='DAV:'><d:response/></d:multistatus>"
    )
    with pytest.raises(webdav_transport.RemoteTransportError):
        webdav_transport._parse_propfind(body, base_url="x", current="y")


def test_parse_propfind_skips_responses_without_href() -> None:
    body = b"""<?xml version='1.0'?>
<d:multistatus xmlns:d='DAV:'>
  <d:response>
    <d:propstat>
      <d:prop><d:resourcetype/></d:prop>
    </d:propstat>
  </d:response>
</d:multistatus>
"""
    assert webdav_transport._parse_propfind(body, base_url="/", current="/") == []


def test_build_basic_auth_handles_missing_username() -> None:
    site = RemoteSite(
        id="x",
        name="x",
        protocol="webdav",
        host="example.com",
        username="",
        port=443,
        root_dir="",
        extra={},
    )
    assert webdav_transport.WebDavTransport._build_basic_auth(site, password="") is None


def test_build_basic_auth_emits_basic_header() -> None:
    site = RemoteSite(
        id="x",
        name="x",
        protocol="webdav",
        host="example.com",
        username="alice",
        port=443,
        root_dir="",
        extra={},
    )
    header = webdav_transport.WebDavTransport._build_basic_auth(site, password="secret")
    assert header is not None
    assert header.startswith("Basic ")
    decoded = base64.b64decode(header.split(" ", 1)[1]).decode("ascii")
    assert decoded == "alice:secret"


def test_build_base_url_with_explicit_override() -> None:
    site = RemoteSite(
        id="x",
        name="x",
        protocol="webdav",
        host="example.com",
        username="",
        port=443,
        root_dir="",
        extra={"webdav_base": "https://files.example.com/remote.php/dav/files/alice"},
    )
    assert (
        webdav_transport.WebDavTransport._build_base_url(site)
        == "https://files.example.com/remote.php/dav/files/alice"
    )


def test_build_base_url_requires_host_when_no_override() -> None:
    site = RemoteSite(
        id="x",
        name="x",
        protocol="webdav",
        host="",
        username="",
        port=443,
        root_dir="",
        extra={},
    )
    with pytest.raises(RemoteTransportError):
        webdav_transport.WebDavTransport._build_base_url(site)


def test_parse_http_date_returns_zero_on_invalid_input() -> None:
    assert webdav_transport._parse_http_date("") == 0.0
    assert webdav_transport._parse_http_date("not a date") == 0.0


def test_file_size_seeks_back_to_original_position() -> None:
    handle = BytesIO(b"abcdefghij")
    handle.seek(3)
    size = webdav_transport._file_size(handle)
    assert size == 10
    assert handle.tell() == 3
