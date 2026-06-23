# QUILL Public Beta Quality Ledger

Living record of the public-beta quality pass. The product name is **QUILL**
(no rename); any "TINDRA" naming is a future, not-yet-applied plan and is out of
scope here.

This ledger is iterative. It is seeded with the work verified in the current pass
plus the baseline gate state; it is not a claim that the entire repository has
been exhaustively re-audited. Sections marked "Deferred / next wave" are honest
about what has not yet been done.

## Baseline (gate state)

Captured on the current branch (`main`), dev environment, Python 3.12.

| Gate | Command | Result |
| --- | --- | --- |
| Lint | `ruff check .` | Pass (3 benign cross-tool `# noqa` warnings, see L-001) |
| Format | `ruff format --check .` | Pass after formatting one new file |
| Types (scoped) | `mypy quill/core quill/io` | Pass (298 files, no issues) |
| Egress audit | `tests/unit/tools/test_network_egress_audit.py` | Pass |
| Docs parity | `scripts/check_docs_artifacts.py` | Pass |
| Build dist | `tests/unit/scripts/test_build_windows_distribution.py` | Pass (15) |
| Speech suite | `tests/unit/core/speech/` (subset) | Pass; one Parakeet test hits a `transformers` import timeout in dev (see TEST-001) |

## Running totals

| Metric | Count |
| --- | --- |
| Production files modified (this pass) | 14 |
| Test files added/modified | 2 |
| Documentation files modified | 4 (md) + regenerated html/epub |
| Bugs fixed | 1 (L-001 class reviewed; see notes) |
| Features hardened / shipped | 4 (Vosk bundling, Groq, ElevenLabs, Faster Whisper on-demand install) |
| Security/egress items reviewed | 1 (SEC-001, pip subprocess egress documented) |
| Accessibility issues fixed | 13 (6 unnamed tab groups, 7 literal snake_case names) |
| Tests added | 2 files (`test_cloud_transcribers.py`, `test_engine_install.py`) |
| Remaining known issues | 1 (TEST-001) |
| Intentional legacy QUILL references reviewed | n/a (no rename; QUILL is the name) |

## Findings

### RELEASE-001 — Faster Whisper engine had no path for packaged users
- Severity: Medium. Category: Packaging / feature completeness.
- Component: `scripts/build_windows_distribution.py`, `quill/core/speech/engine_install.py`, `quill/ui/main_frame_speech.py`, `quill/ui/main_frame_menu.py`, `quill/__main__.py`.
- Problem: the shipped installer uses a frozen embeddable Python, so the
  `[fasterwhisper]` extra was unreachable for non-source users. Only whisper.cpp
  was selectable as an offline engine in a packaged build.
- Resolution: added an on-demand installer. **Tools > Speech > Whisperer >
  Download Faster Whisper Engine...** installs it wheel-only
  (`pip install --only-binary=:all: --target <app data>/engine-packs/faster-whisper`)
  into a user-writable folder (no admin), prepended to `sys.path` at startup so
  the engine appears in the Speech Engine chooser. The shipped runtime now keeps
  `pip` (setuptools/wheel still pruned). Blocked in Safe Mode, behind a
  confirmation + progress dialog.
- Tests: `tests/unit/core/speech/test_engine_install.py` (8 cases).
- Status: Fixed. Needs manual validation on a packaged Windows build (a real
  pip-into-target install and engine activation).

### RELEASE-002 — Vosk engine unreachable for packaged users
- Severity: Low. Category: Packaging / accessibility reach.
- Resolution: Vosk's wheel is self-contained (ships libvosk), so it is now in the
  installer's base dependency groups (`DEFAULT_BUNDLED_DEPENDENCY_GROUPS`),
  available out of the box; its ~40 MB model still downloads on first use.
- Status: Fixed. Needs manual validation on a packaged build.

### SEC-001 — pip subprocess egress (Faster Whisper install)
- Severity: Low (informational). Category: Network egress / privacy.
- The on-demand install runs the runtime's pip in a subprocess, which reaches
  PyPI / pythonhosted. The AST egress scanner only sees `urlopen`/`urlretrieve`,
  so this is documented as a manual comment block in
  `quill/tools/network_egress_audit.py` (alongside the PyGithub block). Gated by
  an explicit user action, a confirmation dialog, and Safe Mode; wheel-only.
- Status: Verified / documented.

### L-001 — Three `# noqa: dialog_button_contract` directives warn under ruff
- Severity: Low. Category: Lint hygiene.
- `quill/ui/main_frame_quillins.py:737,754` and `quill/ui/main_frame.py:13178`
  carry `# noqa: dialog_button_contract`. ruff warns because that is not a ruff
  code — but it is an **intentional cross-tool pragma** consumed by the
  `dialog_button_contract` gate (regex `#\s*noqa\s*:\s*dialog_button_contract`).
