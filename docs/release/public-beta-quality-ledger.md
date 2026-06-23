# QUILL Public Beta Quality Ledger

Living record of the public-beta quality pass. The product name is **QUILL**
(no rename); any "TINDRA" naming is a future, not-yet-applied plan and is out of
scope here.

This ledger is iterative. It is seeded with the work verified in the current pass
plus the baseline gate state; it is not a claim that the entire repository has
been exhaustively re-audited. Sections marked "Deferred / next wave" are honest
about what has not yet been done.

## Reusable wave prompt (run this for each audit wave)

This is the distilled, repo-tuned instruction set for running one focused wave of
the quality/accessibility pass. It is an improved version of the original master
brief: scoped to what is achievable and verifiable in a single pass, and tuned to
this repository's existing gates and conventions. Paste it (optionally with a
"Focus area:" line naming the wave) to drive the next wave.

> **Role.** Act as principal Python/wxPython engineer and accessibility
> specialist for **QUILL**. Investigate, fix, test, and document — do not just
> produce a report.
>
> **Hard constraints.**
> - The product name is **QUILL**. Do **not** rename anything to TINDRA or assume
>   that rename; leave existing QUILL identifiers, paths, and brand strings.
> - Work on a feature branch, never commit to `main`. Make small, logical,
>   attributable commits; do not push, tag, or merge unless explicitly asked.
> - Do not weaken a fix to satisfy a test, broaden `except`, or silence a gate.
>   When a test double is incomplete (e.g. a `_Fake*` missing a method the real
>   widget has), fix the double, not the production change.
> - Respect the existing architecture and import boundaries (core/io are wx-free
>   and strict-typed; ui is gradual-typed).
>
> **Pick a bounded focus area** (one wave): e.g. dialog accessible-naming,
> initial-focus quality, label/field associations, keyboard traps, startup
> init-order, a call-site/attribute audit of one subsystem. Do not attempt the
> whole repo at once; depth over breadth.
>
> **Method.**
> 1. Establish the wave baseline by running the relevant existing gates rather
>    than inventing new ones: `ruff check .`, `ruff format --check .`,
>    `mypy quill/core quill/io` (always scoped — never unscoped), and the targeted
>    pytest suites + tool gates (dialog-inventory, dialog-button-contract,
>    dialog-zorder, announce-gap/GATE-12, a11y-regions, module-size/GATE-11,
>    network-egress, docs-parity). The accessibility infrastructure is strong and
>    gate-backed; aim at what the gates do **not** check (accessible names,
>    initial focus, focus restoration, label associations, verbosity).
> 2. For each finding, determine intent before changing: is it a real defect, an
>    intentional cross-tool pragma, a tested automation handle, or expected
>    behavior? Record reviewed-but-intentional items too.
> 3. Make the minimal correct fix. Prefer native, accessible wx controls and
>    human-readable accessible names (screen readers speak `SetName` verbatim —
>    never snake_case identifiers).
> 4. Run the smallest useful tests after each change; add a regression test where
>    one can be written cleanly (skip brittle full-wx-modal harnesses — record as
>    needs-live-validation instead).
> 5. If a change trips GATE-11 module-size, first try to make the edit net-neutral
>    or extract; only rebaseline with a dated `_rebaseline_<date>` justification
>    comment in `module_size_budgets.json` when growth is genuinely warranted.
> 6. Regenerate docs artifacts for any changed `docs/**/*.md`
>    (`pandoc <f>.md -f gfm -t html5 -s -o <f>.html` and `-t epub3 -o <f>.epub`),
>    and keep this ledger current: running totals, finding IDs
>    (`A11Y-`/`FOCUS-`/`KEY-`/`CALL-`/`PERF-`/`SEC-`/`DOC-`/`TEST-`/`RELEASE-`),
>    severity, root cause, resolution, validation, status.
>
> **Honesty.** Never represent unfinished work as complete. Distinguish
> code-reviewed-against-expected-SR-behavior from live NVDA/JAWS testing. Keep an
> explicit "Deferred / next wave" list. Resolve release blockers before calling
> anything release-ready.
>
> **Deliverables each wave.** The actual fixes + tests; updated ledger; a short
> wave summary (what was audited, found, fixed, deferred); the commands run and
> their results.

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
| Production files modified (this pass) | 19 |
| Test files added/modified | 2 |
| Documentation files modified | 4 (md) + regenerated html/epub |
| Bugs fixed | 1 (L-001 class reviewed; see notes) |
| Features hardened / shipped | 4 (Vosk bundling, Groq, ElevenLabs, Faster Whisper on-demand install) |
| Security/egress items reviewed | 1 (SEC-001, pip subprocess egress documented) |
| Accessibility issues fixed | 13 (6 unnamed tab groups, 7 literal snake_case names) |
| Focus-management issues fixed | 1 (FOCUS-001 wx.html fallback initial focus) |
| Label/field association fixes | 4 dialogs (input controls given accessible names) |
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

