# QUILL 0.7.0 Beta 2 Release Notes

QUILL 0.7.0 Beta 2 is focused on helping you upgrade with less disruption. Your settings, keyboard shortcuts, recent files, and feature choices should follow you forward whenever they are still compatible. When an older setting is no longer usable, QUILL safely returns to the current default instead of leaving you with a feature or shortcut that appears not to work.

This release also includes a substantial collection of accessibility, reliability, portable-use, and macOS improvements. Setup is easier to follow, common keyboard commands behave more naturally, screen readers receive clearer information, and several crashes and focus problems have been corrected.

## Highlights

- Your compatible settings and keyboard customizations carry forward automatically.
- You can choose where QUILL stores your settings, dictionaries, recovery files, and logs.
- The portable Windows edition now starts with a double-click on `quill.exe`, identifies itself as QUILL rather than Python, and stores its data in a sibling `data/` folder.
- Setup and the AI Hub work more reliably on a new installation.
- VoiceOver support and standard macOS keyboard behavior have been significantly improved.
- Closing documents, checking for updates, opening help, and reporting bugs are more dependable.

## A smoother upgrade experience

When you upgrade from QUILL 0.5.0 or 0.7.0 Beta 1, QUILL now checks your saved settings and keyboard shortcuts as it starts.

QUILL keeps a saved choice when it still works with the current release. When an older choice refers to a command that no longer exists, uses an empty shortcut, or conflicts with another command, QUILL removes that unusable entry and uses the current default instead.

For most people, this happens quietly. You should not need to reset your preferences, edit configuration files, or manually repair older shortcuts.

### Keyboard shortcuts return to familiar behavior

Several shortcuts changed during the 0.7.0 development cycle. Beta 2 automatically repairs known older bindings so the menus, status information, and keyboard behavior agree again.

For example, `Ctrl+F` once used a QUILL Key sequence in an earlier beta. Beta 2 repairs that saved binding during the upgrade process so `Ctrl+F` returns to opening Find without requiring you to reassign it manually.

The same cleanup applies to other commands whose defaults changed, including Send to System Tray, Read Aloud, and Dictation.

### Your personal customizations are respected

QUILL starts with the current defaults and then applies your compatible personal changes. It does not replace your configuration with a complete copy of someone else’s settings.

When you import a profile or backup, only meaningful customizations from that file are imported. Your own unrelated keyboard choices are preserved.

### Nothing extra to run

A separate migration utility is still planned for more complex future upgrades. Beta 2 handles the most common upgrade needs automatically, so people moving from 0.5.0 or Beta 1 should not need a separate tool.

A future migration utility is expected to help with:

- larger settings-format changes;
- profiles and Quillins created by older beta releases;
- moving an entire family of customized shortcuts at once; and
- providing a reviewable record of settings that were changed or removed.

## Portable Installation Enhancements and Changes

As we always do, we listened to the community and made a number of very strategic changes in the way your data and the way that the installation is handled for QUILL when installing in portable mode.

QUILL no longer requires everyone to store application data in `%APPDATA%\Quill`.

During first-time setup, the new **Where QUILL stores your data** page offers choices designed for different ways people use QUILL:

- **Use the recommended AppData location.** This is the best choice for most installed copies of QUILL.
- **Keep the data beside portable QUILL.** When QUILL is running from a recognized portable bundle, your settings and recovery information can travel with the USB drive or managed folder.
- **Choose another folder.** You may select an existing folder or create a new one.

You can change this later under **Preferences > General**. Because settings, recovery data, and undo information may be in use while QUILL is open, the move takes place safely the next time QUILL starts. QUILL will offer to restart for you.

Portable mode is only offered when QUILL confirms that it is running from a real portable bundle: a folder containing `quill.exe` with a sibling `data/` folder. This is filesystem evidence of a deliberate portable install — not an environment-variable say-so — so an untrusted setting cannot redirect your data location.

## Portable bundle: `quill.exe` + `data/` (no more `run-quill.cmd`)

The portable bundle is now double-clickable. The launcher is `quill.exe` at the bundle root, and detection is driven by the presence of a `data/` folder next to it — the same pattern VSCode uses to identify a portable install.

- **Double-click to launch.** `quill.exe` at the bundle root starts QUILL with no environment setup. The previous `run-quill.cmd` wrapper is gone.

- **Detection is filesystem evidence.** A folder is treated as a portable install only when it contains `quill.exe` **and** a `data/` folder as siblings. A bare `QUILL_PORTABLE=1` environment variable is no longer sufficient. The Setup Wizard's portable radio button appears automatically when the bundle is verified.

