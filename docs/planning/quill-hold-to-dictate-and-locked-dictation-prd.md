# Product Requirements Document: QUILL Push-to-Talk and Locked Dictation

**Product:** QUILL  
**Feature Area:** Whisper Dictation  
**Document Status:** Phase 1 + 2 partially implemented (2026-06-24)  
**Priority:** High  
**Target Platform:** Windows-first, with architecture suitable for future cross-platform support  
**Primary Audience:** QUILL engineering, accessibility, quality assurance, documentation, and release teams  

---

## 1. Executive Summary

QUILL already includes Whisper-based dictation. This project will add a fast, reliable, and highly accessible way to control dictation directly from the keyboard without opening a dialog or changing focus.

The feature will provide two complementary operating modes:

1. **Hold-to-Dictate**
   - The user holds a configurable key, initially **F9**.
   - Recording begins when the key is pressed.
   - Recording ends when the key is released.
   - QUILL transcribes and inserts the result at the saved document location.

2. **Locked Dictation**
   - The user presses **Ctrl+F9** to begin a continuous dictation session without holding a key.
   - QUILL remains in a clearly announced locked dictation state.
   - The user presses **Ctrl+F9** again to stop and transcribe.
   - The user can also press **Escape** as an immediate safety stop.
   - Additional configurable commands may pause, resume, cancel, or finish the session.

The experience must be safe, private, responsive, screen-reader friendly, recoverable after failure, and resistant to missing keyboard events. Dictated speech must never be silently lost or inserted into the wrong document.

The desired experience is:

> Put the caret where text belongs, hold F9 and speak, then release F9. For longer passages, press Ctrl+F9 once, dictate naturally, and press Ctrl+F9 again when finished.

---

## 2. Problem Statement

Traditional dictation interfaces often require users to:

- Open a separate dialog.
- Move focus away from the document.
- Start recording with one command and search for another command to stop.
- Hold a mouse button.
- Navigate visual recording controls.
- Remember whether the microphone is still active.
- Wait without knowing whether transcription is underway.
- Recover manually when transcription or insertion fails.

These problems are especially significant for blind users, keyboard-only users, users with motor disabilities, and users who rely on screen readers.

Whisper transcription may also take time after recording ends. During that delay, a user may change documents, edit nearby text, close the document, or accidentally cause the transcript to be inserted in the wrong location.

QUILL needs a direct and trustworthy dictation workflow that feels like part of the editor rather than an external recording utility.

---

## 3. Product Vision

QUILL dictation should feel immediate, calm, and dependable.

A user should be able to dictate a sentence, paragraph, list item, note, message, or longer passage without leaving the document and without wondering:

- Whether recording actually started.
- Whether the microphone is still active.
- How to stop recording.
- Where the transcript will be inserted.
- Whether the speech was lost.
- Whether a screen reader announcement was recorded.
- Whether dictation remains active after focus changes.
- Whether the feature can be undone.

The feature should be simple by default and richly configurable for users who need different input devices, timing, feedback, privacy, or accessibility behavior.

---

## 4. Goals

### 4.1 Primary Goals

- Provide reliable hold-to-dictate behavior.
- Provide a clearly identifiable locked dictation mode for longer speech.
- Keep keyboard focus in the editor.
- Make all operations fully accessible without sight.
- Prevent lost or indefinitely running recordings.
- Insert text into the intended document location.
- Preserve dictated content when insertion cannot safely occur.
- Keep the QUILL interface responsive during recording and transcription.
- Make the entire inserted transcript undoable as one operation.
- Provide clear, nonintrusive status feedback.
- Avoid recording QUILL’s own start and stop feedback.
- Support configuration without making the default experience complicated.

### 4.2 Secondary Goals

- Support foot pedals, adaptive switches, programmable keyboard keys, and other activation devices in later releases.
- Provide a recovery history for recent dictations.
- Allow future support for partial transcription, spoken punctuation, and command-and-control features.
- Establish a reusable dictation controller architecture for additional speech engines.

---

## 5. Non-Goals for the Initial Release

The first release will not attempt to provide:

- Full voice command-and-control throughout QUILL.
- Automatic document formatting based on arbitrary spoken commands.
- Speaker identification.
- Multi-speaker transcription.
- Cloud-based transcription unless already supported through a separately configured engine.
- Continuous background listening when dictation is not active.
- System-wide insertion into applications other than QUILL.
- Automatic translation.
- Guaranteed verbatim punctuation correction beyond the transcription engine’s output and conservative insertion normalization.
- A replacement for dedicated accessibility voice-control products.

These capabilities may be explored later without complicating the initial experience.

---

## 6. Personas and Core Use Cases

### 6.1 Blind Screen-Reader User

The user writes with JAWS, NVDA, Narrator, or another screen reader. They need clear tones and concise speech messages, no focus movement, no inaccessible visual-only indicator, and no keyboard conflicts with screen-reader commands.

### 6.2 Keyboard-Only User

The user cannot or does not wish to use a mouse. They need predictable start, stop, pause, cancellation, and settings controls.

### 6.3 User with Limited Hand Endurance

The user can press a shortcut but cannot comfortably hold a key for a long passage. Locked Dictation allows continuous recording after a single shortcut.

### 6.4 User Dictating Short Phrases

The user frequently dictates one sentence or phrase at a time. Holding F9 is faster and safer than toggling a persistent recording mode.

### 6.5 User Dictating Long Passages

The user wants to dictate multiple paragraphs, meeting notes, a letter, or a draft. Ctrl+F9 starts Locked Dictation without requiring continuous pressure.

### 6.6 User with an Adaptive Input Device

The user activates commands through a foot pedal, switch, macro pad, or programmable keyboard. The design must allow future mapping of the same logical actions to alternate devices.

---

## 7. Terminology

### Hold-to-Dictate

A momentary dictation mode. Recording remains active only while the configured activation key is physically held.

### Locked Dictation

