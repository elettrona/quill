# Agent Harnesses — Bring Your Own AI Agent to QUILL

**Product:** QUILL
**Feature area:** Agentic SDK harnesses (GitHub Copilot, Claude Agent, OpenAI Agents, …) as on-demand components
**Status:** Framework and three packs BUILT (PRD §8.1/§8.2/§18.5). This plan turns a strong foundation into a surfaced, magical, validated product experience.
**Owner:** Jeff Bishop / QUILL project
**Last consolidated:** 2026-07-03

---

## 1. The magic, in one breath

You already pay for an AI agent — GitHub Copilot, ChatGPT, or Claude. QUILL
should let you **turn that subscription into your writing agent** in three
speakable steps: pick the account you have, let QUILL fetch the connector on
demand, sign in with a short code — and now QUILL's agent runs on *your* plan,
with *your* models, at *no extra cost*. And because QUILL owns every edit, the
vendor's agent never touches your document directly: it proposes, QUILL reviews,
you accept — one undo away, always.

That is the promise. The engine to deliver it is largely built. What is missing
is the part that makes it *feel* magical: telling the story, lighting the last
wire (Copilot sign-in), and proving it on real accounts.

---

## 2. What already exists (verified 2026-07-03)

QUILL has a real **harness layer** — interchangeable agent engines above the AI
backend — and it is clean, wx-free, and gate-tested.

