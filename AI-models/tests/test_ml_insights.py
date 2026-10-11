"""Tests for the optional ML Profile Match. Run from AI-models:  py -m pytest tests"""
import os

import pytest

import ml_insights
from generate_report import generate_report
from report_template import _pretty_archetype, render_report_html
from scoring import run_full_assessment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL_MODEL = os.path.join(ROOT, "models", "app_archetype_classifier_best.joblib")

INSIGHT = {
    "archetype": "3_partly_digital",
    "confidence": 71.5,
    "alternatives": [{"archetype": "4_cloud_adopting", "confidence": 20.0}],
}


def _use_model(monkeypatch, path):
    monkeypatch.setattr(ml_insights, "MODEL_CANDIDATES", [path] if path else [])
    monkeypatch.setitem(ml_insights._cache, "loaded", False)
    monkeypatch.setitem(ml_insights._cache, "cats", None)


def _report(answers, ml_insight=None, name="Shop"):
    s = run_full_assessment(answers)
    rec = {"summary": "Fine.", "priorities": ["a", "b", "c"], "source": "fallback"}
    return generate_report("t-1", name, "Micro", s, rec, ml_insight=ml_insight)["html"]


# ---------- no model / bad input: must never break anything ----------

def test_no_model_returns_none(monkeypatch, answers):
    _use_model(monkeypatch, None)
    assert ml_insights.predict_archetype(answers, "Micro") is None


@pytest.mark.parametrize("bad", [None, "text", {}, {"infra_1": 1}])
def test_bad_or_partial_answers_give_none(monkeypatch, bad):
    pytest.importorskip("sklearn")
    if not os.path.exists(REAL_MODEL):
        pytest.skip("trained model not present")
    _use_model(monkeypatch, REAL_MODEL)
    assert ml_insights.predict_archetype(bad, "Micro") is None


def test_out_of_range_answer_gives_none(monkeypatch, answers):
    pytest.importorskip("sklearn")
    if not os.path.exists(REAL_MODEL):
        pytest.skip("trained model not present")
    _use_model(monkeypatch, REAL_MODEL)
    assert ml_insights.predict_archetype({**answers, "infra_1": 9}, "Micro") is None


# ---------- your real trained model ----------

@pytest.fixture
def real_model(monkeypatch):
    pytest.importorskip("sklearn")
    pytest.importorskip("pandas")
    if not os.path.exists(REAL_MODEL):
        pytest.skip("trained model not present")
    _use_model(monkeypatch, REAL_MODEL)


def test_real_model_predicts_for_the_worked_example(real_model, answers):
    result = ml_insights.predict_archetype(answers, "Micro", "Retail", "Tamil")
    assert result["archetype"][0].isdigit()  # labels look like "3_partly_digital"
    assert 0 <= result["confidence"] <= 100
    assert len(result["alternatives"]) == 2


def test_real_model_extremes_are_ordered(real_model, uniform):
    low = ml_insights.predict_archetype(uniform(0), "Micro")["archetype"]
    high = ml_insights.predict_archetype(uniform(4), "Micro")["archetype"]
    assert int(low[0]) < int(high[0])


def test_spelling_is_matched_to_what_the_model_learned(real_model, answers):
    ml_insights.predict_archetype(answers, "micro", "retail", "tamil")
    assert ml_insights._match_category("enterprise_size", "micro") == "Micro"
    assert ml_insights._match_category("language", "tamil") == "Tamil"


def test_prediction_does_not_change_the_score(real_model, answers):
    before = run_full_assessment(answers)
    ml_insights.predict_archetype(answers, "Micro")
    assert run_full_assessment(answers) == before


# ---------- the report ----------

def test_report_without_insight_has_no_section(answers):
    assert "Profile Match" not in _report(answers)


def test_report_with_insight_shows_section_and_keeps_score(answers):
    html = _report(answers, INSIGHT)
    assert "Profile Match" in html and "Experimental" in html
    assert "partly digital" in html and "71.5%" in html
    assert "simulated example businesses" in html
    assert "60.5" in html and "Level 4 - Managed" in html
    assert html.strip().endswith("</html>")


def test_insight_text_is_escaped(answers):
    bad = {"archetype": "<script>x</script>", "confidence": 50, "alternatives": []}
    html = _report(answers, bad)
    assert "<script>x" not in html and "&lt;script&gt;" in html


def test_pretty_archetype():
    assert _pretty_archetype("2_phone_whatsapp") == "phone whatsapp"


def test_render_accepts_missing_insight():
    html = render_report_html("B", "Micro", {"infrastructure": 10}, 10, "Level 1 - Initial", [], "s", ["p"], "id1")
    assert "Profile Match" not in html
