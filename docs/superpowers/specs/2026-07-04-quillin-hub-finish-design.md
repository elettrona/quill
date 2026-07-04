# Quillin Hub: finish, document, close #517 and #519

**Date:** 2026-07-04
**Scope:** Code cleanup, documentation, issue closures for the Quillin Hub
workstream in the main QUILL repository.
**Status:** Approved design (post brainstorming).

## Context

The Quillin Hub is the community store and submission service for every
shareable QUILL artifact type. The previous conversation left substantial
work in flight in this repository (modified files plus new modules). The
work is mostly complete: a unified validator, a Hub service in
`quillin-hub/`, an in-app `Submit to Quillin Hub...` command, the PRD §5.83a
section, a user guide section, and 31 passing unit tests. What remains is
the final pass: drop a stale path, fix one broken cross-reference, run
the smoke test, record the work in `CHANGELOG.md` and `docs/release/RELEASE.md`,
close the two tracking issues (#517, #519), and rewrite the legacy Hub
section in `docs/quillins/quillins.md` to point at the unified Hub rather
than the historical Quillin-only narrative.

This is the work for one PR, sized so a maintainer can review the diff in
one sitting and the in-app command and Hub service code share a single
shipped record.

## Goals

- One source of truth for the Quillin Hub in the user-facing docs:
  the unified Hub covers seven artifact types, the validator is
  `quill.tools.artifact_validate`, the in-app command is
  `Tools > Quillins > Submit to Quillin Hub...`, the publication path
  is GitHub PRs.
- `python quillin-hub/smoke_test.py` is green locally and the
  `tests/unit/tools/test_artifact_validate.py` suite stays green.
- `CHANGELOG.md` and `docs/release/RELEASE.md` reflect the work.
- Issue #517 is closed (Hub platform code shipped) with a clear note
  that public deployment is the open work and lives outside this repo.
- Issue #519 is closed (capability model documented) with a clear note
  that signing is the open work and is a 2.0 track.

## Non-goals

- Public deployment of the Hub (requires DNS, hosting, Postgres, GitHub
  org access — out of scope for this repo).
- Implementation of manifest signing (real engineering work; deferred
  to 2.0 per the answer to the clarification question).
- A new `docs/quillins/artifact-developer-guide.md` file (the user
  guide used to promise one; we are removing the promise instead of
  duplicating `quillins.md` content into a new file).
- A re-roll of the seven validator modules or the `quill/tools/`
  linter family. They are already authoritative and the smoke test
  plus the 31 unit tests cover them.
- A new release. The work lands in `main` and is recorded in the
  existing `## 0.9.0 Beta 1` section of `CHANGELOG.md` plus a note in
  the pre-tag checklist of `docs/release/RELEASE.md`. No version bump.

## Design

### Section 1 — Code cleanup

**`quillin-hub/worker/sync_to_pages.py`:**
- Drop `"examples/quillins"` from `_QUILLIN_ROOTS`; the directory does
  not exist in this repo and the worker emits a warning when it is
  missing. After the change, the worker only scans
  `quill/quillins_bundled`, which exists and has 16 Quillin directories
  (verified `ls quill/quillins_bundled`).
- Update the module docstring to add a single line right after the
  "Run as a cron job or worker" line: "Requires `GITHUB_TOKEN` in
  the environment; the worker uses the GitHub Contents API to
  enumerate the repo. Without a token, every API call returns 401
  immediately and no artifacts are synced."
- No changes to `_sync_skill_packs_in` or `_sync_agents` — both work
  with paths that exist.

**`quillin-hub/README.md`:**
- Update the "Registry sync worker" section to name the surviving root
  (`quill/quillins_bundled`) and drop the `examples/quillins` mention.
- Add a one-line cross-reference to
  `tests/unit/tools/test_artifact_validate.py` for the seven-type
  validator coverage.

**No other code changes.** The `quill/tools/artifact_validate.py`,
`quill/ui/quillin_hub_submit.py`, `quill/ui/main_frame_quillins.py`,
the dialog inventory fixture, the public-surface fixture, the
module-size budgets, the Hub service modules, the `quillin-hub/app/`
package, and the smoke test are all in their final state from the
previous session and are not touched in this PR.

### Section 2 — Documentation: one source of truth in `quillins.md`

**`docs/quillins/quillins.md`:**
- Update the file's lead-in line from "Consolidated on 2026-06-13 into
  one document." to "Consolidated on 2026-06-13, last refreshed
  2026-07-04 to point at the unified Quillin Hub."
- Replace lines 2684-2810 (the legacy "Quillin Hub: Community Plugin
  Store" / "Quillin Hub: Deployment & Integration Guide" sections)
  with a single fresh section titled "The Quillin Hub" that:
  - Names the seven artifact types in a table (matching the PRD §5.83a
    table: type id, label, format, authoritative validator)
  - Names `quill.tools.artifact_validate` as the single validation
    authority, with the CLI one-liner and a sentence on exit codes
  - Names the in-app command `Tools > Quillins > Submit to Quillin
    Hub...` and what it does
  - Names the publication path: a Hub submission is reviewed in the
    Hub's Submission Forge, then published via a GitHub pull request
  - Cross-references `docs/Product Requirement Documents and
    Specifications/QUILL-PRD.md` §5.83a and the user guide's "The
    Quillin Hub: sharing what you make" section
  - Replaces the broken link to
    `docs/quillins/artifact-developer-guide.md` with one sentence
    that says: "Per-type authoring is documented alongside the
    bundled Quillin that ships with each format. The seven types and
    their authoritative validators are listed in PRD §5.83a; the
    validator is one command, `python -m quill.tools.artifact_validate
    <path>`."
- The rewrite targets roughly 70-90 lines (the current section is
  127 lines; the new one is shorter because the per-type detail
  already lives in the PRD and the per-bundled-Quillin docs).

**`docs/user guide/userguide.md`:**
- Update the line that says "see `docs/quillins/artifact-developer-guide.md`
  for the developer guide" to instead say: "for the developer guide,
  see `docs/quillins/quillins.md` and PRD §5.83a — the seven artifact
  types and their authoritative validators are listed there, and
  `python -m quill.tools.artifact_validate <path>` runs the same
  checks the Hub runs on submission."

No other user-guide edits. The "Submit to Quillin Hub" section added by
the previous session is correct and stays.

### Section 3 — `CHANGELOG.md` and `docs/release/RELEASE.md`

**`CHANGELOG.md`:**
- Add a single paragraph at the end of the existing "What's New in
  this beta" list (the bullet section under `## 0.9.0 Beta 1`,
  before "A 'Notepad++ experiment' editor surface..."), titled
  "The Quillin Hub: share every QUILL artifact, validate locally
  first." The paragraph covers: seven artifact types, the in-app
  `Tools > Quillins > Submit to Quillin Hub...` command, the single
  validation authority, the GitHub-PR publication path. One
  paragraph, not a section. Tone matches the surrounding entries
  (one short headline line, then a sentence or two of plain
  language).
- The entry does not move the section; the section is already the
  0.9.0 Beta 1 changelog, and this is part of the 0.9.0 line.

**`docs/release/RELEASE.md`:**
- Add one bullet to the "Pre-tag checklist" section (after the
  existing bullets) reading: "**Quillin Hub service code shipped.**
  `quillin-hub/` is a Flask service in the same repo; the registry
  API, Submission Forge, sync worker, and smoke test are
  all in-tree. Public deployment (DNS, hosting, Postgres) is a
  separate ops track and is tracked separately from the release cut."

No structural changes to `RELEASE.md`.

### Section 4 — Issues #517 and #519

**`gh issue close 517 --reason "not planned"`** with a closing comment:

> Closing as the platform work is shipped. What landed: `quillin-hub/`
> Flask service (`app/`, `worker/`, `smoke_test.py`), the unified
> `quill.tools.artifact_validate` covering the seven artifact types
> (with 31 unit tests), the in-app `Tools > Quillins > Submit to
> Quillin Hub...` command and dialog, the PRD §5.83a section, the
> user-guide section, the registry API (`/api/v1/types`,
> `/api/v1/artifacts`, `/api/v1/artifacts/<id>/latest`), the
> Submission Forge, and the GitHub-token-based sync worker.
>
> What remains: public deployment of `hub.quillforall.org`. That
> requires DNS, hosting, Postgres credentials, and GitHub org access,
> all of which are out of this repo's scope. When public deployment
> is ready, file a new issue (or revive this one) with the ops
> checklist and target date. Re-open the platform items here only if
> the in-tree service code needs new functionality.

**`gh issue close 519 --reason "not planned"`** with a closing comment:

> Closing on the documentation acceptance. The capability model is
> documented in `docs/quillins/quillins.md` §6 (Security & consent
> model), §13 (Manifest JSON Schema), and §14 (Extension authoring
> reference, with the capability catalogue in §14.1 and the
> contribution reference in §14.2). The in-process Python snippet
> sandbox hardening (dunder-attribute block, separate-process
> isolation, import allowlist, scrubbed environment, time/memory
> caps) is documented in the 0.9.0 Beta 1 "Enhancements" section
> of `CHANGELOG.md`.
>
> What remains: manifest signing. A signed-manifest flow
> (publisher keypair, detached signature on every released
> artifact, install-time verification) is real engineering work and
> is deferred to QUILL 2.0 alongside the rest of the marketplace
> trust work. When 2.0 planning opens, file a real, scoped issue
> for the signing flow rather than re-opening this one.

Both closes use `--reason "not planned"` because the work that
*this* repo can ship is shipped, and the remaining work is either
ops (#517) or deferred to 2.0 (#519).

### Section 5 — Verification

Run, in order, from `S:/QUILL`:

1. `python -m pytest tests/unit/tools/test_artifact_validate.py -q`
   — expect `31 passed`.
2. `python quillin-hub/smoke_test.py` — expect a `/N passed` line
   and exit 0. (Already 100% pass per the previous session; this PR
   only removes a path the worker does not need.)
3. `python -m pytest tests/unit/ui -q` — sanity check that the
   `dialog_inventory.json` and `main_frame_public_surface.json`
   fixtures still match (no `quillin_hub_submit.py` is exercised
   here, but the public-surface test enumerates `open_hub_submission`).
4. `ruff check .` — expect clean.
5. `ruff format --check .` — expect clean.
6. `git diff --stat` — confirm the doc rewrites are the expected
   size (~70-90 lines in `quillins.md`, ~10 lines in the user
   guide, one paragraph in `CHANGELOG.md`, one bullet in
   `RELEASE.md`).
7. Manual review of the `quillins.md` rewrite to confirm the
   per-type detail is removed in favour of pointing at the PRD
   and the bundled Quillin docs.

No new tests are added in this scope. The 31 existing tests in
`tests/unit/tools/test_artifact_validate.py` cover the seven
types' detection, validation, and CLI; that is the validation
authority the Hub uses and the in-app command uses.

## Files to touch

Code:
- `quillin-hub/worker/sync_to_pages.py` (drop `examples/quillins`
  from `_QUILLIN_ROOTS`, tighten docstring)
- `quillin-hub/README.md` (sync section update)

Docs:
- `docs/quillins/quillins.md` (lead-in line + 127-line rewrite of
  the Hub section)
- `docs/user guide/userguide.md` (replace one broken link)
- `CHANGELOG.md` (one new paragraph under `## 0.9.0 Beta 1`)
- `docs/release/RELEASE.md` (one new bullet under "Pre-tag
  checklist")

Issues:
- Issue #517 closing comment + `gh issue close`
- Issue #519 closing comment + `gh issue close`

No code under `quill/`, no `quillin-hub/app/` changes, no test
changes, no module-size budget changes, no fixture changes.

## Risks

- The `quillins.md` rewrite is the largest single edit. The risk is
  that the rewrite accidentally removes the "Submit" step from
  §0a ("Implementation status (module map)") or other cross-
  references. Mitigation: the rewrite targets a known line range
  (2684-2810) and the cross-references are explicit; the diff will
  be reviewed.
- The user-guide link fix is a one-line change. Risk is low.
- The smoke test was previously green in the previous session. If
  it has regressed, the most likely cause is a missing import in
  the Hub's new templates; the smoke test exercises them.
- The CHANGELOG and RELEASE edits are additive (paragraph + bullet)
  and do not move existing content.
- The issue closes are unrecoverable: once closed with `not planned`,
  the work is "off the plate." Mitigation: the closing comments
  capture exactly what is shipped and what remains, so a future
  issue or re-open has the right context.

## What this PR is NOT

- Not a deployment PR. The Hub's public URL is not in this repo.
- Not a signing PR. #519 closes on documentation, not
  implementation.
- Not a refactor of the validators. They are authoritative.
- Not a release cut. The work lands in `main`; the next release is
  whoever's turn it is.
- Not a UI change. The dialog and menu are already in place from
  the previous session.
