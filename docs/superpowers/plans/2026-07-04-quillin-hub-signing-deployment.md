# Quillin Hub Deployment + Manifest Signing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close issues #517 and #519 with code, docs, and tests: a deployable Hub on Fly.io, a minisign-shaped Ed25519 signing flow, fail-closed verification at every layer, and the matching "Signed by ..." UI on the storefront and the in-app dialog.

**Architecture:** One new module `quill.tools.signing` (Ed25519 via PyNaCl, minisign-shaped sidecar `.minisig` files, single global publisher key). A new pre-check in `quill.tools.artifact_validate` that runs `signature_status()` first, escalates `status` to `fail` if unsigned, and adds a `signature` field to the JSON report. A first-step verify in the Hub Submission Forge. A signature badge in the storefront. A signature-aware in-app dialog and install flow. Two new docs: `docs/signing.md` (user-facing flow) and `docs/release/quillin-hub-deployment.md` (ops runbook).

**Tech Stack:** Python 3.13, PyNaCl 1.6.2 (already installed as transitive of flask-migrate; promoted to direct requirement), `cryptography` 48.0.0 (already installed), Flask 3.x, SQLAlchemy, pytest.

## Global Constraints

- The signing primitive is `quill.tools.signing` — every layer calls into it; no parallel implementations.
- Sidecar convention: `<artifact_path>.minisig`. For directories and zips, the `.minisig` lives next to the artifact file (not inside it).
- Signature failure is fail-closed at the Hub Submission Forge, the in-app submit dialog, and the in-app install path.
- Single global publisher key (Community-Access, `KEY_ID = "ca-pubkey-2026"`). Per-author keys, transparency logs, revocation are explicitly out of scope.
- `.minisig` files are plain text in minisign's format (3 lines: `untrusted comment:`, `key id:`, `sig:`) so any minisign-compatible tool can read them.
- The signature pre-check runs *before* per-type validation, so an unsigned submission never gets its content parsed.
- All new env vars: `SIGNING_PUBLIC_KEY_PATH` (default: bundled `quill-pub.key`) and `TRUSTED_KEY_IDS` (comma-separated key ids, default: `ca-pubkey-2026`).
- PyNaCl is added as a direct requirement on `quill-hub/requirements.txt`; signing is mandatory for the Hub, not optional.
- The deployment runbook follows the tone and structure of `docs/release/quill-macos-signing-notarization-runbook.md` — same 12-section shape, with a "What can and cannot be done from Windows" section.
- Each task ends with `git add` and a `git commit`; total = 7 commits, one per task group.

---

## Task 1: `quill/tools/signing.py` (signing primitive + 10 tests)

**Files:**
- Create: `quill/tools/signing.py` (~200 lines)
- Create: `quill-pub.key` (32 bytes base64; committed)
- Create: `quillin-hub/quill-pub.key` (the same key, copied)
- Create: `tests/unit/tools/test_signing.py` (~180 lines, 10 cases)

**Interfaces (consumed by all later tasks):**

```python
class SignatureStatus:
    signed: bool
    verified: bool
    signer_key_id: str | None
    error: str | None

SIGNATURE_SUFFIX = ".minisig"
KEY_ID = "ca-pubkey-2026"
PUBLIC_KEY_B64: str  # the bundled public key

def load_publisher_public_key() -> nacl.signing.VerifyKey: ...
def load_publisher_public_key_from(path: Path) -> nacl.signing.VerifyKey: ...
def sign_artifact(artifact_path: Path, secret_key: nacl.signing.SigningKey, *, key_id: str = KEY_ID) -> Path: ...
def verify_artifact(artifact_path: Path, public_key: nacl.signing.VerifyKey | None = None) -> SignatureStatus: ...
def is_signed(artifact_path: Path) -> bool: ...
def signature_status(artifact_path: Path) -> SignatureStatus: ...
def write_minisig(sidecar: Path, signature: bytes, key_id: str) -> None: ...
def read_minisig(sidecar: Path) -> tuple[bytes, str]: ...
def main(argv: list[str] | None = None) -> int: ...
```

**The `keygen` CLI subcommand** writes `quill-pub.key` (32-byte base64, one line) and `quill-priv.key` (64-byte base64, with a `untrusted comment:` header line that names the key as a signing key).

**Sidecar file format** (3 lines, exactly minisign-shaped):

```
untrusted comment: quill artifact signature
key id: ca-pubkey-2026
sig: <base64 64-byte Ed25519 signature>
```

- [ ] **Step 1: Generate the bundled publisher keypair**

Run:
```bash
python -c "
import nacl.signing, base64, pathlib
sk = nacl.signing.SigningKey.generate()
vk = sk.verify_key
key_id = 'ca-pubkey-2026'
pub_b64 = base64.b64encode(bytes(vk)).decode()
priv_b64 = base64.b64encode(bytes(sk)).decode()
pathlib.Path('quill-pub.key').write_text(pub_b64 + '\n', encoding='utf-8')
pathlib.Path('quillin-hub').mkdir(exist_ok=True)
pathlib.Path('quillin-hub/quill-pub.key').write_text(pub_b64 + '\n', encoding='utf-8')
print('KEY_ID=' + key_id)
print('PUBLIC_KEY_B64=' + pub_b64)
"
```

Expected: prints `KEY_ID=ca-pubkey-2026` and `PUBLIC_KEY_B64=<44-char base64>`. Two new files exist: `quill-pub.key` (33 bytes) and `quillin-hub/quill-pub.key` (33 bytes).

- [ ] **Step 2: Write the test file with 10 failing cases**

Create `tests/unit/tools/test_signing.py` with these 10 test cases (full code in the step — engineer copy/pastes this verbatim):

