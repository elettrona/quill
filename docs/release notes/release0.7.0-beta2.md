# QUILL 0.7.0 Beta 2 Release Notes (in development)

This is the draft notes file for the 0.7.0 Beta 2 release. Sections here
ship into the final release notes when Beta 2 is tagged.

Beta 2 is the "settings carry-over" release. Most of the visible work is
in the load path: when a user upgrades from 0.5.0 or 0.7.0 Beta 1, their
saved settings, keymap, recent files, and feature profile travel with
them, and any saved entry that has become invalid is cleaned up on
startup instead of silently ignored.

A standalone migration utility is still planned. This release covers the
hot path so a user with a 0.5.0 install does not have to run one.

## Settings carry-over

### The rule

For keyboard shortcuts and any other user-tweakable setting, the default
is the answer. A user's saved setting is honored only if it is still
valid for the current build. If the saved setting is no longer valid
(unknown command id, conflicting chord, removed setting, etc.), it is
dropped and the default takes effect on the same launch — the user does
not have to know anything happened.

### How it works

The keymap load path (`quill.core.keymap.load_keymap`) now starts from
`DEFAULT_KEYMAP` and applies only the saved entries that survive three
checks:

1. The command id is still a registered command in `DEFAULT_KEYMAP`.
2. The chord is non-empty after stripping whitespace.
3. The chord does not collide with another command in the merged map.

Saved entries that fail any check are logged at debug level and dropped
from the loaded keymap. The surviving subset is persisted back to the
on-disk `keymap.json` so the file reflects "what was actually honored"
on the next launch. Files that are already clean (every saved entry
survives the merge) are left untouched — a small per-user delta stays
small.

The same rule applies to settings in general (not just keymap). The
`quill.core.settings_migration` module already provides a versioned,
nested serialization shape with `SETTINGS_SCHEMA_VERSION` and a
lossless round-trip between `from_versioned` and `to_versioned`. The
beta-2 load path is the place where "drop a saved entry whose key no
longer exists" gets the same treatment as the keymap.

### Why this matters for users

A user who upgraded from 0.5.0 to 0.7.0 Beta 1 had to reconfigure any
setting that moved in 0.7.0 — for example, the QUILL Key binding moved
to a brand-visible label, several headings moved off the QUILL-key
prefix and onto `Ctrl+Alt+1..6`, and the legacy preview chord was
retired. With the carry-over rule, those moved defaults take effect
automatically on the next launch, and any user entry that became
invalid is removed from the saved file so it does not cause confusion
later.

### What you may notice on the first launch after upgrading

The carry-over runs silently, but the behavior change is visible in
a few shortcuts that moved between 0.5.0 and 0.7.0. If you have been
using 0.7.0 Beta 1, the most likely case is `Ctrl+F` (Find):

- **Pressing `Ctrl+F` did nothing in 0.7.0 Beta 1.** Earlier in the
  0.7.0 line, `edit.find` defaulted to the QUILL-Key chord
  (`Ctrl+Shift+Grave, F`) instead of the conventional `Ctrl+F`. Your
  saved `keymap.json` on disk still records that stale binding, so
  when you press `Ctrl+F` in 0.7.0 Beta 2, the keystroke reaches
  the editor instead of opening Find — the editor sees it as text
  input or an unhandled key.

  In Beta 2 the load path rewrites the saved entry on first launch,
  and the corrected value is persisted back to `keymap.json` on the
  same launch. The next time you open QUILL, `Ctrl+F` opens Find as
  expected and stays that way. No dialog, no settings panel, no
  manual re-bind.

The same one-time rewrite applies to the other bindings that moved
off the QUILL-Key prefix and back to their conventional shortcuts
in this release (for example `Ctrl+Shift+Grave, T` for "Send to
System Tray", `Ctrl+Shift+Grave, R` for Read Aloud, and
`Ctrl+Shift+Grave, D` for Dictation). After the first launch, the
menu and the chord display in the status bar match.

### What is not a migration

- The on-disk `keymap.json` is still a small delta of overrides, not a
  full copy of `DEFAULT_KEYMAP`. The carry-over only touches entries
  the user had on disk.
- The legacy-rebinding table (`quill.core.keymap.legacy_rebindings`) is
  unchanged. It still rewrites the specific named stale bindings (for
  example `edit.find: "Ctrl+Shift+Grave, F" -> "Ctrl+F"`) on load. The
  carry-over is the safety net for everything else.
- The migration is silent. There is no dialog and no log file. Invalid
  entries are dropped; the user sees the default take effect on the
  affected menu item, key, or setting.

## Planned for the migration utility (Beta 3 or later)

A standalone migration utility is still on the roadmap. It will cover
the cases the carry-over cannot:

- **Settings schema upgrade** beyond the `SETTINGS_SCHEMA_VERSION` bump
  (when fields are renamed, retired, or restructured across the group
  layout that `settings_migration` provides).
- **Profile and Quillin import** from earlier betas, including the
  pre-0.7.0 flat keymap profile format and the pre-0.7.0 Quillin
  manifest v0 shapes.
