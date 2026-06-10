"""S3 / object storage transport (issue #157).

Goals
-----

* Open and save documents to an S3 bucket using the standard HTTPS endpoint.
* Support public-read anonymous reads (no auth) *and* authenticated
  access-key reads and writes via AWS Signature Version 4.
* Avoid a hard dependency on :mod:`boto3`. The manual SigV4 implementation
  in :mod:`quill.io.s3_sigv4` is the fallback; if :mod:`boto3` is present,
  the transport uses it for a faster cold start.

What is *not* here
------------------

* Multipart uploads. A typical QUILL document is well under the 5 GiB
  single-part limit.
* Versioning, lifecycle, ACL management. Bucket owners configure those
  outside the editor.
* S3-compatible services (MinIO, Wasabi, etc.) — supported in 1.0 with a
  ``s3_endpoint`` extra field; tested in CI against the public AWS endpoint.
* AWS SigV4a (asymmetric). v4 is the only signing scheme used here.

Threading: the same model as the other remote transports. Synchronous;
runs in a background worker.
"""

from __future__ import annotations

import time
from typing import IO, Any

from quill.core.remote_sites import RemoteSite
from quill.core.safe_xml import UnsafeXMLError as _SafeXmlError
from quill.io.remote_transport import (
    DownloadResult,
    ProgressCallback,
    RemoteAuthError,
    RemoteEntry,
    RemoteNotFoundError,
    RemoteTransport,
    RemoteTransportError,
    merge_headers,
)

# Default virtual-hosted style bucket host. ``s3_endpoint`` can override.
_DEFAULT_ENDPOINT_HOST = "s3.amazonaws.com"


def _endpoint_host(site: RemoteSite) -> str:
    explicit = (site.extra or {}).get("s3_endpoint", "").strip()
    if explicit:
        return explicit
    bucket = (site.extra or {}).get("s3_bucket", "").strip()
    if not bucket:
        raise RemoteTransportError("S3 site is missing a bucket (set s3_bucket in extras)")
    # Region-specific endpoints. ``s3.<region>.amazonaws.com`` is the modern
    # form; we honour the ``s3_region`` extra when supplied.
    region = (site.extra or {}).get("s3_region", "").strip() or "us-east-1"
    if region in {"", "us-east-1"}:
        return f"{bucket}.s3.amazonaws.com"
    return f"{bucket}.s3.{region}.amazonaws.com"


def _bucket_name(site: RemoteSite) -> str:
    bucket = (site.extra or {}).get("s3_bucket", "").strip()
    if not bucket:
        raise RemoteTransportError("S3 site is missing a bucket (set s3_bucket in extras)")
    return bucket


def _access_keys(site: RemoteSite) -> tuple[str, str]:
    access_key = (site.extra or {}).get("s3_access_key", "").strip()
    secret_key = (site.extra or {}).get("s3_secret_key", "").strip()
    if not access_key or not secret_key:
        return "", ""
    return access_key, secret_key


