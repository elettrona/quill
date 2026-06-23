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
4. Tab-character mode: Ctrl+Alt+M toggles Tab between smart indent and inserting
   a literal tab; new Tab Mode status cell + checkable Format menu item; spoken.
5. Removed the unfinished Pandoc Conversion Center menu item and its code.
6. Documented 1-5 in CHANGELOG, user guide, and release notes.

## Open

7. **(DONE) Hey QUILL settings menu item is now a checkable on/off toggle.**
   `toggle_dictation_voice_commands` flips `settings.voice_commands_enabled`
   directly, persists, syncs the menu check (both basic and full profiles), and
   speaks the new state. The menu item is `AppendCheckItem` and no longer reads
   "...(in Settings)".

8. **Speech model list is disjointed (largest item).**
   - whisper.cpp is missing from the model/engine list (only "fast"/openai show).
   - Want other engines added the way Vosk/Parakeet were wired.
   - Escape in the model list opens the whisper-models list instead of returning
     to the editor. Needs an escape/back contract and a coherent flow.

9. **(DONE) F7/F8 now speak a directional result on a freshly typed
   misspelling.** Instead of a silent "No next misspelling", F7/F8 force-speak
   "No misspellings ahead; N misspelling(s) behind" (and the reverse for F8) via
   the new `_announce_result` helper, so the user knows to reverse rather than
   assume the document is clean. Chose the spoken-count form over auto-wrap to
   keep the caret where the user left it. `_misspellings_behind_message`.

10. **Watch Folder queue "does nothing", returns to editor.** Likely an
    empty-state or no-op path with no spoken feedback. Needs investigation.

11. **(DONE) Ctrl+W closes the active document when there is no split preview.**
    The char-hook Ctrl+W branch consumed the key to close a side preview and,
    when none was open, swallowed it before the accelerator could fire. It now
    falls back to `close_current_document` (guarded to the document surface so it
    doesn't hijack Ctrl+W inside a modal/WebView dialog).

12. **Snapshots submenu confusion.** File > Snapshots IS a submenu (workspace
    snapshots: Save/Open Snapshot, Recent Snapshots, Open Documents in Current
    Workspace) populated by `_refresh_sessions_menu`. User sees right-arrow jump
    to Edit and Enter do nothing, which means it renders empty for them -- a
    population/timing bug to reproduce. Also a terminology collision: "Snapshot"
    is reused under File > Notebook (Save/Restore/Manage Snapshots). Decide:
    fix population, and rename one set to remove the collision (e.g. workspace
    "Snapshots" vs notebook "Versions").

13. **(DONE) "Check for External Changes" now speaks the no-change result.**
    The `ReloadAction.NONE` path force-speaks "'<file>' matches the on-disk
    version." via `_announce_result`, so it is confirmed aloud under a screen
    reader instead of updating a status the user never hears.

14. **Recent files: auto-clear missing entries (setting).** Add a setting to drop
    recent-file entries whose target no longer exists on disk, but **only for
    fixed/internal drives** -- never for removable/USB, network, or portable
    drives (a file "missing" there usually means the drive is detached, not
    deleted). New setting + drive-type detection.

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
