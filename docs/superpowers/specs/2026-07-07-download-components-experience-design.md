# Download Optional Components — the warm, complete experience (design)

Extends GitHub issue #874 (the unified missing-component surface). #874 wired
the *routing* into one picker; this spec makes that picker a first-class,
delightful place: reordered by importance, with install **and** removal, sizes
on every row, a rich description, and a "hear this voice" test — then routes the
scattered startup prompts into it.

## Problem

`quill/ui/optional_components_dialog.py` (`show_optional_components_picker`) is
today a thin list: name / status / size / category columns, a Download button,
and a one-line detail label. It works, but it is not the "magical" hub it should
be, and several rough edges are user-visible:

1. **Order is by category, not importance.** `gather_optional_components()`
   (`quill/core/optional_components.py`) emits engine → voices → tool →
   dictionaries. Users reach for Pandoc and the braille pack first; those should
   lead.
2. **No removal.** A component can be installed but never uninstalled from here,
   and there is no way to reclaim the disk or turn a feature back off.
3. **Missing sizes.** Spell-check dictionary rows pass `size_hint=""` (they show
   "—"); every row should state its size.
4. **Thin description.** The single detail line can't convey what a component
   enables, its size, and its impact.
5. **No confidence check.** After a voice engine installs, nothing lets the user
   *hear* it — the reassurance that the install actually worked.
6. **Focus flow.** The picker closes (`EndModal`) and the download runs behind
   it (`open_optional_components` in `quill/ui/main_frame_speech.py` dispatches
   after the modal closes). The user is dropped back to the document, not kept
   in the hub where the row now reads "Installed".
7. **Scattered entry.** The startup braille-pack prompt
   (`main_frame._maybe_prompt_braille_pack_install`) and #874's failure routes
   are separate journeys; several should simply land the user *here*, guided.

## Non-goals

- Not a new download engine. Each component keeps its tested, progress-reporting
  installer (`_download_kokoro_models`, `install_piper`, `download_braille_pack`,
  `fetch_component`, …). This is a UI + orchestration layer over them.
- Not per-voice rows. Voice *engines* are one row each (Kokoro, Piper, eSpeak,
  DECtalk); individual voice-model downloads stay in the Voice Browser.
- Not removing bundled/system components. Remove targets only QUILL-downloaded
  copies under the app-data dir; it never deletes a system Pandoc, an upgrader's
  `{app}` copy, or anything QUILL did not fetch.

## Design

### 1. Importance ordering

`OptionalComponent` gains an integer `priority` (lower = higher in the list);
`gather_optional_components()` sorts by `(priority, name)`. Proposed order:
Pandoc, braille pack, whisper.cpp, Kokoro, Piper, eSpeak, DECtalk, ffmpeg,
libmpv, MathCAT, Vosk, then the spell-check dictionaries (alphabetical). The
dialog renders in returned order (no re-sort in the UI).

### 2. Sizes on every row

Give the dictionary rows a real `size_hint`. Two options — decide in
implementation:
- **(a)** a static per-dictionary estimate ("~4 MB"), simplest; or
- **(b)** read the pinned asset's size where one exists (the `release_assets`
  entries know their `filename`; a size field could be added).
Recommend (a) for now (dictionaries are all a few MB), with a TODO for (b).

### 3. Rich description box

