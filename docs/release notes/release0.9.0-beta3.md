# QUILL 0.9.0 Beta 3

## A quick follow-up, driven by your bug reports.

*From Community Access. Free. Optional by design. Private by default.*

Beta 3 is a short, focused release: fix what Beta 2 testers found, close out every open community bug report, and ship eight small accessibility-first features that were ready to go. This document explains every new keystroke in full, step by step — no feature here requires you to guess at a shortcut.

This is the friendly companion to the **"0.9.0 Beta 3"** section of `CHANGELOG.md`. The shorter text under **Help > What's New** and **Check for Updates** comes from that changelog; this document tells the fuller story.

---

## Fixes

### Pandoc imports (EPUB and others) could silently produce an empty document

A community member reported — and correctly root-caused — a serious one: importing an EPUB via **File > Import > EPUB Book** could leave you with a completely empty document while Quill reported success. The cause was a subtle encoding mismatch: Quill's subprocess helper decoded Pandoc's output using the system's default locale encoding rather than an explicit one, and on a Windows machine whose locale defaults to a legacy code page instead of UTF-8, Pandoc's UTF-8 output could fail to decode — silently leaving Quill with nothing, while still reporting success. Output is now always decoded as UTF-8 (with a safe fallback so even a genuinely non-UTF-8 byte never crashes or blanks the result), and the Pandoc import path now explicitly fails loudly if it ever gets no output, instead of quietly handing you a blank page. This affected every tool that goes through Quill's subprocess helper, not just EPUB import, so this is a broader reliability fix than it first appears.

### Speech and Dictation crashed on open

Four testers independently reported the same crash: opening **Tools > Speech > Speech and Dictation** raised a `TypeError` instead of showing the dialog, on both the Offline and Online tabs. The dialog's constructor had grown two new required arguments (`kokoro_ok`, `kokoro_can_install`) that the one place calling it was never updated to supply. Both are now populated the same way the existing Vosk availability flags already are, and the dialog opens normally again.

### A rare crash when a keystroke arrived before the first document existed

On macOS, a very early or very late keystroke — before the first document tab finished setting up, or after the last one closed — could raise `AttributeError: 'MainFrame' object has no attribute 'editor'` from the global keyboard hook. One of the three checks in that code path read the editor directly where its neighbors already defended against exactly this case; all three are now consistent.

### A shared dialog crash, already fixed before Beta 2 shipped

"Go to Entry in Notebook" and its sibling tree-navigator dialogs could crash with a `wxAssertionError` on open. We traced this to a fix that had already landed on the development branch before Beta 2's code froze but is worth confirming here for anyone who hit it on a Beta 2 build: the dialog no longer tries to expand its (intentionally hidden) root node.

### Quill no longer offers crash recovery for exits with nothing to diagnose

Two automatic crash-recovery submissions showed logs with only routine background activity right up to the moment QUILL stopped — no exception, no error, nothing actionable. That pattern is consistent with the process being closed externally (a forced shutdown, a killed task) rather than a bug inside QUILL. This is now a real fix, not just an observation: Quill checks the log for genuine error evidence (an `ERROR`, `CRITICAL`, or a traceback) before offering crash recovery at all. An inconclusive exit no longer shows the "Quill detected an unclean exit" dialog — there's simply nothing to prompt you about. A real crash still logs an error and still offers recovery exactly as it always has; only the no-evidence case changed. Your autosave snapshot is never touched by this — it's still on disk either way, this just controls whether Quill asks you about it.

---

## New: eight small, accessibility-first additions

### Quill can add itself to your PATH

