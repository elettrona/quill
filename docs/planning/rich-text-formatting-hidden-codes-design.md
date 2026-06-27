# Rich Text Formatting with Hidden Codes — Design Note

Status: Draft for future consideration (not scheduled)
Author: design exploration, 2026-06-26
Scope: font family, point size, paragraph alignment, and color/highlight in the
QUILL editor, exported faithfully to Word (`.docx`), RTF, and HTML, while the
editing buffer stays free of visible markup.

## 1. Problem and intent

QUILL today can apply only bold, italic, and underline, and it does so by
writing inline markup (`**...**`, `<u>...</u>`) directly into a plain
`wx.TextCtrl`. There is no font family, point size, paragraph alignment, or
color, and Word export runs Markdown through Pandoc (`quill/io/export.py:219`),
whose docx writer silently drops inline CSS for font/size/alignment.

The product intent, stated by the user:

- The user should be able to apply font, style, point size, left/right
  justification, centering, alignment, and (later) color.
- **The formatting codes must be hidden from the user.** The document stays
  "simple, fast, and efficient." The user reads and edits clean text.
- The user can **interrogate** the document — ask "what is the formatting
  here?" — quickly and efficiently, and (being a screen-reader user) *hear* the
  answer.
- The tags are **materialized only at export**: "when exporting to Word, then
  you put the tags in and make magic happen here."

This reframes the feature away from a WYSIWYG/visible-markup editor toward a
clean buffer with a formatting layer that is queried on demand and serialized at
export time.

## 2. Why this fits QUILL's existing architecture

Three existing pieces make the hidden-codes model practical rather than a
rewrite:

1. **A rich intermediate model already exists.** `quill/io/rtf_model.py`
   defines `InlineSpan` / `RichParagraph` / `RichDocument` and the round-trip
   `markdown_to_rich` / `rich_to_markdown`, today carrying bold, italic, links,
   headings, and bullets. It is the natural shared model for every writer.

2. **An offset map between markup and visible text already exists.** The opt-in
   rich-text lens (`quill/ui/rich_text_surface.py`) maps visible caret offsets
   to markup offsets (`analyze_markdown`, `format_at_markdown_offset`). "Hide
   the codes but keep the caret honest" is exactly what that mapping does; it is
   currently used read-only.

3. **A spoken-formatting vocabulary already exists.**
   `quill/core/format_speech.py` (`describe_inline_format`) turns formatting
   flags into phrases like `"bold italic"` or `"heading level 2"`.
   Interrogation = read the formatting at the caret's mapped offset and pass the
   flags to this function.

4. **A precedent for font/size/alignment values already exists.**
   `quill/core/heading_styles.py` validates alignment against exactly
   `{left, right, center, justify}` and emits CSS declarations
   (`font-family`, `font-size: Npt`, `text-align`). The same validation and
   declaration logic generalizes from headings to arbitrary runs and
   paragraphs.

## 3. The materialized tag vocabulary

The tags are only ever produced at export (and on save, depending on the
storage model in section 4). They use Pandoc's generic attribute-span / fenced
-div syntax carrying explicit values. Because Word is written by our own
python-docx code, **we own attribute interpretation** — we are not limited to
Pandoc's named `custom-style`, so arbitrary "14pt Arial red" is expressible. The
syntax still degrades gracefully if ever fed to Pandoc.

```
Inline run:   [Hello world]{font-family="Arial" font-size="14" color="#C00000"}
Paragraph:    ::: {align="center"}
              Centered paragraph text.
              :::
```

Fixed, small vocabulary:

- Inline (run-level): `font-family`, `font-size` (points), `color`, `highlight`,
  plus existing `bold` / `italic` / `underline`.
- Block (paragraph-level): `align` in `{left, right, center, justify}`.

`quill/core/tagging.py:parse_attribute_pairs` already parses `key="value"`
pairs and is reused verbatim.

## 4. Hidden-codes storage — the key decision

The editor never shows tags. There are two coherent ways to honor that. They
differ only in where formatting lives while editing and on save; the export
pipeline is identical in both.

### Option A — Markup canonical, hidden in the view

- `Document.text` remains the Pandoc-span markup.
- The editor renders the visible text with codes stripped and uses the existing
  markup-to-visible offset map so edits and the caret map back to the markup.