Replace the one-line `optional_components_detail` StaticText with a **read-only
multiline** `TextCtrl` (`wx.TE_MULTILINE | wx.TE_READONLY`). On row focus it
shows: what the component enables, its size, its on-disk footprint/impact, its
license note, and its current state ("Installed — Remove to free ~X and turn off
Y" / "Not installed — Download to enable Y"). Copy is warm and concrete. The
text is built by a wx-free `describe_component(component)` helper in
`optional_components.py` so it is unit-testable.

### 4. Install + Remove, installed-state controls

- The **Download** button is disabled (and labeled "Installed") when the focused
  row is installed; enabled otherwise.
- A **Remove** button is enabled only when the focused row is installed and is a
  QUILL-downloaded copy that can be removed.
- Removal logic is wx-free in `optional_components.py`:
  `removable_path(component_id) -> Path | None` (None = nothing QUILL can safely
  remove, e.g. a system Pandoc or bundled copy) and
  `remove_component(component_id) -> bool` (delete that path, clear any discover
  cache). The dialog confirms, calls it, then refreshes the row.

### 5. Remove closes the loop (disable dependent features)

Removing a component turns off what it powered. Most engine availability is
already *dynamic* (e.g. `kokoro_engine_ready()`, `discover_piper_executable()`),
so read paths degrade on their own. What needs explicit handling is durable
settings/menus that assume a component (e.g. braille translation surfaces, a
selected Read Aloud engine that just went away). Introduce a small map,
`COMPONENT_FEATURES: dict[str, tuple[str, ...]]`, from component_id to the
feature ids it enables, and on removal:
- if the removed engine is the *active* `read_aloud_engine`, reset it to the
  always-present SAPI 5 floor; and
- surface (do not silently flip) any feature the component gated, via the
  existing feature manager.

**Open question for implementation:** exact depth — reset active-engine +
refresh menus (recommended) vs. also toggling `features.json` entries. Pin the
concrete braille and Read Aloud call sites first, the way #874 pinned its sites.

### 6. Hear-this-voice test button

For voice-engine rows (Kokoro, Piper, eSpeak, DECtalk — those with an installed
speech engine), a **Test** button synthesizes a short, fixed QUILL blurb in a
default voice for that engine and plays it, so the user hears success. Wx-free
core: `TEST_BLURB` constant + reuse of `synthesize_with_kokoro` /
`synthesize_with_piper` / the eSpeak/DECtalk paths to a temp WAV; the dialog
plays it on the UI thread and announces "Playing a sample of <engine>…". The
button is hidden for non-voice components and disabled until the engine is
installed.

**Open question:** the blurb text. Recommend one short, on-brand line (a new
`TEST_BLURB` in `optional_components.py`), e.g. *"This is QUILL, reading to you
with the <engine> voice."* — confirm wording.

### 7. Keep the hub open; focus to progress, then back

Restructure so the picker **stays open** and drives the download in place:
- Activating Download runs the component's installer, showing the existing
  `AIProgressDialog` (which takes focus and announces progress).
- On completion the progress dialog closes, **focus returns to the picker**, the
  row refreshes to "Installed", Download disables, Remove/Test enable, and the
  description updates — the user never leaves the hub.
- This replaces the current "return the chosen id and `EndModal`, dispatch after
  close" flow in `open_optional_components`; the dispatch table moves into the
  dialog (or a controller it calls back into).

### 8. Route the scattered prompts here (with a guiding popup)

- **Startup braille prompt** (`_maybe_prompt_braille_pack_install`): instead of
  its own yes/no install, open the components dialog **preselected on braille**
  (using #874's `preselect`) and show a one-time guiding popup on landing:
  "You're in Download Optional Components. Braille pack is selected — press
  Download to set up braille translation, or Escape to skip." Gate the popup on
  a `seen_components_intro` setting so it shows once.
- **#874 failure routes** (`_offer_optional_component` / `_nudge_once`): already
  land here preselected; they inherit the richer dialog automatically.

### 9. Warm and fuzzy throughout

Encouraging, plain-language copy on buttons, descriptions, and announcements;
the Test button; the guiding popup; and the stay-in-place flow together make the
hub feel like a friendly setup assistant rather than a bare table.

## Testing

- `optional_components.py`: `priority` ordering; `describe_component` text for an
  installed vs not-installed component; `removable_path`/`remove_component`
  (returns None for a non-QUILL copy; deletes a fake app-data copy); dictionary
  rows now carry a non-empty size; `COMPONENT_FEATURES` maps only real feature
  ids. All wx-free, unit-tested.
- Source-contract tests (matching this beta's convention) for the dialog:
  Download disabled when installed, Remove present, Test present for voice rows,
  multiline read-only description, focus-returns-to-list after install.
- `_maybe_prompt_braille_pack_install` routes to `open_optional_components(
  preselect="braille")` and shows the one-time popup.
- The Test path: `synthesize_*` called with the engine's default voice to a temp
  file (mocked synth), then played.

## Files touched

`quill/core/optional_components.py` (priority, describe_component,
removable_path/remove_component, COMPONENT_FEATURES, TEST_BLURB, dict sizes),
`quill/ui/optional_components_dialog.py` (multiline description, Download/Remove/
Test buttons, installed-state gating, stay-open + focus-return flow),
`quill/ui/main_frame_speech.py` (`open_optional_components` restructure, Test/
Remove dispatch), `quill/ui/main_frame.py`
(`_maybe_prompt_braille_pack_install` reroute + guiding popup, #874 helpers),
`quill/core/settings.py` (`seen_components_intro` and any nudge state), plus
new/updated tests in `tests/unit/core/test_optional_components.py` and
`tests/unit/ui/`.

## Open questions to settle in the implementation plan

1. Remove → feature-disable depth (§5): active-engine reset + menu refresh only,
   or also `features.json` toggles?
2. Test blurb wording (§6).
3. Dictionary sizes: static estimates (§2a) or add a size field to
   `release_assets` and read it (§2b)?
4. Should Remove also be offered for a system-provided Pandoc (no — out of
   scope), and for the braille pack when it came from an upgrader's `{app}` copy
   (no — `removable_path` returns None there)?
