# QUILL Accessible Vault — remaining phases (Phases 3–7)

**Status.** The Accessible Vault's first milestone — **Phases 0–2** (persistent vault +
indexing, wikilinks with Follow Link / create-on-follow / ambiguity chooser, and spoken
backlinks) — is **shipped** and documented in `QUILL-PRD.md` §5.89d, the user guide
(Tools > Vault), the changelog, and the release notes. This file is the **remaining
work**: the unfinished phases and the Phase 0–2 deferred items, each additive,
independently shippable on the same `quill/core/vault` backbone, and accessible on its
own. The roadmap tracks this at [`roadmap.md`](roadmap.md) §1.7.

The guiding principle is unchanged: a **translation table, not a port** — take a
linked-notes model (files, links, backlinks, search, tags) usually shown *visually* and
present it **by voice and keyboard**, which for a screen-reader user is an upgrade, not a
compromise. Everything stays **optional, additive, and plain-text-first**.

---

## 1. Keeping indexes fresh (applies to every remaining phase)

- Indexing runs on the existing background `stability.task_manager.QuillTaskManager`, never on the UI thread; results are applied via `wx.CallAfter`.
- On note save and on **external change** (QUILL already watches folders and reloads cleanly), re-index only the changed note and patch the adjacency/tag/search structures.
- The `.quill/` cache lets a large vault open instantly; a background re-scan reconciles it. Loss of the cache is harmless (rebuild from notes).
- A visible, cancelable "Indexing vault... N of M" status for first-run of a big vault (disabled in Safe Mode).

---

## 2. Unfinished feature designs (each with its screen-reader magic)

### 2.1 Phase 3 — Vault-wide search and the quick switcher

**What.** Instant full-text search across every note, and a name-jump quick switcher.

**The magic (SR experience).**
- **Quick switcher** (a prominent key, e.g. a reimagined Go-To-Note): a modal that filters note titles/aliases as you type, **announces the result count** ("7 matches"), arrow to move (each announced), Enter to open. Fuzzy and forgiving.
- **Search:** a vault search that returns an **accessible results list** - note title, line number, and a snippet with the match - where Enter opens the note *at the matching line*. "Search as you type" announces the running count; "search within results" refines; recent searches are remembered. Regex and whole-word options are checkboxes with labels.

**Model/impl.** `search.py` - a `ripgrep`-backed scan when available (fast, no index to maintain) with a small in-process fallback; results ranked (title hits > body hits, recency tiebreak). The quick switcher uses the title/alias resolver. Both surfaces are dialogs through `_show_modal_dialog` with `apply_modal_ids`.

### 2.2 Phase 4 — Global tags: a spoken tag pane

**What.** Inline `#tag` and front-matter `tags:`, including nested `#area/subarea`, indexed vault-wide.

**The magic (SR experience).** **Show Tags** opens a list of every tag with counts ("#project - 24 notes; #idea - 51"); selecting a tag lists the notes/blocks carrying it (Enter opens at the tag). Typing `#` offers **tag autocomplete** (existing tags first, announced). A tag can be renamed vault-wide with inbound-count confirmation, like link rename.

**Model/impl.** `index.py` tag map (tag > note/block occurrences), nested-tag aware. Autocomplete reuses the same popup as wikilinks. Ties into Story Studio element tags so a character's `#pov` shows in the vault tag index.

### 2.3 Phase 5 — Transclusion, embeds, and block references

**What.** `![[Note]]` embeds a whole note; `![[Note#Heading]]` a section; `![[Note#^blockid]]` a single block. Assign a block id with `^blockid` at a paragraph's end.

**The magic (SR experience).** Because QUILL is plain text, an embed stays as `![[...]]` in the buffer (no silent expansion). But:
- **In preview and on compile/export**, embeds are **expanded** with a spoken/announced "embedded from <note>" boundary, so a compiled manuscript or a shared HTML page contains the real content.
- **"Speak embed at cursor"** reads the transcluded content aloud on demand without altering the buffer.
- **"Resolve embed inline"** pulls the target's text into the document as one undo step, for when you want it materialized.
- **Block references:** an **"Add block reference"** command mints a `^blockid` and copies a `[[Note#^blockid]]` link to the clipboard, announced - so quoting a specific paragraph elsewhere is one gesture.

**Model/impl.** `resolve.py` embed expansion (with cycle detection) feeds the `browser_preview` renderer and `compile_manuscript`. Block ids are parsed by `note.py`.

### 2.4 Phase 6 — Templates and daily notes

**What.** Reusable note templates with variables; date-stamped daily notes.

**The magic (SR experience).**
- **Insert template...** - a picker of templates; on insert, any prompts (`{{prompt:Question}}`) are spoken and answered inline; `{{date}}`, `{{time}}`, `{{title}}`, and a cursor marker resolve automatically; focus lands where the cursor marker was, announced.
- **New note from template...** - creates a note (name prompted or derived) pre-filled.
- **Open today's note** - opens (creating from the daily template if absent) the note at the configured pattern (`Journal/{{date:YYYY-MM-DD}}.md`); **Previous/Next daily note** walk the calendar by key, announcing the date and whether it exists.

**Model/impl.** `templates.py` + `dailynotes.py`, extending the existing Snippet Gallery substitution rather than inventing a second engine. Settings hold the templates folder, daily-note folder, date format, and default templates.

### 2.5 Phase 7 — Sync and publish

**What.** Some knowledge tools sell hosted Sync and Publish. QUILL keeps files yours and adds accessible helpers.

