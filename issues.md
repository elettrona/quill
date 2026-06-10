# QUILL 1.0 — Pre-Release Code Review Issues

> **Status:** CRITICAL / HIGH / LOW / NIT / Magic all closed. 14 MEDIUM remain.
> All closed items documented in `CHANGELOG.md`.
> **Status legend:** ✅ FIXED · 🔵 Open · 🟡 Deferred (needs real Windows runtime)

---

## 1. Open issues — MEDIUM (14)

> M-1, M-2, M-4, M-10, M-11, M-12, M-13, M-16, M-17, M-18, M-19, M-20, M-21, M-22, M-23, M-25, M-26, M-27 are closed.

### Security and privacy

#### M-3 — `core/ai/external_engine.py:165` — `shlex.split` accepts any text
- **File / Category:** `quill/core/ai/external_engine.py:165` / SECURITY
- **Symptom:** A binary outside `PATH` silently passes the `shutil.which` / `Path(exists)` check. The Settings UI does not surface the resolved path of the executable.
- **Suggested fix:** In `configure_engine`, resolve the executable via `shutil.which(command[0])` and reject if it cannot be resolved; show the resolved absolute path in the Settings dialog before save.
- **Regression test:** `tests/unit/core/ai/test_external_engine.py::test_unresolvable_executable_rejected`

#### M-5 — `core/ai/foundation_models.py:120` — `asyncio.run` per call
- **File / Category:** `quill/core/ai/foundation_models.py:120` / BUG, THREAD-SAFETY
- **Symptom:** `asyncio.run(_go())` creates a new event loop per call. On macOS 26+ the Foundation Models SDK requires a single coroutine context; fresh loops leak OS resources.
- **Suggested fix:** Cache a loop on the backend instance and submit coroutines via `asyncio.run_coroutine_threadsafe`. Mark the loop thread daemon.
- **Regression test:** `tests/unit/core/ai/test_foundation_models.py::test_event_loop_reused_across_calls`

#### M-6 — `core/updates.py:228` — `_SIGNATURE_SALT` used as HMAC key
- **File / Category:** `quill/core/updates.py:228` / SECURITY
- **Symptom:** The signature salt (`"quill-manifest-signature-v1"`) is hard-coded and public. Any MITM can forge a valid signature. `QUILL_UPDATE_MANIFEST_KEY` is mentioned but not enforced in the binary.
- **Suggested fix:** Reject any manifest whose signature uses only the salt; move the key to a DPAPI-protected file at install time. Document the salt as a placeholder.
- **Regression test:** `tests/unit/core/test_updates.py::test_salt_only_signature_rejected`

#### M-7 — `core/python_sandbox.py:227` — `__builtins__` re-binding escape
- **File / Category:** `quill/core/python_sandbox.py:227` / SECURITY
- **Symptom:** The sandbox does not strip dunder attributes from `globals_ns`. A user transform can do `globals()["__builtins__"] = original_builtins`; `().__class__.__bases__[0].__subclasses__()` reaches `_io.FileIO` even with `open` blocked.
- **Suggested fix:** Set `globals_ns["__builtins__"] = safe_builtins` (a restricted dict, not the real module). Pass the same dict as both globals and locals to `exec`.
- **Regression test:** `tests/unit/core/test_python_sandbox.py::test_builtins_rebinding_blocked`

#### M-8 — `core/macros.py` — verify macro runner is async-safe
- **File / Category:** `quill/core/macros.py` / A11Y, THREADING
- **Symptom:** A macro that dispatches UI commands will block the worker thread if not marshalled back to the UI thread.
- **Suggested fix:** Confirm `MacroManager.play_macro` routes each command through `wx.CallAfter` or a `ThreadPoolExecutor` with explicit UI marshalling.
- **Regression test:** `tests/unit/core/test_macros.py::test_macro_dispatch_marshalled_to_ui_thread`

### I/O and parsing

#### M-9 — `io/pages.py:115-135` — `ID_NAME_MAP` patch not thread-safe
- **File / Category:** `quill/io/pages.py:115-135` / BUG, THREAD-SAFETY
- **Symptom:** `_patched_id_name_map()` temporarily replaces a global dict; two concurrent `.pages` opens corrupt each other's map.
- **Suggested fix:** Add a module-level `threading.Lock()` around the patch so concurrent reads serialize.
- **Regression test:** `tests/unit/io/test_pages.py::test_concurrent_reads_serialize_via_lock`

