# The Listening Companion — bringing BITS Whisperer's magic into QUILL

**Status:** Vision / north-star design
**Date:** 2026-06-28
**Author:** Jeff (with Claude)
**Related:** [ai-menu-redesign-plan.md](ai-menu-redesign-plan.md), `roadmap-2.0.md`,
`s:\code\bw` (BITS Whisperer)

---

## 1. The dream

You drop a recording into QUILL — a staff meeting, a lecture, a doctor's visit, an
interview, a voice memo to yourself — and QUILL *listens with you*. It transcribes
faithfully, names the speakers, and then quietly asks: **"What would you like me to
make of this?"** You pick *Meeting Minutes*, or *Action Items for my team*, or *Study
notes in my own words*, or one you built yourself last week called *"Turn my rambling
into a clean blog draft."* Moments later there is a finished, well-structured
document in front of you — reviewed, editable, yours.

No syntax. No prompt engineering. No "now copy this into ChatGPT." Just a gentle,
guided path from sound to meaning to a document you can use — and, when you're ready,
the power to shape that path exactly to how *you* work.

That is the magic BITS Whisperer reached for, and QUILL is now the place to make it
whole: **transcription is not the finish line — it's the beginning of an agentic,
user-shaped writing experience.**

---

## 2. Principles (the feeling we are protecting)

- **Easy** — the default path is one choice and one keystroke. A first-timer succeeds
  on their first recording without reading anything.
- **Delightful** — it feels like a capable, warm collaborator, not a settings panel.
- **Guided** — every step explains itself and suggests the obvious next move.
- **Principled** — nothing leaves the machine without consent; every AI edit is
  preview-gated and undoable; transcripts are private by default.
- **Powerful** — under the friendly surface is the full agentic stack (tools,
  multi-step skills, any provider, automation).
- **Adjustable with instruction and prompt** — every experience is a piece of saved
  intent the user can read, tweak in plain language, save, and share.
- **Gentle for learners** — a Basic experience mode hides the machinery; users grow
  into the power on their own timeline.
- **Meets people where they are — and where they wish to become** — from "I just need
  the words" to "automate my whole weekly workflow," the same product carries them.

---

## 3. What BITS Whisperer already dreamed (the parts worth keeping)

From `s:\code\bw`, the magic to carry forward:

- **The AI Action Builder** (`ui/agent_builder_dialog.py`): a *form-based, no-syntax*
  builder where a user defines a post-transcription AI action — a name, plain-language
  instructions, a model, a few tools, attachments — and saves it. "Users don't need to
  know Markdown or metadata syntax." This is the soul of "users defining their own
  experience."
- **Starter presets** (`_INSTRUCTION_PRESETS`): Meeting Minutes, Action Items,
  Executive Summary, Interview Notes, Lecture Notes, Q&A Extraction, General Assistant
  — ready-made experiences that teach by example.
- **Transcript tools** (`_AVAILABLE_TOOLS`): `search_transcript`, `get_speakers`,
  `get_transcript_stats` — small agentic capabilities the action can call.
- **`AgentConfig`** (`core/copilot_service.py`): name, description, instructions,
  model, tools, temperature, max_tokens, a friendly **welcome_message**, and
  **attachments** (reference docs that ground the output — an agenda, a house style,
  a prior example). Saved as JSON, portable.
- **Automation & care** (`watch_folder.py`, `scheduler_service.py`, `dnd_monitor.py`):
  drop-folder and scheduled transcription that respects Focus Assist / Do Not Disturb.
- **Live + diarized listening** (`live_transcription.py`, `diarization.py`) and an
  **experience-mode first-run wizard** (Basic vs. Advanced).

## 4. What QUILL already has (the foundation is built)

QUILL is not starting from zero — the agentic and automation bones already exist:

- **The unified AI Library** (`ai_library_dialog.py`) over the **Prompt → Skill →
  Agent continuum** (`core.ai.library`), with **first-class user agents** now
  shipping (`agent_catalog.user_agents_dir` / `save_user_agent` / `load_full_catalog`)
  and a persistent **skills store** (`core.skill_store`).
- **The Safe Editor Tool Gateway** — every agentic edit is permission-brokered,
  diff-previewed, and one-step undoable. Principled power, already wired.
- **Ask Quill** — the one, context-aware conversation door.
- **Transcription + diarization** (`core/ai/transcription.py`, `diarization.py`) and a
  whole **watch-folder engine**: `watch_profiles`, `watch_profile_store`,
  `watch_actions`, `watch_transcribe`, `watch_queue`, `watch_service`, `watch_worker`,
  `publishing_schedule`.
- **The Concierge** ("What can I do here?") that already reads context and suggests
  the right next action.

**The insight:** BITS Whisperer's "AI Action templates" *are* QUILL Skills and Agents,
specialized for transcripts. We don't need a parallel system — we need to **teach the
AI Library to speak fluent transcript**, add the **guided builder** as a friendly front
door to the continuum we already have, and **connect the watch-folder to AI Actions** so
automation finishes the job.

