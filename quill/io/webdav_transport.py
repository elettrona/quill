"""WebDAV transport (issue #156).

A *minimal*, *RFC 4918*-compliant WebDAV client built on :mod:`urllib`. The
goal is to read and write plain-text-ish files (``.md``, ``.txt``, ``.rst``,
``.html``) on a WebDAV share, not to be a general-purpose WebDAV file system.

Why not use an existing library? ``webdavclient`` and ``easywebdav`` both
pull in :mod:`requests` as a hard dependency and ship with feature sets we
do not need. The protocol surface we exercise is small:

* ``PROPFIND`` for directory listings (depth 1).
* ``GET`` for downloads.
* ``PUT`` for uploads.
* ``MKCOL`` for directory creation (used by the "Save to Remote" dialog).
* ``MOVE`` for renames.
* ``DELETE`` for remove (with a confirm step in the UI layer).

Everything else (locking, partial GET, source/property management) is out
of scope for 1.0 and is documented in ``editors.md`` §10.

Threading: the same model as :class:`quill.io.ftp_transport.FtpTransport`.
Synchronous; one transport per ``Open from Remote`` invocation; progress
callbacks are advisory.
"""

from __future__ import annotations

import io
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import IO, Any
from urllib.request import Request

from quill.core.net import verified_ssl_context
from quill.core.remote_sites import RemoteSite
from quill.core.safe_xml import Element as _SafeElement
from quill.core.safe_xml import UnsafeXMLError as _SafeXmlError
from quill.io.remote_transport import (
    DownloadResult,
    ProgressCallback,
    RemoteAuthError,
    RemoteEntry,
    RemoteNotFoundError,
    RemoteTransport,
    RemoteTransportError,
    chunked_copy,
    merge_headers,
)

_DAV_NS = "{DAV:}"
_MAX_BODY_BYTES = 16 * 1024 * 1024  # 16 MiB; WebDAV listings are tiny.


