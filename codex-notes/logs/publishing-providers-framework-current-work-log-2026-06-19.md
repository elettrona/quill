# Publishing Providers Framework Current Work Log

## Phase 1 Slice A

Reviewed the canonical planning, readiness, follow-up, extraction, handoff, and
review-log records before implementation.

Work completed:

- added an immutable adapter contract joining provider metadata and client
- made registry contribution explicit and package-facing
- rejected mismatched ids before registry mutation
- pinned host-owned secret access and trusted in-process execution
- required a plain network-capability rationale
- added a WordPress bundled package module wrapping existing runtime objects
- avoided shell, menu, dialog, credential, and publishing workflow changes

Validation history:

- all five new adapter tests passed on the first focused run
- four existing publishing tests initially errored because `.tmp` did not exist
- created the test-only parent and reran the complete focused command
- final focused result: `34 passed in 0.69s`
- Ruff passed
- provider registry gate passed
- removed the test-only `.tmp` directory

No Phase 2, Phase 3, or Phase 4 work was performed.

## 2026-06-20 - Main Merge And Phase 1 Slice B

- fetched current `origin/main` at `3df921ea`
- resolved four merge conflicts while preserving both publishing work and main behavior
- rebaselined merge-only module budgets and regenerated the combined MainFrame public surface
- committed the merge as `a3bec29`
- decided normal startup should exercise the trusted bundled-provider contract
- added explicit bundled-provider bootstrap before UI import
- proved WordPress definition/client identity and repeat-bootstrap behavior
- committed the slice as `90a3f6e`

Validation:

- merge-focused: `149 passed`
- slice-focused: `77 passed`
- Ruff: passed
- provider registry gate: passed
- final full unit suite: `4056 passed, 66 failed, 14 skipped`
- full-suite failures were outside publishing/startup; examples include current-main planning-doc/version-gate inconsistencies and state-sensitive fixtures

Validation policy now recorded: every next slice runs focused publishing tests, relevant unit tests, Ruff, registry gate, and the full suite with local temp state.

No schedule publish, compare/sync, worker execution, or live third-party loading work was performed.

## 2026-06-20 - Phase 1 Closeout Audit

- confirmed the branch was clean and synchronized at `630a41fa`
- audited adapter validation, WordPress package shape, startup bootstrap, identity preservation, and deliberate security/runtime boundaries
- found no remaining Phase 1 acceptance gap
- ran the focused closeout battery: `77 passed`
- ran Ruff: passed
- ran the module-size gate: passed
- ran the provider registry gate: passed
- changed documentation only; no product runtime behavior changed
- recorded the user's explicit post-closeout authorization for schedule publishing, compare/sync, Quillin worker execution, and live third-party loading

Phase 1 is closed. The next roadmap phase is schedule publishing.

## 2026-06-21 - Schedule Publishing Implementation

Continued in Claude Code from the Codex restart prompt for this phase; the prompt's Codex `apply_patch` tooling-blocker section did not apply (no sandboxed patch helper in this tool) and was dropped, everything else carried over. Verified repository state first: `origin/main` had advanced one unrelated commit (macOS DMG packaging fix, `34e85556`) past what the restart prompt assumed; merged it into the branch before starting.

Work completed in two commits:

- Core checkpoint: `PUBLISHING_OPERATION_SCHEDULE`; new `quill/core/publishing_schedule.py` (`validate_scheduled_publish_time`); `scheduled_at` parameter added to the `PublishingProviderClient` protocol, the WordPress client (`date_gmt` payload field, `_fields` query param, `scheduled_for` response field), and to `create_publishing_remote_item`/`update_publishing_remote_item`; `publishing_result_message`/`_display_status` extended for the `"scheduled"`/`"future"` case; `PUBLISHING_OPERATION_SCHEDULE` added to the provider/client operation-method validation map; `tzdata` added as a base dependency. New tests: `tests/unit/core/test_publishing_schedule.py` (5 tests) plus 5 new WordPress-payload tests and one unsupported-provider gating test added to the existing `test_publishing_browse.py`/`test_publishing.py` files; 3 pre-existing endpoint-URL assertions updated for the new `date_gmt` `_fields` entry.
- UI + governance checkpoint: `SchedulePublishDialog` in `quill/ui/publishing_tools.py` (date/time `TextCtrl`, IANA timezone `Choice` defaulting to UTC, content-kind `Choice`/`StaticText` depending on context, validate-and-reopen loop); menu id/item/binding and command registration for `publishing.schedule_publish`; `_schedule_publishing_publish` handler in `main_frame.py` covering both new-document and already-open-remote-item scheduling with the same review-first confirmation idiom as the existing publish/update actions. Regenerated `dialog_inventory.json`; added the dialog to `dialogs.md`; bumped `module_size_budgets.json` for the five files that grew, with a dated rebaseline comment; widened the `_request_json` network-egress rationale to cover create/update/schedule (it previously only mentioned browse/open, which was already stale before this change). New test file `test_schedule_publish_dialog_a11y.py` (8 tests); extended `test_main_frame_menu_contract.py`'s publishing menu assertion.

Validation:

- core-focused: `61 passed`
- combined publishing/accessibility/governance battery: `153 passed`
- Ruff: passed (both checkpoints)
- provider registry gate: passed
- scoped `mypy quill/core quill/io`: same 7 pre-existing findings as before this slice (6 in `brf_page_detection.py`, 1 in `publishing_validation.py`'s untouched `_extend_unknown_issues`), none introduced by this work
- full unit suite: `4074 passed, 66 failed, 14 skipped` — the 66 failures are the identical pre-existing set from the `4056 passed, 66 failed, 14 skipped` baseline; the +18 passing delta is exactly the new tests added in this slice

No compare/sync, Quillin worker execution, or live third-party loading work was performed. Committed locally as two checkpoints; not pushed (this session's explicit instruction, matching the standing repo convention).