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


class _FakeSurface:
    """A surface with no real native handle (hwnd 0), for boundary tests."""

    def __init__(self, value: str = "") -> None:
        self._value = value

    def GetHandle(self) -> int:  # noqa: N802 - wx API shape
        return 0

    def GetValue(self) -> str:  # noqa: N802
        return self._value


def test_stream_in_pump_chunks_and_reports_done() -> None:
    import quill.ui.richedit_rtf_surface as mod

    pump = mod._StreamInPump(b"hello world")
    assert pump.read(5) == b"hello"
    assert pump.done is False
    assert pump.read(100) == b" world"  # returns only what's left
    assert pump.done is True
    assert pump.read(10) == b""  # EOF
    assert mod._StreamInPump(b"").done is True


def test_stream_out_sink_accumulates_bytes() -> None:
    import quill.ui.richedit_rtf_surface as mod

    sink = mod._StreamOutSink()
    sink.write(b"{\\rtf1 ")
    sink.write(b"")  # empty chunks ignored
    sink.write(b"hi}")
    assert sink.getvalue() == b"{\\rtf1 hi}"


def test_rtf_streaming_is_gated_off_never_crashes() -> None:
    # On-device testing found the ctypes EDITSTREAM callback hard-crashes msftedit,
    # so streaming is gated off (_NATIVE_STREAM_CALLBACK_BLOCKED). RTF I/O must
    # RAISE a clear error -- never invoke the crashing native path, never no-op.
    import quill.ui.richedit_rtf_surface as mod

    assert mod._NATIVE_STREAM_CALLBACK_BLOCKED is True

    wrapper = mod.QuillRichEdit(_FakeSurface("plain text here"))
    assert wrapper.rtf_streaming_available() is False  # gated off
    caps = wrapper.capabilities()
    assert caps["rtf_load"] is False and caps["rtf_save"] is False
    assert "gated off" in caps["notes"].lower() or "crash" in caps["notes"].lower()

    calls = (lambda: wrapper.load_rtf("x.rtf"), lambda: wrapper.save_rtf("x.rtf"), wrapper.get_rtf)
    for call in calls:
        try:
            call()
        except (mod.RichEditRtfUnavailableError, mod.RichEditRtfError):
            pass
        else:  # pragma: no cover - defensive
            raise AssertionError("gated-off RTF I/O must raise, not run the crashing path")

    ok, detail = wrapper.self_test_rtf_roundtrip()
    assert ok is False and isinstance(detail, str)  # reports, never raises
    # Plain-text extraction still works for search/spell/AI/read-aloud.
    assert wrapper.get_plain_text() == "plain text here"


def test_diagnostic_reports_the_gating() -> None:
    import quill.ui.richedit_rtf_surface as mod

    summary = mod.QuillRichEdit(_FakeSurface()).accessibility_diagnostic_summary()
    assert "gated off" in summary.lower()


def test_formatting_is_the_phase2_stub() -> None:
    import quill.ui.richedit_rtf_surface as mod

    wrapper = mod.QuillRichEdit(_FakeSurface())
    try:
        wrapper.apply_bold()
    except mod.RichEditRtfUnavailableError:
        pass
    else:  # pragma: no cover - defensive
        raise AssertionError("formatting must raise until Phase 2")


def test_load_save_stream_the_native_messages() -> None:
    # The RTF path drives the documented Rich Edit stream messages, not wx LoadFile.
    import inspect

    import quill.ui.richedit_rtf_surface as mod

    source = inspect.getsource(mod)
    assert "_EM_STREAMIN" in source and "_EM_STREAMOUT" in source
    assert "EDITSTREAM" in source and "SendMessageW" in source
    assert "_SF_RTF" in source


def test_diagnostic_summary_carries_no_document_content() -> None:
    import quill.ui.richedit_rtf_surface as mod

    class _FakeSurface:
        def GetHandle(self) -> int:  # noqa: N802
            return 0

    summary = mod.QuillRichEdit(_FakeSurface()).accessibility_diagnostic_summary()
    assert "Win32 class name" in summary
    assert "Document content included: no" in summary
