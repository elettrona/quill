"""MainFrameEditorHost adapter: delegates to MainFrame primitives correctly."""

from __future__ import annotations

from dataclasses import dataclass, field

from quill.core.ai.diff_review import build_diff_review
from quill.ui.agent_editor_host import MainFrameEditorHost


@dataclass
class FakeEditor:
    value: str = "the cat sat on the mat"
    selection: str = "the cat sat on the mat"

    def GetValue(self) -> str:
        return self.value

    def GetStringSelection(self) -> str:
        return self.selection


@dataclass
class FakeOutline:
    title: str


@dataclass
class FakeDoc:
    path: str | None = "notes.md"


@dataclass
class FakeController:
    """Stands in for MainFrame; records the primitive calls the host makes."""

    editor: FakeEditor = field(default_factory=FakeEditor)
    document: FakeDoc = field(default_factory=FakeDoc)
    frame: object = None
    replaced: list[str] = field(default_factory=list)
    inserted: list[str] = field(default_factory=list)
    doc_writes: list[str] = field(default_factory=list)
    checkpoints: list[str] = field(default_factory=list)
    statuses: list[str] = field(default_factory=list)
    commands_run: list[str] = field(default_factory=list)
    diff_calls: list[tuple[str, str]] = field(default_factory=list)
    # Set by the test to simulate the user accepting hunks in the diff dialog.
    diff_accept_text: str | None = None

    def _outline_entries(self):
        return [FakeOutline("Intro"), FakeOutline("Body")]

    def _record_persistent_undo_state(self, text: str) -> None:
        self.checkpoints.append(text)

    def _ai_replace_selection(self, text: str) -> None:
        self.replaced.append(text)

    def _ai_insert_text(self, text: str) -> None:
        self.inserted.append(text)

    def _ai_set_document_text(self, text: str) -> None:
        self.doc_writes.append(text)

    def _ai_run_command(self, command_id: str) -> None:
        self.commands_run.append(command_id)

    def _set_status(self, message: str) -> None:
        self.statuses.append(message)

    def open_ai_diff_review(self, original, revised, on_apply, *, title="Review AI Changes"):
        self.diff_calls.append((original, revised))
        if self.diff_accept_text is not None:
            on_apply(self.diff_accept_text)


def test_reads_delegate_to_editor() -> None:
    c = FakeController()
    host = MainFrameEditorHost(c)
    assert host.get_document() == "the cat sat on the mat"
    assert host.get_selection() == "the cat sat on the mat"
    assert host.get_outline() == ["Intro", "Body"]
    assert host.get_file_type() == "md"


def test_apply_replacement_without_preview_uses_real_path() -> None:
    c = FakeController()
    host = MainFrameEditorHost(c)
    host.create_undo_checkpoint("Writing Companion")
    host.apply_replacement("The cat curled up on the mat.")
    assert c.checkpoints == ["the cat sat on the mat"]
    assert c.replaced == ["The cat curled up on the mat."]


def test_insert_and_run_command_delegate() -> None:
    c = FakeController()
    host = MainFrameEditorHost(c)
    host.apply_insert("hello")
    host.run_command("file.save")
    host.announce("done")
    assert c.inserted == ["hello"]
    assert c.commands_run == ["file.save"]
    assert c.statuses == ["done"]


def test_preview_applies_accepted_hunks_and_suppresses_double_apply() -> None:
    # Simulate the user accepting the proposed text in the per-hunk dialog.
    c = FakeController(diff_accept_text="The cat curled up on the mat.")
    host = MainFrameEditorHost(c)
    review = build_diff_review("the cat sat on the mat", "The cat curled up on the mat.")

    applied = host.preview_diff(review)
    assert applied is True
    # The dialog was shown with original + accept_all proposed.
    assert c.diff_calls == [("the cat sat on the mat", "The cat curled up on the mat.")]
    # Applied the accepted text via the real replace path, with an undo checkpoint.
    assert c.replaced == ["The cat curled up on the mat."]
    assert len(c.checkpoints) == 1

    # The gateway's follow-up checkpoint + apply must NOT double-apply this turn.
    host.create_undo_checkpoint("Writing Companion")
    host.apply_replacement("The cat curled up on the mat.")
    assert c.replaced == ["The cat curled up on the mat."]  # unchanged
    assert len(c.checkpoints) == 1  # unchanged


def test_preview_declined_returns_false_and_applies_nothing() -> None:
    c = FakeController(diff_accept_text=None)  # user closes without applying
    host = MainFrameEditorHost(c)
    review = build_diff_review("a", "b")
    assert host.preview_diff(review) is False
    assert c.replaced == []
    assert c.checkpoints == []


def test_file_type_empty_when_no_path() -> None:
    c = FakeController(document=FakeDoc(path=None))
    assert MainFrameEditorHost(c).get_file_type() == ""
