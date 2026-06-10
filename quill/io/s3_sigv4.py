"""AWS Signature Version 4 (SigV4) implementation for the S3 transport.

This module deliberately ships its own SigV4 signer so QUILL does not require
:mod:`boto3` as a hard dependency. The signer is small (~200 lines), pure
stdlib, and supports the operations the S3 transport actually exercises:

* ``GET`` ``/?list-type=2&...`` (ListObjectsV2)
* ``GET`` ``/{Key}`` (object download — streamed)
* ``PUT`` ``/{Key}`` (object upload)

What is **not** in scope (kept out so the surface stays auditable):

* Chunked uploads / multipart. A QUILL document is well under the single-part
  5 GiB limit; we issue a single ``PUT`` with the whole body.
* Unsigned-payload streaming. The whole body is signed; the upload progress
  callback still gets accurate byte counts.
* STS / temporary credentials. The S3 transport only consumes long-lived
  access/secret pairs from the site ``extra`` keys.

References
----------

* https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-header-based-auth.html
* https://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
"""

from __future__ import annotations

import datetime
import hashlib
import hmac
import time
import urllib.parse
import urllib.request
from typing import IO

from quill.core.net import verified_ssl_context
from quill.io.remote_transport import (
    DownloadResult,
    ProgressCallback,
    RemoteAuthError,
    RemoteNotFoundError,
    RemoteTransportError,
    chunked_copy,
    merge_headers,
)

_SERVICE = "s3"
_ALGORITHM = "AWS4-HMAC-SHA256"
_MAX_DOWNLOAD_BYTES = 256 * 1024 * 1024  # 256 MiB safety cap (documents are small).


def _percent_encode_path(value: str) -> str:
    return "/".join(
        urllib.parse.quote(segment, safe="~-_.()'!*:&=,@")
        for segment in value.split("/")
        if segment
    )


def _canonical_query(query: str) -> str:
    pairs: list[tuple[str, str]] = []
    if query:
        for raw_key, raw_value in urllib.parse.parse_qsl(query, keep_blank_values=True):
            encoded_key = _uri_encode(raw_key, encode_slash=False)
            encoded_value = _uri_encode(raw_value, encode_slash=False)
            pairs.append((encoded_key, encoded_value))
    pairs.sort()
    return "&".join(f"{key}={value}" for key, value in pairs)


def _uri_encode(value: str, *, encode_slash: bool) -> str:
    safe = ""
    if not encode_slash:
        safe = "/"
    return urllib.parse.quote(value, safe=safe + "-_.~")


def _signing_key(secret_key: str, date_stamp: str, region: str) -> bytes:
    prefix = f"AWS4{secret_key}".encode()
    k_date = hmac.new(prefix, date_stamp.encode("utf-8"), hashlib.sha256).digest()
    k_region = hmac.new(k_date, region.encode("utf-8"), hashlib.sha256).digest()
    k_service = hmac.new(k_region, _SERVICE.encode("utf-8"), hashlib.sha256).digest()
    return hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()


def _extract_region_from_host(host: str) -> str:
    # s3.<region>.amazonaws.com or <bucket>.s3-<region>.amazonaws.com
    parts = host.split(".")
    if "s3-" in parts[1] if len(parts) > 1 else False:
        return parts[1].split("-", 1)[1]
    if len(parts) >= 4 and parts[1] == "s3":
        return parts[2]
    return "us-east-1"


def _build_canonical_request(
    method: str,
    canonical_uri: str,
    canonical_query: str,
    canonical_headers: str,
    signed_headers: str,
    payload_hash: str,
) -> str:
    return "\n".join([
        method.upper(),
        canonical_uri,
        canonical_query,
        canonical_headers,
        signed_headers,
        payload_hash,
    ])


def _build_string_to_sign(
    amz_date: str, date_stamp: str, region: str, canonical_request: str
) -> str:
    scope = f"{date_stamp}/{region}/{_SERVICE}/aws4_request"
    hashed = hashlib.sha256(canonical_request.encode()).hexdigest()
    return "\n".join([_ALGORITHM, amz_date, scope, hashed])


def _signature(signing_key: bytes, string_to_sign: str) -> str:
    return hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()


def _amz_now() -> tuple[str, str]:
    now = datetime.datetime.now(datetime.UTC)
    return now.strftime("%Y%m%dT%H%M%SZ"), now.strftime("%Y%m%d")


