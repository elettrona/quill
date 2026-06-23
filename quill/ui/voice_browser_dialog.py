"""Voice Browser dialog — choose TTS engine, voice, and settings with live preview.

Replaces the inline ``choose_read_aloud_configuration()`` closure in MainFrame
with a proper, reusable dialog that adds:

  * Filter-as-you-type voice search (name, accent, description)
  * Per-voice detail panel (accent · style)
  * Preview on Enter key or double-click (no extra button click needed)
  * Export to Speech Audio button (closes and triggers export)
  * Clear installed vs. not-downloaded distinction for Piper/Kokoro voices
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from quill.ui.dialog_contract import apply_modal_ids

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


@dataclass
class VoiceBrowserResult:
    """What the caller should do after the dialog closes."""

    action: str
    """'select' | 'download' | 'export'"""
    engine: str = ""
    voice_id: str = ""
    rate: int = 175
    volume: int = 100
    pitch: int = 50
    dectalk_rate: int = 200
    kokoro_speed: float = 1.0
    espeak_rate: int = 175


class VoiceBrowserDialog:
    """Select a TTS engine and voice with live preview and one-click export.

    Parameters
    ----------
    parent:
        wx parent window.
    engine_options:
        ``[(label, id), ...]`` for the engine RadioBox.
    current_engine:
        Initially selected engine id.
    piper_model_dir:
        Path to the local Piper model folder (used to determine download status).
    settings:
        A settings object with ``read_aloud_*`` attributes (snapshot for defaults).
    preview_fn:
        ``(engine, voice_id) -> None`` — runs on main thread, must start its own
        background work (does NOT block the UI).  Passed directly from MainFrame's
        ``_preview_voice`` method.
    """

    def __init__(
        self,
        parent: object,
        *,
        engine_options: list[tuple[str, str]],
        current_engine: str,
        piper_model_dir: Path,
        settings: object,
        preview_fn: Callable[[str, str], None],
    ) -> None:
        import wx

        self._wx = wx
        self._engine_options = engine_options
        self._engine_labels = [lbl for lbl, _ in engine_options]
        self._engine_values = [val for _, val in engine_options]
        self._current_engine = current_engine
        self._piper_model_dir = piper_model_dir
        self._settings = settings
        self._preview_fn = preview_fn
        self._result: VoiceBrowserResult | None = None
        self._all_voices: list = []
        self._displayed_voices: list = []

        self.dialog = wx.Dialog(
            parent,
            title="Manage Voices & Reading Aloud",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetMinSize(wx.Size(580, 520))
        self.dialog.SetSize(wx.Size(680, 600))
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        wx = self._wx
        s = self._settings
        root = wx.BoxSizer(wx.VERTICAL)

        # Engine radio box.
        self._engine_rb = wx.RadioBox(
            self.dialog,
            label="&Engine",
            choices=self._engine_labels,
            style=wx.RA_SPECIFY_ROWS,
        )
        self._engine_rb.SetName("Engine")
        cur_idx = (
            self._engine_values.index(self._current_engine)
            if self._current_engine in self._engine_values
            else 0
        )
        self._engine_rb.SetSelection(cur_idx)
        root.Add(self._engine_rb, 0, wx.EXPAND | wx.ALL, 10)

        # Filter row.
        filter_row = wx.BoxSizer(wx.HORIZONTAL)
        filter_lbl = wx.StaticText(self.dialog, label="Filter &voices:")
        self._filter_ctrl = wx.TextCtrl(self.dialog)
        self._filter_ctrl.SetName("Filter voices")
        self._filter_ctrl.SetHint("type to search by name, accent, or style...")
        filter_row.Add(filter_lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        filter_row.Add(self._filter_ctrl, 1, wx.EXPAND)
        root.Add(filter_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Voice list.
        voices_lbl = wx.StaticText(self.dialog, label="&Voices (Enter or double-click to preview):")
        root.Add(voices_lbl, 0, wx.LEFT | wx.TOP, 10)
        self._voice_lb = wx.ListBox(self.dialog, style=wx.LB_SINGLE)
        self._voice_lb.SetName("Voices")
        self._voice_lb.SetMinSize(wx.Size(-1, 160))
        root.Add(self._voice_lb, 1, wx.EXPAND | wx.ALL, 10)

        # Voice detail.
        self._detail_lbl = wx.StaticText(self.dialog, label="")
        self._detail_lbl.SetName("Voice details")
        root.Add(self._detail_lbl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Settings panel — shown/hidden per engine.
        settings_box = wx.StaticBoxSizer(wx.StaticBox(self.dialog, label="Settings"), wx.VERTICAL)
        sb = settings_box.GetStaticBox()

        rate_row = wx.BoxSizer(wx.HORIZONTAL)
        self._rate_lbl = wx.StaticText(sb, label="Rate:")
        self._rate_spin = wx.SpinCtrl(
            sb, min=75, max=650, initial=getattr(s, "read_aloud_rate", 175)
        )
        self._rate_spin.SetName("Rate (words per minute)")
        rate_row.Add(self._rate_lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        rate_row.Add(self._rate_spin, 1, wx.EXPAND)
        settings_box.Add(rate_row, 0, wx.EXPAND | wx.ALL, 4)

        vol_row = wx.BoxSizer(wx.HORIZONTAL)
        self._vol_lbl = wx.StaticText(sb, label="Volume (0-100):")
        self._vol_spin = wx.SpinCtrl(
            sb, min=0, max=100, initial=getattr(s, "read_aloud_volume", 100)
        )
        self._vol_spin.SetName("Volume")
        vol_row.Add(self._vol_lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        vol_row.Add(self._vol_spin, 1, wx.EXPAND)
        settings_box.Add(vol_row, 0, wx.EXPAND | wx.ALL, 4)

        pitch_row = wx.BoxSizer(wx.HORIZONTAL)
        self._pitch_lbl = wx.StaticText(sb, label="Pitch (0-100):")
        self._pitch_spin = wx.SpinCtrl(
            sb, min=0, max=100, initial=getattr(s, "read_aloud_pitch", 50)
        )
        self._pitch_spin.SetName("Pitch")
        pitch_row.Add(self._pitch_lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        pitch_row.Add(self._pitch_spin, 1, wx.EXPAND)
        settings_box.Add(pitch_row, 0, wx.EXPAND | wx.ALL, 4)

        kok_row = wx.BoxSizer(wx.HORIZONTAL)
        self._kok_lbl = wx.StaticText(sb, label="Speed (0.5-2.0):")
        self._kok_spin = wx.SpinCtrlDouble(
            sb, min=0.5, max=2.0, initial=getattr(s, "read_aloud_kokoro_speed", 1.0), inc=0.1
        )
        self._kok_spin.SetName("Speed multiplier")
        for _child in self._kok_spin.GetChildren():
            if isinstance(_child, wx.TextCtrl):
                _child.SetName("Speed multiplier")
                break
        kok_row.Add(self._kok_lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        kok_row.Add(self._kok_spin, 1, wx.EXPAND)
        settings_box.Add(kok_row, 0, wx.EXPAND | wx.ALL, 4)

        self._settings_box = settings_box
        self._rate_row = rate_row
        self._vol_row = vol_row
        self._pitch_row = pitch_row
        self._kok_row = kok_row
        self._settings_sb = sb
        root.Add(settings_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Action buttons.
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self._preview_btn = wx.Button(self.dialog, label="&Preview (Enter)")
        self._preview_btn.SetName("Preview selected voice")
        self._download_btn = wx.Button(self.dialog, label="&Download Voice...")
        self._download_btn.SetName("Download voice model")
        self._export_btn = wx.Button(self.dialog, label="E&xport to Audio File...")
        self._export_btn.SetName("Export document to audio file")
        ok_btn = wx.Button(self.dialog, id=wx.ID_OK)
        cancel_btn = wx.Button(self.dialog, id=wx.ID_CANCEL)
        btn_row.Add(self._preview_btn, 0, wx.RIGHT, 6)
        btn_row.Add(self._download_btn, 0, wx.RIGHT, 6)
        btn_row.Add(self._export_btn, 0, wx.RIGHT, 6)
        btn_row.AddStretchSpacer()
        btn_row.Add(ok_btn, 0, wx.RIGHT, 6)
        btn_row.Add(cancel_btn, 0)
        root.Add(btn_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        apply_modal_ids(self.dialog, affirmative_id=wx.ID_OK, escape_id=wx.ID_CANCEL)
        self.dialog.SetSizer(root)

        # Bindings.
        self._engine_rb.Bind(wx.EVT_RADIOBOX, lambda _e: self._on_engine_changed())
        self._filter_ctrl.Bind(wx.EVT_TEXT, lambda _e: self._on_filter_changed())
        self._voice_lb.Bind(wx.EVT_LISTBOX, lambda _e: self._on_voice_selected())
        self._voice_lb.Bind(wx.EVT_LISTBOX_DCLICK, lambda _e: self._do_preview())
        self._voice_lb.Bind(wx.EVT_KEY_DOWN, self._on_voice_key_down)
        self._preview_btn.Bind(wx.EVT_BUTTON, lambda _e: self._do_preview())
        self._download_btn.Bind(wx.EVT_BUTTON, lambda _e: self._do_download())
        self._export_btn.Bind(wx.EVT_BUTTON, lambda _e: self._do_export())

        self._refresh_voices(self._current_engine)

    # ------------------------------------------------------------------
    # Engine / voice refresh
    # ------------------------------------------------------------------

    def _current_engine_id(self) -> str:
        idx = self._engine_rb.GetSelection()
        if 0 <= idx < len(self._engine_values):
            return self._engine_values[idx]
        return self._engine_values[0] if self._engine_values else "pyttsx3"

    def _voices_for_engine(self, eng: str) -> list:

        from quill.core.read_aloud import (
            list_dectalk_voices,
            list_espeak_english_voices,
            list_kokoro_voices,
            list_piper_catalog_voices,
            list_voices,
        )

        if eng == "dectalk":
            return list_dectalk_voices()
        if eng == "piper":
            return list_piper_catalog_voices(self._piper_model_dir)
        if eng == "kokoro":
            return list_kokoro_voices()
        if eng == "espeak":
            return list_espeak_english_voices()
        # pyttsx3 — English-only system voices
        all_v = list_voices()
        return [v for v in all_v if "english" in v.name.lower() or not v.name] or all_v

    def _current_voice_id_for(self, eng: str) -> str:
        from pathlib import Path as _Path

        s = self._settings
        if eng == "dectalk":
            return str(getattr(s, "read_aloud_dectalk_voice", "") or "paul")
        if eng == "piper":
            model = str(getattr(s, "read_aloud_piper_model", "") or "")
            return _Path(model).stem if model else ""
        if eng == "kokoro":
            return str(getattr(s, "read_aloud_kokoro_voice", "") or "af_heart")
        if eng == "espeak":
            return str(getattr(s, "read_aloud_espeak_voice", "") or "en")
        return str(getattr(s, "read_aloud_voice", "") or "")

    def _refresh_voices(self, eng: str) -> None:
        self._all_voices = self._voices_for_engine(eng)
        self._filter_ctrl.Clear()
        self._apply_filter("")
        cur_vid = self._current_voice_id_for(eng)
        idx = next((i for i, v in enumerate(self._displayed_voices) if v.id == cur_vid), 0)
        if self._displayed_voices:
            self._voice_lb.SetSelection(idx)
        self._on_voice_selected()
        self._update_settings_panel(eng)

    def _apply_filter(self, query: str) -> None:
        q = query.strip().lower()
        if q:
            self._displayed_voices = [
                v
                for v in self._all_voices
                if q in v.name.lower()
                or q in getattr(v, "accent", "").lower()
                or q in getattr(v, "description", "").lower()
            ]
        else:
            self._displayed_voices = list(self._all_voices)

        labels = []
        for v in self._displayed_voices:
            accent = getattr(v, "accent", "")
            desc = getattr(v, "description", "")
            installed = getattr(v, "installed", True)
            parts = [p for p in [accent, desc] if p]
            meta = " · ".join(parts)
            tag = "" if installed else "  [not downloaded]"
            labels.append(f"{v.name}  —  {meta}{tag}" if meta else f"{v.name}{tag}")

        self._voice_lb.Set(labels)
        if self._displayed_voices:
            self._voice_lb.SetSelection(0)
        self._on_voice_selected()

    def _update_settings_panel(self, eng: str) -> None:
        s = self._settings
        has_rate = eng in {"pyttsx3", "dectalk", "espeak"}
        has_vol_pitch = eng == "pyttsx3"
        has_kokoro = eng == "kokoro"
        has_any = has_rate or has_vol_pitch or has_kokoro

        if eng == "pyttsx3":
            self._rate_spin.SetRange(80, 450)
            self._rate_spin.SetValue(getattr(s, "read_aloud_rate", 175))
        elif eng == "dectalk":
            self._rate_spin.SetRange(75, 650)
            self._rate_spin.SetValue(getattr(s, "read_aloud_dectalk_rate", 200))
        elif eng == "espeak":
            self._rate_spin.SetRange(80, 450)
            self._rate_spin.SetValue(getattr(s, "read_aloud_espeak_rate", 175))

        if has_vol_pitch:
            self._vol_spin.SetValue(getattr(s, "read_aloud_volume", 100))
            self._pitch_spin.SetValue(getattr(s, "read_aloud_pitch", 50))
        if has_kokoro:
            self._kok_spin.SetValue(getattr(s, "read_aloud_kokoro_speed", 1.0))

        self._settings_box.Show(self._rate_row, has_rate, recursive=True)
        self._settings_box.Show(self._vol_row, has_vol_pitch, recursive=True)
        self._settings_box.Show(self._pitch_row, has_vol_pitch, recursive=True)
        self._settings_box.Show(self._kok_row, has_kokoro, recursive=True)
        self._settings_sb.Show(has_any)
        self._settings_box.ShowItems(has_any)

        show_dl = eng in {"piper", "kokoro"}
        self._download_btn.Show(show_dl)
        if eng == "piper":
            self._download_btn.SetLabel("&Download Piper Voice...")
        elif eng == "kokoro":
            self._download_btn.SetLabel("&Download Kokoro Models (~114 MB)...")

        self.dialog.Layout()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_engine_changed(self) -> None:
        eng = self._current_engine_id()
        self._refresh_voices(eng)

    def _on_filter_changed(self) -> None:
        self._apply_filter(self._filter_ctrl.GetValue())

    def _on_voice_selected(self) -> None:
        idx = self._voice_lb.GetSelection()
        wx = self._wx
        if idx == wx.NOT_FOUND or idx >= len(self._displayed_voices):
            self._detail_lbl.SetLabel("")
            self._preview_btn.Enable(False)
            return
        v = self._displayed_voices[idx]
        accent = getattr(v, "accent", "")
        desc = getattr(v, "description", "")
        installed = getattr(v, "installed", True)
        parts = [p for p in [accent, desc] if p]
        detail = " · ".join(parts)
        if not installed:
            detail = (detail + " — not downloaded") if detail else "Not downloaded"
        self._detail_lbl.SetLabel(detail)
        self._preview_btn.Enable(True)

    def _on_voice_key_down(self, event: object) -> None:
        wx = self._wx
        key = event.GetKeyCode()  # type: ignore[attr-defined]
        if key in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self._do_preview()
        else:
            event.Skip()  # type: ignore[attr-defined]

    def _do_preview(self) -> None:
        idx = self._voice_lb.GetSelection()
        wx = self._wx
        if idx == wx.NOT_FOUND or idx >= len(self._displayed_voices):
            return
        v = self._displayed_voices[idx]
        if not getattr(v, "installed", True):
            return
        eng = self._current_engine_id()
        self._preview_fn(eng, v.id)

    def _do_download(self) -> None:
        eng = self._current_engine_id()
        idx = self._voice_lb.GetSelection()
        voice_id = ""
        if 0 <= idx < len(self._displayed_voices):
            voice_id = self._displayed_voices[idx].id
        self._result = VoiceBrowserResult(
            action="download",
            engine=eng,
            voice_id=voice_id,
            **self._collect_settings(eng),
        )
        self.dialog.EndModal(self._wx.ID_OK)

    def _do_export(self) -> None:
        eng = self._current_engine_id()
        idx = self._voice_lb.GetSelection()
        voice_id = ""
        if 0 <= idx < len(self._displayed_voices):
            voice_id = self._displayed_voices[idx].id
        self._result = VoiceBrowserResult(
            action="export",
            engine=eng,
            voice_id=voice_id,
            **self._collect_settings(eng),
        )
        self.dialog.EndModal(self._wx.ID_OK)

    def _collect_settings(self, eng: str) -> dict:
        s = self._settings
        return {
            "rate": self._rate_spin.GetValue(),
            "volume": self._vol_spin.GetValue(),
            "pitch": self._pitch_spin.GetValue(),
            "dectalk_rate": (
                self._rate_spin.GetValue()
                if eng == "dectalk"
                else getattr(s, "read_aloud_dectalk_rate", 200)
            ),
            "kokoro_speed": self._kok_spin.GetValue(),
            "espeak_rate": (
                self._rate_spin.GetValue()
                if eng == "espeak"
                else getattr(s, "read_aloud_espeak_rate", 175)
            ),
        }

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def show(self, show_modal_dialog: Callable) -> VoiceBrowserResult | None:
        """Open the dialog. Returns what the user chose, or None on cancel."""
        result_code = show_modal_dialog(self.dialog, "Manage Voices & Reading Aloud")
        if result_code == self._wx.ID_OK and self._result is None:
            # User clicked OK without using a special action button.
            eng = self._current_engine_id()
            idx = self._voice_lb.GetSelection()
            voice_id = ""
            if 0 <= idx < len(self._displayed_voices):
                voice_id = self._displayed_voices[idx].id
            self._result = VoiceBrowserResult(
                action="select",
                engine=eng,
                voice_id=voice_id,
                **self._collect_settings(eng),
            )
        self.dialog.Destroy()
        return self._result
