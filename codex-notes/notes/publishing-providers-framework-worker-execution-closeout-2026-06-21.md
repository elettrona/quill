# Publishing Providers Framework Quillin Worker Execution Closeout

## Outcome

The Quillin worker execution boundaries and lifecycle behavior phase is
complete, scoped narrowly to deliver real, testable lifecycle behavior
now while explicitly deferring the actual subprocess/IPC worker boundary
to the live third-party provider loading phase, which is next and last.

## Scope Decision: Defer The Real Boundary

Research before implementation (two parallel codebase explorations)
found QUILL's Quillin extension system already has a full subprocess-
based worker model — Python workers via `subprocess.Popen`
(`quill/core/quillins/host.py` + `host_worker.py`, JSONL IPC) and Node
workers via `quill/core/ai/external_engine.py`'s allowlisted subprocess
runner — with capability/consent gating already wired through. None of
it is reusable for publishing providers without new provider-specific
IPC work, and critically: **there is no untrusted publishing provider
yet to validate a real worker boundary against**. Third-party provider
loading remains locked off by SEC-8 regardless of this phase, so building
a subprocess boundary now would be speculative greenfield work with no
concrete consumer.

The user was presented three explicit options (lifecycle behavior now
with the boundary deferred; build the real boundary now against a fake
test-only provider; skip straight to third-party loading planning) and
chose the first, recommended option. This is a recorded decision, not a
gap discovered by accident: the actual subprocess/IPC worker boundary
remains unbuilt, and building it is the natural first concrete task of
the next (final) roadmap phase, when a real provider will exist to
justify and validate it.

## Acceptance Evidence

- `browse_publishing_content` and the WordPress client's `browse_content`
  (Protocol and implementation) accept an `is_cancelled` callable, checked
  between per-content-kind requests. Cancellation raises the new
  `PublishingOperationCancelled` rather than returning partial results —
  cancel means stop-and-discard, kept distinct from the existing unrelated
  partial-results-on-timeout behavior, which is untouched.
- New `quill/core/publishing_worker.py` is the only publishing module that
  imports `quill.stability.task_manager`; `quill.core.publishing` itself
  stays decoupled from the stability layer, importing nothing beyond a
  plain callable.
- `BrowsePublishingContentDialog` now dispatches its load through
  `MainFrame`'s existing `TaskManager` instead of blocking the UI thread,
  with a real Cancel button. Clicking Cancel detaches the dialog
  immediately and reports "Browse cancelled." honestly — it does not
  claim to forcibly stop an in-flight socket read, which only a real
  subprocess boundary could do. Stale callbacks (after a cancel or dialog
  teardown) are ignored via an operation-id + `_destroyed` guard.
- The existing `wx.ID_CANCEL` Close button and Escape handling are
  untouched — no new escape-trap pattern was introduced, verified by the
  existing `test_dialog_button_contract.py`/`test_dialog_hardening_contract.py`
  gates passing unchanged.
- `quill/core/publishing_adapters.py` recognizes `WORKER_EXECUTION =
  "worker"` as a declared-but-not-yet-implemented execution policy with
  its own honest rejection message, distinct from the generic rejection
  for truly unknown values.

## Honest Limitation (Documented, Not Hidden)

A cooperative cancel only takes effect at a checkpoint the worker
function actually reaches (between the two per-content-kind requests
browse loops over). If Cancel is clicked while the first or only request
is blocked on a socket read, that background thread keeps running until
its own socket timeout fires — the dialog still detaches and reports
"cancelled" to the user immediately, but the thread isn't forcibly
killed. This is exactly the gap a real subprocess worker boundary would
close, and exactly why building one is deferred rather than faked.

## Closeout Validation

- focused battery (core + UI + module-size): `97 passed`
- dialog governance gates (inventory, banned-patterns, button contract,
  hardening, announce-gap): `44 passed`
- Ruff: passed
- provider registry gate: passed
- scoped `mypy quill/core quill/io`: unchanged from before this slice
  (same 7 pre-existing, unrelated findings)
- full unit suite: `4093 passed, 66 failed, 14 skipped` — the 66 failures
  are the identical pre-existing set; the +10 passing delta is exactly
  the new tests added in this slice
- smoke-launched `python -m quill` for ~12s: no startup traceback (only
  an unrelated benign lexicon-file stderr warning), confirming the new
  wiring doesn't break MainFrame construction
- **not verified**: interactive Browse → Load Content → Cancel behavior.
  No pywinauto installed and no project run-skill exists for driving this
  wxPython desktop app, so this could not be automated. Recorded as a
  known verification gap rather than claimed as tested — confidence in
  the runtime behavior rests on the passing governance gates, the static
  source-inspection tests, and code review, consistent with how every
  other wx dialog in this codebase is tested.

## Commits

Two local checkpoints on `feature/publishing-providers-framework`:

1. Core: `PublishingOperationCancelled`, `is_cancelled` threading, new
   `publishing_worker.py`, `publishing_adapters.py` execution-policy
   branch, their tests (including the adapter test fix).
2. UI + governance: `BrowsePublishingContentDialog` cancel wiring,
   `main_frame.py` task_manager threading, UI tests, module-size budget
   bump.

Not pushed — pending explicit request, per the standing repo convention.

## Next Order

Per the 2026-06-20 Phase 1 closeout authorization, this was the third of
four unblocked phases. **Live third-party provider loading is next and
last.** It should begin by building the real subprocess/IPC worker
boundary this phase deliberately deferred — now justified by an actual
untrusted provider — reviewed against SEC-8, consent, validation, and
network-capability requirements before any third-party provider is
exposed.
