"""QUILL Audio Studio — the guided audio-production surface.

One studio, multiple journeys: narrate documents into chaptered speech audio
or an audiobook; combine a folder of recordings into one chaptered master.
The wizard collects a :class:`~quill.ui.audio_studio.request.BatchSpeechRequest`
and the existing ``quill.ui.batch_speech_runner`` executes it — the Studio is
the front door, not a second pipeline.
"""

from __future__ import annotations

from quill.ui.audio_studio.request import BatchSpeechRequest

__all__ = ["BatchSpeechRequest", "show_audio_studio"]


def show_audio_studio(frame: object) -> BatchSpeechRequest | None:
    """Open the Audio Studio wizard for *frame* (a MainFrame); return the request.

    Wires the wizard to the frame's engine catalog, voice lists, voice preview,
    defaults (global settings overlaid by the folder's project profile), the
    screen-reader announcer, and ``_show_modal_dialog``. Returns ``None`` on
    cancel. Imported lazily by the runner so a headless import stays wx-free.
    """
    from quill.core.i18n import _
    from quill.ui import batch_speech_runner as runner
    from quill.ui.audio_studio.wizard import run_audio_studio_wizard

    def on_preview(engine: str, voice: str) -> None:
        if voice:
            frame._preview_voice(engine, voice)
        else:
            frame._set_status(str(_("Choose a voice to preview")))

    return run_audio_studio_wizard(
        frame.frame,
        defaults=runner._defaults(frame),
        engine_options=runner._ENGINE_OPTIONS,
        engine_available=runner._engine_available(frame),
        voices_for=runner._voices_for,
        on_preview=on_preview,
        announce_cb=frame._announce,
        show_modal_fn=frame._show_modal_dialog,
    )
