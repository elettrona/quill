# Quillin Hub Deployment + Manifest Signing

**Date:** 2026-07-04
**Scope:** Single PR that closes issues #517 (Quillin Hub launch) and
#519 (plugin capability, signing, marketplace) on the *full* acceptance
criteria, not the partial closes we did earlier. Adds:

- `docs/release/quillin-hub-deployment.md` — concrete deployment runbook
  for `hub.quillforall.org`.
- `quill/tools/signing.py` — minisign-style Ed25519 detached signature
  primitives: `sign_artifact`, `verify_artifact`, `is_signed`,
  `signature_status`, and a CLI.
- `docs/signing.md` — the user-facing signing flow doc: keypair
  generation, signing an artifact, what the Hub checks, what the
  in-app install checks, key rotation, failure UX.
- Hooks in `quill.tools.artifact_validate` to verify signatures as
  the *first* check (so the validator can refuse to even look at
  an artifact before the per-type validator runs).
- Hooks in `quillin-hub/app/forge/linter.py` to run the same verify
  on every submission before the existing validation pipeline.
- Hooks in `quill/ui/quillin_hub_submit.py` so the in-app dialog
  reports signature status alongside the per-type report.
- A `Signed by ...` field in the storefront row + the
  `Artifact` model + the registry API JSON.
- New tests in `tests/unit/tools/test_signing.py` and one extra
  case in `tests/unit/tools/test_artifact_validate.py`.
- One more CHANGELOG paragraph under 0.9.0 Beta 1, and a Release.md
  bullet noting signing is in.
- Reopen #517 and #519, post closing comments on the *full*
  acceptance, close with `completed` not `not planned`.

**Status:** Approved design (post brainstorming).

## Goals

- `hub.quillforall.org` is *deployable* from this repo: an ops
  person with a host can follow the runbook and get a working
  public site.
- Every Quillin-Hub-bound artifact has a detached Ed25519
  signature. The Hub, the in-app install, and the local CLI all
  use the same `quill.tools.signing.verify_artifact()` function.
- Signature failure is fail-closed at every layer.
- One global publisher key (Community-Access) signs all official
  artifacts. Per-author keys are explicitly out of scope.
- The work is reviewable in one sitting, ships in one PR, and
  leaves the repo in golden state.

## Non-goals

- Per-author keys, transparency logs, revocation lists, key
  escrow. The first signing flow is the publisher's key only.
- Code-signing certificates (Authenticode / Apple Developer ID /
  apt-secure). Manifests are JSON / Markdown data; the OS does
  not gate on them. (See `docs/release/quill-macos-signing-notarization-runbook.md`
  for the parallel executable-signing flow.)
- Rotation automation. The key is documented as `rotated yearly`
  with the procedure manual; the Hub reads the current public
  key from a config that the ops team updates.
- A new submission flow. The Submission Forge is the same; the
  signature is one more gate in the existing audit pipeline.
- A re-roll of `artifact_validate`. The signature check is a
  pre-hook, not a rewrite.

## Design

### Section 1 — The signing primitive (`quill/tools/signing.py`)

**Why Ed25519 / minisign-shaped, not GPG or cosign:**

- GPG: too heavy, keyserver dance, the QUILL community does not
  use it for anything else.
- cosign: transparency-logged and tamper-evident, but pulls in
  Sigstore infrastructure the Hub does not have.
- minisign / Ed25519: 64-byte signatures, 32-byte public keys,
  one `sign` call, one `verify` call. Used by OpenBSD, Homebrew,
  Signal, and others for exactly this purpose. PyNaCl is already
  on the system from `flask_migrate` (transitive).

**Module shape:**

