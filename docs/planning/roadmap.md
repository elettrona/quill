# QUILL — Plan of Record (outstanding work)

> **The single planning document, and it tracks only what is still open.** Shipped
> work is not listed here — once something lands it leaves this file; its behavior
> lives in the user guide and `QUILL-PRD.md`. The only other files in
> `docs/planning/` are the large in-flight feature specs, each with open work of
> its own:
>
> - [`verbosity-system.md`](verbosity-system.md) — verbosity polish backlog.
> - [`quill-native-accessible-table-studio-plan.md`](quill-native-accessible-table-studio-plan.md) — Table Studio (not started).
> - [`quill_end_to_end_agentic_ai_prd.md`](quill_end_to_end_agentic_ai_prd.md) — Agentic AI platform (planned).
> - [`eleven-labs.md`](eleven-labs.md) — ElevenLabs / ElevenDesk integration ideas (not started).
>
> **Operating principle:** everything here is in scope to **ship** for 1.0 (except
> a few rows explicitly marked 2.0). Simplicity for the screen-reader user is king.
> QUILL owns the editor, focus, undo, and announcements; AI and every integration
> are optional and off by default. Platform scope is Windows (primary) and macOS
> (supported).

**Last consolidated:** 2026-06-25.

---

## 0. North star

QUILL is a screen-reader-first writing environment, becoming the home for a family
of accessibility products that Blind Information Technology Solutions (BITS) and
CSE Designs built as separate apps. Rather than ship four editors, we **consolidate
their durable value into QUILL** as optional, keyboard-clear, screen-reader-first
feature families — keeping names users know where they carry brand equity (notably
**BITS Whisperer** for speech). Three sibling products still feed open work:
**BITS Whisperer** (`s:\code\bw`, transcription/speech), **GLOW** (`s:\code\glow`,
accessibility audit + agents), and **ChapterForge** (`c:\code\forum`, audio →
chaptered audiobook). The discipline: take what clears QUILL's quality and
accessibility bar, re-home it on QUILL's invariants (atomic storage, the dialog
contract, the announcement grammar, Safe Mode, the network-egress audit), and
leave behind anything superseded or off-mission.

---

## 1. Workstreams (open work)

### 1.1 Verbosity — polish backlog

The engine and UI are in; the remaining work is the **polish backlog** (the ~100
addenda, #405–#504) — land the high-value knobs (announcement budgets, repetition
collapse, typing-echo controls, per-category detail levels, destructive-action and
undo-available cues) and fold-in-or-defer the speculative rest. Each survivor is a
checklist item in [`verbosity-system.md`](verbosity-system.md) (§ "Polish
backlog"); the screen-reader-redundant ideas are recorded there as "recommend do
not build" (Typing/Command Echo, Speech Rate/Pause knobs, Punctuation/Symbol
Profiles — the SR already owns these).

### 1.2 Speech & Dictation — "BITS Whisperer"

**Batch document-to-speech follow-ups:**

- **Project-profile app wiring** — the `.quill/speech-project.json` format,
  storage, and `to_batch_options` converter exist and are tested, but the app does
  not yet `load_profile()` on folder open. Needs apply-on-open, a precedence
  resolver (this-run > project > global > defaults), a single
  `current_project_dir()`, and a "Remember for this project / Reset to global"
  surface (auto-remember on Start).
- **Chapterization:** `sound_id` → sound-pack resolution (a placeholder chime is
  the current fallback); confirm the `separate`-file-per-article path end-to-end.
- **Extraction/quality:** consider migrating `read_aloud.py` subprocess calls to
  `stability.safe_subprocess`.
- **Upstream:** offer ChapterForge the two fixes already in QUILL's `chapters.py`
  (non-contiguous gap chapters; ID3-tag clobbering); ElevenDesk research pass (see
  [`eleven-labs.md`](eleven-labs.md)).

**Dictation follow-ups:** Dictation History + interactive startup-recovery prompt;
a Dictation Review interface for deferred/unsafe insertions. (The dictation
**settings panel** shipped — Tools > Speech > Hold & Locked Dictation > Dictation
Settings; the minor earcon-volume / retention / visual-indicator knobs and the
larger later-phase capabilities are **2.0** — see §5.)

### 1.3 Agentic AI platform (planned)

**Spec:** [`quill_end_to_end_agentic_ai_prd.md`](quill_end_to_end_agentic_ai_prd.md).

