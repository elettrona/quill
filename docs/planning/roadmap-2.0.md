# QUILL 2.0 — Plan of Record (scope anchor)

> **What 2.0 is.** QUILL 2.0 is the **agentic AI platform**: unify QUILL's existing
> AI stack behind one provider-neutral, multi-harness core whose single front door
> is the AI Hub, with a Safe Editor Tool Gateway, a Permission Broker, a declarative
> Agent Catalog, and an optional layer of interchangeable **harnesses** (Native plus
> SDK packs). The authoritative specification is
> [`quill_end_to_end_agentic_ai_prd.md`](quill_end_to_end_agentic_ai_prd.md); this
> file is the live build tracker against it.
>
> **What 2.0 is not.** The other items historically deferred "to 2.0" in
> [`roadmap.md`](roadmap.md) §5 are **not** part of the 2.0 theme. Many are
> candidates to slot into a **1.xx** release instead. They are parked in §3 below so
> the intent survives, but they do not gate 2.0 and should not be built under the
> 2.0 banner unless explicitly re-scoped.
>
> **Branch.** 2.0 work lives on the `2.0-dev` branch (worktree at `S:\QUILL-2.0`).
> Pull shipping fixes forward with `git merge main`; do not merge `2.0-dev` back into
> `main` until 2.0 is ready to ship. Commit history on this branch is the working
> record from which the user guide, release notes, and PRD updates are written at the
> end.

**Created:** 2026-06-25. **Last updated:** 2026-06-25 (Phase 1 Tier A foundation
complete; harness layer + three SDK packs (OpenAI/Claude/Copilot); Agent Catalog + launch set; Streaming
Event Bridge; native-backend Responder; opt-in editor wiring validated vs live
Claude; Concierge + Selection Action Ring model; native tool-calling loop; admin
policy. Remaining: provider consolidation (§7, Tier B), the AI Hub UI (Tier C),
and provider function-calling planner / live SDK-pack validation).

---

## 0. Principles carried forward

The 2.0 bar is the 1.0 bar (PRD §4). Every change must:

- Be **screen-reader-first** and keyboard-clear; balanced announcements, no token spam.
- Be **optional and off by default**. Base QUILL runs with `provider = "off"`; it
  launches, edits, and saves with AI fully off, and in Safe Mode every harness is
  disabled.
- Keep **QUILL owning the editor**: agents never touch wx controls; they act only
  through the Safe Editor Tool Gateway, which uses the existing replace/undo path.
- Land on QUILL's invariants: atomic storage, the dialog contract, the announcement
  grammar, Safe Mode, the network-egress audit, and the GATE-11 size budget.
- Route every medium+ edit through `diff_review` with one-step undo.
- Honour platform scope: Windows (primary), macOS (supported); Linux/Unix is not a
  target.

Consolidation precedes invention (PRD §23.1): one provider truth, one gateway, one
permission model, one diff/undo path, one activity log — *then* harnesses.

---

## 0a. Landing strategy: what can ship in 1.0 / 1.xx invisibly

Much of the 2.0 foundation is **wx-free, additive, and off until something calls
it.** That work can land on `main` (1.0 / 1.xx) *before* 2.0 ships, with **no
user-visible change**, to de-risk 2.0 and bring structural stability early. The
classification below is an explicit implementation decision, not just planning.

Three tiers:

- **Tier A — Invisible, landable in 1.0 now.** Dormant infrastructure: new modules
  with no menu item, no dialog, no behavior path until wired. Pure additive code +
  unit tests. Zero user-facing change; benefit is latent (structure, test coverage,
  a stable surface for 2.0 to build on) and the risk is essentially nil because
  nothing in the shipping app imports it yet. **Candidate to cherry-pick to `main`.**
  - `ai/events.py` (event vocabulary) — Done.
  - `ai/permissions.py` (Permission Broker) — Done.
  - `ai/activity_log.py` (Activity Log) — Done.
  - `ai/tool_gateway.py` (Safe Editor Tool Gateway) — Done.
  - `ai/context_builder.py` (Context Builder) — Done.
  - `ai/harness/` protocol + registry + capabilities (types only; no pack imported) — Done.
  - `ai/harness/native.py` Native harness + `responder_from_backend` adapter — Done.
  - `ai/agent_catalog.py` + `core/schemas/agent.json` + `ai/agents/*.json` launch set — Done.
  - `ai/event_bridge.py` (Streaming Event Bridge announcement mapping) — Done.
  - `ai_packs/` three SDK harness packs — OpenAI/Claude/Copilot (lazy; report unavailable until installed) — Done.

