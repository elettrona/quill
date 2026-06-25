# QUILL 0.7.0 Beta 2 Release Notes

Beta 2 is the release where QUILL gets serious about proofing, voice, and
accessibility. You can now walk through every misspelling in a fully accessible
guided dialog, decide exactly how much QUILL says and when, transcribe and
caption audio entirely on your own computer, dictate and even run commands by
voice offline, save accessible talking books, and work through a real braille
proofreading workflow. Around those headline features sit a smoother upgrade, a
cleaner startup with no console window for both installed and portable copies,
stronger macOS and screen-reader support, and a long list of reliability fixes.

Everything new here follows the same promises: it is **optional**, it is
**screen-reader-first**, and your content stays **on your machine** unless you
explicitly choose otherwise. QUILL launches, edits, and saves with all of it
turned off.

## At a glance

- **Guided F7 Spelling Review.** A fully accessible, guided spelling dialog —
  local, no AI required — with a readable Context field, all actions by keyboard,
  configurable announcements, and optional letter-by-letter word spelling.
- **Verbosity controls.** Choose how quiet or talkative QUILL is, per action,
  with Quiet and Meeting modes for shared rooms.
- **Private, offline speech.** Transcribe audio/video, make SRT/VTT captions,
  dictate into your document, and run commands by voice — all on-device, nothing
  uploaded.
- **Documents to audio in bulk.** Convert a whole folder to speech with chaptered
  MP3/M4B audiobooks, custom pronunciation dictionaries, text cleanup, and an SSML
  builder for fine pronunciation and prosody control.
- **DAISY talking-book export.** Save any document as a DAISY 2.02 text-only
  talking book for Victor Reader Stream, Plextalk, APH players, and DAISY apps.
- **Braille proofreading workflow.** Restore-your-place, a proofing tracker,
  layout validation, and selection-aware back-translation.
- **A smoother upgrade** that carries your compatible settings and shortcuts
  forward automatically, and a **cleaner startup** — no console window flashing,
  for both installed and portable copies.
- **Stronger macOS + screen-reader behavior**, and many crash, focus, and
  file-fidelity fixes.

---

## Control what QUILL says: the Verbosity system

QUILL now lets you decide how much it announces and when — from full, friendly
context for every action down to near silence — without fighting your screen
reader. Open **Verbosity Preferences** from the command palette
(`Ctrl+Shift+P`, then type "verbosity").

- **Four profiles.** Pick a level: **Beginner** (full context for everything),
  **Normal** (informative, the default), **Expert** (routine confirmations are
  suppressed, but errors always speak), or **Quiet** (speech and earcons off,
  leaving braille and the on-screen status bar). Switching profiles is announced
  so you hear the change.
- **Quiet Mode and Meeting Mode.** `QUILL key + Q` toggles Quiet Mode and
  `QUILL key + Shift + Q` toggles Meeting Mode for a call or a shared room. The
  status bar keeps updating, a `[Q]` or `[M]` indicator shows the mode, and
  `Ctrl+Shift+Z` undoes the last verbosity change.
- **Channels you control.** Speech, Braille, and Sound can each be turned on or
  off; the **Visual** status bar is always on and cannot be disabled, so you
  never lose the on-screen status of an action.
- **Less repetition, no floods.** QUILL no longer re-speaks the same announcement
  when it repeats within a moment (such as holding a key at the end of a list), and
  an optional **announcement budget** caps how many are spoken in a burst. Both
  affect only what is *spoken* — the status bar still shows everything. Find
  **Collapse repeated announcements** and **Announcement budget** under
  Preferences > Accessibility.
- **Make it say exactly what you want.** Advanced users can edit what each action
  announces using simple tokens like `{line}` and filters like `${ordinal:line}`,
  with live validation and a preview before you commit. Save wordings to a
  template **library**, **import/export** your setup as a file, or install a
  community **QUILL Verbosity Pack** — all data-only, never code.
- **Understand and tune it.** A **Preview Lab** lets you hear how a profile sounds
  against everyday scenarios; an **announcement History** lets you replay, copy,
  or ask **"why did QUILL say that?"**; and **Safe Mode** instantly restores the
  built-in announcements if a custom setup ever misbehaves — without deleting your
  work.

QUILL speaks *alongside* your screen reader, never instead of it, so it does not
duplicate the typing echo, speech rate, or punctuation level your screen reader
already controls.

## Speak and listen: private, offline speech

QUILL has a privacy-first speech engine that runs entirely on your computer,
under **Tools > Speech > Whisperer**. It needs **no AI account, key, or
provider** — you do not have to turn on Artificial Intelligence to use any of it
(that is why it no longer lives under the AI menu). The engine ships with QUILL
(choose the *offline
speech engine (whisper.cpp)* installer component, or drop it into
`tools\speech\whispercpp` in a portable copy) — no separate install, no PATH
editing. Then download a model from **Manage Speech Models** (sizes and
trade-offs are shown; the Small model is a good start; downloads come over a
secure connection and are disabled in Safe Mode).

