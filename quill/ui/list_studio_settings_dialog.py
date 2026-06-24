"""Structured List Studio settings surface (PRD §3–§13).

An accessible, keyboard-operable settings dialog over the wx-free
``quill.core.lists.settings``: pick a shipped preset, tweak the high-value knobs,
and export/import the configuration as JSON. The caller owns the ``wx.Dialog`` so
the hardened modal path and ``apply_modal_ids`` live in one scope (matching
``ListStudioDialog``); on OK the resolved :class:`StructuredListSettings` is
exposed as ``result_settings`` for the caller to persist app-wide (app scope).
"""

from __future__ import annotations

from typing import Any

from quill.core.lists import (
    DefinitionMarkdownProfile,
    StructuredListSettings,
    list_studio_presets,
)

_VERBOSITY = [("Concise", "concise"), ("Standard", "standard"), ("Detailed", "detailed")]
_PROFILES = [
    ("Ask each time", DefinitionMarkdownProfile.ASK),
    ("Pandoc ( term / : definition )", DefinitionMarkdownProfile.PANDOC),
    ("Markdown Extra", DefinitionMarkdownProfile.MARKDOWN_EXTRA),
    ("MultiMarkdown", DefinitionMarkdownProfile.MULTIMARKDOWN),
    ("Embedded HTML <dl>", DefinitionMarkdownProfile.HTML_FALLBACK),
    ("Plain 'Term: Definition'", DefinitionMarkdownProfile.PLAIN_FALLBACK),
    ("Disabled", DefinitionMarkdownProfile.DISABLED),
]
_BULLETS = [("Dash -", "-"), ("Asterisk *", "*"), ("Plus +", "+")]
_DELIMITERS = [("Period .", "."), ("Parenthesis )", ")")]


