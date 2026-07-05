"""The Audio Studio's run request and its shared option vocabularies.

:class:`BatchSpeechRequest` is everything the batch speech pipeline
(``quill.ui.batch_speech_runner``) needs to run one export — moved here
verbatim from the retired single-page ``batch_speech_export_dialog`` so the
wizard, the runner, and the project profile all share one contract. The
constants below are the sanctioned orderings for the wizard's Choice
controls; collection code indexes into them rather than parsing labels.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class BatchSpeechRequest:
    """Everything the caller needs to run one chaptered batch export."""

    source_folder: Path
    recursive: bool
    extensions: tuple[str, ...]
    engine: str
    voice: str
    rate: int
    speed: float
    output_format: str  # "wav" | "mp3"
    sound_enabled: bool
    sound_volume: int
    article_gap_ms: int
    sentence_gap_ms: int
    tail_padding_ms: int
    speak_headings: bool
    skip_existing: bool
    # Discovery filters: ;/,-separated globs matched against the file name and the
    # path relative to the source folder; ``max_file_bytes`` of 0 = no size cap.
    include_glob: str = ""
    exclude_glob: str = ""
    max_file_bytes: int = 0
    # What to do when a target audio file already exists.
    on_existing: str = "overwrite"  # skip | overwrite | rename
    # Chapter mode: "single" = one chaptered file per document; "separate" = one
    # audio file per article/heading, into a per-document folder.
    chapter_mode: str = "single"
    # Dry run: write a ``<doc>.preview.txt`` of the exact spoken text (after
    # normalization + pronunciation + polish) for each file, without synthesizing.
    dry_run: bool = False
    preview: bool = False  # internal: a Preview press, not a Start
    # Combine empty headings into the next article (ACB-style) before synthesis.
    combine_headings: bool = False
    # Normalize each output to ACX audiobook loudness (two-pass loudnorm).
    normalize_loudness: bool = False
    # Round-robin voices: ordered voice ids (of the selected engine) cycled one per
    # article/heading. Empty or one voice -> the single `voice` above is used.
    round_robin_voices: tuple[str, ...] = ()
    # Translated audio export (§7): also export each document in these languages.
    # Each target is (language_code, engine, voice_id); the document is translated
    # into the language then synthesized with that voice. Empty = no translation.
    translation_targets: tuple[tuple[str, str, str], ...] = ()
    # Translation backend: "ai_assistant" (configured AI provider) or "libretranslate".
    translation_provider: str = "ai_assistant"
    libretranslate_url: str = "http://localhost:5000"
    # Temporary-files parent folder. Empty = the system temp dir. Each run creates a
    # ``quill-batch-<timestamp>`` subfolder under it for all of its scratch dirs.
    temp_folder: str = ""
    # Save the exact text sent to the engine (after normalization/pronunciation/
    # polish) as a ``<doc>.spoken.txt`` sidecar, in addition to synthesizing.
    save_spoken_text: bool = False
    # Audiobook assembly: when set, combine the produced (or pre-recorded) audio in
    # the source folder into a single chaptered M4B/MP3 with the book tags below.
    make_book: bool = False
    book_title: str = ""
    book_author: str = ""
    book_narrator: str = ""
    book_genre: str = "Audiobook"
    book_year: str = ""
    book_cover_path: str = ""
    book_format: str = "m4b"  # m4b | mp3
    book_output_path: str = ""
    book_acx_normalize: bool = False
    # Pause after synthesis to open the chapter editor (rename/reorder/merge) before
    # the book is built. A folder of pre-recorded audio (no documents) always opens it.
    book_review_chapters: bool = False
    _voice_label: str = field(default="", repr=False)


# Document types offered on the source page: (label, canonical extension).
ALL_EXTENSIONS: list[tuple[str, str]] = [
    ("&Word (.docx)", ".docx"),
    ("&Markdown (.md)", ".md"),
    ("&HTML (.html, .htm)", ".html"),
    ("Plain &text (.txt)", ".txt"),
]
# .html implies .htm in discovery.
EXTENSION_GROUPS = {".html": (".html", ".htm")}
# Existing-file policy choices, in the order they appear in the policy Choice.
EXISTING_POLICIES = ("skip", "overwrite", "rename")
# Output formats, in the order they appear in the format Choice control.
FORMAT_CHOICES = ("mp3", "m4b", "wav")
FORMAT_INDEX = {fmt: i for i, fmt in enumerate(FORMAT_CHOICES)}
# Chapter modes, in the order they appear in the mode Choice control.
MODE_CHOICES = ("single", "separate")
MODE_INDEX = {mode: i for i, mode in enumerate(MODE_CHOICES)}
# Audiobook output formats, in the order they appear in the book format Choice.
BOOK_FORMATS = ("m4b", "mp3")
BOOK_FORMAT_INDEX = {fmt: i for i, fmt in enumerate(BOOK_FORMATS)}

# The Studio's journeys, in the order they appear on the start page.
JOURNEYS = ("documents", "audio")

__all__ = [
    "ALL_EXTENSIONS",
    "BOOK_FORMATS",
    "BOOK_FORMAT_INDEX",
    "BatchSpeechRequest",
    "EXISTING_POLICIES",
    "EXTENSION_GROUPS",
    "FORMAT_CHOICES",
    "FORMAT_INDEX",
    "JOURNEYS",
    "MODE_CHOICES",
    "MODE_INDEX",
]
