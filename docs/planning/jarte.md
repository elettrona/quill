## Executive take

**QUILL is not lacking in ambition or breadth.** Compared with Jarte, QUILL is vastly broader: document rescue, OCR, braille, DAISY, speech, dictation, AI, GLOW, remote files, vaults, Story Studio, formats, extensions, and strong screen-reader-first architecture. QUILL 0.9.0 is described as the final feature beta before 1.0, with the remaining work focused on bug fixes, polish, and reliability. ([quillforall.org][2])

But **Jarte is better at one thing QUILL should take seriously**: it feels like a lightweight, familiar, office-ready word processor first, and a power tool second. QUILL’s biggest risk is not missing “power.” It is missing the calm, obvious, WordPad-like document workflow for someone who wants to write, format, print, send, and move on.

## Jarte’s feature set, grouped

### Core product

Jarte offered a tabbed interface, opened **RTF, DOC, and DOCX**, started quickly, stayed small, ran portably from USB/CD/Dropbox, supported touch scrolling, included automatic screen-reader mode, offered “Clickless Operation,” had spell checking with custom dictionaries, supported templates, exported HTML/PDF, supported bookmarks, favorites, recent files/folders, drag and drop, email sending, zoom, and detailed help. ([jarte.com][3])

### Editing and formatting

Jarte supported inserting pictures, hyperlinks, tables, page breaks, equations, and embeddable objects. It also had paste-plain, multi-level undo/redo, sorting, font styling, text color, highlight, favorite/recent fonts, format brush, paragraph alignment, indents, lists, spacing, tab stops, and paragraph format brushing. ([jarte.com][3])

### Printing and page layout

This is a major Jarte strength. It had print preview, definable margins, reverse page order, odd/even-page printing, and a header/footer designer with page numbers, file dates, current dates, file names, custom text, font control, positioning, and first-page suppression. ([jarte.com][3])

### Tools

Jarte included a 25-item Clip List, screen capture, special-character keyboard, Reference Bar for dictionary/thesaurus/encyclopedia lookup, WordWeb integration, word count, and access to system file search. ([jarte.com][3])

### Jarte Plus

Jarte Plus added printable manuals and shortcut cards, custom shortcut keys, customizable Quick Bar buttons, AutoHotkey scripting, background spell checking, auto-correct, auto-capitalize, split view, AutoOutline, project files, separate “Jarte personalities,” persistent saved clips, custom Reference Bar buttons/links, document notes, file hyperlinks with text targets, smart quotes, status-bar word count, Roman numeral page numbering, and priority support. ([jarte.com][4])

### Screen-reader behavior

Jarte’s screen-reader mode was not just “works with a screen reader.” It changed the interface: when a recognized screen reader was running, Jarte removed visually oriented features and modified other interfaces to make them more screen-reader readable. It also had a manual clipboard phrase workaround for enabling screen-reader mode when detection failed, including for JAWS. ([jarte.com][5])

## Where QUILL is lacking compared with Jarte

### 1. Print and page-layout polish

This is the biggest concrete gap I see.

QUILL’s user guide says **Page Setup** and **Print** exist, but the public QUILL materials I found do not describe anything close to Jarte’s mature print workflow: print preview, margins, odd/even/reverse page printing, header/footer designer, page-number/date/file-name insertion, first-page header/footer suppression, or Roman numeral page numbering. ([quillforall.org][6])

**What QUILL should steal:** an accessible “Print Studio” with spoken page setup, header/footer templates, page-number formats, margins, preview summary by page, odd/even printing, reverse order, and “first page different.” For blind users, this matters because printing is where inaccessible visual layout usually becomes guesswork.

### 2. A first-class “simple word processor” mode

Jarte wins psychologically. It says: open, type, format, print, send. QUILL says: writing studio, document rescue, OCR, AI, braille, audio, vault, GLOW, formats, remote files, extensions. That is powerful, but it can feel like a cockpit.

QUILL has feature profiles — Essential, Writer, Developer, Accessibility Professional, Full QUILL — and custom profiles, which is good. ([quillforall.org][7]) But Jarte’s default product identity is simpler. The user does not have to understand a feature system to get a quiet word processor.

**What QUILL should steal:** a named **“Jarte/WordPad-style Writer”** profile or onboarding choice: File, Edit, Insert, Format, Search, Tools, Help; hide AI, GLOW, vault, audio studio, remote files, and developer features. Make it feel like a friendly replacement for WordPad/Jarte, not like the entire QUILL universe.

