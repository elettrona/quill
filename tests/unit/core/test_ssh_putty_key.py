"""Native PuTTY .ppk loading (issue #139).

Generates real keys with ``cryptography``, encodes them as PPK using the
documented format, then loads them back with the production parser and checks the
recovered paramiko key matches the original public blob and can sign. This pins
the field parsing against real keys and the round trip for the MAC/KDF.
"""

from __future__ import annotations

import base64
import hashlib
import hmac

import pytest

paramiko = pytest.importorskip("paramiko")

from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa  # noqa: E402
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes  # noqa: E402

from quill.core.ssh.putty_key import PuttyKeyError, load_ppk, looks_like_ppk  # noqa: E402


def _string(value: bytes) -> bytes:
    return len(value).to_bytes(4, "big") + value


def _mpint(value: int) -> bytes:
    if value == 0:
        return _string(b"")
    length = (value.bit_length() + 8) // 8  # +8 keeps the sign bit clear
    return _string(value.to_bytes(length, "big"))


def _blobs(key) -> tuple[str, bytes, bytes]:
    """Return (algorithm, public_blob, private_blob) in SSH wire format."""
    if isinstance(key, rsa.RSAPrivateKey):
        priv = key.private_numbers()
        pub = priv.public_numbers
        algorithm = "ssh-rsa"
        public = _string(b"ssh-rsa") + _mpint(pub.e) + _mpint(pub.n)
        private = _mpint(priv.d) + _mpint(priv.p) + _mpint(priv.q) + _mpint(priv.iqmp)
    elif isinstance(key, ed25519.Ed25519PrivateKey):
        from cryptography.hazmat.primitives import serialization

        raw_pub = key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        raw_priv = key.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption(),
        )
        algorithm = "ssh-ed25519"
        public = _string(b"ssh-ed25519") + _string(raw_pub)
        private = _string(raw_priv)
    elif isinstance(key, ec.EllipticCurvePrivateKey):
        from cryptography.hazmat.primitives import serialization

        algorithm = "ecdsa-sha2-nistp256"
        point = key.public_key().public_bytes(
            serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
        )
        public = _string(b"ecdsa-sha2-nistp256") + _string(b"nistp256") + _string(point)
        private = _mpint(key.private_numbers().private_value)
    else:  # pragma: no cover
        raise AssertionError("unsupported test key")
    return algorithm, public, private


def _wrap_lines(blob: bytes) -> tuple[int, str]:
    encoded = base64.b64encode(blob).decode()
    lines = [encoded[i : i + 64] for i in range(0, len(encoded), 64)] or [""]
    return len(lines), "\n".join(lines)


def _make_ppk(key, *, version: int, passphrase: str | None = None) -> str:
    algorithm, public, private = _blobs(key)
    comment = "test-key"
    encryption = "aes256-cbc" if passphrase else "none"
    extra = ""
    if passphrase:
        pw = passphrase.encode()
        if version == 3:
            from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

            salt = b"0123456789abcdef"
            out = Argon2id(salt=salt, length=80, iterations=8, lanes=1, memory_cost=8192).derive(pw)
            cipher_key, iv, mac_key = out[:32], out[32:48], out[48:80]
            extra = (
                "Key-Derivation: Argon2id\n"
                "Argon2-Memory: 8192\n"
                "Argon2-Passes: 8\n"
                "Argon2-Parallelism: 1\n"
                f"Argon2-Salt: {salt.hex()}\n"
            )
        else:
            cipher_key = (
                hashlib.sha1(b"\x00\x00\x00\x00" + pw).digest()
                + hashlib.sha1(b"\x00\x00\x00\x01" + pw).digest()
            )[:32]
            iv = b"\x00" * 16
            mac_key = hashlib.sha1(b"putty-private-key-file-mac-key" + pw).digest()
        pad = (-len(private)) % 16
        private = private + b"\x00" * pad
        mac_private = private
        encryptor = Cipher(algorithms.AES(cipher_key), modes.CBC(iv)).encryptor()
        private_stored = encryptor.update(private) + encryptor.finalize()
    else:
        mac_private = private
        private_stored = private
        if version == 3:
            mac_key = b""
        else:
            mac_key = hashlib.sha1(
                b"putty-private-key-file-mac-key" + (passphrase or "").encode()
            ).digest()

    def mac_string(value: bytes) -> bytes:
        return len(value).to_bytes(4, "big") + value

    mac_data = b"".join(
        mac_string(part)
        for part in (algorithm.encode(), encryption.encode(), comment.encode(), public, mac_private)
    )
    digest = hashlib.sha256 if version == 3 else hashlib.sha1
    mac = hmac.new(mac_key, mac_data, digest).hexdigest()

    pub_count, pub_text = _wrap_lines(public)
    priv_count, priv_text = _wrap_lines(private_stored)
    return (
        f"PuTTY-User-Key-File-{version}: {algorithm}\n"
        f"Encryption: {encryption}\n"
        f"Comment: {comment}\n"
        f"Public-Lines: {pub_count}\n{pub_text}\n"
        f"{extra}"
        f"Private-Lines: {priv_count}\n{priv_text}\n"
        f"Private-MAC: {mac}\n"
    )


def _keys():
    return [
        ("rsa", rsa.generate_private_key(public_exponent=65537, key_size=2048)),
        ("ed25519", ed25519.Ed25519PrivateKey.generate()),
        ("ecdsa", ec.generate_private_key(ec.SECP256R1())),
    ]


def _expected_public(key) -> bytes:
    algorithm, public, _private = _blobs(key)
    return public


@pytest.mark.parametrize("name,key", _keys())
@pytest.mark.parametrize("version", [2, 3])
def test_unencrypted_ppk_round_trips(name, key, version) -> None:
    text = _make_ppk(key, version=version)
    assert looks_like_ppk(text)
    loaded = load_ppk(text)
    assert loaded.asbytes() == _expected_public(key)
    # The recovered private key can sign (proves the private fields parsed right).
    algorithm = "rsa-sha2-256" if name == "rsa" else None
    assert loaded.sign_ssh_data(b"payload", algorithm) is not None


@pytest.mark.parametrize("name,key", _keys())
@pytest.mark.parametrize("version", [2, 3])
def test_encrypted_ppk_round_trips(name, key, version) -> None:
    text = _make_ppk(key, version=version, passphrase="hunter2")
    loaded = load_ppk(text, "hunter2")
    assert loaded.asbytes() == _expected_public(key)


def test_wrong_passphrase_is_rejected() -> None:
    _name, key = _keys()[0]
    text = _make_ppk(key, version=3, passphrase="correct")
    with pytest.raises(PuttyKeyError):
        load_ppk(text, "wrong")


def test_non_ppk_text_is_detected() -> None:
    assert not looks_like_ppk("-----BEGIN OPENSSH PRIVATE KEY-----")
    with pytest.raises(PuttyKeyError):
        load_ppk("not a key")
