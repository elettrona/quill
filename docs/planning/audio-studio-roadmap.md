# Audio Studio: The Road to Feature Complete

## Tier 1 — Merge gate: prove what shipped is true

### 1. Real screen-reader validation (JAWS, then NVDA)

**What:** Walk every new surface with JAWS on real hardware: the wizard
(focus landing on each page change, step announcements, the radio-driven
journey switch, Skip to summary), the Chapter Workbench (list refresh after
each surgery operation, the title edit flow, button states), the player
(transport labels, spoken position slider, chapter-crossing announcements,
Where am I?), and the Publish dialog. Fix what your ears find.

**Outcome:** The feature's core promise — screen-reader-first audiobook
production — is verified by the person it was built for, not just by the
dialog gates. This is the merge gate for PR #839; nothing below matters
until it passes.

### 2. End-to-end run on real audio, especially M4B playback

**What:** One complete journey on real files: narrate a folder into an M4B,
open it in the Workbench, play it, split a chapter at the playhead, save as,
verify in a podcast app. The single riskiest assumption on the branch is
that the wx.media WMP backend loads and seeks M4B reliably; it has only been
exercised by unit tests with stubbed transports.

**Outcome:** Either confidence that the zero-dependency playback engine is
good enough to ship, or an early, cheap discovery that the libmpv backend
(already implemented — drop a `libmpv-2.dll` into `engine-packs\mpv` to use
it today; hosting tracked in `roadmap.md` §1.8) must become the default.
Also shakes out ffmpeg-path issues no unit test can see.
