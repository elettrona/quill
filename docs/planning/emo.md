# QUILL Accessible Emoji Picker
## Product Requirements Document

**Document status:** Draft for product and engineering review
**Product:** QUILL
**Feature area:** Editing / Insert
**Document version:** 1.0
**Date:** July 11, 2026
**Primary platform:** Windows 11, wxPython, keyboard-first and screen-reader-first
**Intended audience:** Product, engineering, accessibility, and documentation

---

## 1. Executive Summary

QUILL will add a first-party **Insert Emoji** dialog (Alt+Period) that lets a
person browse every standard Unicode emoji by category, search for one by
name or by a typed symbol/emoticon they half-remember, and read a rich,
screen-reader-friendly description of what the emoji actually looks like
before inserting it.

The feature has two parts that must both be true for it to be worth
shipping:

1. **A complete, current catalog.** Every standard emoji, correctly
   categorized, searchable by name and by common ASCII emoticon shortcuts,
   sourced from the Unicode Consortium and CLDR rather than hand-maintained.
2. **A rich description for every single emoji, not a curated subset.** A
   blind or low-vision writer choosing between "slightly smiling face,"
   "grinning face," and "smiling face with smiling eyes" needs to know what
   distinguishes them, not just their official names. This document commits
   to full-coverage description generation across the whole catalog (see
   Section 11), replacing an earlier draft's "top 150 only" scope.

Both the catalog and its descriptions are generated **offline, at
development time**, by a dedicated tool, and shipped as a static, committed
data file. Nothing about this feature calls out to the network at runtime;
that would conflict with QUILL's offline-first, Safe-Mode-compatible
architecture and would require a `network_egress_audit.py` entry for no
real benefit, since emoji data changes roughly once a year.

---

## 2. Product Vision

### 2.1 Vision statement

> Nobody should have to guess what a symbol looks like, or dig through a
> visual grid they can't see, to put an emoji in their writing.

### 2.2 Core product promise

A user should be able to:

- Open the picker from anywhere in the editor with one hotkey.
- Move through emoji by category the same way they move through any other
  accessible list — no picture grid, no mouse-only hover states.
- Type a name ("heart"), a partial keyword ("celebrat"), or a remembered
  ASCII emoticon (":)", "<3") and land on the right emoji.
- Read a plain-language description of what the emoji looks like before
  committing to it, every time, for every emoji — not just the popular ones.
- Insert it at the caret and hear confirmation of what was inserted.

### 2.3 Experience principles

1. **Lists, not grids.** Every existing native OS and web emoji picker is a
   visual grid of tiny pictures. QUILL's is a set of accessible lists: a
   category list, a results list, a description pane. Nothing here depends
   on seeing the glyph.
2. **No dead ends.** If an emoji has a name and a code point, it has a
   description. A picker that describes only the popular faces and shrugs
   at everything else has just moved the guessing problem, not solved it.
3. **Offline and deterministic.** The picker works with no network
   connection and behaves identically from one session to the next; the
   underlying data only changes when a maintainer regenerates it.
4. **Authoritative data, not vibes.** Categories and names come from the
   Unicode Consortium and CLDR, not a scraped or informally maintained list.

---

## 3. Background and Problem Statement

QUILL already ships **Insert Special Character**
(`quill/quillins_bundled/insert-character/`), which solves "I know the
Unicode code point, insert this exact character," and
`quill/core/char_describe.py`, a Reveal-Codes-style inspector that describes
whatever character is under the caret. Neither solves "I want to insert an
emoji and either don't know its name or want to know what it looks like
before I use it."

Mainstream emoji pickers (Windows `Win+.`, Slack, Discord, GitHub's
`:shortcode:` popup) are built around a visual grid of small glyphs grouped
by category, with a search box that matches names/shortcodes/keywords. That
UI is unusable non-visually: the grid conveys nothing to a screen reader
beyond "here is a character," and none of the mainstream pickers attempt a
visual description of the glyph at all — sighted users don't need one.

For a screen-reader-first writer, three problems compound:

