# Publishing Providers Framework Phase 1 Slice A Memory

## 2026-06-19 Checkpoint

`BundledPublishingProviderAdapter` pairs reviewed metadata and a client with
fixed host-owned secret and in-process execution policies plus a required
network rationale. WordPress is package-shaped under
`quill.core.publishing_bundled.wordpress` without changing its runtime objects
or user-visible publishing behavior.

Focused validation: `34 passed`; provider registry gate passed.
