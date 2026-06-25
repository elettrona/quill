"""Run a single document's translated speech export (roadmap §7).

Bound to Tools > Speech > Export to Translated Speech Audio. This is the
one-document counterpart to the folder-oriented batch translated export: it reuses
the same tested core (:func:`quill.ui.batch_speech_runner._export_translations`,
which drives ``document_speech`` with a per-language translator and the
voice-failure blacklist) against the active document's file, writing
``<doc> (<Language>).<ext>`` beside it.

Free functions, not a mixin, so the orchestration stays out of the budgeted
``main_frame`` modules (GATE-11). The handler takes the ``MainFrame`` as ``frame``
and uses its established helpers (``_show_modal_dialog``, ``_run_background_task``,
``_show_message_box``, ``_set_status``, ``settings``, ``frame``, ``_wx``).
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from quill.ui.translated_speech_export_dialog import (
    TranslatedSpeechExportDialog,
    TranslatedSpeechRequest,
)


def _active_document(frame: Any) -> Any:
    """The active Document (or None) for the front tab."""
    return getattr(frame, "document", None)


def run_translated_speech_export(frame: Any) -> None:
    """Entry point bound to the Export to Translated Speech Audio menu item."""
    wx = frame._wx
    doc = _active_document(frame)
    path = getattr(doc, "path", None) if doc is not None else None
    if path is None:
        frame._show_message_box(
            "Save the document first, then export it to translated speech audio.",
            "Export to Translated Speech Audio",
            wx.ICON_INFORMATION | wx.OK,
        )
        return
    # Export reads the on-disk file; offer to save unsaved edits so they are spoken.
    if getattr(doc, "modified", False):
        choice = frame._show_message_box(
            "The document has unsaved changes. Save before exporting so they are "
            "included in the translation?",
            "Export to Translated Speech Audio",
            wx.ICON_QUESTION | wx.YES_NO | wx.CANCEL,
        )
        if choice == wx.CANCEL:
            frame._set_status("Translated speech export cancelled")
            return
        if choice == wx.YES:
            frame.save_file()

    source = Path(path)
    dialog = TranslatedSpeechExportDialog(frame.frame, document_name=source.name)
    request = dialog.show(frame._show_modal_dialog)
    if request is None:
        frame._set_status("Translated speech export cancelled")
        return
    _run(frame, source, request)


def _run(frame: Any, source: Path, request: TranslatedSpeechRequest) -> None:
    from quill.core.speech.chapter_assemble import ChapterAssembleOptions
    from quill.core.speech.voice_blacklist import load_blacklist, save_blacklist
    from quill.ui.batch_speech_runner import _build_translator, _export_translations

    s = frame.settings
    suffix = {"mp3": ".mp3", "m4b": ".m4b"}.get(request.output_format, ".wav")
    # A req shim carrying just the fields _export_translations / _build_translator read.
    req = SimpleNamespace(
        translation_targets=request.targets,
        translation_provider=request.translation_provider,
        libretranslate_url=request.libretranslate_url,
        rate=int(s.read_aloud_rate),
        speed=float(s.read_aloud_kokoro_speed),
        combine_headings=False,
        source_folder=source.parent,
    )
    for_language = _build_translator(req)
    if for_language is None:
        frame._set_status("No translation targets selected")
        return

    def opts(_sound_path: Path | None = None) -> ChapterAssembleOptions:
        return ChapterAssembleOptions(
            article_gap_ms=int(s.batch_speech_article_gap_ms),
            sound_enabled=False,
            output_format=request.output_format,
            speak_headings=True,
            sentence_gap_ms=int(s.batch_speech_sentence_gap_ms),
            tail_padding_ms=int(s.batch_speech_tail_padding_ms),
            max_chunk_chars=8000,
        )

    voice_blacklist = load_blacklist()

    def work(_progress: Any) -> object:
        work_dir = Path(tempfile.mkdtemp(prefix="quill_tr_single_"))
        try:
            chapters = _export_translations(
                frame,
                req,
                source,
                source.with_suffix(suffix),
                suffix,
                None,
                opts,
                for_language,
                voice_blacklist,
            )
        finally:
            import shutil

            shutil.rmtree(work_dir, ignore_errors=True)
        save_blacklist(voice_blacklist)
        return chapters

    def on_success(result: object) -> None:
        count = int(result) if isinstance(result, int) else 0
        langs = len(request.targets)
        frame._set_status(
            f"Translated speech export complete: {langs} language(s), {count} chapter(s)"
        )

    frame._run_background_task(
        f"Translated speech export ({len(request.targets)} language(s))",
        work,
        on_success,
        notify_on_success=True,
        notify_on_error=True,
        notification_category="speech",
    )