- Saving `.md` writes the markup (tags present in the file, invisible in QUILL,
  visible only if the file is opened raw elsewhere).

Pros: reuses the lens/offset infrastructure directly; persistence is automatic
and self-contained; lowest risk. Cons: the on-disk `.md`/`.txt` is not literally
clean text; promoting the read-only lens to a fully editable surface is
non-trivial but bounded.

### Option B — Out-of-band overlay

- The buffer and `Document.text` are truly clean text everywhere — in the editor
  and in any saved `.txt`/`.md`.
- Formatting is a separate layer: a list of range annotations
  `{start, end, attrs}` over the plain text, plus per-paragraph `align`.
- Tags are synthesized only at export. For persistence between sessions the
  overlay is stored in a sidecar (e.g. `name.md` + `name.md.quillfmt` JSON) or a
  native QUILL container.

Pros: the document is literally clean text everywhere — the strongest match for
"simple, fast, efficient." Cons: ranges must be shifted on every insert/delete
(offset maintenance), and a persistence container/sidecar must be introduced
(QUILL has no native binary format today).

### Recommendation

Target **Option B** as the product end-state because it most faithfully
realizes the stated intent ("the document stays simple"; tags exist only at
export). Reach it in two moves to manage risk:

1. Build the shared model, builders, writers, menus, and interrogation against
   **Option A** first (markup canonical, hidden in the view). This reuses the
   most existing code and delivers the full user-visible behavior — clean
   editing feel, interrogation, faithful Word/RTF/HTML export — with the least
   new machinery.
2. Then introduce the out-of-band overlay and sidecar persistence (Option B) as
   a focused follow-up: a `FormatOverlay` that holds ranges, an edit-delta
   handler on `EVT_TEXT` that shifts ranges on insert/delete, and a
   serializer that emits the materialized markup for the writers. Because both
   options converge on the same `RichDocument` before any writer runs, the
   writers, menus, speech, and tests built in step 1 carry over unchanged.

The remainder of this note describes the model, writers, UI, and speech, all of
which are common to A and B.

## 5. Shared model and parsing

`quill/io/rtf_model.py`:

- `InlineSpan`: add `underline: bool`, `font_family: str | None`,
  `font_size_pt: int | None`, `color: str | None`, `highlight: str | None`.
- `RichParagraph`: add `align: str | None` (validate via
  `heading_styles._ALLOWED_TEXT_ALIGN`).
- `InlineFormat`: mirror the new inline fields so caret context can report them.
- `markdown_to_rich` / `rich_to_markdown`: teach the inline walker
  (`_walk_inline`) to recognize `[...]{...}` spans and `::: {...}` fenced divs,
  attach attributes to the active span/paragraph, and emit them back. Span
  markup is consumed without contributing visible characters, exactly as `**`
  is today, so caret-offset tracking stays correct.

## 6. Materialization helpers and editor commands

`quill/core/tagging.py`:

- `build_span_insertion(selected_text, attrs) -> InsertionResult` and
  `build_block_alignment(selected_text, align) -> InsertionResult`, alongside
  the existing `build_markdown_insertion` / `build_html_insertion`.
- A merge helper so applying font then size to the same selection merges into
  one span's attribute set rather than nesting spans (model on
  `heading_styles._merge_style_attr`).

`quill/ui/main_frame.py` + `quill/ui/main_frame_menu.py`:

- Thin command wrappers in the shape of `format_bold` (`main_frame.py:22548`):
  gate on `_feature_enabled("core.format")` and `_active_markup_surface()`,
  build, `_apply_insertion_result(...)`, then `_set_status(...)`. New:
  `format_set_font`, `format_set_size`, `format_align(which)`, and later
  color/highlight.
- Format-menu submenus after the Bold/Italic/Underline block: **Font**,
  **Size**, **Align** (Left/Center/Right/Justify), and Color/Highlight. New
  `NewIdRef`s near the existing format ids; bind alongside them. Keep logic in
  `tagging.py` / `rtf_model.py` so `main_frame.py` stays within the module-size
  budget (GATE-11).

In Option B these commands write to the overlay instead of inserting markup, but
their signatures, menu wiring, and announcements are identical.

## 7. Interrogation and screen-reader communication

- Extend `quill/core/format_speech.py:describe_inline_format` with the new
  fields so it speaks `"Arial, 14 point, centered, red"`; alignment comes from
  paragraph context.
