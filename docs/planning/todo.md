# QUILL 2.0 — Master TODO (living checklist)

This is the **living, end-to-end checklist** to take QUILL 2.0 (the Agentic AI
Platform) from where it is now to a shippable, packaged, distributed product that a
screen-reader user can drive with efficiency and delight. It complements the
higher-level [`roadmap-2.0.md`](roadmap-2.0.md) (the plan of record) and the
authoritative spec [`quill_end_to_end_agentic_ai_prd.md`](quill_end_to_end_agentic_ai_prd.md).

**Keep this updated:** check items off (`[x]`) as they land on `2.0-dev`; use `[~]`
for in-progress with a short note; leave `[ ]` for not-started. Each phase ends with
an **Acceptance** line — the phase is not "done" until it is green and accessible.

**Status legend:** `[x]` done · `[~]` in progress / partial · `[ ]` not started.

**Last updated:** 2026-06-26.

---

## Standing rule — always green, always accessible

Every change, every phase:

- [ ] `ruff check` + `ruff format --check` clean.
- [ ] Scoped `mypy quill/core quill/io` clean (core/ai is strict-typed).
- [ ] Gates pass: banned-patterns, GATE-11 module-size, GATE-16 message-box,
  `dialog_inventory` + `dialog_button_contract`, `network_egress_audit`,
  `quillin_lint` (for agent/harness packs).
- [ ] `pytest tests/unit tests/stability` green.
- [ ] Safe Mode disables every AI surface; QUILL still launches/edits/saves with AI off.
- [ ] Every new UI surface is keyboard-reachable with predictable focus and balanced
  announcements (no token spam); verified with a screen reader.

---

## Phase 0 — Agentic core foundation  ✅ (built + tested; back-portable Tier A)

- [x] Event vocabulary — `quill/core/ai/events.py`.
- [x] Permission Broker (4 profiles, risk floor, `SAFE_TOOL_IDS` floor) — `ai/permissions.py`.
- [x] Activity Log (bounded, atomic, redacted) — `ai/activity_log.py`.
- [x] Safe Editor Tool Gateway — `ai/tool_gateway.py`.
- [x] Context Builder + privacy preview — `ai/context_builder.py`.
- [x] Streaming Event Bridge (announcement mapping) — `ai/event_bridge.py`.
- [x] Harness layer (protocol/registry/capabilities) + Native harness + `responder_from_backend` — `ai/harness/`.
- [x] Declarative Agent Catalog + schema + 11-agent launch set — `ai/agent_catalog.py`, `schemas/agent.json`, `ai/agents/*.json`.
- [x] Native multi-step tool-calling loop — `ai/tool_loop.py`.
- [x] Concierge + Selection Action Ring **models** — `ai/concierge.py`.
- [x] Enterprise admin policy — `ai/admin_policy.py`.
- [x] Three SDK harness packs — OpenAI Agents, Claude Agent, GitHub Copilot — `ai_packs/`.
  - [x] OpenAI Agents — validated live.
  - [x] Claude Agent — validated live.
  - [x] GitHub Copilot — cross-checked vs GA SDK (live run pending a Copilot auth).
- [x] Opt-in editor wiring (`QUILL_AI_AGENT_GATEWAY`) — `ui/agent_editor_host.py`; validated live vs Claude + OpenAI.
- **Acceptance:** ✅ ~95 core tests + adapter tests green; all gates pass.

---

## Phase 1 — Consolidation (Tier B; invisible, ships in 1.xx)

- [x] **One provider truth (§7).** `ai_chat.PROVIDERS` now uses the **canonical**
  per-provider credential targets (`assistant_ai.provider_credential_target`), so the
  lightweight chat client and the main AI stack read/write the **same key** per
  provider — no caller rewrites needed (all callers resolve `credential_name`).
  - [x] Reversible, non-destructive, idempotent **key migration**
    (`assistant_ai.consolidate_provider_keys`) copies keys from the legacy
    `quill-<provider>-api-key` slots and the global active-key slot into the canonical
    slots; run guarded at startup in `__main__.main`.
  - [x] All keyed surfaces read one store; changing the key in one place changes it
    for Ask Quill, the chat dialogs, and `SimpleChatBackend`.
