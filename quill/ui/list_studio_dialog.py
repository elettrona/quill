"""Structured List Studio dialog (accessible wx shell over quill.core.lists).

A thin, fully keyboard-operable ``wx.Dialog`` that lets the user build or edit a
list by working with *concepts* — item text, term, definition, checked state —
while ``quill.core.lists`` does the real work of interpreting input and
generating Markdown/HTML source. The dialog never asks the user to type ``-``,
``1.``, ``[ ]``, ``<ul>``, or ``<dl>``; it shows the generated source read-only
as a live preview (PRD §2.1, §23). All list logic lives in core and is unit
tested there, so this module stays a wiring layer.
"""

from __future__ import annotations

from typing import Any

from quill.core.lists import (
    DefinitionEntry,
    DefinitionList,
    FlatList,
    ListItem,
    ListType,
    StructuredListSettings,
    definition_entry_announcement,
    flat_item_announcement,
    list_summary,
    render_html,
    render_markdown,
)
from quill.core.lists.render import DefinitionProfileError

_TYPE_CHOICES: list[tuple[str, ListType]] = [
    ("Bulleted", ListType.BULLET),
    ("Numbered", ListType.ORDERED),
    ("Checklist", ListType.CHECKLIST),
    ("Definition list", ListType.DEFINITION),
]