- **Zero-setup from first launch.** The build script ships an empty `data/` folder inside the bundle, so the install is recognised as portable from the first time you double-click `quill.exe`. You do not need to create the folder yourself unless you are converting an installed build into a portable one.

- **Legacy bundles keep working.** A beta-1 portable bundle that still ships `run-quill.cmd` is accepted as back-compat evidence, so users upgrading from beta 1 do not need to take any action.
- **AI keys follow the bundle.** The DPAPI-encrypted `keys.enc` AI key store is activated automatically for verified portable installs — no environment variable to set.

The new launcher also identifies the product as **QUILL for All**, includes the actual QUILL version, and lists **Community Access** as the publisher. Screen-reader commands that report application or window version information (JAWS's Ctrl+JAWSKey+V, NVDA's Python-version readout, and similar) can now provide useful QUILL information instead of identifying the launcher as Python or speaking only the word “Version.” Installed editions continue to start normally and are not affected by this change.

The installer also keeps the desktop shortcut in sync on upgrade: a previous beta-1 install may have placed a `Quill.lnk` on your desktop pointing at the now-removed `run-quill.cmd`. Beta 2 removes that stale shortcut before writing the new one, so the desktop icon always launches the current launcher.

## Accessibility and screen-reader improvements

### Setup starts in the right place

Each Setup Wizard page now places focus on the page heading first. Screen-reader users hear the purpose of the page before moving into its controls or preview.

The preview is also presented as readable content rather than an editable text field. Sighted users continue to receive the styled visual preview.

### Simpler Back and Next buttons

The Setup Wizard buttons now read simply **Back** and **Next**. Decorative angle characters have been removed, so screen readers no longer announce phrases such as “less than Back” or “Next greater than.”

### A cleaner first launch

On a fresh installation, QUILL now opens the Setup Wizard before creating an Untitled document. This prevents a screen reader from announcing an unrelated document tab before setup begins.

After setup is complete, QUILL creates a new blank document automatically. Returning users continue to receive the familiar Untitled tab at startup.

### VoiceOver recognizes the editor on macOS

VoiceOver now identifies the main editor as a native, editable text area rather than a generic group. This provides more predictable text navigation and announcements on macOS.

Windows behavior is unchanged.

### Bug-report fields have useful names on macOS

VoiceOver now announces the name and purpose of each field in the Report a Bug window, including fields such as Summary and What happened.

The report window is now non-modal, which means you can switch back to the editor while writing your report. This makes it easier to check the document, repeat a problem, or capture the exact steps that caused it.

When you submit a bug report, QUILL copies it to the clipboard. It no longer opens a browser automatically unless you enable that option in Settings.

### The macOS Help menu works like a system Help menu

macOS now recognizes QUILL’s Help menu as the application’s standard Help menu. The conventional `Cmd+?` shortcut works, and VoiceOver’s Help-menu command can move focus there as expected.

Windows and Linux behavior is unchanged.

## More natural keyboard behavior

### Typing R and S no longer launches commands

Typing a normal `R` or `S` in a document no longer starts Read Aloud or opens Insert Snippet.

QUILL’s friendly shortcut descriptions are now displayed as menu information rather than being mistaken for single-letter system shortcuts. Your letters stay in your document, where they belong.

Regular shortcuts that include modifiers, such as `Ctrl+R`, were not affected.

### `Cmd+Q` quits QUILL on macOS

`Cmd+Q` now performs the standard macOS Quit action.

Quote Lines has moved to `Ctrl+Shift+Q`, and Unquote Lines has moved to `Ctrl+Shift+K`. QUILL repairs the older saved binding automatically when needed.

Windows users may continue to use `Alt+F4` or **File > Exit**.

### Word navigation works normally on macOS

`Option+Left` and `Option+Right` once triggered Back Location and Forward Location, preventing standard word-by-word cursor movement and interfering with VoiceOver reading commands.

On macOS, Back Location and Forward Location now use `Cmd+[` and `Cmd+]`. Windows continues to use `Alt+Left` and `Alt+Right`.

Older macOS bindings are corrected automatically during startup.

### Use Y, N, or Escape when closing an unsaved document

The unsaved-changes prompt now uses the operating system’s standard **Yes**, **No**, and **Cancel** choices.

You can press:

- `Y` to save;
- `N` to close without saving; or
- `Esc` to cancel and return to the document.

You may still Tab to the buttons and activate them normally.

## Setup and AI Hub reliability

### The AI Hub opens during first-time setup

