# QUILL F7 Spelling Review

## Product Requirements Document

**Product:** QUILL  
**Feature:** Accessible F7 Spelling Review  
**Status:** Proposed  
**Priority:** High  
**Primary platform:** Windows, wxPython  
**Primary audiences:** Keyboard users, screen-reader users, users who prefer a guided sequential proofreading workflow, and anyone who wants a focused alternative to inline spelling indicators

---

## 1. Executive Summary

QUILL will provide a classic, guided spelling-review experience invoked with **F7**. The feature should preserve what made the traditional Microsoft Word spelling dialog effective: one issue at a time, clear suggestions, predictable actions, and an obvious path through the document. It should substantially improve that experience for screen-reader and keyboard users.

The defining feature will be a focusable, **multiline, read-only Context field** that contains the misspelled word in meaningful surrounding text. The current word will be selected when the field receives focus so users can hear it in context, review it character by character, move by word or line, copy text, and understand punctuation and sentence structure without leaving the spelling-review dialog.

This is not merely a list of possible corrections. It is a guided proofreading workflow with deliberate focus management, controlled speech, reliable keyboard interaction, safe document editing, clear progress information, privacy-preserving local processing by default, and a complete review summary.

---

## 2. Product Vision

Pressing F7 in QUILL should feel reassuring and familiar:

1. QUILL finds the next potentially misspelled word.
2. The Spelling Review dialog opens.
3. Focus lands in a read-only multiline Context field.
4. The problem word is selected inside its sentence or paragraph.
5. The screen reader announces the issue, progress, and context without excessive repetition.
6. The user can inspect the text with normal editing-navigation commands.
7. The user can Tab to the replacement field, suggestions, and actions.
8. Every action immediately confirms what happened and advances to the next issue.
9. At completion, QUILL reports a useful summary and returns focus exactly where the user expects.

The experience should feel like a careful assistant walking through the document with the user, not like an inaccessible side panel or a stream of unexplained alerts.

---

## 3. Goals

### 3.1 Primary goals

- Provide a complete spelling review through **F7**.
- Present each misspelled word in meaningful, navigable context.
- Make the entire workflow usable without a mouse.
- Make the workflow excellent with NVDA, JAWS, Narrator, and other screen readers that use standard Windows accessibility APIs.
- Use standard controls and predictable focus behavior wherever possible.
- Provide concise, useful speech for state changes without duplicating what the screen reader already announces.
- Support Ignore Once, Ignore All, Change, Change All, Add to Dictionary, Undo Last Action, and Cancel or Close.
- Preserve document integrity, undo history, caret position, selection, viewport, formatting, and accessibility state.
- Keep local document text private by default.
- Scale to large documents without freezing QUILL.

### 3.2 Secondary goals

- Support multiple dictionaries and document languages.
- Provide configurable context size and speech verbosity.
- Allow spelling behavior to be extended through a provider interface.
- Provide a reusable review framework that could later support grammar, terminology, style, and accessibility checks without combining them into the initial spelling workflow.

---

## 4. Non-Goals for the Initial Release

The initial release will not attempt to:

- Replace QUILL's existing inline spelling indicators, if present.
- Perform grammar, style, readability, or inclusive-language review in the same dialog.
- Send document text to an online service by default.
- Reproduce Microsoft Word pixel for pixel.
- Require direct integration with a specific screen reader.
- Automatically rewrite text without explicit user action.
- Add an always-open proofing sidebar.
- Provide thesaurus behavior through Shift+F7 unless that is designed as a separate feature.

---

## 5. Design Principles

### 5.1 Familiar, but better

Retain the strengths of the classic sequential spell checker while resolving common accessibility problems such as uncertain focus, insufficient context, repeated speech, ambiguous button behavior, and loss of the user's position.

### 5.2 Context is a first-class control

Context must not be a static label that a screen reader reads once and then makes difficult to inspect. It must be a standard, focusable, multiline, read-only edit control.

### 5.3 Standard controls before custom controls

Use native wxPython controls that expose reliable name, role, state, value, selection, and keyboard behavior. A custom-drawn widget is unacceptable unless no standard control can meet the requirement and the custom widget receives a complete accessibility implementation.

### 5.4 Speech should inform, not compete

QUILL should announce transitions and results. It should not speak every label and value that the screen reader will already announce when focus moves.

### 5.5 No keyboard traps

Every control must be reachable and escapable using standard keyboard commands. Tab and Shift+Tab must move predictably. Escape must never leave the user uncertain about whether changes were applied.

### 5.6 User control over every edit

No spelling correction is applied until the user activates an explicit action. Change All is scoped and disclosed. Persistent dictionary changes are reversible.

### 5.7 Preserve the document experience

When the dialog closes, the user must return to the document with the intended caret, selection, and scroll position restored. The spell checker must not silently disrupt formatting or create fragmented undo history.

---

## 6. Terminology

