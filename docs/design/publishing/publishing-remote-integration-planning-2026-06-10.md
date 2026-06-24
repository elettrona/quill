# Publishing / Remote Integration Planning

Timestamp: `2026-06-10 17:24:40 -04:00`

Purpose:

- planning-only note
- no code changes proposed in this note
- evaluates how much of the publishing framework could be rolled into the newer remote-site infrastructure from current `main`

## Short Answer

Some of it can and probably should be aligned later, but not all of it should be merged.

Best planning direction:

- share storage and transport concepts where they are genuinely the same
- keep publishing-specific content workflows separate where the product semantics are different

In other words:

- unify lower-level remote profile and credential patterns carefully
- do not collapse publishing into generic file-transfer UX

## What The New Remote Infrastructure Already Gives Us

Current `main` now has a real remote-site stack for:

- FTP
- SFTP
- WebDAV
- S3
- generic “open from remote” / “save to remote” flows

That stack already includes:

- a saved remote-site profile model in `quill/core/remote_sites.py`
- password persistence patterns
- a governed remote-sites dialog in `quill/ui/remote_sites_dialog.py`
- `File` menu integration in `quill/ui/main_frame_menu.py`
- remote open/save shell wiring in `quill/ui/main_frame.py`

This means the repo now has a broader “remote destination” concept than when the publishing plan was first drafted.

## Where Publishing And Remote Sites Truly Overlap

These parts overlap enough that future alignment is worth planning:

### 1. Saved Remote Destination Pattern

Both systems need:

- named saved profiles
- a current/last-used selection model
- secure credential storage
- endpoint-specific metadata
- explicit user-driven network actions

Planning takeaway:

- publishing connections and remote sites are both variants of a saved remote destination
- they do not need to stay totally unrelated forever

### 2. Credential Persistence Strategy

Both systems already use the same broad trust model:

- secure persistence
- no plaintext credentials
- explicit user action before network use

Planning takeaway:

- we should eventually standardize the credential-storage facade, naming, and lifecycle expectations
- this is a strong candidate for shared infrastructure

### 3. File Menu Placement And Dialog Rhythm

Both systems live under `File` and follow a similar high-level rhythm:

- choose remote destination
- verify or browse
- act explicitly

Planning takeaway:

- the shell can probably grow toward a more coherent “Remote” mental model without changing the underlying publishing semantics

## Where Publishing And Remote Sites Should Stay Separate

This is the important part.

### 1. Publishing Is Not File Transfer

Remote Sites is fundamentally about files and paths:

- host
- directory
- remote file path
- transport protocol

Publishing is fundamentally about content objects:

- post
- page
- remote content id
- authoring surface
- publish/update semantics
- site API behavior

Planning takeaway:

- publishing should not be rewritten as “just another remote file transport”
- a WordPress post is not analogous to an SFTP path in the user’s mental model or in the code’s behavior

### 2. Publishing Needs Content-Aware Metadata

Publishing already depends on content-specific truth:

- content kind
- remote id
- remote URL
- publishing status
- chosen authoring surface
- open representation

Remote Sites does not own those concepts.

Planning takeaway:

- publishing must continue to own its content identity and representation metadata
- collapsing this into generic remote-site metadata would likely make the design less honest and harder to maintain

### 3. Publishing Uses Provider Logic, Not Just Transport Logic

Remote Sites is transport-oriented.
Publishing is provider-oriented.

That difference matters because publishing needs:

- provider-specific browse logic
- provider-specific content-kind support
- provider-specific create/update workflows
- provider-specific API contracts

Planning takeaway:

- the existing provider/client seam in publishing is still the right architectural center
- remote sites should not replace that seam

## My Recommendation

I would not merge publishing directly into the current Remote Sites feature.

I would plan a phased alignment instead.

## Recommended Alignment Plan

### Phase A: Keep Product Flows Separate

For now:

- keep `File > Publish` as its own content workflow
- keep `Open from Remote` / `Save to Remote` as file-transfer workflows
- keep publishing dialogs and remote-sites dialogs separate

Reason:

- they solve different user jobs
- forcing a single UI too early would create confusion and probably regress accessibility clarity

### Phase B: Introduce A Shared “Remote Destination” Concept Under The Hood

Later, if we want less duplication:

- define a shared lower-level remote destination/storage abstraction
- let both publishing connections and remote sites build on it

That shared layer could eventually cover:

- id / label / endpoint basics
- secret persistence helpers
- current-selection storage
- maybe some normalized trust/network metadata

But it should not own:

- publishing content kinds
- publishing authoring-surface rules
- browse/update/publish semantics
- remote file browser semantics

### Phase C: Consider A Shell-Level Discoverability Cleanup

Once both systems are more mature:

- we could revisit the `File` menu wording and grouping
- maybe shape a clearer “Remote” cluster

Example future direction:

- file transfer actions remain path/file oriented
- publishing actions remain content/site oriented
- both live near each other without pretending they are the same thing

## What Feels Safe To Reuse Later

These are the pieces I think are safest to fold together over time:

- saved-profile persistence conventions
- secret storage helpers
- current-selection / last-used selection behavior
- some dialog structural patterns
- some network/trust validation helpers where semantics truly match

## What I Would Not Reuse Blindly

These should stay publishing-owned unless a later design proves otherwise:

- provider registry
- publishing client seam
- browse published content UX
- remote content identity metadata
- authoring-surface / representation logic
- update remote content flow
- local linkage registry for publish/update relationships

## Overall Judgment

A moderate amount of future consolidation looks worthwhile.

But the right consolidation target is:

- shared remote-destination infrastructure

not:

- one merged publishing-and-file-transfer feature

If we over-merge them, we’ll probably make the code less synchronized in practice, because we’d be forcing two different product models into one abstraction too early.

If we align them at the storage/trust/credential layer, we get most of the maintainability win without losing the publishing model we already planned carefully.

## Best Next Planning Follow-Up

Before any code:

- inventory exactly which fields overlap between `PublishingConnectionProfile` and `RemoteSite`
- separate overlaps into:
  - truly shared
  - superficially similar but semantically different
- decide whether a future shared `remote_destinations` core module would reduce duplication cleanly or just rename it

That would give us a clean answer on whether consolidation is actually worth it before we touch the implementation.