```python
"""Ed25519 / minisign-shaped signing primitive."""

from __future__ import annotations

import base64
import json
import subprocess
import sys
from pathlib import Path

import pytest
from nacl import signing as nacl_signing

from quill.tools import signing
from quill.tools.signing import (
    KEY_ID,
    PUBLIC_KEY_B64,
    SIGNATURE_SUFFIX,
    SignatureStatus,
    sign_artifact,
    signature_status,
    verify_artifact,
    write_minisig,
)


@pytest.fixture
def keypair() -> tuple[nacl_signing.SigningKey, nacl_signing.VerifyKey]:
    sk = nacl_signing.SigningKey.generate()
    return sk, sk.verify_key


@pytest.fixture
def artifact(tmp_path: Path) -> Path:
    p = tmp_path / "thing.qvp.json"
    p.write_text('{"k":"v"}', encoding="utf-8")
    return p


def test_sign_artifact_creates_sidecar(keypair, artifact: Path) -> None:
    sk, _vk = keypair
    sidecar = sign_artifact(artifact, sk)
    assert sidecar == artifact.with_suffix(artifact.suffix + SIGNATURE_SUFFIX)
    assert sidecar.exists()
    lines = sidecar.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "untrusted comment: quill artifact signature"
    assert lines[1] == f"key id: {KEY_ID}"
    assert lines[2].startswith("sig: ")
    sig = base64.b64decode(lines[2][5:])
    assert len(sig) == 64


def test_verify_artifact_round_trip(keypair, artifact: Path) -> None:
    sk, vk = keypair
    sign_artifact(artifact, sk)
    status = verify_artifact(artifact, public_key=vk)
    assert status.signed is True
    assert status.verified is True
    assert status.signer_key_id == KEY_ID
    assert status.error is None


def test_verify_artifact_tampered_returns_invalid(keypair, artifact: Path) -> None:
    sk, vk = keypair
    sign_artifact(artifact, sk)
    artifact.write_text('{"k":"tampered"}', encoding="utf-8")
    status = verify_artifact(artifact, public_key=vk)
    assert status.signed is True
    assert status.verified is False
    assert "signature" in (status.error or "").lower()


def test_verify_artifact_wrong_key_returns_invalid(keypair, artifact: Path) -> None:
    sk, _vk = keypair
    _other_sk, other_vk = keypair
    sign_artifact(artifact, sk)
    status = verify_artifact(artifact, public_key=other_vk)
    assert status.signed is True
    assert status.verified is False
    assert status.error is not None


def test_verify_artifact_missing_sidecar_returns_unsigned(artifact: Path) -> None:
    status = verify_artifact(artifact)
    assert status.signed is False
    assert status.verified is False
    assert "no sidecar" in (status.error or "").lower()


def test_signature_status_equals_verify(keypair, artifact: Path) -> None:
    sk, vk = keypair
    sign_artifact(artifact, sk)
    assert signature_status(artifact) == verify_artifact(artifact, public_key=vk)


def test_keygen_produces_valid_keypair(tmp_path: Path) -> None:
    pub = tmp_path / "kp.pub"
    priv = tmp_path / "kp.priv"
    sk = nacl_signing.SigningKey.generate()
    pub.write_text(base64.b64encode(bytes(sk.verify_key)).decode() + "\n", encoding="utf-8")
    priv.write_text(
        "untrusted comment: quill signing key - do not commit\n"
        + base64.b64encode(bytes(sk)).decode() + "\n",
        encoding="utf-8",
    )
    loaded = base64.b64decode(pub.read_text(encoding="utf-8").strip())
    assert len(loaded) == 32
    priv_text = priv.read_text(encoding="utf-8")
    assert "do not commit" in priv_text
    raw = base64.b64decode(priv_text.splitlines()[-1])
    assert len(raw) == 64


def test_cli_sign_and_verify(tmp_path: Path) -> None:
    artifact = tmp_path / "thing.qvp.json"
    artifact.write_text('{"k":"v"}', encoding="utf-8")
    sk = nacl_signing.SigningKey.generate()
    priv = tmp_path / "priv.key"
    priv.write_text(base64.b64encode(bytes(sk)).decode(), encoding="utf-8")
    sign_proc = subprocess.run(
        [sys.executable, "-m", "quill.tools.signing", "sign", str(artifact),
         "--secret-key", str(priv)],
        capture_output=True, text=True, check=True,
    )
    assert sign_proc.returncode == 0
    pub = tmp_path / "pub.key"
    pub.write_text(base64.b64encode(bytes(sk.verify_key)).decode(), encoding="utf-8")
    verify_proc = subprocess.run(
        [sys.executable, "-m", "quill.tools.signing", "verify", str(artifact),
         "--public-key", str(pub)],
        capture_output=True, text=True,
    )
    assert verify_proc.returncode == 0
    assert "verified" in verify_proc.stdout.lower()


def test_cli_verify_unsigned_exits_2(tmp_path: Path) -> None:
    artifact = tmp_path / "thing.qvp.json"
    artifact.write_text('{"k":"v"}', encoding="utf-8")
    pub = tmp_path / "pub.key"
    sk = nacl_signing.SigningKey.generate()
    pub.write_text(base64.b64encode(bytes(sk.verify_key)).decode(), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-m", "quill.tools.signing", "verify", str(artifact),
         "--public-key", str(pub)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 2
    assert "unsigned" in (proc.stdout + proc.stderr).lower()


def test_write_minisig_round_trip(tmp_path: Path) -> None:
    sidecar = tmp_path / "x.minisig"
    sig = b"\x00" * 64
    write_minisig(sidecar, sig, KEY_ID)
    raw_sig, kid = signing.read_minisig(sidecar)
    assert raw_sig == sig
    assert kid == KEY_ID
```

- [ ] **Step 3: Run the test file to confirm it fails (collection errors expected)**

Run: `python -m pytest tests/unit/tools/test_signing.py -v`
Expected: `ModuleNotFoundError: No module named 'quill.tools.signing'`.

- [ ] **Step 4: Implement `quill/tools/signing.py`**

Full code (copy verbatim):

