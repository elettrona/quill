# QUILL Audio Studio — Consolidation Plan

Status: draft for review. Author: Claude, 2026-07-04.
Decision inputs: name = "QUILL Audio Studio" (chosen); the wizard replaces the
existing Batch Export to Speech Audio dialog (chosen); canonical ChapterForge
source = `s:\code99\forum` (newer, full-featured; ignore `S:\code\Chapter Forge`).

Suggested final home for this document once approved:
`docs/planning/quill-audio-studio-plan.md` (the strict root-file gate will
reject `book.md` at the repo root if committed).

---

## 1. Vision

One place in QUILL where anything becomes a finished, beautifully chaptered,
fully tagged audiobook — and where a finished audiobook can be opened, heard,
reshaped, and published. Three doors, one studio:

- Write it, hear it. A folder of Word, HTML, Markdown, EPUB, or text files
  (or the open document) is narrated by any QUILL voice — local or cloud —
  into a single chaptered audiobook, one chapter per heading or per file.
- Recorded it, bind it. A folder of MP3s (or mixed audio) becomes one
  chaptered master — one chapter per file — with full editorial control over
  the chapter list before the merge.
- Made it, refine it. An existing chaptered MP3 or M4B opens in the studio:
  listen with a chapter-aware player, rename, merge, split at the playhead,
  retime, fix tags and cover, save in place.

Everything is guided by a wizard that never dumps forty controls on one page,
never loses a screen-reader user, and remembers everything so the second run
is three keystrokes: Enter, Enter, Start.

## 2. Naming and menu placement

- The feature family is "QUILL Audio Studio"; the menu item is
  `Tools > Speech > &Audio Studio...` (command id `tools.audio_studio`).
- It replaces the current `&Batch Export to Speech Audio...` item
  (`tools.speech_batch_export`). The old command id is kept as an alias so
  existing keymaps, the command palette, and muscle memory keep working — it
  simply opens the Studio.
- `&Export to Speech Audio...` (single document, quick) and
  `Export to &Translated Speech Audio...` stay as fast single-shot commands;
  the Studio is the destination experience. A later phase can offer "Open in
  Audio Studio" from those dialogs, not the reverse.
- Windows-menu/session naming, progress dialogs, logs, and docs all say
  "Audio Studio" so the brand is coherent.

## 3. What QUILL already has (the foundation is strong)

Shipped and reusable as-is (PRD 5.25d/5.25e):

- The whole synthesis pipeline: every engine (SAPI 5, Kokoro, Piper, eSpeak
  NG, DECtalk, cloud OpenAI/Gemini/ElevenLabs), round-robin voices,
  pronunciation dictionaries, TTS normalization, SSML, chunking, retries,
  parallelism, voice-failure blacklist.
- Document discovery: extensions, recursion, include/exclude globs, size cap.
- Chaptering: chapter per document, or per heading ("separate file per
  article" mode proves the heading-split machinery exists in
  `document_speech`), page-turn earcons between chapters.
- Audiobook assembly: `quill/core/speech/audiobook.py` — folder scan, natural
  sort, `title_from_filename`, cover discovery, ffprobe durations, ffmpeg
  concat build, MP3 ID3 CHAP/CTOC via mutagen, M4B chapter atoms via
  FFMETADATA, tags + cover.
- Chapter review: `audiobook_chapter_editor_dialog.py` (rename, reorder,
  merge) already marshalled onto the UI thread mid-run.
- Mastering: two-pass loudnorm, ACX normalize + post-build RMS/peak verdict
  (`loudness.py`).
- Operations: project profiles (`.quill/speech-project.json`), conversion
  logs, temp-folder policy, spoken-text sidecars, dry-run preview, cost
  estimates for cloud runs, accessible progress dialog, background task pool.
- Translated audio export (per-language voices, local-first).

What QUILL lacks (the ChapterForge delta):

- A guided, multi-step wizard UX (today: one very dense 794-line dialog).
- An "audio files in" first-class journey (today it exists but is buried as a
  side effect of the batch export dialog).
