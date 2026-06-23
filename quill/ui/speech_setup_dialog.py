"""Speech Setup dialog — model catalog with live install/state visibility (#669).

Replaces the three-step SingleChoiceDialog chain (engine chooser → flat model
list → action picker) with a single panel that shows every model's current
state, recommended status, and size at a glance.  The user picks one action
and closes; the caller executes it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from quill.ui.dialog_contract import apply_modal_ids

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class SpeechSetupResult:
    """What the dialog wants to happen after it closes."""

    action: str
    """One of: 'download' | 'remove' | 'ffmpeg' | 'engine' | 'hf_token'."""
    model_id: str | None = None
    model_row: object | None = None
    provider_id: str | None = None


class SpeechSetupDialog:
    """Rich speech model manager with full install-state visibility.

    Parameters
    ----------
    parent:
        wx parent window.
    provider:
        A SpeechProvider (has .display_name, .list_installed_models(), ...).
    rows:
        List[ModelRow] from ``service.describe_models()``.
    machine_summary:
        Short string e.g. "Your computer: 16 GB RAM and no GPU."
    ffmpeg_ok:
        Whether ffmpeg is found on this system.
    engine_ok:
        Whether Faster Whisper is installed.
    all_providers:
        All available providers; enables the engine switcher when > 1.
    total_ram:
        Detected RAM in GB (used when repopulating after an engine switch).
    has_gpu:
        Whether a GPU is detected (used when repopulating after a switch).
    """

    def __init__(
        self,
        parent: object,
        *,
        provider: object,
        rows: list,
        machine_summary: str,
        ffmpeg_ok: bool,
        engine_ok: bool,
        all_providers: list,
        total_ram: float = 0.0,
        has_gpu: bool = False,
    ) -> None:
        import wx

        self._wx = wx
        self._provider = provider
        self._rows = rows
        self._machine_summary = machine_summary
        self._ffmpeg_ok = ffmpeg_ok
        self._engine_ok = engine_ok
        self._all_providers = all_providers
        self._total_ram = total_ram
        self._has_gpu = has_gpu
        self._result: SpeechSetupResult | None = None

        self.dialog = wx.Dialog(
            parent,
            title="Manage Speech Models",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetMinSize(wx.Size(560, 460))
        self.dialog.SetSize(wx.Size(700, 540))
        self._build_ui()

    def _build_ui(self) -> None:
        wx = self._wx
        root = wx.BoxSizer(wx.VERTICAL)

        # Engine row — only shown when multiple providers are registered.
        if len(self._all_providers) > 1:
            eng_row = wx.BoxSizer(wx.HORIZONTAL)
            eng_lbl = wx.StaticText(self.dialog, label="Speech &engine:")
            self._engine_choice = wx.Choice(
                self.dialog,
                choices=[p.display_name for p in self._all_providers],
            )
            self._engine_choice.SetName("Speech engine")
            current_idx = next(
                (i for i, p in enumerate(self._all_providers) if p is self._provider),
                0,
            )
            self._engine_choice.SetSelection(current_idx)
            eng_row.Add(eng_lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
            eng_row.Add(self._engine_choice, 1, wx.EXPAND)
            root.Add(eng_row, 0, wx.EXPAND | wx.ALL, 10)
            self._engine_choice.Bind(wx.EVT_CHOICE, self._on_engine_changed)
        else:
            self._engine_choice = None  # type: ignore[assignment]
            eng_lbl = wx.StaticText(
                self.dialog,
                label=f"Engine: {self._provider.display_name}",  # type: ignore[attr-defined]
            )
            root.Add(eng_lbl, 0, wx.ALL, 10)

        # Machine summary.
        self._summary_text = wx.StaticText(self.dialog, label=self._machine_summary)
        root.Add(self._summary_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Dependencies panel.
        dep_box = wx.StaticBoxSizer(wx.StaticBox(self.dialog, label="Dependencies"), wx.VERTICAL)

        ffmpeg_row = wx.BoxSizer(wx.HORIZONTAL)
        ffmpeg_lbl = wx.StaticText(
            self.dialog,
            label="FFmpeg: Installed" if self._ffmpeg_ok else "FFmpeg: Not installed",
        )
        ffmpeg_row.Add(ffmpeg_lbl, 1, wx.ALIGN_CENTER_VERTICAL)
        if not self._ffmpeg_ok:
            self._btn_ffmpeg = wx.Button(self.dialog, label="Download &FFmpeg...")
            self._btn_ffmpeg.Bind(wx.EVT_BUTTON, lambda _e: self._choose("ffmpeg"))
            ffmpeg_row.Add(self._btn_ffmpeg, 0, wx.LEFT, 8)
        dep_box.Add(ffmpeg_row, 0, wx.EXPAND | wx.ALL, 6)

        eng_dep_row = wx.BoxSizer(wx.HORIZONTAL)
        eng_dep_lbl = wx.StaticText(
            self.dialog,
            label=(
                "Faster Whisper: Installed"
                if self._engine_ok
                else "Faster Whisper: Not installed (optional, GPU-accelerated engine)"
            ),
        )
        eng_dep_row.Add(eng_dep_lbl, 1, wx.ALIGN_CENTER_VERTICAL)
        if not self._engine_ok:
            self._btn_engine = wx.Button(self.dialog, label="&Install Faster Whisper...")
            self._btn_engine.Bind(wx.EVT_BUTTON, lambda _e: self._choose("engine"))
            eng_dep_row.Add(self._btn_engine, 0, wx.LEFT, 8)
        dep_box.Add(eng_dep_row, 0, wx.EXPAND | wx.ALL, 6)
        root.Add(dep_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Model list.
        root.Add(
            wx.StaticText(self.dialog, label="&Models (select one, then Download or Remove):"),
            0,
            wx.LEFT | wx.RIGHT,
            10,
        )
        self._model_list = wx.ListBox(self.dialog, style=wx.LB_SINGLE)
        self._model_list.SetName("Models")
        self._model_list.SetMinSize(wx.Size(-1, 140))
        self._populate_model_list()
        root.Add(self._model_list, 1, wx.EXPAND | wx.ALL, 10)

        # Action buttons.
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_download = wx.Button(self.dialog, label="&Download Selected")
        self._btn_remove = wx.Button(self.dialog, label="&Remove Selected")
        btn_hf = wx.Button(self.dialog, label="&Hugging Face Token...")
        btn_close = wx.Button(self.dialog, label="&Close")
        for btn in (self._btn_download, self._btn_remove, btn_hf, btn_close):
            btn_row.Add(btn, 0, wx.RIGHT, 6)
        root.Add(btn_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self._btn_download.Bind(wx.EVT_BUTTON, lambda _e: self._on_download())
        self._btn_remove.Bind(wx.EVT_BUTTON, lambda _e: self._on_remove())
        btn_hf.Bind(wx.EVT_BUTTON, lambda _e: self._choose("hf_token"))
        btn_close.Bind(wx.EVT_BUTTON, lambda _e: self.dialog.EndModal(wx.ID_CLOSE))
        self._model_list.Bind(wx.EVT_LISTBOX, lambda _e: self._update_buttons())

        self._update_buttons()
        apply_modal_ids(
            self.dialog,
            affirmative_id=self._btn_download.GetId(),
            escape_id=btn_close.GetId(),
        )
        self.dialog.SetSizer(root)

    def _populate_model_list(self) -> None:
        self._model_list.Clear()
        for row in self._rows:
            self._model_list.Append(row.label)

    def _update_buttons(self) -> None:
        sel = self._model_list.GetSelection()
        if sel == self._wx.NOT_FOUND or sel >= len(self._rows):
            self._btn_download.Enable(False)
            self._btn_remove.Enable(False)
            return
        installed = bool(getattr(self._rows[sel], "installed", False))
        self._btn_download.Enable(not installed)
        self._btn_remove.Enable(installed)

    def _on_download(self) -> None:
        sel = self._model_list.GetSelection()
        if sel == self._wx.NOT_FOUND or sel >= len(self._rows):
            return
        row = self._rows[sel]
        self._result = SpeechSetupResult(
            action="download",
            model_id=str(getattr(row, "id", "")),
            model_row=row,
            provider_id=getattr(self._provider, "id", None),
        )
        self.dialog.EndModal(self._wx.ID_OK)

    def _on_remove(self) -> None:
        sel = self._model_list.GetSelection()
        if sel == self._wx.NOT_FOUND or sel >= len(self._rows):
            return
        row = self._rows[sel]
        self._result = SpeechSetupResult(
            action="remove",
            model_id=str(getattr(row, "id", "")),
            provider_id=getattr(self._provider, "id", None),
        )
        self.dialog.EndModal(self._wx.ID_OK)

    def _choose(self, action: str) -> None:
        self._result = SpeechSetupResult(
            action=action,
            provider_id=getattr(self._provider, "id", None),
        )
        self.dialog.EndModal(self._wx.ID_OK)

    def _on_engine_changed(self, event: object) -> None:
        """Switch engine and repopulate the model list without closing."""
        if self._engine_choice is None:
            return
        idx = self._engine_choice.GetSelection()
        if not (0 <= idx < len(self._all_providers)):
            return
        new_provider = self._all_providers[idx]
        if new_provider is self._provider:
            return
        self._provider = new_provider
        from quill.core.speech.service import describe_models

        self._rows = describe_models(new_provider, self._total_ram, self._has_gpu)
        self._populate_model_list()
        self._update_buttons()
        self.dialog.SetTitle(
            f"Manage Speech Models — {new_provider.display_name}"  # type: ignore[attr-defined]
        )

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def show(self, show_modal_dialog: Callable) -> SpeechSetupResult | None:
        """Open the dialog. Returns what the user chose, or None on cancel/close."""
        show_modal_dialog(self.dialog, "Manage Speech Models")
        self.dialog.Destroy()
        return self._result
