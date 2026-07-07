"""Tests for the on-demand Piper engine download integrity check."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from quill.core.speech import piper_install as pi


def test_verify_sha256_passes_on_match(tmp_path: Path) -> None:
    blob = tmp_path / "piper.zip"
    blob.write_bytes(b"pretend piper archive")
    expected = hashlib.sha256(b"pretend piper archive").hexdigest()
    # Must not raise.
    pi._verify_sha256(blob, expected)


def test_verify_sha256_is_case_insensitive(tmp_path: Path) -> None:
    blob = tmp_path / "piper.zip"
    blob.write_bytes(b"data")
    expected = hashlib.sha256(b"data").hexdigest().upper()
    pi._verify_sha256(blob, expected)


def test_verify_sha256_rejects_a_mismatch(tmp_path: Path) -> None:
    blob = tmp_path / "piper.zip"
    blob.write_bytes(b"corrupted or substituted download")
    with pytest.raises(pi.PiperInstallError, match="integrity check"):
        pi._verify_sha256(blob, "0" * 64)


def test_pinned_sha256_is_a_full_length_hex_digest() -> None:
    # A truncated or malformed pin would reject every real download.
    assert len(pi.PIPER_DOWNLOAD_SHA256) == 64
    int(pi.PIPER_DOWNLOAD_SHA256, 16)  # raises ValueError if not hex
