# QUILL Audio Studio — Implementation Plan

Working tracker for the consolidation designed in
[quill-audio-studio-plan.md](quill-audio-studio-plan.md) (the approved design,
formerly `book.md`). Executed inline on branch `feature/audio-studio`.

Ground rules for every task:

- Full parity first: no shipped option (sounder, gaps, round-robin,
  translations, dry run, spoken-text sidecars, profiles, ACX, review editor)
  may be lost in the rebrand. The `BatchSpeechRequest` contract is the
  parity checklist.
- All new UI strings through `_()`; menu items through `_menu_label`.
- Dialogs via `_show_modal_dialog` + `apply_modal_ids`; after adding any
  dialog surface run `python -m quill.tools.dialog_inventory --write` and
  commit the snapshot diff.
- Core logic is wx-free under `quill/core/` (mypy-strict); UI under
  `quill/ui/audio_studio/`.
- Tests + docs (PRD, user guide, CHANGELOG) ship with each phase.

## Phase 1 — Studio shell and rebrand

Deliverable: `Tools > Speech > Audio Studio...` opens a guided wizard that
replaces `BatchSpeechExportDialog` at full option parity, producing the same
`BatchSpeechRequest` consumed by the unchanged `batch_speech_runner`.

Files:
- Create `quill/ui/audio_studio/__init__.py` — `show_audio_studio(frame) ->
  BatchSpeechRequest | None` (constructs the wizard with the runner's
  engine/voice/defaults plumbing).
- Create `quill/ui/audio_studio/request.py` — `BatchSpeechRequest` moved
  verbatim + the shared constants (extensions, policies, formats, modes).
- Create `quill/ui/audio_studio/wizard.py` — `AudioStudioWizard(wx.Dialog)`:
  journey-aware page sequence, Back/Next/Start, step announcements,
  build_request().
- Create `quill/ui/audio_studio/pages_start.py` — journey radio page.
- Create `quill/ui/audio_studio/pages_documents.py` — DocSourcePage,
  VoicesPage (engine/voice/preview/rate/speed/round-robin/translations),
  ChaptersPage (mode, headings, combine, sounder + volume, gaps),
  OutputPage (format, existing policy, normalize, dry run, temp folder,
  spoken-text sidecar).
- Create `quill/ui/audio_studio/pages_audio.py` — AudioSourcePage (folder of
  recordings, recursive).
- Create `quill/ui/audio_studio/pages_shared.py` — BookPage (tags, cover,
  format, ACX, review; forced-on for the audio journey), SummaryPage.
- Modify `quill/ui/batch_speech_runner.py` — import request from the new
  module; `run_batch_export_to_speech` opens the wizard.
- Modify `quill/ui/main_frame_menu.py` — item renamed "&Audio Studio...",
  command id `tools.audio_studio`.
- Delete `quill/ui/batch_speech_export_dialog.py`.
- Tests: replace `tests/unit/ui/test_batch_speech_export_dialog.py` with
  `tests/unit/ui/test_audio_studio_wizard.py` covering the same collection
  behaviors (extension grouping, engine switch reload, rr add/reorder/
  remove/duplicate/clear-on-engine-change, translation add/remove/provider,
  format/mode/policy mapping, book fields, journey routing, sounder volume,
  gaps round-trip) plus journey-B request shape (extensions=(), make_book
  True, review forced).

Journey page sequences:
- documents: Start > DocSource > Voices > Chapters > Output > Book > Summary
- audio: Start > AudioSource > Book > Summary

## Phase 2 — Chapter Workbench power tools

- Create `quill/core/speech/chapter_io.py` — parse/format Audacity labels,
  CUE, plain timestamps, Podcasting 2.0 JSON. Pure text; golden tests.
- Create `quill/core/speech/audio_edit.py` — trim/fades/tempo/split helpers
  (ffmpeg via safe_subprocess).
- Create `quill/core/speech/silence.py` — silencedetect parse, auto-chapter
  proposal, per-item trim.
- Grow `chapters.py` — split/retime/merge plan ops + clamping.
- Grow `audiobook.py` — preflight uniform-stream check, size estimate,
  master detection, post-build verification, chapter report.
- Grow `loudness.py` — per-file ACX measurement.
- Workbench dialog: extend `audiobook_chapter_editor_dialog.py` toward
  `quill/ui/audio_studio/chapter_workbench.py` (list + import/export +
  surgery buttons; player wires in Phase 3).

## Phase 3 — Player + edit-existing journey

- Create `quill/ui/audio_studio/audio_engine.py` — engine protocol +
  wx.media backend (+ libmpv backend when present).
- Create `quill/ui/audio_studio/player_panel.py` — ported PlayerPanel.
- Journey C pages: open existing MP3/M4B into the Workbench; save-in-place
  (mutagen) / Save As re-mux (M4B).
- Core: read chapters/tags from existing files into the plan model.

## Phase 4 — Lookup, job files, completion, narration extras

- `quill/core/metadata_lookup.py` (MusicBrainz + Open Library; consent +
  egress audit entries).
- `quill/core/speech/job_file.py` + schema — .quilljob save/load; wizard
  detection on page 1.
- Completion dialog: verified stats, ACX verdict, Play now, save profile/job.
- Extras: AI chapter titles (gateway, consent), opening/closing credits,
  audition build (first chapter only).

## Phase 5 — Publishing

- `quill/core/publish/rss.py`, `chapters_sidecar.py`, `destinations.py`,
  `auphonic/`. SFTP through QUILL's SSH client + credential manager.
- Consent per destination, egress audit entries, Safe Mode gating.

## Phase 6 — Automation + library extras

- Watch action "Build audiobook from new subfolder".
- Batch library mode; podcast episode mode; DAISY bridge; companion text;
  player position memory + speed + where-am-I.

## Status log

- 2026-07-04: branch `feature/audio-studio` created; design doc moved to
  docs/planning/quill-audio-studio-plan.md; Phase 1 underway.
- 2026-07-04: ALL SIX PHASES SHIPPED on `feature/audio-studio` (six commits,
  one per phase). Beyond the plan, the "greatness" extras landed too:
  audition builds, spoken credits, job files, book lookup, library mode,
  watch action, split-into-episodes, listening-position memory, playback
  speed, Where-am-I. Deliberately NOT built (recorded, not dropped):
  - AI chapter titles — needs transcript text for audio chapters
    (whisper pass); revisit when the Workbench gains transcript access.
  - DAISY bridge — QUILL's DAISY export is document-driven; bridging an
    audio-only master is a different pipeline. Recommend as its own item.
  - Companion text/show notes — the spoken-text sidecars cover the debug
    case; a formatted HTML companion is a future nicety.
  - Incremental per-chapter rebuild cache — worth its own design pass.
  - libmpv engine backend — the engine protocol is ready (`set_rate`,
    seek semantics mirror mpv); deliver libmpv via assets-v1 when wanted.
  Source-folder retirement (design doc section 10) can proceed once this
  branch merges and Jeff validates with a real screen reader.