- **Issue:** A token QUILL's active spelling provider considers unknown or misspelled.
- **Current word:** The word under review.
- **Context:** Surrounding document text shown in the read-only multiline field.
- **Replacement:** The text that will replace the current word when Change is activated.
- **Suggestion:** A spelling-provider recommendation.
- **Review session:** The complete F7 workflow from invocation until completion or cancellation.
- **Review scope:** Selection, current document, or another explicitly supported text range.
- **Session ignore:** A word ignored until the current review session ends.
- **User dictionary:** A persistent, language-specific list of accepted words.

---

## 7. User Stories

### 7.1 Core review

- As a keyboard user, I can press F7 and begin reviewing spelling without locating a menu command.
- As a screen-reader user, I hear the current issue and can inspect it within a meaningful sentence or paragraph.
- As a user, I can arrow around the Context field exactly as I would in a read-only document.
- As a user, I can replace the current word with a suggestion or text I type myself.
- As a user, I can ignore one occurrence or every matching occurrence for the rest of the session.
- As a user, I can add a legitimate word to my dictionary.
- As a user, I can undo the last spell-review action if I make a mistake.
- As a user, I receive a clear summary when review is complete.

### 7.2 Scope and navigation

- As a user with selected text, I can check only the selection.
- As a user without selected text, I can begin at the caret, continue to the end, and optionally wrap to the beginning.
- As a user, I can hear whether the current review applies to a selection or the entire document.
- As a user, I can return focus to the document at a predictable position when I finish or cancel.

### 7.3 Configuration

- As a user, I can choose sentence, paragraph, or line-based context.
- As a screen-reader user, I can choose concise, balanced, or detailed announcements.
- As a user, I can select the spelling language and dictionary.
- As a technical writer or programmer, I can configure whether QUILL skips URLs, email addresses, file paths, code-like identifiers, all-capital words, or words containing digits.

---

## 8. Invocation and Review Scope

### 8.1 Primary command

- **F7:** Start Spelling Review.
- The command must also be available from an accessible menu, tentatively **Tools > Spelling Review...** or **Review > Spelling Review...**, depending on QUILL's menu architecture.
- The menu item must display the F7 shortcut.

### 8.2 Scope rules

Recommended default behavior:

1. If the editor has a nonempty selection, F7 checks the selection only.
2. If there is no selection, F7 starts at the caret and continues to the end of the document.
3. After reaching the end, QUILL offers to continue from the beginning to the original caret position, unless the user has disabled wrapping.
4. If the document contains no spelling issues in the selected scope, QUILL reports that immediately and returns focus to the editor.

The opening announcement must state the scope, for example:

- “Spelling review. Checking selected text.”
- “Spelling review. Starting at the caret.”

A future release may add a Scope control, but the initial experience should avoid an unnecessary setup dialog.

### 8.3 Empty or unsupported content

If the document is empty, read-only, unavailable, or contains no checkable text, QUILL must provide a clear message and take no action.

---

## 9. Main Dialog Specification

### 9.1 Dialog model

Use a **modal dialog** for the first release. A modal dialog provides a contained workflow, prevents accidental editing behind the review UI, and simplifies predictable focus and keyboard behavior.

Suggested title format:

**Spelling Review — Issue 3 of 18**

If the total is not yet known because scanning is lazy or asynchronous:

**Spelling Review — Issue 3**

Once scanning completes, update the title and progress text without stealing focus.

### 9.2 Logical control order

The recommended tab order is:

1. Context field
2. Replacement field
3. Suggestions list
4. Change button
5. Change All button
6. Ignore Once button
7. Ignore All button
8. Add to Dictionary button
9. Undo Last Action button
10. Options or More button, if included
11. Close or Cancel button

The exact visual layout may differ, but the keyboard order must follow the user's task.

### 9.3 Issue summary

Provide an accessible static text label above the Context field:

- “Not in dictionary: accomodate”
- “Repeated word: the” only in a future grammar-capable version

The current spelling-only release should use issue types such as:

- Not in dictionary
- Possible misspelling
- Mixed-language word, when supported

The issue label must not be the only place the current word is exposed.

---

## 10. Context Field

### 10.1 Control requirements

The Context field must be:

- A standard multiline edit control.
- Read-only.
- Focusable.
- Included in normal Tab order.
- Labeled **Context**.
- Capable of standard character, word, line, sentence, Home, End, Ctrl+Home, and Ctrl+End navigation as supported by the platform and screen reader.
- Capable of selection and copying with Ctrl+C.
- Protected from modification, pasting, or deletion.
- Free of decorative prefixes that pollute copied text.

In wxPython, this should preferably use `wx.TextCtrl` with multiline and read-only styles, unless QUILL's editor architecture requires a different native control with equivalent accessibility behavior.

### 10.2 Initial focus and selection

When the dialog opens or advances to a new issue:

1. Populate the Context field.
2. Compute the current word's start and end offsets within the displayed context.
3. Select the exact word in the Context field.
4. Move focus to the Context field.
5. Allow the screen reader to announce the field, its read-only state, and the selected text.

Focus movement and selection updates must be scheduled only after the control is populated and visible. In wxPython, use an event-safe deferred focus operation such as `wx.CallAfter` where required.

### 10.3 Context construction

Default context should include the complete sentence containing the issue, plus enough adjacent text to prevent ambiguity.

Recommended default algorithm:

- Include the current sentence.
- Include the preceding sentence when available.
- Include the following sentence when available.
- Limit the total context to a configurable character ceiling, such as 800 to 1,200 characters.
- Preserve original punctuation and line breaks where useful.
- Do not expose unrelated document content merely to fill space.

Available context modes:

- **Sentence:** Current sentence, optionally with adjacent sentences.
- **Paragraph:** Current paragraph.
- **Lines:** Configurable number of lines before and after the issue.

Recommended default: **Sentence with adjacent sentences**.

### 10.4 Re-locating the word

Once users arrow around the Context field, the original selection will naturally move. Provide a command to return to and reselect the current word:

- **Alt+W:** Focus Context and select the current word.

The Context label should expose the mnemonic, such as **Context around &word**, only if that wording remains natural. Otherwise implement Alt+W as a dialog-level command and mention it in help text.

### 10.5 Context display safeguards

- Normalize only line endings required by the control; do not change visible words or punctuation.
- Preserve Unicode characters.
- Replace unsupported control characters with safe, explainable representations.
- Never insert literal spoken phrases such as “misspelled word begins” into the text because users may copy the context.
- Visual highlighting may supplement selection, but selection is the required accessible indicator.
- If the issue occurs multiple times within the displayed context, select only the active occurrence.

---

## 11. Replacement Field

### 11.1 Control behavior

The Replacement field must be a standard single-line edit control labeled **Change to**.

On each issue:

- Populate it with the highest-ranked suggestion when one exists.
- Otherwise populate it with the original word.
- Select the entire replacement so typing immediately replaces it.
- Preserve user-entered capitalization and punctuation.
- Permit spaces and hyphens when the provider returns multiword or compound suggestions.
- Permit an empty value, but interpret Change with an empty value as deletion and announce that clearly.

### 11.2 Keyboard interaction

- Typing edits the replacement normally.
- Enter activates **Change** when focus is in the Replacement field.
- Ctrl+Enter may activate **Change All**, provided this shortcut is documented and does not conflict with QUILL conventions.
- Escape initiates dialog cancellation behavior rather than clearing the field silently.

---

## 12. Suggestions List

### 12.1 Control requirements

Use a standard accessible list control labeled **Suggestions**.

Each item should expose plain replacement text. Avoid adding decorative confidence percentages unless they provide meaningful value and can be announced without clutter.

### 12.2 Selection behavior

- The first suggestion is selected by default when suggestions exist.
- Changing the selected suggestion updates the Replacement field.
- Arrow keys move through suggestions.
- Home and End move to the first and last suggestion.
- Type-ahead search should work if supported by the native control.
- Enter applies the selected suggestion through Change.
- Double-click may apply the suggestion for mouse users, but it must not be required.

Recommended announcement when selection changes:

“accommodate, suggestion 2 of 6. Press Enter to change.”

The phrase “Press Enter to change” should be spoken only in detailed mode or the first time the user reaches the list during a session.

### 12.3 No suggestions

When no suggestions are available:

- Keep the list present but empty or disabled according to the most accessible native behavior.
- Set Replacement to the original word.
- Announce “No suggestions.”
- Do not trap focus in an empty list.

---

## 13. Actions

### 13.1 Change

Replaces the current occurrence with the Replacement field's value.

Requirements:

- Apply the edit on the main UI thread.
- Preserve surrounding formatting.
- Include the change in the document's normal undo system.
- Confirm the action concisely.
- Advance to the next issue.

Example announcement:

“Changed accomodate to accommodate. Next issue: recieve.”

### 13.2 Change All

Replaces matching occurrences within the active review scope for the current session.

Requirements:

- Match exact normalized spelling according to the active language and provider.
- Use case-aware replacement rules.
- Never modify text outside the declared scope.
- Explain the scope in accessible help.
- Track the number of replacements.
- Make the complete Change All operation undoable.

Case behavior should be deterministic:

- `teh` to `the`
- `Teh` to `The`
- `TEH` to `THE`

Mixed-case tokens that do not fit a known pattern should not be changed automatically without a defined rule.

Example announcement:

“Changed all remaining occurrences of teh to the. 7 replacements.”

### 13.3 Ignore Once

Skips the current occurrence and advances.

Example announcement:

“Ignored once. Next issue: recieve.”

### 13.4 Ignore All

Ignores matching occurrences for the remainder of the current review session.

Requirements:

- Do not persist this decision beyond the session.
- Apply only to the active language and normalized token.
- Report the number of later occurrences skipped in the completion summary.

