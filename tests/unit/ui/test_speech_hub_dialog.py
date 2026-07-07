"""Source-contract test for the Speech Hub dialog (fix.md #3).

Assert the wiring in :mod:`quill.ui.speech_hub_dialog` without spinning up a
real wx UI, matching the convention in test_remote_sites_dialog.py.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "quill" / "ui" / "speech_hub_dialog.py"


def _read_source() -> str:
    return ROOT.read_text(encoding="utf-8")


def test_module_calls_focus_primary_control() -> None:
    src = _read_source()
    # The dialog was opening with focus parked on OK/Cancel instead of the
    # first real Read Aloud / Dictation control (fix.md #3).
    assert "focus_primary_control" in src
