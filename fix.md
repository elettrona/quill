# Proposed fixes — 0.9.0 beta 2

Branch: `feature/0.9.0-beta2`. This is a proposal doc only — no code changes yet.
Covers the five items from the @quillforall feedback thread, GitHub issues
#866 and #867, and the two cross-cutting asks (error codes, better
component-acquisition path).

---

## 1. Whisper model download fails

**Symptom:** user cannot download the Whisper model at all.

**Root cause:** `quill/core/speech/catalog.py` pins whisper.cpp downloads to a
fixed HF Hub revision + sha256 (`_WHISPER_CPP_REVISION`). If HF has since
moved or re-uploaded that revision, every download 404s or fails checksum,
identically, forever. Same bug class already hit once and fixed in `f28a9d7`
("fix tinydiarize 404") — the pin just went stale again.
`whispercpp.py:_download_to_file` (line ~406/417) reports either "integrity
check failed" or a generic "download failed: {exc}", both dead ends for the
user.

**Proposed fix:**
- Re-verify `_WHISPER_CPP_REVISION` and its sha256 values against the live HF
  repo; update the pin.
- In `_download_to_file`, distinguish failure modes instead of one generic
  catch: HTTP 404/410 -> "this QUILL build's model reference is out of date,
  please update QUILL"; checksum mismatch -> same message (it means the pin is
  stale, not that the user's disk/network is bad); connection/timeout ->
  "network problem, check your connection and retry."
- Attach error code `QUILL-SPEECH-WHISPER-DL-404` / `-CHK` / `-NET` (see
  §8) so a pasted code alone tells us which branch fired.
- Add a regression test that hits the pinned URL/revision in CI (or a
  scheduled job) so a future HF-side move is caught before a user reports it,
  not after.

**Files:** `quill/core/speech/catalog.py`, `quill/core/speech/providers/whispercpp.py`.

---

## 2. Kokoro voice error doesn't say where to get the package

**Symptom:** selecting a Kokoro voice throws an error demanding "another
package" with no indication of source.

**Root cause:** `quill/core/read_aloud.py:kokoro_onnx_ready()` (~line 420)
only checks that model *files* exist on disk — it never checks that the
`kokoro_onnx` pip package actually imports. So `main_frame.py:17789` marks
Kokoro "available" even when the pip install step failed or was skipped. The
user only discovers the problem at synthesis time, where `read_aloud.py:508-515`
raises a message listing two unrelated remediations (redo the model download,
or `pip install kokoro` + ~2 GB of torch) and never mentions the actual fix:
**Tools > Speech > Install Kokoro ONNX** (`engine_install.install_kokoro_onnx`).

**Proposed fix:**
- Change the readiness check to `kokoro_onnx_ready() and is_kokoro_onnx_available()`
  (mirroring the pattern already used in `optional_components.py:_kokoro_installed`,
  lines 66-70), so the UI stops reporting "ready" when the pip package is
  missing.
- Rewrite the failure message to name the actual fix first: "Kokoro voices
  need one more component. Tools > Speech > Install Kokoro ONNX will fetch it
  (~114 MB)." Keep the manual-pip-install line only as a secondary/advanced
  option.
- Error code `QUILL-SPEECH-KOKORO-PKG-MISSING` on this path (see §8).
- Covered further by the acquisition-path fix in §7.

**Files:** `quill/core/read_aloud.py`, `quill/ui/main_frame.py` (engine_available wiring),
`quill/ui/voice_browser_dialog.py`.

---

## 3. Speech and Dictation dialog loads slowly; focus doesn't land on content

**Symptom:** dialog is slow to open; user has to switch to the JAWS cursor to
find anything, meaning default focus isn't landing on real content.

**Root cause (two separate bugs):**
- `main_frame.py:open_speech_hub` (~17751) runs `detect_has_gpu()` synchronously
  on the UI thread before the dialog is even constructed. That call chain
  (`speech/service.py:110` -> `bw_speech.py:has_nvidia_gpu`, ~line 148) spawns
  a blocking `nvidia-smi -L` subprocess every single time the dialog opens.
  Same freeze pattern as the `faster_whisper` import fix in `63aaf44` — that
  fix pattern (defer/cache the slow call) was never applied here.
