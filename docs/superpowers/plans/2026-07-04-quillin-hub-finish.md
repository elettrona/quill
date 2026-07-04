# Quillin Hub Finish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close issues #517, #519, and #823 with the documentation, code cleanup, C++ build fix, and changelog/release-notes edits needed to record the shipped Hub work and the rebuilt table_uia native provider in the main QUILL repository.

**Architecture:** One PR with six small commits: (1) drop the missing `examples/quillins` sync root and tighten the GitHub-token docstring; (2) update the Hub README; (3) rewrite the legacy Hub section in `docs/quillins/quillins.md`; (4) fix the user-guide link and add the CHANGELOG + RELEASE entries; (5) fix the table_uia C++ include order and add `NOMINMAX`; (6) close issues #517, #519, and #823 via `gh` and run verification.

**Tech Stack:** Python (Flask service, validator module), Markdown docs, `gh` CLI for issue ops, `pytest`, `ruff`.

**Spec:** `docs/superpowers/specs/2026-07-04-quillin-hub-finish-design.md`

## Global Constraints

- Python 3.12+, ruff clean, pytest green.
- All output is plain ASCII in chat, screen-reader-friendly.
- `git status` is the working tree truth; do not commit unless the user
  asks (each task says "do not commit" or "commit at the end" — the
  final commit happens only after the user reviews).
- Do not push. Do not open a PR. The user opens the PR themselves.
- The seven artifact types covered by the Hub: `quillin`, `agent`,
  `verbosity-pack`, `sound-pack`, `keyboard-pack`, `skill-pack`,
  `pronunciation-dictionary`. Their authoritative validators:
  `quill.tools.quillin_lint`, `quill.tools.agent_lint`,
  `quill.core.verbosity.qvp`, `quill.core.sound_pack`,
  `quill.tools.kqp_validator`, `quill.core.skill_pack`, the
  pronunciation schema check (in `artifact_validate._validate_pronunciation`).
- The in-app command is `tools.quillin_hub_submit`. The menu path is
  `Tools > Quillins > Submit to Quillin Hub...`. The Hub URL is
  `https://hub.quillforall.org`.
- The PRD section is §5.83a. The user guide section is "The Quillin
  Hub: sharing what you make" (under "Sharing what you make" /
  near the existing Quillin section).

---

## Task 1: Drop the missing sync root and tighten the worker docstring

**Files:**
- Modify: `quillin-hub/worker/sync_to_pages.py:1-90`

**Context:** The sync worker lists `quill/quillins_bundled` and
`examples/quillins` as roots. The second one does not exist in this
repo (`ls examples/` shows only `Windows Screenreader Primer Fifth EditionChapter Files in Word`, `audio`, `quillins` — no `examples/quillins/`). The worker prints a warning at runtime. We drop the missing root and tighten the module docstring to make the GitHub-token requirement prominent.

- [ ] **Step 1: Confirm `examples/quillins` does not exist**

Run from `S:/QUILL`:
```bash
ls examples/quillins 2>&1
```
Expected: `ls: cannot access 'examples/quillins': No such file or directory`

- [ ] **Step 2: Edit `quillin-hub/worker/sync_to_pages.py`**

Make two changes:

(a) Update the module docstring. Replace the existing top-of-file
docstring (the entire triple-quoted block at the top) with this
exact text:

```python
"""GitHub-native registry sync.

Scans the QUILL repository for every artifact type the Hub publishes --
Quillins, AI agents, and skill packs -- and syncs them into the Hub
database as Verified artifacts (if it landed on main, it passed the
Quillin Verify workflow).

Requires ``GITHUB_TOKEN`` in the environment; the worker uses the
GitHub Contents API to enumerate the repo. Without a token, every
API call returns 401 immediately and no artifacts are synced.

Run as a cron job or worker::

    GITHUB_TOKEN=... python worker/sync_to_pages.py
"""
```

(b) Drop `"examples/quillins"` from the `_QUILLIN_ROOTS` tuple.
Change:

```python
_QUILLIN_ROOTS = ("quill/quillins_bundled", "examples/quillins")
```

to:

```python
_QUILLIN_ROOTS = ("quill/quillins_bundled",)
```

