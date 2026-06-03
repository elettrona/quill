"""GLOW-1 shared-core engine seam: adapter, backend, and fallback paths."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import quill.core.glow as glow
from quill.core.glow import (
    GlowFileAuditResult,
    _glow_finding_to_quill,
    _map_severity,
    _parse_location,
    audit_file,
    build_file_audit_report,
    fix_file,
)

# --- Fakes mirroring the duck-typed shared-core shapes -----------------------


@dataclass(frozen=True)
class _FakeFinding:
    rule_id: str
    severity: str
    message: str
    description: str = ""
    location: str = ""
    auto_fixable: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class _FakeAuditResult:
    file_path: Path
    score: int
    grade: str
    findings: tuple[_FakeFinding, ...]


@dataclass(frozen=True)
class _FakeFixResult:
    output_path: Path
    total_fixes: int
    audit_result: _FakeAuditResult
    warnings: tuple[str, ...] = ()


class _FakeServices:
    def __init__(self, audit: _FakeAuditResult, fix: _FakeFixResult | None = None) -> None:
        self._audit = audit
        self._fix = fix
        self.audit_calls: list[str] = []
        self.fix_calls: list[tuple[str, str | None]] = []

    def audit_by_extension(self, file_path: Any, **kwargs: Any) -> _FakeAuditResult:
        self.audit_calls.append(str(file_path))
        return self._audit

    def fix_by_extension(
        self, file_path: Any, output_path: Any = None, **kwargs: Any
    ) -> _FakeFixResult:
        self.fix_calls.append((str(file_path), None if output_path is None else str(output_path)))
        assert self._fix is not None
        return self._fix


# --- Adapter: severity mapping ----------------------------------------------


def test_map_severity_collapses_to_three_levels() -> None:
    assert _map_severity("critical") == "error"
    assert _map_severity("HIGH") == "error"
    assert _map_severity("medium") == "warning"
    assert _map_severity("warn") == "warning"
    assert _map_severity("low") == "info"
    assert _map_severity("informational") == "info"
    # Unknown severities default to the safe middle level.
    assert _map_severity("nonsense") == "warning"


# --- Adapter: location parsing ----------------------------------------------


def test_parse_location_handles_line_and_column_forms() -> None:
    assert _parse_location("doc.md:12:5") == (12, 5)
    assert _parse_location("doc.md:12") == (12, None)
    assert _parse_location("line 7, column 3") == (7, 3)
    assert _parse_location("slide 4 title") == (None, None)
    assert _parse_location("") == (None, None)


# --- Adapter: Finding -> GlowFinding ----------------------------------------


def test_glow_finding_to_quill_maps_fields_and_metadata() -> None:
    finding = _FakeFinding(
        rule_id="ACB-IMG-ALT",
        severity="critical",
        message="Image missing alt text.",
        description="Add concise alternative text.",
        location="report.docx:3:1",
        auto_fixable=True,
        metadata={"page": 3, "checker": "acb"},
    )

    adapted = _glow_finding_to_quill(finding)

    assert adapted.rule_id == "ACB-IMG-ALT"
    assert adapted.severity == "error"
    assert adapted.message == "Image missing alt text."
    assert adapted.fixable is True
    assert adapted.line == 3
    assert adapted.column == 1
    assert "Add concise alternative text." in adapted.suggestion
    assert "checker: acb" in adapted.suggestion
    assert "page: 3" in adapted.suggestion


def test_glow_finding_to_quill_defaults_when_fields_absent() -> None:
    class _Bare:
        rule_id = "X"
        severity = "low"
        message = "m"

    adapted = _glow_finding_to_quill(_Bare())

    assert adapted.severity == "info"
    assert adapted.line is None
    assert adapted.column is None
    assert "Review this finding" in adapted.suggestion


# --- Backend present path ----------------------------------------------------


def test_audit_file_uses_backend_and_adapts_findings(monkeypatch) -> None:
    audit = _FakeAuditResult(
        file_path=Path("report.docx"),
        score=72,
        grade="C",
        findings=(
            _FakeFinding(rule_id="ACB-1", severity="high", message="bad", auto_fixable=True),
            _FakeFinding(rule_id="ACB-2", severity="low", message="minor"),
        ),
    )
    services = _FakeServices(audit)
    monkeypatch.setattr(glow, "get_glow_services", lambda: services)
    monkeypatch.setattr(glow, "_load_glow_core", lambda: None)

    result = audit_file("report.docx")

    assert isinstance(result, GlowFileAuditResult)
    assert services.audit_calls == ["report.docx"]
    assert result.score == 72
    assert result.grade == "C"
    assert [f.severity for f in result.findings] == ["error", "info"]
    assert result.findings[0].fixable is True


def test_fix_file_uses_backend_and_carries_warnings(monkeypatch) -> None:
    audit = _FakeAuditResult(
        file_path=Path("deck.pptx"),
        score=88,
        grade="B",
        findings=(_FakeFinding(rule_id="ACB-3", severity="medium", message="warn"),),
    )
    fix = _FakeFixResult(
        output_path=Path("deck.fixed.pptx"),
        total_fixes=4,
        audit_result=audit,
        warnings=("one unsupported slide",),
    )
    services = _FakeServices(audit, fix)
    monkeypatch.setattr(glow, "get_glow_services", lambda: services)
    monkeypatch.setattr(glow, "_load_glow_core", lambda: None)

    result = fix_file("deck.pptx", "deck.fixed.pptx")

    assert services.fix_calls == [("deck.pptx", "deck.fixed.pptx")]
    assert result.output_path == "deck.fixed.pptx"
    assert result.total_fixes == 4
    assert result.warnings == ("one unsupported slide",)
    assert result.audit.score == 88
    assert result.audit.findings[0].severity == "warning"


# --- Backend absent (fallback) path -----------------------------------------


def test_audit_file_falls_back_when_backend_absent(monkeypatch) -> None:
    monkeypatch.setattr(glow, "_load_glow_core", lambda: None)

    result = audit_file("report.docx")

    assert result.backend == "unavailable"
    assert result.score == 0
    assert result.grade == "F"
    assert len(result.findings) == 1
    assert result.findings[0].rule_id == "GLOW-CORE-UNAVAILABLE"


def test_fix_file_falls_back_when_backend_absent(monkeypatch) -> None:
    monkeypatch.setattr(glow, "_load_glow_core", lambda: None)

    result = fix_file("report.docx")

    assert result.backend == "unavailable"
    assert result.total_fixes == 0
    assert result.warnings
    assert "not installed" in result.warnings[0].lower()


def test_glow_backend_available_reflects_loader(monkeypatch) -> None:
    monkeypatch.setattr(glow, "_load_glow_core", lambda: None)
    assert glow.glow_backend_available() is False
    monkeypatch.setattr(glow, "_load_glow_core", lambda: object())
    assert glow.glow_backend_available() is True


# --- Report rendering --------------------------------------------------------


def test_build_file_audit_report_includes_engine_and_score() -> None:
    result = GlowFileAuditResult(
        path="report.docx",
        score=72,
        grade="C",
        findings=(
            glow.GlowFinding(
                rule_id="ACB-1",
                severity="error",
                message="bad",
                suggestion="fix it",
                line=3,
                column=1,
                fixable=True,
            ),
        ),
        backend="glow",
    )

    report = build_file_audit_report(result)

    assert "Engine: glow" in report
    assert "Score: 72 (grade C)" in report
    assert "Automatically fixable: 1" in report
    assert "[ERROR] ACB-1 (line 3, column 1) [auto-fix]" in report


def test_build_file_audit_report_handles_no_findings() -> None:
    result = GlowFileAuditResult(
        path="clean.docx", score=100, grade="A", findings=(), backend="glow"
    )

    report = build_file_audit_report(result)

    assert "No GLOW findings detected" in report
