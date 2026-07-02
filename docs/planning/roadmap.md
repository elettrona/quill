# QUILL — Plan of Record (outstanding work)

> **The single planning document — it tracks only what is still open**, plus the
> register of **locked / hidden** features (consolidated here from the retired
> `deferred-locked-features.md`). Shipped work is not listed here; once something
> lands it leaves this file and its behavior lives in the user guide and
> `QUILL-PRD.md`. The other planning files are the large in-flight feature specs, each
> with open work of its own:
>
> - [`quill-native-accessible-table-studio-plan.md`](quill-native-accessible-table-studio-plan.md) — Table Studio (not started).
>
> The Accessible Vault plan has been **retired**: Phases 0–7 shipped (feature-complete
> for 0.9.0) and the feature now lives in `QUILL-PRD.md` §5.89d and the user guide; the
> small remaining polish is §1.7 below.
>
> **Operating principle:** everything here is in scope to **ship** for 1.0 (except
> rows explicitly marked 2.0). Simplicity for the screen-reader user is king. QUILL
> owns the editor, focus, undo, and announcements; AI and every integration are
> optional and off by default. Platform scope is Windows (primary) and macOS
> (supported).

**Last consolidated:** 2026-07-02 (GLOW shipped as an experimental opt-in; OCR free local tiers shipped;
locked-register GLOW block retired into the real docs).

---

## 0. North star

QUILL is a screen-reader-first writing environment, becoming the home for a family
of accessibility products that Blind Information Technology Solutions (BITS) and
CSE Designs built as separate apps. Rather than ship four editors, we **consolidate
their durable value into QUILL** as optional, keyboard-clear, screen-reader-first
feature families. Sibling products still feeding open work: **GLOW** (`s:\code\glow`,
accessibility audit + agents) and **ChapterForge** (`c:\code\forum`, audio →
chaptered audiobook). The discipline: take what clears QUILL's quality and
accessibility bar, re-home it on QUILL's invariants (atomic storage, the dialog
contract, the announcement grammar, Safe Mode, the network-egress audit), and leave
behind anything superseded or off-mission.

---

## 1. Open workstreams

### 1.1 AI footprint & optimization — remaining wiring + build/hardware sign-off

The measurement-first effort to make QUILL's full AI + speech feature set install
small, start fast, and run on a cheap CPU-only laptop. The durable design (principles,
reliable-acquisition model, host/redistribution rules, size/RAM reference) lives in
[`QUILL-PRD.md`](../Product%20Requirement%20Documents%20and%20Specifications/QUILL-PRD.md)
§5.25f. The wx-free cores (runtime-memory policy, upgrade advisor, cloud↔local
fallback, footprint sampler) and the Vosk unbundle + self-hosting have shipped and
are unit-tested. **Still open:**

- **Live-app sign-off (smoke test)** of the now-wired runtime-memory policy (the
  idle-sweep timer firing, a real model unloading), the model upgrade hint in the AI
  model dialog, and the offline cloud↔local fallback announcement on a real failure.
- **Phase 1 installer-size delta** — needs a real Windows build to measure/confirm.
  Remaining candidates are ruled out or deferred: `win32more` is a real dependency of
  Windows OCR, `vosk` already unbundles on demand, non-en enchant dictionaries already
  download on demand. Concrete new quant catalog entries (q5/q8, int8_float16) need
  real pinned files + SHA-256 hashes.
- **Phase 0 committed numbers** — per-engine peak RSS and cold-start/first-token
  timings need a live run on a reference machine.
- **macOS offline-speech parity** — a mac `whisper-cli`, or Faster Whisper as the mac
  default — the tracked cross-platform gap.

### 1.2 GLOW — shipped as an experimental opt-in (2026-07-02)

