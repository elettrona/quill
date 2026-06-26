"""Optional AI harness packs (PRD §19, §18.5-§18.7).

Each subpackage is a lazily-imported :class:`~quill.core.ai.harness.Harness` that
bridges a third-party agent SDK to QUILL's Safe Editor Tool Gateway and Permission
Broker. Packs are **optional extras**: an uninstalled pack reports
``is_available() == (False, "Install the X pack ...")`` and QUILL keeps working;
none is ever required, and none edits the buffer directly.

Importing this package does NOT import any SDK. SDKs are probed (never imported at
module load) via :func:`quill.ai_packs._base.modules_missing`, and only imported
inside a session when the pack actually runs.

``register_available(registry, invoke_factory=None)`` constructs every pack and
registers it; the Hub then lists whichever ones are installed.
"""

from __future__ import annotations

from quill.ai_packs._base import SdkHarness
from quill.ai_packs.claude import ClaudeAgentHarness
from quill.ai_packs.copilot import CopilotHarness
from quill.ai_packs.langgraph import LangGraphHarness
from quill.ai_packs.microsoft import MicrosoftAgentHarness
from quill.ai_packs.openai_agents import OpenAIAgentsHarness
from quill.ai_packs.openhands import OpenHandsHarness

__all__ = [
    "SdkHarness",
    "CopilotHarness",
    "ClaudeAgentHarness",
    "OpenAIAgentsHarness",
    "MicrosoftAgentHarness",
    "LangGraphHarness",
    "OpenHandsHarness",
    "all_packs",
    "register_all",
]


def all_packs() -> list[SdkHarness]:
    """Construct one instance of every pack (no SDK import happens here)."""
    return [
        CopilotHarness(),
        ClaudeAgentHarness(),
        OpenAIAgentsHarness(),
        MicrosoftAgentHarness(),
        LangGraphHarness(),
        OpenHandsHarness(),
    ]


def register_all(registry: object) -> list[SdkHarness]:
    """Register every pack into ``registry``; return the packs.

    Registering an uninstalled pack is intentional: it appears in the Hub's
    Harnesses tab as available-to-install (``is_available()`` reports the reason),
    rather than vanishing silently.
    """
    packs = all_packs()
    for pack in packs:
        registry.register(pack)  # type: ignore[attr-defined]
    return packs
