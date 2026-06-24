from __future__ import annotations

import logging
import queue as _queue
import sys
import threading
import time as _time
from dataclasses import dataclass, replace
from importlib import import_module
from typing import Any

logger = logging.getLogger(__name__)


def _sapi_available() -> bool:
    """True when Windows SAPI 5 speech can be reached (the self-voicing fallback)."""
    try:
        from quill.platform.windows import sapi5

        return sapi5.available()
    except Exception:  # noqa: BLE001
        return False


_VALID_BACKENDS = {"auto", "prism", "status_only"}

_sr_active_cache: bool | None = None
_sr_cache_timestamp: float = 0.0
_SR_CACHE_TTL = 30.0


def _screen_reader_active() -> bool:
    """Cached check for a running screen reader (so 'auto' TTS doesn't double-talk).

    Re-probes after _SR_CACHE_TTL seconds so that starting a screen reader while
    QUILL is running stops self-voicing within the next announcement cycle.
    """
    global _sr_active_cache, _sr_cache_timestamp
    now = _time.monotonic()
    if _sr_active_cache is None or (now - _sr_cache_timestamp) > _SR_CACHE_TTL:
        try:
            from quill.platform.windows.sr_detect import detect_screen_reader

            _sr_active_cache = bool(detect_screen_reader().detected)
        except Exception:  # noqa: BLE001
            _sr_active_cache = False
        _sr_cache_timestamp = now
    return _sr_active_cache


def normalize_backend_name(value: str | None) -> str:
    raw = (value or "").strip().lower()
    if raw in _VALID_BACKENDS:
        return raw
    return "auto"


# SAPI/COM voice construction is expensive on the first call (hundreds of ms
# for voice enumeration), so the self-voicing engine is a process-wide singleton
# built once on the TTS worker thread and reused for every announcement. A SAPI
# SpVoice is an apartment-threaded COM object: it must be created and spoken to
# on the same thread, which is why it lives on the worker thread instead of
# being shared across callers.
_tts_voice: Any | None = None
_tts_engine_failed: bool = False

# TTS-FALLBACK-ANNOUNCE: callers can check this after startup.
# True means SAPI 5 could not be initialised and the screen-reader fallback is active.
_tts_init_failed: bool = False


def tts_init_failed() -> bool:
    """Return True when SAPI 5 failed to initialise for self-voicing.

    The UI uses this to show a one-shot status-bar prompt:
    "Screen reader fallback active. Press F8 to retry TTS."
    """
    return _tts_init_failed


def _build_tts_voice() -> Any | None:
    """Create the SAPI ``SpVoice`` on the calling (worker) thread, or None.

    A failure flips self-voicing off until :func:`retry_tts_init` clears it.
    """
    global _tts_engine_failed, _tts_init_failed
    if _tts_engine_failed:
        return None
    try:
        from quill.platform.windows import sapi5

        if not sapi5.available():
            raise RuntimeError("SAPI 5 is not available")
        return sapi5.create_voice()
    except Exception:  # noqa: BLE001 - any failure flips us off until retried
        _tts_engine_failed = True
        _tts_init_failed = True
        return None


def retry_tts_init() -> bool:
    """Clear the failure flag so the worker rebuilds the SAPI voice on next use.

    Returns True when SAPI 5 looks usable again. Called from the UI when the user
    presses the F8 retry shortcut shown by the TTS-FALLBACK-ANNOUNCE prompt.
    """
    global _tts_voice, _tts_engine_failed, _tts_init_failed
    _tts_voice = None
    _tts_engine_failed = False
    _tts_init_failed = False
    if not _sapi_available():
        _tts_init_failed = True
        return False
    _ensure_tts_worker()
    return True


def reset_tts_engine_for_tests() -> None:
    """Discard the cached voice and SR cache. Test-only helper."""
    global _tts_voice, _tts_engine_failed, _tts_init_failed
    global _sr_active_cache, _sr_cache_timestamp
    _tts_voice = None
    _tts_engine_failed = False
    _tts_init_failed = False
    _sr_active_cache = None
    _sr_cache_timestamp = 0.0


def flush_tts_for_tests(timeout: float = 2.0) -> None:
    """Block until the TTS worker has processed all queued messages. Test-only."""
    _tts_queue.join()


# ------------------------------------------------------------------
# Non-blocking TTS worker (fix #52: speech must not block the UI thread)
# ------------------------------------------------------------------

_tts_queue: _queue.Queue[str | None] = _queue.Queue()
_tts_worker_started = False
_tts_worker_lock = threading.Lock()


def _ensure_tts_worker() -> None:
    global _tts_worker_started
    with _tts_worker_lock:
        if _tts_worker_started:
            return
        _tts_worker_started = True
        t = threading.Thread(target=_tts_worker_loop, daemon=True, name="quill-tts-worker")
        t.start()


def prewarm_tts_engine() -> None:
    """Start the TTS worker thread now so SAPI init cost is paid ahead of time.

    SAPI/COM voice construction is the expensive part of the first announcement
    of the session (hundreds of ms). Doing it at startup keeps that cost out of
    the quill_key_timeout window where it could otherwise expire the key prefix
    before the user's next keystroke arrived. The SpVoice is an apartment COM
    object, so it is built on the worker thread that later speaks with it.
    """
    if not _sapi_available():
        return
    _ensure_tts_worker()


def _tts_worker_loop() -> None:
    global _tts_voice
    _tts_voice = _build_tts_voice()
    while True:
        msg = _tts_queue.get()
        if msg is None:
            _tts_queue.task_done()
            break
        if _tts_voice is None:
            _tts_voice = _build_tts_voice()
        voice = _tts_voice
        if voice is not None:
            try:
                # Synchronous Speak on this dedicated worker thread; the queue
                # already keeps announcements off the UI thread.
                voice.Speak(msg, 0)
            except Exception:  # noqa: BLE001
                pass
        _tts_queue.task_done()