| Piece | State |
|---|---|
| Harness protocol + capability model + registry (`quill/core/ai/harness/`) | Built. Every harness declares capabilities; the Hub hides what a harness can't do. |
| **Native harness** (QUILL's own agent loop) | Built; the always-available default. |
| **GitHub Copilot** pack (`quill/ai_packs/copilot.py`, extra `ai-copilot`) | Built; text-only bridge; OAuth. |
| **Claude Agent** pack (`quill/ai_packs/claude.py`, extra `ai-claude`) | Built; text-only bridge (`allowed_tools=[]`). |
| **OpenAI Agents** pack (`quill/ai_packs/openai_agents.py`, extra `ai-openai`) | Built. |
| On-demand install planner (`quill/core/ai/sdk_install.py`) | Built; `pip install` the extra the first time a user picks that engine — never bundled. |
| Copilot device-flow sign-in (`quill/core/ai/copilot_auth.py`, AI-19) | Built; token in the OS secure store. **Needs a deploy-time OAuth client id.** |
| UI hook (`tools.copilot_onboarding`) | Wired. |

**The safety law is already enforced and must never change.** Every harness —
native or vendor SDK — drives the *same* `SafeEditorToolGateway` and
`PermissionBroker` and emits the *same* normalized `AgentEvent`s. The SDK packs
run the vendor agent **text-only** (`allowed_tools=[]`): the vendor's own
file-editing and shell tools are **denied**, and QUILL applies the produced text
through its reviewed gateway — diff preview, permission broker, one-step undo. A
vendor agent can *think*, but only QUILL can *touch the document*, and only with
your consent.

---

## 3. Why this matters — the value per harness

QUILL already talks to models directly (OpenAI, Claude, Gemini, OpenRouter,
Ollama) through the Native harness. The SDK harnesses add three things the
direct connections cannot:

1. **Use the subscription you already have.** A Copilot seat, a ChatGPT/OpenAI
   plan, a Claude subscription — drive QUILL's agent on it, no second API key,
   no per-token surprise on your card. For the millions who already pay for one
   of these, QUILL's agent becomes *free to run*.
2. **Vendor-grade orchestration, QUILL-grade safety.** The official SDKs bring
   the vendors' own planning and tool-loop machinery, tuned to their models —
   but constrained to QUILL's gateway, so they gain no powers QUILL's own agent
   lacks. Best of both: their brains, our guardrails.
3. **Interchangeable and on-demand.** Pick the one that matches your account;
   it installs itself; the base download stays lean; and SDK versions are never
   pinned to QUILL's release cadence.

**Who each is for:**
- **Copilot** — developers and technical writers who live in a Copilot seat.
- **OpenAI Agents** — ChatGPT/OpenAI plan holders; the broadest audience.
- **Claude Agent** — Claude subscribers and anyone who prefers Anthropic models.

---

## 4. The magical experience (target)

The flow QUILL should deliver, end to end, screen-reader-first:

1. **Discover.** In AI setup (and in Help → Download Optional Components), a
   plain sentence: *"Already have GitHub Copilot, ChatGPT, or Claude? Use it as
   your QUILL agent — no extra cost."* Each option says what it needs and what
   it gives.
2. **Install on demand.** Pick one. QUILL says *"This adds the Copilot
   connector (about N MB). Install it now?"*, runs the pip install behind a
   cancelable progress bar (Safe-Mode-blocked), and the pack self-registers on
   the next probe — no restart.
3. **Sign in, spoken.** For Copilot, the OAuth **device flow**: QUILL reads a
   short code aloud and opens the browser page; you type the code; QUILL polls
   and stores the token in the OS secure store. For OpenAI/Claude, the existing
   key/consent surface. Either way, one clear success announcement.
4. **Run — reviewed.** Ask Quill and the agents now run on your chosen harness.
   Every proposed change lands as an accessible accept/reject preview and a
   single undo step, exactly as today. A status line names the active harness
   ("Agent: GitHub Copilot").
5. **Switch freely.** A quick-switch (already scaffolded in
   `ai/quick_switch.py`) lets you change harness per task without re-setup.

The magic is that steps 1–3 happen *inside QUILL*, in seconds, by ear — and
step 4 is unchanged from the safety users already trust.

---

## 5. What to build — gaps between "engine" and "experience"

The foundation is done. This is the finishing that makes it real and magical.

### Phase 1 — Light the last wire (Copilot sign-in)
Register a production **GitHub OAuth App**, decide how its **client id** is
injected at build/deploy (`QUILL_GITHUB_CLIENT_ID`), and wire it so
`copilot_auth.is_configured()` is true in shipped builds. Until then the clean
device-flow path is dormant and users fall back to the SDK CLI. Exit criteria:
a real Copilot sign-in from a shipped build, by ear, end to end.

### Phase 2 — Surface the value
Onboarding copy, a **Download Optional Components** listing for the three packs
(with sizes and "uses your existing subscription" notes), a user-guide section,
and release-notes framing. Nothing here is code-deep; it is the story the built
engine has been missing. Exit criteria: a new user who owns a Copilot seat can
*discover and reach* the feature without being told it exists.

### Phase 3 — Prove it on real accounts
A validation matrix run against live subscriptions: Copilot (OAuth + BYOK),
OpenAI Agents, Claude Agent — each through Ask Quill and at least one Agent
Center profile, confirming the text-only/reviewed-edit contract holds and every
event surfaces accessibly. Document results in a quality ledger. This needs a
human with the accounts; no automated test substitutes.

### Phase 4 — Breadth on demand (optional, later)
The registry already anticipates more engines (Microsoft Agent Framework,
LangGraph, OpenHands). Add them only when there is a real audience, each behind
its own extra, each text-only through the same gateway. No new safety surface.

---

## 6. The safety law (non-negotiable, already true)

- **QUILL owns every edit.** SDK harnesses run text-only; the vendor agent's own
  mutating tools are denied. QUILL applies text through the reviewed Safe Editor
  Tool Gateway — permission broker, diff preview, one-step undo.
- **Same events, same review, every harness.** Native or vendor, the user sees
  the identical accessible accept/reject flow.
- **Consent and Safe Mode.** On-demand installs and network calls are explicit,
  cancelable, and blocked in Safe Mode. Tokens live in the OS secure store.
- **No capability assumptions.** The Hub hides what a harness cannot do rather
  than presenting a broken control.

---

## 7. Open questions

1. **GitHub OAuth App ownership** — who registers it, and how is the client id
   provisioned into official builds vs. source builds (env at CI/deploy)?
2. **Optional-components placement** — do the SDK packs belong in the unified
   Download Optional Components dialog, the AI setup flow, or both (cross-linked)?
3. **Discovery without account detection** — QUILL can't see a user's Copilot
   seat; how prominent should the "bring your subscription" prompt be without
   nagging users who have no such account?
4. **Pack sizes** — measure each extra's install footprint to set honest
   size hints in the download prompts.
5. **Model/plan limits** — surface a harness's rate/plan limits gracefully
   (mirror the free-model honesty already in the provider path).
