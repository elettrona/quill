# Hey QUILL — Voice Interaction and Conversation Mode Plan

**Product:** QUILL
**Feature area:** Hands-free voice commands, wake word, conversation mode, sounders
**Status:** Plan of record (feature `core.voice_commands` stays `locked_off` until Phase 1 ships)
**Owner:** Jeff Bishop / QUILL project
**Reference implementation:** the ADP Assistant conversation mode (`s:\code\adp`, `src/adp_mcp/webapp/static/app.js`) — the "Hey Magic" loop whose state machine, sounders, and timing model this plan imports
**Last consolidated:** 2026-07-02

---

## 1. Executive summary

QUILL should let a user say **"Hey QUILL, save file"** — or arm a listening
session with one keystroke and just say **"save file"** — and have the right
command run, with every state of the interaction *audible*: a warm chime when
QUILL starts listening, a tick while it thinks, a sparkle when it acts, and a
spoken confirmation of what happened. Later, the same loop should carry
conversation: a question routes to Ask Quill, the answer is spoken, and a
follow-up window keeps listening so multi-turn exchanges work without
re-waking.

Two build-outs already exist in the codebase; neither is surfaced:

1. **Legacy Hey QUILL** (`quill/core/voice_commands.py`): wake-phrase parsing
   ("hey quill" / "quill"), number-word normalization, and alias generation
   from *every* registered command. Orphaned — it rode the removed Windows
   dictation stream. Disposition: **retire after Phase 1** (its wake-phrase
   parser is the one piece Phase 3 reuses).
2. **Offline Voice Command, "S5"** (`quill/core/speech/voice_commands.py` +
   `main_frame_speech.py` wiring): push-to-talk single-command capture on the
   shipped Whisper stack — implemented, tested, and wired; the Tools > Speech
   menu item is one commented-out `Append`. It has the right safety model
   (see §4) and is the foundation everything below builds on.

The plan: **unlock S5 (Phase 1), wrap it in the ADP conversation loop and
sounders (Phase 2), add the true wake word via a downloadable keyword spotter
(Phase 3), and route non-command utterances into Ask Quill (Phase 4).**

---

## 2. Current state (verified 2026-07-02)

| Piece | State |
|---|---|
| `core.voice_commands` feature | `locked_off=True`; menu item, settings entry ("Hey QUILL voice commands"), keymap entry, and F1 topic all exist and stay registered |
| S5 matcher (`core/speech/voice_commands.py`) | Done: allowlist catalog builder, hand-written aliases, cancel phrases (`cancel`, `never mind`, `stop`, `dismiss`), fuzzy scoring (exact=1.0, subsequence=0.9, token overlap ≥ 0.6), `VoiceOutcome` kinds `run/cancel/no_match/disabled` |
| S5 UI (`main_frame_speech.py`) | Done: `voice_command_toggle` start/stop capture, transcribe, `resolve_transcript`, dispatch through the command registry |
| Legacy wake parser (`core/voice_commands.py`) | Orphaned but useful: `extract_transcript_body` handles the "hey quill …" prefix |
| Always-on listening / wake word | **Does not exist** |
| Conversation states, sounders, follow-up | **Do not exist** |
| Plan | Was one roadmap sentence; this document replaces it |

---

## 3. Learnings imported from ADP (`s:\code\adp`)

The ADP Assistant's hands-free mode is the most polished accessible
conversation loop we have shipped anywhere. Import these wholesale:

### 3.1 The state machine

Six states, every transition both **announced** (text) and **sounded**
(earcon), with screen-reader detection choosing which channel leads:

```text
OFF -> IDLE ("say Hey QUILL") -> ARMED (listening) -> REVIEW (about to act,
cancel window) -> BUSY (thinking) -> SPEAKING (answering) -> back to ARMED
(follow-up window) or IDLE
```

QUILL mapping: the state lives in a wx-free
`quill/core/speech/conversation.py` controller (mirroring the
`DictationController` pattern: explicit states, single-recorder invariant,
watchdogs); the UI layer owns capture and `wx.CallAfter` marshaling.

### 3.2 The timing model (all user-tunable, WCAG-grounded)

- **Silence window** — how long a pause ends an utterance (WCAG 2.2.1
  adjustable timing). ADP default ~2 s; expose in Dictation Settings.
