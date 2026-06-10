# Editors.md — Competitive Analysis and Design Synthesis for QUILL

> Author: this document. Date: 2026-06-01. Scope: a working competitive
> analysis of QUILL against leading general-purpose, programmer, and
> prose editors; a feature matrix; an honest gap analysis with industry
> expectations; a recommended menu consolidation; a Ulysses/Obsidian/Scrivener-
> inspired redesign of Workspaces and the Document Navigator that is
> unmistakably QUILL in spirit; and a long list of "make it amazing"
> proposals. Every recommendation is written for a screen-reader-first
> Windows desktop app whose north star is the QUILL key, Quick Nav, and
> the dialog contract.

---

## 1. Executive summary

QUILL is already a strikingly opinionated editor: stock controls in the
writing path, a screen-reader-first design, the QUILL key chord, Quick
Nav across 13 element types, a deep command palette, Workspace
Snapshots, headings organizer, compare documents, macros, an AI menu
gated by consent, GLOW accessibility, BITS Whisperer dictation, a rich
Quillins extension model, and a stability/safety surface that
mainstream editors rarely equal. Compared to the editor market it sits
somewhere between a programmer's text tool and a pro writing tool —
and that hybrid is exactly its edge.

The competitive analysis shows three things:

1. QUILL's *interactive navigation* and *accessibility-grade confirmations*
   are industry-leading. No mainstream editor matches its 13-element
   Quick Nav, its structured selection primitives, or its dialog
   contract enforcement.
2. QUILL's *document and project organization* (the Workspace concept,
   Document Navigator, multi-document sessions) is functional but
   under-developed compared with Ulysses's library, Obsidian's vault
   and graph, Scrivener's corkboard, and Org-mode's hierarchy and
   agenda.
3. QUILL's *menu* has grown organically and now approaches the depth
   of a kitchen sink. The good news is the architecture supports a
   much cleaner organization. The bad news is that the current Tools
   menu reaches three levels in places and a few entries are mis-homed.

The rest of this document lays out the matrix, the gap list, the
proposed menu consolidation, the Workspaces + Document Navigator
redesign, and a long creative list of "make it amazing" ideas tailored
to QUILL's voice.

---

## 2. Feature matrix

Legend: ✅ first-class, ◑ partial, ○ not present, — N/A. The
"industry expectation" column is the user-facing behavior a sighted,
keyboard-only, or screen-reader user would expect to find without
explanation. The "QUILL today" column is observed from the codebase
and user guide as of 2026-06-01.

