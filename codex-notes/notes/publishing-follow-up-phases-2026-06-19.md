# Publishing Follow-Up Phases

## 2026-06-19 Phase Order

The publishing framework readiness checkpoint is complete. The next work moves into follow-up phases. These phases should be developed deliberately, with local commits and validation after each slice.

Recommended order:

1. WordPress first-party bundled provider package path.
2. Schedule publish.
3. Local-vs-remote compare and first honest sync model.
4. Live third-party publishing provider loading.

This order keeps the highest security and runtime-risk item, live third-party provider loading, last. WordPress extraction can use the trusted first-party bundled path as a proving ground before any third-party provider loading is exposed.

## Phase 1: WordPress First-Party Bundled Provider Package

Goal:

- Move WordPress toward a first-party bundled provider package or adapter while preserving the existing provider/client contract and user-facing behavior.

Initial slices:

- define the bundled-provider adapter contract
- decide whether the first package remains in-process but separately registered, or crosses the Quillin worker boundary
- keep host-owned credential storage and explicit network egress review
- prove the package passes `python -m quill.tools.check_publishing_providers`
- keep all command ids and menus provider-neutral

Done when:

- WordPress can be represented as a first-party bundled provider without shell-specific WordPress assumptions
- the provider registry gate catches missing metadata/client pieces before exposure
- existing publishing workflows behave the same from the user's perspective

Non-goals:

- no third-party provider loading
- no marketplace or auto-discovery of publishing providers
- no rewrite of publishing dialogs just to expose package internals

## Phase 2: Schedule Publish

Goal:

- Add explicit user-controlled scheduled publishing for supported providers.

Initial slices:

- add provider operation metadata for scheduling if the current publish operation is not precise enough
- define scheduled publish data model and validation
- design UI flow with plain-language time/date confirmation
- ensure timezone and date handling are explicit
- add provider-client method or status/date payload strategy as needed
- keep scheduled action review-first and never silent

Done when:

- users can schedule publish for a current or remote publishing document only after explicit confirmation
- unsupported providers report capability gaps clearly
- scheduled publish paths have focused unit tests and dialog/accessibility coverage

Non-goals:

- no background CMS polling
- no recurring schedule automation
- no broad calendar/task system

## Phase 3: Local-Vs-Remote Compare And First Honest Sync Model

Goal:

- Let users understand whether their local publishing document differs from the remote item, without promising automatic bidirectional sync.

Initial slices:

- define remote identity/linkage source of truth
- load current remote state on explicit user request
- compare title, body, status, URL/id, and updated timestamp
- present a readable comparison summary
- decide what conflict states are detectable versus unknown
- keep update/publish actions explicit after comparison

Done when:

- users can request a clear comparison between local and remote publishing content
- Quill reports unknown/stale states honestly
- no automatic overwrite or background sync happens without user action

Non-goals:

- no real-time sync
- no automatic conflict resolution
- no bulk cross-site sync

## Phase 4: Live Third-Party Publishing Provider Loading

Goal:

- Eventually allow non-core publishing providers to register through the same provider/client contract after the runtime, policy, and security gates are ready.

Prerequisites:

- WordPress first-party package path proven
- provider package validation contract complete
- capability and consent flow reviewed for provider network operations
- third-party Quillin/security policy explicitly lifted or scoped for publishing providers
- conflict handling for provider ids and command contributions
- CI gate prevents invalid providers from surfacing

Done when:

- a provider can be discovered, validated, consented, and exposed without weakening SEC-8 or bypassing host-owned secret/network controls
- invalid or conflicting providers are rejected with actionable diagnostics

Non-goals for now:

- do not enable this before the trusted first-party path is proven
- do not make publishing provider loading a hidden side effect of generic Quillin discovery
- do not allow providers to persist secrets outside host-owned storage

## Current Recommendation

Start with Phase 1 slice A: define the bundled-provider adapter contract in docs and tests, then implement only the smallest adapter seam needed to prove WordPress can be package-shaped without changing user-visible publishing behavior.