### 13.5 Add to Dictionary

Adds the current word to the user dictionary for the active language.

Requirements:

- Clearly identify the target language if more than one dictionary is active.
- Store the word using a stable Unicode encoding.
- Avoid duplicate entries.
- Make the addition reversible through Undo Last Action during the session.
- Provide a Dictionary Management dialog elsewhere in QUILL for later removal.
- If the document is using an unknown language, prompt the user to select a dictionary rather than making an ambiguous addition.

Example announcement:

“Added Quillin to the English United States dictionary.”

### 13.6 Undo Last Action

Undo the most recent spell-review action without closing the dialog.

Supported actions should include:

- Change
- Change All
- Ignore Once
- Ignore All
- Add to Dictionary

Undo requirements:

- Restore the prior document text and current issue.
- Restore counters.
- Remove a just-added dictionary word when applicable.
- Reconstruct the prior Context and Replacement state.
- Focus Context and reselect the restored issue.
- Disable the button when no review action can be undone.

A single-level undo is acceptable for the first release, although a small session action stack is preferred.

### 13.7 Cancel and Close

- **Escape** invokes Cancel.
- If no edits have been made, close immediately and restore document focus.
- If edits have been made, do not imply that Cancel reverses completed changes unless QUILL actually implements transaction rollback.
- Preferred button label after edits: **Close**, not Cancel.
- If full-session rollback is implemented, offer a clear choice: “Keep changes” or “Discard all review changes.”

For the initial release, completed changes should remain part of the document's normal undo history. The dialog must communicate this honestly.

---

## 14. Keyboard Map

Required shortcuts within the dialog:

- **Tab / Shift+Tab:** Move forward or backward through controls.
- **Alt+W:** Focus Context and reselect the current word.
- **Alt+C:** Focus Change to.
- **Alt+S:** Focus Suggestions.
- **Alt+G:** Change.
- **Alt+A:** Change All, unless the mnemonic conflicts with Add to Dictionary.
- **Alt+I:** Ignore Once.
- **Alt+L:** Ignore All.
- **Alt+D:** Add to Dictionary.
- **Alt+U:** Undo Last Action.
- **Enter:** Activate the default action appropriate to the focused control.
- **Escape:** Close or cancel review according to the documented behavior.
- **F1:** Open context-sensitive help for Spelling Review.

Mnemonic assignments must be reviewed against actual localized labels. No two visible controls in the same dialog may share an ambiguous mnemonic.

Recommended button labels with possible mnemonics:

- Chan&ge
- Change &All
- &Ignore Once
- Ignore A&ll
- Add to &Dictionary
- &Undo Last
- &Close

Because localized strings may change mnemonic availability, the implementation must support locale-specific mnemonic definitions.

---

## 15. Screen-Reader Experience

### 15.1 Accessibility strategy

Use three layers, in this order:

1. Standard native control semantics and labels.
2. Correct focus and selection management.
3. A provider-neutral announcement service for meaningful state transitions.

Do not make the experience depend on a vendor-specific API. Optional integrations may enhance the experience, but standard Windows accessibility must remain complete.

### 15.2 Announcement service

Create an internal `AccessibilityAnnouncer` abstraction with at least:

- `announce_polite(message)`
- `announce_assertive(message)`
- `cancel_pending()`
- duplicate suppression
- configurable verbosity

The implementation should prefer a standards-based Windows accessibility notification mechanism available to QUILL's supported wxPython and Windows versions. If no reliable mechanism is available, use an accessible status control or event pattern rather than directly scripting a specific screen reader.

### 15.3 Avoiding duplicate speech

QUILL must not announce control names immediately before moving focus to those controls. Let the screen reader announce focus. QUILL should announce only information the control itself will not convey reliably, such as:

- Review scope
- Issue progress
- Result of the previous action
- Completion summary
- Wrap-to-beginning prompt
- Errors or provider failures

### 15.4 Recommended speech sequence

#### Opening, balanced mode

“Spelling review. Issue 1 of 12. Not in dictionary: accomodate.”

Then focus Context and allow the screen reader to announce:

“Context, read only, multiline,” followed by the selected word and surrounding text according to the user's screen-reader settings.

#### After Change

“Changed accomodate to accommodate. Issue 2 of 12.”

Then refresh and focus Context for the next issue.

#### After Ignore Once

“Ignored once. Issue 3 of 12.”

#### No suggestions

“No suggestions are available.”

#### Completion

“Spelling review complete. 9 changes, 2 ignored once, 1 word ignored for this session, and 1 word added to the dictionary.”

### 15.5 Speech verbosity

Provide three modes:

- **Concise:** Progress and action results only.
- **Balanced:** Issue type, current word, progress, and action results.
- **Detailed:** Balanced information plus control hints and scope reminders.

Default: **Balanced**.

### 15.6 Focus behavior