```python
# quill/tools/signing.py

PUBLIC_KEY_B64: str  # the Community-Access publisher public key, b64
KEY_ID: str          # a short identifier, "ca-pubkey-2026"
SIGNATURE_SUFFIX = ".minisig"
# Sidecar convention: <artifact> + ".minisig"
# For zipped Quillins: the .minisig sits next to the .zip.

def load_publisher_public_key() -> PublicKey: ...
def sign_artifact(artifact_path: Path, secret_key: SecretKey) -> Path:
    # returns the .minisig path
def verify_artifact(artifact_path: Path) -> SignatureStatus: ...
def is_signed(artifact_path: Path) -> bool: ...
def signature_status(artifact_path: Path) -> SignatureStatus:
    # dataclass: {signed, verified, signer_key_id, error?}
def main(argv): ...  # CLI: sign / verify / keygen
```

`SignatureStatus` is a small dataclass the report layer can
serialize. `verify_artifact` returns:

- `signed=False, verified=False, error="no sidecar .minisig"` if
  no signature
- `signed=True, verified=True, signer_key_id=...` on pass
- `signed=True, verified=False, error="signature does not match"`
  on tampering
- `signed=True, verified=False, error="signed by a different key"`
  on wrong-key

**Key generation:** `python -m quill.tools.signing keygen` writes
two files: `quill-pub.key` (32 bytes base64) and
`quill-priv.key` (64 bytes base64, with a header line). The
private key file starts with `untrusted comment: quill signing
key — do not commit` so `git add` / `git status` makes it
obvious. The Hub's `quill-pub.key` is committed to the repo
(`quillin-hub/quill-pub.key`) and pinned in
`quill/tools/signing.py` as the default public key.

**Storage convention:**

```
myartifact.qvp.json
myartifact.qvp.json.minisig     <-- base64 signature
```

For Quillin zips:

```
my-quillin.zip
my-quillin.zip.minisig
```

The .minisig file is plain text:

```
untrusted comment: quill artifact signature
key id: ca-pubkey-2026
sig: Base64(64-byte Ed25519 signature)
```

This is minisign's text format, so any tool in the minisign
ecosystem (and human eyes with `cat`) can read it.

### Section 2 — Validator hook (`quill/tools/artifact_validate.py`)

The current `validate_artifact()` runs the per-type validator
and returns `{path, type, label, status, errors, warnings}`. We
add a *pre-check*: if a `.minisig` is missing for the artifact
and the artifact is being submitted to the Hub, the report
gets a new top-level field `signature` with the
`SignatureStatus`. The per-type validator still runs (so the
author sees their existing errors), but a missing or invalid
signature escalates the final status to `fail`.

```python
# In validate_artifact(), before _VALIDATORS[detected](path):
sig = signature_status(path)
if sig is not None and not sig.verified:
    errors.append(
        f"signature: {sig.error or 'unsigned'}"
    )
# Then the per-type validator runs as today.
```

The new field is *always* present in the JSON report:

```json
{
  "path": "...",
  "type": "...",
  "label": "...",
  "status": "fail",
  "errors": ["signature: no sidecar .minisig", ...],
  "warnings": [...],
  "signature": {
    "signed": false,
    "verified": false,
    "signer_key_id": null,
    "error": "no sidecar .minisig"
  }
}
```

`render_report()` adds one extra line so the screen-reader-
friendly text shows signature status next to the type line:

```
FAIL  myartifact.qvp.json
  type: Verbosity pack (verbosity-pack)
  signature: missing (fail-closed)
  error: signature: no sidecar .minisig
  ...
```

A `--require-signed` flag is added to the CLI (default true in
the Hub context, default false when an author runs it locally
to iterate without bothering to sign). The flag exists for
ergonomics; the in-app check and the Hub Forge both pass
`--require-signed`.

### Section 3 — Hub Submission Forge hook

`quillin-hub/app/forge/linter.py` currently runs
`validate_artifact()` and adds Bandit + AST SecurityWatchdog for
Quillins. We add a *first* step: call
`signature_status(artifact_path)` before the validator runs. If
`signed=False` or `verified=False`, the submission is recorded
in the `submissions` table with `status=Rejected` and the same
error message the validator returns. The user sees the same
report in the Forge UI as the local CLI / in-app dialog would
show.