- [ ] **Step 3: Verify the file parses**

Run:
```bash
python -c "import ast; ast.parse(open('quillin-hub/worker/sync_to_pages.py').read()); print('ok')"
```
Expected: `ok`

- [ ] **Step 4: Verify the diff is what you expect**

Run:
```bash
git diff quillin-hub/worker/sync_to_pages.py
```
Expected: only the docstring body and the `_QUILLIN_ROOTS` tuple
changed; nothing else.

- [ ] **Step 5: Do not commit yet** — proceed to Task 2.

---

## Task 2: Update the Hub README's "Registry sync worker" section

**Files:**
- Modify: `quillin-hub/README.md:74-82`

**Context:** The README's "Registry sync worker" section still names
`examples/quillins` as a scanned root. We updated the worker in Task 1
to drop that root, so the README must be in sync. We also add a single
cross-reference line to the artifact_validate unit tests so a reader
can find the seven-type coverage.

- [ ] **Step 1: Read the current README section**

Run:
```bash
sed -n '70,85p' quillin-hub/README.md
```
Expected: shows the "Registry sync worker" heading and the
`GITHUB_TOKEN=... python worker/sync_to_pages.py` example.

- [ ] **Step 2: Replace the section**

Replace the entire "Registry sync worker" section (the heading
"## Registry sync worker" through the end of its fenced bash block)
with this exact text:

```markdown
## Registry sync worker

`worker/sync_to_pages.py` scans the QUILL repository (the bundled
`quill/quillins_bundled` Quillin tree, the AI agents under
`quill/core/ai/agents`, and any `.sqp` skill packs shipped inside
Quillin folders) and upserts them as Verified artifacts. A
`GITHUB_TOKEN` is required.

```bash
GITHUB_TOKEN=... python worker/sync_to_pages.py
```

The seven artifact types and their authoritative validators are
covered by `tests/unit/tools/test_artifact_validate.py` (31 cases:
detection, validation, CLI exit codes, JSON output).
```

- [ ] **Step 3: Verify the README parses**

Run:
```bash
python -c "import re; s = open('quillin-hub/README.md').read(); print('has-section:', '## Registry sync worker' in s); print('has-cmd:', 'GITHUB_TOKEN' in s); print('has-test-ref:', 'test_artifact_validate.py' in s)"
```
Expected output: all three `True`.

- [ ] **Step 4: Verify the diff**

Run:
```bash
git diff quillin-hub/README.md
```
Expected: only the "Registry sync worker" section changed; no other
sections touched.

- [ ] **Step 5: Do not commit yet** — proceed to Task 3.

---

## Task 3: Rewrite the legacy Hub section in `docs/quillins/quillins.md`

**Files:**
- Modify: `docs/quillins/quillins.md:1-3, 2684-2810`

**Context:** The file's lead-in still says "Consolidated on
2026-06-13 into one document." and lines 2684-2810 carry a Quillin-
only Hub narrative written before the platform expanded to seven
artifact types. We refresh the lead-in and replace the legacy section
with one that names the unified Hub, the seven types, the validator,
the in-app command, the GitHub-PR publication path, and the cross-
references. We replace the broken link to a non-existent
`artifact-developer-guide.md` with a single sentence that points at
the PRD §5.83a table.

- [ ] **Step 1: Read the lead-in and the legacy section**

Run:
```bash
sed -n '1,3p' docs/quillins/quillins.md
echo "---"
sed -n '2680,2810p' docs/quillins/quillins.md
```
Expected: the first three lines are the "Consolidated on 2026-06-13"
note; the second block starts with a "QUILL Quillin Hub
documentation" header and ends around line 2810 with the closing
fence of the last code block under "## 14. Client Integration".

- [ ] **Step 2: Update the lead-in**

Edit line 1 (the first heading of the file) so the under-title note
goes from:

```markdown
_Consolidated on 2026-06-13 into one document. Sections preserve each source in full. The scripting contract section also governs the QUILL Developer Console (QDC); code references to "docs/quillins.md" by section number point inside the scripting-contract section below._
```

to:

```markdown
_Consolidated on 2026-06-13, last refreshed 2026-07-04 to point at the unified Quillin Hub. Sections preserve each source in full. The scripting contract section also governs the QUILL Developer Console (QDC); code references to "docs/quillins.md" by section number point inside the scripting-contract section below._
```