A persistent dictation mode. Recording begins after a shortcut and continues until the user explicitly stops, pauses, cancels, or reaches a safety limit.

### Activation Key

The key or key combination assigned to Hold-to-Dictate.

### Lock Shortcut

The command that starts or stops Locked Dictation. The proposed default is Ctrl+F9.

### Dictation Session

The complete operation from recording start through transcription, insertion, recovery, cancellation, or failure.

### Insertion Context

The saved document, editor control, caret, selection, revision, and surrounding text information captured when dictation begins.

### Recovery Item

Saved audio, transcript, and metadata retained because insertion did not complete safely or because QUILL exited unexpectedly.

---

## 8. Default Keyboard Commands

| Action | Proposed Default | Behavior |
|---|---|---|
| Hold-to-Dictate | F9 | Hold to record; release to stop and transcribe |
| Start or finish Locked Dictation | Ctrl+F9 | Toggles locked recording on and off |
| Emergency stop | Escape | Stops the active recording immediately |
| Cancel active dictation | Shift+Escape | Stops and discards after confirmation or according to configured behavior |
| Pause or resume Locked Dictation | Ctrl+Shift+F9 | Pauses or resumes audio capture during a locked session |
| Dictation status | Alt+F9 | Announces current state without changing it |
| Open Dictation History | Ctrl+Alt+F9 | Opens recent transcript and recovery history |
| Undo inserted dictation | Ctrl+Z | Removes the full insertion as one undo operation |

Only F9 and Ctrl+F9 are required for the first implementation. The remaining commands are recommended and may be phased in.

All shortcuts must be configurable.

---

## 9. Core User Experience

## 9.1 Hold-to-Dictate

### Starting

When the user presses and holds F9:

1. QUILL validates that a writable editor context is active.
2. QUILL saves the insertion context.
3. QUILL reserves the key event so it is not inserted or passed to another QUILL command.
4. QUILL begins microphone capture.
5. QUILL plays a short rising start tone after the recorder is ready.
6. QUILL displays:
   - `Dictating — release F9 when finished`
7. Screen-reader speech during active recording is minimized to prevent audio contamination.

### Continuing

While F9 remains held:

- Repeated key-down events caused by keyboard auto-repeat do not restart recording.
- QUILL remains responsive.
- No dialog opens.
- Focus remains in the document.
- A visual elapsed timer may update.
- No recurring spoken announcements occur.
- A watchdog verifies that F9 is still physically held.

### Finishing

When the user releases F9:

1. Audio capture stops immediately.
2. The recorder flushes and safely stores the audio.
3. QUILL plays a short falling stop tone only after microphone capture has ended.
4. QUILL announces or displays:
   - `Transcribing dictation…`
5. Whisper runs on a worker thread.
6. The transcript is inserted at the saved location when safe.
7. QUILL announces:
   - `Dictation inserted, 24 words.`
8. The entire insertion can be undone with one Ctrl+Z.

---

## 9.2 Locked Dictation

Locked Dictation is intended for longer passages or users who cannot comfortably hold a key.

### Starting Locked Dictation

When the user presses Ctrl+F9 while no dictation session is active:

1. QUILL validates that the current editor can accept text.
2. QUILL saves the insertion context.
3. QUILL begins microphone capture.
4. QUILL enters `LOCKED_RECORDING`.
5. QUILL plays a distinctive locked-start tone that differs from the Hold-to-Dictate tone.
6. After the microphone is active, QUILL provides a concise announcement:
   - `Locked dictation on. Press Control F9 to finish. Escape stops.`
7. The status bar displays:
   - `Locked dictation — Ctrl+F9 to finish; Escape to stop`
8. A persistent but nonintrusive visual indicator is shown.
9. Screen-reader users can press Alt+F9 at any time to hear the current status.

### Finishing Locked Dictation

When the user presses Ctrl+F9 again:

1. Audio capture stops.
2. The recording is finalized and saved to temporary recovery storage.
3. QUILL plays the locked-stop tone after capture ends.
4. QUILL changes to `TRANSCRIBING`.
5. Whisper transcribes on a worker thread.
6. QUILL inserts the result at the saved insertion context or preserves it for review.
7. QUILL announces the result.

### Emergency Stop

Escape must always provide a predictable way out.

Default behavior:

- During active recording, Escape **stops recording and keeps the captured speech for transcription**.
- Escape does not silently discard speech.
- QUILL announces:
  - `Dictation stopped. Transcribing captured speech.`

This is safer than making Escape discard content.

A separate command, such as Shift+Escape, may cancel and discard.

### Pause and Resume

Ctrl+Shift+F9 may pause Locked Dictation.

When paused:

- QUILL stops adding microphone samples to the session.
- Existing audio remains safe.
- QUILL announces:
  - `Dictation paused.`
- The status bar displays:
  - `Locked dictation paused — Ctrl+Shift+F9 to resume`
- Ctrl+F9 still finishes the session.
- Escape still stops the session.

When resumed:

- QUILL plays a brief resume tone.
- QUILL announces:
  - `Dictation resumed.`

Pause and resume may be deferred until a later phase if audio engine behavior makes safe pausing difficult. In that case, finishing the current segment and starting another is preferable to unreliable pause behavior.

---

## 10. Lock Mode Safety and Privacy Requirements

Locked Dictation creates a greater risk of unintentionally leaving the microphone active. The following protections are mandatory.

### 10.1 Distinct State

Locked Dictation must have a separate state from Hold-to-Dictate. It must never be represented only by a Boolean such as `is_recording`.

### 10.2 Persistent Status

At least one visual indicator and one nonvisual status command must remain available throughout the session.

### 10.3 Focus-Loss Policy

Default behavior:

- If QUILL loses foreground focus during Locked Dictation, recording stops and the captured audio is preserved for transcription.

Optional setting:

- Continue recording while QUILL is not foreground.

The continue-in-background option must be off by default and include a clear privacy explanation.

### 10.4 Modal Dialog Policy

If a modal dialog opens while Locked Dictation is active:

- QUILL stops recording and preserves the speech, unless the dialog is a known dictation-owned interface explicitly designed to coexist with recording.

### 10.5 Maximum Duration

The default maximum locked recording duration should be five minutes.

Configurable options may include:

- 1 minute
- 3 minutes
- 5 minutes
- 10 minutes
- 15 minutes
- Unlimited

When the limit is reached:

1. QUILL stops recording automatically.
2. QUILL preserves and transcribes the session.
3. QUILL announces:
   - `Maximum dictation time reached. Recording stopped and is being transcribed.`

Unlimited mode must include a privacy warning.

### 10.6 Idle Speech Detection

Optional future behavior:

- Warn after an extended period of silence.
- Stop after a user-configured silence duration.

This must not be enabled by default until thoroughly tested because natural pauses should not unexpectedly terminate dictation.

### 10.7 Application Shutdown

If QUILL closes while recording:

1. Stop audio capture.
2. Save recoverable audio and metadata.
3. Do not wait indefinitely for transcription.
4. Offer recovery on the next launch.

### 10.8 System Suspend, Lock, or Session Change

On Windows workstation lock, sleep, remote-session disconnect, or audio-device loss:

- Stop recording.
- Save captured audio.
- Mark the session as interrupted.
- Offer transcription or recovery when QUILL becomes available again.

### 10.9 Explicit Microphone Ownership

QUILL must clearly report when the microphone cannot be acquired because another application or device owns it.

---

## 11. State Machine

The controller must use an explicit state machine.

Recommended states:

```text
IDLE
VALIDATING
STARTING
HOLD_RECORDING
LOCKED_RECORDING
PAUSED
STOPPING
SAVING_AUDIO
TRANSCRIBING
INSERTING
REVIEW_REQUIRED
COMPLETED
CANCELLED
FAILED
RECOVERING
```

### Valid High-Level Transitions

```text
IDLE
  -> VALIDATING
  -> STARTING
  -> HOLD_RECORDING
  -> STOPPING
  -> SAVING_AUDIO
  -> TRANSCRIBING
  -> INSERTING
  -> COMPLETED
  -> IDLE
```

```text
IDLE
  -> VALIDATING
  -> STARTING
  -> LOCKED_RECORDING
  -> PAUSED
  -> LOCKED_RECORDING
  -> STOPPING
  -> SAVING_AUDIO
  -> TRANSCRIBING
  -> INSERTING
  -> COMPLETED
  -> IDLE
```

Failure from any active state may transition to:

```text
FAILED
  -> RECOVERING
  -> REVIEW_REQUIRED or IDLE
```

No two recording states may be active simultaneously.

---

## 12. Behavior When Commands Overlap

### F9 Pressed During Locked Dictation

Default:

- F9 does not begin a second recording.
- QUILL plays a subtle invalid-action tone or announces only on request.
- The status remains Locked Dictation.

Optional future behavior:

- F9 temporarily pauses while held or marks a segment boundary.

This should not be included initially because it adds complexity.

### Ctrl+F9 Pressed During Hold-to-Dictate

Default:

- Ignore the lock toggle until the held key is released.
- Do not convert the active session into Locked Dictation.

Optional setting:

- `Promote hold session to locked mode`

If implemented later, pressing Ctrl+F9 while holding F9 would allow the user to release F9 and continue recording. This could be magical, but it requires extremely clear feedback and should not be part of the minimum viable release.

### Starting Dictation During Transcription

Default:

- Allow a new recording session if the recorder and transcription architecture can safely support it.
- Queue transcripts in session order.
- Each session retains its own insertion context.

If concurrency is not initially supported:

- Play a brief unavailable tone.
- Announce:
  - `The previous dictation is still being transcribed.`

The interface must never freeze.

---

## 13. Keyboard Event Architecture

## 13.1 QUILL-Focused Mode

The first implementation should work whenever QUILL is the foreground application.

Recommended wxPython mechanisms:

- Application-level or main-frame event filtering.
- `wx.EVT_CHAR_HOOK` for early interception.
- `wx.EVT_KEY_DOWN` and `wx.EVT_KEY_UP` where needed.
- Raw key codes rather than translated character input.
- Explicit auto-repeat rejection.
- A physical key-state watchdog while Hold-to-Dictate is active.

### Key-Down Rules

- The first matching key-down begins Hold-to-Dictate.
- Additional auto-repeat key-down events are ignored.
- The activation key is consumed.
- Unrelated keyboard events continue normally.

### Key-Up Rules

- The matching key-up ends Hold-to-Dictate.
- A key-up without an active held session is ignored.
- Key-up handling must remain available even if the editor control changes internally.

## 13.2 Optional Windows Global Hook

A later phase may use a native Windows low-level keyboard hook to receive reliable key-down and key-up transitions.

The hook callback must only:

- Identify the configured key.
- Record a timestamp.
- Place a lightweight event in a thread-safe queue.
- Return immediately.

It must never:

- Start Whisper.
- Access the document.
- Open the microphone.
- Make accessibility announcements.
- Perform file access.
- Wait on the UI thread.

The UI thread remains responsible for state transitions.

## 13.3 Missing Key-Up Recovery

While Hold-to-Dictate is active, a timer should periodically verify physical key state.

If the activation key is no longer down and no key-up event was received:

- Treat the state as a release.
- Stop recording.
- Preserve and transcribe the captured audio.
- Log the recovered missing-key-up event.

This protection is mandatory.

---

## 14. Audio Capture Requirements

### 14.1 Start Latency

QUILL should minimize the delay between activation and actual audio capture.

The feature should:

- Open the configured input device quickly.
- Begin collecting audio before playing any spoken feedback.
- Optionally support prewarming the audio device.
- Optionally support a short local pre-roll buffer.

### 14.2 Stop Order

The stop sequence must be:

1. Stop accepting microphone samples.
2. Flush and close the recording segment.
3. Verify that recoverable audio exists.
4. Play the stop tone.
5. Begin transcription.

