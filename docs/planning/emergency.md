# QUILL — Emergency Gap List (path to green)

> **Purpose.** A single, prioritized list of the gaps that still stand between
> QUILL and a **green, release-ready state**, ranked most-important first. Compiled
> 2026-06-24 from the user guide, release notes, `QUILL-PRD.md`, `program-tracker.md`,
> `roadmap.md`, `wave-outcomes.md`, the public-beta quality ledger, the live-test
> backlog, and the shipped-feature PRDs' Implementation-Status sections.
>
> **Out of scope (excluded per direction):** the **AI & Agentic** workstream
> (#507–#512, #523/#524, GLOW accessibility-agents #593–#598, the agentic-AI PRD)
> and all **table** work (the native table-studio plan, and the CSV-grid half of
> #514). Also excluded: items explicitly **deferred to QUILL 2.0** and the
> **Linux** platform layer (#520/#565/#589, out of scope).
>
> **Two senses of "green":** (A) tooling green — CI, tests, lint, types, gates;
> (B) release-ready — no known-but-unverified defects, and shipped features are
> actually complete/polished. Both are tracked below.

---

## Tier 0 — Do first (unblocks everything; hours, not days)

1. **Commit and push the in-flight working tree.** There are uncommitted changes
   right now: the retired planning docs (hold-to-dictate, dictation-and-speech,
   braille-mode-backlog, F7 PRDs + artifacts), their reference fixes, the migrated
   follow-ups in this tracker, and this file. Regenerate the changed docs' HTML/EPUB
   (`program-tracker`, `roadmap`, `QUILL-PRD`), run `scripts/check_docs_artifacts.py`,
   and push so `main` CI is green and the tree is clean. *(Blocked momentarily by a
   transient Bash-classifier outage on 2026-06-24; finish the instant it clears.)*
2. **Confirm all CI gates are green on the latest `main` commit.** PR CI, Security
   CI (scoped mypy), Accessibility CI, Docs artifacts. (They were green at
   `46312ff`; re-verify after Tier-0 #1 lands.)

## Tier 1 — Release-blocking verification (B-green): "fixed" but unconfirmed

3. **Live screen-reader sign-off — #526 (DLG-3.8).** The quality ledger lists a
   batch of accessibility fixes marked *"Fixed. Needs live NVDA/JAWS/Narrator
   confirmation"*: A11Y-001 (notebook tab-group names), A11Y-002 (snake_case names),
   A11Y-003 (label association), FOCUS-001 (initial focus), KEY-001 (Tab keyboard
   trap — release-blocker class), A11Y-004 (focus-to-bad-field). Until these are
   walked with JAWS, NVDA, and Narrator, the release is not provably green. **Highest
   single item.**
4. **Live installer smoke on Windows 10/11 — #506 (P0).** Validate a packaged build
   installs, launches, and the first-run wizard runs on clean Win10 and Win11.
5. **Packaged-build validation of the optional speech engines.** RELEASE-001 (Faster
   Whisper install path) and RELEASE-002 (Vosk reachable for packaged users) are
   *"Fixed; needs manual validation on a packaged build."* Verify on the real
   installer, not just from source.
6. **Spell-check preload half — #527 (CQ-11, P1, in-flight).** Close the remaining
   half so first F7 is not slow/cold.
7. **Windows 11 primary menu — #525 (SHELL-3, P1, in-flight).** Finish and verify.

## Tier 2 — Shipped features with rough edges (users can already reach these)

8. ✅ **Speech model-manager: show installable engines with guided install —
   resolved 2026-06-24.** The "Engine & Dependency Status" panel in
   `speech_setup_dialog.py` already lists each optional engine (Faster Whisper,
   Vosk, Kokoro) with Installed / Not-installed status and a guided **Install…**
   button. The remaining gap — a registered-but-not-installed engine (notably
   whisper.cpp without its binary) disappearing from the engine *switcher* — is
   fixed: the dialog is now fed `registry.all()` (not `registry.available()`), and
   switcher entries are labelled "(not installed)" so they stay discoverable and
   reach the install path. Unit-tested (`tests/unit/ui/test_speech_setup_dialog.py`).
9. ◐ **Structured List Studio — Phase 2+ follow-ups** (PRD kept;
   `quill-structured-list-studio-prd.md` §30 Implementation Status). **Done
   (2026-06-24):** nested-list editing (Indent / Outdent / Add child + subtree-aware
   Move up/down, wx-free in `quill/core/lists/nesting.py`, 14 unit tests; the dialog
   shows nesting depth and gates controls structurally), **multiple terms &
   definitions per entry** (terms one-per-line → multiple `<dt>`; definitions
   blank-line-separated → multiple `<dd>`), and **in-place editing of the list under
   the caret** (F2 with no selection detects and replaces the existing list block,
   preserving nesting), and **type-switch conversion with information-loss
   confirmation** (flat↔definition carries content across and confirms before
   dropping structure). *Remaining:* import-from-file/clipboard with preview,
   reparse-and-validate before commit, and the Settings/preset surface. *(This is
   list structure, not the
   excluded table work.)*
10. ◐ **Hold-to-Dictate / Locked Dictation — follow-ups.** **Done (2026-06-24):**
    the dictation *policy* is now user-configurable — `dictation_max_locked_seconds`,
    `dictation_stop_on_focus_loss`, `dictation_intelligent_spacing`, and
    `dictation_min_hold_seconds` are settings (validated, negatives clamped) wired
    into the controller's `DictationConfig` via `_dictation_config()`, replacing the
    hardcoded defaults. *Remaining:* a user-facing settings *panel* for those knobs
    (plus earcon volume / retention / visual indicator); Dictation History +
    interactive startup-recovery prompt; Dictation Review interface for deferred
    inserts; distinct locked-vs-hold earcons; dedicated Dictation menu + one-time
    onboarding.
11. **Watch Folder queue — live repro (#10, live-test).** When `core.watch_folder`
    is enabled the monitor "feels empty"; needs an interactive repro to confirm the
    live queue populates, or a fix.
12. ◐ **Snapshots vs Versions terminology + submenu (#12, live-test) — code half
    resolved 2026-06-24.** The collision is gone: the **notebook** set (Save /
    Restore / Manage) is renamed to **"Versions"** across its menu items, dialog
    titles, prompts, list label, and status/announcement strings; the workspace
    **"Snapshots"** session submenu and the crash-recovery snapshot are left
    untouched. Internal command-ids (`file.save_snapshot`), the `NotebookSnapshot`
    model, and the persisted `snapshots` JSON key stay stable. *Remaining:* the
    empty-submenu render still needs a live repro (manual).

## Tier 3 — Polish & navigation (A-green comfort, not blocking)

13. **Verbosity polish backlog (#405–#504).** The verbosity *engine* shipped; the
    polish set remains. Land the high-value knobs (announcement budgets, repetition
    collapse, typing-echo controls, per-category detail levels, destructive-action
    and undo-available cues) and explicitly fold-in-or-defer the speculative rest so
    the range can close.
14. **Quick Nav enhancements — #513 (P2).** Remaining Quick Nav polish.
15. ✅ **Un-gate structured Word view — #514 (P2) — resolved 2026-06-24.** The open
    path was already fully wired (`_resolve_word_open_mode` → `_create_word_document_tab`,
    `word_open_mode` setting); the only gate was `_word_feature_enabled()` returning
    `False`. Flipped to `True`, so `.doc`/`.docx` now honour the prompt / structured
    / text setting and open in the accessible Word surface. The CSV-grid half stays
    gated (`_csv_feature_enabled`) — that is excluded table work.
16. ✅ **Extract `main_frame_statusbar.py` — #521 (P3, CQ refactor) — resolved
    2026-06-24.** The four remaining status-bar methods (`_set_status`,
    `_set_status_quiet`, `_on_statusbar_context_menu`, `open_status_bar_settings`)
    moved out of `main_frame.py` into the existing `StatusBarMixin`. `main_frame.py`
    ratchets **down** 25957→25727; the statusbar module is re-baselined to receive
    the move. The relocation also surfaced and fixed a latent dialog leak
    (`open_status_bar_settings` never destroyed its `wx.Dialog`). Dialog inventory,
    hardening, banned-pattern, and module-size gates updated and green.

## Tier 4 — Hygiene & architecture (small, cheap green wins)

17. ✅ **L-001: `# noqa: dialog_button_contract` ruff warnings — resolved 2026-06-24.**
    The audit opt-out pragma was respelled from `# noqa: dialog_button_contract` to
    `# dialog_button_contract: exempt` so ruff no longer mis-parses
    `dialog_button_contract` as one of its own rule codes; the gate regex accepts
    both spellings for back-compat, and the gate file's own comments were reworded
    to avoid the literal `# noqa:` token. `ruff check .` is now warning-free.
18. ✅ **wx-in-core anomaly — resolved 2026-06-24.**
    `quill/core/spelling/announcements.py` no longer imports `wx`. It now takes an
    injected one-shot `timer_factory` (the UI passes `wx.CallLater` from
    `spelling_review_dialog.py`; headless/test contexts pass nothing and skip the
    debounced spell-aloud). The `wx`/`wx.*` entries were removed from the mypy
    `ignore_missing_imports` list and the scoped gate (`mypy quill/core quill/io`)
    stays green — core is wx-free again.

## Tier 5 — Larger roadmap (real, but likely beyond "today")

19. **GLOW family — #528–#534 (P1).** Currently `locked_off` (hidden). Decide: finish
    and un-gate for 1.0, or keep hidden and move out of the 1.0 green bar.
20. **Publishing: direct publishing to external platforms — #140.** WordPress and
    other targets (Phase 4). DAISY export already shipped.
21. **Docs & Content backlog — DOC-*, TUT-*, POD-*, CQ-14/23/24 (#535–#564).** User
    tutorials, doc tier-6 items, and content polish.
22. **macOS toward shipping quality — #518 (Phase 5).** Out of the "today" bar but on
    the 1.0 path; Windows remains primary.

---

## Notes

- **Braille (Phases 3/4/6)** is intentionally deferred (tracker #600/#601); the
  shipped P3/P4 work (proofing, validation, back-translation) is done and documented.
  Not a green-state gap.
- **Parakeet** was fully removed 2026-06-24 (provider + BITS-Whisperer gating +
  `[parakeet]` extra); no residual gap.
- Treat Tier 0–1 as the definition of "green to release"; Tiers 2–4 as "green and
  complete"; Tier 5 as roadmap beyond the immediate push.
- **Code green-up status (2026-06-24).** All Tier-4 hygiene items (#17 ruff
  warnings, #18 wx-in-core) and the code-resolvable Tier 2/3 items are done and
  verified: #8 (model-manager installable engines), #12 (notebook Snapshots→
  Versions rename — code half), #15 (un-gate structured Word view), and #16
  (extract the rest of the status-bar surface into `StatusBarMixin`, ratcheting
  `main_frame.py` down and fixing a latent dialog leak). Local gates pass:
  `ruff check .` (warning-free), `ruff format --check`, scoped
  `mypy quill/core quill/io`, the dialog-button-contract / dialog-inventory /
  dialog-hardening / banned-pattern gates, the GATE-11 module-size budget, the
  docs-artifact parity guard, and the UI + tools + speech + spelling unit suites.
  The remaining open items are manual sign-off (Tier 1), the #12 empty-submenu
  repro, and the larger feature backlogs (#9 List Studio Phase 2+, #10 Dictation
  follow-ups, #13 verbosity polish, #14 Quick Nav) — not code-hygiene gaps.
