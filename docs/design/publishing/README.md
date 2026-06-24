# Publishing Providers Framework — Design Documents

Design and planning documents for QUILL's provider-aware publishing feature
(connect to a remote site such as WordPress and browse / open / create / update /
publish content through a vetted provider adapter).

These were authored during the framework's development and relocated here from the
working notes for durable reference.

| Document | What it covers |
|---|---|
| [bundled-publishing-provider-adapter-contract-2026-06-19.md](bundled-publishing-provider-adapter-contract-2026-06-19.md) | The bundled provider adapter contract (the core interface a provider implements). |
| [publishing-providers-framework-current-state-2026-06-19.md](publishing-providers-framework-current-state-2026-06-19.md) | Framework plan state and phase breakdown. |
| [publishing-follow-up-phases-2026-06-19.md](publishing-follow-up-phases-2026-06-19.md) | Planned follow-up phases / roadmap. |
| [publishing-remote-integration-planning-2026-06-10.md](publishing-remote-integration-planning-2026-06-10.md) | Early remote-integration planning. |
| [publishing-profile-restriction-2026-06-22.md](publishing-profile-restriction-2026-06-22.md) | Scoping plan for restricting publishing to writer-tier-and-above profiles. |

## Status: locked off (developer-only)

The feature ships **disabled** behind `future.publishing`, which is `locked_off=True`
in `quill/core/feature_catalog.py`. `FeatureManager.state_for()` returns `OFF` for a
locked-off feature before it consults any user override or active profile, so
`is_enabled("future.publishing")` is always False — a user cannot enable it via
profile, override, or the feature-toggle UI. Only a developer removing `locked_off`
in source can lift the gate. The File > Publish menu and all `publishing.*` commands
are gated on this flag (the command palette and Go to Anything exclude locked-off
features automatically).
