# QUILL 0.6.0 Release Notes

QUILL 0.6.0 is a major step forward for screen-reader-first writing, editing, automation, braille, code review, and extension-powered workflows.

This release is about speed, confidence, and control. You can type a short trigger and get a full template. You can open a braille file and know exactly where you are by page, line, cell, and progress. You can compare two files without visually scanning a diff. You can move through code by tokens instead of guessing where words begin and end. You can export to Word, inspect encoding problems, generate citations, choose better image-description prompts, and shape the sound layer so QUILL confirms what happened without talking over your screen reader.

Under the surface, QUILL 0.6.0 also introduces the most important architectural change yet: Quillins are now a real extension platform. They can own settings, appear in Preferences search, subscribe to document lifecycle events, contribute status-bar cells, declare dependencies, restrict network access, and initialize or shut down cleanly. The platform is designed so users stay in charge and extension authors cannot accidentally ship something unsafe, noisy, or inaccessible.

Everything remains keyboard-first and screen-reader-first. Every new view is a real navigable control. Every action is announced, undoable where appropriate, and discoverable. No mouse is required. No visual-only flourish is required. No silent full-file scanning happens behind your back.

If you are upgrading from QUILL 0.5.0, read **What works differently now** near the end. It lists the few places where menus, habits, or installer choices changed.

## Biggest changes at a glance

- **Insert Automation** turns typed abbreviations, smart triggers, `.LOG` files, document directives, and append anchors into one safe automation system.
- **The Quillin Extension Platform** now supports settings pages, searchable preferences, tabs, document events, lifecycle events, status-bar cells, dependencies, network allowlists, command descriptions, developer logging, announcement priority, scaffolding tools, and stronger validation.
- **Braille Mode** opens and edits braille text files while preserving bytes, form feeds, line endings, and layout. It adds braille-aware status, page navigation, page tools, and optional liblouis-powered translation through the QUILL Braille Pack.
- **Compare Mode** is now a first-class keyboard-driven workflow with difference navigation, speech announcements, and optional sound cues.
- **Code-aware editing** adds language profiles, token movement, manual language selection, and optional indentation tones.
- **Text encoding tools** help you find non-ASCII characters, jump to them, convert them to HTML entities, and save copies in narrower encodings without silent data loss.
- **Word and RTF export** lets you save documents as `.docx` or rich text through Pandoc, preserving real Word heading structure when the source contains structure.
- **Citation insertion** formats MLA 9, Chicago 17, and APA 7 citations from a simple labelled form.
- **The Snippet Gallery** (Insert > Snippet Gallery... or QUILL key, Shift+G) collects parameterized templates from all enabled Quillins into one browseable picker. Smart Insert ships three built-in entries.
- **The Vision Prompt Library**, contributed by Kelly Ford, gives Describe Image with AI twelve evaluated prompt styles and a full management dialog.
- **The Dynamic Keyboard Reference** now reflects the active command registry, your current bindings, and QUILL key layers.
- **Sound notifications** and **indentation tones** add optional non-speech feedback without making existing setups noisier.
- **Major accessibility and startup fixes** make bug reporting, JAWS focus, image description, first run, the user guide, update notifications, and macOS setup more reliable.

---

## Insert Automation: type a trigger, get magic

Insert Automation is the daily-workflow feature that changes how QUILL feels in practice. It combines typed shortcuts, templates, log files, smart text generation, document directives, and append anchors into one coherent keyboard-first system.

Everything is safe by design. Nothing scans your whole file silently. Nothing runs on a partial match. Nothing changes a read-only file. Every insertion is announced, discoverable, and one undo step.

### Typed abbreviations

Type a short abbreviation, press a delimiter such as space, comma, or period, and QUILL replaces the abbreviation with the full text.

The bundled **Smart Insert** Quillin ships with five abbreviations:

- **qbug** inserts a complete bug-report template with Title, Build, Screen reader, Windows version, Steps to reproduce, Expected result, Actual result, and Notes.
- **qmeet** inserts a meeting-notes template with today's date already filled in, plus Attendees, Purpose, Notes, and Action Items.
- **qlog** inserts today's date and time for a quick timestamped entry.
- **qtodo** inserts a short three-item to-do checklist ready to fill in.
- **qbrf** generates a multi-page BRF test document on the spot, ready to feed to the braille translator.

Your own abbreviations always win when there is a conflict. Quillin-provided abbreviations appear in the Insert Automation Reference and can be disabled individually.

### Smart text triggers

Type a command alone on a line and press Enter. QUILL replaces the whole line with the generated result. Smart triggers begin with `=` so they do not collide with ordinary sentences.

```text
=bug()            -> bug report template
=meeting()        -> meeting notes template
=journal()        -> journal entry with today's date
=todo(5)          -> five-item to-do checklist
=logentry()       -> timestamp at the cursor, formatted your way
=rand(3,4)        -> three paragraphs of four readable sentences each
=brftest()        -> a complete, predictable BRF test document
```

