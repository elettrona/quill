"""Audio Studio wizard — the combine-audio-files journey's source page."""

from __future__ import annotations

from pathlib import Path

import wx

from quill.core.i18n import _
from quill.ui.audio_studio.pages_base import StudioPage
from quill.ui.audio_studio.request import BatchSpeechRequest


class AudioSourcePage(StudioPage):
    """Where are the recordings? Folder of audio files to bind into one book."""

    def __init__(self, parent: wx.Window, defaults: BatchSpeechRequest) -> None:
        super().__init__(
            parent,
            "audio_studio.audio_source",
            _("Where are the recordings?"),
            _(
                "Pick the folder of audio files. Each file becomes one chapter,"
                " in natural filename order, and you review the chapter list"
                " before the book is built."
            ),
        )
        self.add_label(_("&Folder of audio files:"))
        row = wx.BoxSizer(wx.HORIZONTAL)
        self.source = wx.TextCtrl(self, value=str(defaults.source_folder))
        self.source.SetName(_("Folder of audio files"))
        browse = wx.Button(self, label=_("B&rowse..."))
        browse.Bind(wx.EVT_BUTTON, self._on_browse)
        row.Add(self.source, 1, wx.EXPAND | wx.RIGHT, 6)
        row.Add(browse, 0)
        self.sizer.Add(row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        self.recursive = wx.CheckBox(self, label=_("Include su&bfolders"))
        self.recursive.SetValue(defaults.recursive)
        self.sizer.Add(self.recursive, 0, wx.LEFT | wx.TOP, 12)

        self.sizer.Add(
            wx.StaticText(
                self,
                label=_(
                    "MP3, M4A/M4B, WAV, FLAC, Opus and OGG files are accepted.\n"
                    "Files that look like previous builds are set aside automatically."
                ),
                name="audio_studio.audio_source_note",
            ),
            flag=wx.ALL,
            border=12,
        )

    def _on_browse(self, _evt: wx.Event) -> None:
        with wx.DirDialog(self, _("Choose the folder of audio files")) as dlg:
            if dlg.ShowModal() == wx.ID_OK:  # GATE-42-OK: native folder picker
                self.source.SetValue(dlg.GetPath())

    def collect(self, req: BatchSpeechRequest) -> None:
        req.source_folder = Path(self.source.GetValue().strip())
        req.recursive = self.recursive.GetValue()
        # A pure-audio run synthesizes nothing: no document types, book always on,
        # and the chapter review step always offered (the runner also forces the
        # editor open when a folder has no documents).
        req.extensions = ()
        req.make_book = True
        req.book_review_chapters = True
        req.dry_run = False

    def is_valid(self) -> tuple[bool, str]:
        text = self.source.GetValue().strip()
        if not text or not Path(text).is_dir():
            return False, _("Choose a folder of audio files that exists.")
        return True, ""
