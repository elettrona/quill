# QUILL Program — User-Experience Outcomes by Phase

> Companion to [`program-tracker.md`](program-tracker.md). The tracker says *what*
> ships and *when*; this document says *what changes for the person using QUILL*.
> Every outcome is written from the user's chair, in plain language, with the
> screen-reader experience first. Each phase lists the concrete moments a user
> will notice, the accessibility wins, and the issues behind them.

Legend: ✅ shipped · 🚧 in progress · ⬜ planned.

> **2026-06-21 reorganisation:** the earlier "waves" were consolidated. The
> completed work — trust-the-basics, the braille suite, dictation honesty, the
> whole offline speech stack, and DAISY export (formerly Waves 0, 1, 3, and 4) —
> is now **Phase 1, complete**. Everything still planned moved forward by one:
> Verbosity & Polish is Phase 2, the AI Hub is Phase 3, faster navigation and
> publishing is Phase 4, and platform polish is Phase 5.

---

## Phase 1 — Trust, braille, and private speech ✅ (complete)

**The promise:** "When I open and save a file I get it back exactly; QUILL tells
me the truth about what it can do; and I can dictate or transcribe entirely on
my own computer."

This phase folds together everything that has shipped (formerly Waves 0, 1, 3,
and 4). With DAISY export (#251) landed, **Phase 1 is complete.**

### Trust the basics (was Wave 0) ✅

- A text file you saved with a byte order mark opens cleanly. No stray invisible
  character sits before your first word, so your screen reader doesn't read a
  phantom symbol and your cursor starts in the right place. (#648)
- Open a Windows text file and save it — it stays a Windows text file. Your line
  endings are preserved, and blank lines you deliberately left in are still there
  (no silent "tidying" that collapses three blank lines into two, and no Markdown
  characters getting mangled). (#649)
- In the AI Hub, VoiceOver now announces the settings tabs as a named group
  instead of an unlabeled cluster, so you can tell where you are. (#643/#646)

### Braille proofing, validation, and back-translation (was Wave 1) ✅

- Reopen a braille (BRF) file and QUILL puts your cursor back where you left off
  and tells you: "BRF file opened. 87 braille pages detected. Last position:
  braille page 12, line 14, cell 31." No more hunting for your place. (#239)
- A new **Braille → Proofing** menu lets you mark a braille page proofed or needing
  review, add a note, hear a progress summary, list proofed or flagged pages, and
  export a plain-text proofing report — all by keyboard, saved beside the file and
  never altering the braille. (#240, built on the #238 sidecar)
- A braille **validator** flags likely formatting problems, with an accessible
  **Warnings List** you can step through entirely by keyboard. (#241/#242)
- **Back-translation** (braille → text) is selection-aware, so you can recover the
  source text of a passage. (#246)

### Dictation honesty + private offline transcription (was Wave 3) ✅

- The dictation settings no longer promise a local engine that never actually
  ran; QUILL states plainly when it uses Windows dictation, and the offline
  engine groundwork is in. (#617 S0)
- Manage Speech Models downloads a local model (recommends Small), then
  **transcribe an audio or video file** fully offline, choosing **plain text,
  Markdown, or HTML**.
- The whisper.cpp engine is a **built-in installer component** (no separate install
  or PATH editing), and the result opens as an editable draft with background,
  non-chatty progress. (#617 S1–S2)
- **Speaker attribution** ("who is speaking when") with the Small English with
  speaker-detection model.

### Speak into the page + captions (was Wave 4) ✅

- **Dictate at the cursor** (QUILL Key + Shift+D): start, speak, stop — text drops
  in where you are as one undoable step, with distinct start/stop earcons, a
  status-bar indicator, and a chosen microphone. (#617 S3)
- **Captions**: turn a recording into SRT or VTT subtitles you can review and save.

### DAISY talking-book export (#251) ✅

- **Export to a DAISY 2.02 text-only talking book** — File > Export > DAISY
  Talking Book turns the document into a DAISY book folder (`ncc.html`,
  `content.html`, `book.smil`) that opens in DAISY software readers and on
  hardware players such as the Victor Reader Stream, Plextalk, and APH units, or
  in APH Book Wizard Producer to add TTS audio. Your headings become player
  navigation points; inline markup is flattened to clean readable text.

Accessibility win: the editor stops doing invisible things to your document,
braille transcribers get a real proofing-and-validation workflow with spoken
progress, dictation stops over-promising, private offline transcription and
dictation are first-class and keyboard-clear, and DAISY export brings accessible
talking-book output.

---

## Phase 2 — Say exactly as much as I want (Verbosity & Polish) ⬜ NEXT

**The promise:** "QUILL speaks at my level — not too much, not too little — and the
small touches feel crafted."

This phase delivers the **whole verbosity workstream in one go** — the core engine
*and* the polish set (formerly a separate "long tail" wave), because it is all one
system and splitting it added no safety.

What you notice:
- A real verbosity system: choose a profile (Beginner, Normal, Expert, Quiet) and
  QUILL adjusts how much it announces for each kind of action.
- **Quiet Mode** and **Meeting Mode** you can toggle with a keystroke when you need
  silence fast, plus a Quiet Undo.
- Announcements stop repeating themselves; you can ask "Where am I?" or "What
  changed?" on demand instead of being told constantly. (#271, #361–#366, §5–§46)
- The polish layer: announcement budgets, repetition collapse, typing-echo
  controls, per-category detail levels, destructive-action and undo-available cues,
  and the rest of the high-value knobs — with speculative extras folded in or set
  aside deliberately. (#405–#504)

Accessibility win: the single biggest comfort lever for daily screen-reader use —
full control over the firehose of speech, plus a thousand small reductions in noise.

---

## Phase 3 — An AI that helps without taking over ⬜

**The promise:** "I choose the AI, pick an agent, and I always see and control
what changes."

What you notice:
- One coherent AI Hub instead of several overlapping dialogs, with per-message
  action buttons in Ask QUILL and a single, unified provider setup. (#507–#509)
- Agents that read your selection and propose edits you preview and undo in one
  step — never silent changes. (agentic-AI plan)

Accessibility win: powerful help that stays reviewable, undoable, and spoken.

---

## Phase 4 — Move faster + publish further ⬜

**The promise:** "Getting around and getting my work out is quicker."

What you notice:
- Quick Navigation enhancements and structured Word / CSV views ungated for
  everyday use. (#513/#514)
- Broader publishing options, e.g. direct publishing to external platforms. (#140)
  (DAISY export #251 lives in Phase 1.)
- GLOW family improvements across the experience. (#528–#534)

Accessibility win: faster keyboard navigation and accessible publishing formats.

---

## Phase 5 — Solid on Windows and macOS ⬜

**The promise:** "QUILL installs cleanly and works the same on Windows and macOS."

What you notice:
- Verified installer behavior on Windows 10/11, progress toward shipping-quality
  **macOS**, native RTF editing, and a Quillin (extension) hub. (#506, #516–#519)
- Better docs, tutorials, and learning material. (#505, #535–#564)

Platform scope: Windows (primary) and macOS (supported). **Linux/Unix is out of
scope** and not a shipping target.

Accessibility win: a dependable, well-documented product on its supported platforms.

---

## How to read progress

- Status and counts live in [`program-tracker.md`](program-tracker.md).
- Each phase's user-facing outcomes are echoed into the **release notes** as the
  work ships, the **user guide** when behavior changes, and the **PRD** /
  workstream specs for design detail — updated continuously, not at the end.
