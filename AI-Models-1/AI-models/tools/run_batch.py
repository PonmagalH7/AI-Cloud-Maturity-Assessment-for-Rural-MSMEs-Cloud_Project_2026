"""
Runs the whole pipeline over a CSV of assessments (offline: rules-based
fallback only, unless --bedrock is passed) and prints a summary.

Usage:  python tools/run_batch.py [data/synthetic_msme_assessments.csv] [--bedrock]
"""
import csv
import logging
import os
import sys
from collections import Counter, defaultdict
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from generate_recommendation import generate_recommendation  # noqa: E402
from scoring import ALL_QUESTION_IDS, AssessmentValidationError, run_full_assessment  # noqa: E402


logging.getLogger("generate_recommendation").setLevel(logging.ERROR)  # offline run: expected fallbacks


def _no_llm(prompt):
    raise RuntimeError("offline run: Bedrock not used")


def run(path, use_bedrock=False):
    results, errors = [], []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                answers = {q: int(row[q]) for q in ALL_QUESTION_IDS}
                scored = run_full_assessment(answers)
            except (AssessmentValidationError, ValueError, KeyError) as exc:
                errors.append((row.get("record_id"), str(exc)))
                continue
            rec = generate_recommendation(
                row.get("enterprise_size", "Micro"), scored["categoryScores"], scored["overallScore"],
                scored["maturityLevel"], scored["gaps"],
                weak_questions=scored["questionBreakdown"], language=row.get("language", "English"),
                llm_call=None if use_bedrock else _no_llm,
            )
            results.append({"row": row, "scored": scored, "rec": rec})
    return results, errors


def summarise(results, errors):
    print(f"Records scored: {len(results)}   rejected: {len(errors)}")
    for rid, msg in errors[:5]:
        print(f"  rejected {rid}: {msg[:100]}")

    by_arch = defaultdict(list)
    for r in results:
        by_arch[r["row"].get("archetype", "unlabelled")].append(r)

    print("\nMean overall score and level mix by archetype")
    for arch in sorted(by_arch):
        rs = by_arch[arch]
        levels = Counter(r["scored"]["levelNumber"] for r in rs)
        mix = ", ".join(f"L{k}:{v}" for k, v in sorted(levels.items()))
        print(f"  {arch:<20} mean {mean(r['scored']['overallScore'] for r in rs):5.1f}   {mix}")

    gap_counts = Counter(g for r in results for g in r["scored"]["gaps"])
    print("\nHow often each category is flagged as a gap:", dict(gap_counts.most_common()))

    sources = Counter(r["rec"]["source"] for r in results)
    unique_tips = {p for r in results for p in r["rec"]["priorities"]}
    print(f"Recommendation source: {dict(sources)}   distinct tips used: {len(unique_tips)}")
    steps = [len(r["scored"]["planToNextLevel"]["steps"]) for r in results if r["scored"]["planToNextLevel"]]
    if steps:
        print(f"Steps to reach next level: mean {mean(steps):.1f}, min {min(steps)}, max {max(steps)}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    csv_path = args[0] if args else os.path.join(os.path.dirname(HERE), "data", "synthetic_msme_assessments.csv")
    res, errs = run(csv_path, use_bedrock="--bedrock" in sys.argv)
    summarise(res, errs)