- **Review-and-cancel window** — after an utterance is captured, a short
  beat ("Submitting…") in which `Escape` or a cancel phrase aborts before
  anything runs. This is what makes "saying the wrong thing" recoverable.
- **Follow-up window** — after an answer/action, stay ARMED for ~7 s
  (0 = off) so a follow-up needs no re-wake. This single feature is what
  makes it feel like conversation instead of commands.
- **Thinking tick** — a quiet, periodic tone while work is in flight, with
  its own delay control and "Off" (WCAG 2.2.2 perceivable waiting).

### 3.3 The sounder palette (adopt as a QUILL earcon set)

ADP synthesizes warm bell tones (sine fundamental + a soft octave shimmer at
16 % amplitude, ~15 ms attack, long exponential decay, overlapping onsets) —
consonant musical intervals, deliberately not beeps. The palette, in Hz:

| Cue | Notes | Meaning |
|---|---|---|
| on | 523, 659, 784 (C–E–G rising) | conversation mode on — "hello" |
| off | 659, 523, 392 (falling) | mode off — "goodbye" |
| wake | 587, 880 (bright lift) | wake word heard — "I'm here" |
| listen | 523, 659 (soft, quieter) | mic open — "go ahead" |
| review | 659, 784 (gentle rise) | utterance captured — "got it" |
| ready | 659, 988 (sparkle) | action done / answer ready |
| idle | 440 (single, quiet) | relaxed back to idle |
| tick | 330 (short, very quiet) | still working |
| err | 392, 294 (low fall) | something's off — calm, not alarming |

QUILL implementation: generate these as a **"Conversation" group in the
sound-events system** (QUILL's default pack already uses synthesized bell
tones; add the nine events with the same synthesis recipe so custom sound
packs can override them like any other event). Locked Dictation's existing
earcons stay distinct.

### 3.4 The politeness details that make it feel magical

- **Screen-reader parity**: when an SR is active, prefer the earcon and skip
  the spoken duplicate (ADP: `if (sr) earcon("ready") else announce(...)`);
  QUILL's verbosity engine is the natural home for this decision.
- **Pre-warmed cue phrases**: the welcome and follow-up prompts are
  synthesized ahead of need so responses are instant.
- **Personalization**: "Hey Jeff! What can I look up?" — one optional name
  field; rotating prompt variants so it never sounds canned.
- **Barge-in discipline**: while a short cue phrase is playing, don't
  capture (or the assistant hears itself); ADP suppresses starts during
  SPEAKING and retries capture on transient errors with a bounded counter.
- **Mic-live perceivability**: the current state is always visible in the
  status bar *and* queryable ("Speak Status" answers "Listening" /
  "Thinking…"), never inferable only from memory of a chime.

### 3.5 What does NOT port

ADP's always-on listening rides the **browser's** continuous
`SpeechRecognition`. Desktop QUILL has no free equivalent; Phase 3 needs a
real on-device keyword spotter (§6.3). Everything else ports.

---

## 4. Command scope and the safety model

The commands voice can invoke are exactly the **agent safe-tool allowlist**
(`quill.core.ai.agent.SAFE_TOOL_IDS`, 24 ids today): save/save all/new,
undo/redo/select all, bold/italic/case transforms, bullet/numbered lists,
word count, spell check, read-aloud start/pause/stop, heading navigation,
outline, find, soft wrap, and the command palette — each with hand-written
spoken aliases in `_ALIASES`.

Policy (unchanged from S5, restated as law):

1. Voice reaches **only** the allowlist — never arbitrary registry commands.
2. Additions to the allowlist require: non-destructive, idempotent-or-
   undoable in one step, and a spoken alias set reviewed for confusability.
