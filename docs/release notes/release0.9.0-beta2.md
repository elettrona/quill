# QUILL 0.9.0 Beta 2 - Polish Release 1

## The screen-reader-first writing studio, built by the people who depend on it.

*From Community Access. Free. Optional by design. Private by default. Yours to make quiet.*

This is the narrative companion to the **"0.9.0 Beta 2"** section of `CHANGELOG.md`
(the canonical, append-as-you-go log). Per the commitment made at Beta 1, **no new
features land in this release** - only bug fixes and polish, driven directly by
beta tester reports. The same text appears in-app under **Help > What's New** and
on **Check for Updates**.

---

## Fixed in this beta

- **Non-UTF-8 text files no longer crash QUILL on open.** A `.txt`/`.md` file saved
  in Windows-1252/Latin-1 - a curly quote, en-dash, or other high-byte character
  without a UTF-8 BOM - used to throw an unhandled error the moment you opened it.
  QUILL now falls back automatically and tells you when it did, in the status bar.
- **A stalled GPU check could freeze the whole app.** The Speech and Dictation
  options' hardware probe ran with no timeout, directly on the UI thread, every
  time the dialog opened. It's now timeout-guarded and only ever runs once per
  session.
- **Whisper model downloads are more resilient.** They now go through the same
  well-tested download library Faster Whisper already uses, so a future hiccup
  on Hugging Face's side surfaces a clear, specific message instead of a
  generic failure.
- **Kokoro voices give you the real fix when something's missing**, instead of
  two confusing, mostly-unrelated options: the message now points straight at
  **Tools > Speech > Install Kokoro ONNX**.
- **Previewing a downloaded Piper voice no longer errors.** After downloading a
  Piper voice, previewing it failed with an internal "Settings object has no
  attribute" message; the missing setting is now in place, so previewing and
  saving audio with Piper work.
- **Kokoro previews are more reliable - and honest when something is wrong.** If
  a freshly downloaded Kokoro voice could not actually speak, QUILL used to fall
  back to a confusing "requires either... or..." message that hid the real
  reason. Now the download sets up everything Kokoro needs, and if synthesis ever
  still fails the true cause is written to the diagnostics log (**Help > Save
  Diagnostics**) instead of being swallowed - so we can pinpoint and fix it.
- **Speech dialogs open with the right control focused** - Speech Hub, Manage
  Speech Models, and Manage Voices no longer land on the OK/Cancel button.
- **Downloading extras is now a warm, one-stop experience.** **Help > Download
  Optional Components** was tidied into a proper hub: the things most people want
  come first (Pandoc, then the braille pack), every row explains what it does and
  how big it is, and the window opens instantly instead of pausing while it checks
  what you have. For anything already installed you get two new buttons: **Test**,
  which *proves it works* - a voice reads you a sample so you hear it, the offline
  speech engine listens to a spoken phrase and shows you what it heard, and tools
  report their version - and **Remove**, which deletes QUILL's copy and turns its
  features back off. Piper voices and the Node.js runtime are now in the list too,
  everything lands in your portable folder when you run QUILL portably, and if a
  download or test ever fails, QUILL offers to send a bug report with the details.
  For components that have their own picker - the speech engines (whisper.cpp,
  Vosk) and the Read Aloud voices - a **Manage** button jumps you straight to
  Manage Speech Models or Manage Voices to choose sizes and voices, so the hub is
  the one place you start no matter which extra you're after.
- **A simpler installer - no more component checkboxes.** Installing Beta 1
  asked you to pick optional components (Pandoc, Node.js, Piper, Braille pack),
  several of which did nothing because those parts are downloaded when you need
  them, not shipped in the installer. The installer now just installs QUILL;
  everything optional - the neural Piper voices, the braille pack, Pandoc,
  Node.js, and the offline speech engines - downloads on demand the first time
  you use it (Piper from Manage Voices; the braille pack and Pandoc from
  **Help > Download Optional Components**).
- **Tabbed dialogs land you on the first control, not the tab strip.** The AI
  Hub (and the About and Quillin-preferences dialogs) used to open with focus on
  the row of tabs. Your screen reader announced a tab while you heard the first
  field's name, so arrowing down did nothing. These dialogs now open with focus
  on the first real control inside the current tab - and because the fix lives in
  the shared dialog machinery, every tabbed dialog behaves this way.
- **Read Aloud no longer mispronounces Markdown formatting.** Headings, bold
  text, and links in a Markdown document used to be read aloud as literal
  symbols (sounding garbled, especially with Piper voices); they're now
  converted to plain, speakable text first, live and on export.
- **macOS: Pandoc installed from the pandoc.org installer is now found.** A
  QUILL window opened from Finder doesn't see the same folders a Terminal
  window does; QUILL now checks the common install locations directly.
- **Fixed doubled ampersands in a few menu titles** - "Writing & Language,"
  "Reading & Dictation," and others sometimes read back as "Writing &&
  Language." They now spell out "and" instead.
- **Added Danish to the Braille Translation menu.** It shipped with the
  underlying engine all along but never made it into QUILL's language list.
- **Fixed a crash opening Profiles and Features.** A translated profile name
  wasn't being fully resolved before being handed to the list box, so opening
  the dialog - from the Tools menu or the command palette - could crash.
- **The status bar stopped saying "Status Bar" over and over.** Pressing F6 to
  jump to the status bar and then arrowing across it made your screen reader
  announce "Status Bar" before every cell. Now you hear it once, when you land
  there; after that each cell just tells you what it is and what it says (for
  example, "Position, Ln 12, Col 7"). Quieter, and the way it was meant to work.
- **Errors now carry a short support code** (like
  `[QUILL-SPEECH-WHISPER-DL-404]`) alongside the message, so if you paste an
  error into a bug report we can pinpoint the exact cause faster. This now
  covers every one of QUILL's internal error types, not just a handful, and the
  code travels with the crash report automatically.

More fixes land in this file as they ship - check back before release day.
