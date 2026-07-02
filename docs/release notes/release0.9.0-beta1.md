# QUILL 0.9.0 Beta 1 - Meet You Where You Are

### The screen-reader-first writing studio, built by the people who depend on it.

*From Community Access. Free. Optional by design. Private by default. Yours to make quiet.*

This is the narrative companion to the **"0.9.0 Beta 1"** section of `CHANGELOG.md`
(the canonical, append-as-you-go log). It tells the story of what changes in
0.9.0 Beta 1 on top of the 0.8.0 line - what each feature is, and, just as
important, **why it matters** for the way you actually work. This is the
feature-complete cut for 0.9.0 - the GLOW accessibility suite ships unlocked in this
beta - and focus from here is polish.

---

## The story of this release

0.8.0 made QUILL a serious writing and document studio. **0.9.0 makes it yours -
and makes it complete.**

Five threads run through this beta. First, a complete, **optional** AI suite that
stays silent until you invite it in. Second, a wave of **power-user editing tools**
in the tradition of the editors people still miss - Reveal Codes, classic-editor
commands, and bookmarks that finally remember where you were. Third, the
**production features** this project was always pointed at: the GLOW accessibility
suite, unlocked, and a document-rescue tool that turns scanned PDFs into real text
with free, on-device OCR - nothing uploaded, ever. Fourth, a teaching library to
match: six hands-on tutorials and a 36-episode audio course narrated by QUILL's own
neural voices. And fifth, a quieter, **lighter, more honest install**: a smaller
download, on-demand components you can fetch from one place, clearer announcements,
and a day of under-the-hood hardening documented further down, because reliability
work deserves release notes too.

Everything new is off, optional, or additive. Nothing here changes how your fingers
already work - it just gives them more to reach for when you want it.

---

## The AI suite - powerful, and entirely up to you

### It is off until you turn it on

The headline addition is a complete, screen-reader-first AI suite under one new
top-level **AI** menu. It works with the provider *you* choose - a private
**on-device** model (Ollama) or an account with **OpenAI, Anthropic (Claude),
Google Gemini, or OpenRouter** - and nothing leaves your machine without your
consent.
**Why it matters:** AI in QUILL is a tool you pick up, not a thing that happens to
you. Set it up once and every feature shares that one connection; never set it up
and QUILL is exactly the editor it always was.

### Set up in seconds - the AI Setup Wizard

A short wizard ("Set Up AI... - start here") offers one choice - on-device, an
account, or not now - with a one-step connect and a Test Connection check. Click any
AI action before setup and QUILL offers the wizard right there instead of failing. A
**Basic** mode keeps the menu small for newcomers.
**Why it matters:** no dead ends, no jargon wall. You are never punished for trying a
button before you have configured anything.

### Free AI for everyone - a path that meets you where you are

You never have to pay to use QUILL's AI. The wizard now leads with the best **free**
options and picks good defaults for you. **Most private:** run a model on your own
computer with Ollama - no account, works offline, and nothing you write ever leaves
your machine. **Best quality:** connect **OpenRouter** with your own free key and
QUILL preselects a strong free writing model for you. Every provider that needs a key
has a **Get API key** button that opens the right signup page in your browser, so
there is no hunting for where to sign up, and model choices say **Free** out loud
when they cost nothing. Both the wizard and the **AI Hub** now offer a real model
**dropdown** - pick a recommended model or list everything your account or device
offers, instead of typing an id from memory. Everyday writing help and the one-shot
agents (Rewrite, Summarize, Expand, Table of Contents) work well on free models, and
Ask Quill quietly simplifies its steps on a small model so it answers instead of
stalling.
**Why it matters:** flagship models are wonderful, but they should be an *option*,
not a toll gate. If you cannot afford one, QUILL still gives you real, useful AI -
and it is honest about the trade-offs: free cloud models can be slower and are
rate-limited to *your own* quota, so keep anything confidential on the private
on-device option.

### Ask Quill - one conversation that knows your document

A single, context-aware chat replaces the old scattered AI dialogs. Ask about your
text, have it draft or rewrite, and apply suggestions through a **reviewable change
preview** applied as one undo step.
**Why it matters:** nothing is ever silently rewritten. You see the change, you
accept or reject it, and one Undo puts everything back.

### The Listening Companion - recordings become finished documents