- [~] **Gateway as the default edit path (§12).** The gateway + `MainFrameEditorHost`
  exist and are the canonical apply path (validated live). Rewiring the *existing*
  Ask Quill / Writing Assistant dialogs to it and removing the
  `QUILL_AI_AGENT_GATEWAY` gate is **UI work** (Phase 6) needing GUI validation.
- [x] Wire **admin policy** into the provider catalog — `providers.allowed_providers(policy)`
  + `ALL_PROVIDERS`. Hub consumption is UI (Phase 6).
- **Acceptance:** keyed surfaces share one provider key store; migration reversible +
  idempotent + never breaks startup; admin policy filters the catalog. Tests:
  `tests/unit/core/ai/test_provider_truth.py` (8). Remaining is the UI rewiring.

---

## Phase 2 — All chat experiences green + unified

- [ ] Inventory every AI chat/inline surface: **Ask Quill**, **Writing Assistant**,
  **Ask AI**, **Prompt Studio**, **Agent Center**, inline grammar/spell/thesaurus,
  Run Python.
- [ ] Route them all through the consolidated provider + gateway (Phase 1).
- [ ] **Ask Quill chat** parity: standard text entry, list-navigable messages,
  copy/stop/retry/insert/replace, "response complete" announcement, streaming via the
  event bridge.
- [ ] Error taxonomy surfaced cleanly (auth/quota/network/context-window) with a
  "what to try next" hint; never a raw traceback.
- [ ] Cancel everywhere (Escape) cancels in-flight model calls and tool loops.
- [ ] Session resume/branch from chat (uses `sessions.py`).
- **Acceptance:** every chat surface works end-to-end against OpenAI, Claude, and a
  local provider, keyboard-only, with green a11y tests.

---

## Phase 3 — Full-document context (the document in focus, handled completely)

- [ ] Wire `ContextBuilder` into every agent run (selection / current section /
  document summary / **full document**).
- [ ] **Large-document handling:** chunking + `compaction.py` summarization so the
  whole document can be reasoned over within a model's context window; announce when
  a summary/compaction is used.
- [ ] **Context preview** ("what will be sent") dialog before any send — words, file,
  headings, whether the full doc/workspace is included; Continue / Show Text / Cancel.
- [ ] **Secret masking + the document-transform round-trip decision.** Resolve how
  redaction interacts with whole-document transforms (redaction breaks round-trip);
  pick policy (warn-and-send vs mask-and-warn) per scope and implement.
- [ ] Outline-aware, **section-scoped** operation for Markdown Publisher /
  Accessibility Editor (per-section previews instead of whole-file rewrites).
- [ ] Token/cost estimate + warning before large sends.
- **Acceptance:** a 50-page document can be summarized, audited, and section-edited
  with a clear preview and no context-window failures; perf within budget.

---

## Phase 4 — Deep agentic actions (agents act IN the document)

The "ask the SDK to take actions in the document, automatically or with prompting."

- [ ] **Register QUILL editor tools as each SDK's native tools** so the agent's own
  planner can read/select/replace/patch/run-command *through the gateway* — not the
  SDK's filesystem.
  - [ ] **Copilot SDK:** route `on_permission_request` → QUILL `PermissionBroker`;
    expose QUILL custom tools; the agent edits the in-focus document via the gateway.
  - [ ] **Claude Agent SDK:** replace `allowed_tools=[]` text-only with QUILL custom
    tools + a permission callback bridged to the broker.
  - [ ] **OpenAI Agents SDK:** register function tools that call the gateway; use
    guardrails/handoffs as available.
- [ ] **Provider function-calling planner** for the native `tool_loop` so the loop can
  drive a cloud model directly (loop is built; needs a real planner).
- [ ] **Two interaction modes**, driven by the safety profile:
  - [ ] **Auto-apply** (Power User): low-risk tool calls apply with one-undo + an
    announcement, no prompt.
  - [ ] **Prompt-to-approve** (Balanced/Careful): each mutating tool call shows the
    diff/permission prompt before applying.
- [ ] Multi-step flows: read document → propose plan → apply as accept/reject hunks →
  summarize what changed, all announced in plain language.
- **Acceptance:** "Copilot, fix the headings in this document" runs, the agent edits
  through QUILL's reviewed gateway (auto or prompted per profile), and every change is
  undoable; same flow proven on Claude and OpenAI.

---

## Phase 5 — Rich agent examples, tested across OpenAI / Claude / Copilot

Build a **library of real, useful agents** and a **cross-SDK test matrix** proving
each runs on all three engines with consistent, reviewed results.

