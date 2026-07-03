# Editor Control Surface Analysis

Date: 2026-07-03. Written after the two startup crashes found while A/B testing
surfaces (the relaunch stdlib-shadowing crash and the RichTextCtrl selection
crash). This maps each of the six `experimental_editor_surface` choices against
QUILL's feature set, the risk each carries, and the changes each would need to
be safe. File is for review; not linked from docs.

## The contract QUILL assumes of the editor

Every feature that touches text goes through `self.editor` and assumes the
wx.TextCtrl API and semantics:

- Value: `GetValue`, `ChangeValue`, `SetValue`, `GetRange`, `IsEmpty` -- LF-only
  text, offsets that match Python string indices into `GetValue()`.
- Caret and selection: `GetInsertionPoint`, `SetInsertionPoint`, `GetSelection`
  returning an `(start, end)` tuple with `(caret, caret)` when empty,
  `SetSelection`, `GetStringSelection`, `ShowPosition`, `GetLastPosition`.
- Editing: `WriteText` at caret, `AppendText`, `Replace`, `Remove`, `Clear`.
- State: `IsModified`, `SetModified`, `MarkDirty`, `DiscardEdits`,
  `SetEditable`, `IsEditable`, `Undo`, `Redo`, `CanUndo`, `CanRedo`.
- Geometry: `PositionToXY`, `XYToPosition`, `GetNumberOfLines` (go-to-line,
  line-oriented commands).
- Events (bound in `_bind_editor_events`): `EVT_TEXT` (dirty tracking, word
  count, Reveal Codes idle sync), `EVT_CHAR_HOOK` (describe-key, Ctrl+K insert
  link, SET-4 typography autoformat, extend-selection Escape), `EVT_KEY_DOWN` /
  `EVT_KEY_UP` (QUILL key chords, typing echo, dictation hotkeys),
  `EVT_LEFT_UP` + `EVT_SET_FOCUS` (caret-activity announcements, status bar,
  braille refresh), `EVT_CONTEXT_MENU`.
