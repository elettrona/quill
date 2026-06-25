"""Build Audiobook from Folder dialog (§1.5 ChapterForge surface).

A standalone, keyboard-first ``wx.Dialog`` that collects a folder of audio files,
the book's tags, a cover image, and the output format, and returns an
:class:`AudiobookRequest`. It does not build the audiobook itself — the caller
(``quill.ui.audiobook_builder_runner.run_build_audiobook``) runs the wx-free
``quill.core.speech.audiobook.build_audiobook`` on the background task pool.

Per the NVDA focus rule (A11Y-SR-2) every control is parented directly on the
dialog. The dialog is opened only via ``MainFrame._show_modal_dialog`` and wires
its OK/Cancel ids through ``apply_modal_ids`` so Escape closes it.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from quill.ui.dialog_contract import apply_modal_ids, show_message_box

# (source_folder, recursive) -> (audio_file_count, detected_cover_path or "")
ScanFn = Callable[[Path, bool], "tuple[int, str]"]

_FORMATS = (("M4B audiobook (native chapters)", "m4b"), ("MP3 (with chapter markers)", "mp3"))


@dataclass(slots=True)
class AudiobookRequest:
    """Everything the caller needs to build one chaptered audiobook."""

    source_folder: Path
    recursive: bool
    output_path: Path
    output_format: str  # m4b | mp3
    album: str
    author: str
    narrator: str
    genre: str
    year: str
    cover_path: str


class AudiobookBuilderDialog:
    """Configuration dialog for the folder-to-audiobook builder."""

    def __init__(
        self,
        parent: object,
        *,
        defaults: AudiobookRequest,
        on_scan: ScanFn,
        announce: Callable[[str], None] | None = None,
    ) -> None:
        import wx

        self._wx = wx
        self._on_scan = on_scan
        # Spoken-status callback so a screen-reader user hears the scan result
        # (the folder pick changes a StaticText that is not otherwise announced).
        self._announce_fn = announce
        self._result: AudiobookRequest | None = None

        self.dialog = wx.Dialog(
            parent,
            title="Build Audiobook from Folder",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetMinSize(wx.Size(600, 560))
        root = wx.BoxSizer(wx.VERTICAL)

        def label(text: str) -> None:
            root.Add(wx.StaticText(self.dialog, label=text), 0, wx.LEFT | wx.TOP, 8)

        # --- Source folder + recurse + scan status ---
        label("&Source folder (audio files, one per chapter):")
        src_row = wx.BoxSizer(wx.HORIZONTAL)
        self._source = wx.TextCtrl(self.dialog, value=str(defaults.source_folder))
        browse = wx.Button(self.dialog, label="B&rowse...")
        browse.Bind(wx.EVT_BUTTON, self._on_browse_source)
        src_row.Add(self._source, 1, wx.EXPAND | wx.RIGHT, 6)
        src_row.Add(browse, 0)
        root.Add(src_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        self._recursive = wx.CheckBox(self.dialog, label="Include su&bfolders")
        self._recursive.SetValue(defaults.recursive)
        self._recursive.Bind(wx.EVT_CHECKBOX, lambda _e: self._rescan())
        root.Add(self._recursive, 0, wx.LEFT | wx.TOP, 8)
        self._scan_status = wx.StaticText(self.dialog, label="No folder chosen yet.")
        root.Add(self._scan_status, 0, wx.LEFT | wx.TOP, 8)

        # --- Book details ---
        grid = wx.FlexGridSizer(cols=2, vgap=4, hgap=8)
        grid.AddGrowableCol(1, 1)
        self._album = self._add_field(grid, "Book &title:", defaults.album)
        self._author = self._add_field(grid, "&Author:", defaults.author)
        self._narrator = self._add_field(grid, "&Narrator:", defaults.narrator)
        self._genre = self._add_field(grid, "&Genre:", defaults.genre)
        self._year = self._add_field(grid, "&Year:", defaults.year)
        root.Add(grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)

        # --- Cover image ---
        label("&Cover image (auto-detected from the folder; optional):")
        cover_row = wx.BoxSizer(wx.HORIZONTAL)
        self._cover = wx.TextCtrl(self.dialog, value=defaults.cover_path)
        cover_browse = wx.Button(self.dialog, label="Bro&wse...")
        cover_browse.Bind(wx.EVT_BUTTON, self._on_browse_cover)
        cover_row.Add(self._cover, 1, wx.EXPAND | wx.RIGHT, 6)
        cover_row.Add(cover_browse, 0)
        root.Add(cover_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        # --- Output format + file ---
        label("Output &format:")
        self._format = wx.Choice(self.dialog, choices=[lbl for lbl, _f in _FORMATS])
        self._format.SetSelection(0 if defaults.output_format != "mp3" else 1)
        self._format.Bind(wx.EVT_CHOICE, lambda _e: self._sync_output_suffix())
        root.Add(self._format, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        label("Save &as:")
        out_row = wx.BoxSizer(wx.HORIZONTAL)
        self._output = wx.TextCtrl(self.dialog, value=str(defaults.output_path))
        out_browse = wx.Button(self.dialog, label="Brow&se...")
        out_browse.Bind(wx.EVT_BUTTON, self._on_browse_output)
        out_row.Add(self._output, 1, wx.EXPAND | wx.RIGHT, 6)
        out_row.Add(out_browse, 0)
        root.Add(out_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        # --- Buttons (OK = Build) ---
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        build_btn = wx.Button(self.dialog, id=wx.ID_OK, label="&Build")
        cancel_btn = wx.Button(self.dialog, id=wx.ID_CANCEL)
        build_btn.Bind(wx.EVT_BUTTON, self._on_build)
        btn_row.AddStretchSpacer()
        btn_row.Add(build_btn, 0, wx.RIGHT, 6)
        btn_row.Add(cancel_btn, 0)
        root.Add(btn_row, 0, wx.EXPAND | wx.ALL, 10)

        apply_modal_ids(self.dialog, affirmative_id=wx.ID_OK, escape_id=wx.ID_CANCEL)
        self.dialog.SetSizer(root)
        self.dialog.Fit()
        if defaults.source_folder and Path(str(defaults.source_folder)).is_dir():
            self._rescan()

    # ------------------------------------------------------------------ helpers

    def _add_field(self, grid: object, text: str, value: str) -> object:
        wx = self._wx
        grid.Add(wx.StaticText(self.dialog, label=text), 0, wx.ALIGN_CENTER_VERTICAL)
        ctrl = wx.TextCtrl(self.dialog, value=value)
        grid.Add(ctrl, 0, wx.EXPAND)
        return ctrl

    def _current_format(self) -> str:
        idx = self._format.GetSelection()
        return _FORMATS[idx][1] if 0 <= idx < len(_FORMATS) else "m4b"

    def _sync_output_suffix(self) -> None:
        text = self._output.GetValue().strip()
        if text:
            self._output.SetValue(str(Path(text).with_suffix(f".{self._current_format()}")))

    def _set_scan_status(self, text: str) -> None:
        """Update the scan status label and speak it (screen-reader status, GATE-12)."""
        self._scan_status.SetLabel(text)
        if self._announce_fn is not None:
            self._announce_fn(text)

    def _rescan(self) -> None:
        folder_text = self._source.GetValue().strip()
        if not folder_text or not Path(folder_text).is_dir():
            self._set_scan_status("No folder chosen yet.")
            return
        try:
            count, cover = self._on_scan(Path(folder_text), self._recursive.GetValue())
        except Exception:  # noqa: BLE001 - a scan failure must not break the dialog
            self._set_scan_status("Could not scan that folder.")
            return
        self._set_scan_status(
            f"{count} audio file(s) found — each becomes a chapter."
            if count
            else "No audio files found in that folder."
        )
        if cover and not self._cover.GetValue().strip():
            self._cover.SetValue(cover)
        if count and not self._output.GetValue().strip():
            default_out = Path(folder_text) / f"{Path(folder_text).name}.{self._current_format()}"
            self._output.SetValue(str(default_out))

    # ------------------------------------------------------------------ events

    def _on_browse_source(self, _evt: object) -> None:
        wx = self._wx
        with wx.DirDialog(self.dialog, "Choose the folder of audio files") as dlg:
            if dlg.ShowModal() == wx.ID_OK:  # GATE-42-OK: native folder picker
                self._source.SetValue(dlg.GetPath())
                self._rescan()

    def _on_browse_cover(self, _evt: object) -> None:
        wx = self._wx
        with wx.FileDialog(
            self.dialog,
            "Choose a cover image",
            wildcard="Images (*.jpg;*.jpeg;*.png)|*.jpg;*.jpeg;*.png",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:  # GATE-42-OK: native file picker
                self._cover.SetValue(dlg.GetPath())

    def _on_browse_output(self, _evt: object) -> None:
        wx = self._wx
        fmt = self._current_format()
        with wx.FileDialog(
            self.dialog,
            "Save the audiobook as",
            wildcard=f"{fmt.upper()} (*.{fmt})|*.{fmt}",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as dlg:
            if dlg.ShowModal() == wx.ID_OK:  # GATE-42-OK: native file picker
                self._output.SetValue(str(Path(dlg.GetPath()).with_suffix(f".{fmt}")))

    def _collect(self) -> AudiobookRequest:
        return AudiobookRequest(
            source_folder=Path(self._source.GetValue().strip()),
            recursive=self._recursive.GetValue(),
            output_path=Path(self._output.GetValue().strip()),
            output_format=self._current_format(),
            album=self._album.GetValue().strip(),
            author=self._author.GetValue().strip(),
            narrator=self._narrator.GetValue().strip(),
            genre=self._genre.GetValue().strip(),
            year=self._year.GetValue().strip(),
            cover_path=self._cover.GetValue().strip(),
        )

    def _on_build(self, evt: object) -> None:
        req = self._collect()
        if not req.source_folder.is_dir():
            self._error("Choose a source folder that exists.")
            return
        if not str(req.output_path).strip():
            self._error("Choose where to save the audiobook.")
            return
        self._result = req
        evt.Skip()  # let ID_OK close the dialog

    def _error(self, message: str) -> None:
        show_message_box(
            message, "Build Audiobook from Folder", self._wx.OK | self._wx.ICON_ERROR, self.dialog
        )

    # ------------------------------------------------------------------ public

    def show(self, show_modal_dialog: Callable[[object, str], int]) -> AudiobookRequest | None:
        """Open the dialog; return the collected request, or ``None`` on cancel."""
        code = show_modal_dialog(self.dialog, "Build Audiobook from Folder")
        result = self._result if code == self._wx.ID_OK else None
        self.dialog.Destroy()
        return result
