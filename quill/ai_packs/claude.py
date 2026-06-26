"""Claude Agent SDK harness pack (PRD §18.5).

Optional extra ``quill[ai-claude]``. Bridges the Claude Agent SDK to QUILL's
gateway; the SDK is imported lazily only when a session runs.
"""

from __future__ import annotations

from quill.ai_packs._base import Invoke, SdkHarness
from quill.core.ai.harness import AgentSpec, AIContext, HarnessCapabilities

__all__ = ["ClaudeAgentHarness"]


class ClaudeAgentHarness(SdkHarness):
    pack_id = "claude_agent_sdk"
    pack_name = "Claude Agent SDK"
    extra = "ai-claude"
    sdk_modules = ("claude_agent_sdk",)

    def capabilities(self) -> HarnessCapabilities:
        return HarnessCapabilities(
            chat=True,
            streaming=True,
            tool_calling=True,
            patch_generation=True,
            mcp=True,
            skills=True,
            subagents=True,
            requires_api_key=True,
            images=True,
            long_context=True,
        )

    def _make_invoke(self) -> Invoke:  # pragma: no cover - requires the SDK installed
        """Transport over the Claude Agent SDK's documented query entrypoint.

        Validated when ``quill[ai-claude]`` is installed; in QUILL the SDK's tool
        calls are wired to the gateway's typed tools. This first transport returns
        the model's proposed text and lets the gateway apply it.
        """
        import asyncio

        from claude_agent_sdk import query  # type: ignore[import-not-found]

        def invoke(agent: AgentSpec, ctx: AIContext) -> str:
            prompt = f"{agent.system_prompt}\n\n{ctx.prompt}\n\n{ctx.context_text}".strip()

            async def _run() -> str:
                chunks: list[str] = []
                async for message in query(prompt=prompt):
                    text = getattr(message, "result", None) or getattr(message, "text", "")
                    if text:
                        chunks.append(str(text))
                return "".join(chunks)

            return asyncio.run(_run())

        return invoke
