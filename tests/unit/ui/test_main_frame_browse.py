"""Tests for BrowseModeMixin prewarm thread management (M-30)."""

from __future__ import annotations

from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[3] / "quill" / "ui" / "main_frame_browse.py").read_text(
    encoding="utf-8"
)


def test_prewarm_thread_cancelled_on_repeat() -> None:
    # M-30: When a new prewarm build starts, the previous cancel event must be
    # set so the in-flight worker drops its stale result rather than applying it.
    assert "_browse_cache_cancel_event" in SOURCE
    assert "old_cancel.set()" in SOURCE


def test_worker_checks_cancel_before_applying_cache() -> None:
    # The worker must check cancel_event.is_set() before calling wx.CallAfter
    # so a cancelled build never triggers a UI update.
    assert "cancel_event.is_set()" in SOURCE
    # The check must appear before the CallAfter call in the source.
    cancel_idx = SOURCE.index("cancel_event.is_set()")
    callafter_idx = SOURCE.index("self._wx.CallAfter(")
    assert cancel_idx < callafter_idx