- Accessibility: the control must report its value, caret, and selection
  through IAccessible/UIA so JAWS and NVDA read and track it, and so braille
  displays follow the caret. This is the reason rich2 is the default (#616).

Features that consume this contract, grouped by what breaks when part of the
contract is missing:

- Offset-anchored: bookmarks and last-cursor memory, inline notes, hidden
  formatting codes and Illuminations, wikilink resolution (Vault), search and
  replace, spell/grammar fix-ups, AI change previews (one `Replace`, one undo
  step), read-aloud position tracking.
- Type-time: typography autoformat (smart quotes/dashes), Quillin smart
  triggers and abbreviations, describe-key, typing echo, QUILL key chords.
- Continuous: status bar cells (selection, stats), Reveal Codes sync, braille
  status line, caret-move formatting announcements.

The two crashes this week were both contract drift: a surface that returned a
different `GetSelection` shape took the app down before first paint. Anything
below rated Medium or higher should get a parametrized contract test (same
assertions, run against each surface with real wx) before we lean on it.

## 1. default -- follow the Accessibility setting

- Classes: none of its own; delegates to whatever `editor_control_kind`
  resolves to (rich2, rich, or plain below).
- What it is: not a surface. Applies whatever `editor_control_kind` says
  (rich2, rich, or plain -- the braille A/B knob from #616/#813).
- Feature impact: none of its own; inherits the target surface's behavior.
- Risk: none beyond the chosen target. This is the correct resting state for
  everyone not actively testing.
- Changes required: none. Keep it first in the choice list and keep the
  explainer text current.

## 2. rich2 -- RichEdit 3.0 (RICHEDIT50W), the shipping default

- Classes: Python `wx.TextCtrl`; Win32 window class `RICHEDIT50W`
  (msftedit.dll -- the modern RichEdit engine).
- What it is: `wx.TextCtrl` with `TE_RICH2 | TE_NOHIDESEL`.
- Undo/redo: native multi-level undo AND redo (`CanRedo`/`Redo` work).
- Feature impact: the baseline. Every feature above was built and tested on
  this surface. Multi-level native undo. No practical size limit. Correct
  IAccessible value reporting (#616).
- Known issues: braille cell-two offset on some displays (the long-standing
  Word quirk); #813 (JAWS braille not showing dots 7-8 on selection) is
  suspected to live here -- that is the open investigation driving this A/B.
- Risk: Low. It is the control everything is calibrated against.
- Changes required: none. If #813 confirms RICHEDIT50W as the cause, the fix
  is likely a UIA/IAccessible selection-reporting workaround here, not a
  default-surface change.

## 3. rich -- RichEdit 2.0 (RICHEDIT20W)

- Classes: Python `wx.TextCtrl`; Win32 window class `RICHEDIT20W`
  (riched20.dll -- the older RichEdit engine).
- What it is: `wx.TextCtrl` with `TE_RICH | TE_NOHIDESEL`; same wx wrapper,
  older native engine.
- Undo/redo: native multi-level undo and redo, same as rich2.
- Feature impact: near-identical to rich2. All contract methods behave the
  same through wx. Differences are engine-internal: older IME handling, some
  formatting/measurement differences we do not use (buffer is plain text).
- Risk: Low-Medium. The risk is not breakage but subtle screen-reader and
  braille differences -- which is exactly why it exists (a comparison point for
  #813). Undo depth and limits match rich2 for our usage.
- Changes required: none to function. Worth capturing JAWS/NVDA/braille
  behavior notes per screen reader once, so the A/B results are recorded
  rather than re-discovered.

## 4. plain -- Notepad-style EDIT via wx.TextCtrl

- Classes: Python `wx.TextCtrl`; Win32 window class `EDIT` (user32 -- the
  classic multiline edit control, same class Notepad used for decades).
- What it is: `wx.TextCtrl` with `TE_MULTILINE` only; wx hosts the classic
  Win32 EDIT class.
- Feature impact: all contract methods work because wx still mediates.
  Two real semantic differences:
  - Undo is single-level and there is NO redo at all. The native EDIT
    control has one undo slot that toggles (undo of the undo is the "redo"),
    and `CanRedo` reports false on this class. `MainFrame.undo()` routes to
    `editor.Undo()`, so an AI preview apply followed by any keystroke leaves
    only the keystroke undoable, and nothing is redoable. This is the largest
    hidden feature regression on this surface and users will not expect it.
    Fixing it properly means an app-level undo/redo engine (see the undo/redo
    note after the rankings) -- real engineering, not a wrapper.
  - No visual rich rendering (QUILL's hidden-codes design makes this mostly
    moot; formatting still round-trips through Illuminations/export).
  - wx raises the EDIT text limit for us, so large documents are fine, but
    very large buffers repaint slower than RichEdit.
- Accessibility: excellent -- native EDIT is the best-understood control for
  every screen reader and avoids the braille cell-two offset entirely. That is
  why it is the #813 A/B candidate.
- Risk: Medium, dominated by the single-level undo. Everything else is solid.
- Changes required if it were ever more than a test knob:
  - A document-level undo stack in QUILL (or a guard that warns when an AI /
    multi-step change is about to become un-undoable).
  - A note in the explainer text about undo depth (it currently says "all
    core editing works" without the undo caveat).

## 5. rtf -- wx.RichTextCtrl (experimental)

- Classes: Python `quill.ui.rtf_edit_surface.RtfEditorSurface`, a subclass of
  `wx.richtext.RichTextCtrl`. There is no native text-control window class
  underneath -- the Win32 class is a generic wx window, which is exactly why
  screen readers do not recognize it as a text field.
- What it is: wx's own rich text widget. Crucially, it is NOT a native Windows
  control -- wx draws the text itself.
- Undo/redo: multi-level via wx's own command processor, but grouping
  semantics differ from RichEdit (AI one-step-undo unverified).
- Feature impact today (after this week's fix wrapped `GetSelection`):
  - Value/caret basics work (`GetValue`/`ChangeValue`/insertion point), so
    typing, dirty tracking, word count, and Reveal Codes sync function.
  - Still divergent from the contract: `PositionToXY`/`XYToPosition` and
    `HitTest` have different shapes/semantics (go-to-line and line-oriented
    commands are suspect); `Replace` goes through its own command processor
    (undo grouping of AI previews unverified); styling APIs differ entirely.
  - Its selection-empty convention was `(-2, -2)` where TextCtrl says
    `(caret, caret)` -- the class of mismatch that crashed the status bar. We
    fixed the one we hit; the remaining API surface has not been audited.
- Accessibility: this is the disqualifying risk. Because the control is
  wx-drawn, it does not present as a native EDIT/RichEdit to JAWS/NVDA.
  Value, caret, and selection reporting depend on wx's generic accessibility
  layer, which is historically weak on Windows. Braille tracking is unlikely
  to work at all. For a screen-reader-first product, this surface currently
  contradicts the product's core promise.
- Risk: High. Both on the API-contract axis (proven by this week's crash) and
  on the accessibility axis (structural, not fixable by a wrapper).
- Changes required to make it viable (large):
  - Full contract-shim layer (selection done; PositionToXY/XYToPosition,
    HitTest, undo grouping, modified-state semantics).
  - A UIA provider or wxAccessible implementation that reports text pattern,
    caret, and selection -- essentially the same class of work as the Table
    Studio native provider, but for a text control. Until then it should stay
    double-gated exactly as it is, with the explainer stating plainly that
    screen readers may not track it.
  - Parametrized surface contract tests.

## 6. win32 -- raw Win32 EDIT hosted via pywin32 (spike)

- Classes: Python `quill.ui.win32_edit_surface._Win32EditHost` (a `wx.Window`
  host); the child is a raw Win32 `EDIT` window class created directly with
  CreateWindowEx, driven by SendMessage.
- What it is: a `wx.Window` hosting a genuine EDIT child created with
  CreateWindowEx; messages bridged by hand (`win32_edit_surface.py`).
- Undo/redo: single-level native undo (WM_UNDO), no redo -- same EDIT-class
  limitation as plain, plus the bridge exposes no redo API at all.
- Feature impact (documented in the spike, confirmed by reading the bridge):
  - Works: typing, native selection, GetValue/SetValue with CRLF<->LF
    translation, dirty tracking via the EN_CHANGE wndproc bridge, status bar
    (its `GetSelection` returns a proper tuple), clipboard, native single
    undo.
  - Bypassed entirely: `_bind_editor_events` takes the `bind_editor_events`
    fast path, so NO wx key events reach QUILL. Describe-key, typography
    autoformat, Quillin smart triggers, typing echo, QUILL key chords, the
    extend-selection Escape, and the context-menu handler are all inert while
    focus is in the native child. Frame accelerators may also be swallowed --
    untested.
  - Offset math: caret/selection offsets are in the control's CRLF space
    while QUILL's buffer is LF. Every offset-anchored feature (bookmarks,
    inline notes, hidden codes, wikilinks, spell fix-ups, AI previews) is off
    by one per preceding newline. This corrupts positions silently -- worse
    than crashing.
  - `EM_GETSEL` packed return clamps around 64K, so caret reporting in large
    documents is approximate; the spike never raises the EDIT text limit, so
    very large documents may truncate on load.
  - `SetWindowLong(GWL_WNDPROC)` is fragile on 64-bit (needs the Ptr variant);
    the bridge already swallows failure, which silently downgrades dirty
    tracking.
- Accessibility: the child EDIT itself is perfectly readable by screen
  readers (same class as Notepad), but focus handoff between the wx host and
  the native child is hand-rolled -- tab order, focus announcements, and the
  editor's accessible name need real screen-reader validation.
- Risk: High for any real use; acceptable only as the spike it is. The
  offset skew is the dangerous part because it corrupts saved anchors without
  any error.
- Changes required to graduate it (effectively a rewrite):
  - LF<->CRLF offset translation on every position API (both directions).
  - `EM_EXGETSEL`-style selection retrieval or buffer-based math to remove
    the 64K clamp; `EM_SETLIMITTEXT` on creation.
  - A key bridge (WM_KEYDOWN/WM_CHAR forwarding) so type-time features and
    chords work, or explicit in-app messaging that they do not.
  - `SetWindowLongPtr` via ctypes for the wndproc; focus/name accessibility
    audit.
  - Given that surface 4 (plain) IS the same EDIT control with all of this
    already solved by wx, the honest conclusion is that this spike has told
    us what it cost and "plain" is the better vehicle for everything it
    offers. Recommend keeping win32 only as a reference implementation.

## 7. stc -- Scintilla, the "Notepad++ experiment" (added 2026-07-03)

- Classes: Python `quill.ui.stc_edit_surface.StcEditorSurface`, a subclass of
  `wx.stc.StyledTextCtrl`; Win32 window class `Scintilla` (the Notepad++
  engine). Wired into the Experimental combo as "Notepad++ experiment
  (Scintilla, wx.stc.StyledTextCtrl)".
- What it is: a real windowed native-ish control (not wx-drawn like rtf),
  built for editing. The only alternative surface that natively answers the
  multi-level undo/redo concern.
- Undo/redo: full multi-level undo AND redo, native to the engine.
- Probe results (2026-07-03, wxPython on this machine): StyledTextCtrl
  implements the whole TextCtrl-compatible API QUILL needs -- tuple
  `GetSelection` with `(caret, caret)` when empty, `GetRange`, `Replace`,
  `PositionToXY`, modified-state via save point. Four contract gaps were
  found and are shimmed in `stc_edit_surface.py`:
  - `wx.EVT_TEXT` never fires natively (only `EVT_STC_CHANGE`), which would
    kill dirty tracking, word count, and Reveal Codes sync. The wrapper
    forwards every change as a `wxEVT_TEXT` event.
  - `ChangeValue` fires change notifications and leaves the buffer reported
    modified -- a freshly opened document would look dirty. The wrapper
    suppresses forwarding and sets the Scintilla save point on load.
  - `SetInsertionPoint` moves the caret but leaves the selection anchor
    behind, so the next `WriteText` would replace the dragged selection
    (probe-confirmed). The wrapper routes through `GotoPos`.
  - Line endings pass through unconverted (CRLF default). The wrapper pins
    LF, converts on load, and converts pasted text.
- Accessibility: the open question, and the point of the testing round.
  NVDA supports Scintilla well (it drives Notepad++ daily). JAWS support is
  partial and braille routing is less proven than EDIT/RichEdit. Needs the
  same JAWS/NVDA/braille pass as the other candidates before any promotion.
- Caret-tracking experiment (2026-07-03, tried and REVERTED): live JAWS
  testing showed Enter advanced the buffer but JAWS stayed on the old line.
  The first fix mirrored an invisible Windows system caret (the ScintillaWin
  technique) -- and made things worse: with a caret present, JAWS switched
  from its screen-content fallback into live-edit-control mode, queried the
  window for its text, got nothing back, and went silent. Reading the real
  ScintillaWin.cxx (the Scintilla Notepad++ ships) explains why: the caret
  mirror is only one third of its accessibility story. It also (a) answers
  WM_GETTEXT, WM_GETTEXTLENGTH, EM_GETSEL, EM_EXGETSEL, and EM_LINEFROMCHAR
  at its window proc, so screen readers can pull text and selection through
  the classic channels, and (b) registers the recognizable "Scintilla"
  window class that JAWS/NVDA key dedicated support off. wx's port provides
  none of the three: its own window class, no system caret, and a window
  proc that answers no text queries. Caret alone = silence. To graduate,
  this surface needs a ctypes window-proc bridge answering those messages
  PLUS the caret mirror, or a UIA TextPattern provider. Licensing is not
  the obstacle (Scintilla is permissively licensed; Notepad++ is GPL-3.0,
  so we learn from it, we do not copy from it) -- the effort and JAWS's
  window-class heuristics are.
- Risk: Medium. The API contract is in good shape (probed, shimmed, gated,
  with the wx.TextCtrl fallback), so the risk concentrates entirely in
  screen-reader and braille behavior.
- Changes still open if it graduates: verify styling hooks if we ever want
  visual spell-check squiggles (Scintilla indicators are good at this), and
  confirm IME/dead-key behavior.

## Preference ranking

Ranked for QUILL's audience (screen-reader-first, data integrity above all):

| Rank | Surface | Class | Risk | Verdict |
|------|---------|-------|------|---------|
| 1 | default | (delegates) | none | correct resting state |
| 2 | rich2 | wx.TextCtrl / RICHEDIT50W | low | shipping default |
| 3 | plain | wx.TextCtrl / EDIT | medium | best braille; loses multi undo/redo |
| 4 | rich | wx.TextCtrl / RICHEDIT20W | low-medium | A/B comparison point only |
| 5 | stc | StcEditorSurface / Scintilla | medium | testing round; only surface with native redo |
| 6 | rtf | RtfEditorSurface (wx-drawn) | high | testing only; SR-invisible |
| 7 | win32 | _Win32EditHost + raw EDIT | high | reference only; silent offset skew |

Placement note for stc: it enters at rank 5 pending screen-reader evidence.
If the JAWS/braille pass comes back clean it arguably belongs at rank 3 --
it would beat plain by keeping multi-level undo/redo -- but it does not get
that rank on promise.

Reasoning for the close calls:

- plain over rich: rich exists only as an engine-comparison point for #813;
  plain has a genuine end-user story (best braille behavior). If #813 lands
  on "RICHEDIT50W is the culprit," plain is the realistic fallback, so it
  outranks rich despite the undo/redo cost.
- rtf over win32: neither is usable, but rtf fails loudly (screen readers
  cannot read it -- users notice immediately), while win32 fails silently
  (offsets skew in CRLF space and corrupt bookmarks/notes/codes without any
  error). Silent data corruption is the worse failure mode; win32 ranks last.

## Undo/redo across surfaces (the multi-redo concern)

- rich2 / rich: native multi-level undo AND redo from the RichEdit engine.
  This is the only place QUILL gets real redo today, and it is free.
- plain / win32: the EDIT class has a single toggling undo slot and no redo.
  `CanRedo` is false; there is nothing to wire up.
- rtf: multi-level undo/redo exists but lives in wx's own command processor
  with different grouping rules.

You are right that fixing this outside the control is heavy engineering: an
app-level undo/redo engine means intercepting every mutation path (typing via
native WM_CHAR, paste, dictation, AI Replace, spell fix-ups, Quillin inserts),
snapshotting or delta-encoding each, and keeping QUILL's stack coherent with
the native one the control still runs internally -- plus braille/SR
announcements for undo/redo state. Estimate: a dedicated milestone, not a
patch. Practical position: staying on the RichEdit surfaces preserves
multi-level undo/redo for free, and that is a strong argument for solving
#813 *inside* rich2 (selection-reporting workaround) rather than migrating
the default to plain. If plain ever must become the default, the undo engine
should be scoped as its own project first.

## Other surfaces worth considering (not currently wired)

Scintilla previously led this list; it is now wired as surface 7 above
("Notepad++ experiment"). Remaining candidates:

- WebView2 + contenteditable (or a JS editor like ProseMirror) hosted in the
  `wx-accessible-webview` dependency QUILL already ships. Chromium exposes a
  full UIA text pattern, so JAWS/NVDA/braille support is first-class, and
  editor libraries bring multi-level undo/redo. Cost: an IPC boundary between
  QUILL's offset-anchored features and the DOM, focus handoff, latency, and a
  rewrite of the editor contract layer. Strategic option, not a knob -- but
  the only path that gives modern rich rendering AND accessibility AND redo.
- WinUI 3 RichEditBox via XAML island. Same msftedit lineage as rich2
  (RichEditD2D), so it likely inherits the same #813 behavior while adding
  heavy hosting machinery. Not recommended; listed for completeness.
- Fully custom surface with a UIA TextPattern provider (the Word / VS Code
  approach). Total control, total cost -- months of provider work like the
  Table Studio native provider but far larger. Only justified if every native
  option fails the braille requirement.

## Recommended next steps

1. Add a parametrized surface contract test: one set of assertions
   (selection tuple shape, empty-selection convention, offset round-trip
   through a multi-line buffer, undo after Replace) instantiated against
   rich2, rich, plain, and rtf with real wx. This week's two crashes would
   both have been caught by it.
2. Document the single-level undo caveat in the plain surface explainer.
3. Keep rtf and win32 double-gated; update the rtf explainer to state the
   screen-reader limitation explicitly.
4. Decide #813 on the rich2 vs plain A/B evidence, then fold the finding back
   into `editor_control_kind` guidance rather than growing the experimental
   list.
