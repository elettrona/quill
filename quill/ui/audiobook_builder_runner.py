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


def _scan(folder: Path, recursive: bool) -> tuple[list[tuple[str, str]], str]:
    """Return ``([(file_path, default_title), …], cover_path)`` for the chapter editor."""
    from quill.core.speech.audiobook import find_cover, scan_audio_folder, title_from_filename

    files = scan_audio_folder(folder, recursive=recursive)
    rows = [
        (str(path), title_from_filename(path) or f"Chapter {index}")
        for index, path in enumerate(files, start=1)
    ]
    cover = find_cover(folder)
    return rows, (str(cover) if cover else "")


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
    from quill.core.speech.audiobook import (
        build_audiobook,
        build_chapter_list,
        chapters_from_plan,
        scan_audio_folder,
    )
    from quill.core.speech.ffmpeg import AudioMetadata

    # Use the edited chapter plan when the dialog supplied one; otherwise scan the
    # folder fresh and use one filename-derived chapter per file.
    if req.chapter_plan:
        plan = [(title, [Path(p) for p in paths]) for title, paths in req.chapter_plan]
        chapter_count = len(plan)
    else:
        files = scan_audio_folder(req.source_folder, recursive=req.recursive)
        if not files:
            frame._show_message_box(
                "No audio files were found in that folder.",
                "Build Audiobook from Folder",
                frame._wx.ICON_INFORMATION | frame._wx.OK,
            )
            return
        plan = None
        chapter_count = len(files)

    metadata = AudioMetadata(
        album=req.album or req.source_folder.name,
        artist=req.author,
        album_artist=req.narrator or req.author,
        genre=req.genre,
        year=req.year,
    )
    cover = Path(req.cover_path) if req.cover_path else None

    def work(_progress: Any) -> object:
        chapters = chapters_from_plan(plan) if plan is not None else build_chapter_list(files)
        result = build_audiobook(
            chapters,
            req.output_path,
            output_format=req.output_format,
            metadata=metadata,
            cover=cover,
            acx_normalize=req.acx_normalize,
            on_progress=lambda msg: frame._wx.CallAfter(frame._set_status, msg),
        )
        # Verify the finished master against ACX loudness (decodes it; safe here on
        # the background pool). The summary is surfaced in the completion status.
        from quill.core.speech.loudness import measure_loudness

        return result, measure_loudness(result.output_path)

    def on_success(payload: Any) -> None:
        result, stats = payload
        note = f" {stats.summary()}" if stats is not None else ""
        frame._set_status(
            f"Audiobook built: {result.output_path.name} ({result.chapter_count} chapters).{note}"
        )

    frame._run_background_task(
        f"Build audiobook ({chapter_count} chapter(s))",
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