### Manage models with confidence
**Manage Speech Models** now guides you to a model that fits your computer and
gets out of your way while it downloads.

- **Machine-aware guidance.** The dialog opens with a summary of your machine
  (RAM, and whether a GPU was found). Each model shows roughly how much memory it
  needs, flags models that are too big for your RAM, marks the best fit as
  **"Recommended for your computer,"** and warns when a large model has no GPU to
  accelerate it.
- **Downloads run in the background with a real percentage.** A download no longer
  freezes QUILL — it runs while you keep working, shows a percentage you can
  **Cancel** at any time (cancelling cleans up the partial file), and announces
  progress for screen-reader users. QUILL also warns about low disk space before
  starting.
- **Deleting a model is now obvious.** After you pick a model, choose **Download**
  or **Remove** explicitly, instead of the action being inferred for you.
- **A startup freeze is fixed.** Opening any Whisperer command no longer stalls
  the app while the optional Faster Whisper engine loads.
- **Open models, no account, nothing to accept.** The speech models QUILL offers
  are open-source (**MIT-licensed**) and free — there is **no Hugging Face account
  or sign-in required**, no license to click through, and no gated models. Each
  model shows its license and links its model card before anything downloads, and
  the files are stored only on your computer.
- **Verified, reproducible downloads.** Models are fetched from a pinned version
  and checked against a known checksum, so a silent re-upload can't change a model
  underneath you. (This also fixed the speaker-detection model, whose download
  link had gone stale — it works again.)
- **Optional token, with guidance, if you want higher limits.** A token is never
  required, but if you download many models and hit Hugging Face's rate limits you
  can add a free access token under **Tools > Speech > Whisperer > Hugging Face
  Token...**. First time, QUILL walks you through it — the steps to create a free
  "Read" token, with a one-click offer to open the Hugging Face token page in your
  browser — then you paste it (entered masked, stored in Windows Credential
  Manager, never in a settings file). A rate-limit error now points you here
  instead of showing a raw failure.

### Transcribe audio and video
**Transcribe Audio or Video (Offline)...** turns a recording into text on your
own machine — no cloud account, and your audio is never uploaded. Choose the
output format (**plain text, Markdown, or HTML**); it opens as an editable draft
while QUILL works in the background. With the speaker-detection model installed,
transcripts label **who is speaking when** ("Speaker 1", "Speaker 2", ...).

**Open almost any file.** QUILL now accepts a wide range of audio and video
formats — MP3, M4A, AAC, FLAC, OGG, Opus, WMA, WAV, MP4, M4V, MOV, MKV, WebM,
and AVI. When **ffmpeg** is available on your computer, QUILL converts the file
automatically before transcribing, so you no longer have to prepare a WAV first.
(Without ffmpeg, the offline Whisper engine still reads 16 kHz mono WAV files;
the Faster Whisper engine reads the other formats on its own.) QUILL does not
bundle ffmpeg, but it can fetch it for you: **Tools > Speech > Whisperer >
Download FFmpeg...** downloads the official build and sets it up — or install it
yourself once with `winget install Gyan.FFmpeg`.

### Captions
**Generate Captions (Offline)...** transcribes a file with timestamps and saves
it as **SRT** or **VTT** subtitles you can review and ship.

### Transcribe a whole folder automatically
Watch Folder automation can now transcribe for you. Point a watch profile at a
folder, choose the **Transcribe audio (Whisperer)** action, and every audio or
video file you drop in is transcribed **on your machine** and saved next to it —
nothing is uploaded. Pick the **Transcript format** per profile: plain **Text**,
**SubRip (.srt)**, **WebVTT (.vtt)**, or **Markdown**. The caption formats carry
timestamps and fall back to plain text when the engine returns no timed segments,
so you never get an empty caption file. If no speech model is installed yet, the
profile tells you where to get one. This automation always uses the on-device
engine — it never uploads your audio.

### Add a cloud transcription provider (optional)
Prefer a cloud service for its accuracy or speed? You can now add one as an
**extension**. QUILL bundles three, each a purely declarative Quillin:

- **OpenAI Whisper** — best-in-class accuracy across 99+ languages (uses your
  OpenAI API key).
- **Groq Whisper** — the same Whisper large-v3-turbo model, run on Groq's
  hardware for very fast turnaround (needs a Groq API key).
- **ElevenLabs Scribe** — high accuracy with optional **speaker diarization**, so
  the transcript marks who spoke each segment (needs an ElevenLabs API key).

Enable one, set its API key, and the provider appears in **Manage Speech Models**.
Cloud transcription is strictly **opt-in and never silent**: audio is uploaded
only when you explicitly transcribe a file with that provider, never offline and
never in Safe Mode — and the folder automation above never uses it. These
extensions ship no code and request no network permission; QUILL itself performs
the upload through its audited network path, so the extension never sees your
audio or your key.

