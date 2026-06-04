from __future__ import annotations

from quill.core.document import Document
from quill.ui.main_frame import MainFrame


class _PlainEditor:
    """Stand-in for the plain wx.TextCtrl surface (advertises no toggle_mode)."""


class _RichEditor:
    """Stand-in for RichTextSurface: advertises surface_kind=='rich' + toggle_mode."""

    def __init__(self) -> None:
        self.toggles = 0

    def surface_kind(self) -> str:
        return "rich"

    def toggle_mode(self) -> str:
        self.toggles += 1
        return "Markdown lens" if self.toggles % 2 else "Rich text lens"


def _build_frame(editor: object, *, editor_surface: str = "plain") -> MainFrame:
    frame = MainFrame.__new__(MainFrame)
    frame.editor = editor
    frame.settings = type("S", (), {"editor_surface": editor_surface})()
    frame._status_message = "Ready"
    frame._set_status = lambda message: setattr(frame, "_status_message", message)
    return frame


def test_rich_editor_enabled_reads_setting() -> None:
    assert _build_frame(_PlainEditor(), editor_surface="rich")._rich_editor_enabled() is True
    assert _build_frame(_PlainEditor(), editor_surface="plain")._rich_editor_enabled() is False


def test_switch_editing_lens_toggles_rich_surface() -> None:
    editor = _RichEditor()
    frame = _build_frame(editor, editor_surface="rich")

    frame.switch_editing_lens()

    assert editor.toggles == 1
    assert frame._status_message == "Markdown lens"


def test_switch_editing_lens_plain_surface_with_rich_off_explains_setting() -> None:
    frame = _build_frame(_PlainEditor(), editor_surface="plain")

    frame.switch_editing_lens()

    assert "Settings" in frame._status_message


def test_switch_editing_lens_plain_surface_with_rich_on_reports_markdown_lens() -> None:
    frame = _build_frame(_PlainEditor(), editor_surface="rich")

    frame.switch_editing_lens()

    assert "Markdown lens" in frame._status_message


def test_announce_rtf_safety_reports_blocked_and_warnings() -> None:
    frame = _build_frame(_PlainEditor(), editor_surface="rich")
    document = Document(path=None, text="")
    document.source_metadata.update({
        "rtf_blocked": ["embedded object"],
        "rtf_warnings": ["remote field INCLUDEPICTURE"],
    })

    frame._announce_rtf_safety(document)

    assert "Rich text lens" in frame._status_message
    assert "embedded object" in frame._status_message
    assert "INCLUDEPICTURE" in frame._status_message