- No dialog in this family calls `dialog_contract.py:focus_primary_control()`.
  That helper exists specifically so focus doesn't default to a button
  (`main_frame.py:7637` and three other dialogs use it) — but
  `speech_hub_dialog.py`, `speech_setup_dialog.py`, and `voice_browser_dialog.py`
  never call it, so focus parks on OK/Cancel instead of the first real control.

**Proposed fix:**
- Cache `has_nvidia_gpu()` per process (it doesn't change during a session) or
  move the probe off the UI thread and populate the GPU-dependent UI once it
  resolves, same as the `faster_whisper` fix.
- Call `focus_primary_control(hub.dialog)` right after `SpeechHubDialog`
  construction (`main_frame.py:17846-17851`), and add the same call to
  `speech_setup_dialog.py` and `voice_browser_dialog.py`.
- This is also the leading hypothesis for issue **#866** — see §6.

**Files:** `quill/ui/main_frame.py`, `quill/core/bw_speech.py`, `quill/core/speech/service.py`,
`quill/ui/speech_setup_dialog.py`, `quill/ui/voice_browser_dialog.py`.

---

## 4. Piper output is garbled / wrong-language with markdown source text

**Symptom:** exporting a text/markdown document to audio with a Piper voice
produces output that sounds like the wrong language or is garbled.

**Root cause:** markdown stripping is inconsistent across three synthesis
paths. Audio Studio batch export (`batch_export.py:_process_one`,
~line 427) and `document_speech.py:synthesize_document_to_chaptered_file`
(~line 330) both run text through `extract_text`/`_clean_markdown`
(`text_polish.py`) before calling Piper — clean. But
**`MainFrame.generate_speech_audio()`** (`main_frame.py:18153-18326`, Piper
call at line 18321) builds text straight from `editor.GetValue()` /
`GetStringSelection()` and passes it to `synthesize_with_piper` with **no**
cleaning step, and the live "Read Aloud" path (`read_aloud.py:_run_piper_live`,
~line 1138) does the same per-sentence. Raw markdown syntax (`#`, `**`, `_`,
`[label](url)`) fed straight to Piper's espeak-ng phonemizer mis-tokenizes
badly enough to sound like a different language. Voice/model selection itself
is fine — `voice_catalog.py` only lists English Piper voices, so this isn't a
language-default bug.

**Proposed fix:**
- Route both `generate_speech_audio()`'s text assembly and
  `_run_piper_live()`'s per-sentence text through the existing
  `extract_text`/`polish_for_tts`/`_clean_markdown` pipeline before synthesis,
  so all three paths share one sanitizer instead of two of three.
- Add a regression test: export a `.md` file with headings/bold/links through
  each of the three paths and assert none of the literal markdown punctuation
  reaches the synthesizer call.

**Files:** `quill/ui/main_frame.py` (~18153-18326), `quill/core/read_aloud.py` (~1138),
`quill/core/speech/text_polish.py` (reuse, no change expected).

---

## 5. Page numbers

**Symptom:** user asks whether QUILL can show "proper page numbers."

**Root cause:** this already exists for **BRF/braille** documents — full
page nav in `main_frame_braille.py` / `main_frame_braille_phase2.py` ("Read
Current Braille Page", "Go to Print Page...", etc.), detection in
`brf_page_detection.py`. But the live announce settings
(`braille_auto_announce_page_changes`, `braille_auto_announce_print_page_changes`,
`settings_specs.py:1878-1894`) are **off by default** and tucked in a
braille-specific menu, so it's easy to miss. For ordinary `.txt`/`.md`/`.docx`
documents there is only a form-feed-based "Go To Page" (`navigation.py:6-18`),
which does nothing useful without literal `\f` characters — there's no real
pagination model (no page count, no page-based navigation) for normal
documents.

**Proposed fix (two tracks, not a quick fix):**
- **Discoverability (small):** surface the two announce-page-changes settings
  more prominently for BRF users — e.g. mention them in the BRF onboarding /
  Braille menu help text, and consider defaulting
  `braille_auto_announce_page_changes` on for BRF documents specifically
  (print-page announce can stay opt-in, since it depends on a heuristic).
- **Real feature (larger, separate track):** a print/PDF/DOCX pagination
  model (estimated page count + page-based Go To/status announcement) is a
  genuine gap, not a bug. Recommend scoping this as its own beta-2-or-later
  issue rather than folding it into this fix pass — it likely needs a page
  metadata field on `Document` and per-format page estimators (PDF has real
  page breaks already available from the reader; DOCX/text would need a
  line-count-per-page heuristic or an explicit reflow model).

**Files (discoverability piece only):** `quill/core/settings_specs.py`,
`quill/ui/main_frame_braille.py`.

---

## 6. Issue #866 — crash recovery after 100+ second UI freeze

**Symptom:** `quill-wx-heartbeat-watchdog` logged the UI blocked continuously
from 48s up to 111+ seconds, and on next launch QUILL offered crash recovery.
No traceback was captured — the watchdog only detects staleness, not cause.

**Root cause:** not confirmed (no stack trace of the blocked thread), but the
duration and shape match a *synchronous, unbounded network or subprocess call
on the UI thread* rather than a quick blocking call — a few-second
`nvidia-smi` probe (§3) wouldn't produce 100+ seconds by itself, but a
synchronous Whisper/Kokoro model download or HF request with no timeout,
blocking on a slow or stalled connection, would. This is speculative but
consistent with both open bugs above.

**Proposed fix:**
- Add a hard timeout to every synchronous network call currently reachable
  from the UI thread in the speech/download paths (`whispercpp.py:_download_to_file`,
  any `huggingface_hub` calls, `engine_install.py` pip-install shellouts) —
  none should be able to block indefinitely.
- Audit whether any of those calls run on the UI thread at all versus
  `QuillTaskManager`; if the download entry points already dispatch to a
  worker thread, the freeze source is elsewhere and needs its own follow-up
  once a user can reproduce it with the heartbeat watchdog's thread dump (if
  it captures one) or a locally attached debugger.
- Track as its own issue with a link back to #866; don't consider it closed
  by §1/§2 fixes alone without confirmation.

**Files:** same as §1/§3, plus whichever caller turns out to run on the UI thread.

---

## 7. Issue #867 — UnicodeDecodeError crash opening a Latin-1/cp1252 file

**Symptom:** opening a non-UTF-8 text file (`0x92` = a Windows-1252 curly
quote) crashes QUILL instead of opening the file.

**Root cause:** `quill/io/text.py:read_text_document` (line 57) always decodes
with `encoding="utf-8"` (the caller-supplied default) and never falls back or
detects the actual encoding. `open_read.py:read_open_document` (line 148) is
the only caller for plain text and never passes an alternate encoding, so any
Windows-1252/Latin-1 file with high-byte characters (curly quotes, en-dashes,
accented letters outside the UTF-8-valid byte patterns) throws an unhandled
`UnicodeDecodeError` straight out of the open flow.

**Proposed fix:**
- On a `UnicodeDecodeError` from the `utf-8` decode attempt, fall back to
  `cp1252` (covers the reported case and is the most common non-UTF-8
  encoding for Windows text files), then `latin-1` as a last resort (`latin-1`
  never raises, so it's a safe terminal fallback — the read will always
  succeed).
- Track which fallback fired in `source_metadata["encoding_detected"]` (or
  similar) so a save doesn't silently re-encode as UTF-8 without the user
  knowing the source was different, and so a status-bar note can say
  "opened as Windows-1252" instead of asking nothing.
- Error code `QUILL-IO-TEXT-DECODE-FALLBACK` (informational, not user-facing
  as an error) when a fallback fires, for support triage if a fallback
  guesses wrong and mangles a document.
- Add a unit test opening a small cp1252-encoded fixture with curly quotes to
  lock in the fallback.

**Files:** `quill/io/text.py`.

---

## 8. Error codes for support triage

**Ask:** a user reporting an error code + message should let us pinpoint the
exact scenario without back-and-forth.

**Current state:** no error-code infrastructure exists. There are ~35 plain
`Exception` subclasses across `quill/core` (`SpeechError`, `EngineInstallError`,
`ReleaseAssetError`, etc.) with free-text messages only.

**Proposed design (small, mechanical, incremental — not a repo-wide sweep):**
- Add `quill/core/error_codes.py`: a `CodedError(Exception)` base with a
  class-level `code: ClassVar[str]` and a `__str__` that prefixes it, e.g.
  `[QUILL-SPEECH-WHISPER-DL-404] The model reference is out of date...`.
- Code format: `QUILL-<DOMAIN>-<SUBSYSTEM>-<SHORT-REASON>` (stable, greppable,
  no incrementing numbers to keep in sync by hand — e.g.
  `QUILL-SPEECH-KOKORO-PKG-MISSING`, `QUILL-IO-TEXT-DECODE-FALLBACK`).
- Migrate only the exception classes touched by this fix pass first
  (`SpeechError`/subclasses used in §1-3, a new decode-fallback note in §7) to
  prove the pattern; leave the other ~30 classes for a follow-up sweep rather
  than doing all of them in this PR.
- Wire `crash_report.py:build_diagnostic_bundle` to include
  `getattr(exc, "code", None)` in the bundle's exception metadata (it already
  captures `exception_class`/`exception_value`; add `error_code` alongside)
  so codes show up automatically in feedback-hub submissions like #866/#867,
  with zero extra work per call site.
