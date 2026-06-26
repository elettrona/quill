# QUILL 2.0 Release Notes — the Agentic AI Platform (in development)

QUILL 2.0 turns QUILL's AI from a set of separate features into one coherent,
provider-neutral, **agentic** platform. The idea is simple: you choose your engine
(and, if you want, an advanced harness), you pick an agent, and QUILL helps you
write, fix, explain, publish, and improve your document — while you always see what
is shared, always control what changes, and can undo anything in one step.

Everything here follows QUILL's existing promises without exception. It is
**optional** — QUILL launches, edits, and saves with AI fully off, and in Safe Mode
every part of this is disabled. It is **screen-reader-first** — every action is
keyboard-reachable, focus is predictable, and announcements are balanced, never a
flood of tokens. And your content stays **on your machine** unless you explicitly
choose a cloud provider and send it.

> **Status: in development.** This document describes what the 2.0 agentic platform
> makes possible. The engine, agents, safety rails, and the editor wiring are built
> and tested; the AI Hub command-center UI and a few advanced pieces are still
> landing. Where something is available today only behind an experimental opt-in, it
> says so plainly.

## At a glance

- **One AI, many engines.** A single provider truth and a single safe path behind
  every AI surface, with an optional layer of advanced **harnesses** — Native plus
  Copilot, Claude, OpenAI, Microsoft, LangGraph, and OpenHands SDK packs — that all
  drive the *same* safe editor tools.
- **A catalog of agents** you can run on your writing: Writing Companion,
  Accessibility Editor, Markdown Publisher, Code Doctor, GitHub Maintainer, PRD
  Architect, Release Notes Builder, Summarizer, Researcher, Reviewer, and the QUILL
  Concierge.
- **Safe by construction.** Agents never touch your document directly. Every edit
  goes through a permission check, a reviewable diff, and a one-step undo, and every
  action is recorded in a redacted activity log.
- **"What can I do here?"** A Concierge that reads your context and offers
  keyboard-reachable next actions, and a Selection Action Ring of one-key transforms
  for the current selection.
- **Agents that take real steps.** A multi-step, permission-gated tool-calling loop,
  so an agent can read your document, propose a change, and apply it as reviewable
  hunks — every step announced in plain language.
- **You always see what's shared and what changed.** A context preview before
  anything is sent, secret-masking on outbound text, and the accessible diff-review
  dialog you already know for every medium-or-larger edit.
- **Enterprise-ready.** Organization policy can constrain which providers are
  allowed and whether users may bring their own keys.

## One front door, many engines

Today QUILL's AI lives behind several different dialogs backed by two different
provider systems. 2.0 unifies them so that choosing your provider and key in one
place changes it everywhere — Ask Quill, the Writing Assistant, inline tools, and
every agent.

On top of that single core sits an optional **harness** layer. A harness is the
engine that drives an agent. QUILL ships a built-in **Native** harness that always
works. If you want the capabilities of a specific vendor SDK, you can install an
optional pack:

- **Copilot SDK** (`quill[ai-copilot]`)
- **Claude Agent SDK** (`quill[ai-claude]`)
- **OpenAI Agents SDK** (`quill[ai-openai]`)
- **Microsoft Agent Framework** (`quill[ai-microsoft]`)
- **LangGraph** (`quill[ai-langgraph]`)
- **OpenHands** (`quill[ai-openhands]`, experimental)

Each pack is **optional and lazily loaded** — QUILL never imports an SDK you have
not installed, and a missing pack simply reports "Install the … pack" and QUILL
keeps working. Crucially, **every harness drives the same safe editor tools**: no
matter which engine produced a change, it lands through QUILL's permission check,
diff review, and one-step undo. None of them edits your document directly.

## Agents you can run on your writing

An **agent** is a named, purpose-built assistant. QUILL 2.0 introduces a declarative
agent catalog and a launch set:

- **Writing Companion** — rewrite, shorten, or warm up the selected text.
- **Accessibility Editor** — find screen-reader-hostile structure (skipped headings,
  "click here" links, layout tables, ambiguous lists) and propose accessible fixes.
- **Markdown Publisher** — clean up Markdown structure section by section.
- **Code Doctor** — explain, document, or tidy selected code without changing
  behavior.
- **GitHub Maintainer** — turn notes into an issue, changelog entry, or PR
  description draft (a draft only — it never publishes anything).
- **PRD Architect** and **Release Notes Builder** — shape notes into structured
  documents.
- **Summarizer**, **Researcher**, **Reviewer** — produce summaries, extract key
  points, and review writing quality.
- **QUILL Concierge** — answers "what can I do here?" with context-aware actions.

Each agent declares what it reads (a selection, a section, or the whole document)
and what it is allowed to change, so QUILL always applies the right safe behavior:
selection agents transform the selection, document agents transform the whole buffer
through a preview, and read-only agents open their output in a new document instead
of overwriting your work. Agents are plain, validated files, so the set can grow —
including, in time, agents contributed by Quillin extensions.

## Safe by construction

This is the heart of 2.0. Agents act only through a **Safe Editor Tool Gateway** —
the single, audited surface every engine uses. Around it sit four guarantees:

- **A permission broker.** Every tool a agent uses (read the selection, read the
  document, change the selection, change the document, run a command, reach the web
  or GitHub, run the terminal) is checked against your **safety profile** — Careful,
  Balanced, Power User, or Locked Down — and the agent's own risk level. A
  higher-risk agent can only ever make a decision *stricter*, never looser. Running
  a QUILL command is hard-limited to a curated safe allowlist that **no profile can
  widen**.
- **Reviewable changes.** Any medium-or-larger edit is shown in the accessible
  diff-review dialog you already use — navigate change by change, accept or reject
  per hunk, and apply as a single undo step. Nothing surprising lands silently.
- **One-step undo, always.** Every applied change creates an undo checkpoint, with a
  spoken "Press Control Z to undo."
- **A redacted activity log.** Every action is recorded — by scope, not raw content,
  with secrets scrubbed — so you can see what the AI did and undo the last change.

Because all of this lives below the engine, the guarantees hold identically whether
the change came from the Native harness or any SDK pack.

## "What can I do here?" — Concierge and the Selection Action Ring

The **Concierge** turns your current context — the file type, whether you have a
selection, how many headings the document has, whether you are in a git repository,
and whether AI is on — into a short list of concrete, keyboard-reachable actions.
Ask "what can I do here?" and get suggestions tuned to the moment, each pointing at
a real command you can run.

With text selected, the **Selection Action Ring** offers one-key transforms tuned to
the file type: *Rewrite clearly*, *Shorten*, *Make warmer*, *Review*, and *Check
accessibility* for prose; *Explain*, *Document*, and *Tidy* for code. Each is bound
to a real agent, so the ring never offers something that cannot run.

## Agents that take real steps

Beyond a single rewrite, 2.0 introduces a **multi-step tool-calling loop**. An agent
can read your selection, read the document, propose a patch, and apply it — taking
several steps, with each step gated by the permission broker and announced in plain
language. If a step is denied, the agent is told and can choose another path rather
than failing; a step limit keeps every run bounded. The result is agents that can do
real, multi-part work while never escaping the same safety rails as a one-shot edit.

## You always see what is shared, and what changed

Before anything is sent to a provider, a **context builder** assembles exactly the
scope you chose — selection, current section, a document summary, or the full
document — and can show a plain "context to share" summary: how many words, which
file, which headings, and whether the whole document is included. Outbound text is
run through **secret masking** so an accidentally pasted key or token is caught
before it leaves your machine. After the model responds, the diff-review dialog shows
you precisely what would change before you accept it.

## Balanced for your screen reader

A new **streaming event bridge** translates everything an agent does into balanced
announcements that honor your verbosity setting — *Quiet*, *Balanced*, *Detailed*,
or *Debug*. You hear that an agent started, that changes were proposed, that a change
was applied (with the undo cue), and that it finished — never a stream of individual
tokens. Safety-bearing events (an error, a permission prompt, an applied change) are
spoken even at the quietest setting.

## Enterprise-ready

For managed deployments, organization policy can list **allowed** or **blocked**
providers and control whether users may supply their **own API keys**. Disabling AI
entirely is always permitted, regardless of policy.

## Trying it today (experimental opt-in)

Most of the platform's engine, agents, and safety rails are built and tested now.
The full **AI Hub** command center that will surface all of this is still landing, so
an early, experimental path is available behind an opt-in for testers:

- Set the environment variable **`QUILL_AI_AGENT_GATEWAY=1`** before launching QUILL.
- A new **AI menu** item, *Run Agent on Selection (experimental)…*, appears, and the
  command palette gains a **Run Agent: …** entry for each catalog agent (so
  document-scoped agents like the Accessibility Editor and Markdown Publisher are
  reachable too).
- Running an agent uses your configured provider, shows the change in the diff-review
  dialog, applies it as one undoable edit, and announces it — exactly as the shipped
  platform will.

With the opt-in off (the default), nothing changes: the experimental command is not
even registered, and every existing AI surface behaves exactly as before.

## The promises, unchanged

- **Optional by design.** Base QUILL runs with the provider set to Off; every harness
  pack is an opt-in extra.
- **QUILL owns the editor.** Agents never touch the editor directly — only through
  the gateway, which uses the same replace-and-undo path QUILL already uses.
- **Reviewable and reversible.** Diff review for every medium-or-larger edit; one-step
  undo for everything.
- **Screen-reader-first.** Keyboard-reachable, predictable focus, balanced
  announcements, and a context preview so you always know what is shared.
- **Your machine, your choice.** Local-only and bring-your-own-key paths are
  first-class; nothing leaves your machine unless you choose a cloud provider.

## Still to come in the 2.0 line

In the interest of honesty, these are built at the engine level but not yet wired
into the everyday UI, or are deliberately staged as later work:

- **The AI Hub as a command center** — a single home with Home, Agents, Chat,
  Sessions, Activity, Providers, Harnesses, Permissions, and Advanced views. The
  experimental opt-in above is the bridge until it lands.
- **One provider truth, fully consolidated** — converging the last second provider
  list so a single setting drives every surface.
- **Live validation of each SDK pack** against its installed vendor SDK, and a
  provider function-calling planner that lets the Native multi-step loop drive a
  cloud model directly.
- **Durable, resumable agent workflows** and an in-app **Agent Builder**.