def signed_request(
    *,
    method: str,
    url: str,
    access_key: str,
    secret_key: str,
    password: str,  # noqa: ARG001 - reserved for STS / session token support
    timeout: float,
    body: bytes | None = None,
    content_type: str | None = None,
) -> tuple[int, dict[str, str], bytes]:
    """Issue a signed HTTPS request and return ``(status, headers, body)``."""

    parsed = urllib.parse.urlparse(url)
    region = _extract_region_from_host(parsed.hostname or "")
    amz_date, date_stamp = _amz_now()
    canonical_uri = _percent_encode_path(parsed.path or "/")
    canonical_query = _canonical_query(parsed.query or "")
    payload_hash = hashlib.sha256(body or b"").hexdigest()
    host = parsed.hostname or ""
    if parsed.port:
        host_header = f"{host}:{parsed.port}"
    else:
        host_header = host
    canonical_headers_parts: list[tuple[str, str]] = [
        ("host", host_header),
        ("x-amz-content-sha256", payload_hash),
        ("x-amz-date", amz_date),
    ]
    if content_type:
        canonical_headers_parts.append(("content-type", content_type))
    canonical_headers_parts.sort(key=lambda pair: pair[0])
    canonical_headers = "".join(f"{name}:{value}\n" for name, value in canonical_headers_parts)
    signed_headers = ";".join(name for name, _ in canonical_headers_parts)
    canonical_request = _build_canonical_request(
        method, canonical_uri, canonical_query, canonical_headers, signed_headers, payload_hash
    )
    string_to_sign = _build_string_to_sign(amz_date, date_stamp, region, canonical_request)
    signing_key = _signing_key(secret_key, date_stamp, region)
    sig = _signature(signing_key, string_to_sign)
    authorization = (
        f"{_ALGORITHM} Credential={access_key}/{date_stamp}/{region}/{_SERVICE}/aws4_request, "
        f"SignedHeaders={signed_headers}, Signature={sig}"
    )
    headers = {
        "Authorization": authorization,
        "Host": host_header,
        "x-amz-content-sha256": payload_hash,
        "x-amz-date": amz_date,
        "User-Agent": "QUILL/1.0",
    }
    if content_type:
        headers["Content-Type"] = content_type
    if body is not None:
        headers["Content-Length"] = str(len(body))
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=timeout, context=verified_ssl_context())
    except urllib.error.HTTPError as exc:
        status = int(exc.code or 0)
        message = exc.reason or f"HTTP {status}"
        if status in (301, 302, 307, 308):
            raise RemoteTransportError(f"S3 redirect not followed: {message}") from exc
        if status in (401, 403):
            raise RemoteAuthError(f"S3 {method} denied: {message}") from exc
        if status == 404:
            raise RemoteNotFoundError(f"S3 {method} {parsed.path}: {message}") from exc
        raise RemoteTransportError(f"S3 {method} failed: {message}") from exc
    except urllib.error.URLError as exc:
        raise RemoteTransportError(f"S3 {method} failed: {exc.reason}") from exc
    with response:
        payload = response.read(_MAX_DOWNLOAD_BYTES)
    return int(response.status), merge_headers(response.headers.items()), payload


def signed_streaming_download(
    *,
    url: str,
    local_path: str,
    access_key: str,
    secret_key: str,
    password: str,  # noqa: ARG001
    timeout: float,
    progress: ProgressCallback | None,
    start: float,
) -> DownloadResult:
    """Issue a signed GET and stream the response body to ``local_path``."""

    parsed = urllib.parse.urlparse(url)
    region = _extract_region_from_host(parsed.hostname or "")
    amz_date, date_stamp = _amz_now()
    canonical_uri = _percent_encode_path(parsed.path or "/")
    canonical_query = _canonical_query(parsed.query or "")
    payload_hash = hashlib.sha256(b"").hexdigest()
    host = parsed.hostname or ""
    host_header = f"{host}:{parsed.port}" if parsed.port else host
    canonical_headers_parts = [
        ("host", host_header),
        ("x-amz-content-sha256", payload_hash),
        ("x-amz-date", amz_date),
    ]
    canonical_headers_parts.sort(key=lambda pair: pair[0])
    canonical_headers = "".join(f"{name}:{value}\n" for name, value in canonical_headers_parts)
    signed_headers = ";".join(name for name, _ in canonical_headers_parts)
    canonical_request = _build_canonical_request(
        "GET", canonical_uri, canonical_query, canonical_headers, signed_headers, payload_hash
    )
    string_to_sign = _build_string_to_sign(amz_date, date_stamp, region, canonical_request)
    signing_key = _signing_key(secret_key, date_stamp, region)
    sig = _signature(signing_key, string_to_sign)
    authorization = (
        f"{_ALGORITHM} Credential={access_key}/{date_stamp}/{region}/{_SERVICE}/aws4_request, "
        f"SignedHeaders={signed_headers}, Signature={sig}"
    )
    headers = {
        "Authorization": authorization,
        "Host": host_header,
        "x-amz-content-sha256": payload_hash,
        "x-amz-date": amz_date,
        "User-Agent": "QUILL/1.0",
    }
    request = urllib.request.Request(url, method="GET", headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=timeout, context=verified_ssl_context())
    except urllib.error.HTTPError as exc:
        status = int(exc.code or 0)
        message = exc.reason or f"HTTP {status}"
        if status in (401, 403):
            raise RemoteAuthError(f"S3 GET denied: {message}") from exc
        if status == 404:
            raise RemoteNotFoundError(f"S3 GET {parsed.path}: {message}") from exc
        raise RemoteTransportError(f"S3 GET failed: {message}") from exc
    except urllib.error.URLError as exc:
        raise RemoteTransportError(f"S3 GET failed: {exc.reason}") from exc
    total_header = response.headers.get("Content-Length")
    try:
        total = int(total_header) if total_header else None
    except ValueError:
        total = None
    with response, open(local_path, "wb") as dest:
        written = chunked_download(response, dest, total=total, progress=progress)
    return DownloadResult(
        path=local_path,
        size=written,
        mime_type=response.headers.get("Content-Type", "") or "",
        elapsed_ms=int((time.monotonic() - start) * 1000),
        headers=merge_headers(response.headers.items()),
    )


def chunked_download(
    response: IO[bytes],
    dest: IO[bytes],
    *,
    total: int | None,
    progress: ProgressCallback | None,
) -> int:
    """Stream an ``urllib`` response body to ``dest`` honouring a 256 MiB cap."""

    if total is not None and total > _MAX_DOWNLOAD_BYTES:
        raise RemoteTransportError(
            f"S3 object is {total} bytes; QUILL refuses downloads larger than 256 MiB"
        )
    return chunked_copy(response, dest, total=total, progress=progress)  # type: ignore[arg-type]