class S3Transport(RemoteTransport):
    """An S3 transport with optional :mod:`boto3` and a manual SigV4 fallback."""

    def __init__(
        self,
        site: RemoteSite,
        *,
        password: str = "",
        timeout: float = 30.0,
    ) -> None:
        self._site = site
        self._password = password
        self._timeout = timeout
        self._boto_client: Any = None
        self._closed = False

    # --- lifecycle -----------------------------------------------------------

    def _ensure_boto(self) -> Any | None:
        if self._boto_client is not None:
            return self._boto_client
        try:
            import boto3  # type: ignore[import-not-found]
            from botocore.config import Config  # type: ignore[import-not-found]
        except ImportError:
            return None
        access_key, secret_key = _access_keys(self._site)
        kwargs: dict[str, Any] = {
            "region_name": (self._site.extra or {}).get("s3_region", "us-east-1") or "us-east-1",
            "config": Config(connect_timeout=self._timeout, retries={"max_attempts": 3}),
        }
        if access_key and secret_key:
            kwargs["aws_access_key_id"] = access_key
            kwargs["aws_secret_access_key"] = secret_key
        endpoint_url = (self._site.extra or {}).get("s3_endpoint", "").strip()
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        self._boto_client = boto3.client("s3", **kwargs)
        return self._boto_client

    def close(self) -> None:
        self._closed = True
        client = self._boto_client
        self._boto_client = None
        if client is None:
            return
        # boto3 has no explicit close on the client; releasing the reference
        # is enough because the underlying HTTP session is owned by the SDK.

    # --- public API ----------------------------------------------------------

    def list_dir(self, path: str) -> list[RemoteEntry]:
        prefix = _normalise_prefix(path or self._site.root_dir or "")
        client = self._ensure_boto()
        if client is not None:
            return self._boto_list_dir(client, prefix)
        return self._signed_list_dir(prefix)

    def download(
        self,
        remote_path: str,
        local_path: str,
        *,
        progress: ProgressCallback | None = None,
    ) -> DownloadResult:
        bucket = _bucket_name(self._site)
        key = _normalise_prefix(remote_path)
        client = self._ensure_boto()
        start = time.monotonic()
        if client is not None:
            try:
                response = client.get_object(Bucket=bucket, Key=key)
            except _boto_not_found() as exc:
                raise RemoteNotFoundError(f"s3://{bucket}/{key} not found") from exc
            except _boto_auth_error() as exc:
                raise RemoteAuthError(f"S3 GET denied: {exc}") from exc
            except _boto_other_error() as exc:
                raise RemoteTransportError(f"S3 GET failed: {exc}") from exc
            body = response["Body"]
            with open(local_path, "wb") as dest:
                written = _drain_boto(body, dest, progress=progress)
            return DownloadResult(
                path=local_path,
                size=written,
                mime_type=response.get("ContentType", "") or "",
                elapsed_ms=int((time.monotonic() - start) * 1000),
                headers={"ETag": str(response.get("ETag", ""))},
            )
        # Manual SigV4 path.
        return _signed_download(
            site=self._site,
            bucket=bucket,
            key=key,
            local_path=local_path,
            timeout=self._timeout,
            progress=progress,
            password=self._password,
            start=start,
        )

    def upload(
        self,
        local_path: str,
        remote_path: str,
        *,
        progress: ProgressCallback | None = None,
    ) -> DownloadResult:
        bucket = _bucket_name(self._site)
        key = _normalise_prefix(remote_path)
        client = self._ensure_boto()
        start = time.monotonic()
        with open(local_path, "rb") as source:
            body = source.read()
        if progress is not None:
            progress(len(body), len(body))
        if client is not None:
            try:
                client.put_object(Bucket=bucket, Key=key, Body=body)
            except _boto_auth_error() as exc:
                raise RemoteAuthError(f"S3 PUT denied: {exc}") from exc
            except _boto_other_error() as exc:
                raise RemoteTransportError(f"S3 PUT failed: {exc}") from exc
            return DownloadResult(
                path=local_path,
                size=len(body),
                mime_type="",
                elapsed_ms=int((time.monotonic() - start) * 1000),
                headers=merge_headers([]),
            )
        return _signed_upload(
            site=self._site,
            bucket=bucket,
            key=key,
            body=body,
            timeout=self._timeout,
            password=self._password,
            start=start,
        )

    # --- boto-backed listing -------------------------------------------------

    def _boto_list_dir(self, client: Any, prefix: str) -> list[RemoteEntry]:
        try:
            paginator = client.get_paginator("list_objects_v2")
            paginate_kwargs = {
                "Bucket": _bucket_name(self._site),
                "Prefix": prefix,
                "Delimiter": "/",
            }
            page_iter = paginator.paginate(**paginate_kwargs)
        except _boto_auth_error() as exc:
            raise RemoteAuthError(f"S3 LIST denied: {exc}") from exc
        except _boto_other_error() as exc:
            raise RemoteTransportError(f"S3 LIST failed: {exc}") from exc
        entries: list[RemoteEntry] = []
        for page in page_iter:
            for common_prefix in page.get("CommonPrefixes", []) or []:
                name = str(common_prefix.get("Prefix", "")).rstrip("/").rsplit("/", 1)[-1]
                if name:
                    entries.append(RemoteEntry(name=name, is_dir=True, size=0))
            for obj in page.get("Contents", []) or []:
                key = str(obj.get("Key", ""))
                if not key or key == prefix:
                    continue
                name = key.rsplit("/", 1)[-1]
                if not name:
                    continue
                last_modified = obj.get("LastModified")
                mtime = 0.0
                if last_modified is not None:
                    mtime = float(last_modified.timestamp())
                entries.append(
                    RemoteEntry(
                        name=name,
                        is_dir=False,
                        size=int(obj.get("Size", 0) or 0),
                        modified=mtime,
                    )
                )
        entries.sort(key=lambda entry: (not entry.is_dir, entry.name.lower()))
        return entries

    # --- manual signing helpers ---------------------------------------------

    def _signed_list_dir(self, prefix: str) -> list[RemoteEntry]:
        # The manual listing returns the same entries as the boto path; we
        # delegate to a shared helper so the response parsing is single
        # source of truth.
        return _signed_list_dir(
            site=self._site,
            bucket=_bucket_name(self._site),
            prefix=prefix,
            timeout=self._timeout,
            password=self._password,
        )


