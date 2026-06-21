# QUILL Roadmap — Consolidated Planning Archive (1.0 / 2.0)

> **Consolidated workstream design spec.** This file gathers the full text of
> every open issue in this workstream so the design reads end to end in one
> place. The issues remain **open and individually tracked** in
> [`program-tracker.md`](program-tracker.md); each closes as its
> implementation ships. Everything here is in scope to ship — issue numbers
> are preserved as section anchors.

This is the consolidated roadmap previously tracked as individual [Planning] issues: near-term opportunities (O1–O21), the GLOW family, the Tier-6 documentation/podcast/tutorial backlog, in-flight items, and the QUILL 2.0 deferred set.


## Triage summary (product judgment)

- **Near-term, real product value:** O1 live-installer smoke (#506), O5/O5b Ask-QUILL action buttons + unifying the two AI stacks (#507/#508 — overlaps the agentic-AI PRD in this folder), O6 AI Hub two-pane settings (#509), O7 decide Azure provider (#510), O10 Quick-Nav (#513), O11 un-gate structured Word/CSV (#514), O20 extract main_frame_statusbar (#521).
- **Strategic / larger:** GLOW family (#528–#534), macOS to shipping quality (#518), plugin signing + marketplace (#519), Linux layer (#520/#565/#589), native RTF editing (#516), Quillin Hub (#517).
- **Larger items, later waves (all shipping — the 2.0 framing is dropped):** the BITS Whisperer set (#566–#577) folds into the Speech & Dictation plan; AI-11/12/18 and FEAT-12–18 (#579–#588) and localization/collaboration/accessibility-agents (#590–#599) schedule into their buckets. The Tier-6 DOC/POD/TUT backlog (#535–#564) is content work scheduled per release wave.


## Contents (95 archived issues)

- [#505](#505-) — [Planning] QUILL 1.0 + 2.0 open roadmap (planning.md)
- [#506](#506-) — [Planning] O1 — Live installer smoke on Windows 10/11
- [#507](#507-) — [Planning] O5 — Ask QUILL per-message action buttons
- [#508](#508-) — [Planning] O5b — Unify the two AI stacks
- [#509](#509-) — [Planning] O6 — AI Hub = Settings-style two-pane
- [#510](#510-) — [Planning] O7 — Azure provider: implement or formally drop
- [#511](#511-) — [Planning] O8 — AI-19 GitHub Copilot SDK (deferred)
- [#512](#512-) — [Planning] O9 — SHELL-2 structured-OCR AI structuring pass
- [#513](#513-) — [Planning] O10 — Quick Nav enhancements
- [#514](#514-) — [Planning] O11 — Un-gate structured Word view + CSV grid
- [#515](#515-) — [Planning] O12 — BITS Whisperer transcription runtime (deferred)
- [#516](#516-) — [Planning] O13 — Native RTF editing
- [#517](#517-) — [Planning] O14 — Quillin Hub launch
- [#518](#518-) — [Planning] O15 — macOS port to shipping quality (#42)
- [#519](#519-) — [Planning] O16 — Plugin capability, signing, marketplace
- [#520](#520-) — [Planning] O17 — Linux platform layer
- [#521](#521-) — [Planning] O20 — Extract main_frame_statusbar.py
- [#522](#522-) — [Planning] O21 — Master backlog (per-tier backlog IDs)
- [#523](#523-) — [Planning] In flight: AI-19 GitHub Copilot SDK
- [#524](#524-) — [Planning] In flight: SHELL-2 OCR AI structuring
- [#525](#525-) — [Planning] In flight: SHELL-3 Windows 11 primary menu
- [#526](#526-) — [Planning] In flight: DLG-3.8 NVDA / JAWS / Narrator sign-off
- [#527](#527-) — [Planning] In flight: CQ-11 spell-check preload half
- [#528](#528-) — [Planning] Tier 2 / 1.0 GLOW family: GLOW-1
- [#529](#529-) — [Planning] Tier 2 / 1.0 GLOW family: GLOW-2
- [#530](#530-) — [Planning] Tier 2 / 1.0 GLOW family: GLOW-3
- [#531](#531-) — [Planning] Tier 2 / 1.0 GLOW family: GLOW-4
- [#532](#532-) — [Planning] Tier 2 / 1.0 GLOW family: GLOW-5
- [#533](#533-) — [Planning] Tier 2 / 1.0 GLOW family: GLOW-6
- [#534](#534-) — [Planning] Tier 2 / 1.0 GLOW family: GLOW-7
- [#535](#535-) — [Planning] Tier 6 / 1.0 backlog: DOC-1
- [#536](#536-) — [Planning] Tier 6 / 1.0 backlog: DOC-2
- [#537](#537-) — [Planning] Tier 6 / 1.0 backlog: DOC-3
- [#538](#538-) — [Planning] Tier 6 / 1.0 backlog: DOC-4
- [#539](#539-) — [Planning] Tier 6 / 1.0 backlog: DOC-5
- [#540](#540-) — [Planning] Tier 6 / 1.0 backlog: DOC-6
- [#541](#541-) — [Planning] Tier 6 / 1.0 backlog: DOC-7
- [#542](#542-) — [Planning] Tier 6 / 1.0 backlog: DOC-8
- [#543](#543-) — [Planning] Tier 6 / 1.0 backlog: DOC-11
- [#544](#544-) — [Planning] Tier 6 / 1.0 backlog: DOC-12
- [#545](#545-) — [Planning] Tier 6 / 1.0 backlog: DOC-14
- [#546](#546-) — [Planning] Tier 6 / 1.0 backlog: DOC-15
- [#547](#547-) — [Planning] Tier 6 / 1.0 backlog: DOC-16
- [#548](#548-) — [Planning] Tier 6 / 1.0 backlog: DOC-17
- [#549](#549-) — [Planning] Tier 6 / 1.0 backlog: DOC-18
- [#550](#550-) — [Planning] Tier 6 / 1.0 backlog: POD-1
- [#551](#551-) — [Planning] Tier 6 / 1.0 backlog: POD-2
- [#552](#552-) — [Planning] Tier 6 / 1.0 backlog: POD-3
- [#553](#553-) — [Planning] Tier 6 / 1.0 backlog: POD-4
- [#554](#554-) — [Planning] Tier 6 / 1.0 backlog: POD-5
- [#555](#555-) — [Planning] Tier 6 / 1.0 backlog: TUT-1
- [#556](#556-) — [Planning] Tier 6 / 1.0 backlog: TUT-2
- [#557](#557-) — [Planning] Tier 6 / 1.0 backlog: TUT-3
- [#558](#558-) — [Planning] Tier 6 / 1.0 backlog: TUT-4
- [#559](#559-) — [Planning] Tier 6 / 1.0 backlog: TUT-5
- [#560](#560-) — [Planning] Tier 6 / 1.0 backlog: TUT-6
- [#561](#561-) — [Planning] Tier 6 / 1.0 backlog: TUT-7
- [#562](#562-) — [Planning] Tier 6 / 1.0 backlog: CQ-14
- [#563](#563-) — [Planning] Tier 6 / 1.0 backlog: CQ-23
- [#564](#564-) — [Planning] Tier 6 / 1.0 backlog: CQ-24
- [#565](#565-) — [Planning] Tier 6 / 1.0 backlog: LINUX-2
- [#566](#566-) — [Planning] QUILL 2.0 deferred: WATCH-8 — GLOW watch action — deferred to QUILL 2.0
- [#567](#567-) — [Planning] QUILL 2.0 deferred: BW-1 — BITS Whisperer BW-1 — deferred to QUILL 2.0
- [#568](#568-) — [Planning] QUILL 2.0 deferred: BW-2 — BITS Whisperer BW-2 — deferred to QUILL 2.0
- [#569](#569-) — [Planning] QUILL 2.0 deferred: BW-3 — BITS Whisperer BW-3 — deferred to QUILL 2.0
- [#570](#570-) — [Planning] QUILL 2.0 deferred: BW-4 — BITS Whisperer BW-4 — deferred to QUILL 2.0
- [#571](#571-) — [Planning] QUILL 2.0 deferred: BW-5 — BITS Whisperer BW-5 — deferred to QUILL 2.0
- [#572](#572-) — [Planning] QUILL 2.0 deferred: BW-6 — BITS Whisperer BW-6 — deferred to QUILL 2.0
- [#573](#573-) — [Planning] QUILL 2.0 deferred: BW-7 — BITS Whisperer BW-7 — deferred to QUILL 2.0
- [#574](#574-) — [Planning] QUILL 2.0 deferred: BW-8 — BITS Whisperer BW-8 — deferred to QUILL 2.0
- [#575](#575-) — [Planning] QUILL 2.0 deferred: BW-9 — BITS Whisperer BW-9 — deferred to QUILL 2.0
- [#576](#576-) — [Planning] QUILL 2.0 deferred: BW-10 — BITS Whisperer BW-10 — deferred to QUILL 2.0
- [#577](#577-) — [Planning] QUILL 2.0 deferred: WATCH-9 — BITS Whisperer WATCH-9 — deferred to QUILL 2.0
- [#578](#578-) — [Planning] QUILL 2.0 deferred: NAV-10 — Navigation NAV-10 — deferred to QUILL 2.0
- [#579](#579-) — [Planning] QUILL 2.0 deferred: AI-11 — AI AI-11 — deferred to QUILL 2.0
- [#580](#580-) — [Planning] QUILL 2.0 deferred: AI-12 — AI AI-12 — deferred to QUILL 2.0
- [#581](#581-) — [Planning] QUILL 2.0 deferred: AI-18 — AI AI-18 — deferred to QUILL 2.0
- [#582](#582-) — [Planning] QUILL 2.0 deferred: FEAT-12 — Feature FEAT-12 — deferred to QUILL 2.0
- [#583](#583-) — [Planning] QUILL 2.0 deferred: FEAT-13 — Feature FEAT-13 — deferred to QUILL 2.0
- [#584](#584-) — [Planning] QUILL 2.0 deferred: FEAT-14 — Feature FEAT-14 — deferred to QUILL 2.0
- [#585](#585-) — [Planning] QUILL 2.0 deferred: FEAT-15 — Feature FEAT-15 — deferred to QUILL 2.0
- [#586](#586-) — [Planning] QUILL 2.0 deferred: FEAT-16 — Feature FEAT-16 — deferred to QUILL 2.0
- [#587](#587-) — [Planning] QUILL 2.0 deferred: FEAT-17 — Feature FEAT-17 — deferred to QUILL 2.0
- [#588](#588-) — [Planning] QUILL 2.0 deferred: FEAT-18 — Feature FEAT-18 — deferred to QUILL 2.0
- [#589](#589-) — [Planning] QUILL 2.0 deferred: LINUX-1 — LINUX-1 spike — deferred to QUILL 2.0
- [#590](#590-) — [Planning] QUILL 2.0 deferred: ECO-1 — Ecosystem ECO-1 — deferred to QUILL 2.0
- [#591](#591-) — [Planning] QUILL 2.0 deferred: L10N-1 — Localization L10N-1 — deferred to QUILL 2.0
- [#592](#592-) — [Planning] QUILL 2.0 deferred: COLLAB-1 — Collaboration COLLAB-1 — deferred to QUILL 2.0
- [#593](#593-) — [Planning] QUILL 2.0 deferred: AX-A — Accessibility Agents AX-A — deferred to QUILL 2.0
- [#594](#594-) — [Planning] QUILL 2.0 deferred: AX-B — Accessibility Agents AX-B — deferred to QUILL 2.0
- [#595](#595-) — [Planning] QUILL 2.0 deferred: AX-C — Accessibility Agents AX-C — deferred to QUILL 2.0
- [#596](#596-) — [Planning] QUILL 2.0 deferred: AX-D — Accessibility Agents AX-D — deferred to QUILL 2.0
- [#597](#597-) — [Planning] QUILL 2.0 deferred: AX-E — Accessibility Agents AX-E — deferred to QUILL 2.0
- [#598](#598-) — [Planning] QUILL 2.0 deferred: AX-F — Accessibility Agents AX-F — deferred to QUILL 2.0
- [#599](#599-) — [Planning] QUILL 2.0 deferred: PKG-1 — Packaging freezing evaluation PKG-1 — deferred to QUILL 2.0



---

## #505 — [Planning] QUILL 1.0 + 2.0 open roadmap (planning.md)

**Labels:** documentation, p2

Parent tracker for all open work captured in `docs/planning/planning.md`.

The full content of planning.md is now distributed across child issues (this is the planned retirement of the planning folder). Each child issue carries the full text and acceptance for its scope.

### Children

Open roadmap:

- O1, O5, O5b, O6, O7, O8, O9 (P0 / P1)
- O10, O11, O12, O13, O14, O15, O16, O17 (P2)
- O20, O21 (P3)

In flight (honestly blocked):

- AI-19, SHELL-2, SHELL-3, DLG-3.8, CQ-11

1.0 Tier 6 backlog:

- DLG-3.8, DOC-1..8, DOC-11, DOC-12, DOC-14..18, POD-1..5, TUT-1..7, CQ-11, CQ-14, CQ-23, CQ-24, LINUX-2

2.0 deferred:

- WATCH-8, BW-1..10, WATCH-9, NAV-10, AI-11, AI-12, AI-18, FEAT-12..18, LINUX-1, ECO-1, L10N-1, COLLAB-1, AX-A..F, PKG-1

This issue is closed when `docs/planning/planning.md` is deleted and every child listed above exists as a tracked issue.

### Acceptance

- Every child issue below is filed.
- `git ls-files docs/planning/` returns empty.



---

## #506 — [Planning] O1 — Live installer smoke on Windows 10/11

**Labels:** p0

Source: `docs/planning/planning.md` Open roadmap P0.

A one-time manual pass on a clean VM:

- Install
- Start-menu launch
- Open-With + Send-to-Quill verbs
- Uninstall data prompt

The classic Explorer menu is code-complete and drift-proof (`test_committed_installer_iss_is_in_sync_with_generator`, SHELL-1/SHELL-3 core work delivered). This is the live-Windows release-time verification that has to be done by a human on a real install.

### Acceptance

- Manual smoke log captured against a named build for 0.7.0.
- Open-With and Send-to-Quill verbs verified.
- Uninstall does not destroy user data without prompt.

### Closes

O1 of `docs/planning/planning.md`.



---

## #507 — [Planning] O5 — Ask QUILL per-message action buttons

**Labels:** ai, feature, p1

Source: `docs/planning/planning.md` Open roadmap P1.

Keep the HTML WebView chat (the user likes it). Add in-WebView per-message copy / insert / regenerate / delete controls. Limited by the external `wx_accessible-webview` component; today granularity is last-response vs whole transcript. Also: model dropdown populated from the provider instead of the free-text model field.

### Acceptance

- Per-message Copy / Insert / Regenerate / Delete buttons render in WebView.
- Model dropdown lists provider-known models, not free-text.

### Closes

O5 of `docs/planning/planning.md`.



---

## #508 — [Planning] O5b — Unify the two AI stacks

**Labels:** ai, feature, p1

Source: `docs/planning/planning.md` Open roadmap P1.

The chat dialog uses `quill.core.ai_chat` (PROVIDERS + credential_store) while the AI Hub / connection dialog uses `quill.core.assistant_ai` (providers.py + per-provider keys). Unify so keys / models / defaults are shared, not duplicated. Partially done — `test_chat`, per-provider key storage, and `set_active_provider` shipped in 0.6.0.

### Acceptance

- One provider list shared between chat and AI Hub.
- One key storage surface.
- `set_active_provider` is the single mutator.

### Closes

O5b of `docs/planning/planning.md`.



---

## #509 — [Planning] O6 — AI Hub = Settings-style two-pane

**Labels:** ai, feature, p1

Source: `docs/planning/planning.md` Open roadmap P1.

Today `AI Hub` opens a provider-dropdown config dialog. The richer design:

- Left = every provider (Ollama local, Ollama Cloud, OpenAI, Claude, OpenRouter, Gemini, custom).
- Right = that provider's config (host, API key, default model, a `List models` picker, `Test Chat`, `Make active`).

Merge `AI Model and Connection` (on-device model tiers) as its own left-pane entry. Every provider's key / model persists independently.

### Acceptance

- Two-pane layout per spec.
- All seven providers surfaced (or formally dropped via O7).
- Per-provider key + model persists independently.

### Closes

O6 of `docs/planning/planning.md`.



---

## #510 — [Planning] O7 — Azure provider: implement or formally drop

**Labels:** ai, feature, p1

Source: `docs/planning/planning.md` Open roadmap P1.

The chat backend parses `azure` deltas (`quill/core/assistant_ai.py:1201`); Azure is not in `settings_specs.py` or the setup wizard. Either surface it in the AI Hub alongside the others, or remove the code path. Docs already accurate.

### Acceptance

- Decision made: keep Azure or remove it.
- If kept: settings_specs.py has Azure; setup wizard offers it.
- If removed: no `azure` parser remains in assistant_ai.py.

### Closes

O7 of `docs/planning/planning.md`.



---

## #511 — [Planning] O8 — AI-19 GitHub Copilot SDK (deferred)

**Labels:** ai, p1

Source: `docs/planning/planning.md` Open roadmap P1.

AI-19 (GitHub Copilot SDK) was deferred from 0.5.0. Needs a live provider device-login endpoint that cannot ship from this environment; remains honestly blocked.

### Acceptance

- Re-evaluation per release with the maintainer. Either ship (if endpoint reachable) or keep documented as honestly blocked.

### Closes

O8 / AI-19 of `docs/planning/planning.md`.



---

## #512 — [Planning] O9 — SHELL-2 structured-OCR AI structuring pass

**Labels:** ai, feature, p1

Source: `docs/planning/planning.md` Open roadmap P1.

Code shipped (`_apply_ocr_structuring`, `structure` operation); the live-key end-to-end verification and structuring-quality tuning on real-world OCR output remain. Needs a configured/available assistant backend and tuning against multi-column PDFs, tables, headers/footers.

### Acceptance

- End-to-end test on a real OCR corpus.
- Tuning log against multi-column / table / header-footer samples.

### Closes

O9 / SHELL-2 of `docs/planning/planning.md`.



---

## #513 — [Planning] O10 — Quick Nav enhancements

**Labels:** feature, p2

Source: `docs/planning/planning.md` Open roadmap P2.

Quick Nav enhancements: live-count panel; table review; misspellings / search as nav types.

### Acceptance

- Live-count panel surfaces for the current document.
- Misspellings and search hits are listed as nav types.

### Closes

O10 of `docs/planning/planning.md`.



---

## #514 — [Planning] O11 — Un-gate structured Word view + CSV grid

**Labels:** feature, p2

Source: `docs/planning/planning.md` Open roadmap P2.

Un-gate structured Word view + CSV grid after validation.

### Acceptance

- Validation report attached.
- Gates removed.
- Tests cover Word view + CSV grid.

### Closes

O11 of `docs/planning/planning.md`.



---

## #515 — [Planning] O12 — BITS Whisperer transcription runtime (deferred)

**Labels:** feature, p2

Source: `docs/planning/planning.md` Open roadmap P2.

Three-tier providers (local / plus / enterprise), `quill/core/transcript.py` keystone, `bw_transcription.py` wrapper, IO JSON ↔ Markdown round-trip. Refs: BW-1, BW-9. Deferred from 1.0 by maintainer direction. Tracked under QUILL 2.0.

### Acceptance

- Re-evaluation per release. Ship only if maintainer re-prioritizes.

### Closes

O12 / BW-1 / BW-9 of `docs/planning/planning.md`.



---

## #516 — [Planning] O13 — Native RTF editing

**Labels:** feature, p2

Source: `docs/planning/planning.md` Open roadmap P2.

`core.rich_text_lens` is `locked_off` (always `"plain"`). RTF as a *format* is delivered as an io-layer round-trip. The rich-text lens is opt-in and read-only today (`RichTextSurface`); an editable rich surface with rich-native persistent undo remains open. Ref: RTF-22.

### Acceptance

- `RichTextSurface` is editable.
- Persistent undo across rich edits.

### Closes

O13 / RTF-22 of `docs/planning/planning.md`.



---

## #517 — [Planning] O14 — Quillin Hub launch

**Labels:** feature, p2

Source: `docs/planning/planning.md` Open roadmap P2.

Quillin Hub launch (`hub.quillforall.org`) — public distribution and review surface.

### Acceptance

- Public site live.
- Manifest + signing documented.

### Closes

O14 of `docs/planning/planning.md`.



---

## #518 — [Planning] O15 — macOS port to shipping quality (#42)

**Labels:** feature, p2

Source: `docs/planning/planning.md` Open roadmap P2.

Keychain persistence for API keys/tokens shipped (`38053a9`); the editor surface parity and live macOS smoke are the remaining work.

### Acceptance

- Editor surface parity tests pass.
- Live macOS smoke test log captured.

### Closes

O15 / #42 of `docs/planning/planning.md`.



---

## #519 — [Planning] O16 — Plugin capability, signing, marketplace

**Labels:** security, feature, p2

Source: `docs/planning/planning.md` Open roadmap P2.

A documented capability and signing model lets vetted third-party plugins load safely off the experimental flag (builds on SEC-8).

### Acceptance

- Capability model documented.
- Signing flow documented.
- Vetted third-party plugin can load off experimental flag.

### Closes

O16 of `docs/planning/planning.md`.



---

## #520 — [Planning] O17 — Linux platform layer

**Labels:** feature, p2

Source: `docs/planning/planning.md` Open roadmap P2.

LINUX-1 (spike) and LINUX-2 (platform layer to product quality). Spike assesses an accessible Linux path.

### Acceptance

- LINUX-1 spike complete.
- LINUX-2 platform layer reaches product quality.

### Closes

O17 / LINUX-1 / LINUX-2 of `docs/planning/planning.md`.



---

## #521 — [Planning] O20 — Extract main_frame_statusbar.py

**Labels:** p3

Source: `docs/planning/planning.md` Open roadmap P3.

Extract `main_frame_statusbar.py` to lower its budget below the rebaselined 540.

### Acceptance

- File line count below the rebaselined budget.
- Module size budget updated with `_rebaseline_<date>` comment.

### Closes

O20 of `docs/planning/planning.md`.



---

## #522 — [Planning] O21 — Master backlog (per-tier backlog IDs)

**Labels:** p3

Source: `docs/planning/planning.md` Open roadmap P3.

The per-tier backlog IDs listed in the Tier completion table below are the authoritative, tier-ordered list (AI-*, GLOW-*, BW-*, DLG-*, DOC-*, MENU-*, SET-*, etc.); this doc is the running narrative around them. Each open backlog ID is its own tracked child issue.

### Acceptance

- Every open tier ID has its own child issue filed.

### Closes

O21 of `docs/planning/planning.md`.



---

## #523 — [Planning] In flight: AI-19 GitHub Copilot SDK

**Labels:** ai, p1

Source: `docs/planning/planning.md` In-flight section.

AI-19 — the GitHub Copilot SDK provider. Code-ready behind the consented AI provider layer; live device-login endpoint verification requires a sandboxed Copilot account and is not available in this environment. Stays honestly blocked until that endpoint is reachable.

### Acceptance

- Document the blocker in the release notes.
- Re-evaluate per release.

### Closes

AI-19 of `docs/planning/planning.md`.



---

## #524 — [Planning] In flight: SHELL-2 OCR AI structuring

**Labels:** ai, p1

Source: `docs/planning/planning.md` In-flight section.

SHELL-2 — the AI structuring pass for the structured-OCR verb. Worker wiring and prompt shipped; structuring *quality* on real-world OCR output (multi-column PDFs, tables, headers/footers) needs tuning against live model responses and an off-thread assistant call to confirm thread-safety and latency under the progress dialog. Needs a configured/available assistant backend.

### Acceptance

- Quality tuning log captured.
- Thread-safety under progress dialog confirmed.

### Closes

SHELL-2 of `docs/planning/planning.md`.



---

## #525 — [Planning] In flight: SHELL-3 Windows 11 primary menu

**Labels:** p1

Source: `docs/planning/planning.md` In-flight section.

SHELL-3 — the Windows 11 *primary*-menu `IExplorerCommand` sparse-package. The classic Explorer menu shipped; the modern-menu packaging is descoped to QUILL 2.0 (the OS gates it behind compiled COM + package identity). The macOS Finder verb (#115) stays blocked on the macOS port (#42, O15).

### Acceptance

- Maintainer direction recorded.

### Closes

SHELL-3 of `docs/planning/planning.md`.



---

## #526 — [Planning] In flight: DLG-3.8 NVDA / JAWS / Narrator sign-off

**Labels:** accessibility, p1

Source: `docs/planning/planning.md` In-flight section.

DLG-3.8 — the manual NVDA / JAWS / Narrator sign-off across `dialogs.md`. Owned by the maintainer, executed against `docs/qa/final-qa-test-plan.md` (§6 dialog estate pass). Needs a live Windows screen-reader runtime and human listening. Honest open until the pass is logged against a single named build.

### Acceptance

- Pass log captured against a single named build.
- All three screen readers verified.

### Closes

DLG-3.8 of `docs/planning/planning.md`.



---

## #527 — [Planning] In flight: CQ-11 spell-check preload half

**Labels:** p1

Source: `docs/planning/planning.md` In-flight section.

CQ-11 (spell-check preload half) — the tier-fallback half shipped in 0.5.0 (`test_spellcheck_backend.py`); the background-preload half stays open until a spell-check preload API exists (tracked by PERF-1).

### Acceptance

- Background-preload implemented.
- OR maintainer direction to drop.

### Closes

CQ-11 of `docs/planning/planning.md`.



---

## #528 — [Planning] Tier 2 / 1.0 GLOW family: GLOW-1

**Labels:** accessibility, feature, p1

Source: `docs/planning/planning.md` Tier completion table.

GLOW-1 is one of the seven GLOW-family items (GLOW-1 through GLOW-7) that returned from QUILL 2.0 into the **1.0** milestone on 2026-06-03 once the shared `quill-glow-core` engine requirements were met (the engine is green). The seven items are classified under **Tier 2** and sequenced for execution after Tier 4.

### Acceptance

- Item implemented per its GLOW-family design.
- Permission and consent flow preserved.
- Tests cover the user-visible behavior.

### Closes

GLOW-1 of `docs/planning/planning.md`.



---

## #529 — [Planning] Tier 2 / 1.0 GLOW family: GLOW-2

**Labels:** accessibility, feature, p1

Source: `docs/planning/planning.md` Tier completion table.

GLOW-2 is one of the seven GLOW-family items (GLOW-1 through GLOW-7) that returned from QUILL 2.0 into the **1.0** milestone on 2026-06-03 once the shared `quill-glow-core` engine requirements were met (the engine is green). The seven items are classified under **Tier 2** and sequenced for execution after Tier 4.

### Acceptance

- Item implemented per its GLOW-family design.
- Permission and consent flow preserved.
- Tests cover the user-visible behavior.

### Closes

GLOW-2 of `docs/planning/planning.md`.



---

## #530 — [Planning] Tier 2 / 1.0 GLOW family: GLOW-3

**Labels:** accessibility, feature, p1

Source: `docs/planning/planning.md` Tier completion table.

GLOW-3 is one of the seven GLOW-family items (GLOW-1 through GLOW-7) that returned from QUILL 2.0 into the **1.0** milestone on 2026-06-03 once the shared `quill-glow-core` engine requirements were met (the engine is green). The seven items are classified under **Tier 2** and sequenced for execution after Tier 4.

### Acceptance

- Item implemented per its GLOW-family design.
- Permission and consent flow preserved.
- Tests cover the user-visible behavior.

### Closes

GLOW-3 of `docs/planning/planning.md`.



---

## #531 — [Planning] Tier 2 / 1.0 GLOW family: GLOW-4

**Labels:** accessibility, feature, p1

Source: `docs/planning/planning.md` Tier completion table.

GLOW-4 is one of the seven GLOW-family items (GLOW-1 through GLOW-7) that returned from QUILL 2.0 into the **1.0** milestone on 2026-06-03 once the shared `quill-glow-core` engine requirements were met (the engine is green). The seven items are classified under **Tier 2** and sequenced for execution after Tier 4.

### Acceptance

- Item implemented per its GLOW-family design.
- Permission and consent flow preserved.
- Tests cover the user-visible behavior.

### Closes

GLOW-4 of `docs/planning/planning.md`.



---

## #532 — [Planning] Tier 2 / 1.0 GLOW family: GLOW-5

**Labels:** accessibility, feature, p1

Source: `docs/planning/planning.md` Tier completion table.

GLOW-5 is one of the seven GLOW-family items (GLOW-1 through GLOW-7) that returned from QUILL 2.0 into the **1.0** milestone on 2026-06-03 once the shared `quill-glow-core` engine requirements were met (the engine is green). The seven items are classified under **Tier 2** and sequenced for execution after Tier 4.

### Acceptance

- Item implemented per its GLOW-family design.
- Permission and consent flow preserved.
- Tests cover the user-visible behavior.

### Closes

GLOW-5 of `docs/planning/planning.md`.



---

## #533 — [Planning] Tier 2 / 1.0 GLOW family: GLOW-6

**Labels:** accessibility, feature, p1

Source: `docs/planning/planning.md` Tier completion table.

GLOW-6 is one of the seven GLOW-family items (GLOW-1 through GLOW-7) that returned from QUILL 2.0 into the **1.0** milestone on 2026-06-03 once the shared `quill-glow-core` engine requirements were met (the engine is green). The seven items are classified under **Tier 2** and sequenced for execution after Tier 4.

### Acceptance

- Item implemented per its GLOW-family design.
- Permission and consent flow preserved.
- Tests cover the user-visible behavior.

### Closes

GLOW-6 of `docs/planning/planning.md`.



---

## #534 — [Planning] Tier 2 / 1.0 GLOW family: GLOW-7

**Labels:** accessibility, feature, p1

Source: `docs/planning/planning.md` Tier completion table.

GLOW-7 is one of the seven GLOW-family items (GLOW-1 through GLOW-7) that returned from QUILL 2.0 into the **1.0** milestone on 2026-06-03 once the shared `quill-glow-core` engine requirements were met (the engine is green). The seven items are classified under **Tier 2** and sequenced for execution after Tier 4.

### Acceptance

- Item implemented per its GLOW-family design.
- Permission and consent flow preserved.
- Tests cover the user-visible behavior.

### Closes

GLOW-7 of `docs/planning/planning.md`.



---

## #535 — [Planning] Tier 6 / 1.0 backlog: DOC-1

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-1 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-1 of `docs/planning/planning.md`.



---

## #536 — [Planning] Tier 6 / 1.0 backlog: DOC-2

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-2 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-2 of `docs/planning/planning.md`.



---

## #537 — [Planning] Tier 6 / 1.0 backlog: DOC-3

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-3 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-3 of `docs/planning/planning.md`.



---

## #538 — [Planning] Tier 6 / 1.0 backlog: DOC-4

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-4 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-4 of `docs/planning/planning.md`.



---

## #539 — [Planning] Tier 6 / 1.0 backlog: DOC-5

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-5 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-5 of `docs/planning/planning.md`.



---

## #540 — [Planning] Tier 6 / 1.0 backlog: DOC-6

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-6 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-6 of `docs/planning/planning.md`.



---

## #541 — [Planning] Tier 6 / 1.0 backlog: DOC-7

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-7 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-7 of `docs/planning/planning.md`.



---

## #542 — [Planning] Tier 6 / 1.0 backlog: DOC-8

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-8 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-8 of `docs/planning/planning.md`.



---

## #543 — [Planning] Tier 6 / 1.0 backlog: DOC-11

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-11 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-11 of `docs/planning/planning.md`.



---

## #544 — [Planning] Tier 6 / 1.0 backlog: DOC-12

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-12 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-12 of `docs/planning/planning.md`.



---

## #545 — [Planning] Tier 6 / 1.0 backlog: DOC-14

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-14 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-14 of `docs/planning/planning.md`.



---

## #546 — [Planning] Tier 6 / 1.0 backlog: DOC-15

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-15 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-15 of `docs/planning/planning.md`.



---

## #547 — [Planning] Tier 6 / 1.0 backlog: DOC-16

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-16 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-16 of `docs/planning/planning.md`.



---

## #548 — [Planning] Tier 6 / 1.0 backlog: DOC-17

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-17 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-17 of `docs/planning/planning.md`.



---

## #549 — [Planning] Tier 6 / 1.0 backlog: DOC-18

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

DOC-18 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

DOC-18 of `docs/planning/planning.md`.



---

## #550 — [Planning] Tier 6 / 1.0 backlog: POD-1

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

POD-1 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

POD-1 of `docs/planning/planning.md`.



---

## #551 — [Planning] Tier 6 / 1.0 backlog: POD-2

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

POD-2 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

POD-2 of `docs/planning/planning.md`.



---

## #552 — [Planning] Tier 6 / 1.0 backlog: POD-3

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

POD-3 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

POD-3 of `docs/planning/planning.md`.



---

## #553 — [Planning] Tier 6 / 1.0 backlog: POD-4

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

POD-4 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

POD-4 of `docs/planning/planning.md`.



---

## #554 — [Planning] Tier 6 / 1.0 backlog: POD-5

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

POD-5 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

POD-5 of `docs/planning/planning.md`.



---

## #555 — [Planning] Tier 6 / 1.0 backlog: TUT-1

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

TUT-1 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

TUT-1 of `docs/planning/planning.md`.



---

## #556 — [Planning] Tier 6 / 1.0 backlog: TUT-2

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

TUT-2 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

TUT-2 of `docs/planning/planning.md`.



---

## #557 — [Planning] Tier 6 / 1.0 backlog: TUT-3

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

TUT-3 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

TUT-3 of `docs/planning/planning.md`.



---

## #558 — [Planning] Tier 6 / 1.0 backlog: TUT-4

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

TUT-4 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

TUT-4 of `docs/planning/planning.md`.



---

## #559 — [Planning] Tier 6 / 1.0 backlog: TUT-5

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

TUT-5 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

TUT-5 of `docs/planning/planning.md`.



---

## #560 — [Planning] Tier 6 / 1.0 backlog: TUT-6

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

TUT-6 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

TUT-6 of `docs/planning/planning.md`.



---

## #561 — [Planning] Tier 6 / 1.0 backlog: TUT-7

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

TUT-7 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

TUT-7 of `docs/planning/planning.md`.



---

## #562 — [Planning] Tier 6 / 1.0 backlog: CQ-14

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

CQ-14 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

CQ-14 of `docs/planning/planning.md`.



---

## #563 — [Planning] Tier 6 / 1.0 backlog: CQ-23

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

CQ-23 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

CQ-23 of `docs/planning/planning.md`.



---

## #564 — [Planning] Tier 6 / 1.0 backlog: CQ-24

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

CQ-24 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

CQ-24 of `docs/planning/planning.md`.



---

## #565 — [Planning] Tier 6 / 1.0 backlog: LINUX-2

**Labels:** documentation, p2

Source: `docs/planning/planning.md` Tier completion table.

LINUX-2 is one of the 32 open Tier-6 / 1.0 backlog items (Documentation and learning surface). See the Tier completion table in planning.md for the canonical list and counts.

### Acceptance

- Item is resolved (implemented, dropped with maintainer direction, or reclassified to QUILL 2.0).

### Closes

LINUX-2 of `docs/planning/planning.md`.



---

## #566 — [Planning] QUILL 2.0 deferred: WATCH-8 — GLOW watch action — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

WATCH-8 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). GLOW watch action — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

WATCH-8 of `docs/planning/planning.md`.



---

## #567 — [Planning] QUILL 2.0 deferred: BW-1 — BITS Whisperer BW-1 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

BW-1 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). BITS Whisperer BW-1 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

BW-1 of `docs/planning/planning.md`.



---

## #568 — [Planning] QUILL 2.0 deferred: BW-2 — BITS Whisperer BW-2 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

BW-2 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). BITS Whisperer BW-2 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

BW-2 of `docs/planning/planning.md`.



---

## #569 — [Planning] QUILL 2.0 deferred: BW-3 — BITS Whisperer BW-3 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

BW-3 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). BITS Whisperer BW-3 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

BW-3 of `docs/planning/planning.md`.



---

## #570 — [Planning] QUILL 2.0 deferred: BW-4 — BITS Whisperer BW-4 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

BW-4 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). BITS Whisperer BW-4 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

BW-4 of `docs/planning/planning.md`.



---

## #571 — [Planning] QUILL 2.0 deferred: BW-5 — BITS Whisperer BW-5 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

BW-5 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). BITS Whisperer BW-5 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

BW-5 of `docs/planning/planning.md`.



---

## #572 — [Planning] QUILL 2.0 deferred: BW-6 — BITS Whisperer BW-6 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

BW-6 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). BITS Whisperer BW-6 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

BW-6 of `docs/planning/planning.md`.



---

## #573 — [Planning] QUILL 2.0 deferred: BW-7 — BITS Whisperer BW-7 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

BW-7 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). BITS Whisperer BW-7 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

BW-7 of `docs/planning/planning.md`.



---

## #574 — [Planning] QUILL 2.0 deferred: BW-8 — BITS Whisperer BW-8 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

BW-8 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). BITS Whisperer BW-8 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

BW-8 of `docs/planning/planning.md`.



---

## #575 — [Planning] QUILL 2.0 deferred: BW-9 — BITS Whisperer BW-9 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

BW-9 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). BITS Whisperer BW-9 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

BW-9 of `docs/planning/planning.md`.



---

## #576 — [Planning] QUILL 2.0 deferred: BW-10 — BITS Whisperer BW-10 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

BW-10 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). BITS Whisperer BW-10 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

BW-10 of `docs/planning/planning.md`.



---

## #577 — [Planning] QUILL 2.0 deferred: WATCH-9 — BITS Whisperer WATCH-9 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

WATCH-9 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). BITS Whisperer WATCH-9 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

WATCH-9 of `docs/planning/planning.md`.



---

## #578 — [Planning] QUILL 2.0 deferred: NAV-10 — Navigation NAV-10 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

NAV-10 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Navigation NAV-10 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

NAV-10 of `docs/planning/planning.md`.



---

## #579 — [Planning] QUILL 2.0 deferred: AI-11 — AI AI-11 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

AI-11 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). AI AI-11 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

AI-11 of `docs/planning/planning.md`.



---

## #580 — [Planning] QUILL 2.0 deferred: AI-12 — AI AI-12 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

AI-12 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). AI AI-12 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

AI-12 of `docs/planning/planning.md`.



---

## #581 — [Planning] QUILL 2.0 deferred: AI-18 — AI AI-18 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

AI-18 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). AI AI-18 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

AI-18 of `docs/planning/planning.md`.



---

## #582 — [Planning] QUILL 2.0 deferred: FEAT-12 — Feature FEAT-12 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

FEAT-12 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Feature FEAT-12 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

FEAT-12 of `docs/planning/planning.md`.



---

## #583 — [Planning] QUILL 2.0 deferred: FEAT-13 — Feature FEAT-13 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

FEAT-13 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Feature FEAT-13 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

FEAT-13 of `docs/planning/planning.md`.



---

## #584 — [Planning] QUILL 2.0 deferred: FEAT-14 — Feature FEAT-14 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

FEAT-14 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Feature FEAT-14 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

FEAT-14 of `docs/planning/planning.md`.



---

## #585 — [Planning] QUILL 2.0 deferred: FEAT-15 — Feature FEAT-15 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

FEAT-15 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Feature FEAT-15 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

FEAT-15 of `docs/planning/planning.md`.



---

## #586 — [Planning] QUILL 2.0 deferred: FEAT-16 — Feature FEAT-16 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

FEAT-16 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Feature FEAT-16 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

FEAT-16 of `docs/planning/planning.md`.



---

## #587 — [Planning] QUILL 2.0 deferred: FEAT-17 — Feature FEAT-17 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

FEAT-17 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Feature FEAT-17 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

FEAT-17 of `docs/planning/planning.md`.



---

## #588 — [Planning] QUILL 2.0 deferred: FEAT-18 — Feature FEAT-18 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

FEAT-18 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Feature FEAT-18 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

FEAT-18 of `docs/planning/planning.md`.



---

## #589 — [Planning] QUILL 2.0 deferred: LINUX-1 — LINUX-1 spike — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

LINUX-1 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). LINUX-1 spike — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

LINUX-1 of `docs/planning/planning.md`.



---

## #590 — [Planning] QUILL 2.0 deferred: ECO-1 — Ecosystem ECO-1 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

ECO-1 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Ecosystem ECO-1 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

ECO-1 of `docs/planning/planning.md`.



---

## #591 — [Planning] QUILL 2.0 deferred: L10N-1 — Localization L10N-1 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

L10N-1 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Localization L10N-1 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

L10N-1 of `docs/planning/planning.md`.



---

## #592 — [Planning] QUILL 2.0 deferred: COLLAB-1 — Collaboration COLLAB-1 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

COLLAB-1 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Collaboration COLLAB-1 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

COLLAB-1 of `docs/planning/planning.md`.



---

## #593 — [Planning] QUILL 2.0 deferred: AX-A — Accessibility Agents AX-A — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

AX-A is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Accessibility Agents AX-A — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

AX-A of `docs/planning/planning.md`.



---

## #594 — [Planning] QUILL 2.0 deferred: AX-B — Accessibility Agents AX-B — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

AX-B is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Accessibility Agents AX-B — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

AX-B of `docs/planning/planning.md`.



---

## #595 — [Planning] QUILL 2.0 deferred: AX-C — Accessibility Agents AX-C — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

AX-C is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Accessibility Agents AX-C — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

AX-C of `docs/planning/planning.md`.



---

## #596 — [Planning] QUILL 2.0 deferred: AX-D — Accessibility Agents AX-D — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

AX-D is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Accessibility Agents AX-D — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

AX-D of `docs/planning/planning.md`.



---

## #597 — [Planning] QUILL 2.0 deferred: AX-E — Accessibility Agents AX-E — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

AX-E is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Accessibility Agents AX-E — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

AX-E of `docs/planning/planning.md`.



---

## #598 — [Planning] QUILL 2.0 deferred: AX-F — Accessibility Agents AX-F — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

AX-F is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Accessibility Agents AX-F — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

AX-F of `docs/planning/planning.md`.



---

## #599 — [Planning] QUILL 2.0 deferred: PKG-1 — Packaging freezing evaluation PKG-1 — deferred to QUILL 2.0

**Labels:** p2

Source: `docs/planning/planning.md` Tier completion table.

PKG-1 is explicitly deferred to QUILL 2.0 per maintainer direction recorded in planning.md (2026-06-02 deferral note). Packaging freezing evaluation PKG-1 — deferred to QUILL 2.0.

### Acceptance

- Re-evaluation when QUILL 2.0 planning opens.

### Closes

PKG-1 of `docs/planning/planning.md`.
