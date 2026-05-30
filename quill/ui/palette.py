from __future__ import annotations

from quill.core.commands import Command, CommandRegistry
from quill.core.features import FeatureManager
from quill.core.palette import (
    load_palette_usage,
    rank_commands,
    record_palette_usage,
    save_palette_usage,
)


class CommandPaletteDialog:
    def __init__(
        self,
        parent: object,
        command_registry: CommandRegistry,
        feature_manager: FeatureManager | None = None,
    ) -> None:
        import wx

        self._wx = wx
        self._registry = command_registry
        self._features = feature_manager
        self._commands: list[Command] = command_registry.list(feature_manager=feature_manager)
        self._usage = load_palette_usage()
        self._filtered_commands: list[Command] = rank_commands(self._commands, "", self._usage)

        self.dialog = wx.Dialog(
            parent,
            title="Command Palette",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetSize((700, 500))

        root = wx.BoxSizer(wx.VERTICAL)
        self.search = wx.SearchCtrl(self.dialog, style=wx.TE_PROCESS_ENTER)
        self.search.ShowSearchButton(True)
        self.search.SetDescriptiveText("Type command (>, :, ?, ~ prefixes supported)")
        root.Add(self.search, 0, wx.EXPAND | wx.ALL, 8)

        self.status = wx.StaticText(self.dialog, label="")
        root.Add(self.status, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.results = wx.ListBox(self.dialog)
        root.Add(self.results, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        self.dialog.SetSizer(root)

        self.search.Bind(wx.EVT_TEXT, self._on_search_changed)
        self.search.Bind(wx.EVT_TEXT_ENTER, self._on_accept)
        self.results.Bind(wx.EVT_LISTBOX_DCLICK, self._on_accept)
        self.results.Bind(wx.EVT_LISTBOX, self._on_result_selected)
        self.dialog.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

        self._refresh_results()

    def show_modal_and_run(self) -> None:
        self.dialog.CentreOnParent()
        try:
            result = self.dialog.ShowModal()
            if result == self._wx.ID_OK:
                self._run_selected()
        finally:
            self.dialog.Destroy()

    def _on_search_changed(self, _event: object) -> None:
        query = self.search.GetValue()
        self._filtered_commands = rank_commands(self._commands, query, self._usage)
        self._refresh_results()

    def _on_accept(self, _event: object) -> None:
        if self.results.GetCount() == 0:
            return
        self.dialog.EndModal(self._wx.ID_OK)

    def _on_char_hook(self, event: object) -> None:
        key_code = event.GetKeyCode()
        if key_code == self._wx.WXK_ESCAPE:
            self.dialog.EndModal(self._wx.ID_CANCEL)
            return
        if key_code in (self._wx.WXK_RETURN, self._wx.WXK_NUMPAD_ENTER):
            self._on_accept(event)
            return
        if key_code == self._wx.WXK_DOWN and self.results.GetCount() > 0:
            self.results.SetSelection(0)
            self.results.SetFocus()
            self._announce_selected_result()
            return
        if key_code == self._wx.WXK_UP and self.results.GetCount() > 0:
            self.results.SetSelection(self.results.GetCount() - 1)
            self.results.SetFocus()
            self._announce_selected_result()
            return
        event.Skip()

    def _refresh_results(self) -> None:
        labels = []
        for command in self._filtered_commands:
            if command.keybinding:
                labels.append(f"{command.title} [{command.keybinding}]")
            else:
                labels.append(command.title)
        self.results.Set(labels)
        if labels:
            self.results.SetSelection(0)
            top = self._filtered_commands[0]
            self.status.SetLabel(
                f"{len(labels)} command(s). Top match: {top.title} ({top.id})"
            )
            return
        self.status.SetLabel("No matching commands")

    def _on_result_selected(self, _event: object) -> None:
        self._announce_selected_result()

    def _announce_selected_result(self) -> None:
        selected = self.results.GetSelection()
        if selected == self._wx.NOT_FOUND:
            return
        if selected < 0 or selected >= len(self._filtered_commands):
            return
        command = self._filtered_commands[selected]
        self.status.SetLabel(f"Selected: {command.title} ({command.id})")
    def _run_selected(self) -> None:
        selected = self.results.GetSelection()
        if selected == self._wx.NOT_FOUND:
            return
        command = self._filtered_commands[selected]
        self._registry.run(command.id)
        self._usage = record_palette_usage(self._usage, command.id)
        save_palette_usage(self._usage)
