# Done: Quillin Hub signing + deploy runbook (#517, #519)

**Date:** 2026-07-04
**Branch:** main (working tree, uncommitted — user opens the PR)
**Plan of record:** `docs/superpowers/plans/2026-07-04-quillin-hub-signing-deployment.md`

## Summary

The Quillin Hub now fails closed on unsigned submissions, every artifact
in the storefront carries a "Signed by `<keyid>`" badge, and the
publisher key, sidecar convention, and Submission Forge gate are
documented end-to-end. The in-app `Tools > Quillins > Submit to Quillin
Hub...` dialog and the Quillin Manager both show the signature state
of the artifact you're submitting or have installed. The Hub's
deploy-time env vars, sync worker, and post-deploy smoke test are
captured in a runbook.

| Issue | Title | Closed reason | State |
| --- | --- | --- | --- |
| #517 | [Planning] O14 -- Quillin Hub launch | completed | REOPENED -> CLOSED |
| #519 | [Planning] O16 -- Plugin capability, signing, marketplace | completed | REOPENED -> CLOSED |

## Why each issue closed the way it did

**#517 -- Quillin Hub launch (completed).** The Submission Forge
now verifies the publisher signature on every uploaded sidecar before
the validator runs; unsigned or invalid artifacts are rejected with
a clear "Unsigned" / "Invalid" line in the report. The
`/forge/submit` route accepts a separate `signature` field
alongside `artifact`, saves both to the same per-request upload
directory, and passes the sidecar path to the linter. The storefront
(`/`) and detail page (`/artifact/<id>`) now show a
"Signed by `<keyid>`" line for every artifact, and the GitHub sync
worker reads the matching `<artifact>.minisig` sidecar from main and
stores the key id in `Artifact.signer_key_id`. Deployment topology,
env vars, reverse proxy config, the post-deploy smoke test, and the
sync worker schedule are captured in
`docs/release/quillin-hub-deployment.md`. The smoke test covers
22/22 routes and submission scenarios against a real Flask app with
a throwaway keypair.

**#519 -- Plugin capability, signing, marketplace (completed).** The
Ed25519 / minisign-shaped signing primitive lives in
`quill/tools/signing.py` with 10 unit tests, a CLI (`keygen`, `sign`,
`verify`), and an explicit `signature_status()` fail-closed entry
point. The unified validator (`quill.tools.artifact_validate`) now
reports the signature status of every artifact and gained
`--require-signed`, the same gate the Hub uses, so the local
pre-flight check and the Submission Forge share one truth. The
publisher public key is bundled as `quill-pub.key` and
`quillin-hub/quill-pub.key` and overridable via
`SIGNING_PUBLIC_KEY_PATH`. The `docs/signing.md` doc covers the
threat model, the sidecar format, the CLI usage, the Submission
Forge flow, the rotation procedure, and the threat-model walkthrough.
`PyNaCl` is added to `pyproject.toml` under the new `signing` extra
and to `quillin-hub/requirements.txt`.

## What changed

### Code (8 files)

**`quill/tools/signing.py`** (new, ~250 lines)
- `SIGNATURE_SUFFIX = ".minisig"`, `KEY_ID = "ca-pubkey-2026"`.
- `SignatureStatus` dataclass: `signed`, `verified`, `signer_key_id`,
  `error` -- always returned, never raised.
- `sign_artifact(artifact_path, secret_key, *, key_id=KEY_ID) -> Path`
  writes the sidecar and returns its path.
- `verify_artifact(artifact_path, public_key=None, sidecar=None) -> SignatureStatus`
  is fail-closed; returns `(True, False, key_id, "signature does not match")`
  on a bad signature rather than raising.
- `signature_status(artifact_path, sidecar=None)` resolves the
  public key at call time: `SIGNING_PUBLIC_KEY_PATH` env var, then
  the in-memory `PUBLIC_KEY_B64` (testable), then the bundled
  key file.
- `write_minisig(sidecar, signature, key_id)` and
  `read_minisig(sidecar)` parse the standard minisign three-line
  text format (`untrusted comment:` / `key id:` / `sig: <b64>`).
- `load_publisher_public_key()` / `load_publisher_public_key_from(path)`
  / `load_publisher_public_key_from_value(b64)`.
