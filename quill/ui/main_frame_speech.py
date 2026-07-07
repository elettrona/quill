"""Offline speech commands: model manager + transcribe (#617, Speech S2 UI).

A mixin on :class:`~quill.ui.main_frame.MainFrame` providing the **AI > Speech**
commands. It uses stock, fully-accessible wx dialogs (single-choice picker,
message box, file dialog) and routes model downloads and transcription through
``_run_background_task`` so the UI never blocks. All speech logic lives in
``quill.core.speech`` (provider, service); this is thin wiring.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

# Transcribe/Captions accept these; ffmpeg transcodes them to 16 kHz mono WAV.
_AV_EXTS = "*.wav;*.mp3;*.m4a;*.aac;*.flac;*.ogg;*.opus;*.wma;*.mp4;*.m4v;*.mov;*.mkv;*.webm;*.avi"
_AUDIO_VIDEO_WILDCARD = f"Audio/Video ({_AV_EXTS})|{_AV_EXTS}|All files (*.*)|*.*"


class SpeechCommandsMixin:
    """AI > Speech command handlers (offline model manager + transcription)."""

    # Relies on MainFrame helpers: _wx, frame, settings, _show_modal_dialog,
    # _show_message_box, _run_background_task, _create_document_tab, _announce,
    # _set_status.

    def _speech_registry(self) -> object:
        from quill.core.speech.service import default_registry

        configured = str(getattr(self.settings, "speech_whisper_path", "") or "") or None
        return default_registry(configured)

    def _speech_provider(self) -> object:
        from quill.core.speech.service import DEFAULT_PROVIDER_ID

        registry = self._speech_registry()
        chosen = str(getattr(self.settings, "speech_provider", "") or "")
        if chosen:
            provider = registry.get(chosen)  # type: ignore[attr-defined]
            try:
                if provider is not None and provider.is_available():
                    return provider
            except Exception:  # noqa: BLE001 - fall back to the bundled engine
                pass
        return registry.get(DEFAULT_PROVIDER_ID)  # type: ignore[attr-defined]

    def _voice_provider(self) -> object:
        """The speech engine that powers the voice-interaction features.

        Honors ``settings.voice_recognition_engine`` — whisper.cpp for accuracy,
        Vosk for fast, low-overhead streaming (ideal for the always-listening
        wake word) — and falls back to the main speech provider when the chosen
        engine is unavailable or has no installed model, so voice always works.
        """
        chosen = str(getattr(self.settings, "voice_recognition_engine", "") or "").strip()
        if chosen:
            registry = self._speech_registry()
            provider = registry.get(chosen)  # type: ignore[attr-defined]
            try:
                if (
                    provider is not None
                    and provider.is_available()
                    and provider.list_installed_models()
                ):
                    return provider
            except Exception:  # noqa: BLE001 - fall back to the main engine
                pass
        return self._speech_provider()

    def _dictation_provider(self) -> object:
        """Cached speech provider for dictation so a loaded model persists across
        sessions (and a startup prewarm stays warm). _speech_registry() builds a
        fresh provider each call, which would reload the model every dictation.
        Rebuilt when the chosen engine changes."""
        chosen = str(getattr(self.settings, "speech_provider", "") or "")
        cached = getattr(self, "_dictation_provider_cache", None)
        if cached is not None and getattr(self, "_dictation_provider_key", None) == chosen:
            provider = cached
        else:
            provider = self._speech_provider()
            self._dictation_provider_cache = provider
            self._dictation_provider_key = chosen
        # Track for the idle-unload / low-resource policy. note_loaded registers or
        # re-touches (so it re-tracks after an idle sweep). unload() frees the model;
        # the cached provider object persists and reloads on the next dictation.
        try:
            from quill.core import lifecycle_service

            lifecycle_service.note_loaded("speech:dictation", provider.unload)  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001 - lifecycle tracking must never break dictation
            pass
        return provider

    def invalidate_dictation_provider(self) -> None:
        """Drop the cached dictation provider (after an engine/model change)."""
        self._dictation_provider_cache = None
        try:
            from quill.core import lifecycle_service

            lifecycle_service.note_unloaded("speech:dictation")
        except Exception:  # noqa: BLE001 - lifecycle untracking must never raise
            pass

    def prewarm_dictation_model(self) -> None:
        """Load the dictation model in the background so the first dictation is
        fast. Best-effort; never blocks the UI or raises. The cached provider
        (_dictation_provider) keeps the model loaded for later dictations."""
        import threading

        if not bool(getattr(self.settings, "warm_dictation_model", True)):
            return

        def _work() -> None:
            try:
                from quill.core.speech.capture import capture_available

                if not capture_available():
                    return
                provider = self._dictation_provider()
                installed = provider.list_installed_models()  # type: ignore[attr-defined]
                warm = getattr(provider, "warm", None)
                if installed and callable(warm):
                    from quill.core import lifecycle_service

                    # Low-resource mode may evict another engine before we warm this one.
                    lifecycle_service.reserve("speech:dictation")
                    warm(self._default_model_id(installed))
                    import logging

                    logging.getLogger(__name__).info("dictation: speech model prewarmed")
            except Exception:  # noqa: BLE001 - prewarm must never break startup
                pass

        threading.Thread(target=_work, daemon=True, name="quill-dictation-prewarm").start()

    def prewarm_kokoro_model(self) -> None:
        """Warm the Kokoro ONNX model in the background so the first preview or
        read-aloud is fast. Best-effort; gated by the warm_kokoro_model setting."""
        if not bool(getattr(self.settings, "warm_kokoro_model", True)):
            return
        import threading

        def _work() -> None:
            try:
                from quill.core.read_aloud import warm_kokoro_onnx

                if warm_kokoro_onnx():
                    import logging

                    logging.getLogger(__name__).info("read-aloud: kokoro model prewarmed")
            except Exception:  # noqa: BLE001 - prewarm must never break startup
                pass

        threading.Thread(target=_work, daemon=True, name="quill-kokoro-prewarm").start()

    # -- model manager ---------------------------------------------------- #

    def open_speech_models(self) -> None:
        """Open the unified Speech Hub on the Dictation tab."""
        self.open_speech_hub(1)

    def set_huggingface_token(self) -> None:
        """Store an optional Hugging Face access token for model downloads (#617).

        A token is not required for QUILL's public models, but it raises Hugging
        Face's anonymous rate limits. First-time users are guided to create one
        (with an offer to open the token page); the token is then entered masked
        and saved to the OS credential store, not to settings. Blank removes it.
        """
        import webbrowser

        from quill.core.speech.hf_auth import HF_TOKEN_URL, load_hf_token, save_hf_token

        wx = self._wx
        current = load_hf_token()
        if not current:
            steps = (
                "A free Hugging Face access token raises download rate limits. It is "
                "optional — QUILL's speech models work without one.\n\n"
                "To create a token:\n"
                "1. Sign in or sign up at huggingface.co (it is free).\n"
                "2. Open your profile menu, then Settings, then Access Tokens.\n"
                "3. Create a token with the 'Read' role and copy it.\n"
                "4. Come back here and paste it.\n\n"
                "Open the Hugging Face token page in your browser now?"
            )
            choice = self._show_message_box(
                steps, "Hugging Face Token", wx.ICON_INFORMATION | wx.YES_NO | wx.CANCEL
            )
            if choice == wx.CANCEL:
                return
            if choice == wx.YES:
                opened = webbrowser.open(HF_TOKEN_URL)
                self._set_status(
                    "Opened the Hugging Face token page in your browser."
                    if opened
                    else f"Create a token at {HF_TOKEN_URL}"
                )
        prompt = "Paste your Hugging Face access token. Leave blank to remove a saved token."
        dlg = wx.PasswordEntryDialog(self.frame, prompt, "Hugging Face Token", current)
        if self._show_modal_dialog(dlg, "Hugging Face Token") != wx.ID_OK:
            return
        value = dlg.GetValue().strip()
        try:
            save_hf_token(value)
        except Exception as exc:  # noqa: BLE001 - surface a clean message
            self._set_status(f"Could not save token: {exc}")
            return
        message = "Hugging Face token saved." if value else "Hugging Face token cleared."
        self._announce(message)
        self._set_status(message)

    def download_ffmpeg(self) -> None:
        """Download an official ffmpeg build so any audio/video format transcribes.

        ffmpeg is GPL/LGPL and QUILL does not bundle it; this fetches it from the
        official builder on an explicit action, into the QUILL tools folder the
        resolver searches. Runs on a worker thread behind a cancelable percentage.
        """
        import threading

        from quill.core.speech.ffmpeg import ffmpeg_available
        from quill.core.speech.ffmpeg_install import (
            FFmpegInstallError,
            ffmpeg_install_supported,
            install_ffmpeg,
        )
        from quill.ui.ai_transcribe_dialog import AIProgressDialog

        wx = self._wx
        if not ffmpeg_install_supported():
            self._show_message_box(
                "Automatic ffmpeg download is Windows-only. On macOS install it with "
                "Homebrew (brew install ffmpeg); on Linux use your package manager.",
                "Download FFmpeg",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        if ffmpeg_available():
            again = self._show_message_box(
                "ffmpeg is already available on this computer. Download QUILL's own "
                "managed copy anyway?",
                "Download FFmpeg",
                wx.ICON_QUESTION | wx.YES_NO,
            )
            if again != wx.YES:
                return
        confirm = self._show_message_box(
            "Download ffmpeg (about 110 MB) from the official Gyan.dev build so QUILL "
            "can transcribe MP3, M4A, MP4, and other formats? ffmpeg is open-source "
            "(GPL/LGPL) and is fetched directly from the builder; QUILL does not bundle "
            "it.",
            "Download FFmpeg",
            wx.ICON_QUESTION | wx.YES_NO,
        )
        if confirm != wx.YES:
            return
        cancel = threading.Event()
        progress = AIProgressDialog(
            self.frame,
            "Downloading FFmpeg",
            "Preparing to download ffmpeg...",
            on_cancel=cancel.set,
            status_fn=self._set_status,
        )
        progress.show()
        self._announce("Downloading ffmpeg.")

        def _on_progress(fraction: float, message: str) -> None:
            if cancel.is_set():
                raise FFmpegInstallError("Download cancelled.")
            percent = int(max(0.0, min(1.0, fraction)) * 100)
            progress.set_progress(percent, f"{message} {percent}%")

        def _run() -> None:
            try:
                install_ffmpeg(_on_progress)
            except Exception as exc:  # noqa: BLE001 - surface a clean message
                wx.CallAfter(progress.close)
                if cancel.is_set():
                    wx.CallAfter(self._set_status, "ffmpeg download cancelled.")
                    wx.CallAfter(self._announce, "ffmpeg download cancelled.")
                else:
                    wx.CallAfter(self._set_status, f"Could not install ffmpeg: {exc}")
                    wx.CallAfter(self._announce, f"Could not install ffmpeg. {exc}")
                return
            wx.CallAfter(progress.close)
            done = "ffmpeg installed. You can now transcribe more audio and video formats."
            wx.CallAfter(self._set_status, done)
            wx.CallAfter(self._announce, done)

        threading.Thread(  # GATE-40-OK: ffmpeg download worker.
            target=_run, daemon=True
        ).start()

    def open_optional_components(self) -> None:
        """Help > Download Optional Components: one place to see what is installed
        versus available, and fetch any of it.

        The picker (quill/ui/optional_components_dialog) returns the chosen
        component id; we then run that component's existing, tested download flow
        (each shows its own progress), so there are no stacked modals."""
        from quill.core.optional_components import gather_optional_components
        from quill.ui.optional_components_dialog import show_optional_components_picker

        wx = self._wx
        components = gather_optional_components()
        chosen = show_optional_components_picker(
            wx, self.frame, components, self._show_modal_dialog
        )
        if not chosen:
            return
        if chosen.startswith("spell-"):
            from quill.ui.spell_language import _download_then_apply

            _download_then_apply(wx, self, chosen[len("spell-") :])
            return
        actions = {
            "whispercpp": self.download_offline_speech_engine,
            "vosk": self.download_vosk,
            "kokoro": self._download_kokoro_models,
            "espeak": self.download_espeak_exe,
            "dectalk": self.download_dectalk_exe,
            "ffmpeg": self.download_ffmpeg,
            "pandoc": self.download_pandoc,
            "braille": self.download_braille_pack,
            "libmpv": self.download_libmpv,
            "mathcat": self.download_mathcat,
        }
        action = actions.get(chosen)
        if action is not None:
            action()

    def download_braille_pack(self, *, on_done: Callable[[bool], None] | None = None) -> None:
        """Fetch the braille pack on demand (footprint unbundle).

        liblouis tables + BRF profiles that power the Translation submenu and
        BRF/embossing export. Pinned + SHA-256-verified via
        quill.core.braille_pack.install_braille_pack, on a worker thread with
        live status progress (no cancel affordance — the fetch is ~9 MB),
        blocked in Safe Mode. Refreshes the menu on success so Translation
        appears without a restart."""
        from quill.core.braille_pack import install_braille_pack, is_braille_pack_installed

        wx = self._wx
        if bool(getattr(self, "_safe_mode", False)):
            self._announce("Downloading the braille pack is disabled in Safe Mode.")
            return
        if is_braille_pack_installed():
            again = self._show_message_box(
                "The braille pack is already installed. Download QUILL's verified "
                "copy again anyway?",
                "Braille Pack",
                wx.ICON_QUESTION | wx.YES_NO,
            )
            if again != wx.YES:
                if on_done is not None:
                    on_done(True)
                return
        proceed = self._show_message_box(
            "QUILL will download the braille translation pack (liblouis tables and "
            "BRF profiles, about 9 MB) and verify it. It powers the Translation "
            "submenu and BRF/embossing export. Continue?",
            "Download Braille Pack",
            wx.ICON_INFORMATION | wx.YES_NO,
        )
        if proceed != wx.YES:
            return

        def _work(progress):
            return install_braille_pack(
                lambda fraction, message: progress(message, int(fraction * 100), 100)
            )

        def _finished(result: object) -> None:
            ok = bool(result)
            if ok:
                self._announce("Braille pack installed. Translation is ready.")
                self._request_menu_refresh()
            else:
                self._announce("The braille pack could not be installed.")
            if on_done is not None:
                on_done(ok)

        self._run_background_task("Downloading braille pack", _work, _finished)

    def download_libmpv(self, *, on_done: Callable[[bool], None] | None = None) -> None:
        """Fetch the mpv playback library for the Audio Studio player.

        Pinned + SHA-256-verified via quill.core.release_assets (the zip carries
        the GPL texts, mpv's Copyright, and a corresponding-source offer), on a
        worker thread with live progress, blocked in Safe Mode. The Audio
        Studio's player prefers libmpv automatically on its next open; nothing
        else in QUILL changes."""
        from quill.core.optional_components import _libmpv_installed

        wx = self._wx
        if bool(getattr(self, "_safe_mode", False)):
            self._announce("Downloading components is disabled in Safe Mode.")
            return
        if _libmpv_installed():
            again = self._show_message_box(
                "The mpv player engine is already installed. Download QUILL's "
                "verified copy again anyway?",
                "mpv Player Engine",
                wx.ICON_QUESTION | wx.YES_NO,
            )
            if again != wx.YES:
                if on_done is not None:
                    on_done(True)
                return
        proceed = self._show_message_box(
            "QUILL will download the mpv playback library (about 44 MB) and verify "
            "it. It upgrades the Audio Studio's player to gapless audio with exact "
            "seeking; the built-in Windows engine keeps working without it. "
            "Continue?",
            "Download mpv Player Engine",
            wx.ICON_INFORMATION | wx.YES_NO,
        )
        if proceed != wx.YES:
            return

        def _work(progress):
            from quill.core.release_assets import fetch_component
            from quill.core.speech.engine_install import engine_packs_dir

            fetch_component(
                "libmpv",
                engine_packs_dir() / "mpv",
                progress=lambda fraction, message: progress(message, int(fraction * 100), 100),
                label="Downloading the mpv player engine...",
            )
            return True

        def _finished(result: object) -> None:
            ok = bool(result)
            if ok:
                self._announce(
                    "mpv player engine installed. The Audio Studio's player will "
                    "use it the next time it opens."
                )
            else:
                self._announce("The mpv player engine could not be installed.")
            if on_done is not None:
                on_done(ok)

        self._run_background_task("Downloading mpv player engine", _work, _finished)

    def download_mathcat(self, *, on_done: Callable[[bool], None] | None = None) -> None:
        """Fetch the MathCAT math-speech engine for Explore Equation Structure.

        Pinned + SHA-256-verified via quill.core.release_assets, on a worker
        thread with live progress, blocked in Safe Mode. "Read this part
        aloud" uses it automatically the next time it runs; nothing else in
        QUILL changes, and the simpler built-in template reading keeps
        working without it."""
        from quill.core.optional_components import _mathcat_installed

        wx = self._wx
        if bool(getattr(self, "_safe_mode", False)):
            self._announce("Downloading components is disabled in Safe Mode.")
            return
        if _mathcat_installed():
            again = self._show_message_box(
                "The MathCAT math speech engine is already installed. Download "
                "QUILL's verified copy again anyway?",
                "MathCAT Math Speech Engine",
                wx.ICON_QUESTION | wx.YES_NO,
            )
            if again != wx.YES:
                if on_done is not None:
                    on_done(True)
                return
        proceed = self._show_message_box(
            "QUILL will download the MathCAT math speech engine (about 3 MB) and "
            "verify it. It upgrades Insert > Explore Equation Structure...'s "
            '"Read this part aloud" to real natural-language math speech; the '
            "simpler built-in reading keeps working without it. Continue?",
            "Download MathCAT Math Speech Engine",
            wx.ICON_INFORMATION | wx.YES_NO,
        )
        if proceed != wx.YES:
            return

        def _work(progress):
            from quill.core.math.mathcat_engine import pack_dir
            from quill.core.release_assets import fetch_component

            fetch_component(
                "mathcat",
                pack_dir(),
                progress=lambda fraction, message: progress(message, int(fraction * 100), 100),
                label="Downloading the MathCAT math speech engine...",
            )
            return True

        def _finished(result: object) -> None:
            ok = bool(result)
            if ok:
                self._announce(
                    "MathCAT math speech engine installed. Explore Equation "
                    "Structure will use it the next time it runs."
                )
            else:
                self._announce("The MathCAT math speech engine could not be installed.")
            if on_done is not None:
                on_done(ok)

        self._run_background_task("Downloading MathCAT math speech engine", _work, _finished)

    def download_pandoc(self, *, on_done: Callable[[bool], None] | None = None) -> None:
        """Fetch the official, pinned Pandoc build on demand (footprint unbundle).

        Pandoc is no longer bundled: this runs from the Download Optional
        Components dialog and from the first-use prompt when a conversion needs
        it. Pinned + SHA-256-verified (quill.core.pandoc_install), on a worker
        thread behind a cancelable percentage (matching download_ffmpeg and the
        other on-demand downloads, #806), blocked in Safe Mode. ``on_done``
        (if given) is called on the UI thread with True on success."""
        import threading

        from quill.core.external_tools import get_external_tool_status
        from quill.core.pandoc_install import (
            PANDOC_DOWNLOAD_BYTES,
            PandocInstallError,
            install_pandoc,
            pandoc_install_supported,
        )
        from quill.ui.ai_transcribe_dialog import AIProgressDialog

        wx = self._wx
        if bool(getattr(self, "_safe_mode", False)):
            self._announce("Downloading Pandoc is disabled in Safe Mode.")
            return
        if not pandoc_install_supported():
            self._show_message_box(
                "The managed Pandoc download is Windows-only. On macOS install it "
                "with Homebrew (brew install pandoc); QUILL will find it automatically.",
                "Pandoc",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        if get_external_tool_status("pandoc").installed:
            again = self._show_message_box(
                "Pandoc is already available. Download QUILL's verified copy again anyway?",
                "Pandoc",
                wx.ICON_QUESTION | wx.YES_NO,
            )
            if again != wx.YES:
                if on_done is not None:
                    on_done(True)
                return
        approx_mb = round(PANDOC_DOWNLOAD_BYTES / 1_000_000)
        proceed = self._show_message_box(
            f"QUILL will download Pandoc (the official jgm/pandoc build, about "
            f"{approx_mb} MB) and verify it. It powers Word, ODT, EPUB, and RTF "
            "conversion. Continue?",
            "Download Pandoc",
            wx.ICON_INFORMATION | wx.YES_NO,
        )
        if proceed != wx.YES:
            return
        cancel = threading.Event()
        progress = AIProgressDialog(
            self.frame,
            "Downloading Pandoc",
            "Preparing to download Pandoc...",
            on_cancel=cancel.set,
            status_fn=self._set_status,
        )
        progress.show()
        self._announce("Downloading Pandoc.")

        def _on_progress(fraction: float, message: str) -> None:
            if cancel.is_set():
                raise PandocInstallError("Download cancelled.")
            percent = int(max(0.0, min(1.0, fraction)) * 100)
            progress.set_progress(percent, f"{message} {percent}%")

        def _run() -> None:
            try:
                install_pandoc(_on_progress)
            except Exception as exc:  # noqa: BLE001 - surface a clean message
                wx.CallAfter(progress.close)
                if cancel.is_set():
                    wx.CallAfter(self._set_status, "Pandoc download cancelled.")
                    wx.CallAfter(self._announce, "Pandoc download cancelled.")
                else:
                    wx.CallAfter(self._set_status, f"Could not install Pandoc: {exc}")
                    wx.CallAfter(self._announce, f"Pandoc could not be installed. {exc}")
                if on_done is not None:
                    wx.CallAfter(on_done, False)
                return
            wx.CallAfter(progress.close)
            done = "Pandoc installed. Conversions are ready."
            wx.CallAfter(self._set_status, done)
            wx.CallAfter(self._announce, done)
            if on_done is not None:
                wx.CallAfter(on_done, True)

        threading.Thread(  # GATE-40-OK: Pandoc download worker.
            target=_run, daemon=True
        ).start()

    def download_offline_speech_engine(self) -> None:
        """Fetch the offline whisper.cpp engine from QUILL's verified release asset.

        The engine ships in the installer, so this is the recovery / optional path
        (e.g. an older install that pre-dated bundling, #742). The download is
        pinned + SHA-256-verified (quill.core.release_assets), runs on a worker
        thread behind a cancelable percentage, and is blocked in Safe Mode. The
        bundled copy is never required to be absent for this to be useful.
        """
        import threading

        from quill.core.release_assets import fetch_component
        from quill.core.speech import models
        from quill.core.speech.providers.whispercpp import resolve_whisper_executable
        from quill.ui.ai_transcribe_dialog import AIProgressDialog

        wx = self._wx
        if resolve_whisper_executable() is not None:
            again = self._show_message_box(
                "The offline speech engine is already installed. Download QUILL's "
                "verified copy again anyway?",
                "Download Offline Speech Engine",
                wx.ICON_QUESTION | wx.YES_NO,
            )
            if again != wx.YES:
                return
        confirm = self._show_message_box(
            "Download the offline speech engine (whisper.cpp, about 8 MB) from "
            "QUILL's own verified release? It powers private, on-device dictation and "
            "transcription, and the download is checksum-verified.",
            "Download Offline Speech Engine",
            wx.ICON_QUESTION | wx.YES_NO,
        )
        if confirm != wx.YES:
            return
        cancel = threading.Event()
        progress = AIProgressDialog(
            self.frame,
            "Downloading Offline Speech Engine",
            "Preparing to download the offline speech engine...",
            on_cancel=cancel.set,
            status_fn=self._set_status,
        )
        progress.show()
        self._announce("Downloading the offline speech engine.")
        last_percent = {"value": -1}

        def _on_progress(fraction: float, message: str) -> None:
            percent = int(max(0.0, min(1.0, fraction)) * 100)
            if percent == last_percent["value"]:
                return  # throttle UI updates to whole-percent changes (#748)
            last_percent["value"] = percent
            progress.set_progress(percent, f"{message} {percent}%")

        target = models.app_data_dir() / "speech-engine"

        def _run() -> None:
            try:
                fetch_component(
                    "whispercpp",
                    target,
                    progress=_on_progress,
                    should_cancel=cancel.is_set,
                    label="Downloading offline speech engine...",
                )
            except Exception as exc:  # noqa: BLE001 - surface a clean message
                wx.CallAfter(progress.close)
                if cancel.is_set():
                    wx.CallAfter(self._set_status, "Speech engine download cancelled.")
                    wx.CallAfter(self._announce, "Speech engine download cancelled.")
                else:
                    wx.CallAfter(self._set_status, f"Could not install the speech engine: {exc}")
                    wx.CallAfter(self._announce, f"Could not install the speech engine. {exc}")
                return
            wx.CallAfter(progress.close)
            done = "Offline speech engine installed. Dictation and transcription are ready."
            wx.CallAfter(self._set_status, done)
            wx.CallAfter(self._announce, done)

        threading.Thread(  # GATE-40-OK: speech engine download worker.
            target=_run, daemon=True
        ).start()

    def download_faster_whisper(self) -> None:
        """Install the optional Faster Whisper engine on demand (#669 follow-up).

        QUILL does not bundle Faster Whisper (its CTranslate2/ONNX dependencies are
        ~110 MB). This installs it wheel-only into a user-writable engine-pack folder
        on an explicit action, then adds it to sys.path so the engine appears in the
        speech registry. Runs on a worker thread behind a progress dialog.
        """
        import threading

        from quill.core.speech.engine_install import (
            EngineInstallError,
            faster_whisper_install_supported,
            install_faster_whisper,
            is_faster_whisper_available,
        )
        from quill.ui.ai_transcribe_dialog import AIProgressDialog

        wx = self._wx
        if not faster_whisper_install_supported():
            self._show_message_box(
                "This build cannot install Faster Whisper automatically. Install it "
                'from source with: pip install -e ".[fasterwhisper]".',
                "Download Faster Whisper",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        if is_faster_whisper_available():
            self._show_message_box(
                "Faster Whisper is already installed. Choose it in Manage Speech "
                "Models under Speech Engine.",
                "Download Faster Whisper",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        confirm = self._show_message_box(
            "Download and install the Faster Whisper speech engine (about 110 MB)? "
            "It is a faster, GPU-capable offline engine. The download happens now, "
            "directly from the Python Package Index; nothing is uploaded.",
            "Download Faster Whisper",
            wx.ICON_QUESTION | wx.YES_NO,
        )
        if confirm != wx.YES:
            return
        cancel = threading.Event()
        progress = AIProgressDialog(
            self.frame,
            "Installing Faster Whisper",
            "Preparing to install Faster Whisper...",
            on_cancel=cancel.set,
            status_fn=self._set_status,
        )
        progress.show()
        self._announce("Installing Faster Whisper.")

        def _on_progress(fraction: float, message: str) -> None:
            if cancel.is_set():
                raise EngineInstallError("Installation cancelled.")
            percent = int(max(0.0, min(1.0, fraction)) * 100)
            progress.set_progress(percent, f"{message} {percent}%")

        def _run() -> None:
            try:
                install_faster_whisper(_on_progress)
            except Exception as exc:  # noqa: BLE001 - surface a clean message
                wx.CallAfter(progress.close)
                if cancel.is_set():
                    wx.CallAfter(self._set_status, "Faster Whisper installation cancelled.")
                    wx.CallAfter(self._announce, "Faster Whisper installation cancelled.")
                else:
                    wx.CallAfter(self._set_status, f"Could not install Faster Whisper: {exc}")
                    wx.CallAfter(self._announce, f"Could not install Faster Whisper. {exc}")
                return
            done = (
                "Faster Whisper is ready. Click OK to open Manage Speech Models "
                "and download a model for it."
            )
            wx.CallAfter(self._set_status, "Faster Whisper installed.")
            wx.CallAfter(self._announce, "Faster Whisper installed.")
            progress.switch_to_ok(done, on_ok=self.open_speech_models)

        threading.Thread(  # GATE-40-OK: Faster Whisper install worker.
            target=_run, daemon=True
        ).start()

    def download_vosk(self) -> None:
        """Install the optional Vosk engine on demand (#669 follow-up).

        Vosk (Kaldi-based, ~50 MB) runs on very low RAM hardware with no GPU.
        Installed wheel-only into a user-writable engine-pack folder and activated
        on sys.path so the engine appears in the speech registry immediately.
        Runs on a worker thread behind a progress dialog.
        """
        import threading

        from quill.core.speech.engine_install import (
            EngineInstallError,
            install_vosk,
            is_vosk_available,
            vosk_install_supported,
        )
        from quill.ui.ai_transcribe_dialog import AIProgressDialog

        wx = self._wx
        if not vosk_install_supported():
            self._show_message_box(
                "This build cannot install Vosk automatically. Install it "
                "from source with: pip install vosk",
                "Install Vosk",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        if is_vosk_available():
            self._show_message_box(
                "Vosk is already installed. Choose it in Manage Speech Models under Speech Engine.",
                "Install Vosk",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        confirm = self._show_message_box(
            "Download and install the Vosk speech engine (about 50 MB)? "
            "It is a lightweight offline engine designed for low-RAM hardware "
            "with no GPU. The download happens directly from the Python Package "
            "Index; nothing is uploaded.",
            "Install Vosk",
            wx.ICON_QUESTION | wx.YES_NO,
        )
        if confirm != wx.YES:
            return
        cancel = threading.Event()
        progress = AIProgressDialog(
            self.frame,
            "Installing Vosk",
            "Preparing to install Vosk...",
            on_cancel=cancel.set,
            status_fn=self._set_status,
        )
        progress.show()
        self._announce("Installing Vosk.")

        def _on_progress(fraction: float, message: str) -> None:
            if cancel.is_set():
                raise EngineInstallError("Installation cancelled.")
            percent = int(max(0.0, min(1.0, fraction)) * 100)
            progress.set_progress(percent, f"{message} {percent}%")

        def _run() -> None:
            try:
                install_vosk(_on_progress)
            except Exception as exc:  # noqa: BLE001 - surface a clean message
                wx.CallAfter(progress.close)
                if cancel.is_set():
                    wx.CallAfter(self._set_status, "Vosk installation cancelled.")
                    wx.CallAfter(self._announce, "Vosk installation cancelled.")
                else:
                    wx.CallAfter(self._set_status, f"Could not install Vosk: {exc}")
                    wx.CallAfter(self._announce, f"Could not install Vosk. {exc}")
                return
            done = (
                "Vosk is ready. Click OK to open Manage Speech Models and download a model for it."
            )
            wx.CallAfter(self._set_status, "Vosk installed.")
            wx.CallAfter(self._announce, "Vosk installed.")
            progress.switch_to_ok(done, on_ok=self.open_speech_models)

        threading.Thread(  # GATE-40-OK: Vosk install worker.
            target=_run, daemon=True
        ).start()

    def download_dectalk_exe(self) -> None:
        """Download the DECtalk runtime (~30 MB) on demand.

        DECtalk is a classic American English synthesizer with 9 distinct voices.
        The runtime is downloaded from the dectalk/dectalk GitHub release, verified
        with a pinned SHA-256 (SEC-6), and saved to the managed speech folder so
        ``discover_dectalk_executable()`` finds it automatically on next use.
        Runs on a worker thread behind a progress dialog.
        """
        import threading

        from quill.core.dectalk_runtime import download_dectalk_runtime
        from quill.core.paths import app_data_dir
        from quill.core.read_aloud import discover_dectalk_executable
        from quill.core.settings import save_settings
        from quill.ui.ai_transcribe_dialog import AIProgressDialog

        wx = self._wx
        configured = getattr(self.settings, "read_aloud_dectalk_executable", "")
        if discover_dectalk_executable(configured) is not None:
            self._show_message_box(
                "DECtalk is already installed. Open Manage Voices to select a voice.",
                "Download DECtalk",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        confirm = self._show_message_box(
            "Download the DECtalk speech runtime (~30 MB) from GitHub?\n\n"
            "DECtalk is a classic American English synthesizer with 9 distinct "
            "voices (Paul, Betty, Harry, and more). The download is SHA-256 "
            "verified before extraction.",
            "Download DECtalk",
            wx.ICON_QUESTION | wx.YES_NO,
        )
        if confirm != wx.YES:
            return
        speech_root = app_data_dir() / "speech" / "dectalk"
        progress = AIProgressDialog(
            self.frame,
            "Downloading DECtalk",
            "Downloading DECtalk runtime...",
            on_cancel=None,
        )
        progress.show()
        self._announce("Downloading DECtalk runtime.")

        def _run() -> None:
            try:
                exe = download_dectalk_runtime(speech_root)
                self.settings.read_aloud_dectalk_executable = str(exe)
                save_settings(self.settings)
            except Exception as exc:  # noqa: BLE001
                wx.CallAfter(progress.close)
                wx.CallAfter(self._set_status, f"DECtalk download failed: {exc}")
                wx.CallAfter(self._announce, f"DECtalk download failed. {exc}")
                return
            done = "DECtalk is ready. Click OK to open Manage Voices and choose a voice."
            wx.CallAfter(self._set_status, "DECtalk ready.")
            wx.CallAfter(self._announce, "DECtalk ready.")
            progress.switch_to_ok(done, on_ok=self.choose_read_aloud_configuration)

        threading.Thread(  # GATE-40-OK: DECtalk runtime download worker.
            target=_run, daemon=True
        ).start()

    def download_piper_exe(self) -> None:
        """Download the Piper TTS engine (~22 MB) on demand.

        Piper is a fast, local, high-quality neural TTS engine. The Windows AMD64
        binary is downloaded from the pinned GitHub release, extracted to the
        managed speech folder, and immediately discoverable without restarting.
        Runs on a worker thread behind a progress dialog. Windows-only.
        """
        import threading

        from quill.core.read_aloud import discover_piper_executable
        from quill.core.speech.piper_install import (
            PiperInstallError,
            install_piper,
            piper_install_supported,
        )
        from quill.ui.ai_transcribe_dialog import AIProgressDialog

        wx = self._wx
        if not piper_install_supported():
            self._show_message_box(
                "Automatic Piper download is Windows-only. "
                "On other platforms, install Piper from "
                "https://github.com/rhasspy/piper/releases",
                "Download Piper",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        if discover_piper_executable() is not None:
            self._show_message_box(
                "Piper is already installed. Open Manage Voices to download a voice.",
                "Download Piper",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        confirm = self._show_message_box(
            "Download the Piper TTS engine (~22 MB) from GitHub?\n\n"
            "Piper is a fast, local, neural text-to-speech engine with dozens "
            "of high-quality English voices. After downloading, open Manage "
            "Voices again to download a Piper voice model.",
            "Download Piper",
            wx.ICON_QUESTION | wx.YES_NO,
        )
        if confirm != wx.YES:
            return
        cancel = threading.Event()
        progress = AIProgressDialog(
            self.frame,
            "Downloading Piper",
            "Preparing download...",
            on_cancel=cancel.set,
            status_fn=self._set_status,
        )
        progress.show()
        self._announce("Downloading Piper TTS engine.")

        def _on_progress(fraction: float, message: str) -> None:
            if cancel.is_set():
                raise PiperInstallError("Download cancelled.")
            percent = int(max(0.0, min(1.0, fraction)) * 100)
            progress.set_progress(percent, f"{message} {percent}%")

        def _run() -> None:
            try:
                install_piper(progress=_on_progress)
            except Exception as exc:  # noqa: BLE001
                wx.CallAfter(progress.close)
                if cancel.is_set():
                    wx.CallAfter(self._set_status, "Piper download cancelled.")
                    wx.CallAfter(self._announce, "Piper download cancelled.")
                else:
                    wx.CallAfter(self._set_status, f"Piper download failed: {exc}")
                    wx.CallAfter(self._announce, f"Piper download failed. {exc}")
                return
            done = "Piper is ready. Click OK to open Manage Voices and download a voice model."
            wx.CallAfter(self._set_status, "Piper ready.")
            wx.CallAfter(self._announce, "Piper ready.")
            progress.switch_to_ok(done, on_ok=self.choose_read_aloud_configuration)

        threading.Thread(  # GATE-40-OK: Piper engine download worker.
            target=_run, daemon=True
        ).start()

    def download_espeak_exe(self) -> None:
        """Download and extract eSpeak-NG (~50 MB) on demand.

        Downloads the official eSpeak-NG Windows x64 MSI from GitHub and
        extracts it admin-free via ``msiexec /a`` into the managed speech
        folder. ``discover_espeak_executable()`` picks up the result
        immediately without restarting. Runs on a worker thread.
        """
        import threading

        from quill.core.read_aloud import discover_espeak_executable
        from quill.core.settings import save_settings
        from quill.core.speech.espeak_install import (
            EspeakInstallError,
            espeak_install_supported,
            install_espeak,
        )
        from quill.ui.ai_transcribe_dialog import AIProgressDialog

        wx = self._wx
        if not espeak_install_supported():
            self._show_message_box(
                "Automatic eSpeak-NG download is Windows-only.\n\n"
                "On macOS install it with Homebrew: brew install espeak-ng\n"
                "On Linux use your package manager (apt/dnf/pacman).",
                "Download eSpeak-NG",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        configured = getattr(self.settings, "read_aloud_espeak_executable", "")
        if discover_espeak_executable(configured) is not None:
            self._show_message_box(
                "eSpeak-NG is already installed. Open Manage Voices to select a voice.",
                "Download eSpeak-NG",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        confirm = self._show_message_box(
            "Download eSpeak-NG (~50 MB) from GitHub?\n\n"
            "eSpeak-NG is a compact, open-source speech synthesizer with many "
            "English accents (British, American, Scottish, Indian, and more). "
            "It is extracted without admin rights using Windows Installer's "
            "admin-install mode.",
            "Download eSpeak-NG",
            wx.ICON_QUESTION | wx.YES_NO,
        )
        if confirm != wx.YES:
            return
        cancel = threading.Event()
        progress = AIProgressDialog(
            self.frame,
            "Downloading eSpeak-NG",
            "Preparing download...",
            on_cancel=cancel.set,
            status_fn=self._set_status,
        )
        progress.show()
        self._announce("Downloading eSpeak-NG.")

        def _on_progress(fraction: float, message: str) -> None:
            if cancel.is_set():
                raise EspeakInstallError("Download cancelled.")
            percent = int(max(0.0, min(1.0, fraction)) * 100)
            progress.set_progress(percent, f"{message} {percent}%")

        def _run() -> None:
            try:
                exe = install_espeak(_on_progress)
                # Save so settings-configured path also finds it immediately.
                self.settings.read_aloud_espeak_executable = str(exe)
                save_settings(self.settings)
            except Exception as exc:  # noqa: BLE001
                wx.CallAfter(progress.close)
                if cancel.is_set():
                    wx.CallAfter(self._set_status, "eSpeak-NG download cancelled.")
                    wx.CallAfter(self._announce, "eSpeak-NG download cancelled.")
                else:
                    wx.CallAfter(self._set_status, f"eSpeak-NG download failed: {exc}")
                    wx.CallAfter(self._announce, f"eSpeak-NG download failed. {exc}")
                return
            done = "eSpeak-NG is ready. Click OK to open Manage Voices and choose an accent."
            wx.CallAfter(self._set_status, "eSpeak-NG ready.")
            wx.CallAfter(self._announce, "eSpeak-NG ready.")
            progress.switch_to_ok(done, on_ok=self.choose_read_aloud_configuration)

        threading.Thread(  # GATE-40-OK: eSpeak-NG download worker.
            target=_run, daemon=True
        ).start()

    def download_kokoro_engine(self) -> None:
        """Install the optional Kokoro ONNX engine packages on demand.

        Installs ``kokoro-onnx`` and ``soundfile`` (~20 MB + onnxruntime) via
        pip into a user-writable engine-pack folder. Use this when the Kokoro
        model files are already downloaded but the Python packages are missing.
        Runs on a worker thread behind a progress dialog.
        """
        import threading

        from quill.core.speech.engine_install import (
            EngineInstallError,
            install_kokoro_onnx,
            is_kokoro_onnx_available,
            kokoro_onnx_install_supported,
        )
        from quill.ui.ai_transcribe_dialog import AIProgressDialog

        wx = self._wx
        if not kokoro_onnx_install_supported():
            self._show_message_box(
                "This build cannot install Kokoro ONNX automatically. Install it "
                "from source with: pip install kokoro-onnx soundfile",
                "Install Kokoro ONNX",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        if is_kokoro_onnx_available():
            self._show_message_box(
                "Kokoro ONNX is already installed. Choose Kokoro in Manage Voices.",
                "Install Kokoro ONNX",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        confirm = self._show_message_box(
            "Download and install the Kokoro ONNX engine (~20 MB)? "
            "This enables Kokoro's high-quality neural text-to-speech. "
            "You will also need to download the Kokoro models (~114 MB) from "
            "Manage Voices if you have not done so already.",
            "Install Kokoro ONNX",
            wx.ICON_QUESTION | wx.YES_NO,
        )
        if confirm != wx.YES:
            return
        cancel = threading.Event()
        progress = AIProgressDialog(
            self.frame,
            "Installing Kokoro ONNX",
            "Preparing to install Kokoro ONNX...",
            on_cancel=cancel.set,
            status_fn=self._set_status,
        )
        progress.show()
        self._announce("Installing Kokoro ONNX.")

        def _on_progress(fraction: float, message: str) -> None:
            if cancel.is_set():
                raise EngineInstallError("Installation cancelled.")
            percent = int(max(0.0, min(1.0, fraction)) * 100)
            progress.set_progress(percent, f"{message} {percent}%")

        def _run() -> None:
            try:
                install_kokoro_onnx(_on_progress)
            except Exception as exc:  # noqa: BLE001
                wx.CallAfter(progress.close)
                if cancel.is_set():
                    wx.CallAfter(self._set_status, "Kokoro ONNX installation cancelled.")
                    wx.CallAfter(self._announce, "Kokoro ONNX installation cancelled.")
                else:
                    wx.CallAfter(self._set_status, f"Could not install Kokoro ONNX: {exc}")
                    wx.CallAfter(self._announce, f"Could not install Kokoro ONNX. {exc}")
                return
            done = "Kokoro ONNX is ready. Click OK to open Manage Voices and choose a Kokoro voice."
            wx.CallAfter(self._set_status, "Kokoro ONNX installed.")
            wx.CallAfter(self._announce, "Kokoro ONNX installed.")
            progress.switch_to_ok(done, on_ok=self.choose_read_aloud_configuration)

        threading.Thread(  # GATE-40-OK: Kokoro ONNX install worker.
            target=_run, daemon=True
        ).start()

    def _maybe_remove_speech_model(self, provider: object, model_id: str) -> None:
        wx = self._wx
        confirm = self._show_message_box(
            f"Remove the '{model_id}' speech model from this computer? "
            "You can download it again later from Manage Speech Models.",
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

    def _maybe_download_speech_model(self, provider: object, row: object) -> None:
        from quill.core.speech.service import enough_disk_for, models_dir_free_gb

        wx = self._wx
        model_id = str(getattr(row, "id", ""))
        estimate = provider.estimate_model_size(model_id)  # type: ignore[attr-defined]
        notes: list[str] = []
        icon = wx.ICON_QUESTION
        warning = str(getattr(row, "ram_warning", "") or "")
        if warning:
            notes.append(f"{warning} It may run very slowly or fail to load.")
            icon = wx.ICON_WARNING
        gpu_note = str(getattr(row, "gpu_note", "") or "")
        if gpu_note:
            notes.append(gpu_note)
        free_gb = models_dir_free_gb()
        if not enough_disk_for(int(estimate.download_mb), free_gb):
            notes.append(
                f"Low disk space: this needs about {estimate.download_mb} MB but only "
                f"{free_gb:.1f} GB is free where models are stored."
            )
            icon = wx.ICON_WARNING
        extra = ("\n\nWarning: " + " ".join(notes)) if notes else ""
        # Be transparent about licensing when downloading on the user's behalf.
        license_name = str(getattr(row, "license_name", "") or "")
        card_url = str(getattr(row, "model_card_url", "") or "")
        license_line = ""
        if license_name:
            license_line = f"\n\nThis model is {license_name} licensed."
            if card_url:
                license_line += f" Model card: {card_url}"
        confirm = self._show_message_box(
            f"Download the '{model_id}' speech model (about {estimate.download_mb} MB) "
            "from the Hugging Face Hub? It is stored on this computer and used for "
            f"private, offline transcription.{license_line}{extra}",
            "Download Speech Model",
            icon | wx.YES_NO,
        )
        if confirm != wx.YES:
            return
        self._download_speech_model_with_progress(provider, model_id)

    def _download_speech_model_with_progress(self, provider: object, model_id: str) -> None:
        """Download a model on a worker thread, showing a cancelable progress gauge.

        The download never touches the UI thread (so the app stays responsive),
        reports a real percentage, and announces coarse milestones for screen
        readers. Cancel is cooperative: the progress callback raises when the
        user cancels, which aborts the stream and cleans up the partial file.
        """
        import threading

        from quill.core.speech.provider import SpeechError, download_progress_percent
        from quill.ui.ai_transcribe_dialog import AIProgressDialog

        wx = self._wx
        cancel = threading.Event()
        progress = AIProgressDialog(
            self.frame,
            "Downloading Speech Model",
            f"Preparing to download the {model_id} model...",
            on_cancel=cancel.set,
            status_fn=self._set_status,
        )
        progress.show()
        self._announce(f"Downloading the {model_id} speech model.")
        last_milestone = {"value": -1}
        last_percent = {"value": -1}

        def _on_chunk(fraction: float, message: str) -> None:
            if cancel.is_set():
                raise SpeechError("Download cancelled.")
            # Throttle to whole-percent changes: snapshot_download (Faster Whisper)
            # fires this per chunk and set_progress marshals each update to the UI
            # thread, so an unthrottled callback floods wx.CallAfter and freezes
            # then crashes the download (#748). ~100 updates/download instead.
            percent = download_progress_percent(fraction)
            if percent == last_percent["value"]:
                return
            last_percent["value"] = percent
            progress.set_progress(percent, f"{message} {percent}%")
            milestone = percent - (percent % 25)
            if percent < 100 and milestone != last_milestone["value"]:
                last_milestone["value"] = milestone
                wx.CallAfter(self._set_status, f"Downloading {model_id}: {percent}%")

        def _run() -> None:
            try:
                provider.download_model(model_id, _on_chunk)  # type: ignore[attr-defined]
            except SpeechError as exc:
                wx.CallAfter(progress.close)
                if cancel.is_set():
                    wx.CallAfter(self._set_status, f"Download of {model_id} cancelled.")
                    wx.CallAfter(self._announce, f"Download of the {model_id} model cancelled.")
                else:
                    wx.CallAfter(self._set_status, f"Could not download model: {exc}")
                    wx.CallAfter(self._announce, f"Could not download the model. {exc}")
                return
            except Exception as exc:  # noqa: BLE001 - surface a clean message
                wx.CallAfter(progress.close)
                wx.CallAfter(self._set_status, f"Could not download model: {exc}")
                wx.CallAfter(self._announce, f"Could not download the model. {exc}")
                return
            wx.CallAfter(self._set_status, f"Downloaded the {model_id} speech model.")
            wx.CallAfter(self._announce, f"Downloaded the {model_id} speech model.")
            # Confirm completion with a clear OK button (or, if minimized, a status
            # line) instead of silently closing — the silent close read as "nothing
            # happened" even when the model downloaded.
            progress.switch_to_ok(
                f"Downloaded the {model_id} speech model. It is ready to use for dictation."
            )

        threading.Thread(  # GATE-40-OK: speech model download worker.
            target=_run, daemon=True
        ).start()

    # -- transcription ---------------------------------------------------- #

    _TRANSCRIPT_FORMATS = (
        ("Plain text", "text"),
        ("Markdown", "markdown"),
        ("HTML", "html"),
    )

    def _select_model_and_diarize(self, installed: list) -> tuple[str, bool]:
        """Prefer an installed speaker-detection model (enables diarization)."""
        from quill.core.speech.catalog import is_diarization_model

        for model in installed:
            if is_diarization_model(model.id):
                return model.id, True
        return self._default_model_id(installed), False

    def _choose_transcript_format(self, title: str) -> str | None:
        wx = self._wx
        labels = [label for label, _key in self._TRANSCRIPT_FORMATS]
        with wx.SingleChoiceDialog(self.frame, "Transcript format:", title, labels) as dialog:
            if self._show_modal_dialog(dialog, title) != wx.ID_OK:
                return None
            choice = dialog.GetSelection()
        if 0 <= choice < len(self._TRANSCRIPT_FORMATS):
            return self._TRANSCRIPT_FORMATS[choice][1]
        return "text"

    def transcribe_audio_offline(self) -> None:
        wx = self._wx
        provider = self._speech_provider()
        installed = self._installed_or_prompt(provider, "Transcribe Audio or Video")
        if installed is None:
            return
        model_id, diarize = self._select_model_and_diarize(installed)
        fmt = self._choose_transcript_format("Transcribe Audio or Video")
        if fmt is None:
            return

        with wx.FileDialog(
            self.frame,
            "Choose an audio or video file to transcribe",
            wildcard=_AUDIO_VIDEO_WILDCARD,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dialog:
            if self._show_modal_dialog(dialog, "Transcribe Audio or Video") != wx.ID_OK:
                return
            source = Path(dialog.GetPath())

        from quill.core.speech.provider import TranscriptionRequest

        request = TranscriptionRequest(
            source_path=source, model_id=model_id, output_timestamps=True, diarize=diarize
        )

        import threading

        from quill.core.speech.provider import SpeechError
        from quill.ui.ai_transcribe_dialog import AIProgressDialog

        cancel = threading.Event()
        progress = AIProgressDialog(
            self.frame,
            "Transcribing",
            f"Transcribing {source.name}...",
            on_cancel=cancel.set,
            # Quiet status mirroring so a minimized run does not announce every
            # percentage over and over; the start/finish are announced once.
            status_fn=self._set_status_quiet,
        )
        progress.show()
        self._announce(f"Transcribing {source.name}. This can take a while for long files.")

        def _on_progress(fraction: float, message: str) -> None:
            if cancel.is_set():
                raise SpeechError("Transcription cancelled.")
            percent = int(max(0.0, min(1.0, fraction)) * 100)
            progress.set_progress(percent, f"{message} {percent}%")

        def _run() -> None:
            try:
                result = provider.transcribe_file(request, _on_progress)  # type: ignore[attr-defined]
            except SpeechError as exc:
                wx.CallAfter(progress.close)
                msg = (
                    f"Transcription of {source.name} cancelled."
                    if cancel.is_set()
                    else f"Could not transcribe {source.name}: {exc}"
                )
                wx.CallAfter(self._set_status, msg)
                return
            except Exception as exc:  # noqa: BLE001 - surface a clean message
                wx.CallAfter(progress.close)
                wx.CallAfter(self._set_status, f"Could not transcribe {source.name}: {exc}")
                return
            # Done: close the progress dialog (which clears its status-bar line) and
            # open the transcript, which announces the word count once.
            wx.CallAfter(progress.close)
            wx.CallAfter(self._open_transcription_result, result, fmt)

        threading.Thread(  # GATE-40-OK: offline transcription worker.
            target=_run, daemon=True
        ).start()

    def _open_transcription_result(self, result: object, fmt: str = "text") -> None:
        from quill.core.document import Document
        from quill.core.speech import formatters

        if fmt == "markdown":
            text = formatters.to_markdown(result)  # type: ignore[arg-type]
        elif fmt == "html":
            text = formatters.to_html(result)  # type: ignore[arg-type]
        else:
            text = formatters.to_plain_text(result)  # type: ignore[arg-type]
        self._create_document_tab(Document(text=text), select=True)
        words = len((getattr(result, "full_text", "") or "").split())
        has_speakers = any(getattr(s, "speaker", "") for s in getattr(result, "segments", ()))
        extra = " with speaker labels" if has_speakers else ""
        self._announce(
            f"Transcription complete{extra}. {words} words. Review the draft transcript."
        )

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
            wildcard=_AUDIO_VIDEO_WILDCARD,
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
        self._set_status_quiet("Dictation listening")
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

        self._set_status_quiet("Transcribing dictation")
        self._announce("Transcribing dictation...")
        self._run_background_task("Transcribing dictation", _work, self._insert_dictation_result)

    def _insert_dictation_result(self, result: object) -> None:
        text = (getattr(result, "full_text", "") or "").strip()
        editor = getattr(self, "editor", None)
        if not text or editor is None:
            self._set_status_quiet("Dictation: no speech detected")
            self._announce("No speech detected.")
            return
        editor.WriteText(text + " ")
        self._play_speech_sound("transcription_word_inserted")
        words = len(text.split())
        self._set_status_quiet(f"Dictation inserted {words} words")
        self._announce(f"Inserted {words} words. Press Control+Z to undo.")

    @staticmethod
    def _play_speech_sound(event_id: str) -> None:
        """Play a dictation earcon (distinct from other sounds); never raises."""
        try:
            from quill.ui.sound_manager import post_sound

            post_sound(event_id)
        except Exception:  # noqa: BLE001 - a missing sound must not break dictation
            pass

    # -- offline voice commands (#663, push-to-talk) --------------------- #

    def voice_command_toggle(self) -> None:
        """Push-to-talk: speak one command and dispatch it (offline, allowlisted)."""
        from quill.core.speech.voice_commands import voice_commands_available

        if not voice_commands_available(
            self.settings, safe_mode_active=bool(getattr(self, "_safe_mode", False))
        ):
            self._announce(
                "Voice commands are off. Turn them on in Settings (they are disabled in Safe Mode)."
            )
            return
        recorder = getattr(self, "_voice_recorder", None)
        if recorder is not None and recorder.is_recording:
            self._stop_and_dispatch_voice_command(recorder)
            return
        # The "Voice conversation mode" setting promises that one Voice Command
        # becomes a hands-free conversation; honor it here instead of leaving
        # the setting with no effect (#793 review).
        if bool(getattr(self.settings, "voice_conversation_enabled", False)):
            self.voice_conversation_toggle()
            return
        self._start_voice_command()

    def _start_voice_command(self) -> None:
        from quill.core.speech.capture import MicRecorder, capture_available

        wx = self._wx
        if not capture_available():
            self._show_message_box(
                "Voice commands need microphone-capture support (the optional "
                "'sounddevice' package).",
                "Voice Commands",
                wx.ICON_INFORMATION | wx.OK,
            )
            return
        provider = self._voice_provider()
        if self._installed_or_prompt(provider, "Voice Commands") is None:
            return
        from quill.core.speech.service import load_input_device

        recorder = MicRecorder()
        try:
            recorder.start(load_input_device())
        except Exception as exc:  # noqa: BLE001 - surface a clean message
            self._set_status(f"Could not start voice commands: {exc}")
            return
        self._voice_recorder = recorder
        self._play_speech_sound("transcription_started")
        self._set_status_quiet("Listening for a command")
        self._announce("Listening for a command. Run the command again to stop and act.")

    def _stop_and_dispatch_voice_command(self, recorder: object) -> None:
        self._voice_recorder = None
        self._play_speech_sound("transcription_stopped")
        try:
            wav_path = recorder.stop()  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Voice command failed: {exc}")
            return
        provider = self._voice_provider()
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

        self._set_status("Recognizing command")
        self._run_background_task("Recognizing command", _work, self._dispatch_voice_result)

    def _dispatch_voice_result(self, result: object) -> None:
        from quill.core.ai.agent import SAFE_TOOL_IDS
        from quill.core.speech.voice_commands import resolve_transcript

        transcript = (getattr(result, "full_text", "") or "").strip()
        outcome = resolve_transcript(transcript, self.commands)
        if outcome.kind == "run" and outcome.command_id in SAFE_TOOL_IDS:
            self._announce(outcome.message)
            try:
                self.commands.run(outcome.command_id)
            except KeyError:
                self._set_status("That command is not available right now.")
        else:
            # cancel / no_match / a command that fell outside the safe allowlist.
            self._set_status(outcome.message)

    # -- conversation mode (#663, Hey QUILL Phase 2) --------------------- #

    def voice_conversation_toggle(self) -> None:
        """Start or stop the hands-free conversation loop (Phase 2).

        Conversation mode wraps the same on-device capture/transcribe/dispatch
        as push-to-talk in the :class:`ConversationController` state machine:
        warm audio cues for every state, a brief cancel window before a command
        runs, and a follow-up window so commands chain without re-arming.
        """
        from quill.core.speech.conversation import Timing
        from quill.core.speech.voice_commands import voice_commands_available

        controller = getattr(self, "_conversation", None)
        if controller is not None and controller.state.value != "off":
            self._conv_run(controller.stop())
            return
        if not voice_commands_available(
            self.settings, safe_mode_active=bool(getattr(self, "_safe_mode", False))
        ):
            self._announce(
                "Voice commands are off. Turn them on in Settings (they are disabled in Safe Mode)."
            )
            return
        from quill.core.speech.capture import capture_available

        if not capture_available():
            self._announce(
                "Conversation mode needs microphone-capture support (the optional "
                "'sounddevice' package)."
            )
            return
        if self._installed_or_prompt(self._voice_provider(), "Conversation Mode") is None:
            return
        from quill.core.speech.conversation import ConversationController

        controller = ConversationController(
            timing=Timing.from_settings(self.settings),
            user_name=str(getattr(self.settings, "voice_conversation_user_name", "") or ""),
            varied_prompts=True,
        )
        self._conversation = controller
        self._conv_timers: dict[str, object] = {}
        self._conv_run(controller.start())

    def _voice_spoken_cues_active(self) -> bool:
        """SR-parity: speak prompts aloud only when the user turned cues on and
        no screen reader is running (so QUILL never talks over the reader)."""
        if not bool(getattr(self.settings, "voice_conversation_spoken_cues", False)):
            return False
        try:
            from quill.platform.windows.sr_detect import detect_screen_reader

            if detect_screen_reader().detected:
                return False
        except Exception:  # noqa: BLE001
            # On Windows a failed detection could mean a reader IS running, so
            # stay quiet rather than talk over it (#795 review). Off Windows
            # there is no detector at all; honor the user's explicit opt-in.
            import sys as _sys

            if _sys.platform == "win32":
                return False
        return True

    def _voice_speak_cue(self, text: str) -> None:
        """Speak a short cue aloud via the read-aloud voice (best-effort).

        Runs on the task pool so it never blocks the UI; barge-in discipline is
        handled by capture only starting after the effect list is executed."""
        if not text or not self._voice_spoken_cues_active():
            return
        try:
            import threading

            voice = self._build_voice_services()
            if voice is None or not voice.output_available():
                return

            def _work(_progress):
                voice.play(text, stop_event=threading.Event(), pause_event=threading.Event())
                return None

            self._run_background_task("Speaking prompt", _work, lambda _r: None)
        except Exception:  # noqa: BLE001 - a cue must never break the loop
            pass

    def _conv_run(self, effects: list) -> None:
        """Execute a list of conversation :class:`Effect` objects in order."""
        wx = self._wx
        for effect in effects:
            kind = effect.kind
            if kind == "sound":
                self._play_speech_sound(effect.value)
            elif kind == "announce":
                self._set_status_quiet(effect.value)
                self._announce(effect.value)
                self._voice_speak_cue(effect.value)
            elif kind == "start_capture":
                self._conv_start_capture()
            elif kind == "stop_capture":
                self._conv_stop_capture(discard=True)
            elif kind == "dispatch":
                self._conv_dispatch(effect.value)
            elif kind == "start_timer":
                self._conv_cancel_timer(effect.value)
                self._conv_timers[effect.value] = wx.CallLater(
                    max(1, effect.delay_ms), self._conv_on_timer, effect.value
                )
            elif kind == "cancel_timer":
                self._conv_cancel_timer(effect.value)

    def _conv_cancel_timer(self, channel: str) -> None:
        timer = getattr(self, "_conv_timers", {}).pop(channel, None)
        if timer is not None:
            try:
                timer.Stop()
            except Exception:  # noqa: BLE001 - already fired/stopped
                pass

    def _conv_on_timer(self, channel: str) -> None:
        self._conv_timers.pop(channel, None)
        controller = getattr(self, "_conversation", None)
        if controller is None:
            return
        from quill.core.speech.conversation import (
            TIMER_FOLLOWUP,
            TIMER_REVIEW,
            TIMER_THINKING,
        )

        if channel == TIMER_REVIEW:
            self._conv_run(controller.on_review_timer())
        elif channel == TIMER_THINKING:
            self._conv_run(controller.on_thinking_timer())
        elif channel == TIMER_FOLLOWUP:
            self._conv_run(controller.on_followup_timer())

    def _conv_start_capture(self) -> None:
        """Open the mic for one conversation turn, ending it when you stop
        speaking (voice-activity detection) with a hard cap as a backstop."""
        from quill.core.speech.capture import CHANNELS, SAMPLE_RATE, MicRecorder
        from quill.core.speech.service import load_input_device
        from quill.core.speech.vad import SilenceDetector

        recorder = MicRecorder()
        try:
            recorder.start(load_input_device())
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Conversation mode could not open the microphone: {exc}")
            self._conv_run(self._conversation.stop())
            return
        self._conv_recorder = recorder
        silence_ms = int(getattr(self.settings, "voice_conversation_silence_ms", 2000))
        if silence_ms <= 0:
            # The setting documents 0 as "the engine default"; for this
            # timed-turn loop that is the standard 2 s pause window (#793).
            silence_ms = 2000
        self._conv_vad = SilenceDetector(sample_rate=SAMPLE_RATE * CHANNELS, silence_ms=silence_ms)
        self._conv_vad_seen = 0
        # Poll microphone energy; a turn ends when speech is followed by the
        # pause window. A hard cap stops a stuck-open mic even if VAD misses;
        # it must exceed the configured pause window (plus margin) or a long
        # window could never elapse before the cut-off (#795 review).
        self._conv_vad_timer = self._wx.CallLater(200, self._conv_poll_vad)
        cap_ms = max(15000, silence_ms + 5000)
        self._conv_capture_timer = self._wx.CallLater(cap_ms, self._conv_finish_capture)

    def _conv_poll_vad(self) -> None:
        recorder = getattr(self, "_conv_recorder", None)
        vad = getattr(self, "_conv_vad", None)
        if recorder is None or vad is None:
            return
        new, self._conv_vad_seen = recorder.frames_since(self._conv_vad_seen)
        if new and vad.feed(new):
            self._conv_finish_capture()
            return
        self._conv_vad_timer = self._wx.CallLater(200, self._conv_poll_vad)

    def _conv_stop_capture(self, *, discard: bool) -> object | None:
        for attr in ("_conv_capture_timer", "_conv_vad_timer"):
            timer = getattr(self, attr, None)
            if timer is not None:
                try:
                    timer.Stop()
                except Exception:  # noqa: BLE001
                    # A timer that is already dead (window destroyed mid-stop)
                    # is exactly what we want; cleanup must never raise.
                    pass
                setattr(self, attr, None)
        recorder = getattr(self, "_conv_recorder", None)
        self._conv_recorder = None
        if recorder is None:
            return None
        try:
            wav_path = recorder.stop()
        except Exception:  # noqa: BLE001
            return None
        if discard:
            try:
                wav_path.unlink(missing_ok=True)
            except OSError:
                pass
            return None
        return wav_path

    def _conv_finish_capture(self) -> None:
        """The turn window elapsed: transcribe and feed the controller."""
        self._conv_capture_timer = None
        wav_path = self._conv_stop_capture(discard=False)
        controller = getattr(self, "_conversation", None)
        if wav_path is None or controller is None:
            return
        provider = self._voice_provider()
        installed = provider.list_installed_models()  # type: ignore[attr-defined]
        if not installed:
            self._conv_run(controller.stop())
            return
        model_id = self._default_model_id(installed)
        from quill.core.speech.provider import TranscriptionRequest

        request = TranscriptionRequest(source_path=wav_path, model_id=model_id)

        def _work(progress):
            try:
                return provider.transcribe_file(  # type: ignore[attr-defined]
                    request, lambda f, m: progress(m, int(f * 100), 100)
                )
            finally:
                try:
                    wav_path.unlink(missing_ok=True)
                except OSError:
                    pass

        self._run_background_task("Recognizing command", _work, self._conv_on_transcript)

    def _conv_on_transcript(self, result: object) -> None:
        from quill.core.ai.agent import SAFE_TOOL_IDS
        from quill.core.speech.voice_commands import normalize, resolve_transcript

        controller = getattr(self, "_conversation", None)
        if controller is None:
            return
        transcript = (getattr(result, "full_text", "") or "").strip()
        outcome = resolve_transcript(transcript, self.commands)
        if outcome.kind == "cancel":
            # The docs promise a spoken "stop" turns conversation mode OFF;
            # the other cancel phrases only abort this turn and re-arm (#793).
            if normalize(transcript) == "stop":
                self._conv_run(controller.stop())
                return
            self._conv_run(controller.on_cancel())
        elif outcome.kind == "run" and outcome.command_id in SAFE_TOOL_IDS:
            self._conv_run(controller.on_transcript(outcome.command_id, outcome.message))
        elif self._voice_route_to_ask_quill(transcript):
            # A question, not a command: handed to Ask Quill. Turn conversation
            # mode off so the mic is free for the chat's own voice controls.
            self._conv_run(controller.stop())
        else:
            self._conv_run(controller.on_transcript(None, outcome.message))

    def _voice_route_to_ask_quill(self, transcript: str) -> bool:
        """Phase 4: if ``transcript`` sounds like a question, open Ask Quill with
        it pre-filled and return True. AI consent and sending stay with the
        user in the chat; voice never fires a request on its own."""
        from quill.core.speech.voice_routing import QUESTION, classify, question_text

        if classify(transcript) != QUESTION:
            return False
        opener = getattr(self, "open_ask_quill_conversation", None)
        if opener is None:
            return False
        self._announce("Opening Ask Quill with your question.")
        opener(initial_prompt=question_text(transcript))
        return True

    def _conv_dispatch(self, command_id: str) -> None:
        controller = getattr(self, "_conversation", None)
        try:
            self.commands.run(command_id)
        except KeyError:
            self._set_status("That command is not available right now.")
        if controller is not None:
            self._conv_run(controller.on_action_done())

    def speak_voice_status(self) -> None:
        """Say what voice is doing right now (ADP mic-live perceivability)."""
        parts: list[str] = []
        wake = getattr(self, "_wake", None)
        if wake is not None and wake.state != "off":
            parts.append(wake.status_text())
        conversation = getattr(self, "_conversation", None)
        if conversation is not None and conversation.state.value != "off":
            parts.append(conversation.status_text())
        recorder = getattr(self, "_voice_recorder", None)
        if recorder is not None and getattr(recorder, "is_recording", False):
            parts.append("Listening for a command")
        message = "; ".join(parts) if parts else "Voice is not listening right now."
        self._announce(message)
        self._set_status(message)

    # -- wake word "Hey QUILL" (#663, Hey QUILL Phase 3) ----------------- #

    def voice_wakeword_toggle(self) -> None:
        """Start or stop always-listening for the phrase "Hey QUILL".

        The microphone stays open in short windows; each is transcribed
        on-device and checked for the wake phrase. On a wake, an inline command
        ("Hey QUILL, save file") runs straight away, while a bare "Hey QUILL"
        opens one command turn. Off by default and always off in Safe Mode; the
        status stays visible and a periodic reminder keeps the live mic
        perceivable.
        """
        from quill.core.speech.voice_commands import voice_commands_available

        wake = getattr(self, "_wake", None)
        if wake is not None and wake.state != "off":
            self._wake_run(wake.stop())
            return
        if not voice_commands_available(
            self.settings, safe_mode_active=bool(getattr(self, "_safe_mode", False))
        ):
            self._announce(
                "Voice commands are off. Turn them on in Settings (they are disabled in Safe Mode)."
            )
            return
        from quill.core.speech.capture import capture_available

        if not capture_available():
            self._announce(
                "Listening for Hey QUILL needs microphone-capture support (the optional "
                "'sounddevice' package)."
            )
            return
        if self._installed_or_prompt(self._voice_provider(), "Hey QUILL") is None:
            return
        from quill.core.speech.wakeword import WakeController

        self._wake = WakeController()
        self._wake_run(self._wake.start())

    def _wake_run(self, effects: list) -> None:
        for effect in effects:
            kind = effect.kind
            if kind == "sound":
                self._play_speech_sound(effect.value)
            elif kind == "announce":
                self._set_status_quiet(effect.value)
                self._announce(effect.value)
            elif kind == "reminder":
                from quill.core.speech.conversation import CUE_IDLE

                self._play_speech_sound(CUE_IDLE)
                self._set_status_quiet('Still listening for "Hey QUILL"')
            elif kind == "listen_again":
                self._wake_capture_window()
            elif kind == "stop_listen":
                self._wake_stop_capture()
            elif kind == "arm":
                self._wake_capture_command()
            elif kind == "dispatch":
                self._wake_dispatch_inline(effect.value)

    def _wake_stop_capture(self) -> None:
        timer = getattr(self, "_wake_timer", None)
        if timer is not None:
            try:
                timer.Stop()
            except Exception:  # noqa: BLE001
                pass
            self._wake_timer = None
        recorder = getattr(self, "_wake_recorder", None)
        self._wake_recorder = None
        if recorder is not None:
            try:
                recorder.stop().unlink(missing_ok=True)
            except Exception:  # noqa: BLE001
                pass

    def _wake_capture_window(self, *, for_command: bool = False) -> None:
        """Record one short window, then transcribe and route it."""
        wake = getattr(self, "_wake", None)
        if wake is None or wake.state == "off":
            return
        from quill.core.speech.capture import MicRecorder
        from quill.core.speech.service import load_input_device

        recorder = MicRecorder()
        try:
            recorder.start(load_input_device())
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Hey QUILL listening stopped: {exc}")
            self._wake_run(wake.stop())
            return
        self._wake_recorder = recorder
        # A short window keeps latency low; command windows are a bit longer.
        window_ms = 4000 if for_command else 2500
        callback = self._wake_finish_command if for_command else self._wake_finish_window
        self._wake_timer = self._wx.CallLater(window_ms, callback)

    def _wake_capture_command(self) -> None:
        self._set_status_quiet("Listening for your command")
        self._wake_capture_window(for_command=True)

    def _wake_transcribe(self, on_text) -> None:
        """Stop the current window and transcribe it, calling on_text(str)."""
        timer = getattr(self, "_wake_timer", None)
        if timer is not None:
            try:
                timer.Stop()
            except Exception:  # noqa: BLE001
                pass
            self._wake_timer = None
        recorder = getattr(self, "_wake_recorder", None)
        self._wake_recorder = None
        if recorder is None:
            return
        try:
            wav_path = recorder.stop()
        except Exception:  # noqa: BLE001
            on_text("")
            return
        provider = self._voice_provider()
        installed = provider.list_installed_models()  # type: ignore[attr-defined]
        if not installed:
            # No model: nothing will consume the recording, so delete it now
            # instead of leaking a temp WAV per toggle (#794 review).
            try:
                wav_path.unlink(missing_ok=True)
            except OSError:
                pass
            self._wake_run(self._wake.stop())
            return
        model_id = self._default_model_id(installed)
        from quill.core.speech.provider import TranscriptionRequest

        request = TranscriptionRequest(source_path=wav_path, model_id=model_id)

        def _work(progress):
            try:
                result = provider.transcribe_file(  # type: ignore[attr-defined]
                    request, lambda f, m: progress(m, int(f * 100), 100)
                )
                return (getattr(result, "full_text", "") or "").strip()
            finally:
                try:
                    wav_path.unlink(missing_ok=True)
                except OSError:
                    pass

        self._run_background_task("Listening", _work, on_text)

    def _wake_finish_window(self) -> None:
        self._wake_transcribe(self._wake_on_window)

    def _wake_on_window(self, transcript: str) -> None:
        wake = getattr(self, "_wake", None)
        if wake is not None:
            self._wake_run(wake.on_window(transcript or ""))

    def _wake_finish_command(self) -> None:
        self._wake_transcribe(self._wake_on_command)

    def _wake_on_command(self, transcript: str) -> None:
        self._wake_dispatch_inline(transcript)

    def _wake_dispatch_inline(self, body: str) -> None:
        """Resolve a spoken command body against the safe allowlist, run it,
        then resume listening for the wake phrase."""
        from quill.core.ai.agent import SAFE_TOOL_IDS
        from quill.core.speech.conversation import CUE_ERROR, CUE_READY
        from quill.core.speech.voice_commands import normalize, resolve_transcript

        wake = getattr(self, "_wake", None)
        outcome = resolve_transcript(body, self.commands)
        if outcome.kind == "run" and outcome.command_id in SAFE_TOOL_IDS:
            self._announce(outcome.message)
            try:
                self.commands.run(outcome.command_id)
                self._play_speech_sound(CUE_READY)
            except KeyError:
                self._set_status("That command is not available right now.")
        elif outcome.kind == "cancel":
            # The docs promise "Hey QUILL, stop" turns always-listening OFF;
            # other cancel phrases just drop this utterance (#794 review).
            if normalize(body) == "stop" and wake is not None:
                self._wake_run(wake.stop())
                return
            self._set_status_quiet("Cancelled.")
        elif self._voice_route_to_ask_quill(body):
            # A question: handed to Ask Quill. Stop always-listening so the mic
            # is free for the chat, and do not resume automatically.
            if wake is not None:
                self._wake_run(wake.stop())
            return
        else:
            self._play_speech_sound(CUE_ERROR)
            self._set_status(outcome.message)
        if wake is not None and wake.state != "off":
            self._wake_run(wake.resume_listening())

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
            ("tools.speech_ffmpeg", "Download FFmpeg", self.download_ffmpeg),
            ("tools.speech_hf_token", "Hugging Face Token", self.set_huggingface_token),
        ]
        for command_id, title, handler in specs:
            self.commands.try_register(
                command_id,
                title,
                handler,
                self._binding_for(command_id),
                feature_id="core.dictation",
            )
