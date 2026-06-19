from __future__ import annotations

import re
from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)
class HeadingBlock:
    source_index: int
    level: int
    title: str
    start: int
    end: int
    section_start: int
    section_end: int
    attributes: str = ""


_MD_HEADING_PATTERN = re.compile(r"^(?P<marker>#{1,6})[ \t]*(?P<title>.*)$", re.MULTILINE)
_HTML_HEADING_PATTERN = re.compile(
    r"<h(?P<level>[1-6])(?P<attrs>[^>]*)>(?P<body>.*?)</h(?P=level)>",
    re.IGNORECASE | re.DOTALL,
)
_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
# Recognise the opening line of a fenced code block.  The closing fence is any
# line that contains only the same fence character (``` or ~~~), optionally
# preceded by up to three spaces of indentation and followed by optional
# trailing whitespace.  We deliberately use a permissive regex here because
# indented closing fences (CommonMark §4.5) are common in real-world docs.
_FENCE_PATTERN = re.compile(r"^(?P<indent>[ ]{0,3})(?P<fence>`{3,}|~{3,})[ \t]*(?P<info>.*)$")


def parse_heading_blocks(text: str, markup_kind: str) -> list[HeadingBlock]:
    if markup_kind == "markdown":
        return _parse_markdown_heading_blocks(text)
    if markup_kind == "html":
        return _parse_html_heading_blocks(text)
    return []


def _is_fence_close(line: str, open_fence: str) -> bool:
    """Return True if ``line`` closes the fence opened with ``open_fence``.

    CommonMark §4.5: a closing fence must use the same character (``` or ~~~)
    as the opening fence and be at least as long.  Indentation up to three
    spaces is allowed.  Anything after the fence is treated as info-string
    content and ignored.
    """
    stripped = line.lstrip(" ")
    indent = len(line) - len(stripped)
    if indent > 3:
        return False
    if not stripped.startswith(open_fence[0]):
        return False
    char = open_fence[0]
    count = 0
    for ch in stripped:
        if ch == char:
            count += 1
        else:
            break
    return count >= len(open_fence) and stripped[count:].strip() == ""


def validate_heading_sequence(
    blocks: list[HeadingBlock],
    *,
    require_single_h1: bool = False,
) -> list[str]:
    issues: list[str] = []
    if not blocks:
        return issues
    first = blocks[0]
    if first.level != 1:
        issues.append(
            f"Heading order should start at H1 (found H{first.level}: {first.title or '(empty)'})"
        )
    h1_count = 0
    previous_level = 0
    for block in blocks:
        title = block.title.strip()
        if not title:
            issues.append(f"Heading H{block.level} is empty")
        if block.level == 1:
            h1_count += 1
        if previous_level and block.level > previous_level + 1:
            issues.append(
                f"Heading level skipped: H{previous_level} -> H{block.level} at "
                f"'{title or '(empty heading)'}'"
            )
        previous_level = block.level
    if require_single_h1 and h1_count > 1:
        issues.append(f"Expected a single H1 but found {h1_count}")
    return issues


@dataclass(frozen=True, slots=True)
class HeadingContext:
    level: int
    ordinal: int
    total: int
    title: str


def heading_context_at(text: str, target: int, markup_kind: str) -> HeadingContext | None:
    """Describe the heading whose start line contains ``target``.

    Returns the heading level (1-6), its 1-based ordinal among all headings,
    the total heading count, and the heading title. Matching is by line so it
    is robust to leading whitespace differences. Returns ``None`` when the
    target is not on a heading line.
    """
    blocks = parse_heading_blocks(text, markup_kind)
    if not blocks:
        return None
    target_line = text.count("\n", 0, target)
    for ordinal, block in enumerate(blocks, start=1):
        if text.count("\n", 0, block.start) == target_line:
            return HeadingContext(
                level=block.level,
                ordinal=ordinal,
                total=len(blocks),
                title=block.title.strip(),
            )
    return None


def apply_heading_organizer_edits(
    text: str,
    markup_kind: str,
    updated_blocks: list[HeadingBlock],
) -> str:
    original_blocks = parse_heading_blocks(text, markup_kind)
    if not original_blocks or not updated_blocks:
        return text
    by_index = {block.source_index: block for block in original_blocks}
    first_start = min(block.section_start for block in original_blocks)
    last_end = max(block.section_end for block in original_blocks)
    rebuilt: list[str] = [text[:first_start]]
    for block in updated_blocks:
        original = by_index.get(block.source_index)
        if original is None:
            continue
        section = text[original.section_start : original.section_end]
        rebuilt.append(
            _rewrite_first_heading(section, markup_kind, block.level, block.title, original)
        )
    rebuilt.append(text[last_end:])
    return "".join(rebuilt)


def _parse_markdown_heading_blocks(text: str) -> list[HeadingBlock]:
    # Walk the document line by line so we can recognise fenced code blocks
    # (``` or ~~~) and skip any `# ...` lines that appear inside them.
    # CommonMark §4.5: an opening fence is 3+ backticks or tildes; a closing
    # fence must use the same character and be at least as long.
    blocks: list[HeadingBlock] = []
    open_fence: str | None = None
    block_index = 0
    line_start = 0
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if open_fence is not None:
            if _is_fence_close(line, open_fence):
                open_fence = None
        else:
            fence_match = _FENCE_PATTERN.match(line) if indent <= 3 else None
            if fence_match is not None:
                open_fence = fence_match.group("fence")
            else:
                heading_match = _MD_HEADING_PATTERN.match(line)
                if heading_match is not None:
                    start = line_start
                    end = line_start + len(line)
                    blocks.append(
                        HeadingBlock(
                            source_index=block_index,
                            level=len(heading_match.group("marker")),
                            title=(heading_match.group("title") or "").strip(),
                            start=start,
                            end=end,
                            section_start=start,
                            section_end=0,  # filled in once the next block is found
                        )
                    )
                    block_index += 1
        line_start += len(line)
    # Fill in section_end for every block: the last block's section runs to
    # end-of-text; earlier blocks end where the next block begins.
    for index, block in enumerate(blocks):
        if index + 1 < len(blocks):
            blocks[index] = replace(block, section_end=blocks[index + 1].start)
        else:
            blocks[index] = replace(block, section_end=len(text))
    return blocks


def _parse_html_heading_blocks(text: str) -> list[HeadingBlock]:
    matches = list(_HTML_HEADING_PATTERN.finditer(text))
    blocks: list[HeadingBlock] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = match.end()
        section_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        raw_title = _HTML_TAG_PATTERN.sub("", match.group("body"))
        blocks.append(
            HeadingBlock(
                source_index=index,
                level=int(match.group("level")),
                title=" ".join(raw_title.split()),
                start=start,
                end=end,
                section_start=start,
                section_end=section_end,
                attributes=match.group("attrs") or "",
            )
        )
    return blocks


def _rewrite_first_heading(
    section: str,
    markup_kind: str,
    level: int,
    title: str,
    original: HeadingBlock,
) -> str:
    normalized_level = min(6, max(1, int(level)))
    normalized_title = title.strip()
    if markup_kind == "markdown":
        return _MD_HEADING_PATTERN.sub(
            f"{'#' * normalized_level} {normalized_title}",
            section,
            count=1,
        )
    if markup_kind == "html":
        replacement = (
            f"<h{normalized_level}{original.attributes}>{normalized_title}</h{normalized_level}>"
        )
        return _HTML_HEADING_PATTERN.sub(replacement, section, count=1)
    return section
