# AI Menu Redesign and Prompt/Skill/Agent Strategy

**Status:** Draft for review
**Date:** 2026-06-27
**Branch:** 2.0-dev
**Owner:** Jeff
**Related:** [quill_end_to_end_agentic_ai_prd.md](quill_end_to_end_agentic_ai_prd.md), [quill-companion-prd.md](quill-companion-prd.md), [roadmap-2.0.md](roadmap-2.0.md)

---

## 1. Goal

Turn QUILL's AI surface from a long, scattered menu into a short, confident,
context-aware menu with one clear mental model. The user should feel that QUILL
has *one* AI that knows where they are and what they can do — not a drawer full
of overlapping tools. Every redundant surface collapses into one of four pillars:

1. **Ask Quill** — the one conversation (companion).
2. **Do** — context actions and agents, driven by the Concierge.
3. **AI Library** — the one place to manage Prompts, Skills, and Agents.
4. **AI Hub** — the one place to configure providers, engines, and sessions.

This is a UI/IA consolidation on top of the agentic stack that already ships. The
plumbing (tool gateway, permission broker, agent catalog, concierge, context
builder, provider truth) is built. The seams are what we are fixing.

---

## 2. What's wrong today (the honest inventory)

The AI menu lives under **Tools > AI Assistant** and currently holds about 36
items across 11 separator groups. The top-level `&AI` menu exists in code but is
gated behind `future.ai_menu_top_level` (locked off). The problems are not just
length — they are duplication of *concepts*.

### 2.1 Three chat front doors

| Surface | Backing | Notes |
| --- | --- | --- |
| Ask Quill (`_open_ask_quill`) | `build_companion_session` -> ConversationSession + gateway | The real, context-aware companion. The future. |
| Writing Assistant (`open_writing_assistant`) | `WritingAssistantDialog` (assistant_tools) | Older single-shot assistant. |
| Ask AI (`open_ask_ai`) | `AskAIDialog` | Generic chat. |

Three doors to "talk to the AI." Only Ask Quill is context-aware and gateway-routed.

### 2.2 Three prompt surfaces, two stores

| Surface | Store | Format |
| --- | --- | --- |
| Prompt Library (`open_prompt_library`) | `core.prompt_library.PromptLibrary` | `.pqp` |
| Prompt Studio (`open_prompt_studio`) | `core.assistant_prompts.CustomPrompt` + builtin presets | none (hands text to Writing Assistant) |
| Vision Prompt Manager (in Settings) | `ai.vision_prompts` | settings |

Two separate custom-prompt data stores (`prompt_library` and `assistant_prompts`)
that do not know about each other. A user who saves a prompt in one cannot find it
in the other.

### 2.3 Two agent systems, plus a linter

| Surface | Backing | Notes |
| --- | --- | --- |
| Agent Center (`open_agent_center`) | `core.assistant_agents.agent_profiles` | Old profile model. |
| Run Agent submenu (`append_agent_menu`) | `core.ai.agent_catalog` (15 agents) | New gateway catalog — the real agentic path. |
| Validate Agents (`open` linter) | `tools.agent_lint` | Dev/author tool. |

Two definitions of "agent." The Run Agent submenu is the one wired through the
Safe Editor Tool Gateway (permissions, diff preview, undo). Agent Center is legacy.

### 2.4 Config scattered, despite a Hub that already consolidates it

The PRD declares the **AI Hub** the single config front door, and the Hub already
merges provider/key/model/test. Yet the menu still surfaces **Switch AI Engine**,
**Set Up GitHub Copilot**, **AI Model**, and **AI Connection** as peers. The
consolidation happened in code but not in the menu.

### 2.5 Flat verb soup duplicating agent capability

Six inline verbs — Rewrite Selection, Summarize Selection, Expand Selection,
Generate Table of Contents, Continue Writing, Fix Grammar — sit as flat items.
These duplicate what the catalog agents and the **Selection Action Ring**
(`concierge.ring_actions`) already produce contextually ("Rewrite clearly",
"Shorten", "Review", ...). We have a context engine and aren't using it in the menu.

