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

More fixes land in this file as they ship - check back before release day.
