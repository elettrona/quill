# QUILL 1.0 — Meet You Where You Are

### The screen-reader-first writing studio, built by the people who depend on it. This is the public beta (build 0.8.0 Beta 1) carrying the complete QUILL 1.0 feature set.

*From Community Access. Free. Optional by design. Private by default. Yours to make quiet.*

> "I started QUILL, but the community is lifting it to levels I could never
> reach alone. This release is about meeting people where they are, then giving
> them a path to grow."
> — Jeff Bishop

---

## The announcement

For years, blind and low-vision writers have been asked to choose. Choose a
plain editor your screen reader can read but that does nothing for you. Choose a
powerful editor that does everything except work with your screen reader. Choose
one tool to transcribe, another to proofread, another to make an audiobook,
another to check a braille file — and choose, every single day, to fight software
that was never built with you in mind.

QUILL 1.0 is the end of that bargain.

QUILL — **Quality, Usable, Inclusive, Lightweight, Literate** — is a complete
writing studio that puts the screen-reader user first. Not as an accessibility
checkbox bolted on at the end, but as the design center everything else is built
around. It writes, edits, and saves like a fast plain editor on day one. Then,
only when you want them, it opens up an enormous range of capabilities — private
on-device speech, document-to-audiobook production, braille proofreading,
talking-book export, guided proofing, multilingual narration, and a whole
writer's toolkit — every one of them optional, every one of them spoken, every
one of them keyboard-first.

This document is the QUILL 1.0 story and its full feature set, and you can use all
of it today. This public beta — versioned **0.8.0 Beta 1** — is the 1.0 feature
set in your hands and the community's hands, ahead of the 1.0 stamp. The only
things between here and 1.0 are live screen-reader sign-off and installer
verification on real machines: the work that only the community and the keyboard
can finish.

---

## What came before

QUILL did not start as one app. It started as a family of focused tools.

Across the accessibility world, small teams built tools that each did one hard
thing well. One turned recordings into text and documents into speech, privately,
on your own computer. **ChapterForge** assembled folders of audio into real,
chaptered audiobooks. And a family of writing utilities — sound packs, compare
mode, encoding repair, citation help, braille translation — grew up alongside
them, the work of Blind Information Technology Solutions and CSE Designs.

Each was good. But for the person using them, the seams showed. Separate
installers. Separate mental models. Separate places your work could live.
Transcribe in one app, paste into another, proof in a third, and hope the
formatting survived the trip. Every handoff was a place for a screen-reader user
to get lost.

QUILL 1.0 is the decision to stop shipping seams. We took what each of those tools
did best, held it to one uncompromising standard — does it launch cleanly, does it
speak clearly, does it work entirely from the keyboard, does it keep your work on
your machine — and re-homed the survivors inside one editor. We left behind, or
deferred to a later release, anything that could not yet meet the bar.

The result is a single, coherent home for writing the accessible way — and a
foundation deliberately built to keep growing.

---

## A community release, in the truest sense

The bigger story is not only what changed. It is **who helped change it**.

QUILL is community-built and community-shaped. People are testing with JAWS, NVDA,
and Narrator. People are contributing code. People are filing issues, describing
real-world workflows, stress-testing accessibility, challenging assumptions,
improving prompts, writing documentation, and cheering the work on when it gets
hard. All of it counts.

Some of that work has names on it. **Kelly Ford** contributed the Vision Prompt
Library that gives image description twelve evaluated styles. **Robert Danaraj**
contributed Math Equations, redesigned as a sandboxed Quillin. **Taylor Arndt**,
**Shane Popplestone**, **Michael Babcock**, and so many others have tested
builds, opened issues, and pushed QUILL to be better than any one person could
make it. The braille tools exist because of the screen-reader users and braille
proofreaders who filed the issues that drove them, and because of the maintainers
of liblouis and the Universal BRF Pack.

> "The future of QUILL is not one person deciding every feature. It is a community
> of people building the tools they wish existed, with accessibility baked into
> the foundation."
> — Jeff Bishop

To everyone who tried a build and told us where it hurt: **thank you.** This
release is yours.

---

## The promise behind every feature

Before the feature tour, the rules QUILL is built to. They are not marketing —
they govern every line below.

- **Optional.** QUILL launches, edits, and saves with everything below turned
  off. You do not have to enable Artificial Intelligence to use the speech
  engine, the proofreader, the braille tools, or anything else that runs locally.