### 2.6 Five overlapping proofing entries

Check Grammar with AI, AI Spell Check, AI Spell Check Interactive, AI Grammar and
Style Check, plus Fix Grammar. A user cannot tell which to pick.

### 2.7 The rest (fine, but flat)

Translate (2), Transcribe/Translate Audio (2), Read Aloud / Stop / Export (4),
Document Q&A, AI Thesaurus, Train Writing Style, Writing Instructions. All
reasonable features, all presented as one long undifferentiated list.

---

## 3. The strategy: one model, four pillars

### 3.1 The unifying idea — a Prompt/Skill/Agent continuum

Stop treating Prompts, Skills, and Agents as three unrelated things in three
menus. They are **three points on one spectrum of saved AI intent**:

```
Prompt            Skill                         Agent
single instruction   multi-step workflow            autonomous, tool-using
"Rewrite warmly"     "Draft -> critique -> revise"   "Review repo and open PR"
.pqp                 .sqp                            catalog .md + permissions
runs once            runs a fixed pipeline           reasons and uses tools
```

One manager — the **AI Library** — presents all three with the *same* verbs:
**Run, New, Edit, Duplicate, Enable/Disable, Import, Export, Share**. The user
learns one interaction model and one sharing story (`.pqp` / `.sqp` / agent
bundle). "Promote" lets a Prompt graduate to a Skill, and a Skill to an Agent,
so the continuum is real, not cosmetic.

This subsumes Prompt Library, Prompt Studio, Skill Library, Agent Center, and the
Vision Prompt Manager into a single tabbed surface with one data model.

### 3.2 The four pillars

1. **Ask Quill** is the single conversation. Voice is a mode of it, not a separate
   door. Writing Assistant and Ask AI are retired into it.
2. **Do** is context-first. The top of the menu shows live, situational actions
   from the Concierge / Action Ring instead of a fixed verb list. "Run Agent"
   stays as the explicit catalog entry.
3. **AI Library** manages the Prompt/Skill/Agent continuum (3.1).
4. **AI Hub** owns all configuration: providers, keys, models, engine switching,
   Copilot onboarding, sessions/branches, consent, safe mode. Nothing config-
   related lives outside it.

---

## 4. The proposed menu

Promote to a top-level **`&AI`** menu (flip `future.ai_menu_top_level` to on for
2.0; keep the Tools fallback for one release behind the flag). Target shape:

```
&AI
  Ask &Quill...                     Alt+Q        <- the companion, the front door
  Ask Quill by &Voice...            Alt+Shift+Q
  ------------------------------------------------
  What can I do &here?              (opens the Concierge action list for context)
  &Rewrite / Improve Selection >    (dynamic: Action Ring entries for the context)
  Run &Agent >                      (catalog agents, via the gateway)
  ------------------------------------------------
  &Proofread >                      (Spell, Spell Interactive, Grammar & Style)
  &Translate >                      (Selection, Document)
  Read A&loud >                     (Selection, Document, Stop, Export as Audio)
  Tra&nscribe >                     (Audio File, Audio to English)
  &More >                           (Document Q&A, Thesaurus, Generate TOC, Train Style, Writing Instructions)
  ------------------------------------------------
  AI &Library...                    (Prompts + Skills + Agents, unified)
  AI &Hub...                        (providers, engines, models, sessions, consent)
  ------------------------------------------------
  Use Artificial &Intelligence      (checkbox; mirror of the Hub master switch)
```

Item count at the top level drops from ~36 to ~13, each either a single high-value
action or a clearly-labeled submenu. Everything is still reachable; nothing is
buried more than one level deep.

### 4.1 What moves where

