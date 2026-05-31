# QUILL Maintainers

This file describes maintainer responsibilities and operational expectations.

## Maintainer team

- Community Access maintainers (`@Community-Access`)

## Responsibilities

1. Triage issues and guide contributors to the right template/workflow.
2. Review pull requests for correctness, accessibility, and maintainability.
3. Keep release process and documentation current.
4. Enforce `CODE_OF_CONDUCT.md` and `SECURITY.md`.
5. Protect user trust: no silent network behavior, no unsafe defaults.

## Review expectations

Maintainers should request changes when a PR:

- introduces accessibility regressions,
- bypasses architecture boundaries from `docs/QUILL-PRD.md`,
- weakens security/privacy constraints,
- omits required tests/checks for changed behavior.

## Availability and handoff

If a maintainer is unavailable, another maintainer should take ownership of:

1. Security reports
2. Release-blocking regressions
3. Accessibility regressions

## Related docs

- `CONTRIBUTING.md`
- `GOVERNANCE.md`
- `SECURITY.md`