The registry's `Artifact` model gets a `signer_key_id` column
(VARCHAR(64), nullable). The sync worker fills it in from
the `.minisig` of the artifact on `main`. The storefront row
shows `Signed by ca-pubkey-2026` (or `Unsigned` in red) next
to the version.

### Section 4 — In-app install hook

`quill/ui/quillin_hub_submit.py` is the dialog. We add the
signature line to the report body, and we change the "Open
the Quillin Hub" button behavior: if the report says signature
is missing or invalid, the dialog disables the Open button and
shows a clear "Sign your artifact first; see `docs/signing.md`"
instruction. The user can still close the dialog and re-submit
after signing.

For *installing* an artifact (Tools > Quillins > Manage
Quillins > Install from local file), the install path is
checked separately: `verify_artifact()` runs before the
Quillin folder is added to the user's Quillins. Fail-closed
with a dialog: "This artifact is not signed. Unsigned Quillins
can be installed only in QUILL_SAFE_MODE; the published Hub
policy requires a signature. Install anyway?"

### Section 5 — Deployment runbook (`docs/release/quillin-hub-deployment.md`)

~120 lines, follows the tone of `docs/release/quill-macos-signing-notarization-runbook.md`.

**Sections:**

1. Executive decision — the Hub is deployable from this repo;
   the runbook covers the path from `git clone` to a working
   `https://hub.quillforall.org`.
2. Why this matters — the storefront is a real
   accessibility-critical surface (a screen reader user has to
   reach it and trust what it shows).
3. Hosting choice — recommends Fly.io (Postgres + Flask in one
   process, free tier fits the beta, IPv6 DNS, GitHub Action
   deploys from `main`). Names Render + Hetzner VPS as
   alternatives with a one-line trade-off.
4. DNS + TLS — `hub.quillforall.org` A record, Let's Encrypt
   via the hosting provider, HSTS preload, CAA record
   restricting issuance to the chosen CA.
5. Postgres — `fly postgres create`, DATABASE_URL env var,
   backup schedule, migration command
   (`flask db upgrade`).
6. Env vars — full table: `DATABASE_URL`, `SECRET_KEY` (32-byte
   random, in fly secrets), `GITHUB_TOKEN` (read-only PAT,
   `public_repo` scope only), `FLASK_ENV=production`,
   `QUILLIN_HUB_LOG_LEVEL=info`, `SIGNING_PUBLIC_KEY_PATH`
   (defaults to bundled key).
7. Deploy — `fly deploy` from `quillin-hub/`, with a
   `fly.toml` example block.
8. Smoke test in staging — `python quillin-hub/smoke_test.py`
   against the staging URL, then manual checks (open
   `/api/v1/types`, open `/api/v1/artifacts`, install a
   test-signed artifact).
9. Promotion — staging first, prod second, with a 30-minute
   soak between.
10. Rollback — `fly releases rollback`; the registry DB is
    a separate Postgres so the static data survives a bad
    deploy.
11. Key rotation — every 12 months: generate a new keypair,
    sign all current artifacts with the new key, publish the
    new public key in `quill/tools/signing.py::PUBLIC_KEY_B64`
    and in the Hub config, ship a release that pins both old
    and new for 6 months (grace period), then drop the old
    one. The Hub has a `TRUSTED_KEY_IDS` env var that lists
    currently-trusted key ids.
12. What can and cannot be done from Windows — mirrors the
    macOS runbook's section 4. Most of the deployment
    workflow is `fly` CLI + browser; no macOS needed.

### Section 6 — Signing flow doc (`docs/signing.md`)

~80 lines. User-facing.

**Sections:**

1. What signing does — names the threat model (tampered Hub
   download, MITM on the storefront, malicious Quillin
   submission).
