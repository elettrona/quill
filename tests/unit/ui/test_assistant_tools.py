"""Tests for RunPythonDialog threading behaviour (M-29)."""

from __future__ import annotations

import time
from types import SimpleNamespace

from quill.ui.assistant_tools import RunPythonDialog


class _TextCtrl:
    def __init__(self, value: str = "") -> None:
        self._value = value

    def GetValue(self) -> str:
        return self._value

    def SetValue(self, value: str) -> None:
        self._value = value


class _Button:
    def __init__(self, *, enabled: bool = True) -> None:
        self._enabled = enabled

    def Enable(self, value: bool = True) -> None:
        self._enabled = value

    def IsEnabled(self) -> bool:
        return self._enabled


class _StaticText:
    def __init__(self) -> None:
        self.label = ""

    def SetLabel(self, value: str) -> None:
        self.label = value


def test_run_python_does_not_block_ui_thread() -> None:
    # M-29: _on_run must submit the sandbox call to a worker thread and
    # re-enable buttons via CallAfter so the UI thread stays responsive.
    call_after_calls: list[tuple] = []

    dialog = RunPythonDialog.__new__(RunPythonDialog)
    dialog._wx = SimpleNamespace(CallAfter=lambda fn, *args: call_after_calls.append((fn, args)))
    dialog._document_text = ""
    dialog._selection_text = ""
    dialog._outline = []
    dialog.code = _TextCtrl("print('hello')")
    dialog.run_button = _Button()
    dialog.apply_button = _Button()
    dialog.status = _StaticText()

    dialog._on_run(object())

    # Buttons disabled immediately (on UI thread).
    assert not dialog.run_button.IsEnabled()
    assert not dialog.apply_button.IsEnabled()
    assert dialog.status.label == "Running..."

    # Wait for the worker thread to finish and fire CallAfter.
    deadline = time.monotonic() + 10.0
    while not call_after_calls and time.monotonic() < deadline:
        time.sleep(0.05)

    assert call_after_calls, "worker thread did not call wx.CallAfter"
    fn, args = call_after_calls[0]
    assert getattr(fn, "__func__", fn) is RunPythonDialog._finish_run


def test_finish_run_re_enables_run_button() -> None:
    from quill.core.python_sandbox import PythonSandboxResult

    dialog = RunPythonDialog.__new__(RunPythonDialog)
    dialog._wx = SimpleNamespace()
    dialog._latest_result = None
    dialog.run_button = _Button(enabled=False)
    dialog.apply_button = _Button(enabled=False)
    dialog.status = _StaticText()
    dialog.preview = _TextCtrl()

    result = PythonSandboxResult(
        stdout="",
        stderr="",
        result="hello",
        error="",
        timed_out=False,
        returncode=0,
        elapsed_seconds=0.1,
    )
    dialog._finish_run(result)

    assert dialog.run_button.IsEnabled()
    assert dialog.apply_button.IsEnabled()
    assert "0.10" in dialog.status.label
