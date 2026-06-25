# QUILL — Plan of Record

> **The single planning document.** This is the one source of truth for what has
> shipped, what is still open, and in what order — merged from the former separate
> `program-tracker.md`, `wave-outcomes.md`, `emergency.md`, `feature-backlog.md`,
> the dated live-test backlog, and the batch-speech `todo.md` (all retired into
> this file). The only other files in `docs/planning/` are the **large in-flight
> feature specs**, each with open work of its own:
>
> - [`verbosity-system.md`](verbosity-system.md) — verbosity polish backlog.
> - [`quill-structured-list-studio-prd.md`](quill-structured-list-studio-prd.md) — List Studio (shipped; manual SR pass + minor scopes remain).
> - [`quill-native-accessible-table-studio-plan.md`](quill-native-accessible-table-studio-plan.md) — Table Studio (not started).
> - [`quill_end_to_end_agentic_ai_prd.md`](quill_end_to_end_agentic_ai_prd.md) — Agentic AI platform (planned).
> - [`eleven-labs.md`](eleven-labs.md) — ElevenLabs / ElevenDesk integration ideas (not started).
>
> **Operating principle:** everything here is in scope to **ship** for 1.0 (the
> old "2.0 deferral" framing is dropped except where a row says otherwise).
> Simplicity for the screen-reader user is king. QUILL owns the editor, focus,
> undo, and announcements; AI and every integration are optional and off by
> default. Shipped design specs are **retired to git history** once delivered;
> their status lives here and their behavior in the user guide + PRD.

**Last consolidated:** 2026-06-25.

**Status legend:** ✅ shipped · ◐ partly shipped · 🚧 in progress · ⬜ planned ·
❌ out of scope.

---

## 0. North star

QUILL is a screen-reader-first writing environment. It is becoming the home for a
family of accessibility products that Blind Information Technology Solutions
(BITS) and CSE Designs have built as separate apps. Rather than ship four editors,
we **consolidate their durable value into QUILL** as optional, keyboard-clear,
screen-reader-first feature families — keeping the names users already know where
they carry brand equity (notably **BITS Whisperer** for speech).

Three sibling products feed this plan:

| Product | Source repo | What it is | Where it lands in QUILL |
| --- | --- | --- | --- |
| **BITS Whisperer** | `s:\code\bw` | Accessibility-first audio transcription: ~18 providers (cloud + on-device), AI translation/summarization, live-mic transcription, speaker diarization, plugins, 7 export formats. | **Speech & Dictation** (§1.2), keeping the BITS Whisperer brand. The offline core shipped (#617 S0–S5); the rest of BW's value is consolidated here. |
| **GLOW** | `s:\code\glow` | Multi-surface accessibility toolkit: Document Audit (ACB Large-Print Guidelines, Microsoft Accessibility Checker, WCAG 2.2 AA), accessibility agents, Office add-in, MCP server, watch action. | **Accessibility Tooling** (§1.4) and the **Agentic AI** agent catalog (§1.3). |
| **ChapterForge** | `c:\code\forum` | Turns a folder of MP3s into one chaptered audiobook/podcast master, screen-reader-first. | **Publishing & Audiobook** (§1.5), beside DAISY export. |

The discipline for every consolidation: take what clears QUILL's quality and
accessibility bar, re-home it on QUILL's invariants (atomic storage, the dialog
contract, the announcement grammar, Safe Mode, the network-egress audit), and
**leave behind** anything superseded by what QUILL already ships or that does not
serve the screen-reader-first mission.

---

## 1. Workstreams

### 1.1 Verbosity system ✅ (engine + UI shipped; polish backlog open)

**Spec:** [`verbosity-system.md`](verbosity-system.md).

Per-action, channel-aware, user-customizable announcements that replace the single
`announcement_verbosity` knob.

- **Shipped:** the pure-domain core (1.1 #361, 1.2 engine + runtime modes #362,
  1.3 QVP packs + library + preview #363), **the wxPython UI** (prefs panel, token
  editor, library, history viewer, preview lab, about — the `verbosity_*.py`
  modules), and **call-site wiring** (Quiet/Meeting modes, undo, "Where am I?" /
  "What changed?", the `VerbositySettings` fields). 220+ tests.