Transcribe an audio or video file (optionally translating to English or identifying
speakers), then turn the transcript into **Meeting Minutes, Action Items, an
Executive Summary, Interview or Study Notes, Q&A, a Follow-Up Email, Key Quotes, a
Decisions Log, or a clean draft** - from one context-aware list. Build your own with
the no-syntax **Action Builder**, or let a watch-folder do it automatically.
**Why it matters:** the gap between "I recorded it" and "I have the document" closes
to a couple of keystrokes.

### The AI Library - Prompts, Skills, and Agents in one place

A tabbed manager with a real promotion path: a **Prompt** graduates into a multi-step
**Skill**, and a Skill into a first-class **Agent** - all reviewable, all running
through the connection you set up once.
**Why it matters:** your reusable know-how grows with you instead of scattering
across dialogs.

### Everyday writing help, always reviewable

Rewrite, summarise, expand, continue, fix grammar, or generate a table of contents;
AI spell check and grammar-and-style check; translate a selection or document; the
AI Thesaurus; and Document Q&A. Read the selection or document aloud, or export it as
audio in a natural cloud voice, alongside QUILL's on-device speech.
**Why it matters:** every proposed change is an accessible accept/reject preview and
a single undo step - help you can trust, not magic you have to babysit.

---

## Rich formatting that stays out of your way

### Hidden codes, spoken on demand

Apply real document formatting - **bold, italic, underline, strikethrough,
super/subscript, font family and point size, colour and highlight**, plus paragraph
**alignment, line spacing, indent, and named styles** - without ever seeing markup
clutter. The buffer stays clean, fast, plain text; the formatting rides along as
invisible codes. Ask **"Describe formatting at cursor"** to *hear* exactly what is in
effect ("Arial, 14 point, centred, bold").
**Why it matters:** you get real formatting and a clean editing experience - you no
longer have to choose between the two.

### Keep your formatting in a plain-text file - Illuminations

A plain `.txt` cannot hold fonts or colours, so saving formatted text as plain text
used to lose them. Now QUILL can write an **Illumination**: a small companion file
(`yourfile.txt.illumination`) that stores the formatting beside the clean text. The
`.txt` stays genuinely plain everywhere else; reopening it *in QUILL* restores every
font, colour, and alignment exactly.
**Why it matters:** your text stays portable and plain, and your formatting still
survives - no lock-in, no surprise loss.

### Faithful round-trips

RTF and Word documents round-trip through the clean buffer and materialise back to
real formatting on export. **Word (.docx)**, **RTF**, and **HTML** carry font, size,
colour, highlight, and alignment; when a format genuinely cannot hold something,
QUILL tells you *before* you commit.
**Why it matters:** you hand documents back looking the way they came in, and you are
never silently stripped of work.

---

## Editing and accessibility - the power tools people missed

### Reveal Codes - see and hear every hidden code (Alt+F3)

The beloved WordPerfect feature, reimagined screen-reader-first. Press **Alt+F3** (or
**View > Reveal Codes**) to open a pane showing your document as a stream of bracketed
codes and text - `[Bold On]`, `[Font: Arial]`, `[Center]`, `[Tab]`, `[Hard Return]`,
`[No-Break Space]`. **F6** moves between the editor, the Reveal Codes pane, and the
status bar (**Shift+F6** back), and the two carets stay in sync. Every code is an
individually-announced, navigable item; jump from a `[Bold On]` to its matching
`[Bold Off]` and hear its reach. Choose a **Structured** list or a **Flowed** view,
with quiet / balanced / detailed verbosity.
**Why it matters:** nothing about your document is hidden from you. The clean editor
stays clean; the truth is one keystroke away.

### Bookmarks that remember - per document, across sessions

Named bookmarks now belong to the **specific file** you set them in and **persist
between sessions**, so reopening a document brings its jump points back. QUILL also
remembers your **last cursor position** in each saved document and returns you there
when you reopen it.
**Why it matters:** close a long document on Friday, reopen it Monday, and you are
right where you left off - with every named landmark intact. (Set Bookmark, Go To
Bookmark, List Bookmarks; List Bookmarks is on Alt+Shift+B.)

### Inline notes - sticky comments that stay with your content

Jot a private note about the current line or selection with **Alt+Shift+I**. The
note is **anchored to the text**, so it follows that content as you edit and comes
back when you reopen the document (per document, like bookmarks). **Alt+Shift+J** /
**Alt+Shift+G** move to the next / previous note (the cursor jumps to the noted text
and QUILL reads the note); **Alt+Shift+H** speaks the note at the cursor, and pressing
it again quickly opens it to view, edit, or delete.
**Why it matters:** the running commentary, queries, and reminders you keep while
drafting finally live *with the words they are about* - surviving edits and reloads -
instead of in a separate file you have to keep in sync. If the noted text is deleted,
the note is kept rather than silently lost.