This prevents the stop tone from entering the recording.

### 14.3 Audio Format

Use a stable transcription-friendly format, such as:

- Mono PCM WAV
- 16 kHz or the engine’s preferred sample rate
- Consistent sample width
- No lossy intermediate encoding unless required

### 14.4 Audio Device Failure

If the microphone disconnects or fails:

- Preserve all audio already captured.
- Stop the session.
- Notify the user after capture has ended.
- Offer to transcribe the partial recording.
- Log device and driver details without storing sensitive audio content in ordinary logs.

### 14.5 No Background Listening

QUILL must not retain or save audio outside an active dictation session.

Any optional pre-roll buffer must:

- Remain in memory.
- Be very short.
- Never be persisted unless dictation is activated.
- Be clearly documented and configurable.

---

## 15. Transcription Requirements

### 15.1 Nonblocking Operation

Whisper transcription must run outside the wxPython UI thread.

The editor must remain usable while transcription occurs.

### 15.2 Session Identity

Every dictation receives a unique session identifier.

The session record includes:

- Session ID
- Dictation mode
- Start and stop time
- Document identity
- Saved caret and selection
- Document revision
- Audio path
- Transcription state
- Insertion state
- Error state
- Recovery status

### 15.3 Multiple Pending Sessions

The architecture should support multiple queued recordings even if the initial interface limits active concurrency.

Each completed transcript must remain associated with its original insertion context.

### 15.4 Empty or Unusable Transcript

If Whisper returns no meaningful text:

- Do not insert an empty string.
- Announce:
  - `No speech was recognized.`
- Retain the recording temporarily according to recovery settings.
- Offer retry with another model or settings when available.

### 15.5 Cancellation

A user may cancel a pending transcription.

Cancellation should:

- Stop waiting for insertion when possible.
- Preserve audio unless the user explicitly discards it.
- Avoid leaving the controller in a busy state.

---

## 16. Insertion Context and Document Safety

When recording begins, QUILL captures:

- Document ID
- File path, when available
- Editor instance
- Caret position
- Selection start and end
- Document revision or change counter
- Surrounding characters
- Current line prefix and indentation
- Read-only state
- Active syntax or content mode
- Timestamp

### 16.1 Original Document Still Available

If the original document remains open and the saved anchor can be resolved safely:

- Insert the transcript there.

### 16.2 Document Changed During Transcription

If edits occurred after dictation began:

- Use a stable marker or document anchor when available.
- Confirm the insertion location is still valid.
- Avoid relying only on a numeric character offset.

### 16.3 Unsafe Insertion

If QUILL cannot prove the original location is safe:

- Do not insert into the currently focused document.
- Save the transcript.
- Open or announce a `Dictation Review Required` state.
- Provide commands to:
  - Insert at current caret
  - Return to original document
  - Copy transcript
  - Save transcript
  - Retry insertion
  - Discard

### 16.4 Closed Document

If the document was closed:

- Preserve the transcript.
- Offer to reopen the document when possible.
- Never insert into another document automatically.

### 16.5 Read-Only Change

If the target becomes read-only:

- Preserve the transcript.
- Explain why automatic insertion could not occur.
- Offer copy or save actions.

---

## 17. Intelligent Text Insertion

The transcript should be inserted as a single editor transaction.

### Required Behavior

- Replace the selection that existed when dictation began.
- Otherwise insert at the saved caret.
- Preserve the clipboard.
- Preserve the document’s line-ending convention.
- Keep the caret at the end of inserted text.
- Avoid duplicate spaces.
- Avoid adding a space before punctuation.
- Respect indentation and list prefixes.
- Preserve Markdown and HTML source without adding markup unexpectedly.
- Support one-step undo.

### Conservative Normalization

The initial release may:

- Trim accidental leading and trailing whitespace.
- Add one leading space when adjoining two words.
- Avoid duplicate punctuation spacing.
- Preserve intentional paragraph breaks returned by Whisper.

The initial release should not aggressively rewrite grammar or punctuation.

### Optional Future Enhancements

- Spoken punctuation commands.
- “New paragraph” and “new line” handling.
- List-aware dictation.
- Markdown-aware formatting.
- Automatic sentence capitalization.
- User dictionaries.
- Vocabulary hints.
- Language switching.
- Domain-specific terminology profiles.

---

## 18. Accessibility Requirements

## 18.1 No Focus Theft

Starting, stopping, pausing, resuming, or transcribing must not move keyboard focus away from the editor.

A review interface may receive focus only when automatic insertion is unsafe or the user explicitly opens it.

## 18.2 Earcons

Provide distinct, short sounds for:

- Hold recording started
- Hold recording stopped
- Locked Dictation started
- Locked Dictation stopped
- Paused
- Resumed
- Error
- Cancellation
- Maximum time reached

Sounds should be:

- Brief
- Distinguishable
- Nonverbal
- Volume-adjustable
- Optional
- Played at the correct point relative to microphone capture

## 18.3 Screen-Reader Announcements

Announcements should be concise and configurable.

Recommended standard messages:

- `Locked dictation on. Press Control F9 to finish. Escape stops.`
- `Dictation paused.`
- `Dictation resumed.`
- `Transcribing dictation.`
- `Dictation inserted, 24 words.`
- `No speech was recognized.`
- `Dictation saved for review.`
- `Microphone unavailable.`
- `Dictation stopped because QUILL lost focus.`

Do not repeatedly announce elapsed time while recording.

## 18.4 Status Command

Alt+F9 should announce one of:

- `Dictation is off.`
- `Hold-to-dictate is recording.`
- `Locked dictation is recording, 1 minute 18 seconds.`
- `Dictation is paused.`
- `Dictation is being transcribed.`
- `A transcript is waiting for review.`

The status command must not alter recording state.

## 18.5 Accessible Settings

Shortcut assignment must use an accessible key-capture interface rather than requiring the user to type shortcut names manually.

The interface should announce:

