# QUILL Batch Document-to-Speech Export

## Implementation Plan: Folder-Scale Document-to-Audio with Voice/Speed Selection, Live Preview, and Pronunciation Dictionaries — in the Background

**Project:** QUILL
**Feature area:** Speech / audio export (with a cross-cutting pronunciation-dictionary feature for all read-aloud)
**Primary target:** Windows 11 with wxPython
**Primary accessibility goal:** A screen-reader-first batch workflow that lets a blind keyboard user convert a folder of documents (Word, Markdown, HTML, and more) into spoken audio with a chosen voice and speed, entirely in the background.
**Status:** Proposed implementation plan
**Date:** 2026-06-24

---

# 1. Executive Summary

QUILL already contains the hard half of this feature. `quill/core/speech/batch_export.py` performs the full pipeline — folder scan, text extraction, TTS polishing, per-engine synthesis, mirrored `.wav` output, per-file progress, cancellation, and per-file error isolation — and it is `wx`-free and thread-safe by design.

The problem is that **the engine is headless**. `run_batch_export` and `BatchExportOptions` have zero callers. There is no dialog, no menu entry, and no test coverage. The module's own docstring promises a UI wrapper ("the UI layer wraps `run_batch_export` in its own thread") that does not exist.

What ships today under **Tools → Export to Speech Audio…** (`generate_speech_audio` in `main_frame.py`) is a *single-document, current-buffer-only* save to one `.wav` via a file dialog. It does not touch the batch module and cannot process a folder.

This plan delivers the missing layer: a fully accessible batch dialog, menu wiring, background execution on `QuillTaskManager`, voice and speed selection per engine, a **live Preview** button so users audition voice and speed before committing, persisted defaults, comprehensive tests for the core module, and a set of cheap, high-value enhancements (`.txt` support, skip-existing/resume, optional MP3 output).

It also introduces a **pronunciation dictionary** feature (§4.7): user-defined words and respellings, scoped on two axes — **location** (**global**, app-wide, vs **project**, stored in the project folder and active only for that folder of files) and **engine** (**all engines** vs **synthesizer-specific**) — all selectable. Crucially this lives in the shared speech pipeline, so a pronunciation fix made once is heard everywhere — interactive Read Aloud, previews, and batch alike — not just in batch; and a project dictionary travels with the folder it belongs to.

The guiding principle: **do not rewrite the engine.** It is well-factored. We build around it, test it, and make it reachable and magical.

---

# 2. Current State Audit

## 2.1 What exists and works

**`quill/core/speech/batch_export.py`** (core, strict-typed, `wx`-free):

- `SUPPORTED_EXTENSIONS = (".md", ".html", ".htm", ".docx")`.
- `BatchExportOptions` dataclass with source/output folders, recurse flag, extension filter, and per-engine settings (SAPI5 voice/rate/volume, DECtalk voice/rate/dictionary, Piper exe/model, Kokoro voice/speed, eSpeak exe/voice/rate).
- `BatchFileResult` dataclass with `status` (`pending`/`processing`/`done`/`error`/`skipped`), error string, and duration.
- `discover_files(folder, extensions, recursive)` — sorted, extension-filtered glob.
- `_output_path_for(...)` — mirrors the source's relative path under the output root with a `.wav` suffix.
- `_synthesize_one(...)` — dispatches to the correct `read_aloud` synthesis function per engine, with `pyttsx3 → sapi5` id migration.
- `run_batch_export(options, results, on_progress, cancel_event)` — processes each file in order, updates results in place, calls `on_progress(done, total, result)` after every file, honors the cancel event, and isolates per-file failures.

**`quill/core/speech/text_polish.py`** (core, `wx`-free):

- `extract_text(path)` for `.md`, `.html/.htm`, `.docx` (stdlib-only: zip + `ElementTree` over `word/document.xml`).
- `polish_for_tts(text)` — abbreviation expansion, URL → "link", markdown stripping, whitespace normalization.

**Synthesis backends** in `quill/core/read_aloud.py`: `synthesize_to_file_with_sapi5`, `synthesize_to_file_with_dectalk`, `synthesize_with_piper`, `synthesize_with_kokoro`, `synthesize_with_espeak`.

**Settings** (`quill/core/settings.py`) already persist per-engine read-aloud preferences: `read_aloud_engine`, `read_aloud_voice`, `read_aloud_rate`, `read_aloud_volume`, `read_aloud_dectalk_voice/rate`, `read_aloud_piper_model`, `read_aloud_kokoro_voice/speed`, `read_aloud_espeak_voice/rate`. Rate is clamped to 80–450; volume 0–100.

## 2.2 What is missing or weak

| # | Gap | Severity |
|---|-----|----------|
| 1 | No UI dialog and no menu entry reach `run_batch_export`. The feature is unreachable. | Blocker |
| 2 | No voice/speed selection surface for batch (the `BatchExportOptions` fields are never populated). | Blocker |
| 3 | Zero tests for `batch_export.py` and `text_polish.py`. Core, strict-typed code with no coverage. | High |
| 4 | No `.txt` support — a glaring omission given "Word, Markdown, HTML, etc." | Medium |
| 5 | `.docx` extraction is shallow: paragraph `<w:t>` only; skips tables, headers/footers, footnotes, list ordering. | Medium |
| 6 | No skip-existing / overwrite handling — a re-run silently clobbers prior output; no resume. | Medium |
| 7 | WAV-only output; no MP3 despite an existing `ffmpeg` module and `ai_tts_export_mp3` path. | Medium |
| 8 | No chunking for very long documents (`tts_chunk.py` exists but is unused here). | Low |
| 9 | No pre-run preview (file count, estimated size/time). | Low |

## 2.3 Deliberate exclusions (decisions, not omissions)

- **Cloud engines in batch** (Gemini / cloud TTS): excluded for v1 due to cost, per-call consent, and the `network_egress_audit` contract. Local engines only.
- **Parallel synthesis**: excluded. Serial is safer — native engines (SAPI, Piper, DECtalk) are not reliably thread-safe, and serial keeps progress and cancellation deterministic.

---

# 3. Product Vision

A user opens **Tools → Batch Export to Speech Audio…**. A dialog appears with focus on the source-folder field. They:

1. Choose a source folder (and whether to recurse).
2. Choose which file types to include (Word, Markdown, HTML, plain text).
3. Choose an output folder (defaults to a sibling `Audio` folder).
4. Pick an engine, a voice, and a speed — pre-filled from their saved Read Aloud preferences — and press **Preview** to hear the chosen voice at the chosen speed before committing.
5. Optionally choose output format (WAV or MP3), whether to skip files already exported, which **pronunciation dictionaries** are active so names and jargon are spoken correctly, and — for documents with headings — whether to **chapterize**: one file with chapter markers (named from the headings) or a separate file per article, with an optional **transition tone** between articles and a configurable **pause** between them (§4.8). Think "read me this newspaper and let me jump between stories."
6. Hear an announced summary: *"42 files found. Estimated output: about 180 megabytes."*
7. Press **Start**. The dialog shows a live, screen-reader-friendly list: each file announces *"Processing 7 of 42: chapter-three.docx"* then *"Done"* / *"Skipped"* / *"Error: …"*.
8. Work runs in the background on the task manager; the user can keep editing or cancel at any time.
9. On completion: *"Batch export complete. 40 succeeded, 1 skipped, 1 error. Output saved to …"* — with a button to open the output folder.

Everything is keyboard operable, every state change is announced, and nothing blocks the UI thread.

---

# 4. Architecture

The layering preserves QUILL's strict import boundaries (`core` has no `wx`; `ui` orchestrates).

```
Tools menu  ──▶  BatchSpeechExportDialog (quill/ui/batch_speech_export_dialog.py)
                      │  collects BatchExportOptions from widgets
                      ▼
              MainFrame.batch_export_to_speech()  (orchestration, snapshot, task launch)
                      │  QuillTaskManager worker thread
                      ▼
              run_batch_export(options, results, on_progress, cancel_event)   ← EXISTS
                      │  per file
                      ▼
              extract_text → polish_for_tts → _synthesize_one → .wav/.mp3     ← EXISTS
                      │  on_progress(done, total, result)
                      ▼
              wx.CallAfter ──▶ dialog list update + Prism announcement
```

## 4.1 Core changes (`quill/core/speech/`)

**`batch_export.py`** — small, surgical additions:

- Extend `SUPPORTED_EXTENSIONS` with `.txt`.
- Add `output_format: Literal["wav", "mp3"] = "wav"` and `skip_existing: bool = False` to `BatchExportOptions`.
- In `_output_path_for`, derive the suffix from `output_format`.
- In `run_batch_export`, when `skip_existing` and the output already exists, mark `status="skipped"`, `error="Already exported"`, and continue.
- When `output_format == "mp3"`, synthesize to a temp `.wav` and transcode to `.mp3`, then place the result. **Corrected scope:** there is *no existing local WAV→MP3 path* to reuse. `quill/core/speech/ffmpeg.py` only offers `transcode_to_wav` (arbitrary → 16 kHz **mono** PCM, tuned for transcription input, the wrong profile for listening), and `ai_tts_export_mp3` produces MP3 only because the *cloud provider* returns it natively. MP3 output therefore requires a **new** helper in the ffmpeg module — e.g. `transcode_to_mp3(source_wav, out_mp3)` building an argv at a listening-appropriate sample rate/bitrate — reusing only `find_ffmpeg()` / `ffmpeg_available()` for discovery. Guard on ffmpeg availability; fall back to WAV with a per-file note if absent. Because this is net-new work, MP3 is a Phase 3 item and a candidate to defer if schedule is tight (WAV-only is fully functional).
- Optionally accept a `kokoro` executable guard parallel to the others (Kokoro is library-based, so likely no exe — confirm during build).

**`text_polish.py`**:

- Add `_extract_txt(path)` (read text, return as-is) and route `.txt` in `extract_text`.
- Leave the shallow `.docx` extractor as-is for v1; add a `# TODO` noting tables/headers/footnotes are out of scope and cross-referencing the document-accessibility tooling.

