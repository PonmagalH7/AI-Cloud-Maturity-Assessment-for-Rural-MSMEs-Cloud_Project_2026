import re

import pytest

from generate_report import generate_report
from generate_recommendation import generate_recommendation
from scoring import run_full_assessment

XSS = "<script>alert(1)</script>"


def _report(answers, name="Sri Lakshmi General Store", priorities=None, summary=None, assessment_id="test-001"):
    s = run_full_assessment(answers)
    rec = generate_recommendation(
        "Micro", s["categoryScores"], s["overallScore"], s["maturityLevel"], s["gaps"],
        weak_questions=s["questionBreakdown"], llm_call=lambda p: None,
    )
    if priorities:
        rec["priorities"] = priorities
    if summary:
        rec["summary"] = summary
    return generate_report(assessment_id, name, "Micro", s, rec)


def test_report_has_expected_content(answers):
    out = _report(answers)
    html = out["html"]
    assert out["filename"] == "reports/test-001.html"
    assert html.startswith("<!DOCTYPE html>") and html.strip().endswith("</html>")
    for text in ["60.5", "Level 4 - Managed", "Sri Lakshmi General Store", "Infrastructure &amp; Technology",
                 "People &amp; Skills", "test-001", "Where the next points are", "<svg"]:
        assert text in html, text


def test_all_dynamic_fields_are_escaped(answers):
    html = _report(answers, name=XSS, priorities=[XSS, "<b>x</b>", "ok"], summary=XSS)["html"]
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "<b>x</b>" not in html


@pytest.mark.parametrize("bad_id", ["../../etc/passwd", "a b", "x/y", "", "a" * 101, None, "id;drop"])
def test_unsafe_assessment_ids_rejected(answers, bad_id):
    with pytest.raises(ValueError):
        _report(answers, assessment_id=bad_id)


def test_report_without_optional_blocks_still_renders():
    from report_template import render_report_html

    html = render_report_html("B", "Micro", {"infrastructure": 10}, 10, "Level 1 - Initial", [], "s", ["p"], "id1")
    assert "<svg" in html and "Where the next points are" not in html


def test_top_level_report_says_so(uniform):
    html = _report(uniform(4))["html"]
    assert "Top maturity level reached" in html and "None - strong across all categories" in html


def test_no_external_resources(answers):
    html = _report(answers)["html"]
    assert not re.search(r'(src|href)=["\']https?://', html)
