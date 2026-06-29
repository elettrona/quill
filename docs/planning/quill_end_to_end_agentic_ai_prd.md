# QUILL Agentic AI Platform PRD

**Product:** QUILL for All  
**Feature Area:** Unified, optional, provider-neutral agentic AI platform built on QUILL's existing AI stack  
**Document Type:** End-to-end Product Requirements Document (implementation-grounded)  
**Version:** 2.0 Draft (rebased on shipping code, 0.7.0-beta2)  
**Date:** June 21, 2026  
**Primary Goal:** Elevate QUILL's already-substantial AI stack into one accessible, provider-neutral, multi-harness agentic platform whose single front door is the **AI Hub** — without breaking the optional, screen-reader-first, "QUILL owns the editor" guarantees that already ship.  

---

## 0. How to read this document

This is **version 2.0**. Version 1.0 was written as if QUILL had no AI. That is not true. QUILL ships a deep AI stack today: a provider-neutral backend, eight providers, streaming, branchable sessions, context compaction, an accessible diff-review model, a command-as-tools bridge, OAuth device login, local model management, and the AI Hub dialog itself.

Therefore this PRD is a **delta plan**, not a greenfield plan. Section 2 is the authoritative inventory of what exists in code. Every later section says explicitly whether a capability **exists**, must be **extended**, or must be **built new**, and points at the real module. Priorities flow from that truth: the first job is **consolidation**, not invention.

The source of truth is the code in `quill/`, verified June 21, 2026 against branch `feature/beta-2`.

---

## 0a. Implementation status (2026-06-26, branch `2.0-dev`)

The **non-UI innerworkings of Phases 1–5 are built and tested**; the remaining work is
the AI Hub UI (Phase 6 here / §5) plus a few live-SDK and product items. Built modules:

- **Foundation** — `ai/events.py`, `ai/permissions.py` (broker, 4 profiles, risk floor,
  `SAFE_TOOL_IDS` floor), `ai/activity_log.py`, `ai/tool_gateway.py`,
  `ai/context_builder.py`, `ai/event_bridge.py`.
- **Harness layer + packs** — `ai/harness/` (protocol/registry/capabilities, Native),
  and three optional SDK packs in `ai_packs/` (OpenAI Agents, Claude Agent, GitHub
  Copilot — Microsoft/LangGraph/OpenHands intentionally dropped). OpenAI + Claude
  validated live; Copilot cross-checked vs the GA SDK.
- **Agents + loop** — `ai/agent_catalog.py` + `schemas/agent.json` + a **15-agent**
  `ai/agents/` set; `ai/tool_loop.py`; `ai/tool_planner.py` (provider-neutral JSON
  tool-calling); `ai/agent_tools.py` (shared tool surface for the loop, planner, and
  SDK packs).
- **Provider truth (§7)** — `ai_chat` reads the canonical per-provider key targets;
  `assistant_ai.consolidate_provider_keys` reversible migration at startup;
  `providers.allowed_providers(policy)` (admin policy, §15).
- **Chat + document (§2.2, §11)** — `ai/chat_session.py` (unified, auto-compacting chat
  engine) and `ai/doc_context.py` (chunk / section / structured summary for whole-doc).
- **Editor wiring** — `ui/agent_editor_host.py` routes agents through the gateway,
  validated live (opt-in behind `QUILL_AI_AGENT_GATEWAY`).
- **Cross-SDK proof** — `tests/unit/core/ai/test_agent_matrix.py`: 15 agents × 4
  engines = 60 cases through the gateway.

Remaining: the AI Hub command center + surfacing (Phase 6, UI); routing the existing
chat dialogs onto `ChatSession` + the gateway (UI); per-SDK native-tool registration
(`on_permission_request` → broker) needing the live SDKs; and the secret-masking
policy for whole-document transforms (a product decision). The live tracker is
[`todo.md`](todo.md); the plan of record is [`roadmap-2.0.md`](roadmap-2.0.md).

---

## 1. Executive Summary

QUILL should not add "one chatbot," and it should not rebuild what it already has. QUILL should **unify** its existing AI features behind one coherent, agentic, provider-neutral platform whose home is the **AI Hub**.

Today a user meets QUILL's AI through at least five different surfaces (AI Hub, Writing Assistant, Prompt Studio, Agent Center, Ask Quill chat) backed by **two different provider-config systems** (`assistant_ai`'s AI-13 connection file and `ai_chat.PROVIDERS`). The plumbing is strong; the seams show. The opportunity is to make the seams disappear: one provider truth, one tool gateway, one permission model, one diff/undo path, one activity log, one place that says "what can I do here?" — and then to layer optional, more powerful **harnesses** (Copilot SDK, Claude Agent SDK, OpenAI Agents SDK, Microsoft Agent Framework, LangGraph, OpenHands) on top of that unified core for users who want them.

The experience should feel magical:

- Select text and rewrite it, with the change applied as one undoable edit and announced cleanly.
- Open a messy Markdown file and have an agent plan, preview, and apply a clean-up as accept/reject hunks.
- Ask the Accessibility Editor to find screen-reader-hostile structure (this agent already exists in `accessibility_agent.py` — it should be promoted into the catalog).
- Ask a GitHub Maintainer agent to turn notes into an issue, changelog, or PR description.
- Ask the QUILL Concierge "what can I do here?" and get context-aware, keyboard-reachable actions.

The experience should stay safe and optional, exactly as it is today:

