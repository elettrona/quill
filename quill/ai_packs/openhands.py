"""OpenHands developer-agent harness pack (PRD §18.7).

Optional, experimental extra ``quill[ai-openhands]``. Sandboxed developer agent;
flag-gated, with a full action log. Bridges to QUILL's gateway; imported lazily
only when a session runs. Because it can run code/tools, every action still flows
through the broker (Terminal category is off by default) and the gateway.
"""

from __future__ import annotations

from quill.ai_packs._base import Invoke, SdkHarness
from quill.core.ai.harness import AgentSpec, AIContext, HarnessCapabilities

__all__ = ["OpenHandsHarness"]


class OpenHandsHarness(SdkHarness):
    pack_id = "openhands"
    pack_name = "OpenHands (experimental)"
    extra = "ai-openhands"
    sdk_modules = ("openhands",)

    def capabilities(self) -> HarnessCapabilities:
        return HarnessCapabilities(
            chat=True,
            streaming=True,
            tool_calling=True,
            patch_generation=True,
            subagents=True,
            requires_api_key=True,
            long_context=True,
        )

    def _make_invoke(self) -> Invoke:  # pragma: no cover - requires the SDK installed
        """Transport over the OpenHands documented agent entrypoint.

        Validated when ``quill[ai-openhands]`` is installed and the experimental
        flag is enabled; OpenHands actions are constrained to the gateway + broker
        (Terminal stays off by default) with a full action log via the Activity
        log. This first transport returns proposed text for the gateway to apply.
        """
        from openhands.core import run_agent  # type: ignore[import-not-found]

        def invoke(agent: AgentSpec, ctx: AIContext) -> str:
            task = f"{agent.system_prompt}\n\n{ctx.prompt}\n\n{ctx.context_text}".strip()
            result = run_agent(task)
            return str(getattr(result, "final_output", result) or "")

        return invoke
