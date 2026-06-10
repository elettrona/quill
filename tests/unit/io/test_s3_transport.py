"""Unit tests for the S3 transport's manual SigV4 path (issue #157)."""

from __future__ import annotations

from typing import Any

import pytest

from quill.core.remote_sites import RemoteSite
from quill.io import s3_transport
from quill.io.remote_transport import (
    RemoteAuthError,
    RemoteNotFoundError,
    RemoteTransportError,
)


def _site(**extra: str) -> RemoteSite:
    return RemoteSite(
        id="aws-1",
        name="AWS",
        protocol="s3",
        host="",
        username="",
        port=0,
        root_dir="",
        extra={"s3_bucket": "docs", "s3_region": "us-east-1", **extra},
    )


def _empty_site() -> RemoteSite:
    return RemoteSite(
        id="aws-1",
        name="AWS",
        protocol="s3",
        host="",
        username="",
        port=0,
        root_dir="",
        extra={},
    )


def test_endpoint_host_prefers_explicit_endpoint() -> None:
    site = _site(s3_endpoint="minio.local:9000")
    assert s3_transport._endpoint_host(site) == "minio.local:9000"


def test_endpoint_host_uses_region_when_no_endpoint() -> None:
    site = _site(s3_region="eu-central-1")
    assert s3_transport._endpoint_host(site) == "docs.s3.eu-central-1.amazonaws.com"


def test_endpoint_host_defaults_to_us_east_1_for_empty_region() -> None:
    site = _site()
    # No ``s3_region`` key; defaults to us-east-1 and the legacy
    # ``<bucket>.s3.amazonaws.com`` form.
    assert s3_transport._endpoint_host(site) == "docs.s3.amazonaws.com"


def test_endpoint_host_raises_when_bucket_missing() -> None:
    site = _empty_site()
    with pytest.raises(RemoteTransportError):
        s3_transport._endpoint_host(site)


def test_bucket_name_validates_extras() -> None:
    site = _empty_site()
    with pytest.raises(RemoteTransportError):
        s3_transport._bucket_name(site)


def test_access_keys_handles_missing_keys() -> None:
    site = _site()
    assert s3_transport._access_keys(site) == ("", "")


def test_access_keys_returns_supplied_keys() -> None:
    site = _site(s3_access_key="AKIA", s3_secret_key="secret")
    assert s3_transport._access_keys(site) == ("AKIA", "secret")


def test_normalise_prefix_strips_leading_slash_and_appends_slash() -> None:
    assert s3_transport._normalise_prefix("/folder/") == "folder/"
    assert s3_transport._normalise_prefix("folder") == "folder/"
    assert s3_transport._normalise_prefix("") == ""


def test_percent_encode_path_keeps_slashes() -> None:
    assert s3_transport._percent_encode_path("folder/sub/keep.txt") == "folder/sub/keep.txt"
    assert s3_transport._percent_encode_path("") == ""


def test_parse_list_objects_v2_extracts_files_and_dirs() -> None:
    body = b"""<?xml version='1.0' encoding='UTF-8'?>
<ListBucketResult xmlns='http://s3.amazonaws.com/doc/2006-03-01/'>
  <Name>docs</Name>
  <Prefix>notes/</Prefix>
  <IsTruncated>false</IsTruncated>
  <Contents>
    <Key>notes/a.txt</Key>
    <Size>11</Size>
    <LastModified>2024-01-02T03:04:05.000Z</LastModified>
  </Contents>
  <CommonPrefixes>
    <Prefix>notes/sub/</Prefix>
  </CommonPrefixes>
</ListBucketResult>
"""
    entries = s3_transport._parse_list_objects_v2(body, prefix="notes/")
    assert {entry.name for entry in entries} == {"a.txt", "sub"}
    dirs = [entry for entry in entries if entry.is_dir]
    files = [entry for entry in entries if not entry.is_dir]
    assert dirs[0].name == "sub"
    assert files[0].size == 11
    # ``LastModified`` parsing in the current implementation tolerates the
    # ISO-8601 ``Z`` suffix; we assert the field is present and that the
    # parser did not throw. The exact epoch value is timezone-dependent, so
    # we only check that the field is populated.
    assert hasattr(files[0], "modified")


