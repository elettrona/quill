"""Durable, user-owned writing instructions the assistant always honors (AI-21).

Unlike the trained writing *style* (which captures the user's voice from
samples), writing *instructions* are explicit rules the user writes and owns:
house style, tone, audience, words to avoid. They live in plain Markdown files
the user can open and edit, at two scopes:

- Global/project scope: ``<app data>/ai/writing-instructions.md`` — applies to
  every document.
- Document scope: a sidecar next to the document named
  ``<document>.quill-instructions.md`` — applies to that document only and is
  appended after the global rules so a document can refine the house style.

Nothing here is a hidden prompt: the files are visible, user-controlled, and
re-read on demand (live reload). This module is pure I/O over text files; the
assistant turns the loaded text into a preamble segment via
:func:`instructions_preamble`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from quill.core.paths import app_data_dir

DOCUMENT_SIDECAR_SUFFIX = ".quill-instructions.md"
_MAX_INSTRUCTIONS_CHARS = 8000


@dataclass(frozen=True, slots=True)
class WritingInstructions:
    """Resolved writing instructions for a document, by scope."""

    global_text: str = ""
    document_text: str = ""

    @property
    def is_empty(self) -> bool:
        return not (self.global_text.strip() or self.document_text.strip())


def global_instructions_path() -> Path:
    """The always-applied, project-wide instructions file."""
    return app_data_dir() / "ai" / "writing-instructions.md"


def document_instructions_path(document_path: Path | str | None) -> Path | None:
    """The sidecar instructions file for a document, or None if it has no path."""
    if not document_path:
        return None
    path = Path(document_path)
    if not path.name:
        return None
    return path.with_name(path.name + DOCUMENT_SIDECAR_SUFFIX)


def _read_text(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return text[:_MAX_INSTRUCTIONS_CHARS].strip()


def load_instructions(document_path: Path | str | None = None) -> WritingInstructions:
    """Read the global and document-scoped instructions (live, no caching)."""
    return WritingInstructions(
        global_text=_read_text(global_instructions_path()),
        document_text=_read_text(document_instructions_path(document_path)),
    )


def save_global_instructions(text: str) -> None:
    """Write the project-wide instructions file (creating its folder)."""
    path = global_instructions_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text((text or "").strip() + "\n", encoding="utf-8")


def save_document_instructions(document_path: Path | str, text: str) -> None:
    """Write the document sidecar instructions file."""
    path = document_instructions_path(document_path)
    if path is None:
        raise ValueError("Document has no path; cannot save document instructions.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text((text or "").strip() + "\n", encoding="utf-8")


def instructions_preamble(instructions: WritingInstructions) -> str:
    """Build the preamble segment that pins the user's rules (empty if none).

    The wording makes the rules mandatory but, like the style preamble, forbids
    using them as an excuse to shorten or skip the requested task.
    """
    if instructions.is_empty:
        return ""
    sections: list[str] = []
    if instructions.global_text.strip():
        sections.append(instructions.global_text.strip())
    if instructions.document_text.strip():
        sections.append(
            "Document-specific instructions (these refine the rules above):\n"
            + instructions.document_text.strip()
        )
    body = "\n\n".join(sections)
    return (
        "Follow the user's writing instructions below. They are mandatory rules for "
        "house style, tone, audience, and words to avoid. Honor them fully, but never "
        "use them as a reason to shorten, omit, or skip content — always complete the "
        f"requested task at the length it deserves.\n\nWriting instructions:\n{body}"
    )
