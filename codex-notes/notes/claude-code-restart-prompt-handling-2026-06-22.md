# Claude Code: Handling Codex Restart Prompts

## Context

This repo's owner alternates between OpenAI Codex and Claude Code on the
same feature branches, using `codex-notes/{plans,memory,logs,notes,handoff}/`
as the cross-session continuity record. Restart/handoff prompts originally
written for Codex sometimes get handed to Claude Code instead. This note
records how to convert one without losing anything that matters, since
it's a feature-independent process question, not specific to any one
branch.

## What to drop

Codex-tool-specific sections do not apply to Claude Code and should be
dropped entirely:

- Instructions to "retry a harmless `apply_patch` edit" or diagnose
  `apply_patch`/sandbox failures — these describe Codex's own patch-tool
  plumbing. Claude Code edits files directly via its Edit/Write tools;
  there is no sandboxed patch helper to test and no equivalent failure
  mode to retry around.
- Any other Codex-CLI-specific tooling references (e.g. Codex's own
  sandbox or elevated-permission model).

## What to keep

Everything else in a Codex restart prompt is tool-agnostic and should
carry over unchanged:

- Repository-state assumptions — but verify them before trusting them.
  `origin/main` and even `origin/<feature-branch>` can move between when a
  prompt was written and when it's acted on; run `git fetch` and compare
  before assuming the prompt's snapshot is current.
- Phase scope and non-goals.
- The acceptance/closeout contract for the work (security, accessibility,
  validation, provider-neutrality, or whatever the project's own standing
  requirements are for that feature).
- Implementation order and the validation commands the prompt specifies.

## Process to follow

- Verify git state first (branch, HEAD, tracking remote, divergence from
  main) before reading anything else.
- Read the relevant codex-notes files for the feature next, most-recently
  -dated sections first.
- For anything non-trivial, research the current code state directly
  rather than trusting the prompt's old file/line references, then plan
  (Claude Code's plan mode) before implementing — especially when the
  prompt implies a decision with more than one defensible scope, or one
  that touches a security/policy boundary rather than pure engineering
  taste. Bring genuine policy forks back to the user explicitly instead of
  picking a side.
- Follow this repo's own standing convention, already recorded in
  `codex-notes/handoff/codex-handoff.md`'s 2026-06-18 "Testing Discipline
  Checkpoint" entry: commit locally as work proceeds; do not push unless
  explicitly requested — even when a restart prompt's own closing
  instructions say to push. Ask the current user first.
- Keep using the existing codex-notes convention: append new dated
  `## YYYY-MM-DD ...` sections to the canonical plan/memory/work-log/status
  /handoff files for the feature rather than creating a new file per
  session, and write one closeout note per completed phase.

## Provenance

First applied 2026-06-21 when converting a Codex-authored restart prompt
for the publishing-providers-framework "schedule publishing" phase — see
`codex-notes/handoff/publishing-providers-framework-restart-2026-06-19.md`'s
2026-06-21 entries for the worked example, including a case where the
prompt's repository-state snapshot had already gone stale (`origin/main`
had advanced one commit past what the prompt assumed) and was caught by
verifying first rather than trusting it. Recorded here as a standalone
note since it applies to any future Codex-to-Claude handoff on this repo,
not just that branch.