> Press the key or key combination you want to assign. Press Escape to cancel.

It must detect conflicts and explain them clearly.

## 18.6 Screen-Reader Speech Contamination

To reduce the chance that screen-reader output is transcribed:

- Prefer earcons at recording start.
- Avoid spoken messages after capture begins.
- Stop capture before playing stop announcements.
- Allow users to select earcons-only operation.
- Document headphones as an optional best practice, not a requirement.

---

## 19. Visual Design

Visual indicators supplement but do not replace nonvisual feedback.

### Status Bar

Examples:

- `Ready`
- `Hold-to-dictate recording — release F9`
- `Locked dictation — Ctrl+F9 to finish`
- `Locked dictation paused`
- `Transcribing dictation…`
- `Transcript waiting for review`

### Optional Recording Indicator

A compact indicator may show:

- Microphone icon
- Mode label
- Elapsed time
- Pause state
- Audio level

It must:

- Not steal focus.
- Not cover the current line of text.
- Respect high contrast and theme settings.
- Expose an accessible name and state.
- Be removable through settings.

---

## 20. Settings

Recommended path:

`Settings > Dictation > Activation and Control`

### 20.1 General

- Enable dictation shortcuts
- Dictation engine
- Input device
- Default language
- Model selection
- Automatically load model when QUILL starts
- Keep model loaded while QUILL is running

### 20.2 Hold-to-Dictate

- Enable Hold-to-Dictate
- Activation key
- Consume activation key
- Minimum hold duration
- Ignore accidental taps
- Stop when QUILL loses focus
- Play start and stop sounds
- Allow promotion to Locked Dictation in a future release

### 20.3 Locked Dictation

- Enable Locked Dictation
- Lock shortcut
- Emergency stop key
- Pause or resume shortcut
- Stop when QUILL loses focus
- Allow recording when QUILL is in the background
- Maximum recording duration
- Warn after extended silence
- Stop after extended silence
- Repeat locked-state reminder
- Reminder interval

Background recording and unlimited duration must include clear privacy warnings.

### 20.4 Feedback

- Earcons only
- Speech only
- Earcons and speech
- No audio feedback
- Announcement verbosity:
  - Minimal
  - Standard
  - Verbose
- Feedback volume
- Show visual recording indicator
- Show elapsed time
- Show audio level

### 20.5 Insertion

- Insert at original location
- Replace original selection
- Intelligent spacing
- Preserve Whisper paragraph breaks
- Capitalize likely sentence starts
- Insert as one undo action
- Open review when location changed
- Copy transcript to clipboard when insertion fails

### 20.6 Recovery and Privacy

- Save audio until insertion succeeds
- Keep successful recordings:
  - Never
  - 15 minutes
  - 1 hour
  - 1 day
  - Until manually deleted
- Keep failed recordings
- Keep transcript history
- Maximum history size
- Clear Dictation History
- Recovery folder location
- Encrypt retained dictation data when practical
- Exclude recovery files from ordinary crash-report attachments

---

## 21. Shortcut Conflict Management

QUILL must validate configurable shortcuts against:

- Existing QUILL commands
- Menu accelerators
- Windows-reserved combinations
- Common screen-reader modifiers and commands
- Text-producing keys
- Modifier-only keys
- Shortcuts with unreliable release behavior
- F12 and other discouraged system keys

The user should receive a clear conflict message:

> Control F9 is currently assigned to Refresh Preview. Choose another shortcut or replace the existing assignment.

The settings interface should support:

- Replace existing assignment
- Choose another shortcut
- Restore default
- Disable the command

---

## 22. Recovery System

Dictation must be treated as a recoverable transaction.

### 22.1 Temporary Storage

After recording stops, save audio before beginning transcription.

Suggested structure:

```text
QUILL user data/
  recovery/
    dictation/
      session-id.wav
      session-id.json
      session-id.txt
```

### 22.2 Metadata

The sidecar file should contain:

```json
{
  "session_id": "unique-id",
  "mode": "locked",
  "created_at": "ISO-8601 timestamp",
  "document_id": "internal-document-id",
  "document_path": "optional path",
  "selection_start": 1200,
  "selection_end": 1200,
  "document_revision": 44,
  "audio_state": "saved",
  "transcription_state": "pending",
  "insertion_state": "not_started"
}
```

Do not store document text beyond the small context required to resolve insertion, and avoid storing sensitive surrounding content where possible.

### 22.3 Cleanup

Delete recovery data only after:

- Successful insertion and expiration of the configured retention period, or
- Explicit user deletion.

### 22.4 Startup Recovery

When QUILL starts and finds incomplete sessions:

- Announce that recovered dictation is available.
- Do not automatically insert it.
- Offer:
  - Transcribe
  - Review transcript
  - Reopen target document
  - Save audio
  - Delete

---

## 23. Dictation History

A future or phase-two Dictation History window should present recent sessions in an accessible list.

Each item should expose:

- Date and time
- Dictation mode
- Duration
- Target document
- Status
- Word count
- Whether audio is retained
- Whether insertion succeeded

Available actions:

- Review transcript
- Reinsert
- Insert at current caret
- Copy
- Save as text
- Retry transcription
- Play audio
- Delete transcript
- Delete audio
- Delete entire item
- Open target document

The history interface must be fully operable with standard list navigation and context menus.

---

## 24. Threading and Component Architecture

### 24.1 UI Thread

Responsible for:

- Keyboard command routing
- State transitions
- Editor context capture
- Status updates
- Accessibility messages
- Final insertion
- Undo transaction creation
- Review interfaces

### 24.2 Audio Capture Worker

Responsible for:

- Opening the input device
- Capturing PCM frames
- Stopping and flushing
- Writing recovery audio
- Detecting device failure

### 24.3 Transcription Worker

Responsible for:

- Running Whisper
- Reporting progress
- Supporting cancellation
- Returning transcript or error
- Never touching wxPython controls directly

### 24.4 Optional Keyboard Hook Thread

