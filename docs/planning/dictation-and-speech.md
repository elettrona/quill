# QUILL Speech & Dictation — Reengineering Plan

**Status:** Active plan (shipping). Folds in issue #617 (Offline Speech-to-Text Provider Architecture) and the dictation reengineering.
**Date:** 2026-06-21
**Principle:** Bold, offline-first architecture underneath; **simplicity for the user is king** on top.

**Status (2026-06-21):** S0 ✅ (dictation setting made honest), S1 ✅ (offline STT
foundation — `quill/core/speech/`: provider protocol, formatters, model store,
registry, catalog), S2 ✅ (whisper.cpp provider + offline file transcription + an
accessible model manager and Transcribe command under **AI > Speech**, with
Hugging Face Hub model downloads). Next: S3 (live dictate-at-cursor + captions).

---

## 1. Where dictation is today (grounded in code)

A candid read of the shipping code, because the plan must build on what exists:

| Area | Module(s) | Reality today |
| --- | --- | --- |
| Dictation control | `quill/core/dictation.py` (`DictationController`) | On Windows, `start()` and `stop()` **both** just call `launch_windows_dictation()` — i.e. they toggle the OS dictation panel (Win+H). QUILL captures nothing itself. |
| "Local engines" | `dictation.py._transcribe_audio` | References `recognizer.recognize_whisper` / `recognize_vosk`, but there is **no audio capture loop**, no recognizer wired in, and `list_dictation_devices()` returns `[]`. These are dead stubs. |
| Settings | `quill/core/settings.py` | `dictation_engine` (vosk/whisper), `dictation_language`, `dictation_model`, `dictation_device_index` exist and validate, but the controller ignores them and launches Windows dictation regardless. **The settings promise local engines the code does not deliver.** |
| Commands / UI | `quill/ui/main_frame.py` | `tools.dictation_toggle` → `toggle_dictation`; `toggle_dictation_voice_commands`; `_on_dictation_state_change`, `_on_dictation_error`. Keymap: `Ctrl+Alt+V` (and a QUILL-Key chord). |
| File transcription | `quill/core/ai/transcription.py` | **Cloud only** — OpenAI Whisper-1, 25 MB cap, `urlopen` (GATE-9 audited). |
| Diarization | `quill/core/ai/diarization.py` | **Cloud only** — Deepgram Nova-3 (2 GB cap). |
| Offline suite | `feature_catalog.py` `core.bw_whisperer` (+ `bw_transcription`, `bw_parakeet`) | "BITS Whisperer" master flag, **locked_off**, was framed as 2.0. Per current direction it **ships**. |
| Model download UX precedent | `quill/ui/main_frame.py` read-aloud (Kokoro/Piper), `quill/core/ai/model_manager.py`, `model_tiers.py` | QUILL already downloads models with accessible progress and tiering — proven patterns to reuse, not reinvent. |

**The core problem:** dictation is a thin shim to the OS panel, the local-engine settings are a promise the code breaks, and transcription/diarization are cloud-only — which contradicts QUILL's privacy-first, offline, accessible mission. #617 is the right destination; this plan gets there while keeping the everyday experience trivially simple.

---

## 2. Product vision

> **You press one key, speak, and your words appear where your cursor is — privately, on your computer, with your screen reader telling you exactly what is happening. The same engine transcribes a recording or makes captions. Nothing leaves your machine unless you choose a cloud option on purpose.**

Two user-facing verbs, nothing more:

- **Dictate** — speak into the current document (live, at the cursor).
- **Transcribe** — turn an audio/video file into text (new document or captions).

Everything else (providers, models, CTranslate2, quantization, push-to-talk grammars) lives *under* an Advanced fold and is never required to get started.

---

## 3. Architecture (bold underneath)

One offline-first **Speech engine** with a provider registry, mirroring the proven shape of QUILL's existing AI provider/backend split (`quill/core/ai/provider_backend.py`, `availability.py`, `model_manager.py`).

