# QUILL — Meet You Where You Are

### The screen-reader-first writing studio, built by the people who depend on it. This is the public beta, build 0.8.0 Beta 2.

*From Community Access. Free. Optional by design. Private by default. Yours to make quiet.*

This release document is the narrative companion to the **"0.8.0 Beta 2"**
section of `CHANGELOG.md` (the canonical, append-as-you-go log). It tracks what
changes in Beta 2 on top of Beta 1.

---

## What Beta 2 adds over Beta 1

Beta 2 carries forward everything in Beta 1 (private on-device speech,
document-to-audiobook production, braille proofreading, talking-book export,
guided proofing, multilingual narration, Mastodon posting, and the upgrade
hardening that makes betas safe to update). The list below is what is new,
fixed, or improved since Beta 1.

### Features

**Rich formatting that stays out of your way — hidden codes, spoken on demand.**
Beta 2's headline feature lets you apply real document formatting — **bold,
italic, underline, strikethrough, superscript/subscript, font family and point
size, text colour and highlight**, plus paragraph **alignment, line spacing,
indent, and named styles** — without ever seeing markup clutter in your editor.
The buffer stays clean, fast, plain text; the formatting rides along as invisible
codes. Apply it from the new **Format** menu (Font / Size / Align / Colour /
Highlight) or the accessible **Font...** dialog, and ask **"Describe formatting
at cursor"** to *hear* exactly what is in effect ("Arial, 14 point, centred,
bold"). An optional setting announces formatting changes as you move the caret.
The plain-text editor, undo, search, and AI all keep working on the same clean
text — nothing about your normal editing changes. RTF and Word documents
round-trip through this clean buffer and materialise back to real formatting on
export: **Word (.docx)** carries font, size, colour, highlight, and alignment via
a native writer (graceful Pandoc fallback if the optional `python-docx` extra is
absent), and **RTF** and **HTML** export carry the same. When a target format
genuinely cannot hold something, QUILL tells you before you commit rather than
dropping it silently.

**Keep your formatting in a plain-text file — Illuminations.** A plain `.txt` has
nowhere to store fonts, colours, or alignment, so saving formatted text as plain
text normally loses them. Beta 2 introduces the **Illumination** — named for the
decorative layer a scribe paints over a manuscript: the clean text is the
manuscript, and a small companion file, `yourfile.txt.illumination`, holds the
formatting beside it. The `.txt` stays genuinely plain everywhere else, and
reopening it *in QUILL* restores every font, colour, and alignment exactly. A new
**Settings → Editing → Saving formatted text as plain text** option lets you
choose to be asked each time, to always write an Illumination, or to save plain
and drop the formatting. If the `.txt` is edited elsewhere, QUILL notices the
mismatch and opens it plain rather than mis-applying old formatting; for one
self-contained file that keeps everything, save as Markdown, Word, or RTF.

### Fixes

- **The portable build launches again, and opens documents.** Double-clicking
  `quill.exe` in the portable bundle now starts QUILL (the bundle-root launcher
  was orphaned from its runtime), and setting QUILL as the default app for Word
  (or other) documents now opens the file when you press Enter on it in your file
  manager — previously nothing happened.
- **The AI Hub opens instead of crashing.** Activating the AI Hub on the 0.7.0
  line failed with a "lazy string" / lazy-loading error; it now opens to the
  provider/authorisation screen. (Community-Access/support #51, #53)
- **Far less double-spoken chatter.** "No misspellings found" was one of many
  actions QUILL spoke twice — once from the status bar (which already speaks) and
  again from a separate announcement. Across updates, GitHub, SSH, dictation, the
  copy tray, and profile switches, these now speak exactly once. (#728)
- **Report a Bug is keyboard-navigable again, and submitting no longer seems to
  lose your text** — you can Tab through the form, and QUILL reliably confirms the
  report was copied to your clipboard on submit for NVDA users. (#729)

### Enhancements

- **Hear how deep your indentation is.** Tab / Shift+Tab can now speak the new
  indentation depth — "4 spaces", "8 spaces", "1 tab" — instead of "Indented
  lines", honouring your tabs-vs-spaces and indent-width settings. Toggle with
  **Announce indentation depth on Tab** (Settings → Accessibility).
- **Quieter dialogs, your choice.** A new **Announce entering and leaving dialogs**
  setting (Settings → Accessibility) turns off the spoken "Entered / Exited *name*
  dialog" cues for people whose screen reader already announces dialogs.

---

## For testers

- Upgrade path: install over Beta 1 and confirm your settings, keymap, and
  documents carry forward (see `docs/release/upgrade-path-regression-0.8.0.md`).
- Fresh install: see `docs/release/fresh-install-regression-0.8.0.md`.
- Acceptance: `docs/release/user-acceptance-test-plan-0.8.0.md`.

## Release mechanics (do not announce yet)

Per the active release hold, the repo stays on Beta 1 labels and the update feed
stays where it is. No version bump, tag, push, or feed change until explicitly
approved. See `RELEASE.md` for the tag-time checklist.