- Focus must never land on the dialog container with no meaningful control.
- Focus must never disappear after an action.
- Focus must not jump to the document between issues.
- Disabled controls must not receive focus.
- Closing the dialog must restore focus to the original editor instance.
- If the original editor no longer exists, focus the active document editor or the main frame safely.

---

## 16. Visual and Low-Vision Experience

Although screen-reader excellence is central, the dialog must also support low-vision and sighted keyboard users.

Requirements:

- Respect Windows text scaling, DPI scaling, high contrast, and QUILL's light or dark appearance.
- Do not communicate the current issue through color alone.
- Visually highlight the current word in Context in addition to selecting it when feasible.
- Ensure strong focus indicators.
- Allow the dialog to resize.
- Remember the last user-selected size and position while keeping the dialog on-screen.
- Avoid fixed pixel dimensions that clip translated labels or large fonts.
- Use logical grouping and sufficient spacing without creating an unnecessarily large Tab path.

---

## 17. Spelling Provider Architecture

### 17.1 Provider interface

Create a provider-neutral interface so QUILL can use one or more spelling engines without coupling the dialog to a particular library.

Suggested interface:

```python
class SpellCheckProvider(Protocol):
    def is_available(self) -> bool: ...
    def supported_languages(self) -> list[str]: ...
    def check_word(self, word: str, language: str) -> bool: ...
    def suggest(self, word: str, language: str, limit: int = 10) -> list[str]: ...
    def add_to_user_dictionary(self, word: str, language: str) -> None: ...
    def remove_from_user_dictionary(self, word: str, language: str) -> None: ...
```

A batch or iterator API should be added for performance:

```python
class SpellIssueIterator(Protocol):
    def next_issue(self, start_position: int) -> SpellingIssue | None: ...
    def cancel(self) -> None: ...
```

### 17.2 Recommended default

Use a locally packaged, Hunspell-compatible dictionary approach or another redistribution-safe local provider after licensing and dependency review. A pure-Python engine may simplify portable builds, while a native engine may offer better performance. The final choice must be tested for:

- Redistributable dictionary licenses
- Windows installation and portable mode
- Startup cost
- Suggestion quality
- Unicode behavior
- Memory use
- Thread safety
- User dictionary support
- Supported languages

The UI and controller must not know which engine is active.

### 17.3 Optional providers

Future providers may include:

- System spelling services
- LanguageTool or another local grammar-capable service
- Organization-specific terminology dictionaries
- Domain dictionaries

Online providers must be opt-in and disclose exactly what text is transmitted.

---

## 18. Tokenization and Skip Rules

### 18.1 Tokenization requirements

The tokenizer must support:

- Unicode letters
- Apostrophes within words
- Hyphenated compounds according to language rules
- Combining marks
- Smart apostrophes and quotation marks
- Language-specific casing
- Words adjacent to punctuation

Tokenization must not be based solely on ASCII regular expressions.

### 18.2 Default skip candidates

The first release should skip or specially handle:

- URLs
- Email addresses
- File paths
- IP addresses
- Tokens made only of digits
- Very long generated identifiers
- Known code spans, when the document format exposes them
- Hidden or protected text, where applicable

Configurable options should include:

- Ignore words in ALL CAPITALS
- Ignore words containing numbers
- Ignore Internet and file addresses
- Ignore mixed-case identifiers
- Check repeated words, reserved for a later proofing category

### 18.3 Language behavior

- Each issue must carry a language identifier.
- The document language is the default.
- If text ranges have language metadata, use it.
- Automatic language detection may be added later but must not silently override explicit document language.

---

## 19. Session Data Model

Suggested immutable or carefully managed data structures:

```python
@dataclass
class SpellingIssue:
    issue_id: str
    document_start: int
    document_end: int
    word: str
    normalized_word: str
    language: str
    context_text: str
    context_word_start: int
    context_word_end: int
    suggestions: tuple[str, ...]

@dataclass
class ReviewCounters:
    reviewed: int = 0
    changed: int = 0
    changed_all_occurrences: int = 0
    ignored_once: int = 0
    ignored_all_words: int = 0
    ignored_all_occurrences: int = 0
    added_to_dictionary: int = 0

@dataclass
class ReviewSession:
    scope_start: int
    scope_end: int
    original_caret: int
    original_selection: tuple[int, int]
    original_viewport_anchor: object | None
    document_revision: object
    current_issue: SpellingIssue | None
    counters: ReviewCounters
    ignored_words: set[tuple[str, str]]
    change_all_map: dict[tuple[str, str], str]
    action_history: list[ReviewAction]
    wrapped: bool = False
```

---

## 20. Document Editing and Range Integrity

### 20.1 Editor adapter

Do not bind spell review directly to a single control implementation. Create a `SpellReviewDocumentAdapter` responsible for:

- Reading text in a range
- Mapping document positions
- Replacing a range
- Starting and ending undo groups
- Creating stable markers or anchors when supported
- Restoring caret, selection, and viewport
- Reporting document revision changes
- Identifying protected or non-checkable ranges
- Preserving formatting around replacements

