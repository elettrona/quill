# QUILL Native Accessible Table Studio

## Proposed Architecture, Research Findings, Accessibility Strategy, and Delivery Plan

**Project:** QUILL  
**Feature area:** Structured table creation and editing  
**Primary target:** Windows 11 with wxPython  
**Cross-platform goal:** Windows, macOS, and Linux where QUILL is supported  
**Primary accessibility goal:** A genuinely usable, efficient, and understandable table-editing experience for blind keyboard users  
**Status:** Proposed implementation plan  
**Related research repository:** https://github.com/Community-Access/wx-accessible-grid

---

# 1. Executive Summary

QUILL should provide a **Table Studio** that lets users create, inspect, edit, restructure, import, and safely regenerate Markdown and HTML tables without requiring them to type table syntax manually.

The defining challenge is not table parsing or serialization. The defining challenge is creating a grid that is:

- Fully keyboard operable.
- Predictable with screen readers.
- Understandable without visual spatial context.
- Fast enough for realistically sized tables.
- Capable of exposing row and column headers.
- Safe for cell editing, insertion, deletion, movement, and structural changes.
- Native where practical.
- Cross-platform in its data model and core experience.
- Extensible with a small platform accessibility hook where necessary.

The recommended design is a **two-layer native table experience**:

1. A spatial grid for orientation, movement, selection, and structural commands.
2. A separate native cell-details and editing region for reliable multiline editing and precise accessibility.

On Windows, QUILL should pursue a **custom native UI Automation provider** layered over a visual `wx.grid.Grid`, potentially implemented through a small C or C++ extension. This is not considered excessive for QUILL. Accessibility is central to the product, and native grid semantics are difficult to achieve through wxPython alone.

The architecture must also provide a **Linear Table View** using conventional native controls. This is not a lesser or emergency accessibility mode. It is an alternate interaction model for users who prefer sequential exploration or whose assistive technology behaves poorly with a spatial grid.

The implementation should retain the strongest lessons from `wx-accessible-grid` while avoiding a required WebView dependency.

---

# 2. Product Vision

A user should be able to place the caret inside a Markdown or HTML table and press F2.

QUILL should open a Table Studio that:

- Identifies the table.
- Announces its dimensions.
- Places the user on the corresponding cell.
- Reports row and column headers.
- Lets the user move cell by cell.
- Lets the user edit the current cell in a native multiline field.
- Lets the user add, remove, reorder, and duplicate rows and columns.
- Lets the user designate row and column headers.
- Lets the user convert selected text or imported data into a table.
- Lets the user preview the generated source.
- Replaces the original source only after validation.
- Makes the entire change one undoable transaction.
- Returns focus to the corresponding table cell in the document.

The experience should feel closer to a purpose-built accessible spreadsheet editor than to editing punctuation and tags.

---

# 3. Guiding Principles

## 3.1 Accessibility is an architectural requirement

Accessibility cannot be added after the grid is complete.

The active-cell model, focus behavior, header relationships, editing workflow, selection model, announcements, and event generation must be designed together.

## 3.2 The model is the source of truth

The visual grid must not own the data.

Every edit must pass through the table model. The model validates, normalizes, accepts, or rejects the edit. The grid then reflects the model’s authoritative result.

## 3.3 Focus and selection are different concepts

A table has:

- One active cell.
- Zero or more selected cells, rows, or columns.
- Possibly a selected rectangular range.

The implementation must not confuse the active cell with selection.

## 3.4 A cell needs complete context

A screen-reader user must be able to determine:

- Table name or purpose.
- Row position.
- Column position.
- Row header.
- Column header.
- Cell value.
- Editable or read-only status.
- Whether the cell is selected.
- Whether the cell participates in a merged region.
- Whether the cell contains complex or multiline content.

## 3.5 The grid should navigate; the editor should edit

The grid is primarily for:

- Orientation.
- Movement.
- Selection.
- Structural operations.
- Finding relationships.

The native details region is primarily for:

- Reading complete content.
- Editing multiline content.
- Validation.
- Cell-specific properties.
- Richer content controls.

## 3.6 Every transformation must be safe and reversible

- Cancel must leave the document unchanged.
- Generated Markdown or HTML must be reparsed before commit.
- The reparsed structure must match the intended model.
- The replacement must be one undo step.
- Source surrounding the table must remain unchanged.

## 3.7 Native controls should be preferred

QUILL should use native wx controls wherever they provide dependable semantics.

Custom accessibility should be introduced only where the platform does not expose the required table relationships.

## 3.8 Cross-platform does not mean lowest-common-denominator

The model, command system, parsers, serializers, and dialog layout should be cross-platform.

Platform-specific accessibility bridges are acceptable when they materially improve the experience.

---

# 4. Lessons Learned from `wx-accessible-grid`

The repository at `Community-Access/wx-accessible-grid` is an important research and behavioral reference.

Its current implementation uses a local WebView with a semantic ARIA table. It does not depend on a remote web service, but the accessibility surface is still HTML, ARIA, JavaScript, DOM focus, and the browser accessibility stack.

## 4.1 Keep the model independent from the grid

The repository’s `GridModel` defines:

- Columns.
- Row count.
- Display values.
- Edit values.
- Per-cell editability.
- Choice values.
- Row labels.
- Validation.
- Persistence.
- Deletion.

The grid asks the model to change data and displays the model’s accepted result.

### QUILL decision

QUILL must use the same separation.

A `TableDocumentModel` will own:

- Logical table structure.
- Cell values.
- Headers.
- Alignment.
- Spans.
- Attributes.
- Source metadata.
- Stable row, column, and cell identifiers.
- Validation rules.
- Undo transaction data.

The visual grid will only present and manipulate this model.

## 4.2 Real focus is more dependable than a visual cursor

The repository originally used `aria-activedescendant` and later changed to real DOM focus on the active cell through a roving `tabindex`.

The practical lesson is broader than ARIA:

> The platform’s actual accessible focus should follow the logical table cursor.

### QUILL decision

The native Windows implementation must expose the active cell as the focused UI Automation fragment.

The visible focus rectangle, internal active-cell coordinates, and screen-reader focus must never disagree.