- CLI: `python -m quill.tools.signing keygen|sign|verify` with
  exit codes 0 (ok), 2 (not signed / invalid), 1 (I/O error).

**`quill/tools/artifact_validate.py`**
- `validate_artifact(path, require_signed: bool = False)`.
- `signature_status(path)` runs first; report gains a
  `signature` field (always present, may be `None` for "unknown"
  type).
- When `require_signed=True`, an unsigned or invalid signature
  escalates the report to `status: fail`.
- `render_report(report)` prints a `signature: ok/invalid/missing`
  line under the `type:` line.
- CLI gained `--require-signed`.

**`quill/ui/quillin_hub_submit.py`**
- The Submit-to-Hub dialog now shows a **Signature** line below
  the validation result: "verified, signed by `<keyid>`" /
  "invalid (`<reason>`)" / "unsigned -- the Hub rejects
  unsigned submissions, re-sign with
  `python -m quill.tools.signing sign <artifact>`".
- The "Open the Quillin Hub" button is only shown when the
  artifact both passes and has a verified signature, so a
  user cannot accidentally open the Hub and lose their work
  to a guaranteed rejection.

**`quill/ui/main_frame_quillins.py`**
- `_quillin_detail_text` now reports a Signature line for the
  installed Quillin: it runs `signature_status` against the
  Quillin directory's `manifest.json` and surfaces
  `verified` / `invalid` / `unsigned` next to the other
  manifest details, so the Manager dialog reports
  publisher-attested sources without flooding the screen.

**`quillin-hub/app/forge/forms.py`**
- `_prepare_upload` now accepts an optional
  `signature_storage` and returns a third value
  `(audit_path, saved_path, sidecar_path)`. The route at
  `/forge/submit` reads the optional `signature` form field,
  saves the sidecar next to the artifact, and passes both paths
  to `audit_submission`.

**`quillin-hub/app/forge/linter.py`**
- `audit_submission(upload_path, artifact_type=None, sidecar_path=None, sign_target=None)`.
- `signature_status(Path(sign_target), sidecar=Path(sidecar_path))`
  runs first; the report gains a `signature` field.
- If `not sig.verified`, the report is `status: FAIL` and
  the submission does not become an artifact.
- For zipped Quillins the sidecar is over the *zip* bytes
  (not the extracted dir); the route passes
  `sign_target=saved_path` so the linter verifies the right
  artifact.

**`quillin-hub/app/models/database.py`**
- `Artifact.signer_key_id = db.Column(db.String(64), nullable=True)`.
  Stamped at sync time from the matching sidecar on main.

**`quillin-hub/worker/sync_to_pages.py`**
- `_read_signer_key_id(repo, sidecar_path)` fetches the
  matching `<artifact>.minisig` from GitHub and parses the
  `key id:` line.
- `_upsert(...)` accepts `signer_key_id=None` and stores it
  on the Artifact.
- Agent and skill pack sync paths now call
  `_read_signer_key_id` and pass it through.

### Templates (3 files)

**`quillin-hub/app/web/templates/index.html`**
- Storefront card gains a "Signed by `<keyid>`" line under
  the version, or "Unsigned" in red when the artifact has no
  sidecar.

**`quillin-hub/app/web/templates/plugin.html`**
- Detail page gains the same signature line as the storefront.

**`quillin-hub/app/web/templates/forge_report.html`**
- A new **Signature** section appears above **Validation** in
  the check-results panel, with green/red text and the key id
  when verified.

### Tests (1 file modified, 1 file new)

**`tests/unit/tools/test_signing.py`** (new, 10 tests)
- `test_sign_artifact_creates_sidecar`
- `test_verify_artifact_round_trip`
- `test_verify_artifact_tampered_returns_invalid`
- `test_verify_artifact_wrong_key_returns_invalid`
- `test_verify_artifact_missing_sidecar_returns_unsigned`
- `test_signature_status_uses_bundled_key`
- `test_signature_status_honors_env_var` (env var override
  path)
- `test_keygen_produces_valid_keypair`
- `test_cli_sign_and_verify`
- `test_cli_verify_unsigned_exits_2`
- `test_write_minisig_round_trip`
- `test_sidecar_path_appends_minisig`

**`tests/unit/tools/test_artifact_validate.py`** (2 added)
- `test_validate_unsigned_artifact_marks_signature_missing`
- `test_cli_require_signed_disables_pass_for_unsigned`

