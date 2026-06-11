"""Tests for quill.tools.menu_lint (GATE-12)."""

from __future__ import annotations

from quill.tools.menu_lint import (
    _check_ctrl_alt,
    _check_depth,
    _check_required_clusters,
    run_checks,
)

# ---------------------------------------------------------------------------
# Ctrl+Alt policy
# ---------------------------------------------------------------------------


def test_ctrl_alt_clean_source_passes() -> None:
    src = 'DEFAULT_KEYMAP: dict[str, str] = {\n    "edit.find": "Ctrl+F",\n}\n'
    assert _check_ctrl_alt(src) == []


def test_ctrl_alt_detects_violation() -> None:
    src = 'DEFAULT_KEYMAP: dict[str, str] = {\n    "edit.bad": "Ctrl+Alt+X",\n}\n'
    errors = _check_ctrl_alt(src)
    assert any("Ctrl+Alt+" in e for e in errors)
    assert any("edit.bad" in e for e in errors)


def test_ctrl_alt_exempted_commands_pass() -> None:
    src = (
        "DEFAULT_KEYMAP: dict[str, str] = {\n"
        '    "view.send_to_tray": "Ctrl+Alt+T",\n'
        '    "view.toggle_tab_control": "Ctrl+Alt+Shift+T",\n'
        "}\n"
    )
    assert _check_ctrl_alt(src) == []


def test_ctrl_alt_case_insensitive() -> None:
    src = 'DEFAULT_KEYMAP: dict[str, str] = {\n    "edit.bad": "ctrl+alt+v",\n}\n'
    errors = _check_ctrl_alt(src)
    assert errors


# ---------------------------------------------------------------------------
# Required clusters
# ---------------------------------------------------------------------------


def test_required_clusters_present() -> None:
    # All nine required cluster labels in one fake source.
    fake = (
        '"R&eading && Dictation" "C&omparison" "&Watch Folder" "AI &Assistant"'
        ' "&Advanced" "&Quillins" "A&ccessibility" "&Customize && Support"'
        ' "&Writing && Language"'
    )
    assert _check_required_clusters(fake) == []


def test_required_clusters_missing_reports_error() -> None:
    fake = '"C&omparison"'  # most clusters absent
    errors = _check_required_clusters(fake)
    assert errors


def test_required_clusters_missing_writing_language() -> None:
    fake = (
        '"R&eading && Dictation" "C&omparison" "&Watch Folder" "AI &Assistant"'
        ' "&Advanced" "&Quillins" "A&ccessibility" "&Customize && Support"'
    )
    errors = _check_required_clusters(fake)
    assert any("Writing" in e for e in errors)


# ---------------------------------------------------------------------------
# Depth check
# ---------------------------------------------------------------------------


def test_depth_two_level_allowed() -> None:
    # tools_menu > power_tools_menu > macro_menu  (depth 2, no further children)
    src = (
        "def build():\n"
        "    tools_menu = wx.Menu()\n"
        "    power_tools_menu = wx.Menu()\n"
        "    macro_menu = wx.Menu()\n"
        "    macro_menu.Append(1, 'item')\n"
        "    power_tools_menu.AppendSubMenu(macro_menu, 'Macros')\n"
        "    tools_menu.AppendSubMenu(power_tools_menu, 'Power Tools')\n"
    )
    assert _check_depth(src) == []


def test_depth_three_level_flagged() -> None:
    # tools_menu > sub1 > sub2 > sub3 — sub2 is depth 2 with children
    src = (
        "def build():\n"
        "    tools_menu = wx.Menu()\n"
        "    sub1 = wx.Menu()\n"
        "    sub2 = wx.Menu()\n"
        "    sub3 = wx.Menu()\n"
        "    sub3.Append(1, 'item')\n"
        "    sub2.AppendSubMenu(sub3, 'Sub3')\n"
        "    sub1.AppendSubMenu(sub2, 'Sub2')\n"
        "    tools_menu.AppendSubMenu(sub1, 'Sub1')\n"
    )
    errors = _check_depth(src)
    assert errors
    assert any("sub2" in e for e in errors)


def test_depth_root_menus_ignored() -> None:
    # file_menu is depth 0 (root); it can have submenus without violation.
    src = (
        "def build():\n"
        "    file_menu = wx.Menu()\n"
        "    recent_menu = wx.Menu()\n"
        "    recent_menu.Append(1, 'item')\n"
        "    file_menu.AppendSubMenu(recent_menu, 'Recent')\n"
    )
    assert _check_depth(src) == []


# ---------------------------------------------------------------------------
# Integration: full run_checks on live source
# ---------------------------------------------------------------------------


def test_run_checks_passes_on_current_codebase() -> None:
    errors = run_checks()
    assert errors == [], "\n".join(errors)
