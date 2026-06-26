"""Wire the 2.0 Safe Editor Tool Gateway to the real editor (opt-in, default off).

This is the UI adapter that lets the new agentic framework drive the actual
QUILL editor, reusing the *exact* primitives the shipping Ask Quill chat already
uses (`_ai_replace_selection`, `_record_persistent_undo_state`,
`open_ai_diff_review`, `_set_status`), so edit/undo/diff behavior is identical to
today.

It is **opt-in and inert by default**: nothing imports this module unless the
experimental command is enabled (the command is only registered when the
``QUILL_AI_AGENT_GATEWAY`` environment variable is set). The legacy chat path is
untouched and remains the default.

:class:`MainFrameEditorHost` implements the gateway's ``EditorHost`` Protocol over
a MainFrame controller. :func:`run_selection_agent` orchestrates one run with
correct threading: the provider/model call happens on a background thread (the
same pattern as ``_run_agent_task``), and every wx touch — the diff preview, the
apply, the announcements — happens back on the UI thread via ``wx.CallAfter``.
"""

from __future__ import annotations

from typing import Any

from quill.core.ai.activity_log import ActivityLog
from quill.core.ai.context_builder import ContextScope
from quill.core.ai.diff_review import DiffReview
from quill.core.ai.event_bridge import AnnouncementLevel, EventBridge
from quill.core.ai.harness import AIContext
from quill.core.ai.harness.native import responder_from_backend
from quill.core.ai.permissions import PermissionBroker, SafetyProfile
from quill.core.ai.tool_gateway import AgentIdentity, SafeEditorToolGateway

__all__ = [
    "MainFrameEditorHost",
    "run_selection_agent",
    "register_experimental_agent_command",
]


def register_experimental_agent_command(controller: Any) -> None:
    """Register the opt-in agentic command, only when explicitly enabled.

    Gated on ``QUILL_AI_AGENT_GATEWAY`` so the default build is unchanged and the
    command does not even appear in the palette. Kept here (not in MainFrame) so
    the wiring adds essentially nothing to the size-budgeted main_frame module.
    """
    import os

    if not os.environ.get("QUILL_AI_AGENT_GATEWAY"):
        return
    controller.commands.register(
        "tools.ai_agent_gateway",
        "Run Agent on Selection (experimental)",
        lambda: run_selection_agent(controller),
        None,
    )


class MainFrameEditorHost:
    """``EditorHost`` over a MainFrame controller, reusing existing primitives.

    The ``controller`` is the live ``MainFrame`` (it exposes ``editor`` and the
    ``_ai_*`` helpers). Because the real per-hunk diff dialog
    (``open_ai_diff_review``) both reviews *and* applies the accepted hunks, this
    host applies inside :meth:`preview_diff` and then makes the gateway's
    follow-up checkpoint/apply a no-op for that turn (tracked by
    ``_applied_in_preview``), so a previewed edit is never applied twice and the
    user's per-hunk choices are honored.
    """

    def __init__(self, controller: Any) -> None:
        self._c = controller
        self._applied_in_preview = False

    # -- reads -------------------------------------------------------------

    def get_document(self) -> str:
        return str(self._c.editor.GetValue())

    def get_selection(self) -> str:
        return str(self._c.editor.GetStringSelection())

    def get_outline(self) -> list[str]:
        try:
            return [entry.title for entry in self._c._outline_entries()]
        except Exception:  # outline is best-effort context, never fatal
            return []

    def get_file_type(self) -> str:
        path = getattr(getattr(self._c, "document", None), "path", None)
        if path is None:
            return ""
        suffix = str(path).rsplit(".", 1)
        return suffix[-1].lower() if len(suffix) == 2 else ""

    # -- mutations (reusing the shipping undo/replace path) ----------------

    def create_undo_checkpoint(self, label: str) -> None:
        if self._applied_in_preview:
            return  # the preview dialog already checkpointed before applying
        self._c._record_persistent_undo_state(str(self._c.editor.GetValue()))

    def apply_replacement(self, text: str) -> None:
        if self._applied_in_preview:
            self._applied_in_preview = False  # already applied the accepted hunks
            return
        self._c._ai_replace_selection(text)

    def apply_insert(self, text: str) -> None:
        self._c._ai_insert_text(text)

    def apply_document_text(self, text: str) -> None:
        if self._applied_in_preview:
            self._applied_in_preview = False
            return
        self._c._ai_set_document_text(text)

    def run_command(self, command_id: str) -> None:
        self._c._ai_run_command(command_id)

    # -- prompts -----------------------------------------------------------

    def confirm(self, message: str) -> bool:
        # Route through MainFrame's sanctioned message-box path (GATE-16), not a
        # raw wx.MessageBox, so z-order parent + SR announcement wrappers apply.
        wx = self._c._wx
        result = self._c._show_message_box(message, "QUILL", wx.YES_NO | wx.ICON_QUESTION)
        return result == wx.YES

    def preview_diff(self, review: DiffReview) -> bool:
        """Show the real per-hunk review dialog; apply the accepted hunks.

        Returns whether the user applied anything. Applying happens here (via the
        dialog's ``on_apply``) so per-hunk choices are honored; the gateway's
        subsequent checkpoint/apply then no-op for this turn.
        """
        self._applied_in_preview = False

        def on_apply(accepted_text: str) -> None:
            self._c._record_persistent_undo_state(str(self._c.editor.GetValue()))
            self._c._ai_replace_selection(accepted_text)
            self._applied_in_preview = True

        self._c.open_ai_diff_review(review.original, review.accept_all(), on_apply)
        return self._applied_in_preview

    def announce(self, message: str) -> None:
        self._c._set_status(message)


