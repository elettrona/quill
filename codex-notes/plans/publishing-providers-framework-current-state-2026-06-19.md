# Publishing Providers Framework Current Plan State

## Phase 1 Slice A Complete

This checkpoint supplements `publishing-providers-framework.md` with the latest
implemented state.

Implemented:

- `BundledPublishingProviderAdapter` pairs a stable provider id, provider
  definition, and matching provider client.
- Registration rejects mismatched ids before changing either existing registry.
- Trusted bundled adapters require a network-capability rationale.
- Secret access is fixed to host-owned storage.
- Execution is fixed to the trusted in-process path for this phase.
- `quill.core.publishing_bundled.wordpress` represents WordPress using the same
  definition and client objects already used by publishing workflows.

Validation:

- focused adapter, publishing, and provider-gate tests: `34 passed in 0.69s`
- Ruff: passed
- provider registry gate: passed

Recommended next Phase 1 slice:

- decide whether normal app bootstrap should register WordPress through the
  bundled adapter
- preserve current provider/client behavior and all user-visible workflows
- rerun focused publishing tests and the provider registry gate

Do not begin schedule publish, compare/sync, worker execution, or live
third-party provider loading without explicit approval.

## Phase 1 Slice B Complete - 2026-06-20

Decision: WordPress should bootstrap through the trusted bundled adapter during normal application startup.

Implemented:

- explicit first-party bootstrap in `quill.core.publishing_bundled`
- bootstrap call at the application entry point before UI import
- repeat-safe registration preserving existing provider-definition and client identity
- no change to credentials, network behavior, commands, menus, dialogs, or user-visible publishing behavior

Required validation for every next slice: focused publishing tests, slice-specific unit tests, Ruff, provider registry gate, and the complete unit suite using a workspace-local temp root. Record any non-slice baseline failures instead of silently omitting the full run.

Phase 1 remains active. The prohibited later-phase work remains out of scope.