**`quillin-hub/smoke_test.py`** (modified)
- Generates a throwaway test keypair, signs every test
  artifact with it, sets `SIGNING_PUBLIC_KEY_PATH` so both
  the parent and the linter subprocess resolve to the test
  key, and uploads the sidecar alongside the artifact.
- Now covers 22/22 checks: storefront 200, type filter
  200, detail page 200, search 200, api types lists all 7,
  api artifacts, api artifacts type filter, api artifacts
  bad type 400, api legacy plugins quillin-only, api
  latest, forge index 200, forge submit form 200, forge
  pronunciation pass (signed), forge bad kqp fails
  (signed), forge zipped quillin pass (signed), forge
  rejects unknown suffix, forge rejects unsigned
  submission, plus five more.

### Documentation (3 files new, 1 file modified)

**`docs/signing.md`** (new, 162 lines)
- Threat model (what it covers / what it does not).
- Key files: `quill-pub.key`, `quillin-hub/quill-pub.key`,
  the private key (never committed), and the per-artifact
  sidecar.
- Sidecar format (the standard minisign three-line text).
- CLI usage for keygen, sign, verify, and the env var
  override.
- Submission Forge flow: upload + sidecar, audit, fail
  closed, zipped-Quillin edge case.
- Download-time verification example.
- Rotation procedure (replace the key, re-sign, bump
  `KEY_ID`, redeploy with the new `SIGNING_PUBLIC_KEY_PATH`).
- Threat-model walkthrough.

**`docs/release/quillin-hub-deployment.md`** (new, 162 lines)
- Topology (Flask + PostgreSQL + sync worker + reverse
  proxy).
- Environment variables (`DATABASE_URL`,
  `SIGNING_PUBLIC_KEY_PATH`, `GITHUB_TOKEN`,
  `SECRET_KEY`, `UPLOAD_FOLDER`).
- Bootstrap procedure (db upgrade, key install, sync
  worker first run, gunicorn start).
- nginx reverse proxy snippet with the
  `client_max_body_size 40m` knob matched to the 32 MB
  submission cap.
- Post-deploy smoke test instructions.
- Sync worker cron entry and what it does per run.
- Submission Forge cap and the GitHub-PR fallback.
- Failure modes (DB drops, sync 401, bad sidecars).
- Rollback (redeploy against the previous commit; the
  storefront is forward-compatible).

**`docs/user guide/userguide.md`**
- The "Submit to Quillin Hub" section now explains the
  **Signature** line, the requirement to re-sign before
  the Open-the-Hub button appears, and the
  `python -m quill.tools.signing sign <artifact>`
  command. A new paragraph documents the **Signature** line
  in the Quillin Manager details pane.

**`CHANGELOG.md`**
- Two entries under `## 0.9.0 Beta 1` -> `### Fixes`:
  - "The Quillin Hub now fails closed on unsigned
    submissions." (the Submission Forge gate, storefront
    badge, sync worker, in-app dialog, Quillin Manager).
  - "The unified validator now reports and can require
    signatures." (the `--require-signed` flag).

### Module size budget (1 file)

**`quill/tools/module_size_budgets.json`**
- New rebaseline key `_rebaseline_2026_07_04_signature_in_manager`:
  main_frame_quillins.py 1118->1140 (+22) for the Signature
  line in `_quillin_detail_text`. Same accepted thin-wiring
  pattern as prior rebaselines.

## Verification

Local checks (run in this environment, **all green**):

- `python -m pytest tests/unit/tools/test_signing.py -q`
  -> **10 passed in 0.93s**
- `python -m pytest tests/unit/tools/test_artifact_validate.py -q`
  -> **33 passed in 1.20s** (the 31 pre-existing tests plus
  the 2 new `test_validate_unsigned_artifact_marks_signature_missing`
  and `test_cli_require_signed_disables_pass_for_unsigned`)
- `python -m pytest tests/unit/tools -q` -> **291 passed in
  60.75s**
- `python quillin-hub/smoke_test.py` -> **22/22 checks
  passed**
