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
from quill.core.ai.permissions import PermissionBroker, PermissionCategory, SafetyProfile
from quill.core.ai.tool_gateway import AgentIdentity, SafeEditorToolGateway

__all__ = [
    "MainFrameEditorHost",
    "run_agent",
    "run_selection_agent",
    "register_experimental_agent_command",
    "append_experimental_agent_menu",
    "experimental_gateway_enabled",
]


def experimental_gateway_enabled() -> bool:
    """True when the opt-in 2.0 agentic path is enabled (QUILL_AI_AGENT_GATEWAY)."""
    import os

    return bool(os.environ.get("QUILL_AI_AGENT_GATEWAY"))


def append_experimental_agent_menu(controller: Any, ai_menu: Any) -> None:
    """Append the opt-in 'Run Agent' AI-menu item when the gateway is enabled.

    No-ops unless ``QUILL_AI_AGENT_GATEWAY`` is set, so the default menu is
    unchanged. Kept here (not in the size-budgeted menu module) so the menu file
    only needs a single call. Runs the Writing Companion on the selection as the
    quick 'try it'; the full agent set (incl. document-scoped) is reachable via
    the ``Run Agent: ...`` command-palette entries.
    """
    if not experimental_gateway_enabled():
        return
    wx = controller._wx
    item_id = wx.NewIdRef()
    ai_menu.AppendSeparator()
    ai_menu.Append(item_id, "Run &Agent on Selection (experimental)...")
    controller.frame.Bind(
        wx.EVT_MENU, lambda _e: run_agent(controller, "writing-companion"), id=item_id
    )