### Read-aloud and TTS

#### M-14 — `core/read_aloud.py:945-963` — DECtalk `Popen` has no wall-clock timeout
- **File / Category:** `quill/core/read_aloud.py:945-963` / BUG, RELIABILITY
- **Symptom:** If the DECtalk or eSpeak child hangs on malformed input, the worker thread waits forever.
- **Suggested fix:** Track `start = time.monotonic()`; after `_max_synthesis_seconds` kill the process and surface a `ReadAloudUnavailableError`.
- **Regression test:** `tests/unit/core/test_read_aloud.py::test_dectalk_killed_after_wall_clock_timeout`

#### M-15 — `core/read_aloud.py:179-192` — Piper stdin may exceed pipe buffer
- **File / Category:** `quill/core/read_aloud.py:179-192` / BUG
- **Symptom:** Very long documents can exceed the OS pipe buffer (64 KiB on Linux). No `timeout=`, so a hung Piper process is unkillable.
- **Suggested fix:** Write text to a temp file and pass it with the `-f` flag; add `timeout=`.
- **Regression test:** `tests/unit/core/test_read_aloud.py::test_piper_long_text_via_temp_file`

### Tools and audit

#### M-24 — `tools/dialog_button_contract.py:34-35` — unbacked `affirmative_id` not audited
- **File / Category:** `quill/tools/dialog_button_contract.py:34-35` / A11Y
- **Symptom:** A `hardened_custom` dialog with `SetAffirmativeId(wx.ID_OK)` but no `wx.ID_OK` button silently ignores Enter. Blind users press Enter repeatedly with no feedback.
- **Suggested fix:** Extend the audit to verify every `apply_modal_ids` `affirmative_id` has a backing button or `CreateButtonSizer` flag.
- **Regression test:** `tests/unit/tools/test_dialog_button_contract.py::test_unbacked_affirmative_id_flagged`

### UI lifecycle and threading

#### M-28 — `ui/main_frame.py:4547` — crash recovery re-show loop leaks focus
- **File / Category:** `quill/ui/main_frame.py:4547` / A11Y
- **Symptom:** Each loop iteration calls `editor.SetFocus()` via `CallAfter`, so when the dialog reopens focus races between the editor and the dialog's primary control.
- **Suggested fix:** Track "in sub-loop" and skip `editor.SetFocus` between iterations.
- **Regression test:** `tests/unit/ui/test_main_frame.py::test_crash_recovery_loop_does_not_steal_focus`

#### M-29 — `ui/assistant_tools.py:143-156` — `Run Python` sandbox blocks UI
- **File / Category:** `quill/ui/assistant_tools.py:143-156` / UX, THREADING
- **Symptom:** Long-running sandbox scripts block the UI thread and freeze the screen reader.
- **Suggested fix:** Run sandbox on a worker thread; show progress; disable Apply until done.
- **Regression test:** `tests/unit/ui/test_assistant_tools.py::test_run_python_does_not_block_ui_thread`

#### M-30 — `ui/main_frame_browse.py:174` — prewarm thread not cancelled before restart
- **File / Category:** `quill/ui/main_frame_browse.py:174` / LIFECYCLE
- **Symptom:** A new prewarm thread starts without checking for an in-flight one; two workers can compute the same cache simultaneously.
- **Suggested fix:** Cancel or `join()` the previous thread before starting a new one.
- **Regression test:** `tests/unit/ui/test_main_frame_browse.py::test_prewarm_thread_cancelled_on_repeat`

#### M-31 — `ui/sticky_notes.py:362` — bare `MessageBox` without contract
- **File / Category:** `quill/ui/sticky_notes.py:362` / A11Y
- **Symptom:** Uses raw `self._wx.MessageBox` without enter/exit announcements; inconsistent with the rest of the dialog contract.
- **Suggested fix:** Replace with `_show_message_box`-style helper.
- **Regression test:** `tests/unit/ui/test_sticky_notes.py::test_delete_confirm_uses_contract_helper`