The **Open AI Hub** button in the Setup Wizard now works on a brand-new profile. You can configure an AI provider during setup without first visiting another part of QUILL.

The AI Hub’s tabs, provider choices, instructions, and image-style choices now load correctly. The Hub opens reliably both from the Setup Wizard and later from the Tools menu.

### A new profile no longer causes startup typing failures

QUILL no longer runs editor caret features before a document is ready. The status bar and indent tone can begin working normally after setup without causing a startup failure.

### The Setup Wizard no longer reappears forever after an elevated installation

When QUILL was installed with administrator approval into a protected folder, the everyday user account could sometimes be unable to remove the “show setup” marker. This caused the Setup Wizard to reopen on every launch.

QUILL now remembers that the marker has already been handled, even when the protected file cannot be deleted. The marker's resolved path is the stable identity, so antivirus tools, filesystem mtime drift, or other processes that touch the marker file no longer fool the launch check into reopening the Setup Wizard. Setup appears when it is needed and stays out of the way afterward.

## Stability and reliability fixes

### Check for Updates opens normally

**Help > Check for Updates** and **Check for GLOW Updates** no longer close QUILL with an internal error. Both commands now open their information dialogs correctly in stable and beta channels.

### Closing an unsaved document no longer crashes QUILL

Choosing **Don’t Save** after pressing `Ctrl+F4` no longer causes QUILL to close unexpectedly while it tries to return focus to an editor that has already been closed.

Save and Cancel continue to return you to the appropriate place.

### Closing the last document is safer

A delayed caret event could occasionally arrive after the final editor had already closed, causing an unexpected error. QUILL now safely ignores that outdated event and closes the document normally.

### Imported profiles preserve your keyboard choices

Importing another person’s profile or a backup no longer replaces your personal shortcuts with that file’s default values. QUILL imports the actual customizations while keeping your unrelated choices in place.

### Saving settings no longer crashes QUILL

Selecting **OK** in Preferences, choosing **Reset to Factory Defaults**, or importing a settings file could close QUILL with `'MainFrame' object has no attribute 'set_theme'`. The routine that applies your settings after these actions was calling several methods that did not exist. All of these calls now reach the correct, existing code, so theme, spell-check, soft wrap, and dirty-title-style preferences apply immediately and reliably whenever you save settings.

### Quillins reporting status no longer crash QUILL

A Quillin calling the standard "set status" host action could close QUILL with `'MainFrame' object has no attribute '_set_status_text'`. The host adapter was calling a method that never existed; it now reaches the real status-bar update, so Quillins can report progress and results without crashing the app.

### The Developer Console correctly reports the active document name

`q.get_document_name()` in the Developer Console always returned an empty string because it called a method that never existed. It now returns the actual file name of the document you are editing.

### Quill Eraser opens correctly on documents with problems

Choosing **Tools > Writing > Quill Eraser** on a document that the engine had findings for closed QUILL with `TypeError: Dialog(): argument 1 has unexpected type 'MainFrame'`. The review dialog was being parented to the `MainFrame` mixin instance instead of the real `wx.Frame` it owns, so wxPython's SIP wrapper rejected the parent. The dialog is now parented to the real frame, so the review dialog opens, the focus lands on the findings list, and you can step through fixes with the keyboard as designed.

### First launch with the Setup Wizard pending no longer crashes

On a fresh install where the Setup Wizard still needs to run, the main window used to fail with `AttributeError: 'MainFrame' object has no attribute 'editor'`. The crash happened because `_build_menu()` ran during `__init__` and asked for the active editor's contents, but the editor was not built until after the wizard closed. The contextual menu refresh is now gated by a lifecycle flag (`self._ui_ready`) and falls back to "plain" markup when the editor is not yet present, so the wizard can open on a clean notebook and the menu items settle into the right state once you have a document to edit.

## Simple File Open dialog

QUILL can now open files through a keyboard-friendly **Simple File Open** dialog in addition to the standard Windows file open dialog. Both dialogs are reached from the same place — **File > Open...** or `Ctrl+O` — so there is still only one File > Open command.

