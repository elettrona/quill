# Publishing Profile Restriction ("Writer and Above") — Scoping Plan

## Status

**Implemented 2026-06-22**, same day as the scoping. The two open
questions in "Open questions / flagged assumptions" below were resolved
before coding: soft restriction (Recommended option chosen) and
`FEATURE_STATE_ON` (Recommended option chosen) for the included profiles.
The third open question (timing) was resolved by the user asking to begin
coding immediately — landed now, while still inert behind
`future.publishing`'s `locked_off=True`.

Implementation: `quill/core/features.py`'s `PROFILE_DEFINITIONS` now match
the table below exactly (`author_or_student`'s previously-absent key was
added, not left as an implicit default). `quill/core/feature_catalog.py`'s
`future.publishing` description was extended to state the restriction.
No UI/menu/palette code changed, confirmed unnecessary as predicted.
Two new tests added to `tests/unit/core/test_publishing_framework.py`:
`test_publishing_profile_states_match_writer_tier_and_above` (the
configured values) and `test_publishing_profile_states_are_overridden_by_the_lock`
(the regression test guarding the lock/profile interaction). Module-size
budget for `features.py` bumped 727->738. Full suite, scoped mypy, ruff,
provider-registry gate, and a smoke launch all clean — see
`codex-notes/logs/publishing-providers-framework-current-work-log-2026-06-19.md`'s
matching 2026-06-22 entry for full validation numbers.

The rest of this document is preserved as written during scoping, for
the historical record of what was decided and why.

## Context

The user was told (by someone above them in the project) that the
publishing feature must only be available in "writer and above"
profiles. This is a separate, additive requirement from the existing
`future.publishing` `locked_off=True` review-gate lock added 2026-06-22
(see `codex-notes/logs/publishing-providers-framework-current-work-log-2026-06-19.md`'s
"Locked publishing off behind the existing feature flag" entry) to keep
publishing out of the public release until this branch's PR is reviewed.

The two are independent and stack:

- **The `locked_off` lock** is the master kill switch. While it's `True`,
  `FeatureManager.state_for("future.publishing")` returns
  `FEATURE_STATE_OFF` unconditionally, for every profile, with no
  exceptions — it is checked before any profile is ever consulted.
- **This profile restriction** describes the feature's *intended
  configuration once that lock is eventually lifted* — which profiles
  should see/use publishing by default once it's actually live. It has
  zero user-visible effect today and will continue to have zero effect
  for as long as `locked_off=True` remains in place.

Do not confuse "configuring the profile states correctly" with "lifting
the review-gate lock." They are two separate decisions; this plan only
scopes the first.

## Decided scope

QUILL's 10 feature profiles (`quill/core/features.py`,
`PROFILE_DEFINITIONS`) have **no existing tier or rank** — they're
independent personas (Essential, Casual Writer, Author or Student, Reader
and Student, Office and Admin, Developer and Power Text, Low Vision,
Braille and Screen Reader Power User, Accessibility Professional, Full
Quill), not a capability ladder. "Writer and above" therefore has no
formal, pre-existing meaning in this codebase. Confirmed directly with
the user (offered three concrete readings; they chose the second):

> **Writer + "serious writing" profiles**: Writer, Author or Student,
> Developer and Power Text, and Full Quill get publishing access.
> Reader and Student, Office and Admin, Low Vision, Braille and Screen
> Reader Power User, and Accessibility Professional are treated as
> different use cases, not a writing-capability tier, and do not get it.
> Essential — the baseline/default profile — does not get it either.

| Profile (id) | Display name | Gets publishing? | Target `future.publishing` state |
| --- | --- | --- | --- |
| `essential` | Essential | No | `FEATURE_STATE_OFF` |
| `writer` | Casual Writer | **Yes** | `FEATURE_STATE_ON` |
| `author_or_student` | Author or Student | **Yes** | `FEATURE_STATE_ON` |
| `reader_and_student` | Reader and Student | No | `FEATURE_STATE_OFF` |
| `office_and_admin` | Office and Admin | No | `FEATURE_STATE_OFF` |
| `developer_power_text` | Developer and Power Text | **Yes** | `FEATURE_STATE_ON` |
| `low_vision` | Low Vision | No | `FEATURE_STATE_OFF` |
| `braille_screen_reader_power_user` | Braille and Screen Reader Power User | No | `FEATURE_STATE_OFF` |
| `accessibility_professional` | Accessibility Professional | No | `FEATURE_STATE_OFF` |
| `full_quill` | Full Quill | **Yes** | already `FEATURE_STATE_ON` — no change needed |