class ListStudioDialog:
    """Builds the dialog and exposes the generated source after OK.

    Usage (the caller owns the ``wx.Dialog`` so the accessible show path and
    ``apply_modal_ids`` live together in one scope, matching List Manager)::

        dlg = wx.Dialog(frame, title="Structured List Studio", style=...)
        studio = ListStudioDialog(wx, flat=model, settings=cfg, target_format="markdown")
        studio.populate(dlg)
        apply_modal_ids(dlg, affirmative_id=wx.ID_OK, ...)
        if show_modal(dlg) == wx.ID_OK:
            new_source = studio.result_source

    The caller passes whichever model it has (``flat`` or ``definition``); the
    other is created empty and the user can switch types in the dialog.
    """

    def __init__(
        self,
        wx: Any,
        *,
        flat: FlatList | None = None,
        definition: DefinitionList | None = None,
        settings: StructuredListSettings | None = None,
        target_format: str = "markdown",
    ) -> None:
        self._wx = wx
        self._settings = settings if settings is not None else StructuredListSettings()
        self._flat = flat if flat is not None else FlatList(items=[ListItem("")])
        self._definition = (
            definition if definition is not None else DefinitionList(entries=[DefinitionEntry()])
        )
        self._format = target_format if target_format in {"markdown", "html"} else "markdown"
        self._type: ListType = self._flat.list_type if definition is None else ListType.DEFINITION
        if definition is not None:
            self._type = ListType.DEFINITION
        self._suppress = False
        self.result_source: str = ""
        self.dialog: Any = None
        self._outer_sizer: Any = None

    # -- construction ------------------------------------------------------ #

    def populate(self, dlg: Any) -> Any:
        """Build all controls into the caller-owned ``dlg`` (a ``wx.Dialog``)."""
        wx = self._wx
        self.dialog = dlg
        outer = wx.BoxSizer(wx.VERTICAL)

        # Type + format row.
        top = wx.BoxSizer(wx.HORIZONTAL)
        top.Add(wx.StaticText(dlg, label="List &type:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self._type_choice = wx.Choice(dlg, choices=[label for label, _t in _TYPE_CHOICES])
        self._type_choice.SetSelection(self._type_index())
        self._type_choice.Bind(wx.EVT_CHOICE, self._on_type_changed)
        top.Add(self._type_choice, 0, wx.RIGHT, 18)
        top.Add(wx.StaticText(dlg, label="&Format:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self._format_choice = wx.Choice(dlg, choices=["Markdown", "HTML"])
        self._format_choice.SetSelection(0 if self._format == "markdown" else 1)
        self._format_choice.Bind(wx.EVT_CHOICE, self._on_format_changed)
        top.Add(self._format_choice, 0)
        outer.Add(top, 0, wx.ALL, 10)

        # Outline + editor row.
        middle = wx.BoxSizer(wx.HORIZONTAL)
        left = wx.BoxSizer(wx.VERTICAL)
        self._outline_label = wx.StaticText(dlg, label="&Items:")
        left.Add(self._outline_label, 0, wx.BOTTOM, 4)
        self._outline = wx.ListBox(dlg, style=wx.LB_SINGLE)
        self._outline.Bind(wx.EVT_LISTBOX, self._on_outline_select)
        left.Add(self._outline, 1, wx.EXPAND | wx.BOTTOM, 6)
        left.Add(self._build_outline_buttons(dlg), 0, wx.EXPAND)
        middle.Add(left, 1, wx.EXPAND | wx.RIGHT, 12)

        middle.Add(self._build_editor_panel(dlg), 1, wx.EXPAND)
        outer.Add(middle, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Source preview.
        outer.Add(
            wx.StaticText(dlg, label="Generated &source (read-only):"),
            0,
            wx.LEFT | wx.TOP,
            10,
        )
        self._preview = wx.TextCtrl(
            dlg, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP, size=(-1, 120)
        )
        outer.Add(self._preview, 0, wx.EXPAND | wx.ALL, 10)

        # The OK/Cancel button sizer and apply_modal_ids are added by the caller
        # (in the same scope as the accessible show path), matching List Manager
        # and the dialog hardening/button contracts. _on_ok captures the source.
        dlg.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
        self._outer_sizer = outer
        return outer

    def finalize(self) -> None:
        """Lay out the dialog and load initial content (after the caller adds buttons)."""
        self.dialog.SetSizerAndFit(self._outer_sizer)
        self.dialog.SetSize((760, 620))
        self._sync_type_visibility()
        self._reload_outline(select=0)

    def _build_outline_buttons(self, dlg: Any) -> Any:
        wx = self._wx
        row = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_add = wx.Button(dlg, label="&Add")
        self._btn_remove = wx.Button(dlg, label="&Remove")
        self._btn_up = wx.Button(dlg, label="Move &up")
        self._btn_down = wx.Button(dlg, label="Move &down")
        self._btn_add.Bind(wx.EVT_BUTTON, self._on_add)
        self._btn_remove.Bind(wx.EVT_BUTTON, self._on_remove)
        self._btn_up.Bind(wx.EVT_BUTTON, lambda _e: self._move(-1))
        self._btn_down.Bind(wx.EVT_BUTTON, lambda _e: self._move(1))
        for btn in (self._btn_add, self._btn_remove, self._btn_up, self._btn_down):
            row.Add(btn, 0, wx.RIGHT, 4)
        return row

    def _build_editor_panel(self, dlg: Any) -> Any:
        wx = self._wx
        panel = wx.BoxSizer(wx.VERTICAL)

        # Flat editor (item text + checked).
        self._item_label = wx.StaticText(dlg, label="Item te&xt:")
        panel.Add(self._item_label, 0, wx.BOTTOM, 4)
        self._item_text = wx.TextCtrl(dlg, style=wx.TE_MULTILINE)
        self._item_text.Bind(wx.EVT_TEXT, self._on_item_text)
        panel.Add(self._item_text, 1, wx.EXPAND | wx.BOTTOM, 6)
        self._checked_box = wx.CheckBox(dlg, label="Tas&k is complete")
        self._checked_box.Bind(wx.EVT_CHECKBOX, self._on_checked)
        panel.Add(self._checked_box, 0, wx.BOTTOM, 6)

        # Definition editor (term + definition).
        self._term_label = wx.StaticText(dlg, label="Te&rm:")
        panel.Add(self._term_label, 0, wx.BOTTOM, 4)
        self._term_text = wx.TextCtrl(dlg, style=wx.TE_MULTILINE)
        self._term_text.Bind(wx.EVT_TEXT, self._on_term_text)
        panel.Add(self._term_text, 1, wx.EXPAND | wx.BOTTOM, 6)
        self._def_label = wx.StaticText(dlg, label="&Definition or description:")
        panel.Add(self._def_label, 0, wx.BOTTOM, 4)
        self._def_text = wx.TextCtrl(dlg, style=wx.TE_MULTILINE)
        self._def_text.Bind(wx.EVT_TEXT, self._on_def_text)
        panel.Add(self._def_text, 1, wx.EXPAND)
        return panel

    # -- state helpers ----------------------------------------------------- #

    def _is_definition(self) -> bool:
        return self._type is ListType.DEFINITION

    def _type_index(self) -> int:
        for index, (_label, list_type) in enumerate(_TYPE_CHOICES):
            if list_type is self._type:
                return index
        return 0

    def _sync_type_visibility(self) -> None:
        definition = self._is_definition()
        for control in (self._term_label, self._term_text, self._def_label, self._def_text):
            control.Show(definition)
        for control in (self._item_label, self._item_text):
            control.Show(not definition)
        self._checked_box.Show(not definition and self._type is ListType.CHECKLIST)
        self._outline_label.SetLabel("&Entries:" if definition else "&Items:")
        if self.dialog is not None:
            self.dialog.Layout()

    # -- outline ----------------------------------------------------------- #

    def _reload_outline(self, *, select: int | None = None) -> None:
        self._suppress = True
        try:
            self._outline.Clear()
            if self._is_definition():
                for index in range(len(self._definition.entries)):
                    self._outline.Append(self._entry_label(index))
                count = len(self._definition.entries)
            else:
                for index in range(len(self._flat.items)):
                    self._outline.Append(self._item_label_text(index))
                count = len(self._flat.items)
            if count:
                target = 0 if select is None else max(0, min(select, count - 1))
                self._outline.SetSelection(target)
        finally:
            self._suppress = False
        self._load_selected_into_fields()
        self._refresh_preview()

    def _item_label_text(self, index: int) -> str:
        return flat_item_announcement(self._flat, index, self._settings) or "(empty)"

    def _entry_label(self, index: int) -> str:
        return definition_entry_announcement(self._definition, index, self._settings) or "(empty)"

    def _selected_index(self) -> int:
        sel = self._outline.GetSelection()
        return sel if sel is not None and sel >= 0 else -1

    def _load_selected_into_fields(self) -> None:
        index = self._selected_index()
        self._suppress = True
        try:
            if self._is_definition():
                entry = self._definition.entries[index] if index >= 0 else DefinitionEntry()
                self._term_text.SetValue(entry.primary_term)
                self._def_text.SetValue(entry.primary_definition)
            else:
                item = self._flat.items[index] if index >= 0 else ListItem("")
                self._item_text.SetValue(item.text)
                self._checked_box.SetValue(item.checked)
        finally:
            self._suppress = False

    # -- event handlers ---------------------------------------------------- #

    def _on_type_changed(self, _event: Any) -> None:
        choice = self._type_choice.GetSelection()
        self._type = _TYPE_CHOICES[choice][1]
        if not self._is_definition():
            self._flat.list_type = self._type
        self._sync_type_visibility()
        self._reload_outline(select=0)

    def _on_format_changed(self, _event: Any) -> None:
        self._format = "markdown" if self._format_choice.GetSelection() == 0 else "html"
        self._refresh_preview()

    def _on_outline_select(self, _event: Any) -> None:
        if self._suppress:
            return
        self._load_selected_into_fields()

    def _on_item_text(self, _event: Any) -> None:
        if self._suppress:
            return
        index = self._selected_index()
        if index >= 0:
            self._flat.items[index].text = self._item_text.GetValue()
            self._update_outline_label(index, self._item_label_text(index))
            self._refresh_preview()

    def _on_checked(self, _event: Any) -> None:
        if self._suppress:
            return
        index = self._selected_index()
        if index >= 0:
            self._flat.items[index].checked = self._checked_box.GetValue()
            self._update_outline_label(index, self._item_label_text(index))
            self._refresh_preview()

    def _on_term_text(self, _event: Any) -> None:
        if self._suppress:
            return
        index = self._selected_index()
        if index >= 0:
            self._definition.entries[index].terms[0] = self._term_text.GetValue()
            self._update_outline_label(index, self._entry_label(index))
            self._refresh_preview()

    def _on_def_text(self, _event: Any) -> None:
        if self._suppress:
            return
        index = self._selected_index()
        if index >= 0:
            self._definition.entries[index].definitions[0] = self._def_text.GetValue()
            self._update_outline_label(index, self._entry_label(index))
            self._refresh_preview()

    def _update_outline_label(self, index: int, label: str) -> None:
        self._suppress = True
        try:
            self._outline.SetString(index, label)
        finally:
            self._suppress = False

    def _on_add(self, _event: Any) -> None:
        index = self._selected_index()
        if self._is_definition():
            at = index + 1 if index >= 0 else len(self._definition.entries)
            self._definition.entries.insert(at, DefinitionEntry())
        else:
            at = index + 1 if index >= 0 else len(self._flat.items)
            self._flat.items.insert(at, ListItem(""))
        self._reload_outline(select=at)

    def _on_remove(self, _event: Any) -> None:
        index = self._selected_index()
        if index < 0:
            return
        collection = self._definition.entries if self._is_definition() else self._flat.items
        if len(collection) <= 1:
            collection[0] = DefinitionEntry() if self._is_definition() else ListItem("")
            self._reload_outline(select=0)
            return
        del collection[index]
        self._reload_outline(select=min(index, len(collection) - 1))

    def _move(self, delta: int) -> None:
        index = self._selected_index()
        if index < 0:
            return
        collection: list[Any] = (
            self._definition.entries if self._is_definition() else self._flat.items  # type: ignore[assignment]
        )
        target = index + delta
        if target < 0 or target >= len(collection):
            return
        collection[index], collection[target] = collection[target], collection[index]
        self._reload_outline(select=target)

    # -- preview + commit -------------------------------------------------- #

    def _current_model(self) -> FlatList | DefinitionList:
        return self._definition if self._is_definition() else self._flat

    def _refresh_preview(self) -> None:
        try:
            source = self._render()
            self._preview.SetValue(source)
        except DefinitionProfileError as exc:
            self._preview.SetValue(f"{exc}\n\nChoose HTML format, or configure a Markdown profile.")

    def _render(self) -> str:
        model = self._current_model()
        if self._format == "html":
            return render_html(model, self._settings)
        return render_markdown(model, self._settings)

    def _on_ok(self, event: Any) -> None:
        try:
            self.result_source = self._render()
        except DefinitionProfileError:
            # Definition Markdown needs a profile; fall back to embedded HTML so the
            # user is never blocked, matching the PRD's safe portable default (§21.3).
            self.result_source = render_html(self._current_model(), self._settings)
        event.Skip()  # let the dialog close with ID_OK

    @property
    def summary(self) -> str:
        return list_summary(self._current_model(), self._settings)