- QUILL owns the editor buffer, focus, undo checkpoints, announcements, and review dialogs.
- Agents act only through QUILL-approved tools (the command registry allowlist already enforces this).
- Safe Mode already disables the assistant and its network calls; that guarantee must hold for every new harness.
- Every provider and every harness is optional; QUILL launches, edits, and saves with AI fully off.

The winning architecture, restated for what exists:

> **Unified AI Core (consolidate what ships) + a formal Safe Editor Tool Gateway and Permission Broker (formalize today's loose callbacks) + an optional Harness layer (new) + a declarative Agent Catalog (extend) — all surfaced through the AI Hub.**

---

## 2. State of Truth: what QUILL ships today

This section is the spine of the plan. Everything below is in the codebase now.

### 2.1 AI Core (exists)

`quill/core/ai/` and `quill/core/assistant_ai.py` are a real, wx-free AI core.

| Concern | Module(s) | Notes |
| --- | --- | --- |
| Backend abstraction | `ai/backend.py` (`AIBackend`, `respond`, `respond_stream`, `ContextWindowExceeded`) | Clean ABC; streaming has a non-streaming fallback (AI-14). |
| Provider backend | `ai/provider_backend.py` (`ProviderChatBackend`, `SimpleChatBackend`) | Adapter over `assistant_ai.generate_assistant_response[_stream]`. |
| Provider catalog | `ai/providers.py` | off, ollama, openai, claude, gemini, openrouter, ollama_cloud, custom. Hosts, models, key requirements, display names, recommendations. |
| Connection + secrets | `assistant_ai.py` (1360 lines) | `AssistantConnectionSettings`, key load/save via Credential Manager + DPAPI (`protect_secret`/`unprotect_secret`), endpoint security checks, verified TLS, error taxonomy, chat body/headers/parse, streaming. |
| Availability | `ai/availability.py` (`AIAvailability`, `blocks_editor=False`) | One speakable sentence for "off / no key / unavailable." Never blocks typing. |
| Agentic decision | `ai/agent.py` (`AgentDecision`, `SAFE_TOOL_IDS`, `allowed_tools`) | Per-turn: answer / insert / replace / run-one-command, constrained to a curated safe command allowlist. |
| Agent session | `ai/agent_session.py` (`run_agent`, `AgentContext`, `AgentResult`, auth/cancel errors) | Single generate + optional refine pass. Blocking, cancellable via `stop_event`. |
| Sessions (memory) | `ai/sessions.py` | Branchable, resumable turn **tree**, persisted under `<data>/ai-sessions` with atomic writes. |
| Context compaction | `ai/compaction.py` | Summarize old turns to fit a token budget; tokenizer-free heuristic; never silently drops. |
| Diff review | `ai/diff_review.py` (`DiffReview`, `DiffHunk`, `build_diff_review`) | Accessible, deterministic, per-hunk accept/reject, one-undo re-apply, speakable summaries. |
| Tools bridge | `ai/tools.py` (`AITool`, `build_tools_from_registry`, `run_tool`) | Every registered command becomes a callable tool. |
| Agent profiles | `assistant_agents.py` (`AgentProfile`, `AgentPlan`, `build_agent_plan`) | rewrite / research / summarize / qa, template-driven. |
| Prompt templates | `assistant_prompts.py` (`CustomPrompt`, render/upsert/delete) | User-defined prompt library. |
| Local models | `ai/model_manager.py`, `ai/model_tiers.py`, `ai/llama_cpp_backend.py`, `ai/foundation_models.py` | RAM tiering, on-device backends. |
| Auth | `ai/device_login.py` | OAuth device-code login. |
| External engine | `ai/external_engine.py` | Allowlisted node/python/quill-engine executables. |
| Feature agents | `ai/grammar_check.py`, `spell_check.py`, `document_qa.py`, `translation.py`, `thesaurus.py`, `vision.py`, `transcription.py`, `diarization.py`, `tts.py`, `style.py`, `writing_instructions.py`, `plain_language.py`, `core/accessibility_agent.py` | A large catalog of working, single-purpose AI features. |
| Simple chat | `ai_chat.py` (`PROVIDERS`, `send_prompt`, `list_models`) | A **second** provider system: openrouter / openai / ollama_local / ollama_cloud. |

### 2.2 AI UI surfaces (exist, fragmented)

| Surface | Module | Role today |
| --- | --- | --- |
| AI Hub | `ui/ai_hub_dialog.py` (896 lines) | Tabbed **settings** center: Provider, On-Device, Audio, Advanced. Entry: `MainFrame.open_ai_hub`, menu `tools.ai_hub` ("AI &Hub..."). |
| Writing Assistant | `ui/assistant_panel.py` `WritingAssistantDialog` | Agent/prompt-driven assistant. Entry: `open_writing_assistant`. |
| Ask Quill chat | `ui/assistant_panel.py` `AskQuillChatDialog` | Chat with editor tool callbacks + command tools + diff review. |
| Prompt Studio | `PromptStudioDialog` | Custom prompt authoring. Entry: `open_prompt_studio`. |
| Agent Center | `AgentCenterDialog` | Agent picker. Entry: `open_agent_center`. |
| Run Python | `ui/assistant_tools.py` `RunPythonDialog` | Sandboxed transform of selection/document. |
| Setup wizard | `ui/setup_wizard.py`, `setup_wizard_pages.py` | Page 2 "Extras (AI/Braille/Automation)", page 3 "AI Provider". |

The **Ask Quill** dialog is the closest thing to a real agent host: it already receives `get_document, get_selection, insert_text, replace_selection, set_text, open_new_document, run_command, tool_catalog, announce, review_changes`. That callback bundle is, in effect, today's Safe Editor Tool Gateway — just unformalized.

### 2.3 Infrastructure invariants already enforced

- **Dialogs** go through `_show_modal_dialog` + `apply_modal_ids` (`ui/dialog_contract.py`); audited by `tools/dialog_inventory.py`.
- **Threading**: background work on `stability/task_manager.py` (`QuillTaskManager`); UI updates via `wx.CallAfter`; `wx_heartbeat`/`wx_dispatch` for liveness.
- **Persistence**: `core/storage.write_json_atomic` (+ schema validation); sessions/settings already use it.
- **Secrets**: `platform/windows/credential_manager.py` + DPAPI; `assistant_ai` never writes keys to plain config.
- **Safe Mode**: `QUILL_SAFE_MODE` forces `assistant_enabled` off and `open_writing_assistant` refuses to open (H-SAFE-1). Network calls are gated behind explicit user action.
- **Network egress**: `tools/network_egress_audit.py` already inventories `assistant_ai._post_chat[_stream]`, `_fetch_models_from_endpoint`, `tts`, `transcription`, `diarization`. Any new outbound call must be added here.
- **Redaction**: `stability/redaction.py` scrubs secrets from logs/crash bundles.
- **Module size budgets**: GATE-11 ratchet in `tools/module_size_budgets.json`. `assistant_ai.py` (1360) and `main_frame.py` (~19k) are already large; new code must not balloon them.
- **Extensions**: Quillins (`quill/quillins_bundled/`, `core/schemas/extension.json`, `tools/quillin_lint.py`) can register commands via `CommandRegistry.try_register`.

### 2.4 The gaps (what is genuinely missing)

These are the only things that do **not** exist and must be built:

1. **One provider truth.** `assistant_ai` (AI-13) and `ai_chat.PROVIDERS` are two catalogs. They must converge.
2. **A formal Safe Editor Tool Gateway** object (today: loose callbacks) with a typed tool surface and a **Permission Broker** (today: none — the only gate is the static `SAFE_TOOL_IDS` allowlist).
3. **A real tool-calling agent loop.** `run_agent` is generate+refine; `AgentDecision` is single-shot. Multi-step, tool-using sessions with per-tool permission prompts do not exist.
4. **A Context Builder** object with explicit scopes and a "show what will be sent" preview (pieces exist: compaction, redaction; the assembling component does not).
5. **A Streaming Event Bridge** with normalized event types feeding accessible announcements (today: ad-hoc token streaming in dialogs).
6. **A Harness layer** above `AIBackend` so optional SDK packs (Copilot, Claude, OpenAI Agents, MS Agent Framework, LangGraph, OpenHands) can drive the same gateway.
7. **A declarative Agent Catalog** (files validated by schema), generalizing `AgentProfile`/`accessibility_agent` into many catalog agents the AI Hub can list.
8. **The AI Hub as command center**, not just settings: agent launcher, activity log, session browser, permission center.
9. **An AI activity/audit log** (audit requirements are specified but not yet a first-class, reviewable surface).

---

## 3. Product Vision

> **QUILL is an accessible editor where the AI Hub is the single front door: you choose your engine and (optionally) your harness, pick an agent, and safely transform documents, code, notes, and publishing workflows with full review and undo — and you can turn all of it off.**

This is agentic editing, writing, accessibility review, publishing, and GitHub help — built on the stack QUILL already has, consolidated and made magical, never bolted on.

---

## 4. Product Principles (unchanged, now mapped to code)

1. **Optional by design.** Base QUILL runs with `provider = "off"`. Already true; keep it true for every harness pack.
2. **User choice.** No AI / local-only / BYOK / Copilot / Claude / OpenAI / Azure / org endpoint / future. The provider catalog already models most of this.
3. **QUILL owns the editor.** Agents never touch wx controls directly. They go through the gateway, which uses the same `_replace_document_text` / `_record_persistent_undo_state` path as `_apply_python_result`.
4. **Magical, not mysterious.** The user always sees what context is shared (Context Builder preview), what was proposed (diff review), what changed, and how to undo.
5. **Screen-reader-first.** Keyboard reachable, predictable focus, balanced announcements via `availability.py` wording and the Streaming Event Bridge; no token spam.
6. **Least privilege.** Permission Broker categories; `SAFE_TOOL_IDS` stays the floor for "run command."
7. **Reviewable changes.** `diff_review.py` is the canonical review path; every edit creates an undo checkpoint.
8. **Provider/harness neutrality.** QUILL agents are defined once (declarative), adapted to harnesses.

---

## 5. The AI Hub as Command Center (centerpiece)

The user's explicit ask: integrate everything into the AI Hub. Today `AIHubDialog` is a four-tab settings dialog. The plan promotes it to the **single hub** for configuration **and** action, while keeping each existing dialog reachable as a focused view.

### 5.1 Target AI Hub structure

```
AI Hub (Alt+A or AI > AI Hub)
  Home                  <- new: status, current provider/harness/agent, "What can I do here?"
  Agents                <- new: catalog list, run, per-agent permissions, recommended-for-this-file
  Chat                  <- embeds AskQuillChatDialog flow (unified)
  Sessions              <- new: browse/resume branchable sessions (sessions.py)
  Activity              <- new: AI activity/audit log (redacted)
  Providers             <- existing Provider + On-Device tabs, now backed by ONE provider truth
  Harnesses             <- new: installed/available harness packs, enable/configure
  Audio                 <- existing (Deepgram, transcription/diarization)
  Permissions           <- new: global safety profile + per-category defaults
  Advanced              <- existing (consent, network audit notes, safe mode, reset)
```

- **Home** shows `AIAvailability` in one sentence, the active provider+harness+agent, and Concierge "What can I do here?" computed from file type, selection state, outline, and git presence.
- **Agents** lists the declarative catalog (Section 13). Each row: run, recommended-for-current-file badge, risk level, permission summary. "Run" launches into Chat or a plan/preview flow.
- **Providers** is the existing Provider/On-Device UI, but reading/writing the **single** consolidated provider store (Section 7) — eliminating the `assistant_ai` vs `ai_chat` split.
- **Harnesses** lists Native (always present) plus any installed optional packs, with availability detection (lazy import; never crash if missing) mirroring `provider_backend.is_available` style.
- **Permissions** sets the global safety profile (Careful / Balanced / Power User / Locked Down) and per-category defaults consumed by the Permission Broker.
- **Activity** renders the audit log with secret redaction; supports "Review last AI change" and "Undo last AI change."

### 5.2 Constraints

- The Hub remains one `_show_modal_dialog` + `apply_modal_ids` surface; new tabs are added to the dialog-inventory fixture.
- Growth must respect GATE-11: split the hub into per-tab modules (`ai_hub_home.py`, `ai_hub_agents.py`, ...) rather than growing `ai_hub_dialog.py` past budget.
- The Hub never performs network or model work on the UI thread; all of it goes through `QuillTaskManager` with `wx.CallAfter` results.

---

## 6. Magical Editor Integration Points (bold, accessible)

These are the rich, in-editor experiences. Each names the real primitive it builds on. All are keyboard-first and announced through the existing status/Prism path.

1. **Selection Action Ring.** With a selection, a hotkey opens a small, list-based menu of recommended actions (Rewrite clearly, Shorten, Make warmer, Explain, Check accessibility) computed from file type. Built on `_selected_text()` and the Writing Companion agent. Apply-with-undo uses `_record_persistent_undo_state`; announce "Selection rewritten. Ctrl+Z to undo. Alt+Shift+D to review."
2. **Apply-with-undo inline edits.** Low-risk selection edits apply immediately as one undoable replacement (same path as `_apply_python_result`), never silently for document-wide edits.
3. **Accessible diff review everywhere.** Any medium/high-risk edit routes through `build_diff_review` -> the review dialog: per-hunk accept/reject, hunk navigation, speakable summary, one-undo apply. This is the universal "preview" surface.
4. **Concierge in the status bar / Home.** "What can I do here?" reads `get_file_type`, selection state, document outline (`_outline_entries`), and git presence, then offers keyboard-reachable suggestions. Lightweight context only.
5. **Command palette as agent surface.** Every AI action is a registered `Command` (so it appears in the palette and is keybindable). Agents can also *invoke* commands via the existing `tools.py` bridge, constrained by `SAFE_TOOL_IDS` + Permission Broker.
6. **Outline-aware agents.** Markdown Publisher and Accessibility Editor consume `read_document_outline` (from `_outline_entries`) to operate per-section, enabling section-scoped previews instead of whole-file rewrites.
7. **Live, summarized streaming.** The Streaming Event Bridge emits balanced announcements ("Three changes proposed", "Agent requests permission to read the document"), never token-by-token, honoring the verbosity setting.
8. **Ambient availability badge.** The existing startup backend-state announcement and `AIAvailability` feed a non-blocking status cue so users always know if AI is ready, needs a key, or is off.
9. **BRF/Braille-aware help.** The Braille/BRF Assistant respects screen-reader-only braille goals: status-bar text and spoken feedback, no heavy visual UI, building on `core/brf_page_detection.py` and braille status modules.
10. **Sessions you can return to.** Resume or branch a prior session from the Hub's Sessions tab (`sessions.py` tree), so a rewrite explored yesterday is still there.
11. **Quillin-contributed agents/tools** appear inline in the same catalog and palette, registered through `CommandRegistry.try_register`, sandboxed and lint-gated.

---

## 7. Consolidation: one provider truth (Priority 1)

The single most valuable change. Two systems exist:

- `assistant_ai` (AI-13): `AssistantConnectionSettings`, per-provider keys via Credential Manager/DPAPI, eight providers, streaming, security checks. **This is the richer, canonical one.**
- `ai_chat.PROVIDERS`: a lighter dict used by `SimpleChatBackend` and `AskQuillChatDialog`'s inline setup.

**Plan:**

1. Make `assistant_ai` the single source. Map `ai_chat`'s four entries onto provider ids that already exist there (`openrouter`, `openai`, `ollama` local, `ollama_cloud`).
2. Reimplement `ai_chat.send_prompt`/`list_models` as thin shims over `assistant_ai`/`ProviderChatBackend`, or migrate callers (`AskQuillChatDialog`, `SimpleChatBackend`) to `ProviderChatBackend` directly, then deprecate `ai_chat.PROVIDERS`.
3. One credential-target convention (`provider_credential_target`) for all providers; migrate `quill-openrouter-api-key` etc. with a one-time settings migration (atomic, reversible).
4. The AI Hub Providers tab reads/writes only the consolidated store.

**Acceptance:** changing the provider/key in the AI Hub changes it for Ask Quill, Writing Assistant, inline grammar/spell/thesaurus, and every harness. No surface has its own private provider list.

---

## 8. Target Architecture

```
QUILL UI Layer
  AI Hub (command center)          [extend ai_hub_dialog -> multi-tab hub]
  Ask Quill chat / Writing Assistant / Agent Center / Prompt Studio  [unify behind Hub]
  Diff Review dialog               [exists: built on diff_review.py]
  Status / Prism announcements     [exists]
  Setup wizard AI pages            [exists]

QUILL AI Core  (quill/core/ai + assistant_ai)
  Provider catalog + connection    [exists: providers.py, assistant_ai.py]   (consolidate, S7)
  Backend abstraction              [exists: backend.py / provider_backend.py]
  Harness Registry                 [NEW: ai/harness/]
  Agent Catalog (declarative)      [extend: assistant_agents.py + schema]
  Context Builder                  [NEW: ai/context_builder.py]  (uses compaction.py, redaction)
  Permission Broker                [NEW: ai/permissions.py]
  Safe Editor Tool Gateway         [NEW: ai/tool_gateway.py]  (formalizes today's callbacks + tools.py)
  Streaming Event Bridge           [NEW: ai/events.py]
  Session Manager                  [exists: sessions.py + compaction.py]
  Activity/Audit log               [NEW: ai/activity_log.py]  (uses redaction, write_json_atomic)
  Availability                     [exists: availability.py]
  Credential vault                 [exists: assistant_ai + credential_manager/DPAPI]

Optional Harness Packs (extras; lazy import; never required)
  Native (default)  Ollama/Local  BYOK/OpenAI-compatible
  Copilot SDK  Claude Agent SDK  OpenAI Agents SDK  MS Agent Framework  LangGraph  OpenHands

QUILL Editor Services (consumed by the Gateway)
  Buffer/Selection/Undo  [main_frame: GetValue, _selected_text, _replace_document_text,
                          _record_persistent_undo_state, _maybe_autosave]
  Outline   [_outline_entries]   Diff [diff_review]   Commands [CommandRegistry]
  Announce  [_announce/_set_status -> Prism]          Git/Workspace [services]
```

### 8.1 The Harness protocol (new)

A thin protocol so the native loop and SDK packs are interchangeable. It sits **above** `AIBackend` (which stays the per-provider transport).

```python
class Harness(Protocol):
    id: str
    display_name: str
    def is_available(self) -> tuple[bool, str | None]: ...      # lazy import inside
    def capabilities(self) -> HarnessCapabilities: ...
    def start_session(self, agent: AgentSpec, ctx: AIContext,
                      gateway: SafeEditorToolGateway,
                      broker: PermissionBroker,
                      emit: Callable[[AgentEvent], None]) -> HarnessSession: ...
    def cancel(self, session_id: str) -> None: ...
```

- **Native harness** wraps today's `run_agent` / `AgentDecision` loop, upgraded to real tool-calling that asks the broker before each tool and streams `AgentEvent`s.
- **SDK harnesses** translate their native tool/skill calls into `SafeEditorToolGateway` calls and their streams into `AgentEvent`s. They **never** edit the buffer directly.
- Availability mirrors `provider_backend.is_available`: an uninstalled pack returns `(False, "Install the X pack")`, and QUILL keeps working.

### 8.2 Capability model

Reuse the v1 capability JSON (chat, streaming, tool_calling, patch_generation, mcp, skills, subagents, local_only, requires_api_key, requires_oauth, images, audio, long_context). QUILL must never assume a capability another harness has. The Hub hides/disables unsupported actions with a one-line reason.

---

## 9. Safe Editor Tool Gateway (formalize today's callbacks)

Promote the `AskQuillChatDialog` callback bundle into one typed object with permission checks, so every harness uses the identical, audited surface.

**Initial tools (all exist today as callbacks or commands):**

```
read_selection()                 -> _selected_text()
read_current_document(scope)     -> editor.GetValue() (scope-gated by Context Builder)
read_document_outline()          -> _outline_entries()
read_document_metadata()         -> file type, length, dirty
read_current_line / surrounding  -> editor APIs
replace_selection(text)          -> _apply_python_result-style replace + undo checkpoint
insert_at_cursor(text)           -> insert + undo checkpoint
apply_text_patch(patch)          -> build_diff_review -> review dialog -> one-undo apply
create_undo_checkpoint(label)    -> _record_persistent_undo_state
show_diff(original, proposed)    -> diff_review dialog
ask_user_permission(msg, opts)   -> Permission Broker prompt
announce_status(msg, politeness) -> _announce / _set_status -> Prism
get_file_type / search_document  -> existing helpers
run_quill_command(id, args)      -> tools.run_tool, constrained to SAFE_TOOL_IDS + broker
create_new_document / open_review_dialog
```

**Future tools (Phase 5+):** `read_github_issues`, `create_github_issue_draft`, `create_pull_request_description`, `run_markdown_linter`, `run_accessibility_checker` (wraps `accessibility_agent`), `convert_document_with_pandoc`, `run_tests`, `read_brf_page_map` (wraps `brf_page_detection`).

**Rules:** every mutating tool creates an undo checkpoint and announces it; document-wide mutations require preview by default; every call is recorded in the Activity log (scope, not raw content, by default).

---

## 10. Permission Broker, Risk Levels, Profiles (new logic, defaults from code)

The broker resolves `allow / deny / ask / preview_required` per tool category, given the active agent's risk level and the global safety profile.

| Permission | Examples | Default |
| --- | --- | --- |
| Read selection | read selected text | Allowed after user action |
| Read document | summarize document | Ask before full document |
| Read workspace | multi-file work | Ask every time initially |
| Modify selection | replace selection | Preview or apply-with-undo |
| Modify document | apply patch | Preview required |
| Create/Save file | draft/write | Ask |
| GitHub | issues/PRs | Ask |
| Terminal | run tests/shell | Ask always (off by default) |
| Web | research | Ask / provider setting |
| Memory | store preference | Ask / visible setting |

Risk levels (low/medium/high/critical) and the four profiles (Careful, Balanced, Power User, Locked Down) carry over from v1 and become Permission-tab settings. **Floor:** `run_quill_command` can only target `SAFE_TOOL_IDS`, regardless of profile.

---

## 11. Context Builder + Privacy (new object, existing parts)

Scopes: selection only, current section, document summary (via `compaction.py`), full document, open documents, workspace summary, explicit files, GitHub context, prompt-only.

- **Preview before send:** an accessible, plain "Context to share" dialog (words, file name/type, included headings, whether full document/workspace included; Continue / Show Text / Cancel).
- **Redaction:** run `stability/redaction.py` patterns before sending; on a hit, "Possible secret detected. QUILL will redact it before sending. Continue?"
- **Never by default:** hidden/.env files, keys, tokens, private keys, large binaries.
- **Egress:** any new outbound path is added to `network_egress_audit.py` and respects Safe Mode.

---

## 12. Diff, Patch, Undo (exists — make it universal)

`diff_review.py` is already the right model. The plan: make it the **only** way medium+ edits land. Normalize every harness's output (replace-selection, insert, unified diff, structured ops, full-document-with-confirmation) into `DiffReview`. Undo always = one checkpoint via `_record_persistent_undo_state`; "Review last AI change" reopens the last `DiffReview`.

---

## 13. Agent Catalog (extend `AgentProfile` into declarative files)

Today: four `AgentProfile`s plus `accessibility_agent`. Target: a declarative catalog (YAML/JSON validated against a new `core/schemas/agent.json`, reusing the Quillin validation style) that the Hub lists and any harness can run.

Each agent declares: id, display name, description, recommended file types, default context scope, risk level, tools, per-category permissions, default harness (`auto`), system prompt.

**Launch set (promote/extend what exists):** Writing Companion (from `rewrite`), Accessibility Editor (`accessibility_agent`), Markdown Publisher, Code Doctor, GitHub Maintainer, PRD Architect, Release Notes Builder, QUILL Concierge, Learning Coach, plus the existing summarize/research/qa as Summarizer/Researcher/Reviewer. **Later:** Screen Reader UX Reviewer, Braille/BRF Assistant, Document Converter, Regex Helper, Snippet Builder (ties to QUILL snippets), Data Cleaner, Meeting Notes, Policy/Governance, Test Builder, Migration Assistant, Agent Builder.

Provider adaptation: one QUILL agent -> Copilot custom agent/skill, Claude skill/subagent, OpenAI agent+guardrails, LangGraph node, or native prompt/tool loop.

---

## 14. Sessions, Memory, Streaming Events

- **Sessions:** keep `sessions.py` (branch/resume tree) and `compaction.py`; surface them in the Hub's Sessions tab; auto-compact long agent runs with an announcement.
- **Streaming Event Bridge (new):** normalize every harness stream into: `agent_started, agent_thinking_summary, agent_text_delta, tool_call_requested, tool_call_allowed, tool_call_denied, tool_call_completed, patch_proposed, patch_applied, permission_required, warning, error, agent_completed, agent_cancelled`. The accessibility layer maps these to balanced announcements; token deltas are summarized, not spoken individually.

---

## 15. Authentication, Keys, Settings

- **Auth:** API key (Credential Manager/DPAPI — exists), env var, no-key local, org-managed, OAuth device login (`device_login.py` — exists). Config stores provider id/base URL/model/non-secret prefs only; never secrets.
- **Settings** stay schema-validated and atomic. New keys live under the existing `ai.*` style and resolve through the consolidated provider store. Examples: `ai.enabled`, `ai.defaultHarness="auto"`, `ai.defaultProvider`, `ai.context.defaultScope="selection_or_section"`, `ai.context.askBeforeFullDocument`, `ai.editing.defaultMode="suggest"`, `ai.editing.allowApplyWithUndo`, `ai.accessibility.announcementVerbosity="balanced"`, `ai.accessibility.streamToScreenReader=false`, `ai.permissions.profile="balanced"`. Enterprise admin policy (`allowedProviders`, `blockedProviders`, `allowUserApiKeys`, `policyNoticeUrl`) is honored by the provider catalog and broker.

---

## 16. Quillin Integration (extensions)

Quillins can contribute **agents** (catalog files), **tools** (registered commands via `try_register`, still subject to `SAFE_TOOL_IDS`/broker), and eventually **harnesses** (declared, lazily imported). All are sandboxed, manifest-validated (`core/schemas/extension.json` + a new `agent.json`), and pass `quillin_lint --strict`. Unsafe permissions require explicit approval at import.

---

## 17. Accessibility Requirements (carry over, enforce via gates)

- Every AI command reachable from menu + command palette; Escape cancels; Ctrl+Z undoes; Alt+Shift+D reviews last change; focus returns to editor (`returnFocusToEditor`).
- Announcement verbosity: Quiet / Balanced / Detailed / Debug. Default Balanced. No per-token speech.
- Diff dialog: summary, next/prev change, original/proposed, accept/reject/all, copy, save-as-text (all already feasible on `diff_review.py`).
- Chat: standard text entry, list-navigable messages, copy/stop/retry/insert/replace, "response complete" announcement.
- All new dialogs pass `dialog_inventory` and `dialog_button_contract`; axe-equivalent keyboard/focus tests in CI.

---

## 18. Implementation Roadmap (rebased; priority order)

Phases reflect the real starting point. Phase numbers are priority order, not calendar.

### Phase 1 — Consolidate and formalize (highest value, lowest risk)
- One provider truth (Section 7): converge `ai_chat.PROVIDERS` into `assistant_ai`; migrate keys; Hub Providers tab on the single store.
- Extract the `AskQuillChatDialog` callbacks into a formal `SafeEditorToolGateway` (`ai/tool_gateway.py`); route all existing AI edits through it and through `diff_review`.
- Add `PermissionBroker` (`ai/permissions.py`) with categories + the four profiles; wire `SAFE_TOOL_IDS` as the floor.
- Add `ActivityLog` (`ai/activity_log.py`) with redaction; add Hub "Activity" + "Review/Undo last AI change."
- **Acceptance:** every existing surface uses one provider, one gateway, one diff/undo path, one log. No behavior regressions; QUILL still runs with AI off and in Safe Mode.

### Phase 2 — AI Hub as command center
- Promote `AIHubDialog` to Home/Agents/Chat/Sessions/Activity/Providers/Harnesses/Audio/Permissions/Advanced (split into per-tab modules for GATE-11).
- Context Builder (`ai/context_builder.py`) + "show what will be sent" preview.
- Streaming Event Bridge (`ai/events.py`) + balanced announcements.
- Concierge "What can I do here?" on Home and status bar.
- **Acceptance:** a user configures, picks an agent, runs it, reviews, undoes, and inspects activity entirely from the Hub, keyboard-only.

### Phase 3 — Declarative Agent Catalog + real native agent loop
- `core/schemas/agent.json`; load catalog files; promote `accessibility_agent` and the four profiles; add Markdown Publisher, Code Doctor, GitHub Maintainer (local-only), PRD Architect, Release Notes Builder, Concierge.
- Upgrade the native harness to a true tool-calling loop (broker-gated, event-streamed) replacing the generate+refine shortcut where richer flows are needed.
- **Acceptance:** Selection Action Ring, document clean-up with hunk preview, and accessibility review all run through catalog agents on the native harness.

### Phase 4 — Local + BYOK polish (mostly exists)
- Harden Ollama/local and OpenAI-compatible/LiteLLM base-URL flows on the consolidated store; test-connection; model selector; cost/context warnings.
- **Acceptance:** local-only and org-endpoint users get the full agent catalog with no cloud account.

### Phase 5 — Optional harness packs (the multi-harness promise)
- Introduce `ai/harness/` registry + protocol; ship Native first; then **Copilot SDK**, **Claude Agent SDK**, **OpenAI Agents SDK** as extras (`quill[ai-copilot]`, `[ai-claude]`, `[ai-openai]`), each bridging to the gateway + broker, lazily imported, added to the network audit.
- **Acceptance:** with a pack installed and authed, a harness reads selection and proposes an edit **only** through QUILL's gateway/diff/undo; uninstalled packs degrade gracefully.

### Phase 6 — Enterprise + durable workflows
- Microsoft Agent Framework pack + admin policy enforcement; LangGraph durable, pause/resume, human-in-the-loop workflows (release prep, accessibility audit, PRD creation) persisted via existing atomic storage.

### Phase 7 — Developer agents + marketplace
- OpenHands experimental pack (sandboxed, flag-gated, full action log); Agent Builder; Quillin-distributed agent/tool/harness packs with signature/trust and lint gates.

---

## 19. Concrete file/module plan

**New (core):** `quill/core/ai/tool_gateway.py`, `permissions.py`, `context_builder.py`, `events.py`, `activity_log.py`, `harness/__init__.py` (`Harness`, `HarnessRegistry`, `HarnessCapabilities`), `harness/native.py`; `quill/core/schemas/agent.json`; agent catalog files under `quill/core/ai/agents/` (or bundled).

**New (UI):** `quill/ui/ai_hub_home.py`, `ai_hub_agents.py`, `ai_hub_sessions.py`, `ai_hub_activity.py`, `ai_hub_harnesses.py`, `ai_hub_permissions.py` (split out of `ai_hub_dialog.py`).

**New (optional packs, extras):** `quill/ai_packs/copilot/`, `claude/`, `openai_agents/`, `microsoft/`, `langgraph/`, `openhands/` — each a lazily imported `Harness`.

**Modified:** `ai_chat.py` (shim/deprecate), `provider_backend.py` (single store), `assistant_ai.py` (provider convergence; watch GATE-11 — extract if needed), `assistant_agents.py` (catalog loader), `ai/agent_session.py` + `ai/agent.py` (tool-calling loop + events), `ui/assistant_panel.py` (use the gateway), `ui/ai_hub_dialog.py` (tab host), `ui/main_frame.py` (gateway provider; Selection Action Ring command; minimal additions), `tools/network_egress_audit.py` (new harness/tool sites), `tools/module_size_budgets.json` (rebaseline with dated comments), dialog-inventory fixtures, `pyproject` extras.

---

## 20. Testing Plan (real layout)

- **Unit (`tests/unit/core/ai/`):** provider convergence + key migration; gateway permission enforcement; broker resolution per profile; context builder scopes + redaction; event normalization; activity-log redaction; harness availability/lazy-import; agent-catalog schema validation; extend existing `test_agent_session`, `test_provider_chat`, `test_document_qa`.
- **Integration (`tests/unit/ui/`, `tests/stability/`):** Mock harness end-to-end through the gateway; fake OpenAI-compatible server; Ollama if available; provider-missing and auth-failure paths; Safe Mode blocks every harness; streaming normalization.
- **Accessibility (`tests/unit/ui/`):** keyboard-only Hub, chat, and diff review; focus return; verbosity; extend `test_ai_hub_lazy_string_regression`, `test_main_frame_accessibility`, `test_connection_dialog_a11y`.
- **Safety:** agent edits/reads without permission are blocked; `run_quill_command` cannot escape `SAFE_TOOL_IDS`; malformed patch handled; secret detection catches token-like content; keys never in logs (assert via redaction).
- **Performance:** large-document context build; cancel long calls; UI responsiveness during sessions; startup with zero packs vs several.
- **Gates:** `ruff`, scoped `mypy quill/core/ai` (core is strict-typed), `dialog_inventory`, `dialog_button_contract`, `network_egress_audit`, GATE-11 budget, `quillin_lint` for agent packs.

---

## 21. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Provider consolidation breaks a surface | Regressions in shipping AI | Shim `ai_chat`; migrate behind tests; reversible key migration |
| SDK packs evolve fast | Broken harness | Optional, lazy, version-checked adapters; Native always works |
| AI edits harm documents | Trust loss | Universal diff review + one-undo via existing path |
| UI freeze | Bad a11y | All work on `QuillTaskManager` + `wx.CallAfter`; cancel everywhere |
| Secrets leak | Security | Redaction before send + in logs; Credential Manager/DPAPI; network audit |
| Hub/`assistant_ai` exceed size budget | GATE-11 failure | Split into per-tab/per-concern modules; rebaseline with reasons |
| Screen-reader noise | Unusable | Verbosity controls; summarized streaming; balanced defaults |
| Too many overlapping dialogs | Confusion | Consolidate behind the Hub; keep focused views reachable |

---

## 22. Developer Handoff Prompts (grounded in real symbols)

**Phase 1A — one provider truth.** "Make `assistant_ai`'s `AssistantConnectionSettings`/provider catalog the single provider source. Reimplement `ai_chat.send_prompt`/`list_models` as shims over `ProviderChatBackend`, or migrate `AskQuillChatDialog` and `SimpleChatBackend` to it; migrate `quill-*-api-key` credentials to `provider_credential_target` with a reversible one-time migration. Keep Safe Mode and the network audit intact. Add tests under `tests/unit/core/ai/`."

**Phase 1B — formal gateway + broker.** "Create `quill/core/ai/tool_gateway.py` (`SafeEditorToolGateway`) capturing the callbacks `AskQuillChatDialog` already receives, plus `quill/core/ai/permissions.py` (`PermissionBroker`, categories, four profiles). Route every AI edit through the gateway and `build_diff_review`; enforce `SAFE_TOOL_IDS` as the floor for `run_quill_command`. Add `ai/activity_log.py` with `redaction`. Unit-test enforcement."

**Phase 2 — Hub command center.** "Promote `AIHubDialog` to tabs Home/Agents/Chat/Sessions/Activity/Providers/Harnesses/Audio/Permissions/Advanced, split into `ai_hub_*` modules for GATE-11. Add `ai/context_builder.py` with a 'show what will be sent' preview and `ai/events.py` Streaming Event Bridge feeding balanced announcements. Keep one `_show_modal_dialog`+`apply_modal_ids` surface; update dialog-inventory fixtures."

**Phase 5 — first harness pack.** "Add `quill/core/ai/harness/` (`Harness` protocol, `HarnessRegistry`, capabilities) with a Native harness wrapping the upgraded tool-calling loop. Then add an optional Copilot SDK pack as a lazily-imported `Harness` that bridges to `SafeEditorToolGateway` + `PermissionBroker` and emits `AgentEvent`s; never edits the buffer directly. Add availability detection, network-audit entries, and mocked tests."

---

## 23. Design decisions recommended now

1. **Consolidate before you expand.** One provider truth and one gateway first.
2. The **AI Hub** is the front door; other dialogs become focused views behind it.
3. **Reuse, don't rebuild:** `diff_review`, `sessions`, `compaction`, `availability`, `tools`, `accessibility_agent`, `device_login`, Credential Manager/DPAPI are the foundation.
4. Every harness drives the **same** gateway/broker/diff/undo; none touches wx controls.
5. Agents are **declarative, QUILL-owned files**; harnesses adapt them.
6. Accessibility, Safe Mode, network audit, and GATE-11 are **gates**, not afterthoughts.
7. The first magic moment stays **selection rewrite + one-undo**.

---

## 24. Final Product Promise

> "I open the AI Hub. I choose my engine, and if I want, my harness. I pick an agent. QUILL understands what I am editing. The agent helps me write, fix, explain, publish, and improve. I always see what is shared. I always control what changes. I can undo anything in one step. It works beautifully with my screen reader. And if I want none of it, QUILL is still QUILL."

That is the magic — built on what QUILL already is.