| Capability                                          | Industry expectation                                                                                          | QUILL today                              | Status |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ------ |
| Undo / redo with persistence                        | Multi-level undo; survives crash                                                                              | Multi-level undo; persistent undo toggle | ✅     |
| Find / replace (text)                               | Modal find bar; next/prev; replace; selection scope                                                            | In-document Find bar, replace, next/prev | ✅     |
| Regex find / replace                                | Toggle for regex; group preview                                                                               | Regex supported; named-group preview planned | ◑ |
| Find in files                                       | Cross-file search with results list                                                                           | Search menu (search_in_files, replace_in_files) | ✅ |
| Bookmarks (named, persistent)                       | Set / go to / list; per-document                                                                              | `navigate.set_bookmark`, `go_to_bookmark`, `list_bookmarks` | ✅ |
| Temporary marks / "point and mark"                  | Push/pop ring; exchange point/mark; list marks                                                                | `edit.set_mark`, `pop_mark`, `exchange_point_mark`, `list_marks` | ✅ |
| Line / paragraph / block selection                  | Three distinct selection units; announce which                                                                 | `select_line`, `select_paragraph`, `select_block` | ✅ |
| Structural navigation                               | Next/prev heading, block, structure; match bracket; region                                                    | `navigate.next_heading`, `next_block`, `next_structure`, `match_bracket`, `next_region` | ✅ |
| Outline / structure panel                           | Dockable tree with preview and jump; per-markup-kind                                                           | `open_outline_navigator`, `_show_tree_navigator` (modal); also a YAML navigator | ◑ |
| Quick Nav (jump to anything)                        | Single keystroke to a categorised index with type-ahead                                                        | `open_quick_nav` (NAV-1/NAV-4) with 13 element types | ✅ |
| Command palette                                     | Fuzzy find over all commands with scope and recent                                                             | `_id_palette`, palette.py                 | ✅     |
| Project / "workspace" concept                       | Named, restorable collection of open documents, settings, and UI state                                          | "Workspace Snapshots" submenu in File (`_sessions_menu`) and `_refresh_sessions_menu`; `core/sessions.py` | ◑ |
| Library / sheet / vault                             | Persistent on-disk collection of many items with grouping, filters, and search                                 | OO position partially filled by Workspace Snapshots | ○ |
| Multi-cursor / multi-selection                      | Multiple carets, column selection, box select                                                                 | Not in core; `extend_selection_mode` toggle | ○ |
| Snippets / text expansion                           | Trigger, tab stops, placeholders, scope                                                                        | `core/snippets.py` (11 KB), `format.insert_snippet`, `format.manage_snippets` | ✅ |
| Snippet variables (date, filename, cursor)          | Tokens at expansion time                                                                                      | Supported (see Snippet format)           | ✅     |
| Command-based snippet system                        | JScript / Lua / Python actions inside snippets                                                                | Python sandbox in core; no in-snippet scripting in user guide | ◑ |
| Spell check                                         | As-you-type; dialog; dictionary management                                                                    | Three-tier spell-check; status / dialog; dictionary status | ✅ |
| Thesaurus                                           | Synonym lookup, inline replace                                                                                | `tools.thesaurus` (background pre-load planned) | ◑ |
| Grammar / style lint                                | Rules engine, inline annotations                                                                              | GLOW audit + fix, selection-level       | ✅     |
| Word count / reading time                           | Document, selection, periodic                                                                                 | `tools.word_count`                       | ✅     |
| Auto-save / recovery                                | Periodic save; recovery on crash with preview                                                                  | `core/autosave.py`; recovery snapshot dialog with 30-line preview | ✅ |
| Backups                                                                     | Local copies of prior versions                                                                                | `core/backups.py`; restore from backup   | ✅     |
| Compare documents                                                              | Side-by-side or unified diff; navigate; announce                                                              | `compare_menu` (Compare Documents) with announce, summary, copy, sync toggle | ✅ |
| Macros                                                                       | Record / play / save; named                                                                                   | `core/macros`; macro menu with start/stop/play/manage | ✅ |
| TTS / read aloud                                                             | Start/pause/stop; voice pick; speed; export audio                                                              | `core/read_aloud.py` (~46 KB), full menu | ✅ |
| Dictation                                                                    | Toggle; voice commands; offline model                                                                          | BITS Whisperer (deferred to 2.0 as a top-level menu; 1.0 ships dictation under Watch/Dictation submenu) | ◑ |
| OCR                                                                          | Image, clipboard, screen; image description                                                                     | `tools.ocr_image`, `tools.ocr_clipboard`, `tools.ocr_screen`, `tools.describe_image` | ✅ |
| OCR result post-processing (cleanup recipes)                                 | One-key cleanup of OCR output                                                                                  | "Clean exports" profile mentioned in roadmap; not surfaced in menu | ◑ |
| On-device / private AI                                                       | Opt-in; explicit consent; no silent network                                                                     | AI menu gated; `core.bw_whisperer` provider model; consent flow | ✅ |
| Cloud AI (ChatGPT, Claude, local endpoints)                                 | Model picker; API key; forget key                                                                              | `AI Model and Connection...`; `Forget API Key`; status badge | ✅ |
| AI rewrite / summarize / continue / fix grammar                              | In-editor actions                                                                                              | `ai_rewrite_selection`, `ai_summarize_selection`, `ai_continue_writing`, `ai_fix_grammar` | ✅ |
| AI prompt studio / agent center                                              | Custom prompts; agent tools                                                                                    | `ai_prompt_studio`, `ai_agent_center`, `ai_hub` | ✅ |
| Conversational AI side panel                                                 | Chat docked to the side, share selection                                                                       | `ask_quill_chat`, `ai_assistant` (windowed) | ◑ |
| Image description / alt-text helper                                          | Generate alt-text for embedded images                                                                          | `tools.describe_image`; accessibility tune-up agent | ✅ |
| Accessibility audit                                                          | Periodic; spoken report                                                                                        | `tools.accessibility_audit`              | ✅     |
| Keyboard trap / tab-order snapshot                                           | Diagnose focus traps                                                                                            | `tools.keyboard_trap_snapshot`           | ✅     |
| Contrast validation                                                          | Check palette against WCAG                                                                                     | `tools.validate_contrast`                | ✅     |
| Sticky notes                                                                  | Quick capture; searchable vault                                                                                | Sticky Notes submenu (sticky_notes, new sticky note) | ✅ |
| Watch folder                                                                  | One folder, one action                                                                                          | Watch Folder Profiles (`watch_folder_settings`, `watch_folder_status`, `watch_folder_toggle`) — single profile set | ◑ |
| Pandoc integration                                                            | Convert between formats                                                                                         | `tools.pandoc_wizard`                    | ✅     |
| External tools / format support                                              | Allowlist of executables                                                                                        | `tools.external_tools`                   | ✅     |
| SSH / remote file open                                                        | Quick connect; site manager                                                                                    | `Open over SSH` submenu (Quick Connect, Site Manager) | ✅ |
| File format readers/writers                                                   | Markdown, HTML, RTF, EPUB, DOCX, PDF, JSON, CSV, YAML, plain text                                             | `quill/io/structured.py` and per-format modules | ✅ |
| EPUB reader / navigator                                                       | Open and jump inside EPUB                                                                                       | `open_epub_navigator`                    | ✅     |
| YAML structure editor                                                         | Visual tree edit for YAML documents                                                                            | `open_yaml_structure_editor`             | ✅     |
| Heading organizer                                                             | Validate and reshape heading sequence                                                                          | `open_heading_organizer`                 | ✅     |
| Customizable menus / keymap                                                   | Editor for menu and keymap                                                                                     | `app.menu_editor`, `keymap_editor`; `core/menu_customization.py` (12 KB) | ✅ |
| Profiles (Essential, Writer, Developer, A11y Pro, Full)                      | Switch whole profile; health check                                                                              | Feature profiles + `switch_feature_profile`; `feature_profile_health_check` | ✅ |
| Feature flag manager                                                          | Per-feature toggle                                                                                              | `individual_feature_toggles`             | ✅     |
| Custom profiles / Quick Profiles                                              | User-saved bundles of settings                                                                                  | `core/custom_profiles.py`                | ✅     |
| Status bar layout customization                                               | Pick cells, persist                                                                                            | `status_bar_settings`                    | ✅     |
| Plug-in / extension model                                                     | Manifest, sandbox, signing                                                                                     | Quillins manifest validated; `quillins_bundled/` examples | ◑ |
| Export and back up / import                                                   | One-key share                                                                                                   | `share_export`, `share_import`           | ✅     |
| Export presets (EPUB, PDF, DOCX, HTML)                                        | Pick target and options                                                                                         | Pandoc wizard; export presets partial    | ◑ |
| Print                                                                          | Page setup, print preview                                                                                      | `file.page_setup`, `file.print`          | ✅     |
| Auto-format / smart punctuation                                              | Smart quotes, dashes, ellipses                                                                                  | Core autoformat; smart quotes not surfaced as toggle | ◑ |
| Word prediction                                                                | Inline completion                                                                                              | `edit.word_prediction`                   | ✅     |
| Intellisense as you type                                                       | Lightweight, scoped to language                                                                                | `core/intellisense.py`                   | ◑ |
| Markdown / HTML / rich-text preview                                           | Side by side or focused                                                                                        | `view.preview`, `view.split_preview`, `view.focus_preview`, `view.browser_preview` | ✅ |
| Distraction / focus mode                                                      | Hide chrome, center text, silence chatter                                                                       | "Focus Preview" is the closest; no full-screen "Focal" mode | ◑ |
| Reading ruler / line focus                                                    | Highlight current line/paragraph                                                                                | Not surfaced; high-contrast settings only | ◑ |
| Inline definitions / word lookup                                              | Single key for dictionary + thesaurus                                                                            | Thesaurus dialog; no inline look-up      | ◑ |
| Document health dashboard                                                    | One pane for accessibility + lint + link inventory                                                              | Accessibility audit; link inventory; contrast; not unified | ◑ |
| External file change watch                                                    | Detect edits; reload safely                                                                                    | `core/external_change.py`                | ✅     |
| Code folding                                                                  | Collapse / expand                                                                                              | Not surfaced                              | ○     |
| Multi-pane editor (split, grid)                                              | Horizontal/vertical split, save layout                                                                          | "Preview Side by Side" exists; no true multi-pane text editor split | ◑ |
| Tab / tile open documents                                                     | One tab per document                                                                                            | `show_tab_control` toggle in View        | ✅     |
| Status bar: line, col, selection length                                      | Always present                                                                                                  | Status bar with cells (status_bar_settings to choose) | ✅ |
| Recent files / recent folders                                                 | MRU list                                                                                                        | `Open Recent` submenu                    | ✅     |
| Recent sessions / restore last session                                        | Auto-restore on launch                                                                                          | "Workspace Snapshots" submenu in File; auto-restore on launch | ✅ |
| Auto-update                                                                    | Notify; one-key update                                                                                          | `check_updates`; auto-check toggle in Settings | ✅ |
| Crash reporting                                                                | Opt-in bundle                                                                                                  | `save_diagnostics`; `report_bug`        | ✅     |
| Localization                                                                   | Multi-language UI                                                                                              | Translation contributor plan in place    | ◑     |
| High-contrast / dark mode                                                     | System-aware                                                                                                    | `toggle_dark_mode`; `validate_contrast`; high-contrast respected | ✅ |
| Math / equation editor                                                        | LaTeX-style inline and block                                                                                    | Not surfaced                              | ○     |
| Bibliographies / citations                                                    | Reference list management                                                                                       | Not surfaced                              | ○     |
| Co-located todos / checkboxes                                                 | Task list with states                                                                                          | Task list insertion (`insert_task_list`); List Manager | ✅ |
| Bidirectional links / backlinks                                               | Wiki-style [[link]] with back-link pane                                                                          | Follow link exists; no backlink pane    | ○     |
| Graph / canvas view                                                            | Visual map of document relationships                                                                            | Not in QUILL                              | ○     |
| Corkboard / index-card view                                                   | One card per document or section                                                                                | Not in QUILL                              | ○     |
| Outline view (dock)                                                            | Persistent tree side panel                                                                                      | Outline Navigator is a modal; no docked tree | ◑ |
| Document statistics / progress goals                                          | Word target, time, deadline                                                                                      | `word_count` shows numbers; no goal/target surface | ◑ |
| Daily / word-count goal                                                       | "500 words today"                                                                                                | Not surfaced                              | ○     |
| Notes within notes (block / sub-document)                                     | Transclusion, block reference                                                                                  | `navigate.next_structure` covers Markdown structures; not block-level | ◑ |
| Tags / keywords                                                                | First-class tag system                                                                                          | List Manager supports tags via markup; no first-class tag system | ◑ |
| Saved searches / smart folders                                                | Dynamic filters                                                                                                  | Not in QUILL                              | ○     |
| Full-text search with snippets                                                | Highlight matches with context                                                                                  | `search_in_files` exists; in-document Find Next/Prev is built-in | ✅ |
| Word / line wrap / soft wrap toggle                                           | Always present                                                                                                  | `view.toggle_soft_wrap`                  | ✅     |
| Indent settings (tabs vs spaces, width)                                       | Per-document                                                                                                   | `format.indent`, `format.outdent`; `convert_indentation_to_*` | ✅ |
| Auto-close brackets / quotes                                                  | Optional                                                                                                       | Not surfaced                              | ○     |
| Bracket matching highlight                                                    | On cursor move                                                                                                  | `navigate.match_bracket`                 | ✅     |
| Column / ruler / margin guides                                                | Visual aids                                                                                                    | Not surfaced                              | ○     |
| Drag-and-drop reordering of lines / blocks                                    | Mouse only or keyboard?                                                                                         | Move Line Up/Down; no block drag         | ◑     |
| Sort / unique / shuffle lines                                                 | Built-in                                                                                                        | Sort, Reverse, Remove Duplicates, Trim, Normalize, Indent conversions all in `Format > Transform Lines` | ✅ |
| Column / rectangular selection                                               | Multi-line, multi-character                                                                                     | Not in core                              | ○     |
| Line numbers (gutter)                                                         | Optional                                                                                                        | Not surfaced                              | ○     |
| Whitespace / EOL visualization                                                | Optional                                                                                                        | Not surfaced                              | ○     |
| Project templates                                                              | New from template                                                                                              | Power Tools file-create group likely contains templates; verify | ◑ |
| Project search and replace                                                    | Cross-file regex                                                                                                | `tools.replace_in_files`                 | ✅     |

