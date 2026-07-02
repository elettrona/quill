# Tutorial 4: Turn a document into an audiobook

**Goal:** hear your document in the voice you want, export it as audio, and
build a chaptered audiobook — plus the DAISY format for accessible book
players.

## 1. Pick a voice

**Tools > Speech > Speech and Dictation...** opens the speech hub. QUILL's
voice lineup spans eras:

- **SAPI 5** — the Windows voices you already have; zero downloads.
- **eSpeak NG** and **DECtalk** — the classics, downloadable on demand
  (yes, Perfect Paul).
- **Kokoro** — modern neural voices that run entirely on your machine
  (about a 114 MB one-time download; no cloud, no account). The QUILL Cast
  podcast is narrated by two of these.
- **ElevenLabs** (optional) — a premium cloud voice if you have an account;
  every use is per-session consented.
- **Read in Browser** (experimental, Settings > Experimental) — an
  accessible reader page using your browser's voice catalog, including
  Edge's online natural voices. QUILL states plainly that online browser
  voices synthesize in the vendor's cloud.

Every download is checksum-verified with visible progress.

## 2. Read aloud

Select text (or just place the caret) and use **Tools > Reading & Dictation >
Read Aloud**. Stop on a key. Try the same paragraph in two or three engines —
voices are a taste, and QUILL does not judge.

For fine control of a passage, the **SSML Builder** composes emphasis,
pauses, and prosody from accessible controls — no hand-written tags — and
plays natively on SAPI 5 and eSpeak NG.

## 3. Export speech audio

1. Palette > `Generate Speech Audio`.
2. Choose the voice and the output format. WAV always works; with the
   **ffmpeg** helper installed (Help > Download Optional Components), you
   also get **MP3, M4A, M4B, OGG, Opus, FLAC**.
3. The export runs in the background with progress; the editor stays yours.

## 4. Build a chaptered audiobook

For a long document with headings:

1. Palette > `batch` — the batch speech tools split a document (or a folder
   of documents) into chaptered audio.
2. Draft with a local voice for speed; re-render the final pass with your
   best voice. M4B output gives you a proper audiobook file with chapters.

## 5. DAISY talking books

**File > Export > DAISY Talking Book** writes a DAISY 2.02 text-only talking
book — the standard for accessible book players and library services. Your
headings become the DAISY navigation structure, so build a clean heading
outline first (GLOW will happily check it: [tutorial 6](06-make-it-accessible-with-glow.md)).

## 6. Round trip: audio in

The same suite works in reverse — `Ctrl+F9` dictates offline via Whisper,
and **transcription** turns a recording into a document privately. Feed a
transcript to the **Listening Companion** and get meeting minutes, action
items, or a summary, reviewably.

**Next:** [Start an Accessible Vault](05-start-a-vault.md).