- Status-bar/announcement surfacing (`main_frame_speech.py:1279-1296` and
  similar catch sites) already format `str(exc)` for the user — since the
  code lives in `__str__`, this falls out for free once the exception classes
  are migrated; no per-call-site changes needed there.

**Files:** new `quill/core/error_codes.py`; `quill/core/speech/provider.py`
(`SpeechError` base), `quill/stability/crash_report.py`.

---

## 9. Better component-acquisition path ("meet people where they are")

**Ask:** beyond fixing the bugs, make it easier for a user to actually get a
missing component in the first place.

This directly folds into §1 and §2 above, plus one cross-cutting piece:

- **Kokoro (§2):** message names the exact menu path
  (Tools > Speech > Install Kokoro ONNX) instead of alternatives that don't
  apply to most users.
- **Whisper (§1):** failure message distinguishes "you need to update QUILL"
  (stale pin) from "check your network" (transient) — right now both look
  identical, so a user has no idea whether retrying will ever help.
- **New, cross-cutting:** consider whether there should be one discoverable
  "Get missing components" surface (a single dialog/status listing every
  optional engine/model — Whisper, Kokoro, Piper voices, espeak, dictionaries
  — with install state and a one-click fetch for each) rather than each
  engine having its own separately-discovered trigger. `optional_components.py`
  and `release_assets.py` already model install state per component; a thin
  UI layer over that (reachable from the same place regardless of which
  feature the user was trying to use when they hit the gap) would mean a
  user never again has to guess which menu governs which missing piece.
  Recommend scoping this as a separate, slightly larger issue rather than
  bundling it into the §1/§2 bug fixes, since it's a net-new surface rather
  than a fix to an existing one.

**Files:** `quill/core/optional_components.py`, `quill/core/release_assets.py`,
new UI surface (TBD, separate issue).

---

## Suggested issue breakdown

1. Whisper stale HF pin (bug) — §1
2. Kokoro readiness check + message (bug) — §2, folds in §9's Kokoro piece
3. Speech Hub blocking GPU probe + missing focus_primary_control (bug) — §3
4. Piper raw-markdown synthesis paths (bug) — §4
5. Page number discoverability (small) + real pagination (feature, separate) — §5
6. #866 UI-thread network timeout audit (bug, needs repro confirmation) — §6
7. #867 text decode fallback (bug) — §7
8. Error-code infrastructure, scoped to the classes touched above (chore) — §8
9. "Get missing components" unified surface (feature, separate/larger) — §9

Let me know which of these to open as issues and which (if any) to start
implementing first.
