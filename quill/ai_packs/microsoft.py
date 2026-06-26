"""Microsoft Agent Framework harness pack (PRD §18.6).

Optional extra ``quill[ai-microsoft]``. Bridges the Microsoft Agent Framework
(import name ``agent_framework``) to QUILL's gateway; imported lazily only when a
session runs. Targets enterprise/Azure scenarios and admin policy (PRD §15).
"""

from __future__ import annotations

from quill.ai_packs._base import Invoke, SdkHarness
from quill.core.ai.harness import AgentSpec, AIContext, HarnessCapabilities

__all__ = ["MicrosoftAgentHarness"]


class MicrosoftAgentHarness(SdkHarness):
    pack_id = "microsoft_agent_framework"
    pack_name = "Microsoft Agent Framework"
    extra = "ai-microsoft"
    sdk_modules = ("agent_framework",)

    def capabilities(self) -> HarnessCapabilities:
        return HarnessCapabilities(
            chat=True,
            streaming=True,
            tool_calling=True,
            patch_generation=True,
            mcp=True,
            subagents=True,
            requires_api_key=True,
            long_context=True,
        )

    def _make_invoke(self) -> Invoke:  # pragma: no cover - requires the SDK installed
        """Transport over the Microsoft Agent Framework's documented ChatAgent API.

        Validated when ``quill[ai-microsoft]`` is installed; the framework's tools
        are wired to the gateway's typed tools and admin policy is honored by the
        provider catalog + broker. This first transport runs the agent and returns
        its text for the gateway to apply.
        """
        import asyncio

        from agent_framework import ChatAgent  # type: ignore[import-not-found]

        def invoke(agent: AgentSpec, ctx: AIContext) -> str:
            user_input = f"{ctx.prompt}\n\n{ctx.context_text}".strip()

            async def _run() -> str:
                sdk_agent = ChatAgent(instructions=agent.system_prompt)
                result = await sdk_agent.run(user_input)
                return str(getattr(result, "text", result) or "")

            return asyncio.run(_run())

        return invoke
