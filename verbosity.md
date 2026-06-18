# Verbosity Rebuild Plan — v3

## Context

On 2026-06-18, an earlier parallel session had built out the verbosity system end to end. That work was destroyed by `git stash drop` (see `memory/feedback_no_stash_drop.md`). This plan rebuilds it from scratch with a refined design shaped by:

- The surviving modified files in the working tree (treated as the new baseline).
- 186 assistant text blocks from `0fd8e4b9-b036-49de-9d26-34771e2cb4a8.jsonl` that survived the loss.
- A focused design pass with the user (profile model, sound channel, magic, audio defaults, editor shape, library, QVP files).
- Two specialist reviews: accessibility-lead (15 findings, 3 critical) and wxPython Specialist (wx architecture + risk register).

**Version target**: 0.7.1 (patch on top of 0.7.0).

## Locked design decisions

| Decision | Choice |
|---|---|
| Profile UX | Hybrid: 4 ladder presets (Beginner/Normal/Expert/Quiet) populate 4 channel checkboxes below; checkboxes editable; "Modified" pill warns when channel edits diverge from preset. Switching profiles announces the reset. |
| Channels | speech / braille / sound / visual (visual is always-on floor). All four combinations expressible; combinations discovered via presets. |
| Sound channel | Per-event sound gating independent of master; quiet-hours auto-engage when sound is off; speech-pause-before-announce (~200ms inside the engine); sound character varies by ladder (Beginner chime / Expert subtle click). |
| Magic | Auto-detect mastery → offer to step down (10s timeout, spoken countdown at 3s); profile preview replays last 3 announcements in new profile (`Ctrl+Shift+Enter` to replay); one-tap Meeting profile (Ctrl+Shift+B); quiet-hours entry/exit toast with Ctrl+Shift+Z undo. |
| Validation timing | On-button only (default). Validation messages ARE spoken when user clicks Validate (Ctrl+T) or Preview (Ctrl+Shift+P). Color is supplementary; shape prefixes `[X]` / `[!]` / `[OK]` carry primary signal. |
| Audio defaults | Validation-spoken is the ONLY audio ON by default. Auto-play on editor open, palette-token audio, focus-out read-back are opt-in toggles. |
| Token editor | Simple (sentence-builder ListBox) + Advanced (raw TextCtrl) toggle via `wx.RadioBox`. Simple is the SR-first default. Both views share backing data. |
| Per-verb default UX | "Use default" is the headline. Per-verb Custom is opt-in. Per-row dropdown shows `—` when using default; rendered + syntax shown when customized. |
| Templates library | v1: full CRUD (save/apply/delete/rename). Flat `wx.ListBox` browse; per-row dropdown apply; no drag-and-drop. |
| Library cross-verb | Auto-filter invalid tokens + warn: "Applied template Concise. Removed 2 tokens because this verb doesn't track them: cell, region." |
| Per-verb table | Master/detail with filter, NOT a grid. Virtual `wx.ListCtrl` (LC_REPORT, LC_VIRTUAL) on the left; detail pane on the right. Filter via `wx.SearchCtrl` matches verb name AND namespace. |
| QVP files | JSON-only `.qvp.json`. Data-only, schema-validated, no signing. Manual file install from Library tab. Namespaced by author (no conflicts). `min_quill_version` gate. Required metadata: name, author, description, version, license. Optional: preview_text, tags, depends. |

## Scope

### A. Profile model

4 ladder presets × channel-mix defaults. Custom is opt-in per-verb.

| Preset | speech | braille | sound | visual | Notes |
|---|---|---|---|---|---|
| `beginner` | on | on | on | on | Verbose hints, full context, teaching style |
| `normal_intermediate` | on | on | on | on | Default. Concise-but-complete. |
| `expert` | on | on | errors only | on | Drops routine confirmations; sound only on errors. |
| `quiet` | off | on | off | on | Quiet-hours-style: braille + status bar. |

**Channels** are the checkbox grid below the preset. Editing a checkbox while a preset is selected:
- Shows a "Modified" pill on the preset radio button.
- Switching presets prompts: "Switched to Expert. Channels reset to Expert defaults: speech on, braille on, sound off, visual on. Your previous edits were discarded. Press Ctrl+S to keep them as a Custom profile." (`Ctrl+S` saves the modified state as a new user profile.)

`Visual` is unchecked-but-disabled with the accessible name: `"Visual status bar, always on, cannot be disabled."`

