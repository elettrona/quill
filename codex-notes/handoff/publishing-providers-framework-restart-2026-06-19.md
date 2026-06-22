# Publishing Providers Framework Restart Handoff

## Branch And Baseline

- repository: `C:\code\git-src\quill`
- branch: `feature/publishing-providers-framework`
- upstream tracking branch: `origin/feature/publishing-providers-framework`
- baseline before Phase 1 slice A: `5181feb9`

## Implemented State

- `quill/core/publishing_adapters.py` defines the trusted bundled adapter.
- `quill/core/publishing_bundled/wordpress.py` returns a package-shaped
  WordPress adapter using existing registry objects.
- `tests/unit/core/test_publishing_adapters.py` covers successful WordPress
  adaptation and pre-exposure rejection of invalid shapes.
- User-visible publishing behavior is unchanged.

## Validation

- focused adapter/publishing/provider-gate battery: `34 passed in 0.69s`
- Ruff: passed
- `python -m quill.tools.check_publishing_providers`: passed

## Resume Boundary

Continue Phase 1 only. The next decision is whether WordPress should bootstrap
through the bundled adapter during normal app startup. Preserve existing
provider/client identity and behavior if implementing that slice.

Do not begin schedule publish, compare/sync, Quillin worker execution, or live
third-party provider loading unless the user explicitly expands scope.

## 2026-06-20 Phase 1 Slice B Handoff

- Merged `origin/main` at `3df921ea` in merge commit `a3bec29`.
- Normal startup now calls `bootstrap_bundled_publishing_providers()` before importing the UI.
- The explicit bootstrap registers WordPress through its bundled adapter while preserving the existing definition and client objects.
- Implementation commit: `90a3f6e`.

Validation:

- focused merge-resolution battery: `149 passed`
- focused publishing/startup/registry/size battery: `77 passed`
- Ruff: passed
- provider registry gate: passed
- full unit suite: `4056 passed, 66 failed, 14 skipped`; no publishing, adapter, startup, size-budget, or provider-gate failures
- remaining full-suite failures are outside this slice and include current-main repository inconsistencies and state-sensitive fixtures

Going forward, every Phase 1 slice must run focused publishing tests, relevant new unit tests, Ruff, the provider registry gate, and the full unit suite with a workspace-local temporary directory. Record both passes and unrelated baseline failures.

Resume inside Phase 1 only. Do not begin schedule publish, compare/sync, Quillin worker execution, or live third-party loading without explicit approval.

## 2026-06-20 Phase 1 Closeout Handoff

Phase 1 is complete. The WordPress bundled-provider adapter contract and normal startup bootstrap passed closeout with `77 passed`, Ruff, the module-size gate, and the provider registry gate. The closeout is documentation-only.

The user explicitly approved schedule publishing, compare/sync, Quillin worker execution, and live third-party provider loading after this audit. Begin the next chat by verifying the clean pushed branch and reviewing the closeout note. The next roadmap phase is schedule publishing; keep it separate from compare/sync, worker execution, and third-party loading.

## 2026-06-21 Schedule Publishing Handoff

Implemented in Claude Code (the restart prompt for this phase was originally written for Codex; its `apply_patch` tooling-blocker section was dropped as not applicable, everything else carried over unchanged). Before implementing, `origin/main` was found one unrelated commit ahead of what the restart prompt assumed (`34e85556`, macOS DMG packaging) and was merged into the branch.

Implemented state:

- `quill/core/publishing_providers.py` defines `PUBLISHING_OPERATION_SCHEDULE`.
- `quill/core/publishing_schedule.py` defines `validate_scheduled_publish_time`.
- `quill/core/publishing.py`'s `create_publishing_remote_item`/`update_publishing_remote_item` accept an optional `scheduled_at` parameter; no new top-level action function was added.
- `quill/core/publishing_clients.py`'s `PublishingProviderClient` protocol and `WordPressPublishingClient` accept the same `scheduled_at` parameter; WordPress sends `status="future"` plus a UTC `date_gmt`, and `PublishingRemoteDocument` gained a `scheduled_for` field populated from the response.
- `quill/ui/publishing_tools.py` defines `SchedulePublishDialog`.
- `quill/ui/main_frame_menu.py` and `quill/ui/main_frame.py` wire `publishing.schedule_publish` as a command, `File > Publish > Schedule Publish...` menu item, and `_schedule_publishing_publish` handler.

Validation: focused core (`61 passed`), combined publishing/accessibility/governance battery (`153 passed`), Ruff, provider registry gate, and a full-suite run (`4074 passed, 66 failed, 14 skipped`) — the 66 failures match the pre-existing baseline exactly; no regressions.

