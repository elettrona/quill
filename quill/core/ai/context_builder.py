"""Context Builder + privacy preview (PRD §11).

Before any text is sent to a provider, exactly one component assembles it from an
explicit *scope*, runs it through redaction, and produces an accessible "what will
be sent" summary the user can read and approve. Today the pieces exist
(compaction, redaction) but nothing assembles them; this is that component.

This is wx-free core. The builder pulls editor state through a
:class:`ContextSource` Protocol and returns a :class:`ContextPreview` describing
the payload (scope, file, headings, word/token counts, whether the full document
is included, whether redaction fired). The UI renders that preview as the plain
"Context to share" dialog (Continue / Show Text / Cancel) and only then sends
``preview.text``.

Never-by-default (PRD §11): hidden/.env files, keys, tokens, private keys, and
large binaries are out of scope here by construction — the builder only ever sees
what the :class:`ContextSource` chooses to expose, and redaction is the backstop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

from quill.core.ai.compaction import estimate_tokens
from quill.stability.redaction import redact_source_tokens

__all__ = [
    "ContextScope",
    "ContextSource",
    "ContextRequest",
    "ContextPreview",
    "ContextBuilder",
]

# Heuristic cap for the document-summary scope body (chars), kept small so a
# "summary" never quietly becomes the whole document.
_SUMMARY_BODY_CHARS = 800


class ContextScope(StrEnum):
    """What slice of the world the agent may see (PRD §11).

    The single-document scopes are wired now. ``OPEN_DOCUMENTS``,
    ``WORKSPACE_SUMMARY``, ``EXPLICIT_FILES``, and ``GITHUB`` are reserved for the
    multi-file / integration phases; building with them raises until a source can
    supply them (so we never silently send less than the user asked for).
    """

    PROMPT_ONLY = "prompt_only"
    SELECTION = "selection"
    CURRENT_SECTION = "current_section"
    DOCUMENT_SUMMARY = "document_summary"
    FULL_DOCUMENT = "full_document"
    OPEN_DOCUMENTS = "open_documents"
    WORKSPACE_SUMMARY = "workspace_summary"
    EXPLICIT_FILES = "explicit_files"
    GITHUB = "github"


_WIRED_SCOPES: frozenset[ContextScope] = frozenset(
    {
        ContextScope.PROMPT_ONLY,
        ContextScope.SELECTION,
        ContextScope.CURRENT_SECTION,
        ContextScope.DOCUMENT_SUMMARY,
        ContextScope.FULL_DOCUMENT,
    }
)


class ContextSource(Protocol):
    """Editor state the builder may read, supplied by the UI."""

    def get_selection(self) -> str: ...
    def get_current_section(self) -> str: ...
    def get_document(self) -> str: ...
    def get_outline(self) -> list[str]: ...
    def get_file_name(self) -> str: ...
    def get_file_type(self) -> str: ...


@dataclass(frozen=True, slots=True)
class ContextRequest:
    """Ask for a payload at ``scope``, optionally prefixed with the user prompt."""

    scope: ContextScope
    prompt: str = ""
    include_outline: bool = True


@dataclass(frozen=True, slots=True)
class ContextPreview:
    """The accessible "what will be sent" summary plus the redacted payload."""

    scope: ContextScope
    text: str
    file_name: str
    file_type: str
    word_count: int
    token_estimate: int
    headings_included: tuple[str, ...] = field(default_factory=tuple)
    includes_full_document: bool = False
    includes_workspace: bool = False
    redaction_triggered: bool = False

    def speakable_summary(self) -> str:
        """One balanced sentence for the screen reader before sending."""
        parts = [
            f"Sharing {self.scope.value.replace('_', ' ')}",
            f"{self.word_count} words",
            f"about {self.token_estimate} tokens",
        ]
        if self.file_name:
            parts.append(f"from {self.file_name}")
        if self.includes_full_document:
            parts.append("the full document is included")
        if self.redaction_triggered:
            parts.append("a possible secret was redacted")
        return "; ".join(parts) + "."


class ContextBuilder:
    """Assemble + redact context for a :class:`ContextRequest`."""

    def __init__(self, source: ContextSource) -> None:
        self._source = source

    def build(self, request: ContextRequest) -> ContextPreview:
        scope = request.scope
        if scope not in _WIRED_SCOPES:
            raise NotImplementedError(
                f"Context scope {scope.value!r} is reserved for a later phase."
            )

        body, includes_full = self._body_for(scope)
        headings = tuple(self._source.get_outline()) if request.include_outline else ()

        assembled = self._assemble(request.prompt, headings, body)
        # Mask accidental key/token pastes inline WITHOUT truncating content
        # (the bundle redactor caps lines to 200 chars — wrong for a payload we
        # intend to send). redact_source_tokens preserves the document text.
        redacted = redact_source_tokens(assembled)
        triggered = redacted != assembled

        return ContextPreview(
            scope=scope,
            text=redacted,
            file_name=self._source.get_file_name(),
            file_type=self._source.get_file_type(),
            word_count=len(redacted.split()),
            token_estimate=estimate_tokens(redacted),
            headings_included=headings,
            includes_full_document=includes_full,
            includes_workspace=False,
            redaction_triggered=triggered,
        )

    # -- internals ---------------------------------------------------------

    def _body_for(self, scope: ContextScope) -> tuple[str, bool]:
        """Return (body text, includes_full_document) for a wired scope."""
        if scope is ContextScope.PROMPT_ONLY:
            return "", False
        if scope is ContextScope.SELECTION:
            return self._source.get_selection(), False
        if scope is ContextScope.CURRENT_SECTION:
            return self._source.get_current_section(), False
        if scope is ContextScope.DOCUMENT_SUMMARY:
            return self._summarize(self._source.get_document()), False
        # FULL_DOCUMENT
        return self._source.get_document(), True

    def _summarize(self, document: str) -> str:
        """Deterministic, tokenizer-free summary: outline + a truncated head.

        Not a model call — a cheap, predictable stand-in so the summary scope is
        always smaller than the full document (the heading list plus a capped
        excerpt). A model-backed summary can replace this body later without
        changing the preview contract.
        """
        outline = self._source.get_outline()
        head = document.strip()[:_SUMMARY_BODY_CHARS]
        truncated = "..." if len(document.strip()) > _SUMMARY_BODY_CHARS else ""
        lines = []
        if outline:
            lines.append("Outline: " + "; ".join(outline))
        lines.append("Excerpt: " + head + truncated)
        return "\n".join(lines)

    def _assemble(self, prompt: str, headings: tuple[str, ...], body: str) -> str:
        sections: list[str] = []
        if prompt:
            sections.append(f"Prompt:\n{prompt}")
        if headings:
            sections.append("Headings: " + "; ".join(headings))
        if body:
            sections.append(f"Content:\n{body}")
        return "\n\n".join(sections)
