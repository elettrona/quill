# Publishing Providers Framework Third-Party Loading Closeout (Roadmap Closed)

## Outcome

The live third-party publishing provider loading phase is complete in the
only form that didn't require a unilateral product security decision: the
validation contract exists and is fully tested, but no third-party
provider can actually register. This closes the publishing-providers-
framework roadmap — all four phases the 2026-06-20 Phase 1 closeout
authorized are now addressed.

## Why This Phase Was Scoped Narrowly

Research before implementation found this phase is not a publishing-
scoped engineering task at heart. SEC-8 (`docs/QUILL-PRD.md`) is a
product-wide lock: the `core.third_party_plugins` feature flag
(`locked_off=True`, `quill/core/feature_catalog.py`) keeps *all*
third-party Quillin code from executing in a default QUILL 1.0 build —
the PRD's own words: "a default build never loads third-party plugin
code... gating this off keeps untrusted plugin code out of the process
entirely." This protects every Quillin capability, not just publishing.

"Install from Folder" already exists (`quill/ui/main_frame_quillins.py`'s
`on_install`, calling `install_extension()` in
`quill/core/quillins/loader.py`) and is not itself gated by the flag — a
user can install a third-party Quillin today — but the installed code
still never runs while the flag is locked off, since
`discover_extensions()`/`load_enabled_manifests()` return empty
regardless of install state.

Critically: `register_publishing_provider` and
`register_publishing_provider_client` (`quill/core/publishing_providers.py`,
`quill/core/publishing_clients.py`) are completely open, ungated module
functions today. Any code already running in-process — including a
loaded Quillin — could call them directly, bypassing even the Phase 1
bundled-adapter validation contract. The only thing actually preventing a
third-party publishing provider today is that third-party code cannot
execute in-process at all yet, which is purely a SEC-8/Quillin-loading
concern, not a publishing-provider-registry concern.

Given this, "live third-party provider loading" amounts to asking whether
to create an exception to, or flip, SEC-8 — a product security policy
decision, not an implementation detail to infer from a roadmap-phase
rubber-stamp. The user was presented three explicit options and chose to
build the contract while leaving SEC-8 and real loading untouched, the
same "build the contract, defer the risky part" pattern used by every
prior phase of this roadmap (the bundled adapter before WordPress was
wired through it; declaring `worker` execution without building it).

## Acceptance Evidence

- `ThirdPartyPublishingProviderAdapter` (`quill/core/publishing_adapters.py`)
  has no trusted defaults for `secret_access`/`execution` — unlike the
  bundled adapter, a third-party contributor must state its policy
  explicitly rather than inherit one meant for reviewed code.
- `register_third_party_publishing_provider` validates, in order: ids
  match; network capability rationale is required; secrets must be
  host-owned; execution must be `worker` (in-process is rejected outright
  — untrusted code never gets the trusted path reserved for bundled
  providers); the provider id must not conflict with an existing bundled
  adapter. Every branch is independently tested.
- The function's last line — reached only by a fully well-formed adapter
  that passed every prior check — unconditionally raises "Live
  third-party publishing provider loading is not implemented yet."
  Proven by a dedicated test that the live registries
  (`PROVIDER_DEFINITIONS`, `_PUBLISHING_PROVIDER_CLIENTS`) are completely
  untouched even in that case.
- The module docstring states explicitly that this contract does not
  loosen, bypass, or duplicate the `core.third_party_plugins`/SEC-8 lock,
  and that implementing real loading remains a separate, explicit product
  decision.
- No UI, dialog, menu, or governance-fixture changes were needed — this
  is a pure core-layer contract with zero runtime exposure.

## Closeout Validation

- focused battery (publishing core + adapters): `82 passed`
- Ruff: passed
- provider registry gate: passed — confirms zero impact on what's actually
  registered/exposed, since nothing third-party ever reaches the registry
- scoped `mypy quill/core quill/io`: unchanged from before this slice
  (same 7 pre-existing, unrelated findings)
- full unit suite: `4100 passed, 66 failed, 14 skipped` — the 66 failures
  are the identical pre-existing set; the +7 passing delta is exactly the
  new tests added in this slice
- `quill/core/publishing_adapters.py` measured at 146 lines, well under
  the untracked 600-line default cap — no module-size budget entry needed

## Commits

One local checkpoint on `feature/publishing-providers-framework`, adding
the contract and its tests. Not pushed — pending explicit request, per
the standing repo convention.

## Roadmap Closed — What's Actually Done And What Isn't

All four phases authorized by the 2026-06-20 Phase 1 closeout:

1. WordPress first-party bundled-provider path — done (Phase 1, prior
   session).
2. Schedule publishing — done 2026-06-21.
3. Local-versus-remote compare and the first honest sync model — done
   2026-06-21.
4. Quillin worker execution boundaries / live third-party provider
   loading — both converged on the same answer this session: build the
   contract, defer the boundary, because no untrusted code can run in
   this product yet.

**Two decisions remain explicitly open** for the user or product owner,
recorded as deliberate non-defaults rather than oversights — neither
should be assumed if this branch is revisited:

- Whether to build the durable, file-path-keyed cross-session publishing-
  linkage registry deferred in the compare phase (`Document.source_metadata`
  does not survive a local save-and-reopen cycle today).
- Whether and when to loosen `core.third_party_plugins`/SEC-8 for real
  third-party Quillin or publishing-provider execution, and if so, what
  signing/review/sandboxing process (SEC-8's own stated prerequisite)
  should gate it.