# --- boto error class helpers (import-free at module top level) -------------


def _boto_not_found() -> tuple[type[BaseException], ...]:
    try:
        from botocore.exceptions import ClientError  # type: ignore[import-not-found]

        return (ClientError,)
    except ImportError:  # pragma: no cover
        return ()


def _boto_auth_error() -> tuple[type[BaseException], ...]:
    from botocore.exceptions import ClientError  # type: ignore[import-not-found]

    class _AuthCodeFilter(ClientError):  # pragma: no cover - sentinel only
        pass

    return (ClientError,)


def _boto_other_error() -> tuple[type[BaseException], ...]:
    from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-not-found]

    return (BotoCoreError, ClientError)


def _drain_boto(body: Any, dest: IO[bytes], *, progress: ProgressCallback | None) -> int:
    written = 0
    chunk = body.read(64 * 1024)
    while chunk:
        dest.write(chunk)
        written += len(chunk)
        if progress is not None:
            progress(written, None)
        chunk = body.read(64 * 1024)
    return written


def _normalise_prefix(value: str) -> str:
    cleaned = (value or "").strip().lstrip("/")
    if cleaned and not cleaned.endswith("/"):
        cleaned += "/"
    return cleaned


# --- manual SigV4 path ------------------------------------------------------


def _signed_list_dir(
    *,
    site: RemoteSite,
    bucket: str,
    prefix: str,
    timeout: float,
    password: str,
) -> list[RemoteEntry]:
    from quill.io.s3_sigv4 import signed_request

    access_key, secret_key = _access_keys(site)
    if not access_key or not secret_key:
        # Anonymous reads still work for public buckets. ``signed_request``
        # accepts an empty key set and emits an unsigned GET.
        access_key, secret_key = "", ""
    host = _endpoint_host(site)
    url = f"https://{host}/?list-type=2&prefix={_percent_encode(prefix)}&delimiter=/"
    try:
        status, _, body = signed_request(
            method="GET",
            url=url,
            access_key=access_key,
            secret_key=secret_key,
            password=password,
            timeout=timeout,
        )
    except RemoteAuthError:
        raise
    except RemoteTransportError:
        raise
    if status == 404:
        raise RemoteNotFoundError(f"s3://{bucket}/{prefix} not found")
    if status in (401, 403):
        raise RemoteAuthError(f"S3 LIST denied (HTTP {status})")
    if status >= 400:
        raise RemoteTransportError(f"S3 LIST failed: HTTP {status}")
    return _parse_list_objects_v2(body, prefix=prefix)


