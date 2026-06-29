# QUILL Companion — Comprehensive Context-Aware Agent PRD

**Product:** QUILL for All
**Feature Area:** A single, context-aware agentic companion that can converse, answer
fact questions about the open document, edit and revise, audit accessibility, read the
app's own state, and research on the web — all inside QUILL's existing privacy, undo,
and screen-reader-first guarantees.
**Document Type:** Implementation-grounded delta plan.
**Version:** 1.0 Draft
**Date:** 2026-06-26
**Branch of record:** `2.0-dev`
**Relationship to other docs:** This is a focused companion to
[`quill_end_to_end_agentic_ai_prd.md`](quill_end_to_end_agentic_ai_prd.md) (the broader
agentic platform PRD). That document inventories the substrate; this one specifies the
single conversational companion that sits on top of it. Plan of record remains
[`roadmap-2.0.md`](roadmap-2.0.md); live tracker is [`todo.md`](todo.md).

---

## 0. How to read this document

This is a **delta plan**, not greenfield. The 2.0 AI substrate already exists and is
tested: a provider-neutral tool loop (`ai/tool_loop.py`), a prompt-based tool planner
(`ai/tool_planner.py`), the shared editor tool surface (`ai/agent_tools.py`), the Safe
Editor Tool Gateway with permission broker + diff preview + undo + audit
(`ai/tool_gateway.py`), the context builder with redaction + a "what will be sent"
preview (`ai/context_builder.py`), large-document helpers (`ai/doc_context.py`), the
deterministic concierge (`ai/concierge.py`), and the editor host adapter
(`ui/agent_editor_host.py`). The companion is mostly **wiring plus three new
capabilities** (a conversational loop, app-state awareness, and web research).

Each section says whether a capability **exists**, must be **extended**, or is **new**,
and points at the real module.

---

## 1. The vision

One companion the user can talk to as a partner in everything QUILL: their document,
the editor, the app, and the open web. In one conversation the user can:

- Ask a question and get an answer (no edit) — including **fact-based questions about
  the content of the open document**.
- Ask for edits and revisions, always preview-gated and undoable.
- Ask "where am I / what can I do here" and "what's turned on or off."
- Ask for an **accessibility audit** and offers to fix what it finds.
- Ask the companion to **research on the web** and fold findings back into the document
  with citations. Example: *"Help me refine this document by doing research on the
  Space Shuttle and the Challenger explosion"* for a student's science paper.

It must feel magical: aware of local document context, the editor surface, and app
state, while never silently sending content off-machine and never editing without a
reviewed, single-undo step.

---

## 2. Hard constraints (non-negotiable)

These come from the codebase invariants (`CLAUDE.md`) and must hold for every phase:

- **Network egress is gated.** Every outbound call is inventoried in
  `tools/network_egress_audit.py` and requires explicit consent. Web research is built
  on the **selected engine's native web capability** (provider fallback to a configured
  search API) behind a **per-session toggle** with a `ContextBuilder` privacy preview
  before the first send, and every call audited. (Product decisions, 2026-06-26.)
- **QUILL owns the editor.** No harness edits the buffer directly; every mutation goes
  through `SafeEditorToolGateway` (permission -> preview -> undo checkpoint -> audit).
- **Threading.** Model/network work runs off the UI thread; every wx touch is marshalled
  via `wx.CallAfter`. Core stays wx-free.
- **Safe Mode** (`QUILL_SAFE_MODE=1`) disables the companion entirely.
- **Privacy by default.** Hidden/.env files, keys, and secrets are out of scope by
  construction; redaction is the backstop on everything assembled for a send.

---

## 3. Architecture: one tool belt, four domains

The companion is the multi-step `run_tool_loop` driven as a **conversation** (memory
across turns), choosing each turn from one tool belt that spans four domains. A `final`
answer with no mutating tool call is a **Q&A response**; a mutating tool call is a
reviewed edit. Everything routes through the gateway.

1. **Document** — `read_selection`, `read_document`, `read_outline` (exist); add
   `read_section` (`doc_context.section_text`) and large-doc chunk/summary
   (`doc_context.chunk_text` / `structured_summary`).
2. **Editor + app state (new)** — `read_app_state`: cursor position, current section,
   file type, dirty flag, AI on/off, Safe Mode, watch folder, git presence, and which
   status-bar items are enabled/disabled. Extends `EditorHost` and enriches
   `ConciergeContext`.
3. **Accessibility (new tool, existing logic)** — `audit_accessibility`: runs the
   existing accessibility-editor checks and returns structured findings.
4. **Web research (new, gated)** — `web_search` + `web_fetch` delegating to the selected
   engine's native web tool; results feed `apply_patch` with citations
   (`citation-link-fixer`).

Mutations stay as today: `replace_selection`, `insert`, `apply_patch` (diff-previewed),
`run_command`.

---

## 4. Phased build order

Each phase ships independently and leaves the app working. Core-first, wx-free, tested,
then thin UI views.

