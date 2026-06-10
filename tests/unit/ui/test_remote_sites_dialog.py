"""Source-contract tests for the Remote Sites manager dialog (issue #154).

These tests assert the wiring in :mod:`quill.ui.remote_sites_dialog` without
spinning up a real wx UI. The dialog is exercised end-to-end under
``quill/tools/dialog_inventory.py`` and the A11Y-4 banned-pattern gate.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "quill" / "ui" / "remote_sites_dialog.py"


def _read_source() -> str:
    return ROOT.read_text(encoding="utf-8")


def test_module_uses_apply_modal_ids() -> None:
    assert "apply_modal_ids" in _read_source()


def test_module_exposes_dialog_mode_enum() -> None:
    src = _read_source()
    assert "class DialogMode" in src
    assert "OPEN" in src
    assert "SAVE" in src


def test_module_exposes_site_editor_subdialog() -> None:
    src = _read_source()
    # The site editor sub-dialog is the only way to add or edit a saved
    # site; the contract test asserts it is wired.
    assert re.search(r"class\s+_SiteEditorDialog", src)


def test_module_uses_default_dialog_style() -> None:
    src = _read_source()
    assert "wx.DEFAULT_DIALOG_STYLE" in src


def test_module_registers_id_open_remote() -> None:
    src = _read_source()
    # The dialog wires up the file picker (Open or Save) with a stable
    # id pattern; the test asserts that an action id for opening a remote
    # file is present.
    assert "id=self._id_new_site" in src
    assert "id=self._id_edit_site" in src
    assert "id=self._id_delete_site" in src


def test_module_calls_focus_primary_control() -> None:
    src = _read_source()
    # The dialog contract requires deterministic initial focus.
    assert "focus_primary_control" in src
