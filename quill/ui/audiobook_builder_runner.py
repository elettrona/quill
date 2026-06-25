"""Orchestration for Tools > Speech > Build Audiobook from Folder.

A free function (not a mixin) so the heavy orchestration lives outside the
budgeted ``main_frame`` modules. The actual build is the tested, wx-free core
``quill.core.speech.audiobook``: scan the folder, derive a chapter per file, and
concatenate into one chaptered MP3/M4B master with tags and cover.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from quill.ui.audiobook_builder_dialog import AudiobookBuilderDialog, AudiobookRequest


def _scan(folder: Path, recursive: bool) -> tuple[int, str]:
    """Count audio files in *folder* and return a detected cover path (or "")."""
    from quill.core.speech.audiobook import find_cover, scan_audio_folder

    files = scan_audio_folder(folder, recursive=recursive)
    cover = find_cover(folder)
    return len(files), str(cover) if cover else ""


def _defaults(frame: Any) -> AudiobookRequest:
    source = Path.home()
    doc_path = getattr(frame, "_active_document_path", lambda: None)()
    if isinstance(doc_path, (str, Path)) and str(doc_path):
        parent = Path(doc_path).parent
        if parent.is_dir():
            source = parent
    return AudiobookRequest(
        source_folder=source,
        recursive=False,
        output_path=Path(""),
        output_format="m4b",
        album="",
        author="",
        narrator="",
        genre="Audiobook",
        year="",
        cover_path="",
    )


def _run(frame: Any, req: AudiobookRequest) -> None:
    from quill.core.speech.audiobook import build_audiobook, build_chapter_list, scan_audio_folder
    from quill.core.speech.ffmpeg import AudioMetadata

    files = scan_audio_folder(req.source_folder, recursive=req.recursive)
    if not files:
        frame._show_message_box(
            "No audio files were found in that folder.",
            "Build Audiobook from Folder",
            frame._wx.ICON_INFORMATION | frame._wx.OK,
        )
        return

    metadata = AudioMetadata(
        album=req.album or req.source_folder.name,
        artist=req.author,
        album_artist=req.narrator or req.author,
        genre=req.genre,
        year=req.year,
    )
    cover = Path(req.cover_path) if req.cover_path else None
    total = len(files)

    def work(_progress: Any) -> object:
        chapters = build_chapter_list(files)
        return build_audiobook(
            chapters,
            req.output_path,
            output_format=req.output_format,
            metadata=metadata,
            cover=cover,
            on_progress=lambda msg: frame._wx.CallAfter(frame._set_status, msg),
        )

    def on_success(result: Any) -> None:
        frame._set_status(
            f"Audiobook built: {result.output_path.name} ({result.chapter_count} chapters)"
        )

    frame._run_background_task(
        f"Build audiobook ({total} file(s))",
        work,
        on_success,
        notify_on_success=True,
        notify_on_error=True,
        notification_category="speech",
    )


def run_build_audiobook(frame: Any) -> None:
    """Entry point bound to the Tools > Speech > Build Audiobook from Folder item."""
    dialog = AudiobookBuilderDialog(
        frame.frame,
        defaults=_defaults(frame),
        on_scan=_scan,
        announce=getattr(frame, "_announce", None),
    )
    request = dialog.show(frame._show_modal_dialog)
    if request is None:
        frame._set_status("Build Audiobook cancelled")
        return
    _run(frame, request)
