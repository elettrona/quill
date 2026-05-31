from __future__ import annotations

import sys

import pytest

from quill.platform.windows.dpapi import protect_secret, unprotect_secret

# DPAPI is a Windows-only API; on macOS/Linux secrets use the platform keychain.
pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="DPAPI is only available on Windows"
)


def test_dpapi_round_trip_secret() -> None:
    encoded = protect_secret("super-secret-token")
    assert encoded
    assert unprotect_secret(encoded) == "super-secret-token"


def test_dpapi_uses_entropy_boundary() -> None:
    encoded = protect_secret("value", entropy=b"one")
    assert unprotect_secret(encoded, entropy=b"one") == "value"
