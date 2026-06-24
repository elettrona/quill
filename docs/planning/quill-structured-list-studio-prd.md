# QUILL Structured List Studio

## Product Requirements Document — Configuration and Definition List Expansion

**Feature:** Structured List Studio  
**Primary command:** F2  
**Supported formats:** Markdown and HTML  
**Supported structures:** Bulleted lists, numbered lists, checklists, nested lists, and definition or description lists  
**Platform:** QUILL for Windows using wxPython  
**Accessibility:** Foundational product requirement  
**Status:** Phase 1 implemented; definition-list source/model implemented (2026-06-24)

---

# 1. Product Expansion

The Structured List Studio must be both:

1. Immediately understandable with excellent defaults.
2. Richly configurable for users who want precise control over behavior, source generation, accessibility announcements, import handling, and keyboard interaction.

The feature must also support **definition lists**, sometimes called **description lists**, through a specialized experience based on:

- Terms.
- Definitions or descriptions.
- Multiple definitions for one term.
- Multiple related terms where the source format supports them.
- Reordering terms and definitions.
- Importing term-and-definition pairs.
- Converting appropriate selected content into a definition list.
- Generating valid Markdown or HTML without requiring the user to type structural syntax.

The user should work with understandable concepts such as:

> Term: Screen reader  
> Definition: Software that presents onscreen information through speech or braille.

The user should not need to work directly with:

```html
<dl>
  <dt>Screen reader</dt>
  <dd>Software that presents onscreen information through speech or braille.</dd>
</dl>
```

or format-specific Markdown definition syntax.

---

# 2. Configuration Philosophy

## 2.1 Excellent defaults first

A user must be able to press F2 and complete the most common task without visiting Settings.

Default behavior should:

- Detect whether the user is editing or creating a list.
- Detect paragraphs or lines intelligently.
- Preserve existing formatting where safe.
- Generate valid source.
- Use accessible native controls.
- Provide concise but useful screen-reader announcements.
- Avoid unexpected nesting.
- Avoid silent data loss.
- Show a preview before ambiguous imports.

## 2.2 Progressive disclosure

Advanced settings must not overwhelm the primary dialog.

The main dialog should expose only controls relevant to the current task.

Less-common controls should appear under clearly labeled expandable sections such as:

- Import Options.
- Numbering Options.
- Checklist Options.
- Definition List Options.
- Source Formatting.
- Accessibility and Announcements.
- Advanced.

## 2.3 Configurable at appropriate scopes

Settings should support these scopes:

### Application defaults

Used across QUILL unless overridden.

### Format defaults

Separate behavior for:

- Markdown.
- HTML.

### Workspace or project defaults

Where QUILL supports workspace-level configuration, projects may define their preferred list conventions.

### Document overrides

An individual document may temporarily or persistently use different settings.

### Current dialog only

Users may change an option for the present operation without changing future defaults.

A control should allow:

> Use for this operation only

or:

> Save as my default

## 2.4 Source preservation

When editing an existing list, preservation of the document’s current conventions should normally take precedence over global formatting defaults.

For example, if a Markdown document already uses asterisks for bullets, QUILL should preserve them unless the user explicitly requests normalization.

## 2.5 Accessible configuration

Every configurable choice must be available through:

- A labeled control.
- A complete keyboard path.
- An accessible explanation.
- A Restore Default action.
- A preview where the effect may not otherwise be obvious.

Settings must not rely on unlabeled icons, color, or visual arrangement.

---

# 3. Configuration Architecture

QUILL should use a structured configuration model rather than scattered dialog preferences.

A representative configuration model is:

```text
StructuredListSettings
    general
    creation
    import
    markdown
    html
    numbering
    checklist
    definition_list
    nesting
    accessibility
    confirmations
    preview
    keyboard
```

Settings should participate in QUILL’s normal:

- Preferences framework.
- Profile system.
- Import and export system.
- Reset-to-default behavior.
- Portable-mode settings storage.
- Workspace configuration where applicable.

---

# 4. General List Settings

Provide a Settings category:

**Editing → Structured List Studio**

## 4.1 Default new-list type

Options:

- Bulleted.
- Numbered.
- Checklist.
- Definition list.
- Remember the most recently used type.
- Ask each time.

Recommended default:

> Bulleted

## 4.2 F2 behavior

Options:

- Fully context-sensitive.
- Edit lists only.
- Ask what to do when outside a list.
- Use a different configured command for list creation.

Recommended default:

> Fully context-sensitive

