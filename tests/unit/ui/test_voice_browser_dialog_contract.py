"""Source-contract test for the Voice Browser dialog (fix.md #3).

Assert the wiring in :mod:`quill.ui.voice_browser_dialog` without spinning up
a real wx UI, matching the convention in test_remote_sites_dialog.py.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "quill" / "ui" / "voice_browser_dialog.py"


def _read_source() -> str:
    return ROOT.read_text(encoding="utf-8")


def test_module_calls_focus_primary_control() -> None:
    src = _read_source()
    assert "focus_primary_control" in src
