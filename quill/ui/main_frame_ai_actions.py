"""AI writing-action mixin for MainFrame (extracted for CQ-1 / GATE-11).

These selection-oriented AI commands (rewrite, summarize, continue, fix
grammar) and their shared guards were lifted out of ``main_frame.py`` to keep
that module under its GATE-11 module-size budget. Every method references
``self`` attributes and helpers that live on :class:`MainFrame`
(``self.editor``, ``self._selected_text``, ``self._set_status``,
``self.open_writing_assistant``), so each call resolves identically through the
method-resolution order. No behavior changed.
"""

from __future__ import annotations

from quill.core.assistant import render_assistant_prompt
from quill.core.selection import paragraph_span


class AiActionsMixin:
    """Selection-scoped AI writing actions, mixed into MainFrame."""

    def open_ai_rewrite_selection(self) -> None:
        if not self._require_ai_enabled():
            return
        target, scope = self._ai_target_text(fallback="paragraph")
        if not target.strip():
            self._set_status("Nothing to rewrite. Type or select some text first.")
            return
        self._announce_ai_scope("Rewriting", scope, target)
        self.open_writing_assistant(
            render_assistant_prompt(
                "rewrite",
                selection_text=target,
                document_text=self.editor.GetValue(),
            )
        )

    def open_ai_summarize_selection(self) -> None:
        if not self._require_ai_enabled():
            return
        target, scope = self._ai_target_text(fallback="document")
        if not target.strip():
            self._set_status("Nothing to summarize. Open or type a document first.")
            return
        self._announce_ai_scope("Summarizing", scope, target)
        self.open_writing_assistant(
            render_assistant_prompt(
                "summarize",
                selection_text=target,
                document_text=self.editor.GetValue(),
            )
        )

    def open_ai_continue_writing(self) -> None:
        if not self._require_ai_enabled():
            return
        target = self._selected_text() or self.editor.GetValue()
        if not target.strip():
            self._set_status("Nothing to continue from. Type some text first.")
            return
        self.open_writing_assistant(
            render_assistant_prompt(
                "continue",
                selection_text=target,
                document_text=self.editor.GetValue(),
            )
        )

    def open_ai_fix_grammar(self) -> None:
        if not self._require_ai_enabled():
            return
        target, scope = self._ai_target_text(fallback="paragraph")
        if not target.strip():
            self._set_status("Nothing to check. Type or select some text first.")
            return
        self._announce_ai_scope("Checking grammar in", scope, target)
        self.open_writing_assistant(
            render_assistant_prompt(
                "grammar",
                selection_text=target,
                document_text=self.editor.GetValue(),
            )
        )

    def _require_ai_enabled(self) -> bool:
        """Return True when AI is on; otherwise announce how to enable it.

        Menu items are greyed out while AI is off, but these actions are also
        reachable via the command palette and keybindings, so guard here too.
        """
        from quill.core.ai.availability import AI_DISABLED_MESSAGE
        from quill.core.ai.model_manager import load_ai_enabled

        if load_ai_enabled():
            return True
        self._set_status(AI_DISABLED_MESSAGE)
        return False

    def _ai_target_text(self, *, fallback: str) -> tuple[str, str]:
        """Resolve the text an AI writing action should operate on.

        Returns ``(text, scope_label)``. When there is a selection it wins. With
        no selection we fall back to the current paragraph or the whole document
        so the action still does something useful instead of sending an empty
        prompt.
        """
        selected = self._selected_text()
        if selected:
            return selected, "selection"
        text = self.editor.GetValue()
        if fallback == "document":
            return text, "document"
        cursor = self.editor.GetInsertionPoint()
        start, end = paragraph_span(text, cursor)
        return text[start:end], "paragraph"

    def _announce_ai_scope(self, verb: str, scope: str, target: str) -> None:
        from quill.core.announcements import format_progress

        word_count = len(target.split())
        self._set_status(format_progress(verb, scope, count=word_count))