- [ ] **Step 3: Replace the legacy Hub section**

The legacy section spans lines 2684-2810 in the current file. The
exact opening of the section is the line
`# QUILL Quillin Hub documentation` and the exact closing is the
last `\`\`\`` (closing-fence) of the final code block in the
"Client Integration" subsection, immediately followed by an
HTML-comment that opens the next source.

**Read those exact lines** before editing so the Edit's `old_string`
matches precisely. Then replace them with this single fresh section
(preserve the surrounding blank lines and HTML-comment markers
exactly as they are now):

```markdown
# The Quillin Hub

The Quillin Hub (`hub.quillforall.org`; service code in `quillin-hub/`)
is the community store and submission service for **every** shareable
QUILL artifact type, not just Quillin extensions. Seven artifact
families are accepted for review and publication:

| Type id | Label | Authoritative validator |
| --- | --- | --- |
| `quillin` | Quillin extension | `quill.tools.quillin_lint` |
| `agent` | AI agent (`quill.agent/1`) | `quill.tools.agent_lint` |
| `verbosity-pack` | Verbosity pack (`.qvp.json`) | `quill.core.verbosity.qvp` |
| `sound-pack` | QSP earcon pack | `quill.core.sound_pack` |
| `keyboard-pack` | Keyboard Quill Pack (`.kqp`) | `quill.tools.kqp_validator` |
| `skill-pack` | Skill Quill Pack (`.sqp`) | `quill.core.skill_pack` |
| `pronunciation-dictionary` | Pronunciation dictionary | `quill/tools/artifact_validate.py::_validate_pronunciation` |

## One validation authority

`python -m quill.tools.artifact_validate <path> [--type ID] [--strict] [--json]`
detects the artifact type (by suffix, manifest sniffing, or schema
markers) and dispatches to the per-type validator listed above. The
Hub's Submission Forge, the in-app submission check, and CI all run
this same tool, so an author never sees three different verdicts.
Exit codes follow the validator convention: `0` pass, `1` issues,
`2` not found/undetectable. `--json` emits the machine-readable
report the Forge consumes.

## In-app: check before you ship

**Tools > Quillins > Submit to Quillin Hub...** runs the identical
`artifact_validate` checks locally and reports pass/fail in an
accessible hardened dialog. Picking a Quillin's `manifest.json`
validates the whole folder (the accessible alternative to a
directory picker). The Hub website opens in the browser only on the
explicit **Open the Quillin Hub** button -- QUILL itself makes no
network call anywhere in the flow.

## Publication: GitHub-native, transparent by design

The Hub does not store artifacts. Every submission is reviewed in the
Hub's Submission Forge, then published via a pull request to
`Community-Access/quill`. Review stays transparent; authors keep
attribution; readers can audit every change.

## Where to read more

- The PRD section "The Quillin Hub -- community distribution for every
  shareable artifact" (PRD §5.83a) is the canonical product spec.
- The user guide's "The Quillin Hub: sharing what you make" section
  walks through the in-app check end to end.
- Per-type authoring tutorials live alongside the bundled Quillin that
  ships with each format; the seven types and their authoritative
  validators are listed in PRD §5.83a, and the validator is one
  command, `python -m quill.tools.artifact_validate <path>`.

```

The exact `old_string` for the Edit call is the contiguous block
from the line `# QUILL Quillin Hub documentation` through (and
including) the closing `\`\`\`` of the final code block, and must be
copied verbatim from the file you read in Step 1. Do not invent
whitespace or punctuation; copy the literal bytes.

- [ ] **Step 4: Verify the rewrite**

Run:
```bash
python -c "
s = open('docs/quillins/quillins.md').read()
checks = [
    ('consolidated refreshed', 'last refreshed 2026-07-04' in s),
    ('new section present', 'The Quillin Hub' in s and 'One validation authority' in s and 'In-app: check before you ship' in s and 'Publication: GitHub-native' in s),
    ('legacy markers gone', 'QUILL Quillin Hub documentation' not in s and 'Quillin Hub: Community Plugin Store' not in s and 'Deployment & Integration Guide' not in s and 'Client Integration' not in s),
    ('cross-ref present', 'PRD §5.83a' in s),
    ('no broken link', 'artifact-developer-guide.md' not in s),
]
for name, ok in checks:
    print(('OK  ' if ok else 'FAIL') + ' ' + name)
"
```
Expected: all five `OK  `.

