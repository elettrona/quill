# QUILL Companion — development log / project memory

Saved from the working session that built the Companion (Phases 1–6) so the
context survives in the branch. The authoritative spec is
[`quill-companion-prd.md`](quill-companion-prd.md); this is the running log of
decisions, what shipped, and open follow-ups.

## Overview

Comprehensive context-aware agentic companion for QUILL 2.0: one conversation that
answers questions (incl. fact questions about the open document), edits/revises
(preview-gated, undoable), audits accessibility, reads editor/app state, and
researches on the web with citations. Example use: "refine this document by
researching the Space Shuttle / Challenger explosion" for a student's science
paper.

Built on the existing 2.0 substrate: `tool_loop`, `tool_planner`, `agent_tools`,
`tool_gateway`, `context_builder`, `doc_context`, `concierge`,
`ui/agent_editor_host`.

## Locked product decisions (2026-06-26)

- Web research uses the selected engine's native web tool (provider fallback to a
  configured search API), not raw requests.
- Consent is a per-session toggle + ContextBuilder privacy preview before the first
  send; every web call is audited via `tools/network_egress_audit.py`. (Implemented
  on the existing `WEB` permission rather than a new category.)

## Phase 1 — Conversational loop (DONE)

`quill/core/ai/conversation.py` (`ConversationSession` drives `run_tool_loop` with
multi-turn memory; Q&A = final answer with no mutating tool; edit = applied
mutating tool). UI: `AskQuillChatDialog` gained a `conversation` callable;
`MainFrame.open_ask_quill_chat` builds it via
`agent_editor_host.build_companion_session` (agent id `quill-companion`, reads
ALLOW, edits PREVIEW_REQUIRED, `SafetyProfile.BALANCED`, `ProviderChatBackend` +
`PromptToolPlanner`). Companion uses `_CompanionEditorHost`, which marshals every
wx call to the UI thread via `_run_on_ui` (the loop runs on a worker thread) and
keeps the gateway review-then-apply shape (preview only reviews; the gateway
applies via the correct per-tool primitive). Legacy `assistant.decide` path kept as
fallback (no provider / Safe Mode). Per-hunk partial acceptance deferred. Tests:
`test_conversation.py` (6), `test_companion_host.py` (5).

## Phase 2 — Context through ContextBuilder (DONE)

`context_builder.py` gained `StringContextSource` + `choose_context_scope`
(selection wins; else FULL verbatim under ~3000 tokens, else DOCUMENT_SUMMARY).
Both `run_agent` and the conversation assemble via `ContextBuilder` so redaction
always applies; `ui/context_preview_dialog.py` `confirm_context_share` (speakable
summary + Show Text toggle + Continue/Cancel, hardened_custom, via
`_show_modal_dialog`) gates the send. `run_agent` previews per run; the chat
previews once per session (consented flag) then reuses. Cancel aborts. Replaced
`_source_for_scope` with `_effective_scope` (downgrades large FULL to SUMMARY).
Tests: `test_context_phase2.py` (7).

## Phase 3 — App/editor-state awareness (DONE)

`EditorHost` + `get_cursor_position` / `get_current_section` / `get_status_flags`
(on `MainFrameEditorHost` and the marshalling `_CompanionEditorHost`); gateway
tools `read_app_state` + `read_section`; `ConciergeContext` +
`cursor_line`/`cursor_column`/`current_section_title`; the gateway probes the
optional host methods via getattr (graceful degrade).

## Phase 4 — Accessibility tool (DONE)

`audit_accessibility` gateway tool reuses
`core/accessibility_agent.build_plan` + `build_plan_report` (structure / link /
alt / plain-language findings), READ_DOCUMENT-gated.

## Phase 5 — Web research (DONE, gated seam)

Uses the existing `WEB` permission (not a new category). New
`core/ai/web_research.py` (`WebResearchProvider` Protocol +
`NullWebResearchProvider` default = inert "not configured", so no silent egress, +
`format_results`); the gateway gained a `web=` param and `web_search`/`web_fetch`
(consent + audit; LOCKED_DOWN blocks). A real backend (engine-native / search API)
plugs into the seam and must add a `network_egress_audit` entry. All five tools are
in `agent_tools` `TOOL_DESCRIPTORS` + `execute_tool`.

## Phase 6 — Voice + thinking indicator (DONE)

Bindings: `Alt+Shift+Q` = `tools.ask_quill_conversation` (opens Ask Quill voice
mode); `Ctrl+F9` = record a spoken question (dialog-local CHAR_HOOK, push-to-talk
toggle). `Ctrl+Shift+Q` was taken (`edit.quote_lines`), so not used. New files:
`core/ai/thinking.py` (`ThinkingIndicator`, tested — drives "thinking" / "still
thinking" earcons after patience 4s / repeat 8s, for text and voice),
`ui/voice_services.py` (wx-free; `MicRecorder` + STT provider capture→text; TTS
speak/export), `ui/speech_player_dialog.py` (`show_speech_player`:
Pause/Resume/Stop/Play/Save-as-media MP3, Escape dismiss). `tts.speak_text` gained
`pause_event` (coarse pause at chunk boundary). `main_frame`:
`open_ask_quill_conversation` + `_open_ask_quill(voice_mode)` +
`_signal_ai_sound` (maps to `SoundEvent.AI_THINKING_STARTED` /
`AI_RESPONSE_RECEIVED` / `AI_ERROR`) + `_build_voice_services`. `assistant_panel`
gained voice params + a thinking `wx.Timer` + Ctrl+F9 capture. Graceful degrade:
no mic/STT model = text input only; no OpenAI TTS key = screen-reader announce
instead of the player. Bindings added to `profile_default` + `profile_sr_friendly`.

## Robustness fixes

- Looping: `run_tool_loop` applies at most one edit per turn — a second mutating
  request finalizes instead of re-applying (fixed the 5x duplicate-insert bug);
  returns a human completion ("Done. I applied the change...") instead of a raw
  `"True"`. `MUTATING_TOOL_NAMES` centralized in `agent_tools.py`.
- Planner parser hardened (`tool_planner._parse`) to accept deviant tool JSON:
  `action`=toolname, a bare `tool` field, top-level args, and fenced ```json blocks
  — what mid-size models tend to emit.

## Live verification (2026-06-26)

`scripts/companion_live_demo.py` + `tests/integration/test_companion_live.py` drive
the real stack against the configured provider (skips without one). No Claude/OpenAI
key on the build box; only Ollama Cloud works (used `gemma4:31b-cloud`); the
provider-agnostic path is proven. Verified: Q&A (read_document, no edit), edit
(read_selection + replace_selection), research→insert (one insert). Capability
samples (read_app_state / read_section / audit_accessibility / web_search /
concierge) all real. Agent matrix 60/60 green; full unit sweep 2003 passed.
[`../../fun.md`](../../fun.md) documents a run.

Note: running the scripts needs `PYTHONPATH` set to the repo root (the editable
install's finder is stale and misses newly added modules).

## Open follow-ups

- Live web research and voice I/O are wired and gated but need a real backend /
  keys (and a microphone + installed STT model) to runtime-verify.
- Per-hunk partial diff acceptance in the companion path is deferred (whole-edit
  accept/reject for now).
- `assistant_panel.py` / `main_frame.py` / `agent_editor_host.py` remain
  decomposition targets; their size budgets were rebaselined for companion growth
  and should be lowered as they are split.
