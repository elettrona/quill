"""Spoken vocabulary for inline text formatting (rtf.md "a spoken formatting model").

QUILL's native rich surface announces formatting the way it already announces
actions, so a screen-reader user *hears* bold, italic, headings and links instead
of only seeing them. This module is wx-free and takes primitive formatting flags
(not any ``quill.io`` rich type) so ``core`` stays at the bottom of the layer
stack: the UI reads the caret context and passes flags here for a phrase.
"""

from __future__ import annotations

__all__ = ["describe_inline_format", "describe_format_transition"]


def describe_inline_format(
    *,
    bold: bool = False,
    italic: bool = False,
    href: str | None = None,
    heading_level: int = 0,
    bullet: bool = False,
) -> str:
    """Return a spoken description of the formatting in effect, or ``""``.

    Examples: ``"bold"``, ``"bold italic"``, ``"link"``, ``"heading level 2"``,
    ``"bullet, bold"``. An empty string means plain body text with no formatting,
    which the announcer should leave silent.
    """
    parts: list[str] = []
    if heading_level:
        parts.append(f"heading level {heading_level}")
    elif bullet:
        parts.append("bullet")
    inline: list[str] = []
    if bold:
        inline.append("bold")
    if italic:
        inline.append("italic")
    if href:
        inline.append("link")
    if inline:
        parts.append(" ".join(inline))
    return ", ".join(parts)


def describe_format_transition(previous: str, current: str) -> str:
    """Describe a change in formatting as the caret moves, or ``""``.

    Speaks only the delta so navigation stays terse: entering bold says ``"bold"``,
    leaving it says ``"plain"``. Identical contexts say nothing.
    """
    if previous == current:
        return ""
    if not current:
        return "plain"
    return current