Responsible only for:

- Receiving native key transitions
- Posting compact events
- Maintaining the Windows message loop
- Releasing the hook cleanly during shutdown

### 24.5 Session Repository

Responsible for:

- Session metadata
- Recovery paths
- State persistence
- Cleanup
- Startup recovery discovery

### 24.6 Insertion Service

Responsible for:

- Resolving saved anchors
- Validating target documents
- Normalizing surrounding whitespace
- Performing one undoable insertion
- Falling back to review when unsafe

---

## 25. Suggested Class Structure

```python
class DictationMode(Enum):
    HOLD = auto()
    LOCKED = auto()


class DictationState(Enum):
    IDLE = auto()
    VALIDATING = auto()
    STARTING = auto()
    HOLD_RECORDING = auto()
    LOCKED_RECORDING = auto()
    PAUSED = auto()
    STOPPING = auto()
    SAVING_AUDIO = auto()
    TRANSCRIBING = auto()
    INSERTING = auto()
    REVIEW_REQUIRED = auto()
    COMPLETED = auto()
    CANCELLED = auto()
    FAILED = auto()
    RECOVERING = auto()


@dataclass
class DictationSession:
    session_id: str
    mode: DictationMode
    state: DictationState
    document_id: str
    document_path: str | None
    selection_start: int
    selection_end: int
    document_revision: int
    started_at: datetime
    stopped_at: datetime | None = None
    audio_path: Path | None = None
    transcript_path: Path | None = None
    transcript: str | None = None
    error: str | None = None
```

Recommended services:

```text
DictationController
DictationShortcutRouter
AudioCaptureService
WhisperTranscriptionService
DictationInsertionService
DictationRecoveryRepository
DictationFeedbackService
DictationSettingsService
DictationHistoryService
```

---

## 26. Controller Behavior Sketch

```python
class DictationController:
    def start_hold(self, context) -> None:
        if self.state is not DictationState.IDLE:
            return

        session = self._create_session(DictationMode.HOLD, context)
        self._start_recording(session, DictationState.HOLD_RECORDING)

    def release_hold(self) -> None:
        if self.state is DictationState.HOLD_RECORDING:
            self._finish_recording(keep_audio=True)

    def toggle_locked(self, context) -> None:
        if self.state is DictationState.IDLE:
            session = self._create_session(DictationMode.LOCKED, context)
            self._start_recording(
                session,
                DictationState.LOCKED_RECORDING,
            )
            return

        if self.state in {
            DictationState.LOCKED_RECORDING,
            DictationState.PAUSED,
        }:
            self._finish_recording(keep_audio=True)

    def emergency_stop(self) -> None:
        if self.state in {
            DictationState.HOLD_RECORDING,
            DictationState.LOCKED_RECORDING,
            DictationState.PAUSED,
        }:
            self._finish_recording(keep_audio=True)

    def cancel_and_discard(self) -> None:
        if self._session_is_active():
            self._stop_capture()
            self._request_discard_confirmation_or_apply_policy()

    def toggle_pause(self) -> None:
        if self.state is DictationState.LOCKED_RECORDING:
            self._pause_capture()
            self.state = DictationState.PAUSED
        elif self.state is DictationState.PAUSED:
            self._resume_capture()
            self.state = DictationState.LOCKED_RECORDING
```

Production code must include:

- Exception boundaries
- Locking
- Shutdown safety
- Cancellation tokens
- State validation
- Recovery persistence
- Main-thread marshalling
- Structured logging
- Telemetry only when explicitly permitted

---

## 27. Error Handling

### Microphone Unavailable

Announce:

> The microphone could not be opened. Check the selected input device and Windows microphone permissions.

Do not enter a recording state.

### Whisper Model Unavailable

If audio was already captured:

- Save it.
- Announce:
  - `The recording was saved, but the Whisper model is unavailable.`
- Offer retry after the model is available.

### Transcription Failure

- Preserve the audio.
- Mark the session recoverable.
- Never insert partial error text into the document.
- Provide retry and save options.

### Insertion Failure

- Preserve the transcript and audio.
- Copy to clipboard only if configured.
- Open or announce Dictation Review.
- Do not insert into another document.

### Keyboard Hook Failure

- Fall back to QUILL-focused shortcuts.
- Inform the user once.
- Do not repeatedly interrupt them.

### Unexpected Exception

- Stop recording safely.
- Persist recoverable data.
- Reset the state machine.
- Log the exception.
- Notify the user without exposing a raw traceback unless diagnostics mode is enabled.

---

## 28. Logging and Diagnostics

Structured diagnostic events should include:

- Session created
- Mode selected
- Recording start requested
- Recording started
- Recording stopped
- Missing key-up recovered
- Focus loss
- Maximum duration reached
- Audio saved
- Transcription started
- Transcription completed
- Transcript empty
- Insertion succeeded
- Insertion deferred
- Recovery item created
- Session cleaned up
- Error category

Logs must not contain:

- Raw audio
- Full transcript text by default
- Sensitive document contents
- API keys
- Full surrounding document context

Diagnostics mode may include limited redacted metadata with explicit user consent.

---

## 29. Performance Requirements

- Keyboard activation should be acknowledged immediately.
- Audio capture should begin quickly enough to avoid clipping the first spoken word.
- QUILL’s UI must remain responsive during all Whisper operations.
- Stop actions should terminate microphone capture immediately.
- Status changes should be posted promptly to the UI.
- The keyboard hook, if enabled, must never block.
- Recovery writes should be incremental or fast enough not to freeze the interface.
- Long recordings should not require the entire audio stream to remain only in memory.

---

## 30. Security and Privacy

- Dictation is off unless explicitly activated.
- QUILL must never silently enter Locked Dictation.
- The locked-start tone and state announcement must be distinctive.
- Background recording is disabled by default.
- Retained audio and transcripts must be visible and manageable.
- Recovery data must use user-specific storage with appropriate file permissions.
- Crash reports must not automatically include dictation audio or transcript files.
- Documentation must explain when recordings are deleted.
- Any cloud transcription option must clearly disclose that audio leaves the computer.
- Local Whisper remains the preferred privacy-preserving default when available.