### B. Channel system

```python
class Channel(enum.Flag):
    SPEECH = enum.auto()
    BRAILLE = enum.auto()
    SOUND = enum.auto()
    VISUAL = enum.auto()  # accessibility floor; always on
```

Per-event sound gating (`core.sound.events`) is independent of the master sound channel — a per-event toggle controls whether that specific event plays a sound even when sound is on. Quiet-hours auto-engage: when the master sound channel turns off, a status-bar indicator shows "Quiet hours auto-engaged" and the engine routes announcements to speech+braille+visual only.

Speech-pause-before-announce: a 200ms silence inserted INSIDE the engine before each announcement, so the screen reader doesn't truncate the start.

Sound character varies by ladder: each ladder selects a sound "voice" (Beginner = friendly chime pack, Expert = subtle click pack). Library can ship alternative voices via QVP.

### C. Token system (the centerpiece)

Each verb declares a `VerbSpec` with:

```python
@dataclass(frozen=True)
class TokenSpec:
    name: str               # e.g. "column"
    type: Literal["str", "int", "float", "bool", "datetime", "duration"]
    description: str        # human-readable, used in editor and SR help
    derive: Callable[[Context], Any]   # how to extract from context dict
    filters: tuple[str, ...] = ()      # allowed filters for this token
```

Custom-template syntax: `{name}` for raw value; `${filter:name}` and `${filter:arg:name}` for filtered values.

**Allowed filters** (engine-implemented): `upper`, `lower`, `title`, `ordinal`, `pad:N`, `pluralize`, `singular`, `duration_human`, `date_long`, `date_short`, `time`, `truncate:N`. Custom filters are NOT supported (security: templates run with no Python access; this prevents injection).

**Validation behavior**:
- **Strict allowlist**: every `{name}` in the template must match a `TokenSpec.name` for that verb. Unknown names are flagged red and **the announcement cannot be saved** while any red token exists.
- **Type check**: filter outputs are type-checked against `TokenSpec.type` (`pad:N` requires `int`; `date_long` requires `datetime`).
- **Filter allowlist per token**: each token declares which filters it accepts. `pad` only works on numeric tokens; `date_long` only on datetime tokens. Mismatches are flagged amber.
- **Default validation mode**: On-button. Validate (Ctrl+T) and Preview Announcement (Ctrl+Shift+P) trigger validation; spoken result. Live and On-focus modes available as alternatives.

**Validation messaging contract**:
- Spoken: `"Validation: 3 tokens, 1 warning, 0 errors."` Then list items on demand.
- Sighted: read-only review field shows `[X] {garbage} → unknown token`, `[!] {pad:4:line} → pad not allowed for line`, `[OK] {column} → 14`.
- Debounce: 250ms on Preview button. If already playing: `"Preview already playing."` (not silence).

### D. Data reordering

Each verb has:

```python
@dataclass(frozen=True)
class DataOrder:
    verb_id: str
    fields: tuple[str, ...]   # ordered list of TokenSpec.name
    separator: str = ", "     # how to join
```

Editor for data reorder is a `wx.ListBox` with up/down reorder buttons.

**Custom override**: if the user has set BOTH a custom template AND a custom data order for a verb, the template wins and the data order is ignored for that verb.

### E. Verbosity tab in Preferences (`quill/ui/verbosity_prefs.py`)

```
VerbosityPrefsPanel (wx.Panel, embedded in Preferences Notebook)
├── ProfilePicker (wx.RadioBox; ladder presets; "Modified" pill state)
├── ChannelMixBox (wx.StaticBoxSizer with 4 wx.CheckBox; visual disabled)
├── MasteryBox (wx.CheckBox + wx.SpinCtrl for N)
├── ValidationModeBox (wx.RadioBox; Live/On-focus/On-button; default On-button)
├── CollapsibleVerbTable (wx.CollapsiblePane, collapsed=False)
│   └── VerbTablePanel
│       ├── FilterBar (wx.SearchCtrl + wx.Choice for namespace)
│       └── MasterSplit (wx.SplitterWindow HORIZONTAL)
│           ├── VerbList (wx.ListCtrl LC_REPORT + LC_VIRTUAL; verb name col)
│           └── VerbDetailPanel (selected verb's controls)
│               ├── LadderChoice (wx.Choice)
│               ├── ChannelCheckBoxes (4)
│               ├── StyleChoice (wx.Choice)
│               ├── TemplatePreview (wx.TextCtrl TE_MULTILINE|TE_RICH2|TE_READONLY; 2 lines)
│               ├── DataOrderSummary (read-only)
│               ├── EditButton + ResetButton
└── StatusLine (wx.StaticText, name="verbosity_status"; role=status, live=polite)
```