The takeaway: QUILL is in the top tier for navigation, accessibility,
AI integration (gated), writing-quality tooling, and document safety.
Its *project organization* layer (workspaces, library, multi-document
graph, smart folders, goals) is functional but under-developed
relative to dedicated writing apps.

---

## 3. Where QUILL aligns with industry

These are the strengths that match or exceed editor expectations, and
the rough proof points inside the codebase.

1. **Stock controls in the writing path.** Per
   `accessible-dialogs.instructions.md`, every input is `wx.TextCtrl` or
   `wx.ListBox`. No custom-drawn editor surface, which means
   screen readers see the same role and name everywhere.
2. **Three-tier spell check** with enchant, wordlist, and stub. Background
   pre-load is on the roadmap (PERF-1) and the menu surfaces every
   level: Spell Check dialog, Previous/Next Misspelling, Misspelling
   List, Dictionary Status, Add to Document Dictionary, Ignore for
   Session.
3. **Structured selection primitives.** Select Line / Paragraph / Block
   are separate commands, not a single ambiguous "extend selection"
   that other editors make the user discover.
4. **Mark ring.** Set / Pop / Exchange / List. Few mainstream editors
   ship a visible mark ring as a first-class menu.
5. **Quick Nav across 13 element types** with a category filter and
   type-ahead. This is VS Code's Command Palette behavior applied to
   document structure, with a count badge.
6. **Heading organizer** validates and rewrites heading sequences for
   accessibility and clean exports. No mainstream editor has this.
7. **Compare Documents** with synchronized navigation, announcement of
   the current difference, a "Difference Summary," and copy
   individual/all differences. Compare in Word is a hidden ribbon
   dialog; in Notepad++ it is a plugin; in VS Code it is an extension
   unless you have Pro. QUILL ships it as a first-class tool.
8. **Workspace Snapshots** that name and restore document sets, caret
   positions, and active document. The naming and saving model is
   Ulysses-like.
9. **Two-stage AI consent.** No silent network; provider, model, scope,
   and confidence are announced.
10. **BITS Whisperer** (deferred to 2.0 as a top-level menu but present
    in 1.0 as a submenu) is genuinely novel for a screen-reader-first
    editor: offline speech-to-text with model management and a queue
    you can monitor without sight.
11. **Watch Folder Profiles** is the rare automation hub that is
    operable with a screen reader; the "many folders, many actions,
    one queue" redesign on the roadmap is a real differentiator.
12. **GLOW (Grammar, Logic, Organization, Writing)** is QUILL's
    accessibility-and-prose-fix engine; the four sub-commands (audit
    document, audit selection, fix document, fix selection) make it
    simple by design.
13. **Quillins extension model** is sandboxed, manifest-validated, and
    ships with a Lint tool (`quill.tools.quillin_lint`). Compared with
    Vimscript or VS Code's open extension marketplace, it is a
    deliberately tight perimeter.

The user-visible principle behind all of this: *every action has a
spoken outcome, every dialog has a default and an escape, every
feature can be turned off*. That is the bar the rest of the editor
market does not consistently meet.

---

## 4. Where QUILL is behind or behaves unexpectedly

These are the gaps the matrix surfaces, with the "industry expects"
framing, the QUILL reality, and an honest callout when current
behavior diverges from what a user would assume.

### 4.1 Project organization is shallow

- **Industry expectation.** Ulysses users live in a "library" with
  groups, filters, and goals. Obsidian users live in a "vault" with
  backlinks, tags, and Bases. Scrivener users live in a "binder" with
  corkboard and outliner. Org-mode users live in a tree with agenda.
- **QUILL today.** Workspace Snapshots save and restore the current
  open-document set. There is no persistent library, no grouping, no
  filters, no per-workspace palette of recent activity. The
  "Recent Files" menu exists but Workspace Snapshots is a sibling
  concept, not a superset.
- **Honest callout.** "Open from Workspace Snapshot" can look like a
  glorified "Reopen Closed Tab" to a new user. The snapshot is
  loadable, but the snapshot UI is not yet a library.

### 4.2 Outline Navigator is a modal, not a dock

- **Industry expectation.** Word, Scrivener, and most writing apps
  ship a persistent outline pane that you can show, hide, and let
  track the cursor. Ulysses shows the editor + sheet list always.
  Obsidian shows the file tree.
- **QUILL today.** `_show_tree_navigator` builds a `wx.Dialog` with a
  splitter (tree + preview), is launched by `open_outline_navigator`
  (and `open_epub_navigator`, `open_yaml_structure_editor`), and is
  destroyed on close. The same pattern is reused for Misspelling
  Navigator, Document Intake, and others.
- **Honest callout.** The dialog is excellent and screen-reader
  friendly, but a power user editing a 200-page manuscript will
  repeatedly open and close the modal. A docked outline tree (toggle
  from View) would match industry behavior without breaking the
  dialog contract.

### 4.3 Multi-cursor / column select is absent

- **Industry expectation.** VS Code, Sublime, JetBrains IDEs, vim,
  Emacs all support multiple carets. Notepad++ supports column /
  block selection. Word supports column select with Alt.
- **QUILL today.** Only an "extend selection mode" toggle exists,
  which extends the next selection motion. No multi-caret, no box
  select.
- **Honest callout.** This is the single largest missing editing
  primitive for users who came from a programmer editor. Add a
  power-tool that toggles column-select on Alt+drag and a
  keyboard command to add a caret above / below.

### 4.4 Word-prediction and intellisense are present but not visible

- **Industry expectation.** Word shows suggestions inline. VS Code
  shows completions on demand and as you type. Notepad++ has an
  autocomplete plugin that does the same.
- **QUILL today.** `edit.word_prediction` opens a dialog. There is no
  as-you-type inline completion surfaced in the menu or the status
  bar. `core/intellisense.py` exists; nothing in the menu says so.
- **Honest callout.** Users will assume the feature is broken. The
  fix is to make it a visible, opt-in "Inline word prediction" toggle
  in the status bar / settings, with announcement on accept.

### 4.5 AI chat is windowed, not docked

- **Industry expectation.** Cursor, VS Code + Copilot, JetBrains AI,
  Notion AI, and Ulysses's "Ask Ulysses" all dock a chat side panel
  that shares selection with the editor.
- **QUILL today.** "Ask Quill Chat..." and "Writing Assistant..."
  open floating windows. The selection is shared only through copy
  and paste.
- **Honest callout.** The chat is functional; it just is not docked,
  and a docked chat panel that owns a left or right dock with the
  outline tree on the other side would be a much more useful default.

### 4.6 Grammar fix is not in the document until asked

- **Industry expectation.** Grammarly underlines; one key accepts.
  GLOW already audits and fixes, but the audit step is explicit.
- **QUILL today.** `glow_audit_document` and `glow_audit_selection`
  must run before `glow_fix_document` and `glow_fix_selection`. The
  fix only changes the document after the user sees the report.
- **Honest callout.** This is a defensible design (transparency), but
  the menu should make it obvious: the "GLOW" submenu already does.
  Keep the contract; add a "GLOW Quick Fix on Selection" that audits
  + fixes + announces the change count in one key.

### 4.7 No "Focus Mode" / "Focal" surface

- **Industry expectation.** Word has Focus Mode. Bear has a
  chrome-less compose. Ulysses has a minimal editor. iA Writer has
  Focus Mode with a sentence highlight. Notepad++ has a "Distraction
  Free" plugin.
- **QUILL today.** The closest is "Focus Preview." That hides the
  editor chrome for the preview, not the editor itself.
- **Honest callout.** "Focus Preview" is misleadingly named. A real
  "Focal Mode" (F11?) that hides status bar, menu bar, sidebar, and
  centers the current paragraph with optional reading ruler and
  sentence highlighting is the correct fit for a screen-reader
  product; it should silence non-essential chatter, keep essential
  confirmations, and be a one-key toggle.

### 4.8 Snippet tab stops / placeholders are not announced

