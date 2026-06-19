"""Section-move primitives for Markdown and plain-text documents.

This module is a thin, pure helper on top of :mod:`quill.core.heading_organizer`.
It exists so a single QUILL-key chord can move the current heading's section up
or down without dragging the whole ``MainFrame`` along for the ride.  The
section-move UI lives in ``quill/ui/main_frame.py``; this module only knows
about text, caret positions, and announce strings.

Public API:

* :class:`Section` — frozen dataclass describing a heading section.
* :class:`MoveResult` — ``OK | NO_SECTION | TOP | BOTTOM | NO_SIBLING``.
* :func:`current_section_at` — find the section containing the caret.
* :func:`move_section` — apply a one-step move and return the new text, new
  caret, the result code, and a screen-reader-friendly announce string.

The Markdown path reuses :func:`quill.core.heading_organizer.parse_heading_blocks`
so fence-awareness (``` and ~~~) is inherited automatically.  For plain text
(no Markdown), we fall back to form-feed (``\\f``) delimited blocks, which the
main editor already produces when text is pasted from certain sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from quill.core.heading_organizer import parse_heading_blocks


@dataclass(frozen=True, slots=True)
class Section:
    level: int
    title: str
    start: int
    end: int

    @property
    def length(self) -> int:
        return self.end - self.start


class MoveResult(StrEnum):
    OK = "ok"
    NO_SECTION = "no_section"
    TOP = "top"
    BOTTOM = "bottom"
    NO_SIBLING = "no_sibling"


def _section_for_caret(blocks: list, caret: int) -> tuple[int, int, int, int] | None:
    """Return ``(index, level, section_start, section_end)`` for the section
    whose start is at or before ``caret`` and whose end is after ``caret``.

    If the caret is past the last section's end, return that last section.
    Returns ``None`` if there are no sections at all.
    """
    if not blocks:
        return None
    chosen_index = 0
    for index, block in enumerate(blocks):
        if block.start <= caret:
            chosen_index = index
        else:
            break
    block = blocks[chosen_index]
    return chosen_index, block.level, block.section_start, block.section_end


def current_section_at(text: str, caret: int, *, markup_kind: str = "markdown") -> Section | None:
    """Return the section containing ``caret``, or ``None`` if no section."""
    if markup_kind == "markdown":
        blocks = parse_heading_blocks(text, "markdown")
        found = _section_for_caret(blocks, caret)
        if found is None:
            return None
        _, level, start, end = found
        return Section(level=level, title="", start=start, end=end)
    # Plain text: split on form-feed (no nesting concept).
    if "\f" not in text:
        return None
    boundaries: list[int] = [0]
    for index, ch in enumerate(text):
        if ch == "\f":
            boundaries.append(index + 1)
    if boundaries[-1] != len(text):
        boundaries.append(len(text))
    for index in range(len(boundaries) - 1):
        section_start = boundaries[index]
        section_end = boundaries[index + 1]
        if section_start <= caret < section_end:
            return Section(level=0, title="", start=section_start, end=section_end)
    if boundaries and caret >= boundaries[-1]:
        last_start = boundaries[-1]
        return Section(level=0, title="", start=last_start, end=len(text))
    return None


def _find_sibling(blocks: list, section_index: int, direction: Literal["up", "down"]) -> int | None:
    """Return the index of the closest sibling (same ``level``) of
    ``blocks[section_index]`` in the requested direction, or ``None``.

    A sibling shares the same level and has the same parent (the nearest
    preceding heading whose level is strictly less).  Top-level headings
    (``level == 1``) all share an implicit parent of 0, so any other
    ``level == 1`` heading is a sibling.
    """
    if not blocks or section_index < 0 or section_index >= len(blocks):
        return None
    current = blocks[section_index]
    if direction == "up":
        for index in range(section_index - 1, -1, -1):
            other = blocks[index]
            if other.level < current.level:
                return None
            if other.level == current.level:
                return index
        return None
    # direction == "down"
    for index in range(section_index + 1, len(blocks)):
        other = blocks[index]
        if other.level < current.level:
            return None
        if other.level == current.level:
            return index
    return None


def _swap_sections(text: str, first: tuple[int, int], second: tuple[int, int]) -> str:
    """Swap two ``(start, end)`` ranges in ``text``.

    Ranges must be non-overlapping and ordered such that ``first`` precedes
    ``second``.  The whitespace gap between the two ranges is attached to
    whichever section ends up on top so the moved heading keeps its
    surrounding blank lines.
    """
    a_start, a_end = first
    b_start, b_end = second
    if a_end > b_start:
        raise ValueError("ranges must be ordered and non-overlapping")
    a_text = text[a_start:a_end]
    b_text = text[b_start:b_end]
    gap = text[a_end:b_start]
    # The gap (whitespace between the sections) rides with whichever
    # section now comes first.  For "up" we want the moved-up heading to
    # keep the gap above it; for "down" we want it below.
    if a_text.endswith("\n") and not b_text.endswith("\n"):
        b_text = b_text.rstrip("\n") + "\n"
    if not b_text.endswith("\n") and gap.endswith("\n"):
        # CommonMark headings should end with a newline.
        b_text = b_text + "\n"
    return text[:a_start] + b_text + gap + a_text + text[b_end:]


def _caret_after_move(
    caret: int,
    section_start: int,
    new_text: str,
    moved_heading_line: str,
) -> int:
    """Compute the caret position after a section has been moved.

    The caret is preserved as an offset from the heading line start (column
    within the heading) so it lands on the same column of the moved heading.
    We look the moved heading up in ``new_text`` rather than relying on a
    precomputed destination, because the swap helper can shift the section
    by an arbitrary offset (the gap between the swapped sections rides
    with the moved section).
    """
    column = max(0, caret - section_start)
    heading_pos = new_text.find(moved_heading_line)
    if heading_pos == -1:
        return caret
    heading_line_end = moved_heading_line.find("\n")
    if heading_line_end == -1:
        heading_line_end = len(moved_heading_line)
    column = min(column, heading_line_end)
    return heading_pos + column


def _announce(result: MoveResult, sibling_title: str = "") -> str:
    if result == MoveResult.TOP:
        return "Top!"
    if result == MoveResult.BOTTOM:
        return "Bottom!"
    if result == MoveResult.NO_SECTION:
        return "No section to move"
    if result == MoveResult.NO_SIBLING:
        return "No sibling to swap with"
    if sibling_title:
        return sibling_title
    return ""


def move_section(
    text: str,
    caret: int,
    direction: Literal["up", "down"],
    *,
    markup_kind: str = "markdown",
) -> tuple[str, int, MoveResult, str]:
    """Move the section containing ``caret`` one step in ``direction``.

    Returns ``(new_text, new_caret, result, announce_text)``.

    * ``new_text`` is the rewritten document.  When the move is rejected
      (no section, already at top/bottom, no sibling), ``new_text`` equals
      the input.
    * ``new_caret`` is the new caret position.  When the move is rejected
      it equals the input caret.
    * ``result`` is one of the :class:`MoveResult` codes.
    * ``announce_text`` is a screen-reader-friendly short string (already
      used by the QUILL-key wrapper).
    """
    if markup_kind in {"markdown", "html"}:
        blocks = parse_heading_blocks(text, markup_kind)
        if not blocks:
            return text, caret, MoveResult.NO_SECTION, _announce(MoveResult.NO_SECTION)
        found = _section_for_caret(blocks, caret)
        if found is None:
            return text, caret, MoveResult.NO_SECTION, _announce(MoveResult.NO_SECTION)
        section_index, _level, section_start, section_end = found
        sibling_index = _find_sibling(blocks, section_index, direction)
        if direction == "up" and section_index == 0:
            return text, caret, MoveResult.TOP, _announce(MoveResult.TOP)
        if direction == "down" and section_index == len(blocks) - 1:
            return text, caret, MoveResult.BOTTOM, _announce(MoveResult.BOTTOM)
        if sibling_index is None:
            return text, caret, MoveResult.NO_SIBLING, _announce(MoveResult.NO_SIBLING)
        sibling = blocks[sibling_index]
        # ``heading_line`` is the unique span we use to locate the moved
        # heading in the new text.  For Markdown it is the full heading line
        # up to the next newline; for HTML (no newlines) it is the
        # whole `<h...>...</h...>` span.
        newline_at = text.find("\n", section_start)
        if newline_at == -1:
            heading_line = text[blocks[section_index].start : blocks[section_index].end]
        else:
            heading_line = text[section_start:newline_at]
        if direction == "up":
            new_text = _swap_sections(
                text,
                (sibling.section_start, sibling.section_end),
                (section_start, section_end),
            )
            new_caret = _caret_after_move(
                caret,
                section_start,
                new_text,
                heading_line,
            )
            return new_text, new_caret, MoveResult.OK, sibling.title.strip()
        # direction == "down"
        new_text = _swap_sections(
            text,
            (section_start, section_end),
            (sibling.section_start, sibling.section_end),
        )
        new_caret = _caret_after_move(
            caret,
            section_start,
            new_text,
            heading_line,
        )
        return new_text, new_caret, MoveResult.OK, sibling.title.strip()

    # Plain-text form-feed fallback.
    if "\f" not in text:
        return text, caret, MoveResult.NO_SECTION, _announce(MoveResult.NO_SECTION)
    section = current_section_at(text, caret, markup_kind="plain")
    if section is None:
        return text, caret, MoveResult.NO_SECTION, _announce(MoveResult.NO_SECTION)
    boundaries: list[int] = [0]
    for index, ch in enumerate(text):
        if ch == "\f":
            boundaries.append(index + 1)
    if boundaries[-1] != len(text):
        boundaries.append(len(text))
    section_index = -1
    for index in range(len(boundaries) - 1):
        if boundaries[index] == section.start:
            section_index = index
            break
    if section_index < 0:
        return text, caret, MoveResult.NO_SECTION, _announce(MoveResult.NO_SECTION)
    if direction == "up" and section_index == 0:
        return text, caret, MoveResult.TOP, _announce(MoveResult.TOP)
    if direction == "down" and section_index == len(boundaries) - 2:
        return text, caret, MoveResult.BOTTOM, _announce(MoveResult.BOTTOM)
    if direction == "up":
        target = section_index - 1
    else:
        target = section_index + 1
    target_start = boundaries[target]
    target_end = boundaries[target + 1]
    if direction == "up":
        new_text = _swap_sections(text, (target_start, target_end), (section.start, section.end))
    else:
        new_text = _swap_sections(text, (section.start, section.end), (target_start, target_end))
    # For plain text, "heading line" doesn't apply; preserve the caret
    # offset within the moved section by looking for the first character
    # of the moved section in the new text.
    moved_prefix = text[section.start : min(section.start + 1, section.end)]
    if moved_prefix:
        moved_pos = new_text.find(moved_prefix)
        if moved_pos != -1:
            column = caret - section.start
            new_caret = moved_pos + column
        else:
            new_caret = caret
    else:
        new_caret = caret
    return new_text, new_caret, MoveResult.OK, ""