| Today | Tomorrow |
| --- | --- |
| Ask Quill | Ask Quill (unchanged, now the canonical door) |
| Writing Assistant, Ask AI | retired into Ask Quill |
| Rewrite/Summarize/Expand/Continue/Fix Grammar | Action Ring submenu (context-driven) + Run Agent |
| Generate TOC | More > |
| Prompt Library, Skill Library, Prompt Studio, Agent Center, Vision Prompt Manager | AI Library (one manager) |
| AI Hub, Switch AI Engine, Set Up Copilot, AI Model, AI Connection, Session Branches | AI Hub (one config center) |
| Validate Agents | AI Library > Agents tab > "Validate" (author action), still CLI-available |
| Check Grammar / AI Spell / Spell Interactive / Grammar & Style | Proofread > |
| Translate Selection/Document | Translate > |
| Transcribe/Translate Audio | Transcribe > |
| Read Aloud x3 + Export Audio | Read Aloud > |
| Document Q&A, Thesaurus, Train Style, Writing Instructions | More > |
| Accessibility Tune-Up | Action Ring ("Check accessibility") + a catalog agent |

---

## 5. The magical part (why this feels amazing, not just tidy)

1. **Context-first top of menu.** "What can I do here?" and the Rewrite/Improve
   submenu are generated by `concierge.suggest` / `ring_actions` from the live
   file type, selection, outline, cursor section, and git state. Open the menu in
   a Python file with a selection and you see "Explain", "Document", "Tidy"; open
   it in prose and you see "Rewrite clearly", "Shorten", "Make warmer", "Review".
   The menu adapts to the user. The engine for this already exists and is unit-
   tested; we are finally surfacing it.

2. **One conversation that remembers.** Ask Quill is the single door, it can see
   the document, run tools through the gateway, and every edit is preview-gated
   and undoable. Voice is the same conversation, not a different feature.

3. **A real continuum, not three drawers.** Save a great instruction as a Prompt;
   when it needs steps, "Promote to Skill"; when it needs to reason and use tools,
   "Promote to Agent." Same Run button throughout. Sharing is one consistent story.

4. **Quiet confidence for screen-reader users.** Short top-level list, predictable
   submenu grouping, every item with a meaningful accessible name and a status
   announcement on run. Fewer, better-labeled choices = faster keyboard review.

---

## 6. Data model and code consolidation

This is the load-bearing work; the menu is the visible 10%.

### 6.1 Unify the custom-prompt stores

`core.prompt_library` (`.pqp`, used by Prompt Library) and `core.assistant_prompts`
(`CustomPrompt`, used by Prompt Studio) must become **one store**. Recommended:
make `prompt_library.PromptLibrary` the canonical store, write a one-time,
reversible migration that imports `assistant_prompts` custom prompts into it
(mirroring the `consolidate_provider_keys` pattern), and have the old API read
through to the new store during a deprecation window.

### 6.2 Retire the legacy agent profile system

`core.assistant_agents.agent_profiles` (Agent Center) is superseded by
`core.ai.agent_catalog`. Map any still-useful built-in profiles onto catalog
agents, then route the AI Library Agents tab solely at the catalog. The linter
(`tools.agent_lint`) becomes the "Validate" action on that tab and stays a CLI gate.

### 6.3 Fold the chat dialogs

`WritingAssistantDialog` and `AskAIDialog` capabilities (provider setup strip,
preset prompts) move into Ask Quill's companion dialog. Keep the classes for one
release as thin shims that open Ask Quill, then delete.

### 6.4 The AI Library dialog

New surface (or rename/extend Prompt Studio) with three tabs — **Prompts**,
**Skills**, **Agents** — over one verb set: Run, New, Edit, Duplicate,
Enable/Disable, Import, Export, Validate (agents), Promote. Built on the existing
list-detail dialog patterns and the modal contract (`apply_modal_ids`,
`_show_modal_dialog`).

### 6.5 Make AI Hub the only config door

Move Switch Engine (as a Hub quick-switch + optional status-bar control), Copilot
onboarding, AI Model, AI Connection, and Session Branches into Hub tabs. The
top-level menu keeps only `AI Hub...` and the `Use AI` checkbox.

---

## 7. Accessibility requirements (non-negotiable)