- **Industry expectation.** VS Code, Sublime, JetBrains, vim, and
  TextMate all support tab stops with placeholders; the user is
  walked through each stop with `Tab` and `Shift+Tab`.
- **QUILL today.** Snippets exist and the menu offers Insert and
  Manage; there is no documented "tab stop" walk-through. The snippet
  format may support placeholders (it does in EdSharp and most modern
  editors).
- **Honest callout.** Verify in `core/snippets.py` and document.
  If placeholders are not yet announced, add a `Snippets` tutorial
  to the user guide and make the placeholder name spoken on arrival.

### 4.9 Goto line / page has no "line" speech preview

- **Industry expectation.** A "Go to line" usually shows the line
  content in a preview before the user commits.
- **QUILL today.** `navigate.go_to_line` jumps; no preview.
- **Honest callout.** Add a one-line preview pane in the Go-To-Line
  dialog with the current line's text, the line number, the column,
  and a "Speak Line" button. Trivial to add, big screen-reader win.

### 4.10 No saved searches / no smart folders

- **Industry expectation.** Most pro editors and writing apps
  support saved filters: "All headings containing TODO," "All
  documents opened this week," "All files with more than N
  misspellings."
- **QUILL today.** None. `file_search` exists but is a one-shot
  search.
- **Honest callout.** Add a "Saved Searches" manager and tie it to
  Workspace Snapshots. Saved searches are an under-rated
  accessibility win because they let a screen-reader user ask
  "what's new?" in a single keystroke.

### 4.11 No word-count goal / writing target

- **Industry expectation.** Ulysses has writing goals (words,
  characters, time). Scrivener has project targets. Word has
  word-count target notifications. Bear has a daily streak.
- **QUILL today.** Word count exists; no goal / target surface.
- **Honest callout.** Add a "Writing Goal" dialog and a status-bar
  cell that announces progress. Tying the goal to a Workspace
  Snapshot makes this very Ulysses-like.

### 4.12 Status bar cells are customizable but the UX is hidden

- **Industry expectation.** VS Code and Word expose a clear "Status
  Bar Layout..." picker.
- **QUILL today.** `status_bar_settings` exists. The menu labels it
  clearly. The dialog must be polished.
- **Honest callout.** Verify the dialog (a screen-reader test pass)
  and add an "Add a cell" / "Remove a cell" / "Reorder" flow that
  is fully keyboard-driven.

### 4.13 No reading ruler / line focus for low-vision users

- **Industry expectation.** Word, Pages, macOS, NVDA, and many
  editors support a reading ruler that follows the caret.
- **QUILL today.** Not surfaced.
- **Honest callout.** Add a "Reading Ruler" toggle and a "Line
  Focus" toggle under View, behind a feature flag, with high-contrast
  aware theming.

### 4.14 Smart quotes / auto-format not surfaced

- **Industry expectation.** Word, Pages, Ulysses, Bear all convert
  straight quotes to typographic quotes as you type.
- **QUILL today.** `core/autoformat.py` exists; not on by default,
  not visible in the menu.