### Three classic-editor power tools

In the WordPerfect Editor tradition, all unbound by default (assign keys in the
Keymap Editor):
- **Repeat Next Command** - set a count, and the next command runs that many times
  (down twenty lines, delete ten words, insert forty dashes) in one gesture.
- **Restore Deleted Text** - QUILL keeps the last three blocks removed by its
  structured delete commands; re-insert any of them at the cursor (distinct from Undo,
  which only reverts in place).
- **Describe Character at Cursor** - names the exact character under the caret (Unicode
  name, code point, category, and notes for invisibles), the screen-reader descendant
  of "Reveal Codes".
**Why it matters:** the precise, repeatable, eyes-free moves that long-time editor
users have been asking QUILL to bring forward.

### Re-read anything QUILL just said - the Spoken Echo

The last twenty announcements are kept and shown newest-first in a read-only dialog
you can arrow through, re-read, and copy (**Alt+Shift+E**). Double-pressing an
informational command opens the Echo instead of re-speaking.
**Why it matters:** speech disappears the instant it is spoken; now you can get it
back.

### A far richer Keyboard Manager

The Keymap Editor searches two ways from one box - type part of a command name to
filter, or type a shortcut to reverse-look-up exactly which command owns it. **Record
Keys** lets you press a combination instead of typing it; assigning a taken key names
the command that holds it and offers to reassign; **Run Diagnostics** audits the whole
keymap and heals duplicate, orphaned, or inert bindings.
**Why it matters:** customising shortcuts no longer means remembering exact syntax or
guessing whether a key is free.

### Quieter, calmer, and quicker to move

- **Hear how deep your indentation is** - Tab / Shift+Tab can speak "4 spaces",
  "1 tab", instead of just "Indented lines".
- **Quieter dialogs by default** - the spoken "Entered / Exited *name* dialog"
  cues are now **off by default**, because every supported screen reader already
  announces a dialog and reads its title on focus, so the extra cue was just
  noise. Want them back? **Preferences > Accessibility > Announce entering and
  leaving dialogs**. Existing users who never deliberately switched them on pick
  up the quieter default automatically on upgrade.
- **Jump straight to an open document** - **Alt+1**...**Alt+9** (and **Alt+0** for the
  tenth) go directly to that document instead of cycling.
- **Quieter Read Aloud** - the follow-along selection is now off by default, so only
  the Read Aloud voice is heard, not "...selected" over it.
**Why it matters:** less chatter, fewer keystrokes, more signal.

---

## Story Studio - organize a whole book

### The binder: your project, one keystroke away

**Tools > Story Studio...** opens a keyboard-navigable **binder** for a project
folder. Your **Manuscript** appears with its parts, chapters, and scenes taken
straight from the Markdown headings you already write, alongside groups for
**Characters, Places, Plot threads, Research, and Brainstorm**. Arrow through the
tree; press Enter on any item to open that file - a chapter opens at its heading,
an element opens its notes.
**Why it matters:** a novel is more than one long file. Story Studio gives a
blind writer the same "see the whole book at a glance" a sighted writer gets from
a corkboard - as a tree a screen reader reads naturally, with no visual board.

### Character sheets and plot threads - a form, not a syntax

Select an element and choose **Edit details...** to fill in a small, accessible
form: a character's **Role, Goal, Motivation, and Arc**; a plot thread's
**Status**; **tags**. Your answers are saved as tidy front matter at the top of
the element's file, so editing the form and editing the file are the same bytes.
Blank fields are dropped, and anything already in the file that Story Studio does
not recognise is kept untouched.
**Why it matters:** structure without a database and without learning any markup
 - and your notes stay in plain, portable text you own.

### Compile the manuscript, then export it your way

Press **Compile manuscript...** and Story Studio stitches every manuscript file
together, in order, into a new document. From there the ordinary **File >
Export** takes over - Markdown, HTML, Word, DAISY, and more - because the compiled
manuscript is just a document like any other.
**Why it matters:** the gap between "chapters in a folder" and "one finished file
to send" closes to a single keystroke, and you export it with tools you know.

### Nothing is locked in