**Synthesis signature (SSML, §4.7.8):** add an `as_ssml: bool = False` parameter to `sapi5.synthesize_to_wav` and `read_aloud.synthesize_to_file_with_sapi5` so the SAPI path can pass `_SVSF_IS_XML` (the flag constant already exists in `sapi5.py`). Defaulting to `False` keeps every existing caller unchanged; only the SSML-rendering path sets it. eSpeak's markup mode is enabled analogously in its CLI args. No other `read_aloud.py` synthesis signatures change.

## 4.2 UI changes (`quill/ui/`)

**New file: `batch_speech_export_dialog.py`** — a `wx.Dialog` subclass that:

- Is constructed and shown only via `MainFrame._show_modal_dialog` (never `ShowModal()` directly).
- Calls `apply_modal_ids` for the keyboard contract.
- Lays out (vertical sizer, all labelled, full tab order):
  - Source folder: read-only text + **Browse…** button + **Include subfolders** checkbox.
  - File types: checkboxes for Word (`.docx`), Markdown (`.md`), HTML (`.html/.htm`), Plain text (`.txt`).
  - Output folder: read-only text + **Browse…** button.
  - Engine: choice control (SAPI5, DECtalk, Piper, Kokoro, eSpeak) — pre-selected from `read_aloud_engine`. Reuse the Speech Hub's `engine_options` list and its `engine_available` map (see §4.5) so unavailable engines are labelled rather than offered blindly.
  - Voice: choice control populated per engine from the **same enumeration the Speech Hub uses** — `quill.platform.windows.sapi5.list_voices()` for SAPI5, `read_aloud.list_piper_catalog_voices()` for Piper, `read_aloud.list_kokoro_voices()` for Kokoro, and engine-native lists for DECtalk/eSpeak. All return the shared `VoiceOption` model (aliased `ReadAloudVoiceOption`), and `_english_only_voices(engine, voices)` already exists as an optional filter.
  - Speed: slider/spin appropriate to the engine (rate 80–450 for SAPI/eSpeak/DECtalk — matching the existing settings clamp; speed multiplier for Kokoro), pre-filled from settings.
  - Output format: WAV / MP3 radio.
  - **Skip files already exported** checkbox.
  - A summary line ("N files found. Estimated …") updated live as filters change.
  - **Preview** button (next to Voice/Speed) that speaks the defined preview phrase at the *currently selected* voice and speed so the user can audition and adjust before committing — see §4.5 for the live-synthesis requirement.
  - A results `wx.ListCtrl` (report mode: File, Status, Duration) — populated during the run.
  - Standard buttons: **Start**, **Cancel/Close** (contract-compliant via `apply_modal_ids`).
- Exposes `build_options() -> BatchExportOptions` and provides `update_result(done, total, result)` for `wx.CallAfter` to drive the list and status announcements.
- Switching the engine choice repopulates the Voice list and reconfigures the Speed control.

**`main_frame_menu.py`**:

- Add `self._id_batch_speech_export = wx.NewIdRef()` and a menu item **&Batch Export to Speech Audio…** under Tools, near the existing `_id_speech_export_audio` entry. Build the label with `self._menu_label(_("&Batch Export to Speech Audio..."), "tools.batch_speech_export")` — the second argument is the command id used by `commands.keybinding_for` for accelerator display, not a registry that rejects new ids, so this is low-friction. Keep the chord-display rule from `test_main_frame_menu_label_accelerator.py` in mind (no accelerator unless a real shortcut is bound).
- Bind it to `lambda _e: self.batch_export_to_speech()`.

**`main_frame.py`** — new method `batch_export_to_speech()`:

- Safe Mode: align with the existing local-synthesis policy. **Verified:** `generate_speech_audio` does *not* gate on Safe Mode, and the only speech/Safe-Mode interaction in `main_frame.py` is suppressing the first-run speech onboarding prompt. So local-engine batch TTS should follow suit and remain available in Safe Mode; do not add a new gate unless product direction says otherwise. (Cloud engines are excluded from batch entirely — see §2.3 — so the Safe-Mode AI gate is not in play here.)
- Open the dialog via `_show_modal_dialog`.
- On OK: read `BatchExportOptions`, pre-resolve engine-specific executables/models exactly as `generate_speech_audio` already does (Piper exe + model, DECtalk exe, eSpeak exe via `discover_piper_executable` / `discover_dectalk_executable` / `discover_espeak_executable`; Kokoro readiness via `kokoro_onnx_ready()`, no exe). Extract this resolution into a shared helper used by both `generate_speech_audio` and the batch path to avoid duplication.
- Call `discover_files` to build the `results` list; if empty, announce and return.
- Persist chosen engine/voice/speed/folders to settings via `save_settings`.
- **Cancellation (corrected):** `_run_background_task` does **not** accept a cancel handle — its `work` callable receives only a `progress(message, current, total)` function. So create a `threading.Event` in `batch_export_to_speech`, close over it in the `work` function, and pass it to `run_batch_export`. The dialog's Cancel button calls `event.set()` (thread-safe). This mirrors the established precedent in `ai_tts_export_mp3`, which owns its own `cancel_event = threading.Event()`. The `work` body calls `run_batch_export(options, results, on_progress, cancel_event)`, and `on_progress` marshals each per-file result to the dialog via `wx.CallAfter`.
- On success: announce the summary (succeeded/skipped/error counts) and offer to open the output folder. Use `notification_category="speech"` consistent with the existing single-file path.

## 4.3 Reuse the Speech Hub, and where batch export should live (open decision)

**Verified:** QUILL already has a unified **Speech Hub** dialog (`quill/ui/speech_hub_dialog.py`, opened via `MainFrame.open_speech_hub` / `choose_read_aloud_configuration`). It centralizes everything the batch dialog needs for the engine/voice/speed third of its UI:

- `engine_options` — the canonical `[(label, id)]` list of the five engines.
- `engine_available` — a per-engine availability map built from `discover_dectalk_executable`, `discover_piper_executable`, `kokoro_onnx_ready`, `discover_espeak_executable` (SAPI5 always true).
- `preview_fn=self._preview_voice` — voice preview wired to the per-engine sample catalog (`_voice_preview_*` helpers).
- Per-engine settings already surfaced and persisted (`read_aloud_*`).

The batch dialog should **reuse these primitives**, not re-implement engine discovery or voice enumeration. That keeps a single source of truth for "which engines exist and which voices each has."

**Open design decision — surface to the user before building Phase 2:**