## 4.3 Header context must be explicit

The repository discovered that relying on implicit table header computation was not sufficient across screen readers.

It composes each cell’s accessible name from:

- Row header.
- Column header.
- Value.
- Editor type.

### QUILL decision

The native provider must expose true row and column header relationships where the platform supports them.

QUILL should also have a configurable spoken-cell formatter as a controlled fallback.

Examples:

- `Arizona, Population, 7,431,344, edit box`
- `Row 4, Notes, Follow up next week, multiline edit`
- `Total, Revenue, $92,500, read only`

## 4.4 Editor type should be discoverable

The repository appends terms such as:

- Edit box.
- Combo box.
- Checkbox.
- Slider.
- Stepper.
- Read only.

### QUILL decision

The current cell should communicate its editing behavior.

For Table Studio, likely cell modes include:

- Text.
- Multiline text.
- Choice.
- Checkbox or boolean.
- Numeric.
- Date.
- Read only.
- Complex source content.

The initial release may expose most imported document cells as multiline text, but the architecture should support typed cells.

## 4.5 Edits should round-trip through the model

The repository allows the model to normalize or reject an edit and then announces the authoritative result.

### QUILL decision

The same pattern is mandatory.

Example:

1. The user edits a Markdown table cell.
2. The model escapes or normalizes unsafe pipe characters.
3. The serializer determines the correct source representation.
4. The model returns the accepted display value.
5. QUILL announces the accepted result.

On rejection:

- Explain why.
- Keep the editing field available.
- Do not silently discard input.
- Do not move focus away unexpectedly.

## 4.6 Native menus are highly valuable

The repository uses native `wx.Menu` context menus even though its grid is rendered in a WebView.

### QUILL decision

All table context menus should be native.

Possible menu commands:

- Edit Cell.
- Insert Row Above.
- Insert Row Below.
- Insert Column Before.
- Insert Column After.
- Delete Row.
- Delete Column.
- Move Row Up.
- Move Row Down.
- Move Column Left.
- Move Column Right.
- Set as Header.
- Clear Cell.
- Cell Properties.
- Table Properties.

## 4.7 Announcements must be intentional

The repository separates normal focus announcements from assertive status announcements.

It reserves assertive messaging for:

- Selection changes.
- Errors.
- Grid entry.
- Important state changes.

### QUILL decision

QUILL should use a centralized table-announcement service with configurable verbosity.

Normal navigation should avoid duplicate speech.

Operations such as deletion, selection, conversion, validation failure, and structural change should be announced explicitly.

## 4.8 Range selection needs its own mental model

The repository distinguishes:

- Bulk row selection.
- Rectangular cell-range selection.
- The active cell.

### QUILL decision

QUILL should explicitly model:

- Active cell.
- Selected cell.
- Selected rectangular range.
- Selected row or rows.
- Selected column or columns.
- Entire table selection.

The interface must announce which type of selection exists.

## 4.9 Full re-rendering can break focus

The repository replaces only the table body for some updates so the table and focus state survive.

### QUILL decision

The native grid should perform incremental refreshes.

After structural changes:

- Preserve stable cell identity where possible.
- Move focus to a deterministic cell.
- Emit one structure-changed event.
- Avoid destroying and recreating the entire widget unless necessary.

## 4.10 Documentation must track implementation

The repository’s README and current implementation have diverged in areas such as paging.

### QUILL decision

Table Studio must maintain:

- Architecture documentation.
- Interaction documentation.
- Keyboard reference.
- Accessibility behavior reference.
- Screen-reader test matrix.
- Source-format support matrix.

Tests should detect behavior drift where practical.

## 4.11 Web semantics are useful as a reference even if QUILL stays native

The ARIA grid implementation provides a valuable behavioral benchmark:

- One active cell.
- Explicit coordinates.
- Explicit headers.
- Explicit editability.
- Keyboard movement.
- Selection semantics.
- Announced validation.
- Focus restoration.

### QUILL decision

The repository should be treated as:

- A research source.
- A comparison implementation.
- A behavior checklist.
- Potential inspiration for automated interaction tests.

It should not be a required runtime dependency unless native work proves unworkable.

---

# 5. Recommended Architecture

## 5.1 Architecture overview

The proposed architecture has five layers:

1. Document integration.
2. Format-neutral table model.
3. Native Table Studio user interface.
4. Platform accessibility adapter.
5. Format-specific parsers and serializers.

```text
QUILL Document Buffer
        |
        v
Table Locator and Source Mapper
        |
        v
Format Adapter: Markdown or HTML
        |
        v
Format-Neutral TableDocumentModel
        |
        +-------------------------------+
        |                               |
        v                               v
Native wxPython Table Studio      Platform Accessibility Adapter
        |                               |
        v                               v
wx.grid.Grid + Details Region     UIA / NSAccessibility / AT-SPI
        |
        v
Validated Serializer and Transactional Replacement
```

## 5.2 Core rule

The platform accessibility layer must never contain document logic.

It should request information from the shared table model and report interaction events back to the controller.

---

# 6. Format-Neutral Data Model

A representative model:

```text
TableDocumentModel
    document_format
    source_range
    original_source
    caption
    summary
    rows
    columns
    header_configuration
    alignment
    attributes
    formatting_preferences
    source_metadata
    selected_cell_id
    validation_state

TableColumn
    column_id
    label
    alignment
    width_hint
    is_header
    data_type
    attributes
    source_metadata

TableRow
    row_id
    label
    is_header
    cells
    attributes
    source_metadata

TableCell
    cell_id
    row_id
    column_id
    content
    display_content
    content_kind
    editable
    row_span
    column_span
    attributes
    source_metadata
```

## 6.1 Stable identifiers

Rows, columns, and cells need stable temporary identifiers.

Indexes change when rows or columns are inserted, deleted, or moved.

Stable identifiers allow QUILL to:

- Restore focus after a structural operation.
- Map a dialog cell back to source.
- Compare generated and reparsed tables.
- Preserve cell attributes.
- Maintain selection.
- Produce understandable error messages.

Identifiers must never be written into the document.

## 6.2 Model commands

All structural mutations should be command objects or transaction-safe model operations.

Examples:

- `SetCellContentCommand`
- `InsertRowCommand`
- `DeleteRowsCommand`
- `MoveRowCommand`
- `InsertColumnCommand`
- `DeleteColumnsCommand`
- `MoveColumnCommand`
- `SetHeaderRowCommand`
- `SetHeaderColumnCommand`
- `SetCellSpanCommand`
- `SplitCellCommand`
- `MergeCellsCommand`
- `SetAlignmentCommand`
- `ImportTableCommand`
- `TransposeTableCommand`

This supports testing and future model-level undo inside the dialog.

---

# 7. Native Table Studio Layout

The Table Studio should be modal for the initial release.

It should be resizable and remember its last useful size.

Recommended regions:

1. Table summary.
2. Spatial grid.
3. Current-cell summary.
4. Native cell-content editor.
5. Row and column actions.
6. Table properties.
7. Import and conversion actions.
8. Generated-source preview.
9. OK and Cancel.

Avoid confusing nested splitter controls if they cause poor screen-reader output.

A carefully managed `wx.SplitterWindow` may be used only if its accessibility is validated. A normal sizer-based layout is preferred.

---

# 8. Spatial Grid Experience

## 8.1 Visual control

Use `wx.grid.Grid` for:

- Visual table layout.
- Native scrolling.
- Row and column sizing.
- Keyboard event capture.
- Mouse interaction.
- Selection visuals.
- High-DPI rendering.
- Platform theme integration.

The native accessibility adapter will expose semantic virtual cells.

## 8.2 Initial focus

When editing an existing table:

- Focus the cell corresponding to the document caret.
- If exact mapping is unavailable, focus the first data cell.
- Announce the table dimensions and current cell.

Example:

> Edit Table. 8 rows and 4 columns. Row 3, column Name, Taylor Arndt.

When creating a new table:

- Focus the first cell.
- Announce the dimensions and header configuration.

## 8.3 Movement

Recommended commands:

- Arrow keys: Move one cell.
- Ctrl+Arrow: Move to first or last cell in the current direction.
- Home: First column in row.
- End: Last column in row.
- Ctrl+Home: First cell.
- Ctrl+End: Last cell.
- Page Up and Page Down: Move by a configurable number of rows.
- Tab and Shift+Tab: Move forward or backward through editable cells.
- F6: Move between major Table Studio regions.
- Escape: Cancel editing or return from a subcontrol; it should not immediately close the whole dialog while an edit is active.

## 8.4 Navigation announcements

Standard mode should generally announce:

- Row header.
- Column header.
- Cell value.
- Position when useful.
- Editable or read-only state when it changes.

Detailed mode may add:

- Row and column numbers.
- Selection state.
- Span information.
- Data type.
- Blank state.
- Header-cell role.

Concise mode may announce:

- Column header and value on horizontal movement.
- Row header and value on vertical movement.

## 8.5 Blank cells

Use explicit language:

> Blank.

Do not allow silence to be ambiguous between:

- Blank cell.
- Failed focus.
- Unavailable content.
- Screen-reader event failure.

---

# 9. Native Cell Editing Region

## 9.1 Primary editing model

Pressing F2 or Enter from the grid moves focus to a native multiline field:

> Cell content — Row 3, Column Description

This field should be a `wx.TextCtrl` with multiline behavior.

The user may:

- Review all cell content.
- Edit by character, word, line, or paragraph.
- Paste content.
- Use standard screen-reader reading commands.
- Preserve multiline content where the target format supports it.

## 9.2 Commit and cancel

Recommended commands:

- Ctrl+Enter: Commit and return to the grid.
- Ctrl+Shift+Enter: Commit and move to the next row in the same column.
- Alt+Right Arrow or a button: Commit and move to the next column.
- Escape: Cancel the cell edit and return to the grid.
- Tab: Move to related cell-property controls, not silently commit unless configured.

The commands must be configurable.

## 9.3 Immediate versus deferred model updates

Recommended default:

- The cell editor updates a temporary cell draft.
- Commit validates the draft.
- Accepted content updates the table model.
- Cancel restores the pre-edit value.

A configurable live-update mode may be added later.

## 9.4 Cell type controls

The details region may expose:

- Content type.
- Alignment.
- Header status.
- Read-only status where applicable.
- Checkbox state for task-like HTML tables.
- Numeric formatting in future versions.
- Span information for HTML.

The initial Markdown release can keep most cells as text.

---

# 10. Linear Table View

## 10.1 Purpose

The Linear Table View presents the same model through conventional sequential controls.

It should be available through:

- A toggle in Table Studio.
- A configurable default.
- A keyboard command.
- An automatic fallback if the spatial provider fails.

## 10.2 Proposed layout

A native list of rows:

> Row 3 of 8: Arizona

Selecting a row exposes a native list of cells:

- State: Arizona
- Population: 7,431,344
- Capital: Phoenix
- Notes: Blank

Selecting a cell exposes the same multiline Cell Content editor.

## 10.3 Why this is not a lesser mode

Some users think spatially and prefer cell-by-cell navigation.

Other users prefer:

- Sequential row review.
- Form-like editing.
- Reduced speech complexity.
- Simpler selection.
- Easier long-cell review.

Both views manipulate the same model.

## 10.4 Synchronization

Switching views must preserve:

- Active cell.
- Selected rows or cells where meaningful.
- Unsaved cell draft.
- Scroll context.
- Current operation state.

---

# 11. Windows Accessibility Adapter

## 11.1 Objective

Expose the visual `wx.grid.Grid` as a true Microsoft UI Automation table or grid.

## 11.2 Recommended implementation

Build a small native extension in C or C++.

Preferred implementation technologies:

- C++17 or newer.
- Microsoft UI Automation provider APIs.
- pybind11, CPython extension API, or a narrow C ABI.
- Minimal dependencies.
- Separate platform module.
- Automated build through QUILL’s packaging process.

## 11.3 Required UIA patterns

Grid provider:

- `IGridProvider`
- `ITableProvider`
- `ISelectionProvider`
- `IScrollProvider` where practical

Virtual cell provider:

- `IGridItemProvider`
- `ITableItemProvider`
- `IValueProvider`
- `ISelectionItemProvider` where appropriate
- `IInvokeProvider` for activation where useful
- `IRangeValueProvider` for future typed numeric cells
- `IToggleProvider` for checkbox cells

## 11.4 Required cell properties

Every accessible cell should expose:

- Name.
- Control type.
- Automation ID.
- Row.
- Column.
- Row span.
- Column span.
- Containing grid.
- Header relationships.
- Value.
- Read-only state.
- Focused state.
- Selected state.
- Offscreen state.
- Bounding rectangle.
- Help text where useful.

## 11.5 Virtual child strategy

The table may contain many cells.

The native provider should expose virtual child elements without requiring one wx window per cell.

The provider maps:

```text
cell_id -> row_id + column_id -> current model coordinates
```

The provider should generate cell fragments on demand and retain stable identities during the dialog lifetime.

## 11.6 Focus synchronization

When the user moves within `wx.grid.Grid`:

1. QUILL updates the active cell in the model/controller.
2. The UIA provider marks that cell as keyboard focused.
3. QUILL raises a UIA focus-changed event.
4. The screen reader queries the cell and its headers.
5. The visual focus rectangle remains on the same cell.

When a screen reader invokes a cell:

1. The provider requests that QUILL focus that cell.
2. QUILL updates the visual grid.
3. The provider confirms focus.
4. F2 or Invoke opens the native Cell Content field.

## 11.7 Structure events

Raise events for:

- Row inserted.
- Row deleted.
- Column inserted.
- Column deleted.
- Table reset.
- Header configuration changed.
- Merge or split changed.
- View switched.

Events must be batched to prevent excessive screen-reader chatter.

## 11.8 Property events

Raise events for:

- Cell value changed.
- Selection changed.
- Read-only state changed.
- Header name changed.
- Checked state changed.
- Validation state changed.

## 11.9 `WM_GETOBJECT`

The native hook will likely need to respond to `WM_GETOBJECT` for the grid’s HWND and return the root UIA provider.

This must be isolated from the rest of QUILL so that:

- The provider cannot crash the editor process through unchecked callbacks.
- Python object lifetimes are managed safely.
- Calls are marshaled to the wx main thread when necessary.
- Screen-reader queries never mutate document data.

## 11.10 Threading

UIA may call provider methods from threads that are not the wx UI thread.

The adapter must:

- Use thread-safe immutable snapshots for read-only properties where possible.
- Marshal focus or mutation requests to the main wx thread.
- Avoid blocking UIA calls on long parser or serializer work.
- Prevent reentrant model mutation.

## 11.11 Failure containment

If the UIA bridge fails:

- The visual grid remains usable.
- The Linear Table View remains available.
- QUILL logs diagnostics.
- The dialog does not crash.
- The user receives a concise, nontechnical message only when necessary.

---

# 12. macOS Accessibility Strategy

The cross-platform model and native details region remain the same.

For macOS, investigate:

- `NSAccessibilityGridRole`
- `NSAccessibilityRowRole`
- `NSAccessibilityCellRole`
- Row and column header relationships.
- Focused UI element.
- Selected rows and cells.

Possible implementation approaches:

- Native Objective-C++ bridge.
- PyObjC bridge if packaging and reliability are acceptable.
- wxWidgets accessibility support where adequate.
- Linear Table View as a guaranteed baseline.

The macOS implementation should be evaluated with VoiceOver from the beginning.

Lessons from the WebView repository show that VoiceOver may intercept navigation differently from Windows screen readers. Native testing must include VoiceOver interaction modes and focus behavior.

---

# 13. Linux Accessibility Strategy

For Linux, evaluate:

- AT-SPI table interfaces.
- GTK accessibility exposure from wxWidgets.
- Orca behavior.
- Native grid support available through the active wxGTK version.

Possible approaches:

- Rely on wxGTK if it exposes adequate table semantics.
- Add a small AT-SPI bridge.
- Use Linear Table View as the first fully supported experience.
- Introduce the spatial grid only after Orca testing.

The format-neutral model must not depend on any platform accessibility API.

---

# 14. `wx.Accessible` Spike

Before the compiled UIA bridge is finalized, QUILL should test how far `wx.Accessible` can go.

The spike should attempt to expose:

- Grid name.
- Focused cell.
- Cell role.
- Cell value.
- Row and column context in the accessible name.
- Selection state.
- Navigation.
- Value changes.

The result should be tested with:

- NVDA.
- JAWS.
- Narrator.

Possible outcomes:

1. `wx.Accessible` is sufficient for a usable initial release.
2. It is useful as a fallback but not sufficient for full table semantics.
3. It causes inconsistent behavior and should be bypassed by the UIA provider.

The plan assumes outcome 2 is most likely.

---

# 15. Table Identification in the Document

## 15.1 Context-sensitive F2

Recommended behavior:

- Caret in a list: open List Studio.
- Caret in a table: open Table Studio.
- Selection resembling table data: open Table Studio import or conversion.
- Selection resembling list data: open List Studio conversion.
- No structure or selection: open a small structured-content chooser or follow the user’s configured default.

## 15.2 Markdown table detection

Use the active Markdown parser or a grammar-aware table parser.

Do not rely on regular expressions alone.

The locator should determine:

- Full table source range.
- Header row.
- Delimiter row.
- Alignment markers.
- Cell source ranges.
- Escaped pipes.
- Inline markup.
- Line ending style.
- Surrounding indentation.
- Whether the syntax is supported by the active Markdown profile.

## 15.3 HTML table detection

Use a standards-compliant HTML parser or QUILL’s DOM.

Resolve the caret to the nearest:

- `td`
- `th`
- `tr`
- `table`

Then identify the containing table and map source ranges.

Preserve:

- `caption`
- `thead`
- `tbody`
- `tfoot`
- `th`
- `td`
- `scope`
- `headers`
- `id`
- `rowspan`
- `colspan`
- Safe global attributes.
- Existing section structure.

---

# 16. Markdown Table Capabilities

Initial support should include:

- Standard pipe tables.
- Optional leading and trailing pipes.
- Header row.
- Alignment markers.
- Escaped pipe characters.
- Inline Markdown.
- Blank cells.
- Multiline logical content where serialized safely.
- CRLF and LF.
- Source-style preservation where practical.