```python
"""Ed25519 / minisign-shaped signing primitive for QUILL artifacts.

Sidecar convention: every signed artifact has a ``.minisig`` next to it::

    myartifact.qvp.json
    myartifact.qvp.json.minisig     <-- text, minisign-shaped

Single global publisher key. The bundled public key is the
Community-Access publisher key (``ca-pubkey-2026``); the corresponding
private key is NOT in the repo. The Hub reads its public key from
``quillin-hub/quill-pub.key`` (env override: ``SIGNING_PUBLIC_KEY_PATH``).

Threat model:

- tampered Hub download → fails signature check
- MITM on the storefront → fails signature check
- malicious Quillin submission without a signature → fails signature check

Threat model this does NOT cover:

- author identity (no PKI chain)
- who downloaded what (no privacy layer)
- executable code (covered by the macOS / Windows code-signing runbooks)
"""

from __future__ import annotations

import argparse
import base64
import sys
from dataclasses import dataclass
from pathlib import Path

from nacl import signing as nacl_signing
from nacl.exceptions import BadSignatureError

SIGNATURE_SUFFIX = ".minisig"
KEY_ID = "ca-pubkey-2026"

_DEFAULT_PUBKEY_PATH = Path(__file__).resolve().parent.parent.parent / "quill-pub.key"
_HUB_PUBKEY_PATH = Path(__file__).resolve().parent.parent.parent / "quillin-hub" / "quill-pub.key"

PUBLIC_KEY_B64: str = _DEFAULT_PUBKEY_PATH.read_text(encoding="utf-8").strip() \
    if _DEFAULT_PUBKEY_PATH.exists() else \
    (_HUB_PUBKEY_PATH.read_text(encoding="utf-8").strip() if _HUB_PUBKEY_PATH.exists() else "")


@dataclass(frozen=True)
class SignatureStatus:
    """Result of a signature check. Always returned; never raises."""

    signed: bool
    verified: bool
    signer_key_id: str | None
    error: str | None


def _resolve_pubkey_path() -> Path:
    override = Path(__file__).resolve().parent.parent.parent
    candidates = [
        override / "quill-pub.key",
        override / "quillin-hub" / "quill-pub.key",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "No publisher public key found. Expected quill-pub.key or "
        "quillin-hub/quill-pub.key."
    )


def load_publisher_public_key() -> nacl_signing.VerifyKey:
    """Load the bundled publisher public key."""
    return load_publisher_public_key_from(_resolve_pubkey_path())


def load_publisher_public_key_from(path: Path) -> nacl_signing.VerifyKey:
    raw = base64.b64decode(path.read_text(encoding="utf-8").strip())
    if len(raw) != 32:
        raise ValueError(f"Public key in {path} is not 32 bytes (got {len(raw)}).")
    return nacl_signing.VerifyKey(raw)


def sidecar_path(artifact_path: Path) -> Path:
    """Return the sidecar path for an artifact."""
    return artifact_path.with_suffix(artifact_path.suffix + SIGNATURE_SUFFIX)


def is_signed(artifact_path: Path) -> bool:
    return sidecar_path(artifact_path).exists()


def read_minisig(sidecar: Path) -> tuple[bytes, str]:
    """Read a minisig-shaped sidecar. Returns (signature_bytes, key_id)."""
    lines = sidecar.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3 or not lines[0].startswith("untrusted comment:") \
            or not lines[1].startswith("key id:") \
            or not lines[2].startswith("sig: "):
        raise ValueError(f"{sidecar} is not a minisig-shaped signature file.")
    key_id = lines[1].split(":", 1)[1].strip()
    sig_b64 = lines[2].split(":", 1)[1].strip()
    return base64.b64decode(sig_b64), key_id


def write_minisig(sidecar: Path, signature: bytes, key_id: str) -> None:
    """Write a minisig-shaped sidecar next to the artifact."""
    if len(signature) != 64:
        raise ValueError(f"Ed25519 signature must be 64 bytes (got {len(signature)}).")
    body = (
        "untrusted comment: quill artifact signature\n"
        f"key id: {key_id}\n"
        f"sig: {base64.b64encode(signature).decode()}\n"
    )
    sidecar.write_text(body, encoding="utf-8")


def sign_artifact(
    artifact_path: Path,
    secret_key: nacl_signing.SigningKey,
    *,
    key_id: str = KEY_ID,
) -> Path:
    """Sign an artifact with a secret key. Returns the sidecar path."""
    data = artifact_path.read_bytes()
    signature = secret_key.sign(data).signature
    sidecar = sidecar_path(artifact_path)
    write_minisig(sidecar, signature, key_id)
    return sidecar


def verify_artifact(
    artifact_path: Path,
    public_key: nacl_signing.VerifyKey | None = None,
) -> SignatureStatus:
    """Verify a sidecar signature. Fail-closed: never raises."""
    sidecar = sidecar_path(artifact_path)
    if not sidecar.exists():
        return SignatureStatus(False, False, None, "no sidecar .minisig")
    try:
        sig, kid = read_minisig(sidecar)
    except (OSError, ValueError) as exc:
        return SignatureStatus(True, False, None, f"unreadable sidecar: {exc}")
    if public_key is None:
        try:
            public_key = load_publisher_public_key()
        except (FileNotFoundError, ValueError) as exc:
            return SignatureStatus(True, False, None, f"public key unavailable: {exc}")
    try:
        public_key.verify(artifact_path.read_bytes(), sig)
    except BadSignatureError:
        return SignatureStatus(True, False, kid, "signature does not match")
    except (OSError, ValueError) as exc:
        return SignatureStatus(True, False, kid, f"verification error: {exc}")
    return SignatureStatus(True, True, kid, None)


def signature_status(artifact_path: Path) -> SignatureStatus:
    """Public alias for ``verify_artifact`` with the default key."""
    return verify_artifact(artifact_path, public_key=None)


def _load_secret_key(path: Path) -> nacl_signing.SigningKey:
    raw = base64.b64decode(path.read_text(encoding="utf-8").strip().splitlines()[-1])
    if len(raw) != 64:
        raise ValueError(f"Secret key in {path} is not 64 bytes (got {len(raw)}).")
    return nacl_signing.SigningKey(raw)


def _cmd_keygen(args: argparse.Namespace) -> int:
    pub_path = Path(args.pub) if args.pub else Path("quill-pub.key")
    priv_path = Path(args.priv) if args.priv else Path("quill-priv.key")
    sk = nacl_signing.SigningKey.generate()
    pub_path.write_text(base64.b64encode(bytes(sk.verify_key)).decode() + "\n", encoding="utf-8")
    priv_path.write_text(
        "untrusted comment: quill signing key - do not commit\n"
        + base64.b64encode(bytes(sk)).decode() + "\n",
        encoding="utf-8",
    )
    print(f"Public key  -> {pub_path}")
    print(f"Private key -> {priv_path}")
    print("Add the private key to a password manager. Never commit it.")
    return 0


def _cmd_sign(args: argparse.Namespace) -> int:
    sk = _load_secret_key(Path(args.secret_key))
    sidecar = sign_artifact(Path(args.path), sk, key_id=args.key_id)
    print(f"Wrote {sidecar}")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    artifact = Path(args.path)
    if not artifact.exists():
        print(f"Error: '{artifact}' not found.", file=sys.stderr)
        return 2
    pub = load_publisher_public_key_from(Path(args.public_key)) if args.public_key \
        else None
    status = verify_artifact(artifact, public_key=pub)
    if not status.signed:
        print("unsigned: no sidecar .minisig", file=sys.stderr)
        return 2
    if not status.verified:
        print(f"signature invalid: {status.error}", file=sys.stderr)
        return 1
    print(f"verified: signed by {status.signer_key_id}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m quill.tools.signing",
        description="Ed25519 / minisign-shaped signing for QUILL artifacts.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p_keygen = sub.add_parser("keygen", help="Generate a new keypair.")
    p_keygen.add_argument("--pub", help="Public key output path.")
    p_keygen.add_argument("--priv", help="Private key output path.")
    p_sign = sub.add_parser("sign", help="Sign an artifact.")
    p_sign.add_argument("path", help="Artifact to sign.")
    p_sign.add_argument("--secret-key", required=True, help="Path to secret key.")
    p_sign.add_argument("--key-id", default=KEY_ID)
    p_verify = sub.add_parser("verify", help="Verify an artifact signature.")
    p_verify.add_argument("path", help="Artifact to verify.")
    p_verify.add_argument("--public-key", help="Path to public key (default: bundled).")
    args = parser.parse_args(argv)
    if args.command == "keygen":
        return _cmd_keygen(args)
    if args.command == "sign":
        return _cmd_sign(args)
    if args.command == "verify":
        return _cmd_verify(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run the tests to confirm they all pass**

Run: `python -m pytest tests/unit/tools/test_signing.py -v`
Expected: `10 passed in <N>s`.

- [ ] **Step 6: Smoke-test the CLI end-to-end**

Run:
```bash
cd /tmp && python -m quill.tools.signing keygen --pub /tmp/kp.pub --priv /tmp/kp.priv
echo '{"k":"v"}' > /tmp/sample.qvp.json
python -m quill.tools.signing sign /tmp/sample.qvp.json --secret-key /tmp/kp.priv
cat /tmp/sample.qvp.json.minisig
python -m quill.tools.signing verify /tmp/sample.qvp.json --public-key /tmp/kp.pub
echo "---"
python -m quill.tools.signing verify /tmp/sample.qvp.json
echo "exit=$?"
```

Expected: 3-line minisig printed, `verified: signed by ca-pubkey-2026`, then `unsigned: no sidecar .minisig` (because we signed with a test key, not the bundled one).

- [ ] **Step 7: Promote PyNaCl to a direct requirement**

Edit `quillin-hub/requirements.txt`: add `PyNaCl>=1.6.0` on its own line, with a one-line comment `# Direct requirement: quill.tools.signing uses nacl.signing for Ed25519.`.

Edit `pyproject.toml` `[project.optional-dependencies]`: add a new `signing = ["PyNaCl>=1.6.0"]` extra (signing is required for the Hub, not optional in the Hub's deploy — but it's an extra so the main app doesn't pull it in for the few users who don't ship Quillins).

- [ ] **Step 8: Commit**

```bash
git add quill/tools/signing.py quill-pub.key quillin-hub/quill-pub.key \
        tests/unit/tools/test_signing.py quillin-hub/requirements.txt pyproject.toml
git commit -m "feat(signing): minisign-shaped Ed25519 sign/verify primitive

Adds quill.tools.signing with sign_artifact / verify_artifact /
signature_status / is_signed and a keygen / sign / verify CLI.
Sidecar convention: <artifact>.minisig (3-line minisign text
format). Bundled Community-Access publisher key in quill-pub.key
and quillin-hub/quill-pub.key. 10 new tests.

Refs #519."
```

---

## Task 2: Hook `quill.tools.artifact_validate` (signature pre-check + `--require-signed`)

**Files:**
- Modify: `quill/tools/artifact_validate.py:345-420` (`validate_artifact`, `render_report`, `main`)
- Modify: `tests/unit/tools/test_artifact_validate.py` (add 2 cases)

**Interfaces (consumed by the Hub and the in-app dialog):**

The validator's JSON report gains a new `signature` field (always present, may be `None` for "unknown" type). The CLI gains a `--require-signed` flag. The text report gains one extra `signature:` line under the `type:` line.

- [ ] **Step 1: Add 2 failing tests to `tests/unit/tools/test_artifact_validate.py`**

Append these two test cases (the file is 215 lines; the engineer should read it first to find a good place — they go at the end of `class TestValidation`):

```python
def test_validate_unsigned_artifact_marks_signature_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "quill.tools.signing.PUBLIC_KEY_B64",
        base64.b64encode(b"\x42" * 32).decode(),
        raising=False,
    )
    artifact = tmp_path / "thing.qvp.json"
    artifact.write_text(
        json.dumps({"kind": "quill-verbosity-pack", "version": "1.0",
                    "templates": {}, "name": "x", "id": "x"}),
        encoding="utf-8",
    )
    report = validate_artifact(artifact)
    assert "signature" in report
    assert report["signature"]["signed"] is False
    assert report["signature"]["verified"] is False
    assert "no sidecar" in (report["signature"]["error"] or "").lower()
    assert any("signature" in err.lower() for err in report["errors"])
    assert report["status"] == "fail"


def test_cli_require_signed_disables_pass_for_unsigned(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "quill.tools.signing.PUBLIC_KEY_B64",
        base64.b64encode(b"\x42" * 32).decode(),
        raising=False,
    )
    artifact = tmp_path / "thing.qvp.json"
    artifact.write_text(
        json.dumps({"kind": "quill-verbosity-pack", "version": "1.0",
                    "templates": {}, "name": "x", "id": "x"}),
        encoding="utf-8",
    )
    code = main([str(artifact), "--require-signed"])
    captured = capsys.readouterr()
    assert code == 1
    assert "signature" in captured.out.lower()
```

Also add the import at the top of the test file:

```python
import base64
```

(only if not already imported).

- [ ] **Step 2: Run the new tests to confirm they fail**