**Initial focus** lands on the Filter `wx.SearchCtrl` (power users land here most often). Profile picker is second in tab order.

**VerbList columns**: Verb name (with firing-context description for SR — "Next Print Page, fired by Ctrl+Page Down, currently Beginner"). The verb row announcement includes the firing context so SR users never have to cross-reference Keyboard Manager.

**Filter**: matches verb name AND namespace. Live-narrow with 150ms debounce. SR users get a focused single-list reading experience.

**VerbDetailPanel** updates on `EVT_LIST_ITEM_SELECTED`. The detail panel exposes one wx.Choice per override (ladder, channels, style, template dropdown), plus an Edit button. Reset button announces: "Reset Next Print Page to profile default; custom template cleared, ladder cleared."

### F. Token editor (`quill/ui/verbosity_token_editor.py`)

Modal dialog opened from VerbDetailPanel's Edit button or from the per-chord mini-editor.

```
VerbosityTokenEditor (wx.Dialog)
├── EditorPane (proportion=1)
│   ├── ModeBar (wx.RadioBox; horizontal; [Simple, Advanced])
│   ├── ReviewField (wx.TextCtrl TE_MULTILINE|TE_RICH2|TE_READONLY; 2 lines)
│   ├── SimpleView (wx.ListBox LB_SINGLE; sentence fragments)
│   ├── AdvancedView (wx.TextCtrl TE_MULTILINE|TE_RICH2; raw template)
│   └── ButtonRow (wx.StdDialogButtonSizer; Preview, Validate, Save, Cancel)
└── Palette (proportion=0, min width 240)
    ├── CollapsiblePane x4 (Position / Count / Document / Time)
    │   └── wx.ListBox of tokens (double-click or Enter to insert)
    └── LibrarySection (user's saved templates)
```

**Initial focus**: Advanced `TextCtrl` if mode is Advanced, else `SimpleView` ListBox.

**Simple/Advanced toggle**: `wx.RadioBox` (horizontal, 2 choices). NOT a `wx.Notebook` — both views share backing data; a notebook implies parallel pages. SR users get a single, unambiguous name + value.

**Simple view fragment-swap**: `EVT_LISTBOX_DBOX` for double-click AND `EVT_CHAR_HOOK` on the parent dialog for Enter when ListBox has focus. **DO NOT** bind `EVT_KEY_DOWN` on the ListBox — NVDA swallows `WM_KEYDOWN` before the ListBox sees it. Add `Ctrl+R` to read the current assembled template aloud.

**Advanced view**: raw `{column}` syntax in a `wx.TextCtrl`. Palette sidebar lists tokens via 4 `wx.CollapsiblePane` sections (Position / Count / Document / Time). Double-click or Enter on a token inserts at caret. `Alt+1..4` jumps to namespace. Validation messages paired with shape prefixes (`[X]`, `[!]`, `[OK]`).

**ReviewField** is `TE_MULTILINE|TE_RICH2|TE_READONLY`. First line: rendered announcement in default font. Second line: raw template in monospace font. Reset `SetDefaultStyle` between lines so styles don't bleed.

**Save button** is disabled when the template contains an unknown token (`btn_save.Enable(template_is_valid)`). Disabled Save surfaces a `SetToolTip` with the reason ("1 unknown token — fix to save"). SR users hear "Save disabled, 1 error" via the focus event.

**Validate / Preview hotkeys**: `EVT_CHAR_HOOK` on the dialog level, NOT the global keymap (modal dialog must consume the accelerator).

### G. Quiet Mode + Meeting Mode + Profile Preview

- `Ctrl+Shift+Q` toggles Quiet Mode globally. `QUILL key + Q` does the same.
- One-shot announcement on toggle: `"Quiet mode on. Speech and sound silenced. Press Ctrl+Shift+Q to turn off."` (and status-bar `[Q]` badge).
- Meeting Mode: `Ctrl+Shift+B` toggles `speech_only`. Announcement: `"Meeting mode on. Quiet hours engaged until you press Ctrl+Shift+B again."`
- Quiet-hours entry/exit toast with `Ctrl+Shift+Z` undo: speaks `"Quiet hours reverted. Speech restored."`
- Profile preview: when user picks a new profile, the last 3 announcements are replayed in the new profile. `Ctrl+Shift+Enter` while profile picker has focus = "Replay preview for current profile."

