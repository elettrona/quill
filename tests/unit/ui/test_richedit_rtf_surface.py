"""QuillRichEdit Phase 0 surface (native Rich Edit wrapper, "richedit_rtf").

Contract-level tests (no live wx): the setting round-trips, the combo offers the
surface, the Experimental-tab explainer covers it, MainFrame dispatches it, and
the wrapper's Phase-0 boundaries are honest (RTF I/O not yet wired, capability
reporting says so, the diagnostic carries no document content). See
docs/planning/editor-surface-experiments.md §8 for the surface entry.
"""

from __future__ import annotations

import inspect

from quill.core.settings import Settings
from quill.core.settings_specs import SETTING_SPECS


def _surface_spec():
    return next(spec for spec in SETTING_SPECS if spec.key == "experimental_editor_surface")


def test_settings_accept_richedit_rtf_surface() -> None:
    loaded = Settings.from_dict({"experimental_editor_surface": "richedit_rtf"})
    assert loaded.experimental_editor_surface == "richedit_rtf"


def test_settings_still_reject_unknown_surfaces() -> None:
    loaded = Settings.from_dict({"experimental_editor_surface": "bogus"})
    assert loaded.experimental_editor_surface == "default"


def test_combo_offers_quill_richedit_surface() -> None:
    choices = dict(_surface_spec().choices)
    assert "richedit_rtf" in choices
    assert "QuillRichEdit" in choices["richedit_rtf"]


def test_explainer_covers_every_surface_choice() -> None:
    # Every combo value must have an Experimental-tab explanation; a missing key
    # silently falls back to the "default" text and users read the wrong one.
    from quill.ui.main_frame import MainFrame

    source = inspect.getsource(MainFrame._build_experimental_explainer)
    for value, _label in _surface_spec().choices:
        assert f'"{value}": (' in source, f"no explainer text for surface {value!r}"


def test_main_frame_dispatches_richedit_rtf_surface() -> None:
    from quill.ui.main_frame import MainFrame

    source = inspect.getsource(MainFrame._create_document_tab)
    assert 'kind == "richedit_rtf"' in source
    assert "create_richedit_rtf" in source


def test_factory_falls_back_and_tags_surface_kind() -> None:
    # Mirror of the win32/rtf/stc defensive pattern: any hosting failure returns
    # a plain control, and a successful build carries surface_kind + wrapper.
    import quill.ui.richedit_rtf_surface as mod

    assert callable(mod.create_richedit_rtf)
    source = inspect.getsource(mod)
    assert "TE_RICH2" in source and "TE_NOHIDESEL" in source
    assert "surface_kind = SURFACE_KIND" in source
    assert "QuillRichEdit(surface)" in source
    # Fallback to a stock TextCtrl on failure.
    assert "return wx_module.TextCtrl(parent, style=style)" in source


def test_phase0_boundaries_are_honest() -> None:
    # Phase 0 is the native control only: RTF I/O must not silently no-op.
    import quill.ui.richedit_rtf_surface as mod

    class _FakeSurface:
        def GetHandle(self) -> int:  # noqa: N802 - wx API shape
            return 0

    wrapper = mod.QuillRichEdit(_FakeSurface())
    assert wrapper.rtf_streaming_available() is False
    caps = wrapper.capabilities()
    assert caps["phase"] == 0 and caps["native_control"] is True
    assert caps["rtf_load"] is False and caps["rtf_save"] is False

    for method in (wrapper.load_rtf, wrapper.save_rtf):
        try:
            method("whatever.rtf")
        except mod.RichEditRtfUnavailableError:
            pass
        else:  # pragma: no cover - defensive
            raise AssertionError("RTF I/O must raise until Phase 1, not no-op")


def test_diagnostic_summary_carries_no_document_content() -> None:
    import quill.ui.richedit_rtf_surface as mod

    class _FakeSurface:
        def GetHandle(self) -> int:  # noqa: N802
            return 0

    summary = mod.QuillRichEdit(_FakeSurface()).accessibility_diagnostic_summary()
    assert "Win32 class name" in summary
    assert "Document content included: no" in summary
