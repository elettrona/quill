# Fix Plan: Save As Conversion, Window Title, and Export Fidelity

> **STATUS: IMPLEMENTED 2026-07-04** on branch `fix/save-as-conversion` (6 commits).
> Tasks 1-8 are code-complete, tested, and documented. Task 9 (manual screen-reader
> spot checks) remains — it needs a human at a real build with JAWS/NVDA.
> Bake-off verdicts (docs/qa/converter-bakeoff.md): MarkItDown and Pandoc passed the
> full corpus; **pydocx rejected permanently** (cannot import on Python 3.10+ —
> `collections.Hashable` removed; last release 2016; it failed every fixture);
> **mammoth not adopted** (7/7 via its HTML writer, but MarkItDown already covers the
> route; if adopted later per the decision tree below, it would be **bundled**, never
> download-on-demand — frozen builds cannot pip-install at runtime). Only python-docx,
> MarkItDown, and Pandoc are ever used by QUILL; pydocx/mammoth were evaluated in a
> throwaway venv and never touched the codebase.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Save As genuinely convert (not just rename), make the window title and save state truthful for every format, protect binary originals from being overwritten with text, pre-fill filenames from the first line, and give users an informed choice of conversion engine.

**Architecture:** All fixes land in the existing layered split: format logic in `quill/io/export.py` (wx-free, unit-testable), UI policy in `MainFrame.save_file` / `save_file_as` in `quill/ui/main_frame.py`, settings in `quill/core/settings.py` + `settings_specs.py`.

**Tech Stack:** Python, wxPython, python-docx (bundled hard dependency), Pandoc (optional external tool), MarkItDown (bundled), LibreOffice headless (optional, legacy .doc/.ppt).

## Global Constraints

- No `wx` imports in `quill/io` or `quill/core` (mypy strict scope).
- All modal dialogs go through `_show_modal_dialog`, never `ShowModal()` directly.
- Atomic JSON writes via `core.storage.write_json_atomic`; document writes follow existing writer patterns.
- New user-facing strings must be speakable plain language (screen-reader-first product).
- Update release notes, user guide, PRD, and CHANGELOG as each bucket ships (incremental-docs rule).
- Run `pytest -m smoke -q` plus the targeted test file after each task; `ruff check .` before commit.
- No new dependencies without an explicit decision (pydocx/mammoth are evaluation-only in this plan).

---

## Part 1: What Caroline hit, decoded

Caroline's mail contains three distinct defects plus one design question. All were reproduced or traced in current `main`.

### Symptom 1: Title bar stuck at "Untitled [modified]" after Save As .docx

**Root cause (verified by repro):** `write_docx_document` in `quill/io/export.py:230-259` is the only writer that never calls `document.mark_saved(target)`.

- Plain text / HTML writers: `_write_utf8` calls `mark_saved` (`export.py:207`).
- Text / Markdown writer: `write_text_document` calls it (`quill/io/text.py:86`).
- RTF writer: `write_rtf_document` calls it (`quill/io/rtf.py:709`).
- DOCX writer: **neither** the python-docx branch **nor** the Pandoc fallback calls it.

Repro run against current main:

```
doc = Document(text='line one\nline two\nline three', path=None, modified=True)
write_document_as(doc, tmp / 'test.docx')
# doc.path -> None          (BUG: stays None)
# doc.modified -> True      (BUG: stays True)
# same test with .html/.rtf/.txt: path set, modified False (correct)
```

So after Save As .docx: the file IS written, the status line says "Saved as x.docx (Word)", but `document.path` stays `None` and `modified` stays `True`. `_refresh_title` (`main_frame.py:7285`) then correctly renders the *wrong* state: "Untitled [modified]".

### Symptom 2: Second Ctrl-S reopens Save As with an empty filename

Same root cause. `save_file` (`main_frame.py:9793`) sees `document.path is None` and falls back to `save_file_as`. The dialog's `defaultFile` comes from `_suggested_save_basename()` (`main_frame.py:9978`), which returns `""` for an untitled document when `first_line_as_title` is off (its default). One bug, both of Caroline's first two symptoms.

### Symptom 3: All lines collapsed into one paragraph in Word

**Root cause:** Caroline is on 0.8.0 Beta 1, which predates the native python-docx writer (it landed with the 2.0 rich-text hidden-codes work; python-docx is now a hard dependency in `pyproject.toml:33`). Her save went through the Pandoc fallback, which does:

```
convert_file_with_pandoc(source, target, from_format="gfm", to_format="docx")
```

In GFM, a single newline is a *soft wrap* -- consecutive lines join into one paragraph. Eight lines, one paragraph. Exactly her report.

**Current status:** the native writer preserves line breaks (verified: 3 editor lines -> 3 Word paragraphs, because `markdown_to_rich` in `quill/io/rtf_model.py:423` treats each editor line as one paragraph). **But the bug is still live in two places:**

1. The Pandoc fallback inside `write_docx_document` (`export.py:258`) still uses bare `"gfm"`.
2. Every File > Export format (`main_frame.py:8202`) uses `from_format="gfm"` -- so Export to ODT, EPUB, PDF, RTF, HTML via Pandoc all collapse single newlines today.

**Policy decision:** QUILL's editor is line-oriented; a line is a line (that is what a screen reader user hears). The canonical model already commits to this (`markdown_to_rich`: one editor line = one paragraph). Therefore every Pandoc call whose source is QUILL canonical text must use `gfm+hard_line_breaks`. Trade-off: a `.md` file authored elsewhere with soft-wrapped paragraphs will export one paragraph per source line -- consistent with what the QUILL editor displays, and the converter-preference feature (Part 5) gives an escape hatch later.