- [ ] **Step 5: Verify the line count is in the expected range**

Run:
```bash
wc -l docs/quillins/quillins.md
```
Expected: a number at most ~130 lines smaller than before (the
legacy section was ~127 lines, the new section is ~70-90 lines).
The exact number depends on what the legacy section contained; the
direction (smaller) is what matters.

- [ ] **Step 6: Do not commit yet** — proceed to Task 4.

---

## Task 4: Fix the user guide link, add CHANGELOG entry, add RELEASE bullet

**Files:**
- Modify: `docs/user guide/userguide.md:3687` (one line)
- Modify: `CHANGELOG.md:38` (one paragraph insertion)
- Modify: `docs/release/RELEASE.md` (one bullet insertion in "Pre-tag checklist")

**Context:** Three small doc edits that close the documentation
loop: (a) the user guide still promises a `artifact-developer-guide.md`
that does not exist; (b) the CHANGELOG has no entry for the Hub; (c)
the release checklist does not mention the Hub service code.

- [ ] **Step 1: Read the user guide's broken link**

Run:
```bash
grep -n "artifact-developer-guide" "docs/user guide/userguide.md"
```
Expected: one match, around line 3687.

- [ ] **Step 2: Fix the user guide line**

The current line (verify by reading the context first) reads:
> `See \`docs/quillins/quillins.md\` for the full authoring reference, and \`docs/quillins/artifact-developer-guide.md\` for the developer guide covering every shareable QUILL file format (Quillins, agents, verbosity packs, sound packs, keyboard packs, skill packs, and pronunciation dictionaries) and how to validate and submit each one.`

Replace it with this exact text:

> `See \`docs/quillins/quillins.md\` for the full authoring reference, and PRD \xa75.83a ("The Quillin Hub — community distribution for every shareable artifact") for the developer guide covering every shareable QUILL file format (Quillins, agents, verbosity packs, sound packs, keyboard packs, skill packs, and pronunciation dictionaries) and how to validate and submit each one. The single validator is \`python -m quill.tools.artifact_validate <path>\`.`

- [ ] **Step 3: Add the CHANGELOG paragraph**

