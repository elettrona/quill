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
    base = BatchSpeechRequest(
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
    # Apply-on-open: a remembered project profile overlays the global defaults.
    return _apply_project_profile(frame, base)


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


def _active_pronunciation_dictionaries(
    frame: Any, engine: str, source_folder: Path, *, language: str | None = None
) -> list[Any]:
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
        return active_dictionaries(
            engine, project_dir=source_folder, enabled_ids=enabled_ids, language=language
        )
    except Exception:  # noqa: BLE001 - a broken dictionary store must not block export
        return []


def _resolve_chapter_sound_path(frame: Any, dest_dir: Path) -> Path | None:
    """Resolve the configured chapter-transition ``sound_id`` to a real WAV.

    Looks the id up in the active sound pack (``settings.sound_pack_path``, or the
    bundled Ink pack) and writes the pre-buffered bytes into *dest_dir*. Returns
    ``None`` when no id is set or it is not in the pack, so chapter assembly falls
    back to its generated placeholder chime (the format-mismatch fallback in
    ``chapter_assemble`` also covers a sound that does not match the section audio).
    """
    settings = frame.settings
    sound_id = (getattr(settings, "batch_speech_chapter_sound_id", "") or "").strip()
    if not sound_id:
        return None
    import quill
    from quill.core.sound_pack import load_sound_pack

    pack_path = (getattr(settings, "sound_pack_path", "") or "").strip()
    pack = (
        Path(pack_path)
        if pack_path
        else Path(quill.__file__).parent / "assets" / "sound_packs" / "ink"
    )
    try:
        data = load_sound_pack(pack).events.get(sound_id)
    except Exception:  # noqa: BLE001 - a broken pack must not block export
        return None
    if not data:
        return None
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / f"chapter_sound_{sound_id}.wav"
    out.write_bytes(data)
    return out


_TRANSLATION_LOCAL_ENGINES = frozenset({"sapi5", "kokoro", "piper", "dectalk", "espeak"})


def _build_translator(req: Any) -> Any:
    """Return ``for_language(name) -> translate(text)->text`` or None when not needed.

    Loads the AI connection/key (or LibreTranslate URL) once; the per-language closure
    wraps :func:`quill.core.ai.translation.translate_text`.
    """
    if not req.translation_targets:
        return None
    from quill.core.ai.translation import translate_text
    from quill.core.assistant_ai import (
        load_assistant_api_key,
        load_assistant_connection_settings,
    )

    conn = load_assistant_connection_settings()
    api_key = load_assistant_api_key()
    provider = req.translation_provider or "ai_assistant"
    lt_url = req.libretranslate_url or "http://localhost:5000"

    def for_language(language_name: str) -> Any:
        def _translate(text: str) -> str:
            translated, _src = translate_text(text, language_name, conn, api_key, provider, lt_url)
            return translated

        return _translate

    return for_language


def _export_translations(
    frame: Any,
    req: Any,
    src: Path,
    base_final: Path,
    suffix: str,
    chapter_sound: Path | None,
    opts_fn: Any,
    for_language: Any,
) -> int:
    """Export *src* in each configured target language; return chapters produced."""
    import shutil
    import tempfile

    from quill.core.ai.translation import LANGUAGE_NAMES
    from quill.core.speech.document_speech import (
        DocumentSpeechError,
        SynthesisSpec,
        synthesize_document_to_chaptered_file,
    )

    chapters = 0
    for lang_code, t_engine, t_voice in req.translation_targets:
        if t_engine not in _TRANSLATION_LOCAL_ENGINES:
            frame._wx.CallAfter(
                frame._set_status, f"Skipped {lang_code} (cloud voices not yet supported)"
            )
            continue
        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
        out = base_final.with_name(f"{base_final.stem} ({lang_name}){suffix}")
        t_dicts = _active_pronunciation_dictionaries(
            frame, t_engine, req.source_folder, language=lang_code
        )
        t_spec = SynthesisSpec(engine=t_engine, voice=t_voice, rate=req.rate, speed=req.speed)
        work = Path(tempfile.mkdtemp(prefix="quill_batch_tr_"))
        try:
            result = synthesize_document_to_chaptered_file(
                src,
                work / f"out{suffix}",
                t_spec,
                opts_fn(chapter_sound),
                work_dir=work / "w",
                pronunciation_dictionaries=t_dicts,
                combine_headings=req.combine_headings,
                translate=for_language(lang_name),
            )
            shutil.copyfile(result.with_tones_path or result.output_path, out)
            chapters += len(result.chapters)
            frame._wx.CallAfter(frame._set_status, f"{out.name}: {len(result.chapters)} chapter(s)")
        except DocumentSpeechError as exc:
            frame._wx.CallAfter(frame._set_status, f"Skipped {out.name}: {exc}")
        except Exception as exc:  # noqa: BLE001 - isolate per-language failures
            frame._wx.CallAfter(frame._set_status, f"Error on {out.name}: {exc}")
        finally:
            shutil.rmtree(work, ignore_errors=True)
    return chapters


def _current_project_dir(frame: Any) -> Path | None:
    """The active document's folder — the project a batch run is scoped to (§4.10)."""
    doc_path = getattr(frame, "_active_document_path", lambda: None)()
    if isinstance(doc_path, (str, Path)) and str(doc_path):
        parent = Path(doc_path).parent
        if parent.is_dir():
            return parent
    return None


def _apply_project_profile(frame: Any, defaults: BatchSpeechRequest) -> BatchSpeechRequest:
    """Overlay the project's remembered speech profile onto *defaults* (apply-on-open).

    Precedence is this-run > **project** > global > defaults: the dialog still wins
    (this-run), but a folder that was "remembered" pre-fills the dialog from its
    `.quill/speech-project.json` instead of the global settings.
    """
    import dataclasses

    project_dir = _current_project_dir(frame)
    if project_dir is None:
        return defaults
    from quill.core.speech.project_profile import load_profile

    profile = load_profile(project_dir)
    if profile is None:
        return defaults
    syn, ch = profile.synthesizer, profile.chapters
    fmt = profile.output.format
    if fmt not in {"mp3", "m4b", "wav"}:
        fmt = defaults.output_format
    return dataclasses.replace(
        defaults,
        engine=syn.engine or defaults.engine,
        voice=syn.voice or defaults.voice,
        rate=syn.rate or defaults.rate,
        speed=syn.speed or defaults.speed,
        output_format=fmt,
        sound_enabled=ch.sound_enabled,
        sound_volume=ch.sound_volume,
        article_gap_ms=ch.article_gap_ms,
        sentence_gap_ms=ch.sentence_gap_ms,
        tail_padding_ms=ch.tail_padding_ms,
        chapter_mode="separate" if ch.mode == "separate" else "single",
        combine_headings=ch.combine_headings,
        normalize_loudness=ch.normalize_loudness,
        round_robin_voices=tuple(ch.round_robin_voices),
    )


def _save_project_profile(frame: Any, req: BatchSpeechRequest) -> None:
    """Remember this run's choices in the source folder's profile (auto-remember on Start)."""
    if not req.source_folder.is_dir():
        return
    from quill.core.speech.project_profile import (
        ChapterProfile,
        OutputProfile,
        SpeechProjectProfile,
        SynthesizerProfile,
        save_profile,
    )

    profile = SpeechProjectProfile(
        synthesizer=SynthesizerProfile(
            engine=req.engine, voice=req.voice, rate=int(req.rate), speed=float(req.speed)
        ),
        output=OutputProfile(format=req.output_format),
        chapters=ChapterProfile(
            mode=req.chapter_mode,
            sound_enabled=req.sound_enabled,
            sound_volume=req.sound_volume,
            article_gap_ms=req.article_gap_ms,
            sentence_gap_ms=req.sentence_gap_ms,
            tail_padding_ms=req.tail_padding_ms,
            combine_headings=req.combine_headings,
            normalize_loudness=req.normalize_loudness,
            round_robin_voices=tuple(req.round_robin_voices),
        ),
    )
    try:
        save_profile(profile, req.source_folder)
    except Exception:  # noqa: BLE001 - remembering is best-effort
        pass


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
        synthesize_document_to_separate_files,
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
    for_language = _build_translator(req)

    def opts(sound_path: Path | None = None) -> ChapterAssembleOptions:
        return ChapterAssembleOptions(
            article_gap_ms=req.article_gap_ms,
            sound_enabled=req.sound_enabled,
            sound_volume=req.sound_volume,
            sound_path=sound_path,
            output_format=req.output_format,
            speak_headings=req.speak_headings,
            sentence_gap_ms=req.sentence_gap_ms,
            tail_padding_ms=req.tail_padding_ms,
            normalize_loudness=req.normalize_loudness,
            # Auto-chunk very long sections so a single synthesis call never runs
            # past the engine timeout; short sections are unaffected (one call).
            max_chunk_chars=8000,
        )

    total = len(files)

    def work(progress: Any) -> object:
        from quill.core.speech.batch_export import (
            _unique_path,
            extract_text,
            transform_preview,
        )

        # Resolve the configured chapter-transition sound once for the whole run;
        # None falls back to the generated placeholder chime in chapter assembly.
        sound_dir = Path(tempfile.mkdtemp(prefix="quill_batch_snd_"))
        chapter_sound = _resolve_chapter_sound_path(frame, sound_dir) if req.sound_enabled else None
        done = skipped = errors = total_chapters = total_subs = 0
        for i, src in enumerate(files, start=1):
            progress(src.name, i, total)
            if req.dry_run:
                # Write the exact spoken text (after pronunciation + polish) to a
                # sidecar instead of synthesizing — a cheap review pass.
                try:
                    preview = transform_preview(
                        extract_text(src),
                        engine=req.engine,
                        pronunciation_dictionaries=dictionaries,
                    )
                    out = src.with_suffix(".preview.txt")
                    out.write_text(
                        f"# Dry run preview for {src.name} "
                        f"({preview.substitutions} pronunciation substitution(s))\n\n"
                        f"{preview.text}\n",
                        encoding="utf-8",
                    )
                    done += 1
                    total_subs += preview.substitutions
                    frame._wx.CallAfter(
                        frame._set_status,
                        f"{src.name}: preview written ({preview.substitutions} substitutions)",
                    )
                except Exception as exc:  # noqa: BLE001 - isolate per-file failures
                    errors += 1
                    frame._wx.CallAfter(frame._set_status, f"Error on {src.name}: {exc}")
                continue
            if req.chapter_mode == "separate":
                out_dir = src.parent / src.stem
                if req.on_existing == "skip" and out_dir.is_dir() and any(out_dir.iterdir()):
                    skipped += 1
                    continue
                sep_work = Path(tempfile.mkdtemp(prefix="quill_batch_sep_"))
                try:
                    written = synthesize_document_to_separate_files(
                        src,
                        out_dir,
                        spec,
                        opts(chapter_sound),
                        work_dir=sep_work / "w",
                        pronunciation_dictionaries=dictionaries,
                        combine_headings=req.combine_headings,
                        voice_rotation=list(req.round_robin_voices),
                    )
                    done += 1
                    total_chapters += len(written)
                    frame._wx.CallAfter(
                        frame._set_status, f"{src.stem}: {len(written)} article file(s)"
                    )
                except DocumentSpeechError as exc:
                    errors += 1
                    frame._wx.CallAfter(frame._set_status, f"Skipped {src.name}: {exc}")
                except Exception as exc:  # noqa: BLE001 - isolate per-file failures
                    errors += 1
                    frame._wx.CallAfter(frame._set_status, f"Error on {src.name}: {exc}")
                finally:
                    shutil.rmtree(sep_work, ignore_errors=True)
                continue
            final = src.with_suffix(suffix)
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
                    opts(chapter_sound),
                    work_dir=work_dir / "w",
                    pronunciation_dictionaries=dictionaries,
                    combine_headings=req.combine_headings,
                    voice_rotation=list(req.round_robin_voices),
                )
                deliverable = result.with_tones_path or result.output_path
                shutil.copyfile(deliverable, final)
                done += 1
                chapter_count = len(result.chapters)
                total_chapters += chapter_count
                frame._wx.CallAfter(frame._set_status, f"{final.name}: {chapter_count} chapter(s)")
                if for_language is not None:
                    total_chapters += _export_translations(
                        frame, req, src, final, suffix, chapter_sound, opts, for_language
                    )
            except DocumentSpeechError as exc:
                errors += 1
                frame._wx.CallAfter(frame._set_status, f"Skipped {src.name}: {exc}")
            except Exception as exc:  # noqa: BLE001 - isolate per-file failures
                errors += 1
                frame._wx.CallAfter(frame._set_status, f"Error on {src.name}: {exc}")
            finally:
                shutil.rmtree(work_dir, ignore_errors=True)
        shutil.rmtree(sound_dir, ignore_errors=True)
        return (done, skipped, errors, total_chapters, total_subs)

    def on_success(result: object) -> None:
        done, skipped, errors, total_chapters, total_subs = result  # type: ignore[misc]
        if req.dry_run:
            frame._set_status(
                f"Dry run complete: {done} preview(s) written, {total_subs} "
                f"substitution(s), {errors} error(s)"
            )
            return
        frame._set_status(
            f"Batch speech export complete: {done} done ({total_chapters} chapters), "
            f"{skipped} skipped, {errors} error(s)"
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
    _save_project_profile(frame, request)  # auto-remember this run for the project
    _run(frame, request)