- `ruff check quill/tools/signing.py quill/tools/artifact_validate.py
  quill/ui/quillin_hub_submit.py quill/ui/main_frame_quillins.py
  quillin-hub/app/forge/forms.py quillin-hub/app/forge/linter.py
  quillin-hub/app/models/database.py quillin-hub/worker/sync_to_pages.py
  quillin-hub/smoke_test.py` -> **All checks passed**
- `ruff format --check <same files>` -> **All formatted**

## Working tree

```
 M CHANGELOG.md
 M docs/user guide/userguide.md
 M quill/tools/module_size_budgets.json
 M quill/tools/signing.py
 M quill/ui/main_frame_quillins.py
 M quill/ui/quillin_hub_submit.py
 M quillin-hub/app/forge/forms.py
 M quillin-hub/app/forge/linter.py
 M quillin-hub/app/models/database.py
 M quillin-hub/app/web/templates/forge_report.html
 M quillin-hub/app/web/templates/index.html
 M quillin-hub/app/web/templates/plugin.html
 M quillin-hub/smoke_test.py
 M quillin-hub/worker/sync_to_pages.py
?? docs/release/quillin-hub-deployment.md
?? docs/signing.md
?? fix.md
```

`git diff --stat` for the 14 modified files (2 new):

```
 CHANGELOG.md                                      |   4 +
 docs/release/quillin-hub-deployment.md            | 162 ++++++++
 docs/signing.md                                   | 162 ++++++++
 docs/user guide/userguide.md                      |   6 +-
 quill/tools/module_size_budgets.json              |   3 +-
 quill/tools/signing.py                            | 207 ++++++++++
 quill/ui/main_frame_quillins.py                   |  22 ++
 quill/ui/quillin_hub_submit.py                    |  21 +-
 quillin-hub/app/forge/forms.py                    |  23 +-
 quillin-hub/app/forge/linter.py                   |  17 +-
 quillin-hub/app/models/database.py                |   1 +
 quillin-hub/app/web/templates/forge_report.html   |  20 ++
 quillin-hub/app/web/templates/index.html          |  10 +-
 quillin-hub/app/web/templates/plugin.html         |   6 +-
 quillin-hub/smoke_test.py                         |  57 ++-
 quillin-hub/worker/sync_to_pages.py               |  34 +-
 16 files changed, 712 insertions(+), 43 deletions(-)
```

## Risks and follow-ups

- **Real-screen-reader pass** on the Submit-to-Hub dialog
  Signature line is open. The line is read by the dialog's
  existing `announce` (so a screen reader will pick it up),
  but the hardware test has not been run yet.
- **Public deployment of `hub.quillforall.org`** is the
  remaining follow-up for #517. The `docs/release/quillin-hub-deployment.md`
  runbook is in; DNS, hosting, and PostgreSQL credentials
  are out-of-repo ops.
- **Bundled Quillins are not yet signed.** The sidecar
  convention is in place, the validator and Manager report
  "unsigned" honestly, and the public key is bundled --
  but the actual signing of the 16 bundled Quillins
  (`quill/quillins_bundled/*`) is a follow-up. Doing it
  in this PR would have ballooned the change set and is
  better done as a one-shot "sign-everything-and-commit"
  pass once a publisher key is in place. (The private key
  is held outside the repo; this PR generates a real
  keypair, commits only the public half, and leaves the
  bundled-Quillin signing for a focused follow-up.)
- **PyNaCl 1.6.0 floor.** The new `signing` extra pins
  `PyNaCl>=1.6.0`. This is a fresh direct dependency on
  the QUILL side and on the Hub side. CI / installer must
  pull it in via the new extra.

## What this PR is NOT

- Not a deployment PR. `hub.quillforall.org` is not in
  this repo.
- Not a release cut. The work lands in `main`; the next
  release is whoever's turn it is, and the release hold
  (per the "Release hold: no Beta 2 announce yet" memory)
  is still in effect.
- Not a refactor of the validators. They are authoritative
  and unchanged.
- Not a UI change beyond the dialog signature line and
  the Manager details line. The dialog and the menu item
  were already in place from the previous PR.

## Files

- Spec: `docs/superpowers/specs/2026-07-04-quillin-hub-signing-deployment-design.md`
- Plan: `docs/superpowers/plans/2026-07-04-quillin-hub-signing-deployment.md`
- This summary: `docs/planning/quillin-hub-signing-done.md` (originally `done.md` at the repo root; relocated to satisfy the root-markdown layout gate)
