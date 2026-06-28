"""Smoke + behavior tests for the unified AI Library dialog.

Drives the real dialog under a wx.App: the three tabs build from their stores,
the verb buttons enable/disable correctly per kind, and the Promote continuum
actually mutates the skill store. Network-backed Run paths are not exercised
here (no provider); they are covered by the live provider regression.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest  # type: ignore[import-not-found]

wx = pytest.importorskip("wx")

from quill.core.prompt_library import PromptLibrary  # noqa: E402
from quill.core.skill_store import SkillStore  # noqa: E402
from quill.ui.ai_library_dialog import AILibraryDialog  # noqa: E402


@dataclass
class _FakeAgent:
    id: str
    display_name: str
    description: str
    system_prompt: str


@dataclass
class _FakeSettings:
    ai_chat_default_provider: str = "openrouter"
    ai_chat_default_model: str = ""
    ai_prompt_default_model: str = ""
    ollama_base_url: str = ""


@pytest.fixture(scope="module")
def wx_app():
    app = wx.App()
    yield app
    app.Destroy()


def _make(wx_app, tmp_path):
    frame = wx.Frame(None)
    lib = PromptLibrary(tmp_path / "prompts.json")
    lib.add("Greeting", "Say hello to {selection}.", "Custom")
    store = SkillStore(tmp_path / "skills")
    agents = [
        _FakeAgent("writing-companion", "Writing Companion", "Helps you write.", "You help."),
    ]
    dlg = AILibraryDialog(
        frame,
        prompt_library=lib,
        skill_store=store,
        agents=agents,
        settings=_FakeSettings(),
        selection="world",
        document="world",
        title="doc",
    )
    return frame, dlg, lib, store


def test_three_tabs_build_from_stores(wx_app, tmp_path):
    frame, dlg, _lib, _store = _make(wx_app, tmp_path)
    try:
        assert dlg._notebook.GetPageCount() == 3
        # Prompts tab lists the seeded prompt (plus any builtins).
        names = [
            dlg._prompt_page._list.GetString(i) for i in range(dlg._prompt_page._list.GetCount())
        ]
        assert any("Greeting" in n for n in names)
        # Skills tab starts empty; Agents tab lists the one fake agent.
        assert dlg._skill_page._list.GetCount() == 0
        agent_names = [
            dlg._agent_page._list.GetString(i) for i in range(dlg._agent_page._list.GetCount())
        ]
        assert any("Writing Companion" in n for n in agent_names)
    finally:
        dlg.close()
        frame.Destroy()


def test_promote_prompt_to_skill_installs_a_skill(wx_app, tmp_path):
    frame, dlg, _lib, store = _make(wx_app, tmp_path)
    try:
        page = dlg._prompt_page
        # Select the Greeting prompt.
        page.select_by_id(next(it.id for it in page._items if it.name == "Greeting"))
        item = page.current()
        assert item is not None and item.can_promote
        dlg.promote(item)
        # A skill now exists in the store and the Skills tab shows it.
        assert store.find_by_name("Greeting") is not None
        assert dlg._skill_page._list.GetCount() == 1
        # The notebook switched to the Skills tab.
        assert dlg._notebook.GetSelection() == 1
    finally:
        dlg.close()
        frame.Destroy()


def test_agent_validate_reports_valid(wx_app, tmp_path):
    frame, dlg, _lib, _store = _make(wx_app, tmp_path)
    try:
        page = dlg._agent_page
        page._list.SetSelection(0)
        page._on_select()
        item = page.current()
        assert item is not None and not item.can_promote
        dlg.agent_validate(item)
        assert "valid" in dlg._status.GetLabel().lower()
    finally:
        dlg.close()
        frame.Destroy()


def test_agent_tab_has_no_promote_or_delete(wx_app, tmp_path):
    frame, dlg, _lib, _store = _make(wx_app, tmp_path)
    try:
        page = dlg._agent_page
        assert "promote" not in page._buttons
        assert "delete" not in page._buttons
        assert "run" in page._buttons and "validate" in page._buttons
    finally:
        dlg.close()
        frame.Destroy()