class WebDavTransport(RemoteTransport):
    """A small WebDAV client (depth-1 PROPFIND, GET, PUT, MKCOL, MOVE)."""

    def __init__(
        self,
        site: RemoteSite,
        *,
        password: str,
        timeout: float = 30.0,
    ) -> None:
        self._site = site
        self._password = password
        self._timeout = timeout
        self._base_url = self._build_base_url(site)
        self._auth_header = self._build_basic_auth(site, password)

    # --- helpers -------------------------------------------------------------

    @staticmethod
    def _build_base_url(site: RemoteSite) -> str:
        scheme = "https"
        host = site.host
        port = site.port or 443
        base = (site.extra or {}).get("webdav_base", "").strip()
        if base.startswith("http://") or base.startswith("https://"):
            return base.rstrip("/")
        if not host:
            raise RemoteTransportError("WebDAV site is missing a host")
        if (port == 80 and scheme == "http") or (port == 443 and scheme == "https"):
            netloc = host
        else:
            netloc = f"{host}:{port}"
        path = base if base.startswith("/") else f"/{base}" if base else ""
        return f"{scheme}://{netloc}{path}".rstrip("/")

    @staticmethod
    def _build_basic_auth(site: RemoteSite, password: str) -> str | None:
        import base64

        username = (site.username or "").strip()
        if not username:
            return None
        token = base64.b64encode(f"{username}:{password or ''}".encode()).decode("ascii")
        return f"Basic {token}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
        stream_to: IO[bytes] | None = None,
    ) -> tuple[int, dict[str, str], bytes]:
        url = self._url_for(path)
        merged_headers = {
            "User-Agent": "QUILL/1.0",
            "Accept": "*/*",
        }
        if self._auth_header is not None:
            merged_headers["Authorization"] = self._auth_header
        if headers:
            merged_headers.update(headers)
        request = Request(url, data=body, method=method, headers=merged_headers)
        try:
            response = urllib.request.urlopen(
                request,
                timeout=self._timeout,
                context=verified_ssl_context(),
            )
        except urllib.error.HTTPError as exc:
            self._raise_for_status(exc, method=method, path=path)
            raise  # unreachable; the helper always raises
        except urllib.error.URLError as exc:
            raise RemoteTransportError(f"WebDAV {method} failed: {exc.reason}") from exc
        with response:
            if stream_to is not None:
                payload = self._stream_response(response, stream_to)
            else:
                payload = response.read(_MAX_BODY_BYTES)
        return response.status, merge_headers(response.headers.items()), payload

    @staticmethod
    def _stream_response(response: Any, dest: IO[bytes]) -> bytes:
        # We track how many bytes we have drained so we can fail loudly if
        # the response is bigger than the dialog is willing to handle.
        drained = bytearray()
        while True:
            chunk = response.read(64 * 1024)
            if not chunk:
                break
            dest.write(chunk)
            if len(drained) + len(chunk) > _MAX_BODY_BYTES:
                raise RemoteTransportError("WebDAV response exceeds the 16 MiB safety cap")
            drained.extend(chunk)
        return bytes(drained)

    @staticmethod
    def _raise_for_status(exc: urllib.error.HTTPError, *, method: str, path: str) -> None:
        status = int(getattr(exc, "code", 0) or 0)
        message = exc.reason or f"HTTP {status}"
        if status in (401, 403):
            raise RemoteAuthError(f"{method} {path}: {message}") from exc
        if status == 404:
            raise RemoteNotFoundError(f"{method} {path}: {message}") from exc
        raise RemoteTransportError(f"{method} {path} failed: {message}") from exc

    def _url_for(self, path: str) -> str:
        if not path:
            return self._base_url + "/"
        if path.startswith("http://") or path.startswith("https://"):
            return path
        cleaned = path.lstrip("/")
        return f"{self._base_url}/{cleaned}"

    # --- public API ----------------------------------------------------------

    def list_dir(self, path: str) -> list[RemoteEntry]:
        target = path or self._site.root_dir or "/"
        url = self._url_for(target)
        body = (
            b'<?xml version="1.0" encoding="utf-8" ?>'
            b'<d:propfind xmlns:d="DAV:">'
            b"<d:prop><d:resourcetype/><d:getcontentlength/><d:getlastmodified/></d:prop>"
            b"</d:propfind>"
        )
        status, _, payload = self._request(
            "PROPFIND",
            target,
            body=body,
            headers={"Depth": "1", "Content-Type": "application/xml; charset=utf-8"},
        )
        if status not in (207, 200):
            raise RemoteTransportError(f"PROPFIND returned HTTP {status}")
        return _parse_propfind(payload, base_url=url, current=target)

    def download(
        self,
        remote_path: str,
        local_path: str,
        *,
        progress: ProgressCallback | None = None,
    ) -> DownloadResult:
        request = Request(self._url_for(remote_path), headers=self._common_headers())
        start = time.monotonic()
        try:
            response = urllib.request.urlopen(
                request,
                timeout=self._timeout,
                context=verified_ssl_context(),
            )
        except urllib.error.HTTPError as exc:
            self._raise_for_status(exc, method="GET", path=remote_path)
            raise
        except urllib.error.URLError as exc:
            raise RemoteTransportError(f"WebDAV GET failed: {exc.reason}") from exc
        total_header = response.headers.get("Content-Length")
        try:
            total = int(total_header) if total_header else None
        except ValueError:
            total = None
        with response, open(local_path, "wb") as dest:
            source = response
            written = chunked_copy(source, dest, total=total, progress=progress)
        return DownloadResult(
            path=local_path,
            size=written,
            mime_type=response.headers.get("Content-Type", ""),
            elapsed_ms=int((time.monotonic() - start) * 1000),
            headers=merge_headers(response.headers.items()),
        )

    def upload(
        self,
        local_path: str,
        remote_path: str,
        *,
        progress: ProgressCallback | None = None,
    ) -> DownloadResult:
        start = time.monotonic()
        with open(local_path, "rb") as source:
            total = _file_size(source)
            buffer = io.BytesIO()
            chunked_copy(source, buffer, total=total, progress=progress)
            body = buffer.getvalue()
        status, headers, _ = self._request(
            "PUT",
            remote_path,
            body=body,
            headers={"Content-Type": "application/octet-stream", "Content-Length": str(len(body))},
        )
        if status not in (200, 201, 204):
            raise RemoteTransportError(f"PUT {remote_path} failed: HTTP {status}")
        return DownloadResult(
            path=local_path,
            size=len(body),
            mime_type=headers.get("Content-Type", ""),
            elapsed_ms=int((time.monotonic() - start) * 1000),
            headers=headers,
        )

    def close(self) -> None:
        # urllib uses one-shot connections; nothing to release explicitly.
        return None

    def _common_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"User-Agent": "QUILL/1.0", "Accept": "*/*"}
        if self._auth_header is not None:
            headers["Authorization"] = self._auth_header
        return headers