- **Tier B — Invisible-if-careful, fits 1.xx behind tests.** Active consolidation
  that changes an internal path users should not notice if the migration is correct,
  and that genuinely improves stability *now* by removing seams. Medium risk;
  gate behind the existing AI tests + reversible migration. Best shipped in a **1.xx**
  point release, not silently in 1.0 GA.
  - One provider truth (PRD §7): converge `ai_chat.PROVIDERS` into `assistant_ai`;
    reversible one-time key migration. Removes the dual-catalog bug surface.
  - Route the existing Ask Quill / Writing Assistant edits through the gateway +
    `diff_review` + the activity log. Same diff/undo behavior the user already sees,
    now uniform and audited. Stability win; must prove no regression.
  - Native harness wrapping today's `run_agent` loop behind the gateway (no new UI).

- **Tier C — Visible; 2.0 only.** Anything the user can see or that adds surface
  area. These define 2.0 and must not be slipped into 1.0.
  - AI Hub command center (Home/Agents/Sessions/Activity/Harnesses/Permissions tabs).
  - The optional SDK harness packs (OpenAI/Claude/Copilot) and their extras.
  - Declarative Agent Catalog as a listed, runnable set; Selection Action Ring;
    Concierge; Streaming announcements wired to the UI.

**Implementation consequence.** Build Tier A on `2.0-dev` (as now), and once a Tier A
module is proven, it is eligible to cherry-pick onto `main` for a 1.0/1.xx release —
it carries no behavior and only adds tested, dormant infrastructure. Tier B is the
natural content of one or more **1.xx** releases that quietly harden the shipping AI
stack. Tier C stays on `2.0-dev` until the 2.0 release. The Phase tables in §1 below
tag each row with its tier.

---

## 1. The 2.0 build: agentic AI platform

Phases below mirror PRD §18 (priority order, not calendar). The status column is the
live tracker; update it as commits land on `2.0-dev`.

### Phase 1 — Consolidate and formalize (foundation)

Tier (see §0a): A = invisible/landable in 1.0 now; B = invisible-if-careful, 1.xx.

| Item | PRD | Tier | Status |
| --- | --- | --- | --- |
| Event vocabulary (`ai/events.py`) | §14 | A | Done |
| Permission Broker (`ai/permissions.py`) | §10 | A | Done |
| Activity Log (`ai/activity_log.py`) | §9, §14 | A | Done |
| Safe Editor Tool Gateway (`ai/tool_gateway.py`) | §9 | A | Done |
| Context Builder (`ai/context_builder.py`) | §11 | A | Done |
| One provider truth (converge `ai_chat.PROVIDERS` into `assistant_ai`) | §7 | B | Not started |
| Route existing AI edits through gateway + `diff_review` | §12 | B | Opt-in path done: `ui/agent_editor_host.py` (EditorHost over MainFrame) + `tools.ai_agent_gateway` command behind `QUILL_AI_AGENT_GATEWAY`; validated end-to-end vs live Claude. Making it the default path is the remaining Tier B step. |

### Phase 2 — AI Hub as command center

| Item | PRD | Status |
| --- | --- | --- |
| Promote `AIHubDialog` to Home/Agents/Chat/Sessions/Activity/Providers/Harnesses/Audio/Permissions/Advanced (per-tab modules for GATE-11) | §5 | Not started (Tier C, visible) |
| Streaming Event Bridge -> balanced announcements | §6, §14 | Core done (`ai/event_bridge.py`); UI subscription pending (Tier C) |
| Concierge "What can I do here?" on Home + status bar | §6 | Catalog agent `quill-concierge` exists; UI surface pending (Tier C) |

### Phase 3 — Declarative Agent Catalog + native tool-calling loop

| Item | PRD | Status |
| --- | --- | --- |
| `core/schemas/agent.json` + catalog loader (`ai/agent_catalog.py`) | §13 | Done |
| Promote `accessibility_agent` + the four `AgentProfile`s; add Markdown Publisher, Code Doctor, GitHub Maintainer, PRD Architect, Release Notes Builder, Concierge | §13 | Done (11-agent launch set in `ai/agents/`) |
| Upgrade native harness to a real broker-gated, event-streamed tool-calling loop | §8.1 | Core done: `ai/tool_loop.py` (planner-driven, gateway-gated, recoverable denials, step cap). Provider function-calling planner is the remaining piece. |
| Selection Action Ring + hunk-preview clean-up + accessibility review on catalog agents | §6 | Model done: `ai/concierge.py` `ring_actions` (+ Concierge `suggest`); the wx ring/Home UI is the remaining Tier C piece. |