- **Screen-reader-first.** QUILL speaks *alongside* your screen reader, never
  instead of it. It does not duplicate your typing echo, your speech rate, or your
  punctuation level. Every dialog focuses its heading first, every control has a
  real name, every result that matters is announced — and only what your screen
  reader would not already say.
- **On your machine.** Transcription, dictation, proofing, captions, braille, and
  audio export all run on-device by default. Nothing is uploaded unless you choose
  a cloud option, and even then QUILL shows the cost, asks first, routes the call
  through an audited network path, and never does it in Safe Mode.

> "A feature is not finished when it exists. It is finished when the person using
> it feels confident, respected, and in control."
> — Jeff Bishop

---

## Meet you where you are

QUILL does not force every user into the same cockpit. A first-time writer opens a
quiet editor and starts typing. A braille professional inspects page, line, and
cell with confidence. A developer moves through code by tokens. A reviewer
compares files without scanning a diff. A power user extends the editor with
Quillins. Everyone starts at the right level and grows from there.

A short startup wizard asks one question — *what kind of writing do you do?* — and
shows a plain-English, screen-reader-readable preview of exactly what you will get,
with no jargon and no list of what you will not get. Seven starting profiles, from
**Just a Text Editor** (QUILL at its quietest) through **Writer**, **Markdown and
Web Author**, **Accessibility Professional**, **Braille Professional**,
**AI-Powered Author**, and **Developer and Power User**, are a curated front door
to the full catalog. Press **Alt+Shift+P** anytime to switch, reading the same
"what you get" description before you commit. Menus, the Command Palette, Go to
Anything, the system tray, and even Preferences all adjust instantly — commands
for features you have not enabled simply do not appear. Cancel the wizard and you
land in the simplest possible editor, never an overwhelming wall of defaults.

> "Meeting people where they are means respecting beginners, professionals, power
> users, and explorers equally. QUILL should feel welcoming on day one and
> powerful on day one hundred."
> — Jeff Bishop

What follows is everything QUILL can do once you are ready for it.

---

## 1. Control what QUILL says — the Verbosity system

Most software has one volume of chattiness, and it is rarely yours. QUILL gives you
a dial, from full friendly context for every action down to near silence, without
ever fighting your screen reader.

- **Four profiles.** **Beginner** (full context), **Normal** (the informative
  default), **Expert** (routine confirmations suppressed, errors always spoken), or
  **Quiet** (speech and earcons off; braille and the status bar stay on). Switching
  is announced, so you hear the change.
- **Quiet Mode and Meeting Mode.** Quiet Mode drops QUILL to a whisper; Meeting
  Mode quiets it for a call or a shared room. Toggle either from the Command
  Palette, or assign your own keys in the Keymap Editor. The status bar keeps
  updating, a `[Q]` or `[M]` badge shows the mode, and an Undo Verbosity Change
  command reverts the last verbosity change.
- **Channels you control.** Speech, Braille, and Sound each toggle independently.
  The visual status bar is always on and cannot be disabled — you never lose the
  on-screen state of an action.
- **No floods.** QUILL collapses repeated announcements (holding a key at the end
  of a list no longer machine-guns the same phrase), and an optional announcement
  budget caps how many are spoken in a burst. Both affect only what is *spoken* —
  the status bar still shows everything.
- **Say it exactly your way.** Rewrite what each action announces with simple
  tokens like `{line}` and filters like `${ordinal:line}`, with live validation and
  a preview. Save wordings to a template library, import or export your whole setup
  as a file, or install a community **QUILL Verbosity Pack** — all data, never code.
- **Understand it.** A **Preview Lab** lets you hear a profile against everyday
  scenarios; an announcement **History** lets you replay, copy, or ask *"why did
  QUILL say that?"*; and **Safe Mode** instantly restores the built-in
  announcements if a custom setup ever misbehaves, without deleting your work.

## 2. Speak and listen, privately — offline speech

QUILL has a privacy-first speech engine that runs entirely on your computer, under
**Tools > Speech**. No AI account, no key, no provider. The engine ships in the
installer (the *offline speech engine (whisper.cpp)* component, included in a Full
install) — no separate download, no PATH editing. Pick a model from **Manage Speech
Models** and you are ready.