### Dictate into your document
**Dictate (Offline)** lets you speak directly into the editor. Press the command
(or `QUILL key + Shift + D`) to start — you hear a start tone and "Dictation
listening" in the status bar — then press again to stop; QUILL inserts what you
said at the cursor as a single undoable edit. **Dictation Microphone...** picks
which microphone to use.

### Hold-to-Dictate and Locked Dictation (new)
Two fast, keyboard-only ways to dictate straight into the document — no dialog, no
focus change. They run on the same on-device Whisper engine as everything else, so
nothing is uploaded.

- **Hold-to-Dictate — hold F9.** Press and hold **F9**, speak, and release: QUILL
  transcribes what you said and inserts it at the cursor as one undoable edit. A
  short tone marks the start and stop (the stop tone is played only after the
  microphone closes, so it is never recorded). Ideal for a phrase or a sentence.
- **Locked Dictation — Ctrl+F9.** Press **Ctrl+F9** once to start a hands-free
  recording session (no need to keep a key held), and **Ctrl+F9** again to finish
  and insert. QUILL announces "Locked dictation on" so the active state is
  unmistakable.
- **Always a dependable stop.** While recording, **Escape** stops and *keeps* your
  speech for transcription; **Shift+Escape** cancels and discards it. Locked
  Dictation also stops automatically after five minutes, and stops and preserves
  your audio if QUILL loses focus.
