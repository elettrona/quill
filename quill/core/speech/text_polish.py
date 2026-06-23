"""Text extraction and TTS polishing for batch speech export.

Extracts human-readable text from Markdown, HTML, and Word (.docx) files,
then applies a polish pipeline to improve TTS output quality.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser
from pathlib import Path

__all__ = [
    "extract_text",
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


def _extract_markdown(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
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


def extract_text(path: Path) -> str:
    """Return raw text from a Markdown, HTML, or Word file."""
    suffix = path.suffix.lower()
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