- **Honest callout.** Surface as a setting ("Auto-format as you
  type") with sub-toggles for quotes, dashes, ellipses. Announce the
  substitution so a screen-reader user knows the character changed.

### 4.15 No image embed flow (other than OCR)

- **Industry expectation.** Markdown editors let you paste / drop an
  image. Ulysses, Bear, iA Writer all do.
- **QUILL today.** OCR Image and Describe Image are present. Image
  insertion is not. Markdown reference links work.
- **Honest callout.** Add "Insert Image from File..." and "Insert
  Image from Clipboard" under Insert. The accessibility win is that
  the dialog should immediately offer a "Describe Image..." button
  that uses Describe Image, so the alt text and the embed happen
  together.

### 4.16 Inline spelling suggestions are not visible in the menu

- **Industry expectation.** Word, Pages, macOS show a context menu
  with "Replace with..." suggestions.
- **QUILL today.** Misspelling List exists; no inline context menu
  for replacements.
- **Honest callout.** Add a context menu for misspelled words
  offering the top three suggestions + "Add to Dictionary" + "Ignore
  for Session." Already possible with the wx context menu; surface
  the wired action in the menu so it is discoverable.

### 4.17 No "duplicate selection" as a structural copy

- **Industry expectation.** Several editors have "Duplicate Line"
  and "Duplicate Selection."
- **QUILL today.** `format.duplicate_line` exists. No
  `duplicate_selection` (block-level copy).
- **Honest callout.** Add `edit.duplicate_selection` to the Edit
  menu; it's two lines of code and a big productivity win.

### 4.18 The Tools menu is deep

- **Industry expectation.** Most successful editors keep top-level
  menus flat with one level of submenu. VS Code's File menu has 9
  items, Edit has 12, View has 22, all flat.
- **QUILL today.** The Tools menu has 14 direct submenus and the
  Read Aloud, BITS Whisperer, and AI submenus each go a level
  deeper. The Custom Profiles under Help also add a third level.
- **Honest callout.** This is a documentation and discoverability
  problem, not a code problem. See §6 for the proposed
  consolidation.

### 4.19 Watch Folder Profiles are documented in the roadmap but
  "single profile" is what the menu exposes today

- **Industry expectation.** Folder Watching tools (Hazel on Mac,
  File Juggler on Windows) all support many rules.
- **QUILL today.** `Watch Folder Profiles...` exists in the menu;
  the roadmap is clear that "many folders, many actions, one
  monitorable queue" is the future.
- **Honest callout.** Land the Watch Profiles feature; it's the
  biggest accessibility-driven productivity story QUILL has.

### 4.20 BITS Whisperer (offline speech-to-text) is deferred

- **Industry expectation.** Dragon, Apple Dictation, Windows Voice
  Typing all exist.
- **QUILL today.** Dictation is a submenu, BITS Whisperer is feature-
  flagged behind `core.bw_whisperer` (off by default in 1.0), and
  per the standing rules, items needing a real Windows runtime must
  stay honestly "In progress."
- **Honest callout.** This is correctly called out in the standing
  rules; keep it in progress and don't pretend it's done.

---

## 5. Industry callouts that QUILL handles correctly

Some behaviors that are easy to get wrong and that QUILL has right —
these are worth saying out loud so they don't regress.

1. **Find and Replace are inside Edit; cross-file search is in
   Search.** This matches the conventional split and matches VS Code
   / Word.
2. **Selection submenu** keeps line / paragraph / block distinct and
   adds "Recent Marks (Ring)" as a nested submenu. This is the Emacs
   influence done well, and it is keyboard-friendly.
3. **The Status Bar settings** live in Tools > Customize, not in
   View. This is a Microsoft convention; it survives menu shuffles.
4. **Insert / Format / Navigate are separate menus.** This matches
   Word and avoids the Notepad++ "everything is in one Format menu"
   trap.
5. **BITS Whisperer is a submenu of Tools when enabled**, and
   demoted from a top-level menu so the main bar stays at ten
   entries.
6. **Pandoc Wizard lives in Tools > Authoring and Automation** —
   not in a buried settings dialog. Power users can find it.
7. **External Tools** lives next to Pandoc and has an executable
   allowlist enforced by the codebase. This is the correct security
   posture.
8. **Compare Documents** is a real submenu (not a sub-submenu) with
   "Next Difference" / "Previous Difference" / "Announce Current" /
   "Difference List" / "Synchronized Navigation" / "Summary" / "Copy
   Current" / "Copy All." That is unusually complete.
9. **Custom Profiles and Feature Profiles** are under Help, not
   buried. Users can find them.
10. **Accessibility Audit, Keyboard Trap Snapshot, Contrast, Link
    Inventory** are all in Tools > Accessibility, not scattered. This
    is a deliberate discoverability choice.

---

## 6. Menu consolidation proposal

The current menu is 10 top-level entries, with Tools being 14-deep
and three submenus reaching a third level. The proposal is to keep
ten top-level menus (the Windows norm) and keep two as the
maximum depth inside any submenu.

### 6.1 Top-level layout (unchanged)

> File, Edit, View, Insert, Format, Navigate, Search, Tools, Window,
> Help. The conventional Windows order. Status bar settings lives in
> Tools > Customize.

### 6.2 Tools submenu: the proposed reorganization

Group the 14 current Tools submenus into 7 logical clusters. The
ordering is by frequency of use: writing essentials first, then
automation, then meta / configuration.

| Cluster                  | Items (submenu)                                                                              | Why                                                                       |
| ------------------------ | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Writing & Language       | Word Count, Spell Check, Previous/Next Misspelling, Misspelling List, Thesaurus, Dictionary Status | Unchanged from current "Writing and Language" submenu.                  |
| Reading & Dictation      | Read Aloud (with Voice / Settings / Generate Audio), Announcement Backend, Dictation, Watch Folder, OCR & Image | Merge Read Aloud + Dictation + Watch Folder + OCR/Image into one "Reading & Dictation" submenu. |
| Automation               | Macros, GLOW, Compare Documents, AI Assistant, BITS Whisperer                                 | Rename the current "Authoring & Automation" cluster; pull AI into it (it already lives under Tools). |
| Workspace                | Workspace Snapshots (relocated here from File), Sticky Notes, Sessions, Recent Files (relocated) | A new cluster that owns document organization. See §7.                 |
| Power Tools              | (All current Power Tools items)                                                              | Unchanged.                                                                 |
| Quillins                 | (All current Quillin items)                                                                  | Unchanged.                                                                 |
| Customization & Support  | Customize (Preferences, Menus, Profiles & Features, Status Bar, Export, Import, Keymap), Accessibility (Audit, Trap, Contrast, Link Inventory), Support (Notifications, Report Bug, Save Diagnostics, Logs, Updates) | A single "Settings & Support" cluster.                                  |

The Tools menu in two-deep form looks like:

```
Tools
├── Command Palette
├── ──────────
├── Writing & Language
│     ├── Word Count
│     ├── Spell Check
│     ├── Previous Misspelling
│     ├── Next Misspelling
│     ├── Misspelling List
│     ├── Thesaurus
│     └── Dictionary Status
├── Reading & Dictation
│     ├── Read Aloud  ▸
│     │     ├── Start / Pause
│     │     ├── Stop
│     │     ├── Voice
│     │     ├── Settings
│     │     └── Generate Audio
│     ├── Announcement Backend
│     ├── Dictation
│     ├── Watch Folder ▸
│     │     ├── Monitoring (in Settings)
│     │     ├── Profiles
│     │     └── Queue
│     ├── OCR Image
│     ├── OCR Clipboard
│     ├── OCR Screen
│     └── Describe Image
├── Automation
│     ├── Macros
│     ├── GLOW
│     ├── Compare Documents
│     ├── Document Intake
│     ├── Pandoc Wizard
│     ├── Regex Helper
│     ├── External Tools
│     └── YAML Structure Editor
├── AI Assistant
│     ├── Use AI
│     ├── AI Status
│     ├── AI Detail
│     ├── AI Hub
│     ├── Ask Quill Chat
│     ├── AI Model and Connection
│     ├── Forget API Key
│     ├── Session Branches
│     ├── Writing Assistant
│     ├── Prompt Studio
│     ├── Agent Center
│     ├── Accessibility Tune-Up
│     ├── Rewrite Selection
│     ├── Summarize Selection
│     ├── Continue Writing
│     ├── Fix Grammar
│     ├── Train Writing Style
│     └── Writing Instructions
├── BITS Whisperer (if enabled)
├── Workspace
│     ├── Workspace Snapshots ▸
│     │     ├── Save Current Snapshot
│     │     ├── Save As...
│     │     ├── Recent Snapshots ▸
│     │     └── Manage Snapshots...
│     ├── New Workspace from Folder...
│     ├── Sticky Notes
│     └── New Sticky Note
├── Power Tools
├── Quillins
├── Accessibility
│     ├── Accessibility Audit
│     ├── Keyboard Trap & Tab-Order Snapshot
│     ├── Validate Contrast
│     ├── Link Inventory & Alt-Text Catalog
│     ├── Inline Word Prediction (toggle)
│     ├── Auto-Format as You Type (toggle)
│     └── Smart Quotes (toggle)
└── Customize & Support
      ├── Preferences
      ├── Customize Menus
      ├── Profiles and Features
      ├── Status Bar Layout
      ├── Export and Back Up
      ├── Import or Restore
      ├── Keymap Editor
      ├── Export Keymap
      ├── Import Keymap
      ├── Reset Keymap
      ├── Notifications
      ├── Report a Bug
      ├── Save Diagnostics
      ├── Open Logs Folder
      ├── Open Diagnostics Folder
      └── Check for Updates
```

Two notable relocations:

- **Workspace Snapshots moves from File > Workspace Snapshots to
  Tools > Workspace**. The File menu is for "open / save this
  document" actions. Workspace is a "session of documents" concept
  and belongs with the cluster that will own the new Library
  surface (§7). A "Recent Snapshots" submenu replaces "Recent
  Sessions" inside the cluster.
- **Read Aloud** keeps its current submenu shape but is now nested
  inside Reading & Dictation. This keeps the two deep clusters
  (Read Aloud and Watch Folder) capped at the second level, which
  matches the standing "no third level" rule from the menu
  consolidation notes.

### 6.3 File menu

Suggested File menu reorganization (kept flat):

```
File
├── New
├── New from Template ▸  (existing Power Tools file-create items)
├── Open...
├── Open Recent ▸
├── Open from URL...
├── Open over SSH ▸
├── Workspace ▸  (new top-level submenu; see §6.4)
├── ──────────
├── Save
├── Save As...
├── Save All
├── Save As Plain Text...
├── ──────────
├── Reload from Disk
├── Restore Backup...
├── ──────────
├── Page Setup...
├── Print...
├── ──────────
├── Close Document
└── Exit
```

The Workspace submenu here is a *gateway* that links to the new
Workspace surfaces (Library, Snapshots, New from Folder) and to the
Tools > Workspace cluster where the management dialogs live. This
gives keyboard and screen-reader users two paths into the same
content.

### 6.4 View menu

```
View
├── Toggle Soft Wrap
├── Auto Side-by-Side Preview
├── Show Tab Control
├── Wrap Find Searches
├── Start With No Document Open
├── ──────────
├── Preview
├── Preview Side by Side
├── Focus Preview
├── Browser Preview
├── ──────────
├── Outline (toggle docked outline panel; new)
├── Library (toggle docked library panel; new)
├── Sticky Notes (toggle docked sticky notes panel; new)
├── AI Chat (toggle docked AI panel; new)
├── ──────────
├── Focus Mode (new; see §9.7)
└── Reading Ruler (new; see §9.8)
```

The four new toggles (Outline / Library / Sticky Notes / AI Chat)
dock the corresponding dialog content as a persistent side panel
(see §7). "Focus Mode" is a one-key "F11" full-screen writing
surface that hides every chrome. "Reading Ruler" is a high-contrast
line-focus toggle for low-vision users.

### 6.5 Navigate menu

Already strong. Suggested additions (all behind the existing
feature-flag system):

- **Go To Bookmark in Workspace** — jump across documents in the
  current Workspace.
- **Go To Snippet** — fuzzy jump to a snippet.
- **Go To Misspelling** — already in the menu under Tools > Writing &
  Language; add a hotkey.
- **Go To Link** — already in Insert and Edit; ensure a key.
- **Go To Heading in Workspace** — cross-document heading jump
  when the active Workspace exposes headings.

### 6.6 Insert menu

Add: **Insert Image from File...**, **Insert Image from Clipboard**,
**Insert Math Block (LaTeX)**, **Insert Citation...** (when a
citation style is configured), **Insert Divider (Horizontal Rule)**,
**Insert Special Character...** (already likely in Power Tools;
promote to a first-class Insert entry).

### 6.7 Format menu

Add: **Auto-Format as You Type** toggle (under
Customize & Support currently; promote to Format or to View), and
**Smart Quotes / Smart Dashes / Smart Ellipses** toggles.

### 6.8 Help menu

Already has a sensible structure. Suggested additions:

- **QUILL Key Primer** (a screen-reader-friendly in-app quick
  reference, gated by the Help system).
- **Keyboard Reference (Printable)** — produces an accessible HTML /
  EPUB cheat sheet filtered by the active profile.
- **Workspace Tour** — first-run walkthrough of the new Library
  surface.

### 6.9 Search menu

Add: **Saved Searches**, **Search Results Window** (toggle docked
results), **Filter by Document** (when a Workspace is loaded).

---

## 7. Workspaces and Document Navigator: the redesign

This is the heart of the ask: take the existing Workspace Snapshots
concept and the existing `open_outline_navigator` modal and turn them
into a Ulysses/Obsidian/Scrivener-inspired but unmistakably QUILL
organization layer. The north star is *calm, keyboard-first, screen-
reader-narrated project organization*, with no new visual chrome a
sighted user would not also value.

### 7.1 Terminology

- **Workspace.** A named, restorable collection of documents,
  bookmarks, snippets, sticky notes, AI conversations, settings
  overrides, and shell hooks. The unit of "this is the project I am
  working on right now."
- **Sheet.** A single document inside a Workspace. Sheets are the
  atomic unit of focus. (The Ulysses name for a single document is
  "sheet" — borrowed on purpose because it is the right metaphor.)
- **Group.** A named, ordered folder of sheets within a Workspace.
  Groups nest. Groups are stored in the Workspace, not on the
  filesystem; the on-disk layout is the user's choice. (Ulysses
  uses "groups"; Scrivener uses "folders" inside the binder.)