- Opening and editing an existing chaptered file.
- A chapter-aware player.
- Chapter surgery: split at playhead, retime a chapter start, per-item silence
  trim, inter-chapter gaps.
- Chapter list import/export (Audacity labels, CUE, plain timestamps,
  Podcasting 2.0 JSON).
- Auto-chapter by silence detection.
- Pre-flight stream checks, output size estimate, post-build chapter-count
  verification, chapter report file.
- Metadata lookup (MusicBrainz, Open Library).
- Publishing: Podcasting 2.0 chapters sidecar, RSS podcast feed, SFTP upload,
  Auphonic post-production.
- Watch-folder auto-build of dropped audio folders.
- Job files (`.cfjob`) — pinned, hand-editable build recipes.

## 4. What ChapterForge brings (source inventory, s:\code99\forum)

Modules to port (wx-free logic lands in `quill/core/`, UI is rebuilt on QUILL
patterns — ChapterForge dialogs are reference designs, not copy targets):

- `core.py` (2,751 lines): probe/scan/natural sort (superseded by QUILL's),
  plus the parts QUILL lacks — `trim_silence_item`, `split_into_files`,
  `trim_file`, `apply_fades`, `apply_tempo`, `probe_audio_stats`,
  `get_file_peak_db`, `_clamp_chapters`, chapter report, size estimation,
  pre-flight uniform-stream checks, master-file detection
  (`is_probable_master`), Opus/FLAC build variants (QUILL policy: keep as
  accepted inputs only; MP3/M4B remain the chaptered outputs).
- `player.py` (809) + `audio_engine.py` (243): chapter-aware accessible
  player on libmpv (`MpvAudioEngine`). Port the panel to QUILL idioms; decide
  engine per section 7.
- `acx.py` (137): per-file ACX measurement — merges into `loudness.py`.
- `lookup.py` (148): MusicBrainz + Open Library title/author search.
- `rss.py` (158): podcast RSS 2.0 + iTunes + Podcasting 2.0 namespace feed
  generation, chapters.json sidecar writer.
- `publish/` (sftp, destinations, credentials, service): SFTP publishing with
  saved destinations. Credentials move to QUILL's DPAPI credential manager.
- `auphonic/` (auth, client, presets, polling, estimate, validate, service,
  db, output_filter): full Auphonic post-production client.
- `wizard.py` (766): reference for tone and flow of a guided, accessible,
  explain-as-you-go wizard.
- `watcher.py` concepts: fold into QUILL's existing watch-folder framework as
  a new watch action ("Build audiobook from new folder").
- Chapter list import/export code paths in `app.py` (Audacity/CUE/
  timestamps/Podcasting 2.0 JSON) — extracted into a new wx-free module.

Explicitly NOT ported (QUILL already owns these concerns):

- `ai/` (whisper/faster-whisper/parakeet transcription) — QUILL's offline
  speech stack already covers it.
- `updates.py`, `tray.py`, `autostart.py`, `notify.py`, `a11y.py`,
  `settings.py`, `manifest.py`, `docs.py`, `feature_flags.py` — QUILL has its
  own updater, app model, Prism announcements, settings schema, and
  experimental-feature gating.
- The standalone CLI (QUILL's CLI surface is a separate conversation; job
  files give most of the repeatability).

## 5. The user experience, in detail

### 5.1 Opening the Studio

`Tools > Speech > Audio Studio...` opens a wizard (via `_show_modal_dialog`,
`apply_modal_ids`, full keyboard contract). Title bar: "QUILL Audio Studio".
The first page greets and branches. Focus lands on the first radio button;
JAWS/NVDA read the page title, one-sentence purpose, then the choice list.

Page 1 — "What would you like to make?"

- ( ) Narrate documents into an audiobook
      "Turn Word, HTML, Markdown, EPUB, or text files into spoken audio with
      chapters." (default)
- ( ) Combine audio files into an audiobook
      "Merge a folder of MP3 or other audio files into one chaptered book —
      one chapter per file."
- ( ) Edit an existing audiobook
      "Open a chaptered MP3 or M4B to listen, fix chapters and tags, split or
      merge, and save."
- [ ] Use my saved settings for this folder (shown when a project profile or
      job file is detected; checking it pre-fills every later page and enables
      "Skip to summary")

Buttons on every page: Back, Next, Skip to summary (enabled once required
fields are satisfiable), Cancel. Every page has a one-line purpose sentence
as a live-region-free static text directly under the title so screen readers
encounter context before controls.

### 5.2 Journey A — documents to audiobook

Page A2 — "What should I read?"
- Source: the open document, or a folder (browse + recent folders combo).
- File types (checkbox list: Word, HTML, Markdown, Text, EPUB), include
  subfolders, include/exclude patterns behind a "More filters" disclosure.
- A live, announced count: "14 documents found, about 92,000 words." The
  count re-runs on the task pool; the field is a read-only text that updates
  via wx.CallAfter and is announced politely once settled.

Page A3 — "Who should read it?"
- Engine and voice pickers (the existing accessible combos), Preview voice
  button (speaks one sample sentence), rate/pitch where supported.
- Round-robin narration (opt-in disclosure): the existing add-from-combobox +
  reorderable list pattern — "each chapter gets the next voice."
- Translated editions (opt-in disclosure): the existing per-language picker.
- The page states plainly which choices are free/offline and which are
  metered cloud voices; the cost estimate appears on the summary page.

Page A4 — "How should chapters work?"
- ( ) Each file becomes one chapter (default for folders)
- ( ) Each heading starts a new chapter — with a level picker
      ("Chapters start at heading level: 1 / 1-2 / 1-3") and a live preview
      list of the first 20 resulting chapter titles in an accessible ListBox
      so the user can audit the split before committing.
- ( ) One single track, no chapters
- Options: combine empty headings into the next chapter (the ACB rule),
  chapter transition sound (page-turn default, sound-pack override), silence
  gap between chapters (0-5000 ms spinner).
- [ ] Let me review and edit the chapter list before the book is built
      (default on) — this routes the run through the Chapter Workbench
      (section 5.5) after synthesis.

Page A5 — Book details (shared, section 5.6).
Page A6 — Output and mastering (shared, section 5.7).
Page A7 — Summary and start (shared, section 5.8).

### 5.3 Journey B — audio files to audiobook

Page B2 — "Where are the recordings?"
- Folder picker; detected files appear in an accessible list, natural-sorted,
  with per-file duration, format, sample rate, channels, bitrate (columns).
- Probable existing masters are auto-excluded and said so ("2 files that look
  like previous builds were set aside — press Include to add one back").
- Pre-flight verdict, in words not icons: "All 24 files share the same
  format; the build will be lossless and fast." or "3 files differ in sample
  rate; the build will re-encode. Details lists which."
- Live output size estimate and total duration, announced when settled.

Page B3 — "Chapter titles"
- Titles from: filenames (cleaned of track numbers) / each file's embedded
  ID3 title / a numbered pattern ("Chapter {n}").
- Per-item silence trim (opt-in): trim leading/trailing silence from each
  file before the merge, with threshold defaults.
- Auto-chapter by silence (for the single-big-file case, offered when the
  folder holds exactly one long file): detect gaps of N seconds below X dB
  and propose chapter marks — the proposal opens in the Chapter Workbench for
  human review, never applied blind.
- The Chapter Workbench review step is ALWAYS on for this journey (matches
  the shipped behavior for pre-recorded folders).

Then the shared pages: Book details, Output and mastering, Summary.

### 5.4 Journey C — edit an existing audiobook

Page C2 — "Open a book"
- File picker filtered to MP3/M4B; recent books list.
- On open: chapters, tags, and cover are read; the user lands directly in the
  Chapter Workbench with the player loaded — this journey IS the Workbench.
- Save writes chapters/tags in place for MP3 (mutagen), Save As re-muxes for
  M4B; the wizard frame offers "Save", "Save As...", and "Export chapter
  list..." instead of "Start".

### 5.5 The Chapter Workbench (the heart of the studio)

One resizable dialog, shared by all three journeys, built from the shipped
`audiobook_chapter_editor_dialog.py` plus the ported player. Layout, top to
bottom, in tab order:

- Chapter list: an accessible ListView — columns Number, Title, Start,
  Duration, Source file. Standard QUILL list keyboard contract. F2 or Enter
  renames in place (announced). Alt+Up/Down reorders. Del removes.
  Ctrl+M merges the selected chapter into the previous one.
- Player panel (ported ChapterForge PlayerPanel): Play/Pause (Space when the
  list has focus plays the selected chapter), Stop, Previous/Next chapter,
  Rewind/Forward with a configurable step, position slider (arrow keys =
  step, PageUp/Down = minute), volume. The current chapter and position are
  announced on chapter change ("Chapter 4: The Long Road, 12 minutes 40
  seconds"). Everything reachable and labeled; slider announces value in
  minutes and seconds, not raw milliseconds.
- Surgery buttons: Split at playhead (creates a new chapter boundary exactly
  where playback stands — the killer feature for fixing a bad split by ear),
  Set chapter start to playhead (retime), Merge with previous, Restore
  original list.
- Import... / Export... menus: Audacity labels, CUE sheet, plain timestamps,
  Podcasting 2.0 JSON. Import proposes; the list shows the result; nothing is
  final until OK.
- A status line reads the running total: "24 chapters, 7 hours 41 minutes."

The Workbench appears: after synthesis (journey A, opt-in), before the merge
(journey B, always), immediately (journey C). In mid-run cases it is
marshalled to the UI thread exactly as the shipped editor is today.

### 5.6 Book details page (shared)

- Title, Author (narrator), Album/Series, Genre, Year, Comment; per-field
  labels, standard grid.
- Cover: auto-detected candidate shown by filename with a Browse override and
  a "No cover" choice. The chosen image's filename and pixel size are stated
  in text.
- "Look up book details..." button: searches MusicBrainz and Open Library by
  the typed title/author, presents results in an accessible list (title,
  author, year, source), and fills the fields on selection. Network call is
  consent-gated the first time ("QUILL will contact MusicBrainz and Open
  Library to search public book records. No account is needed. Allow?") and
  registered in the egress audit.

### 5.7 Output and mastering page (shared)

- Format: MP3 (chapters readable everywhere) or M4B (audiobook apps,
  bookmarkable). One sentence of guidance per choice. Opus/FLAC remain
  accepted as inputs; they are not chaptered outputs (unchanged policy).
- Quality: the existing MP3 VBR picker / AAC bitrate.
- Loudness: Off / Normalize (two-pass loudnorm) / Normalize to ACX — with the
  post-build verdict promise spelled out ("after the build QUILL measures the
  book and tells you whether it lands in ACX's window").
- Inter-chapter gap (if not set earlier), optional fade-in/fade-out per
  chapter (ported `apply_fades`), optional tempo (0.75x-1.25x, ported
  `apply_tempo`, off by default).
- Destination: save-as path (suggested from the book title), temp folder
  disclosure, existing-file policy.
- Extras (disclosure): write Podcasting 2.0 chapters.json sidecar; write a
  chapter report text file; keep per-chapter files as well as the master
  (ported `split_into_files` powers the reverse trip too).

### 5.8 Summary and start

A single readable page — a definition list, not a table — stating every
choice in plain sentences, in the order the pages presented them, each with a
"Change" link-button that jumps back to that page. Then:

- The cost estimate line for any metered cloud voice (existing
  `confirm_cloud_cost` machinery), or "This run is entirely offline and
  free."
- The size and duration estimate.
- [Start] — runs on the task pool with the existing announced progress
  dialog (percentage, minimizable to the status bar). The conversion log
  opens in the output folder before work starts, as today.

Completion dialog: "Your book is ready. 24 chapters, 7 hours 41 minutes,
412 MB. Loudness: within the ACX window (RMS -19.8 dB, peak -3.4 dB).
Chapter count verified." Buttons: Play in Audio Studio (opens journey C on
the new file), Open folder, Save these settings as the folder's defaults
(project profile), Save a job file..., Close. Post-build verification
(re-read the file, confirm chapter count) runs before this dialog and any
mismatch is stated honestly.

### 5.9 Returning users and automation

- Project profiles: every Start updates `.quill/speech-project.json` (already
  shipped); the Studio adds the journey-B fields (title source, gaps, trim,
  mastering) to the same schema. Re-opening the Studio on a known folder
  offers "Use my saved settings" on page 1 and "Skip to summary".
- Job files: "Save a job file..." writes a small, hand-editable UTF-8 text
  file (QUILL flavor of `.cfjob`; extension `.quilljob`, schema-validated
  JSON with comments stripped) pinning order, titles, tags, and options.
  Opening a job file (File > Open, or page 1 detection) pre-loads the whole
  wizard. This is the repeatability story for power users.
- Watch folder: a new watch action "Build audiobook from new subfolder" —
  when a watched folder gains a subfolder of audio, build with that folder's
  project profile/job file and notify via the existing announcement path.
  Consent and Safe Mode gating identical to existing watch actions.

### 5.10 Publishing (consent-gated, later phases)

- Podcasting 2.0 chapters.json sidecar: local file write, ships early.
- RSS podcast feed: "Publish > Update podcast feed..." generates/updates an
  RSS 2.0 + iTunes + podcast-namespace feed for a folder of built masters.
  Local generation is free; any upload is SFTP below.
- SFTP upload: saved destinations (host, path, username), credentials in
  Windows Credential Manager via the existing DPAPI path, host keys via
  QUILL's SSH policy (RejectPolicy default, trust-first-use opt-in) — the
  ported ChapterForge sftp code is replaced by QUILL's own SSH client so the
  invariant holds.
- Auphonic: "Send to Auphonic..." after a build — preset pick, estimate,
  upload, poll, fetch results. API key via credential manager; every endpoint
  in the egress audit; entirely absent in Safe Mode.

### 5.11 Accessibility contract (non-negotiable, inherited and extended)

- Every dialog through `_show_modal_dialog` + `apply_modal_ids`; dialog
  inventory and button-contract gates must pass.
- No checkbox lists; the add/reorder ListBox pattern for collections.
- Every control labeled; every state change that matters is announced via the
  Prism bridge; sliders speak human time.
- The wizard is fully operable with keyboard only; Back/Next are default/esc
  coherent; focus lands deterministically on page change (first interactive
  control) and the page purpose precedes controls in reading order.
- Long operations never block the UI thread; announcements from workers go
  through wx.CallAfter.
- All new strings through `_()` for i18n; menu items through `_menu_label`.

## 6. Architecture and code mapping

New/changed core (wx-free, mypy-strict):

- `quill/core/speech/audiobook.py` — grows: pre-flight checks, size
  estimate, master detection, per-item silence trim, verification. Watch the
  module size budget; split into `audiobook_build.py` if it nears the cap.
- `quill/core/speech/chapters.py` — grows: clamping, retime/split/merge plan
  operations.
- `quill/core/speech/chapter_io.py` — NEW: Audacity/CUE/timestamps/
  Podcasting 2.0 JSON import/export (pure text transforms, heavily unit
  tested).
- `quill/core/speech/silence.py` — NEW: silence detection (ffmpeg
  silencedetect parse) and trim.
- `quill/core/speech/loudness.py` — grows: ACX per-file measurement from
  `acx.py`.
- `quill/core/speech/audio_edit.py` — NEW: trim/fades/tempo/split_into_files
  ffmpeg helpers.
- `quill/core/speech/job_file.py` — NEW: `.quilljob` schema + load/save
  (atomic writes, schema in `quill/core/schemas/`).
- `quill/core/metadata_lookup.py` — NEW: MusicBrainz/Open Library search
  (net-egress-audited, timeout-bounded, no keys).
- `quill/core/publish/` — NEW package: `rss.py`, `destinations.py`,
  `auphonic/` (ported, re-based on QUILL http/consent/credential idioms).

UI (gradual typing, wx):

- `quill/ui/audio_studio/` — NEW package: `wizard.py` (frame + page
  plumbing), `pages_documents.py`, `pages_audio.py`, `pages_shared.py`
  (details/output/summary), `chapter_workbench.py` (list + surgery),
  `player_panel.py` (ported PlayerPanel), `completion.py`. Keeping pages in
  separate modules respects the size budget from day one.
- `quill/ui/batch_speech_runner.py` — becomes the Studio's execution engine
  (rename in a later cleanup; keep the module now to limit churn).
- `quill/ui/batch_speech_export_dialog.py` — retired once the wizard reaches
  parity; its `_collect` contract (BatchSpeechRequest) is the wizard's output
  type, so the runner does not change shape.
- `main_frame_speech.py` mixin gains the `tools.audio_studio` handler; the
  menu item is renamed in `main_frame_menu.py`; old command id aliased.

Player engine decision:

- ChapterForge uses libmpv (`MpvAudioEngine`). Options: (a) bundle libmpv —
  best format coverage and gapless seeking, adds a ~2 MB+ native dependency
  to the installer; (b) wx.media (WMP backend) — zero new dependency, weaker
  format/seek behavior; (c) port MpvAudioEngine with graceful fallback to
  wx.media when libmpv is absent, and offer libmpv through the existing
  on-demand assets-v1 download flow like ffmpeg/whisper models.
  Recommendation: (c). The engine interface is small (load/play/pause/seek/
  position/events) so both backends implement one protocol.

Invariant compliance checklist:

- Threading: all builds/probes/lookups on QuillTaskManager; UI via
  wx.CallAfter. The Workbench mid-run marshalling reuses the shipped pattern.
- Persistence: job files and profiles via write_json_atomic + schema.
- Safe Mode: lookup, RSS upload, SFTP, Auphonic, and watch actions disabled.
- Network egress: new entries for MusicBrainz, Open Library, Auphonic, SFTP
  destinations; consent dialogs on first use.
- Credentials: DPAPI/Credential Manager only; never in settings JSON.
- SSH: QUILL's client and host-key policy for SFTP, not paramiko-direct.
- Subprocesses: all ffmpeg/ffprobe through safe_subprocess with
  CREATE_NO_WINDOW and timeouts.
- Gates: dialog inventory, button contract, banned patterns, module size
  budgets (new modules get entries), menu lint, quillin lint untouched.

## 7. Phasing (each phase ships, tests, and documents independently)

Phase 1 — The Studio shell and rebrand.
- Wizard frame + page plumbing + journey A/B routing built ON TOP of the
  existing runner (BatchSpeechRequest unchanged). Journey A and B reach
  parity with today's dialog; old dialog retired; menu renamed; command id
  aliased. Chapter Workbench = the existing editor dialog embedded unchanged.
- Tests: wizard page navigation/state unit tests; request-equivalence tests
  (same inputs through old dialog fixtures and new wizard produce identical
  BatchSpeechRequest); existing runner suite untouched and green.
- Docs: PRD 5.25e rewritten as "QUILL Audio Studio"; user guide chapter;
  CHANGELOG.

Phase 2 — Chapter Workbench power tools.
- chapter_io.py (import/export), split/retime/merge-plan operations,
  inter-chapter gaps and fades in the build, silence trim, silence
  auto-chapter proposal, pre-flight checks, size estimate, post-build
  verification + chapter report.
- Tests: golden-file tests for every import/export format; chapter math
  property tests (splits/merges preserve total duration; clamping); ffmpeg
  paths behind fakes as in the existing audiobook tests.

Phase 3 — The player and journey C.
- audio engine protocol + wx.media backend + optional libmpv (assets-v1
  on-demand); PlayerPanel port; open-existing-book flow; save-in-place MP3 /
  re-mux M4B.
- Tests: engine protocol fakes for panel logic; tag/chapter round-trip tests
  on fixture files; UIA smoke for the Workbench in the CI-only suite.

Phase 4 — Book details lookup + job files + completion polish.
- metadata_lookup.py + consent + egress entries; .quilljob schema/load/save +
  page-1 detection; completion dialog with Play-now and profile/job saves.

Phase 5 — Publishing.
- chapters.json sidecar (early, local); RSS feed generation; SFTP via QUILL
  SSH + credential manager + destinations UI; Auphonic client + presets +
  polling. Each behind consent, egress audit, and Safe Mode.

Phase 6 — Automation.
- Watch action "Build audiobook from new subfolder" honoring the folder's
  profile/job file.

## 8. Risks and open questions

- libmpv licensing/packaging: LGPL dynamic linking is fine, but confirm the
  assets-v1 delivery and installer story before Phase 3 commits to it.
- EPUB as an input: QUILL's io layer must already read it for journey A to
  list it — verify reader coverage; if absent, EPUB intake is its own small
  workstream and should be cut from page A2 until real.
- Auphonic is an account service; UX must degrade gracefully with no key and
  stay invisible in Safe Mode. Validate demand before polishing presets UI.
- The old dialog's translated-audio and round-robin sections are dense;
  folding them into wizard disclosures needs real screen-reader walkthroughs
  (JAWS + NVDA) before Phase 1 is called done.
- `batch_speech_runner.py` (987 lines) will attract additions; watch the
  budget and extract build-orchestration into core when it strains.
- Heading-level chapter picker (A4) needs `document_speech` to expose its
  section split with level filtering — confirm the seam, else add it.

## 9. Beyond the port — options for greatness and flexibility

Ideas that go past ChapterForge parity, ranked by leverage. Each is optional
and none blocks the phases above; the strongest candidates ride existing
QUILL machinery, which is what makes them cheap magic rather than scope
creep.

Narration magic (rides the AI gateway and speech stack):

- AI chapter titles. When titles come from filenames like `track07.mp3` or
  from heading-less text, offer "Suggest titles with AI": each chapter's
  opening text (or a transcript snippet for audio) is summarized into a
  short title through the configured AI provider. Proposals land in the
  Workbench for review; consent-gated, skipped offline, free with a local
  model.
- Opening and closing credits. Auto-generate the standard audiobook frame
  ("<Title>, written by <Author>. Narrated by <Voice>.") as synthesized
  first/last chapters, from a template the user can edit. One checkbox on
  the Book details page.
- Voice casting. Evolve round-robin into assignment: this voice for chapter
  titles, that voice for body; or per-document voice overrides in the
  Workbench (column: Voice). The rotation machinery already exists; casting
  is a mapping instead of a cycle.
- Audition build. "Build a sample" renders only the first chapter with the
  full mastering chain so the user can judge voice, pace, and loudness in
  two minutes instead of discovering a problem after an eight-hour run.
- Incremental rebuilds. Cache per-chapter WAVs keyed by content hash +
  voice + options; a re-run of a 40-document book after editing one chapter
  re-synthesizes one chapter. Transforms the Studio from a one-shot tool
  into an iterative authoring loop. (Largest engineering item on this list;
  worth its own phase if adopted.)
- Pronunciation preflight. The existing dry-run already writes the exact
  spoken text; add a pass that flags likely trouble (unknown proper nouns,
  number-heavy lines) and deep-links into Manage Pronunciations.

Library and format flexibility:

- Batch library mode (ChapterForge had this; adopt): a folder of book
  subfolders builds every book in one run, each with its own
  profile/job file. Pairs naturally with the watch action.
- Podcast episode mode: the same chapter plan can emit one file per chapter
  plus the RSS feed (episodes = chapters) instead of a single master —
  `split_into_files` plus `rss.py` already cover the mechanics.
- DAISY bridge: QUILL ships DAISY export; offer "Also produce a DAISY
  talking book" from the same wizard run for library-service users. Same
  chapter plan, second renderer.
- Hybrid books: mixing narrated documents and pre-recorded audio in one
  book is already half-shipped (produced + pre-recorded merge); surface it
  deliberately in journey A ("include audio files found alongside the
  documents") with per-chapter loudness matching so mixed sources sit at
  one level.
- Companion text. Because journey A starts from the source text, emit an
  optional HTML/Markdown companion: the full text (or per-chapter summaries)
  with chapter timestamps — instant show notes for podcasts, a reading copy
  for deaf-blind readers, and a debugging artifact for free.
- Per-chapter links and images in the Podcasting 2.0 sidecar (the format
  supports them; the Workbench gains two optional columns).

Player and listening extras:

- Listening position memory per book (resume where you left off), stored in
  app data keyed by file hash.
- Playback speed with pitch preservation (atempo is already ported for the
  build; reuse in the player).
- "Where am I?" key: announce book title, chapter, position, and time
  remaining in chapter and book — the screen-reader equivalent of glancing
  at a progress bar.

Recommended adoption: batch library mode and the audition build are cheap
and high-value (Phase 2/4 riders); AI titles, credits, and companion text
are Phase 4 candidates; incremental rebuilds and podcast episode mode
deserve their own decision after the core ships.

## 10. Retiring the source folders

Goal confirmed: everything lands in QUILL and both source folders go away.

- `S:\code\Chapter Forge` — stale copy (files dated 2026-06-04, no git, a
  strict subset of forum's 2026-06-09 state plus an odd 1.5.0 version
  string). Safe to retire NOW after a single diff pass to confirm nothing
  unique (a quick tree compare against forum; the earlier survey found only
  older, smaller versions of the same modules). Nothing in QUILL references
  it.
- `s:\code99\forum` — canonical, git-clean except two untracked plan files
  (`plan2.md`/`plan2.html`), remote `github.com/BITS-ACB/chapterforge`.
  Retire at the END, gated on parity, with this exit checklist:
  1. All phases above shipped, each with its QUILL test suite green — the
     phase tests ARE the parity proof; no feature is "ported" until a QUILL
     test exercises it.
  2. Copy test fixtures worth keeping into QUILL's test assets (the
     `samples/` chaptered MP3 + cover are real-audio fixtures QUILL's
     chapter round-trip tests can use; mind repo size — trim or regenerate
     short fixtures if needed).
  3. Mine `docs/USER_GUIDE.md` for wording worth carrying into QUILL's user
     guide chapter; commit or discard the untracked plan2 files.
  4. Final commit: README banner "Superseded by QUILL Audio Studio" with a
     link, then ARCHIVE the GitHub repo (read-only — history, issues, and
     releases stay reachable forever).
  5. If any real users run the standalone app, publish one last GitHub
     release note pointing at QUILL (ChapterForge's built-in update check
     reads GitHub releases, so existing installs will see it).
  6. Delete both local folders. History lives on GitHub; nothing local is
     load-bearing after step 4.

## 11. Decision log

- 2026-07-04: Name = "QUILL Audio Studio"; wizard REPLACES the batch dialog
  (single path, profiles keep returning users fast); canonical ChapterForge
  source is `s:\code99\forum` (git, 2026-06-09, full feature set) — the
  `S:\code\Chapter Forge` copy is stale and ignored; the chapter-aware player
  is IN scope ("the player should come along with it"); scope directive:
  "all features here if at all possible, be complete" — everything portable
  is in the plan except the transcription stack, updater, tray, and other
  concerns QUILL already owns; end state: both source folders are retired
  once parity is proven (section 10).
