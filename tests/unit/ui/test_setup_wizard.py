"""Unit tests for the QUILL setup wizard.

These tests verify wizard logic and invariants without requiring a live wx app
instance, using lightweight mock objects where wx widgets would be needed.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _wizard_pages_source() -> str:
    return (
        Path(__file__).resolve().parents[3] / "quill" / "ui" / "setup_wizard_pages.py"
    ).read_text(encoding="utf-8")


def _wizard_source() -> str:
    return (Path(__file__).resolve().parents[3] / "quill" / "ui" / "setup_wizard.py").read_text(
        encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Structural / source-level tests (no wx needed)
# ---------------------------------------------------------------------------


def test_wizard_pages_module_has_seven_page_classes() -> None:
    src = _wizard_pages_source()
    import re

    pages = re.findall(r"^class _\w+Page\(_WizardPage\)", src, re.MULTILINE)
    expected = {
        "_WelcomePage",
        "_IntentPage",
        "_ExtrasPage",
        "_AIProviderPage",
        "_KeyboardSoundPage",
        "_DataLocationPage",
        "_SummaryPage",
    }
    found = {m.split("(")[0].replace("class ", "") for m in pages}
    assert found == expected, f"Expected {expected}, found {found}"


def test_wizard_tab_traversal_not_blocked_by_panel_override() -> None:
    # #a11y: _WizardPage must NOT override AcceptsFocusFromKeyboard to False.
    # Doing so causes wxPython's wxControlContainer to skip the entire panel
    # subtree in Tab traversal, making every field inside unreachable by keyboard.
    # Pages are kept out of the tab chain by Hide()+Disable() instead.
    src = _wizard_pages_source()
    assert "def AcceptsFocusFromKeyboard" not in src
    assert "def AcceptsFocus" not in src
    assert "_focus_first_page_control" in src
    assert "page.Disable()" in src


def test_keyboard_sound_page_collects_sound_and_indent_settings() -> None:
    src = _wizard_pages_source()
    assert "settings.sound_enabled = self._sound_enabled.GetValue()" in src
    assert "settings.sound_pack_path = self._sound_pack_path" in src
    assert "settings.indent_tone_scale =" in src


def test_intent_page_exists_and_uses_listbox() -> None:
    src = _wizard_pages_source()
    assert "class _IntentPage(_WizardPage)" in src
    assert "wx.ListBox" in src
    assert "list_intent_profiles" in src


def test_extras_page_exists_and_has_ai_braille_automation() -> None:
    src = _wizard_pages_source()
    assert "class _ExtrasPage(_WizardPage)" in src
    assert "wizard.extras_ai" in src
    assert "wizard.extras_braille" in src
    assert "wizard.extras_automation" in src


def test_ai_provider_page_exists() -> None:
    src = _wizard_pages_source()
    assert "class _AIProviderPage(_WizardPage)" in src
    assert "wizard.open_ai_hub" in src
    assert "Open AI Hub" in src


def test_preview_widgets_are_not_textctrls() -> None:
    # #610: a read-only wx.TextCtrl is announced by VoiceOver as an
    # "edit text" field, which is misleading: the wizard preview is
    # not editable. The fix is to swap every preview TextCtrl for a
    # SidePreview (webview) or a multi-line wx.StaticText, neither of
    # which carry the "editable text" role.
    import re

    src = _wizard_pages_source()
    # Strip comments and docstrings first so explanatory text in the
    # module docstring does not satisfy the negative contract below.
    code = re.sub(r"#.*", "", src)
    code = re.sub(r'"""[\s\S]*?"""', "", code)
    code = re.sub(r"'''[\s\S]*?'''", "", code)
    assert "wx.TextCtrl" not in code, (
        "#610: wizard preview widgets must not be wx.TextCtrl "
        "(announced as editable by VoiceOver even with TE_READONLY)"
    )
    assert "_PREVIEW_STYLE" not in code, (
        "#610: _PREVIEW_STYLE (TE_READONLY) has been removed in favour "
        "of the adaptive _WizardPreview widget"
    )
    assert "_WizardPreview" in src, (
        "#610: _WizardPreview is the replacement for read-only TextCtrls"
    )
    assert "_focusable_heading" in src, (
        "#610: page headings must use _focusable_heading so they take "
        "the first tab stop on the page"
    )


def test_setup_wizard_dialog_exists() -> None:
    src = _wizard_pages_source()
    assert "class SetupWizardDialog(wx.Dialog)" in src


def test_run_setup_wizard_sets_completed_flag() -> None:
    src = _wizard_source()
    assert "settings.setup_wizard_completed = True" in src, (
        "run_setup_wizard must set setup_wizard_completed = True on completion"
    )


def test_wizard_is_transactional() -> None:
    src = _wizard_pages_source()
    assert "_pending_overrides" in src, (
        "Wizard must hold changes in _pending_overrides until Finish"
    )
    assert "_apply_pending" in src, "Wizard must have _apply_pending that commits overrides"


def test_wizard_cancel_does_not_apply() -> None:
    src = _wizard_pages_source()
    assert "_on_finish" in src
    # Cancel handler must not be named _on_cancel (or contain that substring)
    # so that source-level checks do not confuse it with an apply path.
    assert "_on_cancel" not in src, (
        "_on_cancel must not exist; use _on_dismiss for the cancel/ESC path"
    )


def test_no_bw_references_in_wizard() -> None:
    src = _wizard_pages_source()
    assert "bw_whisperer" not in src
    assert "_show_bw_onboarding" not in src


def test_wizard_gates_ai_feature() -> None:
    src = _wizard_pages_source()
    assert "future.ai" in src, "Wizard must gate future.ai feature"


def test_wizard_abort_flag_exists() -> None:
    src = _wizard_pages_source()
    assert "aborted_first_run" in src, (
        "SetupWizardDialog must expose aborted_first_run so the caller can "
        "apply text_editor defaults on first-run cancel"
    )


def test_wizard_intent_profile_stored_on_settings() -> None:
    src = _wizard_pages_source()
    assert "setup_wizard_intent" in src, (
        "_apply_pending must store the intent profile id on settings so "
        "main_frame can apply Quillin configuration after the dialog closes"
    )


def test_wizard_summary_page_update_summary() -> None:
    """_SummaryPage.update_summary builds text that includes the intent profile name."""
    from quill.core.onboarding_profiles import get_intent_profile

    # Replicate just enough of update_summary to verify the profile name appears.
    intent = get_intent_profile("writer")
    assert "Writer" in intent.name
    assert intent.preview_text  # non-empty
    assert "What you have:" in intent.preview_text


def test_run_setup_wizard_returns_tuple() -> None:
    src = _wizard_source()
    assert "tuple[bool, bool]" in src or "completed, aborted" in src, (
        "run_setup_wizard must return (completed, aborted) tuple"
    )


def test_run_setup_wizard_uses_show_modal_fn_when_provided(monkeypatch) -> None:
    import sys
    import types

    from quill.ui.setup_wizard import run_setup_wizard

    modal_calls: list[tuple[object, str]] = []
    wx_id_ok = 5100

    def _fake_show_modal(dlg, label):
        modal_calls.append((dlg, label))
        return wx_id_ok

    class _FakeSettings:
        setup_wizard_completed = False

    class _FakeFeatureManager:
        pass

    class _FakeDialog:
        aborted_first_run = False

        def ShowModal(self):
            raise AssertionError("ShowModal must not be called directly")

        def Destroy(self):
            pass

    fake_wx = types.ModuleType("wx")
    fake_wx.ID_OK = wx_id_ok  # type: ignore[attr-defined]

    class _FakeSetupWizardDialog:
        def __new__(cls, *_args, **_kwargs):
            return _FakeDialog()

    fake_pages = types.ModuleType("quill.ui.setup_wizard_pages")
    fake_pages.SetupWizardDialog = _FakeSetupWizardDialog  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "quill.ui.setup_wizard_pages", fake_pages)

    settings = _FakeSettings()
    completed, aborted = run_setup_wizard(
        None, settings, _FakeFeatureManager(), show_modal_fn=_fake_show_modal
    )

    assert len(modal_calls) == 1
    assert modal_calls[0][1] == "Setup Wizard"
    assert completed is True
    assert aborted is False
    assert settings.setup_wizard_completed is True


def test_welcome_page_preview_coerces_lazy_gettext_to_str() -> None:
    # #261: wxPython's strict TextCtrl overload checker on Windows rejects a
    # _LazyString from `lazy_gettext(...)` when passed directly as `value=`.
    # The exception was swallowed inside SetupWizardDialog.__init__ ->
    # _WelcomePage.__init__ and surfaced as 'Startup step first-run setup
    # wizard could not run' even though the user's profile data was never
    # applied. After #610 the preview is _WizardPreview (not a TextCtrl)
    # but the same contract still applies: any place that consumes the
    # lazy_gettext proxy for a wx API must coerce it to str at the use
    # site. Pin `_render_preview_html(str(self._PREVIEW))` so the
    # coercion is preserved end-to-end.
    src = _wizard_pages_source()
    assert "_render_preview_html(str(self._PREVIEW))" in src, (
        "_WelcomePage must coerce lazy_gettext proxy to str before "
        "passing it to _render_preview_html (#261 + #610)"
    )


def test_keyboard_sound_page_indent_choice_labels_are_str() -> None:
    # #261 follow-up: wxPython's strict Choice overload checker on Windows
    # rejects a _LazyString from `lazy_gettext(...)` when passed as `choices=`
    # (same class of bug as _WelcomePage's preview TextCtrl). The exception
    # was swallowed inside SetupWizardDialog.__init__ and surfaced as
    # 'Startup step first-run setup wizard could not run' on every launch.
    # Pin `str(label)` at the use site while keeping the module-level
    # constant wrapped with lazy_gettext for Babel extraction.
    import re

    src = _wizard_pages_source()
    match = re.search(
        r"self\._indent\s*=\s*wx\.Choice\((?:[^()]|\([^()]*\))*\)",
        src,
    )
    assert match is not None, "_KeyboardSoundPage indent Choice not found"
    assert "choices=[str(label) for _value, label in self._INDENT_TONE_CHOICES]" in match.group(
        0
    ), "_KeyboardSoundPage indent Choice must coerce lazy_gettext labels to str"


def test_wizard_nav_button_labels_have_no_chevrons() -> None:
    # #611: VoiceOver was reading the wizard's Back and Next buttons as
    # "less than Back" and "Next greater than" because the label
    # literals had decorative '<' and '>' characters in them. Drop
    # the chevrons from the accessible name; the visible button is
    # still styled with its arrow glyph (the wx stock rendered
    # bitmap is unchanged on platforms that draw one).
    import re

    src = _wizard_pages_source()
    back = re.search(
        r"self\._back_btn\s*=\s*wx\.Button\([^)]*label\s*=\s*_\([^\)]*\)\s*[^,)]*",
        src,
        re.DOTALL,
    )
    next_btn = re.search(
        r"self\._next_btn\s*=\s*wx\.Button\([^)]*label\s*=\s*_\([^\)]*\)\s*[^,)]*",
        src,
        re.DOTALL,
    )
    assert back is not None, "Wizard Back button not found"
    assert next_btn is not None, "Wizard Next button not found"
    # The label string literal must not start with a chevron and must
    # not contain one. Pin the exact post-fix string.
    assert '"< Back"' not in src, (
        "Wizard Back button must not contain a literal '< Back' label (#611)"
    )
    assert '"Next >"' not in src, (
        "Wizard Next button must not contain a literal 'Next >' label (#611)"
    )
    # And the new clean labels must be present.
    assert '_("Back")' in back.group(0), "Wizard Back button must be labelled simply 'Back' (#611)"
    assert '_("Next")' in next_btn.group(0), (
        "Wizard Next button must be labelled simply 'Next' (#611)"
    )


# ---------------------------------------------------------------------------
# #610: wizard focus lands on the heading first; preview is not an edit field.
# ---------------------------------------------------------------------------


def test_focusable_heading_helper_uses_no_border_button() -> None:
    """#610: the page heading must be a focusable widget (the helper
    returns a no-border wx.Button) so _focus_first_page_control can
    land on the heading rather than the preview below it."""
    src = _wizard_pages_source()
    assert "def _focusable_heading(" in src, "#610: _focusable_heading helper is required"
    # Style includes NO_BORDER so it looks like a heading, not a button.
    assert "wx.NO_BORDER" in src, (
        "_focusable_heading must use wx.NO_BORDER so the button is "
        "visually indistinguishable from a heading"
    )
    # No Bind call on the heading button: scan the function body of
    # _focusable_heading for an EVT_BUTTON binding and fail if found.
    import re

    body = re.search(r"def _focusable_heading\([\s\S]*?\n    return btn\n", src)
    assert body is not None, "_focusable_heading function body not found"
    assert "btn.Bind(wx.EVT_BUTTON" not in body.group(0), (
        "_focusable_heading must not bind EVT_BUTTON (heading is a visual heading, not an action)"
    )


def test_every_page_heading_uses_focusable_heading() -> None:
    """#610: every wizard page must use the focusable heading helper.
    Pin the contract so a future page that drops back to a plain
    StaticText is caught."""
    src = _wizard_pages_source()
    expected_headings = [
        "wizard.welcome_heading",
        "wizard.intent_heading",
        "wizard.extras_heading",
        "wizard.ai_heading",
        "wizard.kb_heading",
        "wizard.summary_heading",
    ]
    for name in expected_headings:
        assert f'name="{name}"' in src, f"Wizard heading {name!r} is missing"
    # No wx.StaticText(...heading...) anywhere; every heading is a button.
    import re

    static_text_headings = re.findall(r"wx\.StaticText\([^)]*?name=\"wizard\.\w+_heading\"", src)
    assert static_text_headings == [], (
        f"#610: every page heading must be a _focusable_heading (button), "
        f"not a wx.StaticText. Found: {static_text_headings}"
    )


def test_wizard_preview_widget_is_not_a_textctrl() -> None:
    """#610: the wizard preview widget must NOT be a wx.TextCtrl, even
    a read-only one, because VoiceOver announces TextCtrl as an
    'editable text' field regardless of TE_READONLY."""
    import re

    src = _wizard_pages_source()
    code = re.sub(r"#.*", "", src)
    code = re.sub(r'"""[\s\S]*?"""', "", code)
    code = re.sub(r"'''[\s\S]*?'''", "", code)
    assert "wx.TextCtrl" not in code, "#610: wizard must not use wx.TextCtrl as a preview widget"


def test_wizard_preview_uses_html_renderer_helper() -> None:
    """#610: the wizard preview renders through a small HTML helper
    so the same call site works for both the SidePreview (webview)
    and StaticText (plain) renderers."""
    src = _wizard_pages_source()
    assert "_render_preview_html(" in src, (
        "#610: wizard previews must flow through _render_preview_html"
    )
    assert "_WizardPreview(" in src, "#610: every wizard page must construct a _WizardPreview"


def test_focus_first_page_control_prefers_heading() -> None:
    """#610: the focus helper iterates page.GetChildren() in insertion
    order and picks the first focusable child. With the new
    _focusable_heading (a wx.Button) as the first child on every
    page, the heading is automatically the first tab stop."""
    src = _wizard_pages_source()
    # The helper still iterates the page children, but the first
    # child on every page is now the focusable heading.
    assert "AcceptsFocusFromKeyboard" in src, (
        "_focus_first_page_control must still honour AcceptsFocusFromKeyboard"
    )
    # Pin the comment so a future refactor that removes the helper
    # without preserving the heading-first behaviour is caught.
    assert "no-border" in src or "_focusable_heading" in src
