"""#618: source-pin tests for the Report a Bug dialog changes.

The Report a Bug form is a wx.Dialog (or wx.Frame for the modeless
path) and we cannot drive a live wx dialog from a unit test (no
wxWidgets runtime in CI), so the pin is the only regression fence.
If anyone removes the field-name bindings, the modeless branch,
or the auto-open-browser gate, these tests fail immediately and
point at the issue.

The five things that must stay true for #618:

1. Every labelled field in the form has a SetName(label.GetLabel())
   binding so VoiceOver speaks the field name on tab (the Windows
   MSAA chain does not exist on macOS NSAccessibility).
2. The dispatch in _review_bug_report reads the
   report_bug_separate_window setting and routes to either
   _review_bug_report_modal (wx.Dialog) or
   _review_bug_report_modeless (wx.Frame).
3. The modeless branch builds a wx.Frame parented to self.frame
   and shows it with Show(), not ShowModal().
4. EndModal is only called from the modal branch (it would
   crash on a wx.Frame).
5. webbrowser.open is gated on report_bug_auto_open_browser
   inside _complete_bug_report_submission; the default in
   quill/core/settings.py is False.
"""

from __future__ import annotations

import re
from pathlib import Path

MAIN_FRAME = (Path(__file__).resolve().parents[3] / "quill" / "ui" / "main_frame.py").read_text(
    encoding="utf-8"
)
SETTINGS = (Path(__file__).resolve().parents[3] / "quill" / "core" / "settings.py").read_text(
    encoding="utf-8"
)
SETTINGS_SPECS = (
    Path(__file__).resolve().parents[3] / "quill" / "core" / "settings_specs.py"
).read_text(encoding="utf-8")


# Module-level patterns (extracted so the long regexes do not push
# individual test bodies past the 100-char line limit). Each pattern
# matches one full method body in main_frame.py.
_REVIEW_BUG_REPORT_PATTERN = (
    r"def _review_bug_report\(self\) -> tuple\[dict\[str, str\], str\] \| None:.*?(?=^    def |\Z)"
)
_REVIEW_BUG_REPORT_MODAL_PATTERN = (
    r"def _review_bug_report_modal\(self\) -> tuple\[dict\[str, str\], str\] \| None:"
    r".*?(?=^    def |\Z)"
)
_REVIEW_BUG_REPORT_MODELESS_PATTERN = (
    r"def _review_bug_report_modeless\(self\) -> tuple\[dict\[str, str\], str\] \| None:"
    r".*?(?=^    def |\Z)"
)
_BUILD_REPORT_BUG_FORM_BODY_PATTERN = r"def _build_report_bug_form_body\(.*?(?=^    def |\Z)"
_COMPLETE_BUG_REPORT_SUBMISSION_PATTERN = (
    r"def _complete_bug_report_submission\(.*?(?=^    def |\Z)"
)


def test_every_named_field_is_bound_for_screen_readers() -> None:
    """#618: every labelled field in the form has a SetName binding
    so VoiceOver announces the field name on tab."""
    body = re.search(_BUILD_REPORT_BUG_FORM_BODY_PATTERN, MAIN_FRAME, re.MULTILINE | re.DOTALL)
    assert body is not None, "_build_report_bug_form_body not found"
    src = body.group(0)
    # Each (label, field) pair in the form must be followed by
    # field.SetName(label.GetLabel()).
    bindings = [
        ("name_label", "name_field"),
        ("email_label", "email_field"),
        ("sr_label", "sr_combo"),
        ("summary_label", "summary_field"),
        ("happened_label", "happened_field"),
        ("expected_label", "expected_field"),
        ("steps_label", "steps_field"),
    ]
    for label, field in bindings:
        pattern = rf"{field}\.SetName\({label}\.GetLabel\(\)\)"
        assert re.search(pattern, src), (
            f"{field} must be bound to {label} via SetName for VoiceOver"
        )
    # diagnostics_path_field has no separate label widget, so it
    # uses a literal string matching the StaticText label.
    assert re.search(r'diagnostics_path_field\.SetName\("Diagnostics bundle path"\)', src), (
        "diagnostics_path_field must be bound via SetName for VoiceOver"
    )


def test_review_bug_report_dispatches_on_separate_window_setting() -> None:
    """#618: the dispatcher reads report_bug_separate_window and
    routes to the modal or modeless branch."""
    body = re.search(_REVIEW_BUG_REPORT_PATTERN, MAIN_FRAME, re.MULTILINE | re.DOTALL)
    assert body is not None, "_review_bug_report not found"
    src = body.group(0)
    assert "report_bug_separate_window" in src, "dispatcher must read report_bug_separate_window"
    assert "_review_bug_report_modeless()" in src, (
        "dispatcher must route to _review_bug_report_modeless"
    )
    assert "_review_bug_report_modal()" in src, "dispatcher must route to _review_bug_report_modal"


def test_modeless_path_uses_wx_frame() -> None:
    """#618: the modeless branch builds a wx.Frame (not wx.Dialog)
    so the user can alt-tab between the form and the editor."""
    body = re.search(_REVIEW_BUG_REPORT_MODELESS_PATTERN, MAIN_FRAME, re.MULTILINE | re.DOTALL)
    assert body is not None, "_review_bug_report_modeless not found"
    src = body.group(0)
    assert "wx.Frame(self.frame, title=" in src, (
        "modeless path must construct a wx.Frame parented to self.frame"
    )
    assert "Report a Bug" in src, "modeless Frame must use the Report a Bug title"
    assert "frame.Show()" in src or "frame.Show(" in src, (
        "modeless Frame must be shown with Show(), not ShowModal()"
    )
    assert "EndModal" not in src, (
        "modeless path must NOT call EndModal (it would crash on a wx.Frame)"
    )


