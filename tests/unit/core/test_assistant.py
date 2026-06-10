from __future__ import annotations

from quill.core.assistant import (
    assistant_prompt_presets,
    build_assistant_tools,
    rank_assistant_tools,
    render_assistant_prompt,
)
from quill.core.commands import CommandRegistry
from quill.core.features import FeatureManager


def test_assistant_tool_catalog_includes_registered_commands() -> None:
    registry = CommandRegistry()
    registry.register("edit.find", "Find", lambda: None)
    registry.register("tools.run_python", "Run Python", lambda: None)

    tools = build_assistant_tools(registry, FeatureManager())

    assert any(tool.command_id == "edit.find" for tool in tools)
    assert any(tool.command_id == "tools.run_python" for tool in tools)
    assert any(tool.name == "run_python" for tool in tools)


def test_assistant_tool_ranking_prefers_python_matches() -> None:
    registry = CommandRegistry()
    registry.register("edit.find", "Find", lambda: None)
    registry.register("tools.run_python", "Run Python", lambda: None)

    tools = build_assistant_tools(registry, FeatureManager())
    ranked = rank_assistant_tools("python", tools, limit=3)

    assert ranked[0].command_id == "tools.run_python"


def test_assistant_prompt_presets_include_rewrite_and_summary() -> None:
    presets = assistant_prompt_presets()

    assert {preset.name for preset in presets} >= {"rewrite", "summarize", "grammar"}


def test_assistant_prompt_rendering_includes_selection_text() -> None:
    prompt = render_assistant_prompt("rewrite", selection_text="hello world")

    assert "hello world" in prompt


def test_unreachable_provider_announced(monkeypatch, caplog) -> None:
    # M-16: if the configured provider raises during the probe, a WARNING must
    # be emitted so the fallback is visible in the diagnostic log.
    import logging

    from quill.core.ai import assistant as assistant_module
    from quill.core.ai.assistant import make_default_backend

    class _FakePath:
        def exists(self) -> bool:
            return True

    class _BadBackend:
        def is_available(self) -> tuple[bool, object]:
            raise ConnectionError("endpoint unreachable")

    monkeypatch.setattr(
        "quill.core.assistant_ai.assistant_connection_path",
        lambda: _FakePath(),
    )
    monkeypatch.setattr(
        "quill.core.assistant_ai.load_assistant_connection_settings",
        lambda: type("S", (), {"provider": "ollama"})(),
    )
    monkeypatch.setattr(
        "quill.core.ai.provider_backend.ProviderChatBackend",
        lambda _settings: _BadBackend(),
    )

    with caplog.at_level(logging.WARNING, logger=assistant_module.logger.name):
        make_default_backend()

    assert caplog.records, "expected at least one log record from make_default_backend"
    assert any("probe failed" in r.message or "falling back" in r.message for r in caplog.records)
