# QUILL 0.9.0 Beta 2 - Every Save Tells the Truth

### The screen-reader-first writing studio, built by the people who depend on it.

*From Community Access. Free. Optional by design. Private by default. Yours to make quiet.*

This is the narrative companion to the **"0.9.0 Beta 2 (in development)"**
section of `CHANGELOG.md` (the canonical, append-as-you-go log). Beta 2 is the
polish phase of the 0.9.0 line, and this cut is about a single promise: **when
QUILL saves or converts your document, everything it tells you afterward is
true** - the title bar, the modified flag, the announcement, the file on disk.

---

## The story of this release: Caroline's eight lines

A beta tester named Caroline wrote eight lines, pressed Ctrl+S, chose Word
format, named the file, and pressed Enter. QUILL said it saved. Then three
things went quietly wrong. The title bar still read "Untitled [modified]".
Pressing Ctrl+S again brought back the Save dialog with an empty name box, as
if the first save had never happened. And when she opened the file in Word,
her eight lines had been fused into one long unbroken line.

Every one of those symptoms traced to a real defect, and pulling that thread
uncovered more. This beta fixes all of it and then finishes the thought:
saving and converting in QUILL is now honest end to end, and it explains
itself in language a screen reader user can act on.

## What was wrong, and what is true now

**The title bar and the vanishing filename were one bug.** Word (.docx) was
the only Save As format that wrote the file without recording that the
document now lived there. The document stayed "untitled and modified" in
QUILL's mind, so the title never updated and the next save started from
scratch. Fixed - and a regression test now pins the contract for every format:
after any successful save, the document knows its path and knows it is clean.

**The fused lines were a translation dialect problem.** On its way to Word,
your document passed through a Markdown dialect in which a single line break
is a "soft wrap" - a suggestion, not a fact. Eight lines in, one paragraph
out. QUILL's rule is now uniform everywhere: **one editor line is one
paragraph**, in the native Word writer, in the Pandoc fallback, and in every
File > Export format - Word, OpenDocument, HTML, RTF, EPUB, and PDF alike.
What you hear line by line is what the exported document is.

**Your originals can no longer be destroyed by a reflex.** This one no user
had reported yet, and it was the most serious find of the audit. When you open
a PDF, an EPUB, a PowerPoint, or a spreadsheet, QUILL shows you *extracted
text* - the binary original cannot take that text back. Yet Ctrl+S would write
the text over the original file, destroying it. Now QUILL refuses, explains
("this document was opened as extracted text; saving over the original would
destroy it"), and opens Save As so your edits land somewhere that can hold
them. The same guard stops the reverse mistake: typing `notes.pdf` in Save As
no longer produces a Markdown file wearing a `.pdf` name that Acrobat cannot
open - QUILL offers File > Export, which makes a real PDF, or asks you to pick
a format it can genuinely write.

**A converting save now says what it did.** Saving as Word, RTF, or HTML has
always meant: the file on disk is converted; your editor keeps QUILL's clean
text; every further save converts again. That model is sound - and it was
silent. Now QUILL announces it the moment it happens: *"Saved as report.docx,
Word format. You are still editing QUILL text; each save converts it to
Word."* No mystery, no wondering which format you are "really" in.

**Failure sounds like failure.** A save that dies on a full disk or a locked
file now produces a clear spoken error and leaves your document exactly as it
was - never a crash, never a success message over a file that was not written.

## Small kindness, big difference: the filename suggestion

Save an untitled document and the name box now arrives pre-filled from your
document's first line - heading marks, quote markers, and bullets stripped,
Windows-forbidden characters removed, capped to a sane length. For a screen
reader user, an empty edit box is a dead end; a sensible proposal is a running
start. It is on by default, it only ever *suggests* (type anything over it),
and it never renames a document that already has a name. Turn it off with
"Suggest a filename from the first line" in Preferences if you prefer the
blank box.

## Choose your converter - and hear the trade-off before you commit

"Convert to Word" is not one operation. A structure-first engine and a
formatting-first engine both produce legitimate Word documents that differ in
what they keep. QUILL now lets you choose, and - this is the part we care
about - **describes the outcome of every choice in plain spoken language**
before you commit to it.

- **Word document reading engine** (Preferences > Editing): how a .docx
  becomes editable text on open. *Auto* (default) tries MarkItDown first.
  *MarkItDown* is fast and reliable - headings, lists, and tables come
  through; images, comments, and fonts do not. *Pandoc* keeps richer
  structure - footnotes and complex tables survive better - and if Pandoc is
  not installed the preference quietly degrades rather than failing your open.
- **Word document saving engine** (Preferences > Editing): how your text
  becomes a .docx on save. *Native* keeps QUILL's formatting codes - fonts,
  sizes, colors, highlights, alignment - and maps each editor line to one Word
  paragraph; it is the right choice for documents written in QUILL. *Pandoc*
  maps structure to Word styles - headings, lists, tables, links, footnotes -
  but drops the font, size, and color codes.
- **Convert File** gains a per-conversion engine choice (Auto / Pandoc /
  MarkItDown) with a description that updates as you arrow through it. Pick
  MarkItDown for a conversion it cannot honestly do and QUILL says so and
  offers Pandoc - it never silently substitutes an engine you did not choose.

The defaults are unchanged and right for almost everyone. The choices exist
for the days they are not.

**The receipts.** Every engine description is backed by a measured bake-off
(`docs/qa/converter-bakeoff.md`): seven fixture documents - nested lists, a
data table, real footnotes, links, right-to-left Arabic text, a hundred-section
document, and per-run formatting - through every candidate engine. MarkItDown
and Pandoc passed the full corpus. The raw python-docx extract loses tables,
footnotes, and link destinations, which is why it is only a last-resort
fallback. Two outside libraries were evaluated and settled for good: **pydocx**
is rejected permanently (it cannot even be imported on Python 3.10 or newer,
and its last release was 2016), and **mammoth**, though well maintained, is
not adopted because MarkItDown already covers its route at equal fidelity - with
a recorded decision tree for the day that changes.

## For the record

The full conversion behavior - what every Save As choice does, which formats
are protected, the one-line-one-paragraph rule, and the engine trade-offs - is
now documented in the user guide ("Saving in Different Formats" and "Choosing
a conversion engine"), specified in the PRD (section 5.3a.1.1a), and enforced
by io-layer tests rather than UI convention. Caroline: thank you. Eight lines
went a very long way.