The **GLOW accessibility suite shipped for 0.9.0** behind the Experimental tab
(master switch + GLOW checkbox, both default off, no restart): `core.glow` is unlocked, the
in-editor audit/fix commands are live, and the new **GLOW Audit File... / GLOW Fix
File...** commands run the shared engine (DOCX, PPTX, XLSX, PDF, EPUB) on the
background task pool with non-destructive fixed copies. The engine deployment
contract was hardened (`quill-glow-core[glow]>=0.1.1` + `acb-large-print>=8.0.0`).
Canonical docs: **PRD §5.92**, user guide "GLOW Workflows Inside QUILL", release
notes. Only the *extended* GLOW family (ACB large-print document audit, #528–#534,
the WATCH-8 watch action #566) remains future — see §5.

### 1.3 Platform & distribution

- The Quillin Hub (#517); plugin capability + signing + marketplace (#519) — the
  latter gated on the third-party-plugin sandbox (§2).
- **Deferred to 2.0** (tracker #680): the Windows 11 modern primary-menu
  `IExplorerCommand` pass (SHELL-3, #525).

### 1.4 Docs, tutorials & content

One **Documentation & Tutorials** track: user-guide coverage, getting-started
tutorials, the podcast/walkthrough series, and content-quality follow-ups
(#535–#564, #505, #522). Long-horizon ecosystem (#590) and collaboration (#592)
ideas park here.

### 1.5 Native accessible Table Studio (not started)

**Spec:** [`quill-native-accessible-table-studio-plan.md`](quill-native-accessible-table-studio-plan.md).
The accessible table-authoring surface (and the CSV-grid half of #514) — planned
design only.

### 1.6 ElevenLabs — remaining 2.0 extras

Speech-to-text (Quillin), audiobook-grade **Batch Export** TTS, and a selectable **Read
Aloud voice** (per-session consent, Safe-Mode gated) all shipped. What remains is
2.0-deferred: live streaming Read Aloud refinements, voice management / cloning /
design, server-side pronunciation, and Tier-3 surfaces — all in §5. Voice **cloning**
is deliberately descoped (QUILL narrates with the account's existing voices).

### 1.7 Accessible Vault — complete

The Accessible Vault is **complete for 0.9.0** — Phases 0–7 plus all former "remaining
polish" (completion, live-preview resolution, Vault Explorer, incremental indexing)
shipped. Canonical docs: `QUILL-PRD.md` §5.89d, user guide (Tools > Vault), changelog,
release notes. No open Vault work remains.

---

## 2. Locked / hidden features (register)

These features are gated `locked_off=True` in `quill/core/feature_catalog.py` and must
**not** appear in shipping user-facing docs (user guide, release notes, control
reference, PRD). Authoritative state is the catalog; this register is the human summary
(consolidated from the retired `deferred-locked-features.md`). When a feature unlocks,
move its preserved content back into the relevant doc.

**Currently locked (as of 0.9.0 Beta 1):**

- `core.voice_commands` — **Voice Commands** ("say a command out loud"), QUILL's
  hands-free **voice interaction**. Locked because it was tied to the now-removed
  Windows dictation path; it needs re-homing on the shipped offline dictation engine
  before it can return.
- `core.rich_text_lens` — **Rich Text Lens** (native wxPython rich-text editing for
  `.rtf`). Locked pending fuller screen-reader testing; RTF opens as plain text
  meanwhile. Docs must not claim native RTF editing ships.
- `future.publishing` — **Publishing** send path (publishing connections + provider-aware
  remote publishing). Locked while the providers framework is reviewed; the read-only
  inbound half ships. Release notes already frame this as *future*.
- `core.third_party_plugins` — **Third-Party Plugins** loader (SEC-8). Locked until the
  plugin sandbox, signing, and review process ship. Release notes frame third-party
  Quillins / a marketplace as *future*.
- `core.bw_whisperer` — **BITS Whisperer** brand menu (plus `core.bw_transcription`,
  `core.bw_providers`, `core.bw_insights` sub-flags, the `quill/core/bw_providers.py`
  backend, the hidden Whisperer menu, and its commands/settings). This gates only the
  **superseded branded presentation** — the phased-rollout / Provider Center / Status Page
  surface that the shipped flat **Tools > Speech** menu replaced. It does **not** gate the
  speech or agentic-AI *capabilities*, which ship as plain, always-on features.
  **Decision: keep it as-is (locked, inert).** It builds nothing at runtime and ships
  nothing, so there is no benefit to removing it and real risk in the ~1000-line untangle
  (its handlers are coupled to the *shared* `bw_speech.py` and speech settings that the
  live speech service uses). Leave it locked until there is a concrete reason to touch it.

**All voice and speech *capabilities* are shipped and baked in** — offline dictation,
transcription and captions, read-aloud across SAPI 5 / DECtalk / Piper / eSpeak / Kokoro
and the ElevenLabs cloud voice, batch document-to-speech, and audiobook building. The
only speech-adjacent lock left is `core.voice_commands` (hands-free voice interaction).

> **Docs framing.** GLOW ships as an experimental opt-in (2026-07-02) and its preserved user-facing content
> has been restored into the user guide ("GLOW Workflows Inside QUILL"), glossary, help
> topics, and PRD §5.92 — the §2.1 preservation block this file used to carry is gone
> because the real docs now own it. The **BITS Whisperer** brand is retired — earlier
> drafts named a "BITS Whisperer speech suite" / "Tools > Speech > Whisperer"; that is
> now the flat **Tools > Speech** menu and a plain "private, on-device speech suite,"
> with no brand to restore.

---

## 3. Release gap list (path to green)

What's left between QUILL and a **green, release-ready** state is now just **routine
validation**, handled in the normal QA pass rather than tracked as release blockers
(the same disposition as the closed #506 / #518 / #526):

- **Packaged-build validation** of the optional speech engines (Faster Whisper, Vosk)
  on the real installer, not just from source.
- **Watch Folder queue** — a live repro confirming the by-design priming (drop a *new*
  matching file into a running profile, or enable "Process existing files").
- **Snapshots vs Versions** — a live repro of the reported empty-submenu render (toggle
  the `core.notebook` / `core.recovery` flags); the user-facing "Versions" rename is done.

Excluded per direction: all table work (§1.5 + the CSV-grid half of #514).

---

## 4. Planned phase outcomes

What the user will notice as the open work lands, screen-reader experience first.

- **Phase 3 — An AI that helps without taking over.** One coherent AI Hub; agents that
  read your selection and propose edits you preview and undo in one step — never silent
  changes. *Powerful help that stays reviewable, undoable, and spoken.*
- **Phase 4 — Move faster + publish further.** Structured Word/CSV views and the Table
  Studio surface (§1.5); broader publishing, e.g. direct publishing to external
  platforms (#140); the extended GLOW family (§5). *Faster keyboard navigation and
  accessible publishing.*
- **Phase 5 — Solid on Windows and macOS.** The Quillin hub (§1.3); better docs/tutorials
  (§1.4). *A dependable, well-documented product on its supported platforms.*

---

## 5. Deferred to QUILL 2.0

Confirmed out of 1.0 scope. Recorded so the intent is not lost; items graduate into the
open sections above when scheduled.

- **Dictation later phases** — an optional **global Windows key hook** (system-wide
  dictation hotkey), **idle-silence detection** (auto-stop on a pause), and **dictation
  intelligence** (spoken punctuation/commands). Each is sizable beyond the keyboard-only
  Hold/Locked dictation that ships.
- **Voice interaction** (`core.voice_commands`, §2) — re-home the hands-free "say a
  command" surface onto the shipped offline dictation engine (it was tied to the removed
  Windows dictation path), then unlock.
- **BITS Whisperer remainder** (tracker #680) — the consolidation shipped for 1.0; the
  leftovers (a Windows SAPI/WinRT zero-download engine, a consented cloud watch action,
  guided provider onboarding, diarization/live-mic, additional cloud kinds, and the
  Whisperer brand decision) moved to #680 when #669 closed. See also the `bw_whisperer`
  cleanup in §2.
- **Platform singleton** (tracker #680) — the Windows 11 modern primary-menu
  `IExplorerCommand` pass (SHELL-3, #525). *(Freeze/compile packaging — PyInstaller /
  Nuitka — is out of scope: the embedded-Python + Inno Setup model is the shipping
  approach.)*
- **Direct publishing (#140)** — publish a finished document/audiobook to WordPress and
  other platforms; a long-term, likely-**Quillin** integration; early design in
  `docs/design/publishing/`.
- **Remaining ChapterForge surfaces** — Auphonic post-processing, RSS podcast feeds,
  SFTP publishing, and MusicBrainz / Open Library metadata lookup.
- **ElevenLabs Tier-2/3 extras** — live streaming Read-Aloud refinements (SDK streaming,
  sentence prefetch, an aggressive `tts_cache`, a persistent "reading via ElevenLabs
  (cloud)" indicator); voice management / cloning / design / server-side pronunciation
  dictionaries; and the SFX / voice-changer / generation-history surfaces (if ever built,
  as **optional Quillins**, not core). QUILL narrates with the account's existing voices
  and does **not** clone.
- **Native Google Docs support** — read/write/round-trip Google Docs (Drive API, OAuth,
  accessible doc model); spec in
  [`QUILL-Native-Google-Docs-Support-PRD.md`](QUILL-Native-Google-Docs-Support-PRD.md).
- **Extended GLOW family (§1.2)** — the core GLOW suite **shipped (experimental opt-in) for
  0.9.0** (PRD §5.92); what stays future is the extended family: ACB Large-Print
  Guidelines / Microsoft Accessibility Checker / WCAG 2.2 AA document-audit profiles
  (#528–#534) and the WATCH-8 GLOW watch action (#566), re-homed on QUILL's invariants.
  GLOW's server/Keycloak/Office-add-in/MCP surfaces stay in the GLOW product
  (`s:\code\glow`); QUILL takes the authoring-time checks.
- **OCR / document-conversion depth extras** — the supported tool **shipped complete
  for 0.9.0** (all three tiers, the AI Hub Services tab, Review Mode v1, temp-file
  management; canonical spec now **PRD §5.93** — the standalone OCR planning PRD is
  retired). Remaining depth, on demand: the full §12-style review *workspace*
  (outline tree, per-block accept/edit, table review/CSV export, re-run pages in
  accurate mode, OCR dictionary), Datalab advanced options (page ranges, max pages,
  word/table bounding boxes, block IDs, extras, processing region, usage warnings),
  additional providers (Azure Document Intelligence, Mistral OCR, AWS Textract,
  Google Document AI, local Marker/Chandra), a provider comparison view, on-prem
  endpoint guidance, and an optional Ctrl+Shift+O shortcut.
- **Verbosity polish-backlog long tail** — the speculative slice of the ~100 addenda
  (#405–#504) beyond the shipped core/UI/modes/anti-spam; the shipped design lives in
  **PRD §5.91**. Full backlog below.

### Verbosity 2.0 polish backlog (consolidated)

The verbosity engine and its full 1.0 surface shipped (design in **PRD §5.91**). This is
the consolidated reference for the **deferred** polish-backlog addenda (#405–#504),
absorbed here when the standalone `verbosity-system.md` archive was retired. Issue
numbers are kept so each idea stays findable.

**Valuable candidates (build first if the range reopens):**

- **Error coaching (#416)** — turn an error announcement into a next-step hint.
- **Per-category announcement detail levels (#418)** — independent verbosity per category
  (nav / edit / search / system) on top of the global profile.
- **Markdown-aware (#427) / Code-aware (#428) verbosity** — context-sensitive
  announcements when editing Markdown or source.
- **"Undo available" cues (#502)** and richer **destructive-action warnings (#501)** (the
  confirm dialog ships; the spoken cue is the increment).
- **Boundary announcements (#419)** and **progress-announcement controls (#420)**.
- **Details-on-demand (#417)** beyond the existing status-query commands.

**Themed reference well (speculative; build only on demand):**

- *Settings UX:* searchable settings (#406), recipes (#407), bulk edit (#464), undo for
  settings (#465), change history (#466), export preview (#482), import-conflict wizard
  (#483), "try without applying" (#484), reset granularity (#481), explain-my-settings
  (#446), test-my-settings (#467), recommended settings (#468), persona setup (#469).
- *Packs:* community pack preview/diff (#442), trust labels (#443), copy-as-user-template
  (#444), pack-author mode (#461), built-in sample QVPs (#462), conflict checker (#445).
- *Modes / recipes:* focus mode (#487), review mode (#488), session profiles (#485),
  time-based quiet hours (#486), temporary boost (#436), training mode (#438).
- *Privacy / support:* privacy controls (#448), private-document mode (#449), export
  support bundle (#447), copy debug summary (#478), report announcement (#479), developer
  trace verbosity (#495), performance knobs (#496).
- *Output niceties:* last-important announcement (#452), pin status (#456), smart status
  rotation (#457), favorites (#455), labels (#473), per-announcement suppression
  (#471/#472), earcons-with-text (#453), learn-sounds mode (#454), status badges (#497),
  braille status cell (#498), before/after announcements (#500).
- *Content / localization:* friendly names (#440/#477), microcopy style (#490),
  use-my-words labels (#491), abbreviation dictionary (#492), localization readiness
  (#493), readability verbosity (#489).
- *Hardware / context:* multi-monitor / presentation safety (#503), screen-reader handoff
  mode (#410), command discovery (#470), contextual help hooks (#439), hold-to-explain
  (#437), confidence-check wizard (#441).

**Recommend do not build** (the screen reader already owns these; QUILL speaks
*alongside* it and must not duplicate or fight its settings): **typing echo (#411)**,
**command echo (#499)**, **speech rate / pause knobs (#450)**, and **punctuation / symbol
profiles (#426)**.

---

## 6. Feature ledger (open work by workstream)

| Workstream | Open work |
| --- | --- |
| AI footprint & optimization (§1.1) | Live-app smoke test; Phase 1 installer-size build; Phase 0 committed numbers; macOS speech parity. |
| GLOW (§1.2) | **Shipped 0.9.0 (experimental opt-in).** Extended family (ACB audit profiles #528–#534, WATCH-8 #566) in §5. |
| OCR / document conversion (PRD §5.93) | **Free local tiers shipped 0.9.0.** Cloud tier, OCR Review Mode, Services tab in §5. |
| Platform & distribution (§1.3) | #517, #519; #525 deferred to 2.0 (#680). |
| Docs & content (§1.4) | #535–#564, #505, #522, #590, #592. |
| Table Studio (§1.5) | Whole feature (`quill-native-accessible-table-studio-plan.md`). |
| ElevenLabs 2.0 extras (§1.6) | Live streaming Read Aloud, voice management, Tier-3 — all §5. |
| Accessible Vault (§1.7) | **Complete for 0.9.0** — no open work. |
| Locked features (§2) | Voice Commands, Rich Text Lens, Publishing (send), Third-Party Plugins (`bw_whisperer` kept locked/inert — not removed). |
