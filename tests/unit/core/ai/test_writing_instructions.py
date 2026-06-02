"""Tests for durable writing instructions (AI-21)."""

from __future__ import annotations

from pathlib import Path

import pytest

import quill.core.ai.writing_instructions as wi
from quill.core.ai.assistant import Assistant
from quill.core.ai.backend import AIBackend
from quill.core.ai.writing_instructions import (
    DOCUMENT_SIDECAR_SUFFIX,
    WritingInstructions,
    document_instructions_path,
    instructions_preamble,
    load_instructions,
    save_document_instructions,
    save_global_instructions,
)


@pytest.fixture(autouse=True)
def _isolated_app_data(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(wi, "app_data_dir", lambda: tmp_path)


def test_document_sidecar_path_appends_suffix() -> None:
    path = document_instructions_path(Path("notes/story.md"))
    assert path is not None
    assert path.name == "story.md" + DOCUMENT_SIDECAR_SUFFIX


def test_document_sidecar_path_none_without_path() -> None:
    assert document_instructions_path(None) is None
    assert document_instructions_path("") is None


def test_load_instructions_empty_when_no_files(tmp_path: Path) -> None:
    instructions = load_instructions(tmp_path / "doc.md")
    assert instructions.is_empty


def test_save_and_load_global_instructions() -> None:
    save_global_instructions("Use British spelling.")
    instructions = load_instructions(None)
    assert "British spelling" in instructions.global_text
    assert instructions.document_text == ""
    assert not instructions.is_empty


def test_save_and_load_document_instructions(tmp_path: Path) -> None:
    doc = tmp_path / "story.md"
    save_document_instructions(doc, "Second person, present tense.")
    instructions = load_instructions(doc)
    assert "present tense" in instructions.document_text


def test_save_document_instructions_requires_path() -> None:
    with pytest.raises(ValueError, match="no path"):
        save_document_instructions("", "x")


def test_instructions_preamble_empty_when_no_instructions() -> None:
    assert instructions_preamble(WritingInstructions()) == ""


def test_instructions_preamble_includes_both_scopes() -> None:
    preamble = instructions_preamble(
        WritingInstructions(global_text="House style.", document_text="Doc rule.")
    )
    assert "House style." in preamble
    assert "Doc rule." in preamble
    assert "Document-specific" in preamble
    # The mandatory-but-complete framing is present.
    assert "mandatory" in preamble.lower()
    assert "shorten" in preamble.lower()


def test_load_instructions_live_reload(tmp_path: Path) -> None:
    doc = tmp_path / "story.md"
    save_document_instructions(doc, "First version.")
    assert "First version" in load_instructions(doc).document_text
    save_document_instructions(doc, "Second version.")
    # No caching: the second read reflects the new content.
    assert "Second version" in load_instructions(doc).document_text


class _EchoBackend(AIBackend):
    name = "echo"

    def __init__(self) -> None:
        self.last_prompt = ""

    def is_available(self) -> tuple[bool, str | None]:
        return True, None

    def respond(self, prompt: str) -> str:
        self.last_prompt = prompt
        return "ok"


def test_assistant_applies_instructions_then_style_then_prompt() -> None:
    backend = _EchoBackend()
    assistant = Assistant(backend=backend)
    assistant.set_instructions_preamble("RULES")
    assistant.set_style_preamble("VOICE")
    assistant.transform("rewrite", "hello")
    prompt = backend.last_prompt
    assert prompt.index("RULES") < prompt.index("VOICE") < prompt.index("hello")


def test_assistant_no_preambles_leaves_prompt_unwrapped() -> None:
    backend = _EchoBackend()
    assistant = Assistant(backend=backend)
    assistant.transform("rewrite", "hello")
    assert backend.last_prompt.startswith("Rewrite the following")