### Phase 4 — Local + BYOK polish

| Item | PRD | Status |
| --- | --- | --- |
| Harden Ollama/local + OpenAI-compatible/LiteLLM base-URL flows on the consolidated store; test-connection, model selector, cost/context warnings | §18.4 | Not started |

### Phase 5 — Harness layer + harness packs (the multi-harness promise)

Three SDK packs ship — **OpenAI Agents, Claude Agent, GitHub Copilot**. Each is an
optional extra, lazily imported, never required; an uninstalled pack reports
`(False, "Install the X pack")` and QUILL keeps working. Every pack bridges to the
**same** gateway + broker + diff/undo and emits normalized `AgentEvent`s; none edits
the buffer directly.

| Harness | Module / extra | PRD | Status |
| --- | --- | --- | --- |
| Harness protocol + registry + capabilities | `ai/harness/__init__.py` | §8.1, §8.2 | Done |
| Native (default) | `ai/harness/native.py` | §8.1 | Done (single generate-and-apply; tool-loop upgrade is Phase 3) |
| Copilot SDK | `ai_packs/copilot.py` (`quill[ai-copilot]`) | §18.5 | Done (transport scaffolded; validate with SDK installed) |
| Claude Agent SDK | `ai_packs/claude.py` (`quill[ai-claude]`) | §18.5 | **Done — validated live** against the real SDK (`claude_agent_sdk.query`, AssistantMessage/TextBlock, `allowed_tools=[]` text-only). |
| OpenAI Agents SDK | `ai_packs/openai_agents.py` (`quill[ai-openai]`) | §18.5 | **Done — validated live** against the real SDK (`agents.Agent` + `Runner.run_sync` -> `final_output`). |
**Scope note.** QUILL ships exactly three SDK packs — OpenAI Agents, Claude Agent,
and GitHub Copilot — which cover the field. The Microsoft Agent Framework,
LangGraph, and OpenHands packs were intentionally removed to keep the surface small
and well-tested.

**Harness pack status note.** Every pack's identity, capabilities, lazy
availability detection, graceful-degradation, registration, and gateway bridge are
built and unit-tested (the bridge via an injectable transport, since the SDKs are
not installed in CI). Each pack's `_make_invoke` imports its SDK lazily and targets
the SDK's documented entrypoint; the live transport must be **validated against
each SDK once its extra is installed** (Phase 5 acceptance) and richer native
tool-calling against the gateway is a follow-up. The **Copilot pack is cross-checked
against the GA GitHub Copilot SDK** (PyPI `github-copilot-sdk`, import `copilot`,
async `CopilotClient().create_session(...).send(...)`); its bridge denies the SDK's
own file/shell tools via `on_permission_request` so QUILL applies edits through its
gateway — routing that permission hook into the QUILL `PermissionBroker` is the deep
follow-up. Per-pack network-egress-audit entries are added when a pack's transport is
activated against its SDK.

### Phase 6 — Enterprise + durable workflows

Admin policy enforcement (`allowedProviders`/`blockedProviders`/`allowUserApiKeys`):
**core done** — `ai/admin_policy.py` (`AdminPolicy`, `is_provider_allowed`,
`filter_providers`, `from_dict`); wiring it into the provider catalog/Hub is the
remaining piece. Durable, resumable agent workflows (release prep, accessibility
audit, PRD creation) persisted via atomic storage: not started. PRD §15.

### Phase 7 — Developer agents + marketplace

Agent Builder; Quillin-distributed agent/tool/harness packs with signature/trust and
lint gates. PRD §16, §18.7.

### Cross-cutting gates (every phase)

`ruff`; scoped `mypy quill/core/ai` (core is strict-typed); `dialog_inventory` +
`dialog_button_contract` for new dialogs; `network_egress_audit` entries for every
new outbound call (each harness pack); GATE-11 budget (split modules, never balloon
`assistant_ai.py`/`main_frame.py`); `quillin_lint` for agent/harness packs; Safe Mode
must disable every harness. PRD §17, §20.

---

## 2. Documentation (deferred to end of 2.0 work)

User guide, release notes, and PRD updates are written **after** the platform lands,
sourced from the `2.0-dev` commit history (which is kept detailed for this purpose).
Do not batch-update docs mid-build; the commit messages are the interim record.

