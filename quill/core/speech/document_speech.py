"""Drive a document end-to-end to a chaptered speech file (§4.8 glue).

This is the missing production seam between the structure-aware extractor
(:func:`quill.core.speech.text_polish.extract_sections`) and the chapter
assembler (:func:`quill.core.speech.chapter_assemble.assemble_chaptered_audio`).
The assembler deliberately takes an **injected** synthesizer so a real engine and
the test fake share one path; this module resolves a chosen engine/voice into that
synthesizer and runs the whole pipeline:

    document -> extract_sections -> assemble (per-engine synth + sounder) -> WAV/MP3

It is ``wx``-free and strict-typed (it lives in ``quill/core``), so the future
batch UI and headless callers can share exactly this resolution logic rather than
re-deriving it. Local engines only (SAPI 5, Kokoro, Piper, DECtalk, eSpeak-NG).
"""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from quill.core import read_aloud
from quill.core.speech.chapter_assemble import (
    ChapterAssembleOptions,
    ChapterAssembleResult,
    Synthesizer,
    assemble_chaptered_audio,
)
from quill.core.speech.text_polish import extract_sections

# Engine ids accepted by :func:`make_synthesizer`. These mirror the
# ``read_aloud_engine`` setting and the batch options' per-engine blocks.
SUPPORTED_ENGINES = ("sapi5", "kokoro", "piper", "dectalk", "espeak")


class DocumentSpeechError(Exception):
    """Raised when an engine cannot be resolved into a usable synthesizer."""


@dataclass(frozen=True, slots=True)
class SynthesisSpec:
    """A resolved request for one engine + voice + speed.

    ``rate`` is words-per-minute for SAPI 5 / eSpeak / DECtalk; ``speed`` is the
    Kokoro multiplier. ``voice`` is the engine-native voice id (e.g. ``am_liam``
    for Kokoro, a SAPI voice id, or — for Piper — the ``.onnx`` model path when
    ``piper_model`` is not given). ``executable`` overrides auto-discovery for the
    subprocess engines (Piper/DECtalk/eSpeak); when ``None`` they are discovered.
    """

    engine: str
    voice: str = ""
    rate: int = 200
    speed: float = 1.0
    volume: float = 1.0
    piper_model: Path | None = None
    executable: Path | None = None


def make_synthesizer(spec: SynthesisSpec) -> Synthesizer:
    """Resolve *spec* into a ``(text, out_wav) -> None`` synthesizer callable.

    Raises :class:`DocumentSpeechError` for an unknown engine or when a required
    executable/model for a subprocess engine cannot be found.
    """
    engine = spec.engine.strip().lower()
    # pyttsx3 was the historical id for the SAPI 5 path.
    if engine == "pyttsx3":
        engine = "sapi5"

    if engine == "sapi5":

        def _sapi5(text: str, out: Path) -> None:
            read_aloud.synthesize_to_file_with_sapi5(
                text, out, voice=spec.voice, rate=spec.rate, volume=spec.volume
            )

        return _sapi5

    if engine == "kokoro":

        def _kokoro(text: str, out: Path) -> None:
            read_aloud.synthesize_with_kokoro(
                text, out, voice=spec.voice or "af_heart", speed=spec.speed
            )

        return _kokoro

    if engine == "piper":
        piper_exe = spec.executable or read_aloud.discover_piper_executable()
        if piper_exe is None:
            raise DocumentSpeechError("Piper executable was not found.")
        model = spec.piper_model or (Path(spec.voice) if spec.voice else None)
        if model is None or not model.exists():
            raise DocumentSpeechError("A Piper .onnx model path is required.")
        piper_model: Path = model

        def _piper(text: str, out: Path) -> None:
            read_aloud.synthesize_with_piper(
                text, out, executable_path=piper_exe, model_path=piper_model
            )

        return _piper

    if engine == "dectalk":
        dectalk_exe = spec.executable or read_aloud.discover_dectalk_executable()
        if dectalk_exe is None:
            raise DocumentSpeechError("DECtalk runtime (DECtalk.dll) was not found.")

        def _dectalk(text: str, out: Path) -> None:
            read_aloud.synthesize_to_file_with_dectalk(
                text, out, executable_path=dectalk_exe, voice=spec.voice or "paul", rate=spec.rate
            )

        return _dectalk

    if engine == "espeak":
        espeak_exe = spec.executable or read_aloud.discover_espeak_executable()
        if espeak_exe is None:
            raise DocumentSpeechError("eSpeak-NG executable was not found.")

        def _espeak(text: str, out: Path) -> None:
            read_aloud.synthesize_with_espeak(
                text, out, executable_path=espeak_exe, voice=spec.voice or "en", rate=spec.rate
            )

        return _espeak

    raise DocumentSpeechError(
        f"Unknown speech engine {spec.engine!r}. Expected one of {SUPPORTED_ENGINES}."
    )


