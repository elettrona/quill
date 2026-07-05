"""The Chapter Workbench — open, hear, reshape, and save an existing audiobook.

The Audio Studio's *edit an existing audiobook* journey. One dialog holds the
chapter list (with real times), the chapter-aware player, and the surgery
tools: rename, **split at the playhead** (the fix-a-bad-boundary-by-ear
operation), **set a chapter's start to the playhead**, merge into previous,
restore, and full chapter-list import/export (Audacity, CUE, timestamps,
Podcasting 2.0 JSON, CSV). Book tags are editable in place.

Saving: an MP3 saves **in place** (mutagen rewrites only the tags; the audio
is untouched); an M4B saves as a **new file** (lossless ``-c copy`` re-mux).
Long saves run on the caller-provided background runner so the UI thread
never blocks. Chapter math lives in :mod:`quill.core.speech.chapters`; file
IO in :mod:`quill.core.speech.book_file`.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

import wx

from quill.core.i18n import _
from quill.core.speech.book_file import BookFile, save_m4b_book_as, save_mp3_book
from quill.core.speech.chapter_io import (
    EXPORT_FORMATS,
    ChapterParseError,
    export_chapter_text,
    format_timestamp,
    parse_chapter_text,
    suggested_extension,
)
from quill.core.speech.chapters import (
    Chapter,
    ChapterEditError,
    merge_chapter,
    set_chapter_start,
    split_chapter,
)
from quill.ui.audio_studio.player_panel import PlayerPanel
from quill.ui.dialog_contract import (
    apply_listbox_activation,
    apply_modal_ids,
    show_message_box,
)

_log = logging.getLogger(__name__)

# (menu label, chapter_io format key) for Export chapters...
_EXPORT_LABELS: tuple[tuple[str, str], ...] = (
    ("Audacity labels (.txt)", "audacity"),
    ("Timestamps (.txt)", "timestamps"),
    ("CUE sheet (.cue)", "cue"),
    ("Podcasting 2.0 JSON (.chapters.json)", "pod2"),
    ("CSV spreadsheet (.csv)", "csv"),
)


class ChapterWorkbenchDialog(wx.Dialog):
    """Edit an opened book's chapters and tags, with the player as the anchor."""

    def __init__(
        self,
        parent: wx.Window,
        book: BookFile,
        *,
        announce: Callable[[str], None] | None = None,
        run_background: Callable[..., None] | None = None,
    ) -> None:
        super().__init__(
            parent,
            title=str(_("Chapter Workbench")),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
            name="audio_studio.workbench",
        )
        self._book = book
        self._original_chapters = [
            Chapter(index=c.index, title=c.title, start_ms=c.start_ms, end_ms=c.end_ms)
            for c in book.chapters
        ]
        self._announce_fn = announce
        self._run_background = run_background
        self._dirty = False

        root = wx.BoxSizer(wx.VERTICAL)
        heading = wx.StaticText(
            self,
            label=_("Editing {name}").format(name=book.path.name),
            name="audio_studio.workbench_heading",
        )
        heading.SetFont(heading.GetFont().Scaled(1.2).Bold())
        root.Add(heading, 0, wx.ALL, 10)

        root.Add(
            wx.StaticText(
                self,
                label=_("C&hapters (select to hear; edits apply on Save):"),
            ),
            0,
            wx.LEFT,
            10,
        )
        self._chapter_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self._chapter_list.SetName(_("Chapters"))
        self._chapter_list.Bind(wx.EVT_LISTBOX, lambda _e: self._on_selected())
        apply_listbox_activation(self._chapter_list, lambda _e: self._play_selected())
        root.Add(self._chapter_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        title_row = wx.BoxSizer(wx.HORIZONTAL)
        title_row.Add(wx.StaticText(self, label=_("Chapter t&itle:")), 0, wx.ALIGN_CENTER_VERTICAL)
        self._title_edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self._title_edit.SetName(_("Chapter title"))
        self._title_edit.Bind(wx.EVT_TEXT_ENTER, lambda _e: self._on_rename())
        rename_btn = wx.Button(self, label=_("Re&name"))
        rename_btn.Bind(wx.EVT_BUTTON, lambda _e: self._on_rename())
        title_row.Add(self._title_edit, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
        title_row.Add(rename_btn, 0)
        root.Add(title_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        surgery_row = wx.BoxSizer(wx.HORIZONTAL)
        for label, handler in (
            (_("&Split at playhead"), self._on_split),
            (_("Set st&art to playhead"), self._on_retime),
            (_("&Merge into previous"), self._on_merge),
            (_("Rest&ore original"), self._on_restore),
        ):
            btn = wx.Button(self, label=label)
            btn.Bind(wx.EVT_BUTTON, lambda _e, h=handler: h())
            surgery_row.Add(btn, 0, wx.RIGHT, 6)
        root.Add(surgery_row, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        io_row = wx.BoxSizer(wx.HORIZONTAL)
        import_btn = wx.Button(self, label=_("Import chap&ters..."))
        export_btn = wx.Button(self, label=_("E&xport chapters..."))
        import_btn.Bind(wx.EVT_BUTTON, lambda _e: self._on_import())
        export_btn.Bind(wx.EVT_BUTTON, lambda _e: self._on_export())
        io_row.Add(import_btn, 0, wx.RIGHT, 6)
        io_row.Add(export_btn, 0)
        root.Add(io_row, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.player = PlayerPanel(self, announce=announce)
        root.Add(self.player, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        root.Add(wx.StaticText(self, label=_("Book details:")), 0, wx.LEFT | wx.TOP, 10)
        grid = wx.FlexGridSizer(cols=2, vgap=4, hgap=8)
        grid.AddGrowableCol(1, 1)
        self._tag_album = self._tag_field(grid, _("Book ti&tle (album):"), book.tags.album)
        self._tag_artist = self._tag_field(grid, _("A&uthor:"), book.tags.artist)
        self._tag_narrator = self._tag_field(grid, _("Narrato&r:"), book.tags.album_artist)
        self._tag_genre = self._tag_field(grid, _("&Genre:"), book.tags.genre)
        self._tag_year = self._tag_field(grid, _("&Year:"), book.tags.year)
        root.Add(grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self._save_btn = wx.Button(self, label=_("&Save"))
        self._save_btn.Bind(wx.EVT_BUTTON, lambda _e: self._on_save())
        save_as_btn = wx.Button(self, label=_("Save &As..."))
        save_as_btn.Bind(wx.EVT_BUTTON, lambda _e: self._on_save_as())
        close_btn = wx.Button(self, wx.ID_CANCEL, label=_("Close"))
        btn_row.AddStretchSpacer()
        btn_row.Add(self._save_btn, 0, wx.RIGHT, 6)
        btn_row.Add(save_as_btn, 0, wx.RIGHT, 6)
        btn_row.Add(close_btn, 0)
        root.Add(btn_row, 0, wx.EXPAND | wx.ALL, 10)
        if book.kind != "mp3":
            # M4B chapter atoms cannot be rewritten in place; Save As re-muxes.
            self._save_btn.Enable(False)
            self._save_btn.SetToolTip(_("An M4B is saved as a new file; use Save As."))

        apply_modal_ids(self, cancel_id=wx.ID_CANCEL)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.SetMinSize(wx.Size(720, 720))
        self.SetSizer(root)
        self.Fit()
        self.CentreOnParent()
        self._refresh_list()
        self.player.load(str(book.path), book.chapters)

    # -- helpers ---------------------------------------------------------------

    def _tag_field(self, grid: wx.FlexGridSizer, label: str, value: str) -> wx.TextCtrl:
        grid.Add(wx.StaticText(self, label=label), 0, wx.ALIGN_CENTER_VERTICAL)
        ctrl = wx.TextCtrl(self, value=value)
        ctrl.SetName(label.replace("&", "").rstrip(":"))
        grid.Add(ctrl, 0, wx.EXPAND)
        return ctrl

    def _announce(self, text: str) -> None:
        if self._announce_fn is not None:
            self._announce_fn(text)

    def _error(self, message: str) -> None:
        show_message_box(message, str(_("Chapter Workbench")), wx.OK | wx.ICON_ERROR, self)

    def _selected_index(self) -> int:
        idx = self._chapter_list.GetSelection()
        return idx if 0 <= idx < len(self._book.chapters) else -1

    def _refresh_list(self, *, select: int = -1) -> None:
        self._chapter_list.Set([
            _("{num}. {title} — starts {start}, runs {dur}").format(
                num=c.index + 1,
                title=c.title,
                start=format_timestamp(c.start_ms),
                dur=format_timestamp(c.duration_ms),
            )
            for c in self._book.chapters
        ])
        if self._book.chapters:
            index = select if 0 <= select < len(self._book.chapters) else 0
            self._chapter_list.SetSelection(index)
        self._on_selected()
        self.player.set_chapters(self._book.chapters)

    def _on_selected(self) -> None:
        idx = self._selected_index()
        self._title_edit.SetValue(self._book.chapters[idx].title if idx >= 0 else "")

    def _play_selected(self) -> None:
        idx = self._selected_index()
        if idx >= 0:
            self.player.play_chapter(idx)

    def _apply(self, chapters: list[Chapter], *, select: int, spoken: str) -> None:
        self._book.chapters = chapters
        self._dirty = True
        self._refresh_list(select=select)
        self._announce(spoken)

    # -- edits -------------------------------------------------------------------

    def _on_rename(self) -> None:
        idx = self._selected_index()
        if idx < 0:
            return
        title = self._title_edit.GetValue().strip()
        if not title:
            self._error(str(_("A chapter title cannot be empty.")))
            return
        self._book.chapters[idx].title = title
        self._dirty = True
        self._refresh_list(select=idx)
        self._announce(_("Renamed chapter to {title}").format(title=title))

    def _on_split(self) -> None:
        at_ms = self.player.playhead_ms()
        try:
            chapters = split_chapter(self._book.chapters, at_ms, title=str(_("New chapter")))
        except ChapterEditError as exc:
            self._error(str(exc))
            return
        self._apply(
            chapters,
            select=min(
                len(chapters) - 1, next(i for i, c in enumerate(chapters) if c.start_ms == at_ms)
            ),
            spoken=_("Split at {pos}; now {count} chapters").format(
                pos=format_timestamp(at_ms), count=len(chapters)
            ),
        )

    def _on_retime(self) -> None:
        idx = self._selected_index()
        at_ms = self.player.playhead_ms()
        try:
            chapters = set_chapter_start(self._book.chapters, idx, at_ms)
        except ChapterEditError as exc:
            self._error(str(exc))
            return
        self._apply(
            chapters,
            select=idx,
            spoken=_("Chapter {num} now starts at {pos}").format(
                num=idx + 1, pos=format_timestamp(at_ms)
            ),
        )

    def _on_merge(self) -> None:
        idx = self._selected_index()
        try:
            chapters = merge_chapter(self._book.chapters, idx)
        except ChapterEditError as exc:
            self._error(str(exc))
            return
        self._apply(
            chapters,
            select=max(0, idx - 1),
            spoken=_("Merged; {count} chapters remain").format(count=len(chapters)),
        )

    def _on_restore(self) -> None:
        restored = [
            Chapter(index=c.index, title=c.title, start_ms=c.start_ms, end_ms=c.end_ms)
            for c in self._original_chapters
        ]
        self._apply(
            restored,
            select=0,
            spoken=_("Restored the original {count} chapters").format(count=len(restored)),
        )
        self._dirty = False

    # -- import / export -----------------------------------------------------------

    def _on_import(self) -> None:
        with wx.FileDialog(
            self,
            str(_("Import a chapter list")),
            wildcard=(
                "Chapter lists (*.txt;*.cue;*.json;*.csv)|*.txt;*.cue;*.json;*.csv|"
                "All files (*.*)|*.*"
            ),
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:  # GATE-42-OK: native file picker
                return
            path = Path(dlg.GetPath())
        try:
            chapters = parse_chapter_text(path.read_text(encoding="utf-8-sig"), self._book.total_ms)
        except (OSError, ChapterParseError) as exc:
            self._error(str(exc))
            return
        self._apply(
            chapters,
            select=0,
            spoken=_("Imported {count} chapters from {name}").format(
                count=len(chapters), name=path.name
            ),
        )

    def _on_export(self) -> None:
        labels = [label for label, _fmt in _EXPORT_LABELS]
        with wx.SingleChoiceDialog(
            self, str(_("Export the chapter list as:")), str(_("Export chapters")), labels
        ) as picker:
            if picker.ShowModal() != wx.ID_OK:  # GATE-42-OK: native chooser
                return
            fmt = _EXPORT_LABELS[picker.GetSelection()][1]
        assert fmt in EXPORT_FORMATS
        extension = suggested_extension(fmt)
        with wx.FileDialog(
            self,
            str(_("Save the chapter list as")),
            defaultFile=self._book.path.stem + extension,
            wildcard=f"{extension} (*{extension})|*{extension}|All files (*.*)|*.*",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:  # GATE-42-OK: native file picker
                return
            out = Path(dlg.GetPath())
        text = export_chapter_text(
            self._book.chapters,
            fmt,
            audio_filename=self._book.path.name,
            performer=self._tag_artist.GetValue().strip(),
            album=self._tag_album.GetValue().strip(),
        )
        try:
            out.write_text(text, encoding="utf-8")
        except OSError as exc:
            self._error(str(_("Could not write that file: {error}").format(error=exc)))
            return
        self._announce(
            _("Exported {count} chapters to {name}").format(
                count=len(self._book.chapters), name=out.name
            )
        )

    # -- saving ---------------------------------------------------------------------

    def _collect_tags(self) -> None:
        self._book.tags.album = self._tag_album.GetValue().strip()
        self._book.tags.title = self._book.tags.album
        self._book.tags.artist = self._tag_artist.GetValue().strip()
        self._book.tags.album_artist = self._tag_narrator.GetValue().strip()
        self._book.tags.genre = self._tag_genre.GetValue().strip()
        self._book.tags.year = self._tag_year.GetValue().strip()

    def _run_save(self, title: str, work: Callable[[], object], done_message: str) -> None:
        """Run a save on the background pool when available, else inline."""
        if self._run_background is not None:

            def on_success(_result: object) -> None:
                self._dirty = False
                self._announce(done_message)

            self._run_background(title, work, on_success)
            return
        try:
            work()
        except Exception as exc:  # noqa: BLE001 - surfaced, not raised through wx
            self._error(str(exc))
            return
        self._dirty = False
        self._announce(done_message)

    def _on_save(self) -> None:
        self._collect_tags()
        if self._book.kind != "mp3":
            self._on_save_as()
            return
        # The player holds the file open; release it for the in-place rewrite.
        self.player.shutdown()
        book = self._book
        self._run_save(
            str(_("Saving audiobook tags")),
            lambda: save_mp3_book(book),
            str(_("Saved {name}").format(name=book.path.name)),
        )

    def _on_save_as(self) -> None:
        self._collect_tags()
        kind = self._book.kind
        with wx.FileDialog(
            self,
            str(_("Save the book as")),
            defaultFile=self._book.path.stem + f" (edited).{kind}",
            wildcard=f"{kind.upper()} (*.{kind})|*.{kind}",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:  # GATE-42-OK: native file picker
                return
            out = Path(dlg.GetPath())
        book = self._book
        if kind == "mp3":
            import shutil

            def work() -> object:
                shutil.copyfile(book.path, out)
                copy = BookFile(
                    path=out, tags=book.tags, chapters=book.chapters, total_ms=book.total_ms
                )
                save_mp3_book(copy)
                return out

        else:

            def work() -> object:
                return save_m4b_book_as(book, out)

        self._run_save(
            str(_("Saving audiobook")),
            work,
            str(_("Saved {name}").format(name=out.name)),
        )

    # -- lifecycle --------------------------------------------------------------------

    def _on_close(self, evt: wx.CloseEvent) -> None:
        self.player.shutdown()
        evt.Skip()


def open_book_in_workbench(frame: object, path: Path) -> None:
    """Read *path* and open the Workbench on it (the journey-C entry point)."""
    from quill.core.speech.book_file import BookReadError, read_book

    try:
        book = read_book(path)
    except (BookReadError, Exception) as exc:  # noqa: BLE001 - speak, don't crash
        _log.exception("Could not open book")
        frame._show_message_box(  # type: ignore[attr-defined]
            str(_("Could not open that audiobook: {error}").format(error=exc)),
            str(_("Chapter Workbench")),
        )
        return
    dlg = ChapterWorkbenchDialog(
        frame.frame,  # type: ignore[attr-defined]
        book,
        announce=getattr(frame, "_announce", None),
        run_background=getattr(frame, "_run_background_task", None),
    )
    try:
        frame._show_modal_dialog(dlg, str(_("Chapter Workbench")))  # type: ignore[attr-defined]
    finally:
        dlg.Destroy()