---

## 31. Onboarding and Discoverability

After Whisper is configured successfully, QUILL may present a one-time message:

> Dictation is ready. Hold F9 while speaking, or press Control F9 for Locked Dictation. You can change these shortcuts in Dictation Settings.

The Help menu should include:

- Hold-to-Dictate
- Locked Dictation
- Dictation Keyboard Commands
- Microphone Setup
- Recovering Dictation
- Privacy and Audio Retention
- Troubleshooting Whisper

The feature should also be discoverable through the Command Palette and menus.

Suggested menu:

```text
Dictation
  Hold-to-Dictate Help
  Start Locked Dictation
  Pause Dictation
  Finish Dictation
  Cancel Dictation
  Dictation Status
  Dictation History
  Microphone and Model Settings
```

Menu items should update their labels and enabled states based on the current state.

---

## 32. Testing Strategy

## 32.1 Keyboard Tests

- Press and release F9 normally.
- Hold F9 long enough to trigger auto-repeat.
- Release F9 while another key is pressed.
- Lose focus before key-up.
- Open a menu while recording.
- Disconnect and reconnect the keyboard.
- Use remote desktop.
- Use Sticky Keys and Filter Keys.
- Use different keyboard layouts.
- Remap activation shortcuts.
- Test JAWS, NVDA, Narrator, and common screen-reader key combinations.

## 32.2 Locked Dictation Tests

- Start and stop with Ctrl+F9.
- Press Ctrl+F9 repeatedly.
- Press Escape.
- Press Shift+Escape.
- Pause and resume.
- Reach maximum duration.
- Lose focus.
- Open a modal dialog.
- Lock Windows.
- Put the computer to sleep.
- Disconnect the microphone.
- Close QUILL while locked.
- Attempt a second recording while locked.
- Request status with Alt+F9.

## 32.3 Transcription Tests

- Very short speech.
- Long speech.
- Silence.
- Background noise.
- Multiple languages.
- Model not loaded.
- Model load failure.
- Transcription cancellation.
- Multiple queued sessions.
- Empty transcript.
- Partial engine failure.

## 32.4 Insertion Tests

- Empty document.
- Middle of a word.
- Between words.
- Selected text.
- Markdown list item.
- HTML source.
- Read-only document.
- Closed document.
- Document modified during transcription.
- Document switched during transcription.
- Original document reopened.
- Undo and redo.
- Different newline conventions.
- Large document.
- Multiple editors open.

## 32.5 Recovery Tests

- Crash during recording.
- Crash after audio save.
- Crash during transcription.
- Crash before insertion.
- Restart with incomplete session.
- Retry transcription.
- Delete recovery item.
- Cleanup after retention expiration.
- Missing or corrupted sidecar file.
- Missing audio file.

## 32.6 Accessibility Tests

- No unexpected focus movement.
- Accurate accessible names and states.
- Earcons distinguishable without vision.
- Announcements do not overlap excessively.
- Recording start does not capture QUILL speech.
- Stop announcement occurs after capture ends.
- High contrast.
- 200% and higher scaling.
- Keyboard-only settings.
- Screen-reader browse and focus modes.
- Braille display status review.

---

## 33. Acceptance Criteria

### Hold-to-Dictate

1. Holding F9 starts exactly one recording.
2. Keyboard auto-repeat does not restart or duplicate recording.
3. Releasing F9 stops recording.
4. A missing key-up cannot leave recording active indefinitely.
5. Focus remains in the editor.
6. The start and stop state is perceivable without sight.
7. The stop tone is not captured in the recording.
8. The transcript is inserted at the original safe location.
9. The complete insertion is one undo action.
10. Failed insertion preserves the transcript.

### Locked Dictation

1. Ctrl+F9 starts Locked Dictation from the idle state.
2. Ctrl+F9 stops Locked Dictation when active.
3. Locked mode has distinctive feedback.
4. Escape always stops recording safely.
5. The user can determine current status without changing it.
6. Focus loss follows the configured policy.
7. Maximum duration is enforced.
8. QUILL shutdown cannot silently lose the recording.
9. Locked Dictation never starts accidentally from key auto-repeat.
10. Starting Hold-to-Dictate cannot create a second overlapping session.

### Accessibility

1. All functions are keyboard operable.
2. All state changes are available to screen readers.
3. No required information is visual only.
4. No modal interface is required for routine dictation.
5. Shortcut assignment is accessible.
6. Common screen-reader commands remain functional.
7. Feedback verbosity can be reduced.
8. Dictation can be cancelled or stopped through a dependable command.

### Reliability

1. Whisper never runs on the UI thread.
2. Audio is saved before transcription begins.
3. A transcript is never inserted into the wrong document.
4. Recovery data survives an unexpected QUILL exit.
5. The state machine returns to idle after success, cancellation, or failure.
6. Temporary files are cleaned according to policy.
7. Errors are logged without exposing dictated content.

---

## 34. Rollout Plan

### Phase 1: Core Hold-to-Dictate

- F9 hold and release
- Explicit state machine
- Auto-repeat rejection
- Start and stop tones
- Missing key-up watchdog
- Worker-thread transcription
- Saved insertion context
- One-step undo
- Escape safety stop
- Recovery audio
- Basic accessible settings

### Phase 2: Locked Dictation

- Ctrl+F9 toggle
- Distinct locked feedback
- Persistent status
- Focus-loss handling
- Maximum duration
- Status announcement command
- Shutdown recovery
- Basic Dictation History
- Shortcut conflict detection

### Phase 3: Advanced Session Controls

- Pause and resume
- Multiple queued sessions
- Dictation Review interface
- Reinsert and retry
- Configurable background recording
- Silence warning
- Improved document anchors

### Phase 4: Alternate Activation Devices