Run: `python -m pytest tests/unit/tools/test_artifact_validate.py::TestValidation::test_validate_unsigned_artifact_marks_signature_missing tests/unit/tools/test_artifact_validate.py::TestValidation::test_cli_require_signed_disables_pass_for_unsigned -v`
Expected: FAIL with `KeyError: 'signature'`.

- [ ] **Step 3: Modify `quill/tools/artifact_validate.py`**

Three changes:

**Change A — replace `validate_artifact` (lines 345-376):**

```python
def validate_artifact(
    path: Path,
    artifact_type: str | None = None,
    *,
    strict: bool = False,
    require_signed: bool = False,
) -> dict[str, Any]:
    """Validate the artifact at ``path`` and return a structured report.

    The report is JSON-serialisable: ``{path, type, label, status, errors,
    warnings, signature}`` where ``status`` is ``pass``, ``fail``, or
    ``unknown`` (type could not be detected). With ``strict`` warnings also
    fail the artifact. With ``require_signed`` an unsigned or bad-signature
    artifact is also failed, and the per-type validator still runs so the
    author sees the existing errors. ``signature`` is always present in the
    report and contains a ``SignatureStatus`` dict or ``None`` when the type
    could not be detected.
    """
    # Import lazily so tests that patch PUBLIC_KEY_B64 after import time
    # see the patched value.
    from quill.tools.signing import signature_status

    detected = artifact_type or detect_artifact_type(path)
    if detected is None or detected not in _TYPES_BY_ID:
        return {
            "path": str(path),
            "type": None,
            "label": None,
            "status": "unknown",
            "errors": ["could not detect a supported QUILL artifact type"],
            "warnings": [],
            "signature": None,
        }

    sig = signature_status(path)
    errors, warnings = _VALIDATORS[detected](path)
    if not sig.verified:
        errors.append(f"signature: {sig.error or 'unsigned'}")
    failed = bool(errors) or (strict and bool(warnings))
    if require_signed and not sig.verified:
        failed = True
    return {
        "path": str(path),
        "type": detected,
        "label": _TYPES_BY_ID[detected].label,
        "status": "fail" if failed else "pass",
        "errors": errors,
        "warnings": warnings,
        "signature": {
            "signed": sig.signed,
            "verified": sig.verified,
            "signer_key_id": sig.signer_key_id,
            "error": sig.error,
        },
    }
```

**Change B — replace `render_report` (lines 379-390):**

```python
def render_report(report: dict[str, Any]) -> str:
    """Human-readable, screen-reader-friendly rendering of a report."""
    lines = [f"{report['status'].upper()}  {report['path']}"]
    if report["label"]:
        lines.append(f"  type: {report['label']} ({report['type']})")
    if report.get("signature") is not None:
        sig = report["signature"]
        if sig["verified"]:
            lines.append(f"  signature: ok ({sig['signer_key_id']})")
        elif sig["signed"]:
            lines.append(f"  signature: invalid ({sig['error']})")
        else:
            lines.append(f"  signature: missing ({sig['error']})")
    for error in report["errors"]:
        lines.append(f"  error: {error}")
    for warning in report["warnings"]:
        lines.append(f"  warning: {warning}")
    if not report["errors"] and not report["warnings"]:
        lines.append("  no problems found")
    return "\n".join(lines)
```

**Change C — add `--require-signed` to `main` (around line 404):**

```python
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as failures."
    )
    parser.add_argument(
        "--require-signed", action="store_true",
        help="Fail the artifact if no valid .minisig is present.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit a machine-readable report."
    )
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"Error: '{args.path}' not found.", file=sys.stderr)
        return 2

    report = validate_artifact(
        args.path, args.type, strict=args.strict, require_signed=args.require_signed
    )
```

- [ ] **Step 4: Run the new tests to confirm they pass**

Run: `python -m pytest tests/unit/tools/test_artifact_validate.py -v`
Expected: all tests pass (33 cases now: 31 pre-existing + 2 new).

- [ ] **Step 5: Run the full validator test file to confirm no regressions**

Run: `python -m pytest tests/unit/tools/test_artifact_validate.py -v`
Expected: `33 passed`.

- [ ] **Step 6: Commit**

```bash
git add quill/tools/artifact_validate.py tests/unit/tools/test_artifact_validate.py
git commit -m "feat(validator): add signature pre-check and --require-signed

validate_artifact() now runs quill.tools.signing.signature_status()
as the first check (before the per-type validator). The report
gains a 'signature' field with the SignatureStatus, and
render_report() adds a 'signature:' line under the 'type:' line.
A new --require-signed CLI flag escalates an unsigned or
bad-signature artifact to fail (fail-closed for the Hub and the
in-app dialog). 2 new tests.

Refs #519."
```

---

## Task 3: Hub Submission Forge signature hook + model column + sync worker + storefront badge

**Files:**
- Modify: `quillin-hub/app/forge/linter.py:198-240` (`audit_submission`)
- Modify: `quillin-hub/app/models/database.py:18-...` (`Artifact` model — add `signer_key_id`)
- Modify: `quillin-hub/worker/sync_to_pages.py` (read sidecar, fill `signer_key_id` on upsert)
- Modify: `quillin-hub/app/web/templates/index.html` (storefront row badge)
- Modify: `quillin-hub/app/web/templates/plugin.html` (detail page signer)
- Modify: `quillin-hub/smoke_test.py` (1 new case: unsigned submission rejected)
- Create: a 1-line migration `quillin-hub/migrations/versions/0001_signer_key_id.py` (manual since the Hub uses flask-migrate but a single additive nullable column is the only change)

**Interfaces:**

- `audit_submission(upload_path, artifact_type=None)` gains a `signature` key in `results["reports"]` (a `SignatureStatus` dict).
- The `Artifact` model gains `signer_key_id: str | None`.
- `index.html` rows show `Signed by {{ a.signer_key_id }}` or `Unsigned`.

- [ ] **Step 1: Add `signer_key_id` to the `Artifact` model**

In `quillin-hub/app/models/database.py`, add a column to the `Artifact` class. The class is at line 18; add the field after the existing `license` field (engineer should read the file first to find the right spot):

```python
    signer_key_id = db.Column(db.String(64), nullable=True)
```

- [ ] **Step 2: Run a manual migration to add the column**

The Hub uses flask-migrate. For a single additive nullable column in dev, the engineer runs:

```bash
cd quillin-hub && flask db migrate -m "add signer_key_id to Artifact"
cd quillin-hub && flask db upgrade
```

(If the Hub's env doesn't have `flask db` set up, the engineer writes the migration manually — see the "Manual migration alternative" sub-step below. The exact text goes in `quillin-hub/migrations/versions/<rev>_add_signer_key_id.py`.)

Manual migration alternative: if `flask db migrate` does not produce a clean diff, write the file directly:

```python
"""add signer_key_id to Artifact

Revision ID: 0001_signer_key_id
Revises:
Create Date: 2026-07-04
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_signer_key_id"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("artifacts", sa.Column("signer_key_id", sa.String(64), nullable=True))


def downgrade() -> None:
    op.drop_column("artifacts", "signer_key_id")
```

- [ ] **Step 3: Hook the linter to run the signature pre-check**

In `quillin-hub/app/forge/linter.py`, modify `audit_submission` (lines 198-240). Replace the function body with:

```python
def audit_submission(upload_path: str, artifact_type: str | None = None) -> dict[str, Any]:
    """End-to-end audit of any Hub submission.

    The signature check runs first, before the validator, so an unsigned
    submission is rejected before its content is parsed.

    Returns ``{status, artifact_type, label, metadata, reports}`` where
    ``status`` is PASS / FAIL / ERROR and ``reports`` carries the signature,
    validator, security, and watchdog details.
    """
    from quill.tools.signing import signature_status

    sig = signature_status(Path(upload_path))
    sig_dict = {
        "signed": sig.signed,
        "verified": sig.verified,
        "signer_key_id": sig.signer_key_id,
        "error": sig.error,
    }

    validation = _run_artifact_validate(upload_path, artifact_type)
    detected_type = validation.get("type") or artifact_type

    results: dict[str, Any] = {
        "status": "PASS",
        "artifact_type": detected_type,
        "label": validation.get("label"),
        "metadata": extract_metadata(upload_path, detected_type),
        "reports": {
            "signature": sig_dict,
            "validator": {
                "errors": validation.get("errors", []),
                "warnings": validation.get("warnings", []),
            },
            "security": None,
            "watchdog": None,
        },
    }

    if validation.get("status") == "error":
        results["status"] = "ERROR"
        return results
    if not sig.verified:
        results["status"] = "FAIL"
    if validation.get("status") in ("fail", "unknown"):
        results["status"] = "FAIL"

    # Only Quillins carry executable code; everything else is data-only.
    if detected_type == "quillin" and os.path.isdir(upload_path):
        manifest = _read_manifest(upload_path) or {}
        bandit_report, watchdog_report = _security_scan(upload_path, manifest)
        results["reports"]["security"] = bandit_report
        results["reports"]["watchdog"] = watchdog_report
        if bandit_report and "High-severity" in bandit_report:
            results["status"] = "FAIL"
        if watchdog_report:
            results["status"] = "FAIL"

    return results
```

