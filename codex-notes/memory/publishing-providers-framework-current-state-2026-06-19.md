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