def _parse_propfind(payload: bytes, *, base_url: str, current: str) -> list[RemoteEntry]:
    """Translate a depth-1 ``PROPFIND`` XML response into :class:`RemoteEntry` rows."""

    if not payload:
        return []
    from quill.core.safe_xml import ParseError as _SafeParseError
    from quill.core.safe_xml import fromstring as _safe_fromstring

    try:
        root = _safe_fromstring(payload)
    except _SafeXmlError as exc:
        raise RemoteTransportError(f"WebDAV PROPFIND returned unsafe XML: {exc}") from exc
    except _SafeParseError as exc:
        raise RemoteTransportError(f"WebDAV PROPFIND returned malformed XML: {exc}") from exc
    entries: list[RemoteEntry] = []
    base_path = urllib.parse.unquote(urllib.parse.urlparse(base_url).path.rstrip("/"))
    current_path = urllib.parse.unquote(urllib.parse.urlparse(current).path.rstrip("/"))
    for response in root.findall(f"{_DAV_NS}response"):
        href = _find_text(response, f"{_DAV_NS}href") or ""
        if not href:
            continue
        href_path = urllib.parse.unquote(urllib.parse.urlparse(href).path.rstrip("/"))
        # Depth 1 returns the directory itself as the first response; skip it
        # so the dialog shows only the children.
        if href_path == current_path or href_path == base_path and current_path == "":
            continue
        name = href_path.rsplit("/", 1)[-1]
        if not name or name in {".", ".."}:
            continue
        propstat = response.find(f"{_DAV_NS}propstat")
        if propstat is None:
            continue
        prop = propstat.find(f"{_DAV_NS}prop")
        if prop is None:
            continue
        resource_type = prop.find(f"{_DAV_NS}resourcetype")
        is_dir = (
            resource_type is not None and resource_type.find(f"{_DAV_NS}collection") is not None
        )
        try:
            size = int(_find_text(prop, f"{_DAV_NS}getcontentlength") or 0)
        except ValueError:
            size = 0
        mtime = _parse_http_date(_find_text(prop, f"{_DAV_NS}getlastmodified") or "")
        entries.append(RemoteEntry(name=name, is_dir=is_dir, size=size, modified=mtime))
    entries.sort(key=lambda entry: (not entry.is_dir, entry.name.lower()))
    return entries


def _find_text(element: _SafeElement, tag: str) -> str | None:
    child = element.find(tag)
    if child is None or child.text is None:
        return None
    return child.text.strip()


def _parse_http_date(raw: str) -> float:
    if not raw:
        return 0.0
    from email.utils import parsedate_to_datetime

    try:
        return parsedate_to_datetime(raw).timestamp()
    except (TypeError, ValueError):
        return 0.0


def _file_size(handle: IO[bytes]) -> int:
    current = handle.tell()
    handle.seek(0, io.SEEK_END)
    size = handle.tell()
    handle.seek(current)
    return size