### 20.2 Position handling

Document offsets become stale after replacements. Use one of these approaches, in order of preference:

1. Stable editor markers or anchors.
2. A document change map that adjusts later offsets.
3. Rescan from the end of the changed range after every edit.

The implementation must verify that the text at the target range still matches the issue before applying a replacement. If it does not, safely rescan rather than editing the wrong text.

### 20.3 Undo integration

- Each Change is a normal document undo action.
- Change All should be one grouped undo action where possible.
- The entire session may optionally be grouped, but that must not prevent Undo Last Action inside the dialog.
- Undo labels should be meaningful where QUILL supports labeled undo, such as “Spelling change” or “Spelling Change All.”

### 20.4 External document changes

Because the initial dialog is modal, external edits should be rare. Still, the controller must detect:

- Document closure
- Editor destruction
- Plugin-driven edits
- Document reload
- Undo or redo from another command path

When the document revision changes unexpectedly, announce the condition and offer to restart or safely close the review. Never continue with unverified offsets.

---

## 21. Performance and Responsiveness

### 21.1 No UI freezing

- Tokenization and dictionary lookup for large documents must not block the UI for noticeable periods.
- The review may scan lazily, finding the next issue on demand.
- Prefetch a small number of upcoming issues in a worker thread if the provider is thread-safe.
- All wx control updates and document edits must occur on the main thread.
- Provide cancellation tokens for scans.

### 21.2 Progress behavior

If initial scanning takes long enough to be noticeable:

- Open a lightweight accessible progress state or announce “Preparing spelling review.”
- Keep Cancel available.
- Avoid indeterminate progress dialogs that steal focus repeatedly.
- Once the first issue is available, begin review while additional scanning continues.

### 21.3 Large documents

Target behavior:

- Opening the first issue should normally occur quickly without scanning the entire document.
- Memory use should remain bounded.
- Context extraction should read only nearby ranges where the editor adapter permits.
- Change All must avoid quadratic rescanning.

---

## 22. Completion and Wrap Behavior

### 22.1 End of scope

When the scanner reaches the end of the active scope:

- If checking a selection, complete the review.
- If checking from the caret and wrap is enabled, ask whether to continue from the beginning.
- The wrap prompt must state that review will continue only to the original caret position.

Suggested accessible prompt:

“QUILL reached the end of the document. Continue checking from the beginning to the original caret position?”

Buttons:

- Continue
- Finish

### 22.2 Completion summary

Display a small accessible summary dialog or a final state within the review dialog.

Include:

- Issues reviewed
- Individual changes
- Change All replacements
- Ignored occurrences
- Ignored words
- Words added to dictionaries
- Whether the review covered a selection or the full scope

Example:

“Spelling review complete. Reviewed 14 issues. Changed 9 occurrences, ignored 3 occurrences, and added 2 words to the dictionary.”

The primary button should be **Return to Document**.

### 22.3 Focus restoration

On completion or close:

- Return focus to the editor that launched review.
- Restore the original viewport when practical.
- Place the caret according to a documented rule.

Recommended rule:

- On completion, place the caret after the last reviewed or changed word.
- On cancellation before any action, restore the original caret and selection exactly.
- On close after actions, preserve the latest document position but restore editor focus.

A setting may later allow users to choose between returning to the original position and remaining at the last issue.

---

## 23. Settings

Add a **Spelling Review** settings group.

### 23.1 General

- Default language
- Start at caret and wrap to beginning
- Check selection when text is selected
- Maximum suggestions, default 10
- Context mode: Sentence, Paragraph, Lines
- Number of adjacent sentences or lines
- Remember dialog size and position

### 23.2 Ignore rules

- Ignore all-capital words
- Ignore words containing numbers
- Ignore URLs and email addresses
- Ignore file paths
- Ignore mixed-case identifiers

### 23.3 Accessibility

- Announcement verbosity: Concise, Balanced, Detailed
- Announce action results
- Announce progress number
- Automatically focus Context for each issue
- Reselect current word when returning to Context
- Play an optional subtle completion sound, off by default

### 23.4 Dictionaries

- Installed dictionaries
- Active document language
- Manage user dictionary
- Import and export user dictionary
- Reset session ignores, primarily a troubleshooting action

All settings must be keyboard accessible and screen-reader labeled.

---

## 24. Error Handling

Provide clear, actionable messages for:

- No spelling provider installed or available
- Dictionary missing for the current language
- Dictionary failed to load
- User dictionary cannot be written
- Document changed unexpectedly
- Replacement failed
- Provider returned invalid offsets or suggestions
- Background scan failed

Example:

“English United States spelling data is not installed. Choose another language or install the dictionary in Settings.”

Never fail silently. Never display a raw Python traceback to end users. Log diagnostic details with privacy-sensitive text redaction where possible.