Context-sensitive behavior means:

- Inside a list: edit the list.
- With selected ordinary content: convert the selection.
- Without a list or selection: create a new list.

## 4.3 Initial focus

Options:

- Current item in the items outline.
- Item content field.
- List type control.
- Remember the last focus location.

Recommended defaults:

- Existing list: current item.
- New blank list: item content.
- Imported list: first imported item.

## 4.4 Remember dialog size and layout

Options:

- Remember size.
- Remember expanded or collapsed sections.
- Remember source-preview visibility.
- Restore standard layout each time.

Recommended default:

> Remember dialog size but use context-sensitive section visibility.

## 4.5 Default insertion position for imported items

Options:

- After selected item.
- Before selected item.
- At end of current container.
- Ask each time.

Recommended default:

> Ask each time when editing an existing list.

---

# 5. Selection Conversion Settings

## 5.1 Default selection interpretation

Options:

- Automatically detect.
- One item per paragraph.
- One item per nonblank line.
- One item per line, including blank lines.
- Remember the previous choice.

Recommended default:

> Automatically detect

## 5.2 Blank-line behavior

Options:

- Use blank lines as paragraph separators.
- Ignore blank lines.
- Create blank items.
- Ask when blank lines are detected.

Recommended default:

> Use blank lines as separators without creating blank items.

## 5.3 Preserve paragraph line breaks

Options:

- Preserve internal line breaks.
- Join wrapped lines with spaces.
- Ask when multiline paragraphs are detected.

Recommended default:

> Preserve internal line breaks in paragraph mode.

## 5.4 Trim whitespace

Independent options:

- Trim leading whitespace.
- Trim trailing whitespace.
- Preserve indentation.
- Collapse repeated internal spaces.

Recommended defaults:

- Trim leading and trailing whitespace.
- Preserve internal spaces.
- Do not interpret indentation as nesting unless enabled explicitly.

---

# 6. Import Settings

## 6.1 Import sources

Users may create or extend lists from:

- Clipboard content.
- A multiline paste field.
- Plain-text files.
- Markdown files.
- Selected document content.

The import architecture should permit future sources such as:

- CSV columns.
- Spreadsheet ranges.
- Database results.
- Web page selections.

## 6.2 Existing marker detection

Options:

- Detect and remove bullet markers.
- Detect and remove ordered markers.
- Detect Markdown task markers.
- Detect definition-list separators.
- Preserve markers as literal content.
- Ask when markers are detected.

Recommended default:

> Detect consistently used markers and display the interpretation in the preview.

## 6.3 Indentation interpretation

Options:

- Never create nesting from indentation.
- Detect tabs only.
- Detect spaces using a configured width.
- Detect tabs and spaces.
- Ask when indentation patterns are found.

Recommended default:

> Never create nesting automatically.

When enabled, configurable indentation widths should include:

- 2 spaces.
- 3 spaces.
- 4 spaces.
- Document convention.
- Automatically detect.

## 6.4 File encodings

Configuration should include:

- Automatic encoding detection.
- Preferred fallback encoding.
- Ask when uncertain.
- Remember a choice for the current project.

Likely choices include:

- UTF-8.
- UTF-8 with BOM.
- UTF-16.
- Windows-1252.
- System default.

## 6.5 Large import behavior

Options:

- Warn above a configured number of items.
- Open preview for every large import.
- Automatically expand only the first level.
- Disable live source preview while typing for very large lists.

Recommended warning threshold:

> 500 items

The threshold must be configurable.

---

# 7. Markdown Source Settings

## 7.1 Bullet marker style

Options:

- Preserve document style.
- Dash.
- Asterisk.
- Plus.
- Use configured project convention.

Recommended default:

> Preserve document style, otherwise use dash.

## 7.2 Ordered-list marker strategy

Options:

- Sequential numbers.
- Use `1.` for every item.
- Preserve document style.
- Use a configured project convention.

Recommended default:

> Preserve document style, otherwise use sequential numbers.

## 7.3 Ordered delimiter style

Where supported:

- Period.
- Closing parenthesis.
- Preserve existing delimiter.

## 7.4 Task marker style

Options:

- `[ ]` and `[x]`.
- `[ ]` and `[X]`.
- Preserve existing capitalization.
- Use configured project convention.

Recommended default:

> Preserve existing style, otherwise use lowercase `x`.

## 7.5 Tight and loose lists

Options:

- Preserve existing spacing.
- Prefer tight lists.
- Prefer loose lists.
- Determine based on multiline content.