The parser is intentionally strict. A trigger activates only when it is alone on the current line, only accepts the allowed number and type of arguments, and rejects anything it does not recognize. Typing `=bug()` in the middle of a sentence is always safe. If a trigger would create a very large insertion, QUILL asks for confirmation before writing anything.

### `.LOG` file compatibility

Open a file whose first line is `.LOG` and QUILL behaves like Notepad: it finds the correct spot and inserts a fresh timestamp.

If the file contains a `QUILL-LOG-APPEND-HERE` anchor near the bottom, the timestamp lands just before the anchor and the anchor remains in place for the next entry. If the file is read-only, QUILL tells you rather than failing silently.

The timestamp format is configurable in **Preferences -> Smart Insert -> Log Mode**. Available formats include Long date and time, Short, ISO 8601, Date only, Time only, and custom `strftime` patterns.

### Append anchors

Any file can include a `QUILL-APPEND-HERE` marker near the bottom. Generated content lands before that marker instead of being shoved after footer notes, metadata, or other closing content. A stable anchor means generated text always goes exactly where you want it.

### Safety rules

Insert Automation follows clear safety boundaries:

- Abbreviations trigger only after an exact match and a delimiter.
- Smart triggers inspect only the current line and activate only on Enter.
- No file is scanned in full on open.
- Quillin-provided triggers run only while the Quillin is enabled.
- Every result is announced.
- Every insertion is one undo step.
- Read-only files are never modified silently.

---

## The Quillin Extension Platform: extensions become first-class citizens

QUILL 0.6.0 upgrades Quillins from a command-and-snippet mechanism into a full extension platform.

Quillins can now subscribe to events, own settings, add searchable preference pages, display live status-bar data, declare dependencies, restrict network access, log to a developer console, and initialize or shut down cleanly. The manifest, validator, JSON schema, API surface, and developer tooling have all been expanded so accessibility and safety are enforced at install and load time.

### Quillin settings and Preferences pages

Quillins can contribute their own settings pages. A Quillin declares its preferences as structured manifest data: control type, label, description, default value, validation rules, and related metadata. QUILL renders those settings using accessible, keyboard-navigable stock controls.

The Quillin never touches wxPython directly. QUILL handles layout, tab order, focus, keyboard navigation, search, reset, and accessibility.

Quillins with several groups of settings can declare **tabs** inside their preference page. Tabs are arrow-key navigable and clearly announced.

Examples included in 0.6.0:

- **Smart Insert** ships five tabs: General, Log Mode, Smart Triggers, Abbreviations, and BRF Testing.
- **BRF Tools** ships four specialized tabs: Translation defaults, Page Handling, Status Bar display, and Advanced diagnostics.

Quillin settings are stored per Quillin, survive restarts, and migrate when a Quillin updates its manifest. They appear in Preferences search alongside QUILL's own settings and are identified by Quillin, page, and tab.

Individual settings may now include **`search_keywords`**: extra synonyms and technical terms that help users find settings by the words they know. For example, a Date format setting can include `timestamp`, `iso`, and `strftime`, making the setting appear for any of those searches.

### Document and lifecycle events

Quillins can subscribe to document lifecycle events and run automatically when important moments occur.

QUILL 0.6.0 supports fourteen events:

| Event | When it fires |
| --- | --- |
| `document.opened` | A file was opened from disk |
| `document.activated` | The user switched to this document tab |
| `document.before_save` | Right before saving; a Quillin can validate or transform |
| `document.after_save` | After a successful save; safe to log, sync, or confirm |
| `document.before_close` | Before a tab closes; safe to warn |
| `document.after_close` | After a tab closes; safe to clean up |
| `document.created` | A new blank document was created |
| `document.loaded_from_session` | A document was restored from a crash or session file |
| `smart_trigger.entered` | Any smart trigger was activated |
| `abbreviation.expanded` | Any abbreviation was expanded |
| `quillin.enabled` | This Quillin was enabled or QUILL started with it active |
| `quillin.disabled` | This Quillin was disabled in Quillin Manager |
| `quill.shutdown` | QUILL is about to exit |
| `settings.changed` | A setting owned by this Quillin was changed by the user |

High-frequency events such as text changed, cursor moved, and key pressed are deliberately not available. They would allow a Quillin to observe keystrokes, which creates both privacy and performance problems.

Lifecycle events give Quillins a clean way to manage themselves. `quillin.enabled` is for initialization, activation announcements, cache building, or registration that requires the API to be live. `quillin.disabled` allows graceful cleanup. `quill.shutdown` allows state flushing before QUILL exits. `settings.changed` fires immediately when a user saves a preference change so the Quillin can hot-reload internal configuration without restarting.