- **Opt-in via Settings.** The new setting **Settings > General > Use simple file open dialog** controls which dialog QUILL shows. It is off by default; turn it on if you prefer a minimal, screen-reader-friendly picker.
- **A focused list and a small filter.** The Simple File Open dialog shows folders at the top of the list with a `[dir]` prefix and the current folder's files below. The **Filter** dropdown starts at **Supported files** (`.txt`, `.md`, `.html`, `.htm`, `.rtf`) and offers per-type filters and an **All files** option.
- **Keyboard-first navigation.** `Ctrl+L` focuses the path field. `Enter` in the path field navigates into a folder or opens a file. `Enter` in the file list activates the highlighted entry. `Backspace` in the list goes up one folder. `Ctrl+H` toggles hidden files. `Escape` cancels.
- **Recent locations and hidden files.** The **Recent** button opens a popup listing recently opened files for one-click re-open. The **Hidden** toggle shows or hides files whose names start with a dot or whose Windows hidden attribute is set.
- **Windows dialog fallback inside the dialog.** The **Use Windows Dialog** button opens the standard `wx.FileDialog` for one invocation. The setting does not change; the next time you press `Ctrl+O` you are back in the simple dialog. Use this when an edge case (a long file path, a custom file association) calls for the native picker.
- **Accessible error messages.** The status line below the file list shows the current directory, the number of visible entries, and any error. Permission-denied and not-a-directory errors keep the dialog open so you can correct the path and try again.
- **No new File menu items.** File > Open... remains the only File > Open command. The setting is the only switch.

## Help, diagnostics, and everyday usability

### The User Guide stays open and keeps its place

The User Guide and other static information pages no longer refresh every second. They remain stable, do not repeatedly reclaim focus, and stay open until you close them.

The live Browser Preview still refreshes automatically while you edit because that page is designed to follow your changes.

### Log and diagnostics folders open on every supported platform

**Open Log Folder**, **View Startup Logs**, and **Open Diagnostics Folder** now use the correct file manager for your operating system:

- File Explorer on Windows;
- Finder on macOS; and
- the default file browser on Linux.

### macOS menus now use the QUILL name

The application menu on macOS now says **Hide QUILL** and **Quit QUILL** instead of displaying the name of the underlying executable.

### System tray mode is handled honestly on macOS

macOS does not provide the same system-tray behavior used by the Windows and Linux versions of QUILL. When tray mode is selected on macOS, QUILL now explains that it is unavailable and closes normally instead of appearing to remain active without a usable icon.

Windows and Linux tray behavior is unchanged.

## Crash reports offer to submit

When an unhandled exception closes QUILL, a new dialog now appears (during the beta phase, by default) so the user can review a redacted summary of the report and choose whether to send it to the developers.

- **The dialog shows what will be sent.** A redacted preview lists the most recent commands, the active document's name and encoding, the platform and screen-reader information, and the last frames of the traceback. Personal data and credential-shaped strings are scrubbed before the preview is rendered.
- **Three user-controlled outcomes.** Send report submits the redacted summary to the project's public issue tracker (only with a configured GitHub token). Copy to clipboard puts the same redacted summary on the system clipboard. Don't send preserves the local crash file in `app_data_dir()/crash-reports/` and submits nothing.
- **Don't send is the default.** The dialog opens with the **Don't send** button as the default action so a user who opens it by accident does not accidentally send anything. Escape is bound to **Don't send**.
- **Three free-text fields.** What were you doing? What command triggered it? Expected behaviour? Every field is redacted before the report is built, so an accidentally pasted path or token never leaves the machine.
- **Always saves the local file.** The local traceback file is always written to `app_data_dir()/crash-reports/`, regardless of the user's choice in the dialog, so the user has a record of every crash.
- **Opt out in Preferences.** Settings > General > Offer to send crash reports automatically lets you turn the dialog off and return to the previous local-only path. The setting defaults to on during the beta phase so the team can hear about crashes without forcing you to opt in every time.
- **Works with the existing local fallback.** When QUILL cannot show the dialog (because wx is not yet alive, the user disabled the setting, or the dialog itself raised), the existing native `MessageBoxW` from finding #51 still fires, so the user always sees the path to the local crash file.

## Braille improvements

### Continuation page letters are announced correctly (BR-013)

QUILL now recognizes print-page continuation labels such as `7a` when they appear in a BRF document. The detailed braille status information reports the complete page label instead of shortening it to `7`.

This makes it easier to understand exactly where you are when a print page continues across multiple braille pages.

## What you need to do

For most people, nothing special is required:

1. Install or start QUILL 0.7.0 Beta 2.
2. Let QUILL check and update compatible settings during startup.
3. Continue working with your familiar files and preferences.

When QUILL needs to replace an outdated or conflicting setting, it uses the current default so the related feature continues to work. You do not need to edit `keymap.json` or manually rebuild your preferences.

Because this is a beta release, please continue to report anything that feels confusing, inaccessible, unreliable, or harder than it should be. QUILL is being built to meet people where they are, and that includes making setup, upgrades, everyday writing, and problem reporting as welcoming as possible.