#### M-32 — `ui/main_frame_image.py:160-167` — `time.sleep(0.1)` polling
- **File / Category:** `quill/ui/main_frame_image.py:160-167` / PERF
- **Symptom:** Polls 10×/sec during OCR runs; burns CPU.
- **Suggested fix:** Replace polling loop with `wx.Timer` for periodic progress updates.
- **Regression test:** Low-level test asserting the timer is wired.

---

## 2. Open files (MEDIUM only)

| File | Issues |
| --- | --- |
| `quill/core/ai/external_engine.py` | M-3 |
| `quill/core/ai/foundation_models.py` | M-5 |
| `quill/core/updates.py` | M-6 |
| `quill/core/python_sandbox.py` | M-7 |
| `quill/core/macros.py` | M-8 |
| `quill/core/read_aloud.py` | M-14, M-15 |
| `quill/io/pages.py` | M-9 |
| `quill/tools/dialog_button_contract.py` | M-24 |
| `quill/ui/main_frame.py` | M-28 |
| `quill/ui/main_frame_browse.py` | M-30 |
| `quill/ui/main_frame_image.py` | M-32 |
| `quill/ui/assistant_tools.py` | M-29 |
| `quill/ui/sticky_notes.py` | M-31 |

---

## 3. Triage order (remaining 14)

1. M-9 — `threading.Lock` around `ID_NAME_MAP` patch (`pages.py`)
2. M-14 — wall-clock timeout for DECtalk/eSpeak (`read_aloud.py`)
3. M-15 — Piper text via temp file (`read_aloud.py`)
4. M-5 — cache asyncio event loop (`foundation_models.py`)
5. M-6 — HMAC key rotation documentation (`updates.py`)
6. M-7 — `__builtins__` rebinding fix (`python_sandbox.py`)
7. M-8 — verify macro runner threading (`macros.py`)
8. M-3 — resolve executable via `shutil.which` (`external_engine.py`)
9. M-24 — unbacked `affirmative_id` audit (`dialog_button_contract.py`)
10. M-28 — focus leak in crash recovery loop (`main_frame.py`)
11. M-29 — Run Python off UI thread (`assistant_tools.py`)
12. M-30 — prewarm thread cancellation (`main_frame_browse.py`)
13. M-31 — `MessageBox` contract helper (`sticky_notes.py`)
14. M-32 — `wx.Timer` for polling (`main_frame_image.py`)

---

## 4. State of the union

### Severity roll-up

| Severity | Total | Fixed | Open |
| --- | ---: | ---: | ---: |
| CRITICAL | 0 | 0 | 0 |
| HIGH | 13 | 13 | 0 |
| MEDIUM | 32 | 18 | **14** |
| LOW | 22 | 22 | 0 |
| NIT | 16 | 16 | 0 |
| Magic/UX | 16 | 16 | 0 |
| **Total** | **99** | **85** | **14** |

### Closure cadence

| Sweep | MEDIUM closed | LOW closed | NIT closed | Notes |
| --- | ---: | ---: | ---: | --- |
| 1–6 | 0 | 3 | 11 | initial review + HIGH + Magic |
| 7 | 1 (M-27) | 6 | 1 | easiest LOWs/NITs |
| 8 | 0 | 5 | 1 | more LOWs |
| 9 | 2 (M-1, M-4) | 0 | 0 | watch-action humanization |
| 10 | 1 (M-2 resolved) | 2 | 0 | storage_mode + task_manager |
| 11 | 0 | 2 | 1 | DPAPI + cache-reset |
| 12 | 0 | 4 | 2 | §6/§7 fully closed |
| 13 | 0 | 1 (L-23) | 0 | csv_grid stride |
| 14 | **14** (M-10..M-26 batch) | 0 | 0 | stability + IO + AI + tools |
| **Total closed** | **18** | **22** | **16** | — |

### Deferred (needs real Windows runtime)

- 🟡 OCR-1 / OCR-3 — real Windows OCR engine and clipboard paths
- 🟡 AI-19 — live device-login endpoint
- 🟡 SET-2 — sensitivity-aware dictation backend
- 🟡 AGENT-1 — advisory-only by design

---

*14 MEDIUM open. All other severities closed. See `CHANGELOG.md` for closed items.*