Subscriptions can include `conditions` so they fire only for certain file types, path patterns, or content signatures. A template inserter can limit itself to files under `\journal\`. A `.LOG` handler can require `*.log` files. These filters are pure data, not code.

The capability gate is enforced. A Quillin must declare `document.events` in its capabilities to subscribe to events. Missing that capability, or missing the `main` module required to handle the event, fails validation at install time rather than failing later at runtime.

### Status-bar contributions

Quillins can add live cells to the QUILL status bar. A cell has a handler that QUILL calls on demand, such as after save, on tab switch, or on a timer. The handler's return value becomes the cell text.

Example manifest contribution:

```json
"status_bar": [
  {
    "id": "wordcount",
    "label": "Words: --",
    "handler": "get_word_count",
    "tooltip": "Current document word count",
    "width": 12
  }
]
```

To contribute a status cell, a Quillin declares `ui.status` in its capabilities, provides a `main` module, and describes the cell. The `tooltip` is read to screen-reader users when the cell receives focus, so the status bar remains navigable and informative rather than visual-only.

### Categories in Quillins Manager

Quillins can declare one or more category labels for filtering in Quillins Manager.

Available category labels include:

- `writing`
- `accessibility`
- `braille`
- `productivity`
- `developer`
- `formatting`
- `navigation`
- `ai`
- `integration`
- `education`
- `utilities`

Example:

```json
"categories": ["writing", "productivity"]
```

### Dependencies between Quillins

A Quillin can declare that it requires another Quillin to be installed and enabled.

```json
"requires": [{ "id": "com.quill.journalstamp", "min_version": "1.0.0" }]
```

QUILL verifies dependencies at load time. If a dependency is missing or too old, the dependent Quillin is blocked with a clear message.

### Network host allowlist

Quillins with the `net` capability can restrict which servers they are allowed to contact.

```json
"net_allowed_hosts": ["api.openweathermap.org", "*.example.com"]
```

When the list is non-empty, QUILL blocks connections to any host that is not on the list, even after the user has granted blanket `net` consent. Wildcard patterns such as `*.example.com` are supported.

### Command descriptions and search

Commands can now include a `description` field. This description appears in the keyboard reference and command palette as a one-line explanation that is separate from the menu title.

```json
"description": "Inserts a bug report skeleton with title, steps, expected, and actual fields."
```

### Developer logging with `api.log()`

Quillins with the `ui.log` capability can call `api.log(message)` to write structured log lines to the QUILL Developer Console.

The Developer Console opens from **Tools -> Developer Console** in development builds and can be toggled with `QUILL_DEV_BUILD=1`.

In production, with the console closed, `api.log()` is a no-op. It adds zero normal-use overhead and never writes to files or speaks to the screen reader.

### Announcement priority

`api.announce()` now accepts a `priority` keyword argument.

```python
api.announce("Saved.", priority="quiet")
api.announce("File not writable.", priority="urgent")
```

Valid values are `quiet`, `normal`, and `urgent`. The host maps those values to the screen reader's urgency channel. Use `quiet` for informational messages and `urgent` only for errors that need immediate attention.

### Quillin scaffold tool

A new command-line scaffold tool creates a ready-to-edit Quillin directory:

```text
python -m quill.tools.quillin_new com.example.myquillin "My Quillin"
```

Options include:

- `--layer1` for snippet-only Quillins with no Python.
- `--categories` to add category metadata.
- `--doc-events` to include sample lifecycle handlers.
- `--status-bar` to include a sample status cell.

The tool writes `manifest.json`, `extension.py`, `README.md`, and `LICENSE`, then tells the author the next three steps. Authors should run `quillin_lint` on the output before publishing.

### User control and safety enforcement

The Quillin platform is built around user control.

Open **Tools -> Quillins Manager** to enable or disable any Quillin. Select a Quillin and press **Enable** or **Disable**. The change takes effect immediately; no restart is required. Disabling a Quillin stops all of its commands, event handlers, and status-bar cells. Its preferences are preserved so it picks up where it left off if re-enabled.

Four sensitive capabilities require a confirmation dialog every time a Quillin tries to use them:

| Capability | What it does |
| --- | --- |
| `fs.read` | Read a file from disk |
| `fs.write` | Write a file to disk |
| `net` | Make a network request |
| `settings.core.write` | Change a QUILL-wide setting |

When a Quillin requests one of these actions, QUILL pauses and shows a dialog like this:

```text
A Quillin is requesting the 'fs.read' capability for: read_file(path). Allow this action?
```

Choosing no raises a `ConsentDeniedError` that the Quillin must handle gracefully. This confirmation appears for every individual action, not once at install time. A Quillin that reads files can never read one you have not explicitly approved.

The remaining capabilities are granted once at install time, or pre-granted for bundled Quillins. These include editor access, UI announcements, clipboard, storage, `settings.own.*`, document events, status bar, and developer log.

Each document event subscription includes an `enabled_by_default` field. If it is false, the event starts inactive. Users can change this any time from Quillins Manager: select the Quillin and choose **Configure Events...** to see each event subscription with a checkbox. Turning an event off stops the handler from firing; turning it back on resumes it. Per-event state is persisted in `state.json` alongside enable/disable and capability grants.

Capability declarations are enforced, not advisory. If a Quillin calls an API it did not declare in `capabilities`, QUILL blocks the call with a `CapabilityError` and notifies the Quillin instead of crashing. Declarations are validated by `quillin_lint` at install time and re-validated by the manifest parser at load time.

Third-party Quillins remain locked off for QUILL 1.0. The SEC-8 gate, `core.third_party_plugins`, is `locked_off`. A shipping build never discovers, loads, or executes third-party Quillin code. Quillins Manager still opens and remains fully navigable; it simply reports that third-party Quillins are disabled. This gate will lift when the publishing and review process is ready.

`min_quill_version` is enforced at load time. If a Quillin declares `"min_quill_version": "0.6.0"` and the running QUILL is older, the Quillin is rejected during discovery and listed in the Manager with an explanatory error such as `requires QUILL 0.6.0 (running 0.5.x)`.

`requires` is also enforced at load time. If a Quillin depends on another Quillin that is not installed, or is installed at a version too old to satisfy `min_version`, the dependent Quillin is blocked. The Manager shows the specific dependency error. Circular dependencies are caught during validation.

`net_allowed_hosts` is enforced at every fetch call. If a Quillin declares `"net_allowed_hosts": ["api.example.com"]` and tries to fetch from another host, QUILL blocks the call before it reaches the network, even if the user has granted the `net` capability. Wildcard patterns such as `*.example.com` allow subdomains but not the bare domain. An empty `net_allowed_hosts` list with the `net` capability preserves the current behavior: any host is reachable with user consent.

### Five bundled Quillins

QUILL 0.6.0 ships five bundled Quillins. Each is both a useful extension and a reference implementation for the framework.

- **Smart Insert** (`com.quill.smartinsert`) provides typed abbreviations and smart triggers for bug reports, meeting notes, log entries, to-do lists, and BRF test documents. It includes five tabs of configurable preferences, categories `writing`, `productivity`, and `formatting`, plus command `description` fields on every command.
- **BRF Tools** (`com.quill.brftools`) provides preferences for braille translation, page handling, and status-bar display. Its categories are `braille` and `accessibility`.
- **Journal Stamp** (`com.quill.journalstamp`) subscribes to `document.created`, `document.after_save`, `document.loaded_from_session`, `quillin.enabled`, and `settings.changed`. It can insert a date header, announce word count and daily-goal progress after save, announce restored documents, log activation, and hot-reload preferences. Its date-format and daily-goal controls include `search_keywords`. Its categories are `writing` and `productivity`.
- **Document Guardian** (`com.quill.docguardian`) subscribes to `document.before_close`, `document.before_save`, `document.after_save`, `quillin.enabled`, `quillin.disabled`, and `quill.shutdown`. It can warn on unfinished documents, stamp an `Updated:` line, confirm saves with file size, announce and log activation, announce deactivation, and clean up on shutdown. Its categories are `writing` and `productivity`.
- **Status Scribe** (`com.quill.statusscribe`) adds a live word, character, and sentence count to the status bar. It updates after every save and on tab switch. It demonstrates `status_bar` contribution, `ui.log` developer logging, `quillin.enabled`, `quillin.disabled`, `settings.changed`, lifecycle events, and announcement priority. Its categories are `writing`, `productivity`, and `accessibility`.

### What's new in the Quillin platform

- **Timer events (schedule)** — a Quillin can now schedule background work every N seconds (minimum 60, maximum 86400). Timers run in dedicated threads so the editor never blocks. Status Scribe uses this to refresh its word-count cell every 5 minutes without a user action.
- **File-type contributions (file_types)** — a Quillin can declare which file extensions it handles. When a matching file opens, the Quillin's handler fires automatically. BRF Tools announces the braille page count when a `.brf` or `.brl` file opens.
- **Snippet gallery (snippet_gallery)** — a Quillin can contribute named, parameterized templates to a browseable gallery. Open it from **Insert → Snippet Gallery...**, pick a template, fill in any prompts, and the text lands at the cursor. Smart Insert ships three built-in gallery snippets: a report header, a meeting invite, and a Markdown bug report.
- **Document lifecycle events now fire** — the 14 declared events (`document.opened`, `document.after_save`, `quill.shutdown`, and the rest) now actually dispatch at runtime. Journal Stamp and Status Scribe are live.

---

## Braille Mode: professional braille editing inside QUILL

QUILL can now open and edit formatted braille text files. The goal is to let a braille proofreader move through a transcription the way it is actually laid out: by braille pages, lines, cells, hard page breaks, and progress through the document.

### Opening and saving braille files

Open a braille file the same way you open any other file. QUILL reads it as braille text and scans it for any character that is not braille ASCII. Nothing is transformed on the way in; the document reflects the file's bytes.

Saving is byte-for-byte. QUILL does not trim trailing spaces, normalize line endings, or remove form feeds. Hard page breaks are preserved. If the text contains characters outside the braille-ASCII range, QUILL still saves them as-is and gives one non-blocking spoken warning so nothing is silently changed. A round trip of open and save returns an identical file.

### Braille status cell

While a braille file is active, the status bar includes a braille cell that updates as you move:

```text
BRF Pg 12/87 | Ln 14/25 | Cell 31/40 | Print 7
```

That status gives the braille page, line within the page, cell within the line, and print page. Print-page detection arrives in a later phase; until then the print segment reads `Print ?`.

### Braille commands

Braille commands now live under **Tools -> Braille**. Key bindings are intentionally left unset so QUILL does not collide with screen-reader keys or existing editor shortcuts. You can assign your own bindings in the keyboard customizer or run the commands from the Command Palette.

The Braille menu is organized into three groups.

**Status** includes:

- Read Braille Status, respecting your status verbosity.
- Read Detailed Braille Status.
- Read Current Line and Cell.
- Read Current Braille Page.
- Read Current Print Page.
- Read Progress Summary, which reports how far through the document you are.

**Navigation** includes:

- Go to Braille Page..., where you type a page number.
- Next Braille Page.
- Previous Braille Page.

Moving past the first or last page tells you there is no more.

**Page Tools** includes:

- Insert Braille Page Break, which inserts a form feed.
- Remove Braille Page Break at the cursor.
- Recalculate Page Map, which rebuilds the page map after edits.
- Normalize Line Endings, currently present as a placeholder.

Every braille status and navigation command is safe to run on a non-braille document. QUILL simply says, `This is not a braille document`, and does nothing else.

### Translation with the optional QUILL Braille Pack

Forward and back translation between print text and braille require the optional **QUILL Braille Pack**, which can be selected during installation.

The pack uses a three-layer architecture:

1. A full technical catalog of every available liblouis table.
2. User-facing profiles that map friendly names to the correct tables.
3. The translation runtime itself.

When the pack is installed, the Translation submenu is organized into three sections.

**UEB (Unified English Braille)** includes:

- Contracted, Grade 2.
- Uncontracted, Grade 1.
- Translate Selection to UEB.
- Back-Translate UEB.

**Standard American English (Legacy)** includes:

- Contracted, Grade 2.
- Uncontracted, Grade 1.

These use the traditional North American English tables.

**More Languages** is populated automatically from the pack's profile catalog. It includes German, French, Spanish, Russian, Korean, and dozens more. Languages with both contracted and uncontracted variants appear as their own sub-group.

When the pack is absent, the Translation submenu is hidden entirely; you do not see disabled items. The Translation submenu is also hidden in Safe Mode.

Forward translation opens the BRF result in a new document and tells you how many braille pages it produced. Back-translation always opens its result as a clearly labelled draft because automatic back-translation is not authoritative. Translation runs entirely out of process, so a liblouis failure cannot take QUILL down.

---

## Compare Mode: review differences by keyboard and by ear

File comparison is now a first-class keyboard-driven workflow.

Open a comparison and move through it with:

- **F8** for next difference.
- **Shift+F8** for previous difference.
- **Ctrl+F8** to re-announce the current difference.
- **Alt+F8** to hear just the words that changed on the current line.

Differences are presented as a real list, so you can review them one at a time with your screen reader.

If you use a sound pack, Compare Mode also provides distinct cues for opening a comparison, closing a comparison, stepping between differences, and bumping against the first or last difference. The result is a faster review loop: speech tells you what changed, and optional sound tells you where you are in the comparison.

---

## Code-aware editing: move through source files more intelligently

When you open a source file, QUILL loads a language profile from the file extension. Recognized profiles include:

- Python
- JavaScript
- TypeScript
- Kotlin
- Shell
- Markdown
- JSON
- TOML
- SQL

Files with unrecognized extensions use a sensible plain-text fallback.

**Next Token** and **Previous Token**, both in the Navigate menu, move the caret to the next identifier, keyword, operator, or literal. This is more predictable than ordinary word movement when reading code by ear.

**Navigate -> Set Document Language** lets you override the automatic choice. This is useful for unsaved buffers, unusual extensions, or snippets pasted into plain files.

Paired with indentation tones, code-aware editing lets structure come through as pitch while token movement lets you move through meaning.

---

## Sound notifications and indentation tones: optional audio feedback without extra speech

QUILL can now play short non-speech audio cues, called earcons, at meaningful moments such as a file save, a successful search, or opening a comparison. The goal is to let your screen reader remain focused on text while a quick sound confirms that something happened.

### Sound packs

Sounds come from a **sound pack**: either a folder or a single `.qsp` file containing audio clips and a small manifest that maps events to sounds. QUILL ships with a bundled pack called **Ink**, and you can add your own.

### QUILL key confirmation tone

When you press the QUILL key, **Ctrl+Shift+Grave**, to arm the prefix, QUILL now plays a short two-tone ping named `quill_key_pressed`. It is distinct from every other earcon, so you receive instant audio confirmation that the prefix is live without waiting for speech.

This earcon is included in all bundled sound packs and can be toggled individually in **Tools -> Reading & Dictation -> Sound Events...**.

### Per-event control

Open **Tools -> Reading & Dictation -> Sound Events...** to switch individual sound events on or off. Events are grouped into Earcons, Compare, and Indentation tones, so you can keep the cues you like and silence the rest.

**Toggle Sound Notifications** turns all sound notifications on or off at once and plays a short on or off cue so you know where you landed.

Sound is opt-in. Most earcons remain off until you choose a sound pack and enable events, so upgrading does not make your current setup noisier.

### Indentation tones for code

Indentation tones are also opt-in. Pick a musical scale under the **Indentation tones** setting, or leave it Off.

When enabled, QUILL plays a pitch that rises as your caret moves deeper into indented code and falls as you move back out. Blank lines stay silent and hold the last level, so moving through gaps does not chirp. It is a quiet ambient way to feel the shape of code without counting spaces.

---

## Text encoding tools: find, inspect, convert, and save safely

New commands under **Format -> HTML & Encoding** make character and encoding cleanup accessible from inside QUILL.

### Show Non-ASCII Characters

**Show Non-ASCII Characters** opens a read-only report of every character beyond plain ASCII. Each entry includes:

- Line and column.
- Codepoint.
- Character name.
- Whether it converts cleanly to Latin-1.
- Whether it converts cleanly to Windows-1252, also known as MS-ANSI.

This replaces the old command-line ritual of running a file through tools such as `iconv`, inserting a sentinel string, and hunting for what failed.

### Jump between the report and source

While the report is open, move to any character entry row and choose **Format -> HTML & Encoding -> Jump to Source Line**. QUILL switches to the source document and lands on the reported line.

Assign this command a key in the Keymap Editor for faster character-by-character review.

**Jump Back to Non-ASCII Report** returns focus to the report tab so you can continue reviewing the list without using the mouse.

### Convert Non-ASCII to HTML Entities

**Convert Non-ASCII to HTML Entities** rewrites accented letters and symbols as HTML entities, such as `&eacute;`, or numeric entities such as `&#233;` when no named entity exists. Ordinary text and existing markup are left alone.