class ListStudioSettingsDialog:
    """Builds the settings controls and exposes the chosen settings after OK."""

    def __init__(self, wx: Any, *, settings: StructuredListSettings | None = None) -> None:
        self._wx = wx
        self._settings = settings if settings is not None else StructuredListSettings()
        self.result_settings: StructuredListSettings | None = None
        self.dialog: Any = None
        self._outer_sizer: Any = None

    # -- construction ------------------------------------------------------ #

    def populate(self, dlg: Any) -> Any:
        wx = self._wx
        self.dialog = dlg
        outer = wx.BoxSizer(wx.VERTICAL)

        grid = wx.FlexGridSizer(0, 2, 8, 10)
        grid.AddGrowableCol(1, 1)

        def _add(label_text: str, control: Any) -> None:
            grid.Add(wx.StaticText(dlg, label=label_text), 0, wx.ALIGN_CENTER_VERTICAL)
            grid.Add(control, 0, wx.EXPAND)

        self._preset_choice = wx.Choice(dlg, choices=["(Custom)", *list_studio_presets().keys()])
        self._preset_choice.SetSelection(0)
        self._preset_choice.Bind(wx.EVT_CHOICE, self._on_preset_chosen)
        _add("Start from &preset:", self._preset_choice)

        self._verbosity_choice = wx.Choice(dlg, choices=[label for label, _v in _VERBOSITY])
        _add("Announcement &verbosity:", self._verbosity_choice)

        self._profile_choice = wx.Choice(dlg, choices=[label for label, _p in _PROFILES])
        _add("&Definition list Markdown:", self._profile_choice)

        self._bullet_choice = wx.Choice(dlg, choices=[label for label, _b in _BULLETS])
        _add("&Bullet marker:", self._bullet_choice)

        self._delimiter_choice = wx.Choice(dlg, choices=[label for label, _d in _DELIMITERS])
        _add("&Numbered list delimiter:", self._delimiter_choice)

        self._loose_box = wx.CheckBox(dlg, label="&Loose Markdown lists (blank line between items)")
        grid.Add((0, 0))
        grid.Add(self._loose_box, 0, wx.EXPAND)

        self._task_checked_box = wx.CheckBox(dlg, label="New &tasks start checked")
        grid.Add((0, 0))
        grid.Add(self._task_checked_box, 0, wx.EXPAND)

        outer.Add(grid, 0, wx.EXPAND | wx.ALL, 12)

        io_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_export = wx.Button(dlg, label="&Export...")
        btn_import = wx.Button(dlg, label="&Import...")
        btn_export.Bind(wx.EVT_BUTTON, lambda _e: self._on_export())
        btn_import.Bind(wx.EVT_BUTTON, lambda _e: self._on_import())
        io_row.Add(btn_export, 0, wx.RIGHT, 6)
        io_row.Add(btn_import, 0)
        outer.Add(io_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        dlg.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
        self._outer_sizer = outer
        return outer

    def finalize(self) -> None:
        self.dialog.SetSizerAndFit(self._outer_sizer)
        self._load_settings_into_controls(self._settings)

    # -- control <-> model ------------------------------------------------- #

    def _load_settings_into_controls(self, settings: StructuredListSettings) -> None:
        self._verbosity_choice.SetSelection(_index_of(_VERBOSITY, settings.verbosity, 1))
        self._profile_choice.SetSelection(
            _index_of(_PROFILES, settings.definition_markdown_profile, 0)
        )
        self._bullet_choice.SetSelection(_index_of(_BULLETS, settings.bullet_marker, 0))
        self._delimiter_choice.SetSelection(_index_of(_DELIMITERS, settings.ordered_delimiter, 0))
        self._loose_box.SetValue(settings.markdown_loose)
        self._task_checked_box.SetValue(settings.new_task_checked)

    def _settings_from_controls(self) -> StructuredListSettings:
        # Start from the incoming settings so fields without a control are kept.
        settings = StructuredListSettings.from_dict(self._settings.to_dict())
        settings.verbosity = _VERBOSITY[max(0, self._verbosity_choice.GetSelection())][1]
        settings.definition_markdown_profile = _PROFILES[
            max(0, self._profile_choice.GetSelection())
        ][1]
        settings.bullet_marker = _BULLETS[max(0, self._bullet_choice.GetSelection())][1]
        settings.ordered_delimiter = _DELIMITERS[max(0, self._delimiter_choice.GetSelection())][1]
        settings.markdown_loose = self._loose_box.GetValue()
        settings.new_task_checked = self._task_checked_box.GetValue()
        return settings

    # -- events ------------------------------------------------------------ #

    def _on_preset_chosen(self, _event: Any) -> None:
        index = self._preset_choice.GetSelection()
        if index <= 0:
            return  # "(Custom)" — leave the controls as-is
        presets = list(list_studio_presets().values())
        if index - 1 < len(presets):
            self._load_settings_into_controls(presets[index - 1])

    def _on_export(self) -> None:
        import json

        wx = self._wx
        with wx.FileDialog(
            self.dialog,
            "Export List Studio settings",
            wildcard="JSON files (*.json)|*.json",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:  # GATE-42-OK: native wx.FileDialog
                return
            path = dlg.GetPath()
        from pathlib import Path

        try:
            Path(path).write_text(
                json.dumps(self._settings_from_controls().to_dict(), indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def _on_import(self) -> None:
        import json

        wx = self._wx
        with wx.FileDialog(
            self.dialog,
            "Import List Studio settings",
            wildcard="JSON files (*.json)|*.json|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:  # GATE-42-OK: native wx.FileDialog
                return
            path = dlg.GetPath()
        from pathlib import Path

        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        self._load_settings_into_controls(StructuredListSettings.from_dict(data))
        self._preset_choice.SetSelection(0)  # imported values are "(Custom)"

    def _on_ok(self, event: Any) -> None:
        self.result_settings = self._settings_from_controls()
        event.Skip()  # let the dialog close with ID_OK


def _index_of(options: list, value: object, default: int) -> int:
    for index, (_label, candidate) in enumerate(options):
        if candidate == value:
            return index
    return default
