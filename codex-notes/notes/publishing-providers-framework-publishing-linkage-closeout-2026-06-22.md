# Publishing Providers Framework Linkage Registry Closeout

## Outcome

The durable, file-path-keyed publishing linkage registry is complete. This
resolves the first of the two decisions left explicitly open when the
publishing-providers-framework roadmap closed on 2026-06-21. A previously
linked, previously saved publishing document now keeps its Compare/Update/
Schedule link after being closed and reopened, or after the app restarts —
not just for the life of the open tab.

## Why This Was Needed

The compare-with-remote phase (2026-06-21) deliberately scoped to the open
tab's in-memory `Document.source_metadata` and deferred persistence, after
confirming `quill/io/export.py` never serializes `source_metadata` on save
and `quill/io/open_read.py` rebuilds it fresh from file-format detection on
every reopen. That left a real gap: close and reopen a `.md` file that was
linked to a WordPress post, and Compare/Update/Schedule all refuse to act
("Open remote publishing content before...") until the user re-browses and
re-links, even though the file on disk is unchanged.

## What Was Built

- `quill/core/publishing_linkage.py` (new): a path-keyed JSON store at
  `app_data_dir() / "publishing-linkage.json"`, following the exact pattern
  already established by `publishing-connections.json` in
  `quill/core/publishing.py` — `read_json`/`write_json_atomic`, defensive
  `isinstance` checks at every level of the loaded JSON so a corrupt file
  degrades to an empty registry rather than raising. `PublishingLinkageEntry`
  is a frozen dataclass holding the ten `publishing_*` fields. Two converter
  functions, `publishing_linkage_from_source_metadata` and
  `apply_publishing_linkage_to_source_metadata`, round-trip against
  `Document.source_metadata` without ever touching unrelated keys already in
  that dict (CSV/Word open-mode flags, engine names, etc.).
- `MainFrame._sync_publishing_linkage_for_document` (`quill/ui/main_frame.py`):
  the one helper every write path calls. It is called from
  `_write_document_to_disk` (the save chokepoint reached by both `save_file`
  and `save_file_as`) and from all three handlers that refresh publishing
  metadata after a successful network round trip:
  `_send_publishing_remote_item`, the schedule-publish handler, and the
  create-draft/publish-now handler. The latter two were not in the original
  plan — they were discovered while implementing, since they mutate
  `source_metadata` via the identical `publishing_status`/`publishing_updated_at`/
  `publishing_remote_url`/`publishing_remote_title` pattern as the handler
  that *was* planned, and adding them keeps scheduling and creating a new
  remote item from an already-saved local file just as durable as updating
  one.
- `_finish_open_document` looks up the registry by `selected_path` and, on a
  hit, merges the entry into the freshly-read document's `source_metadata`
  before either the new-tab or the refresh-existing branch runs — so a
  reopen, and `_reload_in_place`'s Save-As-then-reload-in-matching-view flow,
  both restore the link identically.

## Deliberate Scope Boundary

`_sync_publishing_linkage_for_document` skips two cases entirely, by design:

- **Untitled documents** (`document.path is None`): never registered. The
  first registry write happens only when the user actually saves the
  document somewhere; browsing and opening a remote item alone does not
  create an entry.
- **CSV grid and Word structured surfaces** (`CsvGridSurface`,
  `WordDocumentSurface`): Compare/Update/Schedule have only ever read
  `self.editor.GetValue()` as markdown/HTML text, a shape those structured
  surfaces were never designed to produce. Without this exclusion, saving a
  previously-linked document as `.docx` and reopening it could have restored
  `source_kind="publishing_remote"` onto a Word tab for the first time ever
  (today this configuration is structurally impossible, since Browse always
  creates a plain-surface document). Excluding it at the write site means it
  can never be wrongly restored at the read site either — no read-side
  guard was needed.

No explicit "unlink" command, no new feature flag, no network egress audit
change, and no dialog/dialog-inventory change: this is pure persistence
plumbing behind commands that already exist, with no new user-facing
surface. Stale entries (file deleted, remote item deleted) are inert dead
weight, not validated against on read — Compare already surfaces remote-side
problems when invoked.

## A Real Bug Caught Mid-Implementation

The first version of `_sync_publishing_linkage_for_document` used bare
`self.editor`/`document.source_metadata` attribute access. That broke an
existing characterization test,
`test_main_frame_cq16_characterization.py::test_write_document_to_disk_routes_rtf_through_the_rtf_writer`,
which calls `_write_document_to_disk` against a bare `MainFrame.__new__()`
test double (no `editor` attribute) and a `SimpleNamespace(path=...)`
document (no `source_metadata` attribute) — that test module's own stated
convention is to stub only the attributes each method actually touches at
the time the test was written. Fixed by rewriting the helper to be fully
`getattr`-defensive: it checks that `source_metadata` is a dict before
doing anything else, so the overwhelmingly common non-publishing-document
save path never touches `self.editor` at all. This matches the pre-existing
defensive style already used a few lines above in the same function for
`self.settings` (`getattr(getattr(self, "settings", None), ...)`).

