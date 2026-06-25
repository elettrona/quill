"""Orchestration for Tools > Speech > Batch Export to Speech Audio.

Free functions (not a mixin) so the heavy orchestration lives outside the
already-budgeted ``main_frame`` modules (GATE-11). Each takes the ``MainFrame``
as ``frame`` and uses its established helpers: ``_show_modal_dialog``,
``_run_background_task``, ``_show_message_box``, ``_preview_voice``,
``_set_status``, ``settings``, ``frame`` (the wx window), and ``_wx``.

The actual conversion is the tested wx-free core: ``document_speech`` drives
``chapter_assemble`` over every discovered document, with the chosen engine,
sounder, gaps, sentence/tail pauses and spoken headings.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Any

from quill.ui.batch_speech_export_dialog import BatchSpeechExportDialog, BatchSpeechRequest

_ENGINE_OPTIONS = [
    ("Windows (SAPI 5)", "sapi5"),
    ("DECtalk", "dectalk"),
    ("Piper (neural, offline)", "piper"),
    ("Kokoro (neural, offline)", "kokoro"),
    ("eSpeak-NG (English variants)", "espeak"),
]


def _voices_for(engine: str) -> list[tuple[str, str]]:
    """[(voice_label, voice_id)] for *engine*, mirroring the Speech Hub lists."""
    from quill.core import read_aloud as ra

    try:
        if engine == "kokoro":
            voices = ra.list_kokoro_voices()
        elif engine == "piper":
            voices = ra.list_piper_catalog_voices()
        elif engine == "espeak":
            voices = ra.list_espeak_english_voices()
        elif engine == "dectalk":
            voices = ra.list_dectalk_voices()
        else:  # sapi5
            voices = ra.list_voices()
    except Exception:  # noqa: BLE001 - a missing engine yields an empty list
        return []
    return [(v.name or v.id, v.id) for v in voices]


def _defaults(frame: Any) -> BatchSpeechRequest:
    s = frame.settings
    engine = (s.read_aloud_engine or "sapi5").strip().lower()
    voice = {
        "kokoro": s.read_aloud_kokoro_voice,
        "dectalk": s.read_aloud_dectalk_voice,
        "espeak": s.read_aloud_espeak_voice,
    }.get(engine, s.read_aloud_voice)
    if engine == "piper" and s.read_aloud_piper_model:
        voice = Path(s.read_aloud_piper_model).stem
    source = Path.home()
    doc_path = getattr(frame, "_active_document_path", lambda: None)()
    if isinstance(doc_path, (str, Path)) and str(doc_path):
        parent = Path(doc_path).parent
        if parent.is_dir():
            source = parent
    return BatchSpeechRequest(
        source_folder=source,
        recursive=False,
        extensions=(".docx", ".md", ".html", ".htm", ".txt"),
        engine=engine,
        voice=voice or "",
        rate=int(s.read_aloud_rate),
        speed=float(s.read_aloud_kokoro_speed),
        output_format="mp3",
        sound_enabled=bool(s.batch_speech_chapter_sound_enabled),
        sound_volume=int(s.batch_speech_chapter_sound_volume),
        article_gap_ms=int(s.batch_speech_article_gap_ms),
        sentence_gap_ms=int(s.batch_speech_sentence_gap_ms),
        tail_padding_ms=int(s.batch_speech_tail_padding_ms),
        speak_headings=True,
        skip_existing=False,
    )


def _engine_available(frame: Any) -> dict[str, bool]:
    from quill.core.read_aloud import (
        discover_dectalk_executable,
        discover_espeak_executable,
        discover_piper_executable,
        kokoro_onnx_ready,
    )

    s = frame.settings
    return {
        "sapi5": True,
        "dectalk": discover_dectalk_executable(s.read_aloud_dectalk_executable) is not None,
        "piper": discover_piper_executable() is not None,
        "kokoro": kokoro_onnx_ready(),
        "espeak": discover_espeak_executable(s.read_aloud_espeak_executable) is not None,
    }


def _active_pronunciation_dictionaries(frame: Any, engine: str, source_folder: Path) -> list[Any]:
    """Resolve the enabled, in-scope pronunciation dictionaries for this batch.

    Honors ``settings.pronunciation_enabled`` and the per-user enabled-id
    selection; the source folder is the project scope (a batch is a project run).
    Returns an empty list when pronunciation is off or none are defined, so the
    default behavior is unchanged until the user sets dictionaries up.
    """
    s = frame.settings
    if not getattr(s, "pronunciation_enabled", True):
        return []
    from quill.core.speech.pronunciation import active_dictionaries

    ids = list(getattr(s, "pronunciation_enabled_dictionary_ids", []) or [])
    enabled_ids = set(ids) if ids else None
    try:
        return active_dictionaries(engine, project_dir=source_folder, enabled_ids=enabled_ids)
    except Exception:  # noqa: BLE001 - a broken dictionary store must not block export
        return []


def _persist_choices(frame: Any, req: BatchSpeechRequest) -> None:
    from quill.core.settings import save_settings

    s = frame.settings
    s.read_aloud_engine = req.engine
    if req.voice:
        if req.engine == "kokoro":
            s.read_aloud_kokoro_voice = req.voice
        elif req.engine == "dectalk":
            s.read_aloud_dectalk_voice = req.voice
        elif req.engine == "espeak":
            s.read_aloud_espeak_voice = req.voice
        elif req.engine == "sapi5":
            s.read_aloud_voice = req.voice
    s.read_aloud_rate = req.rate
    s.read_aloud_kokoro_speed = req.speed
    s.batch_speech_chapter_sound_enabled = req.sound_enabled
    s.batch_speech_chapter_sound_volume = req.sound_volume
    s.batch_speech_article_gap_ms = req.article_gap_ms
    s.batch_speech_sentence_gap_ms = req.sentence_gap_ms
    s.batch_speech_tail_padding_ms = req.tail_padding_ms
    try:
        save_settings(s)
    except Exception:  # noqa: BLE001 - persistence is best-effort
        pass


def _run(frame: Any, req: BatchSpeechRequest) -> None:
    from quill.core.speech.batch_export import discover_files
    from quill.core.speech.chapter_assemble import ChapterAssembleOptions
    from quill.core.speech.document_speech import (
        DocumentSpeechError,
        SynthesisSpec,
        synthesize_document_to_chaptered_file,
    )

    files = discover_files(
        req.source_folder,
        list(req.extensions),
        req.recursive,
        include_glob=req.include_glob,
        exclude_glob=req.exclude_glob,
        max_file_bytes=req.max_file_bytes,
    )
    if not files:
        frame._show_message_box(
            "No matching documents were found in that folder.",
            "Batch Export to Speech Audio",
            frame._wx.ICON_INFORMATION | frame._wx.OK,
        )
        return

    spec = SynthesisSpec(engine=req.engine, voice=req.voice, rate=req.rate, speed=req.speed)
    suffix = {"mp3": ".mp3", "m4b": ".m4b"}.get(req.output_format, ".wav")
    dictionaries = _active_pronunciation_dictionaries(frame, req.engine, req.source_folder)

    def opts() -> ChapterAssembleOptions:
        return ChapterAssembleOptions(
            article_gap_ms=req.article_gap_ms,
            sound_enabled=req.sound_enabled,
            sound_volume=req.sound_volume,
            output_format=req.output_format,
            speak_headings=req.speak_headings,
            sentence_gap_ms=req.sentence_gap_ms,
            tail_padding_ms=req.tail_padding_ms,
        )

    total = len(files)

    def work(progress: Any) -> object:
        from quill.core.speech.batch_export import _unique_path

        done = skipped = errors = 0
        for i, src in enumerate(files, start=1):
            final = src.with_suffix(suffix)
            progress(src.name, i, total)
            if final.exists():
                if req.on_existing == "skip":
                    skipped += 1
                    continue
                if req.on_existing == "rename":
                    final = _unique_path(final)
                # "overwrite": leave ``final`` as-is
            work_dir = Path(tempfile.mkdtemp(prefix="quill_batch_speech_"))
            staged = work_dir / f"out{suffix}"
            try:
                result = synthesize_document_to_chaptered_file(
                    src,
                    staged,
                    spec,
                    opts(),
                    work_dir=work_dir / "w",
                    pronunciation_dictionaries=dictionaries,
                )
                deliverable = result.with_tones_path or result.output_path
                shutil.copyfile(deliverable, final)
                done += 1
            except DocumentSpeechError as exc:
                errors += 1
                frame._wx.CallAfter(frame._set_status, f"Skipped {src.name}: {exc}")
            except Exception as exc:  # noqa: BLE001 - isolate per-file failures
                errors += 1
                frame._wx.CallAfter(frame._set_status, f"Error on {src.name}: {exc}")
            finally:
                shutil.rmtree(work_dir, ignore_errors=True)
        return (done, skipped, errors)

    def on_success(result: object) -> None:
        done, skipped, errors = result  # type: ignore[misc]
        frame._set_status(
            f"Batch speech export complete: {done} done, {skipped} skipped, {errors} error(s)"
        )

    frame._run_background_task(
        f"Batch speech export ({total} file(s))",
        work,
        on_success,
        notify_on_success=True,
        notify_on_error=True,
        notification_category="speech",
    )


def run_batch_export_to_speech(frame: Any) -> None:
    """Entry point bound to the Tools > Speech > Batch Export menu item."""

    def on_preview(req: BatchSpeechRequest) -> None:
        if req.voice:
            frame._preview_voice(req.engine, req.voice)
        else:
            frame._set_status("Choose a voice to preview")

    dialog = BatchSpeechExportDialog(
        frame.frame,
        engine_options=_ENGINE_OPTIONS,
        engine_available=_engine_available(frame),
        voices_for=_voices_for,
        on_preview=on_preview,
        defaults=_defaults(frame),
    )
    request = dialog.show(frame._show_modal_dialog)
    if request is None:
        frame._set_status("Batch speech export cancelled")
        return
    _persist_choices(frame, request)
    _run(frame, request)
