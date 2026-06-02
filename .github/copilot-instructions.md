# Copilot instructions for this repository

## Repository state

This repository contains the implementation source tree together with the product requirements document under `docs/QUILL-PRD.md` and `docs/QUILL-PRD.html`.

When generating code or task plans, treat the PRD as the source of truth for intended architecture and conventions.

## Build, test, and lint commands

There are no runnable project commands in this repo yet. The PRD defines the expected toolchain and CI commands for the future codebase:

```powershell
# Environment setup
uv python install 3.12
uv sync --all-extras
pre-commit install

# Lint + type-check (planned CI)
ruff check .
ruff format .
mypy quill\core quill\io

# Tests (planned CI)
pytest tests\unit -n auto
pytest tests\integration
pytest tests\a11y
pytest tests\perf

# Single test pattern (pytest)
pytest tests\unit\path\to\test_file.py::test_name
```

## High-level architecture (from PRD)

Quill is designed as a screen-reader-first Windows desktop app in Python + wxPython, with a strict separation between UI, core logic, I/O format handlers, platform bindings, and optional AI providers.

- `quill/core/*`: document model, commands, history, keymap, backups, events, metrics, schemas. No `wx` imports.
- `quill/io/*`: per-format readers/writers and outline emitters. Contract is `read(path) -> Document`, optional `write(doc, path)`, optional `outline(doc)`.
- `quill/ui/*`: wxPython shell/editor/dialogs/palette/status bar; consumes `core` and `io`.
- `quill/platform/windows/*`: Windows-specific APIs (screen-reader bridges, DPAPI, shell integration, single-instance, high-contrast, TTS).
- `quill/ai/*`: provider adapters and safety/consent gating for networked actions.
- `quill/plugins/*`: plugin API + manifest validation (v1.0 loader skeleton).
- `quill/tools/*`: internal CLIs (a11y audit, docs generators, diagnostics helpers).
- `tests/{unit,integration,a11y,perf,fixtures}`: split test strategy reflected in CI.

Concurrency model in the PRD:
- UI thread owns widgets and editor buffer.
- Thread pools handle file I/O and heavier compute.
- `wxasync`-managed asyncio handles HTTP/network operations.
- OCR runs in a separate worker process.
- Cross-thread UI updates marshal through `wx.CallAfter`/`wx.CallLater`.

Persistence model in the PRD:
- User data rooted at `%APPDATA%\Quill\...`
- JSON stores validated by schemas under `quill/core/schemas/`
- Atomic writes via temp file + `os.replace`

## Key conventions to preserve

- Screen-reader-first UI: use stock controls in the writing path (`wx.TextCtrl`, `wx.ListBox`, `wx.Dialog`), avoid custom-drawn editor controls.
- The editor surface is the primary interaction surface and should remain plain-text-first.
- Announcements should report action outcomes consistently (NVDA/JAWS/Narrator parity).
- No silent network calls: all cloud/AI actions are explicit opt-in per action with visible progress and outcome.
- `core` must stay UI-framework-agnostic; keep `wx` imports confined to `quill/ui` and `quill/platform/windows`.
- Do not bypass `io` contracts for new format handlers; add format logic as isolated `io/*` modules.
- Avoid shared mutable-state locking patterns in `core`; follow snapshot/merge worker model described in PRD.
- Keep storage robust: schema-validated JSON, `.bak`/recovery behavior, atomic writes on all persistent stores.
- Type and lint policy from PRD: ruff formatting/lint, strict mypy in `core` + `io`, gradual typing in `ui`.
- Security/privacy defaults are non-negotiable: DPAPI for secrets, no document content in logs, explicit consent gate before outbound document data.

## Dialog, Window, and Accessibility Lessons

Apply these rules to every UI change in `quill/ui/*`:

- Keep parent ownership consistent in dialog layout trees.
	- If controls are parented to `panel = wx.Panel(dialog)`, keep that control tree in a panel sizer and attach the panel to an outer dialog sizer.
	- Do not attach the same root sizer to both panel and dialog.
- Prefer stock controls for instructional content users must read.
	- Use `wx.TextCtrl(..., wx.TE_MULTILINE | wx.TE_READONLY)` or list controls for screen-reader review, not transient message boxes when content is long.
