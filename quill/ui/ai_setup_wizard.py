"""AI Setup Wizard — a gentle, magical first run for QUILL's AI.

A short, friendly, screen-reader-first wizard that takes someone from "I don't know
where to start" to "my AI is ready" in seconds, with no jargon and no dead ends. It
drives the wx-free :mod:`quill.core.ai.onboarding` model: welcome, the one real choice
(how should AI run?), a frictionless configure step, and a celebration of what just
became possible — landing the user in the gentle Basic experience mode by default.

One step is shown at a time (one focus context for screen-reader users), each with a
clear heading announced on arrival. Cloud setup pastes a key and can Test it; the
on-device path points at a local Ollama. Nothing is applied until the user reaches the
configure step's Next, and the whole thing can be cancelled at any point with nothing
lost. Reachable on first AI use and any time from ``AI > Set Up AI``.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any

import wx

from quill.core.ai import onboarding as ob
from quill.ui.dialog_contract import apply_modal_ids

_STEP_WELCOME = 0
_STEP_PATH = 1
_STEP_CONFIG = 2
_STEP_DONE = 3


class AISetupWizard:
    """The AI Setup Wizard dialog."""

    def __init__(self, parent: object, *, announce_cb: Callable[[str], None] | None = None) -> None:
        self._announce = announce_cb or (lambda _m: None)
        self._step = _STEP_WELCOME
        self._path = "cloud"
        self._provider = ob.CLOUD_PROVIDER_OPTIONS[0].id
        self._provider_name = ob.CLOUD_PROVIDER_OPTIONS[0].name
        self._busy = False
        self._configured = False

        self.dialog = wx.Dialog(
            parent,
            title="Set Up AI",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetMinSize(wx.Size(620, 520))

        root = wx.BoxSizer(wx.VERTICAL)
        self._heading = wx.StaticText(self.dialog, label="")
        self._heading.SetName("AI setup step")
        font = self._heading.GetFont()
        font.SetPointSize(font.GetPointSize() + 3)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self._heading.SetFont(font)
        root.Add(self._heading, 0, wx.ALL, 12)

        # Parent the per-step controls directly on the dialog (no intermediate
        # wx.Panel): an empty container panel becomes a stray keyboard tab stop, which
        # is confusing for screen-reader users. ``_body`` aliases the dialog so the
        # render code reads naturally; ``_body_sizer`` is a section of the root sizer we
        # clear and rebuild each step.
        self._body = self.dialog
        self._body_sizer = wx.BoxSizer(wx.VERTICAL)
        root.Add(self._body_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 12)

        self._status = wx.StaticText(self.dialog, label="")
        self._status.SetName("AI setup status")
        root.Add(self._status, 0, wx.ALL, 12)

        nav = wx.BoxSizer(wx.HORIZONTAL)
        self._back_btn = wx.Button(self.dialog, label="&Back")
        self._next_btn = wx.Button(self.dialog, label="&Next")
        self._cancel_btn = wx.Button(self.dialog, wx.ID_CANCEL, label="Not &now")
        nav.Add(self._back_btn, 0, wx.RIGHT, 6)
        nav.AddStretchSpacer()
        nav.Add(self._cancel_btn, 0, wx.RIGHT, 6)
        nav.Add(self._next_btn, 0)
        root.Add(nav, 0, wx.EXPAND | wx.ALL, 12)

        self.dialog.SetSizer(root)
        apply_modal_ids(self.dialog, affirmative_id=wx.ID_CANCEL, cancel_id=wx.ID_CANCEL)
        self._back_btn.Bind(wx.EVT_BUTTON, lambda _e: self._go_back())
        self._next_btn.Bind(wx.EVT_BUTTON, lambda _e: self._go_next())

        self._render()

    # -- lifecycle ------------------------------------------------------------

    def show(self) -> int:
        return self.dialog.ShowModal()

    def close(self) -> None:
        self.dialog.Destroy()

    # -- helpers --------------------------------------------------------------

    def _set_status(self, message: str) -> None:
        self._status.SetLabel(message)
        if message:
            self._announce(message)

    def _clear_body(self) -> None:
        self._body_sizer.Clear(delete_windows=True)

    def _add_text(self, text: str, *, grow: bool = False, name: str = "Information") -> wx.TextCtrl:
        """A read-only, multiline, word-wrapped edit control for prose.

        Screen readers can arrow through a read-only edit line by line, which a plain
        StaticText does not allow, so all wizard prose uses this. ``grow`` lets the main
        block fill the step; secondary blocks (hints) get a height that fits the text.
        """
        ctrl = wx.TextCtrl(
            self._body,
            value=text,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
        )
        ctrl.SetName(name)
        if grow:
            self._body_sizer.Add(ctrl, 1, wx.EXPAND | wx.BOTTOM, 8)
        else:
            n_lines = text.count("\n") + 3
            ctrl.SetMinSize(wx.Size(-1, ctrl.GetCharHeight() * n_lines + 14))
            self._body_sizer.Add(ctrl, 0, wx.EXPAND | wx.BOTTOM, 8)
        return ctrl

    # -- rendering ------------------------------------------------------------

    def _render(self) -> None:
        self._clear_body()
        if self._step == _STEP_WELCOME:
            self._render_welcome()
        elif self._step == _STEP_PATH:
            self._render_path()
        elif self._step == _STEP_CONFIG:
            self._render_config()
        else:
            self._render_done()
        self._back_btn.Enable(self._step in (_STEP_PATH, _STEP_CONFIG))
        self._next_btn.SetLabel("&Finish" if self._step == _STEP_DONE else "&Next")
        self._body.Layout()
        self.dialog.Layout()
        self._announce(self._heading.GetLabel())

    def _render_welcome(self) -> None:
        self._heading.SetLabel(ob.WELCOME_TITLE)
        body = self._add_text(ob.WELCOME_BODY, grow=True, name="About QUILL's AI")
        body.SetFocus()

    def _render_path(self) -> None:
        self._heading.SetLabel("How would you like AI to run?")
        self._path_choice = wx.RadioBox(
            self._body,
            label="",
            choices=[p.title for p in ob.ONBOARDING_PATHS],
            majorDimension=1,
            style=wx.RA_SPECIFY_COLS,
        )
        self._path_choice.SetName("How AI should run — pick one; you can change it any time")
        idx = next((i for i, p in enumerate(ob.ONBOARDING_PATHS) if p.id == self._path), 0)
        self._path_choice.SetSelection(idx)
        self._body_sizer.Add(self._path_choice, 0, wx.EXPAND | wx.BOTTOM, 8)
        self._path_detail = self._add_text(
            ob.ONBOARDING_PATHS[idx].detail, grow=True, name="What this means"
        )
        self._path_choice.Bind(wx.EVT_RADIOBOX, self._on_path_changed)
        self._path_choice.SetFocus()

    def _on_path_changed(self, _event: object) -> None:
        idx = self._path_choice.GetSelection()
        path = ob.ONBOARDING_PATHS[idx]
        self._path = path.id
        self._path_detail.SetValue(path.detail)
        self._body.Layout()
        self._announce(f"{path.title}. {path.summary}")

    def _render_config(self) -> None:
        if self._path == "on_device":
            self._render_on_device_config()
        else:
            self._render_cloud_config()

    def _render_cloud_config(self) -> None:
        self._heading.SetLabel("Connect your AI account")
        self._provider_choice = wx.Choice(
            self._body, choices=[p.name for p in ob.CLOUD_PROVIDER_OPTIONS]
        )
        self._provider_choice.SetName("AI provider")
        pidx = next(
            (i for i, p in enumerate(ob.CLOUD_PROVIDER_OPTIONS) if p.id == self._provider), 0
        )
        self._provider_choice.SetSelection(pidx)
        self._body_sizer.Add(wx.StaticText(self._body, label="&Provider:"), 0, wx.BOTTOM, 2)
        self._body_sizer.Add(self._provider_choice, 0, wx.EXPAND | wx.BOTTOM, 8)
        self._provider_hint = self._add_text(self._cloud_hint(pidx), name="About this provider")
        self._body_sizer.Add(wx.StaticText(self._body, label="API &key:"), 0, wx.BOTTOM, 2)
        self._key_ctrl = wx.TextCtrl(self._body, style=wx.TE_PASSWORD)
        self._key_ctrl.SetName("API key")
        self._body_sizer.Add(self._key_ctrl, 0, wx.EXPAND | wx.BOTTOM, 8)
        self._test_btn = wx.Button(self._body, label="&Test connection")
        self._body_sizer.Add(self._test_btn, 0, wx.BOTTOM, 8)
        self._provider_choice.Bind(wx.EVT_CHOICE, self._on_provider_changed)
        self._test_btn.Bind(wx.EVT_BUTTON, lambda _e: self._test_cloud())
        self._key_ctrl.SetFocus()

    def _cloud_hint(self, pidx: int) -> str:
        opt = ob.CLOUD_PROVIDER_OPTIONS[pidx]
        return f"{opt.blurb}\n{opt.key_hint}\nYour key is stored securely on this device only."

    def _on_provider_changed(self, _event: object) -> None:
        pidx = self._provider_choice.GetSelection()
        opt = ob.CLOUD_PROVIDER_OPTIONS[pidx]
        self._provider = opt.id
        self._provider_name = opt.name
        self._provider_hint.SetValue(self._cloud_hint(pidx))
        self._body.Layout()

    def _render_on_device_config(self) -> None:
        self._heading.SetLabel("Connect to Ollama on your computer")
        body = (
            ob.onboarding_path("on_device").detail
            + "\n\nWhen you click Next, QUILL checks for Ollama on this computer "
            "(http://localhost:11434) and connects to it. If Ollama isn't running yet, "
            "install it free from ollama.com and come back — nothing is lost."
        )
        self._add_text(body, grow=True, name="On-device setup").SetFocus()

    def _render_done(self) -> None:
        self._heading.SetLabel("You're all set")
        lines = ob.celebration_lines(self._path, provider_name=self._provider_name)
        text = self._add_text("\n".join(lines), grow=True, name="You're all set")
        if self._path != "skip":
            self._basic_cb = wx.CheckBox(
                self._body, label="Keep it simple — show only the essentials (Basic mode)"
            )
            self._basic_cb.SetName("Keep AI simple (Basic mode)")
            self._basic_cb.SetValue(True)
            self._body_sizer.Add(self._basic_cb, 0, wx.TOP, 8)
            self._basic_cb.SetFocus()
        else:
            text.SetFocus()

    # -- navigation -----------------------------------------------------------

    def _go_back(self) -> None:
        if self._busy:
            return
        if self._step == _STEP_CONFIG:
            self._step = _STEP_PATH
        elif self._step == _STEP_PATH:
            self._step = _STEP_WELCOME
        self._set_status("")
        self._render()

    def _go_next(self) -> None:
        if self._busy:
            return
        if self._step == _STEP_WELCOME:
            self._step = _STEP_PATH
            self._render()
            return
        if self._step == _STEP_PATH:
            if self._path == "skip":
                self._step = _STEP_DONE
            else:
                self._step = _STEP_CONFIG
            self._set_status("")
            self._render()
            return
        if self._step == _STEP_CONFIG:
            if not self._apply_config():
                return
            self._step = _STEP_DONE
            self._set_status("")
            self._render()
            return
        # _STEP_DONE -> finish
        self._finish()

    def _apply_config(self) -> bool:
        """Apply the chosen path's configuration. Returns False to stay on the step."""
        if self._path == "cloud":
            key = self._key_ctrl.GetValue().strip()
            if not key:
                self._set_status("Paste your API key first, or go Back to pick a different path.")
                self._key_ctrl.SetFocus()
                return False
            ob.apply_cloud_setup(self._provider, key)
        else:
            # Don't "configure" Ollama before it's actually there — verify it's
            # reachable with a model, and use one the user genuinely has installed.
            self._set_status("Checking for Ollama on your computer...")
            ok, message, model = ob.ollama_status()
            if not ok:
                self._set_status(message)
                return False
            ob.apply_on_device_setup(model=model)
        self._configured = True
        return True

    def _finish(self) -> None:
        if self._path != "skip" and getattr(self, "_basic_cb", None) is not None:
            ob.save_experience_mode(
                ob.EXPERIENCE_BASIC if self._basic_cb.GetValue() else ob.EXPERIENCE_ADVANCED
            )
        ob.mark_onboarding_complete()
        if self.dialog.IsModal():
            self.dialog.EndModal(wx.ID_OK)

    # -- cloud test -----------------------------------------------------------

    def _test_cloud(self) -> None:
        if self._busy:
            return
        key = self._key_ctrl.GetValue().strip()
        if not key:
            self._set_status("Paste your API key to test it.")
            return
        self._busy = True
        self._set_status(f"Testing {self._provider_name}...")

        provider, name = self._provider, self._provider_name

        def worker() -> None:
            ok, detail = _probe_provider(provider, key)
            wx.CallAfter(self._on_test_result, name, ok, detail)

        threading.Thread(target=worker, daemon=True).start()  # GATE-40-OK: connection probe.

    def _on_test_result(self, name: str, ok: bool, detail: str) -> None:
        self._busy = False
        if ok:
            self._set_status(f"Connected to {name}. You're good to go — click Next.")
        else:
            self._set_status(f"Couldn't reach {name}: {detail}")


