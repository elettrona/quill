"""Structured List Studio settings with the PRD's recommended defaults (§2-§13).

The PRD describes a large, multi-scope configuration surface. This dataclass
captures the options the *core* logic actually consumes — selection
interpretation, marker/spacing styles, the Markdown definition-list profile, and
the verbosity used for announcements — each defaulting to the PRD's recommended
value so that "press F2 and it just works" holds without anyone visiting Settings
(§2.1). The wx settings UI and profile/preset system layer on top of this; they
do not change the meaning of any field here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DefinitionMarkdownProfile(Enum):
    """How a definition list serializes into Markdown (§7.6, §21.2).

    Markdown definition-list syntax is not universal, so the profile is explicit
    rather than assumed. ``ASK`` means the UI must prompt before generating
    (offering embedded HTML as the safe portable option, §21.3).
    """

    ASK = "ask"
    PANDOC = "pandoc"  # term \n : definition
    MARKDOWN_EXTRA = "markdown_extra"  # same colon syntax, looser blank-line rules
    MULTIMARKDOWN = "multimarkdown"
    HTML_FALLBACK = "html_fallback"  # embedded <dl> inside Markdown
    PLAIN_FALLBACK = "plain_fallback"  # "Term: Definition" bullet/paragraph
    DISABLED = "disabled"


@dataclass(slots=True)
class StructuredListSettings:
    """Excellent-defaults configuration for the Structured List Studio."""

    # -- selection conversion (§5) ---------------------------------------- #
    # "Automatically detect" by default; the interpreter falls back to paragraph
    # vs line based on blank-line structure.
    selection_mode: str = "auto"  # auto | paragraph | nonblank_line | every_line
    blank_lines_as_separators: bool = True  # §5.2 recommended
    create_blank_items: bool = False
    preserve_internal_breaks: bool = True  # §5.3 recommended
    trim_leading: bool = True  # §5.4
    trim_trailing: bool = True
    collapse_internal_spaces: bool = False  # preserve internal spaces (§5.4)

    # -- import marker handling (§6.2) ------------------------------------ #
    detect_existing_markers: bool = True  # detect & strip consistent markers
    indentation_as_nesting: bool = False  # §6.3 "never create nesting automatically"

    # -- Markdown source (§7) --------------------------------------------- #
    bullet_marker: str = "-"  # §7.1 preserve-then-dash
    ordered_strategy: str = "sequential"  # sequential | repeat_one (§7.2)
    ordered_delimiter: str = "."  # "." or ")" (§7.3)
    task_check_mark: str = "x"  # lowercase x by default (§7.4)
    markdown_loose: bool = False  # tight by default; loosen when needed (§7.5)
    definition_markdown_profile: DefinitionMarkdownProfile = DefinitionMarkdownProfile.ASK

    # -- HTML source (§8) ------------------------------------------------- #
    html_indent: str = "  "  # two-space convention by default (§8.1)
    html_checkbox_disabled: bool = True  # §8.2 recommended

    # -- numbering (§9) --------------------------------------------------- #
    ordered_start: int = 1
    preserve_start_value: bool = True  # §9 recommended

    # -- checklist (§10) -------------------------------------------------- #
    new_task_checked: bool = False  # §10.1 recommended "Unchecked"

    # -- accessibility (§11) ---------------------------------------------- #
    verbosity: str = "standard"  # concise | standard | detailed (§11.1)

    # -- definition list terminology (§8.5, §25) -------------------------- #
    definition_term_label: str = "Definition"  # Definition | Description | Explanation

    def newline(self) -> str:
        """The line ending used for generated source (LF; QUILL normalizes)."""
        return "\n"
