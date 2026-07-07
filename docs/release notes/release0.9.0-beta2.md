# QUILL 0.9.0 Beta 2 - Polish Release 1

### The screen-reader-first writing studio, built by the people who depend on it.

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
- **Speech dialogs open with the right control focused** - Speech Hub, Manage
  Speech Models, and Manage Voices no longer land on the OK/Cancel button.
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

More fixes land in this file as they ship - check back before release day.
