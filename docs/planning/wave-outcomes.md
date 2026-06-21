# QUILL Program — User-Experience Outcomes by Wave

> Companion to [`program-tracker.md`](program-tracker.md). The tracker says *what*
> ships and *when*; this document says *what changes for the person using QUILL*.
> Every outcome is written from the user's chair, in plain language, with the
> screen-reader experience first. Each wave lists the concrete moments a user
> will notice, the accessibility wins, and the issues behind them.

Legend: ✅ shipped · 🚧 in progress · ⬜ planned.

---

## Wave 0 — Trust the basics ✅

**The promise:** "When I open a file and save it, I get my file back — exactly."

What you notice:
- A text file you saved with a byte order mark opens cleanly. No stray invisible
  character sits before your first word, so your screen reader doesn't read a
  phantom symbol and your cursor starts in the right place. (#648)
- Open a Windows text file and save it — it stays a Windows text file. Your line
  endings are preserved, and blank lines you deliberately left in are still there
  (no silent "tidying" that collapses three blank lines into two, and no Markdown
  characters getting mangled). (#649)
- In the AI Hub, VoiceOver now announces the settings tabs as a named group
  instead of an unlabeled cluster, so you can tell where you are. (#643/#646)

Accessibility win: fewer surprises. The editor stops doing invisible things to
your document, and a settings dialog names itself.

---

## Wave 1 — Honest dictation + braille proofing 🚧

**The promise:** "QUILL tells me the truth about what it can do, and it remembers
where I was in my braille document."

What you notice:
- The dictation settings no longer promise a local engine that never actually
  ran. Today dictation uses Windows' own dictation; QUILL now says so plainly,
  and the groundwork for a real offline engine has begun. (#617 S0) ✅
- Reopen a braille (BRF) file and QUILL puts your cursor back where you left off
  and tells you: "BRF file opened. 87 braille pages detected. Last position:
  braille page 12, line 14, cell 31." No more hunting for your place. (#239) 🚧
- A new **Braille → Proofing** menu lets you mark a braille page proofed or needing
  review, add a note to a page, hear a progress summary ("9 pages proofed, 3 need
  review, about 10 percent complete"), list proofed or flagged pages, and export a
  plain-text proofing report — all by keyboard. Your progress is saved beside the
  file and never alters the braille itself. (#240, built on the #238 sidecar) 🚧

Accessibility win: braille transcribers get real proofing workflow support with
spoken progress, and dictation stops over-promising.

---

## Wave 2 — Say exactly as much as I want ⬜

**The promise:** "QUILL speaks at my level — not too much, not too little."

What you notice:
- A real verbosity system: choose a profile (Beginner, Normal, Expert, Quiet) and
  QUILL adjusts how much it announces for each kind of action.
- **Quiet Mode** and **Meeting Mode** you can toggle with a keystroke when you need
  silence fast, plus a Quiet Undo.
- Announcements stop repeating themselves, and you can ask "Where am I?" or "What
  changed?" on demand instead of being told constantly. (#271, #361–#366, with the
  §5–§46 design behind them)

Accessibility win: the single biggest comfort lever for daily screen-reader use —
control over the firehose of speech.

---

## Wave 3 — Dictate and transcribe, privately ⬜

**The promise:** "I press one key, speak, and my words appear — on my computer,
without sending audio anywhere."

What you notice:
- Pick a speech model once (a friendly, plain-language prompt recommends a small
  one), then **transcribe an audio or video file** into a new document, fully
  offline.
- Clear, non-chatty progress your screen reader can follow, the ability to cancel
  at any time, and a result you can read and edit immediately. (#617 S1–S2)

Accessibility win: private, offline transcription with an accessible model manager
— no cloud account, no jargon.

---

## Wave 4 — Catch braille errors + speak into the page ⬜

**The promise:** "QUILL helps me find problems and lets me dictate straight into
my document."

What you notice:
- A braille **validator** flags likely formatting problems, with an accessible
  Warnings List you can step through by keyboard. (#241/#242)
- **Dictate at the cursor**: start dictation, speak, and text drops in where you
  are, as one undoable step, with a spoken "inserted N words." (#617 S3)
- **Captions**: turn a recording into SRT or VTT subtitles you can review and save.

Accessibility win: proofing and dictation become first-class, keyboard-first, and
screen-reader-clear.

---

## Wave 5 — An AI that helps without taking over ⬜

**The promise:** "I choose the AI, pick an agent, and I always see and control
what changes."

What you notice:
- One coherent AI Hub instead of several overlapping dialogs, with per-message
  action buttons in Ask QUILL and a single, unified provider setup. (#507–#509)
- Agents that read your selection and propose edits you preview and undo in one
  step — never silent changes. (agentic-AI plan)

Accessibility win: powerful help that stays reviewable, undoable, and spoken.

---

## Wave 6 — Move faster + publish further ⬜

**The promise:** "Getting around and getting my work out is quicker."

What you notice:
- Quick Navigation enhancements and structured Word / CSV views ungated for
  everyday use. (#513/#514)
- Export to a **DAISY** talking book, and broader publishing options. (#251, #140)
- GLOW family improvements across the experience. (#528–#534)

Accessibility win: faster keyboard navigation and accessible publishing formats.

---

## Wave 7 — Solid on every machine ⬜

**The promise:** "QUILL installs cleanly and works the same wherever I run it."

What you notice:
- Verified installer behavior on Windows 10/11, progress toward shipping-quality
  macOS and Linux, native RTF editing, and a Quillin (extension) hub. (#506,
  #516–#520)
- Better docs, tutorials, and learning material. (#505, #535–#564)

Accessibility win: a dependable, well-documented product on more platforms.

---

## Wave 8 — Polish the long tail ⬜

**The promise:** "The little touches that make it feel crafted."

What you notice:
- The high-value verbosity refinements (announcement budgets, repetition collapse,
  typing-echo controls, destructive-action and undo-available cues, and more),
  with the speculative extras folded in or set aside deliberately. (#405–#504)

Accessibility win: a thousand small reductions in friction and noise.

---

## How to read progress

- Status and counts live in [`program-tracker.md`](program-tracker.md).
- Each wave's user-facing outcomes are echoed into the **release notes** as the
  wave ships, the **user guide** when behavior changes, and the **PRD** /
  workstream specs for design detail — updated continuously, not at the end.
