"""Guided Action Builder — users define their own AI Action in plain language.

The friendly, no-syntax front door to QUILL's Skill/Agent continuum (the descendant
of BITS Whisperer's Agent Builder). A user gives their action a name, optionally
starts from a Transcript Action preset, writes what they want in plain language, and
saves — and it becomes a real, runnable, Promotable Skill in the AI Library, with no
``.sqp`` syntax in sight.

Saving goes through :func:`quill.core.ai.transcript_actions.action_to_skill_source`
and :class:`~quill.core.skill_store.SkillStore`, so the new action immediately gains
Run / Edit / Enable / Export / Promote for free. ``Preview`` is delegated to an
optional host callback so the dialog stays wx-light and testable.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import wx

from quill.core.ai.transcript_actions import BUILTIN_TRANSCRIPT_ACTIONS, action_to_skill_source
from quill.ui.dialog_contract import apply_modal_ids, show_message_box

_BLANK = "Blank (write my own)"


class ActionBuilderDialog:
    """Build an AI Action: name + plain-language instructions -> a saved Skill."""

    def __init__(
        self,
        parent: object,
        skill_store: Any,
        *,
        announce_cb: Callable[[str], None] | None = None,
        on_preview: Callable[[str, str], None] | None = None,
    ) -> None:
        self._skills = skill_store
        self._announce = announce_cb or (lambda _m: None)
        self._on_preview = on_preview
        self._saved: Any | None = None

        self.dialog = wx.Dialog(
            parent,
            title="Build an AI Action",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetMinSize(wx.Size(560, 480))
        root = wx.BoxSizer(wx.VERTICAL)

        intro = wx.StaticText(
            self.dialog,
            label=(
                "Describe what you want QUILL to do, in your own words. Start from an "
                "example or a blank page. Your action is saved as a Skill you can run, "
                "adjust, and share."
            ),
        )
        intro.Wrap(520)
        root.Add(intro, 0, wx.ALL, 8)

        # Name
        name_row = wx.BoxSizer(wx.HORIZONTAL)
        name_row.Add(
            wx.StaticText(self.dialog, label="&Name:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4
        )
        self._name = wx.TextCtrl(self.dialog)
        self._name.SetName("Action name")
        name_row.Add(self._name, 1)
        root.Add(name_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        # Start from
        start_row = wx.BoxSizer(wx.HORIZONTAL)
        start_row.Add(
            wx.StaticText(self.dialog, label="&Start from:"),
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
            4,
        )
        self._preset = wx.Choice(
            self.dialog, choices=[_BLANK, *[a.name for a in BUILTIN_TRANSCRIPT_ACTIONS]]
        )
        self._preset.SetName("Start from a template")
        self._preset.SetSelection(0)
        start_row.Add(self._preset, 1)
        root.Add(start_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        # Instructions
        root.Add(
            wx.StaticText(self.dialog, label="&Instructions (plain language):"),
            0,
            wx.LEFT | wx.RIGHT,
            8,
        )
        self._instructions = wx.TextCtrl(self.dialog, style=wx.TE_MULTILINE | wx.TE_RICH2)
        self._instructions.SetName("Action instructions")
        root.Add(self._instructions, 1, wx.EXPAND | wx.ALL, 8)

        self._status = wx.StaticText(self.dialog, label="")
        self._status.SetName("Action builder status")
        root.Add(self._status, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        # Buttons
        btns = wx.BoxSizer(wx.HORIZONTAL)
        self._preview_btn = wx.Button(self.dialog, label="&Preview")
        save_btn = wx.Button(self.dialog, wx.ID_OK, label="&Save Action")
        cancel_btn = wx.Button(self.dialog, wx.ID_CANCEL, label="Ca&ncel")
        if self._on_preview is not None:
            btns.Add(self._preview_btn, 0, wx.RIGHT, 6)
        else:
            self._preview_btn.Hide()
        btns.AddStretchSpacer()
        btns.Add(save_btn, 0, wx.RIGHT, 6)
        btns.Add(cancel_btn, 0)
        root.Add(btns, 0, wx.EXPAND | wx.ALL, 8)

        self.dialog.SetSizer(root)
        self.dialog.Layout()
        apply_modal_ids(self.dialog, affirmative_id=wx.ID_OK, affirmative_label="Save Action")

        self._preset.Bind(wx.EVT_CHOICE, self._on_preset)
        self._preview_btn.Bind(wx.EVT_BUTTON, self._on_preview_clicked)
        save_btn.Bind(wx.EVT_BUTTON, self._on_save)
        self._name.SetFocus()

    # -- lifecycle ------------------------------------------------------------

    def show(self) -> int:
        return self.dialog.ShowModal()

    def close(self) -> None:
        self.dialog.Destroy()

    def get_saved(self) -> Any | None:
        """The installed skill created on Save, or None if cancelled."""
        return self._saved

    # -- behavior -------------------------------------------------------------

    def _set_status(self, message: str) -> None:
        self._status.SetLabel(message)
        if message:
            self._announce(message)

    def _on_preset(self, _event: object) -> None:
        idx = self._preset.GetSelection()
        if idx <= 0:
            return
        action = BUILTIN_TRANSCRIPT_ACTIONS[idx - 1]
        self._instructions.SetValue(action.instruction)
        if not self._name.GetValue().strip():
            self._name.SetValue(f"My {action.name}")

    def _values(self) -> tuple[str, str]:
        return self._name.GetValue().strip(), self._instructions.GetValue().strip()

    def _on_preview_clicked(self, _event: object) -> None:
        if self._on_preview is None:
            return
        name, instruction = self._values()
        if not instruction:
            self._set_status("Write some instructions to preview.")
            return
        self._on_preview(name or "Preview", instruction)

    def _on_save(self, _event: object) -> None:
        name, instruction = self._values()
        if not name or not instruction:
            self._set_status("Give your action a name and some instructions first.")
            return
        try:
            source = action_to_skill_source(name, instruction)
            self._saved = self._skills.add_source(source)
        except Exception as exc:  # noqa: BLE001
            show_message_box(
                f"Could not save the action: {exc}",
                "Build an AI Action",
                wx.OK | wx.ICON_ERROR,
                self.dialog,
                announce=self._announce,
            )
            return
        self._announce(f"Saved action: {name}")
        if self.dialog.IsModal():
            self.dialog.EndModal(wx.ID_OK)
