"""The "Ask Quill" AI chat dialog.

A conversation with Quill's on-device assistant (Apple Foundation Models on
macOS). Each turn the assistant decides whether to answer in chat, insert or
replace text in the document, or run a Quill command — and acts on the editor
live via callbacks. The conversation is shown as a scrollable list of message
rows (each "You" / "Quill" message is its own element, which is also better for
screen-reader navigation); the message field is labeled; generation runs off
the UI thread.
"""
from __future__ import annotations

import threading

SUGGESTED_PROMPTS: tuple[str, ...] = (
    "Summarize this document",
    "Fix spelling and grammar",
    "Write an introduction for this",
    "List the key action items",
    "Save the document",
    "Read this aloud",
)


class AskQuillChatDialog:
    def __init__(
        self,
        parent: object,
        assistant: object,
        *,
        get_document,
        get_selection,
        insert_text,
        replace_selection,
        run_command,
        tool_catalog: list[tuple[str, str]],
        announce=None,
    ) -> None:
        import wx
        from wx.lib.scrolledpanel import ScrolledPanel

        self._wx = wx
        self._assistant = assistant
        self._get_document = get_document
        self._get_selection = get_selection
        self._insert_text = insert_text
        self._replace_selection = replace_selection
        self._run_command = run_command
        self._tool_titles = dict(tool_catalog)
        self._tool_ids = tuple(tid for tid, _ in tool_catalog)
        self._announce = announce or (lambda _m: None)
        self._last_response = ""

        self.dialog = wx.Dialog(
            parent, title="Ask Quill", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.dialog.SetSize((720, 640))
        outer = wx.BoxSizer(wx.VERTICAL)

        outer.Add(wx.StaticText(self.dialog, label="Conversation"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 14)
        # Scrollable message list — one row per message.
        self.messages = ScrolledPanel(self.dialog, style=wx.BORDER_SIMPLE | wx.VSCROLL)
        self.messages.SetName("Conversation")
        self.messages_sizer = wx.BoxSizer(wx.VERTICAL)
        self.messages.SetSizer(self.messages_sizer)
        self.messages.SetupScrolling(scroll_x=False)
        self._you_bg = wx.Colour(232, 240, 254)
        self._quill_bg = wx.Colour(238, 238, 238)
        outer.Add(self.messages, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 14)

        outer.Add(wx.StaticText(self.dialog, label="Suggestions"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 14)
        suggestions = wx.WrapSizer(wx.HORIZONTAL)
        self._suggestion_buttons = []
        for text in SUGGESTED_PROMPTS:
            button = wx.Button(self.dialog, label=text)
            button.Bind(wx.EVT_BUTTON, lambda _e, t=text: self._submit(t))
            suggestions.Add(button, 0, wx.RIGHT | wx.BOTTOM, 6)
            self._suggestion_buttons.append(button)
        outer.Add(suggestions, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 14)

        outer.Add(wx.StaticText(self.dialog, label="Your message"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 14)
        input_row = wx.BoxSizer(wx.HORIZONTAL)
        self.input = wx.TextCtrl(self.dialog, style=wx.TE_PROCESS_ENTER)
        self.input.SetName("Your message to Quill")
        self.input.SetHint("Ask Quill to write, edit, or run something…")
        input_row.Add(self.input, 1, wx.EXPAND | wx.RIGHT, 8)
        self.send_button = wx.Button(self.dialog, label="Send")
        self.send_button.SetDefault()
        input_row.Add(self.send_button, 0)
        outer.Add(input_row, 0, wx.EXPAND | wx.ALL, 14)

        # Approval bar — nothing is applied to the document until you approve.
        self._pending = None
        self.approval_label = wx.StaticText(self.dialog, label="")
        self.approve_button = wx.Button(self.dialog, label="Approve")
        self.discard_button = wx.Button(self.dialog, label="Discard")
        approval = wx.BoxSizer(wx.HORIZONTAL)
        approval.Add(self.approval_label, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        approval.Add(self.approve_button, 0, wx.RIGHT, 8)
        approval.Add(self.discard_button, 0)
        outer.Add(approval, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 14)
        self._show_approval(False)

        footer = wx.BoxSizer(wx.HORIZONTAL)
        self.copy_button = wx.Button(self.dialog, label="Copy Last Response")
        self.copy_button.Enable(False)
        footer.Add(self.copy_button, 0, wx.RIGHT, 8)
        footer.AddStretchSpacer()
        footer.Add(wx.Button(self.dialog, wx.ID_CANCEL, label="Close"), 0)
        outer.Add(footer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 14)
        self.dialog.SetSizer(outer)

        self.input.Bind(wx.EVT_TEXT_ENTER, lambda _e: self._submit(self.input.GetValue()))
        self.send_button.Bind(wx.EVT_BUTTON, lambda _e: self._submit(self.input.GetValue()))
        self.approve_button.Bind(wx.EVT_BUTTON, self._on_approve)
        self.discard_button.Bind(wx.EVT_BUTTON, self._on_discard)
        self.copy_button.Bind(wx.EVT_BUTTON, self._on_copy)
        self.dialog.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

        available, reason = assistant.is_available()
        if not available:
            self._append("Quill", f"On-device AI is unavailable: {reason}")
            self._set_busy(True)
        else:
            self._append("Quill", "Hi! Ask me to write, edit, or run something in your document.")

    def _on_char_hook(self, event: object) -> None:
        wx = self._wx
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.dialog.EndModal(wx.ID_CANCEL)
            return
        event.Skip()

    def _append(self, speaker: str, text: str) -> None:
        wx = self._wx
        row = wx.Panel(self.messages)
        row.SetBackgroundColour(self._you_bg if speaker == "You" else self._quill_bg)
        row_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(row, label=f"{speaker}: {text}")
        width = max(self.messages.GetClientSize().width - 50, 420)
        label.Wrap(width)
        # One combined element per message → VoiceOver reads it as a single item.
        row.SetName(f"{speaker} message")
        row_sizer.Add(label, 0, wx.ALL, 8)
        row.SetSizer(row_sizer)
        self.messages_sizer.Add(row, 0, wx.EXPAND | wx.ALL, 5)
        self.messages.Layout()
        self.messages.SetupScrolling(scroll_x=False, scrollToTop=False)
        self.messages.ScrollChildIntoView(row)

    def _set_busy(self, busy: bool) -> None:
        self.send_button.Enable(not busy)
        self.input.Enable(not busy)
        for button in self._suggestion_buttons:
            button.Enable(not busy)

    def _submit(self, message: str) -> None:
        message = (message or "").strip()
        if not message:
            self.input.SetFocus()
            return
        self._append("You", message)
        self.input.SetValue("")
        self._set_busy(True)
        self._announce("Working")
        document = self._get_document()

        selection = self._get_selection()

        def worker() -> None:
            try:
                decision = self._assistant.decide(message, document, self._tool_ids)
                action = decision.action
                if action == "run" and decision.tool:
                    result = ("run", "", decision.tool, "")
                elif action == "insert":
                    text = self._assistant.write_for_document(message, document)
                    result = ("insert", text, "", "")
                elif action == "replace":
                    if selection:
                        text = self._assistant.rewrite_selection(message, selection)
                    else:
                        text = self._assistant.write_for_document(message, document)
                    result = ("replace", text, "", "")
                else:
                    text = self._assistant.answer(message, document)
                    result = ("answer", text, "", "")
            except Exception as exc:  # noqa: BLE001
                result = ("error", "", "", str(exc))
            self._wx.CallAfter(self._apply, *result)

        threading.Thread(target=worker, daemon=True).start()

    def _show_approval(self, show: bool, label: str = "") -> None:
        self.approval_label.SetLabel(label)
        self.approve_button.Show(show)
        self.discard_button.Show(show)
        self.approve_button.Enable(show)
        self.discard_button.Enable(show)
        self.dialog.Layout()

    def _apply(self, action: str, text: str, tool: str, error: str) -> None:
        # Nothing touches the document automatically — propose, then await approval.
        if action == "error":
            self._append("Quill", f"Error: {error}")
        elif action == "run" and tool:
            title = self._tool_titles.get(tool, tool)
            self._pending = ("run", "", tool)
            self._append("Quill", f"I'd like to run: {title}. Approve to run it.")
            self._show_approval(True, f"Run “{title}”?")
        elif action in ("insert", "replace") and text:
            self._last_response = text
            self._pending = (action, text, "")
            verb = "insert this at the cursor" if action == "insert" else "replace the selection with this"
            self._append("Quill", f"I'd like to {verb} (approve to apply):\n{text}")
            self._show_approval(True, "Apply this to the document?")
        else:
            self._last_response = text
            self._append("Quill", text or "(no response)")
        self.copy_button.Enable(bool(self._last_response))
        self._set_busy(False)
        if self._pending:
            self._announce("Quill is proposing a change. Approve or discard.")
            self.approve_button.SetFocus()
        else:
            self._announce("Response ready")
            self.input.SetFocus()

    def _on_approve(self, _event: object) -> None:
        if not self._pending:
            return
        action, text, tool = self._pending
        self._pending = None
        self._show_approval(False)
        try:
            if action == "run":
                title = self._tool_titles.get(tool, tool)
                self._run_command(tool)
                self._append("Quill", f"Ran: {title}")
            elif action == "insert":
                self._insert_text(text)
                self._append("Quill", "Inserted into the document.")
            elif action == "replace":
                if self._get_selection():
                    self._replace_selection(text)
                    self._append("Quill", "Replaced the selection.")
                else:
                    self._insert_text(text)
                    self._append("Quill", "No selection — inserted at the cursor.")
        except Exception as exc:  # noqa: BLE001
            self._append("Quill", f"Couldn't apply that: {exc}")
        self._announce("Applied")
        self.input.SetFocus()

    def _on_discard(self, _event: object) -> None:
        self._pending = None
        self._show_approval(False)
        self._append("Quill", "Discarded — nothing was changed.")
        self._announce("Discarded")
        self.input.SetFocus()

    def _on_copy(self, _event: object) -> None:
        wx = self._wx
        if not self._last_response:
            return
        if wx.TheClipboard.Open():
            try:
                wx.TheClipboard.SetData(wx.TextDataObject(self._last_response))
            finally:
                wx.TheClipboard.Close()
            self._announce("Copied last response to clipboard")

    def show(self) -> None:
        self.dialog.CentreOnParent()
        try:
            self.input.SetFocus()
            self.dialog.ShowModal()
        finally:
            self.dialog.Destroy()
