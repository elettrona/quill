from __future__ import annotations

import sys
import uuid

import pytest

from quill.platform.credential_validation import CredentialValidationError
from quill.platform.windows import credential_manager

pytestmark = pytest.mark.skipif(
    sys.platform != "win32",
    reason="Windows Credential Manager is Windows-only",
)


def test_empty_secret_is_distinct_from_absent_credential() -> None:
    target = f"quill-test-{uuid.uuid4().hex}"

    # Absent: nothing stored yet.
    assert credential_manager.load_generic_credential(target) is None

    # Empty secret: stored, but blank.
    credential_manager.save_generic_credential(target, "")
    try:
        loaded = credential_manager.load_generic_credential(target)
        assert loaded is not None
        assert loaded.secret == ""
    finally:
        credential_manager.delete_generic_credential(target)

    # Absent again after delete.
    assert credential_manager.load_generic_credential(target) is None


def test_load_validates_target_name() -> None:
    with pytest.raises(CredentialValidationError):
        credential_manager.load_generic_credential("-bad")