- Every menu item and submenu has a clear accessible name; dynamic Action Ring
  items include their context in the name ("Rewrite clearly (on the selection)").
- Dynamic items must be stable within an open menu session (build once on open).
- All new/changed dialogs go through `_show_modal_dialog` + `apply_modal_ids`;
  pass the dialog inventory and button-contract gates.
- Running any action announces start and result via the status/announcement path.
- Keyboard reachability for everything; no action is mouse-only.
- Menu mnemonics stay unique within the new `&AI` menu.

---

## 8. Phased delivery

Each phase ships independently and leaves the menu coherent.

- **Phase 0 — Menu IA (low risk, high visible win).** Flip
  `future.ai_menu_top_level` on for 2.0. Regroup existing commands into the
  Section 4 submenus (Proofread, Translate, Read Aloud, Transcribe, More). No new
  backends. Update `menu_lint`, the accessibility menu test, and the user guide.
- **Phase 1 — Context-first top.** Surface Concierge / Action Ring at the top of
  the menu ("What can I do here?", dynamic Rewrite/Improve submenu). Retire the
  six flat verbs into it. Keep Run Agent explicit.
- **Phase 2 — One conversation.** Make Ask Quill the only chat door; shim Writing
  Assistant and Ask AI to it.
- **Phase 3 — AI Library.** Build the unified Prompts/Skills/Agents manager;
  migrate the custom-prompt stores (6.1); retire Agent Center (6.2). Remove Prompt
  Library / Skill Library / Prompt Studio / Vision Prompt Manager menu entries.
- **Phase 4 — Hub as sole config.** Move Switch Engine, Copilot, Model,
  Connection, Sessions into the Hub. Trim the menu to Library + Hub + Use AI.
- **Phase 5 — Polish.** Promote (Prompt->Skill->Agent), status-bar engine
  control, delete the deprecated shims and old stores after the deprecation window.

---

## 9. Risks and decisions to confirm

- **Store migration.** Merging two custom-prompt stores must be reversible and
  must not lose user prompts. Mirror the provider-key consolidation pattern.
- **Dynamic menu cost.** Building Concierge suggestions on every menu-open must be
  cheap and must never block the UI thread; the functions are pure and fast, but
  guard with a timeout/fallback to a static list.
- **Deprecation window.** How long do Writing Assistant / Ask AI / Agent Center
  shims live before deletion? Proposal: one minor release.
- **Top-level menu default.** Confirm we want `&AI` top-level on by default for
  2.0 (recommended) vs. staying under Tools.
- **Module size budgets.** `assistant_tools.py` (~2000 lines) and
  `main_frame_menu.py` are already large; extracting the new Library dialog and
  the dynamic-menu builder should *reduce* both. Update `module_size_budgets.json`
  as a ratchet.

---

## 10. Confirmed decisions (2026-06-27)

1. **Top-level menu:** Promote AI to a real top-level `&AI` menu, unconditionally
   — not gated behind `future.ai_menu_top_level`. The feature flag is retired as a
   placement switch; AI is simply always top-level.
2. **Name:** "AI Library" is the name for the unified Prompt/Skill/Agent manager.
3. **Promote continuum:** Prompt -> Skill -> Agent "Promote" is in 2.0 scope.
4. **Accessibility Tune-Up:** Stays a first-class, top-of-menu item (not buried in
   a submenu), given the screen-reader audience — in addition to being reachable
   as an agent / Action-Ring action.

## 11. Build status

- **Phase 0 (menu IA) — DONE.** AI promoted to a top-level `&AI` menu; the ~36
  flat items regrouped into the Section 4 structure (Ask Quill + Voice,
  Accessibility Tune-Up first-class, Rewrite & Improve + Run Agent, and the
  Proofread / Transform / Translate / Read Aloud / Transcribe / More /
  AI Library / Engine & Sessions submenus). `menu_lint` gate and its tests
  updated to drop the obsolete "AI Assistant" Tools cluster.
