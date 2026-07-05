"""End-to-end: math text through the native docx writer produces a real equation."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

pytest.importorskip("docx")

from quill.io.docx_writer import rich_to_docx_bytes
from quill.io.rtf_model import markdown_to_rich


def test_inline_math_produces_real_omath(tmp_path: Path) -> None:
    rich = markdown_to_rich("Pythagorean theorem: \\(a^2 + b^2 = c^2\\)\n")
    data = rich_to_docx_bytes(rich)
    out = tmp_path / "math.docx"
    out.write_bytes(data)
    with zipfile.ZipFile(out) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    assert "m:oMath" in xml
    assert "Pythagorean theorem:" in xml


def test_display_math_produces_real_omath(tmp_path: Path) -> None:
    rich = markdown_to_rich("$$a^2+b^2=c^2$$\n")
    data = rich_to_docx_bytes(rich)
    out = tmp_path / "math_block.docx"
    out.write_bytes(data)
    with zipfile.ZipFile(out) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    assert "m:oMath" in xml


def test_plain_text_unaffected(tmp_path: Path) -> None:
    rich = markdown_to_rich("Just an ordinary paragraph, $5 and all.\n")
    data = rich_to_docx_bytes(rich)
    out = tmp_path / "plain.docx"
    out.write_bytes(data)
    with zipfile.ZipFile(out) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    assert "m:oMath" not in xml
    assert "$5" in xml
