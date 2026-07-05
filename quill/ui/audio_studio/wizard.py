"""The Audio Studio wizard host dialog.

A guided, journey-aware multi-step dialog (modeled on the shipped Batch
Conversion wizard) that replaces the single-page Batch Export to Speech
dialog. Pages are stacked panels; the visible sequence depends on the journey
chosen on the start page:

- documents: Start > What to read > Voices > Chapters > Output > Book > Summary
- audio:     Start > Recordings folder > Book > Summary

Every page collects into one :class:`BatchSpeechRequest`, the same contract
the classic dialog produced, so ``batch_speech_runner`` runs unchanged. The
step position and page title are announced on every page change; Back/Next/
Start follow the standard wizard keyboard contract, and "Skip to summary"
fast-forwards a returning user whose defaults (project profile) are complete.
"""

from __future__ import annotations

import dataclasses
import logging
from collections.abc import Callable
from pathlib import Path

import wx

from quill.core.i18n import _
from quill.ui.audio_studio.pages_audio import AudioSourcePage, EditSourcePage
from quill.ui.audio_studio.pages_base import StudioPage
from quill.ui.audio_studio.pages_documents import (
    ChaptersPage,
    DocSourcePage,
    EngineOptions,
    OutputPage,
    VoicesFor,
    VoicesPage,
)
from quill.ui.audio_studio.pages_shared import BookPage, SummaryPage
from quill.ui.audio_studio.pages_start import StartPage
from quill.ui.audio_studio.request import BatchSpeechRequest
from quill.ui.dialog_contract import apply_modal_ids, show_message_box

_log = logging.getLogger(__name__)