This is the reliable command when you need to feed text to a tool, such as Pandoc, that refuses high characters.

### Re-encode As...

**Re-encode As...** saves a copy in the encoding you choose:

- UTF-8.
- UTF-8 with a byte-order mark.
- Latin-1.
- Windows-1252.
- ASCII.

Anything that does not fit a narrow target is written as a numeric HTML entity instead of being silently replaced by a question mark. Nothing is quietly lost.

---

## Save as Word or RTF

QUILL can now hand your work over as a Word document or rich text file.

Choose **File -> Save As...**, then select **Word Document (`*.docx`)** or **Rich Text** from the type list. QUILL converts the document on the way out, avoiding the copy-paste-into-Word routine.

The conversion is handled through Pandoc with real Word styles. If your source has headings, those become actual Word headings, not bold text that merely looks like a heading. That keeps the exported file navigable for the next person's screen reader.

The result reflects the structure of the source. A richly formatted Markdown or HTML document exports with that structure. A plain-text file exports as a tidy but unadorned document because there was no structure to carry. QUILL tells you that instead of quietly flattening your work.

---

## Citations without the tears

**Insert -> Insert Citation...** opens a plain labelled form for creating citations.

You choose:

- Source type: book, journal article, or website.
- Style: MLA 9, Chicago 17, or APA 7.
- Output: in-text citation, full bibliography entry, or both.

