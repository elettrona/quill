# Publishing Providers Framework Compare-With-Remote Closeout

## Outcome

The local-versus-remote compare roadmap phase is complete. Users can
request an honest, read-only comparison of an already-open remote
publishing item against its current remote state, without Quill ever
auto-merging, auto-overwriting, or silently syncing either side.

## Scope Decision: Linkage Source Of Truth

The phase's own "Initial slices" list (`publishing-follow-up-phases-2026-06-19.md`,
Phase 3) opens with "define remote identity/linkage source of truth."
Research before implementation confirmed `Document.source_metadata` — the
in-memory carrier of every `publishing_*` field — is never written to disk
by the save path (`quill/io/export.py`) and is rebuilt fresh from
file-format detection on reopen (`quill/io/open_read.py`). A durable,
file-path-keyed linkage registry (sketched in the original plan under
"Remote identity") would be needed to make compare/update survive closing
and reopening a locally-saved publishing document.

This phase deliberately scoped to the **open tab's `source_metadata`** as
the linkage source of truth and explicitly deferred the durable registry —
consistent with every prior phase deferring the same piece, and still
sufficient to satisfy the phase's actual "Done when" criteria. This is a
recorded decision, not a gap discovered by accident: if a future session
needs compare/update to work across app restarts for locally-saved
publishing documents, building that registry is the prerequisite, and it
does not exist yet.

## Acceptance Evidence

- `build_publishing_comparison` (`quill/core/publishing_compare.py`) is a
  pure function: title/body/status diffed field-by-field, plus a
  `remote_changed_since_last_known` signal from comparing the freshly
  fetched remote's `updated_at` against the open tab's cached
  `publishing_updated_at`.
- `compare_publishing_remote_item` reuses the existing
  `load_publishing_remote_item` for fetching and validation — no new
  provider operation, no new client method, no new network-egress call
  site. Comparing is honestly modeled as "load, then diff," not a new
  provider capability.
- `publishing_comparison_message` reports in plain language only: which
  fields match or differ, an explicit remote-changed warning only when
  true, and the remote link — no diff-algorithm output, no jargon.
- One command/menu entry (`publishing.compare_remote_item`, `File >
  Publish > Compare With Remote...`) covers the feature; the handler
  reuses the exact connection-match guard logic already in the
  update/publish-remote handler rather than inventing new wording.
- Reports through the existing native message-box pattern — zero new
  dialog-governance surface, zero `dialogs.md`/`dialog_inventory.json`
  changes.
- No automatic overwrite, merge, or background sync was added; the user
  acts afterward through the existing `Update Remote Content...` /
  `Publish Open Remote Content...` / re-browse-and-open actions.

## Closeout Validation

- focused battery (core + menu contract + module-size + network-egress
  gates): `86 passed`
- Ruff: passed
- provider registry gate: passed
- scoped `mypy quill/core quill/io`: unchanged from before this slice
  (same 7 pre-existing, unrelated findings)
- full unit suite: `4083 passed, 66 failed, 14 skipped` — the 66 failures
  are the identical pre-existing set; the +9 passing delta is exactly the
  new tests added in this slice

## Commits

Two local checkpoints on `feature/publishing-providers-framework`:

1. Core: `publishing_compare.py`, `compare_publishing_remote_item`,
   `publishing_comparison_message`, `feature_command_map.py` entry, tests.
2. UI + governance: menu/command/handler wiring, menu contract test,
   module-size budget bump.

Not pushed — pending explicit request, per the standing repo convention.

## Next Order

Per the 2026-06-20 Phase 1 closeout authorization: Quillin worker
execution boundaries and lifecycle behavior is next, then live
third-party provider loading last. Security, accessibility, validation,
and provider-neutrality requirements remain in force for both.
