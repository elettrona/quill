# QUILL Companion — live agent showcase (fun.md)

Generated 2026-06-26 by actually running the QUILL Companion agent stack end to
end. This is not a mockup: every "agent" result below came from driving the real
path — `ProviderChatBackend` -> `PromptToolPlanner` -> `ConversationSession` ->
`SafeEditorToolGateway` -> editor host — against a live LLM, and every
"capability" result came straight through the real gateway tools.

Reproduce: `python scripts/companion_live_demo.py --model <model>`
(omit `--model` once a Claude/OpenAI key is configured), or
`pytest tests/integration/test_companion_live.py`.

## Honest provider note

This machine has no Claude or OpenAI key configured, so the live runs used a real
cloud model (`gemma4:31b-cloud` via Ollama Cloud) through the exact same
provider-agnostic path Claude/OpenAI use. Add a key and the same code runs them
unchanged. In-app web search reaches the network only through a gated provider
(Phase 5); on this machine that provider is a stand-in, and the real research text
was gathered with a separate web tool and handed to the agent as context — clearly
marked below.

---

## Part 1 — The agent, live (model-driven)

The model decided every step (which tools to call, when to stop). Provider:
ollama (Ollama Cloud); model: gemma4:31b-cloud.

### 1. Ask a question about the document

- You: "In one short sentence, what is this document about?"
- Document: "QUILL is an accessible, screen-reader-first word processor."
- Tools the agent chose: `read_document`
- Quill: "This document is about QUILL, an accessible, screen-reader-first word
  processor."
- Document changed: no. Time: 5.6s.

It read the document and answered — without editing. Exactly right for a question.

### 2. Ask for an edit

- You: "Fix the spelling mistakes in the selected text and replace the selection."
- Selection before: "the cat sat on teh mat"
- Tools the agent chose: `read_selection`, then `replace_selection`
- Selection after: "the cat sat on the mat"
- Quill: "I have corrected the spelling of 'teh' to 'the' in your selection."
- Document changed: yes, as one reviewed, undoable edit. Time: 8.4s.

### 3. Research -> refine -> document (the science-paper flow)

- You: "Using the research notes provided as context, write a clear three-sentence
  summary of the Challenger disaster for a student's science paper, then insert it
  into the document."
- Context: real Challenger research (see Part 3).
- Tools the agent chose: `insert` (exactly once)
- Inserted into the document:

> On January 28, 1986, the Space Shuttle Challenger broke apart 73 seconds after
> launch, resulting in the loss of all seven crew members. The disaster was caused
> by the failure of rubber O-ring seals in a solid rocket booster, which occurred
> due to unusually cold temperatures. This failure was attributed to flawed joint
> design and systemic communication breakdowns within NASA management.

- Document changed: yes. Time: 6.5s.

This is the "help me refine this document by researching X" flow you described —
research in, a clean cited-from-notes paragraph out, inserted for your review.

---

## Part 2 — Capabilities, straight through the gateway (Phases 3-5)

These are the new tools, exercised directly so the output is exact. Each one is
permission-checked and audited like every other agent action.

### Phase 3 — "Where am I?" (app + editor state)

`read_app_state`:

```
Cursor: line 5, column 3
File type: md
Features: ai_enabled=on; safe_mode=off; document_modified=on
```

`read_section` (the section the cursor is in):

```
### Day three

We hiked.
```

The agent now knows where you are and what's on or off — not just the document as
a blob.

### Phase 4 — Accessibility audit

`audit_accessibility` on a document with a skipped heading level and a "click
here" link:

```
Accessibility Tune-Up plan for the document

Scope: current document
Format: markdown
Findings before: 2
Proposed steps: 2 (0 automatic, 2 need review)

Proposed steps:
1. [structure] Heading level jumps by more than one (line 5) [needs review]
   Skipping heading levels breaks the document outline that screen-reader users
   rely on to navigate. Use the next level down instead.
   Context: ### Day three
2. [link-text] Link text does not describe its destination (line 3) [needs review]
   Generic link text like this is meaningless when a screen reader lists links out
   of context. Rewrite it to describe where the link goes.
   Context: [click here](https://x.example)
```

### Phase 5 — Web research (gated)

`web_search` (through the gated provider seam; consent + audit apply). With a
backend available it returns:

```
Web results for 'Challenger disaster cause':
1. Challenger disaster | Britannica — https://www.britannica.com/event/Challenger-disaster
   Broke apart 73 seconds after launch on January 28, 1986; O-ring seal failure.
2. What Caused the Challenger Disaster? | HISTORY — https://www.history.com/articles/how-the-challenger-disaster-changed-nasa
   Cold-stiffened O-rings, flawed booster joint design, NASA communication gaps.
```

By default web research is OFF ("Web research is not configured.") until a
web-capable engine or search provider is enabled — nothing reaches the network
silently.

### Concierge — "What can I do here?"

`suggest(...)` for a markdown document with two headings:

```
- Jump to a heading — 2 headings in this document
- Accessibility Editor — Find screen-reader-hostile structure and propose fixes
- Citation & Link Fixer — Improve link text and flag vague or broken references
- GitHub Maintainer — Turn notes into an issue, changelog, or PR description draft
```

---

## Part 3 — The web research used (real)

Performed with a separate web tool (QUILL's in-app web research backend is the
gated Phase 5 seam). Handed to the agent as context for Part 1, scenario 3.

Query: "Space Shuttle Challenger disaster 1986 cause O-ring facts"

- Challenger broke apart 73 seconds after launch on January 28, 1986, killing all
  seven crew members.
- Immediate cause: two rubber O-rings failed to seal a joint on the right solid
  rocket booster in severe cold, letting hot exhaust gas escape.
- Contributing factors: faulty joint design, insufficient low-temperature testing,
  and poor communication across NASA management; the flaw had been known since 1977.
- The booster was later redesigned with three O-rings.

Sources:
- [Challenger disaster | Britannica](https://www.britannica.com/event/Challenger-disaster)
- [The space shuttle Challenger explodes after liftoff | HISTORY](https://www.history.com/this-day-in-history/january-28/challenger-explodes)
- [What Caused the Challenger Disaster? | HISTORY](https://www.history.com/articles/how-the-challenger-disaster-changed-nasa)

---

## Tests run

- All agents, every engine: `tests/unit/core/ai/test_agent_matrix.py` — 15 agents x
  4 engines = 60 cases, all green.
- New capability tools: `tests/unit/core/ai/test_gateway_phase345.py` — 8 tests
  (app state, current section, graceful degrade, accessibility, web search/fetch,
  locked-down block).
- Conversation, loop, planner, thinking, context: all green.
- Full core/ai suite: 651 passed, 4 skipped.
- Live: `tests/integration/test_companion_live.py` (skips without a provider; passes
  against the cloud model).

## What changed since the last fun.md

- The earlier insert-looping bug is fixed (one edit per turn) AND the planner now
  tolerates the deviant tool JSON mid-size models emit (fenced ```json, tool name
  as the action, top-level args) — which is why scenario 3 now lands exactly one
  clean insert instead of duplicating or no-op'ing.
