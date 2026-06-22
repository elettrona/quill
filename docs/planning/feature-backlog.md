# QUILL Feature Request Backlog Archive

> **Consolidated workstream design spec.** This file gathers the full text of
> every open issue in this workstream so the design reads end to end in one
> place. The issues remain **open and individually tracked** in
> [`program-tracker.md`](program-tracker.md); each closes as its
> implementation ships. Everything here is in scope to ship — issue numbers
> are preserved as section anchors.

Standalone feature requests captured from the tracker.


## Triage summary (product judgment)

- **DAISY 2.02 text-only export (#251):** strongly aligned with QUILL's accessibility mission; a good standalone feature for a future wave (a design already exists in the DAISY export plan).
- **WordPress / direct publishing (#140):** niche relative to QUILL's core editor mission and carries external-API + auth surface; recommend keeping as a long-term idea (or a Quillin) rather than core work.


## Contents (2 archived issues)

- [#140](#140-) — Support Direct Publishing to WordPress and Other Publishing Platforms.
- [#251](#251-) — Suggestion: Export to DAISY talking book



---

## #140 — Support Direct Publishing to WordPress and Other Publishing Platforms.

**Labels:** (none)

# Feature Proposal: Publishing Providers Framework

## Status

Proposed for QUILL 2.x

## Summary

Introduce a Publishing Providers Framework that allows QUILL to directly create, edit, synchronize, schedule, and publish content to supported publishing platforms without requiring users to leave the editor.

WordPress should be the initial provider implementation.

## Background

QUILL already provides a powerful environment for writing, editing, reviewing, auditing, and refining content. However, users must currently leave QUILL when they are ready to publish or update content.

A writer may spend hours creating content within QUILL, only to switch to a browser, navigate a content management system, locate the correct content, and perform publishing tasks elsewhere.

Many users simply prefer QUILL's writing environment over the WordPress block editor and would rather publish from an interface they already know than switch to a browser-based editing experience.

For keyboard-only users, screen-reader users, and users managing multiple sites, this creates unnecessary friction.

## Goals

- Connect publishing platforms directly to QUILL
- Create new content
- Edit existing published content
- Manage drafts
- Schedule publication
- Synchronize content
- Publish without opening a browser

## Why WordPress First

WordPress powers a significant percentage of websites and already exposes mature APIs suitable for content creation and management.

Supported targets should include:

- Self-hosted WordPress
- WordPress.com
- WP Engine
- Any WordPress installation exposing the standard WordPress REST API

## WordPress Capabilities

Initial capabilities should include:

- Connect to a WordPress site
- Create drafts
- Publish content
- Schedule content
- Browse existing content
- Edit existing content
- Update previously published content
- Synchronize content between QUILL and WordPress

Authentication should support WordPress Application Passwords at a minimum.

## Why This Fits QUILL

QUILL already serves as the primary workspace where users:

- Write content
- Review content
- Run GLOW audits
- Perform editing and revision
- Use AI-assisted workflows
- Automate tasks through Quillins

Publishing is the natural next step in that workflow.

Users should be able to move from writing to publication without leaving QUILL.

## Quillins Integration

Publishing providers should eventually be exposed through the Quillins extension architecture, allowing third parties to develop additional providers without requiring changes to QUILL core.

Potential future providers include:

- Ghost
- Medium
- Dev.to
- Hashnode
- Blogger
- Static site generators
- Internal CMS platforms

## Goal

A user who creates content in QUILL should be able to publish, edit, and maintain that content without ever needing to leave QUILL.



---

## #251 — Suggestion: Export to DAISY talking book

**Labels:** (none)

Ability to export a document (hopefully already Markdown or HTML) to a text-only DAISY talking book suitable for reading on a player like Victor Stream or some of the Plextalk/APH units which can read text-only DAISY books, or for opening in something like APH Book Wizard Producer to use TTS to create a full text/audio book. If it's decided that this goes beyond the project vision, no worries, it's just a suggestion.