The Windows installer now offers an opt-in **"Add Quill to PATH"** task (unchecked by default, next to the existing file-association tasks in the installer's task list). Turn it on and `quill` resolves from any terminal, or from a shortcut's Target field, without typing the full install path. Per-user only — no elevation, no other account touched. If you've already installed Beta 2 or earlier, re-run the installer and tick the box to add it retroactively.

### Temporary bookmark — one keystroke, no dialog

Sometimes you just want to mark "right here" and come straight back, without naming anything or picking from a list.

- **Ctrl+Shift+K** sets a single, unnamed jump point at the cursor. Nothing is asked — you'll hear "Temporary bookmark set" and that's it.
- **Alt+Shift+K** jumps back to it. No picker, no dialog — you'll hear "Jumped to temporary bookmark."

Setting a new one silently replaces the old one — there is only ever one temporary bookmark at a time. It does **not** persist between sessions: closing and reopening Quill forgets it. That's by design, not a bug — it's disposable scratch state for the next few minutes of work, distinct from Quill's existing named bookmarks (**Set Bookmark...**, **Go To Bookmark...**, **List Bookmarks...**, still on their usual keys), which are unlimited and do persist per document across restarts.

### Numbered quick bookmarks (0-9) — direct keystrokes, no menu or sub-mode

Ten fixed jump slots, one per digit, each reachable in a single keystroke with nothing in between:

- **Alt+Shift+0** through **Alt+Shift+9** sets the jump point for that slot at the cursor. You'll hear "Quick bookmark 3 set" (for example).
- **Ctrl+Alt+Shift+0** through **Ctrl+Alt+Shift+9** jumps straight to that slot. You'll hear "Jumped to quick bookmark 3," or "Quick bookmark 3 is not set" if you haven't set it yet.

These are direct chords, not a menu item and not a sub-mode you have to enter first — press the keystroke from anywhere in the document and it fires immediately, the same one-step rhythm as the temporary bookmark above. Under the hood they're stored as ordinary named bookmarks (with generated names like "Quick 3"), so they persist per document across restarts exactly like your named bookmarks already do — nothing new to configure, nothing new to lose.

### Spell Check Word (Alt+F7) — instant, single-word spelling check

**Alt+F7** checks just the word at your cursor. If it's spelled correctly, Quill says so and nothing else happens. If it's misspelled, a small list opens with the same choices you'd get from the right-click spelling menu: suggested corrections at the top, then **Add to Dictionary**, then **Ignore**. Arrow to your choice and press Enter (or Escape to cancel without changing anything) — you're back to typing in one step, without launching a full-document Spell Check pass.

If you've used the "press F7 on a focused word" workflow in Microsoft Office, this is that, for Quill. Use **F7** (Spelling Review) when you want to work through a whole document systematically; use **Alt+F7** when you just want to check the one word you're looking at right now.

### Ranked spelling (Ctrl+Shift+L) — misspellings sorted by how often they recur

**Ctrl+Shift+L** opens the misspelling list just like **Alt+Shift+L** (the existing **Misspelling List**) already does, but in a different order: instead of the order the words appear in your document, the word that recurs the *most* comes first. Each entry also shows how many times it occurs, e.g. "teh (Ln 12, Col 4, 8 occurrences)."

This is a Kurzweil-1000-style feature, requested directly by a longtime user: a single OCR misread or a repeated typo (`teh` for `the`, say) is usually the fastest way to clear the bulk of a long misspelling list, since fixing one entry — mentally, or via Add to Dictionary — effectively resolves every occurrence of that word at once. Arrow through the ranked list, press Enter to jump to any occurrence, same as the regular list. The document-order **Misspelling List** on **Alt+Shift+L** is unchanged and stays the default for anyone who prefers reviewing top-to-bottom.

### Ranked Spelling Review (Alt+Shift+F7) — the full guided F7 experience, in ranked order

Where **Ctrl+Shift+L** above is a quick jump-to-occurrence list, **Alt+Shift+F7** is the other half of the same request: the *entire* guided F7 Spelling Review — **Change**, **Change All**, **Ignore Once**, **Ignore All**, **Add to Dictionary**, **Undo Last**, all of it — but walking issues most-frequent-word-first instead of top-to-bottom.

This is the version built for genuinely messy documents — a rough OCR scan, a document with a systematic autocorrect error, or anything with the same handful of mistakes repeated many times. Press **Change All** on the top entry and the ranking re-evaluates immediately: whatever word is now most frequent among what's left rises to the front automatically, so you keep working through the document's worst offenders first instead of hunting for them one at a time in reading order. **F7** (document order) and **Alt+Shift+F7** (ranked order) use the exact same dialog and the exact same set of actions — only the order issues are presented in differs.

### Favorite folders — a short, curated list for instant access

Also requested directly, modeled on a feature from Kurzweil 1000: a short list of folders you mark as favorites, distinct from Windows' recent-folders list. Recent folders tracks what you *recently* opened; favorites tracks what you actually want fast access to — a folder you use constantly but haven't touched in months (the classic example: a document your boss might ask about at any moment) belongs in favorites even though it long ago aged out of any recency-based list.

- **Ctrl+Alt+Shift+A** — **Add Favorite Folder.** Adds the current document's containing folder to your favorites list. (Save the document first if it's untitled — Quill needs a real folder to add.)
- **Ctrl+Alt+Shift+R** — **Remove Favorite Folder...** Opens a list of your current favorites; choose one to remove it.
- **Ctrl+Alt+Shift+O** — **Open From Favorite Folder...** Opens Quick Open (see below) scoped to your favorites.