A Story project is an ordinary **folder of plain-text files** plus one small
companion file that remembers the order and the element groupings. Delete the
companion and you still have every word. Story Studio is entirely optional and
additive: if you never open it, nothing about your editing changes.
**Why it matters:** your book is yours, in files any program can read, forever.

---

## Accessible Vault - linked notes, backlinks, and no picture required

### Type [[a link]], follow it by ear

Linked notes are simply a folder of plain-text notes that point at one another.
The usual way to see those connections is a visual graph of dots and lines: a
wall of pixels a screen reader cannot climb. QUILL keeps the linking and drops
the wall. **Tools > Vault > Open Vault...** points QUILL at a folder of notes; it
indexes them and announces "Vault *name*: 312 notes, 480 links." Type
`[[Note Title]]` anywhere, put your cursor on it, and **Follow Wikilink** opens
that note, at the exact heading or block if you linked one. Link to a note that
does not exist yet and QUILL offers to **create** it on the spot; link to a name
two notes share and QUILL **asks which**, never guesses.
**Why it matters:** note-to-note links, the connective tissue of a real knowledge
base, now work in QUILL, and they work the way a keyboard-and-speech user actually
moves.

### The graph, spoken: Backlinks

**Show Backlinks** answers "what links here?" as a list you can hear: "5 notes
link here," each entry read with the sentence its link sits in, Enter to open the
source right at that mention. That list *is* the graph view - and for a
screen-reader user it is far more useful than a picture ever was.
**Why it matters:** you traverse the web of your notes forwards (follow a link)
and backwards (open a backlink) entirely by keyboard and ear.

### Find any note, find any word

**Go to Note** is a jump box: start typing part of a title and the list narrows
as you go, QUILL speaking the count ("7 matches"); press Enter to open the closest
one. **Search Vault** goes wider - type a word or phrase and hear how many results
turned up, each read as its note, line number, and the sentence it appears in;
flip on **Regex** for patterns or **Whole word** to skip partial hits, and Enter
opens a result at its exact line.
**Why it matters:** in a folder of hundreds of notes, the thing you want is one
short phrase and one keypress away - no scrolling, no squinting.

### Tags that gather your notes

**Show Tags** is a spoken tag pane. Filter your `#tags` - each with a count of how
many notes wear it - open one, and hear the notes that carry it. Nested tags roll
up, so `#area` gathers everything under `#area/sub` too.
**Why it matters:** the same "show me everything about X" that sighted users get
from clicking a tag, delivered as a list you can hear and act on.

### Embeds: pull one note into another

Write `![[Other Note]]` (or `![[Note#Heading]]`, or `![[Note#^block]]`) and QUILL
can pull that content in. **Speak Embed at Cursor** reads what the embed points to
without touching your text; **Resolve Embed Inline** drops the real content in
place as a single change you can undo.
**Why it matters:** reuse a definition, a boilerplate, or a shared section across
notes - and hear exactly what it resolves to before you commit.

### Templates and a daily journal

**Insert Template** picks from a `Templates` folder in your vault, fills in
`{{date}}`, `{{time}}`, and `{{title}}`, asks you any `{{prompt:Question}}` it
finds - spoken, one at a time - and leaves your cursor exactly where you marked
`{{cursor}}`. **Open Today's Note** opens (or creates) today's dated note, and
**Previous / Next Daily Note** step through the days.
**Why it matters:** the friction of "start a new note the same way every time"
disappears, and a daily journal is one command away.

### Turn your vault into a website

**Export Vault as Website** writes a small, self-contained site: one accessible
page per note, your `[[links]]` turned into real links between the pages, your
`![[embeds]]` filled in, and an index page listing everything. It runs in the
background and tells you how many pages it wrote. If your vault folder is a Git
repository, **Sync Vault** commits, pulls, and pushes over your own remote - and
if the same note changed in two places, it lists the conflicts and stops rather
than overwriting a word.
**Why it matters:** your notes can leave the app as a shareable, navigable site,
and stay backed up and in sync across your machines - on infrastructure you own.

### Plain text, yours forever

A vault is an ordinary folder of Markdown files plus one small `.quill` cache you
can delete without losing a word. Links live as plain `[[text]]` in your files -
nothing hidden - so every note opens in any editor. It is entirely optional: never
open a vault and QUILL is the editor it always was.

---

## Learn QUILL by ear - The QUILL Cast and new tutorials

QUILL's documentation now teaches in three registers. The user guide remains
the full reference. A new **tutorials** collection (docs/tutorials) walks six
complete workflows hands-on - your first hour, keyboard mastery, rescuing a
scanned PDF, building an audiobook, starting a Vault, and shipping an
accessible document with GLOW.