### Caroline's implicit design question, and Jeff's: "are we not still in markdown in the editor?"

Yes -- by design, and that is defensible, but it is currently *silent*. After Save As .docx:

- The editing surface keeps QUILL canonical markup (Markdown-style).
- `document.path` becomes `x.docx` (after Task 1); every subsequent Ctrl-S re-converts markup -> Word. This is coherent: the .docx on disk is always a faithful projection of the buffer.
- Reopening `x.docx` later converts Word -> Markdown via MarkItDown (`quill/io/structured.py:40-45`), which is a *different* converter than the one that wrote it, so round trips can drift (images, comments, complex tables).
- `_maybe_reload_surface_after_save_as` (`main_frame.py:10075`) only knows about the RTF rich lens vs plain; it says nothing for .docx.

The fix is honesty, not a behavior change: announce the model after a converting Save As ("Saved as x.docx, Word format. You are still editing QUILL text; each save converts it to Word."). See Task 5.

---

## Part 2: A worse bug found during the audit -- Ctrl-S destroys binary originals

`write_document_as` (`export.py:262-291`) falls through to the **verbatim text writer** for any extension it does not recognize. Two consequences:

1. **Data loss:** Open `report.pdf` (QUILL extracts its text for editing), press Ctrl-S. `document.path` is set, so `save_file` -> `write_document_as` -> suffix `.pdf` matches nothing -> `write_text_document` **overwrites the binary PDF with plain text**. The original is destroyed (a `.bak` backup is made only if backups cover it -- `backup_document` reads the old file first, so partial mitigation, but the on-disk PDF is gone). The same applies to `.epub`, `.pptx`, `.ppt`, `.xlsx`, `.xls`, `.doc`, `.odt`, `.pages`, `.sqlite`, `.db`.
2. **Corrupt output trap:** In Save As, typing `notes.pdf` (the "All files" filter allows anything) writes Markdown text into a file named `.pdf`, marks it saved, and reports success. Acrobat then fails to open it. Verified by repro:

```
doc4 = Document(text='# Title\nbody', path=None, modified=True)
write_document_as(doc4, tmp / 'weird.pdf')
# weird.pdf content: literally "# Title\nbody"  -- marked saved, no warning
```

There is no automatic guard: the read-only guard (`main_frame_power_tools.py:257`) is a manual user toggle, and `read_only_remote` only covers URL-opened documents. Task 3 adds the guard.

Deliberate non-guards (correct today, keep):
- `.brf` / `.brl` / `.pef` / `.ueb`: byte-for-byte text contract, verbatim write is the spec.
- `.json` / `.yaml` / `.toml` / `.xml` / `.ipynb`: opened as pretty-printed text of the same text format; writing the buffer back is what the user edited. (Note in docs: reformat-on-open means diff noise; out of scope.)
- Unknown text extensions (`.log`, `.py`, `.cfg`, ...): verbatim round trip is exactly right.
- `.csv`/`.tsv` in the grid surface: has its own save path (`_save_table_as_csv`); spot-check only.

---

## Part 3: The complete conversion matrix

Every combination QUILL can hit, with the engine used and the honest expected outcome. This section becomes the basis for the user-guide "What happens to my file" page (Task 8).

### 3a. Save As from the editor (canonical QUILL markup -> target extension)

