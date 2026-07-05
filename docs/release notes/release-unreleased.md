# QUILL Unreleased - The Audio Studio: Your Books, By Ear, Start to Finish

### The screen-reader-first writing studio, built by the people who depend on it.

*From Community Access. Free. Optional by design. Private by default. Yours to make quiet.*

This is the narrative companion to the **"Unreleased"** section of
`CHANGELOG.md` (the canonical, append-as-you-go log) for the release that
follows 0.9.0 Beta 1. It will take that release's number and name when the
release is cut; until then it gathers, in one story, everything that has
landed on main since the beta shipped.

One note on the "last feature beta" promise: 0.9.0 said no new features
before 1.0. The Audio Studio is the deliberate, announced exception — it is
not a new promise but the **completion of an old one**: the consolidation of
ChapterForge, the last of the three sibling products (BITS Whisperer, GLOW,
ChapterForge) that QUILL committed to absorbing. With this release that
program is finished; there are no more sibling products waiting outside.

---

## The Audio Studio - one door for everything audio

**Tools > Speech > Audio Studio** replaces the old Batch Export to Speech
Audio dialog — a single screen with some forty controls — with a guided
wizard that asks one thing at a time and speaks every step ("Step 2 of 7:
What should I read?"). Nothing was lost in the move: every option from the
classic dialog survives, from the chapter transition sounder and its volume
to round-robin voices, translated editions, dry runs, and per-folder
remembered settings. Your keyboard binding still works; a repeat run on a
remembered folder is three keystrokes with **Skip to summary**.

The first page asks what you want to make, and the wizard reshapes itself:

- **Narrate documents into an audiobook or speech audio.** Word, Markdown,
  HTML, or text files, read by any QUILL voice — offline or cloud — one
  chapter per document or heading, optionally assembled into a single
  chaptered book with tags and a cover.
- **Combine audio files into one chaptered audiobook.** A folder of
  recordings becomes one master — MP3 with ID3 chapters or a true M4B —
  one chapter per file, natural order, titles from the filenames, and you
  always review the chapter list before the merge.
- **Edit an existing audiobook.** A finished MP3 or M4B opens in the
  Chapter Workbench, described next. A file with no chapters at all opens
  as one chapter, ready to carve.

## The Chapter Workbench - fix a book by ear

The Workbench is the heart of the release: a chapter list that reads each
row in full ("3. The Long Road - starts 1:02:03, runs 12:40"), a built-in
**chapter-aware player** (Play/Pause, previous/next chapter, rewind/forward,
a position slider that speaks minutes and seconds, playback speed from 0.75x
to 2x with pitch preserved), and the surgery that was never possible by ear
before:

- **Split at playhead.** Listen for where the chapter should begin, pause
  there, press the button. The boundary lands exactly under your ear.
- **Set start to playhead** retimes an existing boundary the same way;
  **Merge into previous**, **Rename**, and **Restore original** round out
  the set.
- **Where am I?** answers with the full audible glance: chapter number and
  name, time into the chapter and left in it, position and time remaining
  in the whole book.
- The player **remembers where you stopped** in every book and resumes
  there next time.
- Chapter lists **import and export** in five formats - Audacity labels,
  plain timestamps, CUE sheets, Podcasting 2.0 JSON, and CSV (any
  spreadsheet with a Title column can name your chapters).
- **Split into files** goes the other way: one audio file per chapter,
  named and numbered - instant podcast episodes.

Saving is honest about physics: an MP3 saves its edits **in place** (only
the tags are rewritten; the audio bytes are untouched) and an M4B saves as
a new file through a **lossless re-mux** - no re-encode, no quality loss.

## Builds you can trust

Before a long build, the Studio runs a **pre-flight check** - files whose
sample rate, channels, or format differ are named in the log, file by file -
and states the estimated duration and size. After the build it **re-reads
the finished book and verifies** what a player will actually see: the
completion message says "verified 24 chapters," not just "done." Every book
gets two companions written next to it: a plain-text **chapter report** and
a **Podcasting 2.0 chapters.json** sidecar. An **audition** option converts
just the first document so you can judge the voice, pace, and loudness in
minutes before an overnight run, and **spoken opening and closing credits**
("My Book. Written by Jane Doe. Narrated by Sam Reader.") can be synthesized
in the run's own voice as the first and last chapters.

## Publish what you made

The Workbench's **Publish** button offers three explicit, consent-first
paths. **Podcast feed:** a complete RSS 2.0 file with iTunes and Podcasting
2.0 tags, written next to the book, generated entirely offline. **SFTP
upload:** saved destinations send the book and its companions through
QUILL's own SSH machinery - the strict host-key policy applies, and
passwords live in the Windows Credential Manager, never in a settings file.
**Auphonic:** send the book to your own Auphonic account for professional
post-production; QUILL uploads, waits, and downloads the results beside the
book, with your API token in the credential vault. Every network path is
inventoried in the egress audit, QUILL asks before the first contact with
any service, and the whole dialog is absent in Safe Mode.

## Small kindnesses that add up

- **Job files.** Save a `.quilljob` from the summary page and the entire
  run - folder, voices, chapters, mastering, book details - is pinned in a
  small, hand-editable file. Load it on the Studio's first page and
  everything comes back.
- **Look up book details.** Type a title, press one button, and Open
  Library and MusicBrainz - free, keyless public catalogs - fill in the
  author, genre, and year from the match you choose. Only the title and
  author you typed are ever sent.
- **Library mode.** Point the combine-audio journey at a folder of book
  folders and every subfolder builds as its own audiobook, unattended,
  each titled after its folder.
- **A watch action.** "Build audiobook from the folder" keeps a drop
  folder alive: new recordings trigger a rebuild of that folder's master -
  a batch of files causes one rebuild, not many.

## Where this came from, and what it means

The Audio Studio is the consolidation of **ChapterForge**, rebuilt on
QUILL's invariants: every dialog through the audited accessibility
contract, every network call inventoried and consented, every secret in the
credential vault, all core logic strict-typed and wx-free with its own test
suite. The ChapterForge repository is being archived with a pointer here;
its sample audio lives on in QUILL's test corpus, and its Auphonic design
notes are preserved in `docs/design/publishing/` for the client's future
growth.

As always: if something is rough, tell us and we will fix it. This one, more
than most, was built to be judged by ear - so listen hard.
