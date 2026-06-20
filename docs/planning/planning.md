# QUILL planning: open work and completed log

This is the active planning surface for QUILL. It tracks the prioritized open
roadmap, what is honestly in flight right now, and the running completed log.
Long-form historical planning documents (the master ROADMAP, the editor
competitive analysis, the GLOW / BITS Whisperer / Accessibility Agents
research) were consolidated into a previous version of this file and are
preserved in git history — see [Historical planning archive](#historical-planning-archive-pointer)
at the bottom.

**Target release:** QUILL 1.0. **Current version:** 0.7.0. **Last refreshed:** 2026-06-20.

## How to read this document

- **Open roadmap** is the prioritized, direction-of-the-team list of what's
  next. P0 is ship-blocking or user-harm-preventing; P1 is near-term flagship;
  P2 is post-1.0; P3 is hygiene/backlog.
- **In flight** lists the items that are actively being worked on right now,
  with their honest blockers when they cannot land in the current environment.
- **Completed log** is the running tally of what shipped since the 0.5.0 push,
  newest first. It is not exhaustive — git log is — but it captures the major
  milestones.
- **Feature: Braille Mode** is the long-form spec for the Braille feature,
  rolled in from `docs/braille.md` (which is now removed). Phase 1 (BRF Core)
  and Phase 5 (Translation Pack) shipped in 0.6.0; later phases remain a
  reference design for a future release.

Non-negotiable principle (per project policy): every shipped item must be
fully operable and pleasant with NVDA, JAWS, Narrator, and VoiceOver, by
keyboard alone, in high contrast, and at large font sizes.

---

## Current standing (QUILL 0.6.1 → 1.0)

**Version 0.6.1 ships 0.6.0 + Braille Mode Phase 2 (Page Intelligence).**
Notable releases since the prior planning snapshot:

- **AI Hub consolidation** — the `AI Model and Connection…`, `Forget API Key`,
  and `About BITS Whisperer` menu items were removed; AI Hub is the single
  multi-provider config surface (per-provider keys + default models +
  `test_chat`), and About QUILL folds in About BITS Whisperer.
- **GLOW is on by default** — `core.glow` is no longer `locked_off` (the prior
  0.5.0-era "hide GLOW until it ships" gate is gone). The engine is live;
  optional networked AI features (alt-text, PII redaction, language
  processing) stay off until the user gives explicit consent (GLOW-7).
- **Braille Mode 0.6.0** — Phase 1 (BRF Core: open, save, page map, status
  bar, navigation) and Phase 5 (UEB Translation Pack, opt-in install) shipped.
  Translation is liblouis-based and runs out-of-process.
- **Braille Mode 0.6.1** — Phase 2 (Page Intelligence + Detailed Status).
  `brf_page_detection.py` produces high/medium/low-confidence print-page
  indicators from separator lines and right-margin page numbers; Braille
  menu gains Go to Print Page, Next/Previous Print Page Change, Announce
  Running Head, and the Include/Omit Running Head toggles; detailed
  status now combines print page, continuation letter, running head,
  and confidence. See `Feature: Braille Mode` below.
- **Quillin Platform** — timer events, file-type contributions, snippet
  gallery, event dispatch; Node.js runtime for Quillins with a sandboxed
  worker.
- **Vision Prompt Library** and **AI Writing Toolkit** — image-style editor
  and revised custom instructions.
- **Power Tools feature parity** — the EdSharp F8 anchor model, the
  encoding conversion / minimum-encoding surfacing, Markdown profiles,
  non-AI table of contents, Quill Eraser (deterministic text hygiene
  checker), and Emmet-style abbreviation expansion.
- **Quillins bundled pack** — twelve bundled Quillins ship in the installer
  (`ai-writing-prompts`, `ai-writing-skills`, `brf-tools`, `doc-guardian`,
  `insert-character`, `insert-tools`, `journal-stamp`, `line-tools`,
  `markdown-helpers`, `math-equations`, `smart-insert`, `status-scribe`,
  `text-tools`, `word-count-node`).
- **Sound pack system (QSP)** — Ink earcons, partial packs, overlay
  architecture, and indent tones wired end-to-end.
- **Compare / CLI / accessibility wave** — Ken Perry issues #187–#194 closed
  (`6c061e5`); x3 accessibility wave added announce-gap enforcement
  (GATE-12), thread-daemon enforcement (GATE-15), and the `wx.MessageBox`
  bypassing guard (GATE-16) (`98ef440`).
- **Documentation consolidation** — down to seven root docs; engineering /
  accessibility subfolders retired (the surviving five references are kept
  as actively-wired docs); userguide absorbed developer-console,
  skills-tutorial, and features; QUILL-PRD absorbed engineering, qa,
  deployment, ACCESSIBLEAPPS_INTEGRATION, and the RTF design doc.
  CONTROL_REFERENCE is generated from `topics.json` by `build_docs.py`.
- **macOS port** — Keychain persistence for API keys; `macos_app.py` and
  `setup_macos.py` relocated to `quill/platform/macos/` and `scripts/`.
- **Org-1 closed** — full source-tree organizational review (platform
  relocations, root design docs consolidated, single ignored-output
  convention, repo-wide Markdown health, mechanical layout guard).

**Tier completion tracker (the source of truth for 1.0 / 2.0 scope)** — see
the [Tier completion table](#tier-completion-table) below. As of this
snapshot, Tier 1 (protections), Tier 2 (flagship, **almost complete**),
Tier 4 (structural health), and the EDS power-tool row are at zero
remaining in 1.0 scope; Tier 6 (documentation) is the only 1.0 tier with
substantial open work; BITS Whisperer, axe-core Accessibility Agents, the
GLOW watch action, and the packaging freezing spike are explicitly
deferred to QUILL 2.0.

---

## Feature: Braille Mode

This section was rolled in from `docs/braille.md` (now removed). The detailed
spec below is the source of truth for the Braille Mode data structures, status
bar design, screen-reader announcements, and the opt-in UEB Translation Pack.
**Aggressively trimmed**: the full phasing, dialog fields, validation warning
catalog, deployment script, and source-to-BRF workflow remain as a reference
for a future release; the shipped-in-0.6.0 status of Phases 1 and 5 is
noted at the top of each phase.

### Status

- **Phase 1 (BRF Core)** — **shipped in 0.6.0** (`8e265ee`, `db50e28`,
  `d861abb`, `aec4318`, `cdd480a`, `e0be9b9`). Open / save `.brf` and `.brl`;
  layout-preserving; form-feed and calculated pages; status bar;
  `braille_pack.py`, `braille_worker.py`, `braille_worker_client.py`; the
  Braille menu with Phase 1 commands.
- **Phase 2 (Page Intelligence + Detailed Status)** — **shipped in 0.6.1**
  (`#236`, `#237`). New `brf_page_detection.py` (BR-013) emits high-,
  medium-, and low-confidence print-page indicators from separator lines
  and right-margin page numbers; runs continuation-letter and running-head
  detection on the same source. The Braille menu gains Go to Print Page,
  Next / Previous Print Page Change, Announce Running Head, and the two
  Include / Omit Running Head toggles; detailed status now reads
  print page, continuation, running head, and confidence in the example
  string from the spec.
- **Phase 5 (UEB Translation Pack, opt-in)** — **shipped in 0.6.0**
  (`d861abb`, `8e265ee`). Liblouis runtime + UEB tables ship as an opt-in
  installer component; out-of-process translation worker; installable from
  `Braille → Install Braille Pack…`; Translation submenu appears when
  detected.
- **Phases 3, 4, 6** — **deferred to a future release**. Reference design
  preserved below; data structures, status bar design, and screen-reader
  announcement strings remain the source of truth when those phases land.

### Working title

QUILL Braille Mode.

### Product vision

QUILL Braille Mode provides a lightweight, screen-reader-first environment
for opening, editing, validating, navigating, translating, and tracking
progress in BRF files, with a focus on English UEB workflows.

This feature does not attempt to replace Duxbury, BrailleBlaster, or full
production transcription systems. QUILL is a fast, dependable, accessible
tool for blind users who need to work directly with BRF files, understand
where they are, track transcription or proofreading progress, and
optionally perform English UEB translation without bloating the editor.

### Primary audience

The primary audience is screen-reader users, especially:

- Blind transcriptionists
- Blind proofreaders
- Blind braille readers working with BRF files
- Blind developers or educators reviewing braille output
- Users who need to inspect or lightly edit BRF without launching a full
  transcription suite

Visual preview features stay minimal, optional, and never required for
the workflow.

### Core philosophy

QUILL should not visually imitate braille as its main purpose. QUILL
makes BRF files understandable, navigable, inspectable, and manageable
through speech, keyboard commands, status information, and structured
navigation. The experience should answer these questions instantly:

- What braille page am I on?
- What print page am I on, if known?
- What line and cell am I on?
- Am I on a continuation page?
- Is this page too long?
- Is this line too long?
- Where did I leave off?
- Which pages have I proofed?
- Which pages still need review?
- Is the file likely valid BRF?
- Can I translate or back-translate this section without installing a
  huge package?

### Scope summary

#### Included in QUILL core

- Open and save `.brf` and `.brl` (shipped)
- Preserve all spaces, line breaks, and form feeds (shipped)
- Detect BRF page breaks (shipped)
- Calculate braille page, line, and cell position (shipped)
- Status bar support (shipped)
- Screen-reader announcement commands (shipped)
- Go to braille page (shipped)
- Go to print page when detectable
- Insert page break (shipped)
- Validate BRF layout
- Detect page numbering conventions
- Track reading/proofing progress
- Save progress in a sidecar file
- Provide keyboard-first warnings and navigation

#### Optional Add-On (shipped in 0.6.0)

- Liblouis runtime
- English UEB Grade 1 table
- English UEB Grade 2 table
- Required table dependencies only
- Translation worker process (out-of-process)
- Plain text to UEB BRF
- BRF to draft print text
- Translate selection
- Back-translate current page
- Back-translate selection

### Deployment and packaging the Braille Pack (liblouis)

liblouis is a C library with optional Python bindings and a `lou_translate`
command-line tool. QUILL never imports liblouis in-process; the pack puts a
liblouis runtime plus the UEB tables somewhere the worker subprocess can
find them. The worker shells to `lou_translate` with a table name and the
text on stdin, so ctypes/binding packaging is avoided entirely.

#### What the pack contains

- The liblouis runtime for the platform (`liblouis.dll` on Windows) or the
  self-contained `lou_translate(.exe)` CLI. QUILL prefers the CLI because it
  removes all ctypes/binding packaging.
- The English UEB tables (`en-ueb-g1.ctb`, `en-ueb-g2.ctb`) and only their
  required dependency tables.
- A small `manifest.json` (pack version, table list, SHA-256 of each file)
  for `braille_pack_version()` and installer integrity verification.
- The third-party `LICENSE` files.

The pack installs into `<install-dir>/braille-pack/` (Windows) or the
platform data dir. `is_braille_pack_installed()` checks, in order:
`lou_translate` on `PATH`, the bundled `braille-pack/` location, then an
importable `louis` module — so any of the three delivery paths is detected
the same way.

#### Delivery options (shipped in 0.6.0)

1. **Optional Inno Setup component.** Ships as a selectable component in the
   Windows installer. Offline, deterministic, no hosting required, "just
   works" for users who opt in at install time.
2. **Download-on-demand from inside QUILL.** `install_braille_pack()` fetches
   a pinned, signed pack archive when the user explicitly chooses
   `Braille → Install Braille Pack…`. Keeps the base installer lean and lets
   a user who skipped the component add it later.
3. **System liblouis already on PATH.** Power users (and most Linux installs)
   can `apt install liblouis-bin` / `brew install liblouis`; detection finds
   it with no QUILL packaging at all.

QUILL ships options 1 and 2 together. The optional component is the primary,
offline path; download-on-demand is the fallback for users who skipped it.
Both resolve to the same detection logic, so the Translation submenu appears
whenever any path succeeded and stays hidden otherwise.

#### Inno Setup specifics

- `[Components]` entry: `Name: "braillepack"; Description: "Braille
  translation pack (liblouis + UEB tables)"; Types: full`. Unchecked in the
  default/compact install so the base installer stays small.
- `[Files]` tag `Components: braillepack` so the pack is only laid down
  when the component is selected, into `{app}\braille-pack\`.
- The build pipeline vendors a pinned liblouis Windows build + tables into
  the packaging tree and verifies each file's SHA-256 against `manifest.json`
  before Inno Setup runs. No build ever pulls "latest".

#### Download-on-demand constraints (security)

- Triggered only by the explicit `Install Braille Pack…` action — no
  auto-prompt, no auto-download, no silent network calls.
- Fetches a pinned URL (a specific QUILL release asset), verifies the
  archive's SHA-256 against an embedded expected hash, and verifies a release
  signature before unpacking.
- Registered in the network-egress audit (`_REVIEWED_EGRESS`); the egress
  gate passes because of this entry.
- Respects Safe Mode: like AI and the watch folder, the installer and the
  Translation submenu are hidden when `QUILL_SAFE_MODE=1`.

#### Licensing

liblouis is LGPL-2.1-or-later and the UEB tables carry their own (mostly
free) licenses. Because QUILL invokes liblouis out-of-process, the LGPL's
dynamic-linking obligations are not triggered for QUILL itself. The pack
still ships the upstream `LICENSE`/`COPYING` files and the build records
the exact upstream version so the corresponding source can be offered on
request.

### Supported braille variants for the shipped scope

- English only
- UEB Grade 1
- UEB Grade 2
- Braille ASCII BRF
- Optional Unicode braille conversion for internal processing or export

Nemeth, foreign-language tables, tactile graphics, PDF-to-BRF,
DOCX-to-BRF, and eBraille authoring are explicitly out of scope for the
shipped release.

### Important page concepts (reference for Phase 2)

The following concepts drive Phase 2 (Page Intelligence). Each concept is
something QUILL should understand and announce on demand.

1. **Physical BRF page break** — represented by a form feed. Treated as a
   structural page boundary. Commands: Next Braille Page, Previous Braille
   Page, Insert Braille Page Break, Delete Braille Page Break, Show Page
   Breaks as Text.
2. **Calculated braille page** — when no form feeds exist, QUILL calculates
   pages from the active profile. Default profile: 40 cells × 25 lines.
   Presets: 40 × 25, 39 × 25, 32 × 25, custom.
3. **Print page number** — detected by scanning line 1 of each braille page
   for likely print page numbers (`#a`, `#ab`, `,iv`, `a#c`, `b#c`, `#ab-#ad`).
4. **Page change indicator** — line of unspaced dots 3-6 ending with the
   new print page number (often a row of hyphens ending with a number).
5. **Lettered continuation print pages** — `#a` means print page 1, `a#a`
   means first continuation of print page 1, `b#a` means second
   continuation.
6. **Braille page number** — usually at the right margin on the last line
   of the braille page; detected separately from the print page number.
7. **Transcriber-generated pages** — braille page numbers prefixed with `t`
   (e.g. `t1`).
8. **Front matter braille pages** — prefixed with `p` (e.g. `p1`).
9. **Running head** — appears on the first line of many braille pages;
   must not be confused with body text or a page number.
10. **Combined print page numbers** — `#be-#bi`, `#dd-#de`, `,iv-,v`;
    detected as ranges.
11. **Implied or missing print page numbers** — never pretended to be
    certain unless present or user-confirmed.

### Status bar design (shipped)

The visual status bar stays short:

`BRF Pg 12/87 | Ln 14/25 | Cell 31/40 | Print 7 | 14%`

The screen reader announcement is richer:

- **Normal**: "Braille page 12 of 87. Line 14 of 25. Cell 31 of 40. Print
  page 7. Fourteen percent through file."
- **Detailed**: "Braille page 12 of 87. Line 14 of 25. Cell 31 of 40. Print
  page 7, continuation a. Running head: Chapter 2. Last proofed page: 9.
  Three pages marked needs review."
- **Brief**: "Page 12. Line 14. Cell 31."

### Status verbosity settings (Phase 2 reference)

- Braille status verbosity: Brief / Normal / Detailed
- Announce page changes automatically
- Announce print page changes automatically
- Announce line overflow while typing
- Announce cell position on demand only
- Include proofing status in announcement
- Include running head in announcement
- Include continuation page information

Default is conservative to avoid screen-reader spam.

### Required keyboard commands (Phase 1 shipped, Phase 2–4 reference)

#### Status commands

- Read Braille Status (shipped)
- Read Detailed Braille Status
- Read Current Line and Cell
- Read Current Braille Page
- Read Current Print Page
- Read Current Running Head
- Read Progress Summary

#### Navigation commands

- Go to Braille Page (shipped)
- Go to Print Page
- Next Braille Page (shipped)
- Previous Braille Page (shipped)
- Next Print Page
- Previous Print Page
- Next Page Change Indicator
- Previous Page Change Indicator
- Next Layout Warning
- Previous Layout Warning
- Go to Last Reading Position
- Go to Last Proofed Page

#### Editing commands

- Insert Braille Page Break (shipped)
- Remove Braille Page Break
- Insert Print Page Change Indicator
- Mark Current Line as Print Page Change
- Insert Braille Page Number
- Insert Running Head
- Normalize Line Endings
- Recalculate Page Map

#### Proofing commands

- Mark Current Braille Page as Proofed
- Mark Current Braille Page as Needs Review
- Clear Proofing Mark
- Add Proofing Note
- List Pages Needing Review
- List Proofed Pages
- Export Proofing Report

#### Translation commands (Phase 5 shipped, gated by pack install)

- Translate Plain Text to UEB Grade 1 BRF
- Translate Plain Text to UEB Grade 2 BRF
- Translate Selection to UEB
- Back-Translate BRF to Draft Text
- Back-Translate Current Page
- Back-Translate Selection
- Compare Back-Translation with Source

Back-translation is always labelled as draft output.

### Sidecar progress file

QUILL never modifies the BRF just to store workflow information. A
sidecar file is used: `filename.brf.quill.json` with `documentType`,
`profile`, `position`, `proofing`, `anchors`, and `notes`.

### Validation engine

The BRF validator is keyboard-navigable and useful through speech.
Warnings include: line exceeds selected cell width; page exceeds
selected line count; page has too few lines (possible missing content);
no form feeds found; mixed line endings; unexpected non-Braille-ASCII
character; possible print text in BRF; page change indicator on invalid
line; page change indicator missing page number; braille page number
missing / repeated / out of sequence; print page number out of sequence;
continuation page letter out of sequence; running head inconsistent;
trailing spaces warning (optional); unusual page size; Unicode braille
mistakenly named `.brf`.

Warnings are presented like "Warning 3 of 12. Braille page 14, line 26.
Page has 26 lines; expected 25. Press Enter to move to issue."

### Page map engine

For each page, store: start offset, end offset, physical page number,
calculated page number, detected braille page number, detected print page
number, continuation letter, running head, line count, maximum line
length, whether form feed ended the page, warnings, proofing status. This
gives QUILL instant navigation and status.

### Print page detection strategy

Confidence levels:

- **High**: page change indicator line ending with a valid page number;
  line 1 right-margin page number matching expected pattern; repeated
  print page number with continuation letters; user-confirmed anchor.
- **Medium**: right-aligned number on line 1; consistent sequence across
  several pages; combined page number pattern.
- **Low**: number near right margin but pattern is ambiguous; no running
  head detected; short page with multiple candidates.

Confidence is exposed in detailed status only.

### Transcriptionist progress workflow

Opening a BRF announces count of braille pages, print-page tracking
availability, and last position (if a sidecar exists). During work, the
status command speaks the current position. Marking progress
(`Mark Current Braille Page as Proofed`, `Mark as Needs Review`) announces
the change. `Read Progress Summary` reports totals, current page, proofed
count, needs-review count, last proofed page, current print page, and
estimated completion.

### File handling rules

- Never trim trailing spaces automatically.
- Never normalize line endings without permission.
- Never remove form feeds automatically.
- Never rewrite page numbers automatically without user action.
- Preserve original encoding when possible.
- Warn before saving if non-Braille-ASCII characters exist.
- Use a sidecar for QUILL metadata.
- Provide `Save As Clean BRF` as a deliberate command, not default
  behavior.

### Data structures

#### BRFPage

Fields: `index`, `startOffset`, `endOffset`, `lineStartOffsets`,
`lineCount`, `maxCellCount`, `hasFormFeed`, `detectedBraillePageNumber`,
`detectedPrintPageNumber`, `continuationLetter`, `runningHead`,
`pageChangeIndicators`, `warnings`, `proofingStatus`.

#### PageChangeIndicator

Fields: `offset`, `braillePage`, `line`, `detectedPrintPage`,
`confidence`.

#### ProofingStatus

Values: `none`, `proofed`, `needsReview`, `skipped`, `userNote`.

### Suggested internal modules (shipped where applicable)

- `quill/core/brf_document.py`
- `quill/core/brf_page_map.py`
- `quill/core/brf_ascii.py`
- `quill/core/brf_page_detection.py`
- `quill/core/brf_status.py`
- `quill/core/brf_validator.py`
- `quill/core/brf_progress.py`
- `quill/core/brf_sidecar.py`
- `quill/core/braille_commands.py`
- `quill/core/braille_pack.py` (shipped)
- `quill/core/braille_worker.py` (shipped)
- `quill/core/braille_worker_client.py` (shipped)

### Pragmatic shipping order (reference)

`Phase 1 → Phase 5 → Phase 2 → Phase 3 → Phase 4 → Phase 6`

- Phase 1 (BRF Core) — open/save, page map, status, navigation.
  Foundation for every later phase. **Shipped in 0.6.0.**
- Phase 5 (UEB Translation Pack, opt-in) — translation is the most
  independent phase. Needs Phase 1's open/save round-trip and
  `go_to_page`; does not need print-page detection or validation.
  **Shipped in 0.6.0.**
- Phase 2 (Page Intelligence) — print/braille page numbers, continuation
  letters, running heads, detailed status mode. The proofing counters
  in Phase 3 and the warning rules in Phase 4 both read Phase 2's
  detection signals, so this lands before them.
- Phase 3 (Proofing and Progress) — sidecar, last position, mark proofed
  / needs review, progress summary.
- Phase 4 (Validation) — BRF validation engine.
- Phase 6 (Source-to-BRF linking) — depends on everything above.

### Definition of done for the shipped scope (Phases 1 + 5)

A screen-reader user can:

- Open a BRF
- Hear page, line, and cell status
- Navigate by braille page
- Insert a page break
- Save without damaging the file
- Translate plain text to UEB Grade 1 or 2 (when pack installed)
- Back-translate BRF to draft text (when pack installed)

### Accessibility requirements

- All commands available from menus
- All commands assignable to keyboard shortcuts
- Focus remains in the editor after status commands
- Dialog fields have proper labels
- Warning lists are navigable with arrow keys
- Pressing Enter on a warning moves to the issue
- Escape closes dialogs without changing focus unexpectedly
- No screen-reader spam while typing
- Automatic announcements are configurable
- Manual status command always available
- Status text should be copyable
- Progress report opens as plain text

### Product principle

The best version of this feature is not flashy. The best version is the
one where a blind transcriptionist presses one command and immediately
knows: "I am on braille page 42, print page 18, continuation b, line
14, cell 31. This page is not yet proofed. There is one layout warning
on this page." That is the magic.

---

## Open roadmap (priority order)

The numbers are stable; gaps in the sequence are intentional (a closed
item leaves the slot empty rather than being renumbered).

### P0 — ship-blocking or user-harm-preventing

- **O1. Live installer smoke on Windows 10/11.** A one-time manual pass on
  a clean VM: install, Start-menu launch, Open-With + Send-to-Quill
  verbs, uninstall data prompt. The classic Explorer menu is code-
  complete and drift-proof (`test_committed_installer_iss_is_in_sync_with_generator`,
  SHELL-1/SHELL-3 core work delivered); this is the live-Windows release-
  time verification that has to be done by a human on a real install.

### P1 — near-term flagship

- **O5. Ask QUILL (Alt+Q) — per-message action buttons.** Keep the HTML
  WebView chat (the user likes it); add in-WebView per-message copy /
  insert / regenerate / delete controls. Limited by the external
  `wx_accessible-webview` component; today granularity is last-response
  vs whole transcript. Also: model dropdown populated from the provider
  instead of the free-text model field.
- **O5b. Unify the two AI stacks.** The chat dialog uses
  `quill.core.ai_chat` (PROVIDERS + credential_store) while the AI Hub /
  connection dialog uses `quill.core.assistant_ai` (providers.py +
  per-provider keys). Unify so keys / models / defaults are shared, not
  duplicated. Partially done — `test_chat`, per-provider key storage,
  and `set_active_provider` shipped in 0.6.0.
- **O6. AI Hub = a true Settings-style two-pane.** Today `AI Hub` opens a
  provider-dropdown config dialog. The richer design is left = every
  provider (Ollama local, Ollama Cloud, OpenAI, Claude, OpenRouter,
  Gemini, custom); right = that provider's config (host, API key,
  default model, a `List models` picker, `Test Chat`, `Make active`).
  Merge `AI Model and Connection` (on-device model tiers) as its own
  left-pane entry. Every provider's key / model persists independently.
- **O7. Azure provider — implement or formally drop.** The chat backend
  parses `azure` deltas (`quill/core/assistant_ai.py:1201`); Azure is
  not in `settings_specs.py` or the setup wizard. Either surface it in
  the AI Hub alongside the others, or remove the code path. Docs already
  accurate.
- **O8. AI-19 (GitHub Copilot SDK, deferred from 0.5.0).** Needs a live
  provider device-login endpoint that cannot ship from this environment;
  remain honestly blocked.
- **O9. SHELL-2 — structured-OCR AI structuring pass.** Code shipped
  (`_apply_ocr_structuring`, `structure` operation); the live-key end-to-
  end verification and structuring-quality tuning on real-world OCR
  output remain. Needs a configured/available assistant backend and
  tuning against multi-column PDFs, tables, headers/footers.

### P2 — post-1.0

- **O10. Quick Nav enhancements.** Live-count panel; table review;
  misspellings / search as nav types.
- **O11. Un-gate structured Word view + CSV grid** after validation.
- **O12. BITS Whisperer transcription runtime.** Three-tier providers
  (local / plus / enterprise), `quill/core/transcript.py` keystone,
  `bw_transcription.py` wrapper, IO JSON↔Markdown round-trip.
  Refs: BW-1, BW-9. Deferred from 1.0 by maintainer direction.
- **O13. Native RTF editing.** `core.rich_text_lens` is `locked_off`
  (always `"plain"`). RTF as a *format* is delivered as an io-layer
  round-trip. The rich-text lens is opt-in and read-only today
  (`RichTextSurface`); an editable rich surface with rich-native
  persistent undo remains open. Ref: RTF-22.
- **O14. Quillin Hub launch** (`hub.quillforall.org`) — public
  distribution and review surface.
- **O15. macOS port to shipping quality.** Ref: #42. Keychain
  persistence for API keys/tokens shipped (`38053a9`); the editor surface
  parity and live macOS smoke are the remaining work.
- **O16. Plugin capability, signing, and marketplace model.** A
  documented capability and signing model lets vetted third-party
  plugins load safely off the experimental flag (builds on SEC-8).
- **O17. Linux platform layer.** LINUX-1 (spike) and LINUX-2 (platform
  layer to product quality). Spike assesses an accessible Linux path.

### P3 — hygiene / backlog

- **O20. Extract `main_frame_statusbar.py`** to lower its budget below
  the rebaselined 540.
- **O21. Master backlog:** the per-tier backlog IDs listed in [Tier
  completion table](#tier-completion-table) below are the authoritative,
  tier-ordered list (AI-*, GLOW-*, BW-*, DLG-*, DOC-*, MENU-*, SET-*,
  etc.); this doc is the running narrative around them.

---

## In flight — honestly open

Items being actively worked on, with their exact blockers when they
cannot land in the current environment.

- **AI-19** — the GitHub Copilot SDK provider. Code-ready behind the
  consented AI provider layer; live device-login endpoint verification
  requires a sandboxed Copilot account and is not available in this
  environment. Stays honestly blocked until that endpoint is reachable.
- **SHELL-2** — the AI structuring pass for the structured-OCR verb.
  Worker wiring and prompt shipped; structuring *quality* on real-world
  OCR output (multi-column PDFs, tables, headers/footers) needs tuning
  against live model responses and an off-thread assistant call to
  confirm thread-safety and latency under the progress dialog. Needs a
  configured/available assistant backend.
- **SHELL-3** — the Windows 11 *primary*-menu `IExplorerCommand`
  sparse-package. The classic Explorer menu shipped; the modern-menu
  packaging is descoped to QUILL 2.0 (the OS gates it behind compiled
  COM + package identity). The macOS Finder verb (#115) stays blocked
  on the macOS port (#42, O15).
- **DLG-3.8** — the manual NVDA / JAWS / Narrator sign-off across
  `dialogs.md`. Owned by the maintainer, executed against
  `docs/qa/final-qa-test-plan.md` (§6 dialog estate pass). Needs a live
  Windows screen-reader runtime and human listening. Honest open until
  the pass is logged against a single named build.
- **CQ-11 (spell-check preload half)** — the tier-fallback half shipped
  in 0.5.0 (`test_spellcheck_backend.py`); the background-preload half
  stays open until a spell-check preload API exists (tracked by PERF-1).

---

## Completed log (running total since 0.5.0)

Newest first. This is the running tally of what shipped since the 0.5.0
push; git log is the authoritative source for individual commits.

### 2026-06-19: EdSharp port — heading / list chord pairs and section-move

- **`Ctrl+Alt+1..6` heading chords** — six new default-on chord pairs
  (`Ctrl+Alt+1` through `Ctrl+Alt+6`) that dispatch to
  `format.heading_1..6` and produce H1..H6 on the current line. The
  pre-existing QUILL-key chord `Ctrl+Shift+Grave, 1..6` is retired from
  the default keymap; users with a saved QUILL-key binding migrate
  silently via `legacy_rebindings` (`keymap.py:303-333`).
- **`Ctrl+Alt+7` / `Ctrl+Alt+8` list toggle** — `format.toggle_bullet_list`
  and `format.toggle_numbered_list` are new commands that insert on
  first press and strip on second press. `9` is intentionally absent;
  `Ctrl+K` already covers link insertion. Numbered-list auto-fill is
  gated by a three-way OR: the document is markdown, the user opted
  into `list_auto_fill_numbers` in `Settings → Editing → Lists`, or
  the user just toggled a numbered list on this document (per-document
  arming flag, five-minute TTL).
- **`Alt+Shift+Up` / `Alt+Shift+Down` section-move** — the existing
  `edit.expand_selection` / `edit.shrink_selection` chords are
  migrated to `Ctrl+Shift+Grave, E` and `Ctrl+Shift+Grave, Shift+E`;
  the freed chords become `format.move_section_up` /
  `format.move_section_down` and reorder the current heading section
  with the previous/next sibling. Section-move is enabled in
  **markdown and html** documents only; plain text is announced
  ("Section move is only available in Markdown or HTML documents")
  and the buffer is left untouched. Fence-aware — `# fake heading`
  inside a fenced code block is not promoted to a section.
- **§10.8 contract change** — `quill/tools/menu_lint.py` gains a
  renamed allowlist `_CTRL_ALT_DOCUMENTED` (frozenset of
  `(command_id, justification)` tuples) and an inline escape hatch:
  any `Ctrl+Alt+` binding line in `keymap.py` that ends with
  `# §edsharp-ok` is treated as documented even if not in the
  allowlist. The new allowlist includes the six `format.heading_*`
  ids, `format.insert_bullet_list`, `format.insert_numbered_list`,
  `view.send_to_tray`, and `view.toggle_tab_control`. Each entry
  carries a justification naming the screen-reader binding it
  overrides (e.g. "overrides NVDA switch-to-synth-N"). Tests:
  `test_ctrl_alt_edsharp_heading_permitted` (allowlist path) and
  `test_ctrl_alt_uncommented_still_fails` (regression check that
  the gate still fires for unlisted `Ctrl+Alt+` bindings).
- **Section status bar cell** — `STATUS_BAR_ITEMS` gains
  `section_heading` (hidden by default; users can flip it on in
  `Preferences → Status Bar`). When the caret is on a heading in a
  markdown or html document, the cell reads
  `Section: Heading 2 (3 of 7)`; when the caret is on a body line,
  the cell reports the parent section; for plain text or documents
  with no headings, the cell is empty. Wrapped in `try/except
  RuntimeError` to tolerate a dead editor widget.
- **Tests** — `tests/unit/ui/test_main_frame_section_move.py` (8
  cases), `tests/unit/ui/test_main_frame_list_toggle.py` (15 cases),
  `tests/unit/ui/test_main_frame_statusbar_context.py` (8 new cases),
  and `tests/unit/tools/test_menu_lint.py` (2 new cases). Property
  tests for `parse_heading_blocks` and `move_section` cover fence
  safety and round-trip up-then-down.
- **Docs** — `docs/keybinding-standard.md` (new) codifies the
  revised §10.8 contract: the eight currently documented
  `Ctrl+Alt+` bindings with justifications, the three legacy
  `Ctrl+Alt+` migrations to QUILL-key chords, the new section-move
  pair, and the process for adding a new `Ctrl+Alt+` binding.
  `CONTROL_REFERENCE.md` (and regenerated `.html` / `.epub`),
  `quill/core/help/topics.json`, the user guide, the PRD, the
  release notes for 0.7.0, and `CHANGELOG.md` all reflect the
  new chord pairs.

### 2026-06-18: Braille Mode 0.6.1 — Phase 2 (Page Intelligence + Detailed Status)

- **#236 / BR-013 — `brf_page_detection.py`** — pure detection routines
  for print-page changes, braille-page markers, continuation letters,
  and running heads. Confidence model: high (separator line,
  `---------#ab` style; or right-margin number that matches the
  previous page with a letter), medium (right-aligned line-1 number
  with no other anchor; consistent sequence across pages), low
  (ambiguous right margin; short page). 12 unit tests including the
  real-world 5-page corpus fixture at
  `tests/corpus/braille/one_crazy_night.brf`. Strict-typed; mypy clean.
- **#237 / BR-014 — Detailed status + print-page navigation** — 6 new
  commands in the Braille menu: `Go to Print Page…`, `Next Print Page
  Change`, `Previous Print Page Change`, `Announce Running Head`,
  `Include Running Head in Status`, `Omit Running Head from Status`.
  `read_detailed_braille_status` now composes the full example string
  from the spec — print page, continuation letter, running head,
  proofing state, confidence — pulling live data from the new
  detector. `read_current_print_page` no longer hard-codes "Print page
  unknown". 6 source-level wiring tests + 1 detailed-status assertion.

### 2026-06-18: Braille Mode 0.6.0

- **Phase 1 (BRF Core) shipped** — open/save `.brf` / `.brl`, layout-
  preserving, form-feed + calculated page detection, status bar, Braille
  menu, `Read Braille Status`, `Go to Braille Page`, `Next/Previous
  Braille Page`, `Insert Braille Page Break`, basic profile settings.
- **Phase 5 (UEB Translation Pack, opt-in) shipped** — liblouis runtime
  + UEB tables as an opt-in Inno Setup component; out-of-process
  translation worker (`braille_worker.py` / `braille_worker_client.py`);
  `Braille → Install Braille Pack…` installer; Translation submenu
  appears only when a pack is detected.
- **Settings (BR-008)** — braille profile, page-break mode, and sidecar
  fields wired through `settings_specs.py`.
- **Status strings (BR-009)** — `braille_status.py` builds the short
  status bar string and the three spoken-status variants (brief, normal,
  detailed).
- **BraillePositionResolver** — maps caret to `(page, line, cell)`.
- **Never trap the editor open** — fix to `BraillePositionResolver` so
  the resolver does not hold the editor open across a refresh.

### 2026-06-16: x3 accessibility wave (Ken Perry issues #187–#194; GATE-12/15/16)

- **QDC console** — `EVT_CHAR_HOOK` for Esc / F1 / Ctrl+L / Ctrl+Shift+C
  / Ctrl+S from any element; focus returns to editor on close; history
  Up / Down announces `History N of M`; TS worker start announces ready;
  clipboard copy announces result; TS console opens in TypeScript mode;
  TS host API calls marshaled via `wx.CallAfter` to satisfy the wx
  threading invariant.
- **AI chat (13 sites), Skill Library (9 sites), Prompt Library (5
  sites)** — status changes routed through `_set_status()` which calls
  `SetLabel + announce_cb` so every update is spoken.
- **Command Palette and Go-to-Anything** — result count and unavailable-
  command messages spoken.
- **GitHub browser** — status announced; Enter on repo field works;
  Backspace no longer hijacks; focus moves to first item after directory
  load; temp files use content-addressed slots.
- **SSH remote browser** — directory changes announced after each step.
- **Setup wizard** — each page announces `Step N of 9` and focuses page
  content, not the Next button.
- **All modal dialogs now through z-order gate** — setup wizard,
  devtools consent, GitHub dialogs.
- **Crash dialog** — `Win32 MessageBoxW` so Narrator / NVDA reads it
  even with no wx running.
- **TTS self-voicing** — daemon thread with queue; SR detection cached
  30-second TTL.
- **Safe Mode gates Developer Console** in addition to AI and Quillins.
- **`write_json_atomic`** fsyncs before `os.replace`; `safe_subprocess`
  passes `CREATE_NO_WINDOW`.
- **Redaction** covers GitHub PATs, OpenAI keys, AWS access keys, Slack
  tokens.
- **GitHub URL parser** uses `urllib.parse`; `get_identity()` moved off
  UI thread in all three entry points.
- **GATE-12** — `check_announce_gap.py` pre-commit gate: flags `SetLabel`
  without `announce`.
- **GATE-15** — flags `threading.Thread` without `daemon=True` in quill
  code.
- **GATE-16** — flags raw `wx.MessageBox` bypassing `_show_message_box`;
  existing sites marked `MSGBOX-OK`.
- Budget rebaseline for eight modules grown by accessibility wiring.

### 2026-06-15: Compare, CLI, accessibility fixes (`6c061e5`)

- **Compare documents** — side-by-side diff, navigate, announce.
- **CLI** — robust startup flags and `0.1.5` release updates.
- **Accessibility sweep** — `auto_side_preview`, z-order fixes, dialog
  z-order gate, per-provider model memory.

### 2026-06-15: Quill Eraser — deterministic text hygiene checker

- New `Quill Eraser` runs a deterministic pass over the document to
  normalize whitespace, strip zero-width / BOM / soft-hyphen characters,
  and surface a small hygiene report. No AI.

### 2026-06-15: Markdown profiles, table of contents, encoding (#256, #257)

- **Markdown profiles** — selectable flavour (CommonMark, GFM, Pandoc,
  kramdown, MultiMarkdown) applied on open and export.
- **Non-AI table of contents** — generates a TOC from headings without
  round-tripping through an LLM.
- **Minimum encoding** — surfaces a low-encoding-fallback path so legacy
  documents open without crashing.

### 2026-06-15: Power Tools + Emmet abbreviation expansion

- `cbde6a8` closed the remaining text-utility gaps; added Emmet-style
  abbreviation expansion.

### 2026-06-15: Sound pack system (QSP) and Ink earcons

- `cb12126` — QSP sound pack system, Ink earcons, partial packs, and
  overlay architecture. Indent tones wired end-to-end (`2c85508`).
- Quillin sound path hardened; `x.md` dropped.

### 2026-06-15: AI Writing Toolkit, Image Style editor, revised custom instructions

- `6b3373f` — AI Writing Toolkit; Image Style editor; revised custom
  instructions.

### 2026-06-15: macOS Keychain persistence for API keys (#160)

- `38053a9` — persist API keys and tokens via the login Keychain on
  macOS.

### 2026-06-15: AI Hub unified config; OpenRouter 401 fix; wizard key persistence

- `5eb80e7` — unify AI config in AI Hub; fix OpenRouter 401; wizard key
  persistence.

### 2026-06-15: Language profiles, token navigation, code-aware editing (#198)

- `503e25e` — language profiles, token navigation, code-aware editing.

### 2026-06-15: Close Other Documents command (Ctrl+Shift+F4)

- `976bd28` — `Close Other Documents` command with default
  `Ctrl+Shift+F4` binding.

### 2026-06-15: Math equations Quillin (LaTeX / MathML insertion)

- `0d982e8` — bundled `math-equations` Quillin for LaTeX / MathML
  insertion; `docs/math/` completed.

### 2026-06-15: Date and Time submenu consolidation

- `97994ce` — consolidated `Insert date/time` items into a `Date and
  Time` submenu.

### 2026-06-15: Abbreviation expansion hook

- `1f8add3` — backspace-after-expansion with delete / revert behavior.

### 2026-06-14: QUILL 0.6.0 — Vision Prompt Library, Quillin Prefs, Braille Mode in portable, JAWS fix

- `f72857b` — 0.6.0 release prep: Vision Prompt Library, Quillin
  Prefs, Braille Mode added to the portable build, JAWS announcement
  fix.

### 2026-06-14: QUILL 0.6.0 — Insert Automation, Quillin Platform, Braille Mode, Vision Prompt Library

- `8e265ee` — 0.6.0 release prep: Insert Automation, Quillin Platform
  (timer events, file-type contributions, snippet gallery, event
  dispatch), Braille Mode (the headline Phase 1 + Phase 5 above),
  Vision Prompt Library.

### 2026-06-14: Quillin Snippet Wizard, ruff hygiene

- `14208d9` — Snippet Wizard Quillin; all ruff check violations fixed.

### 2026-06-14: Quillins extension framework

- `0753a84` — complete, test, and document the Quillins extension
  framework. `4ad68bc` shipped the sample Quillin POC and fixed
  Security-CI gates.

### 2026-06-14: Tier C bundled Quillins platform (Wave 0)

- `a3addc6` — Tier C bundled Quillins platform (Wave 0).

### 2026-06-14: Quillins framework expansion

- `2dd0709` — expanded plugin framework and added three new bundled
  Quillins.

### 2026-06-14: Quillins Node.js runtime, QDC tutorial, installer Node.js component

- `54cef8c` — Node.js runtime for Quillins; QDC tutorial; installer
  Node.js component (`#158`).

### 2026-06-14: Phase 2/3 AI chat, Prompt Library, `.pqp`, Quillin Manager

- `b3ecdd8` — Phase 2/3 AI chat; Prompt Library; `.pqp` skill-quill-pack
  format; Quillin Manager.

### 2026-06-14: Skill Quill Pack (SQP) — multi-step AI workflows in plain Markdown

- `a5c4311` — SQP format and runtime: multi-step AI workflows stored
  as plain Markdown.

### 2026-06-14: Portable API key store with DPAPI file and env-var backends

- `d631737` — credential store with portable DPAPI file and env-var
  backends.

### 2026-06-13: Org-1 closed — source-tree reorganization and repo-wide Markdown health

The full source-tree organizational review landed as a sequence of
mechanical, behavior-preserving moves with every gate green:

- **Platform files relocated.** `macos_app.py` →
  `quill/platform/macos/macos_app.py`; `setup_macos.py` →
  `scripts/setup_macos.py`. `pyproject.toml` and `scripts/build_macos.sh`
  repathed.
- **Root design docs consolidated.** `aa`, `glow`, `pi`, and the project
  hub `ROADMAP` (`.md` plus regenerated `.html`/`.epub`) moved into
  `docs/planning/`. All 55 internal relative links in `ROADMAP.md` and
  every external reference were repointed.
- **Single ignored-output convention.** `build/`, `release-dist-*`,
  `installer-smoke*`, `windows-distribution`, and `release-artifacts*`
  consolidated into one ignored tree.
- **Repo-wide Markdown health.** A new root
  `.markdownlint-cli2.jsonc` plus a full cleanup brings every tracked
  `.md` to zero lint errors: MD040 fenced-code languages, MD049/MD050
  emphasis style, MD056 table-column counts, MD010 hard tabs, MD005/MD007
  list indentation, MD022/MD025/MD028/MD032 spacing, and MD012/MD047
  trailing-newline fixes.
- **Mechanical guard.** `tests/unit/structure/test_repo_layout.py`
  enforces the sanctioned layout (no loose root Python, the limited
  root-Markdown allowlist, the relocated planning-doc triples, the macOS
  file homes) so the tree cannot drift.

### 2026-06-12: Documentation consolidation round 3

- Down to seven root docs. `userguide.md` absorbed developer-console,
  skills-tutorial, and features; `QUILL-PRD.md` absorbed engineering,
  qa, deployment, ACCESSIBLEAPPS_INTEGRATION, and the RTF design doc.
  `CONTROL_REFERENCE.md` kept standalone (it is generated from
  `topics.json` by `build_docs.py` — part of the help system). All
  code/test/CI/site references updated; structure test updated;
  artifacts regenerated (7 md / 7 html / 7 epub, parity guard green).
- **AI Hub menu consolidation + About merge.** `AI Hub` now opens the
  full provider config dialog (provider/key/model, **Test Chat**,
  per-provider **Forget key**, **On-device model...**). Removed the
  `AI Model and Connection` and `Forget API Key` menu items; folded
  `About BITS Whisperer` into the single `About Quill` dialog and
  removed its two menu entries.
- **GLOW is on by default** (no longer `locked_off`). The engine ships
  in 0.6.0; optional networked features stay off until the user gives
  explicit consent (GLOW-7).
- **About dialog markdown tables.** `_render_markdown`
  (`browser_preview.py`) now renders GFM pipe tables as real `<table>`
  HTML, so the About dialog's dependency tables (and every Markdown
  preview) render correctly. 9 tests.
- **AI Hub config surface (core shipped).** `AssistantConnectionDialog`
  became a multi-provider config surface: **Test Chat** button (async),
  per-provider **Forget this provider's key** button, per-provider key
  + default-model load on provider switch, and `set_active_provider`
  on save.
- **F1 help on the document window.** The main editor got a friendly
  accessible name (`Document`), and F1 in the editor now routes to the
  `main.editor` help topic via a new `show_topic_help` mixin helper.
- **Session branches blank field.** The unlabeled, empty read-only
  field in the AI Writing Sessions dialog now has a visible
  `Branch details` label, a friendly accessible name, and helpful
  placeholder text.
- **Ask Quill (Alt+Q) core shipped.** Always-visible
  active-provider/model bar with a `Change provider or model` reveal;
  Insert-into-document footer (Last response / Entire transcript x
  Plain / Markdown / HTML). New core: `quill/core/ai/chat_export.py`
  (9 tests), per-provider key + default-model storage and `test_chat`
  in `assistant_ai.py`.
- **About dialog version.** The About body was hardcoded to `Quill
  0.1 Beta`; now uses `quill.__version__` (0.6.0) for the heading and
  prose.
- **`Regex` → `Regular Expressions`.** Renamed the Regular Expression
  Helper and the Count / Extract Regular Expression Matches commands
  (menu labels, dialog title, status messages, the
  `core.search.regex` feature name, and the bundled `text-tools`
  manifest/README); test updated.

### 2026-06-12: Send-to-Quill classic Explorer menu made drift-proof

- Single core verb registry (`quill/core/shell_verbs.py`) drives the
  runtime registry writer, the CLI `--action` flag, the Settings
  toggles, and the Inno Setup installer's `[Registry]` verb entries.
- New guard `test_committed_installer_iss_is_in_sync_with_generator`
  asserts the committed `installer/quill.iss` is byte-identical to the
  generator output. The shipped Explorer menu can never silently
  diverge from the single core verb registry.
- Twelve `test_build_windows_distribution` tests pass; sixteen
  `test_shell_verbs` + `test_shell_integration` tests pass; the
  committed installer is confirmed in sync with the generator at
  version 0.1.5.

### 2026-06-12: Keymap Editor dialog (issue #119) restored

- The Keymap Editor regressed: command list empty, OK button could not
  dismiss the dialog. Root cause was a parent-ownership mismatch in
  `open_keymap_editor`. Fix: every control is now parented directly to
  the dialog and laid out in a single sizer, matching the proven
  `_choose_searchable_option` pattern. New guard
  `tests/unit/ui/test_keymap_editor_contract.py` AST-asserts the
  controls are dialog-parented.

### 2026-06-12: DLG-3 and DLG-2 close (code complete); final-QA test plan written

- **Final-QA test plan** written at `docs/qa/final-qa-test-plan.md`
  (with paired `.html` / `.epub`) — the authoritative manual and
  exploratory plan for the 1.0 release.
- **DLG-3 closed (Done).** Every code-level phase (DLG-3.0–DLG-3.7 plus
  the DLG-3.T triage) is Done and machine-guarded. The one residual
  item — the manual NVDA / JAWS / Narrator pass — is not code; it is
  relocated, not fabricated.
- **DLG-2 closed (Done).** All interactive AI / assistant tool dialogs
  meet the modal/focus/async contract.
- **DLG-3.8 relocated to Tier 6** — manual SR pass is now a standalone
  Tier 6 final-QA item, owned by the maintainer and executed against
  the new test plan.
- `scripts/check_docs_artifacts.py` now recurses the whole `docs/**`
  tree.

### 2026-06-12: CQ-1 complete — main_frame decomposed into eight cohesive mixins

- Final two seams extracted. `SelectionMarksMixin` (line/paragraph/block
  selection, marks, ~223 lines) into `quill/ui/main_frame_selection.py`.
  `MenuBuilderMixin` (the full `_build_menu`, ~2,384 lines) into
  `quill/ui/main_frame_menu.py`. `main_frame.py` dropped from 21,637
  → 19,029 lines.
- All eight clusters now dedicated mixins (browse-mode, AI actions,
  status bar, image capture, QUILL key / Quick Nav, file / session
  lifecycle, selection / marks, menu construction).
- The full 352-test UI suite (green before and after), GATE-11,
  GATE-6 public-surface, the dialog-contract / inventory gates, and
  the A11Y-4 banned-pattern gate all pass.

### 2026-06-12: Tier 2 flagship closed to AI-19 + SHELL-2 + SHELL-3

- Three Tier 2 rows closed: SET-2 (dropped the no-op
  `dictation_sensitivity`), SET-3 (`announce_punctuation_level`
  applied engine-independently via
  `quill/core/punctuation_speech.py`), and AGENT-1 (renamed to
  `Accessibility Tune-Up`; structure + plain language auto-fix; alt-
  text + link-text advisory-only by design).
- `SET-3 (Done)`: `announce_punctuation_level` (none / some / most /
  all) drives engine-independent punctuation verbalization; QUILL
  substitutes spoken symbol names itself because the current TTS set
  never exposed a punctuation parameter.

### 2026-06-12: Native Windows OCR verified end to end (OCR-1 Done)

- `available_engines()` reports `['windows']` once `winsdk` is present;
  `ocr_image(path, engine="windows")` recognized a generated test image
  verbatim through the live WinRT engine — fully offline, no
  Tesseract. `winsdk` is declared in `pyproject.toml`'s `ocr` extra
  under `sys_platform == 'win32'`; the Windows build pipeline bundles
  the `ocr` group by default.

### 2026-06-12: A11Y-4 and GATE-11 closed Done; CQ-1 first seam extracted

- **A11Y-4 (Done, Tier 2):** dialog-construction contract is now
  machine-enforced.
- **GATE-11 (Done, Tier 4):** ratcheting module-size budget gate
  (`quill/tools/module_size_budget.py` + `module_size_budgets.json`,
  eight tests) caps every module at 600 lines unless it carries an
  explicit, acknowledged budget.
- **CQ-1 (In progress, Tier 4 — first seam):** the real decomposition
  began; the 25-method browse-mode navigation cluster (~455 lines)
  extracted into `quill/ui/main_frame_browse.py` as `BrowseModeMixin`.

### 2026-06-12: OCR capture sources completed (OCR-3 Done)

- **OCR-3 (Done, Tier 2):** clipboard-image and screen capture join
  file capture. `ocr_clipboard_image` and `ocr_screen_capture` use the
  wx-free `quill/platform/windows/screen_capture.py` helper and funnel
  through the same shared `_run_ocr_on_path` pipeline.

### 2026-06-12: Sharing dialogs completed (SHARE-1, SHARE-2 Done)

- **`gather_export_offers`** serializes all eight shareable sections
  (settings groups, features / profile, keymap, snippets, macros,
  watch profiles, personal dictionary, writing-style models).
- **`apply_import`** derives `merge` for a `.quillprofile` and
  `replace` for a `.quillbackup`. Personal dictionary stays additive
  in both modes.

### 2026-06-12: Settings tier closed out (SET-1, SET-4, SET-7 Done)

- **SET-1 (Done):** tabbed `wx.Notebook` Settings dialog renders one
  page per registry group from `settings_registry` specs.
- **SET-4 (Done):** the last unwired toggle, `browse_mode_sticky`, now
  makes the QUILL key **N** browse entry lock until Escape.
- **SET-7 (Done):** export to `.qsf`, import, and reset-to-factory all
  work.

### 2026-06-12: Trustworthy AI editing (AI-1, AI-6, AI-7, AI-14 Done)

- **AI-14 / AI-1:** `generate_assistant_response_stream` parses each
  provider's streaming wire format into token deltas via
  `parse_stream_event` + `iter_stream_text`. Ask Quill chat consumes
  the stream as throttled, accessible status announcements.
- **AI-6:** `quill/core/ai/availability.py` is the single source of
  truth for AI readiness; `describe_availability(...)` returns a
  clear, announceable message.
- **AI-7:** `quill/core/ai/diff_review.py` builds a navigable added /
  removed / changed diff; the `DiffReviewDialog` presents hunks as a
  stock `wx.CheckListBox`.

### 2026-06-12: Watch Profiles finished (WATCH-5, WATCH-6, WATCH-7 Done)

- **WATCH-5:** per-profile `name_patterns` (fnmatch globs) and a
  schedule (always, daily active window, midnight-wrapping quiet hours);
  the **Edit Watch Profile** dialog rebuilt to expose the full surface.
- **WATCH-6:** per-profile AI consent control shows the active
  provider/model and scope before arming; resource-cap termination
  announced distinctly.
- **WATCH-7:** `MainFrame` now supplies the real built-in action
  handlers — `_watch_convert_file`, `_watch_run_macro`,
  `_watch_run_ai`.

### 2026-06-12: EdSharp selection parity + QUILL key improvements (QK-6/7/8)

- Eight new selection commands implementing the EdSharp F8-based
  anchor model: `edit.start_selection` (F8), `edit.complete_selection`
  (Shift+F8), `edit.reselect` (Ctrl+Shift+F8),
  `edit.go_to_start_of_selection` (Alt+Shift+F8), `edit.copy_all`
  (Ctrl+F8), `edit.unselect_all` (Ctrl+Shift+A), `edit.say_selected`,
  `edit.read_all` (Alt+F8), `edit.toggle_extend_selection_mode`.

### 2026-06-12: SEC-2 / SEC-3 / SEC-4 / SEC-5 / SEC-15 / SEC-16 / CQ-14 / CQ-17 / CQ-19 / CQ-20 / CQ-22 closed

- **SEC-2:** shared `resolve_within` helper (`PathEscapeError`) in
  `quill/core/storage.py`; `write_json_atomic` gained an opt-in `base`
  parameter; the pure-core app-data JSON writers now pass
  `base=app_data_dir()`.
- **SEC-3:** OCR language codes validated against a strict allowlist.
- **SEC-4 / SEC-15:** `run_subprocess_safely` rejects an empty `args`
  sequence and a `cwd` that is not an existing directory; wraps
  launch `OSError` / `FileNotFoundError` into a clearly logged,
  re-raised `OSError` naming the tool.
- **SEC-5:** every HTTPS call goes through a single verified TLS
  context.
- **SEC-16:** `validate_credential_identifier` rejects empty, over-
  long, control-character, and leading-dash identifiers; wired into
  the Windows credential manager and the macOS keychain.
- **CQ-14:** path-safety tests in `storage.py` pass.
- **CQ-17:** `docs/engineering/thread-safety.md` captures cache-
  locking invariants.
- **CQ-19:** `_atomic_replace` retry loop (five attempts, 50 ms
  backoff) absorbs transient `PermissionError` on Windows.
- **CQ-20:** version pre-release ordering now intentional and tested;
  stages order final > rc > beta > alpha.
- **CQ-22:** `load_generic_credential` documents and debug-logs the
  two "no usable secret" outcomes.

### 2026-06-12: Tier 1 complete — full gate ladder enforced, tree gate-clean

- `pr-ci.yml` adds the required PR pipeline (GATE-2) with a lint job,
  a `unit-tests` job under a hard 70% core+io coverage floor
  (GATE-5, current 72.28%), and a `characterization` job (GATE-6).
- `security-ci.yml` adds a `security-checks` job (GATE-8) running the
  hardened-XML check and the TLS, redaction, XML-bomb, zip-cap,
  sandbox, and OCR-allowlist invariant suites. Accessibility CI now
  also runs the announcement-grammar conformance suite (GATE-7).
- Scoped strict-typing zone is genuinely clean: all 33 real type
  errors across `quill/core` and `quill/io` fixed; `mypy` reports zero
  errors across 96 source files.
- Banned-pattern gate is an AST checker; no-silent-network gate
  inventories every outbound call site.
- Two pre-existing test failures, unrelated but found along the way,
  were fixed: an autosave snapshot-collision bug, and four stale
  keymap tests.

### 2026-06-12: Tier 1 protections landed (latent-crash bugs, cheap security hardening, AI error taxonomy)

- All seven verified latent-crash bugs fixed with regression tests:
  BUG-1 (corrupted onboarding method), BUG-2 (four bare `wx.` heading-
  style calls), BUG-3 (`VoiceOption` annotations), BUG-4 (duplicate
  `URLError` import), BUG-5 (unchecked llama.cpp response shape),
  BUG-6 (DOCX / PPTX element name collision), BUG-7 (non-positive
  chunk-split guard).
- Cheap user-protecting security hardening in: SEC-10 (untrusted XML
  parses with entity expansion disabled), SEC-11 (ZIP-based formats
  enforce a cumulative decompression cap), SEC-13 (diagnostics
  redaction covers token, password, and NAME_KEY patterns), SEC-1
  (configured speech executable paths validated against an
  allowlist).
- Structured AI error taxonomy (auth 401, forbidden 403, rate-limited,
  warming-up, not-running, timeout, unreachable) matched on numeric
  status codes rather than substrings.

### 2026-06-12: Crash dialog buttons, find-in-files Cancel trap (#84), bookmark dialogs (#85)

- `#84`: `_prompt_file_search` added its `StdDialogButtonSizer` with
  `wx.EXPAND` (was `wx.ALIGN_RIGHT`); the identical bug in Status Bar
  Layout dialog was fixed in the same change.
- `#85`: `go_to_bookmark` forces a default selection and wires
  affirmative/escape ids; `_show_tree_navigator` (List Bookmarks)
  wires modal ids, focuses the tree via `CallAfter`, and guarantees
  `Destroy()` in a `finally`.

---

## Tier completion table

This is the source of truth for what is in the QUILL 1.0 scope and what
is deferred to QUILL 2.0. The 1.0 subtotal reaches zero remaining when
1.0 ships. Counts cover the IDs explicitly listed in each tier's prose.

| Tier | Area | Total | Done | Remaining | Open IDs |
| --- | --- | --- | --- | --- | --- |
| Tier 1 | Protect users and unlock the team | 23 | 23 | 0 | (complete) |
| Tier 2 | Flagship experience | 67 | 58 | 9 | AI-19, SHELL-2, SHELL-3, GLOW-1, GLOW-2, GLOW-3, GLOW-4, GLOW-5, GLOW-7 |
| Tier 4 | Structural health and performance | 32 | 32 | 0 | (complete) |
| Tier 6 | Documentation and learning surface | 35 | 3 | 32 | DLG-3.8, DOC-14..18, DOC-11, DOC-12, DOC-1..8, POD-1..5, TUT-1..7, CQ-11, CQ-14, CQ-23, CQ-24, LINUX-2 |
| **1.0 subtotal** | Tiers 1, 2, 4, 6 (the QUILL 1.0 scope) | **157** | **116** | **41** | |
| Tier 3 (2.0) | GLOW watch action — deferred to QUILL 2.0 | 1 | 0 | 1 | WATCH-8 |
| Tier 5 (2.0) | BITS Whisperer transcription — deferred to QUILL 2.0 | 28 | 0 | 28 | BW-1..10, WATCH-9, NAV-10, AI-11, AI-12, AI-18, FEAT-12..18, LINUX-1, ECO-1, L10N-1, COLLAB-1 |
| AX (2.0) | Accessibility Agents / axe-core engine — deferred to QUILL 2.0 | 6 | 0 | 6 | AX-A..F |
| PKG (2.0) | Packaging / freezing evaluation — deferred to QUILL 2.0 | 1 | 0 | 1 | PKG-1 |
| EDS | Power Tools feature parity — delivered in QUILL 1.0 | 21 | 21 | 0 | (complete) |
| **2.0 subtotal** | BITS Whisperer + axe-core + GLOW watch action | **57** | **21** | **36** | |
| **Total** | All tiers (1.0 + 2.0) | **213** | **135** | **78** | |

> Deferral note (2026-06-02): per maintainer direction, the GLOW
> accessibility engine (Tier 3, including WATCH-8), the BITS Whisperer
> transcription suite (Tier 5, including WATCH-9), and the
> Accessibility Agents / axe-core workstream (AX-A through AX-F) are all
> moved out of the 1.0 milestone and into **QUILL 2.0**.
>
> Scope move (2026-06-03): per maintainer direction, the GLOW
> accessibility engine family (GLOW-1 through GLOW-7) returns from QUILL
> 2.0 into the **1.0** milestone now that the shared `quill-glow-core`
> engine requirements are met (the engine is green). The seven items
> are classified under **Tier 2** and sequenced for execution after
> Tier 4. WATCH-8 and AX-A..F stay in 2.0.

---

## Historical planning archive (pointer)

Long-form historical planning documents were consolidated into a previous
version of `planning.md` on **2026-06-13** during the ORG-1 source-tree
reorganization. They are preserved in git history and can be retrieved
with `git show <commit>:docs/planning/planning.md`. They are not
maintained as live documentation; this file is the live planning
surface.

The five historical sources that were consolidated in were:

- **`ROADMAP.md`** — the master roadmap (Parts I–VI: the delight
  program, the verified bug and security and typing and performance
  fixes, the documentation greatness work, the quality-gate ladder, the
  AI and agent program, the combined GLOW and BITS Whisperer suite,
  the impact-ordered build sequence, and the State-of-the-union
  "what QUILL would be" assessment).
- **`aa.md`** — research proposal: integrating the Community Access
  Accessibility Agents project (`s:\code\agents`) into QUILL. Becomes
  the AX-A..F workstream, deferred to QUILL 2.0.
- **`pi.md`** — Power-user and Innovation ideas. Concept backlog for
  future investigations.
- **`glow.md`** — GLOW integration plan. Largely superseded by the
  shipped Tier 2 GLOW family (GLOW-1..7); retained for context on the
  consent / networked-feature design (GLOW-7).
- **`editors.md`** and **`editors2.md`** — competitive analysis of
  QUILL against general-purpose, programmer, and prose editors; feature
  matrix; gap analysis; menu consolidation; Ulysses / Obsidian /
  Scrivener-inspired redesign of Workspaces and the Document Navigator.
  Reference design for COMP-1..6 (the Notepad++-benchmark competitive
  parity plan, QUILL 2.0 scope).

The full text of all five sources as they existed immediately before
consolidation is recoverable from the ORG-1 commit (`git log --oneline
-- docs/planning/planning.md` lists the consolidation). The tier
completion table above is the only piece of the consolidated archive
that remains live in this document; everything else has been either
preserved as a reference design here (Braille Mode Phases 2/3/4/6) or
folded into the Open roadmap / In flight / Completed log sections.