Then you fill in the facts you know, such as author, title, year, and related fields. QUILL handles the punctuation, ordering, formatting details, and insertion at the cursor.

The point is simple: screen-reader users should not be at a disadvantage because citation formatting is visual, finicky, and easy to get wrong.

---

## Snippet Gallery: parameterized templates in one place

The Snippet Gallery collects reusable, fill-in-the-blank templates contributed by Quillins into a single browseable picker. Open it from **Insert > Snippet Gallery...** or press **QUILL key, Shift+G**.

A gallery dialog opens showing every available snippet, grouped by Quillin. Select one, read the preview, and press **Insert**. If the snippet has parameters — a title, a date, a subject line — QUILL prompts you for each one in sequence, then inserts the completed text at your cursor.

Smart Insert ships three built-in entries:

- **Report Header** — a titled section with an author and date line. Prompts: report title, date.
- **Meeting Invitation** — subject, date, location, and agenda block. Prompts: subject, date/time, location, agenda.
- **Bug Report (Markdown)** — a full Markdown bug-report skeleton with title, environment, steps to reproduce, expected result, and actual result. Prompts: title.

Any Quillin can contribute gallery entries by adding a `snippet_gallery` block to its manifest. No extra capability is required.

---

## Vision Prompt Library: better AI image descriptions, contributed by Kelly Ford