3. Destructive or outward-facing actions (close without save, send, publish,
   delete) are **never** voice-invokable in this plan's scope; if ever
   added, they require a spoken confirmation turn ("Say yes to close
   without saving").
4. Off by default, per-profile flag, **always off in Safe Mode**, and no
   network egress anywhere in the loop (transcription is on-device Whisper;
   Phase 4's Ask Quill routing inherits the AI consent posture unchanged).

Candidate allowlist expansions for Phase 2 (each needs the §4.2 review):
next/previous misspelling, next/previous bookmark, go to top/bottom,
open recent (spoken chooser), quiet mode toggle, "where am I" /
"what changed" status queries — the status queries are ideal voice targets
(read-only, high value hands-free).

---

## 5. Grammar

Phase 1–2 (armed listening): bare phrase — "save file", "next heading".
Phase 3 (wake word): "Hey QUILL, <phrase>" — reusing
`extract_transcript_body` semantics ("hey quill" and bare "quill" both wake;
wake-only utterances arm and wait with the *listen* sounder).
Always: cancel phrases abort; an unmatched phrase gets one spoken
"I heard <transcript> — no matching command" with the *err* sounder, never a
silent failure; two consecutive no-matches suggest the command palette.

---

## 6. Phases

### Phase 1 — Surface S5 (SHIPPED 2026-07-02)

Done: the Voice Command (Offline) menu item is live in Tools > Speech;
`core.voice_commands` is unlocked with an honest catalog description; the
settings label/F1 topic describe push-to-talk reality; the legacy
Windows-dictation-era module and its scanner machinery are retired, with
`extract_transcript_body` + `WAKE_PHRASES` preserved in
`quill/core/speech/voice_commands.py` for Phase 3; docs shipped (user guide,
CHANGELOG, release notes). The keymap entry stays unbound by default
(user-assignable); Phase 2 may propose a default chord alongside the
conversation loop.

### Phase 2 — The conversation loop + sounders (the ADP import)

`conversation.py` state controller (wx-free, unit-tested against a scripted
fake recorder/clock); the nine Conversation sound events; silence /
review-cancel / follow-up / thinking-tick settings in Dictation Settings;
status-bar state + Speak Status integration; verbosity-engine SR-parity
routing; pre-warmed cue phrases; optional name. Exit criteria: a full
arm -> speak -> review -> run -> follow-up -> second command exchange with
no keyboard after the arming keystroke, verified with NVDA and JAWS.

### Phase 3 — The wake word ("Hey QUILL" proper)

On-device keyword spotting, CPU-only, as a **verified downloadable
component** (assets-v1 pattern, SHA-256 pinned, Safe-Mode blocked):
evaluate **Vosk keyword mode** (already an optional QUILL engine — likely
winner) vs **openWakeWord** (ONNX; would need a trained "hey quill" model).
Requirements: mic-live is continuously perceivable (status-bar indicator +
optional periodic soft idle tone + Speak Status), one keystroke and one
spoken phrase ("stop listening") both kill it instantly, off across
restarts unless the user opts into persistence, and a false-accept rate
measured before ship (spot-check list of confusable phrases). Exit
criteria: "Hey QUILL, save file" from across the room, and a week of
dogfooding without a false wake during normal dictation or read-aloud.

### Phase 4 — Conversation (route to Ask Quill)

When an utterance matches no command and ends with a question shape (or the
user says "ask …"), route the transcript to Ask Quill; speak the answer via
the read-aloud stack; follow-up window keeps the thread. ADP's `brain.py`
model (LLM over a bounded toolset) maps to Ask Quill's existing document
context and reviewable-edit contract — voice never gains write powers the
keyboard flow doesn't have; proposed edits still land as the accept/reject
preview, announced. AI consent posture unchanged: if no AI is configured,
the router says so and stays a command listener.

---

## 7. Testing and gates

Wx-free controller: scripted state-machine tests (every transition, every
timer, cancel/barge-in paths) with injected clock — no real audio in unit
tests. Matcher: confusability suite (each alias must not fuzzy-match another
command's alias at ≥ threshold). UI: source-contract + fake-host behavior
tests per house pattern. Gates: no new egress entries (Phases 1–3 are fully
local); dialog contract for the settings surface; module budgets; the
allowlist⊆SAFE_TOOL_IDS assertion stays. Manual matrix: NVDA + JAWS +
Narrator, with and without earcons, SR on/off parity.

## 8. Open questions

1. Wake-word engine choice (Vosk keyword vs openWakeWord) — needs a spike
   with false-accept measurements; decides Phase 3's component payload.
2. Should the follow-up window apply after *commands* (ADP applies it after
   answers)? Proposed: yes, but shorter default (3 s vs 7 s).
3. Whether Phase 4 speaks answers with the read-aloud voice or the
   announcement voice — proposed: read-aloud voice, it's the "content"
   channel.
4. Microphone arbitration with Locked Dictation: proposal — arming either
   surface suspends the other, states shown in both status surfaces.
