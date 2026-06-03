"""Broad guard: custom wx.Dialog surfaces must route through the focus seam.

Initial-focus correction lives in ``MainFrame._show_modal_dialog`` (it calls
``focus_primary_control`` for raw ``wx.Dialog`` surfaces). A custom dialog that
is shown via a direct ``dialog.ShowModal()`` bypasses that seam and reopens the
"focus parked on the OK button" defect. This AST guard fails if any function in
``quill/ui/main_frame.py`` constructs a raw ``wx.Dialog`` and then calls
``.ShowModal()`` on it directly instead of handing it to ``_show_modal_dialog``.

It deliberately only flags raw ``wx.Dialog(...)`` locals, so native dialogs
(``wx.PageSetupDialog``, ``wx.FileDialog``, ``wx.MessageDialog``, ...) — which
manage their own focus — are unaffected.
"""

from __future__ import annotations

import ast
from pathlib import Path

_MAIN_FRAME = Path(__file__).resolve().parents[3] / "quill" / "ui" / "main_frame.py"


def _is_raw_wx_dialog_call(node: ast.expr) -> bool:
    """True when *node* is a ``wx.Dialog(...)`` / ``self._wx.Dialog(...)`` call."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    return isinstance(func, ast.Attribute) and func.attr == "Dialog"


def _raw_dialog_locals(func: ast.FunctionDef) -> set[str]:
    """Names assigned a raw ``wx.Dialog(...)`` value within *func*."""
    names: set[str] = set()
    for node in ast.walk(func):
        if isinstance(node, ast.Assign) and _is_raw_wx_dialog_call(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _direct_show_modal_targets(func: ast.FunctionDef) -> set[str]:
    """Names ``x`` on which ``x.ShowModal()`` is called directly within *func*."""
    targets: set[str] = set()
    for node in ast.walk(func):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "ShowModal"
            and isinstance(node.func.value, ast.Name)
        ):
            targets.add(node.func.value.id)
    return targets


def test_no_custom_dialog_bypasses_focus_seam() -> None:
    tree = ast.parse(_MAIN_FRAME.read_text(encoding="utf-8"))
    offenders: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        bypassed = _raw_dialog_locals(node) & _direct_show_modal_targets(node)
        for name in sorted(bypassed):
            offenders.append(f"{node.name}: '{name}.ShowModal()'")

    assert not offenders, (
        "Custom wx.Dialog surfaces must be shown via self._show_modal_dialog(...) "
        "so they inherit initial-focus correction. Direct .ShowModal() bypasses "
        "found:\n  " + "\n  ".join(offenders)
    )