### Phase 1 — Conversational loop (DONE)
**Core (new):** `ai/conversation.py` — a wx-free `ConversationSession` that holds
multi-turn memory and drives `run_tool_loop` per user turn against the same gateway,
returning either an answer (Q&A) or a reflected edit. Fully tested with a scripted
planner.
**UI (done):** the Ask Quill dialog (`ui/assistant_panel.py`) now accepts a
`conversation` callable; `MainFrame.open_ask_quill_chat` builds a `ConversationSession`
via `agent_editor_host.build_companion_session` and passes it in, replacing the legacy
`assistant.decide(...)` heuristic when a provider is available (legacy path remains as
the fallback for inline provider setup and Safe Mode). The companion runs through a
dedicated `_CompanionEditorHost` that marshals every wx touch to the UI thread (the
loop runs on a worker thread) and keeps the gateway's review-then-apply shape so
insert / replace / whole-document edits are each correct. Per-hunk partial acceptance
is deferred (the review accepts/rejects the whole proposed edit).

### Phase 2 — Context through ContextBuilder (DONE)
Both the one-shot `run_agent` and the conversation path now assemble context via
`ContextBuilder` over a new `StringContextSource`, so redaction always applies and a
"what will be sent" preview (`ui/context_preview_dialog.confirm_context_share`:
speakable summary + Show Text + Continue/Cancel) gates the send. Large documents are
sent as a structure-aware summary via `choose_context_scope` (verbatim under the token
limit, `DOCUMENT_SUMMARY` above it; selection wins when present). `run_agent` previews
once per run; the chat previews once per session then reuses consent. Cancel aborts the
send. New core: `StringContextSource`, `choose_context_scope` in `context_builder.py`.

### Phase 3 — App/editor-state awareness (DONE)
`EditorHost` gained `get_cursor_position`, `get_current_section`, `get_status_flags`
(implemented on `MainFrameEditorHost` and the UI-thread-marshalling
`_CompanionEditorHost`); gateway tools `read_app_state` (cursor + file type + feature
flags) and `read_section` (current section text) added to the shared tool surface;
`ConciergeContext` gained `cursor_line` / `cursor_column` / `current_section_title`.
Gateway probes the optional host methods via getattr and degrades gracefully.

### Phase 4 — Accessibility as a tool (DONE)
`audit_accessibility` gateway tool reuses `core/accessibility_agent.build_plan` +
`build_plan_report` (structure / link-text / alt-text / plain-language findings),
gated at READ_DOCUMENT. The agent can run it and explain or fix what it finds.

### Phase 5 — Web research (DONE, gated seam)
Uses the existing `WEB` permission (consent + audit). `web_search` / `web_fetch`
gateway tools call a `core/ai/web_research.WebResearchProvider`; the default
`NullWebResearchProvider` makes web research inert ("not configured") so nothing
reaches the network silently. A real backend (engine-native web tool, or a configured
search API) plugs into the seam and must add a `network_egress_audit` entry, since that
is where the outbound call lives. LOCKED_DOWN blocks it; BALANCED asks consent.

### Phase 6 — Voice conversation + thinking indicator (DONE)
Voice in/out for the Ask Quill chat, on top of the existing speech stack
(`core/speech/capture.py` mic, an installed STT model, `core/ai/tts.py` for spoken
output + MP3 export). Bindings: `Alt+Shift+Q` opens Ask Quill in voice conversation
mode (`tools.ask_quill_conversation`); inside the chat, `Ctrl+F9` records a spoken
question (push-to-talk toggle: press to start, press again to stop, transcribe, and
send). Spoken answers play through `ui/speech_player_dialog.show_speech_player` with
Pause/Resume, Stop, Play (replay), and Save as media (MP3); Escape dismisses. A
`ThinkingIndicator` (`core/ai/thinking.py`, tested) drives a "thinking" earcon +
"still thinking" reminders during long waits in BOTH text and voice modes (via
`AI_THINKING_STARTED` / `AI_RESPONSE_RECEIVED` / `AI_ERROR` earcons). Everything
degrades gracefully: no mic/STT model => text input only; no TTS key (OpenAI) =>
screen-reader announcement instead of the audio player. New: `ui/voice_services.py`
(wx-free, injected), `ui/speech_player_dialog.py`, `core/ai/thinking.py`, a
`pause_event` on `tts.speak_text`. Provider-agnostic STT->agent->TTS pipeline (works
with any chat model); native realtime voice is a possible later tier.

---

## 5. Acceptance per phase

- **Phase 1:** A scripted multi-turn conversation answers a question without editing,
  performs a reviewed edit on request, and carries memory across turns; every edit
  still flows through the gateway. Unit-tested.
- **Phase 2:** A whole-document run shows the privacy preview and redacts an injected
  secret before any send; a large document is summarized/chunked to fit.
- **Phase 3:** The companion can report cursor/section and enabled/disabled features.
- **Phase 4:** The companion lists real accessibility findings for a document.
- **Phase 5:** A research request is gated by the per-session toggle, shows the privacy
  preview, is fully audited, and produces cited edits.

---

## 6. Open items

- Per-engine native web-tool registration depends on the live SDK packs.
- The secret-masking policy for whole-document transforms is a product decision (also
  noted in the broader agentic PRD §0a).
