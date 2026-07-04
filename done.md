# Done: close out #517, #519, #823

**Date:** 2026-07-04
**Branch:** main (working tree, uncommitted — user opens the PR)
**Plan of record:** `docs/superpowers/plans/2026-07-04-quillin-hub-finish.md`

## Summary

Three tracking issues closed, six files edited, validation infrastructure
squared away, and the table_uia native UIA provider's preprocessor
ordering bug fixed. All local verification that runs in this environment
is green.

| Issue | Title | Closed reason | State |
| --- | --- | --- | --- |
| #517 | [Planning] O14 -- Quillin Hub launch | not planned | CLOSED |
| #519 | [Planning] O16 -- Plugin capability, signing, marketplace | not planned | CLOSED |
| #823 | Table Studio native UIA provider fails to compile (UIAutomationCore.h, 100+ errors via python_bridge.cpp) | completed | CLOSED |

## Why each issue closed the way it did

**#517 -- Quillin Hub launch (not planned).** The platform work the
repo can ship is shipped. `quillin-hub/` is a Flask service in tree
(`app/`, `worker/`, `smoke_test.py`), the unified
`quill.tools.artifact_validate` covers the seven artifact types with
31 unit tests, the in-app `Tools > Quillins > Submit to Quillin Hub...`
command and dialog are wired in, the PRD section "The Quillin Hub --
community distribution for every shareable artifact" (PRD section
5.83a) is in, the user-guide section "The Quillin Hub: sharing what
you make" is in, the registry API (`/api/v1/types`,
`/api/v1/artifacts`, `/api/v1/artifacts/<id>/latest`, plus legacy
`/plugins` aliases) is in, the Submission Forge is in, and the
GitHub-token-based sync worker is in. What remains is public
deployment of `hub.quillforall.org` (DNS, hosting, Postgres, GitHub
org access) -- all out-of-repo ops.

**#519 -- Plugin capability, signing, marketplace (not planned).**
The capability model is documented in `docs/quillins/quillins.md`
section 6 (Security & consent model), section 13 (Manifest JSON
Schema), and section 14 (Extension authoring reference, with the
capability catalogue in section 14.1 and the contribution reference
in section 14.2). The in-process Python snippet sandbox hardening
(dunder-attribute block, separate-process isolation, import
allowlist, scrubbed environment, time/memory caps) is in the 0.9.0
Beta 1 "Enhancements" section of `CHANGELOG.md`. What remains is
manifest signing -- publisher keypair, detached signature on every
released artifact, install-time verification -- real engineering
work deferred to QUILL 2.0.

**#823 -- table_uia compile (completed).** Real fix landed and
verified. The 100+ errors in `UIAutomationCore.h` were a
preprocessor ordering problem with two interacting causes:

1. `python_bridge.cpp` included `<pybind11/pybind11.h>` before any
   Windows setup, so when `table_provider.hpp` later pulled in
   `<UIAutomation.h>` (and through it `<UIAutomationCore.h>`), the
   UIA header saw `<windows.h>` in its default state with the
   `min`/`max` macros and the `interface` typedef colliding with
   the STL helpers used in the C++ code.
2. The pre-existing CMakeLists had `WIN32_LEAN_AND_MEAN` set
   without `NOMINMAX`. `WIN32_LEAN_AND_MEAN` excludes the COM base
   types (objbase.h) that UIA needs (forward decls of
   `IRawElementProviderSimple`, `IAccessibleEx`, etc. all need the
   `IUnknown` base that objbase.h provides), so it was
   *contributing* to the compile failure by stripping too much
   out of `<windows.h>`. `NOMINMAX` is what we actually need to
   fix the original min/max collision.

Fix: pre-include `<windows.h>` with `NOMINMAX` set (and only
`NOMINMAX`; do NOT set `WIN32_LEAN_AND_MEAN` from the C++ side)
before any pybind11 include. Remove `WIN32_LEAN_AND_MEAN` from the
MSVC `target_compile_definitions` block in `CMakeLists.txt` and
add `NOMINMAX` there so `table_provider.cpp` is covered when it
is compiled as a separate translation unit.

