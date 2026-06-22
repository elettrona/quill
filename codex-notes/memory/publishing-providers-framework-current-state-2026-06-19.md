# Publishing Providers Framework Current Memory

## Phase 1 Slice A Checkpoint

Branch: `feature/publishing-providers-framework`.

The trusted bundled-provider package contract now exists. WordPress can be
represented through `quill.core.publishing_bundled.wordpress` without replacing
its existing definition, client, commands, menus, dialogs, credentials, network
calls, or user-visible behavior.

Pinned contract decisions:

- adapter, definition, and client ids must match
- malformed adapters are rejected before registry exposure
- bundled providers must explain their network capability
- credentials remain host-owned
- only trusted in-process execution is accepted in this slice
- no package scanning or third-party runtime loading occurs

Validated with `34 passed in 0.69s`, Ruff, and a passing provider registry gate.

Implementation commits before the detailed documentation commit:

- `303a6f3` adapter contract
- `bddebe3` WordPress package-shape proof and tests
- `fce71c4` initial Phase 1 slice A records
- `858d4c8` formatter checkpoint

Resume inside Phase 1 only.

## Phase 1 Slice B Memory - 2026-06-20

`origin/main` at `3df921ea` was merged in `a3bec29`. WordPress now bootstraps through `bootstrap_bundled_publishing_providers()` during normal application startup, before the UI import. The bootstrap uses the existing WordPress definition and client objects, is safe to repeat, and adds no discovery, third-party loading, worker execution, credential change, or network action.

Implementation commit: `90a3f6e`. Focused validation passed with `77 passed`, Ruff, the module-size gate, and the provider registry gate. Final full-unit result was `4056 passed, 66 failed, 14 skipped`; none of the failures touched publishing or this startup slice.

Future slices must include and record focused tests, relevant new unit tests, Ruff, the provider registry gate, and a full unit run with workspace-local temporary state.

## Phase 1 Closeout Memory - 2026-06-20

The WordPress first-party bundled-provider package path is complete. The closeout audit passed with `77 passed`, Ruff, the module-size gate, and the provider registry gate. No product code changed during closeout.

The user explicitly authorized schedule publishing, compare/sync, Quillin worker execution, and live third-party loading after closeout. The next planned phase is schedule publishing. Preserve the existing security, consent, accessibility, provider-neutrality, and validation contracts.

## Schedule Publishing Memory - 2026-06-21

Schedule publishing is implemented and complete. `PUBLISHING_OPERATION_SCHEDULE` exists; WordPress gets it for free through the shared `PUBLISHING_OPERATIONS` tuple. `quill.core.publishing_schedule.validate_scheduled_publish_time` is the timezone-aware validation model — a plain tz-aware `datetime` is the value type, deliberately not wrapped in a new dataclass. `create_publishing_remote_item`/`update_publishing_remote_item` grew an optional `scheduled_at` parameter rather than a new function; when set, status becomes `"future"` and WordPress sends an explicit UTC `date_gmt`, round-tripped back as `PublishingRemoteDocument.scheduled_for`. The UI adds one dialog (`SchedulePublishDialog`, accessible date/time/timezone/content-kind controls, re-validates instead of closing on bad input) and one command/menu entry (`publishing.schedule_publish`) that dispatches to whichever existing core function applies depending on whether the current document is a fresh document or an already-open remote item.

Added `tzdata` as a base dependency (not a `ui` extra) because Windows has no system IANA timezone database and `zoneinfo` needs it.

Validated with the core focused battery (`61 passed`), the combined publishing/accessibility/governance battery (`153 passed`), Ruff, the provider registry gate, and a full-suite run (`4074 passed, 66 failed, 14 skipped`) matching the pre-existing baseline failure set exactly. Committed locally in two checkpoints; not pushed.

Next roadmap phase: local-versus-remote compare and the first honest sync model.

## Compare With Remote Memory - 2026-06-21