def run_selection_agent(
    controller: Any,
    agent_id: str = "writing-companion",
    *,
    instruction: str = "Improve the selected text for clarity and tone.",
) -> None:
    """Run a catalog agent on the current selection through the gateway.

    Threading mirrors ``_run_agent_task``: the provider call runs on a daemon
    thread; the gateway apply (preview dialog, replace, announce) is marshalled
    back to the UI thread with ``wx.CallAfter``. Experimental / opt-in only.
    """
    import threading

    import wx

    from quill.core.ai.agent_catalog import load_catalog
    from quill.core.ai.model_manager import load_ai_enabled
    from quill.core.ai.provider_backend import ProviderChatBackend

    if not load_ai_enabled():
        controller._set_status("AI is turned off. Enable it in the AI menu.")
        return

    selection = controller._selected_text().strip()
    if not selection:
        controller._set_status("Select text first.")
        return

    backend = ProviderChatBackend()
    available, reason = backend.is_available()
    if not available:
        controller._set_status(reason or "AI provider is not available.")
        return

    agent = next((a for a in load_catalog().agents if a.id == agent_id), None)
    if agent is None:
        controller._set_status(f"Unknown agent: {agent_id}")
        return
    if agent.default_scope not in (ContextScope.SELECTION, ContextScope.CURRENT_SECTION):
        # v1 wiring is selection-scoped; document/workspace scopes come later.
        controller._set_status(f"{agent.display_name} is not a selection agent.")
        return

    host = MainFrameEditorHost(controller)
    broker = PermissionBroker(SafetyProfile.BALANCED, overrides=agent.overrides_map())
    bridge = EventBridge(AnnouncementLevel.BALANCED, controller._set_status)
    gateway = SafeEditorToolGateway(
        host=host,
        broker=broker,
        activity=ActivityLog(),
        identity=AgentIdentity(agent_id=agent.id, risk=agent.risk),
        emit=bridge.handle,
    )
    responder = responder_from_backend(backend)
    ctx = AIContext(prompt=instruction, context_text=selection, file_type=host.get_file_type())
    controller._set_status(f"{agent.display_name}: generating...")

    def _run() -> None:
        try:
            proposed = responder(agent, ctx)
        except Exception as exc:  # noqa: BLE001 - surface provider errors, never crash
            wx.CallAfter(controller._set_status, f"{agent.display_name} error: {exc}")
            return

        def _apply() -> None:
            try:
                gateway.replace_selection(proposed, label=agent.display_name)
            except Exception as exc:  # noqa: BLE001
                controller._set_status(f"{agent.display_name} error: {exc}")

        wx.CallAfter(_apply)

    threading.Thread(target=_run, daemon=True).start()  # GATE-40-OK: AI bg thread