### 3. Direct rich-document editing as the default experience

Jarte’s advantage came from sitting directly on the Windows RTF engine. It could handle familiar rich document actions natively: fonts, color, paragraph formatting, pictures, page breaks, equations, objects, printing, and WordPad/Word compatibility. ([jarte.com][1])

QUILL’s public docs describe a different philosophy: the main path is plain text/Markdown with formatting carried through invisible codes, Illuminations, or conversion to Word/RTF/HTML. QUILL also has an optional RTF “Rich text lens,” but it is off by default and keeps Markdown underneath. ([quillforall.org][8])

That is elegant for screen-reader-first authoring, but it means QUILL may still feel less like a direct replacement for Jarte, WordPad, or a small word processor.

**What QUILL should steal:** make the Rich Text lens more discoverable and offer a “Rich Document” workflow for users who want WordPad-like editing without learning Markdown, Illuminations, or export semantics.

### 4. Inline images and embedded document objects

Jarte could insert pictures, hyperlinks, tables, page breaks, equations, and embeddable objects. ([jarte.com][3]) QUILL has strong support for links, tables, equations, OCR, and exporting Word equations, but the public docs emphasize OCR image-to-text, extracted document workflows, and text/Markdown/Word conversion rather than a rich accessible object model for inline images. ([quillforall.org][6])

**What QUILL should steal:** accessible inline object placeholders: “Image: filename, alt text present/missing,” “Page break,” “Equation,” “Embedded object removed for safety.” Allow inserting images with required alt text and export them cleanly to DOCX/HTML/EPUB.

### 5. Header/footer and page-number authoring

This deserves its own callout because it is different from printing.

Jarte had a header/footer designer with page numbering, dates, file names, custom text, font control, positioning, and first-page suppression. Jarte Plus added Roman numeral page numbering. ([jarte.com][3]) I did not find comparable QUILL public documentation beyond general Page Setup/Print and export support. ([quillforall.org][6])

**What QUILL should steal:** a keyboard-first Header/Footer Builder with presets like “title left, page number right,” “filename and date,” “different first page,” “Roman numerals for front matter,” and “start numbering at page N.”

### 6. Clipboard depth and non-text clip support

QUILL’s Copy Tray is excellent for screen-reader users: twelve persistent text slots, labels, pinning, peek-before-paste, search, system tray access, and spoken feedback. ([quillforall.org][6])

But Jarte had a **25-item Clip List**, and Jarte Plus could remember saved clips between sessions and store often-used clips, scraps, images, sounds, or small documents. ([jarte.com][3]) QUILL’s current public docs describe Copy Tray slots as holding text explicitly copied into them. ([quillforall.org][6])

**What QUILL should steal:** a separate **Clipboard History / Clip Library** mode beyond Copy Tray: more than 12 items, optional automatic capture, images/files as named objects, and accessible descriptions for non-text clips.

### 7. Reference Bar / classic lookup tools

Jarte had a Reference Bar for instant dictionary, thesaurus, encyclopedia, grammar aid, quotes, WordWeb integration, and user-defined keyword lookup links. ([jarte.com][1])

QUILL has spell check, thesaurus, optional AI thesaurus, and language tools, which are strong. ([quillforall.org][8]) But Jarte’s Reference Bar is more like a small writer’s research shelf, not an AI feature.

**What QUILL should steal:** a non-AI **Reference Bar** or “Look Up” command group: dictionary, thesaurus, encyclopedia, quotes, web search, WordWeb/local dictionary integration, and user-defined lookup targets. This would be especially useful for people who do not want AI involved in basic writing reference tasks.

### 8. Touch, mouse, and low-vision tablet workflows

Jarte explicitly supported touch-screen gestures such as finger swipe scrolling and pinch zoom, plus clickless operation to reduce mouse clicking. ([jarte.com][3]) QUILL’s public identity is keyboard-first and screen-reader-first; I did not find touch-screen support described in the public QUILL materials I reviewed. QUILL does have low-vision profiles and themes, but touch/tablet ergonomics are not prominent. ([quillforall.org][6])

**What QUILL should steal:** not as a top priority for blind keyboard users, but as a broader accessibility win: large touch targets, pinch zoom, swipe reading, reduced-click controls, and a “low-vision tablet” mode.

### 9. Jarte “personalities” as separate work identities

QUILL has profiles, custom profiles, sessions, snapshots, notebooks, and Story Studio. That is more powerful than Jarte in many ways. ([quillforall.org][6])