## Validation Methodology Finding

This slice's full-suite comparisons used pytest's *default* temp directory,
not a custom `--basetemp`. Every full-suite baseline recorded by the four
earlier phases in this roadmap (`...,66 failed,...`) was validated with
`--basetemp=.tmp\pytest-<slice>-full` — a path under the repository and
therefore outside `Path.home()`. `quill/core/paths.py`'s H-1-core guard
(`_is_constrained_to_home`) silently rejects a `QUILL_DATA_DIR` override
that isn't under home, so any test depending on the shared `quill_data_dir`
conftest fixture (which does not itself override `Path.home`) would have
silently lost isolation under those custom basetemps and fallen through to
the *real* `%APPDATA%\Quill` directory. A `git stash`/clean-tree comparison
run independently in this slice confirms the true pre-existing baseline is
`19 failed` — identical failure names with and without this slice's
changes, none publishing-, document-, or export/open_read-related — not the
`66` recorded in every earlier phase's notes. This is not retroactively
corrected in those earlier notes (out of scope, and the conclusions in them
were not affected — none of those failures were ever publishing-related
either). Flagging it here so a future session does not mistake `66` for
ground truth, and does not repeat the custom-basetemp-outside-home pattern
for any test that depends on `QUILL_DATA_DIR` isolation.

One concrete, harmless side effect surfaced by this discovery: this slice's
own first (buggy) test run, before its own fixture was fixed to override
`Path.home()` defensively, wrote one bogus entry into the real
`%APPDATA%\Roaming\Quill\publishing-linkage.json` on the development
machine. The user was asked directly and chose to leave it as-is (it is
harmless fabricated test data, not real application data, and the sandbox's
auto-mode classifier correctly declined to let it be deleted automatically
since the path is outside the repository).

## Acceptance Evidence

- `tests/unit/core/test_publishing_linkage.py` (16 tests): round-trip
  save/load, path canonicalization via `.resolve()`, overwrite semantics,
  no-op removal of an unknown path, corrupt/malformed JSON degrading to an
  empty registry rather than raising, and both converter functions tested
  independently and round-tripped together.
- `tests/unit/ui/test_main_frame.py` (4 new static-source tests): the save
  chokepoint calls the sync helper; the helper excludes structured
  surfaces; `_finish_open_document` restores from the registry; all three
  publish-success handlers call the sync helper (asserted via an exact
  occurrence count).
- Full battery: `77 passed` (linkage core tests, publishing/compare core
  tests, all of `test_main_frame.py` including the CQ-16 characterization
  suite, module-size budget tests).
- Ruff and `ruff format --check`: passed.
- Scoped `mypy quill/core quill/io`: unchanged — same 7 pre-existing,
  unrelated findings (6 in `brf_page_detection.py`, 1 in
  `publishing_validation.py`) as every prior phase in this roadmap.
- Full unit suite: `4167 passed, 19 failed, 14 skipped`. Clean-tree
  comparison (`git stash`/`git stash pop` around the full suite run)
  independently confirms the same 19 failures at `4147 passed` with this
  slice's changes entirely removed — proving zero regressions and that the
  +20 passing delta is exactly the new tests this slice added.
- `quill/ui/main_frame.py` measured at 25165 lines; module-size budget
  rebaselined 25127->25165 with a dated `_rebaseline_2026_06_22_publishing_linkage`
  entry recording exactly why.

## Commits

Two local checkpoints on `feature/publishing-providers-framework`: core
(the new registry module and its tests), then UI integration (the three
`main_frame.py` call sites, their tests, and the module-size budget bump).
Not pushed, pending explicit request, per the standing repo convention.

## What's Actually Done And What Isn't

Done: linkage now survives save → close → reopen → app restart for any
publishing-linked document that has been saved to a plain-surface local
file (markdown, HTML, plain text, RTF). Not done, and out of scope for this
slice: any UI to inspect, browse, or manually unlink registry entries; any
validation of a registry entry against the actual remote state at open
time (Compare already exists for that, on request); any handling of a
moved or renamed local file (a path-keyed registry has no way to follow a
rename — the old entry simply becomes inert).

**One decision remains explicitly open** for the user or product owner,
unchanged from the roadmap closeout: whether and when to loosen
`core.third_party_plugins`/SEC-8 for real third-party Quillin or
publishing-provider execution, and if so, what signing/review/sandboxing
process (SEC-8's own stated prerequisite) should gate it.
