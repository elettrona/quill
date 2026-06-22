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

## Phase 1 Closed - 2026-06-20

The closeout audit found no remaining acceptance gap in the WordPress first-party bundled-provider path. Phase 1 is complete. Focused closeout validation passed with `77 passed`, Ruff, the module-size gate, and the provider registry gate.

The user explicitly approved schedule publishing, local-versus-remote compare/sync, Quillin worker execution, and live third-party provider loading to become unblocked after this audit. Continue with schedule publishing as the next separately reviewable roadmap phase. Authorization does not waive SEC-8, consent, accessibility, validation, or testing requirements.

## Schedule Publishing Complete - 2026-06-21

Implemented as the smallest coherent slice: one new `schedule` provider operation, a timezone-aware `validate_scheduled_publish_time` model, an optional `scheduled_at` parameter on the existing `create_publishing_remote_item`/`update_publishing_remote_item` functions (no new top-level action function), WordPress `status="future"` + UTC `date_gmt` behavior with round-tripped `scheduled_for`, and one accessible `SchedulePublishDialog` plus one command/menu entry covering both new-document and already-open-remote-item scheduling.

Validation: core focused battery `61 passed`; combined publishing/accessibility/governance battery `153 passed`; Ruff and the provider registry gate passed; full unit suite `4074 passed, 66 failed, 14 skipped`, the 66 failures matching the pre-existing baseline exactly with no new failures.

Next roadmap phase: local-versus-remote compare and the first honest sync model.