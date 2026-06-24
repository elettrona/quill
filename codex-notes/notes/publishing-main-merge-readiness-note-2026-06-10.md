# Publishing Branch Merge Readiness Note

## 2026-06-10 22:48:16 -04:00

## Bottom Line

Recommendation: tell the head developer to hold his horses on a direct merge to `main`.

This branch looks ready for review as a draft PR or scoped integration discussion, but it does not yet look like the cleanest candidate for an immediate merge-to-main as-is.

## Why I Say Hold

### 1. The publishing work is stable, but still functionally incomplete

What is in good shape now:

- provider-based publishing connection framework exists
- publishing dialogs and accessibility hardening are in place
- browse/open published content exists
- remote published content now opens as `Readable Markdown` by default
- per-open `Raw HTML` override exists
- focused publishing and merge-sensitive validation is green

What is still missing from the larger publishing story:

- the explicit `Update Remote Content...` workflow is still not implemented
- send/update behavior based on stored authoring-surface metadata is still pending
- the branch currently proves connection + browse/open foundations more than full round-trip publishing lifecycle completeness

That means this is a strong foundation branch, but not yet the full user-facing publishing feature story.

### 2. `main` has been moving fast in adjacent UI architecture

Since this branch started, `main` has absorbed major work in:

- remote I/O site-manager transports
- menu consolidation and QUILL-key remapping
- notebook workspace UI and notebook store
- Node.js runtime / Quillins packaging work
- ongoing sweep/test/stability cleanup

Recent upstream commits now visible on `origin/main` include:

- `54cef8c` `feat(quillins): Node.js runtime, QDC tutorial, installer Node.js component, test fixes (Closes #158)`
- `106ef2c` `feat(editors): §10.3 menu consolidation, §10.8 QUILL-key remap, M2 notebook store (GATE-12)`
- `d394863` `feat(notebook): §10.4 Milestone 2 — Notebook workspace UI layer`

We successfully merged those changes into this branch and kept our publishing slice green, which is good. But it also means `main` is still in an active period of structural UI churn, and landing a partially-complete publishing branch right now would increase integration surface area.

### 3. The branch contains a lot more than just production publishing code

Compared to `origin/main`, this branch currently includes:

- production publishing modules
- menu/main-frame wiring
- tests and characterization fixture updates
- module-budget and UI-surface updates
- planning docs
- review logs
- handoff notes
- merge/audit notes

That may be exactly what we want for branch continuity, but it is not automatically what we want to merge into `main` in one shot without a cleanup/scoping pass.

## What *Is* Ready

These pieces look reviewable and technically credible:

- `quill/core/publishing.py`
- `quill/core/publishing_clients.py`
- `quill/core/publishing_providers.py`
- `quill/ui/publishing_tools.py`
- command registration / feature wiring for publishing
- focused publishing tests and a11y coverage

The branch-owned verification slice passed after the latest `main` merge:

- 87 tests passed in 9.85s

That says the implemented slice is not shaky. The question is not “is it broken?” The question is “is this the right moment and shape for `main`?” I think the answer there is still “not quite.”

## Recommendation to Give the Lead Developer

Suggested message:

“Please hold off on merging this branch directly into `main` for now. The publishing foundation is integrated with current `main` and its focused test slice is green, but the end-to-end publishing workflow is still incomplete. It’s ready for draft PR review and scoping feedback, but I’d prefer to land at least the update-remote-content path and do a cleanup pass on branch-only planning/log artifacts before asking for a full merge.”

## Best Next Step

My recommendation is one of these two paths:

1. Open a draft PR now if people need visibility.
2. Do one more implementation slice before merge:
   - add `Update Remote Content...`
   - use stored publishing metadata to choose Markdown-to-HTML conversion vs raw-HTML send
   - then do a cleanup pass to separate production changes from branch-process notes

## Final Judgment

- Ready for draft PR: yes
- Ready for technical review: yes
- Ready for direct merge to `main` without caveat: no