```
quill/core/speech/                      [NEW package]
  provider.py        SpeechToTextProvider protocol (#617 §8.1), data objects
  registry.py        provider registry + availability (lazy import; never crashes startup)
  models.py          SpeechModelInfo, InstalledSpeechModel, model store (JSON, atomic)
  capture.py         microphone capture (push-to-talk + continuous), device list
  formatters.py      TXT / SRT / VTT / JSON exporters (pure, unit-tested)
  voice_commands.py  push-to-talk phrase -> command, constrained to SAFE_TOOL_IDS
  providers/
    windows.py       WindowsDictationProvider  (wraps today's launch_windows_dictation — zero-download fallback)
    whispercpp.py    WhisperCppProvider        (DEFAULT offline; pywhispercpp or bundled whisper-cli subprocess)
    cloud_whisper.py CloudWhisperProvider      (wraps existing ai/transcription.py)
    faster_whisper.py FasterWhisperProvider    (OPTIONAL advanced; CTranslate2; lazy)
```

Reuse, don't rebuild:
- **Threading:** `stability/task_manager.QuillTaskManager` + `wx.CallAfter` (never block the UI thread; #617 §8.2).
- **Model download/progress:** the read-aloud Kokoro/Piper download pattern + `ai/model_manager.py` tiering.
- **Storage:** `core/storage.write_json_atomic`; models under the data dir, portable-aware (respects `QUILL_DATA_DIR` rules); model metadata JSON per #617 §8.3.
- **Secrets / cloud:** existing `credential_manager`/DPAPI for any cloud key; **every** new outbound call added to `tools/network_egress_audit.py`.
- **Safe Mode:** the whole speech surface respects `QUILL_SAFE_MODE` (no network, no model download) exactly like the assistant does.
- **Dialogs:** `_show_modal_dialog` + `apply_modal_ids`; pass the dialog-inventory and button-contract gates.
- **Voice-command safety:** reuse the agent's `SAFE_TOOL_IDS` allowlist from `quill/core/ai/agent.py` so voice can only ever trigger the same curated, non-destructive command set — with confirmation for anything destructive.
- **Budgets:** new modules stay under the GATE-11 default cap; optional providers get explicit budget entries with dated notes.

Capability model (so the UI never lies the way today's vosk setting does): each provider reports `is_available()`, install status, supported models, and supported input formats. The UI only shows what a provider can actually do.

---

## 4. The simple surface (king)

### 4.1 First run (one friendly choice)
On first **Dictate**, if no offline model is installed:

> "To dictate privately on this computer, QUILL needs a small speech model (Recommended: Small, about 250 MB). Download it now? You can also use Windows dictation with no download."

Buttons: **Download Recommended** · **Use Windows dictation** · **Not now**. One recommended path, plain language, no jargon (#617 §6, §16).

### 4.2 Everyday dictation
- `Ctrl+Alt+V` (unchanged keymap) starts/stops. Announce: "Listening." → words stream in at the cursor → "Dictation off. Inserted 42 words. Ctrl+Z to undo."
- Each utterance is one undo step (same one-undo discipline as the AI edit path: `_record_persistent_undo_state`).
- Focus returns to the editor every time.

### 4.3 Transcribe a file
**File > Import > Transcribe Audio or Video** → pick file → (model prompt if needed) → background transcribe with accessible progress → result opens in a new document with an optional metadata header (#617 §7.1).

### 4.4 Captions
**Tools > Speech and Transcription > Generate Captions** → SRT/VTT/both → review document → save.

### 4.5 Settings (minimal; Advanced hidden)
Speech & Transcription page: **Engine** (Offline – recommended / Windows / Cloud), **Model** (Recommended), **Language**, **Microphone**. Everything else (provider internals, timestamps default, keep-model-loaded, voice commands, push-to-talk key, model storage path) lives behind **Advanced**.

---

## 5. What we replace / retire

- **Retire the dead vosk/whisper recognizer stubs** in `dictation.py` and the settings that imply them. The `dictation_engine` setting is re-pointed at the new provider registry (`offline` / `windows` / `cloud`) with a migration so existing `vosk`/`whisper` values map to `offline`.
- **Keep** `launch_windows_dictation` — it becomes `WindowsDictationProvider`, the zero-download fallback, so nobody loses today's behavior.
- **Promote** `core.bw_whisperer` from locked_off to shipping (the offline suite is the default story now).
- **Fold** `ai/transcription.py` (cloud) behind `CloudWhisperProvider` so all three paths share one dialog, one progress model, one output formatter set.

---

## 6. Buckets & waves (small, low-risk commits)

Each wave is independently shippable, lands behind feature gating where useful, and is one or a few small commits. Lowest-hanging first.

| Wave | Scope | Risk | Why first |
| --- | --- | --- | --- |
| **S0 — Honesty fix** | Make settings truthful: map `vosk`/`whisper` → `offline`; document that dictation currently launches Windows dictation; remove dead `_transcribe_audio` stub or guard it. Pure cleanup + tests. | Very low | Stops the UI from promising what it can't do; unblocks the rename. |
| **S1 — Foundation** | `speech/` package: provider protocol, registry (lazy, availability), model metadata schema + store, TXT/SRT/VTT/JSON formatters (pure, fully unit-tested), accessible Speech & Transcription dialog skeleton. No engine yet. | Low | Pure, testable core; no heavy deps; no UI risk. |
| **S2 — Offline transcription** | `WhisperCppProvider` (subprocess-first for isolation), model manager download/remove/verify (reuse read-aloud pattern), WAV file → new document, TXT export, cancellation, network-audit entries. | Medium | Delivers the headline offline value on a reliable format (WAV). |
| **S3 — Captions + dictation** | Segment/timestamp model, SRT/VTT export, mic capture (`capture.py`), insert-at-cursor live dictation with one-undo/utterance, language selection. | Medium | Builds on S1/S2; the "press one key and speak" moment. |
| **S4 — Cloud + advanced** | `CloudWhisperProvider` (wrap existing transcription), `FasterWhisperProvider` (optional, lazy, isolated failure), more input formats once packaging is proven. | Low–Med | Pure additions behind the same UI; no effect on offline path. |
| **S5 — Voice commands (experimental, off by default)** | Push-to-talk phrase→command via `SAFE_TOOL_IDS` allowlist, destructive-action confirmation, editable phrase map later. | Med (gated) | Conservative, opt-in, reuses the agent safety floor. |

Acceptance criteria, model tiers/sizes, privacy copy, and error wording are taken verbatim from #617 §11–§12 and §16.

---

## 7. Risk controls (low-risk by construction)

- **No model in the installer**, ever (#617 §5.3). Base install stays lean; models are an explicit, consented download.
- **Lazy imports**: optional providers (Faster Whisper, pywhispercpp) are imported only on activation; a missing/broken one never breaks startup or the other providers (#617 §8.2, §17).
- **Subprocess-first** whisper.cpp for dependency isolation; Python binding only if packaging proves stable.
- **Privacy by default**: local providers never upload; temp audio deleted after use; transcript text never logged; Safe Mode disables network + downloads (#617 §10).
- **Accessibility is a gate, not a hope**: keyboard-only + NVDA/JAWS/Narrator pass required before each wave closes; progress announced without chatter; focus restored (#617 §6.4, §12.4).
- **Everything tracked**: each wave updates the release notes, user guide, PRD speech section, and CHANGELOG, and closes its issue(s) only when its acceptance criteria are green.

---

## 8. Mapping to issues

- **#617** is this plan's spine (provider architecture, model manager, captions, dictation, voice commands, packaging, testing).
- Dictation reengineering (S0/S3) and the offline-suite promotion (`core.bw_whisperer`) are folded in here rather than tracked as scattered stubs.
- New focused issues should be filed per wave (S0–S5) so each is a small, reviewable unit; #617 becomes the epic that closes when S0–S4 ship (S5 may trail as experimental).