- Resolution: **Intentional behavior — left unchanged.** Rewriting them would
  break the dialog-button-contract gate. Recorded so a future pass does not
  "fix" it blindly.
- Status: Intentional behavior.

### TEST-001 — Parakeet provider test triggers a slow `transformers` import in dev
- Severity: Low. Category: Test reliability.
- When `transformers` is installed in the environment, running the full
  `tests/unit/core/speech/` set can hang on NeMo's `transformers` import-structure
  scan during a Parakeet test, hitting the suite timeout. Product code is lazy
  (only `find_spec` at startup), so this is a test-harness artifact, not a runtime
  defect; Parakeet is unbundled and source-only.
- Recommended next step: add `@pytest.mark.timeout(...)` to the Parakeet test and
  ensure it never triggers a real heavy import under collection.
- Status: Found (deferred).

## Accessibility audit — wave 1 (dialogs / tab groups)

Baseline: the repo's accessibility gates are strong and green — 38 tests across
dialog-inventory (ShowModal compliance), dialog-focus-routing, dialog-z-order
(no dialog behind a window), announce-gap (GATE-12: every status update has a
screen-reader announcement), and a11y-region keyboard-trap tracking. The audit
therefore targeted what those gates do not check: accessible names.

### A11Y-001 — Notebook tab groups announced generically (no accessible name)
- Severity: Medium. Category: Accessibility (screen-reader naming).
- Several `wx.Notebook` tab groups had no `SetName`, so a screen reader announces
  an unnamed/generic tab group instead of its purpose.
- Fixed (6): `info_pages.py` About dialog (both the main About notebook and the
  "About" tabbed dialog), `status_dialog.py` (Application Status), `word_view.py`,
  `rich_text_surface.py`, `csv_grid.py` (the three alternate document-view
  surfaces), and the main document tab host in `main_frame.py` (now "Open
  documents"). Notebooks that were already named (Settings, AI Hub, Quillin
  prefs, menu-customization, Preferences listbook) were left as-is.
- Tests: existing UI suites for each surface pass; `test_rich_text_surface.py`'s
  `_FakeNotebook` double gained `SetName` (the production change was correct; the
  test double was incomplete).
- Status: Fixed. Needs live screen-reader confirmation (NVDA/JAWS).

### A11Y-002 — Accessible names set to snake_case identifiers (spoken verbatim)
- Severity: Medium. Category: Accessibility (screen-reader naming).
- Controls used `SetName("status_overview")`-style identifiers as their accessible
  name; a screen reader speaks them literally ("status underscore overview").
- Fixed (7): `status_dialog.py` (5 controls -> "Status overview", "Tasks and
  downloads", "Features", "Recent actions", "Refresh"), `verbosity_prefs.py`
  status line ("Verbosity status", test assertion updated to match), and the
  `info_pages` About notebook name.
- Reviewed — intentional (left unchanged): `simple_open_dialog.py` and
  `crash_report_dialog.py` set a snake_case **dialog window name** that is a
  tested automation handle (`test_main_frame_simple_open.py` asserts
  `GetName() == "simple_open"`); a dialog's spoken accessible name is its title,
  not the window name, so these are not literal-readout defects.
- Status: Fixed (controls) / Intentional (dialog handles).

## Deferred / next wave (not yet done — do not represent as complete)

The master quality-pass scope is repository-wide and multi-session. Not yet
performed in this pass:

- Full test-suite run with a per-test timeout to neutralize TEST-001.
- The accessibility audit continues: wave 1 (tab-group + control naming) is done;
  still to do — initial-focus quality per dialog, label/field associations,
  keyboard-trap spot checks beyond the gate, and the editor surface (Sections 11,
  24 of the brief).
- The startup/shutdown initialization-order hardening review (Section 9).
- The call-site / attribute-contract repository audit (Section 7).
- The performance and visual-polish passes (Sections 13, 14).
- The documentation audit beyond the release notes / CHANGELOG touched here.

## Validation performed this pass

- `ruff check` on all changed files: pass.
- `ruff format` applied to the one new module.
- `python -m pytest tests/unit/core/speech/test_engine_install.py tests/unit/core/speech/test_cloud_transcribers.py tests/unit/core/speech/test_quillin_providers.py tests/unit/tools/test_network_egress_audit.py`: 32 passed.
- `python -m pytest tests/unit/ui/test_main_frame_menu_contract.py tests/unit/ui/test_main_frame_menu_label_accelerator.py tests/unit/ui/test_speech_commands.py`: 11 passed.
- `python -m pytest tests/unit/scripts/test_build_windows_distribution.py`: 15 passed.
- `scripts/check_docs_artifacts.py`: pass.
