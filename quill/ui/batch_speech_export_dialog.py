"""Batch Speech Export dialog — folder of documents to chaptered audio (§4.2).

A standalone, keyboard-first ``wx.Dialog`` that collects everything the chaptered
document-to-speech pipeline needs: a source folder, the file types to include,
the engine/voice/pace, the output format, and the chapter options (transition
sounder, the inter-article / inter-sentence / trailing pauses, and whether the
heading is spoken). It does **not** run the batch itself — :meth:`show` returns a
:class:`BatchSpeechRequest` (or ``None`` on cancel) and the caller
(``quill.ui.batch_speech_runner.run_batch_export_to_speech``) runs it in the
background.

Per the NVDA focus rule (A11Y-SR-2) every control is parented directly on the
dialog, never on an intermediate layout panel. The dialog is opened only via
``MainFrame._show_modal_dialog`` and wires its OK/Cancel ids through
``apply_modal_ids`` so Escape closes it.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from quill.ui.dialog_contract import (
    apply_listbox_activation,
    apply_modal_ids,
    show_message_box,
)

# (label, engine_id) pairs, mirroring the Speech Hub's engine list.
EngineOptions = list[tuple[str, str]]
# engine_id -> [(voice_label, voice_id), ...]
VoicesFor = Callable[[str], list[tuple[str, str]]]


@dataclass(slots=True)
class BatchSpeechRequest:
    """Everything the caller needs to run one chaptered batch export."""

    source_folder: Path
    recursive: bool
    extensions: tuple[str, ...]
    engine: str
    voice: str
    rate: int
    speed: float
    output_format: str  # "wav" | "mp3"
    sound_enabled: bool
    sound_volume: int
    article_gap_ms: int
    sentence_gap_ms: int
    tail_padding_ms: int
    speak_headings: bool
    skip_existing: bool
    # Discovery filters: ;/,-separated globs matched against the file name and the
    # path relative to the source folder; ``max_file_bytes`` of 0 = no size cap.
    include_glob: str = ""
    exclude_glob: str = ""
    max_file_bytes: int = 0
    # What to do when a target audio file already exists.
    on_existing: str = "overwrite"  # skip | overwrite | rename
    # Chapter mode: "single" = one chaptered file per document; "separate" = one
    # audio file per article/heading, into a per-document folder.
    chapter_mode: str = "single"
    # Dry run: write a ``<doc>.preview.txt`` of the exact spoken text (after
    # normalization + pronunciation + polish) for each file, without synthesizing.
    dry_run: bool = False
    preview: bool = False  # internal: a Preview press, not a Start
    # Combine empty headings into the next article (ACB-style) before synthesis.
    combine_headings: bool = False
    # Round-robin voices: ordered voice ids (of the selected engine) cycled one per
    # article/heading. Empty or one voice -> the single `voice` above is used.
    round_robin_voices: tuple[str, ...] = ()
    _voice_label: str = field(default="", repr=False)


_ALL_EXTENSIONS: list[tuple[str, str]] = [
    ("&Word (.docx)", ".docx"),
    ("&Markdown (.md)", ".md"),
    ("&HTML (.html, .htm)", ".html"),
    ("Plain &text (.txt)", ".txt"),
]
# .html implies .htm in discovery.
_EXTENSION_GROUPS = {".html": (".html", ".htm")}
# Existing-file policy choices, in the order they appear in the dialog's Choice.
_EXISTING_POLICIES = ("skip", "overwrite", "rename")
# Output formats, in the order they appear in the format Choice control.
_FORMAT_CHOICES = ("mp3", "m4b", "wav")
_FORMAT_INDEX = {fmt: i for i, fmt in enumerate(_FORMAT_CHOICES)}
# Chapter modes, in the order they appear in the mode Choice control.
_MODE_CHOICES = ("single", "separate")
_MODE_INDEX = {mode: i for i, mode in enumerate(_MODE_CHOICES)}


class BatchSpeechExportDialog:
    """Configuration dialog for chaptered batch document-to-speech export."""

    def __init__(
        self,
        parent: object,
        *,
        engine_options: EngineOptions,
        engine_available: dict[str, bool],
        voices_for: VoicesFor,
        on_preview: Callable[[BatchSpeechRequest], None],
        defaults: BatchSpeechRequest,
    ) -> None:
        import wx

        self._wx = wx
        self._voices_for = voices_for
        self._on_preview = on_preview
        self._engine_options = engine_options
        self._engine_available = engine_available
        self._result: BatchSpeechRequest | None = None
        # Round-robin rotation: ordered (voice_id, label) for the selected engine.
        self._rr_voices: list[tuple[str, str]] = []

        self.dialog = wx.Dialog(
            parent,
            title="Batch Export to Speech Audio",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetMinSize(wx.Size(620, 660))

        root = wx.BoxSizer(wx.VERTICAL)

        def label(text: str) -> None:
            root.Add(wx.StaticText(self.dialog, label=text), 0, wx.LEFT | wx.TOP, 8)

        # --- Source folder + recurse ---
        label("&Source folder (documents to convert):")
        src_row = wx.BoxSizer(wx.HORIZONTAL)
        self._source = wx.TextCtrl(self.dialog, value=str(defaults.source_folder))
        browse = wx.Button(self.dialog, label="B&rowse...")
        browse.Bind(wx.EVT_BUTTON, self._on_browse_source)
        src_row.Add(self._source, 1, wx.EXPAND | wx.RIGHT, 6)
        src_row.Add(browse, 0)
        root.Add(src_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        self._recursive = wx.CheckBox(self.dialog, label="Include su&bfolders")
        self._recursive.SetValue(defaults.recursive)
        root.Add(self._recursive, 0, wx.LEFT | wx.TOP, 8)

        # --- File types ---
        label("File &types to include:")
        self._ext_boxes: list[tuple[wx.CheckBox, str]] = []
        ext_row = wx.BoxSizer(wx.HORIZONTAL)
        for text, ext in _ALL_EXTENSIONS:
            cb = wx.CheckBox(self.dialog, label=text)
            cb.SetValue(ext in defaults.extensions)
            ext_row.Add(cb, 0, wx.RIGHT, 10)
            self._ext_boxes.append((cb, ext))
        root.Add(ext_row, 0, wx.LEFT | wx.TOP, 8)

        # --- Discovery filters (optional) ---
        label("Only incl&ude files matching (globs, ; or , separated; blank = all):")
        self._include = wx.TextCtrl(self.dialog, value=defaults.include_glob)
        root.Add(self._include, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        label("E&xclude files matching (globs, ; or , separated):")
        self._exclude = wx.TextCtrl(self.dialog, value=defaults.exclude_glob)
        root.Add(self._exclude, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        # --- Engine / voice / pace ---
        label("&Engine:")
        self._engine = wx.Choice(
            self.dialog, choices=[self._engine_label(lbl, eid) for lbl, eid in engine_options]
        )
        self._engine.Bind(wx.EVT_CHOICE, lambda _e: self._on_engine_change())
        root.Add(self._engine, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        self._select_engine(defaults.engine)

        label("&Voice:")
        voice_row = wx.BoxSizer(wx.HORIZONTAL)
        self._voice = wx.Choice(self.dialog, choices=[])
        preview_btn = wx.Button(self.dialog, label="&Preview")
        preview_btn.Bind(wx.EVT_BUTTON, self._on_preview_click)
        voice_row.Add(self._voice, 1, wx.EXPAND | wx.RIGHT, 6)
        voice_row.Add(preview_btn, 0)
        root.Add(voice_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        pace_row = wx.BoxSizer(wx.HORIZONTAL)
        pace_row.Add(wx.StaticText(self.dialog, label="R&ate (WPM):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._rate = wx.SpinCtrl(self.dialog, min=80, max=450, initial=defaults.rate)
        pace_row.Add(self._rate, 0, wx.LEFT | wx.RIGHT, 6)
        pace_row.Add(
            wx.StaticText(self.dialog, label="&Kokoro speed:"), 0, wx.ALIGN_CENTER_VERTICAL
        )
        self._speed = wx.SpinCtrlDouble(
            self.dialog, min=0.5, max=2.0, inc=0.05, initial=defaults.speed
        )
        pace_row.Add(self._speed, 0, wx.LEFT, 6)
        root.Add(pace_row, 0, wx.LEFT | wx.TOP, 8)

        # --- Round-robin voices (optional) ---
        label("Round-&robin voices (each article gets the next voice; optional):")
        rr_add_row = wx.BoxSizer(wx.HORIZONTAL)
        self._rr_pick = wx.Choice(self.dialog, choices=[])
        self._rr_pick.SetName("Round-robin voice to add")
        rr_add = wx.Button(self.dialog, label="A&dd voice")
        rr_add.Bind(wx.EVT_BUTTON, lambda _e: self._on_rr_add())
        rr_add_row.Add(self._rr_pick, 1, wx.EXPAND | wx.RIGHT, 6)
        rr_add_row.Add(rr_add, 0)
        root.Add(rr_add_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        self._rr_list = wx.ListBox(self.dialog, style=wx.LB_SINGLE)
        self._rr_list.SetName("Round-robin voice order")
        apply_listbox_activation(self._rr_list, lambda _e: self._rr_pick.SetFocus())
        root.Add(self._rr_list, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        rr_btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self._rr_up = wx.Button(self.dialog, label="Move U&p")
        self._rr_down = wx.Button(self.dialog, label="Move Dow&n")
        self._rr_remove = wx.Button(self.dialog, label="Re&move")
        self._rr_up.Bind(wx.EVT_BUTTON, lambda _e: self._on_rr_move(-1))
        self._rr_down.Bind(wx.EVT_BUTTON, lambda _e: self._on_rr_move(1))
        self._rr_remove.Bind(wx.EVT_BUTTON, lambda _e: self._on_rr_remove())
        for btn in (self._rr_up, self._rr_down, self._rr_remove):
            rr_btn_row.Add(btn, 0, wx.RIGHT, 6)
        root.Add(rr_btn_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        # --- Output format ---
        label("Output &format:")
        self._format = wx.Choice(
            self.dialog,
            choices=[
                "MP3 (with chapter markers)",
                "M4B audiobook (native chapters)",
                "WAV",
            ],
        )
        self._format.SetSelection(_FORMAT_INDEX.get(defaults.output_format, 0))
        root.Add(self._format, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        # --- Chapter mode ---
        label("Chapter &mode:")
        self._mode = wx.Choice(
            self.dialog,
            choices=["Single chaptered file", "Separate file per article"],
        )
        self._mode.SetSelection(_MODE_INDEX.get(defaults.chapter_mode, 0))
        root.Add(self._mode, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        # --- Chapter options ---
        label("Chapter options:")
        self._sound = wx.CheckBox(self.dialog, label="Play a transition s&ounder between headings")
        self._sound.SetValue(defaults.sound_enabled)
        root.Add(self._sound, 0, wx.LEFT | wx.TOP, 8)
        self._speak_headings = wx.CheckBox(self.dialog, label="Speak each &heading aloud")
        self._speak_headings.SetValue(defaults.speak_headings)
        root.Add(self._speak_headings, 0, wx.LEFT | wx.TOP, 8)
        self._combine = wx.CheckBox(
            self.dialog, label="&Combine empty headings into the next article"
        )
        self._combine.SetValue(defaults.combine_headings)
        root.Add(self._combine, 0, wx.LEFT | wx.TOP, 8)
        self._dry_run = wx.CheckBox(
            self.dialog, label="Dr&y run: write preview text only (don't synthesize)"
        )
        self._dry_run.SetValue(defaults.dry_run)
        root.Add(self._dry_run, 0, wx.LEFT | wx.TOP, 8)
        label("If an audio file already e&xists:")
        self._on_existing = wx.Choice(
            self.dialog, choices=["Skip (resume)", "Overwrite", "Rename (keep both)"]
        )
        policy = "skip" if defaults.skip_existing else defaults.on_existing
        policy_idx = _EXISTING_POLICIES.index(policy) if policy in _EXISTING_POLICIES else 1
        self._on_existing.SetSelection(policy_idx)
        root.Add(self._on_existing, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        gap_grid = wx.FlexGridSizer(cols=2, vgap=4, hgap=8)
        self._article_gap = self._add_ms_spin(
            gap_grid, "Pause between &articles (ms):", defaults.article_gap_ms
        )
        self._sentence_gap = self._add_ms_spin(
            gap_grid, "Pause between se&ntences (ms):", defaults.sentence_gap_ms
        )
        self._tail_padding = self._add_ms_spin(
            gap_grid, "Trailing pad per section, anti-cli&pping (ms):", defaults.tail_padding_ms
        )
        self._sound_volume = self._add_ms_spin(
            gap_grid, "Sounder &volume (0-100):", defaults.sound_volume, hi=100
        )
        root.Add(gap_grid, 0, wx.LEFT | wx.TOP, 8)

        # --- Buttons (OK = Start) ---
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        start_btn = wx.Button(self.dialog, id=wx.ID_OK, label="&Start")
        cancel_btn = wx.Button(self.dialog, id=wx.ID_CANCEL)
        start_btn.Bind(wx.EVT_BUTTON, self._on_start)
        btn_row.AddStretchSpacer()
        btn_row.Add(start_btn, 0, wx.RIGHT, 6)
        btn_row.Add(cancel_btn, 0)
        root.Add(btn_row, 0, wx.EXPAND | wx.ALL, 10)

        apply_modal_ids(self.dialog, affirmative_id=wx.ID_OK, escape_id=wx.ID_CANCEL)
        self.dialog.SetSizer(root)
        self.dialog.Fit()
        self._reload_voices(initial_voice=defaults.voice)
        self._seed_rotation(defaults.round_robin_voices)

    # ------------------------------------------------------------------ helpers

    def _engine_label(self, label: str, engine_id: str) -> str:
        if not self._engine_available.get(engine_id, True):
            return f"{label} (not installed)"
        return label

    def _add_ms_spin(self, grid: object, text: str, value: int, *, hi: int = 10000) -> object:
        wx = self._wx
        grid.Add(wx.StaticText(self.dialog, label=text), 0, wx.ALIGN_CENTER_VERTICAL)
        spin = wx.SpinCtrl(self.dialog, min=0, max=hi, initial=int(value))
        grid.Add(spin, 0)
        return spin

    def _select_engine(self, engine_id: str) -> None:
        for i, (_lbl, eid) in enumerate(self._engine_options):
            if eid == engine_id:
                self._engine.SetSelection(i)
                return
        self._engine.SetSelection(0)

    def _current_engine_id(self) -> str:
        idx = self._engine.GetSelection()
        if 0 <= idx < len(self._engine_options):
            return self._engine_options[idx][1]
        return self._engine_options[0][1] if self._engine_options else "sapi5"

    def _reload_voices(self, *, initial_voice: str = "") -> None:
        engine_id = self._current_engine_id()
        self._voice_pairs = self._voices_for(engine_id)
        labels = [lbl for lbl, _vid in self._voice_pairs]
        self._voice.Set(labels)
        self._rr_pick.Set(labels)
        if labels:
            self._rr_pick.SetSelection(0)
        target = initial_voice
        chosen = 0
        for i, (_lbl, vid) in enumerate(self._voice_pairs):
            if vid == target:
                chosen = i
                break
        if self._voice_pairs:
            self._voice.SetSelection(chosen)

    def _on_engine_change(self) -> None:
        # Voices are engine-specific, so switching engines clears the rotation.
        self._reload_voices()
        self._rr_voices = []
        self._refresh_rr_list()

    def _current_voice_id(self) -> str:
        idx = self._voice.GetSelection()
        if 0 <= idx < len(self._voice_pairs):
            return self._voice_pairs[idx][1]
        return ""

    # -------------------------------------------------- round-robin voices

    def _seed_rotation(self, voice_ids: tuple[str, ...]) -> None:
        """Pre-fill the rotation from saved ids, mapping each to its current label."""
        by_id = {vid: lbl for lbl, vid in self._voice_pairs}
        self._rr_voices = [(vid, by_id[vid]) for vid in voice_ids if vid in by_id]
        self._refresh_rr_list()

    def _refresh_rr_list(self, *, select: int = -1) -> None:
        self._rr_list.Set([lbl for _vid, lbl in self._rr_voices])
        if self._rr_voices:
            index = select if 0 <= select < len(self._rr_voices) else 0
            self._rr_list.SetSelection(index)

    def _rr_selected_index(self) -> int:
        idx = self._rr_list.GetSelection()
        return idx if 0 <= idx < len(self._rr_voices) else -1

    def _on_rr_add(self) -> None:
        idx = self._rr_pick.GetSelection()
        if not (0 <= idx < len(self._voice_pairs)):
            return
        label, vid = self._voice_pairs[idx]
        if any(existing == vid for existing, _ in self._rr_voices):
            return  # already in the rotation
        self._rr_voices.append((vid, label))
        self._refresh_rr_list(select=len(self._rr_voices) - 1)

    def _on_rr_move(self, delta: int) -> None:
        idx = self._rr_selected_index()
        target = idx + delta
        if idx < 0 or not (0 <= target < len(self._rr_voices)):
            return
        self._rr_voices[idx], self._rr_voices[target] = (
            self._rr_voices[target],
            self._rr_voices[idx],
        )
        self._refresh_rr_list(select=target)

    def _on_rr_remove(self) -> None:
        idx = self._rr_selected_index()
        if idx < 0:
            return
        del self._rr_voices[idx]
        self._refresh_rr_list(select=min(idx, len(self._rr_voices) - 1))

    def _collect(self, *, preview: bool) -> BatchSpeechRequest:
        exts: list[str] = []
        for cb, ext in self._ext_boxes:
            if cb.GetValue():
                exts.extend(_EXTENSION_GROUPS.get(ext, (ext,)))
        policy_idx = self._on_existing.GetSelection()
        on_existing = _EXISTING_POLICIES[policy_idx] if 0 <= policy_idx < 3 else "overwrite"
        return BatchSpeechRequest(
            source_folder=Path(self._source.GetValue().strip()),
            recursive=self._recursive.GetValue(),
            extensions=tuple(exts),
            engine=self._current_engine_id(),
            voice=self._current_voice_id(),
            rate=int(self._rate.GetValue()),
            speed=float(self._speed.GetValue()),
            output_format=(
                _FORMAT_CHOICES[self._format.GetSelection()]
                if 0 <= self._format.GetSelection() < len(_FORMAT_CHOICES)
                else "mp3"
            ),
            sound_enabled=self._sound.GetValue(),
            sound_volume=int(self._sound_volume.GetValue()),
            article_gap_ms=int(self._article_gap.GetValue()),
            sentence_gap_ms=int(self._sentence_gap.GetValue()),
            tail_padding_ms=int(self._tail_padding.GetValue()),
            speak_headings=self._speak_headings.GetValue(),
            skip_existing=(on_existing == "skip"),
            include_glob=self._include.GetValue().strip(),
            exclude_glob=self._exclude.GetValue().strip(),
            on_existing=on_existing,
            chapter_mode=(
                _MODE_CHOICES[self._mode.GetSelection()]
                if 0 <= self._mode.GetSelection() < len(_MODE_CHOICES)
                else "single"
            ),
            dry_run=self._dry_run.GetValue(),
            preview=preview,
            combine_headings=self._combine.GetValue(),
            round_robin_voices=tuple(vid for vid, _lbl in self._rr_voices),
        )

    # ------------------------------------------------------------------ events

    def _on_browse_source(self, _evt: object) -> None:
        wx = self._wx
        with wx.DirDialog(self.dialog, "Choose the folder of documents to convert") as dlg:
            # Native folder picker owned by this dialog; not a GATE-42 target stem.
            if dlg.ShowModal() == wx.ID_OK:
                self._source.SetValue(dlg.GetPath())

    def _on_preview_click(self, _evt: object) -> None:
        self._on_preview(self._collect(preview=True))

    def _on_start(self, evt: object) -> None:
        req = self._collect(preview=False)
        if not req.source_folder or not req.source_folder.is_dir():
            show_message_box(
                "Choose a source folder that exists.",
                "Batch Export to Speech Audio",
                self._wx.OK | self._wx.ICON_ERROR,
                self.dialog,
            )
            return
        if not req.extensions:
            show_message_box(
                "Select at least one file type to include.",
                "Batch Export to Speech Audio",
                self._wx.OK | self._wx.ICON_ERROR,
                self.dialog,
            )
            return
        self._result = req
        evt.Skip()  # let ID_OK close the dialog

    # ------------------------------------------------------------------ public

    def show(self, show_modal_dialog: Callable[[object, str], int]) -> BatchSpeechRequest | None:
        """Open the dialog; return the collected request, or ``None`` on cancel."""
        code = show_modal_dialog(self.dialog, "Batch Export to Speech Audio")
        result = self._result if code == self._wx.ID_OK else None
        self.dialog.Destroy()
        return result