def _probe_provider(provider: str, api_key: str) -> tuple[bool, str]:
    """Quick, contained connection check for a provider + key. Never raises."""
    try:
        import dataclasses

        from quill.core.ai.provider_backend import ProviderChatBackend
        from quill.core.ai.providers import default_host_for_provider, default_model_for_provider
        from quill.core.assistant_ai import AssistantConnectionSettings

        settings = AssistantConnectionSettings(
            provider=provider,
            host=default_host_for_provider(provider),
            model=default_model_for_provider(provider),
        )
        backend = ProviderChatBackend(settings=dataclasses.replace(settings), api_key=api_key)
        reply = backend.respond("Reply with exactly one word: ok")
        return (bool(reply and reply.strip()), "")
    except Exception as exc:  # noqa: BLE001 - report the reason, never crash the UI
        return (False, str(exc))


def maybe_offer_ai_setup(controller: Any, *, reason: str = "") -> bool:
    """If AI isn't ready, gently offer the setup wizard at a high-intent moment.

    Returns True when AI is usable afterward (already on, or set up just now), so the
    caller can continue; False when AI stays off (already configured-but-off, the user
    declined, or they finished the wizard without enabling). Turns a "you need AI" dead
    end into a one-click on-ramp, without ever nagging a user who has been here before.
    """
    from quill.core.ai.model_manager import load_ai_enabled
    from quill.core.ai.onboarding import ai_needs_setup

    if load_ai_enabled():
        return True
    if not ai_needs_setup():
        return False
    prompt = (f"{reason}\n\n" if reason else "") + (
        "Would you like to set up AI now? It only takes a few seconds, and you can "
        "choose a private on-device option or connect an account."
    )
    dlg = wx.MessageDialog(controller.frame, prompt, "Set Up AI", wx.YES_NO | wx.ICON_QUESTION)
    apply_modal_ids(dlg, affirmative_id=wx.ID_YES, escape_id=wx.ID_NO)
    try:
        yes = dlg.ShowModal() == wx.ID_YES
    finally:
        dlg.Destroy()
    if not yes:
        return False
    run_ai_setup_wizard(controller)
    return load_ai_enabled()


def run_ai_setup_wizard(controller: Any) -> None:
    """Open the AI Setup Wizard for the host MainFrame (keeps main_frame thin)."""
    wizard = AISetupWizard(controller.frame, announce_cb=getattr(controller, "_announce", None))
    controller._show_modal_dialog(wizard.dialog, "Set Up AI")
    wizard.close()
    # Refresh the menu so Basic/Advanced visibility and the new AI state take effect.
    refresh = getattr(controller, "_request_menu_refresh", None)
    if callable(refresh):
        refresh()
