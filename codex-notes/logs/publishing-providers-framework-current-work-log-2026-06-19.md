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

## 2026-06-21 - Compare With Remote Implementation

Continued in the same session immediately after the schedule-publishing phase, plus a small housekeeping detour: the next push returned a GitHub "repository moved" notice, so `origin` was updated to `https://github.com/Community-Access/quill.git` (recorded separately in `codex-handoff.md`) and the schedule-publishing checkpoints were pushed at the user's explicit request.

Before implementing, researched whether `Document.source_metadata` (the in-memory carrier of all `publishing_*` linkage fields) survives a local save-and-reopen cycle, since the phase's "Initial slices" list opens with "define remote identity/linkage source of truth." Confirmed via `quill/io/export.py` and `quill/io/open_read.py` that it does not — metadata is rebuilt from file-format detection on open, never serialized on save. Decided to scope this slice to the open tab's `source_metadata` as the linkage source of truth and explicitly defer the durable file-path-keyed registry, rather than build that larger, separable piece now.

Work completed in two commits:

- Core checkpoint: new `quill/core/publishing_compare.py` (`PublishingComparison` dataclass, `build_publishing_comparison`); `compare_publishing_remote_item` and `publishing_comparison_message` added to `quill/core/publishing.py`; `publishing.compare_remote_item` added to `feature_command_map.py`. New `tests/unit/core/test_publishing_compare.py` (6 tests) plus 3 new tests added to `test_publishing_browse.py` (no-difference, remote-changed, and load-failure-propagation cases against a fake WordPress response) and one command id added to both list-based assertions in `test_publishing_framework.py`.
- UI + governance checkpoint: menu id/item/binding for `publishing.compare_remote_item` placed ahead of `Update Remote Content...`; command registration; `_compare_publishing_remote_item` handler in `main_frame.py` reusing the exact connection-match guard logic already in the update/publish-remote handler. Extended `test_main_frame_menu_contract.py`'s publishing menu assertion. Bumped `module_size_budgets.json` for `publishing.py`/`main_frame.py`/`main_frame_menu.py` growth with a dated rebaseline comment. No dialog-inventory, `dialogs.md`, or network-egress-audit changes — no new dialog surface or network call site.

Validation:

- focused battery (core + menu contract + module-size + network-egress): `86 passed`
- Ruff: passed (both checkpoints)
- provider registry gate: passed
- scoped `mypy quill/core quill/io`: unchanged from before this slice (same 7 pre-existing findings)
- full unit suite: `4083 passed, 66 failed, 14 skipped` — identical pre-existing failure set; +9 passing delta matches the new tests added

No Quillin worker execution or live third-party loading work was performed. Committed locally as two checkpoints; not pushed pending explicit request.

## 2026-06-21 - Quillin Worker Execution Boundaries Implementation

User then asked to push the compare checkpoints (`c8ed954e` pushed cleanly to the corrected remote) and to continue with the next roadmap phase.

Researched QUILL's Quillin/extension architecture via two parallel Explore agents before planning, since this phase's name implied touching the sandboxing model directly: confirmed Quillins already run Python workers via `subprocess.Popen` (`quill/core/quillins/host.py` + `host_worker.py`, JSONL IPC) and Node workers via `quill/core/ai/external_engine.py`'s allowlisted subprocess runner, both with capability/consent gating — but none of this is reusable for publishing providers without new provider-specific IPC work, and there is no untrusted provider yet to justify building it (SEC-8 keeps third-party discovery locked off regardless of this phase). Also confirmed `quill.stability.task_manager.TaskManager` (verified exact class name by reading the file directly) already gives background dispatch + cooperative `CancellationToken` + UI-thread-marshalled callbacks, unused by publishing today.

Presented the user three explicit scope options (lifecycle behavior now/boundary deferred; build the real boundary now against a fake provider; skip straight to third-party loading) via AskUserQuestion; the user picked the first, recommended option.

Work completed in two commits:

- Core checkpoint: `PublishingOperationCancelled` (`quill/core/publishing_providers.py`); `is_cancelled` parameter added to `browse_publishing_content` (`publishing.py`) and to the `PublishingProviderClient.browse_content` Protocol + WordPress implementation (`publishing_clients.py`), checked between per-content-kind requests; new `quill/core/publishing_worker.py` (`browse_publishing_content_task`, the sole bridge to `quill.stability.task_manager`); `publishing_adapters.py` gained `WORKER_EXECUTION = "worker"` with its own "not implemented yet" rejection, distinct from the generic-rejection branch (required fixing one existing parametrized test that had used `"worker"` as its generic-rejection example). New `tests/unit/core/test_publishing_worker.py` (2 tests); 2 new cancellation tests added to `test_publishing_browse.py`; 1 new case added to `test_publishing_adapters.py`'s parametrize.
- UI + governance checkpoint: `BrowsePublishingContentDialog` (`quill/ui/publishing_tools.py`) now threads a required `task_manager` constructor parameter, gained a Cancel button, and dispatches `_on_load` through `task_manager.submit()` instead of blocking the UI thread; new `_on_cancel_load`/`_on_browse_task_success`/`_on_browse_task_failure` with an operation-id staleness guard and a `_destroyed` flag set in `show_modal()`'s teardown (which also best-effort-cancels any in-flight task). Did not touch the `wx.ID_CANCEL` Close button or Escape handling, per this repo's escape-trap governance tests. `main_frame.py`'s `_browse_publishing_content` now passes `self._task_manager`. New static source-inspection tests in `test_publishing_connection_dialog_a11y.py` (4 tests) and one in `test_main_frame.py`; bumped `module_size_budgets.json` for the three touched files.

Validation:

- focused battery (core + UI + module-size): `97 passed`
- dialog governance gates (inventory, banned-patterns, button contract, hardening, announce-gap): `44 passed`
- Ruff: passed (both checkpoints)
- provider registry gate: passed
- scoped `mypy quill/core quill/io`: unchanged from before this slice (same 7 pre-existing findings)
- full unit suite: `4093 passed, 66 failed, 14 skipped` — identical pre-existing failure set; +10 passing delta matches the new tests added
- smoke-launched `python -m quill` for ~12s: no startup traceback (only a benign unrelated lexicon-file stderr warning), confirming the new wiring doesn't break MainFrame construction. Could not interactively click through Browse → Load → Cancel: no pywinauto installed, no project run-skill exists for this wxPython desktop app. Recorded as a known verification gap rather than claimed as tested.

No live third-party provider loading work was performed. Committed locally as two checkpoints; not pushed pending explicit request.