## 16.1 Markdown limitations

Typical Markdown tables do not support:

- True row spans.
- True column spans.
- Multiple header rows.
- Complex block content.
- Nested block structures in cells.

QUILL must clearly distinguish:

- Unsupported by the active Markdown profile.
- Unsupported by the current Table Studio release.
- Preserved as opaque source.
- Convertible through an HTML fallback.

## 16.2 Markdown multiline policy

Possible configurable strategies:

- Convert internal line breaks to `<br>`.
- Join lines with spaces.
- Preserve inline HTML.
- Refuse conversion when unsafe.
- Use an HTML table fallback.

Recommended default:

- Preserve existing representation.
- For new multiline content, ask or use the active Markdown profile.
- Never silently discard line breaks.

---

# 17. HTML Table Capabilities

Initial support should include:

- Captions.
- Header rows.
- Header columns.
- Multiple header rows.
- `thead`, `tbody`, and `tfoot`.
- Row and column spans.
- `scope`.
- `headers` and `id` relationships.
- Safe attributes.
- Inline content.
- Basic block content preservation.
- Table descriptions or summaries where appropriate.

## 17.1 Header authoring

Table Studio should offer understandable controls:

- First row contains column headers.
- First column contains row headers.
- Selected row is a header row.
- Selected column is a header column.
- Advanced header associations.

For complex tables, QUILL should support explicit `headers` and `id` relationships through a guided advanced dialog.

## 17.2 Span editing

Recommended release strategy:

### Initial release

- Parse and preserve existing spans.
- Announce spans.
- Prevent operations that would corrupt spans.
- Permit editing content within a spanned cell.
- Offer a read-only explanation when a structural action is unavailable.

### Later release

- Merge selected rectangular cells.
- Split a merged cell.
- Adjust row span.
- Adjust column span.
- Repair invalid associations.

---

# 18. Creating New Tables

## 18.1 Blank table

The user chooses:

- Number of rows.
- Number of columns.
- Header-row option.
- Header-column option.
- Caption.
- Markdown or HTML profile.

Recommended defaults:

- 2 columns.
- 2 data rows.
- First row is a header.
- No header column.
- Focus first header cell.

## 18.2 Insert command

Possible menu:

**Insert → Table…**

F2 outside structured content may also create a table according to user settings.

## 18.3 Dimension changes

Users can add rows and columns after creation, so the initial dimension dialog must remain simple.

---

# 19. Converting Selected Text to a Table

Supported interpretations:

- Tab-delimited.
- Comma-delimited.
- Semicolon-delimited.
- Pipe-delimited.
- One paragraph per row.
- Fixed number of columns.
- Key and value pairs.
- Automatically detect.
- Custom separator.

The import preview must display:

- Detected rows.
- Detected columns.
- Proposed header row.
- Blank cells.
- Inconsistent row widths.
- Quoting behavior.
- Escaped separators.
- Truncated preview warnings.

No ambiguous conversion should commit without review.

---

# 20. Import from Clipboard or File

## 20.1 Sources

- Clipboard.
- Multiline paste field.
- Plain text.
- CSV.
- TSV.
- Markdown table.
- HTML table.
- Future spreadsheet ranges.

## 20.2 CSV and TSV

Unlike the initial List Studio plan, Table Studio should treat CSV and TSV as real structured formats.

Use Python’s `csv` module or an equivalent standards-aware parser.

Support:

- Quoted fields.
- Embedded delimiters.
- Embedded line breaks.
- Escaped quotes.
- Configurable encoding.
- Header-row detection.
- Delimiter detection.
- Preview.

## 20.3 File import safety

- Do not modify the source file.
- Detect binary or unsupported input.
- Show encoding when uncertain.
- Never silently drop columns.
- Warn when rows have inconsistent widths.
- Allow filling missing cells with blanks.
- Allow rejecting malformed rows.

---

# 21. Row Operations

Required actions:

- Add row above.
- Add row below.
- Duplicate row.
- Delete row.
- Delete selected rows.
- Move row up.
- Move row down.
- Move selected rows as a group.
- Clear row contents.
- Convert row to header.
- Convert header row to data row.
- Select row.
- Select range of rows.

After every operation:

- Preserve focus logically.
- Announce the result.
- Update row numbers.
- Update header relationships.
- Refresh source preview.

---

# 22. Column Operations

Required actions:

- Add column before.
- Add column after.
- Duplicate column.
- Delete column.
- Delete selected columns.
- Move column left.
- Move column right.
- Move selected columns as a group.
- Clear column contents.
- Convert column to row-header column.
- Set alignment.
- Rename conceptual column header through its header cell.
- Select column.
- Select range of columns.

Column operations must account for:

- Existing spans.
- Header associations.
- Markdown alignment row.
- HTML `headers` references.

---

# 23. Cell and Range Operations

Required actions:

- Edit cell.
- Clear cell.
- Copy cell.
- Paste into cell.
- Fill selected cells.
- Select rectangular range.
- Copy range as TSV.
- Paste rectangular range.
- Delete range contents.
- Move range where safe.
- Set alignment for selected cells where supported.
- Mark selected cell as header in HTML.
- Merge and split in a later release.

## 23.1 Paste matrix behavior

When pasted content contains rows and columns:

- If one cell is active, fill outward from that cell.
- If a matching range is selected, replace the range.
- If dimensions differ, preview expansion or truncation.
- Offer to add rows or columns when needed.
- Never silently discard pasted cells.

---

# 24. Table Properties

Properties should include:

- Caption.
- Accessible description.
- Header-row configuration.
- Header-column configuration.
- Alignment.
- Source formatting.
- Markdown table profile.
- HTML section structure.
- Width hints.
- Border or presentation attributes only where semantically appropriate.
- Generated-source options.
- Accessibility validation.

Advanced HTML properties may include:

- `scope`.
- `headers`.
- `id`.
- `abbr`.
- `colspan`.
- `rowspan`.
- Safe classes and data attributes.

---

# 25. Accessibility Validation

Table Studio should include a **Check Table Accessibility** command.

Checks may include:

