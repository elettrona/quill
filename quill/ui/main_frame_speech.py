"""Offline speech commands: model manager + transcribe (#617, Speech S2 UI).

A mixin on :class:`~quill.ui.main_frame.MainFrame` providing the **AI > Speech**
commands. It uses stock, fully-accessible wx dialogs (single-choice picker,
message box, file dialog) and routes model downloads and transcription through
``_run_background_task`` so the UI never blocks. All speech logic lives in
``quill.core.speech`` (provider, service); this is thin wiring.
"""

from __future__ import annotations

from pathlib import Path


class SpeechCommandsMixin:
    """AI > Speech command handlers (offline model manager + transcription)."""

    # Relies on MainFrame helpers: _wx, frame, settings, _show_modal_dialog,
    # _show_message_box, _run_background_task, _create_document_tab, _announce,
    # _set_status.

    def _speech_provider(self) -> object:
        from quill.core.speech.service import DEFAULT_PROVIDER_ID, default_registry

        configured = str(getattr(self.settings, "speech_whisper_path", "") or "") or None
        return default_registry(configured).get(DEFAULT_PROVIDER_ID)

    # -- model manager ---------------------------------------------------- #

    def open_speech_models(self) -> None:
        from quill.core.speech.service import describe_models

        wx = self._wx
        provider = self._speech_provider()
        rows = describe_models(provider)  # type: ignore[arg-type]
        labels = [row.label for row in rows]
        with wx.SingleChoiceDialog(
            self.frame,
            "Speech models for offline transcription. Choose one to download or remove:",
            "Manage Speech Models",
            labels,
        ) as dialog:
            if self._show_modal_dialog(dialog, "Manage Speech Models") != wx.ID_OK:
                return
            selection = dialog.GetSelection()
        if selection < 0 or selection >= len(rows):
            return
        row = rows[selection]
        if row.installed:
            self._maybe_remove_speech_model(provider, row.id)
        else:
            self._maybe_download_speech_model(provider, row.id)

    def _maybe_remove_speech_model(self, provider: object, model_id: str) -> None:
        wx = self._wx
        confirm = self._show_message_box(
            f"Remove the '{model_id}' speech model from this computer?",
            "Remove Speech Model",
            wx.ICON_QUESTION | wx.YES_NO,
        )
        if confirm != wx.YES:
            return
        try:
            provider.remove_model(model_id)  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001 - surface a clean message
            self._set_status(f"Could not remove model: {exc}")
            return
        self._announce(f"Removed the {model_id} speech model.")

    def _maybe_download_speech_model(self, provider: object, model_id: str) -> None:
        wx = self._wx
        estimate = provider.estimate_model_size(model_id)  # type: ignore[attr-defined]
        confirm = self._show_message_box(
            f"Download the '{model_id}' speech model (about {estimate.download_mb} MB) "
            "from the Hugging Face Hub? It is stored on this computer and used for "
            "private, offline transcription.",
            "Download Speech Model",
            wx.ICON_QUESTION | wx.YES_NO,
        )
        if confirm != wx.YES:
            return

        def _work(progress):  # progress: (label, current, total)
            def _on_chunk(fraction: float, message: str) -> None:
                progress(message, int(fraction * 100), 100)

            return provider.download_model(model_id, _on_chunk)  # type: ignore[attr-defined]

        def _done(_installed: object) -> None:
            self._announce(f"Downloaded the {model_id} speech model.")

        self._run_background_task(f"Downloading {model_id} speech model", _work, _done)

    # -- transcription ---------------------------------------------------- #

    def transcribe_audio_offline(self) -> None:
        from quill.core.speech.catalog import RECOMMENDED_MODEL_ID

        wx = self._wx
        provider = self._speech_provider()
        installed = provider.list_installed_models()  # type: ignore[attr-defined]
        if not installed:
            offer = self._show_message_box(
                "No offline speech model is installed yet. Open Manage Speech Models "
                "to download one?",
                "Transcribe Audio or Video",
                wx.ICON_INFORMATION | wx.YES_NO,
            )
            if offer == wx.YES:
                self.open_speech_models()
            return
        installed_ids = [m.id for m in installed]
        model_id = (
            RECOMMENDED_MODEL_ID if RECOMMENDED_MODEL_ID in installed_ids else installed_ids[0]
        )

        with wx.FileDialog(
            self.frame,
            "Choose an audio or video file to transcribe",
            wildcard=(
                "Audio/Video (*.wav;*.mp3;*.m4a;*.flac;*.ogg;*.mp4)|"
                "*.wav;*.mp3;*.m4a;*.flac;*.ogg;*.mp4|All files (*.*)|*.*"
            ),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dialog:
            if self._show_modal_dialog(dialog, "Transcribe Audio or Video") != wx.ID_OK:
                return
            source = Path(dialog.GetPath())

        from quill.core.speech.provider import TranscriptionRequest

        request = TranscriptionRequest(
            source_path=source, model_id=model_id, output_timestamps=True
        )

        def _work(progress):
            def _on_progress(fraction: float, message: str) -> None:
                progress(message, int(fraction * 100), 100)

            return provider.transcribe_file(request, _on_progress)  # type: ignore[attr-defined]

        def _done(result: object) -> None:
            self._open_transcription_result(result, source)

        self._run_background_task(f"Transcribing {source.name}", _work, _done)

    def _open_transcription_result(self, result: object, source: Path) -> None:
        from quill.core.document import Document

        text = getattr(result, "full_text", "") or ""
        header = f"Transcript of {source.name}\n\n"
        self._create_document_tab(Document(text=header + text), select=True)
        words = len(text.split())
        self._announce(f"Transcription complete. {words} words. Review the draft transcript.")