And then there is **The QUILL Cast**: a full **36-episode, two-host audio
course** - about two and a quarter hours across seven parts - that leads a
brand-new user from the installer all the way to every feature family in the
product. Part one covers first steps (install, files, the command palette,
what QUILL says); the everyday-editor part makes you fast; then documents
and formats, files and automation, the speech suite, AI, and finally the
organization, production, and trust features - the Vault, Story Studio,
GLOW, braille production, and extensions. Every episode builds on the one
before it and ends with five minutes of hands-on homework.

The hosts, Liam and Jessica, are QUILL's own on-device **Kokoro** neural
voices - the product literally narrates its own curriculum, produced with
the same speech engine you can install from the Voice Picker. Every episode
ships with a full accessible transcript on the website, and an RSS feed lets
you subscribe in any podcast app.

**Why it matters:** some people learn by reading, some by doing, some by
listening on a walk. Now all three of them get a first-class path into QUILL
- and the audio path is proof-by-existence of what the speech suite can do.

---

## Import / Convert Document - rescue for locked-away documents

Everyone with a screen reader knows the feeling: someone hands you a PDF and
it turns out to be a photograph of a page. Nothing to read, nothing to search,
nothing to fix. This beta ships QUILL's answer - a supported document-rescue
tool with one rule: **free first, local first, and nothing is ever uploaded.**

### How it works

**File > Import > Import / Convert Document (OCR)...** takes almost anything -
Word, PowerPoint, Excel, HTML, EPUB, PDFs, images - and routes it through free,
on-device services:

1. **The free local converter runs first.** Born-digital files and PDFs with a
   real text layer convert instantly into clean, editable text. No account, no
   key, no cost.
2. **Scanned documents are detected, not dumped.** When a PDF comes back nearly
   empty, QUILL says what it found - "it looks scanned or image-based" - and
   *asks* whether to run free on-device OCR. You choose; QUILL never opens a
   blank result silently and never runs OCR behind your back.
3. **On-device OCR rescues the scan.** The local Tesseract engine reads each
   page on your own computer (CPU-only, works offline), keeps page boundaries
   as searchable markers, announces progress page by page, and - honestly -
   tells you when recognition confidence is low so you know to review the
   result rather than trust it blindly.

### A one-time, verified download

The OCR engine is not bundled; it is a free ~48 MB download from
**Tools > Reading & Dictation > Install Local OCR Engine (Tesseract)...**.
QUILL fetches the official installer from its own pinned release, verifies it
byte-for-byte, and opens it for you to complete - never a silent install. If
Tesseract is already on your machine, QUILL just finds it.

### Plain-language services page

**OCR and Conversion Services...** describes each service the way a person
would: what it does, what it is best at, whether it is local or cloud (both
shipped services are local), what it costs (nothing), and the engine's current
install status. A consent-gated cloud tier for the hardest documents is
planned - and when it comes, the free local services will still always run
first.

**Why it matters:** the documents most likely to be inaccessible - scans,
photocopies, image PDFs - are exactly the ones other tools quietly give up on.
QUILL turns them into text you can read, search, and edit, without sending
your mail, your medical letter, or your homework to anyone's cloud.

---

## GLOW - guided accessibility review and repair

GLOW (Guided Layout and Output Workflow) is QUILL's accessibility review system,
and with this beta it graduates from hidden preview to a shipping feature. The
idea is guided confidence, not a compliance dashboard: GLOW reviews what is in
front of you, explains each finding in plain language, and offers only safe,
deterministic fixes you can inspect before accepting.

### Audit what you can hear

**Tools > GLOW > Audit Current Document** reviews the whole file;
**Audit Selection / Paragraph** reviews just the block at your caret. Findings
open as a normal QUILL tab you can arrow through, search, or keep open beside
your document: heading levels that jump, links that just say "click here",
images without alt text, HTML missing its language, tables without header
cells, dense paragraphs that will be hard to listen to. Every finding names its
rule, its severity, and a plain-language suggestion.

### Fix without fear

**Fix Selection / Paragraph** cleans up the block in place and leaves the
result selected for review. **Fix Current Document** goes further: it opens the
repaired text as a *named preview tab* and immediately starts a compare session
against the original, so you accept the change knowing exactly what moved -
never a silent rewrite.

### Structured documents too