def register_experimental_agent_command(controller: Any) -> None:
    """Register the opt-in agentic commands, only when explicitly enabled.

    Gated on ``QUILL_AI_AGENT_GATEWAY`` so the default build is unchanged and the
    commands do not even appear in the palette. Registers a quick selection
    command plus one ``tools.ai_agent.<id>`` command per catalog agent, so
    document-scoped agents (Accessibility Editor, Markdown Publisher, ...) are
    reachable too. Kept here (not in MainFrame) to keep the size-budgeted
    main_frame module unburdened.
    """
    if not experimental_gateway_enabled():
        return
    from quill.core.ai.agent_catalog import load_catalog

    controller.commands.register(
        "tools.ai_agent_gateway",
        "Run Agent on Selection (experimental)",
        lambda: run_agent(controller, "writing-companion"),
        None,
    )
    for agent in load_catalog().agents:
        controller.commands.register(
            "tools.ai_agent." + agent.id.replace("-", "_"),
            f"Run Agent: {agent.display_name} (experimental)",
            lambda agent_id=agent.id: run_agent(controller, agent_id),
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
        # Which apply path the preview dialog should use this turn: "selection"
        # replaces the selection, "document" replaces the whole buffer. The runner
        # sets it from the agent's scope before driving the gateway.
        self._apply_mode = "selection"

    def set_apply_mode(self, mode: str) -> None:
        self._apply_mode = mode

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
            if self._apply_mode == "document":
                self._c._ai_set_document_text(accepted_text)
            else:
                self._c._ai_replace_selection(accepted_text)
            self._applied_in_preview = True

        self._c.open_ai_diff_review(review.original, review.accept_all(), on_apply)
        return self._applied_in_preview

    def announce(self, message: str) -> None:
        self._c._set_status(message)


_SELECTION_SCOPES = (ContextScope.SELECTION, ContextScope.CURRENT_SECTION)
_DOCUMENT_SCOPES = (ContextScope.FULL_DOCUMENT, ContextScope.DOCUMENT_SUMMARY)


def _source_for_scope(controller: Any, scope: ContextScope) -> tuple[str | None, str]:
    """Return (source_text, error). ``source_text`` is None when there is an error.

    The scope decides what the agent READS: selection scopes read the selection;
    document scopes read the whole buffer.
    """
    if scope in _SELECTION_SCOPES:
        selection = controller._selected_text().strip()
        if not selection:
            return None, "Select text first."
        return selection, ""
    if scope in _DOCUMENT_SCOPES:
        document = str(controller.editor.GetValue())
        if not document.strip():
            return None, "Document is empty."
        return document, ""
    return None, "This agent's scope is not supported yet."


def _classify(agent: Any) -> tuple[str, str]:
    """Return (apply_kind, apply_mode) from the agent's WRITE permissions.

    ``apply_kind`` is ``document`` (transform whole buffer), ``selection``
    (transform the selection), or ``produce`` (output is new content, not an
    in-place edit -> opened in a new document). ``apply_mode`` tells the host
    which apply path the preview dialog should use.
    """
    overrides = agent.overrides_map()
    if PermissionCategory.MODIFY_DOCUMENT in overrides:
        return "document", "document"
    if PermissionCategory.MODIFY_SELECTION in overrides:
        return "selection", "selection"
    return "produce", "selection"


def _apply_result(
    controller: Any,
    gateway: SafeEditorToolGateway,
    host: MainFrameEditorHost,
    agent: Any,
    apply_kind: str,
    apply_mode: str,
    proposed: str,
) -> None:
    """Apply the model output per its kind, on the UI thread."""
    host.set_apply_mode(apply_mode)
    if apply_kind == "document":
        original = str(controller.editor.GetValue())
        gateway.apply_text_patch(original, proposed, label=agent.display_name)
    elif apply_kind == "selection":
        gateway.replace_selection(proposed, label=agent.display_name)
    else:  # produce: non-destructive, open the result in a new document
        controller._ai_open_new_document(proposed)
        controller._set_status(f"{agent.display_name}: opened result in a new document.")


def run_agent(
    controller: Any, agent_id: str = "writing-companion", *, instruction: str = ""
) -> None:
    """Run a catalog agent through the gateway, at whatever scope it declares.

    Selection-scope agents transform the selection; document-scope agents
    transform the whole buffer (preview-gated); read-only agents open their output
    in a new document. Threading mirrors ``_run_agent_task``: the provider call is
    on a daemon thread, every wx touch (preview, apply, announce) is marshalled
    back to the UI thread via ``wx.CallAfter``. Experimental / opt-in only.
    """
    import threading

    import wx

    from quill.core.ai.agent_catalog import load_catalog
    from quill.core.ai.model_manager import load_ai_enabled
    from quill.core.ai.provider_backend import ProviderChatBackend

    if not load_ai_enabled():
        controller._set_status("AI is turned off. Enable it in the AI menu.")
        return

    agent = next((a for a in load_catalog().agents if a.id == agent_id), None)
    if agent is None:
        controller._set_status(f"Unknown agent: {agent_id}")
        return

    source, error = _source_for_scope(controller, agent.default_scope)
    if source is None:
        controller._set_status(error)
        return

    backend = ProviderChatBackend()
    available, reason = backend.is_available()
    if not available:
        controller._set_status(reason or "AI provider is not available.")
        return

    apply_kind, apply_mode = _classify(agent)
    host = MainFrameEditorHost(controller)
    gateway = SafeEditorToolGateway(
        host=host,
        broker=PermissionBroker(SafetyProfile.BALANCED, overrides=agent.overrides_map()),
        activity=ActivityLog(),
        identity=AgentIdentity(agent_id=agent.id, risk=agent.risk),
        emit=EventBridge(AnnouncementLevel.BALANCED, controller._set_status).handle,
    )
    responder = responder_from_backend(backend)
    ctx = AIContext(prompt=instruction, context_text=source, file_type=host.get_file_type())
    controller._set_status(f"{agent.display_name}: generating...")

    def _run() -> None:
        try:
            proposed = responder(agent, ctx)
        except Exception as exc:  # noqa: BLE001 - surface provider errors, never crash
            wx.CallAfter(controller._set_status, f"{agent.display_name} error: {exc}")
            return

        def _apply() -> None:
            try:
                _apply_result(controller, gateway, host, agent, apply_kind, apply_mode, proposed)
            except Exception as exc:  # noqa: BLE001
                controller._set_status(f"{agent.display_name} error: {exc}")

        wx.CallAfter(_apply)

    threading.Thread(target=_run, daemon=True).start()  # GATE-40-OK: AI bg thread


def run_selection_agent(controller: Any, agent_id: str = "writing-companion") -> None:
    """Back-compat thin wrapper; prefer :func:`run_agent`."""
    run_agent(controller, agent_id)
