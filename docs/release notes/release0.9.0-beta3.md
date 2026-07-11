# QUILL 0.9.0 Beta 3

## One editor, every format — and the braille fix is on for everyone.

*From Community Access. Free. Optional by design. Private by default.*

Beta 3 carries one big story and a stack of community-driven fixes. The big story: **One Editor, Every Format**. The braille fix you helped us test in Beta 2 is confirmed and now on by default for every user, QUILL gains true rich text editing for RTF and Word documents, and one Document Format switcher moves any document between plain text, Markdown, HTML, Rich Text, and Word mid-session. Alongside it: fix what Beta 2 testers found, close out every open community bug report, and ship eight small accessibility-first features that were ready to go. This document explains every new keystroke in full, step by step — no feature here requires you to guess at a shortcut.

This is the friendly companion to the **"0.9.0 Beta 3"** section of `CHANGELOG.md`. The shorter text under **Help > What's New** and **Check for Updates** comes from that changelog; this document tells the fuller story.

---

## The highlight: One Editor, Every Format

### The braille fix is on — for everyone, by default

In Beta 2 we asked braille display owners to try an experimental setting and tell us what they saw. You did, and it works: text now starts in braille cell 1 (the long-standing "cell two" quirk that RichEdit controls share with Microsoft Word is gone), and selecting text shows dots 7-8 on the display.

So in Beta 3 it simply ships on. There is nothing to enable, no Experimental tab to navigate, no restart dance. Every document opens in the one QUILL editor — the same native Windows control you have always typed in, now carrying the fix out of the box.

Two plain checkboxes on **Preferences > Braille** own the whole fix, both checked by default:

- **Fix braille cell alignment and selection dots (recommended)** — the system-edit emulation that makes the display start at cell 1 and show selection dots.
- **Hide editor border (required for braille cell alignment)** — testing showed the visible window border itself pushes braille output out of cell 1, so the borderless editor frame is part of the fix, not a cosmetic preference. If you uncheck it, QUILL warns you — specifically — that braille cell alignment will break, before anything changes.

If you experimented with editor surfaces in earlier betas, your old experimental settings are retired automatically on upgrade and you land on the new default; QUILL tells you once, in plain language, that your editor settings were simplified.

### Rich text is real now: RTF documents

Open an .rtf and it is *formatted* — genuinely, in the editor. Bold text is bold. Headings are sized. Ctrl+B applies real bold, **Insert > Heading 2** applies a real heading, and **Describe Formatting at Cursor** answers from the live document: "Arial, 14 point, bold, centered."

The rule to hold onto: **bold means bold — QUILL speaks your document's language.** In a Markdown file, Ctrl+B still wraps your selection in `**` exactly as it always has. In HTML, `<strong>`. In an RTF, it is real bold. Same key, same command, the right effect for the format you are writing.

Everything else keeps working, because rich mode changes presentation, not plumbing: search, spell check, AI commands, read aloud, bookmarks, inline notes, and braille all read the same text they always have. Autosave protects the formatting too — rich documents snapshot their full formatting alongside the text, so crash recovery brings back your bold and headings, not just your words.

In a plain .txt file, the first time you press a formatting key QUILL asks — once — what you want: treat the document as Markdown, convert it to Rich Text, or stay plain. Answer "stay plain" and it never nags again.

### Editable Word documents — with your original protected

A .docx can now open for real rich editing and save back as a genuine Word file. Because Word documents can carry things QUILL's editor cannot — tables, images, comments, tracked changes, headers and footers — QUILL is honest about it at the door:

- A **clean** Word file (nothing QUILL can't carry) opens rich, directly.
- A file **with** those features asks first, naming them specifically: open for reading and plain editing (the safe default), edit as Rich Text knowing exactly what a save cannot keep, or edit a copy and leave the original untouched.
- The first rich save over a flagged original writes a **timestamped backup** next to it, automatically. QUILL never silently rewrites your Word file.

### The Document Format switcher

**Format > Document Format...** — or Ctrl+Shift+Grave, K; or the command palette; or the new **Format** cell on the status bar, which shows your current format and opens the switcher when you press Enter on it — moves the current document between Plain text, Markdown, HTML, Rich Text (RTF), and Word (.docx), mid-session.

Switching a Markdown draft to Rich Text turns your `# headings` into real headings. Switching a rich document to Markdown warns first — with the specific list of anything that will not survive — before converting. And a switched document never silently overwrites its old file: the next save proposes the new name (`notes.md` becomes `notes.rtf`) so the format on disk always matches the extension.

### On the Mac

The macOS editor is the same native text view it has always been, and with the optional PyObjC component installed, rich mode works there too — same commands, same heading sizes, same behavior. Without it, RTF and Word documents open converted, exactly as they did before: nothing breaks, nothing is lost, and VoiceOver keeps reading the same native control it always has. We will promote the native Mac path fully once it passes the same live-hardware verification the braille fix did on Windows.

**How to get PyObjC and test rich mode on your Mac.** PyObjC is the small, well-established open-source bridge that lets QUILL talk to macOS's own text engine; it is not bundled, so testing is strictly opt-in. To install it:

1. Open **Terminal** (press Cmd+Space, type "Terminal", press Return).
2. If you run QUILL from source or a pip install, type: `pip install "pyobjc-framework-Cocoa>=10.3"` and press Return. If you installed QUILL as an app bundle, use the same Python that runs QUILL — from the QUILL source folder that is: `python -m pip install ".[mac]"` — the `mac` extra resolves to the identical PyObjC package.
3. Restart QUILL, then open any .rtf file. If the install worked, the document opens formatted and pressing Ctrl+B on a selection announces "Bold" with genuine bold applied; **Describe Formatting at Cursor** reads the live formatting back ("Helvetica, 14 point, bold").
4. If PyObjC is not found, nothing changes: the same .rtf opens converted to editable text with a status message saying so — that is the designed fallback, not an error.

**What we need from VoiceOver users, specifically:** with rich mode active, does VoiceOver still read the editor normally (typing echo, arrow-key review, selection announcements)? Does formatted text — a bold word, a sized heading — read and navigate correctly? Tell us either way through **Help > Report a Bug**, naming your macOS version. Exactly as with the Windows braille fix in Beta 2, real-hardware reports are the promotion gate: the native Mac path becomes the default the moment it passes this test in the field.

---

## Fixes

### Portable updates left you with an unopened .zip and no in-app way to use it

A community member on Mastodon reported that updating a portable install ended with a dialog offering only "Open folder" or "Close" — no way to actually apply the update — so they had to hit Open Folder, find the downloaded ZIP themselves, and extract it by hand. We dug in and confirmed the underlying portable-vs-installed detection was already working correctly (a portable install does download the portable ZIP, not the Windows installer), but the post-download dialog only ever recognized `.exe`/`.msi` as something it could act on — a `.zip` fell through to the bare "Open folder" path with nothing more helpful on offer. Quill now shows an **Extract now** button for a downloaded portable update, which unzips it into a ready-to-run sibling folder and reveals that instead of the raw archive. Quill still doesn't replace its own running files while it's open — you copy your `data` folder over and swap folders yourself, the same as any portable app update — but the archaeology of finding and unzipping the download is gone.

### Pandoc imports (EPUB and others) could silently produce an empty document

A community member reported — and correctly root-caused — a serious one: importing an EPUB via **File > Import > EPUB Book** could leave you with a completely empty document while Quill reported success. The cause was a subtle encoding mismatch: Quill's subprocess helper decoded Pandoc's output using the system's default locale encoding rather than an explicit one, and on a Windows machine whose locale defaults to a legacy code page instead of UTF-8, Pandoc's UTF-8 output could fail to decode — silently leaving Quill with nothing, while still reporting success. Output is now always decoded as UTF-8 (with a safe fallback so even a genuinely non-UTF-8 byte never crashes or blanks the result), and the Pandoc import path now explicitly fails loudly if it ever gets no output, instead of quietly handing you a blank page. This affected every tool that goes through Quill's subprocess helper, not just EPUB import, so this is a broader reliability fix than it first appears.

### Speech and Dictation crashed on open

Four testers independently reported the same crash: opening **Tools > Speech > Speech and Dictation** raised a `TypeError` instead of showing the dialog, on both the Offline and Online tabs. The dialog's constructor had grown two new required arguments (`kokoro_ok`, `kokoro_can_install`) that the one place calling it was never updated to supply. Both are now populated the same way the existing Vosk availability flags already are, and the dialog opens normally again.

### The Kokoro-unavailable error pointed at a menu item that doesn't exist

The same tester who hit the Speech and Dictation crash above also found this while checking Kokoro voices: trying to speak with Kokoro before its extra component was installed said "Tools > Speech > Install Kokoro ONNX will fetch it" — but that item was folded into **Help > Download Optional Components** in an earlier release, and the error text never caught up. It now points to the right place.

### A rare crash when a keystroke arrived before the first document existed

On macOS, a very early or very late keystroke — before the first document tab finished setting up, or after the last one closed — could raise `AttributeError: 'MainFrame' object has no attribute 'editor'` from the global keyboard hook. One of the three checks in that code path read the editor directly where its neighbors already defended against exactly this case; all three are now consistent.

### On macOS, the G key stopped typing and opened Find instead

A tester reported the strangest thing: in a completely blank document, pressing G — upper or lower case — opened a Find dialog instead of typing the letter. Every other key worked normally. We traced it to how Quill builds the little keyboard-shortcut hint shown at the right edge of each menu item. Find Next is Cmd+G on macOS, and that hint text is embedded after a literal tab character in the menu label — which wxWidgets (the toolkit Quill is built on) parses as a second, independent keyboard shortcut, entirely separate from Quill's own shortcut handling. wxWidgets recognizes the words "Ctrl", "Alt", and "Shift" in that hint text, but not the word "Cmd" — so instead of rejecting the whole hint as invalid, it silently dropped "Cmd" and kept the bare "G", accidentally registering plain G as a real system-level shortcut for Find Next. That shortcut then intercepted every G keystroke everywhere in the app, before it could ever reach whatever you were typing into. This affected every macOS-only "Cmd+something" shortcut in Quill, not just Find Next — the fix changes how that one hint is built so wxWidgets always sees a modifier word it understands, while the shortcut you actually see on screen still reads "Cmd+G" exactly as before.

### The portable-update "next launch" confusion

A user asked a very reasonable question after downloading an update and restarting: why did Quill still show the old version? The short answer is that a portable update has never applied itself automatically, on any release — the downloaded ZIP has always needed a manual step from you (previously "Open folder" and unzip it yourself; as of the Extract Now button above, Quill now does the unzip for you). If our own wording anywhere implied it happens on the next launch, that was the actual bug — nothing was silently failing, the automatic step just never existed. We've tightened the wording in this document and in Quill's own update dialog so "swap it into place" reads as the manual step it has always been.

### A shared dialog crash, already fixed before Beta 2 shipped

"Go to Entry in Notebook" and its sibling tree-navigator dialogs could crash with a `wxAssertionError` on open. We traced this to a fix that had already landed on the development branch before Beta 2's code froze but is worth confirming here for anyone who hit it on a Beta 2 build: the dialog no longer tries to expand its (intentionally hidden) root node.

### Narrator becomes a first-class citizen: no more double speech, and QUILL now speaks *through* Narrator

George Kerscher reported that with Narrator running, QUILL's self-voicing spoke at the same time as Narrator — most audibly in the command palette. Beta 3 fixes this at two levels.

**Detection, by API.** Alongside its process check, QUILL now reads the marker Windows itself maintains while Narrator runs (the named `NarratorRunning` system event — one cheap call, no process scanning). Narrator can no longer slip past detection under any elevation or timing condition.

**Speech, directly to Narrator.** QUILL's announcements are now raised as **UI Automation notification events** — the announcement channel Narrator has listened on since Windows 10 1709. That means status changes, palette narration, and all of QUILL's spoken feedback arrive in *your* One Core voice, spoken by Narrator itself, exactly as they arrive in JAWS's or NVDA's voice through their dedicated bridges. If the channel is unavailable on a given system, the message lands in the status bar instead — and the old behavior, QUILL's own SAPI voice talking over your reader, is gone unconditionally: a running screen reader always silences the self-voice, "forced" announcements included.

One honest caveat: the direct-Narrator channel is verified in code and tests but needs real Narrator listening to confirm the experience end to end. If you use Narrator, please try Beta 3 and tell us — through **Help > Report a Bug** — whether announcements now arrive in One Core, once, in the right voice.

### Install Starter Snippet Packs works properly with a screen reader

Reported against Beta 2: the pack list needed a Space press on an invisible checkbox — with no feedback — before Enter would do anything. It's now a plain multi-select list: arrow to `daily-writing`, press Enter, it installs. Hold Shift or Ctrl to pick several; your screen reader announces what's selected as you move.

### A macOS crash while creating a Notebook

Shannon Dyer hit a hard crash ("SystemError: ActivateEvent returned a result with an exception set") while creating a Notebook on macOS — a window-activation handler ran into a wx assertion while dialogs were tearing down, and the whole app went with it. Window activation only exists to put focus back in your document; it is now fully contained and can never take the process down.

### Crash reports now say which beta you're on

Two crash reports arrived this week for a bug that was already fixed in Beta 2 — and they looked like regressions because every 0.9.0 beta reported itself as just "0.9.0." Crash and feedback reports now carry the full version ("0.9.0 Beta 2"), so a report from an older install is recognizable at a glance. If you see the Profiles and Features crash (`_LazyString`), please update to the current beta: it was fixed there.

### Quill no longer offers crash recovery for exits with nothing to diagnose

Two automatic crash-recovery submissions showed logs with only routine background activity right up to the moment QUILL stopped — no exception, no error, nothing actionable. That pattern is consistent with the process being closed externally (a forced shutdown, a killed task) rather than a bug inside QUILL. This is now a real fix, not just an observation: Quill checks the log for genuine error evidence (an `ERROR`, `CRITICAL`, or a traceback) before offering crash recovery at all. An inconclusive exit no longer shows the "Quill detected an unclean exit" dialog — there's simply nothing to prompt you about. A real crash still logs an error and still offers recovery exactly as it always has; only the no-evidence case changed. Your autosave snapshot is never touched by this — it's still on disk either way, this just controls whether Quill asks you about it.

---

## GitHub Items grows up: pins, favorites, real search, and local git sync

Beta 2 introduced the read-only GitHub Items viewer. Beta 3 merges the first tranche of the GHManage/fastgh unification into it — four features, all keyboard-first:

- **Pinned repositories.** The **Pinned...** button keeps a short, curated list of the repos you actually work in. Pick one from the menu to load it instantly; pin or unpin the loaded repo from the same menu. No more retyping `owner/repo`.
- **Favorites.** Press **Ctrl+D** on any selected row — an issue, a PR, a branch, a release — to bookmark it. The **Favorites...** menu lists every bookmark across all your repos and opens any of them in your browser. Bookmarks live only on your machine.
- **Search with full GitHub syntax.** Press **Ctrl+F**, type any GitHub search query — `label:bug is:open crash`, `author:alice is:pr` — and press Enter. Results are scoped to the loaded repository; clearing the search restores the normal list.
- **Local git sync.** The repository field now fills itself in when the document you are editing lives inside a git clone whose origin points at GitHub — any file, however you opened it, not just files opened through QUILL's own GitHub commands.

And the second tranche landed in this same release:

- **PR diffs, read the QUILL way.** Select a pull request, press **Diff...**, and browse its changed files in an accessible list. Each file's before-and-after content runs through the same compare engine as **Compare Documents**, so what you hear is a numbered difference walk — "Difference 2 of 5. Text changed at line 41. main: ... this PR: ..." — with the actual changed words described, never a wall of plus and minus signs. A brand-new file reads as its content; a deleted file says exactly that; a binary or oversized file falls back honestly to its change counts.
- **Batch operations, behind real consent.** Select several rows (the list is multi-select now), press **Batch...**, and close, reopen, or add a label to all of them at once. This is the one deliberate exception to the viewer's read-only rule, and it is fenced accordingly: it only works signed in — the anonymous viewer stays fully read-only — and a confirmation names the exact action and the exact item numbers before anything changes on GitHub. If some items fail, you hear which ones and why; the rest still go through.
- **AI thread summaries.** A hundred-comment issue at 11 pm is nobody's friend. Press **Summarize** on any issue or PR and QUILL's AI condenses the whole discussion into a short, plain-prose TL;DR — what it's about, where it stands, what's still open, and the apparent next step — read into the details pane and announced. It uses the same AI connection and consent gates as every other QUILL AI feature, and nothing runs until you press the button.

The viewer otherwise stays read-only against GitHub, behind the same consent, token, and Safe Mode gates as every other GitHub feature. The rest of the unification review — branch comparison, notifications, a wiki browser, and more — is on the roadmap.

## Headers and footers now live inside your Word and RTF files

The Header/Footer Builder from Beta 2 wrote headers and footers when *printing*; the files themselves didn't carry them. Now they do: save as **.docx** and your header/footer becomes a real Word header and footer — with a live page-number field Word keeps renumbering as the document changes — and save as **.rtf** writes the equivalent native header/footer groups. Roman numerals, a custom starting page number, and a different first page all carry through. A blank spec changes nothing, and a header can never be the reason a save fails.

## New: eight small, accessibility-first additions

### The Clipboard Collector went system-wide

Dean Martineau asked for the EdSharp behavior: turn on the collector, then copy anywhere — a browser, an email, a terminal — and it all lands in your QUILL document. That's exactly what it does now. While **Toggle Clipboard Collector** is on, QUILL watches the system clipboard (a single cheap check, about once a second, that touches the clipboard only when something actually changed) and appends each new copy to the open document, saving as it goes. Copies made inside QUILL still collect instantly, and each distinct copy is collected exactly once.

### QUILL as Thunderbird's external editor

Martin Courcelles asked to write his email in QUILL. Good news: it already works — QUILL's one-process-per-file behavior is exactly what Thunderbird's "External Editor Revived" add-on expects — and the user guide now has a step-by-step "Using QUILL as an external editor" section: install the add-on, point it at `quill.exe`, press Ctrl+E in a compose window, write with every QUILL feature, save and close, and the text drops back into Thunderbird.

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

By default the scan is **top-level files only** within each favorite folder, not recursive — this keeps the filter instant even if one of your favorites happens to contain a huge nested tree, and it matches the "short, curated list" philosophy favorites are built around. Tick the **Include subfolders** checkbox in the dialog to search every subfolder too, if you need to — it's capped at a few thousand files so even a very large favorite can't hang the dialog. And because Quill doesn't have a single-project-root "workspace" concept the way VSCode does, this Quick Open is intentionally scoped to your favorites rather than searching your whole disk.

### Accessible code folding

Fold a heading section or a fenced code block (the ` ``` `...` ``` ` kind, as in Markdown or a code block inside a document) to reduce clutter while you work — without ever losing access to what's folded.

- **Ctrl+Alt+Shift+F** — **Toggle Fold.** Folds or unfolds the smallest foldable region containing your cursor. You'll hear exactly what happened: *"Folded: 14 lines under 'Chapter Two'"* when you fold, *"Unfolded: 'Chapter Two'"* when you unfold.
- **Alt+Shift+]** — **Next Fold.** Jumps to the next foldable region's boundary, whether it's currently folded or not, announcing its label, fold state, and line count on arrival: *"'Chapter Three', expanded, 22 lines."*
- **Alt+Shift+[** — **Previous Fold.** Same as Next Fold, but backward.
- **Ctrl+Alt+Shift+L** — **List Folds...** Opens a dialog listing every foldable region in the document at once, each showing its current fold state and line count. Pick one to jump straight to it — the fastest way to get an overview of a long document's structure and fold state without stepping through it region by region.

We designed this one carefully, and it's worth explaining why it works differently from folding in most other editors. There, folding hides lines visually, and arrow-key navigation silently skips right over a folded block — a screen reader user has no way to tell whether content vanished or was just collapsed, which is a real, long-standing accessibility complaint about folding in mainstream code editors. Quill's folding never does that: **the document text is never touched, and ordinary arrow-key, word, and line navigation is never intercepted.** Fold state is purely something the four commands above announce and act on — arrow through a folded region character by character and you will read every word in it, exactly as if it weren't folded. Folding only changes what a *jump* command does, never what you can reach by moving normally, so nothing you can reach is ever made silently unreachable.

---

## Offline Edition: genuinely offline now

A community member testing the Offline Edition installer found that Kokoro's neural voices still asked for an internet connection the first time they were used — on a build whose entire point is "no internet needed." That report turned into an audit of every optional speech component Quill offers, and this release closes the gaps that audit found.

### What "Offline Edition" means, and where it fell short

The Offline Edition installer is meant to be a genuinely self-contained build: everything you might reasonably use, already on your computer, with no internet connection required after install. Kokoro's *voice model files* were already bundled that way. What wasn't bundled was the small piece of software that actually *reads* those files — Kokoro's underlying package, which pulls in a few supporting libraries the first time it's used. That meant selecting a Kokoro voice on a genuinely offline machine still hit a wall: the model was right there, but the program needed to install its "engine" over a connection that, by definition, an offline machine doesn't have.

### What's fixed

- **Kokoro neural voices** now install completely from files already on your computer, with the Offline Edition build. No connection needed, the first time or ever.
- **whisper.cpp — the speech-to-text engine Quill uses by default** — now comes with its starter model already in place. This one mattered most: whisper.cpp isn't an optional extra you might choose, it's the engine Quill reaches for automatically, so a "no internet needed" build that couldn't actually transcribe anything until it fetched a file was the biggest gap of all. That's fixed.
- **Faster Whisper, Vosk, and MP3 chapter-marker support** — three smaller optional add-ons — get the same treatment. Choosing any of them under the Offline Edition build now works without a connection.
- **Vosk's install got more reliable as a side effect.** Vosk always needed one small supporting library that, until now, could only come from the internet even when Vosk's own file was already verified and local. That gap closes too.

- **Piper gets the same treatment in this release**: the Offline Edition now bundles Piper's engine — integrity-checked against the same pinned fingerprint at build time and again at install time — plus a ready-to-speak starter voice (Lessac, US English, medium quality). Pick Piper on an Offline Edition install and it talks without ever touching the network; more voices download from the online catalog whenever you want them.

### What's still on the list

One component doesn't have this treatment yet: **Node.js-based Quillins** still need a connection the first time you use one, even under the Offline Edition. This is a known, tracked gap rather than an oversight.

## A note on how this release came together

Every fix in this release traces back to a specific community bug report — nine in total, from #939 through #953, every one now closed with an explanation of what was found and (where applicable) what changed. The two "no evidence in the log" reports (#940, #948) turned into a real feature rather than being quietly closed as unreproducible: Quill now recognizes that pattern itself and stops asking about it. And two of the seven new features — ranked spelling and favorite folders — came directly from a tester's side-by-side comparison with a competing product, alongside a third request (an instant single-word spell check) that's also in this release. Keep the reports coming; this is how Quill actually gets built.

## What's next

Beta 3 keeps the beta cycle moving toward 1.0. As always: **Help > Report a Bug** for anything that surprises you, and thank you for testing.
