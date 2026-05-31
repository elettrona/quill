from __future__ import annotations

from quill.core.ai.agent import ACTIONS, SAFE_TOOL_IDS, AgentDecision, allowed_tools


class _Cmd:
    def __init__(self, cid: str, title: str) -> None:
        self.id = cid
        self.title = title


class _Registry:
    def __init__(self, ids: list[str]) -> None:
        self._cmds = [_Cmd(i, i.replace(".", " ").title()) for i in ids]

    def list(self, feature_manager=None):
        return self._cmds


def test_allowed_tools_filters_to_existing_safe_ids() -> None:
    # Registry exposes two safe ids plus a command that is NOT in the allowlist.
    reg = _Registry(["file.save", "edit.undo", "file.delete_everything"])
    ids = [tid for tid, _ in allowed_tools(reg)]
    assert "file.save" in ids
    assert "edit.undo" in ids
    # A non-allowlisted (here: destructive-sounding) command must never surface.
    assert "file.delete_everything" not in ids


def test_allowed_tools_orders_by_allowlist_not_registry() -> None:
    # Registry order is reversed vs SAFE_TOOL_IDS; result follows the allowlist.
    reg = _Registry(["edit.undo", "file.save"])
    ids = [tid for tid, _ in allowed_tools(reg)]
    assert ids.index("file.save") < ids.index("edit.undo")


def test_allowed_tools_excludes_ids_missing_from_registry() -> None:
    reg = _Registry(["file.save"])
    ids = [tid for tid, _ in allowed_tools(reg)]
    assert ids == ["file.save"]


def test_safe_tool_ids_contains_no_destructive_commands() -> None:
    # Guard against accidentally adding a dangerous command to the allowlist —
    # the agent can run these without confirmation.
    banned = ("delete", "remove", "purge", "reset", "overwrite", "drop", "erase", "clear")
    offenders = [tid for tid in SAFE_TOOL_IDS if any(b in tid.lower() for b in banned)]
    assert not offenders, f"destructive ids in SAFE_TOOL_IDS: {offenders}"


def test_safe_tool_ids_are_unique() -> None:
    assert len(SAFE_TOOL_IDS) == len(set(SAFE_TOOL_IDS))


def test_agent_decision_defaults() -> None:
    d = AgentDecision(action="answer")
    assert d.text == ""
    assert d.tool == ""
    assert "answer" in ACTIONS