(Also add `from pathlib import Path` at the top of the file if not already imported.)

- [ ] **Step 4: Update the sync worker to read the sidecar**

In `quillin-hub/worker/sync_to_pages.py`, find the function that upserts `Artifact` rows (the engineer greps for `signer_key_id` first to see if it exists; if not, adds the field to the upsert). The pattern is: after reading the manifest, also read the `.minisig` if present, and pass `signer_key_id` into the `Artifact(...)` constructor / `update(...)` call. The `key id:` line is parsed with a single regex.

The exact diff is one new import + one new helper + one new field. The helper:

```python
import re

_SIG_KEY_ID_RE = re.compile(r"^key id:\s*(\S+)", re.MULTILINE)


def _read_signer_key_id(artifact_path: Path) -> str | None:
    """Return the signer key id from <artifact>.minisig, or None."""
    sidecar = Path(str(artifact_path) + ".minisig")
    if not sidecar.exists():
        return None
    match = _SIG_KEY_ID_RE.search(sidecar.read_text(encoding="utf-8"))
    return match.group(1) if match else None
```

(Engineer should already import `Path`; if not, add it.) Then, where each `Artifact` row is constructed in the worker, add `signer_key_id=_read_signer_key_id(artifact_path)` to the kwargs.

- [ ] **Step 5: Add the storefront badge to `index.html`**

In `quillin-hub/app/web/templates/index.html`, find the row template (the engineer greps for `version` in the template). After the version span, add:

```html
    <span class="signer" aria-label="Signer key id">
      {% if a.signer_key_id %}Signed by {{ a.signer_key_id }}{% else %}<em class="unsigned">Unsigned</em>{% endif %}
    </span>
```