- **Phase 1 (context-first top) — DONE.** The "Rewrite & Improve" submenu is
  generated from the Selection Action Ring (`concierge.ring_actions`), and a new
  top-of-menu **"What can I do here?..."** item (`quill/ui/concierge_menu.py`)
  surfaces the full Concierge `suggest`: it builds a `ConciergeContext` from the
  live file type, selection, outline, and AI state, presents an ordered native
  single-choice list, and runs the chosen suggestion's command through the
  registry (unknown targets refused, not raised). Built as its own module so the
  menu/main_frame size budgets do not grow. Tests in `test_concierge_menu.py`.
- **Phase 3 store consolidation — DONE (the load-bearing half).** The two
  custom-prompt stores are now one: `quill/core/prompt_migration.py`
  (`consolidate_prompts`) copies every legacy `assistant_prompts` prompt into the
  canonical `PromptLibrary` under a stable `assistant-<id>` id, and it runs at
  startup next to the key migration. It is reversible, non-destructive, and
  idempotent (mirrors `consolidate_provider_keys`); a new
  `PromptLibrary.upsert_external()` does the by-id insert. **User-visible effect
  today:** prompts saved in Prompt Studio now appear in the Prompt Library
  (AI Library > Prompts) automatically — the scatter is gone for prompts. Covered
  by `tests/unit/core/test_prompt_migration.py` (6 cases).

- **Architectural finding — the three kinds are not symmetric yet.** Prompts have
  a persistent, now-unified store; Agents have the bundled `agent_catalog` (.md);
  but **Skills have no persistent store** — `.sqp` packs are import-and-run only
  (SkillLibraryDialog parses a file and runs it; nothing is saved). A truly
  uniform 3-tab "Prompts / Skills / Agents" manager needs a persistent skills
  store first. **Decision needed:** build a skills store (so Skills get the same
  Run/New/Edit/Enable/Promote verbs), or ship the unified dialog with Skills as a
  browse/import/run tab for now and add the store later. See §12.