Recommended default:

> Preserve existing spacing; use loose formatting when item structure requires it.

## 7.6 Definition-list Markdown profile

Markdown definition-list syntax is not universal across all Markdown implementations.

QUILL must provide a configurable **Markdown Definition List Profile**.

Possible profiles may include:

- Document or workspace profile.
- Pandoc-compatible.
- Markdown Extra-compatible.
- MultiMarkdown-compatible.
- HTML fallback inside Markdown.
- Plain-text fallback.
- Definition lists disabled for this Markdown profile.

The user should not be required to understand syntax variants during ordinary editing.

The selected document profile should determine serialization.

When QUILL cannot determine that the target renderer supports definition lists, it should say:

> Definition-list support is not configured for this Markdown document.

The user may then choose:

- Configure a Markdown profile.
- Generate embedded HTML.
- Create a standard list instead.
- Cancel.

Recommended default for unknown Markdown environments:

> Ask before generating, with embedded HTML offered as a safe portable option where appropriate.

---

# 8. HTML Source Settings

## 8.1 List indentation

Options:

- Preserve document indentation.
- Tabs.
- 2 spaces.
- 4 spaces.
- Use QUILL HTML formatting settings.

Recommended default:

> Preserve document convention.

## 8.2 Checkbox generation

Options:

- Disabled checkbox inputs.
- Interactive checkbox inputs.
- Use ARIA-compatible custom markup only when explicitly configured.
- Preserve existing checkbox behavior.

Recommended default:

> Disabled native checkbox inputs.

## 8.3 Checkbox label association

Options should ensure that generated checkboxes have readable adjacent content.

Where an explicit HTML `<label>` is generated, QUILL must:

- Create safe unique identifiers.
- Associate the label correctly.
- Avoid changing the visual presentation unexpectedly.

The default simple representation may keep readable text immediately adjacent to the input where that matches the project’s HTML conventions.

## 8.4 Attribute preservation

Options:

- Preserve safe global attributes.
- Normalize generated source.
- Warn before dropping incompatible attributes.
- Show attribute differences in preview.

Recommended default:

> Preserve safe attributes and warn before dropping information.

## 8.5 Definition lists

HTML definition lists must serialize using:

- `<dl>`
- `<dt>`
- `<dd>`

The user-facing experience should use the terminology selected in Settings:

- Definition list.
- Description list.
- Term and description list.

Recommended user-facing term:

> Definition or Description List

A shorter interface label may use:

> Definition List

---

# 9. Numbering Settings

Provide options for:

- Default starting number.
- Whether to preserve non-1 start values.
- Whether numbers appear in outline labels.
- Whether screen readers announce the number on every selection.
- Whether numbering changes are announced immediately.
- Whether hierarchical numbers are displayed as supplemental orientation.
- Whether renumbering is shown in the generated-source preview while moving items.

Recommended defaults:

- Preserve start values.
- Show and announce rendered numbers.
- Do not invent hierarchical numbers that are not represented by the output format.

---

# 10. Checklist Settings

## 10.1 New task state

Options:

- Unchecked.
- Checked.
- Match the preceding task.
- Remember the most recently used state.

Recommended default:

> Unchecked

## 10.2 Toggle key

Default:

> Space while focus is in the items outline

The command must be remappable through QUILL’s keyboard customization system.

## 10.3 Completion announcements

Options:

- State only.
- State and task name.
- State, task name, and completion total.
- No automatic completion announcement.

Recommended default:

> State, task name, and completion total.

Example:

> Checked: Buy coffee. 4 of 10 tasks complete.

## 10.4 Parent and child completion

Options for future use:

- Parent state independent from children.
- Offer to mark children when parent is checked.
- Automatically check parent when all children are checked.
- Three-state parent checkbox.

Recommended initial behavior:

> Parent state remains independent.

Automatic propagation must not be enabled by default.

## 10.5 Checked-item presentation

Possible visual options:

- Standard text.
- Strike-through completed text.
- Dim completed text.
- Move checked items to bottom manually.
- Hide checked items temporarily.

Accessibility requirements:

- Checked state must always be announced explicitly.
- Color, dimming, or strike-through must never be the only indication.
- Hiding checked items must be a temporary view filter, never an automatic deletion.

## 10.6 Checklist presets

Users may create presets such as:

- Shopping list.
- Packing list.
- Project tasks.
- Meeting actions.
- Daily checklist.

A preset may define:

- Default list type.
- New-item state.
- Completion announcement verbosity.
- Checked-item sorting behavior.
- Markdown or HTML output style.
- Preferred import interpretation.

---

# 11. Accessibility and Announcement Settings

## 11.1 Announcement verbosity

Provide profiles:

### Concise

Announce:

- Item text.
- Number or checked state.
- Important operation result.

### Standard

Announce:

- Item text.
- State or number.
- Nesting level.
- Position among siblings.
- Important operation result.

### Detailed

Announce:

- Item text.
- List type.
- Number or task state.
- Level.
- Sibling position.
- Parent.
- Child count.
- Expanded or collapsed state.

### Custom

Allow users to independently enable or disable announcement components.

Recommended default:

> Standard

## 11.2 Operation announcements

Independent settings for:

- Added item.
- Removed item.
- Moved item.
- Indented item.
- Outdented item.
- Checked-state change.
- List-type change.
- Import completed.
- Source validation completed.
- Dialog completion.

## 11.3 Repeated instructions

Options:

- Speak extended instructions on every opening.
- Speak extended instructions the first time only.
- Never speak extended instructions automatically.
- Provide instructions only through F1.

Recommended default:

> Speak brief orientation each time and extended instructions only on first use.

## 11.4 Tree terminology

For flat lists:

- Do not announce “tree” or expand/collapse concepts unnecessarily.

For nested lists:

- Announce level and child information.
- Use familiar words such as “parent” and “child item.”
- Avoid implementation-oriented phrases such as “tree node” unless the screen reader itself supplies them.

## 11.5 Focus restoration behavior

Configurable options:

- Return to edited item.
- Return to beginning of generated list.
- Return to original caret offset.
- Select the generated list.
- Remember the last choice.

Recommended default:

> Return to the item that was selected when OK was activated.

---

# 12. Confirmation Settings

Users should be able to configure confirmations while QUILL retains safety boundaries.

Configurable confirmations may include:

- Removing an item with children.
- Deleting the entire list.
- Replacing all items during import.
- Converting a checklist and losing checked states.
- Flattening a nested list.
- Dropping incompatible HTML attributes.
- Converting between ordinary and definition lists.
- Importing more than a configured item count.

Safety-critical confirmations should not be completely suppressible when irreversible model information would be discarded before the document transaction.

Where appropriate, offer:

> Do not ask again for this type of operation

with a Settings command to restore all warnings.

---

# 13. Configuration Presets

QUILL should ship with accessible presets.

## 13.1 Recommended

Balanced defaults for most users.

## 13.2 Screen Reader Detailed

- Detailed item announcements.
- Parent and child information.
- Completion totals.
- Preview available but collapsed.
- All destructive confirmations enabled.

## 13.3 Screen Reader Concise

- Short item announcements.
- Minimal repetition.
- Operation results enabled.
- Full information available through a command.

## 13.4 Markdown Author

- Preserve source style.
- Markdown-specific preview enabled.
- Existing-marker detection enabled.
- Sequential numbering configurable.
- Definition-list profile visible.

## 13.5 HTML Author

- HTML source preview enabled.
- Attribute-preservation warnings enabled.
- Disabled checkbox inputs by default.
- HTML definition-list generation enabled.

## 13.6 Shopping Checklist

- Checklist default.
- New items unchecked.
- Space toggles completion.
- Completion count announced.
- Paste uses one item per nonblank line.
- Optional Move Checked Items to Bottom command prominently available.

Users may create, name, export, import, duplicate, and reset custom presets.

---

# 14. Definition List Experience

## 14.1 Purpose

Definition lists represent related terms and their explanations, descriptions, values, or details.

Common uses include:

- Glossaries.
- Frequently asked questions.
- Product specifications.
- Names and descriptions.
- Commands and explanations.
- Contact fields.
- Abbreviations and meanings.
- Technical terminology.
- Question-and-answer material.

The interface must make the relationship clear without requiring knowledge of `<dl>`, `<dt>`, `<dd>`, colons, indentation, or Markdown extensions.

## 14.2 User-facing structure

The primary structure should be:

```text
Entry
    One or more terms
    One or more definitions or descriptions
```

Most users will create:

```text
Term
Definition
```

The data model should nevertheless support:

- One term with multiple definitions.
- Multiple equivalent terms sharing definitions.
- Reordering definitions within an entry.
- Reordering complete entries.

## 14.3 Simple definition list behavior

For the common case of one term and one definition:

- The items outline behaves like an ordinary list of entries.
- Each entry is announced using its term.
- Selecting an entry exposes two clearly labeled multiline fields:
  - Term.
  - Definition or description.
- Users do not need to navigate a visible hierarchy.

Example announcement:

> Entry 2 of 8. Screen reader. One definition.

## 14.4 Advanced definition list behavior

When an entry contains multiple terms or definitions:

- The outline may expose expandable children.
- The parent entry is labeled using its first term.
- The accessible name includes term and definition counts.

Example:

> Entry 3 of 12. HTML. Two terms, three definitions. Expanded.

A flat entry should never be burdened with unnecessary tree navigation.

---

# 15. Definition List Dialog Controls

When the selected list type is Definition List, the selected-item region changes appropriately.

## 15.1 Term field

Provide a labeled multiline or single-line field:

> Term

The initial release may use a multiline field to support long terms and reliable screen-reader review.

## 15.2 Definition field

Provide a labeled multiline field:

> Definition or description

This field supports:

- Multiple sentences.
- Multiple paragraphs.
- Inline Markdown.
- Inline HTML where appropriate.
- Links and emphasis.
- Preserved complex content where safe.

## 15.3 Multiple terms

Provide commands:

- Add alternate term.
- Edit selected term.
- Remove selected term.
- Move term up.
- Move term down.

The simple one-term interface should remain primary. Multiple-term controls may appear under:

> Additional Terms

## 15.4 Multiple definitions

Provide commands:

- Add another definition.
- Edit selected definition.
- Remove selected definition.
- Move definition up.
- Move definition down.

The first definition appears directly in the primary Definition field.

Additional definitions may be managed through an accessible list and separate multiline field.

## 15.5 Entry operations

Provide:

- Add entry before.
- Add entry after.
- Remove entry.
- Move entry up.
- Move entry down.
- Duplicate entry.
- Split entry.
- Merge with previous entry.
- Merge with next entry.

Split and merge may be advanced operations.

---

# 16. Definition List Outline Announcements

For a simple entry:

> Term: Screen reader. Entry 2 of 10. One definition.

For multiple definitions:

> Term: Accessibility. Entry 4 of 10. Three definitions.

For alternate terms:

> Terms: HTML and HyperText Markup Language. Entry 5 of 10. Two terms, one definition.

When reviewing a definition child:

> Definition 2 of 3 for Accessibility. A practice that ensures people with disabilities can use a product.

The interface must not announce raw `<dt>` or `<dd>` element names unless the user has enabled source-oriented verbosity.

---

# 17. Creating Definition Lists

## 17.1 Create from scratch

The user chooses Definition List.

QUILL creates:

- One blank term.
- One blank definition.

Focus begins in the Term field.

After the user finishes the term, a configurable command may move to the Definition field.

## 17.2 Convert selected paragraphs

Possible interpretation modes:

- Alternating term and definition paragraphs.
- First line is the term; remaining paragraph content is the definition.
- Paragraph begins with `Term: Definition`.
- Ask the user to map the selected content.
- Open an import preview for confirmation.

No ambiguous conversion should happen silently.

## 17.3 Convert selected lines

Supported patterns may include:

```text
Term: Definition
```

```text
Term<TAB>Definition
```

```text
Term - Definition
```

```text
Term
Definition
Term
Definition
```

The separator must be configurable and previewed.

## 17.4 Paste definition entries

The Paste Items command changes to:

> Paste Terms and Definitions…

The import dialog provides interpretation choices:

- Term and definition separated by a tab.
- Term and definition separated by the first colon.
- Term and definition separated by a configured character.
- Alternating lines.
- Alternating paragraphs.
- First line of each paragraph is the term.
- Automatically detect.
- Treat all imported content as ordinary list items instead.

## 17.5 Read from file

Definition-list import supports the same line-oriented text files as ordinary lists.

The user must see a preview containing:

- Detected term.
- Detected definition.
- Entry count.
- Entries missing terms.
- Entries missing definitions.
- Duplicate terms.
- Multiline definitions.

---

# 18. Definition Import Configuration

## 18.1 Separator choices

Configurable separators include:

- Tab.
- First colon.
- First equals sign.
- First dash surrounded by spaces.
- Custom text separator.
- Alternating lines.
- Alternating paragraphs.

Recommended default:

> Automatically detect and require preview confirmation.

## 18.2 Separator safety

QUILL must be conservative.

For example, a colon may legitimately appear in a sentence or URL.

When confidence is low, QUILL should say:

> QUILL found more than one possible way to divide these terms and definitions.

The user can choose the interpretation from a preview.

## 18.3 Missing values

Options:

- Allow a blank term.
- Allow a blank definition.
- Skip incomplete entries.
- Ask for each incomplete entry.
- Show incomplete entries for correction.

Recommended default:

> Show incomplete entries for correction before import.

## 18.4 Duplicate terms

Options:

- Keep duplicate entries.
- Merge definitions under one term.
- Ask for each duplicate group.
- Highlight duplicates without changing them.

Recommended default:

> Highlight duplicates and do not merge automatically.

---

# 19. Converting Between List Types

## 19.1 Ordinary list to definition list

QUILL must not guess the term and definition relationship without review.

Possible conversion strategies:

- Use each item as a term with a blank definition.
- Split each item at the first colon.
- Split each item at the first tab.
- Use the first line as the term and remaining lines as the definition.
- Open mapping preview.
- Cancel.

Recommended default:

> Open mapping preview.

## 19.2 Definition list to bulleted or numbered list

Offer conversion formats:

- Term only.
- Definition only.
- `Term: Definition`.
- Term as parent item with definitions as children.
- One item for every term-definition pair.

Show a preview before committing.

Recommended default:

> `Term: Definition` for simple entries, with explicit review for entries containing multiple terms or definitions.

## 19.3 Definition list to checklist

Possible use case:

```text
Term: Description
```

becomes an unchecked task.

Because meaning may change, QUILL must preview the result and require confirmation.

## 19.4 Information-loss warnings

Warn before a conversion that would discard:

- Alternate terms.
- Multiple definitions.
- Checked states.
- Ordered start values.
- Attributes.
- Nesting relationships.
- Complex block content.

---

# 20. Nested Content in Definitions

A definition may contain:

- Paragraphs.
- A bulleted list.
- A numbered list.
- A checklist.
- Another supported block structure.

The architecture should allow definitions to contain structured child content.

For the initial implementation:

- Simple multiline definition content should be editable directly.
- Existing nested structures should be preserved.
- Nested list content may be opened in a secondary List Studio operation.
- QUILL must never flatten nested definition content silently.

A future enhancement may provide:

> Edit Structured Content in Definition…

This opens the appropriate editor while preserving the parent definition context.

---

# 21. Definition List Source Generation

## 21.1 HTML

Generate valid semantic HTML:

```html
<dl>
  <dt>Screen reader</dt>
  <dd>Software that presents information through speech or braille.</dd>

  <dt>Magnifier</dt>
  <dd>Software that enlarges visual content.</dd>
</dl>
```

For multiple definitions:

```html
<dl>
  <dt>Accessibility</dt>
  <dd>The quality of being usable by people with disabilities.</dd>
  <dd>A discipline concerned with removing barriers.</dd>
</dl>
```

For multiple related terms:

```html
<dl>
  <dt>HTML</dt>
  <dt>HyperText Markup Language</dt>
  <dd>The markup language used to structure web content.</dd>
</dl>
```

QUILL must preserve valid semantic ordering of `<dt>` and `<dd>` elements.

## 21.2 Markdown

Generation must follow the active Markdown Definition List Profile.

A representative supported style may resemble:

```markdown
Screen reader
: Software that presents information through speech or braille.

Magnifier
: Software that enlarges visual content.
```

QUILL must not assume that every Markdown renderer supports this syntax.

The generated-source preview should identify the active profile:

> Generated Markdown — Pandoc-compatible definition list

## 21.3 Markdown fallback

When native definition-list syntax is unavailable, configurable fallback options include:

- Embedded HTML `<dl>`.
- Bulleted list using `Term: Definition`.
- Heading and paragraph pairs.
- Refuse conversion until a profile is selected.

Recommended default:

> Ask the user, with embedded HTML presented as the first semantic fallback.

---

# 22. Definition List Internal Model

Extend the neutral model:

```text
StructuredListDocumentModel
    source_format
    source_range
    creation_mode
    structure_type
    original_source
    root_structure
    formatting_preferences

DefinitionList
    list_id
    attributes
    entries

DefinitionEntry
    entry_id
    terms
    definitions
    attributes
    original_source_metadata

DefinitionTerm
    term_id
    content
    attributes
    original_source_metadata

DefinitionDescription
    definition_id
    content
    content_kind
    attributes
    child_structures
    original_source_metadata
```

Stable identities must be used for:

- Entries.
- Terms.
- Definitions.
- Child structures.

These identifiers must never appear in the user’s source.

---

# 23. Definition List Accessibility Requirements

A keyboard-only screen-reader user must be able to:

- Determine the number of entries.
- Review every term.
- Review every definition.
- Determine when an entry has multiple terms.
- Determine when an entry has multiple definitions.
- Add, remove, edit, and reorder entries.
- Add and reorder alternate terms.
- Add and reorder multiple definitions.
- Convert imported content.
- Review generated source.
- Return to the corresponding source location.

Use native labeled fields:

- Term.
- Definition or description.
- Additional terms.
- Additional definitions.

Do not represent term and definition relationships only through:

- Columns without accessible headers.
- Visual indentation.
- Punctuation.
- Bold text.
- Font size.
- Color.

---

# 24. Definition List Keyboard Commands

When focus is in the entries outline:

- Up Arrow: Previous entry.
- Down Arrow: Next entry.
- Enter or F2: Edit the term.
- Ctrl+Enter: Move to the primary definition.
- Insert: Add entry after.
- Shift+Insert: Add entry before.
- Delete: Remove entry.
- Alt+Up Arrow: Move entry up.
- Alt+Down Arrow: Move entry down.
- Ctrl+Alt+T: Add alternate term.
- Ctrl+Alt+D: Add another definition.
- F1: Open help.

All shortcuts must be:

- Remappable.
- Available through labeled buttons or menus.
- Tested with JAWS, NVDA, and Narrator.
- Avoided when they conflict with essential screen-reader commands.

---

# 25. Definition List Summary

Examples:

> Definition list, 12 entries.

> Definition list, 12 entries, 14 terms, 18 definitions.

> Definition list. Entry 3 selected: Accessibility. Two definitions.

The summary should use the configured terminology:

- Definition.
- Description.
- Explanation.

Users may choose their preferred label while source semantics remain unchanged.

---

# 26. Definition List Validation

Before committing, validate:

- At least one entry exists.
- Every entry has at least one term unless blank terms are explicitly allowed.
- Every entry has at least one definition unless blank definitions are explicitly allowed.
- Generated HTML has valid `<dl>`, `<dt>`, and `<dd>` ordering.
- Generated Markdown matches the active profile.
- No term or definition content is lost.
- Nested content remains associated with the correct definition.
- Safe attributes remain attached to their original structures.
- Reparsed output matches the internal model.

Validation errors must leave the document unchanged.

---

# 27. Updated Delivery Plan

## Phase 1: Configurable Flat List Studio

- Context-sensitive F2.
- Blank-list creation.
- Selection conversion.
- Clipboard and file import.
- Bulleted and numbered lists.
- Flat checklists.
- Core configuration categories.
- Accessibility verbosity profiles.
- Source formatting controls.
- Presets.
- Generated-source preview.
- One-step undo.

## Phase 2: Nested Lists

- Add Child.
- Indent and Outdent.
- Hierarchical outline.
- Mixed container types.
- Nested checklists.
- Subtree movement.
- Nested import.
- Configuration for nesting behavior.

## Phase 3: Definition Lists

- HTML definition lists.
- Configurable Markdown definition profiles.
- Term and definition fields.
- Multiple definitions.
- Multiple terms.
- Selection and clipboard conversion.
- File import.
- Conversion previews.
- Source validation.
- Screen-reader testing.

## Phase 4: Structured Content Within Definitions

- Nested lists inside definitions.
- Edit Structured Content command.
- Complex block preservation.
- Rich conversion between list types.
- Additional import mappings.

## Phase 5: Advanced Customization

- User-created presets.
- Workspace policies.
- Configuration import and export.
- Custom separator definitions.
- Configurable confirmation rules.
- Custom announcement templates.
- Additional task workflows.
- More structured-data import formats.

---

# 28. Updated Acceptance Criteria

The Structured List Studio is ready when:

1. Excellent defaults allow first-time use without configuration.
2. Advanced users can configure creation, import, source formatting, accessibility, checklist behavior, numbering, nesting, previews, and confirmations.
3. Settings can be scoped appropriately.
4. Existing document conventions are preserved where safe.
5. Presets can simplify common workflows.
6. A screen-reader user can create and edit definition lists without interacting with source syntax.
7. Definition entries expose understandable Term and Definition fields.
8. Multiple terms and multiple definitions are supported by the model.
9. Definition entries can be added, removed, reordered, imported, and converted.
10. Markdown definition syntax is controlled by a format profile rather than assumed universally.
11. HTML definition lists use valid semantic `<dl>`, `<dt>`, and `<dd>` structures.
12. Ambiguous imports always provide an accessible preview.
13. Conversions warn before discarding structural information.
14. Generated source is reparsed and validated before document replacement.
15. Cancel leaves the document unchanged.
16. Successful completion remains one undoable operation.
17. All essential operations work with JAWS, NVDA, Narrator, the keyboard, high contrast, and enlarged display settings.

