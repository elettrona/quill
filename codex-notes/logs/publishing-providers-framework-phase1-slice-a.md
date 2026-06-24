# Publishing Providers Framework Phase 1 Slice A Log

## 2026-06-19 Implementation

- added the trusted `BundledPublishingProviderAdapter` contract
- reject mismatched adapter, definition, and client ids before registry changes
- require host-owned secrets, in-process execution, and a network rationale
- added a package-shaped WordPress adapter using existing runtime objects
- added focused adapter rejection and registry-gate tests
- kept shell, menus, dialogs, and publishing behavior unchanged

Validation:

- `ruff format` completed
- `ruff check` passed
- focused adapter, publishing, and gate tests: `34 passed in 0.69s`
- `python -m quill.tools.check_publishing_providers`: passed

Local implementation commits: `303a6f3`, `bddebe3`.