**Manage models with confidence.** The dialog opens with a read of your machine
(RAM, whether a GPU was found), shows roughly how much memory each model needs,
flags models too big for your RAM, marks the best fit as *"Recommended for your
computer,"* and warns when a large model has no GPU behind it. Downloads run in the
background with a real, cancelable percentage and a low-disk warning. The models
are open-source and **MIT-licensed** — no Hugging Face account, no license to click
through, no gated files — and every download is checksum-pinned so a silent
re-upload can never swap a model underneath you.

**Transcribe audio and video, on-device.** Turn a recording into text without
uploading a byte. Output as plain text, Markdown, or HTML; it opens as an editable
draft while QUILL works in the background. With the speaker-detection model
installed, transcripts label who is speaking when. QUILL accepts a wide range of
formats — MP3, M4A, AAC, FLAC, OGG, Opus, WMA, WAV, MP4, M4V, MOV, MKV, WebM, AVI —
and can fetch **ffmpeg** for you (**Tools > Speech > Download FFmpeg...**) so you
never have to prepare a WAV first.

**Captions.** **Generate Captions (Offline)** transcribes with timestamps and saves
**SRT** or **VTT** subtitles ready to ship.

**Transcribe a whole folder automatically.** Point a Watch Folder profile at a
directory, choose the offline **Transcribe audio** action, and every audio or
video file you drop in is transcribed on your machine and saved beside it — in
Text, SubRip, WebVTT, or Markdown. This automation never uploads, never uses a
cloud provider, and tells you where to get a model if none is installed.

**Cloud transcription, only if you ask.** Add one as an extension — QUILL bundles
three declarative Quillins: **OpenAI Whisper** (99+ languages), **Groq Whisper**
(very fast turnaround), and **ElevenLabs Scribe** (high accuracy with optional
speaker diarization). Audio is uploaded only when you explicitly transcribe a file
with that provider — never offline, never in Safe Mode, never by the folder
automation. The extension ships no code and never sees your audio or key; QUILL
performs the upload through its audited network path.

**Dictate into your document.** **Dictate (Offline)** lets you speak straight into
the editor — start, speak, stop, and QUILL inserts what you said as a single
undoable edit. Then the two fast, keyboard-only ways that need no dialog and no
focus change, on the same on-device engine:

- **Hold-to-Dictate — hold F9.** Press and hold, speak, release; QUILL inserts the
  transcription as one undoable edit. A tone marks start and stop (the stop tone
  plays only after the microphone closes, so it is never recorded).
- **Locked Dictation — Ctrl+F9.** Press once to start a hands-free session, again to
  finish. QUILL announces "Locked dictation on." **Ctrl+Shift+F9** pauses or
  resumes; **Alt+F9** speaks the current state without changing anything.
- **A dependable stop, always.** **Escape** stops and keeps your speech;
  **Shift+Escape** cancels and discards. Locked Dictation auto-stops after five
  minutes and preserves your audio if QUILL loses focus.
- **Safe by design.** Audio is saved to a recovery folder *before* transcription
  begins, so a crash or unplugged microphone never costs you your words — and a
  **History & Review** window lets you insert, copy, or discard any recovered
  recording, doubling as the startup-recovery prompt.
- **Remappable.** F9, Ctrl+F9, and the rest are defaults you can change in the
  Keymap Editor, with conflicts detected and explained.

**Run commands by voice.** **Voice Command (Offline)** drives QUILL hands-free —
say "save", "bold", "next heading", "word count", "command palette". Recognition is
on-device, and voice can invoke only a curated, safe set of commands, so a misheard
phrase can never trigger anything destructive. Off by default, always disabled in
Safe Mode.

**Choose your engine.** The bundled **whisper.cpp** needs nothing extra. On capable
machines, opt into **Faster Whisper** (higher-throughput, multilingual, uses your
GPU) or **Vosk** (very low-resource, CPU-only, ships in the installer for old or
constrained machines). All three run entirely on your computer.

## 3. Read aloud and turn documents into audio

Read Aloud now spans local and cloud voices, and QUILL can produce real audiobooks
from a folder of documents.

**More voices, local and cloud.** Local Read Aloud uses the Windows system voice
through **SAPI 5** directly, plus **DECtalk** (driven through its real synthesis
runtime), **eSpeak-NG**, **Piper**, and **Kokoro** — and every catalog voice ships
a short spoken preview so you can hear it before choosing. For cloud-grade
narration, **AI Voice** supports **OpenAI** (11 voices), **Google Gemini 2.5** (30
voices), and **ElevenLabs** (audiobook-grade export). QUILL shows an estimated cost
before any export, splits long text only on sentence boundaries so audio never
trails off mid-word, and adds a trailing pause so the last sentence is never
clipped.