- **Bulk keymap rebind** when a wholesale change happens — for example,
  if 0.8.0 moves an entire chord family, the utility will offer to
  remap the user's saved bindings as a batch.
- **Audit log** of every entry that was dropped, persisted alongside
  the cleaned keymap so the user can review what changed.

The Beta 2 carry-over is the foundation: a user with a clean install
on Beta 2 has nothing to migrate, and a user with a stale install on
Beta 2 has their keymap and settings already corrected before the
utility ever runs.

## Bug fixes

- **Read Aloud and Insert Snippet fired on plain R and S keystrokes
  (#612).** The friendly chord label in the Tools and Insert menus
  sat in the slot wxWidgets reads as a real native keyboard
  accelerator, and because the label does not start with a modifier
  name wx recognized, the bare letters `R` and `S` got bound as
  modifier-less global shortcuts. Every time you typed a normal `R`
  or `S` in any document, Read Aloud started (or paused) and Insert
  Snippet ran — outside the QUILL Key chord dispatcher entirely, so
  the QUILL Key conflict detector never saw the collision. The chord
  label is now shown as plain parenthetical text after the menu item
  name rather than as a wx accelerator, so the letters belong to
  your text again. Plain (non-chord) shortcuts like `Ctrl+R` were
  never affected.

- **First-run setup could not open the AI Hub, and once it did,
  every later launch crashed on startup (#614).** On a brand-new
  profile the wizard's "Open AI Hub" button raised an internal
  type error before the dialog could draw, leaving the AI Hub
  unreachable until you had already configured a provider elsewhere.
  And on the next launch after that, the editor caret handler
  crashed silently on every keystroke before you had even selected
  a document, blocking the status bar and the indent tone. Both
  crashes are fixed: the AI Hub now opens cleanly on first run from
  the wizard, and the editor caret handler no longer fires before a
  document is loaded.

- **Importing a profile or backup silently undid your keymap
  customizations (#614 follow-up).** When you accepted an exported
  keymap, the recipient's own overrides for individual chords were
  overwritten by the exporter's defaults, so a keymap you had
  carefully tuned (for example a home-row `Ctrl+Shift+B` for bold
  block) could be rolled back to the build's default just because
  you opened a colleague's profile. The import now only carries
  over entries that actually differ from the default, so the
  recipient's customizations are preserved.

- **Check for Updates crashed every time you opened it (#605).** The
  Help menu's Check for Updates and Check for GLOW Updates both
  rely on a small Markdown flattener to render the release-notes
  snippet into the dialog body. That flattener was removed in the
  About dialog rewrite earlier in the 0.7.0 line and the path was
  never updated, so Help -> Check for Updates raised an internal
  ImportError and QUILL announced it had to close. The flattener is
  back in place; Help -> Check for Updates and Check for GLOW
  Updates both open their informational dialog cleanly now, on
  every launch and every channel (stable, beta).

- **Cmd+Q now quits QUILL on macOS (#608).** Earlier in the 0.7.0
  line, `edit.quote_lines` was bound to `Ctrl+Q`, and on macOS
  wxPython maps `Ctrl` accelerators to the `Cmd` key, so pressing
  `Cmd+Q` (the universal macOS Quit shortcut) ran Quote Lines
  instead of quitting. There was no working quit shortcut on
  macOS. Quote Lines has moved to `Ctrl+Shift+Q` and Unquote Lines
  to `Ctrl+Shift+K`, and QUILL's quit command is now bound to
  `Ctrl+Q` (which maps to `Cmd+Q` on macOS). `Alt+F4` still
  works on Windows via the stock File -> Exit accelerator. A
  saved `keymap.json` that still has the old `Ctrl+Q` on Quote
  Lines is rewritten to the new chord on first launch, and the
  corrected value is persisted back so the next launch is clean.

- **AI Hub crashed when the setup wizard opened it (#614 follow-up).**
  The first pass at the AI Hub crash fixed the provider dropdown,
  the instructions list, and the image-style list, but the tab
  titles of the AI Hub Notebook (Provider, On-Device, Audio
  Services, Instructions, Advanced) and the on-device sub-notebook
  (Writing Tasks, Image Styles) were still wrapped in the same
  translation proxy that the dropdowns and lists were. The first
  time you opened the AI Hub, the dialog raised
  `TypeError: Item at index 0 has type '_LazyString' but a
  sequence of bytes or strings is expected` and QUILL announced
  it had to close. The tab labels are now plain text, so the AI
  Hub opens cleanly from the wizard on first run and from the
  Tools menu on every later launch.

- **First-run wizard Back and Next buttons were read with stray
  chevrons by screen readers (#611).** The Back and Next buttons
  in the setup wizard had decorative `<` and `>` characters
  baked into the button labels ("`< Back`" and "`Next >`"), and
  VoiceOver on macOS was reading them as "less than Back" and
  "Next greater than." JAWS in Forms mode on Windows had the
  same problem. The buttons now simply read "Back" and "Next,"
  which is what every screen reader announces, and what every
  sighted user sees on the face of the button.
