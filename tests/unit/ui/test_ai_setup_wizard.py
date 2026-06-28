"""Smoke + flow tests for the AI Setup Wizard."""

from __future__ import annotations

import pytest  # type: ignore[import-not-found]

wx = pytest.importorskip("wx")

import quill.core.ai.onboarding as ob  # noqa: E402
from quill.ui.ai_setup_wizard import AISetupWizard  # noqa: E402


@pytest.fixture(scope="module")
def wx_app():
    app = wx.App()
    yield app
    app.Destroy()


def _wizard(wx_app):
    frame = wx.Frame(None)
    dlg = AISetupWizard(frame)
    return frame, dlg


def test_prose_is_readonly_edit_and_no_stray_panel(wx_app):
    # Screen-reader fixes: wizard prose must be navigable read-only edit controls
    # (not StaticText), and there must be no intermediate container panel (it became
    # a stray keyboard tab stop). Controls parent directly on the dialog.
    frame, dlg = _wizard(wx_app)
    try:
        for step in range(4):
            dlg._step = step
            dlg._render()
            kids = dlg.dialog.GetChildren()
            assert not any(isinstance(c, wx.Panel) for c in kids), f"stray panel on step {step}"
            ro_edits = [
                c
                for c in kids
                if isinstance(c, wx.TextCtrl) and (c.GetWindowStyleFlag() & wx.TE_READONLY)
            ]
            assert ro_edits, f"step {step} prose should be a read-only edit control"
    finally:
        dlg.close()
        frame.Destroy()


def test_welcome_then_path_then_config_cloud(wx_app, monkeypatch):
    frame, dlg = _wizard(wx_app)
    applied = {}
    monkeypatch.setattr(ob, "apply_cloud_setup", lambda p, k, **kw: applied.update(p=p, k=k))
    try:
        # Welcome -> Path
        dlg._go_next()
        assert dlg._step == 1
        # Choose cloud (index 1) -> Config
        dlg._path_choice.SetSelection(1)
        dlg._on_path_changed(None)
        assert dlg._path == "cloud"
        dlg._go_next()
        assert dlg._step == 2
        # No key yet -> stays on config with a hint
        dlg._go_next()
        assert dlg._step == 2
        assert "key" in dlg._status.GetLabel().lower()
        # Enter a key -> applies and advances to Done
        dlg._key_ctrl.SetValue("sk-test")
        dlg._go_next()
        assert dlg._step == 3
        assert applied == {"p": dlg._provider, "k": "sk-test"}
    finally:
        dlg.close()
        frame.Destroy()


def test_skip_path_jumps_to_done_without_configuring(wx_app, monkeypatch):
    frame, dlg = _wizard(wx_app)
    calls = []
    monkeypatch.setattr(ob, "apply_cloud_setup", lambda *a, **k: calls.append("cloud"))
    monkeypatch.setattr(ob, "apply_on_device_setup", lambda *a, **k: calls.append("device"))
    try:
        dlg._go_next()  # -> path
        # Select "Not right now" (skip is index 2)
        skip_idx = next(i for i, p in enumerate(ob.ONBOARDING_PATHS) if p.id == "skip")
        dlg._path_choice.SetSelection(skip_idx)
        dlg._on_path_changed(None)
        dlg._go_next()  # skip -> done directly
        assert dlg._step == 3
        assert calls == []  # nothing configured
    finally:
        dlg.close()
        frame.Destroy()


def test_on_device_blocks_when_ollama_missing_then_proceeds(wx_app, monkeypatch):
    frame, dlg = _wizard(wx_app)
    applied = []
    monkeypatch.setattr(ob, "apply_on_device_setup", lambda **k: applied.append(k.get("model")))
    try:
        dlg._go_next()  # path
        dev_idx = next(i for i, p in enumerate(ob.ONBOARDING_PATHS) if p.id == "on_device")
        dlg._path_choice.SetSelection(dev_idx)
        dlg._on_path_changed(None)
        dlg._go_next()  # -> on-device config
        # Ollama not present: Next does not advance, shows guidance, configures nothing.
        monkeypatch.setattr(ob, "ollama_status", lambda *a, **k: (False, "install ollama", ""))
        dlg._go_next()
        assert dlg._step == 2 and applied == []
        assert "ollama" in dlg._status.GetLabel().lower()
        # Ollama present with a model: now it applies (using that model) and advances.
        monkeypatch.setattr(ob, "ollama_status", lambda *a, **k: (True, "", "llama3.2:1b"))
        dlg._go_next()
        assert dlg._step == 3 and applied == ["llama3.2:1b"]
    finally:
        dlg.close()
        frame.Destroy()


def test_finish_persists_experience_mode_and_completion(wx_app, tmp_path, monkeypatch):
    monkeypatch.setattr(ob, "onboarding_state_path", lambda: tmp_path / "ai" / "onboarding.json")
    monkeypatch.setattr(ob, "apply_on_device_setup", lambda *a, **k: None)
    monkeypatch.setattr(ob, "ollama_status", lambda *a, **k: (True, "", "llama3.2:1b"))
    frame, dlg = _wizard(wx_app)
    try:
        dlg._go_next()  # path
        dev_idx = next(i for i, p in enumerate(ob.ONBOARDING_PATHS) if p.id == "on_device")
        dlg._path_choice.SetSelection(dev_idx)
        dlg._on_path_changed(None)
        dlg._go_next()  # config (on-device)
        dlg._go_next()  # apply + done
        assert dlg._step == 3
        # Uncheck "keep it simple" -> advanced mode persisted on finish.
        dlg._basic_cb.SetValue(False)
        dlg._finish()
        assert ob.onboarding_complete() is True
        assert ob.load_experience_mode() == ob.EXPERIENCE_ADVANCED
    finally:
        frame.Destroy()