Unify QUILL's AI stack behind one provider-neutral, optional, screen-reader-first
platform whose front door is the **AI Hub**: one provider truth, a Safe Editor Tool
Gateway + Permission Broker, a real tool-calling agent loop, a declarative agent
catalog, an activity log, and an optional harness layer. Supersedes the scattered
AI issues O5/O5b/O6 (#507–#509), O7 Azure (#510), O8/AI-19 Copilot SDK (#511/#523),
O9/SHELL-2 OCR structuring (#512/#524), and AI-11/12/18 (#579–#581). The
Accessibility Agents from GLOW (AX-A..F, #593–#598) become catalog agents here.

### 1.4 Accessibility tooling (from GLOW)

**Source:** `s:\code\glow` (`glowplan.md`).

- **Document Audit** — evaluate the current document against ACB Large-Print
  Guidelines, Microsoft Accessibility Checker rules, and WCAG 2.2 AA, returning a
  scored, navigable findings report. Lands as an in-QUILL audit surface (and an
  agent in §1.3).
- **GLOW family** — the seven GLOW capabilities (#528–#534) plus the WATCH-8 GLOW
  watch action (#566), re-homed on QUILL's invariants. Currently `locked_off`
  (hidden); decide for 1.0: finish + un-gate, or keep hidden.
- GLOW's server/Keycloak/Office-add-in/MCP-deployment surfaces stay in the GLOW
  product; QUILL takes the authoring-time checks.

### 1.5 Publishing & audiobook

The ChapterForge **folder-of-audio → one chaptered master** surface has shipped:
**Build Audiobook from Folder** (Tools > Speech) combines a folder of audio files
into a single chaptered **MP3** or **M4B** master (native chapter atoms), one
chapter per file with titles from filenames, plus book tags and an auto-detected
cover (`quill/core/speech/audiobook.py`). Remaining, aligned ChapterForge surfaces:

- **In-dialog chapter editing** — rename/reorder/merge chapters before building
  (today titles come from filenames in natural-sort order).
- **FLAC / Opus output** and an **ACX loudness compliance** check + one-click fix.
- **Direct publishing (#140)** — WordPress and other platforms; a long-term,
  likely-Quillin integration (external-API + auth surface), not core editor work.

Deferred as future-release ChapterForge surfaces (out of the current vision):
Auphonic post-processing, RSS podcast feeds, SFTP publishing, and MusicBrainz /
Open Library metadata lookup.

### 1.6 Platform & distribution

- Live installer smoke on Windows 10/11 (#506); macOS to shipping quality (#518);
  native RTF editing (#516); the Quillin Hub (#517); plugin capability + signing +
  marketplace (#519).
- **Deferred to 2.0** (tracker #680): the Windows 11 modern primary-menu
  `IExplorerCommand` pass (SHELL-3, #525) and the packaging/freeze evaluation
  (PKG-1 — PyInstaller packaging hardening, #599). *(Nuitka is explicitly out of
  scope — too much risk / not reliable enough.)*

### 1.7 Docs, tutorials & content

One **Documentation & Tutorials** track: user-guide coverage, getting-started
tutorials, the podcast/walkthrough series, and content-quality follow-ups
(#535–#564, #505, #522). In-flight QA: **#526** live NVDA/JAWS/Narrator sign-off.
Long-horizon ecosystem (#590) and collaboration (#592) ideas park here.

### 1.8 Structured List Studio — manual SR pass

The feature is shipped; the **only** remaining item is a formal live
**screen-reader pass** (JAWS / NVDA / Narrator) — manual, not closable in code;
only stub-level wiring tests exist. Part of the §2 Tier-1 SR sign-off (#526).

### 1.9 Native accessible Table Studio (not started)

**Spec:** [`quill-native-accessible-table-studio-plan.md`](quill-native-accessible-table-studio-plan.md).
The accessible table-authoring surface (and the CSV-grid half of #514) — planned
design only.

---

## 2. Release gap list (path to green)

What stands between QUILL and a **green, release-ready** state. Two senses of
"green": **(A) tooling green** — CI, tests, lint, types, gates; **(B)
release-ready** — no known-but-unverified defects, shipped features
complete/polished. Excluded per direction: the AI & Agentic workstream (§1.3) and
all **table** work (§1.9 + the CSV-grid half of #514).

### Tier 1 — Release-blocking verification ("fixed" but unconfirmed)

1. **Live screen-reader sign-off — #526.** Walk the accessibility fixes marked
   *"Fixed; needs live NVDA/JAWS/Narrator confirmation"* (notebook tab-group names,
   snake_case names, label association, initial focus, the Tab keyboard-trap class,
   focus-to-bad-field) — plus the List Studio pass (§1.8) — with JAWS, NVDA, and
   Narrator. **Highest single item.**
2. **Live installer smoke on Windows 10/11 — #506.** A packaged build installs,
   launches, and the first-run wizard runs on clean Win10 and Win11.
3. **Packaged-build validation of the optional speech engines** (Faster Whisper
   install path, Vosk reachability) on the real installer, not just from source.

### Tier 2 — Shipped features with rough edges

4. **Dictation follow-ups** — the settings panel and the History/Review surfaces
   (§1.2).
5. **Watch Folder queue — live repro:** when `core.watch_folder` is enabled the
   monitor "feels empty"; needs an interactive repro to confirm the live queue
   populates, or a fix.
6. **Snapshots vs Versions:** the notebook set was renamed to **"Versions"** (code
   half done); the empty-submenu render still needs a live repro.

### Tier 3 — Polish

7. **Verbosity polish backlog** (§1.1) — land the high-value knobs, fold-or-defer
   the rest so the range can close.

---

## 3. Planned phase outcomes

What the user will notice as the open work lands, screen-reader experience first.

### Phase 3 — An AI that helps without taking over

One coherent AI Hub; agents that read your selection and propose edits you preview
and undo in one step — never silent changes (§1.3). *Powerful help that stays
reviewable, undoable, and spoken.*

### Phase 4 — Move faster + publish further

Structured Word/CSV views and the Table Studio surface (§1.9); broader publishing,
e.g. direct publishing to external platforms (#140); GLOW family improvements
(§1.4). *Faster keyboard navigation and accessible publishing.*

### Phase 5 — Solid on Windows and macOS

Verified installer behavior on Windows 10/11, shipping-quality **macOS**, native
RTF editing, the Quillin hub (§1.6); better docs/tutorials (§1.7). *A dependable,
well-documented product on its supported platforms.*

---

## 4. Open-issue ledger (by workstream)

| Workstream | Open work |
| --- | --- |
| Verbosity (§1.1) | Polish backlog #405–#504 (in `verbosity-system.md`). |
| Speech & Dictation (§1.2) | Batch-speech follow-ups (project-profile wiring, sound_id, separate mode, SSML batch handling, richer docx, keyboard-activation audit); dictation follow-ups; BW backlog #515, #566–#577. |
| Agentic AI (§1.3) | #507–#512, #523/#524, #579–#581; Accessibility Agents #593–#598. |
| GLOW family (§1.4) | #528–#534, #566 (locked_off; decide for 1.0). |
| Publishing (§1.5) | #140 WordPress; ChapterForge integration. |
| Platform & distribution (§1.6) | #506, #516, #517, #518, #519; #525/#599 deferred to 2.0 (#680). |
| Docs & content (§1.7) | #526 SR sign-off; #535–#564, #505, #522, #590, #592. |
| List Studio (§1.8) | Manual SR pass (#526). |
| Table Studio (§1.9) | Whole feature (`quill-native-accessible-table-studio-plan.md`). |

---

## 5. Deferred to QUILL 2.0

Confirmed out of the 1.0 scope. Recorded here so the intent is not lost.

- **Dictation later phases** — an optional **global Windows key hook** (system-wide
  dictation hotkey), **idle-silence detection** (auto-stop on a pause), and
  **dictation intelligence** (spoken punctuation/commands). Each is a sizable
  capability beyond the keyboard-only Hold/Locked dictation that already ships.
- **BW consolidation backlog (#515, #566–#577)** — the broader provider-matrix
  tiers and guided onboarding (BW-1..10 / WATCH-8). A large workstream, already
  tagged 2.0-deferred in the program history.
- **Platform / packaging singletons** (tracker #680) — the Windows 11 modern
  primary-menu `IExplorerCommand` pass (SHELL-3, #525) and the PyInstaller
  packaging-hardening evaluation (PKG-1, #599). *(Nuitka is explicitly out of scope
  — too much risk / not reliable enough.)*