- Missing column headers.
- Missing row headers for complex tables.
- Blank header cells.
- Duplicate header labels.
- Empty table.
- Excessively large or complex table.
- Inconsistent row lengths.
- Invalid spans.
- Broken `headers` references.
- Missing IDs referenced by cells.
- Header cells without scope or associations.
- Caption or nearby context concerns.
- Markdown feature incompatibilities.
- Cells containing potentially inaccessible generated controls.

Validation should classify findings as:

- Error.
- Warning.
- Suggestion.

The user should be able to move from a finding to the relevant cell or property.

---

# 26. Generated Source Preview

Provide a read-only multiline source field.

Labels:

- Generated Markdown.
- Generated HTML.

Users should be able to:

- Navigate the source.
- Copy it.
- Review pipes and alignment.
- Review tags and attributes.
- Review spans.
- Review header associations.
- Compare before and after.

Optional future feature:

- Source difference view.

The preview must never execute HTML.

---

# 27. Commit and Document Replacement

When the user activates OK:

1. Commit any active cell draft.
2. Validate the table model.
3. Serialize the model.
4. Reparse the generated source.
5. Compare the reparsed semantic structure with the model.
6. Verify that the original source range has not changed externally.
7. Replace the exact original range or insertion point.
8. Perform the replacement in one editor transaction.
9. Refresh syntax highlighting.
10. Refresh previews and document structure.
11. Mark the document modified.
12. Map the active cell back to the new source.
13. Restore the caret near that cell.
14. Announce completion.

Example:

> Table updated. 8 rows and 4 columns. Row 3, column Name selected.

On validation failure:

- Keep the dialog open.
- Leave the document unchanged.
- Focus an accessible error summary.
- Preserve the user’s edits.
- Keep generated source available for review.

---

# 28. Undo and Redo

## 28.1 Document-level undo

The complete Table Studio operation is one undo step.

## 28.2 Dialog-level undo

A later release should support undo and redo inside Table Studio for:

- Cell edits.
- Row insertion.
- Column insertion.
- Movement.
- Deletion.
- Header changes.
- Import.
- Merge and split.

The command-based model is designed to support this.

---

# 29. Keyboard Command Proposal

All commands must also be available through native menus or buttons.

## Navigation

- Arrow keys: Move one cell.
- Ctrl+Arrow: Move to edge.
- Home and End: First or last column.
- Ctrl+Home and Ctrl+End: First or last cell.
- Page Up and Page Down: Move several rows.
- Tab and Shift+Tab: Next or previous editable cell.
- F6: Move between major regions.

## Editing

- F2 or Enter: Edit cell in native Cell Content field.
- Ctrl+Enter: Commit edit.
- Escape: Cancel edit.
- Printable typing from the grid: Configurable type-to-replace behavior.

## Selection

- Shift+Arrow: Extend rectangular selection.
- Shift+Space: Select row.
- Ctrl+Space: Select column.
- Ctrl+A: Configurable select table or select all rows.
- Escape: Clear selection when not editing.

## Structure

- Alt+Up and Alt+Down: Move row.
- Alt+Left and Alt+Right: Move column.
- Ctrl+Insert: Insert row below.
- Ctrl+Shift+Insert: Insert column after.
- Delete: Clear cells or delete selected rows or columns according to selection type.
- Shift+F10 or Context Menu key: Open native context menu.

Potential conflicts must be tested with screen readers before finalizing.

---

# 30. Configurability

Table Studio should follow the same rich configuration philosophy as List Studio.

Settings categories:

- General.
- Navigation.
- Editing.
- Announcements.
- Selection.
- Import.
- Markdown.
- HTML.
- Headers.
- Validation.
- Preview.
- Platform accessibility.
- Keyboard commands.
- Confirmations.

## 30.1 Announcement verbosity

Profiles:

- Concise.
- Standard.
- Detailed.
- Custom.

## 30.2 Spoken cell components

Allow independent control of:

- Row number.
- Column number.
- Row header.
- Column header.
- Value.
- Blank state.
- Editability.
- Data type.
- Selection state.
- Span information.
- Table name.

## 30.3 View preference

Options:

- Spatial Grid.
- Linear Table View.
- Remember last view.
- Ask for complex tables.
- Automatically use Linear View if platform semantics fail.

## 30.4 Editing preference

Options:

- Always use separate multiline editor.
- Use in-cell editor for short text.
- Type-to-replace.
- Enter begins editing.
- Enter moves down.
- Tab commits.
- Ctrl+Enter commits.

Recommended default:

> Separate multiline editor for all document cells.

## 30.5 Safety confirmations

Configurable confirmations for:

- Delete row.
- Delete column.
- Delete multiple rows.
- Delete multiple columns.
- Clear a selected range.
- Replace table during import.
- Drop incompatible attributes.
- Flatten spans.
- Convert HTML table to Markdown.
- Convert a complex table to a simpler structure.

Information-loss confirmations should not be fully suppressible.

---

# 31. Cross-Platform Feature Levels

## Level A: Shared everywhere

- Table model.
- Markdown parser and serializer.
- HTML parser and serializer.
- Import.
- Generated-source preview.
- Native details editor.
- Linear Table View.
- Commands.
- Validation.
- Transactional replacement.
- Automated model tests.

## Level B: Native spatial grid

- `wx.grid.Grid`.
- Keyboard movement.
- Visual selection.
- Row and column operations.
- Native context menus.

## Level C: Platform semantic grid

- Windows UIA provider.
- macOS accessibility bridge.
- Linux AT-SPI or adequate wxGTK exposure.

QUILL may ship Level A and B on a platform before Level C only if the Linear Table View is fully accessible and the limitations are clearly documented.

---

# 32. Prototype and Research Plan

## Spike 1: Existing `wx.grid.Grid`

Build a small test harness containing:

- 20 rows.
- 5 columns.
- Header row.
- Header column.
- Blank cells.
- Long cells.
- Read-only cells.
- Editable cells.
- Selection.
- Insert and delete operations.

Test unmodified behavior with:

- NVDA.
- JAWS.
- Narrator.

Record:

- Role.
- Header announcements.
- Focus behavior.
- Cell coordinates.
- Selection behavior.
- Editing behavior.
- Braille output.

