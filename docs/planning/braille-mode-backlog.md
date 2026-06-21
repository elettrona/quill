# QUILL Braille Mode — Phases 3/4/6 Backlog Archive

> **Consolidated workstream design spec.** This file gathers the full text of
> every open issue in this workstream so the design reads end to end in one
> place. The issues remain **open and individually tracked** in
> [`program-tracker.md`](program-tracker.md); each closes as its
> implementation ships. Everything here is in scope to ship — issue numbers
> are preserved as section anchors.

Braille Mode phases beyond the shipped core: sidecar metadata, last-position restore, the Proofing submenu, the validator and Warnings List, and source-to-BRF linking. These deliver real value to the braille-transcription audience and are strong candidates for the next feature wave.


## Triage summary (product judgment)

- **Best near-term value:** brf_progress.py restore-last-position (#239) and the Proofing submenu (#240) are self-contained and high-impact.
- **Next:** brf_validator.py (#241) + validation commands / Warnings List (#242), then brf_sidecar.py (#238).
- **Later (v1.1):** source-to-BRF linking (#246). #600/#601 are the tracking + design-reference for this family.


## Contents (8 archived issues)

- [#238](#238-) — [BR-015] brf_sidecar.py (Braille Mode P3)
- [#239](#239-) — [BR-016] brf_progress.py: restore last position on open (Braille Mode P3)
- [#240](#240-) — [BR-017] Braille > Proofing submenu (Braille Mode P3)
- [#241](#241-) — [BR-018] brf_validator.py (Braille Mode P4)
- [#242](#242-) — [BR-019] Validation commands + Warnings List dialog (Braille Mode P4)
- [#246](#246-) — [BR-023] Source-to-BRF linking (Braille Mode P6, v1.1)
- [#600](#600-) — [Planning] Braille Mode Phases 3/4/6 — tracked by #238-#246
- [#601](#601-) — [Planning Archive] Braille Mode design reference - Phases 3/4/6 deferred from 0.7.0



---

## #238 — [BR-015] brf_sidecar.py (Braille Mode P3)

**Labels:** enhancement

[P3] Create `quill/core/brf_sidecar.py`:

- Sidecar path: `<brf_path>.quill.json` (e.g. `notes.brf.quill.json`).
- Schema-validated atomic write via `quill.core.storage.write_json_atomic` (the existing helper that uses temp-file + `os.replace`).
- Schema in `quill/core/schemas/brf_sidecar.json` (or as a Python dataclass with manual validation; match the existing pattern for similar sidecar data).
- Public functions:
  - `read_sidecar(brf_path: Path) -> BRFSidecar | None` — returns `None` if no sidecar exists.
  - `write_sidecar(brf_path: Path, sidecar: BRFSidecar) -> None` — atomic.
  - `clear_sidecar(brf_path: Path) -> None` — removes the sidecar file if present (for tests).
- `BRFSidecar` fields: `document_type` ("brf"), `profile` (subset of settings), `position` (last offset / page / line / cell / print page), `proofing` (last proofed page, pages needing review, proofed pages list), `anchors` (list of user-confirmed anchors with confidence), `notes` (list of per-page notes).

**Tests (`tests/unit/core/test_brf_sidecar.py`):**
- Round-trip: write a sidecar, read it back, deep-equal.
- Atomic: an interrupted write (e.g. SIGKILL simulation by patching `os.replace` to raise) leaves the previous file intact.
- Schema validation: a malformed sidecar raises a clear error.
- `read_sidecar` returns `None` for a missing file.

**Parent plan:** `docs/braille.md` (Phase 3, Proofing and Progress). Tracked in session todos as `br-sidecar`. Depends on #231 (BR-008).



---

## #239 — [BR-016] brf_progress.py: restore last position on open (Braille Mode P3)

**Labels:** enhancement

[P3] In the main_frame open flow, when a `.brf` (or related suffix) is opened and a sidecar exists, restore the last offset and announce the position:

- On open success, call `brf_sidecar.read_sidecar(path)` (BR-015). If `sidecar is not None` and `profile.braille_save_sidecar` is True, set the caret to `sidecar.position.last_offset`.
- On restore, announce: `"BRF file opened. 87 braille pages detected. Print page tracking available. Last position: braille page 12, line 14, cell 31."` (or the no-sidecar / no-print-tracking variants per the spec).
- Never modify the BRF.
- Skip sidecar restore in `QUILL_SAFE_MODE=1`.
- Page map and detection results are recomputed on every open (no caching of the page map across sessions for v1.0).

**Implementation lives in the main_frame open handler and `quill/core/brf_progress.py` (new module exposing `restore_position(document, sidecar) -> int | None`).**

**Tests:**
- `tests/unit/core/test_brf_progress.py`: `restore_position` returns the last offset from the sidecar; returns `None` for a missing sidecar.
- A source-contract test in `tests/unit/ui/test_main_frame_open.py` (or equivalent) asserts the open flow calls `restore_position` and routes the result through `_announce`.
- A safe-mode test (`QUILL_SAFE_MODE=1`) asserts restore is skipped.

**Parent plan:** `docs/braille.md` (Phase 3, Proofing and Progress). Tracked in session todos as `br-restore-position`. Depends on #238 (BR-015) and #233 (BR-010).



---

## #240 — [BR-017] Braille > Proofing submenu (Braille Mode P3)

**Labels:** enhancement

[P3] Add the Phase 3 proofing commands to the registry and the Braille > Proofing submenu.

**Commands:**
- `quill.markPageProofed` — Mark Current Braille Page as Proofed. Updates sidecar `proofing.proofed_pages` and `proofing.last_proofed_braille_page`. Announces `"Braille page 12 marked proofed."`
- `quill.markPageNeedsReview` — Mark Current Braille Page as Needs Review. Updates `proofing.pages_needing_review`. Announces `"Braille page 12 marked needs review."`
- `quill.clearProofingMark` — Clear Proofing Mark on the current page.
- `quill.addProofingNote` — Add Proofing Note (prompts for a free-form note via `wx.TextEntryDialog`, attaches it to the current page in `notes`).
- `quill.readProofingProgress` — Read Progress Summary. Announces `"Progress summary. 87 braille pages. Current page 12. 9 pages proofed. 3 pages need review. Last proofed page 9. Current print page 7. Estimated completion 10 percent."` (or whatever the sidecar yields).
- `quill.listProofedPages` — List Proofed Pages (opens a `wx.ListBox` dialog).
- `quill.listPagesNeedingReview` — List Pages Needing Review (same pattern).
- `quill.exportProofingReport` — Export Proofing Report (opens `wx.FileDialog` with `.txt` default; writes a plain-text report).

All writes are atomic via `brf_sidecar.write_sidecar` (BR-015). Dialogs follow the A11Y-4 contract (label-then-control via lambda factory, `apply_modal_ids`, deterministic focus).

**Tests:**
- `tests/unit/ui/test_main_frame_menu_contract.py` (or new `test_braille_proofing_menu.py`): Braille > Proofing submenu contains all 8 items.
- `tests/unit/core/test_brf_sidecar.py`: mark-proofed updates the sidecar and round-trips.
- `tests/unit/ui/test_dialog_inventory.py` (and A11Y-4 banned-pattern gate): every new `wx.Dialog` and `show_web_form` is registered via `python -m quill.tools.dialog_inventory --write`; the snapshot is staged in the same change.

**Parent plan:** `docs/braille.md` (Phase 3, Proofing and Progress). Tracked in session todos as `br-proof-commands`. Depends on #238 (BR-015).



---

## #241 — [BR-018] brf_validator.py (Braille Mode P4)

**Labels:** enhancement

[P4] Build `quill/core/brf_validator.py` — pure validation routines that produce a list of `BRFWarning` records.

**Warning categories (per `docs/braille.md`):**
- Line too long (configurable, default 40 cells)
- Page too long (configurable, default 25 lines per page)
- Page too short (configurable, default 5 lines per page; signals a stuck page)
- Missing form feeds (where `use_form_feeds=True` and the file has no form feeds but is long)
- Mixed line endings (CRLF + LF in the same file)
- Non-BRF-ASCII (any byte > 0x7F, or U+2800..U+28FF when not in NABCC mode)
- Page-change-indicator problems (e.g. inconsistent format, missing page number)
- Braille / print page numbering issues (sequence gaps, duplicates)
- Running-head consistency (varying running heads across pages where they should match)
- Unicode-braille-as-BRF (file is in U+2800..U+28FF rather than NABCC)

Each `BRFWarning` has `offset`, `line`, `page`, `kind` (one of the categories above), `message` (screen-reader-friendly), `severity` ("info" | "warning" | "error").

**Tests (`tests/unit/core/test_brf_validator.py`):**
- All 10 categories fire on a hand-built fixture.
- Mixed line endings are detected but not auto-corrected (validator is read-only).
- The test corpus `tests/corpus/braille/one_crazy_night.brf` is used as a known-good baseline (no warnings) and a deliberately-broken derivative (missing form feeds, mixed endings) as the warning smoke test.

**Parent plan:** `docs/braille.md` (Phase 4, Validation). Tracked in session todos as `br-validator`. Depends on #236 (BR-013).



---

## #242 — [BR-019] Validation commands + Warnings List dialog (Braille Mode P4)

**Labels:** enhancement

[P4] Wire the BRF validator into a new Braille > Validation submenu with navigable commands.

**Commands:**
- `quill.validateBrailleFile` — Validate BRF Layout (runs the validator (BR-018) and opens the Warnings List dialog).
- `quill.nextValidationWarning` — Next Warning (jumps caret to the next warning; announces "Warning N of M: <message>").
- `quill.previousValidationWarning` — Previous Warning.
- `quill.readValidationSummary` — Warnings Summary (announces total count and top 3 categories).

**Warnings List dialog (`tests/unit/ui/test_dialog_inventory.py` gate):**
- Accessible `wx.ListBox` (or `wx.ListCtrl` with `LC_REPORT`) showing `Line / Page / Severity / Category / Message`.
- Pressing Enter moves the caret to the selected warning.
- Escape closes the dialog.
- A11Y-4 banned-pattern gate must pass: dialog uses `apply_modal_ids`, label-then-control via lambda factory, deterministic focus, explicit default button.

**Tests:**
- `tests/unit/ui/test_main_frame_menu_contract.py`: Braille > Validation submenu contains all 4 items.
- `tests/unit/core/test_brf_validator.py`: integration with main_frame command handlers (source-contract).
- `tests/unit/ui/test_dialog_inventory.py`: warnings dialog is in the inventory snapshot; A11Y-4 gate passes.
- `tests/unit/ui/fixtures/dialog_inventory.json` regenerated via `python -m quill.tools.dialog_inventory --write`; snapshot staged with the change.

**Parent plan:** `docs/braille.md` (Phase 4, Validation). Tracked in session todos as `br-validation-commands`. Depends on #241 (BR-018).



---

## #246 — [BR-023] Source-to-BRF linking (Braille Mode P6, v1.1)

**Labels:** enhancement

[P6] Source-to-BRF linking — anchors, cross-linked progress, and a Compare Back-Translation with Source command. **Deferred to QUILL 1.1.**

**Scope (when picked up):**
- Source positions (line/column in the print original) recorded as anchors in the BRF sidecar.
- BRF positions (braille page / line / cell) for the same anchor.
- Linked progress report: which source pages are transcribed, proofed, or unlinked.
- `quill.compareBackTranslationWithSource` — open the back-translation draft (BR-022) side-by-side with the source print and step through line-by-line differences.
- `quill.listUnlinkedSourcePages` — list source pages that have no BRF anchor.

**Why deferred:**
- Requires a stable Source-position model across all print source formats (TXT, RTF, DOCX, EPUB, PDF); that work is gated on a separate Source-Position effort not in v1.0.
- Needs a careful back-translation-confidence signal from liblouis that is not in current liblouis releases.
- Risk of confusing users with "linked" vs "unlinked" semantics; needs a UX pass.

**Tracking:**
- This issue remains OPEN but is moved into the **v1.1** column on the ROADMAP. It is referenced from BR-017 and BR-022 so the v1.0 work documents the linking stub where appropriate.
- The deprecation note appears in `docs/braille.md` so contributors do not start P6 work before the Source-Position effort lands.

**Parent plan:** `docs/braille.md` (Phase 6, Source-to-BRF Linking). Tracked in session todos as `br-source-link` (pending, intentionally). Depends on #240 (BR-017) and #245 (BR-022).



---

## #600 — [Planning] Braille Mode Phases 3/4/6 — tracked by #238-#246

**Labels:** accessibility, feature, p1

Source: `docs/planning/planning.md` Feature: Braille Mode design content (lines 100-577).

The Braille Mode design in planning.md (data structures, status bar design, screen-reader announcements, opt-in UEB Translation Pack, validation warning catalog, deployment script, source-to-BRF workflow) is the reference design for Phases 3, 4, and 6 of Braille Mode.

### Tracking

Each phase is already tracked by the GitHub issues below. **No new issues are created for braille design content**; this pointer exists only so the planning.md retirement is complete.

- #238 — BRF sidecar (Phase 3 prereq)
- #239 — brf_progress.py + open-flow restore (Phase 3)
- #240 — Proofing submenu (Phase 3)
- #241 — BRF validator (Phase 4)
- #242 — Validation commands + Warnings List dialog (Phase 4)
- #243, #244, #245 — already closed
- #246 — Source-to-BRF linking (Phase 6, now in 0.7.0 scope per user direction)

### Closes

Braille Mode design content (Phases 3, 4, 6) of `docs/planning/planning.md`.



---

## #601 — [Planning Archive] Braille Mode design reference - Phases 3/4/6 deferred from 0.7.0

**Labels:** documentation, enhancement

## Status

The Braille Mode design source-of-truth is in the repo today as
`docs/planning/planning.md` lines 100-577 ("Feature: Braille Mode"
section). This issue captures that design content as a reference for
the future work that will land in 0.7.1 or later.

## Why captured here

The `docs/planning/` folder is being retired as part of the 0.7.0
release-readiness work; per the project's planning-folder retirement
rule, planning files can be deleted once their content is captured in
issues. This issue is the canonical archive of the design that was in
that section.

## Status of the phases

- **Phase 1 (BRF Core)** - shipped in 0.6.0
- **Phase 2 (Page Intelligence + Detailed Status)** - shipped in
  0.6.1; the `brf_page_detection.py` module (BR-013) is on main in
  0.7.0 Beta 1.
- **Phase 5 (UEB Translation Pack, opt-in)** - shipped in 0.6.0
- **Phases 3, 4, 6** - **deferred from 0.7.0**. Reference design
  captured below. The shipped work is governed by #600 (parent
  pointer) and #238-#246; the design captured in this issue is the
  source-of-truth when those phases eventually ship.

## Design content

The full design is too large to inline in one issue. The original
`docs/planning/planning.md` "Feature: Braille Mode" section is the
canonical source. The subsections:

### Working title

QUILL Braille Mode.

### Product vision

QUILL Braille Mode provides a lightweight, screen-reader-first
environment for opening, editing, validating, navigating, translating,
and tracking progress in BRF files, with a focus on English UEB
workflows.

This feature does not attempt to replace Duxbury, BrailleBlaster, or
full production transcription systems. QUILL is a fast, dependable,
accessible tool for blind users who need to work directly with BRF
files, understand where they are, track transcription or proofreading
progress, and optionally perform English UEB translation without
bloating the editor.

### Primary audience

- Blind transcriptionists
- Blind proofreaders
- Blind braille readers working with BRF files
- Blind developers or educators reviewing braille output
- Users who need to inspect or lightly edit BRF without launching a
  full transcription suite

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

Included in QUILL core at various phases:

- Open and save `.brf` and `.brl` (shipped Phase 1)
- Preserve all spaces, line breaks, and form feeds (shipped)
- Detect BRF page breaks (shipped)
- Calculate braille page, line, and cell position (shipped)
- Status bar support (shipped)
- Screen-reader announcement commands (shipped)
- Go to braille page (shipped)
- Go to print page when detectable (shipped Phase 2)
- Insert page break (shipped)
- Validate BRF layout (Phase 3 - `brf_validator.py` #241)
- Detect page numbering conventions (Phase 3)
- Page map engine (Phase 3 - `brf_page_map.py` improvements)
- Detailed status with running head and confidence (shipped Phase 2)
- Sidecar progress file (Phase 3 - `brf_sidecar.py` #238)
- Restore last position on open (Phase 3 - `brf_progress.py` #239)
- Proofing submenu (Phase 3 - `brf_proofing.py` #240)
- Validation commands and Warnings List dialog (Phase 4 - #242)
- Source-to-BRF linking (Phase 6 - `brf_linking.py` #246)

### Deployment and packaging the Braille Pack (liblouis)

The UEB Translation Pack is opt-in. It is downloaded and installed
out-of-process by `scripts/build_braille_pack.py`. The build downloads
the liblouis prebuilts from `S:/QUILL/liblouis/vendor/braille/pack`,
stages them to `build/braille-pack/`, and packages them as an
installer component. The pack is a separate, optional install that
the user enables from `Braille -> Install Braille Pack...`. Once
installed, the Translation submenu appears in the Braille menu and
the worker process is launched on demand.

### Supported braille variants for the shipped scope

English UEB (Unified English Braille), grades 1 and 2. Other variants
(liblouis tables) may be added later through additional packs.

### Important page concepts (reference for Phase 2+)

- **Braille page** - a logical page in the BRF, separated by form feed
  characters (`\f`) or the calculated line count if no form feeds
  exist. A braille page typically holds 28-31 lines.
- **Print page** - the printed-page anchor, read from the right
  margin of line 1 of each braille page. Detected with high/medium/low
  confidence. The first page is always marked "Print ?" because no
  anchor exists.
- **Continuation letter** - a, b, c, ... appended to the print page
  number when a braille page overflows the print page. Detected as a
  right-margin number on line 1 of a continuation page that matches
  the previous detected page.
- **Running head** - the leading text of line 1 after stripping the
  right-margin page number. Detected on every page that has a number
  on line 1.
- **Sidecar progress** - a `.brf.progress.json` file that lives next
  to the BRF and records which pages have been proofed and the last
  position. The status bar reports proofing state from this file.

### Status bar design (shipped)

The Braille status cell shows, in order:
`Page N of M | Line N | Cell N | Print N`. Phase 2 added the print
segment and the running-head segment. Phase 3 will add the proofing
state and confidence. The cell is keyboard-navigable and read in full
by `Read Detailed Braille Status`.

### Status verbosity settings (Phase 2 reference)

- `braille_status_announce_on_page_change` - announce page changes
  on/off.
- `braille_status_announce_running_head` - include running head in
  status.
- `braille_status_announce_confidence` - include detection confidence.

### Required keyboard commands

- **Phase 1 (shipped)**: Braille menu, Open BRF, Save BRF, Go to
  Braille Page, Next/Previous Braille Page, Read Current Braille
  Status.
- **Phase 2 (shipped)**: Go to Print Page, Next/Previous Print Page
  Change, Announce Running Head, Include/Omit Running Head in Status.
- **Phase 3 (deferred)**: Mark Page Proofed, Mark Page Unproofed,
  Jump to Next Unproofed Page, Sidecar progress commands.
- **Phase 4 (deferred)**: Validate BRF, Next Warning, Previous
  Warning, Show Warnings List.
- **Phase 6 (deferred)**: Link to Source, Jump to Linked Source.

### Sidecar progress file

`{basename}.brf.progress.json` next to the BRF. Schema:

```json
{
  "version": 1,
  "last_position": {"braille_page": 12, "line": 5, "cell": 18},
  "proofed_pages": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
  "notes": "Reviewed through page 11 on 2026-05-20"
}
```

### Validation engine

Phase 4. Walks the BRF page map and emits warnings for:

- Pages that are too long (more than 31 lines)
- Lines that are too long (more than the cell width)
- Lines with no terminating space
- Form feed at end of file
- Page numbering inconsistencies

### Page map engine

`quill/core/brf_page_map.py`. Walks the BRF once and emits a list of
`BraillePage` objects with line counts, cell widths, and detected
markers. O(N) pass with one `.split('\f')` call.

### Print page detection strategy

Phase 2 (shipped). Pure detection routine in
`quill/core/brf_page_detection.py`. No `wx` imports. Walks the page
map once and emits confidence-labelled indicators. High confidence:
separator line with anchor (`---------#ab`, `---------#12a`,
`---------#1`) or right-margin continuation. Medium: right-aligned
number on line 1 with no other anchor, or a consistent sequence
across pages. Low: ambiguous right-margin number, or a short page
with multiple candidates.

### Transcriptionist progress workflow

A transcriptionist opens a BRF, navigates by braille page, marks
each page proofed as they go, and can resume from the last position.
The sidecar progress file is the source of truth; QUILL never
modifies the BRF file itself for progress tracking.

### File handling rules

- Never change line endings, trailing whitespace, or form feeds
- Never insert or remove `\f` characters
- Save byte-identical when no edits are made
- Read with `encoding='utf-8'` and `newline=''` (Python file IO
  convention) so form feeds are preserved

### Data structures

```python
@dataclass
class BraillePage:
    number: int
    lines: list[str]
    line_count: int
    max_cell: int
    marker: Optional[BraillePageMarker]
    running_head: Optional[RunningHead]
    print_page_indicator: Optional[PrintPageIndicator]
```

### Suggested internal modules (shipped where applicable)

- `quill/core/brf_document.py` - load/save BRF (shipped)
- `quill/core/brf_ascii.py` - ASCII helpers (shipped)
- `quill/core/brf_page_map.py` - page map (shipped)
- `quill/core/brf_page_detection.py` - print page detection
  (shipped Phase 2)
- `quill/core/brf_position.py` - caret position math (shipped)
- `quill/core/brf_status.py` - status cell rendering (shipped)
- `quill/core/brf_validator.py` - validation engine (Phase 4)
- `quill/core/brf_sidecar.py` - sidecar progress (Phase 3)
- `quill/core/brf_progress.py` - last-position restore (Phase 3)
- `quill/core/brf_linking.py` - source linking (Phase 6)

### Pragmatic shipping order

The reference order in the original design was:

1. Phase 1 (BRF Core) - shipped 0.6.0
2. Phase 2 (Page Intelligence + Detailed Status) - shipped 0.6.1
3. Phase 3 (Proofing + Sidecar) - deferred
4. Phase 4 (Validation + Warnings) - deferred
5. Phase 5 (UEB Translation Pack) - shipped 0.6.0
6. Phase 6 (Source Linking) - deferred

### Definition of done for the shipped scope (Phases 1 + 5)

- BRF open/save is byte-identical
- Page map and status bar work with form-feed-separated and
  calculated pages
- Print page detection works on the 5-page sample at
  `tests/corpus/braille/one_crazy_night.brf`
- Detailed status reads in the order from the spec
- 12+ unit tests cover the page map, position math, and
  detection logic
- Real NVDA + JAWS sign-off on the Braille menu and status cell

### Accessibility requirements

- Every status element has a screen-reader name
- The Braille status cell is keyboard-reachable
- "Read Detailed Braille Status" composes the full example
  string from the spec
- All Braille menu items are announced and discoverable
- Per-page commands are reachable from the menu and from the
  QUILL-key chord space

## Why this is being filed

The `docs/planning/planning.md` "Feature: Braille Mode" section is
the source-of-truth for the Braille Mode feature. The section is
being retired along with the rest of `docs/planning/`. This issue
preserves the design content so the phases that don't ship in 0.7.0
still have a reference when they land in a later release.

## Reference

- #600 - `[Planning] Braille Mode Phases 3/4/6 - tracked by
  #238-#246`
- #238 - `brf_sidecar.py` (Phase 3)
- #239 - `brf_progress.py` (Phase 3)
- #240 - `brf_proofing.py` (Phase 3)
- #241 - `brf_validator.py` (Phase 4)
- #242 - Validation commands + Warnings List dialog (Phase 4)
- #243, #244, #245 - Phase 4 details
- #246 - `brf_linking.py` (Phase 6)
- Original source: `docs/planning/planning.md` lines 100-577
  (now retired with the planning folder)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