New with the unlock, **GLOW Audit File...** and **GLOW Fix File...** take on
the files that are usually hardest to check by ear: Word, PowerPoint, Excel,
PDF, and EPUB. The shared GLOW engine parses the document in the background
(the editor never freezes), and the audit comes back as a scored, graded report
with every finding listed. Fixing a file always writes a repaired copy beside
the original - `report.docx` becomes `report-accessible.docx` - and QUILL
confirms the destination before anything runs. Your source file is never
touched.

### Private by default, updated only on request

The everyday GLOW workflow runs entirely on your machine. The engine's optional
networked helpers (AI alt-text, PII redaction, language processing) are off
until you explicitly turn them on, per action. **Help > Check for GLOW
Updates...** fetches a newer engine only when you ask - the manifest is signed,
every wheel is checksum-verified, and a failed install rolls back to the
bundled engine.

**Why it matters:** accessibility review has mostly been visual dashboards and
sighted checklists. GLOW puts a guided, spoken, keyboard-first repair loop
inside the editor you already use - so the person most affected by an
inaccessible document is also the person best equipped to fix it.

---

## Braille - proofreading for pages that must emboss

A new **Braille > Repair** submenu brings NLS-style proofreading: **Read Layout
Metrics** (longest line and page against your cells-per-line / lines-per-page limits,
with width and depth warnings), **Go to Longest Line / Longest Page**, and **Remove
Trailing Spaces** (this line or the whole file), all honouring your existing braille
page settings. A new **Editor control type (braille)** choice lets braille displays
that show the first character of each line in cell two switch to a plain edit control.
**Why it matters:** the difference between "it looks fine on screen" and "it actually
embosses cleanly", found and fixed before you send it.

---

## A smaller, friendlier install

### Download only what you need

The base installer is smaller because the heavy, optional pieces now download on
demand - checksum-verified, with a cancelable progress bar, disabled in Safe Mode:
- The **offline speech engine** (whisper.cpp), **Kokoro** neural voices, and the
  classic **eSpeak NG** and **DECtalk** voices.
- The **Vosk** speech engine - a tiny, very-low-resource dictation and transcription
  engine for older or low-memory machines with no graphics card. Get it from **Tools >
  Speech > Download Vosk** or the Optional Components dialog below.
- **Spell-check dictionaries for other languages** - pick **Spanish** or **French**
  under **Tools > Spell Check Language** and QUILL fetches the dictionary the first
  time.
- And the audio-export helper, **FFmpeg**.

No speech engine is bundled in the installer any more - even the small default
downloads the first time you dictate - and some build-only data was dropped from the
runtime, so the base download is lighter than ever.

**One place to get them all: Help > Download Optional Components.** A single dialog
lists every optional download with **Installed** vs **Available to download** and its
size, so you never hunt through menus.
**Why it matters:** a faster first download and install, Windows' built-in voices
working immediately, and a clear, accessible touch point for everything else.
**Upgrading?** Any component a previous release bundled is kept and keeps working -
nothing to re-download.

### Runs light on modest, CPU-only machines

Two new settings under **Settings > Performance and Memory** let QUILL fit its full AI
and speech features onto machines with limited memory - never by turning anything off,
only by being careful with memory:
- **Unload idle models after** a few minutes frees an AI or speech model you have
  stopped using; the next time you need it, it simply reloads.
- **Low-resource mode** keeps only one model loaded at a time and prefers the smallest
  one that fits. On a machine with very little memory it turns on automatically and
  tells you once, out loud.

**Why it matters:** the whole feature set - dictation, read-aloud, and AI - stays usable
on an older, CPU-only laptop, because QUILL holds one model in memory at a time instead
of several. You trade a moment of reloading for a much smaller memory footprint.

### AI that fits your machine, and a way forward when you are offline

- When your computer can comfortably run a more accurate on-device model than the one
  you have chosen, the **AI model** dialog now says so - a one-step suggestion you can
  take or ignore. New installs still default to the smallest model that fits.
- If a cloud AI request cannot reach the internet and you have an on-device model
  installed, QUILL now tells you that you can switch to it and keep working offline. It
  never switches for you - your privacy choice stays yours.

### Export speech audio as MP3 and more

With FFmpeg present, Generate Speech Audio now saves as **MP3, M4A, M4B, OGG, Opus, or
FLAC** (WAV still works without it).

---

## A thank-you, and a place to experiment

### Golden Quills