- **Discovery.** Browsing "what emoji exist" by category requires an
  accessible list, not a grid.
- **Recall.** Someone may remember an ASCII emoticon convention (":)")
  without remembering that it now maps to "slightly smiling face" — the
  search needs to bridge that gap.
- **Disambiguation.** Unicode has dozens of visually distinct emoji with
  similar names ("grinning face," "grinning face with big eyes," "beaming
  face with smiling eyes"). Without sight, the name alone often isn't enough
  to choose correctly; a description of the actual visual difference is
  required, and it has to exist for the whole catalog, since there's no way
  to predict in advance which "obscure" emoji a given user will need.

---

## 4. Goals

### 4.1 Primary goals

- Ship a first-party **Insert Emoji** dialog bound to **Alt+Period**.
- Cover every emoji in the current Unicode emoji standard, organized into
  the official Unicode category/subgroup tree.
- Support search by official name, CLDR keyword, and common ASCII emoticon
  aliases, plus direct lookup when an emoji character itself is typed or
  pasted into the search box.
- Generate a rich, accessible visual description for **100% of catalog
  entries** — no "top N" cutoff.
- Keep the catalog refreshable without changing application code when
  Unicode publishes new emoji.

### 4.2 Secondary goals

- Reuse the existing `CharacterDescription` (summary + detail) shape from
  `char_describe.py` so the description pane behaves like a pattern the
  codebase — and screen-reader users of it — already knows.
- Keep the feature fully functional in Safe Mode and fully offline.

### 4.3 Success outcomes

- A screen-reader user can find and correctly distinguish between similar
  emoji using only the description pane, without sighted assistance.
- Typing a common emoticon (":D", "<3", ";)") surfaces the right emoji in
  the top result.
- The catalog survives a Unicode version bump with a single script re-run
  and a reviewable diff, not a rewrite.

---

## 5. Non-Goals

- **Custom/animated/platform-specific emoji** (Slack custom emoji, Apple's
  "Memoji," animated stickers). Standard Unicode emoji only.
- **Rendering a custom glyph grid or colored emoji font.** Presentation
  relies on native accessible controls and text, not a picture surface.
- **Real-time emoji trend data, recently-used ranking, or frequency
  telemetry** — out of scope for v1 (see Section 25, Open Questions, for
  whether a "recently used" category is worth a later pass).
- **Runtime network calls to Unicode.org, CLDR, or any emoji API.** All data
  is generated ahead of time and shipped as a static file.
- **Editing or annotating the emoji catalog from within the picker UI.**
  Maintainers update it via the generator tool, not end users.

---

## 6. Users and Personas

### 6.1 Screen-reader-first writer (primary)

Uses JAWS or NVDA, navigates almost entirely by keyboard, and needs every
control in the dialog — category list, results list, description pane — to
be a normal accessible list/text control with sensible names and states.
This person is the reason the description pane exists at all: they cannot
fall back on "just look at the picture."

### 6.2 Keyboard-first sighted power user

Doesn't use a screen reader but avoids the mouse. Wants the hotkey, wants
fast type-ahead search, and benefits from the same accessible-list layout
because it's also fast to arrow through.

### 6.3 Low-vision user

May be able to see the emoji glyph at high zoom but still benefits from the
name and description to confirm subtle visual details (skin tone, direction
a hand or arrow is pointing, small facial differences) that are easy to
miss even with some vision.

---

## 7. Terminology

- **Base emoji / pictograph** — a single, non-composite emoji character,
  e.g. U+1F600 GRINNING FACE. Unicode's actual count of hand-designed,
  visually distinct pictographs (roughly 1,400-1,600 depending on version).
- **Modifier sequence** — a base emoji plus a skin-tone modifier
  (Fitzpatrick scale, 5 tones) and/or gender sign, e.g. "woman raising hand:
  medium skin tone."
- **ZWJ sequence** — multiple code points joined with U+200D (zero-width
  joiner) into one visual glyph, e.g. family and profession combinations.
- **RGI (Recommended for General Interchange)** — Unicode's list of
  sequences guaranteed broad rendering support; the practical definition of
  "a real emoji" versus an unsupported combination.
- **Flag sequence** — a pair of Regional Indicator Symbols forming a
  country/region flag (roughly 260 entries), or a tag-sequence subdivision
  flag (England, Scotland, Wales).
- **Catalog** — the committed, generated data file this feature reads at
  runtime; never fetched live.

---

## 8. Functional Requirements

| # | Requirement |
|---|---|
| FR-1 | Show all standard Unicode emoji, grouped by official category and subgroup. |
| FR-2 | Search by official Unicode name and CLDR keyword substrings. |
| FR-3 | Search by common ASCII emoticon aliases (":)", "<3", ":D", etc.). |
| FR-4 | Search by pasting/typing the literal emoji character(s) to jump directly to that entry. |
| FR-5 | Every catalog entry has a non-empty, human-readable visual description, not just popular entries. |
| FR-6 | Description is shown in a read-only, multi-line, screen-reader-friendly text control, updated on selection change. |
| FR-7 | Global hotkey **Alt+Period** opens the picker from the editor. |
| FR-8 | Selecting an emoji inserts it at the caret and announces the inserted name. |
| FR-9 | Fully functional offline and in Safe Mode. |
| FR-10 | Catalog is refreshable by re-running a dev-time tool, with no application code changes required for routine annual updates. |

---

## 9. Data Sources and Authority Tiers

No single Unicode file supplies category + name + search keywords + a rich
visual description together. The catalog is built from three tiers, most to
least authoritative, merged by the generator tool (Section 12):

**Tier 1 — Unicode Consortium (defines what counts as a standard emoji, and
its category tree).**
- `https://unicode.org/Public/emoji/latest/emoji-test.txt` — pin a specific
  version for reproducible builds, e.g.
  `https://unicode.org/Public/emoji/16.0/emoji-test.txt`. Gives the official
  group/subgroup/ordering and short name for every RGI sequence, and marks
  which sequences are fully-qualified/component/minimally-qualified.
- `https://unicode.org/emoji/charts/full-emoji-list.html` — human-browsable
  equivalent, used for spot-checking during review, not for parsing.

**Tier 2 — Unicode CLDR (search keywords).**
- `https://github.com/unicode-org/cldr/blob/main/common/annotations/en.xml`
- `https://github.com/unicode-org/cldr/blob/main/common/annotationsDerived/en.xml`
- Official Unicode i18n project; supplies the keyword tags that power
  keyword search (FR-2).

**Tier 3 — curated convention (ASCII emoticon aliases, FR-3).**
Unicode does not define ASCII emoticon shortcuts. Every mainstream picker
maintains its own small table. Rather than inventing one from scratch, seed
it from existing open data and grow it by request:
- `github/gemoji` (MIT) — `https://github.com/github/gemoji/blob/master/db/emoji.json`
- `iamcal/emoji-data` (MIT/CC0-style) —
  `https://github.com/iamcal/emoji-data/blob/master/emoji.json` — has a
  `"text"` field with legacy ASCII emoticon variants, the best available
  starting point.

**Reference implementation used only inside the offline generator, never
at runtime:** the `emoji` PyPI package (MIT,
`https://pypi.org/project/emoji/`) already parses Tier 1/2 data into an
`EMOJI_DATA` table and tracks new Unicode releases. Using it inside
`generate_emoji_catalog.py` avoids hand-rolling an `emoji-test.txt`/CLDR-XML
parser; it is a dev-tooling dependency only and is never imported by
`quill/core` or `quill/ui` at runtime.

---

## 10. Emoji Corpus Breakdown (why "all of them" needs a strategy, not just effort)

The catalog's ~3,700+ RGI entries are not 3,700 independent visual designs;
most are combinatorial expansions of a much smaller set of base pictographs.
Treating every entry as an independent hand-written description would be
both wasteful and inconsistent. Approximate breakdown (varies slightly by
Unicode version, confirmed at generation time from Tier 1 data):

| Group | Approx. count | Description strategy |
|---|---|---|
| Base pictographs (no modifiers) | ~1,500 | Full LLM-generated prose, one per entry (Section 11.2). |
| Skin-tone modifier sequences | ~600 | Base description + composed skin-tone clause (Section 11.3). |
| Gender/role ZWJ sequences (person + profession/role, x gender x skin tone) | ~1,300 | Base role description + composed gender/skin-tone clauses. |
| Family/couple ZWJ sequences | ~150 | Composed from constituent-person descriptions. |
| Flag sequences (regional indicators + a few subdivision flags) | ~260 | Small dedicated LLM/reference batch per Section 11.4, describing the actual flag design. |
| Keycap sequences (0-9, #, \*) | 12 | Trivial template, no generation needed. |

This is why FR-5 ("every entry has a description") is achievable without an
unbounded hand-authoring effort: the ~1,500 base pictographs and ~260 flags
are the only truly distinct visual designs requiring bespoke generation;
everything else is templated composition over that base set.

---

## 11. Rich Description Generation Pipeline (full coverage)

This supersedes the earlier draft's "hand-curate the top 150, synthesize a
thin fallback for the rest" plan. Full coverage is achieved in four passes,
all run offline by `quill/tools/generate_emoji_catalog.py` (or a
companion script it calls), never at runtime:

### 11.1 Structured base data pass

Merge Tier 1 (name, group, subgroup) and Tier 2 (keywords) for every entry,
plus decompose modifier/ZWJ sequences into their constituent parts (base
glyph + skin tone + gender + role), so later passes have structured input
rather than needing to re-parse a code point sequence.

### 11.2 Base pictograph description generation (~1,500 entries)

For each base pictograph, generate one to two sentences of plain-language
visual description using an LLM, prompted with the official name, CLDR
keywords, category/subgroup, and — critically — instructed to describe what
*distinguishes* this glyph from visually similar ones in the same subgroup
(e.g. contrast "grinning face" vs. "grinning face with big eyes" explicitly
by what differs: mouth, eyes, eyebrows). Output is plain text, no markup,
matching the tone of `char_describe.py`'s existing detail lines.

This is a one-time (well: once-per-Unicode-version-bump) offline batch job.
It requires outbound API calls during generation — those happen on a
maintainer's machine or in CI as part of running the generator tool, are
scoped to this one tool, and do not touch `quill/core`/`quill/ui` runtime
code, so they don't add a runtime network dependency. Per this project's
network-egress and external-call conventions, actually executing this batch
(cost, which API key, how many entries) is an implementation-phase decision
made explicitly when this PRD is approved for build — it is not something
to kick off silently as a side effect of writing this document.

### 11.3 Modifier/ZWJ composition (~2,050 entries)

Skin-tone, gender, and family/couple sequences are **not** independently
generated. Their description is composed programmatically from the base
pictograph's description (11.2) plus a small fixed set of clause templates:

- Skin tone: `"{base description} Shown with a {tone} skin tone."` (5 tone
  phrases: light, medium-light, medium, medium-dark, dark, matching
  Unicode's Fitzpatriac-scale naming).
- Gender: `"{base description} Depicted as a {woman/man/person}."`
- Family/couple: composed by joining the constituent members' short
  descriptions, e.g. `"A family of four: a man, a woman, and two boys."`

This keeps descriptions accurate and consistent across every skin-tone/
gender variant of the same base emoji without 2,000+ near-duplicate LLM
calls, and means adding a new base pictograph automatically yields correct
descriptions for all of its future modifier variants for free.

### 11.4 Flag descriptions (~260 entries)

Flags are the one place templating doesn't work — each one is a genuinely
distinct, factual visual design (a specific country or region's flag).
Generate these as their own small batch, prompted with the region name and
asked for the flag's actual design (colors, stripes, emblem), cross-checked
against a reference source during review (e.g. Unicode's own flag charts or
a standard reference like Wikipedia's flag articles) since these are
verifiable facts, not subjective description.

### 11.5 Review and quality gate

Full manual review of ~1,750 generated entries (1,500 base + 260 flags) is
not practical per Unicode release, but every generated description must
pass automated checks before it ships:

- Non-empty, under a maximum length (keeps the description pane readable).
- No literal use of "emoji" the word inside its own description in a way
  that's circular ("an emoji of an emoji").
- No banned placeholder text ("TODO", "description pending").
- A random sample (e.g. 5%) plus every entry in the most-distinguished-from
  neighbor subgroups (faces, hand gestures) gets a human spot-check pass
  before each release.
- Only the *new* entries introduced by a Unicode version bump need fresh
  generation and review — the existing ~3,700 don't change once shipped
  except for corrections filed as issues.

### 11.6 Storage

Generated descriptions are stored in the committed catalog itself (see
Section 14), not fetched or computed at runtime, and are versioned with the
Unicode/CLDR version they were generated against so a future regeneration
can tell which entries are new.

---

## 12. Data Maintenance and Refresh (keeping this current without code changes)

There is no live "emoji API" — Unicode publishes static, versioned files
roughly once a year. Given QUILL's offline-first stance and the
`network_egress_audit.py` gate on every outbound call site, the catalog is
never fetched at runtime. Instead:

- `quill/tools/generate_emoji_catalog.py` (new, dev-only, same family as
  `quillin_lint.py`/`agent_lint.py`) runs Sections 11.1-11.4 end to end and
  writes `quill/core/data/emoji_catalog.json`.
- When Unicode ships a new emoji version, a maintainer bumps the pinned
  version string in the script, re-runs it, reviews a diff that should
  contain only the new entries (existing entries are stable), and commits
  the updated catalog — a data change, not a code change.
- **Stretch, not required for v1:** a scheduled annual CI job that runs the
  generator against the latest published Unicode version and opens a PR if
  the catalog changed, the same shape as an automated dependency-bump bot.

---

## 13. Architecture: Core Data Module

**`quill/core/emoji_data.py`** — pure logic, no `wx` import, strict-typed,
loads the bundled catalog once and caches it at module level.

```
EmojiEntry:
    char: str
    name: str
    category: str
    subgroup: str
    keywords: list[str]
    emoticons: list[str]
    description: str
```

Public functions:

- `list_categories() -> list[str]`
- `list_by_category(category: str) -> list[EmojiEntry]`
- `search(query: str) -> list[EmojiEntry]` — ranked matching, see Section 16.
- `describe(entry: EmojiEntry) -> CharacterDescription` — reuses the
  existing `CharacterDescription(summary, detail)` dataclass from
  `char_describe.py` so the UI layer already knows how to render/announce
  it, and the two "describe a character" surfaces in QUILL stay consistent.

---

## 14. Architecture: Catalog File Format

`quill/core/data/emoji_catalog.json` — a single committed JSON file,
generated, never hand-edited. Sketch:

```json
{
  "unicode_version": "16.0",
  "generated": "2026-07-11",
  "entries": [
    {
      "char": "😀",
      "name": "grinning face",
      "category": "Smileys & Emotion",
      "subgroup": "face-smiling",
      "keywords": ["face", "grin", "happy"],
      "emoticons": [":D", ":-D"],
      "description": "A yellow face with a wide open smile showing the upper teeth and open, round eyes. The widest, most open-mouthed of the standard grinning faces in this subgroup."
    }
  ]
}
```

Modifier/ZWJ sequences carry a `base_char` reference so the UI can, if
useful later, group variants under their base entry rather than listing
every skin tone as a fully separate row (see Open Questions, Section 25).

---

## 15. Architecture: UI

**`quill/ui/main_frame_emoji_picker.py`** (new mixin — new handlers go in a
feature mixin per the existing `main_frame_speech.py`/`main_frame_vault.py`
decomposition pattern, not into `main_frame.py`).

`EmojiPickerDialog`, opened only through `_show_modal_dialog`, IDs applied
via `apply_modal_ids`, covered by the `dialog_inventory.py` gate like every
other modal. Layout — all native accessible controls, deliberately not a
visual grid:

1. **Search box** at the top; live-filters as you type with a short
   debounce; Enter jumps to the first result.
2. **Category list** (`wx.ListBox`) on the left — "All Results" (while
   searching) plus the Tier-1 category names.
3. **Results list** (`wx.ListCtrl`, report view) — glyph + name per row, so
   arrowing through it behaves like any other accessible list; the name is
   spoken, not left to the screen reader to guess at a bare character.
4. **Description pane** — read-only multi-line `wx.TextCtrl`
   (`wx.TE_READONLY | wx.TE_MULTILINE`), updated on every selection change,
   showing `describe(entry).detail`: category, official name, keywords,
   emoticon aliases if any, and the full visual description from
   Section 11. This is the "help pane" shape the original request asked
   for.
5. Standard **Insert / Cancel** buttons, same modal button contract as
   every other QUILL dialog.

Selecting Insert writes the character at the caret and announces "Inserted
{name}," mirroring the existing `insert_character` Quillin's announce
pattern.

---

## 16. Search Behavior Specification

`search(query)` matches in ranked order, returning best matches first:

1. **Symbol paste/typed match (FR-4):** if the query itself is one or more
   emoji characters, look up the exact entry by code point sequence.
2. **Emoticon alias match (FR-3):** exact match against an entry's
   `emoticons` list.
3. **Name match (FR-2):** exact match, then prefix match, then substring
   match against `name`.
4. **Keyword match (FR-2):** substring match against any entry in
   `keywords`.

Empty query shows nothing selected in "All Results" and leaves the category
list as the primary navigation surface.

---

## 17. Command, Menu, and Keymap Wiring

- New command id `edit.insert_emoji` added to `feature_command_map.py`.
- Keymap default: `"edit.insert_emoji": "Alt+."` in both
  `profile_default.json` and `profile_sr_friendly.json`. Checked against
  both files — unused, no conflict with any existing binding.
- Menu entry under **Insert**, alongside the existing "Insert Special
  Character..." Quillin entry — placeholder title "Insert Emoji...",
  finalized in Section 25.

---

## 18. Accessibility Requirements

- Every control has an accessible name; the results list exposes glyph +
  name as its accessible label per row, not the bare glyph alone.
- Focus moves predictably: opening the dialog focuses the search box;
  arrowing into the results list updates the description pane without
  moving focus away from the list.
- Description pane content changes are read-only text, not a live region
  that force-interrupts speech — the screen reader announces it because
  focus follows selection into a context where reading the updated field is
  the user's next natural action, consistent with how `char_describe.py`'s
  detail pane already behaves.
- No color-only signaling anywhere in the dialog.
- Works identically with mouse, keyboard-only, and touch (long term, not a
  v1 requirement given QUILL's current desktop-only scope).

---

## 19. Error Handling and Edge Cases

- Catalog file missing or fails to parse at startup: the Insert Emoji
  command is disabled with a clear "why unavailable" message (matching the
  existing `help.why_unavailable` pattern), not a crash.
- Query matches nothing: results list shows an explicit "No matches" row
  rather than going silently empty, so screen-reader users get positive
  confirmation the search ran.
- Pasting a multi-emoji string (e.g., copied sentence containing several
  emoji) into search: match only if the entire query is exactly one known
  sequence; otherwise fall through to ordinary text search, which will
  correctly find nothing and show "No matches."

---

## 20. Security, Privacy, and Licensing

- No new runtime network egress; no new entry needed in
  `network_egress_audit.py` for the shipped feature itself.
- Unicode and CLDR data are usable under the Unicode Consortium's data
  license (free use with attribution); `gemoji` and `iamcal/emoji-data` are
  MIT-licensed. Add attribution for these three sources to wherever QUILL
  already tracks third-party data/license notices.
- LLM-generated description text (Section 11) is original prose produced
  from factual Unicode metadata, not reproduced third-party copy; no
  licensing concern beyond normal review for accuracy.
- No user data leaves the machine as part of this feature; the only
  network calls in the entire feature happen inside the offline generator
  tool, run by maintainers, never by end users.

---

## 21. Testing Strategy

- `tests/unit/core/test_emoji_data.py`: category listing; name search;
  keyword search; emoticon-alias search; symbol-paste lookup; a completeness
  check that every entry in the committed catalog has a non-empty
  `description` (this is the regression test that enforces FR-5 — it fails
  the build if a future catalog regeneration ships an entry without a
  description).
- `tests/unit/ui/test_main_frame_emoji_picker.py`: dialog opens via
  `_show_modal_dialog`; selection updates the description pane; Insert
  writes the expected character and announces it — same shape as the
  existing `test_main_frame_gh_bridge.py`/`test_optional_components_dialog.py`
  UI tests.
- Update `tests/unit/ui/fixtures/dialog_inventory.json` and
  `main_frame_public_surface.json` for the new dialog and command.
- Generator tool gets its own smoke test asserting the composed
  modifier/ZWJ descriptions (Section 11.3) are well-formed given a small
  fixture set of base descriptions, without needing to call an LLM in CI.

---

## 22. Quality Gates and Acceptance Criteria

- 100% of catalog entries have a non-empty description (automated gate,
  Section 21).
- Alt+Period opens the dialog from the main editing surface with no
  conflicting binding.
- All three search modes (name, emoticon, symbol-paste) return the expected
  top result for a fixed regression list of common queries.
- Dialog passes the existing dialog-inventory and modal-button-contract
  gates like every other QUILL dialog.
- Feature is fully usable with `QUILL_SAFE_MODE=1` and with no network
  connection.

---

## 23. Implementation Plan (proposed waves)

1. **Wave 1 — data pipeline.** Build `generate_emoji_catalog.py` through
   Sections 11.1 and 11.3-11.4's templates/structure; produce a catalog with
   correct categories, names, keywords, and emoticon aliases but placeholder
   descriptions, to unblock UI work in parallel.
2. **Wave 2 — description generation.** Run the base-pictograph and flag
   generation batches (Section 11.2, 11.4), review, and replace placeholders
   with real descriptions across the full catalog.
3. **Wave 3 — core module and UI.** `emoji_data.py`, `EmojiPickerDialog`,
   command/menu/keymap wiring.
4. **Wave 4 — tests, dialog inventory, docs.** Full test coverage, fixture
   updates, user guide and changelog entries.

---

## 24. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| LLM-generated descriptions are inaccurate or inconsistent in tone. | Structured prompting per subgroup (Section 11.2), automated quality gate (Section 21), human spot-check sample (Section 11.5); corrections are a data fix, not a code change. |
| Generation batch (~1,750 entries) has real API cost. | Scoped explicitly as an implementation-phase decision (Section 11.2), not something this PRD authorizes by itself. |
| Unicode ships a new version with structural changes to category names. | Generator diff review catches this; category names are also unit-tested against the fixture catalog. |
| ASCII emoticon table (Tier 3) is inherently incomplete/subjective. | Documented as a curated, growable list (Section 9); not claimed as authoritative. |
| Flag descriptions must be factually correct, not just plausible-sounding. | Dedicated small batch with human cross-check against a reference source (Section 11.4), not folded into the bulk base-pictograph generation. |

---

## 25. Open Questions

- Exact final wording/placement of the Insert menu entry.
- Whether skin-tone/gender variants should appear as separate rows in the
  results list or be collapsed under their base entry with a secondary
  "choose variant" step — affects both UI complexity and how large the
  visible results list gets for common searches like "wave."
- Whether a "Recently Used" pseudo-category is worth adding post-v1.
- Whether the flag-description review should also cross-check against a
  second reference source given the accuracy bar for factual flag design.

---

## 26. Definition of Done

- Catalog covers 100% of current-version RGI emoji with correct category,
  name, keywords, emoticon aliases (where applicable), and a non-empty,
  reviewed description — enforced by an automated completeness test.
- Insert Emoji dialog ships behind the Insert menu and Alt+Period, passes
  the dialog-inventory and modal-button-contract gates, and works fully
  offline and in Safe Mode.
- User guide, changelog, and third-party data attribution updated.
- Generator tool and its data-source pins are documented well enough that a
  future maintainer can regenerate the catalog for a new Unicode version
  without re-deriving this design.