@dataclass(frozen=True, slots=True)
class AnnouncementBackendState:
    requested_backend: str
    active_backend: str
    prism_available: bool
    prism_runtime_ready: bool
    backend_name: str
    last_error: str = ""


class AnnouncementEngine:
    def __init__(self, requested_backend: str = "auto") -> None:
        self._runtime_backend: Any | None = None
        self._state = AnnouncementBackendState(
            requested_backend="auto",
            active_backend="status_only",
            prism_available=False,
            prism_runtime_ready=False,
            backend_name="Status Bar",
            last_error="",
        )
        self.configure(requested_backend)

    def configure(self, requested_backend: str) -> AnnouncementBackendState:
        requested = normalize_backend_name(requested_backend)
        backend, probe = _probe_prism_backend()
        prism_available = probe != "missing"
        prism_runtime_ready = backend is not None
        active_backend = "status_only"
        backend_name = "Status Bar"
        last_error = ""

        if requested == "prism":
            if backend is not None:
                active_backend = "prism"
                backend_name = _backend_name(backend)
            else:
                last_error = _probe_to_message(probe)
        elif requested == "auto":
            if backend is not None:
                active_backend = "prism"
                backend_name = _backend_name(backend)
            else:
                backend_name = "Status Bar"
                if probe not in {"missing", "runtime_unavailable"}:
                    last_error = _probe_to_message(probe)

        self._runtime_backend = backend if active_backend == "prism" else None
        self._state = AnnouncementBackendState(
            requested_backend=requested,
            active_backend=active_backend,
            prism_available=prism_available,
            prism_runtime_ready=prism_runtime_ready,
            backend_name=backend_name,
            last_error=last_error,
        )
        return self._state

    def state(self) -> AnnouncementBackendState:
        return self._state

    def announce(self, message: str, *, force_speech: bool = False) -> str | None:
        if self._runtime_backend is None:
            # macOS: hand the announcement to VoiceOver via the accessibility
            # API. Never self-voice with SAPI — that talks over VoiceOver
            # (the system voice the user already hears). If VoiceOver is off the
            # post is a harmless no-op.
            if sys.platform == "darwin":
                try:
                    from quill.platform.macos.announce import announce as voiceover_announce

                    voiceover_announce(message)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("macOS VoiceOver announce failed: %s", exc)
                return None
            # Windows/Linux: only speak via system TTS when NO screen reader is
            # running — otherwise it talks over Narrator/NVDA/JAWS (the screen
            # reader already reads the UI through the accessibility API).
            # force_speech bypasses that suppression for callers narrating
            # internal-only state (e.g. the QUILL key chord prefix) that has
            # no focus or control change for the screen reader to pick up on
            # its own, so without this the message is silently dropped.
            if (
                self._state.requested_backend == "auto"
                and not _tts_engine_failed
                and (force_speech or not _screen_reader_active())
            ):
                # Queue speech to the worker thread without resolving the voice
                # here: building the SAPI SpVoice costs hundreds of ms the first
                # time and the worker builds the singleton itself, so resolving
                # it on the caller (the UI thread) would block for that long on
                # the first announcement of the session.
                _ensure_tts_worker()
                _tts_queue.put_nowait(message)
                self._state = replace(
                    self._state,
                    active_backend="speech",
                    backend_name="System Speech",
                    last_error="",
                )
            return None
        speak = getattr(self._runtime_backend, "speak", None)
        if not callable(speak):
            error = "Active Prism backend does not expose speak()."
            self._state = replace(self._state, last_error=error)
            return error
        try:
            speak(message, interrupt=False)
            return None
        except TypeError:
            speak(message)
            return None
        except Exception as exc:  # noqa: BLE001
            error = f"Prism announcement failed: {exc}"
            self._state = replace(self._state, last_error=error)
            return error

    def diagnostics_environment(self) -> dict[str, object]:
        return {
            "announcement_backend_requested": self._state.requested_backend,
            "announcement_backend_active": self._state.active_backend,
            "announcement_backend_name": self._state.backend_name,
            "announcement_prism_available": self._state.prism_available,
            "announcement_prism_runtime_ready": self._state.prism_runtime_ready,
            "announcement_backend_error": self._state.last_error,
        }


def _probe_prism_backend() -> tuple[Any | None, str]:
    prism_module = _import_prism_module()
    if prism_module is None:
        return None, "missing"
    try:
        context = prism_module.Context()
    except Exception:  # noqa: BLE001
        return None, "context_error"
    try:
        backend = context.acquire_best()
    except Exception:  # noqa: BLE001
        return None, "acquire_error"
    features = getattr(backend, "features", None)
    runtime_flag = getattr(features, "is_supported_at_runtime", True)
    if not runtime_flag:
        return None, "runtime_unavailable"
    return backend, "ok"


def _import_prism_module() -> Any | None:
    for module_name in ("prism", "prismatoid"):
        try:
            return import_module(module_name)
        except Exception:  # noqa: BLE001
            continue
    return None


def _backend_name(backend: Any) -> str:
    raw = getattr(backend, "name", None)
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return "Prism"


def _probe_to_message(probe: str) -> str:
    messages = {
        "missing": "Prism is not installed.",
        "context_error": "Prism failed to initialize context.",
        "acquire_error": "Prism could not acquire a backend.",
        "runtime_unavailable": "Prism backend is not active at runtime.",
    }
    return messages.get(probe, "Unknown Prism backend error.")
