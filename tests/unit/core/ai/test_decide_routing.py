"""Decision sanitization: the model's raw choice is constrained before it can
touch the document or run a tool. These guard the 'tool issues' class of bugs —
a hallucinated action, an unlisted/destructive tool id, or malformed output."""
from __future__ import annotations

import json

from quill.core.ai.llama_cpp_backend import LlamaCppBackend


def _backend(monkeypatch, payload: str) -> LlamaCppBackend:
    backend = LlamaCppBackend(model_path="dummy.gguf")
    # Bypass the model: feed decide() a crafted completion string.
    monkeypatch.setattr(backend, "_complete", lambda *a, **k: payload)
    return backend


def test_invalid_action_falls_back_to_answer(monkeypatch) -> None:
    b = _backend(monkeypatch, json.dumps({"action": "frobnicate", "text": "x"}))
    assert b.decide("hi", "", ("file.save",)).action == "answer"


def test_run_with_unlisted_tool_is_not_run(monkeypatch) -> None:
    # Model tried to run a tool that isn't in the allowlist for this turn.
    b = _backend(monkeypatch, json.dumps({"action": "run", "tool": "file.delete_all"}))
    decision = b.decide("do it", "", ("file.save",))
    assert decision.action == "answer"
    assert decision.tool == ""


def test_run_with_valid_tool_is_kept(monkeypatch) -> None:
    b = _backend(monkeypatch, json.dumps({"action": "run", "tool": "file.save"}))
    decision = b.decide("save it", "", ("file.save",))
    assert decision.action == "run"
    assert decision.tool == "file.save"


def test_run_without_tool_falls_back_to_answer(monkeypatch) -> None:
    b = _backend(monkeypatch, json.dumps({"action": "run", "tool": ""}))
    assert b.decide("go", "", ("file.save",)).action == "answer"


def test_non_json_output_becomes_answer(monkeypatch) -> None:
    b = _backend(monkeypatch, "I think you should add a heading.")
    decision = b.decide("hi", "", ("file.save",))
    assert decision.action == "answer"
    assert decision.text == "I think you should add a heading."


def test_insert_decision_is_preserved(monkeypatch) -> None:
    b = _backend(monkeypatch, json.dumps({"action": "insert", "text": "Hello world"}))
    decision = b.decide("write hello world", "", ("file.save",))
    assert decision.action == "insert"
    assert decision.text == "Hello world"