- Global Windows key hook
- Foot pedals
- Adaptive switches
- Mouse buttons
- Macro pads
- Configurable external device mappings

### Phase 5: Dictation Intelligence

- Spoken punctuation
- New paragraph commands
- Markdown-aware dictation
- List-aware insertion
- Vocabulary profiles
- Language profiles
- Optional partial transcription
- Optional command-and-control layer

---

## 35. Open Design Decisions

The following decisions should be finalized during implementation planning:

1. Whether F9 conflicts with an existing QUILL command.
2. Whether Escape should always stop-and-keep or be configurable.
3. Whether Shift+Escape should discard immediately or require confirmation.
4. Whether pause and resume can be implemented safely in the first Locked Dictation release.
5. Whether new recording sessions may begin while prior sessions are transcribing.
6. Whether audio prewarming should be enabled by default.
7. Whether a short in-memory pre-roll buffer is desirable.
8. Which document-anchor mechanism is most reliable in each QUILL editor control.
9. Whether background recording should be supported at all in the initial release.
10. Default audio and transcript retention periods.
11. Whether locked mode should provide periodic reminder tones.
12. Whether holding F9 and then pressing Ctrl+F9 should promote the current session into Locked Dictation in a future release.

Recommended defaults are:

- F9 for Hold-to-Dictate.
- Ctrl+F9 to toggle Locked Dictation.
- Escape stops and preserves speech.
- Shift+Escape cancels and discards with confirmation.
- Stop recording when QUILL loses focus.
- Five-minute maximum Locked Dictation duration.
- Earcons plus concise screen-reader announcements.
- Recovery audio retained until successful insertion.
- Background recording disabled.
- No automatic hold-to-lock promotion in the first release.

---

## 36. Success Metrics

Because privacy and accessibility are central, metrics should be local or opt-in.

Useful product indicators may include:

- Percentage of dictation sessions successfully inserted.
- Rate of sessions requiring recovery.
- Missing key-up recovery count.
- Average recording duration.
- Average transcription time.
- Empty transcript rate.
- Insertion conflict rate.
- Dictation cancellation rate.
- Microphone failure rate.
- Number of users enabling Locked Dictation.
- Number of users changing default shortcuts.

No transcript or audio content should be collected for analytics.

---

## 37. Final Product Principle

QUILL must treat every dictation as a protected transaction:

1. The user explicitly starts it.
2. QUILL makes the active state unmistakable.
3. The user always has a dependable way to stop.
4. Audio is secured before transcription.
5. The transcript remains tied to its original document context.
6. Automatic insertion occurs only when safe.
7. Failure results in recovery, not loss.
8. The interface returns to a known state.

Hold-to-Dictate should feel as immediate as pressing a key to type.

Locked Dictation should feel as comfortable as speaking into a trusted recorder, while remaining firmly under the user’s control.

Together, these modes can make Whisper dictation in QUILL fast enough for a phrase, comfortable enough for a long document, and reliable enough for everyday use.

---

## 38. Implementation Status (2026-06-24)

This section records what has shipped against this PRD and what remains. It is the
source of truth for "is this done"; update it as further phases land.

### Implemented

- **wx-free core (`quill/core/speech/dictation/`).** Explicit `DictationController`
  state machine over the §11 states with §11 transition validation; the
  single-recorder invariant and `is_recording`/`is_busy` are state-derived, never a
  bare boolean (§10.1). `DictationSession` + `InsertionContext` records (§16, §25),
  conservative insertion normalization (§17), and `DictationRecoveryRepository`
  (§22: audio saved before transcription, incomplete-session discovery, retention
  cleanup). Fully unit-tested (`tests/unit/core/speech/dictation/`, 42 cases).
- **Hold-to-Dictate (F9)** and **Locked Dictation (Ctrl+F9)** wired in
  `quill/ui/main_frame_dictation_hotkeys.py` over the existing `MicRecorder` +
  offline Whisper provider. Key-down/up matched against the configured bindings in
  the editor key handlers (not the accelerator table), so hold gets a real key-up.
- **Dependable stop and safety:** Escape stops-and-keeps, Shift+Escape
  cancels-and-discards (both consumed only while recording), five-minute max
  duration, focus-loss stop-and-preserve, and a watchdog that recovers a missing
  key-up by polling physical key state (§13.3). Stop tone plays only after capture
  ends (§14.2). Audio is secured to recovery before transcription; transcription
  runs on a worker thread (§15.1); insertion is one undoable edit; an unsafe
  insertion is deferred for review rather than lost.
- **Pause/Resume (Ctrl+Shift+F9)** via a new `MicRecorder.pause()/resume()` that
  drops frames while paused. **Status (Alt+F9)** speaks state without changing it
  (§18.4). Earcons + concise announcements (§18.2/§18.3).
- **All shortcuts remappable** as `tools.dictation_*` keymap entries with conflict
  detection; the F-key/Escape defaults match §8.

### Not yet implemented (planned follow-ups)

- The full **Settings surface** (§20) — max-duration chooser, focus-loss/background
  toggle, verbosity, earcon volume, retention periods, visual recording indicator.
  The controller already reads a `DictationConfig`; only the UI/persistence is
  missing (defaults: 5 min, stop on focus loss, earcons + concise speech).
- **Dictation History** window and the interactive **startup recovery** prompt
  (§22.4, §23) — recovery files are written and discoverable, but there is no UI yet.
- **Dictation Review** interface for deferred/unsafe insertions (§16.3) — the
  transcript is preserved in recovery; a review surface is pending.
- **Concurrent/queued sessions** (§12, §15.3), **distinct locked-vs-hold earcons**
  (§18.2 — currently shared tones plus a distinctive spoken "Locked dictation on"),
  the optional **global Windows key hook** (§13.2, Phase 4), **idle-silence
  detection** (§10.6), and **dictation intelligence** (§Phase 5).
- A dedicated **Dictation menu** (§31) and the one-time **onboarding** message.
