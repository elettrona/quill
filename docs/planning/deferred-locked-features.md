# Deferred / Locked Features — content preserved for future consideration

This file preserves user-facing documentation content for features that are
currently **locked off** in `quill/core/feature_catalog.py` and therefore must
not appear in the shipping user-facing docs (user guide, release notes, control
reference, PRD). When a feature is unlocked, move its content back into the
relevant doc.

Authoritative source of the locked state: `quill/core/feature_catalog.py`
(`locked_off=True`). As of this writing the locked-off features are:

- `core.rich_text_lens` — **Rich Text Lens** (native wxPython rich-text editing
  for `.rtf`). Locked off pending fuller screen-reader testing; RTF files open as
  plain text in the meantime. Docs must not claim native RTF editing ships.
- `core.bw_whisperer` — **BITS Whisperer** transcription suite (the whole branded
  menu). Deferred to QUILL 2.0. The underlying offline speech features still ship
  as plain QUILL features under **Tools > Speech**, so describe those, not the
  brand. (The watch-folder transcription action was rebranded to
  `Transcribe audio (offline)` in `quill/core/watch_transcribe.py`, so no
  "Whisperer" brand string ships in a default build.)
- `core.glow` — **GLOW Accessibility** (document accessibility audit/fix and
  engine updates). Hidden for now while the feature is finished.
- `future.publishing` — **Publishing** (publishing connections and provider-aware
  remote publishing). Locked off while the publishing-providers-framework branch
  is under review. The release notes already frame this as a *future* item, which
  is acceptable.
- `core.third_party_plugins` — **Third-Party Plugins** loader (SEC-8). Locked off
  until the plugin sandbox, signing, and review process ship. The release notes
  already frame third-party Quillins and a plugin marketplace as *future*.

---

## GLOW — control reference content (removed from docs/CONTROL_REFERENCE.md)

### GLOW Workflows Inside QUILL

#### GLOW Issue List

Lists all findings from the GLOW review. Arrow through the list to hear each issue. Press Enter or Tab to move to the detail panel and read the full explanation. Select one or more issues and press Fix Selected to apply automatic repairs.

| Key | Action |
|---|---|
| Tab | Move to detail |
| Alt+F | Fix selected |
| Ctrl+A | Select all issues |

#### Issue Detail

Shows the full description of the selected GLOW issue: what was found, why it matters, and what the automatic fix will do. Read this before applying a fix to understand the change.

#### Severity Filter

Filter the issue list by severity level. Error shows items that will likely break accessibility or structure. Warning shows items worth reviewing. Info shows stylistic or enhancement suggestions.

#### Before (Original)

Shows the original document text as it was before the GLOW fix was applied. Use this panel to verify what changed. Press Ctrl+C to copy the original if you want to compare it manually.

#### After (Fixed)

Shows the document text after the GLOW fix. Compare this to the Before panel to understand the change. Press Accept to apply the fix to your document, or Reject to discard it.

---

## BITS Whisperer / GLOW — release-notes framing (removed)

The 0.8.0 Beta 1 release notes previously:

- Titled the offline-speech section "## 2. Speak and listen, privately — BITS
  Whisperer" and routed it through "Tools > Speech > Whisperer" and
  "Whisperer > Download FFmpeg...". Corrected to the shipping flat **Tools >
  Speech** menu, with the section renamed to "offline speech".
- In "What came before", named **BITS Whisperer** and **GLOW** as consolidated
  apps and asserted "the speech suite is still BITS Whisperer." Removed; the
  history now names only what ships (ChapterForge audiobook workflow and the
  writing utilities) and the on-device speech features without the brand.
- In the roadmap, named the **GLOW** document-audit family and "accessibility-
  audit agents from GLOW." Reworded to generic accessibility-audit / document-
  audit capability (still future).
- In "About QUILL", named the **BITS Whisperer** speech suite. Reworded to
  "a private, on-device speech suite."

When BITS Whisperer / GLOW are unlocked, restore the brand naming and the
dedicated menu paths described above.

---

## GLOW — user guide content (removed from docs/user guide/userguide.md)

### GLOW Workflows Inside Quill

Glow in Quill is about guided confidence. It is not trying to turn the editor into a giant compliance dashboard. It is trying to make accessibility-aware review and safe deterministic fixes feel ordinary.

#### Audit flows

Use document audit when you want the whole file reviewed. Use selection audit when you only care about the paragraph, block, or snippet in front of you.

Audit results open as normal Quill tabs. You can read them, search them, compare them, or keep them open alongside the source.

#### Fix flows

Use selection fix for quick cleanup in place. Use document fix when you want Quill to generate a preview and immediately compare original versus fixed output.

This is where the native integration matters most. GLOW does not pull you away from your working context. It creates another working context beside it.

#### What GLOW is best at today

The first native slice is strongest with:

- plain text review
- Markdown cleanup
- HTML accessibility-aware cleanup
- link-text review
- heading spacing and heading-level sanity
- lightweight readability guidance

The 1.0 roadmap expands this into findings navigation, export-readiness workflows, and richer extraction-aware review for PDF and EPUB.

### GLOW menu (Tools) — removed from user guide

- **Audit Current Document**
- **Audit Selection**
- **Fix Current Document**
- **Fix Selection**

GLOW inside Quill is a guided layout and output workflow for deterministic text review. Today it focuses on plain text, Markdown, and HTML. It looks for issues such as: missing spaces after Markdown heading markers, heading-level jumps, generic link text, missing HTML language metadata, missing HTML image alt attributes, tables without HTML header cells, and dense paragraphs / plain-language friction.

### GLOW glossary entry — removed from user guide

**GLOW (Guided Layout and Output Workflow)** — QUILL's built-in text quality review system. GLOW audits a document for structural issues (heading hierarchy, list consistency, spacing, encoding artefacts) and offers deterministic fixes. Audit results open as readable QUILL tabs; fixing the document opens a named preview and starts a compare session. GLOW focuses on plain text, Markdown, and HTML.

### BITS Whisperer rollout / Status Page content — removed from user guide

The user guide previously documented a BITS Whisperer phased-rollout surface: a
two-mode (Recommended / Manual) speech-model selection flow, a **Provider Center**
and **Provider Status**, a live **Help > Status Page** that surfaced BITS
Whisperer download/provider status, and Preferences > General toggles
("Auto-open Status Page when BITS Whisperer model downloads start", "BITS
Whisperer safe mode lock"). These belong to the locked `core.bw_whisperer`
suite and were removed. The shipping offline-speech model management
(Recommended-for-your-computer guidance, background downloads) is documented in
the "Offline transcription (Tools > Speech)" section instead.
