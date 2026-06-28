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
  the OpenAI Agents, Claude Agent, and GitHub Copilot SDK packs — that all drive the
  *same* safe editor tools.
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

## Setting up AI should feel wonderful

The first thing in the `&AI` menu is **Set Up AI** — a short, gentle, screen-reader-first
wizard that takes you from "I don't know where to start" to "my AI is ready" in
seconds, with no jargon and no dead ends. One welcome, one real choice (private
on-device with Ollama, an AI account, or not right now), one frictionless connect
step with a **Test connection** button, and a friendly "here's what you can do now."
QUILL even offers the wizard at the moment you first reach for AI — so you are never
stuck.

Finish it and you land in **Basic mode** by default: the AI menu stays small and
welcoming (Ask Quill, Transcribe, the everyday tools, the AI Library), with the
power-user agentic entries tucked away until you ask for them via **Show advanced AI
features**. Existing users keep the full menu — Basic mode only ever applies if you
choose it.

## One AI, one menu

QUILL's AI used to be scattered across a long Tools submenu and several overlapping
dialogs. 2.0 collapses all of it into one confident, top-level **`&AI` menu** built
on four pillars:

- **Ask Quill** — the one conversation. There is now a single, context-aware chat
  door; the old "Ask AI" and "Writing Assistant" chat dialogs have been retired into
  it, so there is no more guessing which one to open.
- **Do** — context-first actions. **"What can I do here?"** reads your document and
  offers the most useful next steps, and a **Rewrite & Improve** ring gives one-key
  transforms for the current selection. **Run Agent** lists the full catalog.
- **AI Library** — one place to manage **Prompts, Skills, and Agents** with the same
  verbs (Run, New, Edit, Import, Export) and a **Promote** path that grows a Prompt
  into a Skill and a Skill into an Agent. A guided **Build Action** lets anyone create
  their own AI action in plain language, with no syntax.
- **AI Hub** — one place to configure everything: provider, key, model, engine
  switching, GitHub Copilot setup, and your saved sessions, all in one tabbed window.

Choosing your provider and key in one place changes it everywhere — Ask Quill, the
inline tools, every agent, and the new Transcript Actions.

## One provider core, many engines

Today QUILL's AI lives behind two different provider systems. 2.0 unifies them so
that choosing your provider and key in the AI Hub changes it everywhere.

On top of that single core sits an optional **harness** layer. A harness is the
engine that drives an agent. QUILL ships a built-in **Native** harness that always
works. If you want the capabilities of a specific vendor SDK, you can install an
optional pack — QUILL focuses on the three that cover the field:

- **OpenAI Agents SDK** (`quill[ai-openai]`)
- **Claude Agent SDK** (`quill[ai-claude]`)
- **GitHub Copilot SDK** (`quill[ai-copilot]`)

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

## The Listening Companion — from sound to a finished document

QUILL 2.0 doesn't stop at turning audio into words. When a transcript is ready it
asks **"What would you like me to make of this?"** and offers a short, context-aware
list of **Transcript Actions** — and one keystroke turns the transcript into the
document you actually needed:

- **Meeting Minutes**, **Action Items**, **Executive Summary**, **Interview Notes**,
  **Study Notes**, **Q&A Extraction**, and **Clean Up & Draft**.

QUILL orders the list for the recording in front of you (a multi-speaker meeting
leads with Minutes; a single voice with Clean Up & Draft) and always opens the result
in a new window, so your transcript is never overwritten. The same actions are
reachable anytime from `AI > Transcribe Audio > Transcript Actions...` on whatever
text you are looking at.

Three things make this *yours*, not a fixed menu:

- **Build your own, in plain language.** The guided **Build Action** wizard
  (AI Library > Skills > Build Action) lets you name an action, start from an
  example, describe what you want in your own words, and save it as a real Skill —
  no syntax, ever. It is immediately runnable, adjustable, promotable to an Agent,
  and shareable.
- **Ground it in your template.** Attach a reference — an agenda, your house style,
  a past good example — and QUILL matches its format and terminology. "Make minutes
  that look like last month's."
- **Automate it.** A watch-folder transcribe profile can chain an action onto every
  arriving recording: drop a file in *Meetings*, get the transcript **and** the
  minutes written next to it, automatically, Do-Not-Disturb-aware, in the background.

Like everything else, it is optional, uses your configured provider, and degrades
gently — if AI is off you simply keep the transcript.

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
- An in-app **Agent Builder** for defining your own agents.