| Target | Engine | Outcome today | After this plan |
|---|---|---|---|
| .txt, .text | verbatim writer | Markdown markup kept verbatim (#649); title updates | unchanged (documented) |
| .md, .markdown | verbatim writer | correct | unchanged |
| unknown text ext | verbatim writer | correct | unchanged |
| .html/.htm/.xhtml | native HTML renderer | standalone HTML, MathJax CDN script tag; title updates | unchanged |
| .rtf | native RTF writer | full hidden-codes fidelity; title updates | unchanged |
| .docx | python-docx native | line breaks OK, hidden codes OK, **title never updates** | mark_saved fixed (Task 1) |
| .docx (no python-docx) | Pandoc fallback | **line breaks collapse**, title never updates | hard_line_breaks + mark_saved (Tasks 1-2) |
| .pdf, .odt, .epub typed by hand | verbatim writer | **corrupt file that claims success** | blocked with a routing offer to File > Export (Task 3) |
| .doc, .ppt(x), .xls(x), .pages, .sqlite, .db typed | verbatim writer | **corrupt/mislabeled file** | blocked (Task 3) |
| .brf family | verbatim writer | byte-exact, correct | unchanged |

Also: "Save As Plain Text" (separate command, `main_frame.py:10137`) *strips* Markdown and offers keep-formatting / Illumination sidecar / plain choices. Unchanged; the matrix documents the difference between it and Save As -> .txt.

### 3b. Ctrl-S (Save) when the document already has a path

| Opened as | Engine on save | Outcome today | After this plan |
|---|---|---|---|
| .txt/.md/unknown/.brf | verbatim | correct round trip | unchanged |
| .rtf | native RTF | markup -> RTF, correct | unchanged |
| .docx | native docx | markup -> Word, but read side was MarkItDown so round trips can drift | mark_saved fixed; drift documented; engine choice in Part 5 |
| .pdf, .epub, .pptx, .xlsx, .doc, .odt, .pages, .sqlite | verbatim | **overwrites binary original with text** | guard: explain + route to Save As (Task 3) |
| .json/.yaml/.toml/.xml/.ipynb | verbatim | writes back the (pretty-printed) text; acceptable | unchanged, documented |
| .csv/.tsv grid surface | grid save path | own path | spot check only |
| URL-opened | n/a | already routed to Save a Copy | unchanged |

### 3c. File > Export (Pandoc; forces a save first, reads the saved file)

All routes use `from_format="gfm"` today, so **every one collapses single newlines**. After Task 2 all use `gfm+hard_line_breaks`.

| Export target | Notes beyond line breaks |
|---|---|
| Markdown / CommonMark / GFM | near-identity, dialect normalization |
| HTML | Pandoc fragment/standalone; differs from native Save As HTML (no MathJax tag) |
| Word (.docx) | Pandoc styles-mapped: headings/lists/tables/links/footnotes good; hidden-codes run attrs (font, size, color, highlight, alignment) dropped |
| ODT | same character as Pandoc docx |
| RTF | Pandoc RTF; weaker than QUILL's native RTF writer for hidden codes |
| Plain text | Pandoc flattening (different rules than QUILL's own stripper) |
| EPUB | produces a book; metadata minimal |
| PDF | **requires a PDF engine** (LaTeX or similar) that Pandoc shells out to; if absent, Pandoc errors -- Task 4 makes the failure message speakable and actionable |

### 3d. Export as DAISY (native, reads live buffer)

Line-per-line text-only book; no Pandoc involved. Spot check in Task 9 that line breaks and headings map to phrases correctly (they should -- it was built line-oriented).

### 3e. Open / Import (source format -> editor markup), with engine chain

| Source | Engine chain today | Expected outcome |
|---|---|---|
| .docx | MarkItDown -> python-docx raw extract fallback | headings/lists/pipe tables kept; fonts, colors, comments, images dropped |
| .doc | MarkItDown -> LibreOffice headless -> error | as above; requires LibreOffice for old binaries |
| .pptx / .ppt | MarkItDown -> native extract / LibreOffice | slide text, reading order approximate |
| .xlsx / .xls | MarkItDown -> capped openpyxl extract (50 rows x 20 cols) | table extract, not full sheet |
| | | |
| .pdf | native `extract_pdf_text` | text layer only; no OCR unless OCR tool invoked; layout flattened |
| .epub | native EPUB renderer | chapters flattened to markup |
| .pages | keynote-parser | text extract |
| .odt | native XML extract | text + basic structure |
| .rtf | native RTF reader | full hidden-codes fidelity (the reference round trip) |
| .html | read as text (no conversion on plain open) | raw HTML source in editor; File > Import > HTML converts via Pandoc |
| File > Import (any Tier-1) | Pandoc -> new Markdown tab, path=None | correct: forces an explicit Save As |

---

## Part 4: First line as filename

The machinery already exists and is wired everywhere it needs to be:

- `quill/core/titles.py` -- `suggested_title_from_text`: first non-empty line, strips `#`/`>`/bullets/HTML tags, sanitizes Windows-invalid characters, 60-char cap.
- `_suggested_save_basename` (`main_frame.py:9978`) feeds Save As, Save As Plain Text, Export, and DAISY export dialogs.
- Gated by setting `first_line_as_title` (`settings.py:78`), **default False** -- which is why Caroline saw an empty name box.

**Decision: flip the default to True** (Task 6). Rationale: it only ever pre-fills the name for an *untitled* document; the user can always type over it; it converts a blank, screen-reader-hostile edit box into a meaningful proposal; and it would have softened both of Caroline's symptoms. Users who explicitly turned it off keep their stored False (the loader only defaults when the key is absent).

---

## Part 5: Converter choice -- multiple engines, described outcomes, a default preference

Jeff's ask: when more than one converter can do a job (MarkItDown, Pandoc, python-docx, pydocx, ...), let the user pick, describe the expected outcome of each in plain speakable language, and let them set a default.

### Engine inventory and honest assessment

| Engine | Direction | Status | Character |
|---|---|---|---|
| python-docx | write .docx (and raw read fallback) | bundled hard dep | keeps QUILL hidden codes (font, size, color, highlight, alignment); one editor line = one Word paragraph; no footnotes/TOC fields |
| Pandoc | read+write many formats | optional external tool, download offer exists | structure-first: headings, lists, real tables, footnotes, links map to native Word/ODT styles; drops run-level font/size/color; needs hard_line_breaks flag |
| MarkItDown | read docx/pptx/xlsx/pdf -> Markdown | bundled | fast, good structure, pipe tables; drops images, comments, formatting runs |
| LibreOffice headless | legacy .doc/.ppt -> modern | optional, detected | fidelity of LibreOffice's own filters; slow first launch |
| pydocx | read .docx -> HTML only | **not adopted; evaluate-only** | unmaintained (last release ~2016), docx-to-HTML only, Python 3 support doubtful. Evaluate in the bake-off spike; expected verdict: reject |
| mammoth | read .docx -> HTML/Markdown | **not adopted; evaluate-only** | maintained, semantic style mapping, well-regarded; the credible alternative reader if MarkItDown fidelity disappoints |

The bake-off (Task 7, step 1) runs a small corpus (headings, nested lists, a table, footnotes, an image, tracked changes, RTL text, a long real-world doc) through each available read engine and records what survives. pydocx and mammoth are `pip install`ed into a scratch venv for the spike only.

**Mammoth adoption decision tree (agreed 2026-07-04):**

1. Bake-off first. If MarkItDown holds up on the corpus, mammoth is not adopted at all.
2. If mammoth wins on docx fidelity in ways users would notice, it is **bundled** -- never download-on-demand. It is a small, pure-Python, BSD-licensed pip package; the installed/portable builds cannot pip-install into a frozen environment at runtime, so a Python package is bundle-or-nothing. Download-on-demand remains reserved for external executables (Pandoc, LibreOffice) and large model assets (the assets-v1 pattern).
3. If bundled, it follows the python-docx precedent: imported lazily (like `docx_writer.py`), so a broken import degrades to the existing MarkItDown chain instead of hard-failing, and it appears as a third choice in `docx_read_engine` with its own speakable outcome description.
4. pydocx is expected to be rejected regardless (docx-to-HTML one-way, unmaintained since ~2016); the bake-off records the evidence so the verdict is documented, not folklore.

### User-facing design

New settings (Task 7), starting with the docx route because it is the one users actually hit; the pattern extends to other routes later:

- `docx_read_engine`: `auto` (default) | `markitdown` | `pandoc` -- honored in `read_structured_document`.
- `docx_write_engine`: `auto` (default) | `native` | `pandoc` -- honored in `write_docx_document`.
- `auto` means today's chain (MarkItDown-first read; python-docx-first write), so default behavior is unchanged.

Each option carries a speakable outcome description in `settings_specs.py`, e.g.:

- native: "Keeps QUILL formatting codes: fonts, sizes, colors, highlights, and alignment. Each editor line becomes one Word paragraph. Best for documents written in QUILL."
- pandoc (write): "Maps structure to Word styles: headings, lists, tables, links, and footnotes. Drops font, size, and color codes. Requires Pandoc."
- markitdown (read): "Fast and reliable. Headings, lists, and tables come through; images, comments, and fonts do not."
- pandoc (read): "Richer structure: footnotes and complex tables survive better. Requires Pandoc."

Per-operation override: the Convert File dialog (`quill/ui/convert_file_dialog.py`) gains an "Engine" choice (Auto / MarkItDown / Pandoc where applicable) with a live description StaticText tied to the selection via an `aria`-equivalent label (wx: the description is the control's sibling StaticText named in the accessible name). Save As itself stays engine-silent (it uses the default) to keep the core dialog simple; power users change the default in Settings.

---

## Part 6: Implementation tasks

Phase 1 (Tasks 1-4) is the correctness bucket and directly answers Caroline. Phase 2 (Tasks 5-6) is honesty and ergonomics. Phase 3 (Task 7) is the converter-preference feature. Task 8 is docs, Task 9 manual verification.

### Task 1: `write_docx_document` must mark the document saved

**Files:**
- Modify: `quill/io/export.py:230-259`
- Test: `tests/unit/io/test_export.py`

**Interfaces:**
- Produces: `write_docx_document(document, path)` now leaves `document.path == Path(target)` and `document.modified is False` on success, matching every other writer. No signature change.

- [ ] **Step 1: Write the failing tests**

Append to `tests/unit/io/test_export.py` (it already imports `Document` and `write_document_as`; follow the module's existing imports):

```python
def test_write_docx_marks_saved(tmp_path: Path) -> None:
    doc = Document(text="line one\nline two", path=None, modified=True)
    target = tmp_path / "out.docx"
    result = write_document_as(doc, target)
    assert result == target
    assert doc.path == target
    assert doc.modified is False


def test_write_docx_keeps_line_breaks(tmp_path: Path) -> None:
    import docx as _docx

    doc = Document(text="one\ntwo\nthree", path=None, modified=True)
    target = tmp_path / "breaks.docx"
    write_document_as(doc, target)
    paragraphs = [p.text for p in _docx.Document(str(target)).paragraphs]
    assert paragraphs == ["one", "two", "three"]
```

- [ ] **Step 2: Run tests to verify the first fails**

Run: `pytest tests/unit/io/test_export.py -k docx -q`
Expected: `test_write_docx_marks_saved` FAILS (`doc.path` is `None`); `test_write_docx_keeps_line_breaks` PASSES (native writer already correct -- it pins the regression Caroline hit on 0.8.0).

- [ ] **Step 3: Fix the writer**

Replace the body of `write_docx_document` in `quill/io/export.py`:

```python
def write_docx_document(document: Document, path: Path | None = None) -> Path:
    """Write a document's Markdown markup out as a Word (.docx) file.

    Prefers the native python-docx writer (:mod:`quill.io.docx_writer`), which
    carries QUILL's hidden-codes attributes -- per-run font family, point size,
    color, highlight, underline and per-paragraph alignment -- onto real Word runs
    and paragraphs. When python-docx is not installed, falls back to the Pandoc
    path, which maps headings, lists, emphasis, links, and simple tables to Word
    styles (but drops the font/size/color/alignment attributes). Either way the
    result is a properly structured, screen-reader-navigable document, and the
    document is marked saved at ``target`` like every other writer here.
    """
    target = Path(path or document.path or "")
    if not str(target):
        raise ValueError("A path is required to save this document.")

    from quill.io.docx_writer import python_docx_available, write_docx

    if python_docx_available():
        write_docx(document, target)
        document.mark_saved(target)
        return target

    import tempfile

    from quill.io.pandoc import convert_file_with_pandoc

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "source.md"
        source.write_text(document.text, encoding="utf-8", newline="\n")
        convert_file_with_pandoc(
            source, target, from_format="gfm+hard_line_breaks", to_format="docx"
        )
    document.mark_saved(target)
    return target
```

(Keep the `path or document.path` None-check semantics: `Path("")` is falsy via `str()`; if you prefer the module's existing style, keep the original two-line `target = path or document.path; if target is None: raise` form -- either is fine, be consistent with the file.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/io/test_export.py -k docx -q`
Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add quill/io/export.py tests/unit/io/test_export.py
git commit -m "fix(save-as): mark document saved after .docx write so the title and path update"
```

### Task 2: Hard line breaks on every Pandoc call that consumes QUILL canonical text

**Files:**
- Modify: `quill/io/export.py` (already done for the docx fallback in Task 1)
- Modify: `quill/ui/main_frame.py:8202` (`export_document`)
- Test: `tests/unit/io/test_export.py` (pandoc-gated), `tests/unit/ui/test_main_frame.py` (characterization)

**Interfaces:**
- Consumes: `convert_file_with_pandoc(source, target, *, from_format, to_format)` from `quill/io/pandoc.py`.
- Produces: all editor-sourced exports use `from_format="gfm+hard_line_breaks"`. Convert File / Batch Conversion of *arbitrary on-disk files* keep their detected source formats unchanged (a foreign `.md` keeps standard Markdown semantics there).

- [ ] **Step 1: Write the failing characterization test**

In `tests/unit/ui/test_main_frame.py`, follow the file's existing MainFrame-fixture pattern (it already stubs frames for save tests; copy the neighboring export/save test setup) and assert on the recorded pandoc call:

```python
def test_export_document_uses_hard_line_breaks(frame_fixture, monkeypatch) -> None:
    calls: list[dict] = []

    def _fake_convert(source, target, *, from_format, to_format):
        calls.append({"from": from_format, "to": to_format})

    monkeypatch.setattr("quill.ui.main_frame.convert_file_with_pandoc", _fake_convert)
    # ... use the fixture's established way to run export_document("docx")
    # with a saved document and a stubbed FileDialog returning a target path.
    assert calls and calls[0]["from"] == "gfm+hard_line_breaks"
```

(The exact fixture name and dialog stub differ; mirror the closest existing `export_document` or `save_file_as` test in that file rather than inventing new scaffolding.)

- [ ] **Step 2: Run to verify it fails**

Run: `pytest tests/unit/ui/test_main_frame.py -k hard_line_breaks -q`
Expected: FAIL with `from == "gfm"`.

- [ ] **Step 3: Change the call site**

In `quill/ui/main_frame.py` `export_document` (line 8199-8204), change:

```python
            convert_file_with_pandoc(
                self.document.path or Path(""),
                target,
                from_format="gfm+hard_line_breaks",
                to_format=format_name,
            )
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/unit/ui/test_main_frame.py -k hard_line_breaks -q` then `pytest tests/unit/io/test_export.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add quill/ui/main_frame.py tests/unit/ui/test_main_frame.py
git commit -m "fix(export): preserve editor line breaks in every Pandoc export (gfm+hard_line_breaks)"
```

### Task 3: Guard export-only extensions -- never write text over a binary, never ship a fake .pdf

**Files:**
- Modify: `quill/io/export.py` (new constant + exception + dispatch guard)
- Modify: `quill/ui/main_frame.py` (`save_file` pre-check, `save_file_as` post-dialog check)
- Test: `tests/unit/io/test_export.py`, `tests/unit/ui/test_main_frame.py`

**Interfaces:**
- Produces: `EXPORT_ONLY_SUFFIXES: frozenset[str]` and `class UnsupportedSaveFormatError(ValueError)` (attribute `suffix: str`) exported from `quill.io.export`; `write_document_as` raises it for those suffixes. UI callers catch it and route.

- [ ] **Step 1: Write the failing io tests**

```python
def test_write_document_as_refuses_export_only_suffixes(tmp_path: Path) -> None:
    from quill.io.export import UnsupportedSaveFormatError

    doc = Document(text="# Title\nbody", path=None, modified=True)
    for name in ("a.pdf", "a.epub", "a.odt", "a.doc", "a.pptx", "a.xlsx", "a.pages"):
        with pytest.raises(UnsupportedSaveFormatError):
            write_document_as(doc, tmp_path / name)
        assert not (tmp_path / name).exists()
        assert doc.modified is True  # untouched on refusal


def test_write_document_as_still_allows_brf_and_unknown_text(tmp_path: Path) -> None:
    doc = Document(text="hello", path=None, modified=True)
    write_document_as(doc, tmp_path / "a.brf")
    doc2 = Document(text="hello", path=None, modified=True)
    write_document_as(doc2, tmp_path / "a.log")
    assert (tmp_path / "a.brf").read_text() == "hello"
    assert (tmp_path / "a.log").read_text() == "hello"
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/unit/io/test_export.py -k export_only -q`
Expected: FAIL (no such exception yet; files get written).

- [ ] **Step 3: Implement in `quill/io/export.py`**

Add near the suffix sets:

```python
#: Formats QUILL can open (as extracted text) but cannot write back. Writing the
#: editor's markup to one of these would destroy a binary original (an opened
#: PDF, EPUB, spreadsheet...) or produce a file other apps cannot open (Markdown
#: text named .pdf). Save must refuse and steer the user to Save As / Export.
EXPORT_ONLY_SUFFIXES: frozenset[str] = frozenset({
    ".pdf", ".doc", ".odt", ".epub", ".pages",
    ".ppt", ".pptx", ".xls", ".xlsx", ".sqlite", ".db",
})


class UnsupportedSaveFormatError(ValueError):
    """Save targeted an extension QUILL cannot convert the editor text into."""

    def __init__(self, suffix: str) -> None:
        super().__init__(
            f"QUILL cannot save directly to {suffix}. Use File > Export for this format."
        )
        self.suffix = suffix
```

Add `"EXPORT_ONLY_SUFFIXES"` and `"UnsupportedSaveFormatError"` to `__all__`. In `write_document_as`, immediately after computing `suffix`:

```python
    if suffix in EXPORT_ONLY_SUFFIXES:
        raise UnsupportedSaveFormatError(suffix)
```

- [ ] **Step 4: Run io tests**

Run: `pytest tests/unit/io/test_export.py -q`
Expected: PASS (including the pre-existing dispatch tests).

- [ ] **Step 5: Wire the UI policy**

In `quill/ui/main_frame.py` import `EXPORT_ONLY_SUFFIXES` alongside the existing `write_document_as` import. In `save_file` (`main_frame.py:9789`), after the `read_only_remote` check and before the `path is None` check:

```python
        path = self.document.path
        if path is not None and path.suffix.lower() in EXPORT_ONLY_SUFFIXES:
            # e.g. an opened PDF: the buffer is extracted text. Writing it back
            # would destroy the binary original, so route to Save As instead.
            self._show_message_box(
                f"{self.document.name} was opened as extracted text. QUILL cannot "
                f"write {path.suffix} files directly, so saving over the original "
                "would destroy it. Choose a new name and format (Markdown, Word, "
                "HTML, RTF, or text), or use File > Export.",
                "Save",
                self._wx.ICON_INFORMATION | self._wx.OK,
            )
            self.save_file_as()
            return
```

In `save_file_as`, after `target = self._resolve_save_target(...)` and before leaving the dialog `with` block is fine too, but simplest is right after the block:

```python
        if target.suffix.lower() in EXPORT_ONLY_SUFFIXES:
            wx_mod = self._wx
            export_names = {".pdf": "pdf", ".odt": "odt", ".epub": "epub"}
            fmt = export_names.get(target.suffix.lower())
            if fmt is not None:
                answer = self._show_message_box(
                    f"QUILL saves Markdown, Word, HTML, RTF, and text directly. "
                    f"{target.suffix} goes through Export instead, which converts "
                    "with Pandoc. Open Export now?",
                    "Use Export for this format",
                    wx_mod.ICON_QUESTION | wx_mod.YES_NO | wx_mod.YES_DEFAULT,
                )
                if answer == wx_mod.YES:
                    self.export_document(fmt)
                return
            self._show_message_box(
                f"QUILL cannot save to {target.suffix}. Choose Markdown, Word, "
                "HTML, RTF, or text in the Save as type list.",
                "Format not supported",
                wx_mod.ICON_INFORMATION | wx_mod.OK,
            )
            return
```

- [ ] **Step 6: Write and run the UI characterization test**

Mirror the closest existing `save_file` test in `tests/unit/ui/test_main_frame.py`: open a fake document with `path=tmp_path/'x.pdf'`, stub `_show_message_box` to record and return OK, stub `save_file_as`, call `save_file`, assert the pdf bytes on disk are untouched and `save_file_as` was invoked.

Run: `pytest tests/unit/ui/test_main_frame.py -k export_only -q`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add quill/io/export.py quill/ui/main_frame.py tests/unit/io/test_export.py tests/unit/ui/test_main_frame.py
git commit -m "fix(save): refuse to overwrite binary originals or write fake .pdf/.odt/.epub files"
```

### Task 4: Honest failure handling on the save path

**Files:**
- Modify: `quill/ui/main_frame.py` (`save_file`, `save_file_as` around `_write_document_to_disk`)
- Test: `tests/unit/ui/test_main_frame.py`

**Interfaces:**
- Consumes: writers raise `OSError` on disk failure, `PandocUnavailableError` / `PandocConversionError` on the fallback path, `UnsupportedSaveFormatError` from Task 3.
- Produces: on failure, document state is untouched (`modified` stays True, `path` unchanged), the status line and a message box say what failed, and no "Saved" sound plays.

- [ ] **Step 1: Write the failing test** -- stub `_write_document_to_disk` to raise `OSError("disk full")` inside a `save_file_as` run; assert the method returns without crashing, `document.modified` is still True, and the recorded status starts with "Could not save".

- [ ] **Step 2: Run to verify failure** (currently the exception propagates out of the handler).

- [ ] **Step 3: Implement** -- in both `save_file` and `save_file_as`, wrap the `_write_document_to_disk(...)` call:

```python
        try:
            self._write_document_to_disk(self.document, target)
        except UnsupportedSaveFormatError as error:
            self._show_message_box(str(error), "Save", self._wx.ICON_INFORMATION | self._wx.OK)
            self._set_status("Save cancelled: format not supported")
            return
        except OSError as error:
            self._show_message_box(
                f"Could not save {target.name}: {error}", "Save", self._wx.ICON_ERROR | self._wx.OK
            )
            self._set_status(f"Could not save {target.name}")
            return
```

(`save_file` uses `self.document.path` in place of `target` for the messages. The Pandoc error types are already imported at module top for export; include them in the except tuple on the docx fallback path.)

- [ ] **Step 4: Run tests** -- `pytest tests/unit/ui/test_main_frame.py -k could_not_save -q`. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add quill/ui/main_frame.py tests/unit/ui/test_main_frame.py
git commit -m "fix(save): report save failures honestly instead of crashing or claiming success"
```

### Task 5: Say what a converting Save As actually did

**Files:**
- Modify: `quill/ui/main_frame.py` (`save_file_as`, after `_refresh_title()`)
- Test: `tests/unit/ui/test_main_frame.py`

**Interfaces:**
- Consumes: `format_label_for_path` from `quill.io.export` (already imported).
- Produces: an `_announce` after a Save As whose format is a conversion (docx/rtf/html), one sentence, screen-reader-first.

- [ ] **Step 1: Write the failing test** -- Save As to `x.docx` with a recorded `_announce`; assert the announcement contains "still editing" and "Word".

- [ ] **Step 2: Run to verify failure.**

- [ ] **Step 3: Implement** -- in `save_file_as`, after the existing `self._set_status(f"Saved as {target.name} ...")` line:

```python
        converted = target.suffix.lower() in ({".docx", ".rtf"} | _HTML_SUFFIXES_UI)
        if converted:
            self._announce(
                f"Saved as {target.name}, {format_label_for_path(target)} format. "
                "You are still editing QUILL text; each save converts it to "
                f"{format_label_for_path(target)}."
            )
```

where `_HTML_SUFFIXES_UI = {".html", ".htm", ".xhtml"}` is a module-level constant (or import `_HTML_SUFFIXES` from `quill.io.export` after promoting it to a public name `HTML_SUFFIXES` -- do the promotion; private cross-module imports fail lint).

The existing `_maybe_reload_surface_after_save_as` prompt stays as-is (RTF rich lens only); do not offer a docx reload -- a reload would round-trip through MarkItDown and silently lose formatting the user just saved. Note this in the user guide instead.

- [ ] **Step 4: Run tests.** Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add quill/io/export.py quill/ui/main_frame.py tests/unit/ui/test_main_frame.py
git commit -m "feat(save-as): announce format conversion and that the editor stays QUILL text"
```

### Task 6: First-line filename suggestion on by default

**Files:**
- Modify: `quill/core/settings.py:78` and `quill/core/settings.py:601`
- Test: `tests/unit/core/test_settings.py` (or the settings test module that asserts defaults; find it with `grep -r "first_line_as_title" tests/`)

- [ ] **Step 1: Write/adjust the failing test** -- assert `Settings().first_line_as_title is True` and that loading a settings payload *without* the key yields True while an explicit `false` stays False.

- [ ] **Step 2: Run to verify failure.**

- [ ] **Step 3: Implement** -- `first_line_as_title: bool = True` at `settings.py:78`; `data.get("first_line_as_title", True)` at `settings.py:601`. Update the spec description in `settings_specs.py:218-226` to say it is on by default.

- [ ] **Step 4: Run** `pytest tests/unit/core -k first_line -q` plus `pytest -m smoke -q`. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add quill/core/settings.py quill/core/settings_specs.py tests/unit/core
git commit -m "feat(save-as): suggest a filename from the first line by default"
```

### Task 7: Converter engine preference (docx route first) + engine bake-off

**Files:**
- Spike output: `docs/qa/converter-bakeoff.md` (results table; no dependency changes)
- Modify: `quill/core/settings.py` (+ loader + specs): `docx_read_engine`, `docx_write_engine`
- Modify: `quill/io/structured.py` (`read_structured_document` docx branch honors `docx_read_engine` -- thread the setting in via a parameter with default `"auto"`, keeping the module wx-free and settings-free)
- Modify: `quill/io/export.py` (`write_docx_document` gains `engine: str = "auto"` parameter; `write_document_as` gains and forwards `docx_engine: str = "auto"`; `MainFrame._write_document_to_disk` passes the setting)
- Modify: `quill/ui/convert_file_dialog.py` (Engine choice + outcome description text)
- Test: `tests/unit/io/test_export.py`, `tests/unit/io/test_structured.py`, `tests/unit/ui/test_convert_file_dialog.py`

**Interfaces:**
- Produces: `write_docx_document(document, path, *, engine="auto")` where `engine in {"auto", "native", "pandoc"}`; `read_structured_document(path, encoding="utf-8", *, docx_engine="auto")` where `docx_engine in {"auto", "markitdown", "pandoc"}`. `"auto"` reproduces today's chains exactly.

- [ ] **Step 1: Run the bake-off spike.** Build a corpus of 8 fixture docx files (headings+nested lists, a 5x4 table with a merged cell, footnotes, an embedded image, tracked changes, RTL Arabic paragraph, hyperlinks, a 100-page real document). In a scratch venv, convert each with MarkItDown, Pandoc (`--from docx --to gfm`), python-docx raw extract, pydocx, and mammoth. Record per engine: structure survival, table fidelity, footnote survival, crash/hang, speed. Write `docs/qa/converter-bakeoff.md` with the table and a one-paragraph verdict per engine. Expected verdicts: pydocx rejected (unmaintained, HTML-only); mammoth noted as future optional reader; MarkItDown stays default; Pandoc offered as the richer optional reader.

- [ ] **Step 2: Write failing engine-forcing tests** for `write_docx_document(engine="pandoc")` (skipped when Pandoc absent, follow the existing pandoc-skip marker in the test tree) and `engine="native"`, and for `read_structured_document(docx_engine=...)` with monkeypatched engines recording which was called.

- [ ] **Step 3: Implement the parameters and the settings plumbing.** Settings fields:

```python
    docx_read_engine: str = "auto"   # auto | markitdown | pandoc
    docx_write_engine: str = "auto"  # auto | native | pandoc
```

Specs (choices-type settings with the outcome descriptions from Part 5, keywords `("word", "docx", "converter", "engine", "pandoc", "markitdown")`). `MainFrame._write_document_to_disk` reads `self.settings.docx_write_engine` and forwards; the open path (`read_open_document` callers) forwards `docx_read_engine` the same way `word_mode` already travels.

- [ ] **Step 4: Convert File dialog engine choice.** Add a labelled `wx.Choice` "Conversion engine" (Auto / MarkItDown / Pandoc as available) plus a StaticText description that updates on selection; both keyboard-reachable in the existing tab order; description text is the same speakable copy as the settings specs. Honor it in the conversion request.

- [ ] **Step 5: Run** `pytest tests/unit/io -q` and the dialog test; `python -m quill.tools.dialog_inventory` gate if it covers this dialog. Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add quill/core/settings.py quill/core/settings_specs.py quill/io/structured.py quill/io/export.py quill/ui/main_frame.py quill/ui/convert_file_dialog.py docs/qa/converter-bakeoff.md tests/
git commit -m "feat(convert): user-selectable docx conversion engine with described outcomes"
```

### Task 8: Documentation -- the process must surface ALL conversion-outcome knowledge

The bake-off results and the Part 3 matrix are not internal notes; they become the user-facing knowledge base about what every conversion does. Four destinations, each written richly, not as stubs:

**Files:**
- Modify: user guide (save/export chapter): add "What happens to my file when I choose a format" -- the Part 3 matrix in prose plus small tables; the Save As vs Save As Plain Text vs Export distinction; the "you are still editing QUILL text" model; the engine preference with the outcome description of every engine choice; what each engine keeps and drops, per format, in plain speakable language.
- Modify: `docs/QUILL-PRD.md` save/export section: extension policy table, `EXPORT_ONLY_SUFFIXES` invariant, hard-line-breaks policy statement, the engine-preference model and the mammoth decision tree.
- Modify: `CHANGELOG.md`: entries per task under the next release heading.
- Modify: release notes (docs/release/): after completion, a rich narrative section -- what Caroline's bug was, what changed for saving and exporting, the new binary-file protection, the first-line filename suggestion, and the engine choice, written for end users with the conversion-outcome knowledge inline (not a link out).

- [ ] Update all four as each phase lands (incremental-docs rule), commit with the phase; the release-notes narrative is written last, after Task 9's spot checks confirm behavior.

### Task 9: Manual spot-check script (screen reader session)

Run with JAWS or NVDA on a real build; this is the verification Caroline's report deserves.

- [ ] **Caroline's exact repro:** new document, 8 lines, Ctrl-S, switch type to Word, name it, Enter. Verify: title bar reads "name.docx - QUILL for All ...(no [modified])"; second Ctrl-S saves silently with no dialog; the announcement from Task 5 speaks; the file opens in Word with 8 paragraphs.
- [ ] **Save As each type:** .txt, .md, .html, .rtf, .docx -- title updates, status speaks the format label, file opens in Notepad/browser/WordPad/Word respectively.
- [ ] **Typed rogue extension:** Save As, type `notes.pdf` -- the Export routing prompt appears; accepting lands in Export as PDF; declining returns safely.
- [ ] **Binary protection:** open any .pdf and any .xlsx, edit, Ctrl-S -- the explanation speaks, Save As opens, the original file on disk is byte-identical.
- [ ] **Export each Tier-1 format** (with Pandoc installed) from an 8-line doc -- line breaks survive in docx/odt/html/rtf outputs; PDF either produces a file or speaks the missing-PDF-engine error clearly.
- [ ] **DAISY export** of the same doc -- 8 phrases in the book.
- [ ] **First-line title:** untitled doc starting `# Trip Report`, Ctrl-S -- name box pre-filled "Trip Report".
- [ ] **Engine preference:** flip `docx_write_engine` to pandoc, Save As .docx, open in Word -- structure present, fonts absent, matching the described outcome.

---

## Part 7: Decisions taken (flag if you disagree)

1. **Line-break policy:** one editor line = one paragraph everywhere (native writers already do this; Pandoc paths get `+hard_line_breaks`). The editor is the source of truth a screen reader user hears.
2. **Save As .txt stays verbatim** (#649 round-trip contract); "Save As Plain Text" remains the stripping path. Documented rather than changed.
3. **No auto-reload after Save As .docx** -- reload would round-trip through a different engine and silently lose what was just saved. Announcement instead.
4. **`first_line_as_title` default flips to True.** Stored explicit False is respected.
5. **pydocx is evaluated, not adopted** -- it is a docx-to-HTML one-way reader, unmaintained for years; mammoth is the credible alternative if the bake-off shows MarkItDown gaps. Neither becomes a dependency inside this fix.
6. **Engine preference starts with the docx route only** (`auto` default preserves current behavior); the settings pattern generalizes to pptx/xlsx/pdf routes later if the bake-off motivates it.

## Suggested reply points for Caroline

- The title bar and the reopened empty dialog were one bug: after a Word save, QUILL wrote the file but forgot to record that the document now lives there. Fixed.
- The lost line breaks were the old converter treating single newlines as soft wraps; the new native Word writer keeps every line, and the fallback converter is now told to do the same.
- Bonus from her report: QUILL now refuses to overwrite an opened PDF/spreadsheet with plain text, and suggests a filename from the first line when saving something untitled.
