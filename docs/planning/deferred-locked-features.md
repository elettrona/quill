# Deferred / Locked Features — content preserved for future consideration

This file preserves user-facing documentation content for features that are
currently **locked off** in `quill/core/feature_catalog.py` and therefore must
not appear in the shipping user-facing docs (user guide, release notes, control
reference, PRD). When a feature is unlocked, move its content back into the
relevant doc.

Authoritative source of the locked state: `quill/core/feature_catalog.py`
(`locked_off=True`). The locked-off features, current as of QUILL 0.8.1 Beta 1, are:

- `core.glow` — **GLOW Accessibility** (document accessibility audit/fix and engine
  updates). Hidden while the feature is finished; its user-facing content is
  preserved below for when it unlocks.
- `core.voice_commands` — **Voice Commands** ("say a command out loud"), QUILL's
  hands-free **voice interaction**. Locked because it was tied to the now-removed
  Windows dictation path; it needs re-homing on the shipped offline dictation engine
  before it can return. No preserved content — it never shipped user docs.
- `core.rich_text_lens` — **Rich Text Lens** (native wxPython rich-text editing for
  `.rtf`). Locked pending fuller screen-reader testing; RTF opens as plain text in
  the meantime. Docs must not claim native RTF editing ships.
- `future.publishing` — **Publishing** — the *send* path (publishing connections and
  provider-aware remote publishing). Locked while the publishing-providers framework
  is reviewed; the read-only inbound half ships. Release notes already frame this as
  *future*.
- `core.third_party_plugins` — **Third-Party Plugins** loader (SEC-8). Locked until
  the plugin sandbox, signing, and review process ship. Release notes already frame
  third-party Quillins and a marketplace as *future*.
- `core.bw_whisperer` — **BITS Whisperer** brand menu (plus its `core.bw_transcription`
  and `core.bw_providers` sub-flags). **Superseded, not merely deferred:** every
  offline speech capability shipped as plain QUILL features under a flat **Tools >
  Speech** menu, so the branded rollout / Provider Center / Status Page it gated will
  not ship as specced. Its preserved content has been removed from this file.
  **Recommended follow-up:** retire the flag and its sub-flags from
  `feature_catalog.py` (a separate code change).

**All voice and speech *capabilities* are shipped and baked in** — offline dictation,
offline transcription and captions, read-aloud across SAPI 5 / DECtalk / Piper /
eSpeak / Kokoro and the ElevenLabs cloud voice, batch document-to-speech, and
audiobook building. The only speech-adjacent item still locked is
`core.voice_commands` (hands-free voice interaction), above; no speech content
remains preserved in this file.

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

## GLOW — release-notes / docs framing (removed)

Because `core.glow` is still locked, shipping docs must name accessibility-audit
capability generically, not by the **GLOW** brand:

- The roadmap's "**GLOW** document-audit family" and "accessibility-audit agents
  from GLOW" are reworded to generic accessibility-audit / document-audit capability
  (still future). Restore the **GLOW** naming when the feature unlocks.

**BITS Whisperer branding is retired (superseded), not deferred.** Earlier drafts
titled the offline-speech section "Speak and listen, privately — BITS Whisperer,"
routed it through "Tools > Speech > Whisperer," and named a "BITS Whisperer speech
suite" in About QUILL and the history. All of that is now the shipping flat **Tools >
Speech** menu and a plain "private, on-device speech suite" — there is no brand to
restore, so those notes are not preserved here.

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

