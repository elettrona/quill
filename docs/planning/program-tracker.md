# QUILL Program Tracker — Path to Zero Open Issues

> **Living document.** This is the single source of truth for clearing the issue tracker by **shipping** (not archiving) every open issue except where a strong reason is recorded. Re-run `_gen_tracker.py` to refresh the snapshot; hand-edit the **Status** column as work lands and move rows to Shipped.


**Operating rules:** everything ships (2.0 deferral framing is dropped); track work as individual issues; execute in **buckets** via **small, low-risk commits**; update release notes + user guide + PRD + CHANGELOG with each landed bucket; **simplicity for the user is king**.


_Live status is the **By status** table below. The per-bucket / priority / rating tables are the original portfolio baseline snapshot (252 open) kept for proportions. Issue #617 is in scope (it now ships); Linux/Unix is out of scope._


## Status legend

- ✅ Shipped — merged on this branch, acceptance met.
- 🚧 In progress — actively being implemented.
- ⬜ Planned — not started.
- ❌ Out of scope — will not ship (reason recorded).

**Platform scope:** Windows (primary) and macOS (supported). **Linux/Unix is out of
scope and not a shipping target** — the Linux roadmap issues (#520, #565, #589) are
closed won't-do.


## Dashboard

### By status

| Status | Count |
| --- | ---: |
| ✅ Shipped | 16 (#648, #649, #643, #646, #238, #239, #240, #241, #242, #246, #251, #617, #361, #368, #374, #377) |
| 🚧 In progress | 4 (verbosity foundation partials: #367 §5, #369 §7, #375 §13, #376 §14 — core landed, UI/engine halves open) |
| 🧹 Resolved (bookkeeping) | 2 (#600, #601 — braille design captured in docs) |
| ❌ Out of scope | 3 (Linux/Unix — #520, #565, #589) |
| ⬜ Planned | 232 (incl. new #663 — Speech S5 offline voice commands) |
| **Total tracked** | **257** |

> **Wave 2 (Verbosity) started — core foundation shipped.** Sub-PR 1.1 (#361)
> landed the wx-free `quill/core/verbosity/` package (channels, tokens + 12
> filters, strict parser/validator, profiles + CustomProfile, the 34-verb §15
> catalog + registry, data-order model, JSON schemas); 102 tests, parser
> coverage 99%. This closes the fully-delivered spec sections §6 (#368), §12
> (#374), and §15 (#377); §5/§7/§13/§14 (#367/#369/#375/#376) are partially done
> (core in, UI/engine pending). Next: sub-PR 1.2 (engine, Quiet/Meeting, history,
> explain) — #362.

> **#246 completed via back-translation (source-to-BRF).** The deliverable is
> braille→text **back-translation**, now selection-aware (Braille > Translation >
> Back-Translate (draft) back-translates the selected passage, else the whole
> document) so a proofreader can recover the source text of one passage. The
> "compare back-translation with source" feature was **descoped** per maintainer
> decision, and per-page source linking (`listUnlinkedSourcePages`) remains out of
> scope (it needs a cross-format Source-Position model). #246 is closed as
> completed on the back-translation deliverable.

### By bucket (open)

| Bucket | Open | Risk | Impact | Value | Effort |
| --- | ---: | --- | --- | --- | --- |
| Verbosity System | 146 | Med | High | High | High |
| Docs & Content | 37 | Low | Med | Med | Med |
| AI & Agentic | 17 | Med | High | High | High |
| Speech & Dictation | 13 | Med | High | High | High |
| Navigation & Editor | 11 | Low | Med | Med | Med |
| Platform & Distribution | 10 | High | High | High | High |
| Braille Mode | 8 | Low | Med | High | Med |
| GLOW Family | 8 | Med | High | High | Med |
| Publishing & Export | 2 | Med | Med | Med | Med |
| **Total** | **252** | | | | |

### By priority label (open)

| Priority | Count |
| --- | ---: |
| P0 | 146 |
| P1 | 19 |
| P2 | 74 |
| P3 | 2 |
| — | 11 |

### By risk / impact / value / effort (open, bucket-level)

| Rating | Risk | Impact | Value | Effort |
| --- | ---: | ---: | ---: | ---: |
| High | 10 | 194 | 202 | 186 |
| Med | 186 | 58 | 50 | 66 |
| Low | 56 | 0 | 0 | 0 |

> Risk/impact/value/effort are **bucket-level baselines** for portfolio totals; per-issue overrides are noted inline as work is scoped. Methodology: Risk = chance a change destabilizes shipping behavior; Impact = breadth of users affected; Value = product/mission benefit; Effort = engineering size.


## Execution waves (lowest-hanging first)

1. **Wave 0 — done:** text round-trip + VoiceOver names (#648/#649/#643/#646). ✅
2. **Wave 1 — Speech S0 + complete Braille + DAISY export. ✅ Complete.** Speech S0 honesty fix ✅; Braille #238/#239/#240/#241/#242 ✅ and back-translation #246 ✅ — braille proofing, validation, and back-translation all ship; **DAISY 2.02 text-only export #251 ✅** (File > Export > DAISY Talking Book writes an `ncc.html` + `content.html` + `book.smil` folder readable on Victor Stream / Plextalk / APH players and in Book Wizard Producer).
3. **Wave 2 — Verbosity & Polish** (combined): the core (#271, #361–#366) and the §5–§46 spec (#367–#404) **plus** the addenda polish set (#405–#504) shipped together as one verbosity workstream — keep the high-value knobs, fold or fast-track the rest, close each as it lands. (Formerly split across Waves 2 and 8; merged because it is all one workstream with no cross-wave risk.)
4. **Wave 3 — Speech foundation S1–S2** (#617): provider registry, model manager, offline WAV transcription.
5. **Wave 4 — Captions & dictation** (#617 Speech S3).
6. **Wave 5 — AI & Agentic** (#507–#512, #523/#524) and the agentic-AI PRD.
7. **Wave 6 — Navigation/editor + GLOW + Publishing** (#513/#514/#521, #528–#534, #140 publishing). (DAISY #251 moved to Wave 1.)
8. **Wave 7 — Platform & Distribution** (#506, #516, #517, #518 macOS, #519) and Docs/Content (#505, #535–#564). **Linux/Unix excluded** (#520/#565/#589 are out of scope).


## Shipped

| # | Title | Status |
| ---: | --- | --- |
| 648 | Text round-trip: UTF-8 BOM no longer shows as a stray character | ✅ |
| 649 | Text round-trip: CRLF + blank-line runs preserved on save | ✅ |
| 643 | AI Hub notebook accessible name (VoiceOver) | ✅ |
| 646 | AI Hub tab group accessible name (VoiceOver) | ✅ |
| 617 | Speech **S0–S4** done and epic **closed as delivered**: dictation setting honest; offline STT foundation; whisper.cpp provider + offline transcription + model manager (HF-Hub); **transcript formats (plain/Markdown/HTML)** + **captions (SRT/VTT)**; **speaker attribution** (tinydiarize); **offline dictate-at-cursor** (QUILL Key+Shift+D, start/stop earcons, status bar); **mic selection**; whisper.cpp as a **distributable installer component** + **`sounddevice` bundled**; **optional Faster Whisper engine + Speech Engine chooser (S4)**. The one remaining capability, **S5 offline voice commands**, is split out to **#663**. | ✅ |
| 238 | Braille BR-015 — `brf_sidecar.py` foundation (atomic per-file sidecar: position, proofing, anchors, notes) | ✅ |
| 239 | Braille BR-016 — restore last position on open + spoken announcement (`brf_progress.py`) | ✅ |
| 240 | Braille BR-017 — Proofing submenu (8 commands, sidecar-backed; `brf_proofing.py` + `main_frame_braille_phase3.py`) | ✅ |
| 241 | Braille BR-018 — `brf_validator.py` layout validator (10 warning categories, read-only) | ✅ |
| 242 | Braille BR-019 — Validation submenu (4 commands) + Warnings List dialog | ✅ |
| 246 | Braille BR-023 — selection-aware back-translation (braille→text source recovery); compare + per-page linking descoped | ✅ |
| 251 | DAISY 2.02 text-only talking-book export (File > Export > DAISY Talking Book; wx-free `quill/io/daisy.py` writes ncc.html + content.html + book.smil) | ✅ |
| 617 | Offline speech-to-text S0–S4 (foundation, whisper.cpp + Faster Whisper, transcription, captions, dictation, model manager); closed as delivered, S5 voice commands split to #663 | ✅ |
| 361 | Verbosity Sub-PR 1.1 — core foundation (`quill/core/verbosity/`: channels, tokens + 12 filters, strict parser/validator, profiles + CustomProfile, 34-verb catalog + registry, data-order, schemas); 102 tests, parser cov 99% | ✅ |
| 368 | Verbosity §6 — Profile model (Beginner/Normal/Expert/Quiet + CustomProfile round-trip) | ✅ |
| 374 | Verbosity §12 — Token system (TokenSpec + the 12 engine filters; no custom filters) | ✅ |
| 377 | Verbosity §15 — Verb registry (VerbSpec + Severity + 34-verb catalog + VerbRegistry) | ✅ |

## Out of scope

| # | Title | Reason |
| ---: | --- | --- |
| 520 | O17 — Linux platform layer | Linux/Unix is not a shipping target (macOS yes, Linux no) |
| 565 | Tier-6 LINUX-2 | Linux/Unix out of scope |
| 589 | LINUX-1 spike | Linux/Unix out of scope |

## Open work by bucket


### Speech & Dictation  (13 issues · Risk Med · Impact High · Value High · Effort High)

| # | Priority | Status | Title |
| ---: | :---: | :---: | --- |
| 515 | P2 | ⬜ | [Planning] O12 — BITS Whisperer transcription runtime (deferred) |
| 567 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: BW-1 — BITS Whisperer BW-1 — deferred to QUILL 2.0 |
| 568 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: BW-2 — BITS Whisperer BW-2 — deferred to QUILL 2.0 |
| 569 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: BW-3 — BITS Whisperer BW-3 — deferred to QUILL 2.0 |
| 570 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: BW-4 — BITS Whisperer BW-4 — deferred to QUILL 2.0 |
| 571 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: BW-5 — BITS Whisperer BW-5 — deferred to QUILL 2.0 |
| 572 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: BW-6 — BITS Whisperer BW-6 — deferred to QUILL 2.0 |
| 573 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: BW-7 — BITS Whisperer BW-7 — deferred to QUILL 2.0 |
| 574 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: BW-8 — BITS Whisperer BW-8 — deferred to QUILL 2.0 |
| 575 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: BW-9 — BITS Whisperer BW-9 — deferred to QUILL 2.0 |
| 576 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: BW-10 — BITS Whisperer BW-10 — deferred to QUILL 2.0 |
| 577 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: WATCH-9 — BITS Whisperer WATCH-9 — deferred to QUILL 2.0 |
| 617 | — | ✅ | Offline Speech-to-Text Provider Architecture (S0–S4 shipped; closed as delivered) |
| 663 | — | ⬜ | Offline voice commands (Speech S5, split from #617) |

### Verbosity System  (146 issues · Risk Med · Impact High · Value High · Effort High)

| # | Priority | Status | Title |
| ---: | :---: | :---: | --- |
| 271 | P0 | ⬜ | [P0] Verbosity rebuild: implement per-verb token registry from docs/planning/verbosity.md |
| 361 | P0 | ✅ | [Verbosity] Sub-PR 1.1 — Core foundation: channels, profiles, tokens, parser (shipped: `quill/core/verbosity/`, 102 tests) |
| 362 | P0 | ⬜ | [Verbosity] Sub-PR 1.2 — Engine, quiet, meeting, mastery, history, explain, safe mode |
| 363 | P0 | ⬜ | [Verbosity] Sub-PR 1.3 — QVP, library, preview, schema validation |
| 364 | P0 | ⬜ | [Verbosity] Sub-PR 1.4 — UI: preferences, token editor, library, history, preview lab, about dialog |
| 365 | P0 | ⬜ | [Verbosity] Sub-PR 1.5 — Engine call-site migration, keymap, main_frame wiring |
| 366 | P0 | ⬜ | [Verbosity] Sub-PR 1.6 — Section 53 addendum (100-item UX polish) |
| 367 | P0 | 🚧 | Verbosity: §5 Locked design decisions (12 decisions) — core-testable decisions done (channels floor, profile ladder, default Normal); QVP/token-editor/library decisions pending UI |
| 368 | P0 | ✅ | Verbosity: §6 Profile model (Beginner / Normal / Expert / Quiet + CustomProfile) |
| 369 | P0 | 🚧 | Verbosity: §7 Channel system (Channel enum + routing) — enum + routing + floor shipped; per-channel prefs UI pending |
| 370 | P0 | ⬜ | Verbosity: §8 Sound design (master + per-event gating) |
| 371 | P0 | ⬜ | Verbosity: §9 Quiet Mode (controller + chords) |
| 372 | P0 | ⬜ | Verbosity: §10 Meeting Mode (controller + chords) |
| 373 | P0 | ⬜ | Verbosity: §11 Quiet Undo (Ctrl+Shift+Z) |
| 374 | P0 | ✅ | Verbosity: §12 Token system (TokenSpec + filters) |
| 375 | P0 | 🚧 | Verbosity: §13 Template validation (strict allowlist + type checking) — parser-side validation + spoken summary shipped; token-editor UI (Save-disabled, Ctrl+T/Ctrl+Shift+P) pending |
| 376 | P0 | 🚧 | Verbosity: §14 Data ordering model + editor — frozen DataOrder model shipped; editor UI + persistence pending |
| 377 | P0 | ✅ | Verbosity: §15 Verb registry (VerbSpec + initial verb catalog) |
| 378 | P0 | ⬜ | Verbosity: §16 Per-verb preferences UI |
| 379 | P0 | ⬜ | Verbosity: §17 Verbosity Preferences UI (top-level panel) |
| 380 | P0 | ⬜ | Verbosity: §18 Token editor UI (Simple + Advanced) |
| 381 | P0 | ⬜ | Verbosity: §19 Templates library (CRUD + cross-verb behavior) |
| 382 | P0 | ⬜ | Verbosity: §20 QVP file format (`.qvp.json` schema) |
| 383 | P0 | ⬜ | Verbosity: §21 QVP install flow (file picker + validate + announce) |
| 384 | P0 | ⬜ | Verbosity: §22 Profile preview on switch (replay last 3) |
| 385 | P0 | ⬜ | Verbosity: §23 Preview Lab (scenario-based renderer) |
| 386 | P0 | ⬜ | Verbosity: §24 Announcement history (record + replay + filter) |
| 387 | P0 | ⬜ | Verbosity: §25 Why did QUILL say that? (explanation trace) |
| 388 | P0 | ⬜ | Verbosity: §26 Too Much / Too Little / Just Right (feedback tuning) |
| 389 | P0 | ⬜ | Verbosity: §27 Mastery-based step down (per-verb threshold + 10-second timeout) |
| 390 | P0 | ⬜ | Verbosity: §28 Channel-specific templates (speech / braille / visual / sound_event) |
| 391 | P0 | ⬜ | Verbosity: §29 Safe Mode and Reset (per-verb / per-chord / profile / QVP) |
| 392 | P0 | ⬜ | Verbosity: §30 Import / Export (`.quill-verbosity-profile.json`) |
| 393 | P0 | ⬜ | Verbosity: §31 Task-aware profiles (Markdown / Code / Braille / Review / etc.) |
| 394 | P0 | ⬜ | Verbosity: §32 First-run Verbosity Tour (setup wizard page) |
| 395 | P0 | ⬜ | Verbosity: §33 Keyboard Manager integration (Verbosity tab) |
| 396 | P0 | ⬜ | Verbosity: §34 Hotkey plan (chords + conflict resolution) |
| 397 | P0 | ⬜ | Verbosity: §35 Storage (VerbositySettings + verbosity_custom.json) |
| 398 | P0 | ⬜ | Verbosity: §40 Accessibility requirements (screen-reader-first contract) |
| 399 | P0 | ⬜ | Verbosity: §41 Testing plan (core + UI + golden) |
| 400 | P0 | ⬜ | Verbosity: §42 Golden announcement tests (tests/golden/verbosity/) |
| 401 | P0 | ⬜ | Verbosity: §43 Documentation plan (PRD + userguide + CONTROL_REFERENCE + dev docs) |
| 402 | P0 | ⬜ | Verbosity: §44 Manual smoke test (golden path steps 1-65) |
| 403 | P0 | ⬜ | Verbosity: §45 Verification commands (gates that must be green) |
| 404 | P0 | ⬜ | Verbosity: §46 Order of work (46 steps; sub-PRs follow this) |
| 405 | P0 | ⬜ | Verbosity addendum #1: Settings Should Have Three Layers |
| 406 | P0 | ⬜ | Verbosity addendum #2: Searchable Settings |
| 407 | P0 | ⬜ | Verbosity addendum #3: Verbosity Recipes |
| 408 | P0 | ⬜ | Verbosity addendum #4: Announcement Budget |
| 409 | P0 | ⬜ | Verbosity addendum #5: Repetition Collapse |
| 410 | P0 | ⬜ | Verbosity addendum #6: Screen Reader Handoff Mode |
| 411 | P0 | ⬜ | Verbosity addendum #7: Typing Echo Controls |
| 412 | P0 | ⬜ | Verbosity addendum #8: Indentation and Whitespace Verbosity |
| 413 | P0 | ⬜ | Verbosity addendum #9: Selection Verbosity Knobs |
| 414 | P0 | ⬜ | Verbosity addendum #10: Clipboard Verbosity Knobs |
| 415 | P0 | ⬜ | Verbosity addendum #11: Search Result Verbosity Knobs |
| 416 | P0 | ⬜ | Verbosity addendum #12: Error Coaching |
| 417 | P0 | ⬜ | Verbosity addendum #13: “Details on Demand” |
| 418 | P0 | ⬜ | Verbosity addendum #14: Announcement Detail Levels Per Category |
| 419 | P0 | ⬜ | Verbosity addendum #15: Boundary Announcements |
| 420 | P0 | ⬜ | Verbosity addendum #16: Progress Announcement Controls |
| 421 | P0 | ⬜ | Verbosity addendum #17: Mode Change Announcements |
| 422 | P0 | ⬜ | Verbosity addendum #18: “Where Am I?” Command |
| 423 | P0 | ⬜ | Verbosity addendum #19: “What Changed?” Command |
| 424 | P0 | ⬜ | Verbosity addendum #20: “Speak Status Bar” Command |
| 425 | P0 | ⬜ | Verbosity addendum #21: Braille-Specific Knobs |
| 426 | P0 | ⬜ | Verbosity addendum #22: Punctuation and Symbol Profiles |
| 427 | P0 | ⬜ | Verbosity addendum #23: Markdown-Aware Verbosity |
| 428 | P0 | ⬜ | Verbosity addendum #24: Code-Aware Verbosity |
| 429 | P0 | ⬜ | Verbosity addendum #25: Compare/Diff Verbosity |
| 430 | P0 | ⬜ | Verbosity addendum #26: File Operation Verbosity |
| 431 | P0 | ⬜ | Verbosity addendum #27: Encoding and Line Ending Verbosity |
| 432 | P0 | ⬜ | Verbosity addendum #28: Notification Priority Levels |
| 433 | P0 | ⬜ | Verbosity addendum #29: Verbosity Rules Engine |
| 434 | P0 | ⬜ | Verbosity addendum #30: Per-Workspace Verbosity |
| 435 | P0 | ⬜ | Verbosity addendum #31: Per-File Verbosity |
| 436 | P0 | ⬜ | Verbosity addendum #32: Temporary Verbosity Boost |
| 437 | P0 | ⬜ | Verbosity addendum #33: Hold-to-Explain |
| 438 | P0 | ⬜ | Verbosity addendum #34: Training Mode |
| 439 | P0 | ⬜ | Verbosity addendum #35: Contextual Help Hooks |
| 440 | P0 | ⬜ | Verbosity addendum #36: Friendly Names for Technical Concepts |
| 441 | P0 | ⬜ | Verbosity addendum #37: “Confidence Check” Wizard |
| 442 | P0 | ⬜ | Verbosity addendum #38: Community Pack Preview and Diff |
| 443 | P0 | ⬜ | Verbosity addendum #39: QVP Trust Labels |
| 444 | P0 | ⬜ | Verbosity addendum #40: QVP “Copy as User Template” |
| 445 | P0 | ⬜ | Verbosity addendum #41: Verbosity Conflict Checker |
| 446 | P0 | ⬜ | Verbosity addendum #42: “Explain My Settings” |
| 447 | P0 | ⬜ | Verbosity addendum #43: Export Support Bundle |
| 448 | P0 | ⬜ | Verbosity addendum #44: Privacy Controls |
| 449 | P0 | ⬜ | Verbosity addendum #45: Private Document Mode |
| 450 | P0 | ⬜ | Verbosity addendum #46: Speech Rate and Pause Knobs |
| 451 | P0 | ⬜ | Verbosity addendum #47: Announcement Queue Policy |
| 452 | P0 | ⬜ | Verbosity addendum #48: “Last Important Announcement” |
| 453 | P0 | ⬜ | Verbosity addendum #49: Earcons With Text Equivalents |
| 454 | P0 | ⬜ | Verbosity addendum #50: Learn Sounds Mode |
| 455 | P0 | ⬜ | Verbosity addendum #51: Announcement Favorites |
| 456 | P0 | ⬜ | Verbosity addendum #52: “Pin This Status” |
| 457 | P0 | ⬜ | Verbosity addendum #53: Smart Status Rotation |
| 458 | P0 | ⬜ | Verbosity addendum #54: “Speak Current Template” |
| 459 | P0 | ⬜ | Verbosity addendum #55: Token Help on Demand |
| 460 | P0 | ⬜ | Verbosity addendum #56: Template Examples Per Token |
| 461 | P0 | ⬜ | Verbosity addendum #57: Pack Author Mode |
| 462 | P0 | ⬜ | Verbosity addendum #58: Built-In Sample QVPs |
| 463 | P0 | ⬜ | Verbosity addendum #59: “Make This My Default” |
| 464 | P0 | ⬜ | Verbosity addendum #60: Bulk Editing |
| 465 | P0 | ⬜ | Verbosity addendum #61: Undo for Settings Changes |
| 466 | P0 | ⬜ | Verbosity addendum #62: Settings Change History |
| 467 | P0 | ⬜ | Verbosity addendum #63: “Test My Current Settings” |
| 468 | P0 | ⬜ | Verbosity addendum #64: Recommended Settings Suggestions |
| 469 | P0 | ⬜ | Verbosity addendum #65: Accessibility Persona Setup |
| 470 | P0 | ⬜ | Verbosity addendum #66: Command Discovery Announcements |
| 471 | P0 | ⬜ | Verbosity addendum #67: “Do Not Say This Again” |
| 472 | P0 | ⬜ | Verbosity addendum #68: Per-Announcement Suppression |
| 473 | P0 | ⬜ | Verbosity addendum #69: Announcement Labels |
| 474 | P0 | ⬜ | Verbosity addendum #70: “What Will This Change?” Confirmation |
| 475 | P0 | ⬜ | Verbosity addendum #71: Better Defaults for Experts |
| 476 | P0 | ⬜ | Verbosity addendum #72: Better Defaults for Beginners |
| 477 | P0 | ⬜ | Verbosity addendum #73: Human-Friendly Names Everywhere |
| 478 | P0 | ⬜ | Verbosity addendum #74: “Copy Debug Summary” |
| 479 | P0 | ⬜ | Verbosity addendum #75: “Report This Announcement” |
| 480 | P0 | ⬜ | Verbosity addendum #76: Documentation From Settings |
| 481 | P0 | ⬜ | Verbosity addendum #77: Default Reset Granularity |
| 482 | P0 | ⬜ | Verbosity addendum #78: Settings Export Preview |
| 483 | P0 | ⬜ | Verbosity addendum #79: Import Conflict Wizard |
| 484 | P0 | ⬜ | Verbosity addendum #80: “Try Without Applying” |
| 485 | P0 | ⬜ | Verbosity addendum #81: Session Profiles |
| 486 | P0 | ⬜ | Verbosity addendum #82: Time-Based Quiet Hours |
| 487 | P0 | ⬜ | Verbosity addendum #83: Focus Mode |
| 488 | P0 | ⬜ | Verbosity addendum #84: Review Mode |
| 489 | P0 | ⬜ | Verbosity addendum #85: “Readability / Accessibility Verbosity” |
| 490 | P0 | ⬜ | Verbosity addendum #86: Microcopy Style Settings |
| 491 | P0 | ⬜ | Verbosity addendum #87: “Use My Words” Custom Labels |
| 492 | P0 | ⬜ | Verbosity addendum #88: Abbreviation Dictionary for Announcements |
| 493 | P0 | ⬜ | Verbosity addendum #89: Language and Localization Readiness |
| 494 | P0 | ⬜ | Verbosity addendum #90: Accessibility Testing Assistant Mode |
| 495 | P0 | ⬜ | Verbosity addendum #91: Developer “Trace Verbosity” |
| 496 | P0 | ⬜ | Verbosity addendum #92: Performance Knobs |
| 497 | P0 | ⬜ | Verbosity addendum #93: Status Badges |
| 498 | P0 | ⬜ | Verbosity addendum #94: Braille Status Cell |
| 499 | P0 | ⬜ | Verbosity addendum #95: “Command Echo” |
| 500 | P0 | ⬜ | Verbosity addendum #96: “Before and After” Announcements |
| 501 | P0 | ⬜ | Verbosity addendum #97: Destructive Action Warnings |
| 502 | P0 | ⬜ | Verbosity addendum #98: “Undo Available” Announcements |
| 503 | P0 | ⬜ | Verbosity addendum #99: Multi-Monitor / Presentation Safety |
| 504 | P0 | ⬜ | Verbosity addendum #100: Final Recommendation |
| 602 | — | ⬜ | [Planning Archive] Verbosity System framing, scoping, risks, and release framing - 0.7.0 |

### Braille Mode  (8 issues · Risk Low · Impact Med · Value High · Effort Med)

| # | Priority | Status | Title |
| ---: | :---: | :---: | --- |
| 238 | — | ✅ | [BR-015] brf_sidecar.py (Braille Mode P3) |
| 239 | — | ✅ | [BR-016] brf_progress.py: restore last position on open (Braille Mode P3) |
| 240 | — | ✅ | [BR-017] Braille > Proofing submenu (Braille Mode P3) |
| 241 | — | ✅ | [BR-018] brf_validator.py (Braille Mode P4) |
| 242 | — | ✅ | [BR-019] Validation commands + Warnings List dialog (Braille Mode P4) |
| 246 | — | ✅ | [BR-023] Source-to-BRF linking — back-translation (compare/linking descoped) |
| 600 | P1 | 🧹 | [Planning] Braille Mode Phases 3/4/6 — tracked by #238-#246 |
| 601 | — | 🧹 | [Planning Archive] Braille Mode design reference - Phases 3/4/6 deferred from 0.7.0 |

### AI & Agentic  (17 issues · Risk Med · Impact High · Value High · Effort High)

| # | Priority | Status | Title |
| ---: | :---: | :---: | --- |
| 507 | P1 | ⬜ | [Planning] O5 — Ask QUILL per-message action buttons |
| 508 | P1 | ⬜ | [Planning] O5b — Unify the two AI stacks |
| 509 | P1 | ⬜ | [Planning] O6 — AI Hub = Settings-style two-pane |
| 510 | P1 | ⬜ | [Planning] O7 — Azure provider: implement or formally drop |
| 511 | P1 | ⬜ | [Planning] O8 — AI-19 GitHub Copilot SDK (deferred) |
| 512 | P1 | ⬜ | [Planning] O9 — SHELL-2 structured-OCR AI structuring pass |
| 523 | P1 | ⬜ | [Planning] In flight: AI-19 GitHub Copilot SDK |
| 524 | P1 | ⬜ | [Planning] In flight: SHELL-2 OCR AI structuring |
| 579 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: AI-11 — AI AI-11 — deferred to QUILL 2.0 |
| 580 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: AI-12 — AI AI-12 — deferred to QUILL 2.0 |
| 581 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: AI-18 — AI AI-18 — deferred to QUILL 2.0 |
| 593 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: AX-A — Accessibility Agents AX-A — deferred to QUILL 2.0 |
| 594 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: AX-B — Accessibility Agents AX-B — deferred to QUILL 2.0 |
| 595 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: AX-C — Accessibility Agents AX-C — deferred to QUILL 2.0 |
| 596 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: AX-D — Accessibility Agents AX-D — deferred to QUILL 2.0 |
| 597 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: AX-E — Accessibility Agents AX-E — deferred to QUILL 2.0 |
| 598 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: AX-F — Accessibility Agents AX-F — deferred to QUILL 2.0 |

### Publishing & Export  (2 issues · Risk Med · Impact Med · Value Med · Effort Med)

| # | Priority | Status | Title |
| ---: | :---: | :---: | --- |
| 140 | — | ⬜ | Support Direct Publishing to WordPress and Other Publishing Platforms. |
| 251 | — | ✅ | Suggestion: Export to DAISY talking book |

### Platform & Distribution  (10 issues · Risk High · Impact High · Value High · Effort High)

| # | Priority | Status | Title |
| ---: | :---: | :---: | --- |
| 506 | P0 | ⬜ | [Planning] O1 — Live installer smoke on Windows 10/11 |
| 516 | P2 | ⬜ | [Planning] O13 — Native RTF editing |
| 517 | P2 | ⬜ | [Planning] O14 — Quillin Hub launch |
| 518 | P2 | ⬜ | [Planning] O15 — macOS port to shipping quality (#42) |
| 519 | P2 | ⬜ | [Planning] O16 — Plugin capability, signing, marketplace |
| 520 | P2 | ❌ | [Planning] O17 — Linux platform layer |
| 525 | P1 | ⬜ | [Planning] In flight: SHELL-3 Windows 11 primary menu |
| 565 | P2 | ❌ | [Planning] Tier 6 / 1.0 backlog: LINUX-2 |
| 589 | P2 | ❌ | [Planning] QUILL 2.0 deferred: LINUX-1 — LINUX-1 spike — deferred to QUILL 2.0 |
| 599 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: PKG-1 — Packaging freezing evaluation PKG-1 — deferred to QUILL 2.0 |

### Navigation & Editor  (11 issues · Risk Low · Impact Med · Value Med · Effort Med)

| # | Priority | Status | Title |
| ---: | :---: | :---: | --- |
| 513 | P2 | ⬜ | [Planning] O10 — Quick Nav enhancements |
| 514 | P2 | ⬜ | [Planning] O11 — Un-gate structured Word view + CSV grid |
| 521 | P3 | ⬜ | [Planning] O20 — Extract main_frame_statusbar.py |
| 578 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: NAV-10 — Navigation NAV-10 — deferred to QUILL 2.0 |
| 582 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: FEAT-12 — Feature FEAT-12 — deferred to QUILL 2.0 |
| 583 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: FEAT-13 — Feature FEAT-13 — deferred to QUILL 2.0 |
| 584 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: FEAT-14 — Feature FEAT-14 — deferred to QUILL 2.0 |
| 585 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: FEAT-15 — Feature FEAT-15 — deferred to QUILL 2.0 |
| 586 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: FEAT-16 — Feature FEAT-16 — deferred to QUILL 2.0 |
| 587 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: FEAT-17 — Feature FEAT-17 — deferred to QUILL 2.0 |
| 588 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: FEAT-18 — Feature FEAT-18 — deferred to QUILL 2.0 |

### GLOW Family  (8 issues · Risk Med · Impact High · Value High · Effort Med)

| # | Priority | Status | Title |
| ---: | :---: | :---: | --- |
| 528 | P1 | ⬜ | [Planning] Tier 2 / 1.0 GLOW family: GLOW-1 |
| 529 | P1 | ⬜ | [Planning] Tier 2 / 1.0 GLOW family: GLOW-2 |
| 530 | P1 | ⬜ | [Planning] Tier 2 / 1.0 GLOW family: GLOW-3 |
| 531 | P1 | ⬜ | [Planning] Tier 2 / 1.0 GLOW family: GLOW-4 |
| 532 | P1 | ⬜ | [Planning] Tier 2 / 1.0 GLOW family: GLOW-5 |
| 533 | P1 | ⬜ | [Planning] Tier 2 / 1.0 GLOW family: GLOW-6 |
| 534 | P1 | ⬜ | [Planning] Tier 2 / 1.0 GLOW family: GLOW-7 |
| 566 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: WATCH-8 — GLOW watch action — deferred to QUILL 2.0 |

### Docs & Content  (37 issues · Risk Low · Impact Med · Value Med · Effort Med)

| # | Priority | Status | Title |
| ---: | :---: | :---: | --- |
| 505 | P2 | ⬜ | [Planning] QUILL 1.0 + 2.0 open roadmap (planning.md) |
| 522 | P3 | ⬜ | [Planning] O21 — Master backlog (per-tier backlog IDs) |
| 526 | P1 | ⬜ | [Planning] In flight: DLG-3.8 NVDA / JAWS / Narrator sign-off |
| 527 | P1 | ⬜ | [Planning] In flight: CQ-11 spell-check preload half |
| 535 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-1 |
| 536 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-2 |
| 537 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-3 |
| 538 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-4 |
| 539 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-5 |
| 540 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-6 |
| 541 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-7 |
| 542 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-8 |
| 543 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-11 |
| 544 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-12 |
| 545 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-14 |
| 546 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-15 |
| 547 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-16 |
| 548 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-17 |
| 549 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: DOC-18 |
| 550 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: POD-1 |
| 551 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: POD-2 |
| 552 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: POD-3 |
| 553 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: POD-4 |
| 554 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: POD-5 |
| 555 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: TUT-1 |
| 556 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: TUT-2 |
| 557 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: TUT-3 |
| 558 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: TUT-4 |
| 559 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: TUT-5 |
| 560 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: TUT-6 |
| 561 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: TUT-7 |
| 562 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: CQ-14 |
| 563 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: CQ-23 |
| 564 | P2 | ⬜ | [Planning] Tier 6 / 1.0 backlog: CQ-24 |
| 590 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: ECO-1 — Ecosystem ECO-1 — deferred to QUILL 2.0 |
| 591 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: L10N-1 — Localization L10N-1 — deferred to QUILL 2.0 |
| 592 | P2 | ⬜ | [Planning] QUILL 2.0 deferred: COLLAB-1 — Collaboration COLLAB-1 — deferred to QUILL 2.0 |
