# Backlog review: remaining open issues

## Follow-up from #892

- **DOCX/RTF native header/footer export**: the Header/Footer Builder authors and saves a spec, and draws it when printing, but does not yet write real header/footer XML into DOCX/RTF exports. Deliberately deferred per the issue's own build order (confirm the round-trip once real usage exists to validate against).

## #893 — "Rich Document" workflow discoverability — **P3**

**State:** The Rich Text lens already exists and works — `core.rich_text_lens` (`feature_catalog.py:~149`), wired to `view.switch_editing_lens`, locked_off under at least one profile (`settings.py:~595`). This is discoverability/framing, not a build.

**Proposal:** Surface "Rich Document" as a plain-language onboarding choice (first-run wizard and/or profile-adjacent setting) for users who want WordPad-like editing without learning Markdown — framed as an experience, not as "enable the Rich Text lens flag." Add an in-context "Switch to Rich Document view" affordance (menu + command palette) for users mid-session. Audit which profiles lock the lens off and confirm that's still right if it's being promoted.

**Non-goals:** Not changing the underlying Markdown-with-invisible-codes architecture; not making Rich Text the default for everyone.

**Priority:** P3 — **explicitly downgraded per the issue's own re-check.** QUILL's plain-text/Markdown default *is* the screen-reader-optimized design, not a way-station to a "real" rich mode. This mainly serves a secondary audience (low-vision, sighted co-authors, ex-Word/WordPad users). Real and worth doing — the feature already exists so the cost is low — but it's a "nice for a secondary audience," not a core-mission gap like #891 or #899.

## Suggested sequencing

1. **#893** — the one remaining item; low-urgency discoverability polish, fold into whatever onboarding-wizard work is already happening rather than scheduling standalone.