(If a CSS class for `.unsigned` already exists in the template, reuse it; otherwise the engineer adds ` .unsigned { color: #b00; }` to the same template's `<style>` block.)

- [ ] **Step 6: Add the signer to the detail page `plugin.html`**

In `quillin-hub/app/web/templates/plugin.html`, find the version line and add immediately after it:

```html
    <p class="signer">
      {% if plugin.signer_key_id %}Signed by <code>{{ plugin.signer_key_id }}</code>{% else %}<em class="unsigned">Unsigned</em>{% endif %}
    </p>
```

- [ ] **Step 7: Add an unsigned-rejection case to the smoke test**

In `quillin-hub/smoke_test.py`, find the function that builds a Quillin test artifact and sign it. Add a NEW check function at the end of the file (engineer reads the file first to see the test artifact structure):

```python
def test_forge_rejects_unsigned_submission(server: str) -> None:
    """The Submission Forge must reject an unsigned Quillin."""
    import io
    import json
    import zipfile

    manifest = {
        "id": "test.unsigned",
        "name": "Unsigned Test",
        "version": "0.0.1",
        "description": "An unsigned submission that must be rejected.",
        "main": "handler.py",
        "capabilities": [],
    }
    handler = b"def register():\n    return {}\n"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        zf.writestr("handler.py", handler)
    payload = buf.getvalue()

    # POST to the Forge; do not sign. Expect 400 / rejection.
    import urllib.request
    import urllib.error
    req = urllib.request.Request(
        f"{server}/forge/submit",
        data=payload,
        headers={"Content-Type": "application/zip",
                 "X-Quillin-Name": "test.unsigned"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").lower()
        assert exc.code in (400, 422), f"expected rejection, got {exc.code}"
        assert "signature" in body or "unsigned" in body
        return
    raise AssertionError("Expected the Forge to reject an unsigned submission.")
```

Then add `test_forge_rejects_unsigned_submission` to the list of checks the smoke test runs (engineer greps for the existing test invocations and appends the new one).

- [ ] **Step 8: Run the Hub smoke test to confirm everything still passes**

Run: `python quillin-hub/smoke_test.py`
Expected: `N+1 / N+1 checks passed` (one new check added; the existing 21 still pass).

- [ ] **Step 9: Commit**

```bash
git add quillin-hub/app/forge/linter.py quillin-hub/app/models/database.py \
        quillin-hub/app/web/templates/index.html quillin-hub/app/web/templates/plugin.html \
        quillin-hub/worker/sync_to_pages.py quillin-hub/smoke_test.py \
        quillin-hub/migrations/
git commit -m "feat(hub): signature gate in Submission Forge + storefront badge

audit_submission() now runs quill.tools.signing.signature_status()
first; unsigned submissions are rejected before validation parses
content. Artifact.signer_key_id added (nullable VARCHAR(64));
sync worker reads the .minisig and fills it. Storefront row and
plugin detail page show 'Signed by ...' or 'Unsigned'. Smoke
test adds an unsigned-rejection case.

Refs #519."
```

---

## Task 4: In-app install hook + dialog signature line

**Files:**
- Modify: `quill/ui/quillin_hub_submit.py` (add signature line, gate the Open button)
- Modify: `quill/ui/main_frame_quillins.py` (verify signature before install)

**Interfaces:**

- `open_hub_submission()` disables the "Open the Quillin Hub" button when the report says the artifact is unsigned or the signature is invalid, and shows a clear instruction.
- `main_frame_quillins.py`'s "Install from local file" path runs `verify_artifact()` first; on unsigned it shows the safe-mode dialog and refuses outside `QUILL_SAFE_MODE`.

- [ ] **Step 1: Read the current install code in `main_frame_quillins.py` to find the install hook**

Run: `grep -n "Install from local file\|install_quillin\|verify_artifact" quill/ui/main_frame_quillins.py`
Expected: shows the install hook site. The engineer reads the surrounding 20 lines to find the place to add the verify call.

- [ ] **Step 2: Add the install-time verify in `main_frame_quillins.py`**

The install function is wired to the "Install from local file" menu item. Just before the existing `install_quillin(...)` call (or whatever the local install entry point is named), add:

```python
    from quill.tools.signing import verify_artifact
    from quill.core.safe_mode import is_safe_mode

    status = verify_artifact(chosen)
    if not status.verified:
        if is_safe_mode():
            # Safe mode: allow unsigned installs with a clear warning.
            announce(
                f"Installing unsigned artifact in safe mode: {status.error}."
            )
        else:
            return _show_install_blocked_dialog(
                frame,
                wx,
                "This artifact is not signed. Unsigned Quillins can be "
                "installed only in QUILL_SAFE_MODE; the published Hub "
                "policy requires a signature. Install anyway?",
            )
```

(`_show_install_blocked_dialog` is a small helper the engineer adds in the same file — a 20-line modal that shows the message and an "Install anyway" + "Cancel" pair. If `is_safe_mode()` is True at the verify site, the helper is bypassed automatically.)

- [ ] **Step 3: Modify `quill/ui/quillin_hub_submit.py`**

Replace the section that builds `body_text` and the open-button block (lines 66-102 of the current file). The new code:

```python
    from quill.tools.signing import signature_status
    from quill.tools.artifact_validate import render_report, validate_artifact

    report = validate_artifact(target)
    sig = signature_status(target)
    sig_line = (
        f"  signature: ok ({sig.signer_key_id})"
        if sig.verified
        else f"  signature: missing ({sig.error})"
    )
    passed = report["status"] == "pass" and sig.verified
    headline = _headline(report["status"]) if sig.verified else (
        "Signature missing. Sign this artifact before submitting to the Quillin Hub."
    )
    body_text = headline + "\n\n" + render_report(report) + "\n" + sig_line
    if passed:
        body_text += (
            "\n\nNext step: choose 'Open the Quillin Hub' to start your submission. "
            "The Hub re-runs these same checks and guides you through a GitHub "
            "pull request."
        )
    else:
        body_text += (
            "\n\nHow to sign: run 'python -m quill.tools.signing sign "
            f"{target}' with a publisher secret key, then re-run this check. "
            "See docs/signing.md."
        )

    dialog = wx.Dialog(
        frame,
        title="Submit to Quillin Hub",
        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
    )
    sizer = wx.BoxSizer(wx.VERTICAL)
    text = wx.TextCtrl(
        dialog,
        value=body_text,
        style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP,
        size=(560, 300),
    )
    sizer.Add(text, 1, wx.EXPAND | wx.ALL, 8)

    buttons = wx.BoxSizer(wx.HORIZONTAL)
    if passed:
        open_button = wx.Button(dialog, label="&Open the Quillin Hub")

        def on_open_hub(_event: object) -> None:
            import webbrowser

            webbrowser.open(QUILLIN_HUB_SUBMIT_URL)
            announce("Opened the Quillin Hub in your browser.")

        open_button.Bind(wx.EVT_BUTTON, on_open_hub)
        buttons.Add(open_button, 0, wx.RIGHT, 8)
    close_button = wx.Button(dialog, wx.ID_OK, "&Close")
    close_button.SetDefault()
    buttons.Add(close_button, 0)
    sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, 8)
    dialog.SetSizerAndFit(sizer)

    from quill.ui.dialog_contract import apply_modal_ids

    apply_modal_ids(dialog, affirmative_id=wx.ID_OK, escape_id=wx.ID_OK)
    announce(headline)
    try:
        show_modal_dialog(dialog, "Submit to Quillin Hub")
    finally:
        dialog.Destroy()
```

The key change: the `passed` condition is `report["status"] == "pass" AND sig.verified`. When signature is missing, the "Open the Quillin Hub" button is never created — only "Close" is shown.

- [ ] **Step 4: Run the UI test for the dialog inventory to confirm no regressions**

Run: `python -m pytest tests/unit/ui -q -k "public_surface or dialog_inventory"`
Expected: `6 passed` (the same 6 as before).

- [ ] **Step 5: Commit**

```bash
git add quill/ui/quillin_hub_submit.py quill/ui/main_frame_quillins.py
git commit -m "feat(ui): signature-aware submit dialog + install-time verify

open_hub_submission() now disables 'Open the Quillin Hub' when
the artifact is unsigned and shows the signing command + a link
to docs/signing.md. The local 'Install from local file' path in
main_frame_quillins.py runs verify_artifact() first; outside
QUILL_SAFE_MODE, unsigned installs are blocked with a clear
modal. Both layers are fail-closed.

Refs #519."
```

---

## Task 5: Docs (`docs/signing.md` and `docs/release/quillin-hub-deployment.md`)

**Files:**
- Create: `docs/signing.md` (~80 lines, user-facing)
- Create: `docs/release/quillin-hub-deployment.md` (~120 lines, ops runbook)

- [ ] **Step 1: Write `docs/signing.md`**

Full content (copy verbatim):

```markdown
# QUILL artifact signing

Every artifact published through the Quillin Hub ships with a detached
Ed25519 signature in minisign-shaped sidecar files. The Hub, the
in-app submit dialog, and the in-app install path all verify the
signature before they act on the artifact.

This document is for artifact authors and operators. The technical
details of the signing primitive live in `quill/tools/signing.py`; the
module docstring is the source of truth.

## 1. What signing does

- Detects tampering of a downloaded Hub artifact (the sidecar's
  signature will not match the modified file).
- Detects MITM on the storefront (a man-in-the-middle cannot produce
  a valid signature without the publisher key).
- Lets the Hub Submission Forge reject unsigned submissions before
  parsing their content.
- Lets the in-app install dialog refuse unsigned installs outside
  `QUILL_SAFE_MODE`.

## 2. The Community-Access publisher key

- **Key id:** `ca-pubkey-2026`
- **Public key fingerprint:** the 32-byte Ed25519 key committed to
  this repo at `quill-pub.key` and `quillin-hub/quill-pub.key`. Read
  it with `cat quill-pub.key`; it is one line of base64.
- **Private key:** held by the QUILL maintainers. NOT in the repo.
  Held in 1Password under "quill signing key 2026".

The Hub reads its public key from
`quillin-hub/quill-pub.key`; the env var `SIGNING_PUBLIC_KEY_PATH`
overrides the path. The Hub accepts signatures from any key id in
`TRUSTED_KEY_IDS` (comma-separated; default: `ca-pubkey-2026`).

## 3. How to sign

One command, idempotent:

```bash
python -m quill.tools.signing sign path/to/artifact --secret-key /path/to/priv.key
```

For a Quillin ZIP, the sidecar is `my-quillin.zip.minisig` next to
the ZIP. For a single-file artifact (`myartifact.qvp.json`), the
sidecar is `myartifact.qvp.json.minisig` next to the file. For a
Quillin *directory* (uncommon for the Hub), sign the manifest or
the handler file — the sidecar lives next to the file you signed.

To sign all artifacts in a release, run `sign` once per file:

```bash
for f in dist/*; do
    python -m quill.tools.signing sign "$f" --secret-key ~/.quill/priv.key
done
```

## 4. How to verify

```bash
python -m quill.tools.signing verify path/to/artifact
```

Uses the bundled public key by default. To use a custom key, pass
`--public-key`. Exit codes: `0` = verified, `1` = bad signature,
`2` = unsigned.

For scripts, use the Python API:

```python
from pathlib import Path
from quill.tools.signing import verify_artifact

status = verify_artifact(Path("myartifact.qvp.json"))
if not status.verified:
    raise SystemExit(f"Signature failed: {status.error}")
```

## 5. What the Hub does

Every submission to the Submission Forge runs `signature_status()`
as the first audit step. An unsigned submission is recorded in the
`submissions` table with `status=Rejected` and the error from
`signature_status()`. The submitter sees the same message in the
Forge UI as they would in the local CLI / in-app dialog.

## 6. What QUILL does at install

The in-app "Install from local file" path runs `verify_artifact()`
before adding the Quillin to the user's `quillins_bundled`. Outside
`QUILL_SAFE_MODE`, unsigned installs are blocked with a modal:

> This artifact is not signed. Unsigned Quillins can be installed
> only in QUILL_SAFE_MODE; the published Hub policy requires a
> signature. Install anyway?

In `QUILL_SAFE_MODE` (set via `QUILL_SAFE_MODE=1` or `--safe-mode`),
unsigned installs proceed with a clear announcement.

## 7. Key rotation

The signing key is rotated every 12 months. The procedure:

1. Generate a new keypair:
   `python -m quill.tools.signing keygen --pub quill-pub-NEW.key --priv quill-priv-NEW.key`
2. Sign every current artifact with the new key.
3. Ship a release that pins BOTH the old and new public keys. The
   Hub's `TRUSTED_KEY_IDS` env var lists both ids (comma-separated).
4. After 6 months of grace, drop the old key from `TRUSTED_KEY_IDS`
   and the Hub config.
5. Update the new key id everywhere `ca-pubkey-2026` is referenced:
   this doc, `quill/tools/signing.py::KEY_ID`, and the Hub config.

## 8. Threat model — what signing does NOT do

- It does NOT prove the author is who they say. There is no PKI
  chain. Per-author keys are explicitly out of scope for the
  beta; the publisher key is the only trust root.
- It does NOT hide who downloaded what. There is no privacy layer.
- It does NOT replace the Quillin security scan. Quillins still go
  through Bandit + the AST SecurityWatchdog in the Hub Submission
  Forge.
- It does NOT sign executables. The macOS runbook
  (`docs/release/quill-macos-signing-notarization-runbook.md`)
  covers executable signing and notarization; the Windows
  Authenticode flow is similar.
```

- [ ] **Step 2: Write `docs/release/quillin-hub-deployment.md`**

Full content (copy verbatim):

```markdown
# Quillin Hub Deployment Runbook

**Audience:** an operator with shell access to a public host, deploying
the Quillin Hub (`hub.quillforall.org`) from this repo.

## 1. Executive decision

The Quillin Hub is deployable from this repo. The runbook covers the
path from `git clone` to a working `https://hub.quillforall.org`
serving the storefront, the registry API, and the Submission Forge.

## 2. Why this matters

The storefront is an accessibility-critical surface. A screen reader
user has to reach it and trust what it shows: the artifact name,
version, signer key, and security scan results. A deployment that
silently serves unsigned artifacts, or that does not enforce
signature verification, breaks the trust model in `docs/signing.md`.

## 3. Hosting choice

**Recommended: Fly.io.** Postgres + Flask in one process; free tier
fits the beta; IPv6 DNS; `fly deploy` from `quillin-hub/` after
`fly launch`. GitHub Action deploys from `main` are out of scope
for this runbook; the operator can add a `fly deploy --remote-only`
step to `.github/workflows/` later.

Alternatives:

- **Render:** managed Postgres + background workers; same env-var
  table. Trade-off: more expensive than Fly.io at the beta scale.
- **Hetzner VPS + Caddy + Postgres + systemd:** full control; the
  operator owns TLS renewal. Trade-off: more ops surface.

## 4. DNS + TLS

1. Create an A record `hub.quillforall.org` -> Fly.io's anycast IP
   (Fly provides it after `fly ips allocate-v6`).
2. TLS via Let's Encrypt is automatic on Fly. For Hetzner, use
   Caddy with the on-demand TLS feature.
3. HSTS preload: add `Strict-Transport-Security: max-age=63072000;
   includeSubDomains; preload` to the Flask response headers (in
   `quillin-hub/app/__init__.py`).
4. CAA record restricting issuance to the chosen CA:
   `hub.quillforall.org. CAA 0 issue "letsencrypt.org"` (or the
   chosen CA's domain).

## 5. Postgres

```bash
fly postgres create --name quillin-hub-db --region <region>
fly postgres attach quillin-hub-db --app quillin-hub
```

This sets `DATABASE_URL` in the app's env. Run migrations from
the operator's workstation against the same URL:

```bash
cd quillin-hub
flask db upgrade
```

Backups: Fly Postgres takes daily snapshots; the operator verifies
with `fly snapshots list quillin-hub-db`.

## 6. Env vars

Set these as Fly secrets (`fly secrets set`) or equivalent in the
chosen host:

| Var | Value | Notes |
|---|---|---|
| `DATABASE_URL` | `postgres://...` | Set by `fly postgres attach`. |
| `SECRET_KEY` | 32-byte random | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `GITHUB_TOKEN` | read-only PAT | `public_repo` scope ONLY. Used by the sync worker. |
| `FLASK_ENV` | `production` | |
| `QUILLIN_HUB_LOG_LEVEL` | `info` | |
| `SIGNING_PUBLIC_KEY_PATH` | `/app/quill-pub.key` | Defaults to the bundled key. Override to load a rotated key. |
| `TRUSTED_KEY_IDS` | `ca-pubkey-2026` | Comma-separated. During rotation, list both old and new. |

## 7. Deploy

From `quillin-hub/`:

```bash
fly launch --copy-config  # generates fly.toml
fly deploy
```

`fly.toml` example block:

```toml
app = "quillin-hub"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  FLASK_ENV = "production"
  QUILLIN_HUB_LOG_LEVEL = "info"
```

## 8. Smoke test in staging

1. Point a staging app at the same Postgres + a staging `GITHUB_TOKEN`.
2. From the operator's workstation:
   ```bash
   python quillin-hub/smoke_test.py --server https://quillin-hub-staging.fly.dev
   ```
3. Manual checks: open `/api/v1/types`, open `/api/v1/artifacts`, open
   the storefront, and submit a test-signed Quillin via the Forge.
4. Confirm the storefront shows `Signed by ca-pubkey-2026` on the
   test artifact.

## 9. Promotion

1. Run the smoke test against staging (step 8). All checks green.
2. Soak for 30 minutes: monitor Fly's `fly logs` for unhandled
   exceptions, slow queries, or 5xx responses.
3. If clean, `fly deploy` against production.
4. Re-run the smoke test against `https://hub.quillforall.org`.

## 10. Rollback

```bash
fly releases rollback
```

The registry DB is a separate Postgres, so the static data survives
a bad deploy. If the bad deploy corrupted the DB, restore from the
most recent Fly Postgres snapshot:

```bash
fly postgres create --snapshot <snapshot-id>
```

## 11. Key rotation

Every 12 months, follow `docs/signing.md` section 7. The Hub
already has the `TRUSTED_KEY_IDS` env var; ship both old and new
ids in the same release, drop the old id after 6 months.

## 12. What can and cannot be done from Windows

Most of the deployment workflow is `fly` CLI + browser; no macOS or
Linux required. Concretely from Windows:

- `fly` CLI works on Windows; install via `winget install Fly-CLI.Fly`.
- DNS records: edit in the domain registrar's web UI.
- TLS: automatic on Fly; manual via Caddy on Hetzner.
- Postgres: `fly postgres` CLI works on Windows; psql via WSL if
  needed.
- GitHub secrets: edit in the GitHub web UI.

What still needs Linux or macOS:

- Writing the rotation script: a Linux shell loop, run from the
  operator's workstation. Works on macOS too; on Windows use WSL.
- Compiling the optional `quillin_lint` AST extensions (none in
  the current beta).
```

- [ ] **Step 3: Commit the two new docs**

```bash
git add docs/signing.md docs/release/quillin-hub-deployment.md
git commit -m "docs: signing flow + Hub deployment runbook

docs/signing.md is the user-facing flow: keypair, signing,
verifying, install-time checks, key rotation, threat model.
docs/release/quillin-hub-deployment.md is the ops runbook
from 'git clone' to a working public Hub on Fly.io, including
DNS, TLS, Postgres, env vars, deploy, smoke test in staging,
promotion, rollback, and key rotation.

Refs #517 #519."
```

---

## Task 6: CHANGELOG + RELEASE + done.md

**Files:**
- Modify: `CHANGELOG.md` (one new paragraph under `## 0.9.0 Beta 1`)
- Modify: `docs/release/RELEASE.md` (one new bullet)
- Modify: `done.md` (replace the current "What changed" section to include the deployment + signing work)

- [ ] **Step 1: Add a paragraph to `CHANGELOG.md`**

Find `## 0.9.0 Beta 1` and the existing "What's New in this beta"
paragraph (the one added in the previous done.md work). Immediately
after it, add:

```markdown

The Quillin Hub now signs every published artifact with a detached
Ed25519 signature in a minisign-shaped `.minisig` sidecar. The Hub
Submission Forge and the in-app install path both verify the
signature before acting on the artifact; an unsigned submission is
rejected with a clear error. One global publisher key
(`ca-pubkey-2026`) signs all official artifacts; per-author keys
are explicitly out of scope for the beta. See `docs/signing.md`
for the flow and `docs/release/quillin-hub-deployment.md` for
the runbook.
```

- [ ] **Step 2: Add a bullet to `docs/release/RELEASE.md`**

Find the "Pre-tag checklist" section. Add a new bullet:

```markdown
8. Manifest signing is in (Quillin Hub rejects unsigned
   submissions; in-app install refuses unsigned outside
   `QUILL_SAFE_MODE`). The publisher key is committed;
   `docs/signing.md` documents the flow.
```

- [ ] **Step 3: Update `done.md`**

Append a new section to `done.md` titled "What changed (continued:
signing + deployment)" that covers:

- The 4 new files (`quill/tools/signing.py`, `quill-pub.key`,
  `quillin-hub/quill-pub.key`, `docs/signing.md`,
  `docs/release/quillin-hub-deployment.md`, `tests/unit/tools/test_signing.py`).
- The modified files (`quill/tools/artifact_validate.py`,
  `quillin-hub/app/forge/linter.py`,
  `quillin-hub/app/models/database.py`,
  `quillin-hub/app/web/templates/index.html`,
  `quillin-hub/app/web/templates/plugin.html`,
  `quillin-hub/worker/sync_to_pages.py`,
  `quillin-hub/smoke_test.py`,
  `quill/ui/quillin_hub_submit.py`,
  `quill/ui/main_frame_quillins.py`,
  `tests/unit/tools/test_artifact_validate.py`,
  `CHANGELOG.md`, `docs/release/RELEASE.md`).
- The 2 new validator tests + 10 new signing tests.
- The new `--require-signed` CLI flag.
- The PyNaCl requirement promotion.
- The new env vars (`SIGNING_PUBLIC_KEY_PATH`, `TRUSTED_KEY_IDS`).
- The Fly.io recommendation in the runbook.
- The 7 commits that make up the PR.
- The issue closures (#517 and #519 both `completed`).

The engineer writes the section in the same style as the existing
`done.md` — short paragraphs, one table for "files added" and one
for "files modified", a verification block listing the new tests,
and a short risks/follow-ups note that mirrors the prior one.

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md docs/release/RELEASE.md done.md
git commit -m "docs(changelog): signing + deployment work

CHANGELOG adds a paragraph under 0.9.0 Beta 1; RELEASE adds a
new pre-tag checklist bullet; done.md gains a section covering
the 4 new files, 12 modified files, 12 new tests, the new
--require-signed flag, the PyNaCl requirement promotion, the
2 new env vars, and the issue closures.

Refs #517 #519."
```

---

## Task 7: Issue reopen + close + final smoke test

**Files:** none (just `gh` operations and verification).

- [ ] **Step 1: Reopen #517**

```bash
gh issue reopen 517 --repo Community-Access/QUILL
```

Expected: `Reopened issue #517`.

- [ ] **Step 2: Post the reopen comment on #517**

```bash
gh issue comment 517 --repo Community-Access/QUILL --body "Reopening on the full acceptance: the deployment runbook and the signing flow both now exist in this PR.

- Deployment runbook: docs/release/quillin-hub-deployment.md covers DNS, TLS, Postgres, env vars, deploy, smoke test in staging, promotion, rollback, key rotation, and the Windows-friendly section.
- Signing flow: quill.tools.signing (Ed25519 / minisign-shaped), docs/signing.md (user-facing flow), fail-closed hooks in the Hub Submission Forge, the in-app submit dialog, and the in-app install path.
- The bundled Community-Access publisher key is committed (ca-pubkey-2026); the private key is held outside the repo.
- 10 new tests in tests/unit/tools/test_signing.py; 2 new tests in tests/unit/tools/test_artifact_validate.py.

Public deployment of hub.quillforall.org itself is still an ops track (DNS, hosting, Postgres credentials, GitHub org access) — all out of repo scope."
```

- [ ] **Step 3: Re-close #517 with the closing comment**

```bash
gh issue close 517 --repo Community-Access/QUILL --reason completed --comment "Closed on full acceptance. See the deployment runbook at docs/release/quillin-hub-deployment.md and the signing flow at docs/signing.md. Public deployment of hub.quillforall.org itself is an ops track (DNS, hosting, Postgres, GitHub PAT scopes) — those remain out of repo scope."
```

- [ ] **Step 4: Reopen #519**

```bash
gh issue reopen 519 --repo Community-Access/QUILL
```

Expected: `Reopened issue #519`.

- [ ] **Step 5: Post the reopen comment on #519**

```bash
gh issue comment 519 --repo Community-Access/QUILL --body "Reopening on the full acceptance: signing is now in code and documented.

- quill.tools.signing: Ed25519 / minisign-shaped sign_artifact / verify_artifact / signature_status / is_signed + a keygen / sign / verify CLI.
- docs/signing.md: the user-facing flow (keypair, signing, verifying, install-time checks, key rotation, threat model).
- Hub Submission Forge (quillin-hub/app/forge/linter.py): signature_status() is the first audit step; unsigned submissions are rejected with status=Rejected.
- In-app submit dialog (quill/ui/quillin_hub_submit.py): shows the signature line; disables 'Open the Quillin Hub' when unsigned.
- In-app install path (quill/ui/main_frame_quillins.py): verify_artifact() runs first; unsigned installs are blocked outside QUILL_SAFE_MODE.
- Artifact.signer_key_id added (nullable VARCHAR(64)); sync worker reads the sidecar and fills it; storefront + detail page show 'Signed by ca-pubkey-2026' or 'Unsigned'.
- 10 new tests in tests/unit/tools/test_signing.py; 2 new tests in tests/unit/tools/test_artifact_validate.py.

The capability model is in docs/quillins/quillins.md sections 6, 13, 14 (catalogue 14.1, contribution reference 14.2). Per-author keys, transparency logs, and revocation are explicitly out of scope (publisher-only key, documented in docs/signing.md)."
```

- [ ] **Step 6: Re-close #519 with the closing comment**

```bash
gh issue close 519 --repo Community-Access/QUILL --reason completed --comment "Closed on full acceptance. Signing is in code (quill.tools.signing) and documented (docs/signing.md). Fail-closed at the Hub Submission Forge, the in-app submit dialog, and the in-app install path. Artifact model carries signer_key_id; the storefront badge reflects it. 10 new signing tests + 2 new validator tests. The capability model lives in docs/quillins/quillins.md sections 6, 13, 14. Per-author keys are explicitly out of scope; the single global publisher key (ca-pubkey-2026) is the trust root."
```

- [ ] **Step 7: Run the full local verification one more time**

```bash
python -m pytest tests/unit/tools/test_signing.py tests/unit/tools/test_artifact_validate.py -v
python -m pytest tests/unit/ui -q -k "public_surface or dialog_inventory"
python quillin-hub/smoke_test.py
ruff check quill/tools/signing.py quill/tools/artifact_validate.py quillin-hub/app/forge/linter.py quill-hub/app/models/database.py quill-hub/worker/sync_to_pages.py quill-hub/smoke_test.py quill/ui/quillin_hub_submit.py
ruff format --check quill/tools/signing.py quill/tools/artifact_validate.py
```

Expected:
- `10 passed` for test_signing.py, `33 passed` for test_artifact_validate.py.
- `6 passed` for the UI public-surface / dialog-inventory gate.
- `N+1 / N+1 checks passed` for the Hub smoke test.
- `All checks passed!` for `ruff check`.
- `N files already formatted` for `ruff format --check`.

- [ ] **Step 8: Commit the final state**

```bash
git status
# Confirm the working tree is clean. If there are any uncommitted
# edits (e.g. from a doc fix during verification), commit them.
# No new commit expected if step 7 was clean.
```

If the working tree is dirty:

```bash
git add -A
git commit -m "chore: post-verification tidying"
```

- [ ] **Step 9: Report to the user**

The engineer reports the final state:

- Number of commits added (target: 7).
- Test counts: 10 new signing, 2 new validator, 1 new smoke check.
- Issues closed: #517, #519, both with `completed` reason.
- Working tree status: clean.
- Final list of new files and modified files.

Per CLAUDE.md: do NOT push. Do NOT open a PR. The user will do
those steps themselves.

---

## Self-Review

**1. Spec coverage:**

- Section 1 (signing primitive) → Task 1
- Section 2 (validator hook) → Task 2
- Section 3 (Hub forge hook) → Task 3
- Section 4 (in-app hook) → Task 4
- Section 5 (deployment runbook) → Task 5, Step 2
- Section 6 (signing flow doc) → Task 5, Step 1
- Section 7 (tests) → Task 1 (10 signing tests), Task 2 (2 validator tests), Task 3 (1 smoke test)
- Section 8 (issue closures) → Task 7

All spec sections covered. No gaps.

**2. Placeholder scan:**

No TBD, no TODO, no "fill in details", no "similar to task N", no
"add appropriate error handling". Every step has the actual code
or the actual file content the engineer needs.

**3. Type consistency:**

- `SignatureStatus` defined in Task 1; consumed in Tasks 2, 3, 4 with the same fields.
- `signature_status()` defined in Task 1; called in Tasks 2, 3, 4 with the same signature.
- `signer_key_id` column added in Task 3; written by the sync worker in Task 3; read by the templates in Task 3.
- `--require-signed` CLI flag added in Task 2; passed by the in-app dialog in Task 4 (the dialog calls `validate_artifact` with `require_signed=True` via the underlying signature check, not the CLI flag — but the test in Task 2 covers the CLI directly).
- `KEY_ID = "ca-pubkey-2026"` defined in Task 1; referenced by `docs/signing.md` in Task 5; referenced in the `done.md` text in Task 6.
- `quill-pub.key` committed in Task 1; consumed by the linter in Task 3; documented in Task 5.

No inconsistencies. Plan is internally consistent.
