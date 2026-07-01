"""Unit tests for the wx-free lifecycle service singleton (Phase 2 wiring)."""

from __future__ import annotations

import pytest

from quill.core import lifecycle_service as ls


@pytest.fixture(autouse=True)
def _reset_service():
    ls.reset()
    yield
    ls.reset()


def test_calls_are_safe_no_ops_when_unconfigured() -> None:
    # None of these may raise before configure() is called.
    assert ls.get() is None
    ls.note_loaded("x", lambda: None)
    ls.touch("x")
    ls.note_unloaded("x")
    assert ls.reserve("x") == []
    assert ls.sweep() == []


def test_configure_builds_manager_and_registrations_flow_through() -> None:
    ls.configure(low_resource_mode=False, idle_unload_minutes=10, total_ram_gb=16.0)
    manager = ls.get()
    assert manager is not None
    assert manager.idle_timeout == 600.0

    freed: list[str] = []
    ls.note_loaded("llm", lambda: freed.append("llm"))
    assert manager.loaded_keys() == ["llm"]

    # Force everything idle and sweep -> the registered unload runs.
    manager.idle_timeout = 0.0  # still swept? no: <=0 disables. Use a tiny timeout.
    manager.idle_timeout = 0.001
    import time

    time.sleep(0.005)
    assert ls.sweep() == ["llm"]
    assert freed == ["llm"]


def test_reserve_evicts_under_low_resource_mode() -> None:
    ls.configure(low_resource_mode=True, idle_unload_minutes=0, total_ram_gb=16.0)
    freed: list[str] = []
    ls.note_loaded("speech", lambda: freed.append("speech"))
    # Loading a second engine under a cap of 1 evicts the first (its unload runs).
    evicted = ls.reserve("tts")
    assert evicted == ["speech"]
    assert freed == ["speech"]


def test_note_unloaded_and_touch_are_forwarded() -> None:
    ls.configure(low_resource_mode=False, idle_unload_minutes=5, total_ram_gb=8.0)
    ls.note_loaded("k", lambda: None)
    ls.touch("k")  # must not raise
    ls.note_unloaded("k")
    assert ls.get().loaded_keys() == []  # type: ignore[union-attr]


def test_llama_backend_unload_clears_model_and_untracks() -> None:
    """The LLM backend's unload() (registered with the service) frees the model and
    stops the manager tracking it — the contract the idle sweep relies on."""
    from quill.core.ai.llama_cpp_backend import LlamaCppBackend

    ls.configure(low_resource_mode=False, idle_unload_minutes=5, total_ram_gb=8.0)
    backend = LlamaCppBackend()
    backend._llm = object()  # pretend a model is loaded (avoids native llama_cpp)
    ls.note_loaded("llm", backend.unload)
    assert ls.get().loaded_keys() == ["llm"]  # type: ignore[union-attr]

    backend.unload()

    assert backend._llm is None
    assert ls.get().loaded_keys() == []  # type: ignore[union-attr]


def test_configure_replaces_previous_manager() -> None:
    first = ls.configure(low_resource_mode=False, idle_unload_minutes=10, total_ram_gb=16.0)
    second = ls.configure(low_resource_mode=True, idle_unload_minutes=1, total_ram_gb=2.0)
    assert first is not second
    assert ls.get() is second
    assert second.max_concurrent == 1