- Avoid mutating menu items while menus are open.
	- Defer menu label/enable/check updates until menu close to avoid focus churn and native menu instability under rapid arrow navigation.
- Treat `wx.CallAfter` as optional in tests and fallback environments.
	- Guard with `getattr(wx, "CallAfter", None)` and provide a synchronous fallback where safe.
- Keep dialog focus behavior predictable.
	- Set explicit default buttons, bind Escape/Close consistently, and return focus to editor after modal close.
- Add focused tests for dialog and menu regressions.

## Cloud coding agent directives (read this first)

When you run as the GitHub Copilot coding agent in the cloud, follow these standing
rules in addition to everything above.

### Mission and honesty

- Drive QUILL 1.0 work (Tier 2 roadmap items in `golden.md` plus all associated
  1.0 work, **including documentation**) toward genuine, tested Done.
- HONESTY IS NON-NEGOTIABLE. Only mark an item Done when it is genuinely complete
  and tested. If an item has a real runtime blocker, leave it honestly
  "In progress" with an accurate note explaining why. Never fabricate Done.
- You run on **Linux**, so `wxPython` cannot be imported. That is expected. Do not
  try to instantiate live wx UI. Validate UI work through the existing bar:
  source-contract tests (read the `.py` file as text and assert wiring
  substrings), the A11Y-4 dialog-contract guard
  (`tests/unit/ui/test_dialog_contract.py`), navigation tests, and the
  public-surface fixture.
- Items that need a real Windows runtime CANNOT be finished in cloud and must stay
  honestly "In progress": OCR-1/OCR-3 (real OCR engine, clipboard, display),
  AI-19 (live device-login endpoint), SET-2 (sensitivity-aware dictation backend),
  AGENT-1 (advisory-only by design). Document them; do not mark them Done.

### Out of scope for 1.0 (do NOT work on these)

- GLOW integrations.
- axe-core / vnu (Nu Html Checker) HTML/CSS/SVG validation.
- BITS Whisperer.

These are deferred to QUILL 2.0 and are already tracked as such in `golden.md`.

### Per-change discipline (every commit / PR)

- Format and lint: `ruff format` then `ruff check` (use `--fix` where safe).
- Strict typing on changed `quill/core` and `quill/io` files: `mypy` must report
  "Success: no issues found". `quill/core` and `quill/io` must stay wx-free.
- Run the targeted `pytest` for what you changed; keep the suite green.
- After editing `golden.md`, regenerate `golden.html` with
  `pandoc -s golden.md -o golden.html` and commit both together.
- If a new public `MainFrame` method is added, regenerate the fixture with
  `python -m quill.tools.ui_surface --write` and stage
  `tests/unit/ui/fixtures/main_frame_public_surface.json`.
- Stage SPECIFIC files only. NEVER `git add -A` (it pulls in `.history/` and
  `uv.lock`). Keep `golden.md`, the living lists, and the tracker totals
  reconciled with each change.
	- Include at least one behavior test (or source-contract test when UI stubs are limited) per bug class.

## Keep dialogs.md current

`dialogs.md` in the repo root is the master manual regression checklist for every
user-facing dialog in QUILL, each mapped to the keyboard command or menu path
that opens it. It must stay a faithful, complete map of the shipped dialogs.

- Whenever you add, remove, rename, or rebind a dialog anywhere under `quill/ui/`
  (including `main_frame.py`, `palette.py`, `assistant_panel.py`,
  `assistant_tools.py`, `ai_model_panel.py`, `style_panel.py`, `sticky_notes.py`,
  `preview_dialog.py`, and `web_form.py`), update the matching row in `dialogs.md`
  in the same change.
- New dialogs are added as a `- [ ]` checklist item in the correct section, with
  the keyboard command (or "via menu" when there is no default keybinding, using
  the literal binding from `quill/core/keymap.py`). Nested dialogs go in the
  nested section noting their parent; startup-only dialogs go in the startup
  section noting their trigger.
- Do not tick checkboxes in `dialogs.md` from code changes. The checkboxes record
  the outcome of a manual regression pass and are ticked by a human tester.
- The checklist is the manual companion to the A11Y-4 machine-enforced dialog
  contract guard; keep both in mind when touching dialog construction.
