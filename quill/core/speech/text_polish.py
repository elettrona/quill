"""Text extraction and TTS polishing for batch speech export.

Extracts human-readable text from Markdown, HTML, and Word (.docx) files,
then applies a polish pipeline to improve TTS output quality.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

__all__ = [
    "extract_text",
    "extract_sections",
    "DocumentSection",
    "polish_for_tts",
    "UnsupportedFormatError",
]

_WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# Abbreviations that trip up TTS (period causes a pause mid-word).
_ABBREV_MAP: dict[str, str] = {
    r"\bDr\.": "Doctor",
    r"\bMr\.": "Mister",
    r"\bMrs\.": "Missus",
    r"\bMs\.": "Miss",
    r"\bProf\.": "Professor",
    r"\bSr\.": "Senior",
    r"\bJr\.": "Junior",
    r"\betc\.": "et cetera",
    r"\bvs\.": "versus",
    r"\be\.g\.": "for example",
    r"\bi\.e\.": "that is",
    r"\ba\.k\.a\.": "also known as",
    r"\bapprox\.": "approximately",
    r"\bmax\.": "maximum",
    r"\bmin\.": "minimum",
    r"\bno\.": "number",
    r"\bvol\.": "volume",
    r"\bfig\.": "figure",
}

# URL pattern — replace with "link" to avoid TTS spelling out h-t-t-p-s.
_URL_RE = re.compile(
    r"https?://\S+|www\.\S+",
    re.IGNORECASE,
)

# Markdown code fence (```...```) — skip the content entirely.
_CODE_FENCE_RE = re.compile(r"```[^\n]*\n.*?```", re.DOTALL)
# Inline code — strip backticks but keep text.
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
# ATX headings — keep the text, drop the # markers.
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
# Bold / italic — keep text.
_BOLD_ITALIC_RE = re.compile(r"\*{1,3}(.+?)\*{1,3}|_{1,3}(.+?)_{1,3}")
# Markdown links — keep the label, drop URL.
_MD_LINK_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)|\[([^\]]*)\]\([^)]*\)")
# Horizontal rules and setext headings underlines.
_HR_RE = re.compile(r"^[-=*]{3,}\s*$", re.MULTILINE)
# HTML within Markdown.
_HTML_TAG_RE = re.compile(r"<[^>]+>")
# Excess blank lines.
_MULTI_BLANK_RE = re.compile(r"\n{3,}")


class UnsupportedFormatError(ValueError):
    """Raised when a file extension has no extractor."""


class _TextCollector(HTMLParser):
    """Minimal HTMLParser subclass that collects visible text."""

    _SKIP_TAGS = frozenset({"script", "style", "head", "noscript", "template", "svg", "math"})

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag.lower() in self._SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        if tag.lower() in {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "br", "tr"}:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self._parts.append(data)

    def result(self) -> str:
        return "".join(self._parts)


def _clean_markdown(raw: str) -> str:
    # Remove fenced code blocks first (before heading expansion).
    text = _CODE_FENCE_RE.sub("\n", raw)
    # Expand headings to plain text.
    text = _HEADING_RE.sub(r"\1", text)
    # Inline code — keep text only.
    text = _INLINE_CODE_RE.sub(r"\1", text)
    # Images — keep alt text or drop.
    text = _MD_LINK_RE.sub(lambda m: m.group(1) or m.group(2) or "", text)
    # Bold / italic — keep text.
    text = _BOLD_ITALIC_RE.sub(lambda m: m.group(1) or m.group(2) or "", text)
    # Remaining HTML tags.
    text = _HTML_TAG_RE.sub("", text)
    # Horizontal rules.
    text = _HR_RE.sub("", text)
    return text


def _extract_markdown(path: Path) -> str:
    return _clean_markdown(path.read_text(encoding="utf-8", errors="replace"))


def _extract_html(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    parser = _TextCollector()
    parser.feed(raw)
    return parser.result()


def _extract_docx(path: Path) -> str:
    """Extract paragraph text from a Word .docx file using stdlib only."""
    parts: list[str] = []
    try:
        with zipfile.ZipFile(path, "r") as zf:
            if "word/document.xml" not in zf.namelist():
                return ""
            with zf.open("word/document.xml") as fh:
                tree = ET.parse(fh)
    except (zipfile.BadZipFile, ET.ParseError):
        return ""

    root = tree.getroot()
    for para in root.iter(f"{{{_WORD_NS}}}p"):
        texts = [node.text for node in para.iter(f"{{{_WORD_NS}}}t") if node.text]
        line = "".join(texts).strip()
        if line:
            parts.append(line)
    return "\n".join(parts)


def _extract_txt(path: Path) -> str:
    """Plain text is returned as-is (decoded permissively). Has no headings."""
    return path.read_text(encoding="utf-8", errors="replace")


# --- Heading-aware section extraction (§4.8.2) ---------------------------- #


@dataclass(slots=True)
class DocumentSection:
    """One heading-delimited part of a document: the heading and its body text.

    ``title`` is the heading text, or ``""`` for the lead-in before the first
    heading (the caller substitutes the configured intro title) and for formats
    or documents that have no headings (a single whole-document section).
    """

    title: str
    text: str


# ATX (``## Heading``) and the heading line as a whole, captured separately.
_ATX_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*#*[ \t]*$", re.MULTILINE)
# Setext heading: a non-blank text line immediately followed by === or --- .
_SETEXT_HEADING_RE = re.compile(r"^(?P<title>[^\n]+)\n(?P<rule>=+|-+)[ \t]*$", re.MULTILINE)


def _sections_from_markdown(raw: str) -> list[DocumentSection]:
    # Normalise setext headings to ATX so a single splitter handles both.
    def _setext_to_atx(m: re.Match[str]) -> str:
        level = "#" if m.group("rule").startswith("=") else "##"
        return f"{level} {m.group('title').strip()}"

    normalised = _SETEXT_HEADING_RE.sub(_setext_to_atx, raw)
    matches = list(_ATX_HEADING_RE.finditer(normalised))
    if not matches:
        return [DocumentSection("", _clean_markdown(normalised))]

    sections: list[DocumentSection] = []
    lead_in = normalised[: matches[0].start()]
    if lead_in.strip():
        sections.append(DocumentSection("", _clean_markdown(lead_in)))
    for i, m in enumerate(matches):
        title = m.group(2).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(normalised)
        body = _clean_markdown(normalised[body_start:body_end])
        sections.append(DocumentSection(title, body))
    return sections


class _HtmlSectionizer(HTMLParser):
    """Collects visible text, splitting into sections at h1–h6 boundaries."""

    _SKIP_TAGS = _TextCollector._SKIP_TAGS
    _HEADINGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
    _BREAKS = frozenset({"p", "div", "li", "br", "tr"})

    def __init__(self) -> None:
        super().__init__()
        self._sections: list[DocumentSection] = []
        self._cur_title = ""
        self._cur_parts: list[str] = []
        self._skip_depth = 0
        self._in_heading = False
        self._heading_parts: list[str] = []

    def _flush(self) -> None:
        text = "".join(self._cur_parts).strip()
        if self._cur_title or text:
            self._sections.append(DocumentSection(self._cur_title, text))
        self._cur_parts = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        t = tag.lower()
        if t in self._SKIP_TAGS:
            self._skip_depth += 1
        elif t in self._HEADINGS:
            self._flush()  # close the previous section
            self._cur_title = ""
            self._in_heading = True
            self._heading_parts = []

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in self._SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        elif t in self._HEADINGS and self._in_heading:
            self._cur_title = "".join(self._heading_parts).strip()
            self._in_heading = False
        elif t in self._BREAKS:
            self._cur_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._in_heading:
            self._heading_parts.append(data)
        else:
            self._cur_parts.append(data)

    def result(self) -> list[DocumentSection]:
        self._flush()
        return self._sections


def _sections_from_html(raw: str) -> list[DocumentSection]:
    parser = _HtmlSectionizer()
    parser.feed(raw)
    sections = parser.result()
    if not sections:
        return [DocumentSection("", "")]
    # No headings at all → one whole-document section.
    if all(not s.title for s in sections):
        joined = "\n".join(s.text for s in sections if s.text).strip()
        return [DocumentSection("", joined)]
    return sections


# Word heading paragraphs carry a pStyle whose val is "Heading1".."Heading9",
# "Title", or a localized equivalent; outline level (w:outlineLvl) is the robust
# fallback. We treat any of these as a section boundary.
_WORD_HEADING_STYLE_RE = re.compile(r"^(heading[1-9]|title)$", re.IGNORECASE)


def _docx_paragraph_is_heading(para: ET.Element) -> bool:
    ppr = para.find(f"{{{_WORD_NS}}}pPr")
    if ppr is None:
        return False
    style = ppr.find(f"{{{_WORD_NS}}}pStyle")
    if style is not None:
        val = style.get(f"{{{_WORD_NS}}}val", "")
        if _WORD_HEADING_STYLE_RE.match(val.replace(" ", "")):
            return True
    outline = ppr.find(f"{{{_WORD_NS}}}outlineLvl")
    if outline is not None:
        level = outline.get(f"{{{_WORD_NS}}}val")
        if level is not None and level.isdigit():
            return True
    return False


def _docx_paragraph_text(para: ET.Element) -> str:
    return "".join(node.text for node in para.iter(f"{{{_WORD_NS}}}t") if node.text).strip()


def _sections_from_docx(path: Path) -> list[DocumentSection]:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            if "word/document.xml" not in zf.namelist():
                return [DocumentSection("", "")]
            with zf.open("word/document.xml") as fh:
                tree = ET.parse(fh)
    except (zipfile.BadZipFile, ET.ParseError):
        return [DocumentSection("", "")]

    root = tree.getroot()
    sections: list[DocumentSection] = []
    cur_title = ""
    cur_lines: list[str] = []
    started = False

    def flush() -> None:
        text = "\n".join(cur_lines).strip()
        if cur_title or text:
            sections.append(DocumentSection(cur_title, text))

    for para in root.iter(f"{{{_WORD_NS}}}p"):
        if _docx_paragraph_is_heading(para):
            flush()
            cur_title = _docx_paragraph_text(para)
            cur_lines = []
            started = True
        else:
            line = _docx_paragraph_text(para)
            if line:
                cur_lines.append(line)
    flush()

    if not sections:
        return [DocumentSection("", "")]
    if not started:  # no heading paragraphs at all
        return [DocumentSection("", "\n".join(s.text for s in sections if s.text).strip())]
    return sections


def extract_sections(path: Path) -> list[DocumentSection]:
    """Split a document into heading-delimited sections (§4.8.2).

    Markdown, HTML, and Word headings become section boundaries; the heading text
    becomes the section title. Plain text (and any document without headings)
    returns a single section with an empty title. Each section's ``text`` is the
    same cleaned plain text :func:`extract_text` produces, scoped to that section.
    """
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return [DocumentSection("", _extract_txt(path))]
    if suffix == ".md":
        return _sections_from_markdown(path.read_text(encoding="utf-8", errors="replace"))
    if suffix in {".html", ".htm"}:
        return _sections_from_html(path.read_text(encoding="utf-8", errors="replace"))
    if suffix == ".docx":
        return _sections_from_docx(path)
    raise UnsupportedFormatError(f"No extractor for {suffix!r}")


def extract_text(path: Path) -> str:
    """Return raw text from a plain-text, Markdown, HTML, or Word file."""
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return _extract_txt(path)
    if suffix == ".md":
        return _extract_markdown(path)
    if suffix in {".html", ".htm"}:
        return _extract_html(path)
    if suffix == ".docx":
        return _extract_docx(path)
    raise UnsupportedFormatError(f"No extractor for {suffix!r}")


def polish_for_tts(text: str) -> str:
    """Apply TTS-quality improvements to extracted text."""
    # Replace URLs before any other substitution.
    text = _URL_RE.sub("link", text)
    # Expand abbreviations.
    for pattern, replacement in _ABBREV_MAP.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    # Collapse excess whitespace within lines.
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    text = "\n".join(lines)
    # Collapse 3+ blank lines to 2 (paragraph pause).
    text = _MULTI_BLANK_RE.sub("\n\n", text)
    return text.strip()