**Documents to audio, in bulk.** **Batch Export to Speech Audio** points QUILL at a
folder, picks an engine, voice, and pace, and converts every document on a
cancelable background task — with include/exclude filters and a maximum file size.
Output as **WAV, MP3, M4A, M4B (audiobook), Opus, FLAC, or OGG**; stamp album,
author/narrator, genre, and year; and turn long documents into **chaptered audio
with real MP3 chapter markers** you can jump between in any podcast app, with a
natural page-turn transition cue and configurable pauses.

**Shape it.** Export one chaptered file or a separate file per article; combine
empty headings so you never hear hollow "chapter" announcements; **round-robin
voices** so each article is read by the next voice in a list you build; normalize
loudness to audiobook (ACX) level; and **dry-run** to write the exact spoken text
for proofreading before paying for any synthesis.

**Narrate in other languages.** Pick one or more languages and a voice for each,
and QUILL translates each document and narrates it — `<doc> (Spanish).mp3` beside
the original — for a whole folder or for just the open document (**Export to
Translated Speech Audio**). Translation uses any AI provider you have configured or
a local **LibreTranslate**; voices are local-first (eSpeak speaks nearly every
language offline) with premium multilingual cloud voices as the quality tier.
Pronunciation dictionaries can be scoped to a language, you see a **combined cost
estimate** before any metered cloud run, and a project remembers its language
targets.

**Robust by default.** If a voice fails to synthesize, QUILL remembers it and skips
it next time, so one broken voice never derails a batch. When an output already
exists, choose skip (cheap resume), overwrite, or rename. Mirror source folders or
flatten them, rename with a template, and turn on a manifest for a CSV/JSON
summary. A folder remembers its whole speech setup, so you configure a project once
and re-run it anytime.

**Teach QUILL how to say things.** **Manage Pronunciations** adds corrections —
names, brands, acronyms, technical terms — that apply everywhere speech happens,
batch and live, with a live preview. Dictionaries can be global or per-project, and
a starter dictionary ships with common terms covered. An optional **text cleanup**
pass fixes the typography that trips up engines (curly quotes, dashes, ellipses,
symbols, fractions, emoji) and speaks phone numbers, emails, and URLs clearly.

**Fine pronunciation and prosody.** A new **SSML Builder** composes emphasis,
pauses, say-as, phonemes, and prosody from accessible controls, and Read Aloud
plays that markup natively on SAPI 5 and eSpeak-NG, so the emphasis actually takes
effect instead of being read aloud.

**Build a full audiobook from a folder.** **Build Audiobook from Folder** combines a
folder of audio into a single chaptered **MP3** or **M4B** master (native chapter
atoms) with book tags and an auto-detected cover. Before building, rename, reorder,
and merge chapters; then one-click **Normalize to ACX** brings the master into the
loudness range audiobook platforms require, measured and reported. This is
ChapterForge, re-homed inside your editor.

## 4. Read and proof braille

Braille support is not a novelty bolted on — it is designed around the way braille
professionals actually work, and it never changes your braille file. Progress and
notes live in a small companion file beside it.

- **QUILL remembers your place.** Reopen a `.brf`, `.brl`, `.pef`, or `.ueb` file
  and your cursor returns to where you left off, announced precisely: "BRF file
  opened. 87 braille pages detected. Last position: braille page 12, line 14,
  cell 31."
- **Track proofreading.** Mark a page proofed or needs-review, add notes, hear a
  spoken progress summary, jump to pages that still need work, and export a
  plain-text proofing report.
- **Validate layout.** QUILL flags over-long lines or pages, missing page breaks,
  mixed line endings, stray non-braille characters, malformed page indicators,
  numbering gaps, inconsistent running heads, and Unicode-vs-NABCC mismatches —
  then steps you through each finding with spoken position and detail. It only
  reads your file.
- **Recover source text.** **Back-Translate (draft)** turns a selected passage (or
  the whole file) into draft text via the optional QUILL Braille Pack and liblouis,
  so you can check the source wording. Continuation pages such as `7a` are reported
  in full, not shortened to `7`.

> "Braille users deserve tools that understand braille workflows, not tools that
> merely tolerate braille files."
> — Jeff Bishop