class AudioStudioWizard(wx.Dialog):
    """The wizard host: stacked page panels with Back/Next/Start/Cancel."""

    def __init__(
        self,
        parent: wx.Window,
        *,
        defaults: BatchSpeechRequest,
        engine_options: EngineOptions,
        engine_available: dict[str, bool],
        voices_for: VoicesFor,
        on_preview: Callable[[str, str], None],
        announce_cb: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(
            parent,
            title=str(_("QUILL Audio Studio")),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
            name="audio_studio.wizard",
        )
        self._announce_cb = announce_cb
        self._defaults = defaults
        self._result: BatchSpeechRequest | None = None
        self._current_idx = -1

        self.start_page = StartPage(self)
        self.doc_source = DocSourcePage(self, defaults)
        self.voices = VoicesPage(
            self,
            defaults,
            engine_options=engine_options,
            engine_available=engine_available,
            voices_for=voices_for,
            on_preview=on_preview,
        )
        self.chapters = ChaptersPage(self, defaults)
        self.output = OutputPage(self, defaults)
        self.book = BookPage(self, defaults, forced=False)
        self.audio_source = AudioSourcePage(self, defaults)
        self.audio_book = BookPage(self, defaults, forced=True)
        self.edit_source = EditSourcePage(self)
        self.summary = SummaryPage(self)

        self._sequences: dict[str, list[StudioPage]] = {
            "documents": [
                self.start_page,
                self.doc_source,
                self.voices,
                self.chapters,
                self.output,
                self.book,
                self.summary,
            ],
            "audio": [
                self.start_page,
                self.audio_source,
                self.audio_book,
                self.summary,
            ],
            "edit": [
                self.start_page,
                self.edit_source,
            ],
        }
        self._all_pages: list[StudioPage] = [
            self.start_page,
            self.doc_source,
            self.voices,
            self.chapters,
            self.output,
            self.book,
            self.audio_source,
            self.audio_book,
            self.edit_source,
            self.summary,
        ]
        self.start_page.bind_journey_changed(self._on_journey_changed)

        self._build_ui()
        self._show_page(0)

        self.SetMinSize(wx.Size(680, 620))
        self.Fit()
        self.CentreOnParent()
        apply_modal_ids(self, affirmative_id=wx.ID_OK, cancel_id=wx.ID_CANCEL)
        self.Bind(wx.EVT_INIT_DIALOG, lambda _e: wx.CallAfter(self._focus_current_page))

    # -- layout ---------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = wx.BoxSizer(wx.VERTICAL)
        self._page_container = wx.BoxSizer(wx.VERTICAL)
        for page in self._all_pages:
            self._page_container.Add(page, proportion=1, flag=wx.EXPAND)
            page.Hide()
            page.Disable()
        outer.Add(self._page_container, proportion=1, flag=wx.EXPAND | wx.ALL, border=4)
        outer.Add(wx.StaticLine(self), flag=wx.EXPAND)

        nav = wx.BoxSizer(wx.HORIZONTAL)
        self._progress = wx.StaticText(self, name="audio_studio.progress_label")
        nav.Add(self._progress, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=8)
        nav.AddStretchSpacer()

        self._back_btn = wx.Button(self, label=_("< &Back"), name="audio_studio.back")
        self._next_btn = wx.Button(self, label=_("&Next >"), name="audio_studio.next")
        self._skip_btn = wx.Button(
            self, label=_("Skip to su&mmary"), name="audio_studio.skip_to_summary"
        )
        self._start_btn = wx.Button(self, wx.ID_OK, label=_("&Start"), name="audio_studio.start")
        self._cancel_btn = wx.Button(
            self, wx.ID_CANCEL, label=_("Cancel"), name="audio_studio.cancel"
        )
        nav.Add(self._back_btn, flag=wx.LEFT, border=4)
        nav.Add(self._next_btn, flag=wx.LEFT, border=4)
        nav.Add(self._skip_btn, flag=wx.LEFT, border=4)
        nav.Add(self._start_btn, flag=wx.LEFT, border=4)
        nav.Add(self._cancel_btn, flag=wx.LEFT | wx.RIGHT, border=8)
        outer.Add(nav, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=8)

        self._back_btn.Bind(wx.EVT_BUTTON, self._on_back)
        self._next_btn.Bind(wx.EVT_BUTTON, self._on_next)
        self._skip_btn.Bind(wx.EVT_BUTTON, self._on_skip_to_summary)
        self._start_btn.Bind(wx.EVT_BUTTON, self._on_start)
        self.Bind(wx.EVT_BUTTON, lambda _e: self.EndModal(wx.ID_CANCEL), id=wx.ID_CANCEL)

        self.SetSizer(outer)

    # -- journey / sequence -----------------------------------------------------

    def journey(self) -> str:
        return self.start_page.journey()

    def _sequence(self) -> list[StudioPage]:
        return self._sequences[self.journey()]

    def _on_journey_changed(self) -> None:
        # Only reachable while the start page is showing; the later pages of the
        # new journey are re-entered via Next as usual.
        self._sync_nav()

    # -- navigation ---------------------------------------------------------------

    def _show_page(self, idx: int) -> None:
        seq = self._sequence()
        if 0 <= self._current_idx < len(seq):
            old = seq[self._current_idx]
            old.Hide()
            old.Disable()
        self._current_idx = idx
        page = seq[idx]
        page.on_shown(self.build_request())
        page.Enable()
        page.Show()
        self.Layout()
        self._sync_nav()
        title = page.GetName()
        heading = page.FindWindowByName(f"{title}.heading", page)
        label = heading.GetLabel() if heading is not None else title
        if self._announce_cb is not None:
            self._announce_cb(
                _("Step {step} of {total}: {title}").format(
                    step=idx + 1, total=len(seq), title=label
                )
            )
        wx.CallAfter(self._focus_current_page)

    def _sync_nav(self) -> None:
        seq = self._sequence()
        idx = self._current_idx
        total = len(seq)
        self._progress.SetLabel(_("Step {step} of {total}").format(step=idx + 1, total=total))
        self._back_btn.Enable(idx > 0)
        self._next_btn.Show(idx < total - 1)
        self._skip_btn.Show(0 < idx < total - 2)
        self._start_btn.Show(idx == total - 1)
        self._start_btn.SetLabel(
            str(_("&Open in Workbench")) if self.journey() == "edit" else str(_("&Start"))
        )
        self.Layout()

    def _focus_current_page(self) -> None:
        try:
            self._sequence()[self._current_idx].SetFocus()
        except Exception:  # noqa: BLE001 - safe focus fallback
            _log.exception("Audio Studio wizard failed to set focus")

    def _validate_current(self) -> bool:
        page = self._sequence()[self._current_idx]
        valid, message = page.is_valid()
        if not valid:
            show_message_box(message, _("Please complete this step"), wx.ICON_INFORMATION, self)
        return valid

    def _on_back(self, _evt: wx.Event) -> None:
        if self._current_idx > 0:
            self._show_page(self._current_idx - 1)

    def _on_next(self, _evt: wx.Event) -> None:
        if not self._validate_current():
            return
        if self._current_idx < len(self._sequence()) - 1:
            self._show_page(self._current_idx + 1)

    def _on_skip_to_summary(self, _evt: wx.Event) -> None:
        """Fast-forward to the summary, stopping at the first page that objects."""
        seq = self._sequence()
        for idx in range(self._current_idx, len(seq) - 1):
            valid, message = seq[idx].is_valid()
            if not valid:
                self._show_page(idx)
                show_message_box(message, _("Please complete this step"), wx.ICON_INFORMATION, self)
                return
        self._show_page(len(seq) - 1)

    def _on_start(self, _evt: wx.Event) -> None:
        seq = self._sequence()
        for idx, page in enumerate(seq):
            valid, message = page.is_valid()
            if not valid:
                self._show_page(idx)
                show_message_box(message, _("Please complete this step"), wx.ICON_INFORMATION, self)
                return
        # The edit journey opens the Workbench instead of running a batch; the
        # caller reads edit_path() and no request is produced.
        if self.journey() != "edit":
            self._result = self.build_request()
        self.EndModal(wx.ID_OK)

    # -- result ---------------------------------------------------------------------

    def build_request(self, *, preview: bool = False) -> BatchSpeechRequest:
        """Collect every active page into a fresh request based on the defaults."""
        req = dataclasses.replace(self._defaults)
        for page in self._sequence():
            page.collect(req)
        req.preview = preview
        return req

    def result(self) -> BatchSpeechRequest | None:
        """The collected request after a Start, else ``None``."""
        return self._result

    def edit_path(self) -> Path | None:
        """The audiobook chosen in the edit journey (None for the other journeys)."""
        return self.edit_source.chosen_path() if self.journey() == "edit" else None
