# Bundled Publishing Provider Adapter Contract

## Phase 1 Slice A Decision

The first trusted bundled-provider path remains in-process. A bundled publishing
provider contributes one `BundledPublishingProviderAdapter` containing:

- a stable provider id
- its `PublishingProviderDefinition`
- its matching `PublishingProviderClient`
- an explicit network-capability rationale
- the fixed `host_owned` secret-access policy
- the fixed `in_process` execution policy

Registration validates the package shape before changing either existing
provider registry. Definition, client, and adapter ids must match. Missing
network rationale, provider-owned secret storage, and worker execution are
rejected in this slice.

WordPress now has a package-shaped adapter factory under
`quill.core.publishing_bundled.wordpress`. It wraps the same in-tree definition
and client already used by publishing workflows, so registering it through the
adapter preserves object identity and user-visible behavior.

## Deliberate Boundaries

- no package scanning or auto-discovery
- no live third-party provider loading
- no Quillin worker boundary yet
- no provider-owned credential persistence
- no new network action or consent surface
- no shell, command, menu, or dialog change
- no schedule-publish or compare/sync work

The existing provider registry gate remains authoritative after adapter
registration. Focused tests prove WordPress passes that gate in package shape
and malformed adapters are rejected before registry exposure.

## Startup Bootstrap Decision - 2026-06-20

Normal application startup explicitly calls `bootstrap_bundled_publishing_providers()` before importing the UI. WordPress is registered through `wordpress_bundled_provider_adapter()` on this path. Repeated bootstrap replaces only the adapter record; the existing provider definition and client objects retain identity.

This decision does not add package scanning, third-party loading, worker execution, credential access, or network activity. Those boundaries remain unchanged.

Every future adapter/bootstrap slice must run focused publishing tests, relevant unit tests, Ruff, the provider registry gate, and the full unit suite with workspace-local temporary state.

## Phase 1 Contract Finalized - 2026-06-20

The closeout audit accepts this bundled-adapter contract as the completed Phase 1 foundation. Later phases may extend execution and loading policy only in separate reviewed slices; they must not silently weaken identity validation, host-owned secret handling, explicit network action, or validation-before-exposure.