### H. Magical Keyboard Manager integration

`quill/ui/keyboard_manager_dialog.py` gains a **Verbosity tab**. Each chord gets a single `wx.Choice` for verbosity:

| Chord | Action | Verbosity |
|---|---|---|
| `Ctrl+Home` | Document Start | Profile default |
| `Ctrl+Shift+Right` | Select Word Right | Quiet |
| `Ctrl+G` | Go to Line… | Custom for this chord… |

Choice options: `Profile default / Quiet / Beginner / Normal / Expert / Custom for this chord…`. The last option opens a mini-editor (`verbosity_chord_editor.py`) scoped to ONLY the verbs fired by that chord. Channels and style cascade from the chosen ladder unless Custom is selected.

**Mini-editor entry announcement**: `"Ctrl+Shift+Right fires Select Word Right. Mini-editor will scope to this verb."`

Group chords by category (Nav / Edit / Doc) with `Ctrl+1..N` to jump between groups.

### I. Templates Library (`quill/ui/verbosity_library.py`)

Two surfaces, one model:
1. **Library tab** in Verbosity Preferences. `wx.ListCtrl` (LC_LIST style, single column) with `wx.SearchCtrl` filter and namespace grouping. Each item announces: `Template name, last modified date, source (User or QVP-installed), verb count, applies to verbs: yes/no`. Built-in templates read-only; user templates deletable.
2. **Per-row dropdown** (`wx.Choice` — NOT `wx.ComboBox`) in the VerbDetailPanel. Lists: `Built-in Default / Built-in Concise / Built-in Verbose / [separator] / <user templates> / <QVP-installed templates>`. Selecting one applies it; "Browse library..." opens the Library tab.

**Save flow**: `Ctrl+S` while editing in Simple or Advanced opens "Save as template" with a single name field. No category picker — optional, off by default.

**Apply announcement**: `"Applied template Concise. Removed 2 tokens because this verb doesn't track them: cell, region."`

### J. QVP files (`.qvp.json`)

JSON-only. Data-only, no code. Schema-validated; no signing.

```json
{
  "schema_version": 1,
  "kind": "quill-verbosity-pack",
  "min_quill_version": "0.7.1",
  "pack": {
    "name": "Audio Descriptive Concise",
    "author": "kellyford",
    "description": "Concise templates optimized for audio description workflows.",
    "version": "1.0.0",
    "license": "MIT",
    "tags": ["screen-reader", "concise", "audio-descriptive"],
    "preview_text": "Now reading page 7, line 14.",
    "depends": ["kellyford.audio-descriptive-core"]
  },
  "templates": [
    {
      "id": "kellyford.audio-descriptive-concise",
      "name": "Concise",
      "applies_to": ["nav.*"],
      "template": "{running_head}, page {print_page} of {print_page_total}.",
      "data_order": ["running_head", "print_page", "print_page_total"],
      "separator": ", ",
      "preview": "Chapter 2, page 7 of 87."
    },
    {
      "id": "kellyford.audio-descriptive-verbose",
      "name": "Verbose",
      "applies_to": ["nav.*"],
      "template": "Now reading {running_head}. Print page {print_page} of {print_page_total}. Line {line} of {total_lines}.",
      "preview": "Now reading Chapter 2. Print page 7 of 87. Line 14 of 25."
    }
  ]
}
```

**Field reference**:
- `schema_version` (int, required): currently 1.
- `kind` (str, required): must be `"quill-verbosity-pack"`.
- `min_quill_version` (str, required): gates install via existing Quillin platform logic.
- `pack.name`, `pack.author`, `pack.description`, `pack.version`, `pack.license`: required metadata.
- `pack.tags` (list[str], optional): for Library filter.
- `pack.preview_text` (str, optional): shown in Library detail before install.
- `pack.depends` (list[str], optional): other QVP names that should also be installed. Library install handles dep ordering.
- `templates[].id` (str, required): namespaced by author (e.g., `kellyford.audio-descriptive-concise`).
- `templates[].name` (str, required): human-readable name shown in dropdown.
- `templates[].applies_to` (list[str], required): verb namespaces this template targets (e.g., `["nav.*"]`). Glob support.
- `templates[].template` (str, required): the raw template string with `{token}` and `${filter:arg:token}` syntax.
- `templates[].data_order` (list[str], optional): field order for default rendering.
- `templates[].separator` (str, optional): default `", "`.
- `templates[].preview` (str, optional): rendered preview shown in the Library detail pane.

