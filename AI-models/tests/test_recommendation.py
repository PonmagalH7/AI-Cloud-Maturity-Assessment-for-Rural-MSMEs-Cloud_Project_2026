import pytest

from bedrock_client import extract_json
from fallback_recommendations import QUESTION_TIPS, get_fallback_recommendation
from generate_recommendation import generate_recommendation, validate_llm_result
from recommendation_prompt import build_prompt
from scoring import ALL_QUESTION_IDS, run_full_assessment

GOOD = {
    "summary": "Your business scored 60.5 out of 100 and is at Level 4. People and security need the most work.",
    "priorities": ["Turn on two-step login for email.", "Train one person on your cloud tools.", "Back up files weekly."],
}


def _scored(answers):
    return run_full_assessment(answers)


def _call(scored, llm, business_type="Micro", **kw):
    return generate_recommendation(
        business_type, scored["categoryScores"], scored["overallScore"], scored["maturityLevel"],
        scored["gaps"], weak_questions=scored["questionBreakdown"], llm_call=llm, **kw,
    )


def test_every_question_has_a_free_and_upgrade_tip():
    assert set(QUESTION_TIPS) == set(ALL_QUESTION_IDS)
    assert all(t["free"] and t["upgrade"] and t["free"] != t["upgrade"] for t in QUESTION_TIPS.values())


def test_good_llm_reply_is_used(answers):
    r = _call(_scored(answers), lambda prompt: GOOD)
    assert r["source"] == "bedrock" and r["priorities"] == GOOD["priorities"]


@pytest.mark.parametrize(
    "bad",
    [
        {"summary": "ok"},                                                      # no priorities
        {"summary": "ok", "priorities": ["a", "b"]},                            # only 2
        {"summary": "ok", "priorities": ["a", "b", "c", "d"]},                  # 4
        {"summary": "ok", "priorities": ["a", "", "c"]},                        # empty step
        {"summary": "", "priorities": ["a", "b", "c"]},                         # empty summary
        {"summary": "You scored 87 out of 100.", "priorities": ["a", "b", "c"]},  # invented number
        {"summary": "ok", "priorities": ["Spend 9999 rupees", "b", "c"]},         # invented number in a step
        "just text", None, ["list"],
    ],
)
def test_bad_llm_replies_fall_back(answers, bad):
    r = _call(_scored(answers), lambda prompt: bad)
    assert r["source"] == "fallback" and len(r["priorities"]) == 3 and r["fallback_reason"]


def test_llm_exception_falls_back(answers):
    def boom(prompt):
        raise TimeoutError("read timeout")

    r = _call(_scored(answers), boom)
    assert r["source"] == "fallback" and "TimeoutError" in r["fallback_reason"]


def test_rounded_scores_are_allowed(answers):
    ok = {**GOOD, "summary": "Your business scored 61 out of 100, which is Level 4."}
    assert _call(_scored(answers), lambda p: ok)["source"] == "bedrock"


def test_unsupported_language_falls_back(answers):
    r = _call(_scored(answers), lambda p: GOOD, language="Klingon")
    assert r["source"] == "fallback"


def test_prompt_contains_weak_questions_and_language(answers):
    s = _scored(answers)
    prompt = build_prompt("Micro", s["categoryScores"], s["overallScore"], s["maturityLevel"],
                          s["gaps"], weak_questions=s["questionBreakdown"], language="Tamil")
    assert "answered" in prompt and "Tamil" in prompt and "Do not invent or change any numbers" in prompt


def test_prompt_rejects_unknown_language(answers):
    s = _scored(answers)
    with pytest.raises(ValueError):
        build_prompt("Micro", s["categoryScores"], 1, "x", [], language="Elvish")


def test_extract_json_handles_fences_and_chatter():
    assert extract_json('Sure!\n```json\n{"a": 1}\n```\nHope that helps') == {"a": 1}
    with pytest.raises(ValueError):
        extract_json("no json here")


# ---------------- fallback behaviour ----------------
def test_fallback_is_personalised_to_answers(uniform):
    weak_data = {**uniform(4), "data_2": 0}          # only backups are missing
    weak_sec = {**uniform(4), "security_1": 0}       # only passwords are missing
    tip_d = _call(_scored(weak_data), lambda p: None)["priorities"][0]
    tip_s = _call(_scored(weak_sec), lambda p: None)["priorities"][0]
    assert tip_d == QUESTION_TIPS["data_2"]["free"]
    assert tip_s == QUESTION_TIPS["security_1"]["free"]


def test_micro_never_gets_paid_tips(uniform):
    answers = {**uniform(3)}
    tips = _call(_scored(answers), lambda p: None, business_type="Micro")["priorities"]
    assert not any(t in {v["upgrade"] for v in QUESTION_TIPS.values()} for t in tips)


def test_small_gets_upgrade_tips_for_answers_of_two_or_more(uniform):
    tips = _call(_scored(uniform(3)), lambda p: None, business_type="Small")["priorities"]
    assert any(t in {v["upgrade"] for v in QUESTION_TIPS.values()} for t in tips)


def test_fallback_always_three_distinct_tips(uniform):
    for value in range(5):
        for size in ("Micro", "Small", "Medium"):
            tips = _call(_scored(uniform(value)), lambda p: None, business_type=size)["priorities"]
            assert len(tips) == 3 and len(set(tips)) == 3


def test_legacy_category_only_fallback_still_works():
    r = get_fallback_recommendation(60.5, "Level 4 - Managed", ["people", "security"], "Micro")
    assert len(r["priorities"]) == 3 and "People & Skills" in r["summary"]