- [ ] Expand the catalog with rich, opinionated agents (each a validated
  `ai/agents/*.json` + a system prompt that produces consistent, reviewable output):
  - [ ] **Accessibility Editor** — full WCAG-ish structural fixes, section-scoped.
  - [ ] **Markdown Publisher** — heading/list/table/link normalization.
  - [ ] **Plain-Language Rewriter** — reading-level target.
  - [ ] **Citation/Link Fixer** — fix link text + dead-link flags.
  - [ ] **Meeting-Notes → Action Items**.
  - [ ] **Code Doctor** — explain/document/tidy (no behavior change).
  - [ ] **GitHub Maintainer** — issue/changelog/PR-description drafts.
  - [ ] **Release Notes Builder**, **PRD Architect**, **Summarizer**, **Researcher**.
- [ ] **Cross-SDK acceptance matrix** (agent × {OpenAI, Claude, Copilot, Native}):
  each cell has a scripted scenario with an input document, the run, and an assertion
  on the applied result / announcement (mock transport in CI; live runs gated behind
  installed extras + keys, recorded in a manual validation log).
- [ ] **Golden transcripts / fixtures** for deterministic regression of the gateway
  bridge per SDK.
- [ ] Document each agent in the user guide with a worked example.
- **Acceptance:** every catalog agent runs on all three SDK packs + Native through the
  gateway, with a recorded live validation per (agent, SDK) of the headline set.

---

## Phase 6 — The AI Hub command center + magical surfaces (the visible 2.0)

This is the front door; nothing is user-visible without it. Needs in-GUI +
screen-reader validation.

- [ ] Promote `AIHubDialog` to a multi-tab hub (split per-tab module for GATE-11):
  - [ ] **Home** — availability sentence, active provider/harness/agent, Concierge.
  - [ ] **Agents** — catalog list, run, recommended-for-this-file badge, risk +
    permission summary.
  - [ ] **Chat** — embeds the unified Ask Quill flow.
  - [ ] **Sessions** — browse/resume branchable sessions.
  - [ ] **Activity** — redacted audit log + "Review/Undo last AI change".
  - [ ] **Providers** — on the single consolidated store.
  - [ ] **Harnesses** — installed/installable packs (OpenAI/Claude/Copilot), enable/configure.
  - [ ] **Permissions** — safety-profile chooser + per-category defaults.
  - [ ] **Audio** + **Advanced** (existing) — consent, network audit, Safe Mode, reset.
- [ ] **Selection Action Ring** wx widget (model done: `concierge.ring_actions`) — a
  hotkey opens a list of recommended one-key transforms for the selection.
- [ ] **Concierge** on Home + status bar ("what can I do here?").
- [ ] **Streaming announcements** wired from the event bridge to the announcer.
- [ ] **Ambient availability badge** (AI ready / needs key / off).
- [ ] Every Hub action reachable from menu + command palette; Escape cancels; Ctrl+Z
  undoes; Alt+Shift+D reviews last change; focus returns to the editor.
- **Acceptance:** a user configures, picks an agent, runs it, reviews, undoes, and
  inspects activity entirely from the Hub, keyboard-only, with a screen reader.

---

## Phase 7 — Local + BYOK polish

- [ ] Harden Ollama/local + OpenAI-compatible/LiteLLM base-URL flows on the
  consolidated store: test-connection, model selector, cost/context warnings.
- [ ] Local-only users get the full agent catalog with no cloud account.
- **Acceptance:** local-only and org-endpoint users run the headline agents with no
  cloud key.

---

## Phase 8 — Enterprise + durable workflows + extensibility

- [ ] Admin policy fully enforced in provider selection + Hub (allowed/blocked,
  allowUserApiKeys, policy notice URL).
- [ ] Durable, resumable agent workflows (release prep, accessibility audit, PRD
  creation) persisted via atomic storage; pause/resume/human-in-the-loop.
- [ ] **Agent Builder** — define a new agent in-app (validated against `agent.json`).
- [ ] **Quillin-contributed agents/tools/harnesses** — loaded via the catalog's extra
  dirs, manifest-validated, `quillin_lint --strict`, with trust/signature gating.
- **Acceptance:** an org can constrain providers; a user can build and run their own
  agent; a Quillin can contribute one safely.

---

## Phase 9 — Prove it: efficiency, accessibility, and greatness

