"""Shared validation for credential and keychain identifiers (SEC-16).

The Windows Credential Manager ``target_name`` and the macOS Keychain
``account`` / ``service`` labels are identifiers that Quill controls, but they
flow into OS APIs (``CredWriteW``) and the ``security`` command-line tool. This
module centralizes a conservative "safe pattern" check so no identifier can be
empty, carry control characters or NUL bytes, be mistaken for a command-line
flag, or grow unreasonably long. It is pure and importable on any platform so
the rule can be unit-tested everywhere.
"""

from __future__ import annotations

_MAX_IDENTIFIER_LENGTH = 256


class CredentialValidationError(ValueError):
    """Raised when a credential or keychain identifier fails validation."""


def validate_credential_identifier(value: str, *, field: str = "identifier") -> str:
    """Return ``value`` if it is a safe credential identifier, else raise.

    Safe means: a non-empty string of at most 256 characters, with no control
    characters or NUL bytes, and not beginning with ``-`` (which a CLI such as
    ``security`` could otherwise interpret as an option).
    """

    if not isinstance(value, str):
        raise CredentialValidationError(f"{field} must be a string")
    if not value:
        raise CredentialValidationError(f"{field} must not be empty")
    if len(value) > _MAX_IDENTIFIER_LENGTH:
        raise CredentialValidationError(
            f"{field} must be at most {_MAX_IDENTIFIER_LENGTH} characters"
        )
    if value[0] == "-":
        raise CredentialValidationError(f"{field} must not start with '-'")
    if any(ord(char) < 0x20 or ord(char) == 0x7F for char in value):
        raise CredentialValidationError(f"{field} must not contain control characters")
    return value