## Spike 2: `wx.Accessible`

Add a custom accessible object.

Test whether it can reliably expose:

- Active cell.
- Complete cell name.
- Value.
- Focus.
- Selection.
- Structural events.

## Spike 3: Minimal UIA provider

Implement only:

- Grid root.
- Row count.
- Column count.
- `GetItem`.
- Cell row and column.
- Cell value.
- Focus.
- Header names.

Validate with Accessibility Insights and screen readers.

## Spike 4: Native Cell Content region

Test focus movement:

- Grid to editor.
- Editor to grid.
- Commit.
- Cancel.
- Validation error.
- Structural update.
- Dialog close.

## Spike 5: Linear Table View

Build the alternate view and compare efficiency.

## Spike 6: WebView reference comparison

Use `wx-accessible-grid` as a benchmark for:

- Navigation speech.
- Header context.
- Selection announcements.
- Editing confirmation.
- Context menu behavior.

The goal is not to adopt the WebView. The goal is to ensure the native implementation does not regress in user experience.

---

# 33. Automated Testing Strategy

## 33.1 Model tests

Test:

- Stable identities.
- Insert row.
- Delete row.
- Move row.
- Insert column.
- Delete column.
- Move column.
- Cell edits.
- Header changes.
- Spans.
- Selection.
- Validation.
- Import.
- Conversion.
- Serialization.

## 33.2 Markdown fixtures

Include:

- Basic table.
- Leading and trailing pipes.
- No outer pipes.
- Alignment.
- Escaped pipes.
- Inline formatting.
- Blank cells.
- Long cells.
- CRLF.
- LF.
- Malformed delimiter rows.
- Inconsistent columns.
- Unsupported multiline cases.
- Tables near lists or code blocks.

## 33.3 HTML fixtures

Include:

- Simple table.
- Caption.
- Header row.
- Header column.
- Multiple header rows.
- `thead`, `tbody`, `tfoot`.
- `scope`.
- `headers` and `id`.
- `rowspan`.
- `colspan`.
- Safe attributes.
- Nested inline markup.
- Complex cell content.
- Malformed structures.
- Comments and whitespace.

## 33.4 Import fixtures

Include:

- CSV.
- TSV.
- Quoted commas.
- Embedded line breaks.
- Empty cells.
- Inconsistent rows.
- Unicode.
- UTF-8 BOM.
- UTF-16.
- Windows-1252.
- Large imports.
- Clipboard matrices.

## 33.5 Native accessibility tests

Where possible, create Windows UIA automation tests for:

- Grid pattern.
- Table pattern.
- Cell lookup.
- Row and column values.
- Header relationships.
- Focus.
- Value changes.
- Selection.
- Structure changes.
- Bounding rectangles.
- Offscreen state.

## 33.6 Manual screen-reader matrix

Windows:

- NVDA.
- JAWS.
- Narrator.

macOS:

- VoiceOver.

Linux:

- Orca.

Test:

- Speech.
- Braille.
- Keyboard-only use.
- High contrast.
- 200% and higher scaling.
- Long tables.
- Blank cells.
- Multiline cells.
- Selection.
- Context menus.
- Validation.
- Import.
- Focus restoration.
- Dialog closure.
- View switching.

---

# 34. Performance Requirements

Targets:

- Open a 100-row by 20-column table without a noticeable freeze.
- Navigate cell to cell immediately.
- Avoid rebuilding all accessible fragments on ordinary movement.
- Debounce source preview.
- Keep UIA queries fast.
- Avoid parsing the full document on every cell move.
- Use source maps created when the dialog opens.
- Batch structure-change events.
- Permit larger tables through virtualization only after accessibility behavior is proven.

For extremely large tables:

- Warn the user.
- Offer Linear View.
- Disable live preview if configured.
- Avoid generating thousands of simultaneous announcements.
- Preserve the ability to cancel.

---

# 35. Security and Privacy

- All parsing and editing occur locally.
- No table content is sent to external services.
- Logs must not contain complete table contents by default.
- Native accessibility providers expose only the active dialog’s table data to local assistive technology.
- HTML previews must not execute scripts or active content.
- Imported files must be treated as data, not executable content.

---

# 36. Packaging and Build Plan

## 36.1 Windows extension

The UIA bridge should be built for all supported Python and processor combinations.

Likely requirements:

- x64 Windows.
- ARM64 when QUILL supports it.
- Debug symbols retained for internal diagnostic builds.
- Signed release binaries.
- Reproducible build instructions.
- Graceful import failure.

## 36.2 Repository organization

Suggested structure:

```text
quill/
    structured_tables/
        model.py
        controller.py
        commands.py
        validation.py
        importers/
        formats/
            markdown.py
            html.py
        ui/
            table_studio.py
            spatial_grid.py
            linear_view.py
            cell_editor.py
        accessibility/
            base.py
            windows_uia.py
            macos.py
            linux.py

native/
    windows_table_uia/
        CMakeLists.txt
        src/
        tests/
```

## 36.3 Feature flags

Initial flags:

- `structured_table_studio`
- `native_table_uia`
- `linear_table_view`
- `html_table_spans`
- `table_import_csv`

The release UI should not expose confusing experimental flags to ordinary users unless QUILL already has a supported experimental-features screen.

---

# 37. Delivery Roadmap

## Phase 0: Research and native spikes

- Test current wx grid behavior.
- Test `wx.Accessible`.
- Build minimal UIA provider.
- Build native Cell Content region.
- Build Linear View.
- Compare with `wx-accessible-grid`.
- Publish a test report.

## Phase 1: Core model and flat Markdown tables

- Format-neutral model.
- Markdown parser and serializer.
- Existing table editing.
- Blank table creation.
- Row and column operations.
- Native details editor.
- Source preview.
- Transactional commit.
- Linear View.
- Initial Windows UIA provider.

## Phase 2: Import and conversion

- Selection conversion.
- Clipboard matrix paste.
- CSV and TSV import.
- File import.
- Header detection.
- Import preview.
- Dimension repair.

## Phase 3: HTML simple tables

- Basic HTML parsing and serialization.
- Captions.
- Header rows.
- Header columns.
- Sections.
- Safe attributes.
- Accessibility validation.

