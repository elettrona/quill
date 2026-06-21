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

    def _installed_or_prompt(self, provider: object, title: str) -> list | None:
        """Return installed models, or None after offering to open the manager."""
        wx = self._wx
        installed = provider.list_installed_models()  # type: ignore[attr-defined]
        if installed:
            return installed
        offer = self._show_message_box(
            "No offline speech model is installed yet. Open Manage Speech Models to download one?",
            title,
            wx.ICON_INFORMATION | wx.YES_NO,
        )
        if offer == wx.YES:
            self.open_speech_models()
        return None

    @staticmethod
    def _default_model_id(installed: list) -> str:
        from quill.core.speech.catalog import RECOMMENDED_MODEL_ID

        ids = [m.id for m in installed]
        return RECOMMENDED_MODEL_ID if RECOMMENDED_MODEL_ID in ids else ids[0]

    # -- captions --------------------------------------------------------- #

    def generate_captions_offline(self) -> None:
        wx = self._wx
        provider = self._speech_provider()
        installed = self._installed_or_prompt(provider, "Generate Captions")
        if installed is None:
            return
        model_id = self._default_model_id(installed)
        with wx.FileDialog(
            self.frame,
            "Choose an audio or video file to caption",
            wildcard=(
                "Audio/Video (*.wav;*.mp3;*.m4a;*.flac;*.ogg;*.mp4)|"
                "*.wav;*.mp3;*.m4a;*.flac;*.ogg;*.mp4|All files (*.*)|*.*"
            ),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dialog:
            if self._show_modal_dialog(dialog, "Generate Captions") != wx.ID_OK:
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

        self._run_background_task(
            f"Captioning {source.name}", _work, lambda result: self._save_captions(result, source)
        )

    def _save_captions(self, result: object, source: Path) -> None:
        from quill.core.speech import formatters

        wx = self._wx
        segments = getattr(result, "segments", ()) or ()
        if not segments:
            self._announce("No timed segments were produced, so captions cannot be made.")
            return
        formats = ["SubRip captions (.srt)", "WebVTT captions (.vtt)"]
        with wx.SingleChoiceDialog(
            self.frame, "Caption format:", "Generate Captions", formats
        ) as dialog:
            if self._show_modal_dialog(dialog, "Generate Captions") != wx.ID_OK:
                return
            choice = dialog.GetSelection()
        if choice == 0:
            text, ext = formatters.to_srt(segments), ".srt"
        else:
            text, ext = formatters.to_vtt(segments), ".vtt"
        with wx.FileDialog(
            self.frame,
            "Save captions",
            defaultFile=f"{source.stem}{ext}",
            wildcard="Caption files (*.srt;*.vtt)|*.srt;*.vtt|All files (*.*)|*.*",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as dialog:
            if self._show_modal_dialog(dialog, "Save captions") != wx.ID_OK:
                return
            target = Path(dialog.GetPath())
        target.write_text(text, encoding="utf-8", newline="\n")
        self._announce(f"Captions saved to {target.name}.")

    # -- dictation (offline, push-to-talk) -------------------------------- #

    def dictate_offline_toggle(self) -> None:
        recorder = getattr(self, "_mic_recorder", None)
        if recorder is not None and recorder.is_recording:
            self._stop_and_insert_dictation(recorder)
        else:
            self._start_dictation()

    def _start_dictation(self) -> None:
        from quill.core.speech.capture import MicRecorder, capture_available

        wx = self._wx
        if not capture_available():
            self._show_message_box(
                "Offline dictation needs microphone-capture support (the optional "
                "'sounddevice' package). You can also use Windows dictation with "
                "Ctrl+Alt+V.",
                "Dictate (Offline)",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        provider = self._speech_provider()
        if self._installed_or_prompt(provider, "Dictate (Offline)") is None:
            return
        from quill.core.speech.service import load_input_device

        recorder = MicRecorder()
        try:
            recorder.start(load_input_device())
        except Exception as exc:  # noqa: BLE001 - surface a clean message
            self._set_status(f"Could not start dictation: {exc}")
            return
        self._mic_recorder = recorder
        self._play_speech_sound("transcription_started")
        self._set_status("Dictation listening")
        self._announce("Listening. Run Dictate (Offline) again to stop and insert.")

    def _stop_and_insert_dictation(self, recorder: object) -> None:
        self._mic_recorder = None
        self._play_speech_sound("transcription_stopped")
        try:
            wav_path = recorder.stop()  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Dictation failed: {exc}")
            return
        provider = self._speech_provider()
        installed = provider.list_installed_models()  # type: ignore[attr-defined]
        if not installed:
            self._set_status("No speech model installed.")
            return
        model_id = self._default_model_id(installed)

        from quill.core.speech.provider import TranscriptionRequest

        request = TranscriptionRequest(source_path=wav_path, model_id=model_id)

        def _work(progress):
            def _on_progress(fraction: float, message: str) -> None:
                progress(message, int(fraction * 100), 100)

            try:
                return provider.transcribe_file(request, _on_progress)  # type: ignore[attr-defined]
            finally:
                try:
                    wav_path.unlink(missing_ok=True)
                except OSError:
                    pass

        self._set_status("Transcribing dictation")
        self._announce("Transcribing dictation...")
        self._run_background_task("Transcribing dictation", _work, self._insert_dictation_result)

    def _insert_dictation_result(self, result: object) -> None:
        text = (getattr(result, "full_text", "") or "").strip()
        editor = getattr(self, "editor", None)
        if not text or editor is None:
            self._set_status("Dictation: no speech detected")
            self._announce("No speech detected.")
            return
        editor.WriteText(text + " ")
        self._play_speech_sound("transcription_word_inserted")
        words = len(text.split())
        self._set_status(f"Dictation inserted {words} words")
        self._announce(f"Inserted {words} words. Press Control+Z to undo.")

    @staticmethod
    def _play_speech_sound(event_id: str) -> None:
        """Play a dictation earcon (distinct from other sounds); never raises."""
        try:
            from quill.ui.sound_manager import post_sound

            post_sound(event_id)
        except Exception:  # noqa: BLE001 - a missing sound must not break dictation
            pass

    # -- microphone selection --------------------------------------------- #

    def choose_dictation_microphone(self) -> None:
        from quill.core.speech.capture import list_input_devices
        from quill.core.speech.service import load_input_device, save_input_device

        wx = self._wx
        devices = list_input_devices()
        if not devices:
            self._show_message_box(
                "No microphones were found, or microphone-capture support (the "
                "optional 'sounddevice' package) is not installed.",
                "Dictation Microphone",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        current = load_input_device()
        labels = ["System default microphone"] + [name for _index, name in devices]
        selected_row = 0
        for row, (index, _name) in enumerate(devices, start=1):
            if index == current:
                selected_row = row
        with wx.SingleChoiceDialog(
            self.frame,
            "Choose the microphone for offline dictation:",
            "Dictation Microphone",
            labels,
        ) as dialog:
            dialog.SetSelection(selected_row)
            if self._show_modal_dialog(dialog, "Dictation Microphone") != wx.ID_OK:
                return
            choice = dialog.GetSelection()
        if choice <= 0:
            save_input_device(-1)
            self._announce("Dictation microphone set to the system default.")
            return
        index, name = devices[choice - 1]
        save_input_device(index)
        self._announce(f"Dictation microphone set to {name}.")

    # -- command registration --------------------------------------------- #

    def _register_speech_commands(self) -> None:
        specs = [
            ("tools.speech_models", "Manage Speech Models", self.open_speech_models),
            (
                "tools.speech_transcribe",
                "Transcribe Audio or Video (Offline)",
                self.transcribe_audio_offline,
            ),
            (
                "tools.speech_captions",
                "Generate Captions (Offline)",
                self.generate_captions_offline,
            ),
            ("tools.speech_dictate", "Dictate (Offline)", self.dictate_offline_toggle),
            ("tools.speech_microphone", "Dictation Microphone", self.choose_dictation_microphone),
        ]
        for command_id, title, handler in specs:
            self.commands.try_register(
                command_id,
                title,
                handler,
                self._binding_for(command_id),
                feature_id="core.dictation",
            )