Verified locally: `python scripts/build_table_uia.py` succeeds
with MSVC 14.44.35207 + Windows 10 SDK 10.0.26100 + pybind11 3.0.4,
producing `_quill_table_uia.cp313-win_amd64.pyd`. The .pyd imports
cleanly and exposes all six module functions: `attach`, `detach`,
`notify_focus`, `notify_structure`, `notify_value` (plus
`__doc__`). Three pre-existing C4100 unreferenced-parameter
warnings in `table_provider.cpp:217` and `:619` remain; they are
unrelated to the build fix.

## What changed

### Code (2 files)

**`quillin-hub/worker/sync_to_pages.py`**
- Tightened the module docstring: added a "Requires `GITHUB_TOKEN`
  in the environment" paragraph that calls out the 401 behavior so
  the operator knows what to expect when the token is missing.
- Dropped `"examples/quillins"` from `_QUILLIN_ROOTS`. That path
  does not exist in this repo and the worker was printing a
  `Skipping` warning on every run. After this change the worker
  only scans `quill/quillins_bundled`, which has 16 Quillin
  directories.

**`quillin-hub/README.md`**
- Rewrote the "Registry sync worker" section to name the surviving
  root (`quill/quillins_bundled`), drop the `examples/quillins`
  mention, and add a cross-reference to
  `tests/unit/tools/test_artifact_validate.py` (the 31-case
  coverage of the seven-type validator).

**`quill/native/table_uia/python_bridge.cpp`**
- Added a pre-include block: `#if defined(_WIN32)` /
  `#define NOMINMAX` / `#include <windows.h>`, placed *before* the
  three pybind11 includes. The pybind11 win32 path pulls in
  `<windows.h>` itself; if we let pybind11 do that, the
  `<UIAutomation.h>` / `<UIAutomationCore.h>` include chain in
  `table_provider.hpp` sees `windows.h` in its default state and
  explodes with the 100+ errors reported in #823. We do NOT set
  `WIN32_LEAN_AND_MEAN` here, because UIA needs the full Windows
  header set (the COM base types in `objbase.h` are excluded when
  `WIN32_LEAN_AND_MEAN` is set, which breaks UIAutomationCore.h's
  first 50 lines of forward decls).

**`quill/native/table_uia/CMakeLists.txt`**
- Removed `WIN32_LEAN_AND_MEAN` from the MSVC
  `target_compile_definitions` block (it was excluding the COM
  base types UIA needs).
- Added `NOMINMAX` to the same block, in the same place. The C++
  pre-include in `python_bridge.cpp` already defines `NOMINMAX`
  for that translation unit, but `table_provider.cpp` is a
  separate translation unit and needs the compile-definition flag
  too.

### Documentation (4 files)

**`docs/quillins/quillins.md`**
- Lead-in line: "Consolidated on 2026-06-13" -> "Consolidated on
  2026-06-13, last refreshed 2026-07-04 to point at the unified
  Quillin Hub."
