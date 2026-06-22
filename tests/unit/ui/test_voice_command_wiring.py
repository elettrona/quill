"""Source-contract tests for the offline voice-command wiring (#663)."""

from __future__ import annotations

import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]


def _src(rel: str) -> str:
    return (_ROOT / rel).read_text(encoding="utf-8")


def test_command_registered() -> None:
    src = _src("quill/ui/main_frame.py")
    assert '"tools.voice_command"' in src
    assert "self.voice_command_toggle" in src


def test_handler_present_and_gated() -> None:
    src = _src("quill/ui/main_frame_speech.py")
    assert "def voice_command_toggle" in src
    assert "voice_commands_available" in src  # off-by-default + Safe Mode gate
    assert "SAFE_TOOL_IDS" in src  # double-gate before dispatch


def test_menu_item_present() -> None:
    src = _src("quill/ui/main_frame_menu.py")
    assert "_id_speech_voice_command" in src
    assert "tools.voice_command" in src


def test_keymap_entry_present_unbound_by_default() -> None:
    b = json.loads(
        (_ROOT / "quill" / "core" / "keymap" / "profile_default.json").read_text(encoding="utf-8")
    )["bindings"]
    assert b.get("tools.voice_command") == ""  # discoverable; users bind their own


def test_dispatch_only_runs_safe_tool_ids() -> None:
    # The dispatch path checks command_id in SAFE_TOOL_IDS before registry.run.
    src = _src("quill/ui/main_frame_speech.py")
    assert "outcome.command_id in SAFE_TOOL_IDS" in src