- **Section.** A heading range inside a sheet. Sections are the
  unit of focus within a sheet. Already surfaced by
  `_outline_navigator`; now first-class inside the Library.
- **Library.** The on-screen, persistent side panel that shows the
  current Workspace's structure (Groups, Sheets, Sections) and
  drives the editor. (Ulysses name; matches the metaphor.)
- **Sticky Note.** A per-Workspace or global note pinned to a sheet
  or section. (Already exists; promote to a first-class Library
  surface.)
- **Snip.** A saved snippet bound to a Workspace. (New; extends the
  snippet system with a per-Workspace scope.)
- **Goal.** A writing target bound to a Workspace (daily / session /
  deadline). (Ulysses feature; new to QUILL.)
- **Filter.** A saved search / smart folder inside a Workspace.
  Filters are evaluated against the Workspace's sheets and persist
  with it.
- **Snapshot.** A saved point-in-time state of a Workspace.
  (Already exists; renamed for clarity.)
- **Session.** A loaded Workspace with the live documents open in
  the editor.

### 7.2 The Library panel

A docked `wx.Panel` on the left of the editor, toggleable from View
("Library"). The Library is the screen-reader page region with a
list of groups, sheets, and sections. It is *not* a tree (a flat
list with a heading level is more accessible); it shows the
Workspace's structure as a list with a single "level" disclosure
indicator.

Components (all stock wx):

- **Header** — Workspace name, last-saved time, word / character
  count, optional progress goal.
- **Filter** — a `wx.TextCtrl` at the top with a type-ahead filter.
  Matches sheet titles, sheet text, section titles, sticky note
  text, and tags. Announces the match count as it changes.
- **Tree-list** — a `wx.ListBox` populated from the current
  Workspace's structure. Each entry has a label ("Chapter 3 >
  Beat sheet > 4. The reversal"), a kind (Group / Sheet / Section
  / Sticky Note / Filter result), and an optional state badge
  ("draft," "reviewed," "misspellings: 4," "modified").
- **Action bar** — buttons (or keyboard shortcuts): New Sheet, New
  Group, Rename, Delete, Move Up / Down, Promote / Demote, Open
  Sticky Note, Set Goal, Snapshot Now.
- **Context menu** — wired to the same actions. Stock wx context
  menu; no custom-drawn tree.

Behavior:

- **Live focus follows caret.** When the cursor moves to a section,
  the Library's selection moves with it (if the user has not
  manually scrolled the Library). Announce the change.
- **Drag-reorder via keyboard.** Power Tools recirculation. "Move
  Sheet Up" / "Move Sheet Down" / "Move Sheet to Group..." all in
  the Edit and Library menus.
- **Open in new editor tab / new window.** Long-form editing
  benefits from multiple open sheets. The Window menu gets "Next
  Sheet" / "Previous Sheet" if the user opts in to "open sheets in
  a tabbed editor."
- **Read-only by default; explicit write.** New Workspaces are
  empty until the user creates a sheet. Opening an existing
  Workspace Snapshot loads the document set, the caret positions,
  the AI sessions, and the sticky notes.
- **Save behavior.** A Workspace saves automatically on sheet save,
  on snapshot, and on a debounced interval (similar to settings
  persistence). Manual "Save Snapshot" is a menu item.

### 7.3 Outline panel (a docked tree)

Use the existing `_show_tree_navigator` logic but render it as a
panel, not a modal. The current modal is excellent for the
"right-now jump to" use case; the docked panel is for "let me see
the structure as I work." Behind the scenes both share a common
"outline index" primitive in `core/outline.py`.

- The docked panel reads from the active sheet only.
- The modal still works for cross-document jumps inside a
  Workspace.
- Both speak the same names: headings, sections, blocks.

### 7.4 Workspace creation and persistence

