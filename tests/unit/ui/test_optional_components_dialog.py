"""Source-contract tests for the Download Optional Components dialog.

Constructing a real wx.Dialog is not exercised in this suite (matching the
repo's dialog-test convention); these assert the source wires the warm-hub
contract: a rich description box, Download-gating, Test and Remove buttons, the
seam helpers, and controller delegation.
"""

from __future__ import annotations

from pathlib import Path

_UI = Path(__file__).resolve().parents[3] / "quill" / "ui"


def _src(name: str) -> str:
    return (_UI / name).read_text(encoding="utf-8")


def test_dialog_has_download_test_remove_buttons() -> None:
    src = _src("optional_components_dialog.py")
    assert 'name="optional_components_download"' in src
    assert 'name="optional_components_test"' in src
    assert 'name="optional_components_remove"' in src


def test_dialog_uses_a_readonly_multiline_description() -> None:
    src = _src("optional_components_dialog.py")
    assert "TE_MULTILINE" in src and "TE_READONLY" in src
    assert "describe_component(" in src


def test_dialog_gates_download_when_installed() -> None:
    src = _src("optional_components_dialog.py")
    assert "download_btn.Enable(not comp.installed)" in src
    assert "test_btn.Enable(comp.installed)" in src


def test_dialog_delegates_to_controller_and_uses_the_seam() -> None:
    src = _src("optional_components_dialog.py")
    assert "controller.test(" in src
    assert "controller.remove(" in src
    assert "controller.removable(" in src
    assert "apply_modal_ids(" in src
    assert "show_message_box(" in src  # not raw wx.MessageBox
    assert "preselect" in src


def test_open_optional_components_routes_and_covers_all_downloads() -> None:
    src = _src("main_frame_speech.py")
    # Stay-open hub via a controller, preselect support, and the two newly
    # catalogued downloads wired into the dispatch.
    assert "preselect" in src
    assert '"piper": self.download_piper_exe' in src
    assert '"node": self.download_node_runtime' in src
    assert "def download_node_runtime" in src
    assert "def _test_optional_component" in src
    assert "def _remove_optional_component" in src


def test_startup_braille_prompt_routes_into_the_hub() -> None:
    src = _src("main_frame.py")
    assert 'open_optional_components(preselect="braille")' in src


def test_dialog_loads_component_list_off_the_ui_thread() -> None:
    """gather runs tool version probes + filesystem scans; the dialog must build
    the list on a worker so it opens instantly, not stall on those probes."""
    src = _src("optional_components_dialog.py")
    assert "import threading" in src
    assert "threading.Thread(" in src
    assert "wx.CallAfter(_populate" in src
    assert "Loading components" in src
