"""Structured List Studio command wiring (F2).

A thin :class:`~quill.ui.main_frame.MainFrame` mixin that opens the accessible
:class:`~quill.ui.list_studio_dialog.ListStudioDialog`, builds its initial model
context-sensitively (convert the selection, or start a fresh blank list), and
applies the generated source as a single undoable edit (PRD §2.2 context-
sensitive F2, §28 one undoable operation). All list logic lives in
``quill.core.lists``; this is wiring only.
"""

from __future__ import annotations


class ListStudioMixin:
    """The ``format.list_studio`` command handler (context-sensitive F2)."""

    # Relies on MainFrame helpers: _wx, frame, editor, document, settings,
    # _show_modal_dialog, _show_message_box, _set_status, _announce,
    # _atomic_replace, _feature_enabled, _document_is_read_only,
    # _effective_markup_kind.

    def open_list_studio(self) -> None:
        """Open the Structured List Studio for the selection or a new list (F2)."""
        if not self._feature_enabled("core.format"):
            self._set_status("Structured List Studio is unavailable in this profile")
            return
        if self._document_is_read_only():
            self._set_status("Document is read-only")
            return

        from quill.core.lists import (
            FlatList,
            ListItem,
            ListType,
            find_list_block,
            interpret_selection,
            list_block_to_flat,
        )
        from quill.ui.dialog_contract import apply_modal_ids
        from quill.ui.list_studio_dialog import ListStudioDialog

        wx = self._wx
        target_format = "html" if self._effective_markup_kind() == "html" else "markdown"
        settings = self._structured_list_settings()

        start, end = self.editor.GetSelection()
        flat = FlatList(list_type=ListType.BULLET, items=[ListItem("")])
        in_place = False
        if end > start:
            selected = self.editor.GetValue()[start:end]
            interpreted = interpret_selection(selected, settings)
            items = [
                ListItem(text=content, checked=checked)
                for content, _kind, checked in interpreted
                if content.strip() or len(interpreted) == 1
            ]
            if items:
                # If every line carried a task marker, open as a checklist.
                list_type = (
                    ListType.CHECKLIST
                    if all(kind == "task" for _c, kind, _ck in interpreted)
                    else ListType.BULLET
                )
                flat = FlatList(list_type=list_type, items=items)
        else:
            # No selection: if the caret sits inside an existing list, edit that
            # list in place (§4.2) rather than starting a fresh one. The detected
            # block becomes the replace range, so OK rewrites just that list and
            # its nesting levels are preserved.
            block = find_list_block(self.editor.GetValue(), self.editor.GetInsertionPoint())
            if block is not None:
                start, end = block
                flat = list_block_to_flat(self.editor.GetValue()[start:end], settings)
                in_place = True

        studio = ListStudioDialog(
            wx,
            flat=flat,
            settings=settings,
            target_format=target_format,
            confirm_conversion=self._confirm_list_conversion,
        )
        dialog = wx.Dialog(
            self.frame,
            title="Structured List Studio",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        outer = studio.populate(dialog)
        buttons = dialog.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        outer.Add(buttons, 0, wx.EXPAND | wx.ALL, 10)
        studio.finalize()
        apply_modal_ids(
            dialog,
            affirmative_id=wx.ID_OK,
            affirmative_label="&Replace list" if in_place else "&Insert list",
            cancel_id=wx.ID_CANCEL,
            cancel_label="Cancel",
        )
        try:
            if self._show_modal_dialog(dialog, "Structured List Studio") != wx.ID_OK:
                self._set_status("Structured List Studio cancelled")
                return
            source = studio.result_source
            summary = studio.summary
            issues = studio.validation_issues()
        finally:
            dialog.Destroy()

        if not source.strip():
            self._set_status("Structured List Studio: nothing to insert")
            return
        # §26: reparse-and-validate before replacing document text. On any issue
        # the document is left unchanged and the problem is surfaced.
        if issues:
            self._show_message_box(
                "The list was not inserted:\n\n" + "\n".join(f"• {issue}" for issue in issues),
                "Structured List Studio",
                wx.OK | wx.ICON_WARNING,
            )
            self._set_status("Structured List Studio: list not inserted (validation)")
            return
        # Replace the captured range: the in-place list block, the original
        # selection, or the caret (empty range) for a fresh insert.
        self._apply_list_studio_source(source, start, end)
        verb = "Replaced" if in_place else "Inserted"
        self._announce(f"{summary} {verb}. Press Control+Z to undo.")
        self._set_status(summary)

    def _apply_list_studio_source(self, source: str, start: int, end: int) -> None:
        """Replace the captured ``start``..``end`` range as one undo step."""
        self._atomic_replace(start, end, source)
        self.document.set_text(self.editor.GetValue())

    def _confirm_list_conversion(self, reasons: list[str]) -> bool:
        """Warn before a lossy list-type conversion and return the user's choice (§19.4).

        Routed through the hardened message box so the screen-reader entry/exit
        announcement and focus return apply. Yes proceeds with the conversion; No
        leaves the list unchanged.
        """
        wx = self._wx
        detail = "\n".join(f"• {reason}" for reason in reasons)
        message = f"Changing the list type will lose some structure:\n\n{detail}\n\nConvert anyway?"
        result = self._show_message_box(
            message, "Convert list type", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )
        return result == wx.ID_YES

    def _structured_list_settings(self) -> object:
        """Build the studio settings, resolving the Markdown definition profile.

        Defaults come straight from the PRD's recommended values; a Markdown
        document advertises a Pandoc-compatible definition profile so the common
        case generates native definition syntax, while HTML documents always have
        valid ``<dl>`` output available.
        """
        from quill.core.lists import StructuredListSettings
        from quill.core.lists.settings import DefinitionMarkdownProfile

        settings = StructuredListSettings()
        if self._effective_markup_kind() == "html":
            settings.definition_markdown_profile = DefinitionMarkdownProfile.HTML_FALLBACK
        else:
            settings.definition_markdown_profile = DefinitionMarkdownProfile.PANDOC
        return settings

    def _register_list_studio_commands(self) -> None:
        self.commands.try_register(
            "format.list_studio",
            "Structured List Studio",
            self.open_list_studio,
            self._binding_for("format.list_studio"),
            feature_id="core.format",
        )