A Workspace is a JSON file under `%APPDATA%\Quill\workspaces\`
(validated against `quill/core/schemas/workspace.json`). The
schema is intentionally tight:

```jsonc
{
  "schema_version": 1,
  "id": "ws_<uuid>",
  "name": "My Novel",
  "description": "Working title for the third book.",
  "created_at": "2026-06-01T12:00:00Z",
  "updated_at": "2026-06-01T12:00:00Z",
  "groups": [
    {
      "id": "g_chapters",
      "name": "Chapters",
      "sheets": ["s_intro", "s_chapter1", "s_chapter2"],
      "groups": []
    }
  ],
  "sheets": {
    "s_intro": {
      "id": "s_intro",
      "title": "Introduction",
      "path": "C:\\...\\intro.md",
      "format": "markdown",
      "sticky_notes": ["n_open_question"],
      "snippets": ["sn_opening_quote"],
      "tags": ["draft"],
      "last_caret": 1234
    }
  },
  "sticky_notes": {
    "n_open_question": {
      "id": "n_open_question",
      "title": "Open question",
      "body": "Is the protagonist a reliable narrator?",
      "pinned_to": "s_intro"
    }
  },
  "snippets": {
    "sn_opening_quote": {
      "id": "sn_opening_quote",
      "title": "Opening quote",
      "body": "> ..."
    }
  },
  "tags": ["draft", "reviewed"],
  "filters": [
    {
      "id": "f_open_loose_ends",
      "name": "Open loose ends",
      "query": "TODO OR FIXME"
    }
  ],
  "goal": {
    "kind": "words_per_day",
    "target": 500,
    "period": "day"
  },
  "snapshots": [
    {
      "id": "snap_<uuid>",
      "name": "First draft complete",
      "saved_at": "2026-06-01T12:00:00Z"
    }
  ]
}
```

The schema is intentionally simple: groups nest, sheets live in
groups, sticky notes and snippets are flat collections with
optional pinning. Tags are a free-form string list. Filters and
goals are optional.

### 7.5 File-system mapping

A Workspace is a *logical* layer on top of the user's filesystem;
it does not require a particular directory layout. The user
chooses where each sheet lives; the Workspace stores the path. The
"New from Folder..." command:

1. Walks the chosen folder.
2. Filters by extension (configurable: `.md`, `.txt`, `.epub`, etc.).
3. Suggests a Group / Sheet structure based on the folder tree.
4. Asks once: "Use this layout? Yes / Preview / Edit." The Preview
   shows the proposed tree before any save.
5. Writes the Workspace file.

A "New from EPUB..." command opens an EPUB and creates a Workspace
where the chapters are sheets and the headings are sections.
Matches `open_epub_navigator` semantics.

### 7.6 Workspace Snapshots reborn

- Rename "Workspace Snapshots" to **Snapshots** (the term in the
  Ulysses vocabulary).
- A Snapshot stores the *complete state* of a Workspace at a point
  in time: sheets, caret positions, sticky notes, snippets, AI
  sessions, and the document bytes. This is what the current
  Workspace Snapshots already does; it just needs the rename and
  the menu relocation.
- A Snapshot is immutable. Restoring a Snapshot reopens the
  Workspace from the saved state. Diffing Snapshots is exposed
  through Compare Documents (current menu, current engine).
- Snapshots are exportable as a single `.qws.json` file (the
  Workspace file) and importable, with a conflict-resolution
  dialog for name collisions.

### 7.7 Filters and Smart Folders

A Filter is a saved search. Evaluation rules:

- Match sheets by title, body, sticky-note text, snippet text, or
  tags.
- Boolean expressions: `tag:draft AND title:ch*`.
- Regex support is opt-in.
- Result is a virtual group; opening a result jumps to the match
  in the source sheet.

Filters surface in the Library as a "Filters" sub-list. Selecting
a filter narrows the Library list to its matches; selecting
"Clear Filter" returns to the full list.

### 7.8 Goals and Progress

A Goal is a daily, session, or deadline target. The simplest form:

- Words per day (or characters or sentences).
- Words per session.
- Word count deadline ("reach 50,000 words by 2026-09-30").

The status bar gets a "Progress" cell that announces the
percentage and the remaining words. The Library header shows the
same. A "Streak" cell tracks consecutive days. A spoken
notification at end of session ("Goal reached: 500 words today")
is opt-in and respects the shared announcement grammar.

### 7.9 Cross-document navigation

A Workspace exposes new Navigate menu items:

- **Go To Heading in Workspace** — fuzzy jump across sheets in
  the current Workspace.
- **Go To Bookmark in Workspace** — same.
- **Go To Sticky Note in Workspace** — same.
- **Go To Tag** — opens the Library with the tag filter applied.
- **Go To Filter Result** — opens the active filter's matches.

All of these compose with the existing `quick_nav` index and
benefit from the same prewarm cache.

### 7.10 What this looks like as a flow

A first-run writer opens QUILL and is offered: "Start a new
Workspace, open a recent Workspace, or open a file." Selecting
"Start a new Workspace" shows a dialog: "Name, optional
description, optional folder to import from." A new Library
panel slides in (or the docked tree appears) and the user starts
writing.

After 20 minutes the Library is full of groups, sheets, sticky
notes, and one filter ("TODO"). The status bar shows "Words:
1,234 of 500 today — goal reached." A single keystroke (Ctrl+K,
or QUILL+K) opens the command palette; typing "snapshot" offers
"Snapshot Workspace" and "Manage Snapshots."

A blind user goes through the same flow with the screen reader
narrating "Group: Chapters. Sheet: Introduction. Section: The
premise. Heading level 1. Word count 312." The panel is a
single list region, not a tree, and the focus is always
predictable.

### 7.11 Why this matches the Ulysses / Obsidian / Scrivener bar

- **Ulysses** — library, sheets, groups, filters, goals. QUILL
  borrows the *vocabulary* and the *single-list region* but
  replaces the Mac-only metaphors (sheet sidebar, keyboarder
  two-pane split) with the QUILL key + Quick Nav + docked panel
  + Workspace Snapshot model.
- **Obsidian** — vault, graph, backlinks, Bases. QUILL borrows
  the *vault metaphor* (Workspace = local vault) and the
  *saved filters* (Filters) but explicitly does not adopt the
  graph view in 1.0 (per the standing rules, axe-core, etc., are
  deferred to 2.0). A future "Backlinks" panel that scans the
  Workspace for `[[wiki-style]]` links is a natural 2.0 add-on.
- **Scrivener** — binder, corkboard, outliner, snapshots.
  QUILL borrows the *snapshots* (immutable saves) and the
  *binder* (Library panel) and adds a *Filter* concept that
  Scrivener lacks.
- **Org-mode** — tree, tags, agenda, babel. QUILL borrows the
  *tags* and the *agenda* (Goal) but not the babel / executable
  block. The user Python sandbox and Quillins cover similar
  ground in a more contained way.

The shape is *QUILL-native*: a docked left panel, the QUILL key,
Quick Nav, command palette, and a Workspace Snapshot JSON. The
metaphors are borrowed because they are the right ones; the
implementation is QUILL's.

---

## 8. "Make it amazing" — creative proposals

These are not strict backlog items. They are sketches to inspire
discussion, in priority order.

### 8.1 The QUILL key "what can I do here" panel

The roadmap already calls for a non-modal QUILL key overlay. The
proposal: when the user presses the QUILL key and pauses (no
follow-on key within 250ms), a small overlay appears at the
bottom-left of the editor showing the top ten follow-on keys for
the current context. The overlay is *navigable by arrows*, *closes
on Escape*, and is *announced by the screen reader*. Pressing a
follow-on key dismisses the overlay and runs the command. This is
"Spotlight meets the QUILL key."

### 8.2 Spoken Workspace Tour

A first-run experience for Workspaces: when the user opens a new
Workspace, the QUILL voice narrator walks through the structure
("Workspace: My Novel. 3 groups, 12 sheets, 4 sticky notes. Group
1: Chapters. Sheet 1: Introduction..."). The user can press
Escape to skip, or Space to continue. This is Ulysses's "Sheets"
onboarding, screen-reader-first.

### 8.3 Inline word and character count per section

A docked *Section Stats* cell that shows the word count, the
character count, the reading time, and the "misspelling hint" (a
small badge that links to the Misspelling List filtered to this
section). Updates as the user types. Announced on demand by a
status-bar query.

### 8.4 "Focal Mode" (F11)

A full-screen writing surface that hides the menu bar, the status
bar, the Library panel, the sticky notes, and the AI chat. The
editor is centered, the current paragraph is highlighted, and a
reading ruler (an optional 2-line band) follows the cursor. The
screen reader narrates the current sentence, the next sentence,
and the document position on every caret move. Voice: "Sentence
twelve of forty-two, paragraph three of seven, sheet
'Introduction', line 41." This is a writer's room, not a
distraction surface.

### 8.5 Audio Workspace

A Workspace that lives in the audio domain. A user opens an
audio file (or records into QUILL via BITS Whisperer), the
transcript becomes a sheet, the sticky notes become bookmarks,
and the Workspace's Goal is "minutes recorded today." This is
the same Workspace concept applied to a different content
type — and it is genuinely novel for a screen-reader-first
editor.

### 8.6 In-line AI "ghost" suggestions

A non-modal AI completion surface: as the user types, a small
ghost text appears (gray, italic) showing the AI's suggested
continuation. Pressing a configurable key ("QUILL + ." or "Tab
when no other completion is showing") accepts the suggestion.
"QUILL + ," dismisses. The suggestions are opt-in per Workspace
and respect the consent gate. This is a much lighter-weight AI
experience than the dialog-based rewrite / continue flow that
already exists.

### 8.7 Reading Mode

A mode that turns the editor into a read-only surface with a
configurable line-focus highlight, an optional reading ruler,
and a single key ("R") that reads the current sentence / line /
paragraph aloud using the existing Read Aloud engine. The screen
reader is *not* competing; the editor narrates only on demand.
This is iA Writer's Focus Mode with a screen-reader twist.

### 8.8 "Speak workspace" command

A single key that reads the Library's current selection in full:
the Workspace name, the structure (group > sheet > section), the
sticky notes pinned to the current sheet, the goal status, and
the last snapshot time. This is QUILL's "I am here" speech. It
takes one line of code and is a confidence-builder for new
users.

### 8.9 Inline status for sticky notes

When a sticky note is pinned to a sheet, a small status-bar cell
shows the count and the most-recent title. Hover (or focus) on
the cell opens a tooltip; pressing Enter jumps to the Sticky
Notes panel filtered to the current sheet.

### 8.10 Quick Goal

A status-bar cell that opens a one-field "Daily Goal" prompt on
Enter. The user types 500, presses Enter, and the Goal is set
for the current Workspace. The cell updates to show progress.

### 8.11 Section-level Word Prediction

Take the existing `edit.word_prediction` dialog and add an inline,
opt-in, as-you-type variant that completes the current word from
the surrounding 50 characters of context. The screen reader is
*not* interrupted; the suggestion appears as a status-bar cell
and is accepted with one key. This is a much smaller lift than
LLM completion and is a high-frequency productivity win.

### 8.12 "Reveal in Workspace"

A context-menu action on any file path in the editor: "Reveal in
Workspace." If the file is in the current Workspace, the Library
panel scrolls to the matching sheet and announces it. If the
file is not in the current Workspace, the user is offered "Add
to Workspace" / "Open in New Workspace" / "Cancel."

### 8.13 Cross-document outline

A new Quick Nav category: "Workspace Headings" — every heading
in every sheet in the current Workspace, with a small badge
("Chapter 3 > 4. The reversal") showing the parent sheet. A
single keystroke jumps to it. This composes with `quick_nav`
without a new code path.

### 8.14 Section-level diff and review

A "Review Changes" mode that shows the diff between the current
sheet and the last Snapshot, organized by section. The screen
reader announces the section name and the change count. This is
Scrivener's "Compare" applied at the section level.

### 8.15 Section-anchored sticky notes

A sticky note can be pinned to a *section*, not just a sheet. The
note moves with the section as the user edits. This is a small
data-model change with a large usability impact for writers
doing research-heavy work.

### 8.16 Snippet: "paste Workspace context"

A snippet that, when expanded, pastes a YAML or Markdown
front-matter block with the current Workspace name, sheet name,
section name, line, and column. Useful for AI prompts, bug
reports, and structured notes.

### 8.17 Per-sheet feature profile

Allow a Workspace to override the global feature profile per
sheet. A research sheet might have AI disabled; a draft sheet
might have GLOW disabled; a publish sheet might have macros
disabled. This is a power-user feature; it does not need to be
the default.

### 8.18 Custom panel slots

A `View > Panels` submenu that lets the user choose which docked
panels to show: Library, Outline, Sticky Notes, AI Chat, Spell
Check, Search Results, Misspelling List. Each panel is a single
wx region; the user composes the layout.

### 8.19 Workspace-only "export to EPUB"

A command on the Workspace that orders the sheets, applies the
heading hierarchy, generates a table of contents, and exports a
single EPUB. The Pandoc wizard already does the conversion; the
Workspace layer does the assembly.

### 8.20 Workspace as a search corpus

Add a checkbox to the existing `search_in_files` dialog: "Limit
to current Workspace." The user can search the whole machine
or just the project.

### 8.21 "Sticky Note to Sheet" promote

A command on a sticky note that promotes it to a full sheet.
The note's title becomes the sheet title; the body becomes the
sheet's first paragraph. This is the inverse of "Sheet to
Sticky Note" and a common workflow ("I wrote a note, now I want
to expand it").

### 8.22 AI on a Workspace

The AI Hub gets a "Workspace" tab that shows the current
Workspace's structure and lets the user ask questions like
"What open loose ends do I have?" or "List the three
introductions that mention the antagonist." Answers cite the
sheet and section. The consent gate is the same.

### 8.23 Cross-Workspace references

A Workspace can include sheets from other Workspaces as
"references." Useful for a research Workspace feeding a
manuscript Workspace. The reference is a read-only copy in the
referring Workspace; updates are detected on Snapshot save.

### 8.24 "Today" view

A new panel that shows everything that changed in the current
Workspace today: new sheets, edited sheets, new sticky notes,
new snapshots, AI sessions, and the Goal progress. This is
Ulysses's "Today" list, screen-reader-first.

### 8.25 Workspace Diff

Two Workspaces can be diffed (sheet presence, sticky note text,
filter results). Useful for "what's different between the draft
I sent to the editor and the one I have now?"

### 8.26 Voice-driven Workspace navigation

A voice command (Hey QUILL) that opens a sheet by name, sets a
goal, or pins a sticky note. "Hey QUILL, open the introduction."
"Hey QUILL, set today's goal to 750 words." The dictation
engine is the same; the command grammar is Workspace-aware.

### 8.27 Workspace onboarding

A first-run "Try a Sample Workspace" that ships with QUILL:
a tiny project ("Letter to a friend") with three sheets, one
sticky note, one filter, and one goal. The user opens it,
explores the Library, the Outline, the Sticky Notes, the
Snapshots, and the AI Hub — all without writing a word. The
onboarding is itself screen-reader-friendly.

### 8.28 Per-section reading time and Flesch-Kincaid

Each section gets an announced reading time and a Flesch-Kincaid
grade level. The status bar cell toggles between "Words,"
"Reading time," and "Grade level." This is a writing-quality
superpower for a screen-reader user who can't see the wall of
text and wants a number.

### 8.29 Workspace focus session

A "Start a 25-minute focus session" command that opens a single
sheet, hides the Library and Sticky Notes, sets a 25-minute
timer, and announces the start and end. At the end, the Library
returns, the Goal cell updates, and a "Snapshot" button is
offered.

### 8.30 "I am stuck" command

A single key that opens a Workspace-aware AI prompt: "Help me
write the next paragraph of the current sheet, using these
three notes and this filter result as context." The consent
gate is the same; the response is previewed in a docked panel
and accepted with a single key. This is the AI "writer's block"
killer.

---

## 9. Implementation roadmap

Suggested sequencing, mapped to the existing roadmap priority
language.

### 9.1 Tier 1 (1.0 essentials)

- **Workspaces and Library panel** (§7). The core of the redesign.
  The new schema, the docked panel, the snapshot rename.
- **Menu consolidation** (§6). Pure reorganization. Ship a
  `menus.md` companion document alongside.
- **Focus Mode** (§8.4). Single screen, hides chrome.
- **Inline word prediction** (§8.11). High-frequency, low-risk.
- **Auto-format toggle** (§4.14). High discoverability win.
- **Context menu for misspellings** (§4.16). High discoverability
  win.
- **Duplicate selection** (§4.17). Tiny lift, big win.
- **Image insert** (§4.15). Required for many writing apps.
- **Go To Line preview** (§4.9). Trivial.

### 9.2 Tier 2 (post-1.0, near-term)

- **Filters and Smart Folders** (§7.7). Composes with Library.
- **Goals and Progress** (§7.8). Composes with Library.
- **Cross-document outline and quick nav extensions** (§7.9, §8.13).
- **Section-level stats** (§8.3).
- **Inline status for sticky notes** (§8.9).
- **Quick Goal** (§8.10).
- **Reveal in Workspace** (§8.12).
- **Multi-cursor / column select** (§4.3). Larger lift; needs a
  design pass.
- **Saved Searches** (§4.10).
- **Snippets tab stop / placeholder walkthrough** (§4.8).
- **AI chat docked** (§4.5).
- **Reading Ruler** (§4.13).

### 9.3 Tier 3 (exploratory, 2.0 and beyond)

- **Backlinks panel / vault graph** (Obsidian-style; explicit
  deferral per standing rules).
- **Corkboard view** (Scrivener-style).
- **Audio Workspace** (§8.5). Needs BITS Whisperer complete.
- **In-line AI ghost suggestions** (§8.6). Needs the consent
  surface to be a first-class UI element.
- **Cross-Workspace references** (§8.23).
- **Workspace diff** (§8.25).
- **Voice-driven Workspace navigation** (§8.26). Needs the
  voice-commands grammar to mature.

### 9.4 Tier 4 (creativity, optional)

- **"Speak workspace" command** (§8.8). One-liner; high delight.
- **Workspace-only "export to EPUB"** (§8.19).
- **Per-section reading time and grade level** (§8.28).
- **Section-anchored sticky notes** (§8.15).
- **Sticky Note to Sheet promote** (§8.21).
- **"Today" view** (§8.24).
- **Workspace focus session timer** (§8.29).
- **"I am stuck" command** (§8.30).
- **Sample Workspace onboarding** (§8.27).
- **Snippet: paste Workspace context** (§8.16).
- **Per-sheet feature profile** (§8.17).
- **Custom panel slots** (§8.18).
- **Reading Mode** (§8.7).
- **Inline status for sticky notes** (§8.9, overlap).
- **Snippets for Workspace context** (§8.16, overlap).

---

## 10. Closing

QUILL is an editor that treats screen-reader users as the primary
audience and proves it in the architecture: stock controls, dialog
contracts, a typed core, a tight menu, and a roadmap that names the
right risks. The competitive analysis confirms that QUILL is at or
near the front of the pack on accessibility, navigation, AI
integration, and writing-quality tooling, and that the most
under-developed area is the project-organization layer.

The recommendations in this document are conservative in spirit: a
new Workspace JSON schema, a docked Library panel, a Goals surface,
a menu consolidation that flattens Tools, and a long list of
"delight" proposals that are mostly *composition* of primitives
that already exist in the codebase. Nothing in §7 or §8 requires
breaking the dialog contract, the feature-flag discipline, or the
core / io / ui boundary. Everything is a v1.x candidate; the most
ambitious items are honestly Tier 3 and explicitly future.

The bar is: a screen-reader user opens QUILL, presses the QUILL key,
types "library," and the Library panel appears with the current
Workspace's structure announced. They press "G" for group, name a
new group, name a sheet, paste a sticky note, set a daily goal of
500 words, and start writing. Two hours later they press
Ctrl+Shift+S to snapshot, type a name, and the snapshot is saved.
The next morning they press Ctrl+Shift+O, choose the snapshot, and
the editor re-opens to the same place with the same sticky note
pinned to the same section. That is a writing environment that is
not a compromise. That is QUILL.
