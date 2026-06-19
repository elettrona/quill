# Main Branch Audit Note

Timestamp: `2026-06-10 16:19:03 -04:00`

This note captures findings from a full-suite audit that was run locally after merging current `main` into `features/publishing-providers-framework`.

Important scope note:

- this was a local audit only
- no main-branch fixes from this note were kept on the feature branch
- the branch-specific verification was later reset back to the publishing-owned test slice only

## Why This Note Exists

During a mistaken full-suite run, several failures/timeouts surfaced that appear to belong to current `main` behavior or test coverage rather than to the publishing branch itself.

Those findings were useful enough to preserve for the maintainers of `main`, even though the related local tightening work was reverted from the feature branch.

## Full-Suite Findings

### 1. Stale Tests Against Current `QUILL_DATA_DIR` Contract

Observed failure pattern:

- multiple tests attempted to write under `C:\Users\spopp\AppData\Roaming\Quill\...`
- in this environment that produced `PermissionError` failures
- failing clusters included:
  - `tests/integration/test_document_workflows.py::test_text_document_roundtrip_and_backup`
  - `tests/unit/core/ai/test_ai_sessions.py::test_save_load_round_trip`
  - `tests/unit/core/ai/test_ai_sessions.py::test_list_and_most_recent`
  - `tests/unit/core/test_recent.py`
  - `tests/unit/core/test_recovery.py`
  - `tests/unit/core/test_ipc.py`
  - `tests/unit/core/test_keymap.py::test_load_keymap_merges_overrides`
  - `tests/unit/core/test_menu_customization.py::test_round_trip_persistence`

Likely root cause:

- current `main` documents `QUILL_DATA_DIR` as a dev-only override
- in dev mode the override is accepted only when it resolves under `Path.home()`
- many older tests still set `QUILL_DATA_DIR` directly to `tmp_path`, which is outside that home-constrained boundary in this environment
- those tests therefore silently fell back to real app-data paths and failed there

Suggested direction:

- introduce a shared test fixture for a home-scoped fake data directory
- migrate stale persistence/config tests to that fixture rather than per-test raw `tmp_path` overrides

### 2. TLS Audit Test Scales Poorly in Full Suite

Observed behavior:

- `tests/unit/core/test_net_tls.py::test_no_check_hostname_or_verify_mode_disabled` passed in isolation
- during the full suite it timed out while walking AST nodes across the package

Likely root cause:

- the test parses every Python file and then walks every AST, even when the file does not mention `check_hostname` or `verify_mode`

Suggested direction:

- prefilter files by text content before AST parsing, while preserving the same security assertion

### 3. Thesaurus Cold-Load Pressure in Full Suite

Observed behavior:

- `tests/unit/core/test_reset_caches.py::test_thesaurus_preload_after_reset_is_idempotent` passed in isolation
- during the full suite it later timed out while reparsing thesaurus data after cache reset

Likely root cause:

- cumulative suite pressure rather than a direct functional break
- the thesaurus parse path currently does redundant synonym-cleaning work per entry

Suggested direction:

- profile `quill/core/thesaurus.py` cold-load path
- remove duplicate cleaning work in `_parse_mythes`
- decide whether this should be treated as implementation optimization, test budget tuning, or both

## Local Verification That Supported These Findings

The following targeted reruns were green locally during investigation:

- stale persistence/recovery slice: `11 passed`
- IPC/keymap/menu persistence slice: `11 passed`
- TLS audit file: `5 passed`
- thesaurus reset-cache repro: `1 passed`

Interpretation:

- the main concern is not that these areas are fundamentally broken
- the bigger issue is that current `main` has stale tests around the data-dir contract and a couple of full-suite scalability hot spots

## Branch Impact

- none of the above findings were kept as branch code changes
- publishing-branch validation was rerun afterward on the maintained publishing slice only
- that scoped branch slice passed: `84 passed in 9.75s`