def _wrap_with_pronunciations(
    synth: Synthesizer, engine: str, dictionaries: list[Any] | None
) -> Synthesizer:
    """Wrap *synth* so the active pronunciation set is applied before synthesis."""
    if not dictionaries:
        return synth

    from quill.core.speech.pronunciation import apply_pronunciations

    engine_id = "sapi5" if engine.strip().lower() == "pyttsx3" else engine.strip().lower()

    def _corrected(text: str, out: Path) -> None:
        synth(apply_pronunciations(text, engine_id, dictionaries).text, out)

    return _corrected


def synthesize_document_to_chaptered_file(
    source: Path,
    output_path: Path,
    spec: SynthesisSpec,
    options: ChapterAssembleOptions,
    *,
    work_dir: Path | None = None,
    pronunciation_dictionaries: list[Any] | None = None,
) -> ChapterAssembleResult:
    """Convert one document to a chaptered audio file using a real engine.

    Extracts heading-bounded sections from *source*, synthesizes each with the
    engine described by *spec*, and assembles them into *output_path* with the
    inter-article gap / sounder and chapter markers described by *options*. When
    *work_dir* is ``None`` a temporary directory is created and removed afterward.

    *pronunciation_dictionaries* (the resolved active set, most-specific-first) is
    applied to **every spoken string** just before synthesis — so corrections
    reach the spoken heading, the body, and each sentence — while the chapter
    marker titles stay the raw heading text. Returns the
    :class:`ChapterAssembleResult` (the clean file plus, when the sounder is
    enabled, the with-tones variant carrying identical chapter timing).
    """
    sections = extract_sections(source)
    if not sections:
        raise DocumentSpeechError(f"No readable text found in {source.name}.")
    synth = make_synthesizer(spec)
    synth = _wrap_with_pronunciations(synth, spec.engine, pronunciation_dictionaries)

    owns_work_dir = work_dir is None
    work_dir = work_dir or Path(tempfile.mkdtemp(prefix="quill_docspeech_"))
    try:
        return assemble_chaptered_audio(sections, output_path, synth, options, work_dir=work_dir)
    finally:
        if owns_work_dir:
            import shutil

            shutil.rmtree(work_dir, ignore_errors=True)


_UNSAFE_NAME = re.compile(r'[\\/:*?"<>|\x00-\x1f]+')


def _safe_filename(text: str, fallback: str) -> str:
    """A filesystem-safe file stem from a heading title, trimmed and de-spaced."""
    cleaned = _UNSAFE_NAME.sub(" ", text).strip().rstrip(". ")
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned[:80].strip() or fallback


def synthesize_document_to_separate_files(
    source: Path,
    output_dir: Path,
    spec: SynthesisSpec,
    options: ChapterAssembleOptions,
    *,
    work_dir: Path | None = None,
    pronunciation_dictionaries: list[Any] | None = None,
) -> list[Path]:
    """Convert one document to **one audio file per article** (the `separate` mode).

    Each heading-bounded section becomes its own file in *output_dir*, named
    ``NNN - <heading>.<ext>`` (natural order preserved, headings made
    filesystem-safe). Each file is produced through the same single-section
    assembly path as the chaptered output (so engine, chunking, pronunciation,
    and format/encoding match), just without an inter-article boundary. Returns
    the written paths in order.
    """
    sections = extract_sections(source)
    if not sections:
        raise DocumentSpeechError(f"No readable text found in {source.name}.")
    synth = make_synthesizer(spec)
    synth = _wrap_with_pronunciations(synth, spec.engine, pronunciation_dictionaries)
    suffix = f".{options.output_format}" if options.output_format in {"mp3", "m4b"} else ".wav"

    owns_work_dir = work_dir is None
    work_dir = work_dir or Path(tempfile.mkdtemp(prefix="quill_docspeech_"))
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    try:
        for index, section in enumerate(sections, start=1):
            title = section.title.strip() or options.intro_section_title
            stem = f"{index:03d} - {_safe_filename(title, f'section_{index:03d}')}"
            out = output_dir / f"{stem}{suffix}"
            result = assemble_chaptered_audio(
                [section], out, synth, options, work_dir=work_dir / f"sep_{index:04d}"
            )
            written.append(result.output_path)
    finally:
        if owns_work_dir:
            import shutil

            shutil.rmtree(work_dir, ignore_errors=True)
    return written