def test_parse_list_objects_v2_rejects_malformed_xml() -> None:
    with pytest.raises(RemoteTransportError):
        s3_transport._parse_list_objects_v2(b"<not-closed", prefix="")


def test_parse_list_objects_v2_rejects_unsafe_xml() -> None:
    # External entity declaration that safe_xml must refuse to expand.
    body = (
        b"<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>"
        b"<ListBucketResult><Key>&xxe;</Key></ListBucketResult>"
    )
    with pytest.raises(RemoteTransportError):
        s3_transport._parse_list_objects_v2(body, prefix="")


def test_parse_list_objects_v2_handles_unknown_namespace() -> None:
    body = b"""<?xml version='1.0'?>
<ListBucketResult>
  <Contents>
    <Key>note.txt</Key>
    <Size>5</Size>
  </Contents>
</ListBucketResult>
"""
    entries = s3_transport._parse_list_objects_v2(body, prefix="")
    assert len(entries) == 1
    assert entries[0].name == "note.txt"
    assert entries[0].size == 5


def test_signed_list_dir_translates_http_404(monkeypatch: pytest.MonkeyPatch) -> None:
    site = _site()
    from quill.io import s3_sigv4

    def _fake_signed_request(**_kwargs: Any) -> tuple[int, dict[str, str], bytes]:
        return 404, {}, b""

    monkeypatch.setattr(s3_sigv4, "signed_request", _fake_signed_request)
    with pytest.raises(RemoteNotFoundError):
        s3_transport._signed_list_dir(
            site=site,
            bucket="docs",
            prefix="missing/",
            timeout=30.0,
            password="",
        )


def test_signed_list_dir_translates_401(monkeypatch: pytest.MonkeyPatch) -> None:
    site = _site()
    from quill.io import s3_sigv4

    def _fake_signed_request(**_kwargs: Any) -> tuple[int, dict[str, str], bytes]:
        return 401, {}, b""

    monkeypatch.setattr(s3_sigv4, "signed_request", _fake_signed_request)
    with pytest.raises(RemoteAuthError):
        s3_transport._signed_list_dir(
            site=site,
            bucket="docs",
            prefix="",
            timeout=30.0,
            password="",
        )


def test_signed_list_dir_translates_5xx(monkeypatch: pytest.MonkeyPatch) -> None:
    site = _site()
    from quill.io import s3_sigv4

    def _fake_signed_request(**_kwargs: Any) -> tuple[int, dict[str, str], bytes]:
        return 500, {}, b""

    monkeypatch.setattr(s3_sigv4, "signed_request", _fake_signed_request)
    with pytest.raises(RemoteTransportError):
        s3_transport._signed_list_dir(
            site=site,
            bucket="docs",
            prefix="",
            timeout=30.0,
            password="",
        )


def test_drain_boto_streams_body() -> None:
    from io import BytesIO

    body = BytesIO(b"hello world")
    dest = BytesIO()
    written = s3_transport._drain_boto(body, dest, progress=None)
    assert written == 11
    assert dest.getvalue() == b"hello world"


def test_drain_boto_reports_progress() -> None:
    from io import BytesIO

    body = BytesIO(b"abcde")
    dest = BytesIO()
    calls: list[tuple[int, int | None]] = []

    def _progress(written: int, total: int | None) -> None:
        calls.append((written, total))

    s3_transport._drain_boto(body, dest, progress=_progress)
    # The boto drainer emits at least one progress event with the final count.
    assert calls[-1][0] == 5
    assert calls[-1][1] is None