## Current state vs. target state

Read directly from `quill/core/features.py` (lines as of this writing):

- Every profile listed above **except `author_or_student`** already has
  an explicit `"future.publishing": FEATURE_STATE_QUIET` entry in its
  `states` dict (lines 76, 104, 155, 177, 200, 224, 248, 270). All of
  these need to change from `FEATURE_STATE_QUIET` to either
  `FEATURE_STATE_ON` (the 3 included profiles: `writer`,
  `developer_power_text`) or `FEATURE_STATE_OFF` (the 5 excluded
  profiles: `essential`, `reader_and_student`, `office_and_admin`,
  `low_vision`, `braille_screen_reader_power_user`,
  `accessibility_professional` — that's 6, not 5; see the table above for
  the authoritative list).
- `author_or_student`'s `states` dict (lines 116-134) has **no**
  `"future.publishing"` key at all. Today, ignoring the lock, that
  silently falls back to the default `FEATURE_STATE_ON` via
  `state_for()`'s `self.active_profile.states.get(feature_id,
  FEATURE_STATE_ON)` — which happens to already match the target state,
  but as an unintentional gap, not a deliberate choice. The implementation
  should add the key explicitly (`FEATURE_STATE_ON`) so the intent is
  documented in the data rather than relying on an accidental default.
- `full_quill`'s `states` dict is `{feature_id: FEATURE_STATE_ON for
  feature_id in FEATURE_DEFINITIONS}` — a comprehension over every
  registered feature. It already evaluates to `ON` for
  `future.publishing` and needs no change.

## Why no UI/menu code changes are needed

The gating added for the review-gate lock already reads the *live,
active* profile on every call — confirmed by tracing the call chain:

```
main_frame_menu.py:
    if self._feature_enabled("future.publishing"):   # wraps the Publish submenu

MainFrame._feature_enabled (main_frame.py:7082-7086):
    return self.features.is_enabled(feature_id)

FeatureManager.is_enabled (features.py:451-459):
    if self.state_for(feature_id) == FEATURE_STATE_OFF: return False
    ...

FeatureManager.state_for (features.py:436-446):
    if definition.locked_on: return ON
    if definition.locked_off: return OFF          # <- short-circuits today
    if feature_id in self.overrides: return override
    return self.active_profile.states.get(feature_id, ON)   # <- profile-aware