1. **Standalone Batch Export dialog** (this plan's default) that *calls into* the shared engine/voice/availability helpers. Cleaner mental model ("batch" is its own task), simpler focus model, but duplicates some layout.
2. **A "Batch Export" tab inside the existing Speech Hub.** Maximum reuse of the hub's engine/voice/speed controls and preview, one place for "all things speech," but the hub is already large and multi-tab (Read Aloud + Dictation), and a long-running batch job living inside a settings-style dialog is an awkward lifecycle fit (the dialog is modal; the batch should keep running if dismissed).

**Recommendation:** standalone dialog (option 1), reusing the hub's engine/voice/availability helpers and `_preview_voice`. Rationale: a batch job is a *task with a lifecycle and progress*, not a *settings panel*; coupling it to a modal configuration dialog fights the "runs in the background" requirement. Voice **preview** in the batch dialog is a near-free win because `_preview_voice` already exists — include it.

## 4.4 Legacy / bridged engines (e.g. bestSpeech — issue #696)

[Issue #696](https://github.com/Community-Access/quill/issues/696) requests **bestSpeech** (a classic English + multilingual synthesizer, in the same spirit as the already-supported DECtalk) via the [`gozaltech/bstspeech-sapi`](https://github.com/gozaltech/bstspeech-sapi) SAPI5 bridge. This is its own feature issue, but it informs the batch architecture and the batch plan should accommodate it rather than be reworked later.

There are two integration shapes, and the batch design already covers the better one:

- **As a SAPI5 voice (preferred, zero batch changes).** Because bestSpeech ships as a SAPI5 driver that registers with Windows, it surfaces as just another system voice under the existing `sapi5` engine. The batch dialog's Voice list — populated from `sapi5.list_voices()` (the same enumeration the Speech Hub uses) — picks it up automatically, and `synthesize_to_file_with_sapi5` synthesizes it with no new code in `batch_export.py`. This is the path to prefer: legacy engines exposed through SAPI "just work" in batch.
- **As a dedicated engine (only if a SAPI bridge is unavailable/insufficient).** If bestSpeech must be driven through its own executable (as DECtalk is), add a `bestspeech` block to `BatchExportOptions` (`bestspeech_executable`, `bestspeech_voice`, `bestspeech_rate`, optional dictionary) and a branch in `_synthesize_one`, mirroring the DECtalk shape exactly. The batch dialog's engine/voice/speed controls already generalize to this; only the options dataclass and dispatch grow.

**Security note:** the bestSpeech DLLs are third-party binaries distributed off-platform (Google Drive links in the issue). A SAPI5-registered driver is invoked by Windows, not through QUILL's external-engine allowlist, so it does not touch the `_ENGINE_EXECUTABLE_BASENAMES` contract. If instead a dedicated executable path is added, it **must** be added to the external-engine allowlist and routed through `stability.safe_subprocess`, consistent with the DECtalk/Piper/eSpeak engines. Acquisition and verification of those binaries is tracked under #696, not this batch work.

**Recommendation:** treat bestSpeech support as #696's deliverable, land it as a SAPI5 voice, and confirm during Phase 2 that it appears in the batch Voice list under the `sapi5` engine with no batch-specific changes required. Capture any dedicated-engine fallback as a small follow-up if the SAPI bridge proves insufficient.

## 4.5 Preview control — hear the voice *and speed* before committing

Before a user commits to synthesizing a whole folder, the batch dialog must let them **hear the selected voice at the selected speed** and adjust, rather than discovering after a long run that the rate was wrong.

- **Control:** a **Preview** button beside the Voice and Speed controls. Activating it speaks a fixed, defined phrase using the *currently selected* engine, voice, and speed.
- **Defined phrase:** reuse the project's existing preview phrase, `MainFrame._PREVIEW_TEXT` — *"Hello, this is a voice preview. The quick brown fox jumps over the lazy dog."* — so the phrasing is consistent with the rest of QUILL. (Single source of truth: reference the constant, don't re-type the string.)
- **Important nuance (verified):** the existing `_preview_voice` / `_voice_preview_sample_path` path plays **pre-rendered sample files at a fixed speed**, so it can preview the *voice* but **not** the chosen *speed*. Because the whole point here is letting users tune speed, the Preview button must **synthesize the phrase live** at the selected rate/speed via the same `read_aloud` synthesis functions the batch uses (to a temp WAV, then play, or stream where the engine supports it). Cached samples are acceptable only as an instant fallback for the *default* speed.
- **Threading:** run the preview synth off the UI thread (it can take a moment for neural engines) and play via the existing audio-playback path; never block the dialog. Debounce/replace so rapid Preview presses don't stack.
- **Accessibility:** announce "Previewing voice at speed N" on activation and restore focus to the Preview button afterward; ensure the button has a clear accessible name.
- **Reuse:** the engine/voice resolution for preview is the *same snapshot logic* used to launch the batch, so factor a small `current_preview_params()` out of the dialog and feed both Preview and `build_options()`.

This makes speed a tunable, auditioned choice — users adjust the slider, press Preview, and only then Start the batch with confidence.

## 4.6 Background execution and announcements

- Reuse the existing `_run_background_task` infrastructure (as `generate_speech_audio` does) so cancellation, error notification, and the task label all behave consistently.
- Per-file progress flows: worker thread → `on_progress` → `wx.CallAfter(dialog.update_result, …)` → ListCtrl update + `_set_status` + Prism announcement.
- Throttle announcements for large batches (announce every file in the status line, but consider summarizing Prism speech to avoid flooding the screen reader — e.g. announce start, then every Nth file, then the final summary).

## 4.7 Pronunciation dictionaries — global and per-synthesizer (new feature)

A pronunciation dictionary lets users teach QUILL how to say words it gets wrong — names, acronyms, brand names, technical jargon, foreign words. This is its own feature with value far beyond batch: it should improve **every** spoken output in QUILL (interactive Read Aloud, batch export, and previews), so it lives in `core` and is consumed by both the live and batch paths.

### 4.7.1 Concept and scope model

A **dictionary** is a named, ordered collection of **entries**, each mapping a source term to how it should be spoken. Scope is expressed as **two orthogonal dimensions** — *where the dictionary lives / when it activates* (**location**) and *which engine it targets* (**engine**) — so a dictionary is one of four combinations.

**Location dimension:**

- **Global** — stored under `app_data_dir()/speech/pronunciation/` and available in every window and every project. The app-wide vocabulary.
- **Project** — stored *inside the project folder* (see "Project definition" below) and active **only while that project is open**. This is the per-use-case dictionary: a fix that should apply to *this body of work* (a book, a client's documents, a code base) without polluting the global set, and that **travels with the folder** so it can be shared or version-controlled alongside the content.

**Engine dimension:**

- **All engines** (`engine = None`) — applied as pre-synthesis text substitution, so it works universally (SAPI5, DECtalk, Piper, Kokoro, eSpeak) because it changes the text before the engine ever sees it.
- **Synthesizer-specific** (`engine = sapi5/dectalk/piper/kokoro/espeak`) — applied *only* when that engine is active. This lets power users exploit engine-native pronunciation syntax (e.g. DECtalk phoneme codes `[ˈkwɪl]`-style, eSpeak `[[kwIl]]` phoneme input) that would be meaningless to another engine. A synthesizer-specific dictionary may itself be **global** (that engine, everywhere) or **project** (that engine, this project only — "a synthesizer case tied to a project").

**Project definition.** A *project* is **a folder and the files it contains**. QUILL resolves the current project folder from, in order: an open Notebook's root folder; otherwise the directory of the active document; and, in the batch dialog, the chosen **source folder** (a batch *is* a project run). Project dictionaries live under `<project>/.quill/pronunciation/<id>.json` — a `.quill` project-data folder in the project root — discovered when that project is opened and ignored otherwise. This is **in addition to** (never instead of) the global and synthesizer dictionaries; it is the existing spell-check/scope-dictionary precedent applied to pronunciation.

Dictionaries are **selectable**: each can be toggled on/off, and a synthesizer-specific dictionary auto-activates when its engine is chosen (and is individually toggleable too). The **active set** for a given `(engine, project_folder)` = enabled dictionaries whose location is *global* **or** *project (from the current project folder)*, **and** whose engine is *all* **or** *the current engine*.

**Precedence on a term conflict** (after longest-term-first matching), most specific wins, by this total order: **project + engine-specific > project + all-engines > global + engine-specific > global + all-engines**. Project beats global (the per-use-case fix is the user's deliberate, content-specific intent); engine-specific beats all-engines (an engine-native pronunciation is chosen on purpose). The order is fixed and unit-tested so a batch is reproducible.

### 4.7.2 Entry model

Each `PronunciationEntry` carries:

- `term` — the word/phrase to match.
- `replacement` — how to speak it. **Three modes:**
  - **Respelling** (default, engine-agnostic): a plain-text phonetic respelling, e.g. `QUILL → "kwill"`, `GIF → "jiff"`, `Pétur → "pay-tur"`. Works on every engine.
  - **Phonetic/native** (advanced, engine-scoped only): raw phoneme syntax for engines that accept it (DECtalk, eSpeak). Validated against the engine; hidden for neural engines that don't support it.
  - **SSML** (advanced, SSML-capable engines): an SSML fragment such as `<phoneme alphabet="ipa" ph="kwɪl">QUILL</phoneme>`, `<sub alias="kwill">QUILL</sub>`, `<say-as interpret-as="characters">SQL</say-as>`, or `<prosody rate="slow">…</prosody>`. See §4.7.8 for the engine-support reality and rendering rules.
- `plain_fallback` — a respelling/alias used automatically when the active engine cannot honor the chosen mode (e.g. an SSML or phoneme entry on a neural engine). **Required for SSML and phoneme entries** so a "global" entry still helps on every engine and degrades gracefully rather than reading raw markup aloud.
- `match` options: `whole_word` (default true), `case_sensitive` (default false), and an optional `regex` flag for advanced patterns.
- `enabled` — per-entry toggle.
- `note` — optional human comment ("client name", "product").

### 4.7.3 Core module (`quill/core/speech/pronunciation.py`, new, wx-free, strict-typed)

- Dataclasses `PronunciationEntry` and `PronunciationDictionary(id, name, scope, engine, entries, enabled)`, where `scope` is `"global"` or `"project"` and `engine` is `None` (all engines) or an engine id.
- JSON persistence in two locations by scope, both written via `core.storage.write_json_atomic` and schema-validated against a new `quill/core/schemas/pronunciation.json` (consistent with the extension-schema pattern):
  - **Global** dictionaries: `app_data_dir() / "speech" / "pronunciation" / <id>.json`.
  - **Project** dictionaries: `<project_folder> / ".quill" / "pronunciation" / <id>.json` (the `.quill` folder is created on first save; a project with no `.quill/pronunciation/` simply has no project dictionaries). The project folder is supplied by the caller (`current_project_dir()` in the UI layer), keeping the core module wx-free and path-injection-clean.
- `apply_pronunciations(text, engine, dictionaries) -> PronunciationResult` — the single substitution engine, returning the transformed text, an `is_ssml` flag, and a substitution report (which entries fired and how often — see §4.7.10). **Match order: longest term first**, then the §4.7.1 specificity order (project+engine > project+all > global+engine > global+all) resolves conflicts deterministically. Respelling entries do plain/whole-word/regex replacement; native-phoneme entries are inserted in the engine's accepted syntax; SSML entries are rendered (or fall back to `plain_fallback`) per the §4.7.8 engine rules, including whole-utterance XML escaping when SSML mode engages.
- A loader/registry `load_dictionaries(project_dir=None)` returning all stored dictionaries (global always, plus project dictionaries from `project_dir/.quill/pronunciation/` when a project dir is given), plus `active_dictionaries(engine, *, project_dir, enabled_ids)` resolving the enabled, in-scope set for the `(engine, project)` pair. Saving a dictionary routes to the global or project location by its `scope`; setting a dictionary's scope to *project* writes it into the current project folder (and removing it from global), and vice-versa, so "make this a project dictionary" physically moves the file.
- Small pure helpers for the builder/validation: `validate_ssml_fragment(text) -> bool` (well-formed XML check, wx-free) and `assemble_ssml(text, fragments) -> str` (escape + splice + `<speak>` wrap), unit-testable without any engine.

### 4.7.4 Pipeline integration (one path, used everywhere)

Insert pronunciation application as a distinct stage in the shared TTS text pipeline so live and batch behave identically:

```
extract_text → apply_pronunciations(text, engine, active_dicts) → polish_for_tts → synthesize
```

- Apply pronunciations **before** `polish_for_tts` so respellings then get the normal whitespace/abbreviation cleanup, but guard the abbreviation map from re-touching a user respelling.
- `run_batch_export` calls it via the engine already known in `BatchExportOptions`; the interactive Read Aloud path calls the same function with the live engine. **This is the key design point: pronunciation correction is not batch-only — wire it into the live read-aloud path too, for one consistent voice across the app.**
- **Project resolution per path.** The UI layer resolves the active set with the right project folder: the live Read Aloud path passes `current_project_dir()` (the open Notebook root or the active document's folder); the batch path passes the **source folder** as the project dir (so a project dictionary stored alongside a folder of documents is automatically in play for that batch). The core stays wx-free — callers hand it the resolved dictionary set, never a window.
- **DECtalk bridge (reuse what exists):** `BatchExportOptions.dectalk_dictionary` / `synthesize_to_file_with_dectalk(dictionary_path=…)` already exist (currently a no-op pass-through — DECtalk loads its own `dtalk_us.dic` system dictionary, not a `-d` user dictionary). For a DECtalk-scoped dictionary we therefore apply entries as **text substitution** like the other engines rather than fighting DECtalk's native dictionary loader; note the existing limitation in code comments and keep the native-dictionary path as a future enhancement.

### 4.7.5 Management UI (`quill/ui/pronunciation_dictionary_dialog.py`, new)

An accessible manager dialog (routed through `_show_modal_dialog`, `apply_modal_ids`, registered in the dialog inventory):

- Left: list of dictionaries with scope badges — **location** ("Global" / "Project") combined with **engine** ("All engines" / "Piper" etc.) — and enable checkboxes. Project dictionaries show the project folder name so the user knows which folder they travel with.
- Right: entry table for the selected dictionary (Term, Spoken as, Mode, Enabled), with Add / Edit / Delete.
- Dictionary-level: New, Rename, **Set location (Global ↔ Project — physically moves the JSON file into / out of the current project's `.quill/pronunciation/`)**, Set engine (All engines vs a synthesizer), Duplicate, Import, Export. "Project" actions are enabled only when a project folder is resolvable; otherwise they are disabled with an explanatory tooltip.
- Reachable from the Speech Hub, from the batch dialog ("Manage pronunciations…"), and from the editor.

### 4.7.6 Making it magical and delightful

- **Add-from-selection:** select a word in the editor → context-menu / command **"Add to Pronunciation Dictionary…"**. The dialog opens pre-filled with the word.
- **Audition-before-commit (the centerpiece interaction):** the entry editor is a small dialog — Term, Mode (Respelling / Phoneme / SSML), the replacement field, and **two prominent buttons**:
  - **▶ Play original** — speaks the bare `term` exactly as the engine says it *today*, with no entry applied, so the user hears the problem.
  - **▶ Play corrected** — speaks the `term` with the pending entry applied through the **real synthesis path** (respelling substituted, or SSML rendered via the engine's SSML mode per §4.7.8), so the user hears precisely what the dictionary will produce — *before* anything is saved.

  Both use the §4.5 live-preview machinery (current voice + speed, off the UI thread, debounced). The flow is: type the fix → **Play original**, **Play corrected**, compare → **Save** only when it sounds right. **Save** stays available without forcing a listen, but the two buttons are the obvious path. This is the delight: you never commit a pronunciation you haven't heard. The corrected preview renders the *exact* SSML/respelling that will ship, so there are no surprises in the batch run.
- **SSML made approachable (not raw XML typing):** in SSML mode, offer quick-insert buttons for the common tags — **Phoneme (IPA)**, **Spell out** (`say-as characters`), **Substitute** (`sub alias`), **Pause** (`break`), **Slow/Fast** (`prosody rate`), **Pitch** (`prosody pitch`) — that wrap the current term in the right markup so users get SSML's power without memorizing syntax. For deeper authoring (assembling phonemes vowel-by-vowel, tuning inflection by ear), open the full **SSML Builder** in §4.7.9. Validate well-formed XML on every keystroke and block Save on malformed markup, with the **Play corrected** button as the live truth check.
- **Smart candidate detection:** offer to surface likely-mispronounced tokens in the open document (ALL-CAPS acronyms, CamelCase, names with diacritics, unit/number patterns) as one-tap "teach me this word" suggestions.
- **Respelling guidance:** inline hints and examples ("Spell it like it sounds: photo → foe-toh") so non-phonetics users succeed without learning IPA. Phoneme mode is opt-in and engine-validated for the few who want precision.
- **Starter dictionaries:** ship a small bundled global dictionary of commonly-mangled tech/brand terms (and the word "QUILL" itself) that users can enable as a starting point and extend.
- **Live everywhere:** because it's in the shared pipeline, a fix the user makes once is heard immediately in Read Aloud, previews, and the next batch — no per-document reconfiguration. That consistency is what makes it feel magical rather than a buried setting.
- **Portability:** Import/Export as JSON so users can share a team or project dictionary; entries round-trip losslessly.

### 4.7.7 Batch dialog and options integration

- Add `active_pronunciation_dictionary_ids: list[str]` (or resolved `dictionaries`) to `BatchExportOptions`; `run_batch_export` passes them to `apply_pronunciations`.
- The batch dialog shows a compact **Pronunciations** section: the active global dictionaries (toggleable), the auto-activated engine dictionary for the chosen engine, and a **Manage pronunciations…** button opening §4.7.5. Changing the engine refreshes which synthesizer-specific dictionary is in play.

### 4.7.8 SSML injection — engine support and rendering rules

SSML is powerful but **engine-dependent**, so the design must apply it where it works and degrade gracefully where it does not.

**Engine support matrix (verified against the code where applicable):**

| Engine | SSML support | How |
|--------|--------------|-----|
| **SAPI 5** | Full W3C SSML | `quill/platform/windows/sapi5.py` already defines `_SVSF_IS_XML = 8  # speak the argument as SSML`, but `synthesize_to_wav` currently calls `sp_voice.Speak(text, 0)` with the flag **off**. Enabling SSML is a *one-line plumbing change*: pass `_SVSF_IS_XML` when the utterance is SSML. Supports `<phoneme>`, `<sub>`, `<say-as>`, `<prosody>`, `<break>`, `<emphasis>`. |
| **eSpeak-NG** | SSML subset | eSpeak parses a markup subset (`<break>`, `<emphasis>`, `<prosody>`, `<say-as>`); enable via its markup mode on the CLI. Phoneme input via its own `[[…]]` syntax. |
| **DECtalk** | No SSML | Native inline `[…]` phoneme/command syntax only → SSML entries use `plain_fallback`; optional native-phoneme entries handle the advanced case. |
| **Piper / Kokoro** | No SSML (neural) | Plain text only → SSML entries use `plain_fallback`. |

**Rendering rules (the important part — SSML is all-or-nothing per utterance on SAPI):**

- When the active engine is **not** SSML-capable, `apply_pronunciations` substitutes each SSML entry's `plain_fallback` (never the raw markup). Result: clean text, no `<angle brackets>` read aloud.
- When the engine **is** SSML-capable and at least one SSML entry applies, the pipeline switches that utterance into **SSML mode**: XML-escape the surrounding document text, splice the SSML fragments in at the matched positions, wrap the whole thing in `<speak>…</speak>`, and call synthesis with the SSML flag set. This avoids the classic failure where a stray `<` or `&` in normal text breaks XML parsing.
- Synthesis signature change: add an `as_ssml: bool` parameter (or auto-detect a `<speak>` root) to `sapi5.synthesize_to_wav` and `read_aloud.synthesize_to_file_with_sapi5`, defaulting `False` so all existing callers are unaffected. The batch and live paths set it when the rendered text is SSML.
- **Validation:** SSML fragments are validated as well-formed XML at entry-save time (§4.7.6) *and* the assembled utterance is validated before a flagged Speak; on malformed SSML, fall back to plain rendering and log rather than crash the run.
- **Scope guidance:** because SSML is engine-specific, SSML entries are most natural in a **synthesizer-specific (SAPI 5)** dictionary. They are still allowed in a global dictionary, but the mandatory `plain_fallback` is what global non-SSML engines use.

### 4.7.9 SSML builder — guided, audible authoring (no raw XML required)

Beyond the §4.7.6 quick-insert buttons, ship an interactive **SSML Builder** so users can *construct* pronunciations and inflections by ear instead of writing XML. It opens from the entry editor ("Build SSML…") and from the Speech Hub.

- **Phoneme builder:** an IPA helper for the term — a categorized, searchable chart of **vowels** (monophthongs/diphthongs), **consonants**, and **stress marks**, each with a **▶ hear this sound** button (rendered live through the SSML-capable engine). Click sounds to assemble the pronunciation, or type IPA with inline validation; the builder emits a `<phoneme alphabet="ipa" ph="…">term</phoneme>`.
- **Inflection / prosody panel:** sliders for **rate**, **pitch**, and **volume**, plus **emphasis** (strong/moderate/reduced) and **break/pause** insertion — each adjustable while **▶ Play corrected** re-renders so the user *hears* the inflection change. Emits `<prosody>` / `<emphasis>` / `<break>` wrappers.
- **Say-as helper:** pick an interpretation (spell-out characters, digits, ordinal, date, time, telephone) to emit `<say-as interpret-as="…">`.
- **Substitution helper:** the simplest path — `<sub alias="…">term</sub>` — for users who just want "say it like this."
- **Live, always-audible:** every adjustment is one button press from being heard at the current voice/speed via the §4.5 machinery; the builder never shows XML the user must trust blindly — they confirm by ear.
- **Output:** the builder writes back a validated SSML fragment into the entry's `replacement`, and auto-suggests a `plain_fallback` (the `<sub>` alias or a respelling) so the same entry still works on neural engines.
- **Accessibility:** the builder is fully keyboard navigable; the phoneme chart is a labelled grid with per-cell "hear" actions; sliders announce their values; nothing depends on sighted drag-and-drop.

### 4.7.10 Rich dictionary handling when building speech files (batch)

When the batch actually converts files, dictionary application should be **rich and transparent**, not a silent black box:

- **Per-file substitution accounting:** `apply_pronunciations` returns not just the transformed text but a small report — which entries fired, how many times, and whether SSML mode was engaged — so each `BatchFileResult` can carry a `pronunciation_applied` count surfaced in the results list and the final summary ("312 pronunciation fixes applied across 42 files").
- **SSML-mode promotion per file:** the per-file pipeline decides plain vs SSML rendering based on the active engine and whether any SSML entry matched that file's text, applying the §4.7.8 escaping rules per document. Long documents that get chunked keep consistent SSML wrapping per chunk.
- **Dry-run / preview transform:** a **Preview transformed text** action on a selected file shows the exact post-dictionary (and post-SSML-assembly) text that will be synthesized, so users can verify the dictionary's effect on real content before committing a long run.
- **Graceful per-file degradation:** a malformed SSML assembly for one file falls back to plain rendering for *that file only*, is recorded in its result row, and never aborts the batch.
- **Deterministic and reproducible:** the same files + same active dictionaries + same engine produce identical output; ordering and precedence (§4.7.3) are fixed, so a batch is auditable.

## 4.8 Heading-aware chapterization — article separation, MP3 chapter markers, and transition earcons (new feature)

A long document — or a compiled feed like a newspaper, a set of web articles, or a multi-section report — is much more listenable when the listener can **jump article-to-article** and **hear when a new section begins**. When a source document contains **headings**, QUILL should optionally treat each heading as an **article / chapter boundary** and produce navigable audio. **Chapter titles are taken from the heading text** of the material.

### 4.8.1 The use case

"Read me this newspaper / these articles and let me move between them." The listener wants to (a) skip to the next article with their player's chapter/track controls, and (b) *hear* an unmistakable transition cue so they know, ears-only, that one article ended and the next began — exactly the affordance a sighted reader gets from a headline and white space.

### 4.8.2 Section extraction (structure-aware)

Add a structure-aware extractor alongside the flat `extract_text` (§4.1, `text_polish.py`):

- `extract_sections(path) -> list[DocumentSection]`, each `DocumentSection(title, level, body_text)`:
  - **Markdown:** ATX (`#`–`######`) and Setext headings start a section; the heading text is the title.
  - **HTML:** `<h1>`–`<h6>` start a section (title = heading text content).
  - **DOCX:** paragraphs whose style is a `Heading N` style start a section (reusing/extending the existing shallow `<w:t>` walk to read paragraph `pStyle`).
  - **TXT:** no reliable heading model → a single section (whole file); chapterization is simply unavailable, never wrong.
- A document with **no headings** yields **one section** (the whole document). Chapterization then degrades to "single file, no chapters" automatically — the feature is opt-in and never produces a one-chapter oddity unless asked.
- Leading text *before* the first heading becomes an implicit "Introduction" section (configurable title) so nothing is dropped.
- Pronunciation correction (§4.7) and `polish_for_tts` run **per section body**, so chaptering composes cleanly with the dictionary pipeline.

### 4.8.3 Output modes

A per-run **Chapters** choice in the batch (and single-document) dialog:

1. **Single file, no chapters** (today's behavior; the default).
2. **Single file with chapter markers** — the whole document is synthesized into one audio file, and the start time of each section is recorded as a chapter marker the player can navigate. **Per-document** (one chaptered file per source document) or, optionally, **one master file for the whole folder** (each *document* a top-level chapter, each *heading* a sub-section where the container format supports nesting; MP3's flat CTOC lists them in order).
3. **Separate file per article** — each section is synthesized to its **own** audio file, named from its heading (e.g. `03 - Local Election Results.mp3`), mirrored under the output folder. This is the "one file per article" option for players/workflows that prefer discrete tracks.

### 4.8.4 Chapter model and marker writing (borrow ChapterForge)

A sibling BITS project, **ChapterForge** (`d:\code99\forum`, MIT-licensed, also Community Access / BITS), already solves chapter-marker writing and is the reference to **borrow from** rather than reinvent:

- **Model:** a `Chapter(index, title, start_ms, end_ms)` list — mirror ChapterForge's `core.Chapter` / `compute_chapters`.
- **MP3 markers:** ID3v2.3 **CHAP + CTOC** frames via **mutagen**, exactly as ChapterForge's `write_tags_and_chapters`: one `CHAP` per chapter (`start_time`/`end_time` in ms, a `TIT2` sub-frame carrying the *heading* as the chapter title) and a top-level ordered `CTOC` listing them. This is the format Apple Podcasts, Overcast, Pocket Casts, VLC, foobar2000, etc. navigate.
- **M4B markers:** the M4B/AAC path writes native MP4 chapter atoms (ChapterForge's M4B branch) when M4B output is selected.
- **Dependency note:** mutagen is the new dependency for chapter writing; add it behind the MP3/chapters feature (and the `network_egress_audit`/`THIRD_PARTY` accounting), reusing ffmpeg for transcode (§4.1). Cite ChapterForge in `THIRD_PARTY.md` / code comments as the borrowed approach.

### 4.8.5 Transition earcon (the "sounder") and the with/without-sound pair

- A **configurable transition sound** (earcon) plays at each chapter/article boundary so the listener hears the transition. It reuses QUILL's existing **sound-pack** system (`quill/core/sound_pack.py`, the `quill/assets/sound_packs/` infrastructure already used for editor earcons) plus a bundled "chapter chime"; the user can choose the sound, toggle it on/off, and set its volume.
- **When the earcon is enabled, produce TWO outputs:** a **clean** file (speech only) **and** a **with-tones** file (the earcon spliced in at each boundary) — e.g. `Daily News.mp3` and `Daily News (with chapter tones).mp3`. The listener picks; some want the cue, some want clean audio with silent chapter markers only. When the earcon is off, only the clean file is produced. The chapter **markers** are written to *both* files identically (the markers are metadata; the tone is audio) — so navigation works either way, the tone is the audible bonus.
- The earcon's duration is included when computing chapter start times for the with-tones file (the chapter begins at the tone, or immediately after — a per-setting choice), so markers stay frame-accurate in each variant.

**Inter-article pause (controls the pacing/"state" of the reading).** Independently of the earcon, a **configurable silence gap** is inserted **between** articles/chapters so the listener gets a clear, unhurried beat at each transition — the audible equivalent of white space, and the control that sets how relaxed or brisk the reading feels. It is `batch_speech_article_gap_ms` (§4.8.8), a duration in milliseconds (0 = back-to-back). The gap is generated as PCM silence and placed at each section boundary; when the earcon is on, the order at a boundary is **`[half-gap] → earcon → [half-gap]`** (so the tone sits in a pocket of silence rather than colliding with speech), and in the clean variant the *same total* gap of pure silence is used so both variants share identical chapter timing. The gap composes with — and is distinct from — the per-sentence `read_aloud_sentence_pause_ms` that already exists for within-text pacing: this one is specifically the *between-article* beat. ChapterForge's `gap_ms` / `_chapters_with_gaps` is the borrowable precedent for inserting and accounting for these gaps in the chapter offsets.

### 4.8.6 Pipeline (per-section synthesize → measure → concat → tag)

Chapterized output extends the §4.7.4 pipeline with a measure-and-assemble stage, reusing the existing per-engine `synthesize_*` (to-file) functions — **still silent; everything writes to disk, nothing is read aloud** (§silent-batch):

```
for each section:  extract → apply_pronunciations → polish_for_tts → synthesize_to_temp_wav → measure duration
assemble:          concat section WAVs, inserting the inter-article gap (PCM silence,
                   batch_speech_article_gap_ms) between sections — and, for the with-tones
                   variant, the earcon WAV inside that gap ([half-gap] earcon [half-gap])
                   → cumulative offsets become Chapter.start_ms/end_ms (titles = headings)
                   → transcode to MP3/M4B (ffmpeg, §4.1) → write CHAP/CTOC chapter markers (mutagen)
                   → if earcon on: also emit the clean variant (concat without the earcon WAVs)
```

- Concatenation and duration measurement are wav-level (stdlib `wave` for PCM, or an ffmpeg concat) — no playback.
- "Separate file per article" skips concat/tagging and just writes each section's transcoded file.
- Per-file accounting (§4.7.10) extends to a per-document **chapter count** in `BatchFileResult`.

### 4.8.7 Dialog controls (added to the batch dialog, §4.2)

- **Chapters:** a choice — *None* / *Single file with chapter markers* / *Separate file per article*. Disabled-with-explanation for `.txt`-only selections (no headings).
- **Chapter transition sound:** on/off checkbox; a sound chooser (reusing the sound-pack picker) and a volume control, enabled only when Chapters ≠ None and the format supports it.
- **Pause between articles:** a duration control (slider/spin, milliseconds or seconds) bound to `batch_speech_article_gap_ms`, so the user dials in how much silence separates articles. Available whenever Chapters ≠ None (and for "separate file per article" it simply pads each file's tail, or is a no-op — confirm during build).
- A note that enabling the sound produces **both** a clean and a with-tones file.
- All controls labelled, in tab order, announced; the chapter list (when "single file with markers" is chosen) is previewable — the headings that will become chapters are read back before Start, so a screen-reader user confirms the structure.

### 4.8.8 Settings

- `batch_speech_chapter_mode: str` (`"none"` / `"single"` / `"separate"`, validated).
- `batch_speech_chapter_sound_enabled: bool`.
- `batch_speech_chapter_sound_id: str` (sound-pack sound id; "" = bundled chapter chime).
- `batch_speech_chapter_sound_volume: int` (0–100, clamped).
- `batch_speech_article_gap_ms: int` (silence inserted between articles/chapters; 0–10000, clamped; default e.g. 1200). See §4.8.5.
- `batch_speech_intro_section_title: str` (default "Introduction") for pre-first-heading text.

## 4.9 Text cleanup and normalization for speech — configurable, with great defaults (new feature)

Real-world documents — especially Word and copy-pasted web content — are full of typography that makes TTS engines stumble or "go crazy": curly quotes and the apostrophe-lookalikes (’ ‘ ʼ ′ ´ and the grave accent), em- and en-dashes (`— –`), ellipses (`…`), non-breaking and zero-width spaces, soft hyphens, ligatures (`ﬁ ﬂ`), bullets and arrows (`• ▪ ‣ → ★`), symbols (`© ® ™ ° × ÷ § ¶ † ‡`), fractions (`½ ¾`), math operators (`≤ ≥ ≠ ± ≈`), stray control characters, and emoji. Some engines read these literally ("right single quotation mark"), some choke, some insert wrong pauses. QUILL should **clean the text deterministically before synthesis**, with **excellent defaults** so it "just works," and **rich, granular options** for users who want control.

This is the deterministic *typographic* layer; pronunciation dictionaries (§4.7) are the *semantic* per-term layer. Both share the one pipeline and improve **all** speech (live Read Aloud, previews, and batch), not just export — though it is surfaced prominently in the export settings as requested.

### 4.9.1 Core module (`quill/core/speech/text_normalize.py`, new, wx-free, strict-typed)

- `TextNormalizationOptions` dataclass — booleans + a few small enums, every field defaulting to the recommended value, with `to_dict`/`from_dict` (persist/round-trip like `StructuredListSettings`).
- `normalize_for_tts(text, options) -> str` — applies the enabled passes in a fixed, documented order. Pure and fully unit-testable (no engine, no wx).

### 4.9.2 Normalization passes (each individually toggleable; defaults in **bold**)

- **Quotes & apostrophes** (**on**): curly quotes → straight; all apostrophe-lookalikes → ASCII `'` (so a word typed with a curly, grave, or modifier apostrophe all reads as "don't").
- **Dashes** (**on**, mode = **comma-pause**): em-dash → `, ` (a natural pause), en-dash → `-`; optional *smart ranges* turns `5–10`/`Mon–Fri` into "5 to 10" / "Mon to Fri". Mode choices: comma-pause / hyphen / spoken ("em dash") / remove.
- **Ellipsis** (**on**): `…` and `...` → a single pause (`, `), so the engine doesn't say "dot dot dot" or stall.
- **Spaces & invisibles** (**on**): non-breaking / figure / narrow / zero-width spaces → normal space; zero-width joiners, soft hyphens (`­`), BOM, and bidi marks → removed.
- **Ligatures** (**on**): `ﬁ ﬂ ﬀ ﬃ ﬄ` → `fi fl ff ffi ffl`.
- **Bullets & list glyphs** (**on**): `• ◦ ▪ ‣ ⁃ ● ○ ■ ▶ →` at line starts → removed (or `, ` mid-line) so lists read as items, not "black circle".
- **Symbols** (**mode = speak**): `© → "copyright"`, `® → "registered"`, `™ → "trademark"`, `° → "degrees"`, `× → "times"`, `÷ → "divided by"`, `§ → "section"`, `¶ → "paragraph"`, `† ‡`, arrows/stars/checks, currency (`$ € £ ¥ → dollars/euros/…`, positioned correctly), `% → "percent"`, common math (`≤ ≥ ≠ ± ≈ ∞`). A built-in, **user-extendable** symbol→word map. Mode: speak / strip / keep.
- **Fractions** (**on**): `½ ¾ ⅓` → "one half" etc.
- **Emoji & pictographs** (**mode = strip**): strip by default; optional "speak name" (e.g. 🎉 → "party popper") via a name table; optional "keep".
- **Repeated punctuation** (**on**): `!!!`→`!`, `???`→`?`, `?!?!`→`?!`, runs of `-`/`*`/`=` (rule lines) → pause/removed.
- **Control characters** (**on**): any C0/C1 control except tab/newline → removed.
- **Compatibility normalize (NFKC)** (**off** by default — opt-in): fold fullwidth/superscript/decorated compatibility characters to canonical forms. Off by default because it is heavier and occasionally surprising; available for messy input.

### 4.9.3 "Magical" optional passes (off-by-default power features)

- **Phone numbers** (opt-in but high-value): detect common patterns — `(555) 123-4567`, `555-123-4567`, `+1 555 123 4567`, `555.123.4567`, extensions (`x123`) — and speak them as **grouped digits with pauses** ("five five five … one two three … four five six seven"), never as subtraction or a date. The dashes/dots inside a detected phone number are handled here, *before* the generic dash pass, so a phone number is never mangled into "555 minus 1234". A toggle plus a light format choice (grouped-digits / digit-by-digit).
- **Numbers spoken naturally** (opt-in): years (`1999` → "nineteen ninety-nine"), large numbers with grouping, decimals, ordinals, currency amounts. Needs a light, dependency-free heuristic (or a vetted `num2words`-style helper — record the dependency decision during build).
- **Acronyms** (opt-in): ALL-CAPS tokens that aren't dictionary words → spelled out (`SQL` → "S Q L"), with an allow-list of acronyms that *are* words (`NASA`, `RADAR`). Ties into the §4.7 smart-candidate detector and the pronunciation dictionary (a respelling always wins).
- **Citations / footnote markers** (opt-in): `[1]`, superscript footnote digits → removed or "footnote".
- **Inline code / backticks** (opt-in): strip backtick characters around inline code (and optionally announce "code") so code spans don't read punctuation.
- **Acronym dotting** (opt-in): `U.S.A.` → `USA`.
- **Quote/aside cues** (opt-in, verbosity-style): announce "quote"/"end quote" around quotations or pause around parentheticals — for users who want structure cues.
- **Heading cue** (ties to §4.8): when chapterizing, optionally prefix a section with "Heading: <title>" in addition to the chapter marker/tone.

### 4.9.4 The escape hatch — user character/word replacement map

- `extra_replacements: dict[str, str]` (a small, user-editable map) for **anything** the built-in passes don't cover — paste a weird glyph, type how to say it, done. This is the "magical, make-it-yours" lever and complements the §4.7 pronunciation dictionaries (which handle whole *terms*; this handles raw *characters/sequences*). Applied last so it can override built-ins.

### 4.9.5 Pipeline placement and scope

```
extract_text → normalize_for_tts(text, opts) → apply_pronunciations → polish_for_tts → synthesize
```

- Runs **first** so phone/number detection, pronunciation matching, and abbreviation expansion operate on clean, de-typographied text (and so the phone pass claims dashes before the generic dash pass).
- Shared by **live Read Aloud and batch** (one implementation), exactly like §4.7 — a single, consistent "clean voice" everywhere.
- Deterministic and order-stable, so output is reproducible and auditable.

### 4.9.6 Settings and UI

- Persist as a `tts_normalization` dict (serialized `TextNormalizationOptions`) in settings — one source of truth shared by export and Read Aloud; plus a master `tts_normalization_enabled: bool` (default **true**). The §4.9.7 address controls live in the same options: `tts_address_mode` (announce / speak / **speak_then_repeat**), `tts_address_spell_letters: bool`, `tts_address_char_pause_ms: int` (inter-segment pause, clamped), `tts_address_trailing_pause_ms: int` (clamped), and `tts_address_long_url_threshold: int`.
- **Export settings dialog:** a **"Clean up text for speech"** section — a master checkbox with great defaults active immediately, and a **Customize…** button opening a grouped, fully-keyboard panel of the §4.9.2/§4.9.3 toggles (dash/symbol/emoji modes, the phone-number format), the **Emails & URLs** controls (mode, spell-letters, inter-segment pause, trailing pause), and the §4.9.4 replacement-map editor. Also reachable from Read Aloud settings so the cleanup applies to interactive speech.
- **Presets** (à la the list-studio presets): "Recommended", "Minimal (quotes & spaces only)", "Aggressive (also phone numbers, numbers, acronyms, NFKC)", "Off".

### 4.9.7 Emails and URLs — speak clearly, optionally repeat, configurable pacing

Email addresses and web addresses are the hardest things to catch by ear and the most painful to get wrong — a listener can't glance back at the screen. QUILL treats **emails and URLs identically** with a dedicated, magical pass (replacing today's blunt `URL → "link"`):

- **Mode** (per the user's request): *Announce only* ("link" / "email address") · *Speak it* · **Speak then repeat** (say the whole address, pause, say it again) — default **Speak then repeat** for addresses, so the listener gets a second chance. A length guard falls back to *Announce only* for absurdly long URLs (configurable threshold) to avoid reading a 300-character tracking link twice.
- **Spell-for-clarity with configurable inter-character/segment pacing:** the address is spoken with deliberate spacing so each part lands. Punctuation becomes words — `@ → "at"`, `. → "dot"`, `/ → "slash"`, `: → "colon"`, `- → "dash"`, `_ → "underscore"`, `~ → "tilde"`, `? → "question mark"`, `& → "and"`, `= → "equals"`, `# → "hash"` — and a **configurable inter-segment pause** (`tts_address_char_pause_ms`) is inserted between characters/segments so `jeff@jeffbishop.com` reads as "jeff … at … jeffbishop … dot … com" at a pace the user sets (0 = natural, higher = spelled slowly). A sub-option spells the *local part* and host **letter-by-letter** for maximum clarity (great for unusual addresses), also paced by the same setting.
- **Configurable trailing pause:** a settable silence **after** the address (`tts_address_trailing_pause_ms`) before the narration continues, so it doesn't run straight into the next sentence.
- **Implementation of the pauses:** on SSML-capable engines (SAPI 5 / eSpeak, §4.7.8) the pauses are exact `<break time="…ms"/>`; on plain engines they degrade to comma/period approximations (a comma ≈ short, a period ≈ long) so the *effect* survives everywhere even if the millisecond precision doesn't. Detection runs **inside §4.9.5 before the generic symbol/dash passes**, so an address's `.`/`-`/`/` are claimed here and never mangled into "dot dot" or "minus".
- **Shared with §4.9.3 phone numbers:** emails, URLs, and phone numbers are the three "structured tokens" that get spell-with-pacing treatment from one mechanism, with the same pause settings family.

### 4.9.8 Tests

- `normalize_for_tts`: each pass in isolation (quotes/apostrophes, dashes incl. smart ranges, ellipsis, invisibles, ligatures, bullets, symbol speak/strip/keep, fractions, emoji, repeated punctuation, control chars, NFKC); phone-number patterns spoken as grouped digits and **not** mangled by the dash pass; the escape-hatch map applied last and overriding built-ins; defaults round-trip via `to_dict`/`from_dict`; deterministic ordering.
- Emails/URLs: punctuation→words mapping; speak-then-repeat emits the address twice; inter-segment and trailing pauses appear as `<break>` on SSML engines and comma/period approximations on plain engines; the address pass claims `.`/`-`/`/` before the generic passes; the long-URL guard falls back to announce-only.

## 4.10 Project-remembered settings — configure once, never again (new feature)

**The principle: set it once per project, then it just remembers.** Re-entering an engine, voice, speed, output format, chapter options, text-cleanup choices, and dictionary selection every time you open a folder is exactly the kind of friction that makes a powerful tool feel tedious. A **project** (the folder and its files, §4.7.1) should carry its **whole speech profile** with it, so the second time you open it, everything is already right and Start is one keystroke away.

### 4.10.1 What is remembered

The full export/speech configuration: engine, voice, speed; output format (WAV / MP3 / M4B); chapter mode + transition sound + inter-article pause (§4.8); the complete `tts_normalization` options incl. email/URL/phone pacing (§4.9); the enabled pronunciation-dictionary ids (§4.7); and the source/output folders. In short, a project becomes a **self-contained, portable speech profile** — open it and press Start.

### 4.10.2 Where it lives (one `.quill/` project home)

- A single project-data folder `<project>/.quill/` holds **everything project-scoped**: `pronunciation/` (the project dictionaries, §4.7) **and** `speech-project.json` (the remembered settings), schema-validated and atomic-written. It travels with the folder — shareable, version-controllable — so a colleague who receives the folder gets your voice, your pronunciations, your chapter style, for free.
- A single `current_project_dir()` resolver (open Notebook root → active document's folder → batch source folder) is the **one** source of "which project," reused by §4.7 dictionaries and §4.10 settings alike (closing the hole of two different notions of "project").

### 4.10.3 Resolution and the "save once" interaction

- **Precedence, most specific wins:** this-run dialog tweaks → **project settings** (when a project is open) → global app settings → built-in defaults. Opening a project **silently applies** its remembered settings as the dialog's starting values; the user can still override for a single run without disturbing the saved project profile.
- **Saving:** a **"Remember for this project"** action writes the current values to `speech-project.json`; an opt-in **auto-remember on Start** (default **on** — the "why set it twice" default) saves whatever you just ran so the next open matches. A clear, always-visible indicator shows the source of the current values ("Project profile" vs "Global defaults"), and a **"Reset to global"** clears the project profile.
- **Global stays the fallback and the new-project seed:** a brand-new project with no `.quill/speech-project.json` inherits the user's global defaults, so even first use is pre-tuned.

### 4.10.4 Magical + simple

This is the simplicity layer over all the richness: the §4.7–§4.9 power (dictionaries, chapters, cleanup) is configured **once per body of work** and then disappears into the background. Combined, a project folder is a living, portable "how this content should sound" — set up the newspaper project once, and forever after it reads the way you like, with your names pronounced right, your chapter tones, your pacing, everywhere.

### 4.10.5 Settings, UI, tests

- **Storage/serialization:** `speech-project.json` is the serialized profile (reuse the `to_dict`/`from_dict` pattern); global equivalents stay in app settings (§7). Add `batch_speech_auto_remember_project: bool` (default true) to global settings.
- **UI:** the batch/speech dialog's "Remember for this project" / "Reset to global" actions and the source indicator; project profile loads on open.
- **Tests (wx-free):** save→reload round-trip of a project profile under a temp `<project>/.quill/`; precedence resolution (this-run > project > global > defaults); a missing project profile falls back to global; the shared `current_project_dir()` contract.

---

# 5. Accessibility Requirements

This is a screen-reader-first application; the batch UI must be excellent for blind keyboard users.

- **Dialog contract**: routed through `_show_modal_dialog`; `apply_modal_ids` applied; registered in the dialog inventory fixture and passing `dialog_inventory.py` and `dialog_button_contract.py` gates.
- **Labelling**: every control has an explicit, programmatically associated label. The results list has column headers.
- **Tab order**: logical top-to-bottom; the **Start** button reachable without mouse.
- **Live announcements**: each file's start and completion announced; a final summary announced. Status surfaced both in the status bar (`_set_status`) and via `prism_bridge`.
- **No color-only status**: the ListCtrl Status column uses text ("Done", "Error", "Skipped"), not color alone.
- **Cancellation**: a clearly labelled control; cancel is honored promptly (the engine already checks `cancel_event` before each file) and the partial result is announced.
- **Focus management**: on completion, focus moves to a sensible control (e.g. the **Open Output Folder** button or the results list), not lost.

Note: the accessibility work here is desktop/wxPython screen-reader practice (NVDA/JAWS/Narrator with UI Automation), not web a11y. The repo's wxPython accessibility patterns and the Desktop Accessibility specialists apply; the web accessibility agents do not.

---

# 6. Testing Strategy

## 6.1 Core unit tests (new) — the priority

**`tests/unit/core/speech/test_batch_export.py`**:

- `discover_files`: extension filtering, recursive vs non-recursive, sorting, empty folder, mixed-case extensions.
- `_output_path_for`: relative-path mirroring; nested subfolders; files outside the source root fall back to basename; suffix follows `output_format`.
- `run_batch_export` with a **fake synthesis** (monkeypatch `_synthesize_one`): all-success path; per-file error isolation (one bad file does not stop the batch); `UnsupportedFormatError` → `skipped`; empty/whitespace text → `skipped`; `on_progress` called with correct `(done, total)` monotonic counts.
- Cancellation: set the event partway; remaining files marked `skipped`; no synthesis called after cancel.
- `skip_existing`: pre-create an output file; assert it is skipped.

**`tests/unit/core/speech/test_text_polish.py`**:

- `extract_text` for `.md` (code fences dropped, headings/links/emphasis flattened), `.html` (script/style skipped, block tags → newlines), `.docx` (build a minimal in-memory docx zip and assert paragraph extraction), `.txt` (passthrough), and unsupported suffix → `UnsupportedFormatError`.
- `polish_for_tts`: abbreviation expansion, URL → "link", whitespace/blank-line collapsing.

**`tests/unit/core/speech/test_pronunciation.py`** (new feature, §4.7):

- `apply_pronunciations`: respelling substitution (whole-word vs substring), case sensitivity, regex entries, and **longest-match-first** ordering.
- Conflict precedence: a synthesizer-specific entry overrides a global entry for the same term when that engine is active; global-only when not.
- Scope resolution: `active_dictionaries(engine, project_dir, enabled_ids)` returns the enabled, in-scope set — global + the current project's dictionaries, intersected with all-engine + the current engine — and excludes other engines' dictionaries and other projects' dictionaries.
- Location resolution: a project dictionary under a temp `<project>/.quill/pronunciation/` is loaded only when that `project_dir` is passed; a global dictionary is always loaded; the project/engine **precedence order** (project+engine > project+all > global+engine > global+all) is asserted on a same-term conflict across all four combinations.
- **SSML rendering (§4.7.8):** on an SSML-capable engine an SSML entry produces a `<speak>`-wrapped, XML-escaped utterance with `is_ssml=True`; on a non-capable engine the same entry yields the `plain_fallback` with `is_ssml=False` and **no raw markup** in the output. A stray `<`/`&` in surrounding text is correctly escaped when SSML mode engages.
- `validate_ssml_fragment` accepts well-formed fragments and rejects malformed ones; `assemble_ssml` escapes + splices + wraps deterministically.
- Substitution **report**: `apply_pronunciations` reports which entries fired and counts (drives the §4.7.10 per-file accounting).
- Round-trip: write a dictionary (including an SSML entry with fallback), reload it, assert entries are byte-stable; schema validation rejects malformed JSON.
- Disabled entries and disabled dictionaries are skipped.

All of the above are pure/`wx`-free; the SSML *playback* (engine flag) is exercised in manual verification, but assembly/validation/precedence are fully unit-tested.

All tests must be `wx`-free and run under the standard `pytest -q` session (respecting the `_DEV_BUILD` conftest fixture).

## 6.2 Dialog / contract tests

- Add both new dialogs (batch export and the pronunciation manager) to the dialog inventory fixture; assert `dialog_inventory.py` and `dialog_button_contract.py` pass.
- A smoke test constructing `BatchExportOptions` from a simulated dialog state via `build_options()` (no real `wx` event loop), verifying engine/voice/speed and active-dictionary mapping.

## 6.3 Manual / live verification

- Run a real folder of mixed `.docx/.md/.html/.txt` through each available local engine; confirm output files, mirrored structure, cancellation mid-run, skip-existing on re-run, and MP3 transcode when ffmpeg is present.
- NVDA pass: confirm every control is labelled, the results list is navigable, and progress + summary are announced.

---

# 7. Settings and Persistence

Reuse existing `read_aloud_*` settings as the source of truth for engine/voice/speed defaults so the batch dialog pre-fills from the user's Read Aloud configuration. Add only what batch needs that is genuinely new:

- `batch_speech_last_source_folder: str`
- `batch_speech_last_output_folder: str`
- `batch_speech_output_format: str` (`"wav"` / `"mp3"`, validated)
- `batch_speech_skip_existing: bool`
- `batch_speech_extensions: list[str]` (last-used file-type filter)

For pronunciation dictionaries (§4.7), the dictionaries themselves live in their own JSON files — **global** ones under `app_data_dir()/speech/pronunciation/`, **project** ones under `<project>/.quill/pronunciation/`; settings stores only the **selection state**:

- `pronunciation_enabled: bool` (master on/off)
- `pronunciation_enabled_dictionary_ids: list[str]` (which dictionaries — global and project, all-engine and per-engine — are active; keyed by dictionary id, which is unique across locations)

Project dictionaries are discovered from the open project's `.quill/pronunciation/` folder, so they appear and disappear with the project automatically; their enabled state is remembered by id in the same `pronunciation_enabled_dictionary_ids` list (an id for a project that is not currently open is simply inert until that project is opened again). A dictionary's own `enabled` flag (persisted in its JSON) is the default; the settings list is the per-user override.

All persisted via the existing schema-validated `save_settings` path with sensible defaults and clamping, consistent with how `read_aloud_*` values are validated.

---

# 8. Delivery Phases

**Phase 1 — Lock the engine (tests first).**
Write `test_batch_export.py` and `test_text_polish.py` against the code as it stands. This pins current behavior before any change. Add `.txt` support and its tests.

**Phase 2 — Make it reachable (minimum viable batch).**
Build `batch_speech_export_dialog.py` (folder pickers, file-type filter, engine/voice/speed from settings reusing the Speech Hub helpers, **Preview** button per §4.5, results list, Start/Cancel). Wire the Tools menu item and `batch_export_to_speech()`. Background execution via `_run_background_task` with a dialog-owned `threading.Event` for cancellation. WAV output only. Dialog inventory + contract green.

**Phase 3 — Make it magical.**
Skip-existing/resume, pre-run summary (file count + estimate), MP3 output via a **new** `transcode_to_mp3` ffmpeg helper (see §4.1 — no existing path to reuse; deferrable), refined announcements (start/Nth/summary throttling), and **Open Output Folder** on completion.

**Phase 4 — Polish and persist.**
New `batch_speech_*` settings, last-used defaults, focus management, and the live NVDA pass. Update the user guide and CHANGELOG.

**Phase 5 — Pronunciation dictionaries (§4.7) — independently shippable.**
Build the `pronunciation.py` core module + schema + tests, wire `apply_pronunciations` into **both** the batch and live Read Aloud pipelines, build the manager dialog and the add-from-selection flow, and the audition-before-commit entry editor with **Play original / Play corrected** buttons. Ship a starter global dictionary and persist selection state. This phase delivers value across all of QUILL's speech, not just batch, and can land before or after Phase 3 since it doesn't depend on MP3. Sub-sequence: (a) core model + storage for **both global and project locations** and the all/per-engine axis, the resolver, and `apply_pronunciations` with full precedence tests (respelling first); (b) pipeline integration with project-dir resolution per path (instant win for live Read Aloud; batch uses the source folder as the project); (c) manager UI with location/engine scope controls (incl. Global ↔ Project move), audition buttons, and delight features. The **project-scope dictionary** is part of (a)/(b)/(c), not a later add-on.

**Phase 6 — SSML injection and the SSML Builder (§4.7.8–4.7.10).**
Flip on the SAPI `_SVSF_IS_XML` path (add `as_ssml`), implement SSML-mode assembly/escaping/validation and graceful fallback, add the SSML entry mode and quick-insert buttons, then build the guided **SSML Builder** (phoneme/vowel chart with per-sound preview, prosody/inflection sliders, say-as/sub helpers) and the rich batch-time handling (per-file substitution accounting, dry-run transform preview, per-file degradation). Layered on Phase 5 so respelling-only dictionaries ship first and SSML is additive.

**Phase 7 — Heading-aware chapterization (§4.8).**
Add the structure-aware `extract_sections` (Markdown / HTML / DOCX headings; TXT = single section) and the per-section synthesize→measure→concat→tag pipeline. Deliver the three output modes (none / single-file-with-chapters / separate-file-per-article), MP3 **CHAP/CTOC** chapter markers via mutagen and M4B native chapters — **chapter titles from the headings** — borrowing ChapterForge's (`d:\code99\forum`, MIT/BITS) chapter model and writer. Add the configurable **transition earcon** (reusing the sound-pack system) with the **clean + with-tones** output pair, and the configurable **inter-article pause** (`batch_speech_article_gap_ms`). Wire the dialog controls (Chapters mode, transition sound, pause), the new settings, the chapter-list preview/announcement, and tests for section extraction, chapter-offset computation (with gap + earcon accounting), and marker round-tripping. Depends on the MP3 path (Phase 3 + the `transcode_to_mp3` helper); ships after a folder can already produce plain audio.

**Phase 8 — Text cleanup and normalization (§4.9).**
Build the wx-free `text_normalize.py` with `TextNormalizationOptions` and `normalize_for_tts`, implement the §4.9.2 default passes (quotes/apostrophes, dashes, ellipsis, invisibles, ligatures, bullets, symbols, fractions, emoji, repeated punctuation, control chars, NFKC) and the §4.9.3 opt-in passes (phone numbers first-class, numbers, acronyms, citations, code, etc.) plus the §4.9.4 user replacement-map, wire it as the **first** stage of the shared pipeline (live Read Aloud + batch), and surface it in the export and Read Aloud settings (master toggle, Customize panel, presets). Fully unit-tested (§4.9.7). Independently shippable and an instant win for live speech — can land early, before or alongside Phase 5.

**Related but separately tracked:** **bestSpeech** legacy TTS support (issue #696) — land it as a SAPI5 voice so it flows through the batch `sapi5` engine unchanged (see §4.4); confirm it in the Phase 2 voice list rather than building batch-specific code for it.

**Deferred (post-v1):** richer `.docx` extraction (tables/headers/footnotes), long-document chunking via `tts_chunk.py`, cloud-engine support, and parallel synthesis.

---

# 9. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Native engine subprocess crash mid-batch | Per-file `try/except` already isolates failures. **Verified:** `read_aloud.py` currently calls `subprocess.run`/`Popen` **directly** (with timeouts), *not* `stability.safe_subprocess`. Batch inherits that behavior; whether to migrate the engine subprocess calls to `safe_subprocess` is a separate, pre-existing hardening question and should not block this feature. |
| Screen-reader announcement flooding on large batches | Throttle Prism speech (start / every Nth / final summary); keep full detail in the ListCtrl and status bar. |
| ffmpeg absent for MP3 | Detect via the `ffmpeg` module; fall back to WAV with a per-file note; never hard-fail the batch. |
| Long opaque wait per large document | Accept for v1 (per-file granularity); document chunking deferred to a later phase. |
| Voice list mismatch across engines | Engine-change handler repopulates the Voice control and reconfigures Speed; validate selections in `build_options()`. |
| Duplicate engine-resolution logic vs `generate_speech_audio` | Extract the Piper/DECtalk/eSpeak path-resolution into a shared helper used by both. |
| Dialog gate regressions | Register both new dialogs in the dialog inventory fixture from the start; run the contract gates in CI. |
| Pronunciation substitution corrupts unrelated text (e.g. "GIF" inside "GIFTED") | Default `whole_word` matching; longest-match-first; per-entry case sensitivity; preview the effect before saving. Regex mode is opt-in for advanced users. |
| Conflicting entries across global vs engine dictionaries | Deterministic precedence: synthesizer-specific overrides global; documented and unit-tested in `apply_pronunciations`. |
| Engine-native phoneme syntax misused on engines that don't support it | Phoneme mode is only offered for engines that accept it (DECtalk/eSpeak) and is validated; neural engines expose respelling only. |
| Pronunciation dictionary diverges between live and batch speech | Single shared `apply_pronunciations` stage in one pipeline consumed by both paths — never two implementations. |
| SSML markup read aloud literally on non-SSML engines | SSML entries require a `plain_fallback`; non-capable engines (Piper/Kokoro/DECtalk) get the fallback, never raw tags. Verified the SAPI flag plumbing (`_SVSF_IS_XML`) before relying on it. |
| Stray `<`/`&` in document text breaks SSML parsing | SSML mode is whole-utterance: escape surrounding text, splice fragments, wrap in `<speak>`, validate before a flagged Speak; malformed assembly degrades to plain rendering per file and is logged, never aborting the batch. |
| SSML/IPA authoring too hard for users | Quick-insert buttons plus the guided **SSML Builder** (audible phoneme chart, inflection sliders) and a mandatory **Play corrected** audition — users confirm by ear, never trust raw XML. |

---

# 10. Definition of Done

- Tools → **Batch Export to Speech Audio…** opens an accessible dialog that converts a chosen folder of `.docx/.md/.html/.txt` files to audio with a selected engine, voice, and speed, in the background, without blocking the UI.
- A **Preview** button speaks the defined preview phrase at the currently selected voice **and speed** (live synthesis), so users audition and adjust before starting a batch.
- Cancellation, skip-existing, and per-file error isolation all work and are announced.
- `batch_export.py` and `text_polish.py` have full unit coverage; the new dialog passes the inventory and button-contract gates.
- Settings persist last-used folders, format, filter, and skip-existing; engine/voice/speed pre-fill from Read Aloud preferences.
- Pronunciation dictionaries (§4.7) exist across **global** and **project** locations and **all-engine** and **per-synthesizer** engine scopes (a project dictionary stored in the project folder travels with it and activates only while that project is open), are selectable, and are applied consistently in **both** live Read Aloud and batch export; a user can add a word from the editor, **Play original** then **Play corrected** to audition the fix before committing, and have it take effect everywhere immediately. The manager dialog passes the gate suite and `apply_pronunciations` is unit-tested for ordering and the project/engine precedence (§4.7.1).
- SSML injection works on SSML-capable engines (SAPI 5 via the `_SVSF_IS_XML` path; eSpeak subset) with whole-utterance escaping and graceful `plain_fallback` on neural/DECtalk engines; the guided **SSML Builder** lets users author phonemes, vowels, and inflection by ear; and batch conversion applies the dictionary richly with per-file substitution accounting and a dry-run transform preview.
- **Heading-aware chapterization (§4.8):** a document with headings (Word / Markdown / HTML; plain text has none and is one section) can be produced as a **single file with chapter markers** (MP3 CHAP/CTOC via mutagen, or M4B native chapters, **titled from the headings**) or as **separate files per article**, so a listener can jump article-to-article in their player. A configurable **transition earcon** marks each boundary audibly and, when enabled, yields **both** a clean and a with-tones file; a configurable **inter-article pause** (`batch_speech_article_gap_ms`) sets the spacing between articles. Section extraction, chapter-offset computation (gap + earcon accounted), and marker round-tripping are unit-tested; the chapter list is announced before Start. Approach borrowed from ChapterForge (`d:\code99\forum`, MIT/BITS), credited in `THIRD_PARTY.md`.
- **Text cleanup and normalization (§4.9):** weird Word/web typography (curly quotes and apostrophe-lookalikes, em/en-dashes, ellipses, invisible spaces, soft hyphens, ligatures, bullets, symbols, fractions, emoji, control characters) is cleaned before synthesis with excellent defaults, and **phone numbers**, **emails**, and **URLs** are spoken clearly — phone numbers as grouped digits; emails/URLs handled identically with a **speak-then-repeat** option, punctuation→words, a configurable **inter-segment pause** and **trailing pause** (exact `<break>` on SSML engines, comma/period approximation elsewhere). Everything is configurable (per-pass toggles, modes, a user replacement-map, presets) and shared by live Read Aloud and batch via one `normalize_for_tts` stage; fully unit-tested.
- **Project-remembered settings (§4.10):** a project (folder of files) carries its whole speech profile — engine/voice/speed, output format, chapter options, text-cleanup options, and the active pronunciation dictionaries — in `<project>/.quill/speech-project.json`, applied automatically when the project opens, so the user configures **once per project** and never re-enters it; this-run > project > global > defaults precedence is unit-tested, one shared `current_project_dir()` resolves the project for both settings and dictionaries, and "Remember for this project" / "Reset to global" plus auto-remember-on-Start make it effortless.
- `ruff`, scoped `mypy quill\core quill\io`, and the test suite are green.
- User guide and CHANGELOG updated.