**Install flow**: Library tab → "Install QVP from file…" → file picker → schema validation → min_quill_version check → `templates[].id` collision check (should never happen with namespaced IDs, but assert) → `pack.depends` resolution → install. Each step announces: `"Validating pack..."`, `"Min QUILL version 0.7.1, you have 0.7.1. OK."`, `"Pack installed. 2 templates added. Author: kellyford."`

**Library entries from QVPs**: read-only in the Library tab. Source shown as `QVP: kellyford.audio-descriptive`. Removing a QVP requires uninstalling the whole pack.

**No drag-and-drop, no auto-update, no Hub integration in v1.** v2 may add Quillin Hub browse.

### K. New files

**Core** (`quill/core/verbosity/`)
- `__init__.py` — public surface
- `channels.py` — `Channel` enum (Flag); `visual` is the floor
- `styles.py` — `Style` enum
- `profiles.py` — `Profile` dataclass + 4 ladder presets + Custom escape hatch
- `tokens.py` — `TokenSpec` dataclass; filter implementations; type-check helpers
- `parser.py` — token template parser; produces `ParseResult` with valid tokens, amber warnings, red errors
- `verbs.py` — `VerbSpec` dataclass + ~50 `VERB_*` constants across namespaces
- `registry.py` — `VerbRegistry` lookup; legacy `_announce()` calls route as `_legacy`
- `data_order.py` — `DataOrder` dataclass + helpers
- `engine.py` — `VerbosityEngine`; applies profile + style + channel gates + per-verb overrides + chord overrides; runs parser, builds AST, resolves tokens, renders to channels
- `mastery.py` — per-verb success counter; auto-step-down with 10s spoken countdown
- `quiet.py` — `QuietMode` controller; one-shot toggle announcements
- `meeting.py` — `MeetingMode` controller
- `storage.py` — read/write `verbosity_custom.json` (atomic via `core.storage.write_json_atomic`); rejects invalid overrides on load with non-blocking warning dialog
- `schema.py` — JSON schema for `verbosity_custom.json`
- `preview.py` — engine-side helper: take a `ParseResult` and a `Context`, return rendered strings (one per channel)
- `qvp.py` — QVP file load/save; schema validation; min_quill_version check; dep resolution
- `library.py` — Templates Library model; user templates + QVP-installed templates; CRUD operations