**The magic (SR experience).**
- **Sync:** QUILL does not host sync; the vault is plain files, so any sync (OneDrive, Dropbox, git) already works, and QUILL's external-change watch reloads safely. We add an optional **Vault Git Sync**: "Sync vault" runs commit/pull/push with an **accessible conflict resolver** (a spoken, itemized "these 3 notes changed both places - keep mine / keep theirs / merge") instead of a diff view. Reuses the existing SSH/remote and safe-subprocess machinery.
- **Publish:** extend the publishing framework two ways - **Publish note** (push a note to the existing WordPress connection, resolving `[[links]]` and embeds to real HTML), and **Export vault as a linked site** (a static HTML site with working links and a generated index, via the existing export/`browser_preview` path). Both announce what will be sent and ask first (network-egress-audited).

**Model/impl.** Git sync via a thin wx-free `vault/sync.py` over `safe_subprocess`; publish via the existing publishing providers + link/embed resolution.

---

## 3. Phase 0–2 deferred items (same backbone)

Small extensions to what already shipped, tracked here so they are not lost:

- **`[[` autocomplete** — a real listbox filtering note titles/aliases as you type, announcing the highlighted match and remaining count, inserting `[[Match]]` on Enter with a spoken "Linked to <note>." Heading/block targets after `#`. Reuse the intellisense popup in `main_frame_intellisense.py`.
- **Preview/export link resolution** — render `[[...]]` as real anchors via the existing `browser_preview` renderer.
- **Unlinked-mentions UI** — the core `unlinked_mentions` exists; add the list + a one-key "Link this mention" action.
- **Neighborhood navigation** — a command that reads forward-links and backlinks together so the web of notes is walkable purely by keyboard and ear.
- **Rename-with-link-update** — renaming a note offers "Update 12 inbound links?" with an accessible summary and one-undo application.
- **A dedicated Vault Explorer window** — a `wx.TreeCtrl` where every note is an announced item, grouped by folder / tag / recency, reachable by key and returned from by Escape/F6 (reuse the Story Studio binder tree).
- **Background/incremental indexing** and the **Story-Studio-as-collection refactor** (the two packages already share the front-matter/heading machinery).

---

## 4. Accessibility standards (the consolidated "magic")

These apply to every feature and are non-negotiable acceptance criteria:

- **Keyboard-complete and palette-discoverable.** Insert link, follow link, backlinks, quick switcher, search, tags, insert template, daily note, sync, publish - each is a registered command with a friendly title, listed in the command palette (PRD principle 8) and assignable in the keymap editor. No mouse-only paths.
- **Spoken counts and outcomes.** "7 matches," "5 notes link here," "#idea, 51 notes," "Linked to <note>," "Opened <note> at Chapter 3." The user never has to *look* to know the result.
- **Contextual, not just positional.** Backlinks and search read the *sentence* around a hit, so the list is meaningful without opening each note.
- **Ambiguity is a spoken choice, never a guess.** Duplicate titles > an accessible chooser; a broken link > "no note named X - create it?"
- **Quiet by default.** Indexing, link updates, and previews never chatter; they announce on explicit action and summarize bulk operations once.
- **Focus is deliberate.** Every new pane/dialog lands focus on its content, returns via Escape/F6, and manages focus per the accessibility rules; the Spoken Echo captures any fleeting announcement.
- **Plain text stays sacred.** The buffer is never silently rewritten; links and embeds live as text and are resolved by voice/preview/export, preserving QUILL's core invariant.

---

## 5. Phased delivery

Each phase is independently shippable, additive, and accessible on its own:

4. **Phase 3 — Vault-wide search & quick switcher.** ripgrep-backed search results list + fuzzy name switcher.
5. **Phase 4 — Global tags.** Tag index + tag pane + `#` autocomplete + tag rename.
6. **Phase 5 — Transclusion/embeds/block refs.** Expansion in preview/compile + speak/resolve-inline + block ids.
7. **Phase 6 — Templates & daily notes.** Template engine (extending Snippets) + daily-note navigation.
8. **Phase 7 — Sync & publish.** Vault Git Sync with accessible conflict resolution + Publish note / Export vault as a linked site.

---

## 6. Risks and open questions

- **Link resolution ambiguity.** Title-based links break with duplicate titles; path-based links break on move. Resolve by title/alias with a deterministic disambiguation (folder proximity, then a spoken chooser), and offer link-update on rename/move.
- **Index scale and performance.** Large vaults (10k+ notes) need incremental, cached, background indexing; prefer `ripgrep` for search to avoid maintaining a heavy inverted index. Benchmark before Phase 3.
- **Coexistence with the per-document world.** The editor, tabs, bookmarks, and inline notes must keep working unchanged when no vault is open. Guard every entry point behind "a vault is active."
- **Wikilink vs Markdown coexistence.** The parser must not mangle `[label](url)`, code spans, or math.
- **Rename/move propagation** touches many files at once — must be atomic-ish, undoable, and clearly summarized.
- **Migration.** Existing Story Studio projects must open unchanged as vaults/collections; a one-time, non-destructive adoption path.

---

## 7. Non-goals

- **Graph view and Canvas as visual surfaces.** We deliver the link *relationships* as accessible lists and navigation; no rendered graph or infinite visual canvas.
- **A hosted, paid sync/publish service.** QUILL keeps files yours; we add helpers over the user's own sync and the existing publishing framework.
- **A second editing paradigm.** No WYSIWYG/live-preview mode; the plain-text, hidden-codes editor remains the one editor.
- **A dedicated plugin marketplace.** Extensibility rides the existing Quillin system.