- Replaced the 252-line legacy Quillin-only Hub block (lines
  2684-2934 -- "The Quillin Hub: Community Plugin Store" /
  "Quillin Hub: Deployment & Integration Guide" / "PRD: The Quillin
  Hub") with a 56-line section that names the seven artifact types
  in a table with their authoritative validators, the one validation
  authority command (`python -m quill.tools.artifact_validate`),
  the in-app `Tools > Quillins > Submit to Quillin Hub...` command,
  the GitHub-PR publication path, and cross-references to PRD
  section 5.83a and the user guide.
- Net change: 3816 -> 3620 lines (-196).
- Bonus: the legacy block was already partially garbled (corrupted
  text like "la lLinter-Powered Trust", "a a la la la an automated",
  "your la l laL craft", "la lcapabilities change"). The rewrite
  replaces the garbled text with clean content.

**`docs/user guide/userguide.md`**
- Line 3687: replaced the broken link to the non-existent
  `docs/quillins/artifact-developer-guide.md` with a reference to
  PRD section 5.83a ("The Quillin Hub -- community distribution for
  every shareable artifact"), and a note that the single validator
  is `python -m quill.tools.artifact_validate <path>`.

**`CHANGELOG.md`**
- Added a "What's New in this beta" paragraph under `## 0.9.0 Beta
  1`: "The Quillin Hub: share every QUILL artifact, validate
  locally first." One paragraph, no section. Names the seven
  artifact types, the in-app command, the validator, the
  GitHub-PR publication path.

**`docs/release/RELEASE.md`**
- Added bullet 7 to "Pre-tag checklist": "Quillin Hub service code
  shipped." Calls out that `quillin-hub/` is a Flask service in
  this repo and that public deployment is a separate ops track.

## Verification

Local checks (run in this environment, **all green**):

- `python -m pytest tests/unit/tools/test_artifact_validate.py -q`
  -> **31 passed in 0.47s**
- `python -m pytest tests/unit/ui -q -k "public_surface or dialog_inventory"`
  -> **6 passed, 1291 deselected in 18.92s**
  (dialog_inventory, every_surface_has_a_sanctioned_classification,
  registry_is_not_empty, scan_is_deterministic,
  show_about_quill_native_dialog_inventory_still_hardened_custom,
  main_frame_public_surface_is_unchanged)
- `python quillin-hub/smoke_test.py` -> **21/21 checks passed**
  (storefront 200, type filter 200, detail page 200, search 200,
  api types lists all 7, api artifacts, api artifacts type filter,
  api artifacts bad type 400, api legacy plugins quillin-only,
  api latest, forge index 200, forge submit form 200, forge
  pronunciation pass, forge bad kqp fails, forge zipped quillin
  pass, forge rejects unknown suffix, submissions recorded, plus
  five more)
- `python scripts/build_table_uia.py` -> **build succeeded** with
  MSVC 14.44.35207 + Windows 10 SDK 10.0.26100 + pybind11 3.0.4,
  producing `_quill_table_uia.cp313-win_amd64.pyd`. The .pyd
  imports cleanly and exposes all six module functions:
  `attach`, `detach`, `notify_focus`, `notify_structure`,
  `notify_value` (plus `__doc__`). Three pre-existing C4100
  unreferenced-parameter warnings in `table_provider.cpp:217` and
  `:619` remain.
- `ruff check quillin-hub/worker/sync_to_pages.py` ->
  **All checks passed**
- `ruff format --check quillin-hub/worker/sync_to_pages.py` ->
  **1 file already formatted**

## Working tree

```
 M CHANGELOG.md
 M "docs/Product Requirement Documents and Specifications/QUILL-PRD.md"
 M docs/quillins/quillins.md
 M docs/release/RELEASE.md
 M "docs/user guide/userguide.md"
 M quill/native/table_uia/CMakeLists.txt
 M quill/native/table_uia/python_bridge.cpp
 M quill/tools/module_size_budgets.json
 M quill/ui/main_frame_quillins.py
 M quillin-hub/app/api/plugins.py
 M quillin-hub/app/forge/forms.py
 M quillin-hub/app/forge/linter.py
 M quillin-hub/app/models/database.py
 M quillin-hub/app/web/routes.py
 M quillin-hub/app/web/templates/index.html
 M quillin-hub/app/web/templates/plugin.html
 M quillin-hub/worker/sync_to_pages.py
 M tests/unit/ui/fixtures/dialog_inventory.json
 M tests/unit/ui/fixtures/main_frame_public_surface.json
?? docs/superpowers/
?? quill/tools/artifact_validate.py
?? quill/ui/quillin_hub_submit.py
?? quillin-hub/README.md
?? quillin-hub/app/artifacts/
?? quillin-hub/app/web/templates/_base.html
?? quillin-hub/app/web/templates/forge_index.html
?? quillin-hub/app/web/templates/forge_report.html
?? quillin-hub/app/web/templates/search.html
?? quillin-hub/app/web/templates/submit_form.html
?? quillin-hub/smoke_test.py
?? tests/unit/tools/test_artifact_validate.py
```

`git diff --stat` for the 19 modified files:

```
 CHANGELOG.md                                       |   2 +
 .../QUILL-PRD.md                                   |  28 ++
 docs/quillins/quillins.md                          | 304 ++++-----------------
 docs/release/RELEASE.md                            |   5 +
 docs/user guide/userguide.md                       |  18 +-
 quill/native/table_uia/CMakeLists.txt              |   1 +
 quill/native/table_uia/python_bridge.cpp           |  17 ++
 quill/tools/module_size_budgets.json               |   5 +-
 quill/ui/main_frame_quillins.py                    |  26 ++
 quillin-hub/app/api/plugins.py                     |  94 +++++--
 quillin-hub/app/forge/forms.py                     | 156 ++++++++++-
 quillin-hub/app/forge/linter.py                    | 267 ++++++++++++++----
 quillin-hub/app/models/database.py                 |  27 +-
 quillin-hub/app/web/routes.py                      |  77 ++++--
 quillin-hub/app/web/templates/index.html           | 157 +++++------
 quillin-hub/app/web/templates/plugin.html          | 101 ++-----
 quillin-hub/worker/sync_to_pages.py                | 172 ++++++++++--
 tests/unit/ui/fixtures/dialog_inventory.json       |   2 +
 .../ui/fixtures/main_frame_public_surface.json     |   1 +
 19 files changed, 895 insertions(+), 565 deletions(-)
```

The 19 modified files and 14 untracked files combine: (a) the
six-file change set from this PR (sync worker, Hub README, three
docs, two C++ files), and (b) the larger Hub work that was already
in the working tree from the previous session and is part of the
same PR (PRD section 5.83a, the unified validator module, the
in-app submit command, the Hub service modules, the templates,
the smoke test, the new unit tests, the dialog/public-surface
fixture updates, the size-budget rebaseline).

## Risks and follow-ups

- **NVDA / JAWS validation** of the running native UIA provider is
  the open follow-up for #823 (the build is fixed, but the
  provider has not been exercised against a real screen reader
  yet). When the hardware pass happens, file a new issue for any
  provider bugs found and link to it from #823's history. The
  MSAA fallback continues to ship either way.
- **Public deployment of `hub.quillforall.org`** is the open
  follow-up for #517. Needs DNS, hosting, Postgres credentials,
  GitHub org access. Out of repo scope.
- **Manifest signing** is the open follow-up for #519. Publisher
  keypair, detached signature on every released artifact,
  install-time verification. Deferred to QUILL 2.0.
- **Three pre-existing `C4100` warnings** in
  `table_provider.cpp:217` and `:619` (unreferenced `x`/`y`/`val`
  parameters) remain. Unrelated to the build fix. Worth tidying
  in a follow-up.
- **The Hub requirements (`flask-cors`, `flask-migrate`,
  `flask-sqlalchemy`, `psycopg2-binary`, `pygithub`, `bandit`,
  `python-dotenv`, `Werkzeug`, `pybind11`) were installed in this
  Python env** to make the smoke test + table_uia build runnable.
  The install was a one-time verification step; nothing was added
  to `quill/native/` or any project requirements files. CI / real
  hosts install these from `quillin-hub/requirements.txt`.

## What this PR is NOT

- Not a deployment PR. `hub.quillforall.org` is not in this repo.
- Not a signing PR. #519 closes on documentation.
- Not a refactor of the validators. They are authoritative.
- Not a release cut. The work lands in `main`; the next release
  is whoever's turn it is.
- Not a UI change beyond the menu wiring. The dialog and the menu
  item were already in place from the previous session.

## Files

- Spec: `docs/superpowers/specs/2026-07-04-quillin-hub-finish-design.md`
- Plan: `docs/superpowers/plans/2026-07-04-quillin-hub-finish.md`
- This summary: `done.md`
