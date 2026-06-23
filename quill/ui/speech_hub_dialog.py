"""Speech Hub dialog — unified Read Aloud + Dictation settings in one tabbed window.

Replaces the two separate dialogs (VoiceBrowserDialog for TTS, SpeechSetupDialog
for STT) with a single ``wx.Notebook``-based dialog so users can switch between
TTS and STT settings without closing and reopening different dialogs.

Preview works without closing the hub.  Download and export actions close the
hub so the caller can start the background operation; after completion the hub
is reopened on the same tab via the existing ``on_ok`` callback pattern.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from quill.ui.dialog_contract import apply_modal_ids

if TYPE_CHECKING:
    from collections.abc import Callable

    from quill.ui.speech_setup_dialog import SpeechSetupResult
    from quill.ui.voice_browser_dialog import VoiceBrowserResult


class SpeechHubDialog:
    """Unified Speech Settings dialog with Read Aloud and Dictation tabs.

    Parameters
    ----------
    parent:
        wx parent window.
    read_aloud_kwargs:
        Keyword arguments forwarded to ``VoiceBrowserDialog`` (all except
        ``embed_in`` and ``on_action``).
    dictation_kwargs:
        Keyword arguments forwarded to ``SpeechSetupDialog`` (all except
        ``embed_in`` and ``on_action``).
    initial_tab:
        Which tab to select initially (0 = Read Aloud, 1 = Dictation).
    """

    def __init__(
        self,
        parent: object,
        *,
        read_aloud_kwargs: dict,
        dictation_kwargs: dict,
        initial_tab: int = 0,
    ) -> None:
        import wx

        self._wx = wx
        self._ra_action: VoiceBrowserResult | None = None
        self._dict_action: SpeechSetupResult | None = None

        self.dialog = wx.Dialog(
            parent,
            title="Speech Settings",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetMinSize(wx.Size(640, 580))
        self.dialog.SetSize(wx.Size(740, 660))

        root = wx.BoxSizer(wx.VERTICAL)
        self._nb = wx.Notebook(self.dialog)

        # Read Aloud tab
        ra_page = wx.Panel(self._nb)
        from quill.ui.voice_browser_dialog import VoiceBrowserDialog

        self._voice_browser = VoiceBrowserDialog(
            ra_page,
            embed_in=ra_page,
            on_action=self._on_ra_action,
            **read_aloud_kwargs,
        )
        self._nb.AddPage(ra_page, "Read Aloud")

        # Dictation tab
        dict_page = wx.Panel(self._nb)
        from quill.ui.speech_setup_dialog import SpeechSetupDialog

        self._speech_setup = SpeechSetupDialog(
            dict_page,
            embed_in=dict_page,
            on_action=self._on_dict_action,
            **dictation_kwargs,
        )
        self._nb.AddPage(dict_page, "Dictation")

        if 0 <= initial_tab < self._nb.GetPageCount():
            self._nb.SetSelection(initial_tab)

        root.Add(self._nb, 1, wx.EXPAND | wx.ALL, 6)

        # Dialog-level OK / Cancel
        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self.dialog, id=wx.ID_OK)
        cancel_btn = wx.Button(self.dialog, id=wx.ID_CANCEL)
        btn_row.AddStretchSpacer()
        btn_row.Add(ok_btn, 0, wx.RIGHT, 6)
        btn_row.Add(cancel_btn, 0)
        root.Add(btn_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        apply_modal_ids(self.dialog, affirmative_id=wx.ID_OK, escape_id=wx.ID_CANCEL)
        self.dialog.SetSizer(root)

    # ------------------------------------------------------------------
    # Internal callbacks from embedded panels
    # ------------------------------------------------------------------

    def _on_ra_action(self, result: VoiceBrowserResult) -> None:
        """Download / export triggered from the Read Aloud tab — close hub."""
        self._ra_action = result
        self.dialog.EndModal(self._wx.ID_OK)

    def _on_dict_action(self, result: SpeechSetupResult) -> None:
        """Any action triggered from the Dictation tab — close hub."""
        self._dict_action = result
        self.dialog.EndModal(self._wx.ID_OK)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def show(
        self, show_modal_dialog: Callable
    ) -> tuple[VoiceBrowserResult | None, SpeechSetupResult | None]:
        """Open the hub.

        Returns ``(ra_result, dict_result)`` where each is ``None`` when no
        action was taken in that tab.  When the user clicks the dialog-level
        OK button without triggering a specific action, the current Read Aloud
        selection is collected and returned as a ``'select'`` result.
        """
        result_code = show_modal_dialog(self.dialog, "Speech Settings")
        ra_result = self._ra_action
        dict_result = self._dict_action
        if result_code == self._wx.ID_OK and ra_result is None and dict_result is None:
            ra_result = self._voice_browser.collect_result()
        self.dialog.Destroy()
        return ra_result, dict_result
