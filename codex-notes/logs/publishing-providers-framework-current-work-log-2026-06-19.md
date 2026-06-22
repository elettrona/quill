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

## 2026-06-21 - Live Third-Party Provider Loading (Final Phase, Roadmap Closed)

User asked to continue, and confirmed wanting memory/docs kept current throughout (already the established practice this session).

Researched QUILL's SEC-8 policy and the "Install from Folder" Quillin flow via one Explore agent before scoping, since the phase name implied loosening a security boundary: confirmed SEC-8 (`docs/QUILL-PRD.md`, `core.third_party_plugins` flag in `quill/core/feature_catalog.py`, `locked_off=True`) is product-wide — it keeps all third-party Quillin code from running in a default v1.0 build, regardless of publishing. "Install from Folder" (`quill/ui/main_frame_quillins.py` → `quill/core/quillins/loader.py`'s `install_extension()`) is already open and ungated, but installed code still never executes while the flag is locked off. Found `register_publishing_provider`/`register_publishing_provider_client` are themselves completely open functions with no gate — third-party provider loading is blocked today ENTIRELY by the Quillin-execution lock, not by anything publishing-specific.

Presented the user three explicit options via AskUserQuestion (build the contract with loading kept locked off; flip the SEC-8 flag and wire real loading; stop here as policy-blocked). The user chose the first, recommended option, matching the "build the contract, defer the risky part" pattern used in schedule/compare/worker-execution.

Work completed in one commit (no UI/dialog/menu/budget changes needed — this was a pure core-contract addition):

- `quill/core/publishing_adapters.py`: new `ThirdPartyPublishingProviderAdapter` dataclass (no trusted defaults for `secret_access`/`execution`, unlike the bundled adapter) and `register_third_party_publishing_provider()`. Validation cascade: ids must match; network rationale required; secrets must be host-owned; execution must be `worker` (in-process rejected outright for untrusted code); provider id must not conflict with an existing bundled adapter; then an unconditional final rejection ("Live third-party publishing provider loading is not implemented yet."). Module docstring states explicitly this contract does not loosen, bypass, or duplicate the SEC-8 lock.
- `tests/unit/core/test_publishing_adapters.py`: 14 new tests — each validation branch independently triggered, an id-mismatch case, a bundled-id-conflict case, and a proof test that even a fully well-formed third-party adapter still gets rejected with the live registries (`PROVIDER_DEFINITIONS`, `_PUBLISHING_PROVIDER_CLIENTS`) left completely untouched.

Validation:

- focused battery (publishing core + adapters): `82 passed`
- Ruff: passed
- provider registry gate: passed (confirms zero registry impact)
- scoped `mypy quill/core quill/io`: unchanged from before this slice (same 7 pre-existing findings)
- full unit suite: `4100 passed, 66 failed, 14 skipped` — identical pre-existing failure set; +7 passing delta matches the new tests added
- `publishing_adapters.py` measured at 146 lines, well under the untracked 600-line default cap — no module-size budget entry needed

**This closes the publishing-providers-framework roadmap.** All four phases authorized by the 2026-06-20 Phase 1 closeout are addressed. Two decisions remain explicitly open for the user/product, recorded as deliberate non-defaults rather than oversights: the deferred cross-session publishing-linkage registry (compare phase), and whether/when to loosen `core.third_party_plugins`/SEC-8 for real third-party execution (this phase). Committed locally; not pushed pending explicit request.

## 2026-06-22 - Durable Publishing Linkage Registry (Resolves First Open Decision)

User asked to resolve the first of the two decisions left open at roadmap close. Planned via `EnterPlanMode`/`ExitPlanMode` after reading the actual call sites directly (`Document.source_metadata`, `_write_document_to_disk`, `_finish_open_document`, the three publish-success handlers, `quill/io/export.py`'s `mark_saved` call, `quill/core/publishing.py`'s connections-store pattern to mirror).

Work completed in two commits:

1. **Core**: new `quill/core/publishing_linkage.py` — `PublishingLinkageEntry` frozen dataclass, path-keyed JSON store at `app_data_dir() / "publishing-linkage.json"` (mirrors `publishing-connections.json`: `read_json`/`write_json_atomic`, defensive `isinstance` checks at every JSON level), `load_publishing_linkage_registry`/`save_publishing_linkage_registry`/`get_publishing_linkage`/`upsert_publishing_linkage`/`remove_publishing_linkage`, and `publishing_linkage_from_source_metadata`/`apply_publishing_linkage_to_source_metadata` converters. 16 new tests in `tests/unit/core/test_publishing_linkage.py`.
2. **UI integration**: `MainFrame._sync_publishing_linkage_for_document` (the one shared helper) called from `_write_document_to_disk` (after every save) and from all three handlers that refresh publishing metadata after a successful network round trip — `_send_publishing_remote_item`, the schedule-publish handler, and the create-draft/publish-now handler (the latter two were not in the original plan; discovered while implementing, since they mutate `source_metadata` via the identical pattern, and added for consistency). `_finish_open_document` looks up the registry by `selected_path` and restores a hit into `source_metadata` before either tab branch runs. The helper skips untitled documents and `CsvGridSurface`/`WordDocumentSurface` tabs (Compare/Update only ever read markdown/HTML text from `self.editor.GetValue()`, a shape those structured surfaces don't produce). 4 new static-source tests in `tests/unit/ui/test_main_frame.py`; `main_frame.py`'s module-size budget bumped 25127->25165.

Real bug caught mid-implementation: the first version of the helper used bare `self.editor`/`document.source_metadata` attribute access and broke `test_main_frame_cq16_characterization.py::test_write_document_to_disk_routes_rtf_through_the_rtf_writer`, which calls `_write_document_to_disk` against a bare `MainFrame.__new__` test double and a `SimpleNamespace(path=...)` document — neither has those attributes, matching that suite's documented convention of stubbing only what each method touches. Fixed by rewriting the helper to be fully `getattr`-defensive (checks `source_metadata` is a dict before touching anything else, so the common non-publishing case never reaches `self.editor` at all), confirmed by re-running the full suite and seeing the previously-broken test pass again with no new failures introduced.

Validation methodology finding, recorded for future sessions: ran the full suite with pytest's *default* temp directory rather than a custom `--basetemp` this time. Every prior full-suite baseline in this roadmap was recorded using `--basetemp=.tmp\pytest-<slice>-full`, a path under the repo and therefore outside `Path.home()` — and `quill/core/paths.py`'s H-1-core guard (`_is_constrained_to_home`) silently rejects a `QUILL_DATA_DIR` override outside home, so any test using the shared `quill_data_dir` conftest fixture would have silently lost isolation under those basetemps and fallen through to the real `%APPDATA%\Quill`. A `git stash`/clean-tree comparison run this slice independently confirms the true pre-existing baseline is `19 failed` (identical names with or without this slice's changes), not the `66` recorded in every earlier phase's notes. Not retroactively corrected in those notes; flagged here only so a future session doesn't mistake `66` for ground truth or repeat the same basetemp pattern. One harmless concrete side effect from finding this: the slice's own first (buggy) test run wrote a single bogus entry into the real `%APPDATA%\Roaming\Quill\publishing-linkage.json`; asked the user, who chose to leave it (harmless test data).

Validation:

- focused battery: `77 passed`
- Ruff and `ruff format --check`: passed
- scoped `mypy quill/core quill/io`: unchanged (same 7 pre-existing findings)
- full unit suite: `4167 passed, 19 failed, 14 skipped`; clean-tree comparison (`git stash`) shows the identical 19 failures at `4147 passed`, proving zero regressions and that the +20 delta is exactly the new tests added

Committed locally as two checkpoints (core, then UI integration); not pushed pending explicit request.

**One decision remains open**: whether/when to loosen `core.third_party_plugins`/SEC-8 for real third-party Quillin or publishing-provider execution.

## 2026-06-22 - Merged origin/main (Beta 2) into the branch

User asked to integrate upstream changes, preserving this branch's work and
keeping it fully compliant, updating our code only where main's changes
required it. `origin/main` had advanced 116 commits (PR #664, "Beta 2":
offline speech/Whisper, the verbosity system, braille proofing, i18n
display-language switching, crash-submit dialog, data-location migration,
and more) since this branch's fork point.

`git merge origin/main` auto-merged `main_frame.py` and `main_frame_menu.py`
cleanly; 5 files needed manual resolution:

- `quill/__main__.py`: a real conflict, not just textual — main's Beta-2
  work replaced the old `_bootstrap_storage_mode()` first-run storage-mode
  prompt (inherited boilerplate from before this branch forked, not our
  code) with `_propagate_portable_environment()` +
  `apply_pending_data_location_migration()`. The merge silently dropped
  `_bootstrap_storage_mode`'s *definition* while leaving a stray call to it
  in the conflict region. Resolved by dropping the stale call (main's
  replacement already runs earlier in `main()`) and keeping our actual
  contribution, the `bootstrap_bundled_publishing_providers()` call, intact.
- `quill/tools/module_size_budgets.json`: resolved programmatically rather
  than by hand — both sides' historical `_rebaseline_*` comment entries were
  unioned (main's side was a superset for every region but one, where a
  one-line annotation difference was kept from main), and every `budgets`
  dict entry was set to the file's actual measured line count in the merged
  tree (not either side's stale recorded number), since both branches had
  independently grown several shared files (`main_frame.py`:
  25165/25499→**26092** actual; `main_frame_menu.py`: 3633/3658→**3780**
  actual).
- `tests/unit/ui/fixtures/dialog_inventory.json`: regenerated from source
  (`python -m quill.tools.dialog_inventory --write`) rather than hand-merged
  — it's a generated snapshot, AST-scanned from `quill/**/*.py`.
- `tests/unit/ui/test_main_frame_menu_contract.py` and
  `test_power_tools_command_wiring.py`: both sides had added independent,
  non-overlapping tests/assertions at the same insertion point; kept both.

Two test failures surfaced after conflicts were resolved, both expected
consequences of main's legitimate growth, not regressions:

- 3 `test_compile_translations.py` failures: `ModuleNotFoundError: babel`.
  Main's i18n work added `Babel>=2.18.0` to the `dev` extra in
  `pyproject.toml`; this dev environment hadn't re-run
  `pip install -e ".[ui,dev]"` since. Fixed by reinstalling.
- `test_main_frame_characterization.py::test_main_frame_public_surface_is_unchanged`:
  main's Beta-2 features legitimately added ~29 new public `MainFrame`
  methods (verbosity, speech, braille proofing, etc.). Regenerated the
  snapshot (`python -m quill.tools.ui_surface --write`).

Validation: `ruff check .` passed (clean); `ruff format --check .` flagged 2
files main itself owns (`test_keymap_format.py`,
`test_prompt_unsaved_changes_native_labels.py`) — verified via a throwaway
`git worktree add` of `origin/main` alone that this is pre-existing on main,
caused by a ruff version bump (0.15.16→0.15.18) changing line-wrap
heuristics, not anything this merge touched; left alone since it isn't our
code and needs no functional change. Scoped `mypy quill/core quill/io`:
**down** to 1 finding (the pre-existing `publishing_validation.py` one) —
the 6 `brf_page_detection.py` findings present before this merge are gone,
resolved by main's own braille-proofing work. Module-size budget gate,
provider registry gate, and the Quillin self-lint (`--strict`, 14/14
bundled Quillins) all passed. Full suite: `4885 passed, 4 failed, 13
skipped`. The 4 failures (`test_about_info`, `test_open_read`,
`test_build_windows_distribution`, `test_check_version_consistency`) were
verified, via a throwaway `git worktree add` of `origin/main` alone, to be
byte-for-byte identical pre-existing failures on main itself (a real,
unrelated version-skew between `quill/__init__.py` ("0.7.0") and
`installer/quill.iss`/`CHANGELOG.md` ("0.7.0 Beta 1"), plus two
environment/build-state-sensitive checks) — not introduced by this merge.
Re-ran the full publishing-specific test battery (144 tests across core +
UI) after the merge commit: all pass. Smoke-launched the app: no traceback.

One harmless side effect: an automatic `--write` regeneration step (`pip
install`) bumped the installed `ruff` from 0.15.16 to 0.15.18 in this dev
environment as a transitive consequence of reinstalling for the `babel`
dependency; not pinned or reverted, since the project's own `pyproject.toml`
doesn't pin an exact ruff version.

Committed as a single merge commit (`a17acdd2`); not pushed pending
explicit request, per the standing repo convention.