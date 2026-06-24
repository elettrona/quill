# Publishing Providers Framework Schedule-Publishing Closeout

## Outcome

The schedule-publishing roadmap phase is complete. WordPress can now schedule
either a new post/page from the current document or an already-open remote
item, behind one provider-neutral command/menu entry and one accessible
dialog. This phase was continued in Claude Code from a Codex-authored restart
prompt; the prompt's Codex-specific `apply_patch` tooling-blocker section did
not apply (no sandboxed patch helper in this tool) and was dropped, while the
repository-state verification, phase scope, acceptance contract, and
implementation order carried over unchanged.

## Acceptance Evidence

- `PUBLISHING_OPERATION_SCHEDULE` is a real provider operation; WordPress
  implements it through the existing shared `PUBLISHING_OPERATIONS` tuple,
  with no provider-specific shell assumptions.
- `validate_scheduled_publish_time` rejects timezone-naive values and values
  that are not strictly in the future, and is exercised directly by both
  core action functions and the dialog before any network call.
- `create_publishing_remote_item`/`update_publishing_remote_item` cover both
  the new-document and already-open-remote-item paths through one additional
  optional parameter, preserving the existing provider-neutral function
  shapes rather than adding a parallel "schedule" action function.
- WordPress sends `status="future"` and an explicit UTC `date_gmt`; the
  provider's returned `date_gmt` is round-tripped honestly into
  `PublishingRemoteDocument.scheduled_for` and surfaced in the result message
  and updated document metadata.
- `SchedulePublishDialog` uses only standard accessible wx controls
  (`TextCtrl`, `Choice`, `StaticText`), the repository's `apply_modal_ids`/
  `show_modal_dialog` contract, immediate label-control pairing, and
  re-validates instead of closing silently on bad input.
- The handler runs a plain-language, explicit review-first confirmation
  naming the target site, title, scheduled time, and authoring surface
  before any network request, matching the existing publish-now/update
  confirmation idiom.
- Unsupported providers and invalid/past times are reported through the
  same honest, specific error-message path as every other publishing action
  — no generic failure string.
- No timers, polling, recurring automation, or delayed Quill-side execution
  were added; the provider does the scheduling, not Quill.

## Closeout Validation

- core-focused battery: `61 passed`
- combined publishing/accessibility/governance battery: `153 passed`
- Ruff: passed
- provider registry gate: passed
- scoped `mypy quill/core quill/io`: unchanged from before this slice (6
  pre-existing `brf_page_detection.py` findings, 1 pre-existing
  `publishing_validation.py` finding in code this slice did not touch)
- full unit suite: `4074 passed, 66 failed, 14 skipped` — the 66 failures are
  the identical pre-existing set from the recorded `4056 passed, 66 failed,
  14 skipped` baseline; the +18 passing delta is exactly the new tests added
  in this slice

## Commits

Two local checkpoints on `feature/publishing-providers-framework`:

1. Core: schedule operation, validation module, client/payload extension.
2. UI + governance: `SchedulePublishDialog`, menu/command/handler wiring,
   dialog inventory, `dialogs.md`, module-size budgets, network-egress
   audit wording.

Not pushed — per this session's explicit instruction, matching the repo's
standing "commit locally; do not push unless explicitly requested"
convention.

## Authorization And Next Order

The 2026-06-20 Phase 1 closeout authorized schedule publishing,
local-versus-remote compare/sync, Quillin worker execution, and live
third-party provider loading to proceed in separately reviewable slices.
Schedule publishing is now closed. Continue in roadmap order:

1. local-versus-remote compare and the first honest sync model
2. Quillin worker execution boundaries and lifecycle behavior
3. live third-party provider loading, last, with SEC-8, consent,
   validation, and network-capability requirements reviewed before exposure

This closeout does not waive security, accessibility, validation, or
explicit-user-action requirements for later phases.