Committed locally in two checkpoints (core, then UI+governance); the user then explicitly asked for these to be pushed, which was done (`af28e198`). A subsequent push returned a GitHub "repository moved" notice; `origin` was updated to `https://github.com/Community-Access/quill.git` (see `codex-handoff.md`, 2026-06-21 entry).

## 2026-06-21 Compare With Remote Handoff

Continued in the same session as the schedule-publishing work. Implemented the local-versus-remote compare phase as the smallest slice satisfying the Phase 3 "Initial slices" list, after confirming `Document.source_metadata` does not survive a local save-and-reopen cycle (`quill/io/export.py` never serializes it; `quill/io/open_read.py` rebuilds it fresh on open). Decision: compare against the open tab's `source_metadata` only for this slice; the durable file-path-keyed linkage registry from this plan's "Remote identity" section remains explicitly deferred, not built.

Implemented state:

- `quill/core/publishing_compare.py` defines `PublishingComparison` and `build_publishing_comparison`.
- `quill/core/publishing.py`'s `compare_publishing_remote_item` delegates entirely to the existing `load_publishing_remote_item` (no new provider operation, no new client method) and `publishing_comparison_message` formats the plain-language report.
- `quill/core/feature_command_map.py` maps `publishing.compare_remote_item` to `future.publishing`.
- `quill/ui/main_frame_menu.py` and `quill/ui/main_frame.py` wire the command, a `File > Publish > Compare With Remote...` menu item ahead of `Update Remote Content...`, and the `_compare_publishing_remote_item` handler, which reuses the existing connection-match guards and the existing native message-box reporting pattern — no new dialog surface was added.

Validation: focused battery (`86 passed`), Ruff, the provider registry gate, and a full-suite run (`4083 passed, 66 failed, 14 skipped`) — the 66 failures match the pre-existing baseline exactly; no regressions.

Committed locally in two checkpoints (core, then UI+governance); the user then explicitly asked for these to be pushed, which was done (`c8ed954e`), pushing cleanly to the corrected `https://github.com/Community-Access/quill.git` remote.

## 2026-06-21 Quillin Worker Execution Boundaries Handoff

Continued in the same session. Before planning, researched QUILL's Quillin/extension architecture directly (two parallel Explore agents) since the phase name implied touching the sandboxing model: confirmed Quillins already run via subprocess isolation (`quill/core/quillins/host.py` + `host_worker.py` for Python, `quill/core/ai/external_engine.py` for Node) with capability/consent gating, but none of it is reusable for publishing providers without new provider-specific IPC work — and there's no untrusted provider yet to justify building it, since SEC-8 keeps third-party discovery locked off regardless. Presented the user three explicit scope options; they picked "lifecycle behavior now, real boundary deferred" (the recommended option).

Implemented state:

- `quill/core/publishing_providers.py` defines `PublishingOperationCancelled`.
- `quill/core/publishing.py`'s `browse_publishing_content` and `quill/core/publishing_clients.py`'s `PublishingProviderClient.browse_content`/`WordPressPublishingClient.browse_content` accept an `is_cancelled` callable, checked between per-content-kind requests.
- New `quill/core/publishing_worker.py` (`browse_publishing_content_task`) is the sole bridge from `quill.core.publishing` to `quill.stability.task_manager` — `publishing.py` itself stays decoupled from the stability layer.
- `quill/ui/publishing_tools.py`'s `BrowsePublishingContentDialog` now requires a `task_manager` constructor parameter, dispatches loads through it with a real Cancel button, and ignores stale callbacks via an operation-id + `_destroyed` guard. `quill/ui/main_frame.py` threads `self._task_manager` through.
- `quill/core/publishing_adapters.py` gained `WORKER_EXECUTION = "worker"`, explicitly rejected with a distinct "not implemented yet" message.

Validation: focused battery (`97 passed`), dialog governance gates (`44 passed`), Ruff, mypy, the provider registry gate, and a full-suite run (`4093 passed, 66 failed, 14 skipped`) — the 66 failures match the pre-existing baseline exactly. Smoke-launched the app to confirm no startup traceback; could not interactively click through Browse/Cancel (no pywinauto, no project run-skill for this wx app) — recorded honestly as a verification gap rather than claimed as tested.

Committed locally in two checkpoints (core, then UI+governance); **not pushed** pending explicit request. Resume by verifying local branch state before continuing into the final roadmap phase: live third-party provider loading.