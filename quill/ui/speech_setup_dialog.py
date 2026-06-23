"""Speech Setup dialog — model catalog with live install/state visibility (#669).

Replaces the three-step SingleChoiceDialog chain (engine chooser → flat model
list → action picker) with a single panel that shows every model's current
state, recommended status, and size at a glance.  The user picks one action
and closes; the caller executes it.

Supports embed mode: pass ``embed_in`` to build the UI into an existing
``wx.Panel`` (used by SpeechHubDialog for the Dictation notebook tab).
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
    """One of: 'download' | 'remove' | 'ffmpeg' | 'engine' | 'vosk' | 'kokoro_engine'
    | 'hf_token'."""
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
    embed_in:
        When given, build the UI into this existing ``wx.Panel`` instead of
        creating a new ``wx.Dialog``.
    on_action:
        Callback invoked (with a ``SpeechSetupResult``) when any action button
        is triggered in embed mode.  Ignored when ``embed_in`` is None.
    """

    def __init__(
        self,
        parent: object,
        *,
        provider: object,
        rows: list,
        machine_summary: str,
        whispercpp_ok: bool,
        ffmpeg_ok: bool,
        engine_ok: bool,
        vosk_ok: bool,
        vosk_can_install: bool,
        kokoro_ok: bool,
        kokoro_can_install: bool,
        all_providers: list,
        total_ram: float = 0.0,
        has_gpu: bool = False,
        embed_in: object | None = None,
        on_action: Callable[[SpeechSetupResult], None] | None = None,
    ) -> None:
        import wx

        self._wx = wx
        self._provider = provider
        self._rows = rows
        self._machine_summary = machine_summary
        self._whispercpp_ok = whispercpp_ok
        self._ffmpeg_ok = ffmpeg_ok
        self._engine_ok = engine_ok
        self._vosk_ok = vosk_ok
        self._vosk_can_install = vosk_can_install
        self._kokoro_ok = kokoro_ok
        self._kokoro_can_install = kokoro_can_install
        self._all_providers = all_providers
        self._total_ram = total_ram
        self._has_gpu = has_gpu
        self._result: SpeechSetupResult | None = None
        self._on_action = on_action

        if embed_in is not None:
            self._root = embed_in
            self.dialog = None  # type: ignore[assignment]
            self._embed_mode = True
        else:
            self.dialog = wx.Dialog(
                parent,
                title="Manage Speech Models",
                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
            )
            self.dialog.SetMinSize(wx.Size(560, 460))
            self.dialog.SetSize(wx.Size(700, 540))
            self._root = self.dialog
            self._embed_mode = False

        self._build_ui()

    def _build_ui(self) -> None:
        wx = self._wx
        root = wx.BoxSizer(wx.VERTICAL)
        parent = self._root

        # Engine row — only shown when multiple providers are registered.
        if len(self._all_providers) > 1:
            eng_row = wx.BoxSizer(wx.HORIZONTAL)
            eng_lbl = wx.StaticText(parent, label="Speech &engine:")
            self._engine_choice = wx.Choice(
                parent,
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
                parent,
                label=f"Engine: {self._provider.display_name}",  # type: ignore[attr-defined]
            )
            root.Add(eng_lbl, 0, wx.ALL, 10)

        # Machine summary.
        self._summary_text = wx.StaticText(parent, label=self._machine_summary)
        root.Add(self._summary_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Engine & dependency status panel.
        dep_box = wx.StaticBoxSizer(
            wx.StaticBox(parent, label="Engine & Dependency Status"), wx.VERTICAL
        )

        wc_row = wx.BoxSizer(wx.HORIZONTAL)
        wc_lbl = wx.StaticText(
            parent,
            label=(
                "Whisper engine binary: Installed"
                if self._whispercpp_ok
                else "Whisper engine binary: Not found — re-run the QUILL installer"
            ),
        )
        wc_row.Add(wc_lbl, 1, wx.ALIGN_CENTER_VERTICAL)
        dep_box.Add(wc_row, 0, wx.EXPAND | wx.ALL, 6)

        ffmpeg_row = wx.BoxSizer(wx.HORIZONTAL)
        ffmpeg_lbl = wx.StaticText(
            parent,
            label="FFmpeg: Installed" if self._ffmpeg_ok else "FFmpeg: Not installed",
        )
        ffmpeg_row.Add(ffmpeg_lbl, 1, wx.ALIGN_CENTER_VERTICAL)
        if not self._ffmpeg_ok:
            self._btn_ffmpeg = wx.Button(parent, label="Download &FFmpeg...")
            self._btn_ffmpeg.Bind(wx.EVT_BUTTON, lambda _e: self._choose("ffmpeg"))
            ffmpeg_row.Add(self._btn_ffmpeg, 0, wx.LEFT, 8)
        dep_box.Add(ffmpeg_row, 0, wx.EXPAND | wx.ALL, 6)

        fw_row = wx.BoxSizer(wx.HORIZONTAL)
        fw_lbl = wx.StaticText(
            parent,
            label=(
                "Faster Whisper: Installed"
                if self._engine_ok
                else "Faster Whisper: Not installed (optional, GPU-accelerated)"
            ),
        )
        fw_row.Add(fw_lbl, 1, wx.ALIGN_CENTER_VERTICAL)
        if not self._engine_ok:
            self._btn_engine = wx.Button(parent, label="Install Faster &Whisper...")
            self._btn_engine.Bind(wx.EVT_BUTTON, lambda _e: self._choose("engine"))
            fw_row.Add(self._btn_engine, 0, wx.LEFT, 8)
        dep_box.Add(fw_row, 0, wx.EXPAND | wx.ALL, 6)

        vosk_row = wx.BoxSizer(wx.HORIZONTAL)
        vosk_lbl = wx.StaticText(
            parent,
            label=(
                "Vosk: Installed"
                if self._vosk_ok
                else "Vosk: Not installed (optional, very low RAM, old hardware)"
            ),
        )
        vosk_row.Add(vosk_lbl, 1, wx.ALIGN_CENTER_VERTICAL)
        if not self._vosk_ok and self._vosk_can_install:
            self._btn_vosk = wx.Button(parent, label="Install &Vosk...")
            self._btn_vosk.Bind(wx.EVT_BUTTON, lambda _e: self._choose("vosk"))
            vosk_row.Add(self._btn_vosk, 0, wx.LEFT, 8)
        dep_box.Add(vosk_row, 0, wx.EXPAND | wx.ALL, 6)

        kokoro_row = wx.BoxSizer(wx.HORIZONTAL)
        kokoro_lbl = wx.StaticText(
            parent,
            label=(
                "Kokoro ONNX: Installed"
                if self._kokoro_ok
                else "Kokoro ONNX: Not installed (optional, high-quality neural TTS)"
            ),
        )
        kokoro_row.Add(kokoro_lbl, 1, wx.ALIGN_CENTER_VERTICAL)
        if not self._kokoro_ok and self._kokoro_can_install:
            self._btn_kokoro = wx.Button(parent, label="Install &Kokoro...")
            self._btn_kokoro.Bind(wx.EVT_BUTTON, lambda _e: self._choose("kokoro_engine"))
            kokoro_row.Add(self._btn_kokoro, 0, wx.LEFT, 8)
        dep_box.Add(kokoro_row, 0, wx.EXPAND | wx.ALL, 6)
        root.Add(dep_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Model list.
        root.Add(
            wx.StaticText(parent, label="&Models (select one, then Download or Remove):"),
            0,
            wx.LEFT | wx.RIGHT,
            10,
        )
        self._model_list = wx.ListBox(parent, style=wx.LB_SINGLE)
        self._model_list.SetName("Models")
        self._model_list.SetMinSize(wx.Size(-1, 140))
        self._populate_model_list()
        root.Add(self._model_list, 1, wx.EXPAND | wx.ALL, 10)

        # Action buttons.
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_download = wx.Button(parent, label="&Download Selected")
        self._btn_remove = wx.Button(parent, label="&Remove Selected")
        btn_hf = wx.Button(parent, label="&Hugging Face Token...")
        btn_row.Add(self._btn_download, 0, wx.RIGHT, 6)
        btn_row.Add(self._btn_remove, 0, wx.RIGHT, 6)
        btn_row.Add(btn_hf, 0, wx.RIGHT, 6)

        if not self._embed_mode:
            btn_close = wx.Button(parent, label="&Close")
            btn_row.Add(btn_close, 0)
            btn_close.Bind(wx.EVT_BUTTON, lambda _e: self.dialog.EndModal(wx.ID_CLOSE))  # type: ignore[union-attr]
            apply_modal_ids(
                parent,
                affirmative_id=self._btn_download.GetId(),
                escape_id=btn_close.GetId(),
            )

        root.Add(btn_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self._btn_download.Bind(wx.EVT_BUTTON, lambda _e: self._on_download())
        self._btn_remove.Bind(wx.EVT_BUTTON, lambda _e: self._on_remove())
        btn_hf.Bind(wx.EVT_BUTTON, lambda _e: self._choose("hf_token"))
        self._model_list.Bind(wx.EVT_LISTBOX, lambda _e: self._update_buttons())

        self._update_buttons()
        self._root.SetSizer(root)

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
        result = SpeechSetupResult(
            action="download",
            model_id=str(getattr(row, "id", "")),
            model_row=row,
            provider_id=getattr(self._provider, "id", None),
        )
        self._dispatch_action(result)

    def _on_remove(self) -> None:
        sel = self._model_list.GetSelection()
        if sel == self._wx.NOT_FOUND or sel >= len(self._rows):
            return
        row = self._rows[sel]
        result = SpeechSetupResult(
            action="remove",
            model_id=str(getattr(row, "id", "")),
            provider_id=getattr(self._provider, "id", None),
        )
        self._dispatch_action(result)

    def _choose(self, action: str) -> None:
        result = SpeechSetupResult(
            action=action,
            provider_id=getattr(self._provider, "id", None),
        )
        self._dispatch_action(result)

    def _dispatch_action(self, result: SpeechSetupResult) -> None:
        if self._embed_mode and self._on_action is not None:
            self._on_action(result)
        else:
            self._result = result
            self.dialog.EndModal(self._wx.ID_OK)  # type: ignore[union-attr]

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
        if not self._embed_mode and self.dialog is not None:
            self.dialog.SetTitle(
                f"Manage Speech Models — {new_provider.display_name}"  # type: ignore[attr-defined]
            )

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def show(self, show_modal_dialog: Callable) -> SpeechSetupResult | None:
        """Open the dialog. Returns what the user chose, or None on cancel/close."""
        if self._embed_mode:
            raise RuntimeError("SpeechSetupDialog.show() cannot be called in embed mode")
        show_modal_dialog(self.dialog, "Manage Speech Models")
        self.dialog.Destroy()  # type: ignore[union-attr]
        return self._result