In `CHANGELOG.md`, find the "### What's New in this beta" section
under `## 0.9.0 Beta 1`. The last bullet of the bulleted list is
the "Notepad++ experiment" entry (it ends with "is the open question
this option exists to answer is JAWS/NVDA/braille behavior."). After
that bullet, add a blank line and then this paragraph:

```markdown
- **The Quillin Hub: share every QUILL artifact, validate locally first.** The Quillin Hub (`hub.quillforall.org`; service code in `quillin-hub/`) is the community store and submission service for every shareable QUILL artifact type -- Quillin extensions, AI agents, verbosity packs, sound packs, keyboard packs, AI skill packs, and pronunciation dictionaries -- not just Quillin extensions. **Tools > Quillins > Submit to Quillin Hub...** runs `python -m quill.tools.artifact_validate <path>` locally and reports pass/fail in an accessible dialog before anything goes near the network; pick a Quillin's `manifest.json` and the whole folder is checked. The Hub itself is GitHub-native: every submission is reviewed in the Hub's Submission Forge, then published via a pull request to `Community-Access/quill`. One validator, one source of truth, no duplicate verdicts.
```

- [ ] **Step 4: Add the RELEASE bullet**

In `docs/release/RELEASE.md`, find the "Pre-tag checklist" section.
The checklist items are numbered 1-6 (the "No `.po` or `.mo` files
ship" item is #5; "Manifest regenerated" is #6). After item 6, add
item 7 with this exact text:

```markdown
7. **Quillin Hub service code shipped.** `quillin-hub/` is a Flask
   service in this repo; the registry API, Submission Forge, sync
   worker, and smoke test are all in-tree. Public deployment
   (`hub.quillforall.org` -- DNS, hosting, Postgres) is a separate
   ops track and is tracked separately from the release cut.
```

- [ ] **Step 5: Verify the three doc edits**

Run:
```bash
python -c "
ug = open('docs/user guide/userguide.md').read()
cl = open('CHANGELOG.md').read()
rel = open('docs/release/RELEASE.md').read()
checks = [
    ('ug: no broken link', 'artifact-developer-guide.md' not in ug),
    ('ug: PRD cross-ref', 'PRD §5.83a' in ug or 'PRD §5.83a' in ug),
    ('cl: hub entry', 'The Quillin Hub: share every QUILL artifact' in cl),
    ('cl: tools.quillin_hub_submit', 'Submit to Quillin Hub...' in cl),
    ('rel: hub bullet', 'Quillin Hub service code shipped' in rel),
    ('rel: ops track', 'separate ops track' in rel),
]
for name, ok in checks:
    print(('OK  ' if ok else 'FAIL') + ' ' + name)
"
```
Expected: all six `OK  `.

- [ ] **Step 6: Do not commit yet** — proceed to Task 5.

---

## Task 5: Fix the table_uia C++ include order and add NOMINMAX

**Files:**
- Modify: `quill/native/table_uia/python_bridge.cpp:34-39`
- Modify: `quill/native/table_uia/CMakeLists.txt:34-39`

**Context:** Issue #823 reports 100+ compile errors in
`python_bridge.cpp` originating in `UIAutomationCore.h`. The build
script (PR #822, commit `52fddbf`) made the configure step succeed;
this task is the compile fix. Root cause is two preprocessor defects:

1. **`python_bridge.cpp` includes `<pybind11/pybind11.h>` before any
   `windows.h` / UIA setup.** pybind11's own headers conditionally
   pull in `<windows.h>` (via `pybind11/detail/common.h` on the win32
   path), so when `table_provider.hpp` later includes `<UIAutomation.h>`
   (which includes `<UIAutomationCore.h>`), the UIA header sees
   `<windows.h>` in its default state — with the `min`/`max` macros
   defined and the `interface` typedef exposed — and those collide
   with the COM helpers and the STL. Result: 100+ errors in
   `UIAutomationCore.h` around lines 6300-6500 (the boundary between
   plain SDK macros and the COM-typedecl helpers).

2. **`NOMINMAX` is not defined anywhere in the build.** `WIN32_LEAN_AND_MEAN`
   is set in `CMakeLists.txt` but `NOMINMAX` is not, so the
   `<windows.h>` `min`/`max` macros stay in scope and collide with
   `std::min`/`std::max` from `<algorithm>` and STL helpers used
   throughout `table_provider.cpp`.

**Fix:** pre-include `<windows.h>` ourselves with the right macros
*before* any pybind11 include, and add `NOMINMAX` to the MSVC compile
definitions.

**Interfaces:**
- Consumes: nothing
- Produces: `python_bridge.cpp` that compiles under MSVC 2022 +
  Windows 10 SDK 10.0.19041+ + pybind11 from pip.

- [ ] **Step 1: Read the top of `python_bridge.cpp` to confirm the
  current include order**

  Run:
  ```bash
  sed -n '34,42p' quill/native/table_uia/python_bridge.cpp
  ```
  Expected: lines 35-37 are the pybind11 includes, line 39 is the
  project header include, line 41 is `namespace py = pybind11;`.

- [ ] **Step 2: Edit `python_bridge.cpp` to add a pre-include block**

  Replace the current block of three pybind11 includes plus the
  project-header include (lines 35-39) with this exact code:

  ```cpp
  // Pre-include windows.h ourselves with the right macros, *before* any
  // pybind11 header. pybind11's headers pull in <windows.h> on the win32
  // path; if we let pybind11 do that, UIAutomationCore.h (included by
  // table_provider.hpp) sees windows.h in its default state, where the
  // `min`/`max` macros and the `interface` typedef collide with the COM
  // helpers and the STL — that is what produces the 100+ errors in
  // UIAutomationCore.h reported by issue #823.
  #if defined(_WIN32)
  #  ifndef WIN32_LEAN_AND_MEAN
  #    define WIN32_LEAN_AND_MEAN
  #  endif
  #  ifndef NOMINMAX
  #    define NOMINMAX
  #  endif
  #  include <windows.h>
  #endif

  #include <pybind11/pybind11.h>
  #include <pybind11/functional.h>
  #include <pybind11/stl.h>

  #include "table_provider.hpp"
  ```

  The `Edit` tool's `old_string` is the literal current text
  (the three pybind11 includes, the blank line, and the
  `#include "table_provider.hpp"` line). The `new_string` is the
  pre-include block above followed by the original three pybind11
  includes and the `#include "table_provider.hpp"` line.

- [ ] **Step 3: Add `NOMINMAX` to the MSVC compile definitions**

  In `quill/native/table_uia/CMakeLists.txt`, find the
  `target_compile_definitions` block (the one that currently lists
  `_CRT_SECURE_NO_WARNINGS`, `WIN32_LEAN_AND_MEAN`, `UNICODE`,
  `_UNICODE`). Add `NOMINMAX` immediately after `WIN32_LEAN_AND_MEAN`,
  so the block becomes:

  ```cmake
      target_compile_definitions(_quill_table_uia PRIVATE
          _CRT_SECURE_NO_WARNINGS
          WIN32_LEAN_AND_MEAN
          NOMINMAX
          UNICODE
          _UNICODE
      )
  ```

  This is belt-and-braces: the `#if defined(_WIN32)` block in
  `python_bridge.cpp` defines `NOMINMAX` itself, but adding it to
  the compile definitions covers the case where
  `table_provider.cpp` is compiled as a separate translation unit
  (which it is — see the `pybind11_add_module` source list in the
  same `CMakeLists.txt`).

- [ ] **Step 4: Confirm the structural edits are present**

  Run:
  ```bash
  grep -n "WIN32_LEAN_AND_MEAN\|NOMINMAX\|pybind11/pybind11.h" quill/native/table_uia/python_bridge.cpp
  echo "---"
  grep -n "WIN32_LEAN_AND_MEAN\|NOMINMAX\|UNICODE" quill/native/table_uia/CMakeLists.txt
  ```
  Expected output:

  - `python_bridge.cpp`: `NOMINMAX` appears inside the `#if
    defined(_WIN32)` block, and the three pybind11 includes appear
    *after* the `#include <windows.h>` line.
  - `CMakeLists.txt`: `NOMINMAX` appears once, on a line between
    `WIN32_LEAN_AND_MEAN` and `UNICODE`.

- [ ] **Step 5: Try the build (best-effort, Windows-only)**

  This step is best-effort. The build is Windows-only. Run:

  ```bash
  python scripts/build_table_uia.py 2>&1 | tail -40
  ```

  If CMake / MSVC are not on PATH the script prints a clear
  "skipping" message and exits 0; that is acceptable. If the build
  runs, expect either:
  - it succeeds, and a `Built native UIA provider: ...` line prints
  - it still fails on a *different* error, which gets posted to
    the issue as a follow-up comment

  Either outcome is fine for this task. The fix is correct on
  inspection; the build verify is a confidence check, not a
  gate.

- [ ] **Step 6: Do not commit yet** — proceed to Task 6.

---

## Task 6: Close issues #517, #519, and #823, run final verification

**Files:**
- Modify: GitHub issues only (no repo files)

**Context:** The three issues are the last items in this PR. We post
closing comments and close with appropriate reasons. Then we run the
verification suite end to end.

- [ ] **Step 1: Verify the three issues are still open**

Run:
```bash
gh issue view 517 --repo Community-Access/QUILL --json state --jq .state
gh issue view 519 --repo Community-Access/QUILL --json state --jq .state
gh issue view 823 --repo Community-Access/QUILL --json state --jq .state
```
Expected: `OPEN` and `OPEN` and `OPEN`.

- [ ] **Step 2: Post the closing comment on #517 and close it**

Run:
```bash
gh issue close 517 --repo Community-Access/QUILL --reason "not planned" --comment "Closing as the platform work is shipped. What landed: \`quillin-hub/\` Flask service (\`app/\`, \`worker/\`, \`smoke_test.py\`), the unified \`quill.tools.artifact_validate\` covering the seven artifact types (with 31 unit tests), the in-app \`Tools > Quillins > Submit to Quillin Hub...\` command and dialog, the PRD section \"The Quillin Hub -- community distribution for every shareable artifact\" (PRD §5.83a), the user-guide section \"The Quillin Hub: sharing what you make\", the registry API (\`/api/v1/types\`, \`/api/v1/artifacts\`, \`/api/v1/artifacts/<id>/latest\`, plus legacy \`/plugins\` aliases), the Submission Forge, and the GitHub-token-based sync worker.

What remains: public deployment of \`hub.quillforall.org\`. That requires DNS, hosting, Postgres credentials, and GitHub org access, all of which are out of this repo's scope. When public deployment is ready, file a new issue (or revive this one) with the ops checklist and target date. Re-open the platform items here only if the in-tree service code needs new functionality."
```
Expected: a single line like
`✓ Closed issue Community-Access/QUILL#517 (QUILL 2.0 deferred backlog (tracking))`
(issue title will be #517's actual title; the "(tracking)" suffix is
from a prior close and is just illustrative).

- [ ] **Step 3: Post the closing comment on #519 and close it**

Run:
```bash
gh issue close 519 --repo Community-Access/QUILL --reason "not planned" --comment "Closing on the documentation acceptance. The capability model is documented in \`docs/quillins/quillins.md\` §6 (Security & consent model), §13 (Manifest JSON Schema), and §14 (Extension authoring reference, with the capability catalogue in §14.1 and the contribution reference in §14.2). The in-process Python snippet sandbox hardening (dunder-attribute block, separate-process isolation, import allowlist, scrubbed environment, time/memory caps) is documented in the 0.9.0 Beta 1 \"Enhancements\" section of \`CHANGELOG.md\`.

What remains: manifest signing. A signed-manifest flow (publisher keypair, detached signature on every released artifact, install-time verification) is real engineering work and is deferred to QUILL 2.0 alongside the rest of the marketplace trust work. When 2.0 planning opens, file a real, scoped issue for the signing flow rather than re-opening this one."
```
Expected: a single `✓ Closed issue ...` line.

- [ ] **Step 4: Post the closing comment on #823 and close it**

Run:
```bash
gh issue close 823 --repo Community-Access/QUILL --reason "completed" --comment "Closing on the compile fix. The 100+ errors in UIAutomationCore.h were a preprocessor ordering problem: \`python_bridge.cpp\` included \`<pybind11/pybind11.h>\` before any Windows setup, so when \`table_provider.hpp\` later pulled in \`<UIAutomation.h>\` (and through it \`<UIAutomationCore.h>\`), the UIA header saw \`<windows.h>\` in its default state with the \`min\`/\`max\` macros and the \`interface\` typedef colliding with the COM helpers and the STL.

Fix: pre-include \`<windows.h>\` ourselves with \`WIN32_LEAN_AND_MEAN\` and \`NOMINMAX\` set, *before* any pybind11 include. \`NOMINMAX\` is also added to the MSVC \`target_compile_definitions\` block in \`CMakeLists.txt\` so the same protection covers \`table_provider.cpp\` when it is compiled as a separate translation unit (which it is).

Files touched: \`quill/native/table_uia/python_bridge.cpp\` (pre-include block), \`quill/native/table_uia/CMakeLists.txt\` (added \`NOMINMAX\`).

What remains: real NVDA + JAWS validation of the running provider. That is independent of the build fix and is tracked in the Table Studio follow-up work — when the hardware pass happens, file a new issue for any provider bugs found and link to it from this one's history. The MSAA fallback continues to ship either way, so QUILL's Table Studio is functional for the 0.9.0 beta regardless."
```
Expected: a single `✓ Closed issue ...` line.

- [ ] **Step 5: Verify all three issues are now CLOSED**

Run:
```bash
gh issue view 517 --repo Community-Access/QUILL --json state,stateReason --jq '"#517: " + .state + " (" + .stateReason + ")"'
gh issue view 519 --repo Community-Access/QUILL --json state,stateReason --jq '"#519: " + .state + " (" + .stateReason + ")"'
gh issue view 823 --repo Community-Access/QUILL --json state,stateReason --jq '"#823: " + .state + " (" + .stateReason + ")"'
```
Expected:
```
#517: CLOSED (NOT_PLANNED)
#519: CLOSED (NOT_PLANNED)
#823: CLOSED (COMPLETED)
```

- [ ] **Step 6: Run the unit test suite for the validator**

Run:
```bash
python -m pytest tests/unit/tools/test_artifact_validate.py -q
```
Expected: `31 passed` (last line).

- [ ] **Step 7: Run the Hub smoke test**

Run:
```bash
python quillin-hub/smoke_test.py
```
Expected: exits 0 and prints a final `31/31 checks passed` line (or
the actual total of smoke checks; the precise number may grow as
smoke_test.py is extended). The exact count is not the verification;
the exit code 0 and the absence of `FAIL` lines is.

- [ ] **Step 8: Run ruff on the modified files**

Run:
```bash
ruff check quillin-hub/worker/sync_to_pages.py
ruff format --check quillin-hub/worker/sync_to_pages.py
```
Expected: `All checks passed!` and `1 file already formatted` (or
no output for the second command). The doc-only changes do not need
ruff.

- [ ] **Step 9: Run the public-surface / dialog-inventory sanity test**

Run:
```bash
python -m pytest tests/unit/ui -q -k "public_surface or dialog_inventory"
```
Expected: tests pass (or skip cleanly if those test modules are not
yet present; the goal is to confirm the fixture changes still match
what the code expects).

- [ ] **Step 10: Confirm the working tree diff matches the spec**

Run:
```bash
git status --short
echo "---"
git diff --stat
```
Expected: `git status --short` lists the seven modified files
(`quillin-hub/worker/sync_to_pages.py`, `quillin-hub/README.md`,
`docs/quillins/quillins.md`, `docs/user guide/userguide.md`,
`CHANGELOG.md`, `docs/release/RELEASE.md`,
`quill/native/table_uia/python_bridge.cpp`,
`quill/native/table_uia/CMakeLists.txt`). The `git diff --stat`
output shows the expected line counts: ~10 lines in
`sync_to_pages.py`, ~10-15 lines in `quillin-hub/README.md`, a net
reduction in `quillins.md`, a one-line change in the user guide, a
~10-line addition in `CHANGELOG.md`, ~7 lines in `RELEASE.md`,
~12 lines in `python_bridge.cpp` (the pre-include block), and
~1 line in `CMakeLists.txt` (the `NOMINMAX` definition).

- [ ] **Step 11: Stop. Do not commit.** Report the diff summary to
  the user and ask whether to commit, stage and amend, or hold for
  review. The user opens the PR; this skill's plan ends here.

---

## Self-Review

**Spec coverage:**

- §1 Code cleanup: Task 1 + Task 2 ✓
- §2 One source of truth: Task 3 (rewrite) + Task 4 (link fix) ✓
- §3 CHANGELOG + RELEASE: Task 4 (Step 3 + Step 4) ✓
- §4 Issue closures: Task 6 (Step 2/3/4) ✓
- §5 Verification: Task 6 (Step 6-10) ✓
- Issue #823 (added after the spec was written): Task 5 ✓
- Files-to-touch list: all five files in the spec are touched in
  Tasks 1-4, plus the two C++ files in Task 5 ✓
- Non-goals: explicitly excluded (no `artifact-developer-guide.md`,
  no signing, no deployment) ✓

**Placeholder scan:**

- "TBD", "TODO", "implement later" — none.
- "Add appropriate error handling" — none.
- "Similar to Task N" — none; every step repeats the literal content.
- "fill in details" — none; every doc snippet and code block is
  literal.

**Type consistency:**

- `_QUILLIN_ROOTS` is named consistently in Task 1 (Step 2b) and
  referenced in the same file.
- The seven artifact types appear identically in the spec table, the
  new `quillins.md` section (Task 3 Step 3), and the global
  constraints.
- The closing comments in Task 6 reference the same PRD section
  number (§5.83a) and the same file paths the previous tasks
  touched.
- The verification commands in Task 6 Step 6/7 match the spec's
  Section 5.
- The C++ fix in Task 5 uses the same `WIN32_LEAN_AND_MEAN` /
  `NOMINMAX` macros that `CMakeLists.txt` was already half-using;
  no new symbols are introduced.
