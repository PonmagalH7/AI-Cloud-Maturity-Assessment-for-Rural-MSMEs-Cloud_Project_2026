"""
Pipeline checks over the SYNTHETIC dataset (300 made-up businesses).
These prove the code behaves consistently; they say nothing about real-world accuracy.
"""
import csv
import os
from statistics import mean

import pytest

from generate_recommendation import generate_recommendation
from scoring import ALL_QUESTION_IDS, plan_to_next_level, run_full_assessment


def _answers(row):
    return {q: int(row[q]) for q in ALL_QUESTION_IDS}


@pytest.fixture(scope="module")
def scored(synthetic_rows):
    return [(row, run_full_assessment(_answers(row))) for row in synthetic_rows]


def test_dataset_shape(synthetic_rows):
    assert len(synthetic_rows) == 300
    assert {r["archetype"] for r in synthetic_rows} == {
        "1_paper_only", "2_phone_whatsapp", "3_partly_digital", "4_cloud_adopting", "5_cloud_mature"}
    assert all(0 <= int(r[q]) <= 4 for r in synthetic_rows for q in ALL_QUESTION_IDS)


def test_dataset_is_reproducible():
    from generate_synthetic_dataset import generate

    assert generate(5, seed=1) == generate(5, seed=1)
    assert generate(5, seed=1) != generate(5, seed=2)


def test_committed_csv_matches_generator(synthetic_rows):
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "synthetic_msme_assessments.csv")
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(synthetic_rows)
    assert all(rows[i]["record_id"] == synthetic_rows[i]["record_id"] for i in range(len(rows)))
    assert all(int(rows[i][q]) == synthetic_rows[i][q] for i in (0, 150, 299) for q in ALL_QUESTION_IDS)


def test_every_record_scores_and_stays_in_range(scored):
    for _, r in scored:
        assert 0 <= r["overallScore"] <= 100
        assert 1 <= r["levelNumber"] <= 5
        assert len(r["gaps"]) <= 3


def test_mean_score_rises_with_archetype(scored):
    by = {}
    for row, r in scored:
        by.setdefault(row["archetype"], []).append(r["overallScore"])
    means = [mean(by[k]) for k in sorted(by)]
    assert means == sorted(means) and means[-1] - means[0] > 50


def test_archetype_level_bands(scored):
    """Most businesses of each profile should land in the expected level band."""
    expected = {"1_paper_only": {1, 2}, "2_phone_whatsapp": {2, 3}, "3_partly_digital": {3, 4},
                "4_cloud_adopting": {4, 5}, "5_cloud_mature": {4, 5}}
    for arch, levels in expected.items():
        group = [r["levelNumber"] for row, r in scored if row["archetype"] == arch]
        assert sum(l in levels for l in group) / len(group) >= 0.85, arch


def test_every_record_gets_three_distinct_recommendations(scored):
    for row, r in scored:
        rec = generate_recommendation(
            row["enterprise_size"], r["categoryScores"], r["overallScore"], r["maturityLevel"], r["gaps"],
            weak_questions=r["questionBreakdown"], llm_call=lambda p: (_ for _ in ()).throw(RuntimeError("offline")),
        )
        assert rec["source"] == "fallback" and len(set(rec["priorities"])) == 3


def test_plan_reaches_next_level_for_every_non_top_record(scored):
    for row, r in scored:
        if r["nextLevel"] is None:
            assert r["planToNextLevel"] is None
            continue
        plan = plan_to_next_level(_answers(row))
        assert plan["resultingScore"] > r["nextLevel"]["scoreToExceed"]
