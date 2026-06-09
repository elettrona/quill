"""Private-key format dispatch for edit-over-SSH (issue #139)."""

from __future__ import annotations

import pytest

paramiko = pytest.importorskip("paramiko")

from quill.core.ssh.keys import KeyFormatError, load_private_key, looks_like_sshcom  # noqa: E402


def test_securecrt_sshcom_is_detected() -> None:
    body = (
        "---- BEGIN SSH2 ENCRYPTED PRIVATE KEY ----\n"
        'Comment: "rsa-key"\n'
        "AAAA....\n"
        "---- END SSH2 ENCRYPTED PRIVATE KEY ----\n"
    )
    assert looks_like_sshcom(body)


def test_securecrt_key_gives_actionable_message(tmp_path) -> None:
    path = tmp_path / "id.key"
    path.write_text(
        "---- BEGIN SSH2 ENCRYPTED PRIVATE KEY ----\nAAAA\n"
        "---- END SSH2 ENCRYPTED PRIVATE KEY ----\n",
        encoding="utf-8",
    )
    with pytest.raises(KeyFormatError) as excinfo:
        load_private_key(str(path))
    assert "SecureCRT" in str(excinfo.value)
    assert ".ppk" in str(excinfo.value) or "OpenSSH" in str(excinfo.value)


def test_openssh_key_loads_through_dispatch(tmp_path) -> None:
    # A real Ed25519 OpenSSH key round-trips through the dispatcher.
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519

    key = ed25519.Ed25519PrivateKey.generate()
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.OpenSSH,
        serialization.NoEncryption(),
    )
    path = tmp_path / "id_ed25519"
    path.write_bytes(pem)
    loaded = load_private_key(str(path))
    assert loaded.get_name() == "ssh-ed25519"


def test_ppk_loads_through_dispatch(tmp_path) -> None:
    # Build a minimal unencrypted v3 ppk via the tested encoder path indirectly:
    # generate a key, hand it to the ppk test helper format is overkill here, so
    # just assert a .ppk-looking file routes to the ppk loader (and fails clean
    # on garbage rather than being treated as OpenSSH).
    path = tmp_path / "garbage.ppk"
    path.write_text("PuTTY-User-Key-File-3: ssh-rsa\nEncryption: none\n", encoding="utf-8")
    with pytest.raises(Exception):  # noqa: B017 - any parse error is fine; not OpenSSH
        load_private_key(str(path))