- **Phase 2 core (the symmetric foundation) — DONE.** The three kinds now share a
  uniform, persistent, promotable model, all wx-free and unit-tested:
  - `quill/core/skill_store.py` — `SkillStore`, the persistent installed-skills
    store that closes the asymmetry (list / import / export / enable / remove,
    `.sqp` source preserved verbatim, slug ids, enabled-state index). 11 tests.
  - `quill/core/ai/library.py` — `LibraryItem` (one uniform shape over Prompt /
    Skill / Agent) plus the **Promote continuum**: `prompt_to_skill_source`
    (wraps a prompt as a valid one-step `.sqp`) and `skill_to_agent_markdown`
    (generates a valid agent `.md` from a skill's steps). Tests assert the
    generated source actually parses/validates. 6 tests.
  - Catalog stays bundled-only and deterministic; Promote-to-Agent will surface
    the generated `.md` for the user to save (a user-agents catalog dir is a
    later enhancement so promoted agents become first-class).

- **Phase 2 UI (unified AI Library dialog) — DONE.** `quill/ui/ai_library_dialog.py`
  is a `wx.Notebook` over `library.LibraryItem` with three tabs (Prompts / Skills /
  Agents), one uniform verb set, and the real Promote continuum: Prompt -> Skill
  installs an `.sqp` into `SkillStore`; Skill -> Agent generates a reviewable agent
  `.md` the user can save (`_PromotedAgentDialog`). Prompt/skill Run reuse the
  tested `ai_chat.send_prompt` / `skill_pack.run_skill` primitives and the existing
  `_PromptEditDialog` / `_Skill*Dialog` editors; agent Run goes through the gateway.
  The Agents-tab **Validate** folds in the full standards-linter dialog (the same
  one the CI gate uses) via `on_validate_agents`. The transitional six-item submenu
  collapses to a single **"AI Library..."** item; Prompt Studio / Writing Assistant
  / Agent Center / Validate Agents stay reachable as commands during the
  deprecation window. `open_skill_library` was extracted to a module helper to keep
  `main_frame.py` from growing. Smoke + behavior tests in `test_ai_library_dialog.py`;
  routing test in `test_main_frame_libraries.py`.

- **Phase 2 (one conversation door) — menu-level DONE.** The AI menu now exposes
  only Ask Quill + Ask Quill by Voice as chat doors; Writing Assistant and Ask AI
  are no longer menu entries. Retiring their dialog classes into thin shims and
  deleting them is Phase 5 (post-deprecation), so no risky redirects were made.

- **Phase 4 (Hub as sole config) — DONE.** Engine switching and GitHub Copilot
  setup live in the Hub's Engines tab (`ai_hub_engines_panel.py`); Session Branches
  folded into a new Hub **Sessions** tab (`ai_hub_sessions_panel.py`, mirroring the
  Engines panel). The "Engine & Sessions" submenu is gone entirely — the AI menu's
  config region is now just **AI Hub...** plus the Use AI switch. All three are
  still reachable from the status-bar engine cell / cycle hotkey / command palette.

- **Phase 5 — functionally DONE; deletions deferred by design.**
  - **Promote continuum + first-class agents — DONE.** Prompt -> Skill -> Agent all
    work; Skill -> Agent now saves into a real user-agents catalog
    (`agent_catalog.user_agents_dir` / `save_user_agent` / `load_full_catalog`), so
    a promoted agent appears in the Agents tab and runs through the gateway
    immediately.
  - **Status-bar engine control — already present** (`open_ai_engine_switcher` is
    the status-bar engine cell's Enter action; `ai_engine_status_text` drives the
    label; `cycle_ai_engine` is the hotkey).
  - **Deprecated dialogs — RETIRED (2026-06-28).** Chat is now one magical door,
    and the redundant management dialogs are gone:
    - **Ask AI → Ask Quill.** `AskAIDialog` deleted (`ai_chat_dialog.py` is now just
      the read-only `AIResponseDialog`); `open_ask_ai` / `tools.ask_ai` removed. The
      unified, context-aware companion (`tools.ask_quill_chat`) is the only chat door.
    - **Prompt Studio → AI Library (Prompts).** `PromptStudioDialog` deleted; its
      entry points redirect to `open_ai_library`.
    - **Agent Center → AI Library (Agents).** `AgentCenterDialog` deleted; redirects
      to `open_ai_library`.
    `assistant_tools.py` ratcheted 2020 → 1577; the live dialogs (RunPython,
    AccessibilityAgent, DiffReview, ModelPicker, Hub, Connection) are untouched, and
    the live `assistant_agents` / `assistant_prompts` modules stay (they back the
    agent-run path and the prompt migration). Dialog-specific tests removed;
    inventory + public-surface snapshots regenerated.
  - **Writing Assistant — RETAINED on purpose (not a chat door).** It is the result
    surface for the inline writing-action verbs (rewrite / summarize / continue /
    fix grammar), which carry nuanced behavior — paragraph-vs-document fallback and a
    `summarize` agent via `build_agent_plan`. Those verbs are already out of the menu
    (the Action Ring + Run Agent are the menu path); fully retiring the dialog means
    rebuilding the verb→result flow onto the gateway, a deliberate feature refactor
    rather than a deprecation. Scoped as a future change; nothing user-facing depends
    on it as a "door" today.
  - `core.assistant_prompts` stays until the startup prompt migration
    (`prompt_migration.consolidate_prompts`) is sunset — removing it would orphan
    unmigrated user prompts.

## 12. Decision needed: the skills store

To make the unified manager symmetric, recommend building a small persistent
skills store mirroring `PromptLibrary` (an installed-skills directory of `.sqp`
packs with list / import / enable / remove), wx-free and unit-tested, before the
3-tab dialog. The alternative is a thinner first cut where the Skills tab only
imports and runs (no saved library), with the store added in a follow-up. The
former makes the dialog and the Promote continuum cleaner; the latter ships the
dialog sooner.