---

## 3. Parked: candidates for a 1.xx release (NOT 2.0)

These were historically tagged "defer to 2.0" in `roadmap.md` §5, but 2.0 is the
agentic AI theme. They are candidates to slot into a **1.xx** release and are kept
here only so the intent is not lost. None gates 2.0.

- **Dictation later phases** — global Windows key hook, idle-silence detection,
  dictation intelligence (spoken punctuation/commands).
- **BITS Whisperer consolidation backlog** (#515, #566–#577) — provider-matrix tiers
  and guided onboarding.
- **Accessibility tooling from GLOW** (#528–#534, #566) — Document Audit (ACB
  Large-Print, MS Accessibility Checker, WCAG 2.2 AA) as authoring-time checks; source
  `s:\code\glow`.
- **ElevenLabs beyond export TTS** — live streaming Read Aloud, voice
  management/cloning/design, Tier-3 surfaces. Spec
  [`eleven-labs.md`](eleven-labs.md).
- **Native Google Docs support** — Drive API + OAuth + accessible doc model. Spec
  [`QUILL-Native-Google-Docs-Support-PRD.md`](QUILL-Native-Google-Docs-Support-PRD.md).
- **Direct publishing** (#140) — WordPress and other platforms, likely a Quillin
  integration; early design in `docs/design/publishing/`.
- **Remaining ChapterForge surfaces** — Auphonic, RSS feeds, SFTP publishing,
  MusicBrainz/Open Library metadata.
- **Platform / packaging singletons** (#680) — Windows 11 `IExplorerCommand` pass
  (#525), PyInstaller hardening (#599). Nuitka out of scope.
- **Table Studio** — spec
  [`quill-native-accessible-table-studio-plan.md`](quill-native-accessible-table-studio-plan.md).
- **Verbosity 2.0 polish backlog** — long tail (#405–#504); reference in
  `roadmap.md` §5.

---

## 4. Working agreement

- **One planning file for 2.0:** this document plus the agentic AI PRD. New 2.0 design
  goes into the PRD or a referenced spec, not inlined here.
- **Keep the Phase tables current** as commits land; that is the build tracker.
- **Commit frequently**, with detailed messages — they are the source for the
  end-of-cycle docs.
- **Stay current with main:** merge `main` into `2.0-dev` regularly.
- **Graduation:** when a 1.xx candidate from §3 is scheduled, move it into
  `roadmap.md` for that release and delete its row here.

---

## 5. Phase 0 — the dormant foundation: what's done, and what 1.xx gains

"Phase 0" is the name we give the **already-built, dormant Tier A foundation** for
the 2.0 agentic platform (the §1 Phase 1 Tier A rows, plus the harness layer and
SDK packs). It is finished, tested, and sitting on `2.0-dev`. This section records
exactly what it is, whether 1.xx gains anything by adopting it, and the evidence
that doing so is safe — so the decision to port it into a 1.xx release can be made
from facts, not hope.

### 5.1 What is done (the Phase 0 surface)

All wx-free, strict-typed `quill/core/ai/*` (plus `quill/ai_packs/*`), additive:

- `events.py` — normalized agent-event vocabulary.
- `permissions.py` — Permission Broker (4 profiles, monotone risk floor, hard
  `SAFE_TOOL_IDS` floor).
- `activity_log.py` — bounded, redacted, atomic audit log.
- `tool_gateway.py` — Safe Editor Tool Gateway (typed host protocol, permission
  checks, diff-preview routing, undo checkpoints, audit).
- `context_builder.py` — scoped context + secret-masking "what will be sent"
  preview.
- `harness/` + `harness/native.py` — Harness protocol/registry/capabilities,
  Native harness, and `responder_from_backend` (runs Native on the existing
  provider stack).
- `ai_packs/` — three optional SDK harness packs (OpenAI Agents, Claude Agent,
  GitHub Copilot), lazily imported, graceful when uninstalled.
- `agent_catalog.py` + `schemas/agent.json` + `ai/agents/*.json` — declarative
  Agent Catalog + the 11-agent launch set.
- `event_bridge.py` — verbosity-aware mapping from events to balanced
  announcements.

Test coverage: ~95 new tests under `tests/unit/core/ai/` (full `tests/unit/core/ai`
= 448 passing).

### 5.2 Does 1.xx gain anything from it?

**Be precise: Phase 0 adopted on its own delivers no user-facing change and no new
runtime behavior.** Every module is dormant — nothing in the shipping app calls it
(proven in §5.3). So a user on a 1.xx build that includes Phase 0 would see and
feel exactly what they see today.

What 1.xx *does* gain is **latent and strategic, not functional**:

1. **A proven substrate, shipped early.** The permission model, audit log, gateway,
   diff/undo routing, and event grammar exist as tested code in the release stream,
   de-risking the later visible 2.0 work and any 1.xx hardening built on top.
2. **The prerequisite for the real stability win.** The genuine, user-invisible
   *stability* improvement (one provider truth; routing today's Ask Quill / Writing
   Assistant edits through one audited gateway + one diff/undo path) is the **Tier B**
   work in §1. Tier B cannot land without Phase 0 underneath it. Porting Phase 0 to
   1.xx is what makes a subsequent quiet 1.xx hardening release *possible*.
3. **No new dependencies for default installs.** The SDK packs are opt-in extras; a
   normal install pulls none of them.

So the honest answer to "does it gain anything?": **by itself, nothing the user
notices — it is an enabling foundation.** The payoff is realized only when a
follow-up Tier B change switches part of it on; that change is separate,
behavior-changing, and must be proven on its own.

### 5.3 Can we prove it is safe to bring into 1.xx? Yes — evidence

The safety claim is "adopting Phase 0 cannot change how 1.xx behaves." Four
independent checks support it:

1. **Additive only — zero deletions.** The diff from the 2.0 fork point
   (`f1e2f87`) is **30 files changed, 2456 insertions, 0 deletions**. Every
   `quill/` change is a brand-new file except `pyproject.toml`. No existing line of
   shipping code was modified or removed.
2. **The one touched existing file is additive and inert at runtime.**
   `pyproject.toml` gains three *optional-dependency* extras (`ai-openai`,
   `ai-claude`, `ai-copilot`) and two wheel `force-include` lines for the new data
   files (the §0a note predates trimming the pack set). Optional extras are not in
   the default `[ui]`/`[dev]` install, so default install and runtime are unchanged;
   the force-includes only package the new, otherwise-unused JSON.
3. **Unreachable from the shipping app.** A grep for `import` statements of every
   new module, across all of `quill/`, excluding the files created on this branch,
   returns **no pre-existing importer**. Nothing the running app loads imports the
   Permission Broker, gateway, activity log, events, context builder, event bridge,
   harness layer, agent catalog, or `ai_packs`. Code that nothing calls cannot
   change behavior.
4. **Verified green, all gates.** Full suite passes on both branches
   (`2.0-dev` 5647 passed; `main` 5580 passed; 0 failures). `ruff check`,
   `ruff format --check`, and scoped `mypy quill/core/ai` are clean; the
   banned-patterns, GATE-11 module-size, and network-egress gates pass. No new
   outbound network call site was added — the SDK packs call their SDKs lazily and
   only inside a running session, which cannot occur without an installed extra and
   an explicit user action — so the egress audit is unchanged and Safe Mode's
   guarantees are untouched.

**Conclusion:** porting Phase 0 into a 1.xx release is safe because it is provably
inert: additive new files, no shipping importer, optional dependencies, green CI.
It buys 1.xx a tested foundation with no behavior risk — and nothing more until a
later, separately-reviewed change wires it in.

### 5.4 Guidance — how to land Phase 0 in 1.xx

1. **Port it as one additive PR.** Cherry-pick or port the Phase 0 files onto a
   1.xx branch as a single "new files only" change. Because it is inert, review is
   about code quality and tests, not behavior regression; CI should be green with no
   diff in any existing behavior test.
2. **Do not wire anything in.** Add no menu item, command, dialog, or call site in
   the 1.xx PR. Enabling any of it is Tier B/C and belongs in its own change. Keeping
   the PR inert is precisely what makes it safe.
3. **Sequence the real win separately.** Schedule the Tier B hardening (one provider
   truth, then gateway-routed edits) as a follow-up 1.xx PR, gated by the existing AI
   tests + a reversible key migration. That PR is where stability is actually
   delivered and where the careful regression review must focus.
4. **Leave the SDK packs as optional, unadvertised extras.** Their transports are
   not yet validated against live SDKs (they require the extras installed); keeping
   them opt-in and unlisted in 1.xx means that open item cannot affect 1.xx users.
5. **Keep the egress audit honest.** When a future change first makes a pack's
   transport reach the network, add its call site to `network_egress_audit.py` in the
   *same* change — not before.
