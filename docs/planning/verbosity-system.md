# QUILL Verbosity System — Consolidated Design Archive

> **Consolidated workstream design spec / reference archive.** This file gathers the
> full text of every issue in this workstream so the design reads end to end in one
> place. Status lives in the [`roadmap.md`](roadmap.md) plan of record (§1.1).
>
> **Verbosity is complete for 1.0** (roadmap §1.1): the engine, the eleven `verbosity_*`
> UI surfaces, the runtime modes (Quiet / Meeting / Quiet-Undo), the status-query
> commands (Where am I? / What changed? / Speak Status), mastery step-down, history,
> the explain trace, Safe Mode/reset, QVP packs + library + preview lab, task-aware
> profiles, import/export, destructive-action confirmation, and **announcement
> anti-spam** (repetition collapse + budget) have all shipped.
>
> What remains is the **speculative slice of the polish backlog** (#405–#504),
> **deferred to 2.0** (roadmap §5). This file is now the **reference well** for those
> items — issue numbers are preserved as section anchors; the screen-reader-redundant
> ideas are flagged "recommend do not build."

The Verbosity System is QUILL's screen-reader-first announcement engine: profiles, channels, per-verb token templates, Quiet/Meeting modes, a QVP pack format, and a large UX-polish surface. The core engine and UI shipped in the 0.7.0 line; the remaining polish set is the multi-item backlog below.


## Triage summary (product judgment)

- **Core (do first, highest value):** #271 parent and Sub-PRs #361–#366 (channels, profiles, tokens, parser; engine + Quiet/Meeting/mastery/history/explain; QVP + library + preview; preferences/token-editor UI; call-site migration; the §53 polish set). The §5–§46 design sections (#367–#404) are the spec these implement against.
- **Valuable knobs worth keeping in scope:** repetition collapse (#409), announcement budget (#408), typing-echo controls (#411), 'Where am I?' (#422), 'What changed?' (#423), error coaching (#416), per-category detail levels (#418), Markdown/Code-aware verbosity (#427/#428), destructive-action + undo-available warnings (#501/#502).
- **Speculative long tail (defer or cut):** much of addenda #38–#100 (community-pack diffing, pack-author mode, time-based quiet hours, multi-monitor presentation safety, abbreviation dictionaries, etc.). These are real ideas but should not gate a release; keep them here as a reference well to draw from, not as open work.


## Contents (146 archived issues)

- [#271](#271-) — [P0] Verbosity rebuild: implement per-verb token registry from docs/planning/verbosity.md
- [#361](#361-) — [Verbosity] Sub-PR 1.1 — Core foundation: channels, profiles, tokens, parser
- [#362](#362-) — [Verbosity] Sub-PR 1.2 — Engine, quiet, meeting, mastery, history, explain, safe mode
- [#363](#363-) — [Verbosity] Sub-PR 1.3 — QVP, library, preview, schema validation
- [#364](#364-) — [Verbosity] Sub-PR 1.4 — UI: preferences, token editor, library, history, preview lab, about dialog
- [#365](#365-) — [Verbosity] Sub-PR 1.5 — Engine call-site migration, keymap, main_frame wiring
- [#366](#366-) — [Verbosity] Sub-PR 1.6 — Section 53 addendum (100-item UX polish)
- [#367](#367-) — Verbosity: §5 Locked design decisions (12 decisions)
- [#368](#368-) — Verbosity: §6 Profile model (Beginner / Normal / Expert / Quiet + CustomProfile)
- [#369](#369-) — Verbosity: §7 Channel system (Channel enum + routing)
- [#370](#370-) — Verbosity: §8 Sound design (master + per-event gating)
- [#371](#371-) — Verbosity: §9 Quiet Mode (controller + chords)
- [#372](#372-) — Verbosity: §10 Meeting Mode (controller + chords)
- [#373](#373-) — Verbosity: §11 Quiet Undo (Ctrl+Shift+Z)
- [#374](#374-) — Verbosity: §12 Token system (TokenSpec + filters)
- [#375](#375-) — Verbosity: §13 Template validation (strict allowlist + type checking)
- [#376](#376-) — Verbosity: §14 Data ordering model + editor
- [#377](#377-) — Verbosity: §15 Verb registry (VerbSpec + initial verb catalog)
- [#378](#378-) — Verbosity: §16 Per-verb preferences UI
- [#379](#379-) — Verbosity: §17 Verbosity Preferences UI (top-level panel)
- [#380](#380-) — Verbosity: §18 Token editor UI (Simple + Advanced)
- [#381](#381-) — Verbosity: §19 Templates library (CRUD + cross-verb behavior)
- [#382](#382-) — Verbosity: §20 QVP file format (`.qvp.json` schema)
- [#383](#383-) — Verbosity: §21 QVP install flow (file picker + validate + announce)
- [#384](#384-) — Verbosity: §22 Profile preview on switch (replay last 3)
- [#385](#385-) — Verbosity: §23 Preview Lab (scenario-based renderer)
- [#386](#386-) — Verbosity: §24 Announcement history (record + replay + filter)
- [#387](#387-) — Verbosity: §25 Why did QUILL say that? (explanation trace)
- [#388](#388-) — Verbosity: §26 Too Much / Too Little / Just Right (feedback tuning)
- [#389](#389-) — Verbosity: §27 Mastery-based step down (per-verb threshold + 10-second timeout)
- [#390](#390-) — Verbosity: §28 Channel-specific templates (speech / braille / visual / sound_event)
- [#391](#391-) — Verbosity: §29 Safe Mode and Reset (per-verb / per-chord / profile / QVP)
- [#392](#392-) — Verbosity: §30 Import / Export (`.quill-verbosity-profile.json`)
- [#393](#393-) — Verbosity: §31 Task-aware profiles (Markdown / Code / Braille / Review / etc.)
- [#394](#394-) — Verbosity: §32 First-run Verbosity Tour (setup wizard page)
- [#395](#395-) — Verbosity: §33 Keyboard Manager integration (Verbosity tab)
- [#396](#396-) — Verbosity: §34 Hotkey plan (chords + conflict resolution)
- [#397](#397-) — Verbosity: §35 Storage (VerbositySettings + verbosity_custom.json)
- [#398](#398-) — Verbosity: §40 Accessibility requirements (screen-reader-first contract)
- [#399](#399-) — Verbosity: §41 Testing plan (core + UI + golden)
- [#400](#400-) — Verbosity: §42 Golden announcement tests (tests/golden/verbosity/)
- [#401](#401-) — Verbosity: §43 Documentation plan (PRD + userguide + CONTROL_REFERENCE + dev docs)
- [#402](#402-) — Verbosity: §44 Manual smoke test (golden path steps 1-65)
- [#403](#403-) — Verbosity: §45 Verification commands (gates that must be green)
- [#404](#404-) — Verbosity: §46 Order of work (46 steps; sub-PRs follow this)
- [#405](#405-) — Verbosity addendum #1: Settings Should Have Three Layers
- [#406](#406-) — Verbosity addendum #2: Searchable Settings
- [#407](#407-) — Verbosity addendum #3: Verbosity Recipes
- [#408](#408-) — Verbosity addendum #4: Announcement Budget
- [#409](#409-) — Verbosity addendum #5: Repetition Collapse
- [#410](#410-) — Verbosity addendum #6: Screen Reader Handoff Mode
- [#411](#411-) — Verbosity addendum #7: Typing Echo Controls
- [#412](#412-) — Verbosity addendum #8: Indentation and Whitespace Verbosity
- [#413](#413-) — Verbosity addendum #9: Selection Verbosity Knobs
- [#414](#414-) — Verbosity addendum #10: Clipboard Verbosity Knobs
- [#415](#415-) — Verbosity addendum #11: Search Result Verbosity Knobs
- [#416](#416-) — Verbosity addendum #12: Error Coaching
- [#417](#417-) — Verbosity addendum #13: “Details on Demand”
- [#418](#418-) — Verbosity addendum #14: Announcement Detail Levels Per Category
- [#419](#419-) — Verbosity addendum #15: Boundary Announcements
- [#420](#420-) — Verbosity addendum #16: Progress Announcement Controls
- [#421](#421-) — Verbosity addendum #17: Mode Change Announcements
- [#422](#422-) — Verbosity addendum #18: “Where Am I?” Command
- [#423](#423-) — Verbosity addendum #19: “What Changed?” Command
- [#424](#424-) — Verbosity addendum #20: “Speak Status Bar” Command
- [#425](#425-) — Verbosity addendum #21: Braille-Specific Knobs
- [#426](#426-) — Verbosity addendum #22: Punctuation and Symbol Profiles
- [#427](#427-) — Verbosity addendum #23: Markdown-Aware Verbosity
- [#428](#428-) — Verbosity addendum #24: Code-Aware Verbosity
- [#429](#429-) — Verbosity addendum #25: Compare/Diff Verbosity
- [#430](#430-) — Verbosity addendum #26: File Operation Verbosity
- [#431](#431-) — Verbosity addendum #27: Encoding and Line Ending Verbosity
- [#432](#432-) — Verbosity addendum #28: Notification Priority Levels
- [#433](#433-) — Verbosity addendum #29: Verbosity Rules Engine
- [#434](#434-) — Verbosity addendum #30: Per-Workspace Verbosity
- [#435](#435-) — Verbosity addendum #31: Per-File Verbosity
- [#436](#436-) — Verbosity addendum #32: Temporary Verbosity Boost
- [#437](#437-) — Verbosity addendum #33: Hold-to-Explain
- [#438](#438-) — Verbosity addendum #34: Training Mode
- [#439](#439-) — Verbosity addendum #35: Contextual Help Hooks
- [#440](#440-) — Verbosity addendum #36: Friendly Names for Technical Concepts
- [#441](#441-) — Verbosity addendum #37: “Confidence Check” Wizard
- [#442](#442-) — Verbosity addendum #38: Community Pack Preview and Diff
- [#443](#443-) — Verbosity addendum #39: QVP Trust Labels
- [#444](#444-) — Verbosity addendum #40: QVP “Copy as User Template”
- [#445](#445-) — Verbosity addendum #41: Verbosity Conflict Checker
- [#446](#446-) — Verbosity addendum #42: “Explain My Settings”
- [#447](#447-) — Verbosity addendum #43: Export Support Bundle
- [#448](#448-) — Verbosity addendum #44: Privacy Controls
- [#449](#449-) — Verbosity addendum #45: Private Document Mode
- [#450](#450-) — Verbosity addendum #46: Speech Rate and Pause Knobs
- [#451](#451-) — Verbosity addendum #47: Announcement Queue Policy
- [#452](#452-) — Verbosity addendum #48: “Last Important Announcement”
- [#453](#453-) — Verbosity addendum #49: Earcons With Text Equivalents
- [#454](#454-) — Verbosity addendum #50: Learn Sounds Mode
- [#455](#455-) — Verbosity addendum #51: Announcement Favorites
- [#456](#456-) — Verbosity addendum #52: “Pin This Status”
- [#457](#457-) — Verbosity addendum #53: Smart Status Rotation
- [#458](#458-) — Verbosity addendum #54: “Speak Current Template”
- [#459](#459-) — Verbosity addendum #55: Token Help on Demand
- [#460](#460-) — Verbosity addendum #56: Template Examples Per Token
- [#461](#461-) — Verbosity addendum #57: Pack Author Mode
- [#462](#462-) — Verbosity addendum #58: Built-In Sample QVPs
- [#463](#463-) — Verbosity addendum #59: “Make This My Default”
- [#464](#464-) — Verbosity addendum #60: Bulk Editing
- [#465](#465-) — Verbosity addendum #61: Undo for Settings Changes
- [#466](#466-) — Verbosity addendum #62: Settings Change History
- [#467](#467-) — Verbosity addendum #63: “Test My Current Settings”
- [#468](#468-) — Verbosity addendum #64: Recommended Settings Suggestions
- [#469](#469-) — Verbosity addendum #65: Accessibility Persona Setup
- [#470](#470-) — Verbosity addendum #66: Command Discovery Announcements
- [#471](#471-) — Verbosity addendum #67: “Do Not Say This Again”
- [#472](#472-) — Verbosity addendum #68: Per-Announcement Suppression
- [#473](#473-) — Verbosity addendum #69: Announcement Labels
- [#474](#474-) — Verbosity addendum #70: “What Will This Change?” Confirmation
- [#475](#475-) — Verbosity addendum #71: Better Defaults for Experts
- [#476](#476-) — Verbosity addendum #72: Better Defaults for Beginners
- [#477](#477-) — Verbosity addendum #73: Human-Friendly Names Everywhere
- [#478](#478-) — Verbosity addendum #74: “Copy Debug Summary”
- [#479](#479-) — Verbosity addendum #75: “Report This Announcement”
- [#480](#480-) — Verbosity addendum #76: Documentation From Settings
- [#481](#481-) — Verbosity addendum #77: Default Reset Granularity
- [#482](#482-) — Verbosity addendum #78: Settings Export Preview
- [#483](#483-) — Verbosity addendum #79: Import Conflict Wizard
- [#484](#484-) — Verbosity addendum #80: “Try Without Applying”
- [#485](#485-) — Verbosity addendum #81: Session Profiles
- [#486](#486-) — Verbosity addendum #82: Time-Based Quiet Hours
- [#487](#487-) — Verbosity addendum #83: Focus Mode
- [#488](#488-) — Verbosity addendum #84: Review Mode
- [#489](#489-) — Verbosity addendum #85: “Readability / Accessibility Verbosity”
- [#490](#490-) — Verbosity addendum #86: Microcopy Style Settings
- [#491](#491-) — Verbosity addendum #87: “Use My Words” Custom Labels
- [#492](#492-) — Verbosity addendum #88: Abbreviation Dictionary for Announcements
- [#493](#493-) — Verbosity addendum #89: Language and Localization Readiness
- [#494](#494-) — Verbosity addendum #90: Accessibility Testing Assistant Mode
- [#495](#495-) — Verbosity addendum #91: Developer “Trace Verbosity”
- [#496](#496-) — Verbosity addendum #92: Performance Knobs
- [#497](#497-) — Verbosity addendum #93: Status Badges
- [#498](#498-) — Verbosity addendum #94: Braille Status Cell
- [#499](#499-) — Verbosity addendum #95: “Command Echo”
- [#500](#500-) — Verbosity addendum #96: “Before and After” Announcements
- [#501](#501-) — Verbosity addendum #97: Destructive Action Warnings
- [#502](#502-) — Verbosity addendum #98: “Undo Available” Announcements
- [#503](#503-) — Verbosity addendum #99: Multi-Monitor / Presentation Safety
- [#504](#504-) — Verbosity addendum #100: Final Recommendation
- [#602](#602-) — [Planning Archive] Verbosity System framing, scoping, risks, and release framing - 0.7.0



---

## #271 — [P0] Verbosity rebuild: implement per-verb token registry from docs/planning/verbosity.md

**Labels:** enhancement, accessibility, feature, p0

## Problem
`quill/core/verbosity/` ships only `__pycache__/`. Zero `.py` files. The release notes describe a per-verb verbosity token registry that has no source. Five settings (`announcement_verbosity`, `announce_wrap`, `announce_counts`, `announce_mode_changes`, `announce_spelling`) are parsed and clamped at `quill/core/settings.py:511-523` but no consumer reads them.

## Canonical plan
The full design is intact and detailed:

**`docs/planning/verbosity.md`** (2,544 lines, 52 sections)

The plan specifies:
- 23 missing core files (section 36): `__init__.py`, `channels.py`, `styles.py`, `profiles.py`, `tokens.py`, `parser.py`, `verbs.py`, `registry.py`, `data_order.py`, `engine.py`, `mastery.py`, `quiet.py`, `meeting.py`, `storage.py`, `schema.py`, `preview.py`, `qvp.py`, `library.py`, `history.py`, `explain.py`, `safe_mode.py`, `import_export.py`, `task_profiles.py`, `feedback_tuning.py`
- 10 missing UI files (section 37): `verbosity_prefs.py`, `verbosity_token_editor.py`, `verbosity_data_order.py`, `verbosity_chord_editor.py`, `verbosity_library.py`, `verbosity_history.py`, `verbosity_preview_lab.py`, `verbosity_safe_mode.py`, `verbosity_import_export.py`, `about_dialog.py`
- 46-step order of work (section 46): channels -> profiles -> tokens -> parser -> verbs -> registry -> engine -> quiet/meeting -> mastery -> history -> explain -> safe mode -> QVP -> library -> UI
- 49 non-negotiables (section 49): profile ladder, channel model, quiet mode, meeting mode, token parser, strict validation, simple+advanced token editor, per-verb overrides, keyboard manager integration, templates library, QVP JSON packs, announcement history, "why did QUILL say that?", safe mode/reset, golden announcement tests, screen-reader-first accessibility
- 49 success criteria (section 51)

## Explicit risk note (section 47)
The original work was lost due to `git stash drop`. **Mitigation: Do not use git stash for this rebuild. Use a topic branch. Commit frequently. Use small checkpoints. Push remote backups.**

## Acceptance
- All 23 core files and 10 UI files exist per the plan
- `announcement_verbosity`, `announce_wrap`, `announce_counts`, `announce_mode_changes`, `announce_spelling` are read by a real consumer
- All 49 success criteria from section 51 pass
- Golden announcement tests cover the 49 non-negotiables
- Tests added for each module

## Reference
- `docs/planning/verbosity.md` — canonical spec (READ THIS FIRST)
- `quill/core/settings.py:511-523` — dead knobs to wire up
- `quill/core/verbosity/__pycache__/` — artifacts of the lost work, do not trust them

---

## Sub-issues

Track each phase of this rebuild as it lands. Issues will close one per commit.

- [ ] #361 — Sub-PR 1.1: Core foundation (channels, profiles, tokens, parser)
- [ ] #362 — Sub-PR 1.2: Engine, quiet, meeting, mastery, history, explain, safe mode
- [ ] #363 — Sub-PR 1.3: QVP, library, preview, schema validation
- [ ] #364 — Sub-PR 1.4: UI surfaces (preferences, token editor, library, history, preview lab, about dialog)
- [ ] #365 — Sub-PR 1.5: Engine call-site migration, keymap, main_frame wiring
- [ ] #366 — Sub-PR 1.6: Section 53 addendum (100-item UX polish)

## Original body
## Sub-issues (PR boundaries)
- [ ] #361 — Sub-PR 1.1: Core foundation
- [ ] #362 — Sub-PR 1.2: Engine + modes
- [ ] #363 — Sub-PR 1.3: QVP + library + preview
- [ ] #364 — Sub-PR 1.4: UI surfaces
- [ ] #365 — Sub-PR 1.5: Call-site migration + keymap
- [ ] #366 — Sub-PR 1.6: Section 53 addendum (100 items)

## Verbosity design sections
- [ ] #367 — §5 Locked design decisions
- [ ] #368 — §6 Profile model
- [ ] #369 — §7 Channel system
- [ ] #370 — §8 Sound design
- [ ] #371 — §9 Quiet Mode
- [ ] #372 — §10 Meeting Mode
- [ ] #373 — §11 Quiet Undo
- [ ] #374 — §12 Token system
- [ ] #375 — §13 Template validation
- [ ] #376 — §14 Data ordering
- [ ] #377 — §15 Verb registry
- [ ] #378 — §16 Per-verb preferences UI
- [ ] #379 — §17 Verbosity Preferences UI
- [ ] #380 — §18 Token editor UI
- [ ] #381 — §19 Templates library
- [ ] #382 — §20 QVP file format
- [ ] #383 — §21 QVP install flow
- [ ] #384 — §22 Profile preview
- [ ] #385 — §23 Preview Lab
- [ ] #386 — §24 Announcement history
- [ ] #387 — §25 Why did QUILL say that?
- [ ] #388 — §26 Too Much / Too Little / Just Right
- [ ] #389 — §27 Mastery step down
- [ ] #390 — §28 Channel-specific templates
- [ ] #391 — §29 Safe Mode and Reset
- [ ] #392 — §30 Import / Export
- [ ] #393 — §31 Task-aware profiles
- [ ] #394 — §32 First-run Verbosity Tour
- [ ] #395 — §33 Keyboard Manager integration
- [ ] #396 — §34 Hotkey plan
- [ ] #397 — §35 Storage
- [ ] #398 — §40 Accessibility requirements
- [ ] #399 — §41 Testing plan
- [ ] #400 — §42 Golden announcement tests
- [ ] #401 — §43 Documentation plan
- [ ] #402 — §44 Manual smoke test
- [ ] #403 — §45 Verification commands
- [ ] #404 — §46 Order of work

## Verbosity addendum (100 items)
- [ ] #405 — Addendum #1: Three Layers
- [ ] #406 — Addendum #2: Searchable Settings
- [ ] #407 — Addendum #3: Verbosity Recipes
- [ ] #408 — Addendum #4: Announcement Budget
- [ ] #409 — Addendum #5: Repetition Collapse
- [ ] #410 — Addendum #6: Screen Reader Handoff Mode
- [ ] #411 — Addendum #7: Typing Echo Controls
- [ ] #412 — Addendum #8: Indentation and Whitespace
- [ ] #413 — Addendum #9: Selection Verbosity Knobs
- [ ] #414 — Addendum #10: Clipboard Verbosity Knobs
- [ ] #415 — Addendum #11: Search Result Verbosity Knobs
- [ ] #416 — Addendum #12: Error Coaching
- [ ] #417 — Addendum #13: Details on Demand
- [ ] #418 — Addendum #14: Detail Levels Per Category
- [ ] #419 — Addendum #15: Boundary Announcements
- [ ] #420 — Addendum #16: Progress Announcement Controls
- [ ] #421 — Addendum #17: Mode Change Announcements
- [ ] #422 — Addendum #18: Where Am I?
- [ ] #423 — Addendum #19: What Changed?
- [ ] #424 — Addendum #20: Speak Status Bar
- [ ] #425 — Addendum #21: Braille-Specific Knobs
- [ ] #426 — Addendum #22: Punctuation and Symbol Profiles
- [ ] #427 — Addendum #23: Markdown-Aware Verbosity
- [ ] #428 — Addendum #24: Code-Aware Verbosity
- [ ] #429 — Addendum #25: Compare/Diff Verbosity
- [ ] #430 — Addendum #26: File Operation Verbosity
- [ ] #431 — Addendum #27: Encoding and Line Ending Verbosity
- [ ] #432 — Addendum #28: Notification Priority Levels
- [ ] #433 — Addendum #29: Verbosity Rules Engine
- [ ] #434 — Addendum #30: Per-Workspace Verbosity
- [ ] #435 — Addendum #31: Per-File Verbosity
- [ ] #436 — Addendum #32: Temporary Verbosity Boost
- [ ] #437 — Addendum #33: Hold-to-Explain
- [ ] #438 — Addendum #34: Training Mode
- [ ] #439 — Addendum #35: Contextual Help Hooks
- [ ] #440 — Addendum #36: Friendly Names for Technical Concepts
- [ ] #441 — Addendum #37: Confidence Check Wizard
- [ ] #442 — Addendum #38: Community Pack Preview and Diff
- [ ] #443 — Addendum #39: QVP Trust Labels
- [ ] #444 — Addendum #40: QVP Copy as User Template
- [ ] #445 — Addendum #41: Verbosity Conflict Checker
- [ ] #446 — Addendum #42: Explain My Settings
- [ ] #447 — Addendum #43: Export Support Bundle
- [ ] #448 — Addendum #44: Privacy Controls
- [ ] #449 — Addendum #45: Private Document Mode
- [ ] #450 — Addendum #46: Speech Rate and Pause Knobs
- [ ] #451 — Addendum #47: Announcement Queue Policy
- [ ] #452 — Addendum #48: Last Important Announcement
- [ ] #453 — Addendum #49: Earcons With Text Equivalents
- [ ] #454 — Addendum #50: Learn Sounds Mode
- [ ] #455 — Addendum #51: Announcement Favorites
- [ ] #456 — Addendum #52: Pin This Status
- [ ] #457 — Addendum #53: Smart Status Rotation
- [ ] #458 — Addendum #54: Speak Current Template
- [ ] #459 — Addendum #55: Token Help on Demand
- [ ] #460 — Addendum #56: Template Examples Per Token
- [ ] #461 — Addendum #57: Pack Author Mode
- [ ] #462 — Addendum #58: Built-In Sample QVPs
- [ ] #463 — Addendum #59: Make This My Default
- [ ] #464 — Addendum #60: Bulk Editing
- [ ] #465 — Addendum #61: Undo for Settings Changes
- [ ] #466 — Addendum #62: Settings Change History
- [ ] #467 — Addendum #63: Test My Current Settings
- [ ] #468 — Addendum #64: Recommended Settings Suggestions
- [ ] #469 — Addendum #65: Accessibility Persona Setup
- [ ] #470 — Addendum #66: Command Discovery Announcements
- [ ] #471 — Addendum #67: Do Not Say This Again
- [ ] #472 — Addendum #68: Per-Announcement Suppression
- [ ] #473 — Addendum #69: Announcement Labels
- [ ] #474 — Addendum #70: What Will This Change? Confirmation
- [ ] #475 — Addendum #71: Better Defaults for Experts
- [ ] #476 — Addendum #72: Better Defaults for Beginners
- [ ] #477 — Addendum #73: Human-Friendly Names Everywhere
- [ ] #478 — Addendum #74: Copy Debug Summary
- [ ] #479 — Addendum #75: Report This Announcement
- [ ] #480 — Addendum #76: Documentation From Settings
- [ ] #481 — Addendum #77: Default Reset Granularity
- [ ] #482 — Addendum #78: Settings Export Preview
- [ ] #483 — Addendum #79: Import Conflict Wizard
- [ ] #484 — Addendum #80: Try Without Applying
- [ ] #485 — Addendum #81: Session Profiles
- [ ] #486 — Addendum #82: Time-Based Quiet Hours
- [ ] #487 — Addendum #83: Focus Mode
- [ ] #488 — Addendum #84: Review Mode
- [ ] #489 — Addendum #85: Readability / Accessibility Verbosity
- [ ] #490 — Addendum #86: Microcopy Style Settings
- [ ] #491 — Addendum #87: Use My Words Custom Labels
- [ ] #492 — Addendum #88: Abbreviation Dictionary
- [ ] #493 — Addendum #89: Language and Localization Readiness
- [ ] #494 — Addendum #90: Accessibility Testing Assistant Mode
- [ ] #495 — Addendum #91: Developer Trace Verbosity
- [ ] #496 — Addendum #92: Performance Knobs
- [ ] #497 — Addendum #93: Status Badges
- [ ] #498 — Addendum #94: Braille Status Cell
- [ ] #499 — Addendum #95: Command Echo
- [ ] #500 — Addendum #96: Before and After Announcements
- [ ] #501 — Addendum #97: Destructive Action Warnings
- [ ] #502 — Addendum #98: Undo Available Announcements
- [ ] #503 — Addendum #99: Multi-Monitor / Presentation Safety
- [ ] #504 — Addendum #100: Final Recommendation

## Planning.md children
- [ ] #505 — Planning parent
- [ ] #506 — O1 Live installer smoke
- [ ] #507 — O5 Ask QUILL per-message buttons
- [ ] #508 — O5b Unify the two AI stacks
- [ ] #509 — O6 AI Hub two-pane
- [ ] #510 — O7 Azure provider
- [ ] #511 — O8 AI-19 Copilot
- [ ] #512 — O9 SHELL-2 OCR
- [ ] #513 — O10 Quick Nav
- [ ] #514 — O11 Un-gate Word/CSV
- [ ] #515 — O12 BITS Whisperer
- [ ] #516 — O13 Native RTF
- [ ] #517 — O14 Quillin Hub
- [ ] #518 — O15 macOS port
- [ ] #519 — O16 Plugin capability
- [ ] #520 — O17 Linux platform
- [ ] #521 — O20 statusbar extract
- [ ] #522 — O21 master backlog
- [ ] #523 — AI-19 in flight
- [ ] #524 — SHELL-2 in flight
- [ ] #525 — SHELL-3 in flight
- [ ] #526 — DLG-3.8 in flight
- [ ] #527 — CQ-11 in flight
- [ ] #528 — GLOW-1
- [ ] #529 — GLOW-2
- [ ] #530 — GLOW-3
- [ ] #531 — GLOW-4
- [ ] #532 — GLOW-5
- [ ] #533 — GLOW-6
- [ ] #534 — GLOW-7
- [ ] #535 — DOC-1
- [ ] #536 — DOC-2
- [ ] #537 — DOC-3
- [ ] #538 — DOC-4
- [ ] #539 — DOC-5
- [ ] #540 — DOC-6
- [ ] #541 — DOC-7
- [ ] #542 — DOC-8
- [ ] #543 — DOC-11
- [ ] #544 — DOC-12
- [ ] #545 — DOC-14
- [ ] #546 — DOC-15
- [ ] #547 — DOC-16
- [ ] #548 — DOC-17
- [ ] #549 — DOC-18
- [ ] #550 — POD-1
- [ ] #551 — POD-2
- [ ] #552 — POD-3
- [ ] #553 — POD-4
- [ ] #554 — POD-5
- [ ] #555 — TUT-1
- [ ] #556 — TUT-2
- [ ] #557 — TUT-3
- [ ] #558 — TUT-4
- [ ] #559 — TUT-5
- [ ] #560 — TUT-6
- [ ] #561 — TUT-7
- [ ] #562 — CQ-14
- [ ] #563 — CQ-23
- [ ] #564 — CQ-24
- [ ] #565 — LINUX-2
- [ ] #566 — WATCH-8
- [ ] #567 — BW-1
- [ ] #568 — BW-2
- [ ] #569 — BW-3
- [ ] #570 — BW-4
- [ ] #571 — BW-5
- [ ] #572 — BW-6
- [ ] #573 — BW-7
- [ ] #574 — BW-8
- [ ] #575 — BW-9
- [ ] #576 — BW-10
- [ ] #577 — WATCH-9
- [ ] #578 — NAV-10
- [ ] #579 — AI-11
- [ ] #580 — AI-12
- [ ] #581 — AI-18
- [ ] #582 — FEAT-12
- [ ] #583 — FEAT-13
- [ ] #584 — FEAT-14
- [ ] #585 — FEAT-15
- [ ] #586 — FEAT-16
- [ ] #587 — FEAT-17
- [ ] #588 — FEAT-18
- [ ] #589 — LINUX-1
- [ ] #590 — ECO-1
- [ ] #591 — L10N-1
- [ ] #592 — COLLAB-1
- [ ] #593 — AX-A
- [ ] #594 — AX-B
- [ ] #595 — AX-C
- [ ] #596 — AX-D
- [ ] #597 — AX-E
- [ ] #598 — AX-F
- [ ] #599 — PKG-1
- [ ] #600 — Braille Mode Phases 3/4/6 pointer



---

## #361 — [Verbosity] Sub-PR 1.1 — Core foundation: channels, profiles, tokens, parser

**Labels:** feature, p0

## Sub-PR 1.1 — Core foundation: channels, profiles, tokens, parser

Parent: #271 ([P0] Verbosity rebuild).

Slice of the verbosity rebuild that ships the pure-domain building blocks with no UI, no call-site migration. Lands parser coverage to 90%+ before any UI is touched.

### Files (all new under `quill/core/verbosity/`)

- `__init__.py` — package facade; re-exports the public names.
- `channels.py` — `Channel(enum.Flag)` with SPEECH, BRAILLE, SOUND, VISUAL.
- `profiles.py` — built-in profiles (Beginner, Normal, Expert, Quiet) + `CustomProfile` dataclass.
- `tokens.py` — `TokenSpec` dataclass, allowed-filters table, type registry.
- `parser.py` — strict parser; only `{name}`, `${filter:name}`, `${filter:arg:name}`. No custom filters. Errors are structured, never exceptions to callers.
- `verbs.py` — `VerbSpec` dataclass + the verb catalog (`nav.*`, `edit.*`, `doc.*`, `search.*`, `system.*` from section 15).
- `registry.py` — `VerbRegistry` with `register(verb)`, `get(verb_id)`, `all()`.
- `data_order.py` — `DataOrder` model + ordered renderer.
- `schema.py` — JSON schemas for verbosity settings, custom data, QVP, profile import/export.

### Wire the dead knobs

`quill/core/settings.py:519-525` reads `announcement_verbosity`, `announce_wrap`, `announce_counts`, `announce_mode_changes`, `announce_spelling` but no consumer reads them. Add a real consumer: `VerbosityEngine.speak(verb_id, ctx, profile)` returns a `RenderedAnnouncement` and routes through channels. Bind `announcement_verbosity` to the profile ladder (minimal=Expert, normal=Normal, verbose=Beginner). Bind the four booleans to per-event channel toggles. (Engine itself is added in 1.2; this sub-PR just adds the read-side contract.)

### Tests

- `tests/unit/core/test_verbosity_channels.py`
- `tests/unit/core/test_verbosity_profiles.py`
- `tests/unit/core/test_verbosity_tokens.py`
- `tests/unit/core/test_verbosity_filters.py`
- `tests/unit/core/test_verbosity_parser.py` — aim for 90%+ coverage.
- `tests/unit/core/test_verbosity_data_order.py`

### Acceptance

- All 9 core files exist and pass `ruff check` + `mypy quill/core`.
- Parser coverage is 90%+ (per `pytest --cov`).
- `announcement_verbosity` setting is read by a real consumer.
- All 6 new test modules green.
- Working tree clean; pushed to `release/0.7.0-verbosity`.

### Closes

Replaces sections 4-6, 12-15 of `docs/planning/verbosity.md` (channels, profile model, token system, registry).



---

## #362 — [Verbosity] Sub-PR 1.2 — Engine, quiet, meeting, mastery, history, explain, safe mode

**Labels:** feature, p0

## Sub-PR 1.2 — Engine, quiet, meeting, mastery, history, explain, safe mode, feedback, task profiles

Parent: #271 ([P0] Verbosity rebuild).

Builds on sub-PR 1.1's foundation. Adds the central engine, the runtime modes, mastery tracking, history, the explain trace, safe mode, feedback tuning, task profiles, import/export, and the storage layer. No call-site migration yet — only adds the engine so existing `_announce` paths keep working.

### Files (all new under `quill/core/verbosity/`)

- `engine.py` — central routing engine. `speak(verb_id, ctx, *, quiet=False, meeting=False)` returns `RenderedAnnouncement`. Decides: profile, channels, suppressions, QVP override, per-verb override, per-chord override, sound event.
- `quiet.py` — `QuietMode` controller. `enter()` / `exit()` / `undo()` (Ctrl+Shift+Z per section 34).
- `meeting.py` — `MeetingMode` controller.
- `mastery.py` — per-verb usage counter with step-down suggestion timer.
- `history.py` — `AnnouncementHistory(max_entries=100, redact_text=True)`.
- `explain.py` — builds a "Why did QUILL say that?" trace.
- `safe_mode.py` — `VerbositySafeMode` that disables custom verbosity and restores built-ins.
- `feedback_tuning.py` — Too-Much/Too-Little/Just-Right signal store.
- `task_profiles.py` — task-aware suggestions (Markdown mode, code mode, etc.).
- `import_export.py` — `.quill-verbosity-profile.json` import/export.
- `storage.py` — `verbosity_custom.json` atomic read/write.

### Wire call sites (small slice)

Have `engine.speak()` called by `quill/ui/assistant_panel.py:_announce` (already a lambda) and `quill/ui/ai_hub_dialog.py:_announce`. Add ONE legacy passthrough so existing call sites keep working.

### Tests

- `tests/unit/core/test_verbosity_engine.py` — 8-12 scenarios (Beginner/Normal/Expert/Quiet × 3 verbs minimum).
- `tests/unit/core/test_verbosity_quiet.py`
- `tests/unit/core/test_verbosity_meeting.py`
- `tests/unit/core/test_verbosity_mastery.py`
- `tests/unit/core/test_verbosity_history.py`
- `tests/unit/core/test_verbosity_explain.py`
- `tests/unit/core/test_verbosity_safe_mode.py`
- `tests/unit/core/test_verbosity_import_export.py`
- `tests/unit/core/test_verbosity_feedback_tuning.py`
- `tests/unit/core/test_verbosity_task_profiles.py`
- `tests/unit/core/test_verbosity_storage.py`

Aim for 70%+ coverage on `engine.py`.

### Acceptance

- All 11 new core files exist and pass lint + mypy.
- `engine.speak()` is reachable from the assistant panel and AI hub paths.
- All 11 new test modules green.
- 70%+ coverage on `engine.py` (per `pytest --cov`).
- Working tree clean; pushed to `release/0.7.0-verbosity`.

### Closes

Replaces sections 9-11, 24-31 of `docs/planning/verbosity.md` (quiet, meeting, history, explain, safe mode, feedback tuning, task profiles, import/export).



---

## #363 — [Verbosity] Sub-PR 1.3 — QVP, library, preview, schema validation

**Labels:** feature, p0

## Sub-PR 1.3 — QVP, library, preview, schema validation

Parent: #271 ([P0] Verbosity rebuild).

Adds the QVP (QUILL Verbosity Pack) format, the library that owns built-in + user + QVP-installed templates, and the scenario-based preview renderer. No UI surface yet — just the core.

### Files

- `quill/core/verbosity/qvp.py` — QVP loader/validator. JSON-only, schema-validated, namespaced, `min_quill_version` gated, no code execution. Install flow returns a `QVPInstallResult` with `accepted`, `rejected_templates`, `warnings`.
- `quill/core/verbosity/library.py` — `TemplateLibrary` (built-in + user + QVP-installed).
- `quill/core/verbosity/preview.py` — scenario-based preview renderer (called by Preview Lab in 1.4).
- `quill/core/schemas/extension.json` (extend existing) or new `quill/core/schemas/qvp.json`.

### Tests

- `tests/unit/core/test_verbosity_qvp.py` — pack validation, schema rejection, version gate, dependency check.
- `tests/unit/core/test_verbosity_library.py`
- `tests/unit/core/test_verbosity_preview.py`
- 5+ golden tests under `tests/golden/verbosity/` (per section 42).

### Acceptance

- All 3 new core files plus the QVP JSON schema exist.
- All 3 new test modules green; 5+ golden tests pass.
- QVP loader rejects: non-JSON, schema-invalid, version-mismatched, dependency-missing packs.
- No code-execution path exists — verified by `grep` for `exec`, `eval`, `__import__` returning no hits in the QVP loader.
- Working tree clean; pushed to `release/0.7.0-verbosity`.

### Closes

Replaces sections 20-23, 42 of `docs/planning/verbosity.md` (QVP files, install flow, profile preview, preview lab, golden tests).



---

## #364 — [Verbosity] Sub-PR 1.4 — UI: preferences, token editor, library, history, preview lab, about dialog

**Labels:** accessibility, feature, p0

## Sub-PR 1.4 — UI: preferences, token editor, library, history, preview lab, safe mode, about dialog

Parent: #271 ([P0] Verbosity rebuild).

Largest UI slice of the verbosity rebuild. Adds the embeddable prefs panel, token editor, data order editor, chord mini-editor, templates library, history viewer, preview lab, safe-mode reset UI, import/export UI, and the 3-tab About dialog.

### Files (all new under `quill/ui/`)

- `verbosity_prefs.py` — embeddable prefs panel (3 layers: Simple / Customize / Advanced).
- `verbosity_token_editor.py` — Simple + Advanced token editor with EVT_CHAR_HOOK on the modal.
- `verbosity_data_order.py` — Data Order editor.
- `verbosity_chord_editor.py` — Mini-editor scoped to chord-fired verbs.
- `verbosity_library.py` — Templates Library tab.
- `verbosity_history.py` — Announcement History viewer.
- `verbosity_preview_lab.py` — Scenario-based preview tool.
- `verbosity_safe_mode.py` — Reset UI.
- `verbosity_import_export.py` — Profile import/export UI.
- `about_dialog.py` — 3-tab notebook (Overview / Dependencies / Links).

### Accessibility contract (A11Y-4)

- All dialogs use `_show_modal_dialog` (in `MainFrame`).
- All `wx.Dialog` subclasses go through `apply_modal_ids`.
- Label-then-control via lambda factory.
- Deterministic focus.
- SetName / SetHint / SetDefault on every interactive widget.
- No icon-only buttons.

### Tests

- `tests/unit/ui/test_verbosity_prefs.py`
- `tests/unit/ui/test_verbosity_token_editor.py`
- `tests/unit/ui/test_verbosity_data_order.py`
- `tests/unit/ui/test_verbosity_chord_editor.py`
- `tests/unit/ui/test_verbosity_library.py`
- `tests/unit/ui/test_verbosity_qvp_install.py`
- `tests/unit/ui/test_verbosity_history.py`
- `tests/unit/ui/test_verbosity_preview_lab.py`
- `tests/unit/ui/test_verbosity_safe_mode.py`
- `tests/unit/ui/test_verbosity_import_export.py`
- `tests/unit/core/test_about_info.py` — 3-tab dialog contract.

Regenerate `tests/unit/ui/fixtures/dialog_inventory.json` and pass the A11Y-4 gate.

### Acceptance

- All 10 new UI files plus the about dialog exist.
- A11Y-4 banned-pattern gate passes.
- `dialog_inventory.json` regenerated and committed.
- All new UI test modules green.
- Working tree clean; pushed to `release/0.7.0-verbosity`.

### Closes

Replaces sections 17-19, 25, 33-34 of `docs/planning/verbosity.md` (prefs UI, token editor, templates library, history UI, preview lab, safe mode UI).



---

## #365 — [Verbosity] Sub-PR 1.5 — Engine call-site migration, keymap, main_frame wiring

**Labels:** feature, p0

## Sub-PR 1.5 — Engine call-site migration, keymap, main_frame wiring

Parent: #271 ([P0] Verbosity rebuild).

The wiring sub-PR. Adds the new chords, registers feature commands, swaps high-traffic `_announce(...)` call sites in `main_frame.py` over to `VerbosityEngine.speak(...)`, and retires the legacy `announce_*` settings by binding them to the new profile ladder (their reads already work after 1.1; this sub-PR removes the dead knobs from the UI but keeps the names as aliases that map to profile defaults).

### Files to modify

- `quill/core/feature_command_map.py` — add verbosity feature commands per section 39.
- `quill/core/keymap.py` — register new chords per section 34 (Ctrl+Shift+Q, Ctrl+Shift+B, Ctrl+Shift+M, Ctrl+Shift+Z, QUILL key + H, etc.). Move Unquote Lines from Ctrl+Shift+Q to Alt+Shift+Q per the conflict note.
- `quill/ui/main_frame.py` — swap 30+ `_announce(...)` call sites to `VerbosityEngine.speak(...)`.
- `quill/ui/main_frame_menu.py` — Quiet/Meeting badges `[Q]` `[M]`.
- `quill/ui/main_frame_statusbar.py` — Quiet/Meeting status badges.
- `quill/ui/setup_wizard_pages.py` — Verbosity tour page per section 32.
- `quill/ui/keyboard_manager_dialog.py` — Keyboard Manager integration per section 33.
- `quill/ui/info_pages.py` — Updates reflecting new chords.
- `quill/core/settings.py` — Remove dead knobs from UI; keep aliases for profile defaults.

### Tests

- `tests/unit/ui/test_main_frame_quill_key.py`
- `tests/unit/core/test_quill_key_help.py`
- `tests/unit/core/test_about_info.py` (refresh for 3-tab About dialog).
- Update `tests/unit/ui/test_main_frame_menu_contract.py` if badges change menu structure.

### Docs

- `docs/release notes/release0.7.0.md` — finalize "Verbosity System" section with call-site migration note.
- `docs/keybinding-standard.md` — add new verbosity chords.
- `docs/CONTROL_REFERENCE.md` — regenerated by `python -m quill.tools.build_docs`.
- `CHANGELOG.md` — final verbosity entry.

### Acceptance

- 30+ `_announce(...)` call sites in `main_frame.py` replaced with `engine.speak(...)`.
- New chords registered and surfaced in Keyboard Manager.
- Quiet/Meeting badges appear in status bar and menu when active.
- `module_size_budgets.json` rebaselined AFTER wiring is complete (per section 46 step 46).
- `docs/CONTROL_REFERENCE.md` regenerated; topic count grows by ~25.
- Working tree clean; pushed to `release/0.7.0-verbosity`.

### Closes

Replaces sections 32, 33, 34, 39, 46 (steps 27-39) of `docs/planning/verbosity.md` (keymap, keyboard manager, setup wizard, feature commands, main_frame wiring).



---

## #366 — [Verbosity] Sub-PR 1.6 — Section 53 addendum (100-item UX polish)

**Labels:** feature, p0

## Sub-PR 1.6 — Section 53 addendum (100-item UX polish)

Parent: #271 ([P0] Verbosity rebuild).

Implements the 100 addendum items from `docs/planning/verbosity.md` section 53 (per user direction: ship both the 49 non-negotiables from section 49 AND the 100 addendum items, both in 0.7.0). Adds new knobs, new UI surfaces, new modes/recipes, mastery/tuning, and privacy/safety extensions.

### 1.6.a — New knobs (settings)

Add to `quill/core/verbosity/settings_knobs.py` (extend `quill/core/settings.py` or create a sub-package):

- 53.4 announcement budget (collapse repeats, suppress-after-N)
- 53.5 repetition collapse
- 53.6 screen-reader handoff mode
- 53.7 typing echo controls
- 53.8 indentation/whitespace verbosity
- 53.9 selection verbosity knobs
- 53.10 clipboard verbosity knobs
- 53.11 search result verbosity knobs
- 53.15 boundary announcements
- 53.16 progress announcement controls
- 53.21 braille-specific knobs
- 53.22 punctuation/symbol profiles
- 53.25 compare/diff verbosity
- 53.26 file-operation verbosity
- 53.27 encoding/line-ending verbosity
- 53.28 notification priority levels
- 53.41 verbosity conflict checker (validator pass)
- 53.44 privacy controls
- 53.46 speech rate/pause knobs
- 53.49 earcons with text equivalents
- 53.55 token help on demand (parser already supports this; wire UI)
- 53.86 microcopy style settings
- 53.88 abbreviation dictionary for announcements
- 53.92 performance knobs (collapse repeats defaults)
- 53.95 command echo

### 1.6.b — New UI surfaces

- 53.2 searchable settings (search bar in prefs)
- 53.13 details-on-demand ("Press QUILL key + D for details" hook)
- 53.18 "Where Am I?" command (Ctrl+QUILL key + W) — `verbosity_where_am_i.py` UI
- 53.19 "What Changed?" command
- 53.20 "Speak Status Bar" command (Ctrl+QUILL key + S)
- 53.42 "Explain My Settings" command
- 53.54 "Speak Current Template" in token editor
- 53.62 settings change history (extend `history.py`)
- 53.70 "What Will This Change?" confirmation (apply to bulk actions)
- 53.74 "Copy Debug Summary" from explain
- 53.79 import conflict wizard
- 53.80 "Try Without Applying" (session-scoped verbosity)

### 1.6.c — New modes / recipes

- 53.32 temporary verbosity boost (Ctrl+QUILL key + Up/Down for next command)
- 53.34 training mode (extends Beginner)
- 53.83 focus mode (recipe)
- 53.84 review mode (recipe)
- 53.86 microcopy style (Friendly/Professional/Minimal/Technical/Teaching)
- 53.65 accessibility persona setup in setup wizard

### 1.6.d — Mastery / tuning

- 53.26 "too much / too little / just right" feedback (expand shortcuts)
- 53.68 per-announcement suppression
- 53.72 better defaults for beginners
- 53.73 human-friendly names everywhere (translation layer)
- 53.86 microcopy style (above)

### 1.6.e — Privacy / safety

- 53.45 private document mode
- 53.43 export support bundle (extends safe_mode.py)
- 53.78 settings export preview

### Tests

- One test file per category (1.6.a-e). UI tests for new surfaces. Settings round-trip tests.
- Each category has at least 3 tests verifying the new behavior.

### Docs

- `docs/Product Requirement Documents and Specifications/QUILL-PRD.md` — new "Future Verbosity Ideas" appendix listing all 100 items with status. Section 53.1-53.100 each get a short port.
- `docs/user guide/userguide.md` — extend Verbosity chapter with all new settings, organized by the three-layer model (53.1).
- `docs/release notes/release0.7.0.md` — "Verbosity System Advanced" section.
- `CHANGELOG.md` — single entry summarizing the 100-item addendum.

### Acceptance

- All 25 new knobs (1.6.a) present and round-trip through settings save/load.
- All 12 new UI surfaces (1.6.b) exist; chords registered.
- All 6 new modes/recipes (1.6.c) wired to the engine.
- All 5 mastery/tuning extensions (1.6.d) deliver their behavior.
- All 3 privacy/safety extensions (1.6.e) gated on QUILL_SAFE_MODE.
- 15+ new tests across the 5 categories, all green.
- PRD appendix lists all 100 items with current status.
- Working tree clean; pushed to `release/0.7.0-verbosity`.

### Closes

Replaces section 53 of `docs/planning/verbosity.md` (the 100-item addendum).



---

## #367 — Verbosity: §5 Locked design decisions (12 decisions)

**Labels:** feature, p0

Parent: #271

Implements section 5 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Captures the 12 locked design decisions from `docs/planning/verbosity.md` section 5. Each decision is the answer to a question that the user/community already settled; this issue tracks that the code matches the locked answer.

### Decisions

1. **Profile UX** — Hybrid model: four ladder presets (Beginner / Normal / Expert / Quiet), each populates four channel checkboxes (Speech, Braille, Sound, Visual). Edits after preset expose a `Modified` state. Switching profiles announces the channel reset.
2. **Channels** — Speech, Braille, Sound, Visual. Visual is the accessibility floor and remains always-on (disabled but checked with accessible name `Visual status bar, always on, cannot be disabled`).
3. **Sound channel** — Independent and per-event aware. Master channel, per-event gating, off during Quiet Mode, error-only in Expert, character varies by profile.
4. **Validation timing** — Default `On-button`. Available: `Live`, `On-focus`, `On-button`. The latter is default to avoid interruption.
5. **Audio defaults** — Only validation-spoken feedback is on by default. Auto-play on editor open, palette token audio, and focus-out read-back are opt-in.
6. **Token editor shape** — Two views (Simple default + Advanced), backed by shared data. wx.RadioBox to switch (not wx.Notebook — implies separate pages).
7. **Per-verb default UX** — `Use default` is the headline. Per-row dropdowns show `—` when using default. Rendered preview appears only when customized.
8. **Templates library v1** — Full CRUD: Save, Apply, Delete, Rename. Flat wx.ListBox/ListCtrl. Per-row dropdown apply. No drag-and-drop in 0.7.0.
9. **Library cross-verb behavior** — Auto-filter invalid tokens; warn. Example: `Applied template Concise. Removed 2 tokens because this verb does not track them: cell, region.`
10. **Per-verb table** — Master/detail with filter (not a grid). Virtual wx.ListCtrl report style on the left, detail pane on the right, wx.SearchCtrl filter that matches name + namespace.
11. **QVP files** — `.qvp.json`, JSON-only, data-only, schema-validated, no executable code, no signing in v1, namespaced by author, `min_quill_version` gated, manually installed.
12. **Required QVP metadata** — Name, Author, Description, Version, License. Optional: Preview text, Tags, Dependencies.

### Files

Primary owners (per sub-PRs #361, #363, #364):

- `quill/core/verbosity/profiles.py` (#361)
- `quill/core/verbosity/channels.py` (#361)
- `quill/core/verbosity/qvp.py` (#363)
- `quill/core/schemas/qvp.json` (#363)
- `quill/ui/verbosity_prefs.py` (#364)
- `quill/ui/verbosity_token_editor.py` (#364)
- `quill/ui/verbosity_library.py` (#364)

### Acceptance

- Each of the 12 decisions is testable: at least one unit test or UI test verifies the locked behavior.
- `quill/core/verbosity/profiles.py` exposes `Beginner`, `Normal`, `Expert`, `Quiet` and `CustomProfile`.
- `quill/core/verbosity/channels.py` Channel enum has VISUAL with `always_on=True`.
- Token editor uses RadioBox (not Notebook) to switch Simple/Advanced.
- QVP loader rejects files without required metadata.

### Closes

Section 5 of `docs/planning/verbosity.md`.



---

## #368 — Verbosity: §6 Profile model (Beginner / Normal / Expert / Quiet + CustomProfile)

**Labels:** feature, p0

Parent: #271

Implements section 6 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the four built-in verbosity profiles plus the `CustomProfile` data model from `docs/planning/verbosity.md` section 6.

### Scope

- **Beginner** — full context for every verb; spoken and braille; chime earcons.
- **Normal** — informative, not chatty; standard defaults.
- **Expert** — routine confirmations suppressed; errors still speak; subtle click earcons.
- **Quiet** — minimal announcement; suitable for meeting rooms.
- **CustomProfile** — user-defined combination of profile + channel mix + per-verb overrides; persisted.

Each preset populates four channel checkboxes: Speech, Braille, Sound, Visual. The Visual checkbox is the accessibility floor (always-on, disabled).

### Files

Primary owner (per sub-PR #361):

- `quill/core/verbosity/profiles.py`

### Acceptance

- `Beginner`, `Normal`, `Expert`, `Quiet` are exposed as built-in `VerbosityProfile` constants.
- `CustomProfile` dataclass with name, channel mix, per-verb overrides, per-chord overrides, optional templates, optional data order.
- Round-trip: save CustomProfile to JSON, load it back; deep equality.
- Default profile for new installs is `Normal`.

### Closes

Section 6 of `docs/planning/verbosity.md`.



---

## #369 — Verbosity: §7 Channel system (Channel enum + routing)

**Labels:** accessibility, feature, p0

Parent: #271

Implements section 7 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the `Channel` enum and channel routing from `docs/planning/verbosity.md` section 7.

### Scope

- `Channel(enum.Flag)` with SPEECH, BRAILLE, SOUND, VISUAL.
- Routing helpers that decide which channels fire for a given verb under a given profile.
- Visual always-on (disabled but checked) regardless of profile.
- Per-channel mute/unmute through the prefs panel.

### Files

Primary owner (per sub-PR #361, #362):

- `quill/core/verbosity/channels.py`
- `quill/core/verbosity/engine.py` (route through channels)

### Acceptance

- `Channel.SPEECH | Channel.BRAILLE | Channel.SOUND | Channel.VISUAL` is the default mix.
- Visual channel cannot be removed via the prefs panel.
- A unit test confirms Visual is always present in the routed channel set.

### Closes

Section 7 of `docs/planning/verbosity.md`.



---

## #370 — Verbosity: §8 Sound design (master + per-event gating)

**Labels:** feature, p0

Parent: #271

Implements section 8 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the sound channel design from `docs/planning/verbosity.md` section 8.

### Scope

- Master sound mute/unmute.
- Per-event sound gating (each verb has a sound_event id; on/off per profile).
- Sound off during Quiet Mode.
- Sound error-only in Expert mode.
- Profile-character earcons: friendly chimes for Beginner; subtle clicks for Expert; quiet-hours style when sound is off.

### Files

Primary owners (per sub-PR #361, #362):

- `quill/core/verbosity/profiles.py` — sound policy per profile.
- `quill/core/verbosity/engine.py` — sound routing decision.
- `quill/platform/sound_player.py` — `set_muted`, `set_disabled`, `play`.

### Acceptance

- Sound gating matrix tested: Beginner chimes play, Expert errors-only, Quiet silence.
- `set_muted(True)` silences everything; `set_disabled(events)` silences specific events.
- A unit test confirms Quiet Mode suppresses all earcons.

### Closes

Section 8 of `docs/planning/verbosity.md`.



---

## #371 — Verbosity: §9 Quiet Mode (controller + chords)

**Labels:** feature, p0

Parent: #271

Implements section 9 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements Quiet Mode from `docs/planning/verbosity.md` section 9.

### Scope

- `QuietMode` controller with `enter()`, `exit()`, `undo()`, `is_active`.
- Chord: `Ctrl+Shift+Q` toggles Quiet Mode. Also reachable via `QUILL key + Q`.
- Badge `[Q]` in status bar and menu when active.
- Suppresses all announcements except braille + visual floor.
- Quiet Mode persists for the session; user can opt-in to remember across sessions.

### Files

Primary owners (per sub-PR #362, #365):

- `quill/core/verbosity/quiet.py`
- `quill/core/keymap.py` — chord registration.
- `quill/ui/main_frame_statusbar.py` — `[Q]` badge.
- `quill/ui/main_frame_menu.py` — menu entry + badge.

### Acceptance

- Toggling Quiet Mode announces `Quiet Mode on` / `Quiet Mode off` on the transition.
- `[Q]` badge visible in status bar when active.
- `is_active()` returns True between enter() and exit().

### Closes

Section 9 of `docs/planning/verbosity.md`.



---

## #372 — Verbosity: §10 Meeting Mode (controller + chords)

**Labels:** feature, p0

Parent: #271

Implements section 10 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements Meeting Mode from `docs/planning/verbosity.md` section 10.

### Scope

- `MeetingMode` controller with `enter()`, `exit()`, `is_active`.
- Chord: `Ctrl+Shift+B` toggles Meeting Mode.
- Badge `[M]` in status bar and menu when active.
- Hard mutes all sound; routes speech through a reduced set; braille and visual remain.

### Files

Primary owners (per sub-PR #362, #365):

- `quill/core/verbosity/meeting.py`
- `quill/core/keymap.py`
- `quill/ui/main_frame_statusbar.py`
- `quill/ui/main_frame_menu.py`

### Acceptance

- Meeting Mode mutes all earcons.
- `[M]` badge visible in status bar when active.
- `is_active()` returns True between enter() and exit().

### Closes

Section 10 of `docs/planning/verbosity.md`.



---

## #373 — Verbosity: §11 Quiet Undo (Ctrl+Shift+Z)

**Labels:** feature, p0

Parent: #271

Implements section 11 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements Quiet Undo from `docs/planning/verbosity.md` section 11.

### Scope

- `Ctrl+Shift+Z` undoes the last quiet-hours / verbosity state change.
- Undo applies to: Quiet Mode on/off, Meeting Mode on/off, per-verb override apply/revert, profile change, channel mix change.
- State stack keeps the last 20 transitions.

### Files

Primary owners (per sub-PR #362, #365):

- `quill/core/verbosity/quiet.py` — undo stack.
- `quill/core/keymap.py` — chord registration.

### Acceptance

- Pressing `Ctrl+Shift+Z` after entering Quiet Mode restores the previous mode.
- Pressing it twice undoes two transitions.
- An empty undo stack announces `Nothing to undo`.

### Closes

Section 11 of `docs/planning/verbosity.md`.



---

## #374 — Verbosity: §12 Token system (TokenSpec + filters)

**Labels:** feature, p0

Parent: #271

Implements section 12 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the token system from `docs/planning/verbosity.md` section 12.

### Scope

- `TokenSpec` dataclass: name, type (`str | int | float | bool | datetime | duration`), description, derive callable, filters tuple.
- Template syntax: `{name}`, `${filter:name}`, `${filter:arg:name}`.
- Engine-implemented filters: `upper`, `lower`, `title`, `ordinal`, `pad:N`, `pluralize`, `singular`, `duration_human`, `date_long`, `date_short`, `time`, `truncate:N`.
- **Custom filters are not supported in 0.7.0** — prevents injection, keeps QVP files data-only.

### Files

Primary owner (per sub-PR #361):

- `quill/core/verbosity/tokens.py`

### Acceptance

- `TokenSpec` is a frozen dataclass with the documented fields.
- All 12 engine filters implemented and tested.
- Parser rejects unknown filters with a structured error.
- Parser rejects custom filters (security boundary).

### Closes

Section 12 of `docs/planning/verbosity.md`.



---

## #375 — Verbosity: §13 Template validation (strict allowlist + type checking)

**Labels:** feature, p0

Parent: #271

Implements section 13 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements template validation from `docs/planning/verbosity.md` section 13.

### Scope

- **Strict allowlist.** Every token in a template must match the verb's TokenSpec list. Unknown tokens are errors.
- **Type checking.** Filters are checked against token types. Examples: `pad:N` requires numeric; `date_long` requires datetime.
- **Filter allowlist per token.** Each token declares allowed filters.
- **Validation messages.** Spoken summary `Validation: 3 tokens, 1 warning, 0 errors.` Detailed review field uses `[X]`, `[!]`, `[OK]` prefixes.
- **Save behavior.** Save disabled when blocking errors present; tooltip explains why; screen reader announces `Save disabled, N errors.`
- **Validation command.** `Ctrl+T` triggers validation inside the token editor.
- **Preview command.** `Ctrl+Shift+P` triggers preview. Debounced 250ms.
- **Validation timing.** Default `On-button`. Available: `Live`, `On-focus`, `On-button`.

### Files

Primary owners (per sub-PR #361, #362, #364):

- `quill/core/verbosity/parser.py` (#361)
- `quill/core/verbosity/preview.py` (#362)
- `quill/ui/verbosity_token_editor.py` (#364) — Save disabled state, validation/preview chords.

### Acceptance

- A template referencing an unknown token cannot be saved.
- A template referencing a wrong-type filter is rejected.
- `Ctrl+T` speaks the summary and updates the review field.
- `Ctrl+Shift+P` speaks the preview; debounce confirmed in test.
- Save button has `tooltip=1 error — fix to save` when disabled.

### Closes

Section 13 of `docs/planning/verbosity.md`.



---

## #376 — Verbosity: §14 Data ordering model + editor

**Labels:** feature, p0

Parent: #271

Implements section 14 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements Data Ordering from `docs/planning/verbosity.md` section 14.

### Scope

- `DataOrder` dataclass: `verb_id`, `fields: tuple[str, ...]`, `separator: str = ", "`.
- Editor: wx.ListBox with Move Up, Move Down, Reset, Preview buttons.
- Template precedence: when both a custom template and a custom data order exist for a verb, the template wins.

### Files

Primary owners (per sub-PR #361, #364):

- `quill/core/verbosity/data_order.py` (#361)
- `quill/ui/verbosity_data_order.py` (#364)

### Acceptance

- `DataOrder` is frozen; mutable reorderings produce new instances.
- Move Up / Move Down reorder fields; persisted to user data.
- Test confirms template wins when both exist.
- A unit test confirms the dataclass is hashable (frozen).

### Closes

Section 14 of `docs/planning/verbosity.md`.



---

## #377 — Verbosity: §15 Verb registry (VerbSpec + initial verb catalog)

**Labels:** feature, p0

Parent: #271

Implements section 15 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the Verb Registry from `docs/planning/verbosity.md` section 15.

### Scope

- `VerbSpec` dataclass: id, namespace, human name, firing context, default profile behavior, supported tokens, default template, default data order, description, severity (`routine | warning | error | progress | navigation | editing | document_state`).
- `VerbRegistry` with `register(verb)`, `get(verb_id)`, `all()`.
- Initial verb catalog (44 verbs from section 15):
  - Navigation: `nav.next_line`, `nav.previous_line`, `nav.next_word`, `nav.previous_word`, `nav.next_character`, `nav.previous_character`, `nav.document_start`, `nav.document_end`, `nav.next_print_page`, `nav.previous_print_page`.
  - Editing: `edit.insert_text`, `edit.delete_character`, `edit.delete_word`, `edit.select_word_right`, `edit.select_line`, `edit.unquote_lines`.
  - Document: `doc.open`, `doc.save`, `doc.save_as`, `doc.modified`, `doc.read_only`, `doc.encoding_changed`.
  - Search: `search.find`, `search.find_next`, `search.find_previous`, `search.no_results`, `search.replace`, `search.replace_all`.
  - System: `system.error`, `system.warning`, `system.info`, `system.progress`, `system.operation_complete`.
  - Legacy: `_legacy`.

### Files

Primary owner (per sub-PR #361):

- `quill/core/verbosity/verbs.py`
- `quill/core/verbosity/registry.py`

### Acceptance

- All 44 verbs registered by default.
- Duplicate registration raises a structured error.
- `get()` returns the registered verb; `all()` returns a tuple sorted by id.

### Closes

Section 15 of `docs/planning/verbosity.md`.



---

## #378 — Verbosity: §16 Per-verb preferences UI

**Labels:** accessibility, feature, p0

Parent: #271

Implements section 16 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the per-verb preferences UI from `docs/planning/verbosity.md` section 16.

### Scope

- Master/detail layout (not a grid).
- Left side: virtual wx.ListCtrl report style, virtual mode.
- Right side: detail pane for selected verb.
- Filter: wx.SearchCtrl that matches verb name and namespace.
- Per-verb row dropdown: Profile default | Quiet | Beginner | Normal | Expert | Custom for this verb…
- `Use default` is the headline; per-row dropdown shows `—` when using default.
- Rendered and syntax preview appear only when customized.

### Files

Primary owner (per sub-PR #364):

- `quill/ui/verbosity_prefs.py` (the CollapsibleVerbTable child panel)

### Acceptance

- Tab order: filter search first, profile picker second, then table.
- The detail pane shows the current override when one exists.
- Search filter narrows the verb list live.
- A11Y-4 contract: every interactive element has a label; SetName/SetHint on the listctrl rows.

### Closes

Section 16 of `docs/planning/verbosity.md`.



---

## #379 — Verbosity: §17 Verbosity Preferences UI (top-level panel)

**Labels:** accessibility, feature, p0

Parent: #271

Implements section 17 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the top-level Verbosity Preferences UI from `docs/planning/verbosity.md` section 17.

### Scope

- Tree:
  - ProfilePicker
  - ChannelMixBox
  - MasteryBox
  - ValidationModeBox
  - SafeModeBox
  - PreviewLabButton
  - AnnouncementHistoryButton
  - CollapsibleVerbTable
    - FilterBar
    - MasterSplit (VerbList + VerbDetailPanel)
  - StatusLine
- Initial focus: Filter SearchCtrl (power users come here to find a verb).
- Status line: named `verbosity_status`; polite for nonblocking, assertive for blocking.

### Files

Primary owner (per sub-PR #364):

- `quill/ui/verbosity_prefs.py`

### Acceptance

- Panel structure matches the tree above.
- Initial focus on Filter SearchCtrl.
- Status line updates via `wx.CallAfter` and is announced politely / assertively per A11Y-4.
- A11Y-4 banned-pattern gate passes.

### Closes

Section 17 of `docs/planning/verbosity.md`.



---

## #380 — Verbosity: §18 Token editor UI (Simple + Advanced)

**Labels:** accessibility, feature, p0

Parent: #271

Implements section 18 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the Token Editor UI from `docs/planning/verbosity.md` section 18.

### Scope

- Two views sharing backing data: Simple (sentence-builder ListBox) and Advanced (raw multiline TextCtrl).
- Mode switcher: wx.RadioBox (not Notebook).
- Simple view: fragments list with Move Up/Down, Insert Token menu (palette of valid tokens), Remove.
- Advanced view: multiline TextCtrl with insert-token menu and live validation mark.
- Review field shows rendered output.
- Insert-token menu only shows tokens valid for the current verb.
- Hotkeys: `Ctrl+T` validate, `Ctrl+Shift+P` preview, `Ctrl+R` read assembled template, `Ctrl+S` save as template, `Escape` cancel.
- Save disabled when validation has errors.

### Files

Primary owner (per sub-PR #364):

- `quill/ui/verbosity_token_editor.py`

### Acceptance

- Both views serialize to the same backing data.
- Insert-token palette is verb-scoped.
- Validation summary speaks on `Ctrl+T`.
- Preview debounced 250ms.
- Save disabled state announced.
- EVT_CHAR_HOOK installed on the modal for hotkeys.

### Closes

Section 18 of `docs/planning/verbosity.md`.



---

## #381 — Verbosity: §19 Templates library (CRUD + cross-verb behavior)

**Labels:** feature, p0

Parent: #271

Implements section 19 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the Templates Library from `docs/planning/verbosity.md` section 19.

### Scope

- Full CRUD in v1: Save, Apply, Delete, Rename.
- Flat wx.ListBox or ListCtrl for browsing.
- Per-row dropdown apply.
- Cross-verb behavior: when applying a template to a verb that doesn't support all tokens, auto-filter invalid tokens and warn. Example: `Applied template Concise. Removed 2 tokens because this verb does not track them: cell, region.`
- No drag-and-drop in 0.7.0.

### Files

Primary owners (per sub-PR #363, #364):

- `quill/core/verbosity/library.py` (#363)
- `quill/ui/verbosity_library.py` (#364)

### Acceptance

- Save persists to `verbosity_custom.json` atomically.
- Apply validates against the target verb and strips invalid tokens.
- Delete prompts for confirmation; undo-able for 5 seconds.
- Rename updates the persisted entry without changing its id.
- Cross-verb warning is spoken and surfaced in the detail pane.

### Closes

Section 19 of `docs/planning/verbosity.md`.



---

## #382 — Verbosity: §20 QVP file format (`.qvp.json` schema)

**Labels:** feature, p0

Parent: #271

Implements section 20 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the QVP file format from `docs/planning/verbosity.md` section 20.

### Scope

- `.qvp.json` extension.
- JSON-only, data-only, no code, no Python execution, schema-validated.
- Namespaced by author.
- `min_quill_version` gated.
- Manually installed in v1.
- Read-only once installed unless copied as user template.

### Required top-level fields

- `schema_version`
- `kind` (must equal `quill-verbosity-pack`)
- `min_quill_version`
- `pack` (with name, author, description, version, license)
- `templates` (list with id, name, applies_to, template)

### Optional fields per template

- `tags`, `preview_text`, `depends`, `data_order`, `separator`, `preview`, `speech_template`, `braille_template`, `visual_template`, `sound_event`

### Files

Primary owners (per sub-PR #363):

- `quill/core/verbosity/qvp.py`
- `quill/core/schemas/qvp.json`

### Acceptance

- JSON schema validates the documented fields and types.
- Loader rejects: non-JSON, schema-invalid, missing required fields, wrong `kind`.
- Loader rejects packs with `min_quill_version` higher than the running QUILL.
- `grep -E 'exec|eval|__import__' quill/core/verbosity/qvp.py` returns no hits.

### Closes

Section 20 of `docs/planning/verbosity.md`.



---

## #383 — Verbosity: §21 QVP install flow (file picker + validate + announce)

**Labels:** accessibility, feature, p0

Parent: #271

Implements section 21 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the QVP install flow from `docs/planning/verbosity.md` section 21.

### Scope

- Library tab button: `Install QVP from file…`
- Flow:
  1. Open file picker.
  2. Validate JSON.
  3. Validate schema.
  4. Check `kind`.
  5. Check `min_quill_version`.
  6. Check required metadata.
  7. Check template IDs.
  8. Check namespace collisions.
  9. Resolve dependencies if supported.
  10. Validate templates against known verbs where possible.
  11. Install pack.
  12. Announce result.
- Spoken sequence example: `Validating pack.` `Minimum QUILL version 0.7.0, you have 0.7.0. OK.` `Pack installed. 2 templates added. Author: Kelly Ford.`
- Dependency behavior: if dependencies are listed but missing, announce `This pack depends on X, which is not installed.` and offer cancel / proceed only if dependencies are optional.

### Files

Primary owners (per sub-PR #363, #364):

- `quill/core/verbosity/qvp.py` (#363)
- `quill/core/verbosity/library.py` (#363)
- `quill/ui/verbosity_library.py` (#364)
- `quill/ui/verbosity_qvp_install.py` (#364) — modal install dialog.

### Acceptance

- All 12 flow steps have a unit test.
- Dependency check tested with present and missing dependencies.
- Spoken sequence recorded in a golden test.
- `QVPInstallResult` reports `accepted`, `rejected_templates`, `warnings`.

### Closes

Section 21 of `docs/planning/verbosity.md`.



---

## #384 — Verbosity: §22 Profile preview on switch (replay last 3)

**Labels:** feature, p0

Parent: #271

Implements section 22 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements profile preview from `docs/planning/verbosity.md` section 22.

### Scope

- When a user changes profile, replay the last three announcements using the new profile.
- Command: `Ctrl+Shift+Enter` (when profile picker has focus) replays profile preview.
- Purpose: users hear the difference between Beginner / Normal / Expert / Quiet without guessing.

### Files

Primary owners (per sub-PR #362, #364):

- `quill/core/verbosity/engine.py` — last-N announcements buffer (#362).
- `quill/ui/verbosity_prefs.py` — profile picker event hook (#364).

### Acceptance

- Last 3 announcements stored per session.
- Switching profiles announces `Profile preview:` then the three replays.
- `Ctrl+Shift+Enter` replays the preview when the profile picker has focus.

### Closes

Section 22 of `docs/planning/verbosity.md`.



---

## #385 — Verbosity: §23 Preview Lab (scenario-based renderer)

**Labels:** feature, p0

Parent: #271

Implements section 23 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the Preview Lab from `docs/planning/verbosity.md` section 23.

### Scope

- Lets users test profiles, templates, channel mixes, and QVP packs against canned scenarios.
- Built-in scenarios:
  - Plain text editing
  - Long document navigation
  - Markdown document
  - Code file
  - Search results
  - Replace operation
  - Save file
  - Open file
  - Error state
  - Warning state
  - Selection movement
  - Print page navigation
  - Status / progress update
  - Future BRF / braille workflow sample
- For each scenario, surface:
  - Speech output
  - Braille output
  - Visual status output
  - Sound event
  - Suppressed content
  - Active profile
  - Active template
  - Active channel mix

### Files

Primary owners (per sub-PR #363, #364):

- `quill/core/verbosity/preview.py` (#363)
- `quill/ui/verbosity_preview_lab.py` (#364)

### Acceptance

- All 14 scenarios have a sample Context.
- Output per channel is shown side-by-side in the lab dialog.
- QVP authors can switch active template and see the rerun output.
- Golden tests cover at least 3 scenarios.

### Closes

Section 23 of `docs/planning/verbosity.md`.



---

## #386 — Verbosity: §24 Announcement history (record + replay + filter)

**Labels:** feature, p0

Parent: #271

Implements section 24 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements Announcement History from `docs/planning/verbosity.md` section 24.

### Scope

- NOT deferred. Spoken output disappears quickly; history gives recovery, confidence, debugging, copyability.
- Commands:
  - `QUILL key + H`: repeat last announcement.
  - `QUILL key + Shift+H`: open Announcement History.
  - `QUILL key + Ctrl+H`: copy last announcement to clipboard.
- Each history entry stores: timestamp, verb id, human name, trigger / chord, active profile, channel mix, speech / braille / visual output, sound event, template source, token values, suppressed content, Quiet / Meeting state, per-verb override state, per-chord override state, QVP source if any, severity.
- History UI: review recent, replay selected, copy selected, explain selected, search / filter, filter by verb / channel / profile / warnings+errors, compare across profiles, clear history, privacy-safe behavior.
- Privacy settings: enable/disable history, max entries, clear on exit, exclude selected document content, clear now.

### Files

Primary owners (per sub-PR #362, #364, #365):

- `quill/core/verbosity/history.py` (#362)
- `quill/ui/verbosity_history.py` (#364)
- `quill/core/keymap.py` — chords (#365)

### Acceptance

- History record holds the documented fields.
- `QUILL key + H` repeats the last announcement.
- Filter widgets narrow the list live.
- Compare-across-profiles uses the engine to rerun each entry.
- Privacy settings round-trip through save/load.

### Closes

Section 24 of `docs/planning/verbosity.md`.



---

## #387 — Verbosity: §25 Why did QUILL say that? (explanation trace)

**Labels:** feature, p0

Parent: #271

Implements section 25 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the explanation trace system from `docs/planning/verbosity.md` section 25.

### Scope

For any recent announcement, the user can ask why it happened. The explanation includes:

- Verb fired
- Triggering command or chord
- Active profile
- Active channel mix
- Template source
- Token values used
- Output per channel
- Suppressed content
- Whether Quiet Mode affected it
- Whether Meeting Mode affected it
- Whether a per-verb override applied
- Whether a per-chord override applied
- Whether a QVP template applied
- Whether sound was suppressed
- Whether routine confirmation was hidden
- Whether validation warnings existed

Example:

```
Verb: nav.next_print_page
Trigger: Ctrl+Page Down
Profile: Expert
Channels: speech, braille, visual
Template source: QVP KellyFord Concise
Speech output: Page 7 of 87
Braille output: p7/87
Visual output: Page 7 of 87
Suppressed: Running head hidden by Expert profile
```

### Files

Primary owners (per sub-PR #362, #364):

- `quill/core/verbosity/explain.py` (#362)
- `quill/ui/verbosity_history.py` (Explain button on a selected entry) (#364)

### Acceptance

- Each announcement in history has an `ExplanationTrace` attached.
- `Explain` button on a selected entry reads the trace aloud.
- The trace includes every documented field.
- Exporting the trace produces plain text (copyable).

### Closes

Section 25 of `docs/planning/verbosity.md`.



---

## #388 — Verbosity: §26 Too Much / Too Little / Just Right (feedback tuning)

**Labels:** feature, p0

Parent: #271

Implements section 26 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements local tuning feedback from `docs/planning/verbosity.md` section 26.

### Scope

- Commands:
  - `QUILL key + Minus`: That was too much.
  - `QUILL key + Plus`: I needed more detail.
  - `QUILL key + 0`: That was just right.
- Stores local preference signals per verb.
- After repeated feedback, QUILL may suggest a change. Example: `You often reduce detail for selection movement. Switch Select Word Right to Expert?`
- Local only, no telemetry, no cloud required, user-controlled, reversible, non-pushy.

### Files

Primary owners (per sub-PR #362, #365):

- `quill/core/verbosity/feedback_tuning.py` (#362)
- `quill/core/keymap.py` — chord registration (#365)

### Acceptance

- Each chord records a feedback signal on the most recent announcement.
- Threshold-based suggestion speaks when crossed.
- `Reset feedback signals` setting clears the store.
- Suggestion can be declined without re-suggesting.

### Closes

Section 26 of `docs/planning/verbosity.md`.



---

## #389 — Verbosity: §27 Mastery-based step down (per-verb threshold + 10-second timeout)

**Labels:** feature, p0

Parent: #271

Implements section 27 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements mastery detection from `docs/planning/verbosity.md` section 27.

### Scope

- Tracks successful repeated use per verb.
- When threshold is crossed, offer step-down.
- 10-second timeout on the offer.
- Speak countdown at 3 seconds.
- Let user accept or ignore.
- Do not repeatedly nag.

Example: `You seem comfortable with Select Word Right. Switch this command to Expert? Press Enter to accept or Escape to keep current verbosity.`

### Controls

- Enable mastery suggestions (default on).
- Mastery threshold (default 25 successful uses).
- Reset mastery data.
- Per-verb disable.

### Files

Primary owners (per sub-PR #362):

- `quill/core/verbosity/mastery.py`

### Acceptance

- Mastery counter increments per success; resets per verb on threshold raise.
- Step-down offer dialog has a 10-second timer; speaks countdown at 3.
- Accept changes the per-verb override; ignore keeps it.
- `Reset mastery data` clears counters.

### Closes

Section 27 of `docs/planning/verbosity.md`.



---

## #390 — Verbosity: §28 Channel-specific templates (speech / braille / visual / sound_event)

**Labels:** feature, p0

Parent: #271

Implements section 28 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements channel-specific templates from `docs/planning/verbosity.md` section 28.

### Scope

- Speech, braille, and visual status are not forced to use the same text.
- Speech: natural and descriptive.
- Braille: compact output.
- Visual status: short summary.
- Sound: event id only.
- Template fields: `template`, `speech_template`, `braille_template`, `visual_template`, `sound_event`.
- Even if the first UI exposes only global templates, the 0.7.0 schema and engine support channel-specific template fields to avoid future breaking changes.

Example templates:

- Speech: `Now reading Chapter 2. Print page 7 of 87. Line 14.`
- Braille: `Ch2 p7/87 l14`
- Visual: `Chapter 2, page 7 of 87, line 14`

### Files

Primary owners (per sub-PR #361, #363):

- `quill/core/verbosity/tokens.py` (#361)
- `quill/core/verbosity/registry.py` (#361)
- `quill/core/verbosity/library.py` (#363)
- `quill/core/schemas/qvp.json` (#363)

### Acceptance

- VerbSpec supports the channel-specific fields.
- Schema validates the optional fields per template.
- Engine routes the right template to the right channel.
- A unit test confirms fallback to `template` when channel-specific fields are absent.

### Closes

Section 28 of `docs/planning/verbosity.md`.



---

## #391 — Verbosity: §29 Safe Mode and Reset (per-verb / per-chord / profile / QVP)

**Labels:** feature, p0

Parent: #271

Implements section 29 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements Verbosity Safe Mode from `docs/planning/verbosity.md` section 29.

### Scope

Safe Mode supports:

- Temporarily disable all custom verbosity.
- Reset this verb.
- Reset this chord.
- Reset this profile.
- Disable all QVP packs.
- Restore built-in verbosity.
- Export current settings before reset.
- Start QUILL with built-in verbosity only.

### UI

A Safe Mode section in Verbosity Preferences with actions:

- Disable custom verbosity temporarily.
- Reset selected verb.
- Reset selected chord.
- Disable QVP packs.
- Restore built-in defaults.
- Export before reset.

### Files

Primary owners (per sub-PR #362, #364):

- `quill/core/verbosity/safe_mode.py` (#362)
- `quill/ui/verbosity_safe_mode.py` (#364)

### Acceptance

- `enter_safe_mode()` disables all per-verb and per-chord overrides; visual floor remains.
- `exit_safe_mode()` restores overrides.
- Reset operations are scoped to the verb / chord / profile as labeled.
- `QUILL_SAFE_MODE=1` environment variable starts QUILL with built-ins only.
- Export-before-reset produces a `.quill-verbosity-profile.json` artifact.

### Closes

Section 29 of `docs/planning/verbosity.md`.



---

## #392 — Verbosity: §30 Import / Export (`.quill-verbosity-profile.json`)

**Labels:** feature, p0

Parent: #271

Implements section 30 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements profile import / export from `docs/planning/verbosity.md` section 30.

### Scope

- `.quill-verbosity-profile.json` extension.
- Export may include:
  - Custom profiles
  - Channel choices
  - Per-verb overrides
  - Per-chord overrides
  - User templates
  - Validation mode
  - Quiet Mode preferences
  - Meeting Mode preferences
  - Mastery settings
  - Too Much / Too Little preferences
  - Preview Lab sample overrides if applicable

### Use cases

- Jeff's quiet meeting setup
- Kelly's screen-reader optimized setup
- Beginner classroom setup
- Expert authoring setup
- Braille-first editing setup
- Markdown authoring setup
- Training lab setup

### Security

- Profile imports are data-only and schema-validated. They do not run code.

### Files

Primary owners (per sub-PR #362, #364):

- `quill/core/verbosity/import_export.py` (#362)
- `quill/core/verbosity/schema.py` (#361) — profile schema.
- `quill/ui/verbosity_import_export.py` (#364)

### Acceptance

- Export produces a JSON file matching the schema.
- Import validates; rejects schema-invalid input with a structured error.
- Round-trip: export → import restores all settings.
- A unit test confirms no `exec` / `eval` / `__import__` paths in `import_export.py`.

### Closes

Section 30 of `docs/planning/verbosity.md`.



---

## #393 — Verbosity: §31 Task-aware profiles (Markdown / Code / Braille / Review / etc.)

**Labels:** feature, p0

Parent: #271

Implements section 31 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements task-aware profiles from `docs/planning/verbosity.md` section 31.

### Scope

Possible task profiles:

- Writing mode
- Coding mode
- Markdown mode
- Review mode
- Braille / transcription mode
- Presentation mode
- Meeting mode
- Training mode

### Initial 0.7.0 behavior

- No forced automatic switching.
- Optional suggestions only.
- Example: `Markdown file detected. Use Markdown verbosity profile?`
- Automatic switching: off by default, user-approved, reversible, per file type configurable.

### Files

Primary owners (per sub-PR #362, #364):

- `quill/core/verbosity/task_profiles.py` (#362)
- `quill/ui/verbosity_prefs.py` — per-file-type mapping UI (#364)

### Acceptance

- Per-file-type mapping setting round-trips through save/load.
- Suggestion appears on file open if automatic is enabled.
- Reject / accept persists per file type.
- Test confirms default is off.

### Closes

Section 31 of `docs/planning/verbosity.md`.



---

## #394 — Verbosity: §32 First-run Verbosity Tour (setup wizard page)

**Labels:** accessibility, feature, p0

Parent: #271

Implements section 32 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the First-Run Verbosity Tour from `docs/planning/verbosity.md` section 32.

### Scope

- Setup Wizard gains a Verbosity page.
- Instead of a raw settings panel, the page asks `How much should QUILL talk while you learn?`
- Choices:
  - Teach me as I go.
  - Keep me informed.
  - Stay out of my way.
  - Be silent except for braille/status.
- After choosing, QUILL previews:
  - Moving by line
  - Saving a file
  - Encountering an error
  - Navigating by page
  - Performing a repeated command

This helps users understand the consequences of the profile selection immediately.

### Files

Primary owners (per sub-PR #365):

- `quill/ui/setup_wizard_pages.py`

### Acceptance

- Wizard page inserted at the right position (per Wave 0 #297 ordering).
- Each choice maps to a built-in profile.
- Preview plays after a choice is selected; user can replay it.
- The page is announced as `Step N of M` (already shipped in the x3 accessibility wave).

### Closes

Section 32 of `docs/planning/verbosity.md`.



---

## #395 — Verbosity: §33 Keyboard Manager integration (Verbosity tab)

**Labels:** accessibility, feature, p0

Parent: #271

Implements section 33 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements Keyboard Manager integration from `docs/planning/verbosity.md` section 33.

### Scope

- The Keyboard Manager gains a Verbosity tab.
- Each chord exposes a verbosity choice:
  - Profile default
  - Quiet
  - Beginner
  - Normal
  - Expert
  - Custom for this chord…
- Example table:

| Chord            | Action            | Verbosity              |
| ---------------- | ----------------- | ---------------------- |
| Ctrl+Home        | Document Start    | Profile default        |
| Ctrl+Shift+Right | Select Word Right | Quiet                  |
| Ctrl+G           | Go to Line        | Custom for this chord… |

- Choosing `Custom for this chord…` opens a mini-editor scoped only to the verbs fired by that chord.
- Entry announcement: `Ctrl+Shift+Right fires Select Word Right. Mini-editor will scope to this verb.`
- Group chords by category: Navigation, Editing, Document, Search, System.
- Support `Ctrl+1..N` to jump between groups.

### Files

Primary owners (per sub-PR #364, #365):

- `quill/ui/keyboard_manager_dialog.py` (#365)
- `quill/ui/verbosity_chord_editor.py` (#364)

### Acceptance

- New tab visible in Keyboard Manager.
- Verbosity column reads `Profile default` / `Quiet` / etc.
- Mini-editor scopes its token list to the verb(s) fired by the selected chord.
- `Ctrl+1..N` jumps between category groups.

### Closes

Section 33 of `docs/planning/verbosity.md`.



---

## #396 — Verbosity: §34 Hotkey plan (chords + conflict resolution)

**Labels:** feature, p0

Parent: #271

Implements section 34 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the hotkey plan from `docs/planning/verbosity.md` section 34.

### Scope

- Global hotkeys:
  - `Ctrl+Shift+Q` toggle Quiet Mode
  - `QUILL key + Q` toggle Quiet Mode
  - `Ctrl+Shift+B` toggle Meeting Mode
  - `Ctrl+Shift+M` open Verbosity Preferences
  - `Ctrl+Shift+Z` undo quiet / verbosity state change
  - `QUILL key + H` repeat last announcement
  - `QUILL key + Shift+H` open Announcement History
  - `QUILL key + Ctrl+H` copy last announcement
  - `QUILL key + Minus` too much
  - `QUILL key + Plus` too little
  - `QUILL key + 0` just right
- Token editor hotkeys:
  - `Ctrl+T` validate
  - `Ctrl+Shift+P` preview
  - `Ctrl+R` read assembled template
  - `Ctrl+S` save as template
  - `Escape` cancel / close
- Profile preview: `Ctrl+Shift+Enter` (when profile picker has focus).

### Conflict note

- If `Ctrl+Shift+Q` was previously used for unquote lines, move unquote lines to `Alt+Shift+Q`.

### Files

Primary owners (per sub-PR #365):

- `quill/core/keymap.py`
- `quill/core/feature_command_map.py`

### Acceptance

- Every chord above is registered with the documented feature id.
- `Alt+Shift+Q` is the new binding for unquote lines.
- All chords appear in CONTROL_REFERENCE after `python -m quill.tools.build_docs`.

### Closes

Section 34 of `docs/planning/verbosity.md`.



---

## #397 — Verbosity: §35 Storage (VerbositySettings + verbosity_custom.json)

**Labels:** feature, p0

Parent: #271

Implements section 35 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements Storage from `docs/planning/verbosity.md` section 35.

### Scope

- New `VerbositySettings` added to `quill.core.settings`.
- Recommended fields:
  - `current_profile`
  - `custom_profiles`
  - `channels_modified`
  - `mastery_enabled`
  - `mastery_threshold`
  - `validation_mode`
  - `quiet_mode`
  - `meeting_mode`
  - `quiet_hours_enabled`
  - `verbosity_custom_overrides`
  - `announcement_history_enabled`
  - `announcement_history_limit`
  - `announcement_history_clear_on_exit`
  - `qvp_enabled_packs`
  - `safe_mode_enabled`
  - `task_profile_suggestions_enabled`

### Custom data file: `verbosity_custom.json`

- User templates.
- Per-verb overrides.
- Per-chord overrides.
- Custom profiles.
- Data order overrides.
- Mastery state.
- Too Much / Too Little preference signals.

Atomic writes. Reject invalid overrides on load with a nonblocking warning dialog.

### Files

Primary owners (per sub-PR #361, #362):

- `quill/core/settings.py` — add the fields (#365 — wiring).
- `quill/core/verbosity/storage.py` (#362)

### Acceptance

- All 16 fields round-trip through save/load.
- Invalid `verbosity_custom.json` triggers a nonblocking warning dialog and starts with empty defaults.
- Atomic write uses `write_json_atomic` (no torn writes).

### Closes

Section 35 of `docs/planning/verbosity.md`.



---

## #398 — Verbosity: §40 Accessibility requirements (screen-reader-first contract)

**Labels:** accessibility, feature, p0

Parent: #271

Implements section 40 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the Accessibility Requirements from `docs/planning/verbosity.md` section 40.

### Scope

- **General**
  - Every dialog has a useful initial focus.
  - Every control has an accessible name.
  - Every interactive element exposes name, role, and value.
  - Every button has a real text label.
  - No icon-only buttons.
  - Every action has a keyboard path.
  - Tab order is logical.
  - Focus indicators are not obscured.
  - Color is not the only signal.
  - Shape prefixes accompany validation states.
  - No motion-only feedback.
  - Plain language is used throughout.
  - Visual badges are supplementary.
  - Spoken and braille output are primary.

### Live regions / status

- Nonblocking warnings: polite.
- Blocking errors: assertive.
- Status line is named and discoverable.
- Validation is reviewable without sight.

### Screen-reader commitments

- Test with NVDA.
- Test with JAWS.
- Verify wx.CollapsiblePane behavior.
- Verify modal hotkeys.
- Verify ListBox Enter behavior.
- Verify disabled Save announcement.
- Verify status bar updates.
- Verify Announcement History workflow.
- Verify Quiet Mode recovery.
- Verify Meeting Mode recovery.

### Files

All verbosity UI files. Also:

- `quill/tools/check_banned_patterns.py`
- `quill/tools/dialog_inventory.py`
- `quill/tools/dialog_button_contract.py`

### Acceptance

- Every verbosity dialog passes A11Y-4 banned-pattern gate.
- Dialog inventory regenerated after each verbosity UI PR.
- Manual NVDA / JAWS smoke log present in the 0.7.0 release notes.

### Closes

Section 40 of `docs/planning/verbosity.md`.



---

## #399 — Verbosity: §41 Testing plan (core + UI + golden)

**Labels:** feature, p0

Parent: #271

Implements section 41 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the verbosity testing plan from `docs/planning/verbosity.md` section 41.

### Scope

#### Core test files

- `tests/unit/core/test_verbosity.py`
- `tests/unit/core/test_verbosity_channels.py`
- `tests/unit/core/test_verbosity_profiles.py`
- `tests/unit/core/test_verbosity_tokens.py`
- `tests/unit/core/test_verbosity_filters.py`
- `tests/unit/core/test_verbosity_parser.py`
- `tests/unit/core/test_verbosity_data_order.py`
- `tests/unit/core/test_verbosity_preview.py`
- `tests/unit/core/test_verbosity_storage.py`
- `tests/unit/core/test_verbosity_qvp.py`
- `tests/unit/core/test_verbosity_library.py`
- `tests/unit/core/test_verbosity_mastery.py`
- `tests/unit/core/test_verbosity_quiet.py`
- `tests/unit/core/test_verbosity_meeting.py`
- `tests/unit/core/test_verbosity_history.py`
- `tests/unit/core/test_verbosity_explain.py`
- `tests/unit/core/test_verbosity_safe_mode.py`
- `tests/unit/core/test_verbosity_import_export.py`
- `tests/unit/core/test_verbosity_feedback_tuning.py`
- `tests/unit/core/test_verbosity_task_profiles.py`
- `tests/unit/core/test_about_info.py`

#### UI test files

- `tests/unit/ui/test_verbosity_prefs.py`
- `tests/unit/ui/test_verbosity_token_editor.py`
- `tests/unit/ui/test_verbosity_data_order.py`
- `tests/unit/ui/test_verbosity_chord_editor.py`
- `tests/unit/ui/test_verbosity_library.py`
- `tests/unit/ui/test_verbosity_qvp_install.py`
- `tests/unit/ui/test_keyboard_manager_verbosity.py`
- `tests/unit/ui/test_quiet_mode.py`
- `tests/unit/ui/test_meeting_mode.py`
- `tests/unit/ui/test_verbosity_history.py`
- `tests/unit/ui/test_verbosity_preview_lab.py`
- `tests/unit/ui/test_verbosity_safe_mode.py`
- `tests/unit/ui/test_verbosity_import_export.py`
- `tests/unit/ui/test_info_pages.py`
- `tests/unit/ui/test_post_show_foreground.py`
- `tests/unit/ui/test_main_frame_quill_key.py`
- `tests/unit/core/test_quill_key_help.py`

#### Script tests

- `tests/unit/scripts/test_build_windows_distribution.py`

### Acceptance

- All 21 core test files exist and pass.
- All 17 UI test files exist and pass.
- Script test for build_windows_distribution passes.

### Closes

Section 41 of `docs/planning/verbosity.md`.



---

## #400 — Verbosity: §42 Golden announcement tests (tests/golden/verbosity/)

**Labels:** feature, p0

Parent: #271

Implements section 42 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the Golden Announcement Tests from `docs/planning/verbosity.md` section 42.

### Scope

- Add golden tests for announcement output under `tests/golden/verbosity/`.
- Each test defines:
  - Verb
  - Context
  - Profile
  - Channel mix
  - Template source
  - Expected speech
  - Expected braille
  - Expected visual
  - Expected sound
  - Expected suppressed content
  - Expected explanation trace

### Example golden case (concept)

```json
{
  "name": "next_print_page_expert",
  "verb": "nav.next_print_page",
  "profile": "expert",
  "channels": ["speech", "braille", "visual"],
  "context": {
    "running_head": "Chapter 2",
    "print_page": 7,
    "print_page_total": 87
  },
  "template_source": "builtin:expert:nav.next_print_page",
  "expected_speech": "Page 7 of 87",
  "expected_braille": "p7/87",
  "expected_visual": "Page 7 of 87",
  "expected_sound": null,
  "expected_suppressed": ["running_head"]
}
```

### Acceptance

- At least 5 golden tests covering Beginner, Normal, Expert, Quiet × at least 3 verbs.
- Each golden test asserts every expected field.
- Test framework reads JSON, runs the engine, compares with deep equality.

### Closes

Section 42 of `docs/planning/verbosity.md`.



---

## #401 — Verbosity: §43 Documentation plan (PRD + userguide + CONTROL_REFERENCE + dev docs)

**Labels:** documentation, p0

Parent: #271

Implements section 43 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the Documentation Plan from `docs/planning/verbosity.md` section 43.

### Scope

Update:

- `docs/Product Requirement Documents and Specifications/QUILL-PRD.md`
- `docs/user guide/userguide.md`
- `docs/CONTROL_REFERENCE.md`
- `docs/release notes/release0.7.0.md`
- `CHANGELOG.md`
- Developer docs for verbs
- Developer docs for tokens
- Developer docs for QVP
- Developer docs for announcement testing

### User guide chapter

Include:

- What verbosity means.
- Choosing Beginner / Normal / Expert / Quiet.
- Quiet Mode.
- Meeting Mode.
- Announcement History.
- Why did QUILL say that?
- Simple token editor.
- Advanced token editor.
- Templates Library.
- QVP install.
- Keyboard Manager verbosity.
- Preview Lab.
- Safe Mode.
- Import / export.

### Developer docs

Include:

- How to register a verb.
- How to declare tokens.
- How to create safe templates.
- How to add filters.
- How to write golden announcement tests.
- How to create QVP packs.
- How to support channel-specific templates.
- How Quillins can register custom verbs.

### Acceptance

- All five canonical docs updated.
- All 15 user-guide subsections present.
- All 8 developer-doc subsections present.

### Closes

Section 43 of `docs/planning/verbosity.md`.



---

## #402 — Verbosity: §44 Manual smoke test (golden path steps 1-65)

**Labels:** documentation, p0

Parent: #271

Implements section 44 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the Manual Smoke Test from `docs/planning/verbosity.md` section 44.

### Scope

A 65-step golden path covering:

1-4 Launch, open Preferences > Verbosity, see four profiles.
5-11 Switch to Beginner, switch to Expert, edit channel checkbox, confirm Modified, switch profile, confirm spoken reset.
12-17 Type in per-verb filter, narrow list, select verb, open token editor (Simple default).
18-22 Arrow through fragments, `Ctrl+R`, switch to Advanced.
23-26 Insert `{column}` from palette, type `{garbage}`, Save disabled.
27-29 `Ctrl+T` validate (spoken), `Ctrl+Shift+P` preview (spoken + status).
30-35 Quiet Mode / Meeting Mode badges, `Ctrl+Shift+Z` quiet undo.
36-40 Open Announcement History, replay, copy, Why did QUILL say that?.
41-42 Preview Lab, run Beginner / Normal / Expert / Quiet on same scenario.
43-44 Save custom template, appears in Library.
45-48 Install sample QVP, metadata spoken, apply QVP template, invalid tokens removed with warning.
49-52 Open Keyboard Manager, set chord to Quiet, press that chord, only that action is quiet.
53-55 Too Much / Too Little / Just Right feedback.
56-59 Safe Mode enabled (custom disabled), disabled (custom returns).
60-62 Export profile, import it, settings restore.
63-64 Help > About shows 3-tab dialog.
65 Run full test suite.

### Acceptance

- Smoke-test script written to `docs/qa/verbosity-smoke-test.md`.
- All 65 steps executable on a Windows 10/11 build.
- Manual log captured against a named build for the 0.7.0 release.

### Closes

Section 44 of `docs/planning/verbosity.md`.



---

## #403 — Verbosity: §45 Verification commands (gates that must be green)

**Labels:** documentation, p0

Parent: #271

Implements section 45 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the Verification Commands gate from `docs/planning/verbosity.md` section 45.

### Scope

The verification set:

- `pytest -q`
- `ruff check .`
- `ruff format --check .`
- `mypy quill\core quill\io`
- `python -m quill.tools.quillin_lint quill\quillins_bundled --strict`

Additional gates:

- Pre-commit hooks pass.
- Module size gate passes (or rebaselined after final wiring, per #356 / #359 pattern).
- Dialog inventory passes.
- Banned patterns pass.
- Network egress checks pass.
- Button contract passes.
- Golden announcement tests pass.
- Manual NVDA smoke test passes.
- Manual JAWS smoke test passes.

### Acceptance

- All five required commands run cleanly on every verbosity sub-PR.
- Each sub-PR lists the verification commands run in the PR body.
- For the final 0.7.0 release, the manual smoke logs are linked from the release notes.

### Closes

Section 45 of `docs/planning/verbosity.md`.



---

## #404 — Verbosity: §46 Order of work (46 steps; sub-PRs follow this)

**Labels:** documentation, p0

Parent: #271

Implements section 46 of `docs/planning/verbosity.md`. Each verbosity design / operational section gets its own issue so we can track it as code lands.

Implements the Order of Work from `docs/planning/verbosity.md` section 46.

### Scope

The 46-step implementation order is:

1. Core channels.
2. Profiles.
3. Styles.
4. TokenSpec.
5. Filters.
6. Parser.
7. Parser tests to high coverage before UI.
8. VerbSpec.
9. Verb registry.
10. Data order.
11. Preview renderer.
12. Engine.
13. Quiet Mode.
14. Meeting Mode.
15. Mastery.
16. Announcement History.
17. Explain trace system.
18. Safe Mode.
19. Feedback tuning.
20. QVP schema.
21. QVP loader / validator.
22. Library model.
23. Import / export.
24. Storage integration.
25. Settings integration.
26. Keymap integration.
27. Token editor UI.
28. Data order UI.
29. Verbosity Preferences UI.
30. Library UI.
31. QVP install UI.
32. Announcement History UI.
33. Preview Lab UI.
34. Safe Mode UI.
35. Chord mini-editor.
36. Keyboard Manager integration.
37. Main frame menu / status bar integration.
38. Setup Wizard integration.
39. About dialog.
40. Distribution script updates.
41. Documentation.
42. Release notes.
43. Version bump.
44. Full verification.
45. Manual screen-reader smoke testing.
46. Rebaseline module size only after all wiring is complete.

### Acceptance

- The 6 sub-PRs (#361-#366) cover steps 1-46 in order.
- Each sub-PR's body references the steps it covers.
- After step 46 lands, `quill/tools/module_size_budgets.json` is rebaselined.

### Closes

Section 46 of `docs/planning/verbosity.md`.



---

# Polish backlog (1.0) — consolidated from the 100 addenda

> **This is the working backlog.** The 100 "Verbosity addendum" sections that
> follow (#405–#504) are the original brainstorm, kept for reference. They are
> deduplicated and triaged here into a small set of themed features. The
> individual addendum issues are closed on the tracker; this section is their
> home. Most "knobs" are not new features — they are per-verb overrides the verb
> registry already models, so they ship as *verbs + the per-verb UI*, not as
> bespoke settings.

## Already covered by the shipped core or the 1.4 UI (no new work)

Three-layer settings (#405), searchable settings (#406), settings undo/history
(#465/#466), test-my-settings (#467), reset granularity (#481), export/import
preview + conflict (#482/#483), try-without-applying (#484), do-not-say-again /
per-announcement suppression (#471/#472), QVP copy-as-template / trust labels /
sample packs (#440/#443/#444/#462), token help / examples / speak-current-template
(#458/#459/#460), better defaults for experts/beginners (#475/#476). These map to
the profile model, the verb registry, the QVP loader/library, and the prefs/token
editor in sub-PR 1.4.

## Themed features worth building (1.0)

1. **Per-category verbosity, via the verb registry.** Indentation/whitespace,
   selection, clipboard, search-result, boundary, progress, mode-change,
   file-operation, and encoding/line-ending announcements (#412–#421, #430/#431,
   #418) are all per-verb overrides — ship the verbs and the per-verb table, not
   ten settings panels.
2. **Status query commands.** "Where am I?", "What changed?", "Speak status bar"
   (#422/#423/#424) — three small, high-value commands.
3. **Announcement flow control.** Budget, repetition collapse, queue policy,
   notification priority, and the support-bundle export (#408/#409/#451/#432/#447).
4. **Safety announcements.** Destructive-action warnings, "undo available",
   before/after, and "what will this change?" confirmation (#500/#501/#502/#474).
5. **Friendly names.** One feature: human-friendly names for technical concepts
   everywhere (consolidates #436/#440/#473/#477).
6. **Status bar surfacing.** Pin-this-status, status badges, favorites, last
   important announcement (#452/#455/#456/#497).
7. **Scope profiles.** Per-workspace / per-file verbosity, session profiles, and
   time-based quiet hours (#434/#435/#485/#486); task-aware Markdown/Code modes
   already exist in core (#393/#427/#428).
8. **Sound learnability.** Earcons-with-text-equivalents and a "learn sounds" mode
   (#453/#454), under the §8 sound design.
9. **Coaching & discovery.** Error coaching, details-on-demand, command-discovery
   announcements, contextual-help hooks (#416/#417/#470/#439).
10. **Braille channel polish.** Braille-specific knobs and the braille status cell
    (#425/#498), under the braille channel.

## Recommend: do not build (screen-reader-redundant or out of scope)

Recorded here deliberately rather than silently dropped:

- **Typing Echo (#411)** and **Command Echo (#499)** — the screen reader already
  echoes typed characters/words and announces outcomes; QUILL adding its own echo
  double-speaks or fights the SR. The correct answer is the **Screen-Reader
  Handoff** mode (#410), not a second echo engine.
- **Speech Rate and Pause knobs (#450)** — QUILL does not own the screen reader's
  voice; rate/pacing is an SR setting.
- **Punctuation and Symbol Profiles (#426)** — punctuation level is a core
  NVDA/JAWS/Narrator setting; duplicating it in QUILL conflicts with the SR. (A
  braille-only punctuation note may live under braille polish.)
- **Smart Status Rotation (#457)** — auto-rotating status is unpredictable for SR
  users. **Multi-Monitor/Presentation Safety (#503)** — the audio half is Meeting
  Mode, already built.
- **Final Recommendation (#504)** — a meta summary, not a feature.
- Reconcile, do not re-implement: **Abbreviation dictionary for announcements
  (#492)** overlaps the existing Abbreviation Manager; **Language/Localization
  readiness (#493)** overlaps the shipped i18n work.

## Remaining spec-section polish (from the closed #271–#404 range)

The verbosity rebuild (sub-PRs 1.1–1.6, #361–#366) shipped and its issue range
(#271 epic + the §-section issues #367–#404) is closed. A few **spec sections
were only partly built**; their remainder is tracked here rather than as open
issues:

- **§8 sound design (#370)** — the per-profile sound *policy* (all / errors-only /
  off) ships in the engine; the master + per-event earcon gating matrix is the
  remaining piece.
- **§22 profile preview on switch (#384)** — the Preview Lab previews any profile
  on demand; auto-replaying the last three announcements when you switch profiles
  is not built.
- **§26 feedback tuning (#388)** — `FeedbackStore` ships; the QUILL key + / − / 0
  chords and the gentle suggestion surface remain.
- **§27 mastery step-down (#389)** — `MasteryTracker` ships; the 10-second offer
  dialog with the 3-second spoken countdown remains.
- **§28 channel-specific templates (#390)** — the engine renders one text to all
  channels today; distinct speech/braille/visual/sound templates per verb remain.
- **§31 task-aware profiles (#393)** — `TaskProfileSuggester` + its setting ship
  (off by default); the on-file-open suggestion prompt remains.
- **§32 first-run verbosity tour (#394)** — a setup-wizard page introducing the
  profiles is not built.

Everything else in the range shipped: §33 Keyboard Manager integration (#395,
commands auto-register), §34 hotkey plan (#396), §40 accessibility contract
(#398, A11Y-4), §41 testing (#399), §42 golden tests (#400), §43 documentation
(#401), §45 verification gates (#403). §44 (#402) is the pre-release manual smoke
run, and §46 (#404) was the build order — both process, not code.

---

## Original addenda (reference archive — issues closed, see backlog above)

## #405 — Verbosity addendum #1: Settings Should Have Three Layers

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 1.

**Title:** Settings Should Have Three Layers

### Design content from planning

To prevent overwhelming users, QUILL should organize verbosity controls into three layers.

## Layer 1: Simple

Shown to everyone.

* Beginner
* Normal
* Expert
* Quiet
* Meeting Mode
* Announcement History
* Reset/Safe Mode

## Layer 2: Customize

For users who want more control.

* Channel checkboxes
* Per-verb overrides
* Per-chord overrides
* Token templates
* QVP packs
* Preview Lab
* Import/export

## Layer 3: Advanced

For power users, testers, pack authors, and contributors.

* Token parser details
* Golden test preview
* Explanation traces
* Channel-specific templates
* Suppression rules
* Repetition collapse settings
* Screen reader handoff behavior
* Braille compacting rules
* Debug logging

This avoids dumping every knob into one giant settings page.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #406 — Verbosity addendum #2: Searchable Settings

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 2.

**Title:** Searchable Settings

### Design content from planning

QUILL should include a search box in Verbosity Preferences.

Users should be able to type:

* “quiet”
* “braille”
* “sound”
* “selection”
* “search results”
* “errors”
* “repeat”
* “history”
* “QVP”
* “keyboard”
* “too much”
* “page”

The settings UI should narrow to matching settings and actions.

This is especially valuable for screen reader users because it avoids arrowing through long settings lists.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #407 — Verbosity addendum #3: Verbosity Recipes

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 3.

**Title:** Verbosity Recipes

### Design content from planning

QUILL should ship with ready-made “recipes” in addition to the four base profiles.

Examples:

* Beginner Writer
* Expert Editor
* Braille First
* Meeting Safe
* Classroom Training
* Markdown Author
* Code Reviewer
* Minimal Navigation
* Detailed Search
* Compare Review
* Document Cleanup
* Transcription Prep

A recipe is not a separate profile engine. It is a saved combination of profile, channel mix, per-verb defaults, and optional templates.

The UI could say:

> Start with a recipe.

Then the user can customize from there.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #408 — Verbosity addendum #4: Announcement Budget

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 4.

**Title:** Announcement Budget

### Design content from planning

Add an “announcement budget” concept.

This prevents QUILL from becoming chatty during repeated actions.

Settings:

* Collapse repeated announcements.
* Suppress identical announcements after N repeats.
* Speak every Nth repeated movement.
* Always speak errors.
* Always speak document boundary changes.
* Always speak mode changes.
* Never suppress warnings.

Example:

If the user holds down Down Arrow, QUILL should not necessarily speak a full context message every time.

Instead:

> Line 14
> Line 15
> Line 16
> 10 more lines moved.

Or in Expert:

> 14
> 15
> 16

This makes QUILL feel calmer and faster.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #409 — Verbosity addendum #5: Repetition Collapse

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 5.

**Title:** Repetition Collapse

### Design content from planning

Repeated announcements should be collapsible.

Example:

If the same message happens repeatedly:

> No next heading.

Instead of saying it ten times, QUILL could say:

> No next heading. Repeated 5 times.

Settings:

* Collapse repeated routine messages.
* Collapse repeated errors.
* Collapse repeated navigation boundary messages.
* Delay before summarizing repeated messages.
* Never collapse critical errors.

This is a huge quality-of-life feature.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #410 — Verbosity addendum #6: Screen Reader Handoff Mode

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 6.

**Title:** Screen Reader Handoff Mode

### Design content from planning

QUILL should avoid fighting the screen reader.

Some information should be spoken by QUILL. Some should be left to the screen reader.

Add a setting:

> Screen reader handoff

Options:

* QUILL speaks full context.
* QUILL speaks only editor-specific context.
* Let screen reader handle text; QUILL speaks state changes only.
* Expert handoff: only errors, modes, and structural changes.

This helps avoid double-speaking.

Example:

When arrowing through text, the screen reader may already read the line. QUILL may only need to add:

> Modified. Markdown heading level 2.

Or:

> Search result 3 of 12.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #411 — Verbosity addendum #7: Typing Echo Controls

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 7.

**Title:** Typing Echo Controls

### Design content from planning

QUILL should expose typing echo preferences separate from screen reader behavior.

Settings:

* Character echo
* Word echo
* No typing echo
* Punctuation echo
* Whitespace echo
* Indentation echo
* Speak tabs
* Speak spaces
* Speak blank lines
* Speak autocorrect or expansion results

This is especially useful for users writing Markdown, code, or structured text.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #412 — Verbosity addendum #8: Indentation and Whitespace Verbosity

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 8.

**Title:** Indentation and Whitespace Verbosity

### Design content from planning

For coding and Markdown, indentation matters.

Add settings:

* Speak indentation changes.
* Speak indentation level only when it changes.
* Speak tabs as “tab” or “4 spaces.”
* Speak trailing spaces.
* Warn on mixed tabs and spaces.
* Warn on indentation-sensitive files.
* Suppress indentation in plain prose.
* Enable indentation detail for Python, YAML, Markdown lists, and code blocks.

Example:

> Indent level 2, list item.

Or:

> Python block, 4 spaces.

This should be task-aware, not noisy everywhere.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #413 — Verbosity addendum #9: Selection Verbosity Knobs

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 9.

**Title:** Selection Verbosity Knobs

### Design content from planning

Selection feedback needs its own controls.

Settings:

* Speak selected text.
* Speak selection length only.
* Speak start and end positions.
* Speak line count.
* Speak word count.
* Speak character count.
* Speak first N characters of selection.
* Speak last N characters of selection.
* Suppress selection text above N characters.
* Announce selection direction.
* Announce rectangular/block selection if supported.

Examples:

Beginner:

> Selected “accessibility agents,” 2 words.

Expert:

> Selected 2 words.

Quiet/Braille:

> sel 2w

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #414 — Verbosity addendum #10: Clipboard Verbosity Knobs

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 10.

**Title:** Clipboard Verbosity Knobs

### Design content from planning

Clipboard actions deserve careful control.

Settings:

* Speak copied text.
* Speak copied length only.
* Speak cut text.
* Speak pasted text.
* Speak paste length only.
* Warn when pasting multiline content.
* Warn when clipboard is empty.
* Warn when copied content includes hidden characters.
* Suppress clipboard text above N characters.

Examples:

> Copied 3 lines, 42 words.

> Pasted 12 lines.

> Clipboard empty.

This avoids accidental huge speech dumps.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #415 — Verbosity addendum #11: Search Result Verbosity Knobs

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 11.

**Title:** Search Result Verbosity Knobs

### Design content from planning

Search is one of the most important places for verbosity control.

Settings:

* Speak result number.
* Speak total results.
* Speak surrounding context.
* Speak line number.
* Speak column.
* Speak wrap-around.
* Speak no-results suggestions.
* Speak replacement count.
* Speak skipped binary/large files if applicable.
* Speak first result automatically.
* Suppress repeated “not found” messages.

Examples:

Beginner:

> Result 3 of 12. Line 42. Found “keyboard manager” in heading level 2.

Expert:

> 3 of 12, line 42.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #416 — Verbosity addendum #12: Error Coaching

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 12.

**Title:** Error Coaching

### Design content from planning

Errors should be more helpful in Beginner mode.

Instead of only:

> Error.

QUILL should support error coaching.

Example:

> Could not save file. The folder may be read-only. Press Ctrl+Shift+E for details.

Settings:

* Beginner error coaching on/off.
* Include likely cause.
* Include suggested next action.
* Include technical details only on request.
* Copy error details to clipboard.
* Add error to Announcement History.

Expert mode can stay concise:

> Save failed. Access denied.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #417 — Verbosity addendum #13: “Details on Demand”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 13.

**Title:** “Details on Demand”

### Design content from planning

QUILL should avoid over-speaking by making more details available on demand.

Pattern:

Say the short version first.

Then offer:

> Press QUILL key + D for details.

Examples:

> Save failed. Press QUILL key + D for details.

> 12 replacements made. Press QUILL key + D for details.

Settings:

* Enable details-on-demand.
* Timeout for details prompt.
* Always offer details for errors.
* Offer details for warnings.
* Never offer details for routine confirmations.

This keeps the main flow fast but keeps help nearby.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #418 — Verbosity addendum #14: Announcement Detail Levels Per Category

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 14.

**Title:** Announcement Detail Levels Per Category

### Design content from planning

Instead of only global Beginner/Normal/Expert, let users tune categories independently.

Categories:

* Navigation
* Editing
* Selection
* Search
* Replace
* File operations
* Markdown
* Code
* Errors
* Warnings
* Progress
* Git/GitHub integration later
* Braille/BRF workflow later

Each category can use:

* Beginner
* Normal
* Expert
* Quiet
* Profile default

Example:

A user might want:

* Expert navigation
* Normal editing
* Beginner search
* Detailed errors
* Quiet selection

This gives real-world flexibility.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #419 — Verbosity addendum #15: Boundary Announcements

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 15.

**Title:** Boundary Announcements

### Design content from planning

Boundary messages should be configurable.

Settings:

* Speak top of document.
* Speak bottom of document.
* Speak start/end of line.
* Speak start/end of selection.
* Speak first/last search result.
* Speak beginning/end of paragraph.
* Speak beginning/end of heading region.
* Speak when navigation wraps.
* Use sound for boundary.
* Use braille-only boundary markers.

Examples:

> Top of document.

> Bottom.

> Wrapped to first result.

Expert users may want very short boundary announcements.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #420 — Verbosity addendum #16: Progress Announcement Controls

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 16.

**Title:** Progress Announcement Controls

### Design content from planning

Long operations need thoughtful progress speech.

Settings:

* Speak progress every N percent.
* Speak progress every N seconds.
* Speak only start and finish.
* Speak errors immediately.
* Braille progress updates.
* Sound on completion.
* Quiet completion behavior.
* Cancel announcement detail.

Examples:

> Converting Markdown to EPUB, 40 percent.

> Complete. 12 files converted, 1 warning.

This will matter for QUILL workflows involving conversion, validation, compare, search across files, and document processing.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #421 — Verbosity addendum #17: Mode Change Announcements

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 17.

**Title:** Mode Change Announcements

### Design content from planning

QUILL should treat mode changes as high-priority announcements.

Examples:

* Insert/overwrite mode.
* Read-only mode.
* Markdown mode.
* Code mode.
* Quiet Mode.
* Meeting Mode.
* Search panel active.
* Compare mode.
* Preview mode.
* Snippet expansion mode.
* Abbreviation mode.
* Console mode if added later.

Settings:

* Always speak mode changes.
* Play sound for mode changes.
* Show status badge.
* Repeat mode on demand.

Command:

* `QUILL key + M`: speak current modes.

Example:

> Markdown file. Expert profile. Quiet Mode off. Meeting Mode off. Modified document.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #422 — Verbosity addendum #18: “Where Am I?” Command

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 18.

**Title:** “Where Am I?” Command

### Design content from planning

Add a command for complete current context.

Recommended:

* `QUILL key + W`: Where am I?

It should speak a profile-aware summary.

Beginner:

> You are in Chapter 2, heading “Token Editor,” line 14 of 80, column 5. Markdown file. Modified. Expert verbosity is off.

Expert:

> Token Editor, line 14, column 5, modified.

Braille:

> Token Editor l14 c5 mod

Settings:

* Include file name.
* Include path.
* Include heading.
* Include line/column.
* Include page.
* Include selection.
* Include modified state.
* Include profile/modes.
* Include encoding.
* Include indentation mode.

This would be one of the most useful screen-reader-first commands in QUILL.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #423 — Verbosity addendum #19: “What Changed?” Command

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 19.

**Title:** “What Changed?” Command

### Design content from planning

Add a command that summarizes what changed recently.

Recommended:

* `QUILL key + Shift+W`: What changed?

Examples:

> Since last checkpoint: 3 lines inserted, 1 heading changed, document modified.

Or:

> Last action: replaced 12 occurrences of “foo” with “bar.”

This can be powered by the same announcement history and event trace infrastructure.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #424 — Verbosity addendum #20: “Speak Status Bar” Command

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 20.

**Title:** “Speak Status Bar” Command

### Design content from planning

The status bar should be reachable.

Recommended:

* `QUILL key + S`: speak status bar.

Output should include:

* File state.
* Line/column.
* Selection.
* Encoding.
* Profile.
* Quiet/Meeting state.
* Modified/read-only state.
* Active mode.
* Current operation if any.

This gives parity with visual users.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #425 — Verbosity addendum #21: Braille-Specific Knobs

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 21.

**Title:** Braille-Specific Knobs

### Design content from planning

Braille users need dedicated controls.

Settings:

* Use compact braille announcements.
* Use full braille announcements.
* Clip braille output to display width.
* Preferred braille display width.
* Use short labels: `ln`, `col`, `p`, `sel`.
* Include page number.
* Include line number.
* Include heading.
* Include selection count.
* Prioritize position over prose.
* Prioritize errors over routine info.
* Use braille-only status markers.

Example compact braille:

> p7/87 l14 c3 mod

This should be separate from speech verbosity.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #426 — Verbosity addendum #22: Punctuation and Symbol Profiles

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 22.

**Title:** Punctuation and Symbol Profiles

### Design content from planning

QUILL should have symbol verbosity presets.

Useful for Markdown and code.

Profiles:

* None
* Some
* Most
* All
* Code
* Markdown
* Math
* Custom

Settings:

* Speak asterisk as star or asterisk.
* Speak backtick.
* Speak hash as heading marker in Markdown.
* Speak brackets.
* Speak quotes.
* Speak underscores.
* Speak indentation.
* Speak list markers.
* Speak table pipes.
* Speak code fences.

Example:

Markdown mode:

> Heading level 2, Verbosity System

Instead of:

> number number space Verbosity System

But in raw/code mode, users may want the actual symbols.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #427 — Verbosity addendum #23: Markdown-Aware Verbosity

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 23.

**Title:** Markdown-Aware Verbosity

### Design content from planning

QUILL should eventually include Markdown-specific verbosity knobs.

Settings:

* Announce heading level.
* Announce list nesting.
* Announce task list checked/unchecked.
* Announce blockquote.
* Announce code block language.
* Announce link text and URL on demand.
* Announce image alt text.
* Announce table cell coordinates.
* Announce horizontal rule.
* Suppress raw Markdown markers when helpful.
* Speak raw markers in code/review mode.

Examples:

> Heading level 2, Token Editor.

> Bullet, level 2.

> Link: QUILL homepage. Press details for URL.

This would make QUILL feel deeply aware of authoring workflows.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #428 — Verbosity addendum #24: Code-Aware Verbosity

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 24.

**Title:** Code-Aware Verbosity

### Design content from planning

For code files, QUILL should have optional code-aware output.

Settings:

* Speak function/class boundaries.
* Speak indentation changes.
* Speak syntax errors if known.
* Speak matching bracket context.
* Speak comment line.
* Speak docstring start/end.
* Speak folded region if folding exists.
* Speak current symbol.
* Speak current scope.
* Speak line diagnostics.
* Speak imports section.
* Speak TODO/FIXME comments.

Examples:

> Function save_template, line 42.

> Indent level 3.

> Closing bracket for if statement.

This should be opt-in and language-aware where possible.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #429 — Verbosity addendum #25: Compare/Diff Verbosity

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 25.

**Title:** Compare/Diff Verbosity

### Design content from planning

QUILL’s compare workflows should get special verbosity.

Settings:

* Speak change type: inserted, deleted, modified.
* Speak changed text.
* Speak line number.
* Speak previous/next change count.
* Speak surrounding context.
* Speak only summary.
* Braille compact diff mode.
* Sound on change boundary.
* Collapse repeated unchanged lines.

Examples:

Beginner:

> Change 4 of 12. Modified line 83. Original: “Normal profile.” New: “Expert profile.”

Expert:

> Change 4 of 12, modified, line 83.

This would be powerful for screen reader users reviewing documents or code.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #430 — Verbosity addendum #26: File Operation Verbosity

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 26.

**Title:** File Operation Verbosity

### Design content from planning

Opening, saving, and exporting should have knobs.

Settings:

* Speak full path.
* Speak file name only.
* Speak extension.
* Speak encoding.
* Speak line ending style.
* Speak modified state.
* Speak read-only state.
* Speak file size.
* Speak autosave status.
* Speak backup status.
* Warn on format conversion.
* Warn on destructive overwrite.

Examples:

> Saved verbosity.md.

> Saved. UTF-8, Windows line endings.

> Warning: saving as plain text may remove formatting.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #431 — Verbosity addendum #27: Encoding and Line Ending Verbosity

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 27.

**Title:** Encoding and Line Ending Verbosity

### Design content from planning

Since QUILL cares about text formats, expose settings for technical users.

Settings:

* Announce encoding on open.
* Announce encoding on save.
* Announce line endings.
* Warn on mixed line endings.
* Warn before changing encoding.
* Speak minimum encoding decision.
* Speak Unicode normalization warnings.
* Speak invalid character replacement warnings.

This pairs nicely with QUILL’s broader document/format ambitions.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #432 — Verbosity addendum #28: Notification Priority Levels

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 28.

**Title:** Notification Priority Levels

### Design content from planning

Announcements should have priorities.

Priority levels:

* Silent
* Trace
* Routine
* Info
* Success
* Warning
* Error
* Critical

Each profile can decide what to do with each priority.

Example:

Expert:

* Routine: suppress
* Info: braille/status only
* Success: short speech
* Warning: speech + braille
* Error: speech + braille + sound
* Critical: assertive speech + sound

This creates a clean architecture for future features.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #433 — Verbosity addendum #29: Verbosity Rules Engine

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 29.

**Title:** Verbosity Rules Engine

### Design content from planning

Add an advanced rules layer later, but design for it now.

Example rules:

* If document is Markdown and line starts with `#`, announce heading level.
* If selection is more than 500 characters, speak count only.
* If command repeats more than 5 times, switch to compact output.
* If Meeting Mode is on, route routine messages to braille only.
* If error occurs, always override Quiet Mode with status/braille and optional speech prompt.

Rules should be data-only and safe.

No arbitrary Python.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #434 — Verbosity addendum #30: Per-Workspace Verbosity

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 30.

**Title:** Per-Workspace Verbosity

### Design content from planning

QUILL could support workspace-level verbosity.

Examples:

* Writing project uses Normal.
* Coding project uses Expert with indentation details.
* Training folder uses Beginner.
* Meeting notes folder uses Quiet/Meeting Safe.
* Braille transcription folder uses Braille First.

Settings:

* Use global defaults.
* Use workspace profile.
* Ask when opening folder.
* Remember choice for this folder.

This makes QUILL adapt to real work contexts.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #435 — Verbosity addendum #31: Per-File Verbosity

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 31.

**Title:** Per-File Verbosity

### Design content from planning

Some files need different behavior.

Examples:

* Markdown guide: heading/list verbosity.
* Python file: indentation/symbol verbosity.
* BRF file: page/line/braille position.
* Log file: timestamp and severity verbosity.
* CSV file: row/column verbosity.

Settings:

* Ask when file type is detected.
* Remember for this file.
* Remember for this extension.
* Never ask again.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #436 — Verbosity addendum #32: Temporary Verbosity Boost

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 32.

**Title:** Temporary Verbosity Boost

### Design content from planning

Sometimes users need more detail for just a moment.

Add:

* `QUILL key + Up`: temporarily increase verbosity for next command.
* `QUILL key + Down`: temporarily decrease verbosity for next command.

Examples:

A user normally works in Expert but wants the next command explained in Beginner.

> Next command will use Beginner detail.

After one command, QUILL returns to the prior profile.

This is magical and very useful.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #437 — Verbosity addendum #33: Hold-to-Explain

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 33.

**Title:** Hold-to-Explain

### Design content from planning

A variation of temporary boost:

If the user holds a command slightly longer or uses a modified chord, QUILL gives more detail.

Example:

* Press command normally: concise.
* Press command with QUILL key: detailed explanation.

This should be used carefully, but it could make learning easier.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #438 — Verbosity addendum #34: Training Mode

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 34.

**Title:** Training Mode

### Design content from planning

Training Mode is different from Beginner.

Beginner changes announcement detail.

Training Mode teaches commands.

Training Mode might say:

> You moved to the next word. The shortcut was Ctrl+Right. You can customize this in Keyboard Manager.

Settings:

* Teach shortcuts.
* Teach concepts.
* Teach related commands.
* Stop teaching after N successful uses.
* Always offer details on demand.
* Include link to help topic.
* Include “do not teach this again.”

This could be wonderful for new users.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #439 — Verbosity addendum #35: Contextual Help Hooks

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 35.

**Title:** Contextual Help Hooks

### Design content from planning

Announcements could connect to help.

Example:

> Unknown token. Press F1 for token help.

Or:

> QVP install failed. Press F1 for pack requirements.

Settings:

* Offer help hints in Beginner.
* Suppress help hints in Expert.
* Always show help in status bar.
* Add help link to explanation trace.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #440 — Verbosity addendum #36: Friendly Names for Technical Concepts

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 36.

**Title:** Friendly Names for Technical Concepts

### Design content from planning

Some settings should use plain language but expose technical terms.

Example:

User-facing:

> Be quiet during meetings.

Technical:

> Meeting Mode: suppress routine speech and sound.

User-facing:

> Say less when I repeat a command.

Technical:

> Repetition collapse.

User-facing:

> Let me hear that again.

Technical:

> Announcement History replay.

This keeps the product friendly without hiding power.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #441 — Verbosity addendum #37: “Confidence Check” Wizard

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 37.

**Title:** “Confidence Check” Wizard

### Design content from planning

After setup, QUILL could run a short confidence check.

It asks:

> Did that feel like too much, too little, or just right?

For sample actions:

* Move by line.
* Save file.
* Search result.
* Error.
* Selection.

This can tune the initial profile.

No AI needed. No telemetry needed.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #442 — Verbosity addendum #38: Community Pack Preview and Diff

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 38.

**Title:** Community Pack Preview and Diff

### Design content from planning

When installing a QVP, QUILL should show what it will change.

Before install:

* Pack name.
* Author.
* Version.
* License.
* Applies to which verbs.
* New templates.
* Conflicting templates.
* Required QUILL version.
* Sample preview.

Add “Compare with current profile.”

Example:

> Current: Page 7 of 87.
> Pack: Chapter 2, page 7 of 87.

This makes QVP install trustworthy.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #443 — Verbosity addendum #39: QVP Trust Labels

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 39.

**Title:** QVP Trust Labels

### Design content from planning

Even without signing in v1, QUILL can provide trust labels.

Labels:

* Built-in
* User-created
* Imported from file
* QVP installed
* Unknown author
* Requires newer QUILL
* Contains unsupported tokens
* Safe data-only pack

This helps users understand source and risk.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #444 — Verbosity addendum #40: QVP “Copy as User Template”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 40.

**Title:** QVP “Copy as User Template”

### Design content from planning

Users should be able to copy a QVP template into their own library.

Action:

> Copy to My Templates

Then they can edit it without modifying the installed pack.

This respects pack integrity while allowing customization.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #445 — Verbosity addendum #41: Verbosity Conflict Checker

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 41.

**Title:** Verbosity Conflict Checker

### Design content from planning

QUILL should detect conflicting settings.

Examples:

* Speech disabled globally but user expects speech template.
* Quiet Mode on while Preview Lab tests speech.
* Per-chord override conflicts with per-verb override.
* QVP template applies to no verbs.
* Braille template exists but braille channel off.
* Sound event configured but sound channel off.

Offer explanations:

> This template has a speech version, but speech is currently off in Quiet Mode.

This prevents confusion.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #446 — Verbosity addendum #42: “Explain My Settings”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 42.

**Title:** “Explain My Settings”

### Design content from planning

Add a summary command:

> Explain my verbosity settings.

Output:

> You are using Expert profile. Speech and braille are on. Sound is errors only. Quiet Mode is off. Meeting Mode is off. Selection movement is set to Quiet. Search results use Beginner detail. Announcement History keeps the last 100 items.

This helps users and support people.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #447 — Verbosity addendum #43: Export Support Bundle

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 43.

**Title:** Export Support Bundle

### Design content from planning

For bug reports and community support, QUILL should export a safe support bundle.

Include:

* Verbosity settings.
* Enabled QVP metadata.
* Recent announcement traces with document text redacted.
* Version.
* Screen reader if detectable.
* OS.
* Active profile.
* Keymap conflicts.

Exclude or redact:

* Document content.
* File paths if privacy mode is enabled.
* Clipboard contents.
* Personal text.

This would make troubleshooting much easier.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #448 — Verbosity addendum #44: Privacy Controls

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 44.

**Title:** Privacy Controls

### Design content from planning

Because Announcement History and traces can contain document text, include privacy settings.

Settings:

* Store announcement history.
* Store document text in history.
* Redact document text in history.
* Clear history on exit.
* Clear history now.
* Do not include text in support exports.
* Private mode for current document.
* Disable history for files in specific folders.

This is important for trust.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #449 — Verbosity addendum #45: Private Document Mode

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 45.

**Title:** Private Document Mode

### Design content from planning

Add a per-document mode:

> Private Document Mode

When enabled:

* Do not store announcement history for this file.
* Do not include text in traces.
* Do not include text in support bundle.
* Copy/replay only structural info unless user explicitly allows.

Useful for:

* Legal documents.
* Medical information.
* Personal writing.
* Password notes.
* Confidential work.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #450 — Verbosity addendum #46: Speech Rate and Pause Knobs

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 46.

**Title:** Speech Rate and Pause Knobs

### Design content from planning

Some users may want announcement pacing controls.

QUILL may not control screen reader speech rate directly, but it can control pacing.

Settings:

* Pause before announcements.
* Pause after mode changes.
* Pause between multi-part announcements.
* Delay details-on-demand prompt.
* Keep announcements short during rapid navigation.
* Interrupt previous announcement on new command.
* Queue announcements.
* Drop stale routine announcements.

This matters when users move quickly.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #451 — Verbosity addendum #47: Announcement Queue Policy

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 47.

**Title:** Announcement Queue Policy

### Design content from planning

QUILL should define how it handles rapid events.

Options:

* Interrupt routine announcements.
* Queue warnings.
* Always speak latest position.
* Drop stale navigation messages.
* Never drop errors.
* Collapse repeated messages.
* Finish current announcement before preview.

This prevents speech backlog.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #452 — Verbosity addendum #48: “Last Important Announcement”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 48.

**Title:** “Last Important Announcement”

### Design content from planning

In addition to last announcement, support last important announcement.

Command:

* `QUILL key + Shift+I`: repeat last important announcement.

Important means:

* Warning
* Error
* Mode change
* Save failure
* Operation complete
* Search no results

This helps when routine navigation has already replaced the last announcement.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #453 — Verbosity addendum #49: Earcons With Text Equivalents

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 49.

**Title:** Earcons With Text Equivalents

### Design content from planning

If QUILL uses sounds, every sound must have a text equivalent.

Settings:

* Sound only when text equivalent is available.
* Speak sound meaning on first use.
* Learn sounds mode.
* Disable decorative sounds.
* Error sound on/off.
* Success sound on/off.
* Boundary sound on/off.

Example first-use teaching:

> You heard the boundary sound. It means top or bottom of a region.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #454 — Verbosity addendum #50: Learn Sounds Mode

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 50.

**Title:** Learn Sounds Mode

### Design content from planning

A small onboarding feature:

> Learn QUILL sounds

The user can arrow through sounds:

* Success
* Warning
* Error
* Boundary
* Mode change
* Completion
* Search result

Each plays and explains its meaning.

This makes sound usable rather than mysterious.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #455 — Verbosity addendum #51: Announcement Favorites

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 51.

**Title:** Announcement Favorites

### Design content from planning

Let users mark helpful announcements or templates as favorites.

Use cases:

* Favorite a template.
* Favorite a QVP pack.
* Favorite a history entry.
* Favorite a Preview Lab scenario.
* Favorite a setting.

This may be optional, but it adds polish.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #456 — Verbosity addendum #52: “Pin This Status”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 52.

**Title:** “Pin This Status”

### Design content from planning

Allow a user to pin one piece of status to the status bar or braille/status output.

Examples:

* Current heading
* Current page
* Current line/column
* Current profile
* Modified state
* Selection count
* Search result count

Braille users especially may appreciate persistent compact status.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #457 — Verbosity addendum #53: Smart Status Rotation

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 53.

**Title:** Smart Status Rotation

### Design content from planning

For limited braille/status space, QUILL could rotate or prioritize status fields.

Priority order examples:

* Errors
* Warnings
* Current mode
* Selection
* Position
* Modified state
* Profile

Settings:

* Prioritize position.
* Prioritize document state.
* Prioritize search.
* Prioritize braille page.
* Custom order.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #458 — Verbosity addendum #54: “Speak Current Template”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 54.

**Title:** “Speak Current Template”

### Design content from planning

In token editor and per-verb settings, add:

> Speak current template

Command:

* `Ctrl+Shift+R`

This reads:

* Human preview.
* Raw template.
* Supported tokens.
* Validation state.
* Source.

Useful for template authors.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #459 — Verbosity addendum #55: Token Help on Demand

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 55.

**Title:** Token Help on Demand

### Design content from planning

In the token palette, pressing F1 on a token should explain it.

Example:

> print_page: The current print page number if available. Type: integer. Filters allowed: ordinal, pad. Available for print page navigation verbs.

This helps nontechnical users learn the system.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #460 — Verbosity addendum #56: Template Examples Per Token

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 56.

**Title:** Template Examples Per Token

### Design content from planning

Each token should include examples.

Example for `{selection_count}`:

* “3 characters selected”
* “2 words selected”
* “4 lines selected”

The token editor could expose:

> Examples for this token

This makes customization less intimidating.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #461 — Verbosity addendum #57: Pack Author Mode

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 57.

**Title:** Pack Author Mode

### Design content from planning

For QVP authors, add an advanced mode.

Features:

* Validate all templates.
* Preview against all built-in scenarios.
* Export sample QVP.
* Check unsupported tokens.
* Check missing metadata.
* Check channel-specific fields.
* Generate golden test fixtures.
* Copy pack summary.

This helps the community create high-quality packs.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #462 — Verbosity addendum #58: Built-In Sample QVPs

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 58.

**Title:** Built-In Sample QVPs

### Design content from planning

Ship a few sample packs:

* Beginner Friendly
* Expert Minimal
* Braille Compact
* Markdown Author
* Meeting Safe
* Compare Review

These demonstrate the system and give users useful starting points.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #463 — Verbosity addendum #59: “Make This My Default”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 59.

**Title:** “Make This My Default”

### Design content from planning

When a user customizes a verb, template, or profile, offer:

> Make this my default for similar actions?

Examples:

* All navigation commands.
* All selection commands.
* All search commands.
* All Markdown commands.
* All errors.

This reduces repetitive customization.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #464 — Verbosity addendum #60: Bulk Editing

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 60.

**Title:** Bulk Editing

### Design content from planning

Advanced users should be able to bulk apply settings.

Examples:

* Set all navigation to Expert.
* Set all selection to Quiet.
* Set all errors to Beginner detail.
* Apply template to all search verbs.
* Reset all Markdown verbs.

This should live in Advanced or Library, not the basic UI.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #465 — Verbosity addendum #61: Undo for Settings Changes

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 61.

**Title:** Undo for Settings Changes

### Design content from planning

Verbosity settings changes should be undoable.

Examples:

> Applied Expert to 12 navigation verbs. Press Ctrl+Z to undo.

This is especially important for bulk changes and QVP applies.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #466 — Verbosity addendum #62: Settings Change History

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 62.

**Title:** Settings Change History

### Design content from planning

Keep a small local history of verbosity settings changes.

Useful actions:

* Undo last change.
* View recent changes.
* Restore previous verbosity state.
* Compare before/after.

This helps users experiment safely.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #467 — Verbosity addendum #63: “Test My Current Settings”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 63.

**Title:** “Test My Current Settings”

### Design content from planning

Add a button:

> Test my current settings

It runs a short Preview Lab sequence:

* Navigation
* Selection
* Search
* Save
* Error

Then asks:

> Was that too much, too little, or just right?

This ties together Preview Lab and feedback tuning.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #468 — Verbosity addendum #64: Recommended Settings Suggestions

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 64.

**Title:** Recommended Settings Suggestions

### Design content from planning

QUILL can make local, rules-based suggestions.

Examples:

* “You use Quiet Mode often. Make Meeting Safe your default for this workspace?”
* “You often mark selection announcements as too much. Set selection to Expert?”
* “You installed a braille compact pack but braille is off. Turn braille channel on?”
* “You are editing Markdown files often. Enable Markdown-aware announcements?”

No AI required. No telemetry required.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #469 — Verbosity addendum #65: Accessibility Persona Setup

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 65.

**Title:** Accessibility Persona Setup

### Design content from planning

Setup Wizard could ask what kind of experience the user wants.

Not medical or identity-based. Just workflow-based.

Examples:

* I am learning QUILL.
* I move quickly and want less speech.
* I use braille heavily.
* I often work in meetings.
* I write Markdown.
* I write code.
* I review documents.
* I want maximum guidance.

Then QUILL chooses a recipe.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #470 — Verbosity addendum #66: Command Discovery Announcements

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 66.

**Title:** Command Discovery Announcements

### Design content from planning

In Beginner or Training Mode, QUILL can occasionally teach related commands.

Example:

> You used Find. Press F3 for next result.

Or:

> You selected text. Press Ctrl+C to copy or Shift+Arrow to extend selection.

Settings:

* Enable command discovery.
* Only in Beginner.
* Stop after N times.
* Never repeat dismissed tips.
* Reset tips.

This makes QUILL feel like a teacher.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #471 — Verbosity addendum #67: “Do Not Say This Again”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 67.

**Title:** “Do Not Say This Again”

### Design content from planning

For any optional tip or repeated guidance, allow:

> Do not say this again.

Command:

* `QUILL key + Delete`: do not say this tip again.

This gives users control over teaching behavior.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #472 — Verbosity addendum #68: Per-Announcement Suppression

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 68.

**Title:** Per-Announcement Suppression

### Design content from planning

Users should be able to suppress a specific announcement.

Example:

After QUILL says something annoying:

* `QUILL key + Shift+Minus`: make this specific announcement quieter.

QUILL asks:

> Suppress this exact announcement, this verb, or this category?

Options:

* This exact message.
* This verb.
* This category.
* Cancel.

This is powerful, but should be under Advanced or confirmation-driven.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #473 — Verbosity addendum #69: Announcement Labels

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 69.

**Title:** Announcement Labels

### Design content from planning

Each announcement could have internal labels.

Examples:

* navigation
* selection
* repeated
* boundary
* error
* warning
* markdown
* code
* search
* progress
* clipboard

Labels enable:

* Filtering history.
* Applying rules.
* Bulk editing.
* Explanation.
* Golden tests.
* Category settings.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #474 — Verbosity addendum #70: “What Will This Change?” Confirmation

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 70.

**Title:** “What Will This Change?” Confirmation

### Design content from planning

Before applying a big change, QUILL should summarize.

Example:

> This will set 18 navigation verbs to Expert and suppress routine movement confirmations. Continue?

For QVP:

> This pack will add 12 templates and apply none automatically.

For reset:

> This will remove 7 custom verb overrides and 2 chord overrides.

This prevents surprises.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #475 — Verbosity addendum #71: Better Defaults for Experts

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 71.

**Title:** Better Defaults for Experts

### Design content from planning

Expert should not merely be “less.”

It should be smarter.

Expert should prioritize:

* Position changes.
* Boundaries.
* Errors.
* Search results.
* Selection size.
* Mode changes.
* Operation completion.

Expert should suppress:

* Routine success confirmations.
* Obvious repeated context.
* Teaching hints.
* Long prose.

This distinction matters.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #476 — Verbosity addendum #72: Better Defaults for Beginners

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 72.

**Title:** Better Defaults for Beginners

### Design content from planning

Beginner should not merely be “more.”

It should be educational.

Beginner should include:

* Context.
* Next action hints.
* Recovery hints.
* Meaning of sounds.
* Meaning of modes.
* Where settings can be changed.
* Clear plain-language errors.

But it should still use repetition collapse to avoid becoming exhausting.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #477 — Verbosity addendum #73: Human-Friendly Names Everywhere

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 73.

**Title:** Human-Friendly Names Everywhere

### Design content from planning

Avoid internal labels in the UI unless in advanced mode.

Use:

* “Say less during repeated commands”
* “Keep errors loud”
* “Use braille-friendly short messages”
* “Let me hear that again”
* “Explain why QUILL said this”
* “Preview before saving”
* “Restore safe defaults”

Instead of exposing only:

* `repetition_collapse`
* `error_priority`
* `braille_template`
* `history_replay`
* `trace_explain`
* `validation_mode`

Advanced mode can show internal IDs.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #478 — Verbosity addendum #74: “Copy Debug Summary”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 74.

**Title:** “Copy Debug Summary”

### Design content from planning

From “Why did QUILL say that?” provide:

> Copy debug summary

It should copy a clean support-ready report.

Example:

```text
QUILL Verbosity Debug Summary
Verb: nav.next_print_page
Trigger: Ctrl+Page Down
Profile: Expert
Channels: speech, braille, visual
Template source: QVP KellyFord Concise
Speech: Page 7 of 87
Braille: p7/87
Suppressed: running_head, line
Quiet Mode: off
Meeting Mode: off
```

This is great for bug reports.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #479 — Verbosity addendum #75: “Report This Announcement”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 75.

**Title:** “Report This Announcement”

### Design content from planning

Optional future integration:

> Report this announcement

It creates a local issue template or copies a GitHub-ready report.

Include:

* Debug summary.
* QUILL version.
* Profile.
* Verb.
* Template source.
* Expected behavior field.
* Actual behavior field.

No automatic upload required.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #480 — Verbosity addendum #76: Documentation From Settings

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 76.

**Title:** Documentation From Settings

### Design content from planning

Each setting should have:

* Plain-language description.
* Example.
* Recommended users.
* Default value.
* Related settings.

The UI can expose this through F1 or Help.

This makes the advanced system learnable.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #481 — Verbosity addendum #77: Default Reset Granularity

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 77.

**Title:** Default Reset Granularity

### Design content from planning

Reset should be granular.

Options:

* Reset current control.
* Reset current verb.
* Reset current category.
* Reset current profile.
* Reset all custom templates.
* Reset all QVP packs.
* Reset all verbosity settings.
* Reset everything except user templates.
* Reset everything except QVP installs.

Granular reset makes users less afraid.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #482 — Verbosity addendum #78: Settings Export Preview

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 78.

**Title:** Settings Export Preview

### Design content from planning

Before exporting a profile, show what is included.

Options:

* Include user templates.
* Include QVP references.
* Include QVP contents.
* Include per-verb overrides.
* Include per-chord overrides.
* Include local tuning data.
* Include mastery data.
* Exclude history.
* Exclude private document rules.

This gives control and privacy.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #483 — Verbosity addendum #79: Import Conflict Wizard

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 79.

**Title:** Import Conflict Wizard

### Design content from planning

When importing a profile, handle conflicts accessibly.

Examples:

* Same template name.
* Same profile name.
* Missing QVP.
* Unsupported QUILL version.
* Unknown token.
* Chord no longer exists.

Offer:

* Rename imported item.
* Replace existing.
* Keep both.
* Skip.
* Cancel import.

Announce each conflict clearly.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #484 — Verbosity addendum #80: “Try Without Applying”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 80.

**Title:** “Try Without Applying”

### Design content from planning

For QVPs, recipes, and imported profiles, allow:

> Try temporarily

This applies settings for the current session only.

Then:

> Keep these settings?

Options:

* Keep.
* Revert.
* Save as new profile.

This encourages experimentation.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #485 — Verbosity addendum #81: Session Profiles

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 81.

**Title:** Session Profiles

### Design content from planning

Sometimes users want temporary settings.

Examples:

* “For this meeting only.”
* “For this file only.”
* “Until QUILL closes.”
* “For the next hour.”
* “Until I turn it off.”

Add session-scoped verbosity changes.

This is useful for Meeting Mode, training, demos, and one-off workflows.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #486 — Verbosity addendum #82: Time-Based Quiet Hours

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 82.

**Title:** Time-Based Quiet Hours

### Design content from planning

The original plan put Quiet Hours scheduler out of scope. It can remain later, but design hooks should exist.

Settings:

* Enable scheduled quiet hours.
* Start time.
* End time.
* Days.
* Use Meeting Safe profile.
* Allow errors through.
* Speak reminder before entering.
* Undo with Ctrl+Shift+Z.

This could be v0.7.x, but the architecture should allow it.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #487 — Verbosity addendum #83: Focus Mode

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 83.

**Title:** Focus Mode

### Design content from planning

Focus Mode is slightly different from Quiet Mode.

Focus Mode could reduce everything except:

* Errors
* Save failures
* Search results
* Explicit user-requested status

Useful for writing.

Command:

* `QUILL key + F`: Focus Mode toggle, if no conflict.

This could be a recipe built on the same engine.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #488 — Verbosity addendum #84: Review Mode

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 84.

**Title:** Review Mode

### Design content from planning

Review Mode could increase structural announcements.

Useful for proofreading, Markdown review, compare, and accessibility checking.

It may announce:

* Heading levels.
* List nesting.
* Link text.
* Image alt text.
* Table position.
* Extra spaces.
* Repeated words.
* Unicode oddities.
* Formatting markers.

This aligns with QUILL’s broader document quality mission.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #489 — Verbosity addendum #85: “Readability / Accessibility Verbosity”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 85.

**Title:** “Readability / Accessibility Verbosity”

### Design content from planning

Future GLOW/QUILL alignment could include announcements for document quality.

Examples:

> Heading level skipped from 2 to 4.

> Link text says click here.

> Image missing alt text.

> Table may need headers.

These should have their own verbosity category so users can control how much guidance they receive.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #490 — Verbosity addendum #86: Microcopy Style Settings

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 86.

**Title:** Microcopy Style Settings

### Design content from planning

Some users prefer different announcement language.

Settings:

* Friendly
* Professional
* Minimal
* Technical
* Teaching

Example:

Friendly:

> All set. Your file is saved.

Professional:

> File saved.

Technical:

> Save completed: verbosity.md, UTF-8.

This is not just verbosity; it is tone.

QVP packs could also define microcopy style.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #491 — Verbosity addendum #87: “Use My Words” Custom Labels

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 87.

**Title:** “Use My Words” Custom Labels

### Design content from planning

Allow users to rename certain spoken labels.

Examples:

* Say “chapter” instead of “running head.”
* Say “page” instead of “print page.”
* Say “quiet” instead of “silenced.”
* Say “mark” instead of “bookmark.”

This is advanced, but it helps users personalize QUILL.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #492 — Verbosity addendum #88: Abbreviation Dictionary for Announcements

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 88.

**Title:** Abbreviation Dictionary for Announcements

### Design content from planning

Add an optional abbreviation layer.

Examples:

* “column” → “col”
* “selection” → “sel”
* “modified” → “mod”
* “heading” → “hdg”
* “paragraph” → “para”

Separate dictionaries for:

* Speech
* Braille
* Visual status

This supports compact output without requiring every template to be rewritten.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #493 — Verbosity addendum #89: Language and Localization Readiness

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 89.

**Title:** Language and Localization Readiness

### Design content from planning

Design announcement strings so they can be localized.

Requirements:

* Avoid concatenating untranslatable fragments.
* Token templates should support localization.
* QVP metadata should declare language.
* Built-in templates should be localizable.
* Date/time filters should be locale-aware.
* Pluralization should be locale-aware where possible.

This matters if QUILL becomes international.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #494 — Verbosity addendum #90: Accessibility Testing Assistant Mode

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 90.

**Title:** Accessibility Testing Assistant Mode

### Design content from planning

A future testing mode could speak more diagnostic information.

Example:

> Button has accessible name Save. Role button. Enabled.

For QUILL UI development, this could help contributors verify accessibility.

This is advanced and probably not default, but it fits QUILL’s mission.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #495 — Verbosity addendum #91: Developer “Trace Verbosity”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 91.

**Title:** Developer “Trace Verbosity”

### Design content from planning

Developers should be able to enable trace output.

Settings:

* Log every verb fired.
* Log suppressed announcements.
* Log channel routing.
* Log template chosen.
* Log token derivation failure.
* Log QVP source.
* Log timing.
* Log screen reader handoff.

This should be separate from user Announcement History.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #496 — Verbosity addendum #92: Performance Knobs

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 92.

**Title:** Performance Knobs

### Design content from planning

For very large files or rapid navigation, QUILL should stay responsive.

Settings/engine behavior:

* Drop stale routine messages.
* Limit token derivation cost.
* Cache expensive token values.
* Avoid blocking UI thread.
* Use async where safe.
* Never block typing for speech.
* Time out expensive preview render.

Performance should be part of the design.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #497 — Verbosity addendum #93: Status Badges

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 93.

**Title:** Status Badges

### Design content from planning

Status bar badges should be consistent.

Possible badges:

* `[Q]` Quiet
* `[M]` Meeting
* `[F]` Focus
* `[R]` Review
* `[B]` Braille-first
* `[T]` Training
* `[P]` Private document
* `[H]` History enabled

Badges are sighted supplementary indicators. They must always have accessible equivalents.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #498 — Verbosity addendum #94: Braille Status Cell

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 94.

**Title:** Braille Status Cell

### Design content from planning

If possible, create a compact status string optimized for braille:

Example:

```text
Q off | M off | Expert | l14 c3 | mod
```

Or compact:

```text
Exp l14 c3 mod
```

Users could choose status order.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #499 — Verbosity addendum #95: “Command Echo”

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 95.

**Title:** “Command Echo”

### Design content from planning

Some users like hearing the command they invoked.

Settings:

* Speak command name.
* Speak shortcut.
* Speak result only.
* Speak both command and result.
* Speak command only in Training Mode.
* Suppress command echo in Expert.

Example:

> Ctrl+S, Save file. Saved.

Or Expert:

> Saved.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #500 — Verbosity addendum #96: “Before and After” Announcements

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 96.

**Title:** “Before and After” Announcements

### Design content from planning

For actions that transform text, QUILL could optionally speak before/after summaries.

Examples:

* Case conversion.
* Trim whitespace.
* Sort lines.
* Format document.
* Replace all.
* Markdown conversion.

Example:

> Converted 12 lines to title case.

Details on demand can expose before/after examples.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #501 — Verbosity addendum #97: Destructive Action Warnings

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 97.

**Title:** Destructive Action Warnings

### Design content from planning

Verbosity should include special handling for destructive actions.

Examples:

* Delete file.
* Replace all.
* Clear document.
* Close unsaved file.
* Reset settings.
* Uninstall QVP.
* Bulk apply template.

Settings:

* Always confirm destructive actions.
* Speak full consequence in Beginner.
* Speak concise warning in Expert.
* Require typed confirmation for high-risk actions.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #502 — Verbosity addendum #98: “Undo Available” Announcements

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 98.

**Title:** “Undo Available” Announcements

### Design content from planning

After actions that can be undone, QUILL may announce undo availability.

Beginner:

> Replaced 12 occurrences. Press Ctrl+Z to undo.

Expert:

> Replaced 12. Undo available.

Settings:

* Speak undo hints in Beginner.
* Suppress undo hints in Expert.
* Always speak undo after destructive bulk changes.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #503 — Verbosity addendum #99: Multi-Monitor / Presentation Safety

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 99.

**Title:** Multi-Monitor / Presentation Safety

### Design content from planning

For users presenting or teaching, Meeting Mode could include presentation safety.

Settings:

* Suppress private file paths.
* Suppress clipboard contents.
* Suppress selected text.
* Speak only structural summaries.
* Disable history storage during presentation.
* Hide private status fields.

This helps during workshops and screen sharing.

---

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #504 — Verbosity addendum #100: Final Recommendation

**Labels:** feature, p0

Parent: #271

Parent: #271 (Verbosity rebuild). Source: `docs/planning/screen reader first.md` item 100.

**Title:** Final Recommendation

### Design content from planning

Add these ideas as optional expansion sections to the 0.7.0 plan, but do not expose all knobs at once.

The highest-value additions to consider for 0.7.0 are:

1. Searchable verbosity settings.
2. Announcement budget and repetition collapse.
3. Screen reader handoff mode.
4. Typing echo and indentation controls.
5. Selection and clipboard verbosity knobs.
6. Search result verbosity knobs.
7. Where Am I command.
8. Speak Status Bar command.
9. Braille-specific knobs.
10. Details on Demand.
11. QVP preview/diff before install.
12. Privacy controls for history and traces.
13. Import conflict wizard.
14. Try Without Applying.
15. Temporary verbosity boost.

These features would make QUILL feel truly screen-reader-first, not merely accessible.

They preserve the core philosophy:

> QUILL should meet users where they are, let them work the way they want, and always give them a safe way back.

### Implementation guidance

This item is part of the 100-item addendum to the Verbosity System. The user has directed that the addendum ships in 0.7.0 alongside the 49 non-negotiables (covered by sub-PRs #361-#366). Implement the design above; pick the simplest UX that satisfies it.

### Acceptance

- The behavior described in the design content is observable.
- It passes A11Y-4 (accessible name, label-then-control, no icon-only buttons).
- It round-trips through save/load where settings-driven.
- One unit test (or UI test) covers the happy path.
- A changelog / userguide / CONTROL_REFERENCE update is included if user-facing.



---

## #602 — [Planning Archive] Verbosity System framing, scoping, risks, and release framing - 0.7.0

**Labels:** documentation, enhancement

## Status

The Verbosity System design source-of-truth is in the repo today as
`docs/planning/verbosity.md` (2543 lines, 52 sections). The
implementation work for 0.7.0 Beta 1 is fully tracked by issues
#361-#366 (verbosity sub-PRs) and #367-#504 (per-verb token scoping,
100 items, the "screen reader first" list). This issue captures the
remaining design content that is not already tracked in issues, so
the planning folder can be retired.

## Why captured here

The `docs/planning/` folder is being retired as part of the 0.7.0
release-readiness work. Per the project's planning-folder retirement
rule, planning files can be deleted once their content is captured in
issues. This issue is the canonical archive of the framing and scoping
content from `verbosity.md` that is not already tracked.

## What is already in issues

- Sub-PRs for the verbosity feature: #361, #362, #363, #364, #365, #366
- Per-verb token scoping (100 items): #405-#504 (from
  `docs/planning/screen reader first.md`, which is also being retired)
- The verbosity.md sections §1-§35 and the subsections of §36 (§37 UI
  Modules) that map directly to the sub-PR work above

## Content captured from verbosity.md §36-§52

The remaining content from §36 onwards is the deployment and packaging
plan, the module/file list, the feature command list, accessibility
requirements, the testing plan, the risks, non-negotiables, release
positioning, success criteria, and final statement. These are
captured below in the order they appear in `verbosity.md`.

### §36 Core Modules

Recommended new core package: `quill/core/verbosity/`.

Files in `quill/core/verbosity/`:

- `__init__.py`
- `channels.py`
- `styles.py`
- `profiles.py`
- `tokens.py`
- `parser.py`
- `verbs.py`
- `registry.py`
- `data_order.py`
- `engine.py`
- `mastery.py`
- `quiet.py`
- `meeting.py`
- `storage.py`
- `schema.py`
- `preview.py`
- `qvp.py`
- `library.py`
- `history.py`
- `explain.py`
- `safe_mode.py`
- `import_export.py`
- `task_profiles.py`
- `feedback_tuning.py`

Responsibilities are: `channels.py` defines the Channel enum;
`styles.py` defines verbosity style concepts; `profiles.py` defines
built-in profiles and custom profile model; `tokens.py` defines
TokenSpec, filters, type checks, and helpers; `parser.py` parses
templates and returns validation output; `verbs.py` defines VerbSpec
and built-in verbs; `registry.py` is the central verb lookup and
registration; `data_order.py` handles ordered token rendering;
`engine.py` is the central routing engine; `mastery.py` tracks
mastery and step-down suggestions; `quiet.py` is the Quiet Mode
controller; `meeting.py` is the Meeting Mode controller; `storage.py`
reads/writes verbosity customization data; `schema.py` defines the
schema for settings; `preview.py` is the preview renderer;
`qvp.py` reads/writes QVP files; `library.py` is the Templates
Library model; `history.py` records announcement history;
`explain.py` produces explanation traces; `safe_mode.py` is the safe
reset recovery; `import_export.py` imports/exports full profiles;
`task_profiles.py` models task-scoped profiles;
`feedback_tuning.py` handles the user feedback
("too much"/"too little"/"just right") pipeline.

### §37 UI Modules

Recommended new UI package: `quill/ui/verbosity/`. Files:
`verbosity_prefs.py` (main settings), `verbosity_token_editor.py`
(Simple and Advanced token editor), `verbosity_data_order.py` (data
order editor), `verbosity_chord_editor.py` (mini-editor scoped to
chord-fired verbs), `verbosity_library.py` (Templates Library and
QVP install flow), `verbosity_history.py` (Announcement History
viewer), `verbosity_preview_lab.py` (scenario-based preview tool),
`verbosity_safe_mode.py` (recovery and reset UI),
`verbosity_import_export.py` (import/export UI for full profiles),
and `about_dialog.py` (three-tab About dialog: Overview, Dependencies,
Links).

### §38 Files to Modify

- **Core**: `quill/core/feature_command_map.py`,
  `quill/core/keymap.py`, `quill/core/settings.py`,
  `quill/core/settings_specs.py`, `quill/core/about_info.py`.
- **UI**: `quill/ui/main_frame.py`, `quill/ui/main_frame_menu.py`,
  `quill/ui/main_frame_quill_key.py`,
  `quill/ui/main_frame_statusbar.py`, `quill/ui/info_pages.py`,
  `quill/ui/keyboard_manager_dialog.py`,
  `quill/ui/setup_wizard_pages.py`.
- **Quillins**: `quill/quillins_bundled/doc-guardian/extension.py`
  (add hook for Quillins to register custom verbs).
- **Scripts**: `scripts/build_windows_distribution.py` (include
  `verbosity_custom.json`, `qvps/*.qvp.json`, exported verbosity
  profiles if needed).
- **Tooling**: `quill/tools/module_size_budgets.json` (rebaseline
  after integration).
- **Versioning**: `quill/__init__.py`, `installer/quill.iss` (set to
  0.7.0).

### §39 Feature Commands to Register

`feature.verbosity_prefs`, `feature.quiet_mode_toggle`,
`feature.meeting_mode_toggle`, `feature.undo_quiet_hours`,
`feature.about_dialog`, `feature.validate_announcement`,
`feature.preview_announcement`, `feature.replay_profile_preview`,
`feature.qvp_install`, `feature.qvp_uninstall`,
`feature.announcement_history`, `feature.repeat_last_announcement`,
`feature.copy_last_announcement`, `feature.explain_last_announcement`,
`feature.verbosity_safe_mode`, `feature.verbosity_reset_selected`,
`feature.verbosity_import`, `feature.verbosity_export`,
`feature.feedback_too_much`, `feature.feedback_too_little`,
`feature.feedback_just_right`, `feature.preview_lab`.

### §40 Accessibility Requirements

The system must be screen-reader-first.

**General**: every dialog must have a useful initial focus; every
control must have an accessible name; every interactive element must
expose name, role, and value; every button must have a real text
label (no icon-only buttons); every action must have a keyboard path;
tab order must be logical; focus indicators must not be obscured;
color must not be the only signal; shape prefixes should accompany
validation states; no motion-only feedback; plain language should be
used throughout; visual badges are supplementary; spoken and braille
output are primary.

**Live regions/status**: nonblocking warnings are polite; blocking
errors are assertive; status line should be named and discoverable;
validation should be reviewable without sight.

**Screen reader commitments**: test with NVDA; test with JAWS;
verify wx.CollapsiblePane behavior; verify modal hotkeys; verify
ListBox Enter behavior; verify disabled Save announcement; verify
status bar updates; verify Announcement History workflow; verify
Quiet Mode recovery; verify Meeting Mode recovery.

### §41 Testing Plan

**Core tests** (`tests/unit/core/`):

`test_verbosity.py`, `test_verbosity_channels.py`,
`test_verbosity_profiles.py`, `test_verbosity_tokens.py`,
`test_verbosity_filters.py`, `test_verbosity_parser.py`,
`test_verbosity_data_order.py`, `test_verbosity_preview.py`,
`test_verbosity_storage.py`, `test_verbosity_qvp.py`,
`test_verbosity_library.py`, `test_verbosity_mastery.py`,
`test_verbosity_quiet.py`, `test_verbosity_meeting.py`,
`test_verbosity_history.py`, `test_verbosity_explain.py`,
`test_verbosity_safe_mode.py`, `test_verbosity_import_export.py`,
`test_verbosity_feedback_tuning.py`,
`test_verbosity_task_profiles.py`, `test_about_info.py`.

**UI tests** (`tests/unit/ui/`):

`test_verbosity_prefs.py`, `test_verbosity_token_editor.py`,
`test_verbosity_data_order.py`, `test_verbosity_chord_editor.py`,
`test_verbosity_library.py`, `test_verbosity_qvp_install.py`,
`test_keyboard_manager_verbosity.py`, `test_quiet_mode.py`,
`test_meeting_mode.py`, `test_verbosity_preview_lab.py`,
`test_verbosity_import_export.py`, `test_verbosity_safe_mode.py`,
`test_verbosity_history.py`, `test_about_info_dialog.py`.

**Script tests** (`tests/unit/scripts/`):

`test_build_windows_distribution.py` (extended for verbosity
artifacts).

### §48 Risks

The original risks section enumerates eight categories of risk that
must be managed as the system ships.

**Parser risk** - the template parser is the foundation of the
customization story. A flaky parser creates untrusted customization
and breaks the "safe to customize" guarantee. Mitigation: strict
allowlist of filters, type-checked tokens, golden tests, reject
invalid overrides on load with a nonblocking warning dialog.

**UI complexity risk** - the system has many surfaces (prefs, token
editor, data order, chord editor, library, preview lab, history,
explain, safe mode, import/export). Each surface must be
screen-reader-first and discoverable. Mitigation: small, focused
dialogs; keyboard-first navigation; initial-focus rules; no modal
overload.

**Sound annoyance risk** - sounds that are too loud, too frequent,
or triggered at the wrong moments will be turned off and never
re-enabled. Mitigation: per-event sound gating; per-profile sound
character; obvious way to silence globally; never use sound for
errors alone (visual + status + speech are also required).

**Silent failure risk** - a "QUILL didn't say anything" moment is
worse than a noisy moment. Mitigation: assertive live region for
blocking errors; status line always discoverable; "Repeat Last
Announcement" command; announcement history viewer.

**QVP trust risk** - community-contributed announcement packs could
ship unsafe wording, broken templates, or content that conflicts with
QUILL's tone. Mitigation: QVP files are JSON-only (no code);
strict schema validation; nonblocking warnings on install; easy
uninstall; safe reset to recover from broken packs.

**Module-size risk** - the verbosity subsystem is large and would
risk breaking the module-size budget on `main_frame.py` and other
hot files. Mitigation: dedicated `quill/core/verbosity/` package;
dedicated `quill/ui/verbosity/` package; rebaseline
`module_size_budgets.json` after integration; do not let the
verbosity subsystem touch `main_frame.py` more than is strictly
needed for menu wiring.

**Stash discipline risk** - the verbosity subsystem touches many
files; in-progress branches can accumulate cruft. Mitigation: small,
reviewable sub-PRs (one per §36 module group, tracked by #361-#366);
delete stash entries before opening new sub-PRs; keep `main` clean.

**Accessibility regression risk** - introducing the verbosity system
risks regressing existing screen-reader behavior if the routing
engine replaces a path that currently bypasses it. Mitigation:
golden announcement tests for the existing paths; per-verb override
defaults to "shipped behavior"; ship Quiet Mode and Meeting Mode
behind obvious controls; verify with NVDA and JAWS before declaring
done.

### §49 Non-Negotiables for 0.7.0

Do not cut:

1. Profile ladder.
2. Channel model.
3. Quiet Mode.
4. Meeting Mode.
5. Token parser.
6. Strict validation.
7. Simple and Advanced token editor.
8. Per-verb overrides.
9. Keyboard Manager integration.
10. Templates Library.
11. QVP JSON-only packs.
12. Announcement History.
13. "Why did QUILL say that?" (explain)
14. Safe Mode/reset.
15. Golden announcement tests.
16. Screen-reader-first accessibility commitments.

These define the system. Without them, the feature becomes a
preferences panel rather than a trusted announcement architecture.

### §50 Release Positioning

Suggested release framing:

> QUILL 0.7.0 introduces a complete screen-reader-first Verbosity
> System, giving users control over what QUILL says, where it says
> it, how much detail it provides, and how announcements can be
> reviewed, explained, customized, shared, and safely reset.

Suggested community framing:

> QUILL now meets you where you are. Whether you are learning,
> moving fast, working silently in a meeting, using braille,
> authoring documents, writing Markdown, reviewing code, or
> building your own community verbosity pack, QUILL gives you
> control over the communication layer of the editor.

Suggested accessibility framing:

> For screen reader users, verbosity is not decoration. It is the
> interface. QUILL 0.7.0 treats announcements as a first-class,
> testable, customizable, recoverable part of the product.

### §51 Success Criteria

QUILL 0.7.0 succeeds if:

- A beginner can choose Beginner mode and feel guided.
- A normal user can work without being overwhelmed.
- An expert can move quickly without routine chatter.
- A meeting participant can silence disruptive output.
- A braille user can keep meaningful output.
- A user can replay missed announcements.
- A user can ask why QUILL said something.
- A user can safely customize announcement wording.
- A user can install a community QVP pack.
- A user can recover from broken customization.
- A tester can verify announcement behavior with golden tests.
- A developer can add verbs without inventing a new announcement
  path.
- A Quillin author can register custom verbs safely.
- A support person can diagnose user reports from explanation
  traces.
- QUILL feels calm, intentional, trustworthy, and magical.

### §52 Final Statement

The QUILL 0.7.0 Verbosity System should be treated as a foundational
product pillar.

This is not simply about changing how much the editor talks. It is
about building a trustworthy communication architecture for a
screen-reader-first editor.

The complete system should include profiles, channels, quiet and
meeting modes, tokenized templates, validation, preview, per-verb and
per-chord overrides, QVP packs, announcement history, explanation
traces, safe reset, local tuning, mastery suggestions,
import/export, Preview Lab, and robust tests.

This is the kind of system that makes QUILL feel different from
ordinary editors.

It gives users power without fear.

It gives beginners guidance.

It gives experts speed.

It gives braille users control.

It gives the community a way to contribute.

It gives testers something reliable to verify.

Most importantly, it gives screen reader users confidence that QUILL
is communicating clearly, intentionally, and respectfully.

That is the magic of QUILL 0.7.0.

## Why this is being filed

The `docs/planning/verbosity.md` framing and scoping content is the
source-of-truth for the Verbosity System feature. The file is being
retired along with the rest of `docs/planning/`. This issue
preserves the design content not already captured by #361-#504 so
the verbosity implementation work that ships in a later release
still has a reference.

## Reference

- #361, #362, #363, #364, #365, #366 - Verbosity System sub-PRs
- #367-#404 - Verbosity section issues (from `verbosity.md` §5-§46)
- #405-#504 - Per-verb token scoping (100 items, from
  `docs/planning/screen reader first.md`)
- Original source: `docs/planning/verbosity.md` (now retired with
  the planning folder)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
