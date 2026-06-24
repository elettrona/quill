"""Hold-to-Dictate and Locked Dictation hotkeys (F9 / Ctrl+F9).

Wires the wx-free :class:`~quill.core.speech.dictation.DictationController` to the
live editor: it builds the insertion context from the caret, drives microphone
capture (:class:`~quill.core.speech.capture.MicRecorder`), runs Whisper on a
worker thread, secures audio to the recovery repository before transcribing, and
inserts the transcript as one undoable edit. Key activation is matched against
the *configured* keymap bindings (so every shortcut is remappable) in the
editor's key-down/up handlers rather than the accelerator table, because
Hold-to-Dictate needs a real key-up that accelerators never deliver.

Default shortcuts (all remappable in Keyboard settings):

* ``tools.dictation_hold``           F9              hold to record, release to insert
* ``tools.dictation_lock_toggle``    Ctrl+F9         start / finish Locked Dictation
* ``tools.dictation_pause``          Ctrl+Shift+F9   pause / resume Locked Dictation
* ``tools.dictation_status``         Alt+F9          speak the current state
* ``tools.dictation_emergency_stop`` Escape          stop now, keep the speech
* ``tools.dictation_cancel``         Shift+Escape    stop and discard

Escape / Shift+Escape are only consumed while a dictation session is active, so
they behave normally the rest of the time.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

_DICTATION_COMMANDS: tuple[tuple[str, str], ...] = (
    ("tools.dictation_hold", "Hold-to-Dictate"),
    ("tools.dictation_lock_toggle", "Locked Dictation (start/finish)"),
    ("tools.dictation_pause", "Pause or Resume Dictation"),
    ("tools.dictation_status", "Dictation Status"),
    ("tools.dictation_emergency_stop", "Stop Dictation (keep speech)"),
    ("tools.dictation_cancel", "Cancel Dictation (discard)"),
)


class _LiveDictationServices:
    """``DictationServices`` implementation backed by the MainFrame mixin."""

    def __init__(self, frame: DictationHotkeysMixin) -> None:
        self._frame = frame
        self._recorder: Any = None
        self._repo: Any = None

    def _repository(self) -> Any:
        if self._repo is None:
            from quill.core.speech.dictation import DictationRecoveryRepository

            self._repo = DictationRecoveryRepository()
        return self._repo

    def start_capture(self, session: Any) -> None:
        from quill.core.speech.capture import MicRecorder
        from quill.core.speech.service import load_input_device

        recorder = MicRecorder()
        recorder.start(load_input_device())  # raises on failure -> MIC_UNAVAILABLE
        self._recorder = recorder

    def stop_capture(self, session: Any) -> Path | None:
        recorder = self._recorder
        self._recorder = None
        if recorder is None:
            return None
        try:
            return recorder.stop()
        except Exception:  # noqa: BLE001 - capture cleanup must not raise over the result
            return None

    def pause_capture(self, session: Any) -> None:
        if self._recorder is not None:
            self._recorder.pause()

    def resume_capture(self, session: Any) -> None:
        if self._recorder is not None:
            self._recorder.resume()

    def discard_capture(self, session: Any) -> None:
        recorder = self._recorder
        self._recorder = None
        if recorder is None:
            return
        try:
            path = recorder.stop()
            Path(path).unlink(missing_ok=True)
        except Exception:  # noqa: BLE001 - discarding must never raise
            pass

    def save_audio(self, session: Any, wav_path: Path) -> None:
        try:
            self._repository().save_audio(session, wav_path)
        except Exception:  # noqa: BLE001 - recovery write must not wedge the machine
            pass

    def transcribe(self, session: Any) -> None:
        frame = self._frame
        controller = frame._live_dictation
        provider = frame._speech_provider()
        installed = provider.list_installed_models()  # type: ignore[attr-defined]
        if not installed:
            controller.transcription_failed(session.session_id, "No speech model installed.")
            return
        model_id = frame._default_model_id(installed)
        audio_path = Path(session.audio_path) if session.audio_path else None
        session_id = session.session_id

        from quill.core.speech.provider import TranscriptionRequest

        request = TranscriptionRequest(source_path=audio_path, model_id=model_id)

        def _work(progress: Any) -> Any:
            try:
                result = provider.transcribe_file(  # type: ignore[attr-defined]
                    request, lambda f, m: progress(m, int(f * 100), 100)
                )
                return ("ok", (getattr(result, "full_text", "") or "").strip())
            except Exception as exc:  # noqa: BLE001 - report failure to the controller
                return ("error", str(exc))

        def _done(payload: Any) -> None:
            kind, value = payload
            if kind == "ok":
                controller.transcription_succeeded(session_id, value)
            else:
                controller.transcription_failed(session_id, value)

        frame._run_background_task("Transcribing dictation", _work, _done)

    def insert(self, session: Any, text: str) -> bool:
        frame = self._frame
        editor = getattr(frame, "editor", None)
        if editor is None or frame._document_is_read_only():
            return False  # defer to recovery/review
        full = editor.GetValue()
        ctx = session.context
        start, end = ctx.selection_start, ctx.selection_end
        if not (0 <= start <= end <= len(full)):
            caret = editor.GetInsertionPoint()
            start = end = caret
        frame._atomic_replace(start, end, text)
        frame.document.set_text(editor.GetValue())
        return True

    def feedback(self, event: Any, session: Any) -> None:
        self._frame._dictation_feedback(event, session)

    def now(self) -> float:
        return time.time()


class DictationHotkeysMixin:
    """F9 Hold-to-Dictate and Ctrl+F9 Locked Dictation, fully remappable."""

    # Relies on MainFrame helpers: _wx, frame, editor, document, settings,
    # commands, _binding_for, _parse_keybinding, _announce, _set_status,
    # _atomic_replace, _document_is_read_only, _effective_markup_kind,
    # _run_background_task, _speech_provider, _default_model_id,
    # _play_speech_sound.

    _live_dictation: Any = None
    _dictation_services: Any = None
    _dictation_timer: Any = None

    # -- lifecycle --------------------------------------------------------- #

    def _ensure_dictation_controller(self) -> Any:
        if self._live_dictation is None:
            from quill.core.speech.dictation import DictationController
            from quill.core.speech.dictation.controller import DictationConfig

            self._dictation_services = _LiveDictationServices(self)
            self._live_dictation = DictationController(self._dictation_services, DictationConfig())
        return self._live_dictation

    def _register_dictation_hotkey_commands(self) -> None:
        handlers = {
            "tools.dictation_hold": self.start_hold_dictation,
            "tools.dictation_lock_toggle": self.toggle_locked_dictation,
            "tools.dictation_pause": self.toggle_dictation_pause,
            "tools.dictation_status": self.speak_dictation_status,
            "tools.dictation_emergency_stop": self.stop_dictation_keep_speech,
            "tools.dictation_cancel": self.cancel_dictation_discard,
        }
        for command_id, title in _DICTATION_COMMANDS:
            self.commands.try_register(
                command_id,
                title,
                handlers[command_id],
                self._binding_for(command_id),
                feature_id="core.dictation",
            )

    # -- command handlers (also callable from the command palette) --------- #

    def start_hold_dictation(self) -> None:
        if not self._dictation_preflight():
            return
        self._ensure_dictation_controller().start_hold(self._dictation_context())
        self._start_dictation_watchdog()

    def release_hold_dictation(self) -> None:
        if self._live_dictation is not None:
            self._live_dictation.release_hold()

    def toggle_locked_dictation(self) -> None:
        controller = self._ensure_dictation_controller()
        if not controller.is_busy and not self._dictation_preflight():
            return
        controller.toggle_locked(self._dictation_context())
        self._start_dictation_watchdog()

    def toggle_dictation_pause(self) -> None:
        if self._live_dictation is not None:
            self._live_dictation.toggle_pause()

    def stop_dictation_keep_speech(self) -> None:
        if self._live_dictation is not None:
            self._live_dictation.emergency_stop()

    def cancel_dictation_discard(self) -> None:
        if self._live_dictation is not None:
            self._live_dictation.cancel_and_discard()

    def speak_dictation_status(self) -> None:
        from quill.core.speech.dictation import DictationState

        controller = self._live_dictation
        state = controller.state if controller is not None else DictationState.IDLE
        self._announce(_DICTATION_STATUS_TEXT.get(state, "Dictation is off."), force=True)

    # -- preflight + context ---------------------------------------------- #

    def _dictation_preflight(self) -> bool:
        """Confirm capture support and an installed model before recording."""
        from quill.core.speech.capture import capture_available

        if getattr(self, "_safe_mode", False):
            self._announce("Dictation is disabled in Safe Mode.", force=True)
            return False
        if not capture_available():
            self._announce(
                "Dictation needs microphone support (the optional sounddevice package).",
                force=True,
            )
            return False
        provider = self._speech_provider()
        try:
            if not provider.list_installed_models():  # type: ignore[attr-defined]
                self._announce(
                    "No speech model is installed. Open Tools, Speech, Whisperer, "
                    "Manage Speech Models.",
                    force=True,
                )
                return False
        except Exception:  # noqa: BLE001 - a provider probe must not block the editor
            return False
        return True

    def _dictation_context(self) -> Any:
        from quill.core.speech.dictation import InsertionContext

        editor = self.editor
        text = editor.GetValue()
        start, end = editor.GetSelection()
        caret = editor.GetInsertionPoint()
        return InsertionContext(
            document_id=str(id(self.document)),
            document_path=str(self.document.path) if self.document.path else None,
            caret=caret,
            selection_start=start,
            selection_end=end,
            prefix_char=text[caret - 1] if caret > 0 else "",
            suffix_char=text[caret] if caret < len(text) else "",
            read_only=self._document_is_read_only(),
            content_mode=self._effective_markup_kind(),
        )

    # -- key routing (called from the editor key handlers) ----------------- #

    def _dictation_match(
        self, event: Any, binding: str | None, *, ignore_mods: bool = False
    ) -> bool:
        # Key routing for this optional feature must never break normal typing:
        # any failure resolving the binding (e.g. a minimal wx during tests, or a
        # malformed chord) means "no match" so the editor's own handling proceeds.
        try:
            parsed = self._parse_keybinding(binding)
            if parsed is None:
                return False
            flags, key_code = parsed
            if event.GetKeyCode() != key_code:
                return False
            if ignore_mods:
                return True
            wx = self._wx
            return (
                event.ControlDown() == bool(flags & wx.ACCEL_CTRL)
                and event.ShiftDown() == bool(flags & wx.ACCEL_SHIFT)
                and event.AltDown() == bool(flags & wx.ACCEL_ALT)
            )
        except Exception:  # noqa: BLE001 - never let dictation routing break a keystroke
            return False

    def _dictation_handle_key_down(self, event: Any) -> bool:
        """Return True if the key began/affected a dictation session (consumed)."""
        active = self._live_dictation is not None and self._live_dictation.is_busy
        # Escape / Shift+Escape only when a session is active, so normal Escape works.
        if active and self._dictation_match(event, self._binding_for("tools.dictation_cancel")):
            self.cancel_dictation_discard()
            return True
        if active and self._dictation_match(
            event, self._binding_for("tools.dictation_emergency_stop")
        ):
            self.stop_dictation_keep_speech()
            return True
        if self._dictation_match(event, self._binding_for("tools.dictation_lock_toggle")):
            self.toggle_locked_dictation()
            return True
        if self._dictation_match(event, self._binding_for("tools.dictation_pause")):
            self.toggle_dictation_pause()
            return True
        if self._dictation_match(event, self._binding_for("tools.dictation_status")):
            self.speak_dictation_status()
            return True
        if self._dictation_match(event, self._binding_for("tools.dictation_hold")):
            self.start_hold_dictation()
            return True
        return False

    def _dictation_handle_key_up(self, event: Any) -> bool:
        if self._live_dictation is None:
            return False
        # Match the hold key by its main key code, ignoring modifiers (they are
        # often already released by the time the key-up arrives).
        if self._dictation_match(
            event, self._binding_for("tools.dictation_hold"), ignore_mods=True
        ):
            self.release_hold_dictation()
            return True
        return False

    # -- watchdog timer (max duration, missing key-up, focus loss) --------- #

    def _start_dictation_watchdog(self) -> None:
        wx = self._wx
        if self._dictation_timer is None:
            self._dictation_timer = wx.Timer(self.frame)
            self.frame.Bind(wx.EVT_TIMER, self._on_dictation_tick, self._dictation_timer)
        if not self._dictation_timer.IsRunning():
            self._dictation_timer.Start(500)

    def _on_dictation_tick(self, _event: Any) -> None:
        controller = self._live_dictation
        if controller is None or not controller.is_busy:
            if self._dictation_timer is not None and self._dictation_timer.IsRunning():
                self._dictation_timer.Stop()
            return
        controller.tick()  # max-duration enforcement
        # Focus-loss policy: stop and preserve if QUILL is no longer foreground.
        try:
            if controller.is_recording and not self.frame.IsActive():
                controller.on_focus_lost()
        except Exception:  # noqa: BLE001 - foreground probe is best-effort
            pass
        # Missing key-up recovery: if the physical hold key is no longer down.
        from quill.core.speech.dictation import DictationState

        if controller.state is DictationState.HOLD_RECORDING:
            parsed = self._parse_keybinding(self._binding_for("tools.dictation_hold"))
            if parsed is not None:
                try:
                    if not self._wx.GetKeyState(parsed[1]):
                        controller.on_missing_keyup()
                except Exception:  # noqa: BLE001 - key-state probe is best-effort
                    pass

    # -- feedback (earcons + announcements) -------------------------------- #

    def _dictation_feedback(self, event: Any, session: Any) -> None:
        from quill.core.speech.dictation.controller import FeedbackEvent

        earcon, message, status = _DICTATION_FEEDBACK.get(event, ("", "", ""))
        if event is FeedbackEvent.INSERTED and session is not None:
            words = len((session.transcript or "").split())
            message = f"Dictation inserted, {words} words. Press Control Z to undo."
            status = f"Dictation inserted, {words} words"
        if earcon:
            self._play_speech_sound(earcon)
        if status:
            self._set_status(status)
        if message:
            self._announce(message, force=True)


# State -> Alt+F9 status announcement (PRD §18.4).
def _build_status_text() -> dict:
    from quill.core.speech.dictation import DictationState

    return {
        DictationState.IDLE: "Dictation is off.",
        DictationState.HOLD_RECORDING: "Hold-to-dictate is recording.",
        DictationState.LOCKED_RECORDING: "Locked dictation is recording.",
        DictationState.PAUSED: "Dictation is paused.",
        DictationState.TRANSCRIBING: "Dictation is being transcribed.",
        DictationState.REVIEW_REQUIRED: "A transcript is waiting for review.",
    }


def _build_feedback() -> dict:
    from quill.core.speech.dictation.controller import FeedbackEvent

    return {
        FeedbackEvent.HOLD_START: ("transcription_started", "", "Dictating; release to insert"),
        FeedbackEvent.LOCKED_START: (
            "transcription_started",
            "Locked dictation on. Press the lock key again to finish. Escape stops.",
            "Locked dictation - press the lock key to finish; Escape to stop",
        ),
        FeedbackEvent.HOLD_STOP: ("transcription_stopped", "", ""),
        FeedbackEvent.LOCKED_STOP: ("transcription_stopped", "", ""),
        FeedbackEvent.PAUSED: ("", "Dictation paused.", "Locked dictation paused"),
        FeedbackEvent.RESUMED: ("transcription_started", "Dictation resumed.", ""),
        FeedbackEvent.TRANSCRIBING: ("", "Transcribing dictation.", "Transcribing dictation"),
        FeedbackEvent.INSERTED: ("transcription_word_inserted", "Dictation inserted.", ""),
        FeedbackEvent.NO_SPEECH: ("", "No speech was recognized.", "No speech recognized"),
        FeedbackEvent.REVIEW: (
            "",
            "Dictation saved for review; it could not be inserted here.",
            "Dictation saved for review",
        ),
        FeedbackEvent.CANCELLED: ("", "Dictation cancelled.", "Dictation cancelled"),
        FeedbackEvent.MAX_TIME: (
            "transcription_stopped",
            "Maximum dictation time reached. Recording stopped and is being transcribed.",
            "",
        ),
        FeedbackEvent.FOCUS_LOST: (
            "transcription_stopped",
            "Dictation stopped because QUILL lost focus.",
            "",
        ),
        FeedbackEvent.MISSING_KEYUP: ("", "", "Dictation stopped"),
        FeedbackEvent.MIC_UNAVAILABLE: (
            "",
            "The microphone could not be opened. Check your input device and "
            "Windows microphone permissions.",
            "Microphone unavailable",
        ),
        FeedbackEvent.BUSY: ("", "The previous dictation is still being transcribed.", ""),
        FeedbackEvent.ERROR: ("", "Dictation failed; the recording was kept for recovery.", ""),
    }


_DICTATION_STATUS_TEXT = _build_status_text()
_DICTATION_FEEDBACK = _build_feedback()