def test_modal_path_uses_wx_dialog() -> None:
    """#618: the modal branch builds a wx.Dialog and ends modal on submit/cancel."""
    body = re.search(_REVIEW_BUG_REPORT_MODAL_PATTERN, MAIN_FRAME, re.MULTILINE | re.DOTALL)
    assert body is not None, "_review_bug_report_modal not found"
    src = body.group(0)
    assert "wx.Dialog(self.frame, title=" in src, (
        "modal path must construct a wx.Dialog parented to self.frame"
    )
    assert "apply_modal_ids" in src, "modal path must apply the shared modal id contract"
    assert "_show_modal_dialog" in src, "modal path must show through _show_modal_dialog"
    # EndModal is fine in the modal path (it is a wx.Dialog).
    assert "EndModal" in src, "modal path must use EndModal on submit/cancel"


def test_auto_open_browser_is_gated_on_setting() -> None:
    """#618: webbrowser.open is gated on report_bug_auto_open_browser
    inside _complete_bug_report_submission. The default behaviour
    is "Quill copies, you decide whether to open the browser"."""
    body = re.search(
        _COMPLETE_BUG_REPORT_SUBMISSION_PATTERN,
        MAIN_FRAME,
        re.MULTILINE | re.DOTALL,
    )
    assert body is not None, "_complete_bug_report_submission not found"
    src = body.group(0)
    assert "report_bug_auto_open_browser" in src, (
        "_complete_bug_report_submission must read report_bug_auto_open_browser"
    )
    # The webbrowser.open call must be inside an `if auto_open:` block,
    # not unconditional. A simple regex check that the call comes after
    # the `if auto_open:` line.
    auto_open_idx = src.find("if auto_open:")
    webbrowser_idx = src.find("webbrowser.open(issue_url)")
    assert 0 <= auto_open_idx < webbrowser_idx, (
        "webbrowser.open(issue_url) must be inside the `if auto_open:` branch"
    )


def test_settings_class_has_separate_window_default_true() -> None:
    """#618: the Settings class declares report_bug_separate_window
    with default True so the 0.7.0 default is a separate-window form."""
    pattern = r"report_bug_separate_window: bool = True"
    assert re.search(pattern, SETTINGS), "Settings.report_bug_separate_window must default to True"


def test_settings_class_has_auto_open_browser_default_false() -> None:
    """#618: the Settings class declares report_bug_auto_open_browser
    with default False so 0.5.0-upgrade users get the new
    "Quill copies, you decide whether to open the browser" behaviour."""
    pattern = r"report_bug_auto_open_browser: bool = False"
    assert re.search(pattern, SETTINGS), (
        "Settings.report_bug_auto_open_browser must default to False"
    )


def test_settings_specs_registers_both_keys() -> None:
    """#618: the new settings are registered in the spec list so
    they show up in the Settings UI and the doc-generator."""
    assert '"report_bug_separate_window"' in SETTINGS_SPECS, (
        "settings_specs must register report_bug_separate_window"
    )
    assert '"report_bug_auto_open_browser"' in SETTINGS_SPECS, (
        "settings_specs must register report_bug_auto_open_browser"
    )
    # Both must be in the "general" group.
    separate_window_block = re.search(
        r'"report_bug_separate_window",.*?\)', SETTINGS_SPECS, re.DOTALL
    )
    assert separate_window_block and '"general"' in separate_window_block.group(0), (
        "report_bug_separate_window must be in the 'general' group"
    )
    auto_open_block = re.search(r'"report_bug_auto_open_browser",.*?\)', SETTINGS_SPECS, re.DOTALL)
    assert auto_open_block and '"general"' in auto_open_block.group(0), (
        "report_bug_auto_open_browser must be in the 'general' group"
    )


def test_dispatcher_getattr_falls_back_to_true_for_separate_window() -> None:
    """#618: getattr(self.settings, "report_bug_separate_window", True)
    so a missing setting key (e.g. a settings file from before #618
    shipped) defaults to the new behaviour."""
    body = re.search(_REVIEW_BUG_REPORT_PATTERN, MAIN_FRAME, re.MULTILINE | re.DOTALL)
    assert body is not None
    src = body.group(0)
    pattern = r'getattr\(\s*self\.settings,\s*"report_bug_separate_window",\s*True\s*\)'
    assert re.search(pattern, src), (
        "getattr fallback for report_bug_separate_window must default to True"
    )


def test_completion_helper_getattr_falls_back_to_false_for_auto_open() -> None:
    """#618: getattr(self.settings, "report_bug_auto_open_browser", False)
    so a missing setting key (e.g. a settings file from before #618
    shipped) defaults to the new "no auto-open" behaviour."""
    body = re.search(
        _COMPLETE_BUG_REPORT_SUBMISSION_PATTERN,
        MAIN_FRAME,
        re.MULTILINE | re.DOTALL,
    )
    assert body is not None
    src = body.group(0)
    pattern = r'getattr\(\s*self\.settings,\s*"report_bug_auto_open_browser",\s*False\s*\)'
    assert re.search(pattern, src), (
        "getattr fallback for report_bug_auto_open_browser must default to False"
    )