---

## 25. Privacy and Security

- Local processing is the default.
- No document content is transmitted without explicit opt-in.
- Online providers must display a clear privacy explanation before first use.
- Diagnostic logs must not contain full context passages by default.
- When issue text is necessary for debugging, require an explicit diagnostic mode or redact surrounding content.
- User dictionary files must be stored in a user-writable application data location with safe permissions.
- Validate dictionary paths and imported dictionary files.
- Treat provider output as untrusted data and sanitize strings before displaying or logging them.

---

## 26. Localization

- All visible and spoken strings must be translatable.
- Do not construct sentences by concatenating fragments that cannot be reordered by translators.
- Progress pluralization must use locale-aware forms.
- Mnemonics must be configurable per locale.
- Context selection offsets must remain correct after line-ending normalization.
- Right-to-left text and bidirectional contexts must be tested, even if full first-release support is limited.
- Dictionary language names must be localized.

---

## 27. Accessibility Test Plan

### 27.1 Screen readers

Test manually with current supported versions of:

- NVDA
- JAWS
- Windows Narrator

Where feasible, include VoiceOver testing for any future macOS build, but Windows is the initial release target.

### 27.2 Required scenarios

For each screen reader:

- Launch with F7.
- Confirm initial focus is in Context.
- Confirm Context is announced as read-only and multiline.
- Confirm the current word is selected.
- Navigate Context by character, word, and line.
- Copy context text.
- Use Tab and Shift+Tab through every control.
- Select suggestions with arrow keys.
- Type a custom replacement.
- Activate every action by keyboard.
- Undo every supported action.
- Complete review and verify focus restoration.
- Cancel before and after edits.
- Test no suggestions.
- Test empty document and no errors found.
- Test wrap to beginning.
- Test large document scanning and cancellation.
- Test missing dictionary and provider failure.
- Test high speech verbosity and concise mode.
- Confirm there is no duplicate or overlapping speech severe enough to obscure the workflow.

### 27.3 Keyboard-only testing

- Complete an entire review without a mouse.
- Confirm no keyboard trap.
- Confirm visible focus at all times.
- Confirm all mnemonics.
- Confirm Escape behavior.
- Confirm Enter behavior in Context, Replacement, Suggestions, and buttons.

### 27.4 Visual testing

- Windows high contrast
- 200% and 300% scaling
- Large system text
- QUILL light and dark appearance
- Narrow and wide dialog sizes
- Long translated labels
- Long words and long suggestions

### 27.5 Content testing

- Apostrophes
- Hyphenated words
- Smart quotes
- Accented characters
- Combining marks
- Emoji adjacent to words
- URLs and email addresses
- File paths
- Code-like identifiers
- All-capital words
- Words containing digits
- Repeated occurrences with different capitalization
- Right-to-left text
- Very large paragraphs
- Multiple languages in one document

---

## 28. Automated Test Plan

### 28.1 Unit tests

- Tokenization
- Context extraction
- Context-relative selection offsets
- Case-preserving Change All
- Ignore All normalization
- User dictionary add and remove
- Session counters
- Undo action stack
- Scope boundaries
- Wrap boundaries
- Offset adjustment after replacement
- Stale issue detection
- Skip-rule behavior
- Speech message construction
- Pluralization inputs

### 28.2 Controller tests

Use a fake document adapter and fake provider to test:

- Session start
- First issue loading
- Every action transition
- No-suggestion behavior
- Provider failure
- Document revision mismatch
- Completion summary
- Focus restoration requests
- Cancellation

### 28.3 UI tests

Where QUILL's UI test framework permits:

- Control existence and accessible labels
- Tab order
- Enabled and disabled states
- Default button behavior
- Mnemonics
- Context selection
- Suggestions updating Replacement
- Dialog resizing
- Focus after each action

### 28.4 Performance tests

- Large plain-text document
- Large document with many unique misspellings
- Change All across thousands of occurrences
- Slow provider simulation
- Cancellation during scan
- Memory profile during long sessions

---

## 29. Telemetry and Diagnostics

No document text should be collected.

Optional local or opt-in aggregate diagnostics may include:

- Review started
- Review completed or canceled
- Provider name and version
- Dictionary language
- Number of issues reviewed
- Action counts
- Scan duration
- Error category

Do not collect words, suggestions, replacements, context, or document titles unless the user explicitly creates a diagnostic package and reviews its contents.

---

## 30. Suggested wxPython Component Structure

```text
quill/
  spelling/
    __init__.py
    models.py
    provider.py
    provider_registry.py
    tokenizer.py
    context_builder.py
    user_dictionary.py
    review_session.py
    review_controller.py
    document_adapter.py
    announcements.py
  ui/
    dialogs/
      spelling_review_dialog.py
      spelling_completion_dialog.py
      dictionary_manager_dialog.py
  settings/
    spelling_settings.py
  tests/
    unit/spelling/
    ui/test_spelling_review_dialog.py
```

