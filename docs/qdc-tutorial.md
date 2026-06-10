# QUILL Developer Console Tutorial

Status: **Planned for QUILL 1.1** — not yet implemented.
This tutorial documents the intended interface described in the QDC PRD
(`docs/QUILL Developer Console and Automation.md`). Use it as the authoritative
reference when building or testing the QDC.

---

## What the QDC is

The QUILL Developer Console (QDC) is an embedded scripting surface for
developers, power users, and accessibility professionals. It lets you inspect
and automate the running editor without rebuilding or adding temporary menu
items.

The QDC is not for ordinary users. It is profile-gated and off by default for
Essential, Writer, and Reader profiles. It appears as a first-class feature for
Developer and Power Text profiles.

There are two consoles:

- **Python console** — runs in-process. Full access to the scripting API via `q`.
  Prompt: `>>>` (continuation `...`).
- **TypeScript console** — runs through a Node subprocess bridge. Async API via
  `quill`. Prompt: `ts>` (async pending `ts*>`).

Both are read through the same transcript window and announced through QUILL's
standard accessibility announcement path.

---

## Opening the console

Menu: `Tools > Authoring and Automation > Developer Console > Open Python Console`
or `Open TypeScript Console`.

Command palette: `quill.console.openPython` / `quill.console.openTypeScript`.

The console opens as a separate dialog. Press `Esc` to return focus to the
editor. The dialog stays open and preserves its namespace until you explicitly
close it.

---

## Console layout

The console has five areas, navigable with `F6`:

1. **Transcript** — read-only. Shows prompts, output, errors, and return values.
2. **Input** — single-line by default; `Shift+Enter` adds a newline for multi-line
   blocks.
3. **Language selector** — switch between Python and TypeScript.
4. **Status line** — current language, prompt state, active document, worker status.
5. **Buttons** — Run, Clear, Copy transcript, Save transcript, Insert snippet, Help, Close.

---

## Keyboard reference

| Key | Action |
| --- | --- |
| Enter | Execute current command |
| Shift+Enter | Insert newline (multi-line input) |
| Ctrl+Enter | Force execute multi-line block |
| Up / Down | Previous / next history (when cursor is at line boundary) |
| Ctrl+L | Clear transcript |
| Ctrl+Shift+C | Copy transcript |
| Ctrl+S | Save transcript |
| Ctrl+F | Find in transcript |
| F6 | Move between transcript, input, status, and buttons |
| Esc | Return focus to editor |
| F1 | Console help |
| Ctrl+Space | Trigger completion |

---

## Python console

### Available names

The following names are in scope when the console opens:

| Name | What it is |
| --- | --- |
| `q` | Primary QUILL scripting API — start here |
| `app` | Application-level read-mostly object |
| `commands` | Command registry facade |
| `doc` | Active document snapshot |
| `editor` | Active editor snapshot |
| `sel` | Current selection snapshot |
| `caret` | Current caret snapshot |
| `profile` | Active feature profile snapshot |
| `settings` | Safe settings facade |
| `diagnostics` | Diagnostics facade |
| `a11y` | Announcement / testing facade |
| `log` | Console-safe logger |
| `wx` | wx module (Developer profile only) |

`doc`, `sel`, and `caret` are read-only snapshots of state at the time they were
captured. They do not update automatically. Call `q.refresh_context()` to pull
current state, or they update automatically when the active document changes.

### Basic operations

Insert text at the cursor:

```python
>>> q.insert_text("Hello from QUILL.")
```

Replace the current selection:

```python
>>> q.replace_selection("Replacement text")
```

Jump to a line:

```python
>>> q.goto_line(42)
```

Run a built-in command by ID:

```python
>>> q.run_command("quill.document.wordCount")
```

Send a screen-reader announcement:

```python
>>> q.a11y.announce("Test announcement.")
```

### Inspecting state

Read the active document name:

```python
>>> doc.name
'notes.txt'
```

Read the current selection:

```python
>>> sel.text
'selected words here'
```

Read the caret position (1-based line and column):

```python
>>> caret.line, caret.column
(12, 5)
```

Search for commands by keyword:

```python
>>> commands.search("spell")
['quill.spell.check', 'quill.spell.addWord', 'quill.spell.nextError']
```

Get a diagnostic summary (useful for support tickets):

```python
>>> q.support.diagnostic_summary()
```

### Accessibility diagnostics

Read the last screen-reader announcements:

```python
>>> q.a11y.last_announcements()
['Title Case applied', '5 words selected']
```

Describe the currently focused region:

```python
>>> q.focus.describe()
'Editor: notes.txt, line 12, col 5, no selection'
```

### Multi-line blocks

Use `Shift+Enter` to add newlines, then `Enter` or `Ctrl+Enter` to execute:

```python
>>> def count_words(text):
...     return len(text.split())
...
>>> count_words(doc.text)
487
```

### Macro recording

Record a sequence of commands as a reusable macro:

```python
>>> q.begin_macro("Clean OCR text")
>>> q.run_command("quill.text.normalizeUnicode")
>>> q.run_command("quill.text.dehyphenateLines")
>>> q.run_command("quill.text.reflowParagraphs")
>>> q.end_macro()
Macro saved: "Clean OCR text"
```

---

## TypeScript console

The TypeScript console requires Node.js on PATH. If Node.js is not found, QUILL
announces the requirement and offers installation assistance.

### TypeScript prompt behavior

```text
ts> await quill.insertText("Hello.");
ts*>
Result: undefined
```