QUILL 0.6.0 includes a Vision Prompt Library for **Describe Image with AI**, contributed by [Kelly Ford](https://github.com/kellylford).

Kelly independently built and evaluated twelve prompt styles drawn from his [Image Description Toolkit](https://github.com/kellylford/Image-Description-Toolkit), an experimental toolkit for accessible image interaction.

Instead of one hardcoded image-description prompt, QUILL now lets you choose from twelve IDT-evaluated styles. Each style targets a specific use case, such as:

- Concise identification.
- Detailed scene description.
- Alt text optimized for web publishing.
- Screen-reader-first narrative.
- Document-context interpretation.
- Additional curated description styles.

These styles are evaluated and curated, not randomly generated.

### How the library works

- **Zero disruption by default.** If you never change a setting, Describe Image behaves exactly as before. The default IDT style is applied silently with no extra clicks.
- **Try a different prompt.** After a description arrives, a **Try a different prompt...** button appears in the review dialog. One click re-runs the description with the next style in the list. No re-uploading, no dialog re-opening, and no extra navigation.
- **Opt-in pre-describe picker.** Enable the style picker in **Settings -> AI** if you want to choose a prompt style before describing an image. Once enabled, QUILL shows a focused keyboard-navigable list of the twelve styles before every description.
- **Manage Image Prompts dialog.** Open **AI Hub -> Image Prompt Styles...** to review all built-in styles with a read-only preview pane, toggle styles on or off, set the default, and add custom prompts. Built-in styles are immutable; custom prompts are additive.
- **Settings sync immediately.** A bug where AI Hub changes to vision settings, including picker toggle and default style, did not apply until restart. That is fixed. Changes apply as soon as you save.

Kelly's Image Description Toolkit is worth bookmarking: <https://github.com/kellylford/Image-Description-Toolkit>.

Kelly also maintains several screen-reader-friendly applications:

- [QuickMail](https://github.com/kellylford/QuickMail), an accessible IMAP email client.
- [RSSQuick](https://github.com/kellylford/rssquick), an accessible WPF RSS reader.
- [ChatViewer](https://github.com/kellylford/ChatViewer), a GitHub Copilot Chat viewer.

Thank you, Kelly, for work that consistently puts screen-reader users first.

---

## Dynamic Keyboard Reference

The keyboard reference is no longer a static document. It is generated live from the active command registry and your current feature profile.

The reference now:

- Reflects your actual setup. If you rebind a key or switch to a different keyboard pack, the exported HTML reference updates to show exactly what is bound.
- Documents QUILL's layered keyboard model, including QUILL key prefix chords and dedicated browse-mode, also called Quick Nav, shortcuts.
- Exports as clean semantic HTML designed for high-performance screen-reader review.

---

## Smaller additions worth knowing

QUILL 0.6.0 also includes these practical additions:

- From the QUILL key, press **F** to speak the window title, **P** to speak the full file path, or **Q** to speak a short status summary without leaving the editor.
- **Ctrl+Tab** switches to the next document, and **Ctrl+Shift+Tab** switches back.
- Open and Save As now start in your Documents folder.
- You can set your own default startup folder in Preferences, so QUILL no longer drops you into the install directory.
- `--goto FILE:LINE:COL` opens a file at a specific position from one argument, which is useful when a linter or search result provides a `file:line:column` string.
- `--diff LEFT RIGHT` opens two files directly into Compare Mode.
- **Help -> Report a Bug...** now opens focused on the Summary field, remembers your name and email after the first entry, and asks which screen reader you use. QUILL preselects the screen reader it detects so the team can reproduce reader-specific issues.
- Feature search now finds copy tray, macros, and abbreviations.
- The Open dialog includes more file types, including common developer extensions such as Kotlin, TypeScript, Go, Rust, and more.
- HEIC and HEIF images are now supported for AI image description.
- The About screen now credits every GitHub contributor, including new project owner Kelly Ford and design contributor Ken Perry.

---

## Fixes that change the day-to-day

This release fixes a group of problems that directly affected accessibility, startup reliability, image description, reporting, and platform setup.

### Report a Bug accepts typing and no longer freezes QUILL

Under NVDA, the bug-report fields were refusing keyboard input. The dialog has been rebuilt so every field is editable. It also moved to the Help menu, where users expect support-related commands.

Submitting a report no longer freezes the app while contacting the server. That work now happens in the background with a timeout. The impact is simple: reporting a problem is no longer itself a problem.

### JAWS focus is quieter

JAWS no longer says stray phrases such as `splitter window` and `panel` when menus close or the app receives focus. The invisible layout container is no longer exposed to the screen reader, so focus changes are cleaner and quieter.

### Describe Image with AI works again

A small internal error was silently stopping **Describe Image with AI** from running. The feature now completes as intended, restoring an accessibility feature blind users rely on.

### Startup is faster and quieter

Screen-reader detection now runs in the background instead of stalling the first window. A preview warm-up crash is fixed. The title bar no longer flashes `untitled Quill unavailable` before the app is ready. The preview pane no longer hangs for minutes with no way to close it.

### First run is more reliable

The first window now comes to the foreground so the trust and privacy dialog is reachable. If you skipped the personalization wizard, you can re-open it later. The wizard's startup beep and Cancel-button focus are fixed.

### Personalize Quill wizard is cleaner

Two setup wizard issues are fixed:

- The **Play sounds for mode changes** checkbox on step 2 now reads with its label instead of as an unlabeled control.
- The profile choices on step 3 now wrap when you arrow past the last one instead of dumping focus onto the Back and Next buttons.

### User guide opens safely

The user guide now opens as a read-only page in your browser instead of as an editable Markdown document you could accidentally change. A stray edit can no longer trigger a `0x8007139f` browser error. A glossary of QUILL terms has also been added to the guide.

### Upgrade prompt for the Braille Pack

The QUILL Braille Pack, which provides braille translation, BRF and BRL export, and liblouis integration, is an optional installer component. Some 0.5.0 users may miss it during upgrade.

On first launch of 0.6.0, QUILL now detects when the pack is absent and offers to run the installer again so you can add it without re-downloading. It uses the copy already in your updates folder. Choose **Not Now** and the prompt goes away permanently. You can still add the pack later by re-running the installer and checking the Braille Pack component.

### Skipped-update notifications work again

If you previously used **Skip this update**, Notification Center was silently reporting `no newer version` instead of reminding you that a skipped update was still waiting. That is fixed.

### macOS keeps API keys correctly

Saving an Ask Quill API key on macOS used to crash. Keys and tokens are now stored in the login Keychain, so you set them up once and on-device or cloud AI continues to work.

### macOS builds install cleanly

The notarized macOS build now signs its bundled image libraries and uses hardened-runtime entitlements, so the app installs without security warnings.

---

## What works differently now

Most habits carry forward, but a few things moved or changed.

### Braille commands moved under Tools

The top-level **Braille** menu is gone. All braille commands now live under **Tools -> Braille**, including status, navigation, page tools, and translation. The commands are still present; they simply live alongside the other authoring tools.

### Translation menu is dynamic

The old flat list of UEB items has been replaced with a structured menu:

- **UEB**.
- **Standard American English (Legacy)**.
- **More Languages**, built from the installed pack's profiles.

If you used to reach a translation item by position, check the new structure the first time you open it.

### No Install Braille Pack item in the menu

The Braille menu no longer includes **Install Braille Pack**. The pack is now selected during the QUILL installer. Check the Braille Pack component in the installer if you want translation. Once installed, the Translation submenu appears automatically.

### Report a Bug moved near Check for Updates

**Report a Bug** now sits immediately before **Check for Updates** in the Help menu, matching where most people look for support and maintenance items.

### Two entity commands now have two different jobs

The older **Encode HTML Entities** command still escapes only the five markup characters: `<`, `>`, `&`, `"`, and `'`.

The new **Convert Non-ASCII to HTML Entities** command handles accents and symbols. If you previously reached for the old command expecting it to fix accented text for Pandoc, use the new command instead.

### Insert Date and Time is now a submenu

The old flat **Date and Time** and **Calculated Date...** items have been replaced by one **Insert -> Date and Time** submenu.

That submenu includes:

- Insert Date.
- Insert Time.
- Insert Date and Time.

The bundled `com.quill.bundled.insert-tools` Quillin owns this submenu. It is now the canonical home for date and time snippets and is the model for migrating other built-in conveniences into Quillins.

### Sound remains opt-in

Most earcons are off until you choose a sound pack and enable events. Existing setups should not get noisier on upgrade. Turn sound on from **Preferences -> Sound** and **Tools -> Reading & Dictation -> Sound Events...**.

### Indentation tones default to Off

Indentation tones do not play until you pick a scale. Code files remain silent unless you ask QUILL for tone feedback.

## Closing summary

QUILL 0.6.0 is more than a feature release. It is a statement about what an accessible editor can be when screen-reader users are treated as the primary audience, not an afterthought.

This release brings practical power to everyday writing through Insert Automation, typed abbreviations, smart triggers, log mode, citations, Word and RTF export, and better encoding tools. It brings confidence to specialized work through Braille Mode, the optional QUILL Braille Pack, professional translation workflows, page-aware BRF navigation, and status information that speaks the way braille readers actually work. It brings speed to review and development through compare mode, code-aware navigation, indentation tones, dynamic keyboard documentation, and command-line launch options for precise workflows.

Underneath those visible improvements, the new Quillin platform gives QUILL a foundation for growth: accessible preferences, document lifecycle events, status bar contributions, settings search, dependency checks, network safeguards, developer logging, bundled reference Quillins, and strict user control over what extensions can do.

Just as important, 0.6.0 fixes the kinds of issues that matter deeply in daily use: bug reporting now accepts typing, JAWS announcements are quieter, Describe Image works again, startup is faster, first-run dialogs are reachable, the user guide opens safely, update notifications are more reliable, and macOS builds install and store keys correctly.

The result is a release that feels faster, quieter, more predictable, and more empowering. QUILL 0.6.0 gives writers, braille users, developers, students, accessibility professionals, and screen-reader users of every kind a stronger place to work — one built around keyboard control, spoken feedback, user choice, and the belief that accessible software can also be powerful, elegant, and joyful to use.
