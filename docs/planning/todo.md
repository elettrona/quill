# QUILL Batch Document-to-Speech: Road to Golden State

**Scope:** what remains to take the batch document-to-speech + pronunciation +
text-cleanup + chapterization feature set from "core complete and proven
headlessly" to a shipped, polished, fully-wired "golden" state.
**As of:** 2026-06-24
**Companion docs:** [batch-document-to-speech-plan.md](batch-document-to-speech-plan.md) (the full plan, with the §1.1 status table) and [speech-project-format.md](speech-project-format.md) (the project JSON format).

The **core / non-UI layer is done** (14/14 in §1.1) and validated by the headless
stress harness (`tests/unit/core/speech/test_headless_speech_matrix.py`). What
follows is everything still between here and golden.

---

## 1. UI layer (the big remaining block)

None of the wxPython surface exists yet; the cores are built to be wrapped.

1. **Batch Export dialog** (U1) — folder pickers, file-type filter, engine/voice/speed (reuse the Speech Hub helpers), results list, Start/Cancel. Must pass the dialog inventory + button-contract gates from day one.
2. **Live Preview button** (U2) — audition the selected voice *and speed* before starting (§4.5).
3. **Tools menu wiring + background execution** (U3) — `batch_export_to_speech()` on `QuillTaskManager`, dialog-owned cancel `Event`, throttled announcements.
4. **Pronunciation manager dialog** (U4) — add-from-selection, Play original / Play corrected audition, global↔project move, all/per-engine scope.
5. **Chapter controls** (U5) — Chapters mode (none / single / separate), transition-sound chooser + volume, inter-article pause, and a chapter-list preview that reads back the headings before Start.
6. **Text-cleanup settings panel** (U6) — master toggle, Customize panel, presets, per-type (phone/email/URL) speed + Preview.
7. **Project "Remember / Reset"** (U7) — "Remember for this project" / "Reset to global", auto-remember on Start.

---

## 2. Wire the project profile into the app (§4.10)

The format, storage, and converters exist; the app does not use them yet.

- **Apply on open:** when a folder/project opens, `load_profile()` and apply.
- **Precedence resolver:** this-run > project > global > defaults, unit-tested as one shared path.
- **Single `current_project_dir()`** used by both settings and pronunciation dictionaries.
- **Save points:** the U7 surface plus auto-remember on Start.

---

## 3. Chapterization follow-ups (inside the done cores)

- **M4B native chapters** — only MP3 CHAP/CTOC is implemented; add the MP4 chapter-atom path (borrow ChapterForge's M4B branch) for the M4B output option.
- **`sound_id` resolution** — `chapters.sound_id` is accepted but not yet resolved to a real sound-pack file; today a generated placeholder chime (`earcon.py`) is used. Wire `sound_id` → `sound_pack.py` lookup, keep the placeholder as the default/fallback, and let the user pick or supply a WAV.
- **`separate` mode end-to-end** — `chapter_assemble` covers `single`; confirm the "separate file per article" path (one transcoded file per section, no concat) is wired through `batch_export` with per-article naming from headings.
- **Per-file chapter count** in `BatchFileResult` (§4.7.10) surfaced in the results list.

---

## 4. Keyboard-activation accessibility audit (systemic; surfaced by #709)

#709 (DECtalk preview not firing on Enter/Space) is the visible tip of a pattern:
a `wx.ListBox` emits **no** item-activated event (unlike `wx.ListCtrl`'s
`EVT_LIST_ITEM_ACTIVATED`), so any list that binds **only** `EVT_LISTBOX_DCLICK`
to an action is keyboard-inaccessible unless a key handler or the dialog's default
button covers it. **#709 itself is fixed** (voice browser now previews on Enter,
NumpadEnter, and Space). The rest to audit/fix:

- **No key handler at all** (verify Enter/Space activate, add if missing): `ssh_dialogs.py`, `copy_tray_dialog.py`, `prompt_library_dialog.py`, `remote_sites_dialog.py` (two listboxes), `main_frame_copy_tray.py`, `skill_library_dialog.py`, `publishing_tools.py`.
- **`EVT_LIST_ITEM_ACTIVATED` (ListCtrl)** handles Enter natively but **not Space** — decide whether Space should also activate (`info_pages.py`, `github_dialogs.py`, `sticky_notes.py`, `ai_thesaurus_dialog.py`, `abbreviation_manager_dialog.py`).
- **Recommended fix:** a small shared helper, e.g. `apply_listbox_activation(listbox, on_activate)`, that binds `EVT_LISTBOX_DCLICK` plus an `EVT_KEY_DOWN` handler for Enter / NumpadEnter / Space, consuming the event so the modal default button does not also fire. Apply it everywhere above, and add a lightweight gate/test so new `EVT_LISTBOX_DCLICK` bindings must pair with keyboard activation.

---

## 5. SSML (Phase 6, sequenced after the UI)

- `as_ssml` flag on the SAPI path (`_SVSF_IS_XML`) and eSpeak markup mode.
- SSML-mode assembly/escaping/validation with graceful `plain_fallback`.
- The guided SSML Builder (audible phoneme/vowel chart, prosody sliders, say-as/sub helpers).
- Rich batch-time handling: per-file substitution accounting, dry-run transform preview.

---

## 6. Testing and validation

- **Run the headless matrix against the real sample project** — the Word "Screenreader Primer" chapter files the user added (gitignored). Confirm `extract_sections` finds the chapter headings and the chaptered MP3 navigates correctly in a real player.
- **Richer `.docx` extraction** — tables, headers/footers, footnotes, list ordering (today: paragraph `<w:t>` only).
- **Long-document chunking** — wire the existing `tts_chunk.py` into the batch/assembly path for very long sections.
- **Engine-subprocess hardening** — consider migrating `read_aloud.py` subprocess calls to `stability.safe_subprocess` (pre-existing; not a blocker).

---

## 7. Docs, credits, and housekeeping

- **User guide + CHANGELOG** entries for batch export, chapters, pronunciation, text cleanup, and project profiles.
- **THIRD_PARTY / credits** — mutagen (new dependency) and the ChapterForge approach credit.
- **ChapterForge upstream** — fix the two bugs noted in plan §4.8.4 in ChapterForge itself: (1) non-contiguous gap chapters; (2) `write_tags_and_chapters` clobbering existing ID3 tags. (Both already fixed in QUILL's `chapters.py`.)
- **ElevenDesk research pass** — review `D:\code\ElevenDesk` (home: drive `S:`; upstream github.com/ivansoto0/ElevenDesk) for queue/library UX, voice browsing, and chunking ideas; fold license-compatible, accessible patterns into §4.2 / §4.5 / §4.10. (Cloud-only engine, so inspiration not dependency.)

---

## Suggested order

1. Batch Export dialog + Tools wiring + Preview (U1-U3) — makes the feature reachable.
2. Chapter controls + project Remember/Reset (U5, U7) + apply-on-open (§2) — the magical, configure-once flow.
3. Pronunciation + text-cleanup panels (U4, U6).
4. Keyboard-activation audit (§4) — small, high-value accessibility sweep; can land anytime.
5. M4B + sound-pack `sound_id` + richer docx (§3, §6).
6. SSML (§5).
7. Docs/credits + ChapterForge upstream + ElevenDesk pass (§7).