`ts>` is the ready prompt. `ts*>` means an async operation is in flight. Results
and errors appear in the transcript automatically.

### Available globals

| Global | What it is |
| --- | --- |
| `quill` | Async QUILL scripting proxy |
| `console` | Captured: `.log()`, `.warn()`, `.error()` appear in transcript |
| `setTimeout` / `clearTimeout` | Standard timer |
| `AbortController` | For cancellable operations |

### Basic operations

Insert text:

```ts
ts> await quill.insertText("Hello from TypeScript.");
```

Replace selection:

```ts
ts> await quill.replaceSelection("Replacement text");
```

Jump to a line:

```ts
ts> await quill.gotoLine(42);
```

Run a built-in command:

```ts
ts> await quill.runCommand("quill.markdown.normalizeHeadings");
```

### Inspecting state

```ts
ts> const doc = await quill.activeDocument();
ts> console.log(doc.name);
notes.txt
```

```ts
ts> const stats = await quill.documentStats();
ts> console.log(`${stats.words} words, ${stats.lines} lines`);
487 words, 38 lines
```

### Multi-line TypeScript

Use `Shift+Enter` to enter a multi-line block, `Ctrl+Enter` to execute:

```ts
ts> const text = await quill.getText();
ts> const words = text.trim().split(/\s+/).filter(Boolean);
ts> await quill.announce(`${words.length} words`);
```

### TypeScript type definitions

QUILL ships `quill-console.d.ts`. If you have Node.js and an IDE, copy it into
your project to get completion:

```ts
// quill is typed as:
interface QuillConsoleApi {
  insertText(text: string): Promise<void>;
  replaceSelection(text: string): Promise<void>;
  gotoLine(line: number): Promise<void>;
  runCommand(commandId: string, args?: Record<string, unknown>): Promise<unknown>;
  activeDocument(): Promise<QuillDocumentSnapshot>;
  documentStats(): Promise<QuillDocumentStats>;
  announce(text: string): Promise<void>;
}
```

---

## Screen-reader notes

- New output in the transcript is announced without stealing focus.
- Errors are announced with the prefix "Error".
- Return values are announced with the prefix "Result".
- Long output is summarized in the announcement; review the transcript with your
  screen reader for the full text.
- `Ctrl+Shift+C` copies the transcript at any time.
- The console uses QUILL's central Prism announcement path — the same one used
  by all other QUILL announcements.
- No custom-drawn controls are used.

---

## Console safety settings

`Tools > Authoring and Automation > Developer Console > Console Safety Settings`
or command `quill.console.openSafetySettings`.

Settings:

| Setting | Default | Notes |
| --- | --- | --- |
| Python console enabled | Profile-dependent | Off for Essential / Writer |
| TypeScript console enabled | Profile-dependent | Off except Developer profile |
| Require developer profile | On | Prevents accidental access in Writer profiles |
| Max execution time (Python) | 30 s | Hard kill after timeout |
| Max execution time (TypeScript) | 30 s | Worker restart after timeout |
| Allow `wx` module access | Developer profile only | Not available in any other profile |
| Remote console | Locked off | Not available in QUILL 1.x |

---

## Transcript commands

| Command | What it does |
| --- | --- |
| `quill.console.copyTranscript` | Copy entire transcript to clipboard |
| `quill.console.saveTranscript` | Save transcript to a file |
| `quill.console.clear` | Clear the transcript |
| `quill.console.saveInputAsSnippet` | Save the current input as a named snippet |
| `quill.console.insertSnippet` | Insert a saved snippet into input |
| `quill.console.runSelection` | Run selected text in the transcript as a command |
| `quill.console.runCurrentDocument` | Run the active QUILL document as a script |
| `quill.console.showContext` | Print current snapshot values to transcript |
| `quill.console.resetNamespace` | Reset the Python namespace (clears all variables) |
| `quill.console.restartTypeScriptWorker` | Kill and restart the Node worker |

---

## For Quillin authors: testing your extension in the QDC

The QDC is a useful live test surface for Quillin development. Open the Python
console while your Quillin is loaded and explore its manifest and command
registry entry:

```python
>>> from quill.core.quillins.loader import get_loader
>>> loader = get_loader()
>>> ext = loader.get_extension("com.example.myextension")
>>> ext.manifest
ExtensionManifest(id='com.example.myextension', runtime='python', ...)
>>> ext.manifest.contributes.commands
(ExtensionCommand(id='ext.myext.run', title='My Command', ...),)
```

Invoke a command directly through the command registry:

```python
>>> q.run_command("ext.myext.run")
```

Inspect what a command announced:

```python
>>> q.a11y.last_announcements()
['My command completed: 3 items processed']
```

For Node.js Quillins, the TypeScript console is the natural test surface:

```ts
ts> await quill.runCommand("ext.myext.nodeHandler");
ts> // Check the last announcement
ts> const ann = await quill.lastAnnouncement();
ts> console.log(ann);
```

---

## Implementation status

The QDC is planned for QUILL 1.1. The Node.js subprocess bridge described
in the TypeScript console section builds on the same `external_engine.py`
transport and `node_quillin_runner.py` introduced in issue #158.

The Python console (`quill/devtools/python_console.py`) and the TypeScript
worker bridge (`quill/devtools/ts_console_bridge.py`) are not yet written.

The scripting API object `q` is not yet implemented. The `QuillScriptingApi`
class described in the PRD (§10) is the planned implementation target.

When the QDC ships, the Implementation Status map in `docs/scripting.md §0a`
will be updated with the new module entries.