## 5. Save accessible talking books — DAISY

**File > Export > DAISY Talking Book** saves your document as a **DAISY 2.02
text-only talking book** — the format read by DAISY software and by hardware
players like the Victor Reader Stream, Plextalk, and APH units. It exports what is
on screen (no need to save first), your headings become the player's navigation
points, and because it is a standard DAISY book you can open the folder later in a
tool like APH Book Wizard Producer to add recorded or synthesized audio.

## 6. Proof your work — guided F7 Spelling Review

Press **F7** and QUILL walks you through every misspelling in your document or your
selection, one at a time. No AI, no network, nothing uploaded — the same local
dictionary engine that powers as-you-type checking.

The heart of it is a read-only **Context field** that shows the misspelled word
highlighted inside its sentence, where focus lands automatically; arrow through it
character by character, move by word, copy — just like the editor, and **Alt+W**
brings you back to the word whenever you need it. The actions are **Change**,
**Change All** (capitalization preserved: `teh`→`the`, `Teh`→`The`, `TEH`→`THE`, as
one undo step), **Ignore Once**, **Ignore All**, **Add to Dictionary**, and **Undo
Last** — all by keyboard, all announced, with nothing double-read.

Tune everything under **Settings > Spelling Review**: announcement verbosity
(Concise / Balanced / Detailed), spell-the-word-aloud letter by letter with an
adjustable pause, sentence-or-paragraph context, and wrap-to-beginning. And
`Ctrl+F7` / `Ctrl+Shift+F7` jump to the next or previous misspelling right in the
editor without opening the dialog at all.

## 7. Write in any language — Document Language

QUILL now lets a document be edited *as* a language even when its filename says
otherwise — so a plain `.txt`, an unsaved buffer, or a pasted snippet can get real
HTML, Markdown, or code editing.

Set the language from the **Format > Document Language** submenu (or **Navigate >
Set Document Language...**), and Bold/Italic insert the right markup,
the heading/table/list/tag items light up, comment toggling uses that language's
syntax, and the outline, link insertion, and live preview all follow it. Recognized
languages include HTML, Markdown, CSS, Python, JavaScript, TypeScript, C, C++, C#,
PHP, Go, Rust, Kotlin, Shell, YAML, JSON, TOML, and SQL. It is an editing aid, not a
rename — setting HTML on a `.txt` reminds you to Save As. And **optional
auto-detection** (off by default) recognizes code you paste into a plain file, in
your choice of Hint, Suggest-and-announce, or Switch-automatically modes — cautious,
never guessing on prose, never overriding a real extension, and unlike editors that
switch silently, always keeping a screen-reader user informed.

## 8. Find your way faster — Quick Nav

**Go to Anything** (`QUILL key + G`) is one search panel for everything worth
jumping to: headings, links, lists, tables, block quotes, bookmarks, code blocks —
each with a live count and a type-ahead filter. It also lists your document's
**misspellings** and, when a search is active, the current query's **search hits**
as their own navigable types, so you can open one panel and jump straight to the
next misspelled word or the next match the same way you jump to a heading.

## 9. Build lists by concept — Structured List Studio (F2)

Press **F2** and build lists by working with plain concepts — item text, a checked
box, a term and its definition — while QUILL writes the correct Markdown or HTML for
you. You never type `-`, `1.`, `[ ]`, `<ul>`, or `<dl>` by hand. Four list types
(Bulleted, Numbered, Checklist, and Definition), live read-only source as you work,
full nesting with subtree moves, multiple terms and definitions, and convert/import
that warns before dropping structure. With text selected, F2 turns your selection
into a list; with nothing selected it starts a new one; inside an existing list it
loads that block back in to edit. Every control is keyboard-reachable and labelled,
and inserting the finished list is a single undo step.

## 10. The writer's toolkit you already had — now in one place

QUILL 1.0 also carries forward the toolkit that grew up across earlier releases —
the durable value of those separate apps and earlier betas, re-homed on QUILL's
invariants:

- **AI writing, on your terms.** An **AI Hub** (Provider, On-Device, Audio
  Services, Instructions, Advanced) keeps one provider truth across Anthropic
  Claude, OpenAI, Google Gemini, OpenRouter, and Ollama. **Ask Quill**, plus
  Rewrite, Summarize, Expand, Generate Table of Contents, Grammar Check, Document
  Q&A, and an **AI Thesaurus** (Ctrl+Alt+Shift+H) run on a background thread with a stop
  button and present results you **Insert**, **Replace**, **Copy**, or **Re-Run** —
  never a silent change. Per-task **Custom Instructions**, a **Vision Prompt
  Library** for image descriptions (contributed by Kelly Ford), and provider-aware
  prompt caching round it out. All optional, all off until you turn AI on.