But Jarte Plus “personalities” were wonderfully concrete: separate shortcuts could launch different Jarte personalities, each with its own settings, favorite files, favorite fonts, clips, and project context. ([jarte.com][4])

**What QUILL should steal:** launchable **work personas**: “School,” “BITS,” “QUILL docs,” “Python coding,” “Office admin,” each with its own profile, open session, favorites, copy tray set, default folder, keymap, and optional startup documents.

### 10. Split view for simple document comparison

QUILL has Compare Mode and keyboard-first diff, which is probably better for screen-reader review. ([quillforall.org][8]) But Jarte Plus had a very simple split-view mode for viewing two documents or two views of the same document side by side. ([jarte.com][4])

**What QUILL should steal:** a simple “Open Second View” command: same document, independent cursor; or two tabs in a synchronized comparison view. Keep Compare Mode, but also offer the plain old “look at two things at once” workflow.

### 11. AutoOutline as a frictionless office feature

QUILL has Markdown heading numbering, structure navigation, lists, Story Studio, and a much deeper long-form architecture. ([quillforall.org][8]) Jarte Plus’s AutoOutline, however, was simple: indentation level controls numbering style, and the outline renumbers itself as you edit. ([jarte.com][4])

**What QUILL should steal:** an **Accessible AutoOutline** command that works in plain text/Markdown and exports cleanly to Word. This would be useful for meeting agendas, policies, bylaws, reports, and board packets.

### 12. Email/send workflow

Jarte could send documents by email directly. ([jarte.com][3]) QUILL’s public docs describe Mastodon posting, experimental read-only WordPress, remote files, GitHub, SFTP, and publishing workflows, but I did not find a simple “send current document by email” workflow in the public materials I reviewed. ([quillforall.org][8])

**What QUILL should steal:** “Send as Email,” “Send as Attachment,” and “Copy as Email Body,” with pre-send spell check and explicit consent.

### 13. Screen-reader simplification triggered by detection

QUILL is far more intentionally screen-reader-first than Jarte overall. QUILL supports NVDA, JAWS, and Narrator, treats parity as a requirement, detects screen readers, routes announcements, and tests accessibility claims through automated gates. ([quillforall.org][7])

The specific Jarte idea still worth stealing is this: when screen-reader mode turns on, the interface removes visually oriented features that would slow users down. ([jarte.com][5]) QUILL has profiles and quieting controls, but a user may still need to choose the right profile or learn the settings. ([quillforall.org][7])

**What QUILL should steal:** an optional “screen-reader detected: simplify visual-only controls?” first-run prompt, with choices like Essential, Writer, Braille Power User, Accessibility Professional, and Full QUILL.

## The highest-value Jarte ideas for QUILL

If I were turning this into a roadmap, I would prioritize:

1. **Print Studio**: accessible print preview, margins, headers/footers, page numbering, odd/even/reverse printing.
2. **Jarte-style Writer profile**: a calm WordPad/Jarte replacement mode.
3. **Rich Document workflow**: easier RTF/DOCX editing without making users understand conversion.
4. **Inline object placeholders**: images, page breaks, equations, embedded objects, alt text, export-safe.
5. **Reference Bar**: non-AI dictionary/thesaurus/encyclopedia/quotes/user lookups.
6. **Clip Library**: bigger clipboard history, optional auto-capture, non-text clips.
7. **Work Personas**: launchable profiles tied to sessions, favorites, copy tray sets, and folders.

## Bottom line

QUILL does not need to become Jarte. QUILL is already aiming at something much larger.

But Jarte is a warning: **a beloved accessible editor does not win only by having the most features. It wins by making ordinary writing feel light, obvious, and trustworthy.** The places QUILL is most lacking are the old-school office-writing edges: printing, headers/footers, simple rich documents, inline objects, reference lookup, and a truly quiet “just write and print” personality.

[1]: https://www.jarte.com/ "FREE Word Processor Based on Microsoft's WordPad Engine"
[2]: https://quillforall.org/docs/release0.9.0-beta1.html "release0.9.0-beta1"
[3]: https://www.jarte.com/features.html "Jarte's Word Processing Features"
[4]: https://www.jarte.com/jarte_plus.html "Exclusive Jarte Plus Features"
[5]: https://www.jarte.com/help_new/screen_reader_mode.html "Screen Reader Mode"
[6]: https://quillforall.org/docs/userguide.html "userguide"
[7]: https://quillforall.org/faq.html "FAQ - QUILL"
[8]: https://quillforall.org/ "QUILL - Screen-reader-first writing environment"
