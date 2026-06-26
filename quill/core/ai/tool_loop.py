"""Native multi-step tool-calling loop (PRD §8.1, §10, §14).

The base Native harness does a single generate-and-apply pass. This module adds
the real agent loop: the model takes multiple steps, each either a **tool call**
(read selection, read document, replace selection, apply a patch, run a command)
or a **final** answer. Every tool call goes through the
:class:`~quill.core.ai.tool_gateway.SafeEditorToolGateway`, so the broker's
permission checks, the diff preview, undo checkpoints, and the audit log all apply
to every step; every step emits normalized :class:`AgentEvent`s.

The loop is provider-neutral and fully testable because the model is abstracted
behind :class:`ToolPlanner`: ``next_step`` returns the next :class:`ToolStep`
given the agent, context, and the transcript so far. A real planner wraps a
function-calling model; tests use a scripted planner. The loop never references
wx.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from quill.core.ai.events import AgentEvent, AgentEventKind
from quill.core.ai.harness import AgentSpec, AIContext, HarnessResult
from quill.core.ai.tool_gateway import Emit, PermissionDeniedError, SafeEditorToolGateway

__all__ = [
    "ToolStep",
    "ToolResult",
    "ToolPlanner",
    "run_tool_loop",
    "MAX_STEPS",
]

MAX_STEPS = 8


@dataclass(frozen=True, slots=True)
class ToolStep:
    """One planner decision: a tool call, or the final answer.

    ``kind`` is ``"tool"`` or ``"final"``. For a tool step, ``tool`` is the tool
    name and ``args`` its string arguments (e.g. ``{"text": ...}``,
    ``{"proposed": ..., "original": ...}``, ``{"command_id": ...}``). For a final
    step, ``final_text`` is the answer.
    """

    kind: str
    tool: str = ""
    args: dict[str, str] = field(default_factory=dict)
    final_text: str = ""


@dataclass(frozen=True, slots=True)
class ToolResult:
    """The recorded outcome of a tool step, fed back to the planner."""

    tool: str
    ok: bool
    output: str


class ToolPlanner(Protocol):
    """Decides the next step given the running transcript."""

    def next_step(
        self, agent: AgentSpec, ctx: AIContext, transcript: tuple[ToolResult, ...]
    ) -> ToolStep: ...


def _dispatch(gateway: SafeEditorToolGateway, step: ToolStep) -> str:
    """Run one tool step against the gateway; return a string result for the log."""
    tool = step.tool
    args = step.args
    if tool == "read_selection":
        return gateway.read_selection()
    if tool == "read_document":
        return gateway.read_current_document(args.get("scope", "full"))
    if tool == "read_outline":
        return "\n".join(gateway.read_document_outline())
    if tool == "replace_selection":
        return str(
            gateway.replace_selection(args.get("text", ""), label=args.get("label", "Replace"))
        )
    if tool == "insert":
        return str(
            gateway.insert_at_cursor(args.get("text", ""), label=args.get("label", "Insert"))
        )
    if tool == "apply_patch":
        applied = gateway.apply_text_patch(
            args.get("original", ""), args.get("proposed", ""), label=args.get("label", "Apply")
        )
        return str(applied)
    if tool == "run_command":
        return str(gateway.run_quill_command(args.get("command_id", "")))
    raise ValueError(f"Unknown tool: {tool!r}")


def run_tool_loop(
    planner: ToolPlanner,
    agent: AgentSpec,
    ctx: AIContext,
    gateway: SafeEditorToolGateway,
    emit: Emit,
    *,
    max_steps: int = MAX_STEPS,
) -> HarnessResult:
    """Drive the planner against the gateway until a final answer or the cap.

    A denied permission is *not* fatal: it is recorded in the transcript so the
    planner can choose another path. An unknown tool or a gateway exception ends
    the run with an error result. Reaching ``max_steps`` ends the run cleanly with
    whatever final text is available.
    """
    emit(AgentEvent(AgentEventKind.AGENT_STARTED, f"{agent.display_name} started."))
    transcript: list[ToolResult] = []

    for _ in range(max_steps):
        step = planner.next_step(agent, ctx, tuple(transcript))

        if step.kind == "final":
            emit(AgentEvent(AgentEventKind.AGENT_COMPLETED, f"{agent.display_name} finished."))
            return HarnessResult(status="completed", final_text=step.final_text)

        emit(AgentEvent(AgentEventKind.TOOL_CALL_REQUESTED, f"{agent.display_name}: {step.tool}"))
        try:
            output = _dispatch(gateway, step)
        except PermissionDeniedError as exc:
            # Recoverable: tell the planner and let it adapt.
            transcript.append(ToolResult(step.tool, ok=False, output=str(exc)))
            emit(AgentEvent(AgentEventKind.TOOL_CALL_DENIED, f"{step.tool} denied."))
            continue
        except Exception as exc:  # unknown tool / gateway failure: end the run
            emit(AgentEvent(AgentEventKind.ERROR, f"{step.tool} failed."))
            return HarnessResult(status="error", error=str(exc))

        transcript.append(ToolResult(step.tool, ok=True, output=output))
        emit(AgentEvent(AgentEventKind.TOOL_CALL_COMPLETED, f"{step.tool} done."))

    emit(AgentEvent(AgentEventKind.WARNING, "Agent reached the step limit."))
    last_text = transcript[-1].output if transcript else ""
    return HarnessResult(status="completed", final_text=last_text)