All three are also on the **File** menu, under a new **Favorite Folders** submenu, if you'd rather navigate by menu than remember the chords.

### Open From Favorite Folder — a VSCode-style Quick Open, scoped to your favorites

Press **Ctrl+Alt+Shift+O** and a small dialog opens with a text box already focused. Start typing part of a filename and the list below filters live, case-insensitively, across every one of your favorite folders at once — the same type-to-filter rhythm as VSCode's Ctrl+P. Arrow down to a match (each entry shows which favorite folder it came from, since two favorites can both contain a file with a similar name) and press Enter, or click **OK**, to open it. Escape or **Cancel** backs out with nothing changed.

Two scope notes worth knowing: the scan is **top-level files only** within each favorite folder, not recursive — this keeps the filter instant even if one of your favorites happens to contain a huge nested tree, and it matches the "short, curated list" philosophy favorites are built around. And because Quill doesn't have a single-project-root "workspace" concept the way VSCode does, this Quick Open is intentionally scoped to your favorites rather than searching your whole disk.

### Accessible code folding

Fold a heading section or a fenced code block (the ` ``` `...` ``` ` kind, as in Markdown or a code block inside a document) to reduce clutter while you work — without ever losing access to what's folded.

- **Ctrl+Alt+Shift+F** — **Toggle Fold.** Folds or unfolds the smallest foldable region containing your cursor. You'll hear exactly what happened: *"Folded: 14 lines under 'Chapter Two'"* when you fold, *"Unfolded: 'Chapter Two'"* when you unfold.
- **Alt+Shift+]** — **Next Fold.** Jumps to the next foldable region's boundary, whether it's currently folded or not, announcing its label, fold state, and line count on arrival: *"'Chapter Three', expanded, 22 lines."*
- **Alt+Shift+[** — **Previous Fold.** Same as Next Fold, but backward.
- **Ctrl+Alt+Shift+L** — **List Folds...** Opens a dialog listing every foldable region in the document at once, each showing its current fold state and line count. Pick one to jump straight to it — the fastest way to get an overview of a long document's structure and fold state without stepping through it region by region.

We designed this one carefully, and it's worth explaining why it works differently from folding in most other editors. There, folding hides lines visually, and arrow-key navigation silently skips right over a folded block — a screen reader user has no way to tell whether content vanished or was just collapsed, which is a real, long-standing accessibility complaint about folding in mainstream code editors. Quill's folding never does that: **the document text is never touched, and ordinary arrow-key, word, and line navigation is never intercepted.** Fold state is purely something the four commands above announce and act on — arrow through a folded region character by character and you will read every word in it, exactly as if it weren't folded. Folding only changes what a *jump* command does, never what you can reach by moving normally, so nothing you can reach is ever made silently unreachable.

---

## A note on how this release came together

Every fix in this release traces back to a specific community bug report — nine in total, from #939 through #953, every one now closed with an explanation of what was found and (where applicable) what changed. The two "no evidence in the log" reports (#940, #948) turned into a real feature rather than being quietly closed as unreproducible: Quill now recognizes that pattern itself and stops asking about it. And two of the seven new features — ranked spelling and favorite folders — came directly from a tester's side-by-side comparison with a competing product, alongside a third request (an instant single-word spell check) that's also in this release. Keep the reports coming; this is how Quill actually gets built.

## What's next

Beta 3 keeps the beta cycle moving toward 1.0. As always: **Help > Report a Bug** for anything that surprises you, and thank you for testing.