---

## 5. The magical experiences

### 5.1 "What would you like me to make of this?" (the moment after transcription)

When a transcription completes (manual, live, or watch-folder), QUILL surfaces a warm,
single prompt with the most relevant **Transcript Actions** for this audio — generated
by the Concierge from the content (a meeting with many speakers → *Minutes* and *Action
Items* first; a lecture → *Study Notes*; one voice → *Clean Up & Draft*). One Enter
runs it through the gateway and opens the finished document, reviewed and editable.

### 5.2 Bundled Transcript Skills (teach by example)

Ship the BW presets as **bundled skills** in the AI Library, retuned for QUILL's
multi-step skill format: *Meeting Minutes*, *Action Items*, *Executive Summary*,
*Interview Notes*, *Lecture/Study Notes*, *Q&A Extraction*, *Clean Up & Draft*. They
appear in the Library's Skills tab — runnable, readable, **Promotable to Agents**, and
**adjustable** (open one, change "include attendees" to "include attendees and their
roles," save your own copy).

### 5.3 The guided Action Builder (users define their own experience)

A gentle, form-based **"Build an AI Action..."** wizard layered on the AI Library — the
direct descendant of BW's Agent Builder, but writing into QUILL's existing stores so it
inherits Run / Promote / Import / Export / Share for free:

- **Name** it ("My Monday standup notes").
- **Start from** a preset or a blank page.
- **Describe in plain language** what you want — that's the instruction. No metadata.
- **Attach references** (an agenda, your house style, a past good example) to ground it.
- **Pick tools** (find a topic, list speakers, count words) if it should reason.
- **Choose a model / tone** or leave it on Recommended.
- **Preview** on the current transcript, then **Save** — it becomes a Skill (or, with
  tools, a first-class user Agent via the catalog we just built).

The builder is the friendly face; the continuum underneath is the power. A user can
graduate their own prompt → skill → agent without ever seeing a file.

### 5.4 Reference attachments (grounding the magic)

Bring BW's `Attachment` idea into QUILL's context layer: a Transcript Action can carry
reference documents that are injected (consented, previewed) so the output matches *your*
agenda, *your* terminology, *your* template. "Make minutes that look like last month's."

### 5.5 Automation that meets people where they are

Wire the existing **watch-folder profiles** to **AI Actions**: a profile becomes "When a
recording lands in *Meetings/*, transcribe it, run *Meeting Minutes*, and save the doc
next to it" — DND-aware, background, announced gently when done. The user sets it up once
in plain language and their Tuesdays get quieter. Scheduled and recurring runs follow the
same model.

### 5.6 Live and diarized, still gentle

Live transcription with speaker labels feeds the same actions in near-real-time
("running action items as the meeting goes"), with the same one-keystroke,
screen-reader-first review at the end.

---

## 6. Accessibility is the magic, not a constraint

This audience is why the gentleness is non-negotiable. Every action announces its start
and result; every generated document is navigable by heading; the builder is fully
keyboard-driven with named fields and spoken help; the "what would you like me to make of
this?" moment is a single, clearly-labeled choice list, not a wall of options. Basic
experience mode keeps the surface tiny until the user reaches for more. The power is
always one keystroke away and never in the way.

---

## 7. Phased delivery (grounded, shippable)

- **Phase A — Transcript Actions as bundled skills.** Port the seven BW presets into
  QUILL skill packs; add the post-transcription "What would you like me to make of this?"
  Concierge moment over the existing transcription result path. *No new stores — reuses
  the AI Library + gateway.*
- **Phase B — The guided Action Builder.** A wx wizard that writes Skills / user Agents
  via `skill_store` / `save_user_agent`, with presets, plain-language instructions,
  preview, and Save. Inherits Run/Promote/Share automatically.
- **Phase C — Reference attachments.** Extend the context layer so an action can carry
  consented reference docs; surface "Attach a reference..." in the builder and at run.
- **Phase D — Automation.** Connect watch-folder profiles and the scheduler to AI
  Actions ("transcribe → run action → save"), DND-aware, with gentle completion
  announcements.
- **Phase E — Live & diarized actions.** Stream actions over live, diarized
  transcription; same review surface.
- **Phase F — Experience modes & onboarding.** A Basic/Guided first-run for the listening
  workflow; per-action welcome text; "grow into power" prompts.

Each phase ships independently and leaves a coherent, delightful product.

---

## 8. The north star, in one line

> **QUILL listens with you, understands who spoke and what mattered, and — guided by a
> few plain words from you — turns the sound into the exact document you needed, every
> time, for everyone.**

Dream big. This is buildable on what already exists — the foundation is laid, the
gateway is principled, the Library is unified. What remains is to make QUILL *listen*,
and to hand every user a gentle, powerful way to say what they wish to make.