def _signed_download(
    *,
    site: RemoteSite,
    bucket: str,
    key: str,
    local_path: str,
    timeout: float,
    progress: ProgressCallback | None,
    password: str,
    start: float,
) -> DownloadResult:
    from quill.io.s3_sigv4 import signed_streaming_download

    access_key, secret_key = _access_keys(site)
    host = _endpoint_host(site)
    url = f"https://{host}/{_percent_encode_path(key)}"
    return signed_streaming_download(
        url=url,
        local_path=local_path,
        access_key=access_key,
        secret_key=secret_key,
        password=password,
        timeout=timeout,
        progress=progress,
        start=start,
    )


def _signed_upload(
    *,
    site: RemoteSite,
    bucket: str,
    key: str,
    body: bytes,
    timeout: float,
    password: str,
    start: float,
) -> DownloadResult:
    from quill.io.s3_sigv4 import signed_request

    access_key, secret_key = _access_keys(site)
    host = _endpoint_host(site)
    url = f"https://{host}/{_percent_encode_path(key)}"
    status, headers, _ = signed_request(
        method="PUT",
        url=url,
        access_key=access_key,
        secret_key=secret_key,
        password=password,
        timeout=timeout,
        body=body,
        content_type="application/octet-stream",
    )
    if status in (401, 403):
        raise RemoteAuthError(f"S3 PUT denied (HTTP {status})")
    if status >= 400:
        raise RemoteTransportError(f"S3 PUT failed: HTTP {status}")
    return DownloadResult(
        path="",
        size=len(body),
        mime_type="application/octet-stream",
        elapsed_ms=int((time.monotonic() - start) * 1000),
        headers=headers,
    )


def _percent_encode(value: str) -> str:
    import urllib.parse

    return urllib.parse.quote(value, safe="~")


def _percent_encode_path(value: str) -> str:
    import urllib.parse

    # S3 keys may contain ``/``; we want each segment percent-encoded but
    # keep the slashes.
    segments = [urllib.parse.quote(segment, safe="~") for segment in value.split("/") if segment]
    return "/".join(segments)


def _parse_list_objects_v2(body: bytes, *, prefix: str) -> list[RemoteEntry]:
    from quill.core.safe_xml import ParseError as _SafeParseError
    from quill.core.safe_xml import fromstring as _safe_fromstring

    try:
        root = _safe_fromstring(body)
    except _SafeXmlError as exc:
        raise RemoteTransportError(f"S3 LIST returned unsafe XML: {exc}") from exc
    except _SafeParseError as exc:
        raise RemoteTransportError(f"S3 LIST returned malformed XML: {exc}") from exc
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}", 1)[0] + "}"
    entries: list[RemoteEntry] = []
    for common_prefix in root.findall(f"{ns}CommonPrefixes"):
        raw = common_prefix.find(f"{ns}Prefix")
        if raw is None or raw.text is None:
            continue
        name = raw.text.rstrip("/").rsplit("/", 1)[-1]
        if name:
            entries.append(RemoteEntry(name=name, is_dir=True, size=0))
    for content in root.findall(f"{ns}Contents"):
        key_el = content.find(f"{ns}Key")
        if key_el is None or key_el.text is None:
            continue
        key = key_el.text
        if key == prefix.rstrip("/"):
            continue
        name = key.rsplit("/", 1)[-1]
        if not name:
            continue
        size_el = content.find(f"{ns}Size")
        modified_el = content.find(f"{ns}LastModified")
        size = 0
        if size_el is not None and size_el.text:
            try:
                size = int(size_el.text)
            except ValueError:
                size = 0
        modified = 0.0
        if modified_el is not None and modified_el.text:
            from email.utils import parsedate_to_datetime

            try:
                modified = parsedate_to_datetime(modified_el.text).timestamp()
            except (TypeError, ValueError):
                modified = 0.0
        entries.append(RemoteEntry(name=name, is_dir=False, size=size, modified=modified))
    entries.sort(key=lambda entry: (not entry.is_dir, entry.name.lower()))
    return entries
