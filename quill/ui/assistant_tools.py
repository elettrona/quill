from __future__ import annotations

from collections.abc import Callable

from quill.core.assistant import (
    assistant_prompt_presets,
    build_assistant_tools,
    rank_assistant_tools,
    render_assistant_prompt,
)
from quill.core.assistant_ai import (
    AssistantConnectionSettings,
    load_assistant_api_key,
    load_assistant_connection_settings,
    save_assistant_api_key,
    save_assistant_connection_settings,
)
from quill.core.commands import CommandRegistry
from quill.core.features import FeatureManager
from quill.core.python_sandbox import PythonSandboxResult, run_python_sandbox


class RunPythonDialog:
    def __init__(
        self,
        parent: object,
        *,
        document_text: str,
        selection_text: str,
        outline: list[dict[str, object]] | None = None,
        apply_callback: Callable[[str], None],
    ) -> None:
        import wx

        self._wx = wx
        self._document_text = document_text
        self._selection_text = selection_text
        self._outline = outline
        self._apply_callback = apply_callback
        self._latest_result: PythonSandboxResult | None = None

        self.dialog = wx.Dialog(
            parent,
            title="Run Python",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetSize((900, 680))

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(
            wx.StaticText(
                self.dialog,
                label=(
                    "Sandboxed Python can read document_text and selection_text. "
                    "Set result or print output, then apply the transformed text."
                ),
            ),
            0,
            wx.EXPAND | wx.ALL,
            8,
        )

        self.code = wx.TextCtrl(
            self.dialog,
            style=wx.TE_MULTILINE | wx.TE_PROCESS_TAB | wx.BORDER_SIMPLE,
            size=(-1, 280),
        )
        self.code.SetValue(
            "# document_text and selection_text are available.\n"
            "# Set result or call set_result(...).\n"
            "result = selection_text or document_text\n"
        )
        root.Add(self.code, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.status = wx.StaticText(self.dialog, label="Ready.")
        root.Add(self.status, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.preview = wx.TextCtrl(
            self.dialog,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SIMPLE,
            size=(-1, 220),
        )
        root.Add(self.preview, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.run_button = wx.Button(self.dialog, label="Run")
        self.apply_button = wx.Button(self.dialog, label="Apply Result")
        self.close_button = wx.Button(self.dialog, id=wx.ID_CANCEL, label="Close")
        self.apply_button.Enable(False)
        buttons.Add(self.run_button, 0, wx.RIGHT, 8)
        buttons.Add(self.apply_button, 0, wx.RIGHT, 8)
        buttons.AddStretchSpacer(1)
        buttons.Add(self.close_button, 0)
        root.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.dialog.SetSizer(root)
        self.run_button.Bind(wx.EVT_BUTTON, self._on_run)
        self.apply_button.Bind(wx.EVT_BUTTON, self._on_apply)
        self.close_button.Bind(wx.EVT_BUTTON, lambda _e: self.dialog.EndModal(wx.ID_CANCEL))
        self.dialog.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self.code.SetFocus()

    def show_modal(self) -> None:
        self.dialog.CentreOnParent()
        try:
            self.dialog.ShowModal()
        finally:
            self.dialog.Destroy()

    def _on_char_hook(self, event: object) -> None:
        if event.GetKeyCode() == self._wx.WXK_ESCAPE:
            self.dialog.EndModal(self._wx.ID_CANCEL)
            return
        event.Skip()

    def _on_run(self, _event: object) -> None:
        result = run_python_sandbox(
            self.code.GetValue(),
            document_text=self._document_text,
            selection_text=self._selection_text,
            outline=self._outline,
        )
        self._latest_result = result
        self.preview.SetValue(self._render_result(result))
        self.apply_button.Enable(
            result.succeeded and bool((result.result or result.stdout).strip())
        )
        if result.succeeded:
            self.status.SetLabel(f"Completed in {result.elapsed_seconds:.2f}s.")
            return
        if result.timed_out:
            self.status.SetLabel("Execution timed out.")
            return
        if result.error:
            self.status.SetLabel("Execution failed.")
            return
        self.status.SetLabel("Execution finished.")

    def _on_apply(self, _event: object) -> None:
        if self._latest_result is None:
            return
        updated = self._latest_result.result.strip() or self._latest_result.stdout.strip()
        if not updated:
            return
        self._apply_callback(updated)
        self.dialog.EndModal(self._wx.ID_OK)

    def _render_result(self, result: PythonSandboxResult) -> str:
        parts = [
            f"Return code: {result.returncode}",
            f"Timed out: {result.timed_out}",
            "",
        ]
        if result.result:
            parts.extend(("Result:", result.result, ""))
        if result.stdout:
            parts.extend(("Stdout:", result.stdout, ""))
        if result.stderr:
            parts.extend(("Stderr:", result.stderr, ""))
        if result.error:
            parts.extend(("Error:", result.error, ""))
        return "\n".join(parts).strip()


class WritingAssistantDialog:
    def __init__(
        self,
        parent: object,
        command_registry: CommandRegistry,
        feature_manager: FeatureManager | None,
        *,
        open_python_tool: Callable[[], None],
        selection_text: str = "",
        document_text: str = "",
        initial_prompt: str = "",
        assistant_enabled: bool = False,
        prompt_style: str = "balanced",
    ) -> None:
        import wx

        self._wx = wx
        self._registry = command_registry
        self._open_python_tool = open_python_tool
        self._selection_text = selection_text
        self._document_text = document_text
        self._assistant_enabled = assistant_enabled
        self._prompt_style = prompt_style
        self._all_tools = build_assistant_tools(command_registry, feature_manager)
        self._filtered_tools = list(self._all_tools)
        self._prompt_presets = assistant_prompt_presets()

        self.dialog = wx.Dialog(
            parent,
            title="Writing Assistant",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetSize((960, 700))

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(
            wx.StaticText(
                self.dialog,
                label=(
                    "Use the local command catalog to find writing actions quickly. "
                    "This shell is CPU-only and keeps tool actions accessible."
                ),
            ),
            0,
            wx.EXPAND | wx.ALL,
            8,
        )

        preset_row = wx.BoxSizer(wx.HORIZONTAL)
        self.preset_choice = wx.Choice(
            self.dialog,
            choices=[preset.title for preset in self._prompt_presets],
        )
        self.preset_choice.SetSelection(0 if self._prompt_presets else wx.NOT_FOUND)
        self.load_prompt_button = wx.Button(self.dialog, label="Load Prompt")
        self.use_selection_button = wx.Button(self.dialog, label="Use Selection")
        self.use_document_button = wx.Button(self.dialog, label="Use Document")
        preset_row.Add(
            wx.StaticText(self.dialog, label="Prompt presets"),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )
        preset_row.AddSpacer(8)
        preset_row.Add(self.preset_choice, 1, wx.RIGHT, 8)
        preset_row.Add(self.load_prompt_button, 0, wx.RIGHT, 8)
        preset_row.Add(self.use_selection_button, 0, wx.RIGHT, 8)
        preset_row.Add(self.use_document_button, 0)
        root.Add(preset_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.prompt = wx.TextCtrl(self.dialog, style=wx.TE_MULTILINE | wx.TE_PROCESS_TAB)
        self.prompt.SetHint("Describe the edit, review, or command you want")
        if initial_prompt.strip():
            self.prompt.SetValue(initial_prompt)
        elif self._prompt_presets:
            self.prompt.SetValue(
                render_assistant_prompt(
                    self._prompt_presets[0].name,
                    selection_text=self._selection_text,
                    document_text=self._document_text,
                )
            )
        root.Add(self.prompt, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.status = wx.StaticText(self.dialog, label="Showing all available tools.")
        root.Add(self.status, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.chat_log = wx.TextCtrl(
            self.dialog,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SIMPLE,
            size=(-1, 110),
        )
        self.chat_log.SetValue(self._initial_chat_log())
        root.Add(self.chat_log, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.results = wx.ListBox(self.dialog)
        root.Add(self.results, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.details = wx.TextCtrl(
            self.dialog,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SIMPLE,
            size=(-1, 120),
        )
        root.Add(self.details, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.suggest_button = wx.Button(self.dialog, label="Suggest")
        self.run_button = wx.Button(self.dialog, label="Run Selected Action")
        self.python_button = wx.Button(self.dialog, label="Run Python...")
        self.close_button = wx.Button(self.dialog, id=wx.ID_CANCEL, label="Close")
        buttons.Add(self.suggest_button, 0, wx.RIGHT, 8)
        buttons.Add(self.run_button, 0, wx.RIGHT, 8)
        buttons.Add(self.python_button, 0, wx.RIGHT, 8)
        buttons.AddStretchSpacer(1)
        buttons.Add(self.close_button, 0)
        root.Add(buttons, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.dialog.SetSizer(root)
        self.suggest_button.Bind(wx.EVT_BUTTON, self._on_suggest)
        self.run_button.Bind(wx.EVT_BUTTON, self._on_run_selected)
        self.python_button.Bind(wx.EVT_BUTTON, lambda _e: self._open_python_tool())
        self.close_button.Bind(wx.EVT_BUTTON, lambda _e: self.dialog.EndModal(wx.ID_CANCEL))
        self.results.Bind(wx.EVT_LISTBOX, self._on_selection_changed)
        self.results.Bind(wx.EVT_LISTBOX_DCLICK, self._on_run_selected)
        self.prompt.Bind(wx.EVT_TEXT, self._on_prompt_changed)
        self.load_prompt_button.Bind(wx.EVT_BUTTON, self._on_load_prompt)
        self.use_selection_button.Bind(wx.EVT_BUTTON, self._on_use_selection)
        self.use_document_button.Bind(wx.EVT_BUTTON, self._on_use_document)
        self.dialog.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

        self._refresh_results()

    def show_modal(self) -> None:
        self.dialog.CentreOnParent()
        try:
            self.dialog.ShowModal()
        finally:
            self.dialog.Destroy()

    def _on_char_hook(self, event: object) -> None:
        key_code = event.GetKeyCode()
        if key_code == self._wx.WXK_ESCAPE:
            self.dialog.EndModal(self._wx.ID_CANCEL)
            return
        if key_code in (self._wx.WXK_RETURN, self._wx.WXK_NUMPAD_ENTER) and not event.ShiftDown():
            self._run_selected()
            return
        event.Skip()

    def _on_prompt_changed(self, _event: object) -> None:
        self._refresh_results()

    def _on_suggest(self, _event: object) -> None:
        self._refresh_results()

    def _initial_chat_log(self) -> str:
        lines = [
            "Chat log:",
            "- Use a preset to seed a prompt.",
            "- Run a command or Python transform, then apply the result back into the editor.",
        ]
        if self._assistant_enabled:
            lines.append(f"- Assistant prompts are enabled with the {self._prompt_style} style.")
        return "\n".join(lines)

    def _append_chat_log(self, line: str) -> None:
        current = self.chat_log.GetValue().rstrip()
        if current:
            current += "\n"
        self.chat_log.SetValue(f"{current}{line}".strip())

    def _on_load_prompt(self, _event: object) -> None:
        self._apply_prompt_from_preset()

    def _on_use_selection(self, _event: object) -> None:
        self.prompt.SetValue(self._selection_text.strip())
        self._append_chat_log("Loaded selection into the prompt.")

    def _on_use_document(self, _event: object) -> None:
        self.prompt.SetValue(self._document_text.strip())
        self._append_chat_log("Loaded document text into the prompt.")

    def _apply_prompt_from_preset(self) -> None:
        selected = self.preset_choice.GetSelection()
        if selected == self._wx.NOT_FOUND or selected < 0 or selected >= len(self._prompt_presets):
            return
        preset = self._prompt_presets[selected]
        prompt = render_assistant_prompt(
            preset.name,
            selection_text=self._selection_text,
            document_text=self._document_text,
        )
        self.prompt.SetValue(prompt)
        self._append_chat_log(f"Loaded preset: {preset.title}")

    def _refresh_results(self) -> None:
        query = self.prompt.GetValue()
        self._filtered_tools = rank_assistant_tools(query, self._all_tools, limit=50)
        labels: list[str] = []
        for tool in self._filtered_tools:
            suffix = f" [{tool.command_id}]" if tool.command_id else ""
            labels.append(f"{tool.title}{suffix}")
        self.results.Set(labels)
        if labels:
            self.results.SetSelection(0)
            self._update_details()
            self.status.SetLabel(f"{len(labels)} tool(s) matched.")
        else:
            self.details.SetValue("")
            self.status.SetLabel("No matching tools.")

    def _on_selection_changed(self, _event: object) -> None:
        self._update_details()

    def _update_details(self) -> None:
        selected = self.results.GetSelection()
        if selected == self._wx.NOT_FOUND:
            return
        if selected < 0 or selected >= len(self._filtered_tools):
            return
        tool = self._filtered_tools[selected]
        extra = ""
        if tool.command_id:
            extra = f"\nCommand: {tool.command_id}"
        self.details.SetValue(
            f"{tool.title}\n\n{tool.description}\n\nCategory: {tool.category}{extra}"
        )

    def _on_run_selected(self, _event: object) -> None:
        self._run_selected()

    def _run_selected(self) -> None:
        selected = self.results.GetSelection()
        if selected == self._wx.NOT_FOUND:
            return
        if selected < 0 or selected >= len(self._filtered_tools):
            return
        tool = self._filtered_tools[selected]
        if tool.command_id is None:
            if tool.name == "run_python":
                self._open_python_tool()
            return
        if tool.requires_confirmation:
            answer = self._wx.MessageBox(
                f"Run '{tool.title}' now?",
                "Confirm Assistant Action",
                style=self._wx.YES_NO | self._wx.ICON_WARNING,
            )
            if answer != self._wx.YES:
                return
        self._append_chat_log(f"Ran action: {tool.title}")
        self._registry.run(tool.command_id)
        self.dialog.EndModal(self._wx.ID_OK)


class AssistantConnectionDialog:
    def __init__(self, parent: object) -> None:
        import wx

        self._wx = wx
        self.dialog = wx.Dialog(
            parent,
            title="AI Connection Settings",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetSize((700, 420))

        self._settings = load_assistant_connection_settings()
        self._api_key = load_assistant_api_key()

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(
            wx.StaticText(
                self.dialog,
                label=(
                    "Ollama does not require a key for local use. If you connect to an "
                    "authenticated endpoint, Quill stores the key with Windows DPAPI."
                ),
            ),
            0,
            wx.EXPAND | wx.ALL,
            8,
        )

        panel = wx.Panel(self.dialog)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.provider = wx.Choice(
            panel,
            choices=["Off", "Ollama (local)", "Custom HTTP"],
        )
        self.provider.SetSelection(
            {"off": 0, "ollama": 1, "custom": 2}.get(self._settings.provider, 1)
        )
        panel_sizer.Add(
            wx.StaticText(panel, label="Provider"),
            0,
            wx.LEFT | wx.RIGHT | wx.TOP,
            8,
        )
        panel_sizer.Add(self.provider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.host = wx.TextCtrl(panel)
        self.host.SetValue(self._settings.host)
        panel_sizer.Add(wx.StaticText(panel, label="Host URL"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        panel_sizer.Add(self.host, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.model = wx.TextCtrl(panel)
        self.model.SetValue(self._settings.model)
        panel_sizer.Add(wx.StaticText(panel, label="Model"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        panel_sizer.Add(self.model, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.api_key = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        self.api_key.SetValue(self._api_key)
        panel_sizer.Add(
            wx.StaticText(
                panel,
                label="API key (optional; stored encrypted with DPAPI)",
            ),
            0,
            wx.LEFT | wx.RIGHT | wx.TOP,
            8,
        )
        panel_sizer.Add(self.api_key, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        panel.SetSizer(panel_sizer)
        root.Add(panel, 1, wx.EXPAND | wx.ALL, 8)

        buttons = self.dialog.CreateButtonSizer(wx.OK | wx.CANCEL)
        if buttons is not None:
            root.Add(buttons, 0, wx.EXPAND | wx.ALL, 8)
        self.dialog.SetSizerAndFit(root)

    def show_modal(self) -> bool:
        self.dialog.CentreOnParent()
        try:
            if self.dialog.ShowModal() != self._wx.ID_OK:
                return False
            settings = AssistantConnectionSettings(
                provider={"0": "off", "1": "ollama", "2": "custom"}.get(
                    str(self.provider.GetSelection()),
                    "ollama",
                ),
                host=self.host.GetValue().strip() or "http://localhost:11434",
                model=self.model.GetValue().strip() or "llama3.1",
            )
            save_assistant_connection_settings(settings)
            save_assistant_api_key(self.api_key.GetValue())
            return True
        finally:
            self.dialog.Destroy()
