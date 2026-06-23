# Live-test backlog (2026-06-22)

Captured during an interactive screen-reader test pass. Items 1-6 are done and
validated in the working tree (uncommitted). Items 7+ are open.

## Root-cause theme: status confirmations are silent under a screen reader

`_set_status(msg)` is the standard way commands report their result. It updates
the status-bar text and calls the announcement engine, but the engine
**deliberately stays silent while JAWS/NVDA is active** (prism_bridge.py:303-314)
to avoid talking over the screen reader -- on the assumption the screen reader
will read whatever focus/control change the action caused. Commands that change
nothing focus-wise (an indent, a "no changes" check, a "nothing found" result)
therefore produce a visible status the user never hears. The Tab-indent fix
(item 3) used the `force=True` escape hatch. The same pattern explains items 9
and 13, and likely contributes to 10. A small systemic fix is proposed below.

## Done (this session)

1. F6 now reaches the document tab bar (Document Tabs region) when Show Tab
   Control is on.
2. "Clear All Notifications" added to the notifications status-cell context menu.
3. Tab indent/outdent (and list nest/promote) now spoken under a screen reader
   via forced announcement.
4. Tab-character mode: QUILL Key + U toggles Tab between smart indent and inserting
   a literal tab; new Tab Mode status cell + checkable Format menu item; spoken.
5. Removed the unfinished Pandoc Conversion Center menu item and its code.
6. Documented 1-5 in CHANGELOG, user guide, and release notes.

## Open

7. **(DONE) Hey QUILL settings menu item is now a checkable on/off toggle.**
   `toggle_dictation_voice_commands` flips `settings.voice_commands_enabled`
   directly, persists, syncs the menu check (both basic and full profiles), and
   speaks the new state. The menu item is `AppendCheckItem` and no longer reads
   "...(in Settings)".

8. **Speech model list is disjointed (largest item). (PARTIAL)**
   - **(DONE) Escape/back contract.** `_choose_speech_engine` now returns
     `(cancelled, provider)`; `open_speech_models` aborts to the editor when the
     chooser is cancelled. Previously `_choose_speech_engine() or
     self._speech_provider()` made Escape fall through to the default engine's
     model list — the "Escape opens the whisper-models list" bug. Unit-tested.
   - **(REMAINING) Engine-list completeness.** whisper.cpp is hidden when its
     binary isn't installed because the chooser lists `registry.available()`
     only; the user wants registered-but-not-installed engines shown with an
     install path (the "cloud and engine install" work this branch is named
     for). That is a model-manager redesign (show `registry.all()` with per-row
     install status + guided install per engine) and should be its own change.

9. **(DONE) F7/F8 now speak a directional result on a freshly typed
   misspelling.** Instead of a silent "No next misspelling", F7/F8 force-speak
   "No misspellings ahead; N misspelling(s) behind" (and the reverse for F8) via
   the new `_announce_result` helper, so the user knows to reverse rather than
   assume the document is clean. Chose the spoken-count form over auto-wrap to
   keep the caret where the user left it. `_misspellings_behind_message`.

10. **(PARTIAL) Watch Folder queue "does nothing", returns to editor.** The most
    likely cause matched the silent-status theme: when `core.watch_folder` is
    gated off in the active profile, `show_watch_folder_status` set a silent
    status and returned focus to the editor. That early return now force-speaks
    "Watch folder is unavailable in this profile" via `_announce_result`. If the
    feature is enabled and the monitor still feels empty, that needs a live
    repro (the dialog populates from the live queue).

11. **(DONE) Ctrl+W closes the active document when there is no split preview.**
    The char-hook Ctrl+W branch consumed the key to close a side preview and,
    when none was open, swallowed it before the accelerator could fire. It now
    falls back to `close_current_document` (guarded to the document surface so it
    doesn't hijack Ctrl+W inside a modal/WebView dialog).

12. **(DEFERRED — needs live repro) Snapshots submenu confusion.** Reviewed
    `_refresh_sessions_menu`: at menu-build time (`_menu_open_depth == 0`) it
    populates four items (Save/Open Snapshot, Recent Snapshots, separator, Open
    Documents in Current Workspace) and the deferral guard returns *before*
    clearing, so a deferred refresh cannot empty an already-built submenu. No
    blind code change made — the empty-render needs an interactive repro to find
    the actual trigger. The terminology collision (workspace "Snapshots" vs
    notebook "Snapshots") is a real, separate UX fix (rename notebook set to
    "Versions"); it touches many labels/docs and should be its own change.

13. **(DONE) "Check for External Changes" now speaks the no-change result.**
    The `ReloadAction.NONE` path force-speaks "'<file>' matches the on-disk
    version." via `_announce_result`, so it is confirmed aloud under a screen
    reader instead of updating a status the user never hears.

14. **(DONE) Recent files: auto-clear missing entries (setting).** New
    `recent_files_auto_clear_missing` setting (off by default, General tab).
    When on, `prune_missing_recent_files` drops entries whose file is gone, but
    only on a **confirmed fixed/internal drive** (Win32 `GetDriveTypeW` ==
    `DRIVE_FIXED`); removable/USB/network/unknown drives and non-Windows
    platforms are never probed and always kept, so a detached drive can't wipe
    its history. Applied at startup load; the pruned list is persisted. Logic is
    wx-free in `quill/core/recent.py` with unit tests.

15. **(DONE) Search menu no longer announces a dangling "Separator".** The
    power-tools group's first item declares `separator_before`, so when the regex
    Find/Replace items above are feature-gated off the menu opened with a leading
    separator. Added `_prune_menu_separators` (strips leading/trailing/doubled
    separators) and applied it to the Search menu after it is built.

16. **(DONE) Removed the Tools > Accessibility "Speak" items.** Speak Cursor
    Address, Speak Document Status, and Speak Selection Length removed: the three
    declarative power-tool entries, their handlers, the unused cursor_address
    imports, and the three ids in the wiring test. Public-surface snapshot
    regenerated; power-tools wiring + characterization tests pass.

17. **(DONE) Moved "View Startup Logs" from Help to Tools.** It now sits in
    Tools > Customize & Support next to "Open Logs Folder"; the Help copy is
    gone. Command id and binding unchanged, so the existing menu-id test still
    passes; handler docstring updated. (Note: it was never actually duplicated in
    Tools; this consolidation puts it where the user expected it.)

## Systemic fix (covers 9, 13, and the class) — DONE

Added `MainFrame._announce_result(msg)`: it sets the status text and force-speaks
it, the idiom for explicit command results that cause no focus change. Items 9
and 13 route through it. Decision (per the user): forced speech bypasses
Quiet/Meeting suppression for these results, because the user explicitly invoked
the command and asked for the confirmation.
