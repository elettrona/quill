from __future__ import annotations

import hmac
import json

from quill.core.updates import (
    DEFAULT_UPDATE_MANIFEST_URL,
    GitHubRelease,
    is_newer_version,
    parse_update_manifest,
    select_latest,
)


def _signed_payload(version: str, download_url: str, published_at: str, notes: str) -> str:
    canonical = json.dumps(
        {
            "download_url": download_url,
            "notes": notes,
            "published_at": published_at,
            "version": version,
        },
        separators=(",", ":"),
        sort_keys=True,
    )
    signature = hmac.new(
        b"quill-manifest-signature-v1",
        canonical.encode("utf-8"),
        "sha256",
    ).hexdigest()
    return json.dumps({
        "version": version,
        "download_url": download_url,
        "published_at": published_at,
        "notes": notes,
        "signature": signature,
    })


def test_parse_update_manifest_accepts_valid_signature() -> None:
    payload = _signed_payload(
        "1.2.3",
        "https://community-access.github.io/quill/releases/download/v1.2.3/Quill-Setup.exe",
        "2026-05-01",
        "Fixes.",
    )
    manifest = parse_update_manifest(payload)
    assert manifest.version == "1.2.3"
    assert manifest.download_url.endswith("/Quill-Setup.exe")


def test_parse_update_manifest_rejects_bad_signature() -> None:
    payload = json.dumps({
        "version": "1.2.3",
        "download_url": "https://community-access.github.io/quill/releases/download/v1.2.3/Quill-Setup.exe",
        "published_at": "2026-05-01",
        "notes": "Fixes.",
        "signature": "bad",
    })
    try:
        parse_update_manifest(payload)
    except ValueError as exc:
        assert "signature verification failed" in str(exc)
    else:
        raise AssertionError("Expected signature verification failure")


def test_is_newer_version_compares_semver_triplets() -> None:
    assert is_newer_version("0.1.0", "0.2.0") is True
    assert is_newer_version("1.2.3", "1.2.3") is False


def test_final_release_outranks_its_prereleases() -> None:
    # A final build is newer than any pre-release of the same x.y.z.
    assert is_newer_version("1.2.0-rc1", "1.2.0") is True
    assert is_newer_version("1.2.0", "1.2.0-rc1") is False


def test_prerelease_stages_order_rc_above_beta_above_alpha() -> None:
    assert is_newer_version("1.2.0-beta1", "1.2.0-rc1") is True
    assert is_newer_version("1.2.0-alpha1", "1.2.0-beta1") is True
    assert is_newer_version("1.2.0-rc1", "1.2.0-rc2") is True


def test_prerelease_suffix_does_not_leak_into_patch_number() -> None:
    # "1.2.0-rc1" must not be read as patch 1, which would outrank 1.2.0.
    assert is_newer_version("1.2.0", "1.2.0-rc1") is False


def _release(version: str, *, prerelease: bool) -> GitHubRelease:
    return GitHubRelease(
        version=version,
        download_url="https://example.invalid/x",
        published_at="2026-01-01",
        notes="",
        prerelease=prerelease,
    )


def test_select_latest_prefers_final_over_prerelease() -> None:
    releases = [
        _release("1.2.0-rc1", prerelease=True),
        _release("1.2.0", prerelease=False),
    ]
    latest = select_latest(releases, include_prereleases=True)
    assert latest is not None and latest.version == "1.2.0"


def test_default_update_manifest_url_points_to_hidden_pages_feed() -> None:
    assert DEFAULT_UPDATE_MANIFEST_URL.startswith("https://community-access.github.io/quill/")
    assert "/updates/." in DEFAULT_UPDATE_MANIFEST_URL


def test_parse_update_manifest_rejects_untrusted_download_host() -> None:
    payload = _signed_payload("1.2.3", "https://example.com/download", "2026-05-01", "Fixes.")
    try:
        parse_update_manifest(payload)
    except ValueError as exc:
        assert "not trusted" in str(exc)
    else:
        raise AssertionError("Expected trusted-host validation failure")
