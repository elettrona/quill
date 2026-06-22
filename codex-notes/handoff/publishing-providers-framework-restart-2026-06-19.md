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

Committed locally in two checkpoints (core, then UI+governance); **not pushed**, per this session's explicit instruction. Resume by verifying the local branch state (it will be ahead of `origin/feature/publishing-providers-framework`) before continuing into the next roadmap phase: local-versus-remote compare and the first honest sync model.