- **Open:** the **polish backlog** (the ~100 addenda, #405–#504) — land the
  high-value knobs (announcement budgets, repetition collapse, typing-echo
  controls, per-category detail levels, destructive-action and undo-available
  cues) and fold-in-or-defer the speculative rest. Each survivor is a checklist
  item in `verbosity-system.md` (§ "Polish backlog"), not a separate issue. The
  screen-reader-redundant ideas are recorded there as **"recommend do not build"**
  (Typing Echo, Command Echo, Speech Rate/Pause knobs, Punctuation/Symbol
  Profiles — the SR already owns these).

### 1.2 Speech & Dictation — "BITS Whisperer" ✅◐ (largely shipped)

**Brand: BITS Whisperer** (`s:\code\bw`). Shipped design specs (the S0–S5 plan,
the batch document-to-speech plan, the project-format spec, the hold-to-dictate
PRD) were retired to git history; behavior lives in the user guide (Speech) and
**`QUILL-PRD.md` §5.25** and §5.25d.

**Shipped:**

- **Offline STT (#617 S0–S4):** dictation honesty, the offline foundation,
  whisper.cpp + Faster Whisper engines, offline transcription, transcript/caption
  formats (plain/Markdown/HTML, SRT/VTT), speaker attribution, dictate-at-cursor
  (QUILL Key + Shift+D), mic selection, the model manager, and the installer
  component. Plus the **Vosk** low-resource engine (#677) and cloud transcription
  providers shipped as Quillins (OpenAI/Groq/ElevenLabs).
- **Offline voice commands (#663, Speech S5).**
- **Watch Folder auto-transcribe (WATCH-9):** on-device, consent-free, with
  selectable transcript format.
- **Read Aloud engines:** SAPI 5 system voice (pyttsx3 removed), DECtalk (via the
  real DLL runtime), eSpeak-NG, Piper, Kokoro — every catalog voice with a spoken
  preview; AI Voice cloud TTS (OpenAI + Google Gemini).
- **Hold-to-Dictate (F9) + Locked Dictation (Ctrl+F9)** — phases 1–2, with a
  dedicated Tools > Speech menu and user-configurable policy settings.
- **Batch Document-to-Speech** (Tools > Speech > Batch Export to Speech Audio):
  folder → chaptered audio, with MP3 chapter markers, **pronunciation
  dictionaries**, **TTS text normalization**, the **SSML Builder** + native SSML
  playback (SAPI 5 / eSpeak), and the full batch-flexibility surface (formats incl.
  M4B/Opus/FLAC, MP3 quality, existing-file policy, naming, audiobook metadata,
  retry/stop, parallel workers, run manifest, eSpeak/Piper engine knobs).

**Open — batch document-to-speech follow-ups** (folded in from the former
`todo.md`):

- **Project-profile app wiring** — the `.quill/speech-project.json` format,
  storage, and `to_batch_options` converter ship and are tested, but the app does
  not yet `load_profile()` on folder open. Needs apply-on-open, a precedence
  resolver (this-run > project > global > defaults), a single
  `current_project_dir()`, and a "Remember for this project / Reset to global"
  surface (auto-remember on Start).
- **Chapterization:** M4B **native** chapter atoms (today M4B ships as a format but
  markers are MP3 ID3 CHAP/CTOC); `sound_id` → sound-pack resolution (placeholder
  chime is the current fallback); confirm the `separate`-file-per-article path
  end-to-end; surface per-file chapter count in results.
- **Keyboard-activation accessibility audit** (systemic; surfaced by #709, which
  is fixed): a `wx.ListBox` emits no item-activated event, so any list binding only
  `EVT_LISTBOX_DCLICK` is keyboard-inaccessible. Audit/fix `ssh_dialogs.py`,
  `copy_tray_dialog.py`, `prompt_library_dialog.py`, `remote_sites_dialog.py`,
  `main_frame_copy_tray.py`, `skill_library_dialog.py`, `publishing_tools.py`
  (no key handler), and decide Space activation for the `EVT_LIST_ITEM_ACTIVATED`
  ListCtrls (`info_pages.py`, `github_dialogs.py`, `sticky_notes.py`,
  `ai_thesaurus_dialog.py`, `abbreviation_manager_dialog.py`). Recommended: a
  shared `apply_listbox_activation(listbox, on_activate)` helper + a gate so new
  `EVT_LISTBOX_DCLICK` bindings must pair with keyboard activation.
- **SSML batch-time handling:** per-file substitution accounting; a dry-run
  transform preview (show the normalized/pronounced/SSML text before running).
- **Extraction/quality:** richer `.docx` extraction (tables, headers/footers,
  footnotes, list ordering — today paragraph `<w:t>` only); wire `tts_chunk.py`
  into the batch/assembly path for very long sections; consider migrating
  `read_aloud.py` subprocess calls to `stability.safe_subprocess`.
- **Credits/upstream:** THIRD_PARTY credit for mutagen + the ChapterForge
  approach; offer ChapterForge the two fixes already in QUILL's `chapters.py`
  (non-contiguous gap chapters; ID3-tag clobbering); ElevenDesk research pass
  (see [`eleven-labs.md`](eleven-labs.md)).

**Open — dictation follow-ups:** a settings *panel* for the dictation knobs (plus
earcon volume / retention / visual recording indicator); Dictation History +
interactive startup-recovery prompt; a Dictation Review interface for
deferred/unsafe insertions; distinct locked-vs-hold earcons; one-time dictation
onboarding; and later phases (optional global Windows key hook, idle-silence
detection, spoken punctuation/commands).

**Open — BW consolidation backlog:** the broader provider matrix tiers and guided
onboarding tracked as the BW-1..10 / WATCH-8 planning markers (#515, #566–#577) —
folded here, not a separate per-ID stub set.

### 1.3 Agentic AI platform ⬜ (planned — PRD ready)

**Spec:** [`quill_end_to_end_agentic_ai_prd.md`](quill_end_to_end_agentic_ai_prd.md).

Unify QUILL's already-deep AI stack behind one provider-neutral, optional,
screen-reader-first platform whose front door is the **AI Hub**: one provider
truth, a Safe Editor Tool Gateway + Permission Broker, a real tool-calling agent
loop, a declarative agent catalog, an activity log, and an optional harness layer.
Supersedes the scattered AI issues O5/O5b/O6 (#507–#509), O7 Azure (#510),
O8/AI-19 Copilot SDK (#511/#523), O9/SHELL-2 OCR structuring (#512/#524), and
AI-11/12/18 (#579–#581). The **Accessibility Agents** from GLOW (AX-A..F,
#593–#598) become catalog agents here.

### 1.4 Accessibility tooling (from GLOW) ⬜

**Source:** `s:\code\glow` (`glowplan.md`).

- **Document Audit** — evaluate the current document against ACB Large-Print
  Guidelines, Microsoft Accessibility Checker rules, and WCAG 2.2 AA, returning a
  scored, navigable findings report. Lands as an in-QUILL audit surface (and an
  agent in §1.3).
- **GLOW family** — the seven GLOW capabilities (#528–#534) plus the WATCH-8 GLOW
  watch action (#566), re-homed on QUILL's invariants. Currently `locked_off`
  (hidden); decide for 1.0: finish + un-gate, or keep hidden.
- **Out of scope:** GLOW's server/Keycloak/Office-add-in/MCP-deployment surfaces
  stay in the GLOW product; QUILL takes the authoring-time checks.

### 1.5 Publishing & audiobook ◐

- **Shipped:** DAISY 2.02 text-only export (#251, `quill/io/daisy.py`).
- **ChapterForge integration** ⬜ — turn a folder of audio (or a document's
  sections) into a chaptered audiobook/podcast master; ties to DAISY and the
  BITS Whisperer stack.
- **Direct publishing (#140)** ⬜ — WordPress and other platforms; a long-term,
  likely-Quillin integration (external-API + auth surface), not core editor work.

### 1.6 Braille mode ✅ (Phases 3/4)

Proofing, validation, restore-your-place, and selection-aware back-translation
shipped (#238–#242, #246). The deferred Phases 3/4/6 backlog was retired to git
history (#600/#601 bookkeeping); remaining braille ideas live in the verbosity
braille channel.

### 1.7 Navigation & editor ◐

- **Shipped:** Quick Navigation enhancements incl. misspellings/search-hits nav
  types (#513; NAV-10 #578 folded in); structured Word view un-gated for everyday
  use (#514, the CSV-grid half stays gated as excluded table work);
  `main_frame_statusbar.py` / `StatusBarMixin` extraction (#521, GATE-11).
- **Open:** the FEAT-12..18 stubs (#582–#588) were content-free 2.0-deferred
  placeholders; if a real feature resurfaces it re-enters through the relevant
  workstream.

### 1.8 Platform & distribution ⬜

- Live installer smoke on Windows 10/11 (#506); macOS to shipping quality (#518);
  native RTF editing (#516); the Quillin Hub (#517); plugin capability + signing +
  marketplace (#519).
- **Deferred to 2.0** (tracker #680): the Windows 11 modern primary-menu
  `IExplorerCommand` pass (SHELL-3, #525) and the packaging/freeze evaluation
  (PKG-1 — Nuitka/PyInstaller hardening, #599).
- **Out of scope:** Linux/Unix (#520, #565, #589). Platform scope is Windows
  (primary) and macOS (supported).

### 1.9 Docs, tutorials & content ◐

One **Documentation & Tutorials** track: user-guide coverage, getting-started
tutorials, the podcast/walkthrough series, and content-quality follow-ups
(#535–#564, #505, #522). In-flight QA: **#526** live NVDA/JAWS/Narrator sign-off;
**#527** spell-check preload ✅ (resolved 2026-06-24). Long-horizon ecosystem
(#590) and collaboration (#592) ideas park here. Localization L10N-1 (#591)
already shipped (display-language switcher + translation workflow).

### 1.10 Structured List Studio ✅ (shipped; SR pass remains)

**Spec:** [`quill-structured-list-studio-prd.md`](quill-structured-list-studio-prd.md) (§30 Implementation Status).

Build/edit lists by concept (F2): Bulleted/Numbered/Checklist/Definition,
nested-list editing, multiple terms & definitions per entry, in-place editing of
the list under the caret, type-switch conversion with information-loss
confirmation, import-with-preview, reparse-and-validate before commit, and a
Settings/preset surface that persists app-wide. **Open:** a formal live
**screen-reader pass** (manual) and the low-value profile-prompt / intermediate
config scopes.

### 1.11 Native accessible Table Studio ⬜ (not started)

**Spec:** [`quill-native-accessible-table-studio-plan.md`](quill-native-accessible-table-studio-plan.md).
The accessible table-authoring surface (and the CSV-grid half of #514) — excluded
from the current green bar; planned design only.

---

## 2. Phase outcomes (what changes for the user)

Written from the user's chair, screen-reader experience first. Status: ✅ shipped ·
⬜ planned.

### Phase 1 — Trust, braille, and private speech ✅

Text round-trip fidelity (#648/#649) and accessible AI-Hub tab names (#643/#646);
the **braille** proofing/validation/restore-place/back-translation suite
(#238–#242, #246); **dictation honesty + private offline transcription** with the
model manager, captions, dictate-at-cursor, and speaker attribution (#617 S0–S4);
and **DAISY 2.02 talking-book export** (#251). *The editor stops doing invisible
things to your document; braille transcribers get a real spoken proofing workflow;
private offline transcription/dictation are first-class; talking-book output ships.*

### Phase 2 — Say exactly as much as I want (Verbosity) ✅

A real verbosity system: choose a profile (Beginner/Normal/Expert/Quiet) and QUILL
adjusts how much it announces per action; **Quiet Mode** and **Meeting Mode** by
keystroke with a Quiet Undo; announcements stop repeating; ask "Where am I?" /
"What changed?" on demand. *The single biggest comfort lever for daily
screen-reader use.* Remaining: the polish backlog (§1.1).

### Phase 2.5 — Documents into audio ✅

Batch Document-to-Speech with chaptered MP3/M4B audiobooks, pronunciation
dictionaries, text cleanup, and the SSML Builder (§1.2). *Convert a whole folder to
speech and control exactly how it sounds.*

### Phase 3 — An AI that helps without taking over ⬜

One coherent AI Hub; agents that read your selection and propose edits you preview
and undo in one step — never silent changes (§1.3). *Powerful help that stays
reviewable, undoable, and spoken.*

### Phase 4 — Move faster + publish further ⬜

Quick Navigation and structured Word/CSV views ungated (§1.7); broader publishing,
e.g. direct publishing to external platforms (#140); GLOW family improvements
(§1.4). *Faster keyboard navigation and accessible publishing.*

### Phase 5 — Solid on Windows and macOS ⬜

Verified installer behavior on Windows 10/11, shipping-quality **macOS**, native
RTF editing, the Quillin hub (§1.8); better docs/tutorials (§1.9). Platform scope:
Windows (primary) and macOS (supported); Linux/Unix out of scope.

---

## 3. Release gap list (path to green)

The prioritized list of what stands between QUILL and a **green, release-ready
state**. Two senses of "green": **(A) tooling green** — CI, tests, lint, types,
gates; **(B) release-ready** — no known-but-unverified defects, shipped features
complete/polished. Excluded per direction: the AI & Agentic workstream (§1.3), all
**table** work (§1.11 + the CSV-grid half of #514), 2.0-deferred items, and Linux.

### Tier 0 — Do first

1. **Commit and push the in-flight working tree** so `main` CI is green and the
   tree is clean (regenerate changed docs' HTML/EPUB, run
   `scripts/check_docs_artifacts.py`).
2. **Confirm all CI gates green** on the latest `main`: PR CI, Security CI (scoped
   mypy), Accessibility CI, Docs artifacts.

### Tier 1 — Release-blocking verification (B-green): "fixed" but unconfirmed

3. **Live screen-reader sign-off — #526.** Walk the batch of accessibility fixes
   marked *"Fixed; needs live NVDA/JAWS/Narrator confirmation"* (notebook tab-group
   names, snake_case names, label association, initial focus, the Tab keyboard-trap
   class, focus-to-bad-field) with JAWS, NVDA, and Narrator. **Highest single item.**
4. **Live installer smoke on Windows 10/11 — #506.** A packaged build installs,
   launches, and the first-run wizard runs on clean Win10 and Win11.
5. **Packaged-build validation of the optional speech engines** (Faster Whisper
   install path, Vosk reachability) on the real installer, not just from source.

### Tier 2 — Shipped features with rough edges

6. **Structured List Studio** — the formal live screen-reader pass (code-complete;
   §1.10).
7. **Dictation follow-ups** — the settings panel and the History/Review surfaces
   (§1.2).
8. **Watch Folder queue — live repro** (live-test #10): when `core.watch_folder` is
   enabled the monitor "feels empty"; needs an interactive repro to confirm the
   live queue populates, or a fix.
9. **Snapshots vs Versions** (live-test #12): the notebook set was renamed to
   **"Versions"** (code half done); the empty-submenu render still needs a live
   repro.

### Tier 3 — Polish & navigation (A-green comfort)

10. **Verbosity polish backlog** (§1.1) — land the high-value knobs, fold-or-defer
    the rest so the range can close.

### Resolved this cycle (kept here for the record)

- ✅ Spell-check preload (#527), structured Word view un-gate (#514), status-bar
  extraction (#521), Quick Nav (#513), model-manager installable-engine
  discoverability, `# dialog_button_contract: exempt` ruff respelling, and the
  `quill/core/spelling/announcements.py` wx-in-core removal — all 2026-06-24.

---

## 4. Open-issue ledger (by workstream)

Live status mirrors the GitHub tracker; only real, actionable work stays open.
Counts collapsed dramatically in the 2026-06-21 consolidation (232 → ~42 open) by
closing the 100 verbosity addenda (→ `verbosity-system.md` backlog), the AI
placeholders (→ §1.3), the Tier-6 doc stubs (→ §1.9), content-free FEAT stubs, the
done localization item, Linux (out of scope), and meta/archive placeholders.

| Workstream | Open work |
| --- | --- |
| Verbosity (§1.1) | Polish backlog #405–#504 (in `verbosity-system.md`). Engine + UI #271/#361–#404 shipped. |
| Speech & Dictation (§1.2) | Batch-speech follow-ups (project-profile wiring, M4B atoms, sound_id, separate mode, SSML batch handling, richer docx, keyboard-activation audit); dictation follow-ups; BW backlog #515, #566–#577. #617/#663 shipped. |
| Agentic AI (§1.3) | #507–#512, #523/#524, #579–#581; Accessibility Agents #593–#598. |
| GLOW family (§1.4) | #528–#534, #566 (locked_off; decide for 1.0). |
| Publishing (§1.5) | #140 WordPress; ChapterForge integration. #251 DAISY shipped. |
| Navigation & editor (§1.7) | #582–#588 (content-free 2.0 stubs). #513/#514/#521/#578 shipped. |
| Platform & distribution (§1.8) | #506, #516, #517, #518, #519; #525/#599 deferred to 2.0 (#680). |
| Docs & content (§1.9) | #526 SR sign-off; #535–#564, #505, #522, #590, #592. #527 shipped. |
| List Studio (§1.10) | Manual SR pass + minor scopes (`quill-structured-list-studio-prd.md`). |
| Table Studio (§1.11) | Whole feature (`quill-native-accessible-table-studio-plan.md`). |

### Out of scope (closed won't-do)

| # | Title | Reason |
| ---: | --- | --- |
| 520 | O17 — Linux platform layer | Linux/Unix is not a shipping target |
| 565 | Tier-6 LINUX-2 | Linux/Unix out of scope |
| 589 | LINUX-1 spike | Linux/Unix out of scope |

---

## 5. Source repos for the consolidations

These external repos are the design source for the integrations above; QUILL takes
the durable, accessibility-first value and re-homes it on QUILL's invariants.

- **BITS Whisperer:** `s:\code\bw` (transcription/speech; brand retained).
- **GLOW:** `s:\code\glow` (`glowplan.md`; accessibility audit + agents).
- **ChapterForge:** `c:\code\forum` (audio → chaptered audiobook/podcast).