```

The same chain backs `quill/ui/palette.py`'s `is_visible()` (Command
Palette / Go to Anything filtering, via `COMMAND_FEATURE_MAP`). Once
`locked_off` is lifted, both surfaces will automatically respect whichever
profile is active — **no changes are needed in `main_frame_menu.py`,
`quill/ui/palette.py`, or `quill/core/feature_command_map.py`** for the
profile restriction itself. The only source-of-truth file is
`quill/core/features.py`'s `PROFILE_DEFINITIONS`.

## Implementation checklist (for whenever this is actually built)

1. In `quill/core/features.py`, change `"future.publishing"` in these
   `states` dicts:
   - `PROFILE_ESSENTIAL` → `FEATURE_STATE_OFF`
   - `PROFILE_WRITER` → `FEATURE_STATE_ON`
   - `PROFILE_AUTHOR_STUDENT` → **add** `"future.publishing":
     FEATURE_STATE_ON` (key currently absent)
   - `"reader_and_student"` → `FEATURE_STATE_OFF`
   - `"office_and_admin"` → `FEATURE_STATE_OFF`
   - `PROFILE_DEVELOPER_POWER_TEXT` → `FEATURE_STATE_ON`
   - `"low_vision"` → `FEATURE_STATE_OFF`
   - `"braille_screen_reader_power_user"` → `FEATURE_STATE_OFF`
   - `PROFILE_ACCESSIBILITY_PROFESSIONAL` → `FEATURE_STATE_OFF`
   - `PROFILE_FULL_QUILL` — no change (comprehension already yields `ON`)
2. Update `future.publishing`'s `description` in
   `quill/core/feature_catalog.py` to also state the profile restriction
   once it's actually live (today's description only mentions the
   review-gate lock — e.g. append something like "Once enabled, available
   by default in the Casual Writer, Author or Student, Developer and
   Power Text, and Full Quill profiles; off by default elsewhere, but any
   user can still turn it on individually via Manage Individual
   Features.").
3. No changes to `main_frame_menu.py`, `palette.py`,
   `feature_command_map.py`, or any dialog/menu surface (see above).

## Test plan (for whenever this is implemented)

- **Direct profile-data assertions** (independent of the live
  `locked_off` short-circuit — these test the *configured* values):
  for each of the 10 profile ids, assert
  `PROFILE_DEFINITIONS[profile_id].states["future.publishing"]` equals
  the target state in the table above. Natural home:
  `tests/unit/core/test_features.py` or a new test in
  `tests/unit/core/test_publishing_framework.py`.
- **Lock/profile interaction regression test** (important — prevents a
  future session from mistaking "the profile data says ON" for "the
  feature is actually reachable"): with the profile states set as above
  and `locked_off` still `True`, assert
  `FeatureManager(active_profile_id=...).state_for("future.publishing")`
  is `FEATURE_STATE_OFF` for **every** profile, including the 3 that are
  configured `ON`. This documents the lock's precedence explicitly rather
  than leaving it implicit.
- **Once the lock is separately lifted** (a later, distinct change — not
  part of this profile-restriction work):
  - `FeatureManager(active_profile_id=PROFILE_WRITER).is_enabled("future.publishing")`
    is `True`; same for `PROFILE_AUTHOR_STUDENT`,
    `PROFILE_DEVELOPER_POWER_TEXT`, `PROFILE_FULL_QUILL`.
  - `FeatureManager(active_profile_id=PROFILE_ESSENTIAL).is_enabled("future.publishing")`
    is `False`; same for the other 5 excluded profiles.
  - `open_individual_feature_toggles`'s feature list still includes
    `future.publishing` (proves the restriction is a soft per-profile
    default, not a hard lock — see below) once `locked_off` no longer
    excludes it from that screen.

## Open questions / flagged assumptions (confirm before implementing)

These are genuine product decisions, not engineering defaults — flagged
explicitly rather than silently assumed:

1. **Soft vs. hard restriction.** Every profile-scoped feature in this
   catalog today (`future.ai`, `future.character_inspector`,
   `future.cleanup`, and publishing itself) uses a *soft* default: the
   profile sets what's on by default, but `open_individual_feature_toggles`
   lets any user override any non-locked feature regardless of profile.
   There is no existing mechanism in this codebase for a *hard*,
   unoverridable per-profile restriction — building one would be new
   infrastructure, not a data change. **This plan assumes soft**
   (matching every existing precedent). If "only available in writer and
   above" was meant literally — i.e., an Essential-profile user must never
   be able to turn it on even manually — that requires a different,
   larger design and should be raised explicitly before implementing.
2. **`FEATURE_STATE_ON` vs. `FEATURE_STATE_QUIET` for the 3 included
   profiles.** This plan recommends `ON` (fully available, not gated
   behind a separate "show quiet/future features" toggle) since the
   instruction was "available," not "discoverable for advanced users
   only." `QUIET` would mean even Writer-profile users wouldn't see it by
   default without first enabling that separate toggle.
3. **Timing.** This plan doesn't decide *when* to make the
   `features.py` edit — it could land now (harmless and inert while
   `locked_off=True` stays in place) so it's ready the instant the
   review-gate lock is lifted, or it could be deferred until the
   lock-lifting decision is made. That's a separate "when" question for
   the user, not an engineering call.

## Relationship to the rest of the roadmap

This is a refinement of the already-closed publishing-providers-framework
roadmap, not a new roadmap phase. See
`codex-notes/plans/publishing-providers-framework.md` for the full
history; a one-paragraph pointer to this file has been appended there.