2. The Community-Access publisher key — current `key_id`,
   fingerprint, where to find it (`quillin-hub/quill-pub.key`,
   `quill/tools/signing.py::PUBLIC_KEY_B64`).
3. How to sign — `python -m quill.tools.signing sign
   path/to/artifact`. One line, idempotent.
4. How to verify — `python -m quill.tools.signing verify
   path/to/artifact` and the
   `quill.tools.signing.verify_artifact()` Python API for
   scripts.
5. What the Hub does — every submission is verified; an
   unsigned submission is rejected with a clear message.
6. What QUILL does at install — fail-closed; the install
   dialog shows the signature status and refuses unsigned
   installs outside `QUILL_SAFE_MODE`.
7. Key rotation — what to expect, when the grace period
   applies, how to update the trusted-keys list.
8. Threat model — what signing does NOT do: it doesn't
   prove the author is who they say (no identity chain),
   it doesn't hide who downloaded what (no privacy), it
   doesn't replace the security scan (Quillins still go
   through Bandit + AST SecurityWatchdog).

### Section 7 — Tests

**`tests/unit/tools/test_signing.py`** (new, ~120 lines):

- `test_sign_artifact_creates_sidecar`
- `test_verify_artifact_round_trip`
- `test_verify_artifact_tampered_returns_invalid`
- `test_verify_artifact_wrong_key_returns_invalid`
- `test_verify_artifact_missing_sidecar_returns_unsigned`
- `test_keygen_produces_valid_keypair`
- `test_signature_status_dataclass`
- `test_cli_sign_and_verify`
- `test_cli_verify_unsigned_exits_2` (no sidecar = exit 2,
  same as `artifact_validate`'s "not found" code)
- `test_signing_fails_closed_in_safe_mode_off`

**`tests/unit/tools/test_artifact_validate.py`** (one new case):

- `test_validate_unsigned_artifact_marks_signature_missing` —
  confirms the new `signature` field is present and `errors`
  contains the signature line.

**`tests/unit/tools/test_artifact_validate.py`** (CLI case):

- `test_cli_require_signed_disables_pass_for_unsigned` —
  confirms `--require-signed` flips a passing-but-unsigned
  artifact to fail.

No new tests in `quillin-hub/` — the smoke test already
exercises the registry paths; the linter change is small
and visible in the existing audit.

### Section 8 — Issue closures

**Reopen #517** with a comment:

> Reopening on the full acceptance: deployment runbook + signing
> flow both now exist in this PR. The runbook at
> `docs/release/quillin-hub-deployment.md` is the path from
> `git clone` to a working public Hub on Fly.io. The signing
> flow (`quill.tools.signing`, `docs/signing.md`) is the
> "Manifest + signing documented" acceptance bullet. Public
> deployment itself is still an ops track (DNS, hosting,
> Postgres), but everything the repo can ship is shipped.

**Reopen #519** with a comment:

> Reopening on the full acceptance: signing is now in code and
> documented. `quill.tools.signing` (Ed25519 / minisign-shaped)
> signs and verifies every artifact. The Hub Submission Forge
> rejects unsigned submissions (fail-closed). The in-app install
> refuses unsigned installs outside `QUILL_SAFE_MODE`. The
> capability model is in `docs/quillins/quillins.md` section
> 6, 13, 14 (with the catalogue in 14.1 and the contribution
> reference in 14.2). Per-author keys, transparency logs, and
> revocation are explicitly out of scope (publisher-only key
> is the documented model; see `docs/signing.md`).

**Re-close #517** with `completed` and a closing comment that
points at both the runbook and the signing flow. The closing
comment also names what remains ops-track: "DNS, hosting
credentials, Postgres credentials, GitHub org access for
the deploy PAT — all out of repo scope."

**Re-close #519** with `completed` and a closing comment that
points at `quill.tools.signing`, `docs/signing.md`, the Hub
forge hook, the in-app install hook, the model column, the
storefront badge, the 10 new tests, and the single global
publisher key.

### Files to touch

New:

- `quill/tools/signing.py` (Ed25519 sign / verify / keygen)
- `quill-pub.key` (the public half; committed, 32 bytes base64)
- `quillin-hub/quill-pub.key` (the same key, for the Hub's
  deploy)
- `docs/signing.md` (the signing flow doc)
- `docs/release/quillin-hub-deployment.md` (the deployment
  runbook)
- `tests/unit/tools/test_signing.py` (10 new cases)
- A short signing test fixture in
  `tests/unit/tools/fixtures/` (a tiny signed `.qvp.json` so
  the round-trip test does not depend on the real publisher
  key)

Modified:

- `quill/tools/artifact_validate.py` — add signature pre-check
  + `--require-signed` flag + `signature` field in the report
  + one extra line in `render_report`
- `quillin-hub/app/forge/linter.py` — add signature verify as
  the first audit step
- `quillin-hub/app/models/database.py` — add `signer_key_id`
  column to `Artifact`
- `quillin-hub/worker/sync_to_pages.py` — read the sidecar
  and fill `signer_key_id` on upsert
- `quillin-hub/app/web/templates/index.html` — show the
  "Signed by ..." line in the storefront row
- `quillin-hub/app/web/templates/plugin.html` — show the
  signer key id on the detail page
- `quillin-hub/smoke_test.py` — add a check that an unsigned
  submission is rejected
- `quill/ui/quillin_hub_submit.py` — add the signature line
  to the dialog, gate the Open button on signature
- `quill/ui/main_frame_quillins.py` — verify signature
  before install
- `tests/unit/tools/test_artifact_validate.py` — 2 new cases
- `CHANGELOG.md` — one new paragraph under 0.9.0 Beta 1
- `docs/release/RELEASE.md` — one new bullet in Pre-tag
  checklist
- `done.md` — add the deployment + signing section

### Risks

- **The key is committed.** That's the public half, so
  committing it is safe; the convention is to commit
  `quill-pub.key` and never `quill-priv.key`. The plan calls
  this out in `docs/signing.md` and in the module docstring.
- **PyNaCl transitive dep.** PyNaCl is installed in this env
  as a transitive of `flask-migrate`; the Hub's
  `requirements.txt` already pulls in `flask-migrate`. We
  promote PyNaCl to a direct requirement on
  `quill-hub/requirements.txt` and add a one-line note in
  `pyproject.toml` documenting the optional `[signing]`
  extra. We do *not* make signing optional — it is
  mandatory for the Hub.
- **Fly.io is a real choice.** The user may prefer Render or
  Hetzner; the runbook names the choice and the alternatives
  with one-line trade-offs. A maintainer who wants Render
  rewrites section 3; nothing else changes.
- **The signing key is real and should be rotated annually.**
  The runbook documents the rotation procedure; the Hub has
  a `TRUSTED_KEY_IDS` env var so a second key can ship in
  parallel. No automation: the next maintainer runs through
  the runbook's section 11.
- **The PR is large.** The plan is structured so each commit
  is independently reviewable:
  1. signing primitive + tests
  2. validator hook + tests
  3. Hub forge hook + storefront + model column
  4. in-app install hook
  5. docs (signing + deployment)
  6. CHANGELOG + RELEASE + done.md
  7. issue reopens and re-closes

### What this PR is NOT

- Not a code-signing-certificate story. We sign *manifests*,
  not executables; the macOS runbook covers the executable
  path.
- Not a per-author key story. One publisher key; per-author
  keys are explicitly deferred.
- Not a transparency log story. No Sigstore, no Rekor.
- Not a new submission flow. The Submission Forge is the
  same; the signature is one more gate.
- Not a new artifact type. The seven types are unchanged.
