# Publishing Providers Framework Current Memory

## Phase 1 Slice A Checkpoint

Branch: `feature/publishing-providers-framework`.

The trusted bundled-provider package contract now exists. WordPress can be
represented through `quill.core.publishing_bundled.wordpress` without replacing
its existing definition, client, commands, menus, dialogs, credentials, network
calls, or user-visible behavior.

Pinned contract decisions:

- adapter, definition, and client ids must match
- malformed adapters are rejected before registry exposure
- bundled providers must explain their network capability
- credentials remain host-owned
- only trusted in-process execution is accepted in this slice
- no package scanning or third-party runtime loading occurs

Validated with `34 passed in 0.69s`, Ruff, and a passing provider registry gate.

Implementation commits before the detailed documentation commit:

- `303a6f3` adapter contract
- `bddebe3` WordPress package-shape proof and tests
- `fce71c4` initial Phase 1 slice A records
- `858d4c8` formatter checkpoint

Resume inside Phase 1 only.

## Phase 1 Slice B Memory - 2026-06-20

`origin/main` at `3df921ea` was merged in `a3bec29`. WordPress now bootstraps through `bootstrap_bundled_publishing_providers()` during normal application startup, before the UI import. The bootstrap uses the existing WordPress definition and client objects, is safe to repeat, and adds no discovery, third-party loading, worker execution, credential change, or network action.

Implementation commit: `90a3f6e`. Focused validation passed with `77 passed`, Ruff, the module-size gate, and the provider registry gate. Final full-unit result was `4056 passed, 66 failed, 14 skipped`; none of the failures touched publishing or this startup slice.

Future slices must include and record focused tests, relevant new unit tests, Ruff, the provider registry gate, and a full unit run with workspace-local temporary state.