The user-experience proof that this is usable with delight, not just functional.

- [ ] **Screen-reader walkthroughs** (NVDA + JAWS): scripted end-to-end journeys for
  each headline flow; capture and fix any announcement gaps.
- [ ] **Latency budgets**: first-announcement < ~1s; model work off the UI thread;
  cancel always responsive; no freezes during sessions.
- [ ] **Efficiency**: keyboard-only task completion for the top flows in ≤ N
  keystrokes; the Action Ring and palette make common transforms 1–2 keys.
- [ ] **Error recovery**: every failure path (auth, quota, network, context window,
  denied permission, malformed patch) degrades cleanly with a next-step hint.
- [ ] **Trust**: every applied change is reviewable + one-undo; activity log shows
  what happened; nothing leaves the machine without an explicit, previewed send.
- [ ] **a11y CI**: keyboard/focus tests for the Hub, chat, diff review, Action Ring;
  axe-equivalent checks where applicable.
- **Acceptance:** a blind user can discover, run, review, and undo agentic edits
  across all three SDKs efficiently, end to end, with no sighted assistance.

---

## Phase 10 — Packaging, distribution, deployment, assets

- [ ] **Optional extras** finalized in `pyproject.toml`: `ai-openai`, `ai-claude`,
  `ai-copilot` (+ existing `ui`, `dev`, etc.); document install matrix.
- [ ] **Wheel/data**: ensure `force-include` covers `schemas/agent.json`,
  `ai/agents/*.json`, and any new assets; build a clean wheel.
- [ ] **Windows installer** (Inno Setup, `ISCC.exe`): bundle the app; offer the AI
  extras as optional components; verify no console window; portable build parity.
- [ ] **macOS build** (py2app) parity for the agentic surfaces.
- [ ] **Version mechanics**: bump to 2.0 via `build/version.toml` → `quill.iss` +
  CHANGELOG; GATE-VC; do **not** flip the public update feed until release.
- [ ] **Code signing** (Windows/macOS) for the installer/app.
- [ ] **Update feed** entry prepared but held until 2.0 ships (per the release-hold
  discipline).
- [ ] **Assets**: any new earcons/sounds for agent start/propose/apply/deny in the
  bundled Ink pack; icons/menu art; ensure assets are packaged.
- [ ] **Telemetry/consent** review for any optional SDK calls; network-egress audit
  entries added when each pack's transport goes live.
- [ ] **Fresh-install + upgrade test kit** run for 2.0 (mirrors the 0.8.0 kit).
- **Acceptance:** a clean installer produces a working 2.0 with AI off by default, the
  three extras installable, signed, with a fresh-install regression pass.

---

## Phase 11 — Documentation finalization

- [ ] **Release notes** — `release2.0.0-dev.md` → finalized `release2.0.0.md` at tag.
- [ ] **CHANGELOG** — 2.0 section finalized.
- [ ] **User guide** — add the agentic section (held until the feature ships out of
  the opt-in): AI Hub, choosing a provider/harness, running agents, the Action Ring,
  the Concierge, reviewing/undoing, permissions/profiles, per-agent worked examples.
- [ ] **PRD** — reconcile `quill_end_to_end_agentic_ai_prd.md` with shipped state.
- [ ] **Regenerate** `.epub`/`.html` artifacts for the release notes + user guide via
  the docs pipeline.
- [ ] Retire/merge superseded planning files once shipped (per the doc-then-remove
  discipline).
- **Acceptance:** docs describe shipped behavior accurately; generated artifacts current.

---

## Cross-cutting backlog (do alongside, not a phase)

- [ ] Per-pack `network_egress_audit.py` entries when transports activate.
- [ ] Deep Copilot `on_permission_request` → `PermissionBroker` mapping (Phase 4 detail).
- [ ] Rotate any keys exposed during validation; never persist chat-pasted keys.
- [ ] Keep `roadmap-2.0.md` Phase tables and this TODO in sync as work lands.

---

## Definition of done for 2.0

2.0 ships when: the AI Hub is the working front door; every chat + inline AI surface
runs through one provider/gateway/diff/undo/log; a user can run rich agents on the
in-focus document (full-document aware) across OpenAI, Claude, and Copilot, with
auto or prompted actions, all reviewed and undoable; a screen-reader user completes
the headline journeys efficiently; and the signed installer delivers it with AI off
by default — with the full suite and all gates green.