## Accessibility audit — wave 2 (initial-focus quality)

Audited which control receives focus when a dialog opens and whether focus is
restored on close.

Verified (strong, no change needed): the centralized `MainFrame._show_modal_dialog`
runs `focus_primary_control(dialog)` so custom `wx.Dialog` surfaces open with focus
on their first real content control — not the OK button — via
`dialog_contract.find_primary_focus_target` over a comprehensive
`_PREFERRED_FOCUS_CLASSES` list (lists, trees, dataviews, text, search, combo,
choice, spin, radio, checkbox, slider). It honors a construction-time
`SetFocus()` and the `_quill_keep_initial_focus` opt-out (e.g. crash recovery,
where the primary button should hold focus). On close it restores focus to the
editor by default (`restore_editor_focus`), and dialogs that should not pass
`restore_editor_focus=False`. Native dialogs are deliberately left to manage their
own focus. The dialog-inventory gate ensures dialogs route through this path.

### FOCUS-001 — wx.html fallback dialog opened on the Close button, not its content
- Severity: Medium. Category: Accessibility (initial focus).
- `preview_dialog.AccessibleHtmlDialog` (the `wx.html.HtmlWindow` fallback used
  when `wx-accessible-webview` is absent) calls the standalone `show_modal_dialog`,
  which does no focus management, and `HtmlWindow` is not a preferred focus class —
  so the dialog opened with focus parked on its default Close button. A
  screen-reader user landed on "Close" instead of the readable content.
- Resolution: store the view and `self._view.SetFocus()` before showing (mirrors
  the already-tested `SidePreview.focus()`), so focus lands on the content.
- Considered and rejected: adding `HtmlWindow`/`Grid` to `_PREFERRED_FOCUS_CLASSES`.
  Only this fallback dialog used `HtmlWindow` as primary content (fixed directly),
  and no modal dialog uses `Grid` as primary content (`csv_grid` is a panel
  surface). Changing the shared list risks shifting initial focus in existing
  multi-control dialogs (the walker returns the first preferred control in tab
  order), so the localized fix is safer.
- Tests: `test_preview_dialog_accessibility.py` (4) still pass; behavioral
  modal-focus assertion needs a full wx.App + shown window, so it is recorded as
  needs-live-validation rather than added as a brittle test.
- Status: Fixed. Needs live NVDA/JAWS confirmation.

## Accessibility audit — wave 3 (label/field associations)

wxPython does not associate a `StaticText` label with the following control the
way HTML `<label for>` does; on some screen readers a field with only a nearby
visual label is announced without a name. The reliable fix is an explicit
`SetName` on each input. Audited input-control naming coverage across the UI and
fixed the clearest gaps.

### A11Y-003 — Input controls labeled only by an adjacent StaticText
- Severity: Medium. Category: Accessibility (screen-reader field naming).
- Fixed across four dialogs:
  - `skill_library_dialog.py`: the Skills list and Description field, and every
    dynamically-built parameter control (`_make_control` now sets the accessible
    name from `param.label or param.name`, covering Choice/CheckBox/SpinCtrl/
    TextCtrl).
  - `assistant_tools.py`: 10 authoring fields across the prompt-authoring and
    model-search dialogs (Title, Tone, Audience, Goal, Template, Prompt, Search).
  - `web_form.py`: every dynamically-rendered form control is named from its
    field label at the single assignment site (`SetName(label)`).
  - `sticky_notes.py`: the Title and Note editors.
- GATE-11: `assistant_tools.py` (+10) and `skill_library_dialog.py` (+6)
  rebaselined with a dated justification (per-control `SetName` lines are not
  extractable); `web_form.py`/`sticky_notes.py` stayed within budget.
- Tests: existing dialog suites pass (assistant_tools 12, web_form/sticky_notes
  24, skill-library routing 1). Naming is structural; no behavioral test added.
- Status: Fixed. Needs live NVDA/JAWS confirmation.
- Continued work (next pass): remaining lower-coverage files (e.g.
  `batch_wizard_pages.py`, read-only display areas in `info_pages.py`) and a
  broader sweep of single-field dialogs.

## Deferred / next wave (not yet done — do not represent as complete)

The master quality-pass scope is repository-wide and multi-session. Not yet
performed in this pass:

- Full test-suite run with a per-test timeout to neutralize TEST-001.
- The accessibility audit is a 6-wave plan: wave 1 (tab-group + control naming),
  wave 2 (initial-focus quality), and wave 3 (label/field associations) are done.
  Remaining: wave 4 (keyboard-trap / tab-order spot checks beyond the gate),
  wave 5 (error-to-field association + announcement), wave 6 (the editor surface
  itself). Plus a label/field continuation sweep of the lower-coverage dialogs.
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
