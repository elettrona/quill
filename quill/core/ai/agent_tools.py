"""The shared agent tool surface (PRD §9) — one definition for every harness.

The native tool loop, the prompt planner, and the optional SDK packs all need the
*same* set of editor tools, described the same way, executing the same way through
the Safe Editor Tool Gateway. This module is that single source of truth:

- :data:`TOOL_DESCRIPTORS` — name, description, and parameter schema for each tool,
  so a pack can register them as the SDK's custom tools (and deny the SDK's own
  filesystem/shell tools) — letting e.g. Copilot's agent *take actions in the
  document* only through QUILL's reviewed gateway.
- :func:`execute_tool` — run one tool against the gateway (permission + preview +
  undo + audit all apply). The native loop dispatches here, so there is exactly one
  place that maps tool names to gateway calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from quill.core.ai.tool_gateway import SafeEditorToolGateway

__all__ = ["AgentToolDescriptor", "TOOL_DESCRIPTORS", "tool_names", "execute_tool"]


@dataclass(frozen=True, slots=True)
class AgentToolDescriptor:
    """A tool the agent may request: name, one-line description, arg schema."""

    name: str
    description: str
    # arg name -> human description. Empty when the tool takes no arguments.
    parameters: dict[str, str] = field(default_factory=dict)


TOOL_DESCRIPTORS: tuple[AgentToolDescriptor, ...] = (
    AgentToolDescriptor("read_selection", "Read the current selection."),
    AgentToolDescriptor("read_document", "Read the whole document.", {"scope": "optional scope"}),
    AgentToolDescriptor("read_outline", "Read the document's heading outline."),
    AgentToolDescriptor(
        "replace_selection",
        "Replace the current selection with new text (reviewed + undoable).",
        {"text": "the new text"},
    ),
    AgentToolDescriptor(
        "insert", "Insert text at the cursor (undoable).", {"text": "the text to insert"}
    ),
    AgentToolDescriptor(
        "apply_patch",
        "Replace the whole document (reviewed + undoable).",
        {"original": "the full original text", "proposed": "the full new text"},
    ),
    AgentToolDescriptor(
        "run_command",
        "Run a safe, allowlisted QUILL command.",
        {"command_id": "the command id"},
    ),
)

_NAMES = tuple(d.name for d in TOOL_DESCRIPTORS)


def tool_names() -> tuple[str, ...]:
    """Return the canonical tool names (the keys ``execute_tool`` accepts)."""
    return _NAMES


def execute_tool(gateway: SafeEditorToolGateway, name: str, args: dict[str, str]) -> str:
    """Run one tool against the gateway; return a string result for the transcript.

    The single mapping of tool name -> gateway call. Reads return their content;
    mutations return ``"True"``/``"False"`` (applied or declined). An unknown tool
    raises ``ValueError`` so the caller can end the run cleanly.
    """
    if name == "read_selection":
        return gateway.read_selection()
    if name == "read_document":
        return gateway.read_current_document(args.get("scope", "full"))
    if name == "read_outline":
        return "\n".join(gateway.read_document_outline())
    if name == "replace_selection":
        return str(
            gateway.replace_selection(args.get("text", ""), label=args.get("label", "Replace"))
        )
    if name == "insert":
        return str(
            gateway.insert_at_cursor(args.get("text", ""), label=args.get("label", "Insert"))
        )
    if name == "apply_patch":
        return str(
            gateway.apply_text_patch(
                args.get("original", ""), args.get("proposed", ""), label=args.get("label", "Apply")
            )
        )
    if name == "run_command":
        return str(gateway.run_quill_command(args.get("command_id", "")))
    raise ValueError(f"Unknown tool: {name!r}")
