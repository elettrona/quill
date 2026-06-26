"""GitHub Copilot SDK harness pack (PRD §18.5).

Optional extra ``quill[ai-copilot]``. Bridges the Copilot SDK to QUILL's gateway;
imported lazily only when a session runs. Copilot authenticates via the user's
GitHub account (OAuth), so the harness declares ``requires_oauth``.
"""

from __future__ import annotations

from quill.ai_packs._base import Invoke, SdkHarness
from quill.core.ai.harness import AgentSpec, AIContext, HarnessCapabilities

__all__ = ["CopilotHarness"]


class CopilotHarness(SdkHarness):
    pack_id = "copilot"
    pack_name = "GitHub Copilot SDK"
    extra = "ai-copilot"
    sdk_modules = ("copilot",)

    def capabilities(self) -> HarnessCapabilities:
        return HarnessCapabilities(
            chat=True,
            streaming=True,
            tool_calling=True,
            patch_generation=True,
            mcp=True,
            skills=True,
            requires_oauth=True,
            long_context=True,
        )

    def _make_invoke(self) -> Invoke:  # pragma: no cover - requires the SDK installed
        """Transport over the Copilot SDK's documented client entrypoint.

        Validated when ``quill[ai-copilot]`` is installed; Copilot skills are wired
        to the gateway's typed tools. This first transport returns the proposed
        text for the gateway to apply.
        """
        import copilot  # type: ignore[import-not-found]

        def invoke(agent: AgentSpec, ctx: AIContext) -> str:
            client = copilot.Client()
            prompt = f"{agent.system_prompt}\n\n{ctx.prompt}\n\n{ctx.context_text}".strip()
            response = client.complete(prompt)
            return str(getattr(response, "text", response) or "")

        return invoke
