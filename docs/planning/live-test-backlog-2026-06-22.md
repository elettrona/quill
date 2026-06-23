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

7. **Hey QUILL settings menu item should be a checkable on/off toggle.** Today it
   tries (and fails) to jump to a settings tab. Make it a checkable menu item
   that flips the Hey QUILL setting directly and reflects current state.

8. **Speech model list is disjointed (largest item).**
   - whisper.cpp is missing from the model/engine list (only "fast"/openai show).
   - Want other engines added the way Vosk/Parakeet were wired.
   - Escape in the model list opens the whisper-models list instead of returning
     to the editor. Needs an escape/back contract and a coherent flow.

9. **F7 (next misspelling) "does nothing" on a freshly typed misspelling.** F7
   searches forward from the caret; after typing "teest" the caret is past it, so
   there is no *next* misspelling and the result ("No next misspelling") is
   silent under a screen reader (theme above). Fix: speak the result, and decide
   whether F7 should wrap to misspellings before the caret (recommend wrap, or a
   spoken "no misspellings ahead; N behind").

10. **Watch Folder queue "does nothing", returns to editor.** Likely an
    empty-state or no-op path with no spoken feedback. Needs investigation.

11. **Ctrl+W should also close the active document/window.** Today it only closes
    a split side-preview; otherwise it does nothing. Add document close as the
    fallback.

12. **Snapshots submenu confusion.** File > Snapshots IS a submenu (workspace
    snapshots: Save/Open Snapshot, Recent Snapshots, Open Documents in Current
    Workspace) populated by `_refresh_sessions_menu`. User sees right-arrow jump
    to Edit and Enter do nothing, which means it renders empty for them -- a
    population/timing bug to reproduce. Also a terminology collision: "Snapshot"
    is reused under File > Notebook (Save/Restore/Manage Snapshots). Decide:
    fix population, and rename one set to remove the collision (e.g. workspace
    "Snapshots" vs notebook "Versions").

13. **"Check for External Changes" says nothing when there are no changes.** It
    calls `_set_status("'<file>' matches the on-disk version.")` -> silent under a
    screen reader (theme above). User wants a dialog or at least a spoken result.

14. **Recent files: auto-clear missing entries (setting).** Add a setting to drop
    recent-file entries whose target no longer exists on disk, but **only for
    fixed/internal drives** -- never for removable/USB, network, or portable
    drives (a file "missing" there usually means the drive is detached, not
    deleted). New setting + drive-type detection.

15. **Search menu announces a "Separator" you can't arrow to.** The Search menu
    (`search_menu`, main_frame_menu.py ~530) ends with
    `_append_power_tools_search_items` + `_append_quillin_menu_items(... "Search")`,
    which likely append a trailing/leading separator even when the following
    section is empty. A dangling separator is read by the screen reader but is not
    focusable. Fix: only append the separator when items actually follow it.

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

## Proposed systemic fix (covers 9, 13, and the class)

Add a single helper, e.g. `_announce_result(msg)`, that sets the status text and
force-speaks it, and route explicit command results that have no focus change
through it. Open question for the user: in Quiet/Meeting verbosity modes,
forced speech bypasses suppression -- should explicit, user-invoked results
still be spoken in those modes (recommended: yes, because the user asked for
them), or stay suppressed?
