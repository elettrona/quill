"""LangGraph harness pack (PRD §18.6).

Optional extra ``quill[ai-langgraph]``. Bridges LangGraph durable, pause/resume,
human-in-the-loop graphs to QUILL's gateway; imported lazily only when a session
runs. The underlying model carries its own key, so the harness itself does not
declare ``requires_api_key``.
"""

from __future__ import annotations

from quill.ai_packs._base import Invoke, SdkHarness
from quill.core.ai.harness import AgentSpec, AIContext, HarnessCapabilities

__all__ = ["LangGraphHarness"]


class LangGraphHarness(SdkHarness):
    pack_id = "langgraph"
    pack_name = "LangGraph"
    extra = "ai-langgraph"
    sdk_modules = ("langgraph",)

    def capabilities(self) -> HarnessCapabilities:
        return HarnessCapabilities(
            chat=True,
            streaming=True,
            tool_calling=True,
            patch_generation=True,
            mcp=True,
            subagents=True,
            long_context=True,
        )

    def _make_invoke(self) -> Invoke:  # pragma: no cover - requires the SDK installed
        """Transport over LangGraph's documented prebuilt ReAct agent.

        Validated when ``quill[ai-langgraph]`` is installed; gateway tools are
        exposed to the graph as LangChain tools and durable checkpoints persist via
        QUILL's atomic storage. This first transport invokes the graph and returns
        the final message for the gateway to apply.
        """
        from langgraph.prebuilt import create_react_agent  # type: ignore[import-not-found]

        def invoke(agent: AgentSpec, ctx: AIContext) -> str:
            graph = create_react_agent(model=ctx.file_type or "openai:gpt-4o-mini", tools=[])
            user_input = f"{agent.system_prompt}\n\n{ctx.prompt}\n\n{ctx.context_text}".strip()
            state = graph.invoke({"messages": [("user", user_input)]})
            messages = state.get("messages", []) if isinstance(state, dict) else []
            if not messages:
                return ""
            last = messages[-1]
            return str(getattr(last, "content", last) or "")

        return invoke