**Help > About QUILL** has a new **Golden Quills** tab recognising the people who
support the project financially, in alphabetical order, with our heartfelt thanks. It
includes an optional **Donate** button.
**Why it matters:** QUILL is free and always will be - donating is completely optional
and never required. This is simply gratitude, made visible.

### Experimental settings (for testing)

A new **Settings > Experimental** tab lets you test how QUILL feels on different
editor surfaces - **RichEdit 3.0 / 2.0**, **Notepad** (a plain edit control),
**Rich text**, or a **native Win32 EDIT** spike. A read-only panel explains each
choice's user and technical impact as you select it, and the options stay ignored
until you tick **"I understand features may degrade based on the control selected."**
A **Hide editor border** toggle is here too. QUILL warns you to restart when you change
these.
**Why it matters:** a safe sandbox for power users and testers to help shape the
editor, with a clear gate so nothing changes by accident.

### Read your document in the browser's best voices (experimental)

New in this beta, off by default: turn on **Read the document aloud in your
browser** under **Settings > Experimental** (it takes effect immediately - no
restart) and a **Read in Browser** command appears under **Tools > Reading &
Dictation > Read Aloud** and in the command palette. QUILL writes a
self-contained, accessible reader page - a labelled voice picker, Speed,
Play/Pause/Stop, a live status line, Escape to stop - and opens it in your
chosen browser, where the browser's full voice set is available, including
Edge's "Online (Natural)" voices that the built-in engines cannot reach. It
reads section by section so book-length documents stay reliable, **Pause**
keeps your place and tells you where you are ("Paused at section 12 of 300"),
and your voice and speed choices are remembered.
**Why it matters / privacy:** the best-sounding free voices live in real
browsers. QUILL itself makes no network call and no audio file is produced -
but the browser's "Online (Natural)" voices synthesize in the vendor's cloud,
so choosing one sends the text being read to that service; voices labelled
"on this device" stay fully local, and the setting text says all of this
plainly. The reader page is deleted when you close QUILL, so no plaintext
copy of your document lingers.

### Proofread before you publish

- **Proofread Mastodon posts before sending (per account)** - tick it and pressing
  Post opens the F7 Spelling Review on the post text first.
- **Spell check a document before saving** - opens F7 automatically on Save / Save As.

---

## Under the hood - quality, reliability, and honest engineering

The features above stand on a day of unglamorous work that deserves its own
telling, because this is the part most release notes hide.

### The GLOW engine can no longer silently vanish

The most interesting bug of the cycle: GLOW's shared engine could be
*installed and silently unavailable* at the same time. The engine's recent
architecture split moved its analysis backend into a new component, but the
version floor QUILL asked for was loose enough that an older, pre-split
install could satisfy it - and the engine would simply report "not
installed" with no error anywhere. QUILL now pins the exact backend floor it
needs, the vendored offline wheels install cleanly on a bare machine, and
the failure mode is extinct by construction. If you ever wondered why an
optional engine "didn't take" - this class of problem is what got fixed.

### Startup can no longer be taken down by a warm-up

QUILL's deferred startup runs each step - screen-reader detection, crash
recovery, watch folders - inside its own isolation so a failing step is
logged and skipped, never fatal. One recent addition (the browser-preview
warm-up scheduler) had slipped outside that pattern; a failure there could
have killed startup. It is now isolated like everything else, and the
regression test that guards the whole contract is green again.

### Responsiveness as a policy, not an accident

Everything heavy that shipped this cycle runs on the background task pool:
GLOW's structured-file audits, document conversion, page-by-page OCR (with
cancel checks between pages), and the verified engine download. The editor
never freezes for any of it - progress lands in the status bar, results
arrive as tabs, and your cursor stays exactly where you left it. On-device
OCR is CPU-only by design, and the speech and AI engines continue to load
on demand and unload when idle, so a modest laptop stays a first-class
citizen.

### Documentation as part of the product

Every feature that shipped this cycle shipped *documented, everywhere, at
once*: user-guide sections for GLOW and Import / Convert Document, glossary
entries, F1 help for every new command (the control reference now covers
469 topics, regenerated from the same source of truth as the app), product
requirements updated, the roadmap reconciled so it tracks only genuinely
open work, six new tutorials, and a 36-episode audio course. If you can
reach a feature, you can read about it - and now, hear about it.

### The little disciplines

The whole repository now passes its style gate completely clean; the module
size budgets, dialog inventory, network egress audit, and UI-surface
snapshots were all re-verified; and the full test suite - 6,776 tests -
passes. New capability this cycle arrived with 44 new tests of its own.
None of this is visible in a menu. All of it is why the menus keep working.

