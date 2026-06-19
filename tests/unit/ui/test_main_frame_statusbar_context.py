from __future__ import annotations

import pytest

from quill.core.settings import Settings
from quill.ui.main_frame import MainFrame, _StatusBarCell


class _MenuItem:
    def __init__(self, item_id: int, label: str) -> None:
        self.item_id = item_id
        self.label = label
        self.enabled = True

    def Enable(self, enabled: bool) -> None:
        self.enabled = enabled


class _Menu:
    def __init__(self) -> None:
        self.items: list[_MenuItem] = []
        self.bindings: dict[int, object] = {}

    def Append(self, item_id: int, label: str) -> _MenuItem:
        item = _MenuItem(item_id, label)
        self.items.append(item)
        return item

    def Bind(self, _event: object, handler: object, id: int) -> None:
        self.bindings[id] = handler

    def FindItemById(self, item_id: int) -> _MenuItem | None:
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None


class _Wx:
    EVT_MENU = object()

    def __init__(self) -> None:
        self._next_id = 1000

    def Menu(self) -> _Menu:
        return _Menu()

    def NewIdRef(self) -> int:
        self._next_id += 1
        return self._next_id


@pytest.fixture()
def frame() -> MainFrame:
    frame = MainFrame.__new__(MainFrame)
    frame._wx = _Wx()
    frame.settings = Settings()
    frame.statusbar = object()
    frame._status_message = ""
    frame._statusbar_cells = [_StatusBarCell(item="line_column", button=object())]
    frame._set_status = lambda message: setattr(frame, "_status_message", message)  # type: ignore[method-assign]
    frame._apply_statusbar_layout = lambda: None  # type: ignore[method-assign]
    frame._activate_statusbar_cell = lambda _item: None  # type: ignore[method-assign]
    frame.open_status_bar_settings = lambda: None  # type: ignore[method-assign]
    frame._popup_context_menu = lambda *_args, **_kwargs: None  # type: ignore[method-assign]
    return frame


def test_hide_statusbar_cell_updates_hidden_items(
    frame: MainFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("quill.ui.main_frame.save_settings", lambda _settings: None)
    frame._hide_statusbar_cell("word_count")
    assert "word_count" in frame.settings.status_bar_hidden


def test_hide_statusbar_cell_does_not_hide_message(frame: MainFrame) -> None:
    frame._hide_statusbar_cell("message")
    assert "message" not in frame.settings.status_bar_hidden
    assert frame._status_message == "Status Message cannot be hidden"


def test_restore_default_statusbar_layout_uses_settings_defaults(frame: MainFrame) -> None:
    frame.settings.status_bar_order = ["word_count", "message"]
    frame.settings.status_bar_hidden = ["line_column"]
    frame._restore_default_statusbar_layout()
    defaults = Settings()
    assert frame.settings.status_bar_order == defaults.status_bar_order
    assert frame.settings.status_bar_hidden == defaults.status_bar_hidden


def test_statusbar_cell_context_menu_offers_required_actions(frame: MainFrame) -> None:
    captured: dict[str, object] = {}
    activated: list[str] = []
    hidden: list[str] = []
    opened: list[str] = []

    def capture_popup(target: object, menu: _Menu, _event: object) -> None:
        captured["target"] = target
        captured["menu"] = menu

    frame._popup_context_menu = capture_popup  # type: ignore[method-assign]
    frame._activate_statusbar_cell = lambda item: activated.append(item)  # type: ignore[method-assign]
    frame._hide_statusbar_cell = lambda item: hidden.append(item)  # type: ignore[method-assign]
    frame.open_status_bar_settings = lambda: opened.append("settings")  # type: ignore[method-assign]

    frame._on_statusbar_cell_context_menu(object(), "line_column")

    menu = captured["menu"]
    assert isinstance(menu, _Menu)
    labels = [item.label for item in menu.items]
    assert labels == ["Activate", "Hide this item", "Status bar settings..."]
    assert captured["target"] is frame._statusbar_cells[0].button

    for item in menu.items:
        handler = menu.bindings[item.item_id]
        handler(None)  # type: ignore[misc]
    assert activated == ["line_column"]
    assert hidden == ["line_column"]
    assert opened == ["settings"]


class _DeadButton:
    """Stand-in for a wx button whose C++ object has been destroyed.

    Every wx attribute/method raises RuntimeError, mimicking the
    'wrapped C/C++ object of type ... has been deleted' condition that
    surfaces when ctrl+F4 closes a tab while a caret event is still
    in the queue (#269)."""

    def __getattr__(self, _name: str) -> object:  # pragma: no cover - always raises
        raise RuntimeError("wrapped C/C++ object of type TextCtrl has been deleted")


class _LiveButton:
    def __init__(self) -> None:
        self.label = ""
        self.help_text = ""
        self.name = ""
        self.min_size: tuple[int, int] | None = None

    def SetLabel(self, label: str) -> None:
        self.label = label

    def SetHelpText(self, text: str) -> None:
        self.help_text = text

    def SetName(self, name: str) -> None:
        self.name = name

    def SetMinSize(self, size: tuple[int, int]) -> None:
        self.min_size = size


def test_refresh_statusbar_skips_dead_widget_cell(frame: MainFrame) -> None:
    """#269: ctrl+F4 leaves a dead C++ button behind; _refresh_statusbar must
    skip it instead of crashing the whole statusbar refresh."""

    live = _LiveButton()
    dead = _DeadButton()
    frame._statusbar_cells = [
        _StatusBarCell(item="file_path", button=dead),
        _StatusBarCell(item="line_column", button=live),
    ]

    class _Statusbar:
        def Layout(self) -> None:
            pass

    frame.statusbar = _Statusbar()

    # No exception should bubble out, even though the first cell's button is
    # already destroyed at the C++ layer.
    frame._refresh_statusbar()

    # The live cell still gets its label written (skipped cells do not).
    assert live.label != ""


def test_statusbar_text_for_item_returns_empty_when_editor_is_dead() -> None:
    """#269: closing a tab can leave self.editor pointing at a destroyed
    C++ TextCtrl. _statusbar_text_for_item must return an empty string
    instead of letting the RuntimeError crash the statusbar refresh."""

    frame = MainFrame.__new__(MainFrame)
    frame._wx = _Wx()
    frame.settings = Settings()
    frame._status_message = "Ready"
    frame._read_aloud = None
    frame._notifications = []
    frame._autosave_interval = None  # type: ignore[assignment]
    frame.document = None  # type: ignore[assignment]

    class _DeadEditor:
        def GetValue(self) -> str:  # pragma: no cover - always raises
            raise RuntimeError("wrapped C/C++ object of type TextCtrl has been deleted")

        def GetInsertionPoint(self) -> int:  # pragma: no cover - always raises
            raise RuntimeError("wrapped C/C++ object of type TextCtrl has been deleted")

        def GetSelection(self) -> tuple[int, int]:  # pragma: no cover - always raises
            raise RuntimeError("wrapped C/C++ object of type TextCtrl has been deleted")

    frame.editor = _DeadEditor()  # type: ignore[assignment]

    # These three items all read from self.editor; they must all return ""
    # when the underlying C++ object has been deleted.
    assert frame._statusbar_text_for_item("line_column") == ""
    assert frame._statusbar_text_for_item("word_count") == ""
    assert frame._statusbar_text_for_item("selection") == "Sel 0"
