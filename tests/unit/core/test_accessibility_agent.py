from __future__ import annotations

from quill.core.accessibility_agent import (
    AccessibilityPlan,
    apply_plan,
    build_plan,
    build_plan_report,
    summarize_plan,
)


def _accept_all(plan: AccessibilityPlan) -> set[str]:
    return {step.step_id for step in plan.steps}


def test_build_plan_clean_markdown_has_no_steps() -> None:
    plan = build_plan("clean.md", "# Title\n\nA short, clear sentence.\n", "markdown")

    assert plan.steps == ()
    assert plan.findings_before == 0
    assert "no actionable" in build_plan_report(plan).lower()


def test_build_plan_finds_markdown_heading_spacing_and_is_auto_fixable() -> None:
    plan = build_plan("note.md", "#Heading\n", "markdown")

    heading_steps = [s for s in plan.steps if s.category == "structure"]
    assert len(heading_steps) == 1
    step = heading_steps[0]
    assert step.auto_fixable is True
    assert step.before == "#Heading"
    assert step.after == "# Heading"
    assert step.line == 1


def test_apply_plan_fixes_markdown_heading_spacing() -> None:
    plan = build_plan("note.md", "#Heading\n", "markdown")
    result = apply_plan(plan, "#Heading\n", _accept_all(plan))

    assert result.text == "# Heading\n"
    assert result.changed is True
    assert len(result.applied) == 1
    assert result.findings_after < result.findings_before


def test_apply_plan_respects_per_step_consent() -> None:
    plan = build_plan("note.md", "#Heading\n", "markdown")

    result = apply_plan(plan, "#Heading\n", set())

    assert result.text == "#Heading\n"
    assert result.applied == ()
    assert len(result.skipped) == len(plan.steps)


def test_markdown_image_missing_alt_is_advisory_not_auto() -> None:
    plan = build_plan("img.md", "![](photo.png)\n", "markdown")

    alt_steps = [s for s in plan.steps if s.category == "alt-text"]
    assert len(alt_steps) == 1
    assert alt_steps[0].auto_fixable is False

    # Accepting an advisory step does not change text (needs human judgement).
    result = apply_plan(plan, "![](photo.png)\n", _accept_all(plan))
    assert result.text == "![](photo.png)\n"


def test_markdown_generic_link_text_is_flagged() -> None:
    plan = build_plan(
        "links.md", "See [click here](https://example.com) for details.\n", "markdown"
    )

    link_steps = [s for s in plan.steps if s.category == "link-text"]
    assert len(link_steps) == 1
    assert link_steps[0].auto_fixable is False


def test_plain_language_step_is_auto_fixable_and_preserves_case() -> None:
    plan = build_plan("memo.md", "Utilize the tool in order to begin.\n", "markdown")

    plain_steps = [s for s in plan.steps if s.category == "plain-language"]
    assert len(plain_steps) == 2

    result = apply_plan(plan, "Utilize the tool in order to begin.\n", _accept_all(plan))
    assert result.text == "Use the tool to begin.\n"


def test_html_missing_lang_and_img_alt() -> None:
    text = "<html><body><img src='x.png'></body></html>\n"
    plan = build_plan("page.html", text, "html")

    categories = {s.category for s in plan.steps}
    assert "structure" in categories  # missing lang
    assert "alt-text" in categories  # missing alt

    lang_steps = [s for s in plan.steps if s.category == "structure" and s.auto_fixable]
    assert len(lang_steps) == 1
    result = apply_plan(plan, text, {lang_steps[0].step_id})
    assert '<html lang="en">' in result.text


def test_cleanup_trims_trailing_whitespace() -> None:
    text = "Title   \n\nBody line.   \n"
    plan = build_plan("draft.md", text, "markdown")

    cleanup_steps = [s for s in plan.steps if s.category == "cleanup"]
    assert len(cleanup_steps) == 1

    result = apply_plan(plan, text, {cleanup_steps[0].step_id})
    assert result.text == "Title\n\nBody line.\n"


def test_summarize_plan_speaks_counts() -> None:
    plan = build_plan("note.md", "#Heading\n", "markdown")
    summary = summarize_plan(plan)

    assert "Accessibility plan" in summary
    assert "applied automatically" in summary


def test_summarize_plan_handles_clean_document() -> None:
    plan = build_plan("clean.md", "# Title\n\nClear text.\n", "markdown")
    summary = summarize_plan(plan)

    assert "no actionable issues" in summary.lower()


def test_run_report_reports_resolved_findings() -> None:
    text = "#Heading\n"
    plan = build_plan("note.md", text, "markdown")
    result = apply_plan(plan, text, _accept_all(plan))

    assert "Findings before:" in result.report
    assert "Findings after:" in result.report
    assert "resolved" in result.report.lower()


def test_apply_plan_applies_only_accepted_subset() -> None:
    text = "#One\n\nUtilize this.\n"
    plan = build_plan("multi.md", text, "markdown")
    heading = next(s for s in plan.steps if s.category == "structure")

    result = apply_plan(plan, text, {heading.step_id})

    assert result.text.startswith("# One")
    assert "Utilize" in result.text  # plain-language step was not accepted
    assert len(result.applied) == 1


def test_build_plan_report_lists_steps_with_before_after() -> None:
    plan = build_plan("note.md", "#Heading\n", "markdown")
    report = build_plan_report(plan)

    assert "Proposed steps:" in report
    assert "Before: #Heading" in report
    assert "After: # Heading" in report