- **Quillins — the extension platform.** Sandboxed, declarative extensions with
  validated manifests, live preference dialogs, document lifecycle events,
  status-bar cells, dependency declarations, network allowlists, and a capability-
  and-consent model that asks before a Quillin reads a file, writes a file, or
  reaches the network. Fourteen ship bundled — including **Math Equations** for
  LaTeX/MathML with MathJax preview (contributed by Robert Danaraj) and a
  **Node.js** word-count example proving Quillins can be written in JavaScript too.
  Third-party Quillins stay locked off until the publishing and review process is
  ready.
- **Sound packs.** A pluggable earcon engine with the synthesized **Ink** pack and
  four indentation-tone packs that play a pitched tone as the caret crosses indent
  levels — accessible feedback you can hear instead of read.
- **Compare mode, encoding tools, and text power tools.** Keyboard-first document
  **Compare Mode** (Ctrl+Alt+Shift+. for next difference, Ctrl+Alt+Shift+D to hear
  just what changed);
  **code-aware editing** with token movement; minimum-required-encoding analysis;
  OEM/ANSI and line-drawing repair; multi-replace, count-occurrences, advanced line
  numbering, and line statistics; **Quill Eraser** rule-based text hygiene;
  **citation help** (MLA, Chicago, APA); a non-AI **Table of Contents** and Markdown
  profiles; and **Emmet-style abbreviation expansion** for HTML and CSS.
- **Capture and organize.** Sticky Notes, Notebooks for long-form projects, Macros,
  workspace Snapshots, a 12-slot Copy Tray, snippets and the Snippet Gallery, typed
  abbreviations and smart triggers (Insert Automation), and optional remote files
  (FTP, SFTP, WebDAV, S3, GitHub).
- **Faithful files.** No stray byte-order mark under your cursor; exact CRLF and
  blank-line round-trips; **Save As Word (.docx)** through Pandoc with real Word
  styles; broad document intake (DOCX, EPUB, PPTX, PDF, OCR, CSV/TSV); and an
  opt-in, fully keyboard-friendly **Simple File Open dialog** for when the native
  picker gets in your way.

## 11. A smoother upgrade, a cleaner start, and a sturdier app

- **A smoother upgrade.** QUILL checks your saved settings and shortcuts at startup
  and carries forward everything that still works; an entry that points at a removed
  command, has an empty shortcut, or conflicts is quietly dropped for the current
  default — so a feature never silently appears "broken." Familiar bindings that
  drifted during development are repaired automatically.
- **A cleaner start.** Installed and portable copies both launch through
  `quill.exe`, a real windowed launcher — **no console window flashing** — with an
  honest identity ("QUILL for All", the real version, "Community Access" as
  publisher) so your screen reader's "what window / what version" commands say
  something useful instead of "Python." A first-run page lets you choose where QUILL
  stores your data, and a folder counts as portable only with real evidence on disk,
  so a stray setting can never redirect where your work lives.
- **Accessibility and platform refinements.** Setup pages focus their heading first
  with readable explanatory text; single letters like `R` and `S` type themselves
  instead of being mistaken for shortcuts; Tab indent is spoken under JAWS and NVDA
  again; F6 reaches the document tab bar; and macOS / VoiceOver identifies the
  editor as a real editable area, with proper Cmd+Q, word movement, and a
  recognized Help menu.
- **Honest, redacted crash reporting.** When an unexpected error closes QUILL, a
  crash-report dialog shows a **redacted preview** of exactly what would be sent —
  recent commands, document name and encoding, platform and screen-reader info, and
  the last traceback frames, with personal data and credential-shaped strings
  scrubbed first. You choose Send, Copy, or Don't Send (the default). A local copy
  is always saved. Reliability is part of accessibility: your work should never be
  silently lost.

---

## How QUILL meets you where you are

Read those eleven sections again and notice what is *not* there: no demand. QUILL
does not require you to learn a new way to write. It does not make you turn on AI.
It does not move your files to a server. It does not talk over your screen reader.