---

## Fixes worth calling out

- **Bookmarks now persist** per document and across sessions (see above), and QUILL
  restores your last cursor position - fixing the old behaviour where bookmarks were
  forgotten on close and shared across documents.
- **Opening Word and other documents with QUILL as the default app works** - pressing
  Enter on a file in your file manager now opens it instead of doing nothing.
- **Far less double-spoken chatter** - actions like "No misspellings found" were
  spoken twice; now exactly once (#728).
- **Report a Bug is keyboard-navigable again** and reliably confirms the report was
  copied (#729).
- **No alarming "text-to-speech failed"** when your screen reader is running; the
  SAPI fallback also initialises correctly under a read-only install (#749).
- **Offline dictation works out of the box** - the engine is fetched on first use
  instead of failing with "whisper binary not found" (#742).
- **Saving a model no longer freezes at 2% and crashes** - download progress is
  throttled so it cannot flood the UI (#748).
- **Spell check finds real misspellings again** - when Hunspell is present its verdict
  is authoritative, instead of a permissive word list waving typos through.
- **The portable build launches and opens documents**, and the **AI Hub opens**
  instead of erroring on a lazy-string.
- **Live preview no longer flickers or re-announces as you type** - the external
  browser preview refreshes only after you pause typing (debounced) and keeps
  your place on reload (returning to the section you are editing, or your previous
  scroll position), instead of reloading on every keystroke and jumping to the
  top. The in-app side preview (Ctrl+F6 to focus it) updates silently in place
  with no reload - the recommended live preview for screen-reader/braille users.
- **The crash-report dialog tells you what happened** - choosing Send, Copy, or
  Send without a sign-in used to complete silently, indistinguishable from doing
  nothing for a screen-reader user; QUILL now confirms out loud that the report
  was sent, copied to your clipboard (and what to do next), or that sending
  failed and it was copied instead.
- **Snappier, less alarming startup** - the one-time WebView2 warm-up runs after
  the editor is ready, not before it, so a slow first setup no longer looks like a
  freeze; short UI stalls now also capture a diagnostic stack snapshot, and
  startup task timings are always written to the logs so a slow launch can be
  reported with evidence.
- **Idle AI models are actually released now** - the background idle-unload sweep
  crashed on every tick, so idle models were never freed; it now runs correctly.
- **F1 help now covers every command** - all 319 commands that previously had no
  help topic now have a plain-language description and their shortcut, so pressing
  F1 on any menu item or command always says something useful.
- **Smart triggers and Quillin-contributed abbreviations now actually fire** -
  typing `=bug()`, `=todo(10)`, or `=rand(3,4)` alone on a line and pressing Enter
  now inserts the generated text, and contributed abbreviations like `qbug` expand
  as you type (with Abbreviation Expansion on). Both were declared and documented
  since 0.7.0 but never dispatched. Numeric arguments work, every insertion is
  announced and undoable, and the per-trigger toggles on the Quillin's preferences
  page are honoured.
- **Quiet failures now speak up** - List Studio settings export/import confirms
  success or explains the failure, the Pronunciation Dictionaries dialog warns
  when a dictionary could not be saved, and the Quillin wizard's Copy JSON only
  claims "copied" when the clipboard actually took the text.
- **The Python snippet sandbox is harder to escape** - snippets are now also
  statically blocked from dunder attribute access (the classic route from a
  harmless-looking expression to the OS), on top of the existing
  separate-process isolation, import allowlist, and time/memory caps; if the
  OS refuses a resource cap, QUILL logs it instead of staying silent.

---

## For testers

- Upgrade path: install over Beta 1 and confirm your settings, keymap, and
  documents carry forward (see `docs/release/upgrade-path-regression-0.8.0.md`).
- Fresh install: see `docs/release/fresh-install-regression-0.8.0.md`.
- Acceptance: `docs/release/user-acceptance-test-plan-0.8.0.md`.
- New this beta to exercise: **Alt+F3** Reveal Codes; **Set/Go To/List Bookmarks**
  then reopen the file; **Tools > Spell Check Language**; **Help > Download Optional
  Components**; **Settings > Experimental**; **Help > About > Golden Quills**.

## Release mechanics (do not announce yet)

Per the active release hold, the repo stays on Beta 1 labels and the update feed
stays where it is. No version bump, tag, push, or feed change until explicitly
approved. See `RELEASE.md` for the tag-time checklist.
