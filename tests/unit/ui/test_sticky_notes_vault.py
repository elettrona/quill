"""Tests for StickyNotesVaultDialog dialog contract (M-31)."""

from __future__ import annotations

from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[3] / "quill" / "ui" / "sticky_notes.py").read_text(
    encoding="utf-8"
)


def test_delete_confirm_uses_contract_helper() -> None:
    # M-31: _delete_selected must use show_message_box (the dialog-contract
    # helper) rather than raw self._wx.MessageBox, so screen readers hear the
    # enter/exit announcement cues.
    assert "from quill.ui.dialog_contract import" in SOURCE
    assert "show_message_box" in SOURCE
    # Must NOT use the bare wx.MessageBox or self._wx.MessageBox pattern.
    assert "self._wx.MessageBox" not in SOURCE
    assert "wx.MessageBox" not in SOURCE