Compare is implemented and complete. `quill.core.publishing_compare.build_publishing_comparison` is the pure diff model (title/body/status match-or-differs, plus `remote_changed_since_last_known` from comparing the freshly-fetched remote `updated_at` against the open tab's cached `publishing_updated_at`). `compare_publishing_remote_item` (`quill/core/publishing.py`) is a thin wrapper around the existing `load_publishing_remote_item` — deliberately reuses `PUBLISHING_OPERATION_LOAD` rather than adding a new operation, since comparing is just "fetch and diff," not a new provider capability. `publishing_comparison_message` formats the plain-language report. One command/menu entry (`publishing.compare_remote_item`, `File > Publish > Compare With Remote...`) reports through the existing native message-box pattern — zero new dialog-governance surface.

Important scope decision recorded here for future sessions: `Document.source_metadata` does not survive a local save+reopen (confirmed by reading `quill/io/export.py` and `quill/io/open_read.py` — metadata is rebuilt fresh on open, never serialized on save). This phase deliberately compares against the *currently open tab's* metadata only, and defers the durable file-path-keyed linkage registry sketched in the plan's "Remote identity" section. If a future session is asked to make compare/update work after closing and reopening a locally-saved publishing document, that registry is the prerequisite — it does not exist yet.

Validated with the focused battery (`86 passed`), Ruff, the provider registry gate, and a full-suite run (`4083 passed, 66 failed, 14 skipped`) matching the pre-existing baseline failure set exactly. Committed locally in two checkpoints; not pushed.

Next roadmap phase: Quillin worker execution boundaries and lifecycle behavior.

## Quillin Worker Execution Boundaries Memory - 2026-06-21

Researched first: QUILL's Quillin extension system already has a full subprocess-based worker model (`quill/core/quillins/host.py` + `host_worker.py`, Node via `quill/core/ai/external_engine.py`) with capability/consent gating, but it's Quillin-specific. Publishing providers only support `execution="in_process"`. Building a real provider-specific subprocess/IPC worker boundary would be greenfield work with no concrete consumer — third-party providers remain SEC-8-locked regardless, so nothing real exists yet to validate a worker boundary against. Scoped this phase to real, testable lifecycle behavior instead (confirmed with the user via an explicit three-option choice), deferring the actual boundary build to the live third-party loading phase.

`quill.stability.task_manager.TaskManager` (the class is `TaskManager`, not `QuillTaskManager` despite CLAUDE.md's prose) already provides background dispatch + cooperative cancellation (`CancellationToken`) + UI-thread-marshalled callbacks (`call_ui_safely`/`wx.CallAfter`) — it does not enforce a wall-clock timeout itself; the existing per-request socket timeout in `publishing_clients.py` remains the real timeout enforcement. `MainFrame._task_manager` already exists and was threaded into `BrowsePublishingContentDialog`.

Implemented: `is_cancelled` checkpoint in `browse_publishing_content`/WordPress `browse_content` (raises `PublishingOperationCancelled` between per-kind requests, not a partial-results return — cancel means stop-and-discard); new `publishing_worker.py` as the sole bridge from `quill.core.publishing` to `quill.stability.task_manager`; `BrowsePublishingContentDialog` Cancel button + task-manager dispatch with stale-callback guards; `publishing_adapters.py`'s `WORKER_EXECUTION = "worker"` declared-but-deferred policy.

Important limitation recorded honestly (not hidden): a cooperative cancel can only take effect at a checkpoint the worker function reaches. If cancel is clicked while the first/only request is blocked on a socket read, that thread keeps running until its own socket timeout — the dialog detaches and reports "cancelled" immediately either way, but nothing is forcibly killed. That's exactly the gap a real subprocess worker boundary would close.

Validated with the focused battery (`97 passed`), Ruff, mypy, the provider registry gate, and a full-suite run (`4093 passed, 66 failed, 14 skipped`) matching the pre-existing baseline. Smoke-launched the app to confirm no startup traceback; could not interactively click through Browse/Cancel — no pywinauto or project run-skill exists for this wx app, recorded as a known gap. Committed locally in two checkpoints; not pushed.

Next roadmap phase: live third-party provider loading.