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

## Phase 1 Closed - 2026-06-20

The closeout audit passed. The WordPress first-party bundled-provider path is complete, including trusted adapter validation and normal startup bootstrap.

The user's post-closeout approval unblocks the later roadmap phases. Current order: schedule publishing, compare/sync, Quillin worker execution, then live third-party loading. No later-phase implementation was performed during closeout.

## Schedule Publishing Complete - 2026-06-21

Schedule publishing is implemented and closed out. WordPress can now schedule a new post/page or an already-open remote item via `status="future"` + UTC `date_gmt`, behind one provider-neutral command/menu entry and one accessible dialog. Compare/sync, Quillin worker execution, and live third-party loading remain unresolved and explicitly unapproved-for-implementation until separately reviewed. Current order: compare/sync next, then Quillin worker execution, then live third-party loading.

## Compare With Remote Complete - 2026-06-21

Compare is implemented and closed out. Users can request an honest comparison of an already-open remote publishing item against its current remote state (title/body/status, plus a "remote changed since you last synced" signal) without any automatic overwrite or merge. Cross-session linkage persistence was explicitly deferred — `source_metadata` does not survive a local save/reopen, and building a durable registry remains a separate, unscheduled piece of work. Quillin worker execution and live third-party loading remain unresolved and explicitly unapproved-for-implementation until separately reviewed. Current order: Quillin worker execution next, then live third-party loading.