A student writing a paper meets QUILL as a fast, faithful editor with citations and
a table of contents. A podcaster meets it as a transcription and captioning studio.
An author meets it as an audiobook pipeline. A braille transcriber meets it as a
proofreading workflow that never touches the source. A blind developer meets it as
a code-aware editor that finally announces the indent. A person who just wants
quiet meets it as an editor that will, genuinely, be quiet.

That is the whole idea. One studio, many doors, and you choose which to open.

> "Delight is not about fireworks. Delight is when the editor does the small helpful
> thing at exactly the right moment and then gets out of your way."
> — Jeff Bishop

---

## What comes next — QUILL 1.1 and beyond

QUILL 1.0 is a foundation, and it was built to grow. The roadmap is tracked openly,
and every item here is optional and screen-reader-first by the same rules as
everything above.

- **An AI that helps without taking over.** A unified, provider-neutral **Agentic
  AI Hub** with a safe editor-tool gateway and a permission broker: agents that read
  your selection and propose edits you preview and undo in one step — never silent
  changes. Accessibility-audit agents join the catalog here.
- **Move faster and publish further.** A native, accessible **Table Studio** and
  structured Word/CSV views; **direct publishing** to external platforms; and a
  document-audit family (ACB large-print guidelines, the Microsoft Accessibility
  Checker, WCAG 2.2 AA) brought in as authoring-time checks.
- **Speak even more freely.** Dictation's later phases — an optional global Windows
  dictation hotkey, idle-silence auto-stop, and spoken punctuation and commands —
  plus **ElevenLabs** live streaming Read Aloud and voice management beyond today's
  export.
- **Solid everywhere you work.** Verified installer behavior on Windows 10 and 11,
  shipping-quality **macOS**, native RTF editing, and a **Quillin Hub** with plugin
  signing and a marketplace so the community can publish the tools it wishes existed.
- **More ways in.** Native Google Docs round-tripping, a deeper getting-started
  tutorial and walkthrough series, and a growing library of community Verbosity
  Packs, sound packs, and Quillins.

Some of these are close; some are 2.0. All are built on the same promises, so
nothing new will ever cost you the quiet, the privacy, or the control you have
today.

---

## Availability

QUILL is **free**. This public beta carries the complete 1.0 feature set:

- **Windows installer** — per-user, no admin required, with every speech engine
  (whisper.cpp, eSpeak-NG, DECtalk, Piper), Pandoc, and the braille pack bundled.
  Choose components during setup; a Full install includes everything.
- **Portable edition** — the same fully-bundled studio in a folder you can carry on
  a drive, with an empty `data/` folder so it works from the first launch.

The road to the **1.0** stamp is short and deliberate: live screen-reader sign-off
across JAWS, NVDA, and Narrator, and installer verification on clean Windows 10 and
11 machines. That is work the community does best, which is why the feature set is
in your hands now.

## How to help shape 1.0

The fastest way to influence QUILL 1.0 is to use this beta for real work — write
with it, review with it, customize it, push it. Then tell us what works, what
breaks, and what should be better:

1. Install or start QUILL.
2. Let it carry forward your compatible settings at startup.
3. Keep working with your familiar files and preferences.
4. Send feedback from **Help > Report a Bug** — bugs, accessibility issues,
   confusing workflows, and feature requests all land where the team can act on
   them.

Optional extras, only if you want them: the offline speech engine ships in the
installer (or drop it into `tools\speech\whispercpp` in a portable copy), then
download a model from **Manage Speech Models**; **ffmpeg** (one click from
**Tools > Speech > Download FFmpeg...**) lets you transcribe formats beyond WAV; and
**Faster Whisper** adds a GPU engine on capable machines. None are required to
launch, edit, or save.

---

## About QUILL

QUILL — **Quality, Usable, Inclusive, Lightweight, Literate** — is a
screen-reader-first writing studio from **Community Access**, built on the
conviction that accessibility is not a feature you add at the end but the center
you design around. It consolidates the durable value of a family of accessibility
tools — including a private, on-device speech suite and the **ChapterForge**
audiobook workflow — into one optional-by-design, private-by-default, keyboard-first
environment. QUILL owns the editor, the focus, the undo, and the announcements; AI
and every external integration are optional and off by default. Platform scope is
Windows (primary) and macOS (supported).

QUILL is community-built and community-shaped. With QUILL, accessibility is not the
finish line. Accessibility is where we begin.

*Learn more at https://quillforall.org.*
