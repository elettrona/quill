from __future__ import annotations

import pytest

from quill.platform.credential_validation import (
    CredentialValidationError,
    validate_credential_identifier,
)


def test_accepts_normal_identifier() -> None:
    assert validate_credential_identifier("Quill") == "Quill"
    assert validate_credential_identifier("quill-api-key.openai") == "quill-api-key.openai"


def test_rejects_empty() -> None:
    with pytest.raises(CredentialValidationError):
        validate_credential_identifier("")


def test_rejects_leading_dash() -> None:
    with pytest.raises(CredentialValidationError):
        validate_credential_identifier("-w")


def test_rejects_control_characters() -> None:
    with pytest.raises(CredentialValidationError):
        validate_credential_identifier("bad\nname")
    with pytest.raises(CredentialValidationError):
        validate_credential_identifier("nul\x00byte")


def test_rejects_overly_long_identifier() -> None:
    with pytest.raises(CredentialValidationError):
        validate_credential_identifier("a" * 257)


def test_field_name_appears_in_message() -> None:
    with pytest.raises(CredentialValidationError, match="target_name"):
        validate_credential_identifier("", field="target_name")