- Add a **"Describe formatting at cursor"** command (with a hotkey) that reads
  `format_at_markdown_offset` at the caret and announces via `_set_status` /
  `announce` (`quill/platform/windows/sr_announce.py:37`). This is the primary
  "interrogate the document" affordance — explicit and quiet, so navigation does
  not chatter.
- Optionally, an on-caret-move announcement of formatting transitions
  (`describe_format_transition` already exists) behind a user toggle, for users
  who want continuous feedback.
- Every apply action announces its result (e.g. "Centered", "Arial 14 point
  applied").
- The opt-in rich lens (`rich_text_surface.py:256`) inherits the richer
  descriptions automatically, since it already calls `describe_inline_format`.

## 8. Export pipeline (identical for A and B)

All writers consume the extended `RichDocument`:

- **Word (`.docx`)** — new `quill/io/docx_writer.py`, replacing the Pandoc
  branch in `write_docx_document` (`export.py:219`). Per paragraph: set
  `paragraph.alignment` (`WD_ALIGN_PARAGRAPH`), map headings/bullets to Word
  styles; per run: set `run.bold/italic/underline`, `run.font.name`,
  `run.font.size = Pt(...)`, `run.font.color.rgb`, and highlight. Fall back to
  the existing Pandoc path if python-docx is unavailable, so docx export never
  hard-fails.
- **RTF** (`quill/io/rtf.py`) — emit `\ul`, a font table with `\fN`, `\fsN`
  (half-points), a color table with `\cfN`, and `\qc/\qr/\qj` alignment. Drop
  the now-supported items from `_UNSUPPORTED_FEATURES` (`rtf_model.py:451`).
- **HTML** (`markdown_to_html`, `export.py:172`) — render spans/divs to
  `<span style>` / `<div style>` reusing `heading_styles.declarations`.
- **Plain text** (`markdown_to_plain_text`) — strip wrappers, keep visible text,
  and use the existing "honest fidelity" reporting (`scan_*`,
  `rtf_model.py:465`) to warn that formatting is lost on plain-text save.

## 9. Dependencies and gates

- Add **`python-docx`** (pure-Python) to `pyproject.toml` dependencies;
  installation needs explicit approval.
- mypy stays scoped to `core` / `io`; the new/changed modules
  (`core/tagging.py`, `core/format_speech.py`, `io/rtf_model.py`,
  `io/docx_writer.py`) must type-check.
- First cut uses menus only, so the dialog inventory / button-contract gates are
  not triggered. A later "Font..." dialog would route through
  `_show_modal_dialog`.
- No new network egress.

## 10. Phasing

1. Inline run formatting: model fields (underline/font/size) + span
   materialization + `tagging` builders + Font/Size menus + interrogation;
   HTML/RTF render. (Storage Option A.)
2. Paragraph alignment: `RichParagraph.align` + fenced-div materialization +
   Align menu + interrogation.
3. python-docx Word writer; add the dependency.
4. Color / highlight across model, builders, all writers, and speech.
5. Out-of-band overlay + sidecar persistence (storage Option B) as the
   clean-document end-state, reusing everything above.

## 11. Verification

- Unit: extend `tests/unit/io/test_rtf_model.py` for span/div round-trip and
  offset stability; add `tests/unit/core/` cases for `format_speech` phrases and
  `tagging` builders/merge; add `tests/unit/io/test_docx_writer.py` that opens
  the produced `.docx` with python-docx and asserts `run.font.name/size`,
  `color.rgb`, and `paragraph.alignment`.
- Round-trip: markdown -> rich -> markdown is identity for the new attributes.
- End-to-end: `python -m quill`, apply Font/Size/Align to a selection, confirm
  the announcement and the at-caret description, Save As `.docx` and verify in
  Word, then export `.rtf` and `.html`.
- Lint/types: `ruff check .` and `mypy quill\core quill\io`.

## 12. Open questions for future scheduling

- Confirm storage Option A-then-B versus committing to B immediately.
- Sidecar format and naming for Option B persistence, and behavior when a `.txt`
  is opened in another editor (overlay is dropped vs. warned).
- Interrogation default: on-demand only, or on-caret-move behind a toggle.
- Font/size pickers: menu presets plus a "More..." accessible dialog later.
