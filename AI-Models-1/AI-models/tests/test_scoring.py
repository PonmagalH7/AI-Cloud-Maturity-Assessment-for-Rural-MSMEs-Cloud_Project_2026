import pytest

from scoring import (
    ALL_QUESTION_IDS,
    AssessmentValidationError,
    get_maturity_level,
    identify_gaps,
    plan_to_next_level,
    run_full_assessment,
    what_if,
)


def test_worked_example(answers):
    r = run_full_assessment(answers)
    assert r["categoryScores"] == {
        "infrastructure": 60.0, "process": 70.0, "people": 50.0, "data": 65.0, "security": 55.0,
    }
    assert r["overallScore"] == 60.5
    assert r["maturityLevel"] == "Level 4 - Managed"
    assert r["levelNumber"] == 4


def test_gaps_for_worked_example(answers):
    # people (50) and security (55) are below 60; security is ranked first because
    # weight x shortfall is larger (0.20 x 45 = 9.0 vs 0.15 x 50 = 7.5).
    assert run_full_assessment(answers)["gaps"] == ["security", "people"]


@pytest.mark.parametrize(
    "score,label",
    [
        (0, "Level 1 - Initial"), (20, "Level 1 - Initial"), (20.01, "Level 2 - Developing"),
        (39.99, "Level 2 - Developing"), (40, "Level 2 - Developing"), (40.01, "Level 3 - Defined"), (60, "Level 3 - Defined"), (60.01, "Level 4 - Managed"),
        (80, "Level 4 - Managed"), (80.01, "Level 5 - Optimized"), (100, "Level 5 - Optimized"),
    ],
)
def test_level_boundaries(score, label):
    assert get_maturity_level(score) == label


def test_all_zero_and_all_four(uniform):
    low, high = run_full_assessment(uniform(0)), run_full_assessment(uniform(4))
    assert low["overallScore"] == 0 and low["levelNumber"] == 1
    assert high["overallScore"] == 100 and high["levelNumber"] == 5
    assert high["gaps"] == [] and high["quickWins"] == [] and high["nextLevel"] is None
    assert high["planToNextLevel"] is None


def test_gaps_capped_at_three(uniform):
    assert len(run_full_assessment(uniform(0))["gaps"]) == 3


# ---------------- validation ----------------
def test_missing_answers_rejected(answers):
    del answers["data_2"]
    with pytest.raises(AssessmentValidationError, match="missing answers: data_2"):
        run_full_assessment(answers)


@pytest.mark.parametrize("bad", [9, -1, 2.5, "3", None, True])
def test_bad_values_rejected(answers, bad):
    answers["infra_1"] = bad
    with pytest.raises(AssessmentValidationError, match="infra_1"):
        run_full_assessment(answers)


def test_unknown_question_rejected(answers):
    answers["infra_9"] = 1
    with pytest.raises(AssessmentValidationError, match="unknown question ids: infra_9"):
        run_full_assessment(answers)


def test_all_problems_reported_at_once(answers):
    del answers["people_1"]
    answers["infra_1"] = 7
    with pytest.raises(AssessmentValidationError) as exc:
        run_full_assessment(answers)
    assert "people_1" in str(exc.value) and "infra_1" in str(exc.value)


def test_whole_floats_accepted(answers):
    answers["infra_1"] = 3.0  # JSON often delivers 3.0
    assert run_full_assessment(answers)["overallScore"] == 60.5


def test_non_dict_rejected():
    with pytest.raises(AssessmentValidationError):
        run_full_assessment([1, 2, 3])


# ---------------- explanation ----------------
def test_breakdown_points_lost_sum_to_missing_score(answers):
    r = run_full_assessment(answers)
    lost = sum(q["pointsLost"] for q in r["questionBreakdown"])
    assert lost == pytest.approx(100 - r["overallScore"], abs=0.1)
    assert len(r["questionBreakdown"]) == 25


def test_quick_wins_sorted_and_limited(answers):
    wins = run_full_assessment(answers)["quickWins"]
    assert len(wins) == 5
    assert [w["pointsLost"] for w in wins] == sorted((w["pointsLost"] for w in wins), reverse=True)


def test_next_level_info(answers):
    nxt = run_full_assessment(answers)["nextLevel"]
    assert nxt["level"] == "Level 5 - Optimized" and nxt["scoreToExceed"] == 80
    assert nxt["pointsToExceed"] == 19.5


# ---------------- what-if and plan ----------------
def test_what_if_improves_score(answers):
    out = what_if(answers, {"data_5": 4, "people_1": 4})
    assert out["scoreDelta"] > 0
    assert out["after"]["overallScore"] == pytest.approx(out["before"]["overallScore"] + out["scoreDelta"])


def test_what_if_can_change_level(uniform):
    base = uniform(2)  # 50 -> Level 3
    out = what_if(base, {q: 4 for q in ALL_QUESTION_IDS if q.startswith(("infra", "process"))})
    assert out["levelChanged"] is True


def test_what_if_validates(answers):
    with pytest.raises(AssessmentValidationError):
        what_if(answers, {"nope": 1})
    with pytest.raises(AssessmentValidationError):
        what_if(answers, {"infra_1": 8})
    with pytest.raises(AssessmentValidationError):
        what_if(answers, {})


@pytest.mark.parametrize("value", [0, 1, 2, 3])
def test_plan_actually_reaches_next_level(uniform, value):
    base = uniform(value)
    before = run_full_assessment(base)
    plan = plan_to_next_level(base)
    assert plan["resultingScore"] > before["nextLevel"]["scoreToExceed"]
    assert plan["steps"][-1]["scoreAfter"] == plan["resultingScore"]
    # every step is exactly +1 on one question
    assert all(s["to"] == s["from"] + 1 for s in plan["steps"])


def test_plan_does_not_mutate_input(answers):
    snapshot = dict(answers)
    plan_to_next_level(answers)
    run_full_assessment(answers)
    assert answers == snapshot


def test_monotonic_raising_any_answer_never_lowers_score(answers):
    base = run_full_assessment(answers)["overallScore"]
    for qid in ALL_QUESTION_IDS:
        if answers[qid] < 4:
            bumped = {**answers, qid: answers[qid] + 1}
            assert run_full_assessment(bumped)["overallScore"] > base