## Phase 4: Complex HTML tables

- Existing span preservation.
- Complex header associations.
- Merge and split.
- Advanced accessibility repair.
- Multiple header regions.

## Phase 5: Cross-platform semantic adapters

- macOS native accessibility bridge.
- Linux assessment and adapter.
- Platform parity testing.
- Shared behavior conformance suite.

## Phase 6: Advanced productivity

- Dialog-level undo.
- Typed cells.
- Sorting.
- Transpose.
- Formula-free computed summaries.
- Table templates.
- Column presets.
- Bulk editing.
- Find within table.
- Compare table versions.
- Accessible table repair assistant.

---

# 38. Risks and Mitigations

## Risk: UIA provider complexity

Mitigation:

- Keep the provider narrow.
- Keep all data in Python.
- Build a minimal provider first.
- Add patterns incrementally.
- Use stable identifiers.
- Test with Accessibility Insights early.

## Risk: Screen-reader differences

Mitigation:

- Maintain configurable announcements.
- Expose proper platform semantics.
- Keep Linear View.
- Test NVDA, JAWS, and Narrator continuously.
- Avoid relying on one screen reader’s heuristics.

## Risk: Focus loss after model updates

Mitigation:

- Stable cell IDs.
- Deterministic focus rules.
- Incremental refresh.
- Explicit focus events.
- Automated focus tests.

## Risk: Complex HTML tables

Mitigation:

- Preserve before editing.
- Disable unsafe structural operations.
- Add advanced support in phases.
- Never silently flatten spans or associations.

## Risk: Markdown limitations

Mitigation:

- Use profiles.
- Offer HTML fallback.
- Preview output.
- Explain unsupported structures.
- Never imply that Markdown can represent features it cannot.

## Risk: Native extension packaging

Mitigation:

- Isolate the extension.
- Provide graceful fallback.
- Automate builds.
- Sign release binaries.
- Keep Linear View functional without it.

## Risk: Excessive verbosity

Mitigation:

- Concise, Standard, Detailed, and Custom profiles.
- Speak changed context rather than all context.
- Provide a command to hear full cell details.
- Avoid duplicate provider and application announcements.

---

# 39. Recommended Product Decisions

These decisions are recommended as defaults:

1. Use context-sensitive F2 across lists and tables.
2. Use `wx.grid.Grid` for the visual spatial grid.
3. Build a native Windows UIA provider.
4. Keep the native provider small and model-driven.
5. Use a separate multiline Cell Content editor as the primary editing surface.
6. Provide a fully supported Linear Table View.
7. Keep model, parsing, serialization, validation, and commands cross-platform.
8. Permit platform-specific accessibility hooks.
9. Preserve existing HTML spans in the first release but defer authoring new spans.
10. Support real CSV and TSV import.
11. Use native menus.
12. Reparse generated source before commit.
13. Make the complete document replacement one undo step.
14. Treat `wx-accessible-grid` as a behavioral reference, not a mandatory runtime dependency.
15. Do whatever platform-specific engineering is required to produce greatness rather than limiting QUILL to the weakest abstraction available.

---

# 40. Acceptance Criteria for the Native Accessibility Foundation

The foundation is acceptable when a blind keyboard user can:

1. Enter the grid and hear the table name and dimensions.
2. Move through cells with arrow keys.
3. Hear the correct row and column headers.
4. Identify blank, editable, and read-only cells.
5. Open a native multiline editor for the active cell.
6. Commit or cancel an edit predictably.
7. Add and remove rows and columns.
8. Move rows and columns.
9. Select a row, column, or rectangular cell range.
10. Hear selection changes.
11. Open a native context menu.
12. Switch to Linear Table View.
13. Return to the same logical cell after switching views.
14. Close the dialog and return to the corresponding document location.
15. Undo the entire table operation with one Ctrl+Z.
16. Complete all essential tasks with NVDA, JAWS, and Narrator.
17. Use the dialog in high contrast and at high display scaling.
18. Recover gracefully if the native provider is unavailable.

---

# 41. Definition of Done

QUILL Table Studio is complete when users can create and edit Markdown and HTML tables without typing table syntax, while receiving dependable row, column, header, value, selection, and editing information through native assistive technology.

The feature is not done merely because a table is visually displayed or because arrow keys move.

It is done when:

- The active cell is semantically exposed.
- Header relationships are correct.
- Editing is predictable.
- Structural changes are announced.
- Focus never becomes lost.
- The model and source remain safe.
- Cross-platform fallbacks are strong.
- Windows provides true native table semantics.
- A blind user can work efficiently and confidently with real documents.

---

# 42. Immediate Next Engineering Actions

1. Create a standalone `wx.grid.Grid` accessibility test harness.
2. Test current behavior with NVDA, JAWS, and Narrator.
3. Add a `wx.Accessible` prototype.
4. Design the format-neutral `TableDocumentModel`.
5. Build a native Cell Content editing region.
6. Build the Linear Table View.
7. Implement a minimal Windows UIA provider exposing a 3-by-3 virtual grid.
8. Validate the provider with Accessibility Insights.
9. Connect provider focus to the wx grid.
10. Compare navigation behavior with `wx-accessible-grid`.
11. Write the native spike report.
12. Convert the validated architecture into the full Table Studio PRD.

---

# 43. Research References

Primary implementation reference:

- https://github.com/Community-Access/wx-accessible-grid

Key files reviewed:

- `README.md`
- `src/wx_accessible_grid/model.py`
- `src/wx_accessible_grid/grid.py`
- `src/wx_accessible_grid/render.py`
- `src/wx_accessible_grid/assets.py`
- `tests/test_render.py`
- `pyproject.toml`

Primary Microsoft accessibility concepts for the implementation phase:

- UI Automation Grid pattern.
- UI Automation GridItem pattern.
- UI Automation Table pattern.
- UI Automation TableItem pattern.
- UI Automation Selection pattern.
- UI Automation Value pattern.
- UI Automation fragment providers.
- `WM_GETOBJECT`.
- Focus and structure-changed events.

The implementation phase should use current Microsoft documentation as the source of truth for exact interfaces and provider contracts.
