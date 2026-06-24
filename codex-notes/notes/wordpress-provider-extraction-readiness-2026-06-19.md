# WordPress Provider Extraction Readiness

## 2026-06-19 Summary

WordPress should remain the in-tree reference publishing provider for the next implementation slices. The framework boundary is much sharper now, but extraction into a first-party bundled Quillin is not ready until the provider package can satisfy the same metadata, client, validation, consent, and lifecycle contracts without weakening SEC-8 or adding shell assumptions.

This note is an extraction-readiness checkpoint, not an instruction to move WordPress now.

## Current Boundary

Provider-neutral pieces already exist:

- provider metadata lives in `quill.core.publishing_providers`
- provider clients live behind `PublishingProviderClient` in `quill.core.publishing_clients`
- publishing actions route through provider ids, provider capabilities, and provider clients instead of directly through WordPress UI paths
- `validate_publishing_provider_definition(...)` checks provider metadata contract shape
- `validate_publishing_provider_client(...)` checks client/operation drift
- `python -m quill.tools.check_publishing_providers` is wired into local pre-commit and PR CI internal gates
- WordPress declares its current auth, content-kind, and operation support as data rather than as hidden shell behavior

WordPress-specific pieces are still intentionally contained in the WordPress provider/client layer:

- WordPress REST endpoint construction
- WordPress REST payload parsing
- WordPress application-password verification
- WordPress status vocabulary normalization for publish/draft flows
- WordPress posts/pages endpoint mapping
- WordPress-specific remote HTML response normalization helpers where the response shape is provider-specific

## Extraction Blockers

Before WordPress can become a first-party bundled Quillin or equivalent provider package, the following must be true:

1. Provider registration must have a package-facing contract.

   A bundled provider needs a reviewed way to contribute a `PublishingProviderDefinition` and a matching `PublishingProviderClient` without importing arbitrary third-party provider code at app startup.

2. The lifecycle bridge must be explicit.

   The current Quillins runtime is command/event oriented. Publishing provider clients are synchronous Python objects called from core publishing flows. A bundled-provider adapter must define how provider calls cross the Quillin boundary, including timeouts, errors, and result dataclasses.

3. Network consent and egress review must stay intact.

   WordPress performs explicit user-initiated network operations. A provider package must declare and justify network capability, and the existing no-silent-network inventory must remain truthful about the call path.

4. Secret handling must remain host-owned.

   Publishing credentials should continue to use Quill's credential manager / protected storage path. A provider package may request a secret for a specific operation, but it should not own long-lived credential persistence directly.

5. Provider validation must run before provider exposure.

   Any bundled provider must pass the provider registry gate before appearing in user-facing connection choices. That includes metadata subset checks, known auth/operation ids, content-kind labels, client registration, and declared-operation method coverage.

6. Shell and UI wording must remain provider-neutral.

   File menu commands, command ids, dialogs, status messages, and result messages must keep using publishing concepts. WordPress names may appear in provider labels/help text only.

7. Third-party loading must remain locked off.

   QUILL 1.0 keeps third-party Quillin discovery/execution behind the locked-off `core.third_party_plugins` SEC-8 gate. WordPress extraction may target the trusted bundled Quillin path, but it must not imply live third-party publishing provider loading.

8. Performance and reliability must be measured.

   Publishing operations include network timeouts and may run from UI-triggered flows. A bundled provider adapter must not introduce UI stalls, unbounded worker waits, or less clear cancellation/error behavior.

## Minimum Bundled Provider Package Expectations

A future first-party bundled publishing provider should provide or declare:

- stable provider id
- `PublishingProviderDefinition`
- matching provider client registration
- supported and implemented auth methods
- supported and implemented content kinds
- supported and implemented operations
- singular and plural content-kind labels
- provider-owned help text for setup/auth expectations
- explicit network capability rationale
- host-owned secret access strategy
- clear timeout and failure messages
- focused provider validation tests
- passing `python -m quill.tools.check_publishing_providers`
- no shell command ids or menu entries named after the provider

## Current Recommendation

Keep WordPress in `quill.core.publishing_clients` as the reference provider while the publishing lifecycle and contract settle. Continue extraction-readiness work in small slices:

- document the provider package adapter shape before implementing it
- avoid moving WordPress until provider package registration, network consent, and host-owned secret access are explicit
- keep new publishing behavior provider-neutral and covered by the registry gate
- treat third-party provider loading as a later policy/runtime milestone, not part of the current publishing branch