- **Pause and check state.** **Ctrl+Shift+F9** pauses or resumes a locked session;
  **Alt+F9** speaks the current state ("Locked dictation is recording", "Dictation
  is being transcribed", and so on) without changing anything.
- **Safe by design.** Audio is saved to a recovery folder *before* transcription
  begins, so a crash or unplugged microphone never loses your words; a missing
  key-up can never leave the microphone running; and if the transcript cannot be
  safely inserted it is kept for review rather than dropped.
- **Every shortcut is remappable.** F9, Ctrl+F9, and the rest are defaults you can
  change under **Settings > Keyboard** (Keymap Editor); conflicts are detected and
  explained.

This first release covers Hold-to-Dictate and Locked Dictation while QUILL is the
foreground window; pause/resume, recovery review, and an optional global key hook
are planned follow-ups.

### Run commands by voice (new)
**Voice Command (Offline)** lets you drive QUILL hands-free. Run it, say a
command — "save", "bold", "next heading", "word count", "command palette" — and
run it again to act. Recognition is on-device, and voice can only invoke a
curated, **safe set of commands**, so a misheard phrase can never trigger
something destructive. It is off by default (turn it on in Settings) and always
disabled in Safe Mode. Say "cancel" or "never mind" to dismiss without acting.

### Choose your engine
The bundled **whisper.cpp** engine needs nothing extra. On capable machines you
can opt into two more, each by installing an optional dependency:

- **Faster Whisper** — a higher-throughput multilingual engine that uses your
  **GPU** when one is available. Install it in one step with **Tools > Speech >
  Whisperer > Download Faster Whisper Engine...** (about 110 MB, downloaded on
  demand; no source checkout needed), or from source as the `fasterwhisper`
  dependency.
- **Vosk (English)** — a **very low-resource, CPU-only** engine that runs on a
  ~40 MB model with no GPU, for old or constrained machines. It ships **in the
  Windows installer**, so it is available out of the box (no extra install); from
  source it is the `vosk` dependency. Its model still downloads on first use.

**Manage Speech Models** then offers a **Speech Engine** chooser, and your choice
is used for transcription, captions, and dictation; each engine has its own
models, so download one after switching. Pressing **Escape** on the engine
chooser now returns you to the editor rather than opening the default engine's
model list. All three run **entirely on your computer**. (For speaker labels,
use the whisper.cpp speaker-detection model.)

## Read aloud: more voices, cloud and local

Read Aloud now spans local and cloud voices.

- **AI Voice now supports Google Gemini as well as OpenAI.** `AI > Read Selection
  Aloud (AI Voice)`, `Read Document Aloud (AI Voice)`, and `Export Document as
  Audio...` can use **OpenAI** (11 voices) or **Google Gemini 2.5** (30 voices).
  Pick the provider, model, and voice under **Settings > Read Aloud**, and add the
  matching API key in AI Hub. The status bar shows an **estimated cost** before an
  export runs; OpenAI exports MP3, Gemini exports WAV.
- **No more clipped or awkward endings.** Long documents are split for the cloud
  only on **sentence boundaries** — never mid-word — so the audio never trails off
  at a strange spot, and Gemini exports add a short trailing pause so the last
  sentence is never cut off.
- **Local Read Aloud is broader and more reliable.** The Windows system voice now
  uses **SAPI 5** directly (pyttsx3 is gone), **DECtalk** works again (driven
  through its real synthesis runtime instead of the graphical sample that
  crashed), and **eSpeak-NG**, **Piper**, and **Kokoro** round out the offline
  engines. Every catalog voice ships a short spoken **preview** so you can hear it
  before choosing.

## Turn documents into audio: batch export, pronunciation, and SSML

QUILL can now convert documents to speech audio in bulk and give you fine control
over how they sound.

- **Batch Export to Speech Audio (Tools > Speech).** Point QUILL at a folder of
  documents (.docx, .md, .html, .txt), pick an offline engine, voice, and pace,
  and it converts every document to audio on a background task with progress you
  can cancel. You can include subfolders and narrow what is converted with
  **include/exclude filters** and a **maximum file size**.
- **Audiobook-ready output.** Choose **WAV, MP3, M4A, M4B (audiobook), Opus,
  FLAC, or OGG**; set the **MP3 quality**; and stamp **album, author/narrator,
  genre, and year** onto the files (each file's title comes from its heading, and
  its track number from its position). Long documents become **chaptered** audio
  with real MP3 chapter markers you can jump between in any podcast app, with an
  optional **transition sound** and configurable **pauses** between articles and
  sentences.
- **You are in control of existing files and naming.** When an output already
  exists, choose to **skip** it (cheap resume), **overwrite** it, or **rename**
  so both are kept. Mirror the source folders or **flatten** everything into one
  folder, and rename outputs with a **template** like `001 - Chapter One`. Turn on
  a **manifest** to get a `manifest.csv`/`.json` summary of the run.
- **Set it once per project.** A folder remembers its whole speech setup — engine,
  voice, output format, chapters, text cleanup, and pronunciation dictionaries —
  so you configure a project once and re-run it anytime.
- **Teach QUILL how to say things (pronunciation dictionaries).** **Tools > Speech
  > Manage Pronunciations…** lets you add corrections (names, brands, acronyms,
  technical terms) that apply everywhere speech happens — both batch export and
  live Read Aloud — with a live preview so you can hear the result. Dictionaries
  can be **global** or specific to a **project**, and a small **starter
  dictionary** ships with common terms already covered.
- **Cleaner speech from messy documents.** An optional **text cleanup** pass fixes
  the typography that trips up speech engines (curly quotes, dashes, ellipses,
  bullets, symbols, fractions, emoji) and speaks **phone numbers, emails, and
  URLs** clearly — including an option to say an address, pause, and repeat it.
- **Fine-tune pronunciation and prosody (SSML).** A new **SSML Builder** composes
  emphasis, pauses, say-as, phonemes, and prosody from accessible controls, and
  Read Aloud now plays that markup **natively on SAPI 5 and eSpeak-NG** so the
  pauses and emphasis actually take effect instead of being read aloud.

## Read and proof braille

Braille Mode gained a real proofreading and quality workflow, and it never
changes your braille file — progress and notes live in a small companion file
beside it.

- **QUILL remembers your place.** Reopen a `.brf`, `.brl`, `.pef`, or `.ueb`
  file and your cursor returns to where you left off, announced precisely — for
  example, "BRF file opened. 87 braille pages detected. Last position: braille
  page 12, line 14, cell 31."
- **Track proofreading.** A **Braille > Proofing** menu lets you mark a page
  proofed or needs-review, add notes, hear a spoken progress summary, jump to
  pages that still need work, and export a plain-text proofing report.
- **Validate layout.** A **Braille > Validation** menu flags common problems —
  over-long lines or pages, missing page breaks, mixed line endings, stray
  non-braille characters, malformed page indicators, numbering gaps, inconsistent
  running heads, and Unicode-vs-NABCC mismatches — then steps you through each
  finding with spoken position and detail. It only reads your file.
- **Recover source text.** **Braille > Translation > Back-Translate (draft)**
  back-translates a selected passage (or the whole file) to draft text, so you
  can check the source wording of a paragraph. Requires the optional QUILL
  Braille Pack.
- **Continuation pages read correctly.** Print-page continuation labels such as
  `7a` are now reported in full instead of being shortened to `7`.

## Save accessible talking books (DAISY)

**File > Export > DAISY Talking Book** saves your document as a **DAISY 2.02
text-only talking book** — the accessible format read by DAISY software and by
hardware players such as the Victor Reader Stream, Plextalk, and APH units.

- It exports what is on screen, so you do not have to save first.
- A DAISY book is a *folder* (the name you choose), holding the three files a
  player expects; QUILL asks before writing into a folder that already has files.
- Your headings become the player's navigation points; a document with no
  headings gets a title heading so navigation still works.
- The book is text-only, so a player reads it with its own text-to-speech — and
  because it is a standard DAISY book, you can open the folder in a tool like APH
  Book Wizard Producer to add recorded or synthesized audio later.

---

## Write in any language: Document Language and auto-detection

QUILL now lets a document be edited *as* a language even when its file name says
otherwise — so a plain `.txt`, an unsaved buffer, or a snippet you pasted can get
real HTML, Markdown, or code editing.

- **Set the language and get its characteristics.** **Ctrl+Shift+L** (also
  **Navigate > Set Document Language...**, the new **Format > Document Language**
  list, or Enter on the status-bar **Language** segment) pins a language for the
  current document. Once set, **Bold/Italic** insert the right markup,
  the heading/table/list/tag menu items light up, **comment toggling** uses that
  language's syntax, and heading navigation, the outline, link insertion, and
  live preview all follow it. The status bar shows **(set)** when you chose the
  language yourself. Recognised languages now include HTML, Markdown, CSS,
  Python, JavaScript, TypeScript, C, C++, **C#**, **PHP**, Go, Rust, Kotlin,
  Shell, YAML, JSON, TOML, and SQL.
- **It is an editing aid, not a rename.** Setting HTML on a `.txt` does not change
  the file; QUILL reminds you to use **Save As** to write it as `.html`. The
  choice is per-tab and resets when you close the file. **Auto-detect from file**
  clears the override.
- **Optional automatic detection (off by default).** Turn on **Settings >
  Editing > Auto-detect document language** to have QUILL recognise the language
  when you paste or type code into a plain `.txt`/untitled document. Choose how
  assertive it is: **Hint** (status bar only), **Suggest and announce** (you
  confirm), or **Switch automatically**. Detection is cautious — it acts only
  when confident, never guesses on ordinary prose, learns lightly from the
  languages you use, and **never** overrides a real extension or a language you
  set. Unlike editors that switch silently or show a visual-only hint, QUILL
  keeps a screen-reader user informed in every mode. Braille content is never
  affected — it has its own Braille Mode.

---

## Find your way faster: Quick Nav

**Go to Anything** (the QUILL key + `G`) is a single search panel for everything
worth jumping to in your document. It lists every navigable element — headings,
links, lists, **tables**, block quotes, bookmarks, code blocks — with a category
filter that shows a **live count** of each type, plus a type-ahead box to filter
and jump.

It now also lists your document's **misspellings** and, when a search is active,
the current query's **search hits** as their own navigable types. So you can open
one panel and jump straight to the next misspelled word, or to any match of your
last search, the same way you jump to a heading or a link — with a live count of
how many of each there are.

---

## Proof your work: guided F7 Spelling Review

Press **F7** and QUILL walks you through every misspelling in your document — or
just in your selection — one at a time. No AI, no network, nothing uploaded. It
runs entirely on your machine using the same local dictionary engine that powers
as-you-type checking.

The heart of the dialog is a **read-only Context field** that shows the
misspelled word highlighted inside the surrounding sentence. Focus lands there
automatically. You can arrow through the sentence character by character, move by
word, copy the text — just as you would in the editor. When you Tab away to take
action and then need to re-read the word in context, **Alt+W** brings you back
and reselects it instantly.

**The actions:**

- **Change** — replace this occurrence and move to the next issue. Press Enter
  in the Change to field to do the same without reaching for the button.
- **Change All** — replace every remaining occurrence in scope. QUILL counts
  them and confirms. Capitalisation is preserved automatically: `teh→the`,
  `Teh→The`, `TEH→THE`. The whole operation is a single undo step.
- **Ignore Once** — skip this occurrence and continue.
- **Ignore All** — skip all remaining occurrences for this session. Resets
  when you start a new review.
- **Add to Dictionary** — add the word to your personal dictionary
  permanently.
- **Undo Last** — reverse your most recent spelling action without closing the
  dialog. The button is greyed out until you have done something to undo.
- **Close** — finish the review. Any changes already made stay in the
  document's normal undo history.

**Screen-reader first.** QUILL announces the issue, your progress, and the
result of each action — but only what your screen reader would not already say
when focus moves. No double-reading of control names or field values.

**Configure it your way.** Every aspect of the spelling review experience is
tunable under **Settings > Spelling Review**:

- **Announcement verbosity** — three levels so QUILL says exactly as much as
  you want:
  - **Concise** — progress numbers and action results only. Best for
    experienced users who want to move fast.
  - **Balanced** *(default)* — issue type, current word, progress, and results.
    The right level for most workflows.
  - **Detailed** — adds control hints, action reminders, and scope descriptions.
    Helpful when you are learning the dialog or using it infrequently.

- **Spell word aloud** *(on by default)* — after announcing the misspelling,
  QUILL reads it letter by letter so you hear exactly what was mistyped. Turn
  this off if you prefer to navigate the Context field yourself.

- **Pause before spelling** — how long QUILL waits after announcing the word
  before it starts spelling it out. Adjustable from 100 ms to 3 000 ms;
  default is 800 ms. Increase it if you want time to process the announcement
  first; decrease it if you find the pause too long.

- **Context mode** — controls how much surrounding text appears in the Context
  field:
  - **Sentence** *(default)* — the current sentence plus adjacent sentences,
    up to roughly 900 characters. Enough to understand the word in its natural
    reading flow.
  - **Paragraph** — the full paragraph containing the issue, useful when
    sentence boundaries are unclear or when you want broader editorial context.

- **Wrap to beginning** *(on by default)* — when QUILL reaches the end of the
  document without finding more issues, it wraps back to the beginning and
  continues to the point where you started. Turn this off if you always want
  the review to stop at the end of the document.

**Jump without the dialog.** `Ctrl+F7` moves to the next misspelling in the
editor without opening Spelling Review; `Ctrl+Shift+F7` goes to the previous
one. Both announce the word and its position so you can deal with a quick fix
inline before running a full review.

---

## A smoother upgrade

When you upgrade from QUILL 0.5.0 or Beta 1, QUILL checks your saved settings and
keyboard shortcuts as it starts and carries forward everything that still works.
If an older choice points at a command that no longer exists, has an empty
shortcut, or conflicts with another command, QUILL quietly drops just that entry
and uses the current default — so a feature never silently appears "broken."

- **Familiar shortcuts come back.** Bindings that drifted during 0.7.0
  development (for example `Ctrl+F` for Find, plus Send to System Tray, Read
  Aloud, and Dictation) are repaired automatically.
- **Your customizations are respected.** QUILL starts from the current defaults
  and layers your compatible changes on top; importing someone's profile brings
  in only their real customizations and leaves your unrelated shortcuts alone.
- **Nothing extra to run.** Beta 2 handles the common upgrade needs on its own. A
  fuller migration utility (for larger format changes, older-beta profiles and
  Quillins, and a reviewable record of what changed) is still planned.

## How QUILL starts: installer and portable

QUILL now starts the same clean way whether you used the **Windows installer** or
the **portable** edition: both run through `quill.exe`, a proper windowed
launcher. However you open QUILL — pressing Enter on the Start-menu or desktop
shortcut after an install, or opening `quill.exe` in a portable folder — you get
the same behaviour described here.

- **No more console window flashing at startup.** The old `run-quill.cmd` batch
  launcher is gone, replaced by the windowed `quill.exe`. That removes the brief
  black command window some people saw when QUILL started — for **both installed
  and portable** copies. Upgrading also replaces any old Start-menu or desktop
  shortcut that still pointed at the batch file, so the flash does not return.
- **Honest identity.** The launcher reports itself as **QUILL for All** with the
  real version and **Community Access** as the publisher, so a screen reader's
  "what is this window / what version" commands say something useful instead of
  "Python." On upgrade, a stale shortcut pointing at the old launcher is replaced.
- **Choose where QUILL stores your data.** A first-run **Where QUILL stores your
  data** page offers the recommended AppData location, a spot beside a portable
  bundle, or a folder you choose; change it later under **Preferences > General**
  and QUILL moves your data there safely on the next restart. A folder counts as
  portable only when it contains both `quill.exe` **and** a sibling `data/`
  folder — real evidence on disk, so a stray setting can never redirect where your
  work lives.
- **Zero-setup and backward-compatible.** New portable bundles ship an empty
  `data/` folder so they work from the first launch; older Beta 1 bundles that
  still include `run-quill.cmd` keep working. AI keys (DPAPI-encrypted) travel
  with a verified portable bundle automatically.

## Accessibility and screen-reader refinements

- **Setup starts on the heading**, and its text is readable. Each Setup Wizard
  page focuses its heading first, so you hear the page's purpose before its
  controls; the explanatory text sits in a **read-only field you can arrow
  through line by line**, exactly like the About window, for both Windows screen
  readers and VoiceOver; and the buttons read plainly as **Back** and **Next**
  (no "less than Back").
- **A cleaner first launch.** On a fresh install the Setup Wizard opens before any
  Untitled document, so a screen reader doesn't announce a stray tab first; a
  blank document is created after setup.
- **macOS / VoiceOver.** VoiceOver now identifies the editor as a real editable
  text area; the Report a Bug fields have proper names and the window is
  non-modal (switch back to your document while writing it); and the Help menu is
  recognized as the system Help menu (`Cmd+?` works).

## More natural keyboard behavior

- **Typing `R` or `S` types `R` or `S`.** Friendly single-letter shortcut hints
  no longer get mistaken for system shortcuts, so your letters stay in your
  document. Modifier shortcuts like `Ctrl+R` are unaffected.
- **macOS standards.** `Cmd+Q` quits; word movement (`Option+Left/Right`) works
  normally; Back/Forward Location use `Cmd+[` and `Cmd+]`. Quote/Unquote Lines
  moved to `Ctrl+Shift+Q` / `Ctrl+Shift+K`. Older bindings are repaired on
  startup.
- **Closing an unsaved document.** The prompt uses the standard Yes/No/Cancel:
  press `Y` to save, `N` to discard, or `Esc` to cancel — or Tab to the buttons.

## Editing and keyboard polish

- **The Tab key can now insert a tab character.** Tab still defaults to smart
  line indent (Shift+Tab outdents; on a Markdown list item it nests or promotes
  the item). Press **QUILL Key + U** to switch the Tab key to insert a literal tab
  character at the cursor instead — Quill's take on the VS Code "Tab key" toggle
  (Ctrl+M is reserved for the mark ring). The current mode shows in the new
  **Tab Mode** status-bar cell and the checkable **Format > Tab Key Inserts Tab
  Character** menu item, and the mode change is spoken.
- **Tab indent is spoken under a screen reader again.** Indenting with Tab now
  announces aloud even while JAWS or NVDA is running, where it had gone silent.
- **F6 reaches the document tab bar.** With **Show Tab Control** on, F6 now cycles
  Editor, Document Tabs, Preview, and Status Bar, so the tab strip is reachable
  from the keyboard.
- **Clear All Notifications** is now a one-step action on the notifications
  status-cell context menu.
- **Hey QUILL Commands is a real on/off toggle.** The Reading > Dictation > Hey
  QUILL Commands menu item is now checkable: it flips the setting directly,
  remembers it, and says "Hey QUILL voice commands on" or "off" — it no longer
  sends you to a settings tab.
- **Results that don't move the cursor are now spoken.** Pressing **Ctrl+F7**
  (next misspelling) or **Ctrl+Shift+F7** (previous misspelling) now says
  "No misspellings ahead; N behind" (and the reverse) instead of staying silent,
  and **Check for External Changes** announces when the file still matches what
  is on disk. (**F7** opens the full Spelling Review dialog; use Ctrl+F7 and
  Ctrl+Shift+F7 to jump between misspellings without leaving the editor.)
- **Ctrl+W closes the current document.** If no side preview is open, Ctrl+W now
  closes the active document instead of doing nothing.
- **Recent Files can tidy itself.** A new General setting, **Drop missing recent
  files automatically** (off by default), removes Recent Files entries whose file
  is gone — but only on your fixed internal drives. Files on USB, removable, or
  network drives are left alone, since "missing" there usually just means the
  drive is unplugged or offline.
- The unfinished **Pandoc Conversion Center** menu item was removed; use
  **File > Import** / **File > Export** (and **Tools > Batch Conversion** for
  folders).

## Structured List Studio: build lists by concept, not syntax (F2)

A new **Structured List Studio** lets you build and edit lists by working with
plain concepts — item text, a checked box, a term and its definition — while
QUILL writes the correct Markdown or HTML for you. You never have to type `-`,
`1.`, `[ ]`, `<ul>`, or `<dl>` by hand.

- **Press F2 to open it.** F2 is context-sensitive: with text selected it turns
  your selection into a list (one item per line or per paragraph, detected
  automatically, with any existing bullet/number/task markers stripped); with
  nothing selected it starts a new list. The studio is also on the
  **Insert > List > Structured List Studio...** menu. (F2 was previously Insert
  Special Character, which moves to **Shift+F2**; both shortcuts are remappable
  in Keyboard settings.)
- **Four list types.** Bulleted, Numbered, Checklist, and **Definition (or
  description) list**. A choice control switches between them, and a Markdown/HTML
  control picks the output; the dialog shows the generated source live, read-only,
  as you work.
- **Definition lists without the tags.** Build glossaries, FAQs, and
  term/description pairs through clearly labelled **Term** and **Definition**
  fields. QUILL generates valid `<dl>`/`<dt>`/`<dd>` for HTML and a
  Pandoc-compatible definition syntax for Markdown — it never asks you to know
  which one your renderer supports.
- **Accessible by construction.** Every control is keyboard-reachable and
  labelled; the items/entries outline announces each item's text, number or
  checked state, and position; and inserting the finished list is a single
  Ctrl+Z-able edit.

- **Nesting, multiple terms/definitions, and editing in place.** Indent / outdent
  / add-child build nested lists (Move up/down carries a whole subtree); a term can
  have several synonyms and a definition several paragraphs; and pressing F2 with no
  selection inside an existing list loads it back into the studio to edit and
  rewrite just that block.
- **Convert, import, and stay safe.** Switching a list's type carries the content
  across and warns before dropping structure; **Import from clipboard / file** pulls
  text in with the live preview as its interpretation; and on OK the studio reparses
  and validates the generated source, leaving your document unchanged if anything
  looks wrong. When a Markdown definition list has no profile configured for the
  document, QUILL **asks** how to generate it — embedded HTML, a specific Markdown
  profile (Pandoc / Markdown Extra / MultiMarkdown), or a plain "Term: Definition"
  list — instead of guessing.
- **Settings and presets.** A **List Studio Settings…** dialog (Insert > List) picks
  a shipped preset, tweaks the high-value options, and exports/imports the
  configuration as JSON; your choices persist and seed the next F2.

A formal screen-reader sign-off across JAWS, NVDA, and Narrator is the remaining
release-verification step for this feature.

## Opening and saving files faithfully

### Plain-text fidelity
- **No stray byte-order mark.** A UTF-8 BOM is kept out of the editable text (so
  it can't sit under your cursor or be read aloud) and re-added on save if the
  original had one.
- **Round-trip exactness.** Open and save and you get the same file back: Windows
  `CRLF` line endings stay `CRLF`, and runs of blank lines (and Markdown-looking
  lines) are preserved verbatim. Use **File > Save As Plain Text** when you
  *want* to flatten formatting.

### Simple File Open dialog
An opt-in, keyboard-friendly picker (turn on **Settings > General > Use simple
file open dialog**), reached from the same **File > Open...** / `Ctrl+O`:
folders first with a `[dir]` prefix, a small **Filter** dropdown, `Ctrl+L` to
focus the path, `Enter` to open or descend, `Backspace` to go up, `Ctrl+H` for
hidden files, a **Recent** popup, and a **Use Windows Dialog** button for the
native picker when you need it. Accessible error messages keep the dialog open so
you can fix a path and retry.

## Setup and AI Hub reliability

- The **Open AI Hub** button works on a brand-new profile, and the Hub's tabs,
  provider choices, instructions, and image styles all load correctly — from the
  Setup Wizard or the Tools menu.
- A new profile no longer triggers a startup typing failure.
- The Setup Wizard no longer reopens on every launch after an elevated install
  into a protected folder: QUILL remembers that setup is done even when it cannot
  delete the marker file.

## Stability and crash reporting

Several crashes and rough edges are fixed: **Check for Updates** and **Check for
GLOW Updates** open correctly; choosing **Don't Save** after `Ctrl+F4` no longer
crashes; closing the last document is safe from a late caret event; **saving
settings** (OK, Reset to Factory Defaults, or importing) applies theme,
spell-check, soft-wrap, and title-style cleanly; a Quillin reporting status no
longer crashes the app; the Developer Console reports the real document name;
**Quill Eraser** opens its review dialog correctly; and a fresh install with the
Setup Wizard pending no longer crashes on startup.

When an unexpected error does close QUILL, a new **crash-report dialog** (on by
default during the beta) shows a **redacted preview** of what would be sent —
recent commands, the document name and encoding, platform and screen-reader info,
and the last traceback frames, with personal data and credential-shaped strings
scrubbed first. You choose: **Send** (to the public issue tracker, only with a
configured token), **Copy to clipboard**, or **Don't send** (the default; Escape
triggers it). A local copy is always saved to your crash-reports folder, and you
can turn the dialog off in **Settings > General**.

Everyday housekeeping also improved: the User Guide and other static pages stay
put instead of refreshing every second (the live Browser Preview still follows
your edits); **Open Log Folder**, **View Startup Logs**, and **Open Diagnostics
Folder** use the right file manager per platform; the macOS app menu says **Hide
QUILL** / **Quit QUILL**; and macOS explains honestly that system-tray mode is
unavailable there rather than pretending to run.

## What is coming next

QUILL's roadmap is tracked openly, and every workstream is targeted to ship.
**Landed in this beta:** the guided F7 Spelling Review dialog (local, fully accessible, configurable announcements and letter-spelling); the verbosity system; the offline speech suite (transcription, captions, dictation, speaker labels, voice commands, and the optional Faster Whisper engine); DAISY talking-book export; and the braille proofing, validation, restore-your-place, and back-translation workflow.

**Coming next:** broader publishing options (including direct publishing to
external platforms and chaptered audiobook export), a unified agentic AI hub, and
deeper accessibility-checking tools — all optional and screen-reader-first.

## What you need to do

For most people, nothing special:

1. Install or start QUILL 0.7.0 Beta 2.
2. Let QUILL check and carry forward your compatible settings at startup.
3. Keep working with your familiar files and preferences.

**Optional extras, only if you want them:**

- **Offline speech engine.** The on-device transcription engine (whisper.cpp)
  ships with the Windows installer — choose the *offline speech engine
  (whisper.cpp)* component during setup (it is included in a Full install). In a
  portable copy you can drop it into `tools\speech\whispercpp`. Then download a
  model from **Tools > Speech > Whisperer > Manage Speech Models**.
- **ffmpeg, for transcribing anything but WAV.** To transcribe or caption MP3,
  M4A, MP4, MOV, MKV, and other formats you need **ffmpeg**. The easiest way is
  **Tools > Speech > Whisperer > Download FFmpeg...**, which fetches the official
  build and sets it up for you; or install it yourself (for example,
  `winget install Gyan.FFmpeg`) and QUILL finds it on your PATH. QUILL does not
  bundle ffmpeg — it uses the copy on your computer — so without it the offline
  engine reads only 16 kHz mono WAV files. No ffmpeg is needed for typing,
  editing, or
  any non-speech feature.
- **Faster Whisper (advanced, GPU).** On capable machines you can install the
  optional `faster-whisper` package to add a higher-throughput engine; QUILL then
  offers a Speech Engine chooser.

None of these are required to launch, edit, or save — QUILL runs fully without
them.

**Installing from source (developers).** If you install with `pip` rather than the
Windows installer and the on-device AI extra, note that `llama-cpp-python` has
prebuilt CPU wheels but no Windows wheel on PyPI itself. If `pip` starts a slow
source build, force the wheel with `pip install --only-binary=llama-cpp-python ...`
(QUILL's requirements already point at the CPU wheel index). Installer users are
unaffected.

You should not need to edit `keymap.json` or rebuild your preferences by hand.
Because this is a beta, please keep telling us anything that feels confusing,
inaccessible, unreliable, or harder than it should be — your feedback shapes what
ships next.
