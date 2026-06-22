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

## Live Third-Party Provider Loading Memory - 2026-06-21 (Roadmap Closed)

Researched first, found this phase is not really publishing-scoped: SEC-8 (`docs/QUILL-PRD.md`) is a product-wide lock via the `core.third_party_plugins` feature flag (`locked_off=True`, defined in `quill/core/feature_catalog.py`) — it keeps ALL third-party Quillin code from executing in a default v1.0 build, not just publishing. "Install from Folder" (`quill/ui/main_frame_quillins.py`'s `on_install`, calling `install_extension()` in `quill/core/quillins/loader.py`) is already unconditionally available and not gated by the flag, but installed third-party code still never runs while the flag is locked off — `discover_extensions()`/`load_enabled_manifests()` return empty regardless. Critically: `register_publishing_provider`/`register_publishing_provider_client` are completely open, ungated module functions with zero security check of their own — the ONLY thing stopping a third-party provider today is that third-party code can't execute in-process at all yet.

This made "live third-party provider loading" a product security policy question (whether to create an exception to, or flip, SEC-8), not an engineering scoping one. Presented three explicit options; the user chose to build the validation contract while leaving the SEC-8 lock and real loading untouched.

Implemented: `ThirdPartyPublishingProviderAdapter` + `register_third_party_publishing_provider` in `quill/core/publishing_adapters.py`. Unlike the bundled adapter, `secret_access`/`execution` have no trusted defaults. Validation cascade (each independently tested): ids match → rationale required → host-owned secrets → execution must be `worker` (in-process explicitly rejected for untrusted code) → provider id must not conflict with a bundled adapter → unconditional final rejection ("not implemented yet"), proven to leave the live registries completely untouched even for a fully well-formed adapter.

Validated with the focused battery (`82 passed`, 14 new tests), Ruff, mypy, the provider registry gate (confirms zero registry impact), and a full-suite run (`4100 passed, 66 failed, 14 skipped`) matching the pre-existing baseline. No UI/dialog/menu/budget changes — `publishing_adapters.py` stayed at 146 lines. Committed locally in one checkpoint; not pushed.

**Roadmap closed.** All four phases the 2026-06-20 Phase 1 closeout authorized are addressed. Two decisions remain explicitly open for the user/product, not engineering defaults to assume if this branch is revisited: (1) whether to build the durable cross-session publishing-linkage registry deferred in the compare phase (`Document.source_metadata` doesn't survive save/reopen), and (2) whether/when to loosen `core.third_party_plugins`/SEC-8 for real third-party Quillin or publishing-provider execution.

## Durable Publishing Linkage Registry Memory - 2026-06-22

The user chose to resolve decision (1) above. New `quill/core/publishing_linkage.py` holds a path-keyed JSON store (`app_data_dir() / "publishing-linkage.json"`, mirroring the existing `publishing-connections.json` pattern) with a `PublishingLinkageEntry` frozen dataclass and converters to/from `Document.source_metadata`'s ten `publishing_*` fields plus the `source_kind`/`source_label` guard keys.

Three `main_frame.py` integration points, all funneling through one new helper, `_sync_publishing_linkage_for_document`: the save chokepoint `_write_document_to_disk` (persists after every save); `_finish_open_document` (restores a registry hit into the freshly-read document's `source_metadata` before either tab branch runs); and all three handlers that refresh publishing metadata after a successful network round trip (`_send_publishing_remote_item`, the schedule-publish handler, the create-draft/publish-now handler — research during planning found only the first; the other two were discovered while implementing and added for consistency, since they mutate `source_metadata` the same way). The helper skips untitled documents (`path is None`) and CSV grid/Word structured surfaces, since Compare/Update only ever read `self.editor.GetValue()` as markdown/HTML text — a shape those surfaces were never designed to produce, so linkage for them is never persisted and therefore never wrongly restored either.

A real bug surfaced during implementation: the first cut of the helper did bare (non-defensive) attribute access on `self.editor`/`document.source_metadata` and broke an existing characterization test that exercises `_write_document_to_disk` against a bare `MainFrame.__new__`/`SimpleNamespace` test double with neither attribute set. Fixed by making the helper fully `getattr`-defensive, matching that test suite's own stated convention ("stub only the attributes each method touches") and the pre-existing defensive style already used a few lines above it in the same function for `self.settings`.

Important methodology finding for future sessions: this slice's full-suite validation used pytest's default temp directory rather than a custom `--basetemp`. Every full-suite baseline recorded earlier in this roadmap (`...,66 failed,...`) was validated with `--basetemp=.tmp\pytest-<slice>-full` — a path under the repo, outside `Path.home()`. The H-1-core guard in `quill/core/paths.py` silently rejects a `QUILL_DATA_DIR` override outside home, so any test depending on the shared `quill_data_dir` conftest fixture would have silently fallen through to the real `%APPDATA%\Quill` directory under those custom basetemps, breaking isolation. A `git stash`/clean-tree comparison this slice ran independently confirms the *true* pre-existing baseline is `19 failed` (identical failure names with or without this slice's changes), not `66`. Not fixed retroactively in earlier notes; flagged here so it isn't mistaken for a regression or repeated. One harmless side effect from discovering this: a single bogus entry landed in the real `%APPDATA%\Roaming\Quill\publishing-linkage.json` from this slice's own first (buggy) test run; the user was asked and chose to leave it as-is.

Validated with the focused battery (`77 passed`), Ruff/`ruff format --check`, scoped mypy (unchanged, same 7 pre-existing findings), and the full-suite comparison above. `main_frame.py`'s module-size budget bumped 25127->25165. Committed locally in two checkpoints; not pushed.

**One decision remains open**: whether/when to loosen `core.third_party_plugins`/SEC-8 for real third-party Quillin or publishing-provider execution.