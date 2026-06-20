# Publishing Providers Framework Current Status

## Follow-Up Phase Progress

1. WordPress first-party bundled provider path: in progress; slice A complete.
2. Schedule publish: not started.
3. Local-vs-remote compare and honest sync model: not started.
4. Live third-party publishing provider loading: not started.

The first extraction blocker is partially resolved for the trusted in-process
path: a bundled package can contribute paired provider metadata and a client
through an adapter with explicit security/runtime policy.

Still unresolved before deeper extraction:

- whether WordPress bootstraps through the adapter during normal app startup
- whether a later provider call crosses a Quillin worker boundary
- worker timeout, error, cancellation, and result-dataclass behavior
- discovery/loading policy beyond explicitly imported first-party packages

SEC-8 remains unchanged. Third-party publishing providers are not enabled.

## 2026-06-20 Status

Phase 1 slice B is complete. WordPress now bootstraps through the trusted bundled adapter in normal application startup while retaining the same provider definition, client, credentials, REST behavior, commands, menus, dialogs, and visible workflows.

The next work must remain within Phase 1. Worker execution and third-party discovery/loading remain unresolved and explicitly unapproved.