**UI** (`quill/ui/`)
- `verbosity_prefs.py` — `VerbosityPrefsPanel` (embeddable in Preferences Notebook) + `VerbosityPrefsDialog`
- `verbosity_token_editor.py` — `VerbosityTokenEditor` (Simple + Advanced; Palette; Validate; Preview; Save)
- `verbosity_data_order.py` — `VerbosityDataOrderDialog` (up/down reorder)
- `verbosity_chord_editor.py` — `VerbosityChordEditor` (mini-editor scoped to chord's verbs)
- `verbosity_library.py` — Library tab + browse dialog; QVP install flow
- `about_dialog.py` — `AboutDialog` (3-tab Notebook; depends on `quill/core/about_info.py`)

### L. Files to modify

- `quill/core/feature_command_map.py` — register `feature.verbosity_prefs`, `feature.quiet_mode_toggle`, `feature.meeting_mode_toggle`, `feature.about_dialog`, `feature.validate_announcement`, `feature.preview_announcement`, `feature.qvp_install`, `feature.qvp_uninstall`
- `quill/core/keymap.py` — `Ctrl+Shift+Q` → `feature.quiet_mode_toggle`; `Ctrl+Shift+B` → `feature.meeting_mode_toggle`; `Alt+Shift+Q` → `edit.unquote_lines`; `Ctrl+Shift+M` → `feature.verbosity_prefs`; `Ctrl+T` (in token editor) → `feature.validate_announcement`; `Ctrl+Shift+P` (in token editor) → `feature.preview_announcement`; `Ctrl+Shift+Z` → `feature.undo_quiet_hours`; `Ctrl+Shift+Enter` (in profile picker) → `feature.replay_profile_preview`
- `quill/core/settings.py` — add `VerbositySettings` (current_profile, channels_modified, mastery_enabled, mastery_threshold, validation_mode, quiet_hours_enabled, meeting_mode, verbosity_custom_overrides)
- `quill/core/settings_specs.py` — schema entries for new verbosity fields
- `quill/ui/main_frame.py` — wire VerbosityPrefsPanel into Preferences dialog; AboutDialog from Help menu; Quiet/Meeting Mode hotkeys; status-bar `[Q]` and `[M]` badges
- `quill/ui/main_frame_menu.py` — View menu: Verbosity Preferences…, Quiet Mode toggle, Meeting Mode toggle; Help menu: About Quill…
- `quill/ui/main_frame_quill_key.py` — `QUILL key + Q` chord for Quiet Mode
- `quill/ui/main_frame_statusbar.py` — `[Q]` and `[M]` badge cells; "Quiet hours auto-engaged" status text
- `quill/ui/info_pages.py` — wire Help > About to AboutDialog
- `quill/ui/keyboard_manager_dialog.py` — add Verbosity tab; per-chord override `wx.Choice`
- `quill/ui/setup_wizard_pages.py` — add Verbosity page (profile picker only)
- `quill/quillins_bundled/doc-guardian/extension.py` — register a Quillin hook for verb specs (extension authors can register custom verbs)
- `scripts/build_windows_distribution.py` — include `verbosity_custom.json` and `qvps/*.qvp.json` in backup bundle
- `quill/tools/module_size_budgets.json` — re-baseline `main_frame.py` after edits complete

### M. Tests

Core:
- `tests/unit/core/test_verbosity.py` — engine gates per profile/style/channel
- `tests/unit/core/test_verbosity_tokens.py` — token parser, type checks, filter allowlist per token, strict mode rejects unknown
- `tests/unit/core/test_verbosity_filters.py` — each filter's behavior
- `tests/unit/core/test_verbosity_parser.py` — parser AST, amber/red classification
- `tests/unit/core/test_verbosity_data_order.py` — data reorder joins correctly
- `tests/unit/core/test_verbosity_preview.py` — preview helper resolves tokens and produces channel-specific output
- `tests/unit/core/test_verbosity_storage.py` — atomic write, schema validation, invalid overrides rejected
- `tests/unit/core/test_verbosity_qvp.py` — QVP load/save, schema validation, min_quill_version gate, namespaced IDs, dep resolution
- `tests/unit/core/test_verbosity_library.py` — user template CRUD; QVP-installed entries read-only; conflict resolution
- `tests/unit/core/test_verbosity_mastery.py` — auto-step-down with timeout; spoken countdown
- `tests/unit/core/test_verbosity_quiet.py` — QuietMode controller; one-shot announcements
- `tests/unit/core/test_verbosity_meeting.py` — MeetingMode controller
- `tests/unit/core/test_about_info.py` — AboutInfo construction

UI:
- `tests/unit/ui/test_verbosity_prefs.py` — Preferences panel builds, profile picker reacts, "Modified" pill state, master/detail split, filter narrows
- `tests/unit/ui/test_verbosity_token_editor.py` — editor builds, Simple + Advanced modes, palette insertion, Validate button updates review field, Save blocked on invalid token, Preview Announcement debounced
- `tests/unit/ui/test_verbosity_data_order.py` — up/down reorder
- `tests/unit/ui/test_verbosity_chord_editor.py` — mini-editor scopes to chord's verbs only
- `tests/unit/ui/test_verbosity_library.py` — Library tab, save/apply/delete/rename, QVP install flow, namespaced IDs shown
- `tests/unit/ui/test_verbosity_qvp_install.py` — file picker → schema validation → min_quill_version check → install; namespaced IDs visible in per-row dropdown
- `tests/unit/ui/test_keyboard_manager_verbosity.py` — per-chord override `wx.Choice`, mini-editor launch
- `tests/unit/ui/test_quiet_mode.py` — Ctrl+Shift+Q, QUILL key + Q, status bar `[Q]` badge, one-shot announcement (mocked)
- `tests/unit/ui/test_meeting_mode.py` — Ctrl+Shift+B, status bar `[M]` badge
- `tests/unit/ui/test_info_pages.py` — Help > About opens 3-tab dialog
- `tests/unit/ui/test_post_show_foreground.py` — existing test still passes after AboutDialog wiring
- `tests/unit/scripts/test_build_windows_distribution.py` — verbosity backup integration; QVP bundle integration
- `tests/unit/ui/test_main_frame_quill_key.py` — `QUILL key + Q` chord
- `tests/unit/core/test_quill_key_help.py` — chord list includes Quiet Mode

### N. Docs

- `docs/Product Requirement Documents and Specifications/QUILL-PRD.md` — new section: Verbosity System (~100 lines: profiles, channels, ladder, token system, data order, mastery, Keyboard Manager integration, QVP files)
- `docs/user guide/userguide.md` — new chapter: Verbosity (~200 lines; user-facing walkthrough of profile picker, custom editor with screenshots-in-prose, token palette, Validate, Preview, Keyboard Manager overrides, mastery ladder, QVP install flow)
- `docs/CONTROL_REFERENCE.md` — register `Ctrl+Shift+Q`, `Alt+Shift+Q`, `Ctrl+Shift+B`, `Ctrl+Shift+M`, `Ctrl+Shift+Z`, `Ctrl+T`, `Ctrl+Shift+P`, `Ctrl+Shift+Enter`
- `docs/release notes/release0.7.1.md` — release notes for the rebuild (5 new hotkeys enumerated)
- `CHANGELOG.md` — 0.7.1 entry

### O. Versioning

- `quill/__init__.py`: `__version__ = "0.7.1"`
- `installer/quill.iss`: AppVersion + OutputBaseFilename → 0.7.1

## Accessibility commitments

- **SR-first**: every dialog has tab order that lands on the most useful control first; every button has a real `label=` not just an icon; every interactive element has a name/role/value exposed.
- **Live regions**: token validation messages use `role=status`, `aria-live=polite` for warnings, `assertive` for blocking errors.
- **Keyboard-only path**: every action has a keybinding; tab order is verified; focus indicators meet WCAG 2.4.11 (focus not obscured).
- **Contrast**: text on backgrounds meets WCAG AA; the red/amber/green color coding is paired with shape prefixes (`[X]` / `[!]` / `[OK]`) so colorblind users get the same info.
- **No motion-only feedback**: Preview Announcement has a text equivalent (status bar shows what was spoken).
- **Plain language**: profile names are human-readable; "Beginner", "Normal", "Expert", "Quiet" not "L0/L1/L2".
- **One-shot toggle announcements**: Quiet/Meeting Mode toggles speak their state change immediately. `[Q]` and `[M]` badges in the status bar are sighted-only; the spoken announcement is the canonical signal.
- **Master/detail with filter**: the per-verb table is a master/detail with a filter input. SR users can narrow to a few verbs without arrowing through 50.
- **Firing context in row announcement**: per-verb rows announce name + firing chord + current override, so SR users never need to cross-reference Keyboard Manager.

## Order of work

1. **Core engine (no UI yet)**: channels → styles → profiles → tokens → filters → parser → verbs → registry → data_order → mastery → quiet → meeting → storage → schema → preview → qvp → library → engine → `__init__.py`.
2. **Tests in lockstep** with each module. Parser tests must hit >95% coverage before any UI uses it (hard gate).
3. **`quill/core/about_info.py`** + tests.
4. **`quill/core/settings.py` + `settings_specs.py`** integration.
5. **`quill/core/keymap.py`** updates (5 global hotkeys + 2 editor hotkeys).
6. **`quill/ui/verbosity_token_editor.py`** + tests (the centerpiece — gets UX iteration time). Build against a mocked engine.
7. **`quill/ui/verbosity_data_order.py`** + tests.
8. **`quill/ui/verbosity_prefs.py`** + tests (wires the editor and data-order dialog into the master/detail split). The 50-row table is the second-biggest UX risk.
9. **`quill/ui/verbosity_chord_editor.py`** + tests.
10. **`quill/ui/verbosity_library.py`** + tests (Library tab + per-row dropdown + QVP install flow).
11. **`quill/ui/keyboard_manager_dialog.py`** — Verbosity tab + per-chord overrides.
12. **`quill/ui/about_dialog.py`** + tests.
13. **`quill/ui/main_frame.py` + menu + status bar + quill-key wiring**. Re-baseline module-size budget AFTER wiring is complete.
14. **`quill/ui/setup_wizard_pages.py`** integration.
15. **`scripts/build_windows_distribution.py`** integration (verbosity_custom.json + qvps/).
16. **`quill/tools/module_size_budgets.json`** rebaseline.
17. **Docs**: PRD, user guide, CONTROL_REFERENCE, release notes, CHANGELOG.
18. **Version bump**: 0.7.0 → 0.7.1.

## Verification

- `pytest -q` — full suite green
- `ruff check . && ruff format --check .` — clean
- `mypy quill\core quill\io` — strict-typed modules pass
- `python -m quill.tools.quillin_lint quill\quillins_bundled --strict` — lint clean
- **Manual smoke (golden path)**:
  1. Launch QUILL, navigate to Preferences > Verbosity. Verify profile picker shows 4 ladder presets + Custom.
  2. Switch to Beginner → confirm announcements are verbose and full-context.
  3. Switch to Expert → confirm routine confirmations are silenced; errors still announced.
  4. Edit a channel checkbox → confirm "Modified" pill appears on the preset radio.
  5. Switch profiles → confirm spoken reset announcement.
  6. Type in the per-verb filter → confirm list narrows live.
  7. Select a verb → confirm detail pane shows current override + Edit button.
  8. Click Edit → confirm token editor opens in Simple view by default.
  9. Arrow through fragments → confirm each announces. Press Ctrl+R → confirm assembled template read aloud.
  10. Toggle to Advanced → confirm raw TextCtrl + Palette sidebar visible.
  11. Insert `{column}` from Palette → confirm read-only review field shows rendered output.
  12. Type `{garbage}` → confirm red flag, Save button disabled.
  13. Click Validate → confirm spoken "Validation: 1 token, 0 warnings, 1 error."
  14. Click Preview Announcement → confirm Prism speaks it, braille display shows it, status bar shows it. Confirm 250ms debounce.
  15. Press `Ctrl+Shift+Q` → confirm spoken "Quiet mode on" + `[Q]` badge.
  16. Press `Ctrl+Shift+B` → confirm spoken "Meeting mode on" + `[M]` badge.
  17. Press `Ctrl+Shift+M` → confirm Verbosity tab opens.
  18. Open Keyboard Manager → Verbosity tab → set `Ctrl+Shift+Right` to Quiet → press the chord → confirm speech silenced for just that action.
  19. Confirm `edit.unquote_lines` is on `Alt+Shift+Q` (was `Ctrl+Shift+Q`).
  20. Trigger a verb enough times to cross its mastery threshold → confirm spoken countdown at 3s → confirm auto-step-down.
  21. Save a custom template to Library → confirm it appears in the per-row dropdown.
  22. Install a sample QVP from file → confirm pack metadata spoken, templates added to Library with `kellyford.audio-descriptive-concise` ID.
  23. Apply a QVP template to a verb → confirm cross-verb token filter announcement.
  24. Open Help > About Quill → confirm 3-tab Notebook (Overview / Dependencies / Links).
- **Pre-commit hooks pass** (GATE-11 module size, dialog inventory, banned patterns, network egress, button contract).

## Risks

- **GATE-11 module-size budget**: `main_frame.py` will grow. Re-baseline only after edits are complete; do not preemptively bump.
- **Stash discipline**: do NOT use `git stash` at all during this rebuild — work directly on `main` with frequent commits, or use a topic branch if more than one session is collaborating.
- **Pre-existing modified files**: treat their current state as the new baseline and ADD verbosity hooks on top — do not try to reconstruct the lost diffs.
- **Parser surface area**: the token parser is the highest-risk module — type checks, filter allowlists, and locked-on-invalid all hinge on it. Build parser tests FIRST and aim for >95% coverage before any UI uses it.
- **QVP trust model expansion**: v1 has no signing. If a community need emerges for signed QVPs, that's a v2 follow-up. Don't pre-build signing infra.
- **Modal-dialog keyboard handling**: `Ctrl+T` and `Ctrl+Shift+P` inside the token editor must consume via `EVT_CHAR_HOOK`, not the global keymap. Test with NVDA + JAWS explicitly.
- **macOS VoiceOver compatibility**: `wx.CollapsiblePane` announces state changes on Windows SRs; macOS may differ. Test before release.

## Out of scope for v1

- QVP signing / cryptographic trust chain
- QVP auto-update via Quillin Hub
- QVP marketplace / browse UI
- Drag-and-drop template application
- Beginner Fade (verbose hints that gracefully quiet with mastery; separate from per-verb mastery ladder)
- Braille-adapted text (auto-clip verbose braille to 39 chars)
- Quiet Hours scheduler (silent auto-engage at 10pm; chime on exit)
- Announcement History (`QUILL key + Shift+H`)

These are documented as future enhancements; the v1 design supports them as extensions without breaking changes.