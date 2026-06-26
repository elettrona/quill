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

**Created:** 2026-06-25. **Last updated:** 2026-06-25.

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

## 1. The 2.0 build: agentic AI platform

Phases below mirror PRD §18 (priority order, not calendar). The status column is the
live tracker; update it as commits land on `2.0-dev`.

### Phase 1 — Consolidate and formalize (foundation)

| Item | PRD | Status |
| --- | --- | --- |
| Event vocabulary (`ai/events.py`) | §14 | Done |
| Permission Broker (`ai/permissions.py`) | §10 | Done |
| Activity Log (`ai/activity_log.py`) | §9, §14 | Done |
| Safe Editor Tool Gateway (`ai/tool_gateway.py`) | §9 | In progress |
| Context Builder (`ai/context_builder.py`) | §11 | Not started |
| One provider truth (converge `ai_chat.PROVIDERS` into `assistant_ai`) | §7 | Not started |
| Route existing AI edits through gateway + `diff_review` | §12 | Not started |

### Phase 2 — AI Hub as command center

| Item | PRD | Status |
| --- | --- | --- |
| Promote `AIHubDialog` to Home/Agents/Chat/Sessions/Activity/Providers/Harnesses/Audio/Permissions/Advanced (per-tab modules for GATE-11) | §5 | Not started |
| Streaming Event Bridge -> balanced announcements | §6, §14 | Not started |
| Concierge "What can I do here?" on Home + status bar | §6 | Not started |

### Phase 3 — Declarative Agent Catalog + native tool-calling loop

| Item | PRD | Status |
| --- | --- | --- |
| `core/schemas/agent.json` + catalog loader | §13 | Not started |
| Promote `accessibility_agent` + the four `AgentProfile`s; add Markdown Publisher, Code Doctor, GitHub Maintainer, PRD Architect, Release Notes Builder, Concierge | §13 | Not started |
| Upgrade native harness to a real broker-gated, event-streamed tool-calling loop | §8.1 | Not started |
| Selection Action Ring + hunk-preview clean-up + accessibility review on catalog agents | §6 | Not started |

### Phase 4 — Local + BYOK polish

| Item | PRD | Status |
| --- | --- | --- |
| Harden Ollama/local + OpenAI-compatible/LiteLLM base-URL flows on the consolidated store; test-connection, model selector, cost/context warnings | §18.4 | Not started |

### Phase 5 — Harness layer + all harness packs (the multi-harness promise)

The user's directive: **all harnesses are built for 2.0.** Each SDK pack is an
optional extra, lazily imported, never required; an uninstalled pack reports
`(False, "Install the X pack")` and QUILL keeps working. Every pack bridges to the
**same** gateway + broker + diff/undo and emits normalized `AgentEvent`s; none edits
the buffer directly.

| Harness | Module / extra | PRD | Status |
| --- | --- | --- | --- |
| Harness protocol + registry + capabilities | `ai/harness/` | §8.1, §8.2 | Not started |
| Native (default) | `ai/harness/native.py` | §8.1 | Not started |
| Copilot SDK | `ai_packs/copilot/` (`quill[ai-copilot]`) | §18.5 | Not started |
| Claude Agent SDK | `ai_packs/claude/` (`quill[ai-claude]`) | §18.5 | Not started |
| OpenAI Agents SDK | `ai_packs/openai_agents/` (`quill[ai-openai]`) | §18.5 | Not started |
| Microsoft Agent Framework | `ai_packs/microsoft/` (`quill[ai-microsoft]`) | §18.6 | Not started |
| LangGraph (durable, human-in-the-loop) | `ai_packs/langgraph/` (`quill[ai-langgraph]`) | §18.6 | Not started |
| OpenHands (sandboxed, flag-gated) | `ai_packs/openhands/` (`quill[ai-openhands]`) | §18.7 | Not started |

### Phase 6 — Enterprise + durable workflows

Admin policy enforcement (`allowedProviders`/`blockedProviders`/`allowUserApiKeys`),
LangGraph durable pause/resume workflows (release prep, accessibility audit, PRD
creation) persisted via atomic storage. PRD §15, §18.6.

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