---

# 29. Updated Definition of Done

The Structured List Studio is complete when users can create and edit:

- Bulleted lists.
- Numbered lists.
- Checklists.
- Nested mixed lists.
- Definition or description lists.

They must be able to do so from:

- Existing document structures.
- Selected paragraphs.
- Selected lines.
- Clipboard content.
- Imported text files.
- A blank dialog.

The experience must be richly configurable while remaining immediately useful with defaults.

A keyboard-only screen-reader user must be able to understand every item, number, task state, nesting relationship, term, definition, operation, warning, and generated-source result without needing to inspect Markdown syntax or HTML tags.

---

# 30. Implementation Status (2026-06-24)

This section records what has shipped against this PRD. It is the source of truth
for "is this done"; update it as further phases land.

## Implemented

- **wx-free core (`quill/core/lists/`), fully unit-tested
  (`tests/unit/core/lists/`, 42 cases):**
  - Neutral model (§22): `FlatList`/`ListItem` and `DefinitionList`/
    `DefinitionEntry` with stable ids that never appear in source.
  - Import interpretation (§5, §6, §17, §18): selection→items (auto paragraph/
    line, blank-line policy, whitespace trimming, marker detection/stripping) and
    conservative definition-separator detection that flags ambiguity instead of
    guessing (§18.2).
  - Source generation (§7, §8, §21): Markdown + HTML for bulleted, numbered,
    checklist, and definition lists; HTML emits semantic `<dl>`/`<dt>`/`<dd>`;
    Markdown definition output follows a configurable profile and refuses native
    syntax when the profile is unset.
  - Conversions with information-loss detection (§19) and accessible
    announcements/summaries at concise/standard/detailed verbosity (§11, §16, §25).
- **F2 Structured List Studio dialog** (`quill/ui/list_studio_dialog.py`,
  `quill/ui/main_frame_list_studio.py`): context-sensitive F2 (convert selection or
  start a new list), type + format choosers, items/entries outline with add/remove/
  move, item-text or Term/Definition fields, live read-only source preview, and a
  single-undo apply. Remappable; F2 displaced Insert Special Character to Shift+F2
  with a legacy-binding migration. Excellent defaults work with no Settings visit
  (§2.1).
- **Nested-list editing (Phase 2):** Indent / Outdent / Add child in the dialog for
  flat lists, with the outline showing nesting depth and Move up/down reordering a
  whole subtree among its siblings so a parent never leaves its children behind. All
  rules are wx-free in `quill/core/lists/nesting.py` (`indent`, `outdent`,
  `add_child`, `move_subtree`, `can_indent`, `can_outdent`, `subtree_end`) and
  unit-tested (`tests/unit/core/lists/test_nesting.py`, 14 cases). The dialog
  enables Indent/Outdent only when structurally valid and hides the row for
  definition lists. Screen readers hear "level N" via the existing announcements.

## Not yet implemented (planned follow-ups)

- The full **Settings/preset surface** (§3–§13): scopes (app/format/workspace/
  document/this-operation), the Settings category, shipped presets, and
  import/export. Defaults currently live in `StructuredListSettings`.
- **Multiple terms / multiple definitions** editing UI (§15.3–§15.4) — the model
  and renderers support them; the dialog edits the primary term/definition only.
- **Import dialogs with preview** (§6, §17.4–§17.5) and **conversion previews /
  information-loss confirmations** (§12, §19) — the core computes interpretations,
  ambiguity, and loss reasons; the preview/confirmation surfaces are pending.
- **In-place editing** of the list under the caret (§4.2) — F2 currently converts a
  selection or starts fresh; the older List Manager still edits an existing Markdown
  list in place.
- **Reparse-and-validate before commit** (§26, §28.14) and the definition Markdown
  **profile prompt** (§7.6, §21.3 — the dialog currently falls back to embedded HTML
  when no profile is set).
- A formal **screen-reader pass** (JAWS/NVDA/Narrator, §28.17); only stub-level
  wiring tests exist so far.
