# QUILL 2.0 — Plan of Record (scope anchor)

> **What this is.** The single planning document for QUILL 2.0. It exists to
> *anchor scope* — to hold the work that was consciously deferred out of 1.0 so the
> intent is not lost — not to schedule it. Nothing here is committed for a date.
> When a 2.0 item is picked up, it graduates into the active 1.0-style ledger
> (`roadmap.md`) for the release that ships it and leaves this file.
>
> **Relationship to 1.0.** 1.0 is the plan of record in
> [`roadmap.md`](roadmap.md) and remains the priority. This file is the downstream
> backlog: every row here traces back to a "defer to 2.0" decision already recorded
> in `roadmap.md` §5 or the large in-flight specs. Do not add net-new ambition here
> without first deciding it is genuinely post-1.0.
>
> **Branch.** 2.0 work lives on the `2.0-dev` branch (worktree at `S:\QUILL-2.0`).
> Pull shipping fixes forward with `git merge main`; do not merge `2.0-dev` back
> into `main` until 2.0 is ready to ship.

**Created:** 2026-06-25.

---

## 0. Principles carried forward

The 2.0 bar is the 1.0 bar. Every item below must, when built:

- Be **screen-reader-first** and keyboard-clear — simplicity for the SR user is king.
- Be **optional and off by default**; QUILL owns the editor, focus, undo, and
  announcements, and no integration may weaken that.
- Land on QUILL's invariants: atomic storage, the dialog contract, the announcement
  grammar, Safe Mode, and the network-egress audit.
- Honour platform scope: Windows (primary), macOS (supported); Linux/Unix is not a
  target and carries no forward promise.

Anything that cannot clear that bar does not ship, regardless of which list it sits
on below.

---

## 1. Workstreams (deferred from 1.0)

Each row is confirmed out of 1.0 and recorded so the intent survives. Canonical
design, where it exists, is linked — this file does not duplicate it.

### 1.1 Dictation — later phases

Optional **global Windows key hook** (system-wide dictation hotkey),
**idle-silence detection** (auto-stop on a pause), and **dictation intelligence**
(spoken punctuation / commands). Each is a sizable capability beyond the
keyboard-only Hold/Locked dictation that already shipped in 1.0.

### 1.2 BITS Whisperer consolidation backlog (#515, #566–#577)

The broader provider-matrix tiers and guided onboarding (BW-1..10 / WATCH-8). A
large workstream, already tagged 2.0-deferred in the program history.

### 1.3 Accessibility tooling from GLOW (#528–#534, #566)

Document Audit (ACB Large-Print Guidelines, Microsoft Accessibility Checker,
WCAG 2.2 AA) and the GLOW family, re-homed on QUILL's invariants. Contributions
stay `locked_off` until built. QUILL takes the **authoring-time checks** only;
GLOW's server / Keycloak / Office-add-in / MCP-deployment surfaces stay in the GLOW
product. Source: `s:\code\glow` (`glowplan.md`).

### 1.4 ElevenLabs beyond export TTS

The 1.0 slice is export-only cloud TTS. Deferred here: live Read-Aloud
**streaming** + continuous-consent model, **voice management / cloning / design /
server-side pronunciation dictionaries**, and the Tier-3 **SFX / voice-changer /
history** surfaces. Full reasoning in [`eleven-labs.md`](eleven-labs.md).

### 1.5 Native Google Docs support

Read / write / round-trip Google Docs from within QUILL (Drive API, OAuth,
accessible doc model). A full external-service + auth + sync workstream. Spec:
[`QUILL-Native-Google-Docs-Support-PRD.md`](QUILL-Native-Google-Docs-Support-PRD.md).

### 1.6 Direct publishing (#140)

Publish a finished document / audiobook to WordPress and other platforms. Long-term,
likely a **Quillin** integration (external-API + auth surface), not core editor work.
Early design in `docs/design/publishing/`.

### 1.7 Remaining ChapterForge surfaces

Out of the 1.0 audiobook vision: Auphonic post-processing, RSS podcast feeds, SFTP
publishing, and MusicBrainz / Open Library metadata lookup.

### 1.8 Platform / packaging singletons (#680)

The Windows 11 modern primary-menu `IExplorerCommand` pass (SHELL-3, #525) and the
PyInstaller packaging-hardening evaluation (PKG-1, #599). Nuitka is explicitly out
of scope — too much risk, not reliable enough.

### 1.9 Large in-flight feature specs (not started)

These have their own specs and open work; they are 2.0-or-later unless promoted:

- [`quill-native-accessible-table-studio-plan.md`](quill-native-accessible-table-studio-plan.md)
  — Table Studio.
- [`quill_end_to_end_agentic_ai_prd.md`](quill_end_to_end_agentic_ai_prd.md)
  — end-to-end agentic AI platform.

---

## 2. Verbosity 2.0 polish backlog

The verbosity engine and its 1.0 surface shipped (see `roadmap.md` §1.1 and PRD
§5.91). What remains is the deferred polish-backlog long tail (addenda #405–#504).
The consolidated reference — valuable candidates, themed reference well, and the
"recommend do not build" list — lives in **`roadmap.md` §5, "Verbosity 2.0 polish
backlog"**. Build order if the range reopens:

1. Error coaching (#416).
2. Per-category announcement detail levels (#418).
3. Markdown-aware (#427) / Code-aware (#428) verbosity.
4. "Undo available" cues (#502) and richer destructive-action warnings (#501).
5. Boundary announcements (#419) and progress-announcement controls (#420).
6. Details-on-demand (#417) beyond the existing status-query commands.

The themed reference well (settings UX, packs, modes, privacy, output niceties,
localization) is speculative — build only on demand. The "recommend do not build"
items (Typing/Command Echo, Speech Rate/Pause knobs, Punctuation/Symbol Profiles)
stay rejected: the screen reader already owns those.

---

## 3. Working agreement for 2.0

- **One planning file.** This document plus the linked large specs. New 2.0 design
  goes into a dedicated spec under `docs/planning/` and is referenced here, not
  inlined.
- **Graduation, not accumulation.** When an item is scheduled, move it into
  `roadmap.md` for the shipping release and delete its row here.
- **Keep issue numbers.** They are how each idea stays findable across the move.
- **Stay current with main.** Merge `main` into `2.0-dev` regularly so 2.0 builds on
  the latest 1.0 fixes.