Suggested primary classes:

- `SpellingReviewController`
- `SpellingReviewDialog`
- `SpellCheckProvider`
- `SpellProviderRegistry`
- `SpellReviewDocumentAdapter`
- `ContextBuilder`
- `UserDictionaryManager`
- `AccessibilityAnnouncer`
- `ReviewSession`
- `ReviewAction`

The dialog should contain presentation logic only. The controller owns workflow state. The provider owns spelling decisions. The adapter owns editor integration.

---

## 31. Event Flow

### 31.1 Start

1. User presses F7.
2. Command handler identifies active editor and review scope.
3. Controller captures caret, selection, viewport, document revision, and language.
4. Controller starts or prepares the spelling provider.
5. Controller finds the first issue.
6. Dialog opens.
7. Dialog renders issue.
8. Dialog selects the word in Context.
9. Deferred focus moves to Context.
10. Announcement service reports scope and issue progress.

### 31.2 Change

1. User activates Change.
2. Dialog sends action request to controller.
3. Controller validates issue range and current text.
4. Controller applies replacement through adapter.
5. Controller records action and updates counters.
6. Controller scans from the end of the replacement.
7. Dialog renders the next issue.
8. Focus returns to Context and selects the next word.
9. Announcement service reports the result and progress.

### 31.3 Completion

1. Controller detects no remaining issue in scope.
2. Controller handles wrap if applicable.
3. Controller finalizes counters.
4. Completion summary is presented.
5. User activates Return to Document.
6. Dialog closes.
7. Adapter restores focus and intended caret or selection state.

---

## 32. Acceptance Criteria

The feature is ready for public beta only when all of the following are true:

1. F7 starts Spelling Review from the active editable document.
2. A nonempty selection is checked without modifying text outside the selection.
3. The dialog uses standard accessible controls.
4. Initial focus lands in the multiline read-only Context field.
5. The active word is selected in Context.
6. Users can navigate Context by character, word, and line and can copy text.
7. Users can reselect the active word with a keyboard command.
8. Replacement and Suggestions are fully keyboard operable.
9. Change, Change All, Ignore Once, Ignore All, Add to Dictionary, Undo Last Action, and Close work correctly.
10. Every action results in a concise, understandable state update.
11. Focus never becomes lost or trapped.
12. Closing returns focus to the originating editor.
13. Changes participate correctly in QUILL's undo history.
14. Change All respects scope and capitalization rules.
15. Missing dictionaries and provider failures produce accessible errors.
16. Large documents do not freeze the UI.
17. Local processing is the default and no text is transmitted silently.
18. NVDA, JAWS, and Narrator can complete the workflow without mouse input.
19. The dialog works in high contrast and at 200% scaling without clipping essential controls.
20. Automated tests cover context offsets, session actions, scope boundaries, stale positions, and completion behavior.
21. User documentation explains F7, review scope, all actions, and keyboard commands.
22. Release notes describe the feature in user-centered language.

---

## 33. Phased Delivery

### Phase 1: Foundation

- Provider interface
- Tokenizer
- Document adapter
- Session model
- Context builder
- Basic local dictionary provider
- Unit tests

### Phase 2: Core dialog

- Modal dialog
- Context field
- Replacement field
- Suggestions list
- Change, Ignore Once, and Close
- Correct focus management

### Phase 3: Complete actions

- Change All
- Ignore All
- Add to Dictionary
- Undo Last Action
- Completion summary
- Wrap behavior

### Phase 4: Accessibility hardening

- Announcement service
- Verbosity settings
- Screen-reader test passes
- High contrast and scaling
- Keyboard and mnemonic audit
- Duplicate-speech tuning

### Phase 5: Performance and beta readiness

- Lazy scanning and prefetch
- Cancellation
- Large-document testing
- Error recovery
- Diagnostics
- Documentation
- Public beta feedback instrumentation that excludes document content

---

## 34. Future Enhancements

These should remain separate from the initial spelling release but can reuse the review framework:

- Grammar review
- Repeated-word detection
- Style and clarity review
- Terminology enforcement
- Custom organizational dictionaries
- Domain-specific dictionaries
- Thesaurus through a separate command
- “Explain this suggestion” for advanced providers
- Resume an interrupted review session
- Review only comments, headings, or selected structural regions
- Plugin-contributed proofing providers
- Braille-optimized announcement mode
- A compact review mode for experienced users
- Optional modeless review pane after the modal workflow is mature and proven accessible

---

## 35. Final Product Requirement

The F7 Spelling Review must never feel like an accessibility accommodation added after the fact. The read-only multiline Context field, selected current word, predictable focus, restrained announcements, reversible actions, and exact keyboard behavior are core product requirements.

A successful implementation will let a screen-reader user press F7, understand every issue in context, make or reject corrections confidently, recover from mistakes, finish the document, and return to writing without losing their place or wondering what QUILL just did.
