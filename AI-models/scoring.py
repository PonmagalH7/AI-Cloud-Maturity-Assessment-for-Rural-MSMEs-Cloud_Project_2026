"""
Cloud maturity scoring engine (deterministic, no ML).

Public entry point: run_full_assessment(responses)

Everything the report and the AI layer say is derived from the numbers
produced here, so this module is the single source of truth.
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "categories.json"), encoding="utf-8") as f:
    CATEGORIES = json.load(f)

with open(os.path.join(BASE_DIR, "questions.json"), encoding="utf-8") as f:
    QUESTIONS = json.load(f)

MIN_ANSWER_VALUE = 0
MAX_ANSWER_VALUE = 4  # scale is 0-4

CATEGORY_LABELS = {
    "infrastructure": "Infrastructure & Technology",
    "process": "Processes & Digital Operations",
    "people": "People & Skills",
    "data": "Data Management",
    "security": "Security & Governance",
}

# (upper bound inclusive, label). Level number = position in this list + 1.
MATURITY_LEVELS = [
    (20, "Level 1 - Initial"),
    (40, "Level 2 - Developing"),
    (60, "Level 3 - Defined"),
    (80, "Level 4 - Managed"),
    (100, "Level 5 - Optimized"),
]
LEVEL_NUMBERS = {label: i + 1 for i, (_, label) in enumerate(MATURITY_LEVELS)}

# A category below this score is reported as a gap (60 = top of the "Defined" band).
GAP_THRESHOLD = 60
MAX_GAPS = 3


class AssessmentValidationError(ValueError):
    """Raised when the submitted answers are incomplete or out of range."""


# --------------------------------------------------------------------------
# Config consistency (fails loudly at import time instead of mis-scoring)
# --------------------------------------------------------------------------
def _check_config():
    total_weight = sum(c["weight"] for c in CATEGORIES.values())
    if abs(total_weight - 1.0) > 1e-9:
        raise RuntimeError(f"Category weights must sum to 1.0, got {total_weight}")
    for cat, details in CATEGORIES.items():
        ids_cat = list(details["questions"])
        ids_q = [q["id"] for q in QUESTIONS.get(cat, [])]
        if ids_cat != ids_q:
            raise RuntimeError(
                f"categories.json and questions.json disagree for '{cat}': {ids_cat} vs {ids_q}"
            )
        if cat not in CATEGORY_LABELS:
            raise RuntimeError(f"No display label for category '{cat}'")


_check_config()

ALL_QUESTION_IDS = [qid for details in CATEGORIES.values() for qid in details["questions"]]
QUESTION_TEXT = {q["id"]: q["text"] for qs in QUESTIONS.values() for q in qs}
QUESTION_CATEGORY = {
    qid: cat for cat, details in CATEGORIES.items() for qid in details["questions"]
}


def step_value(category):
    """Overall-score points gained when ONE answer in this category goes up by 1."""
    n = len(CATEGORIES[category]["questions"])
    return CATEGORIES[category]["weight"] * 100 / (n * MAX_ANSWER_VALUE)


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def validate_responses(responses):
    """
    Returns a cleaned {question_id: int} dict, or raises AssessmentValidationError
    listing EVERY problem found (missing, unknown, wrong type, out of range).
    """
    if not isinstance(responses, dict):
        raise AssessmentValidationError("responses must be a dict of {question_id: answer}")

    problems = []
    missing = [q for q in ALL_QUESTION_IDS if q not in responses]
    if missing:
        problems.append(f"missing answers: {', '.join(missing)}")
    unknown = [k for k in responses if k not in QUESTION_TEXT]
    if unknown:
        problems.append(f"unknown question ids: {', '.join(map(str, unknown))}")

    cleaned = {}
    for qid in ALL_QUESTION_IDS:
        if qid not in responses:
            continue
        value = responses[qid]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            problems.append(f"{qid}: must be a number 0-{MAX_ANSWER_VALUE}, got {value!r}")
            continue
        if value != int(value) or not (MIN_ANSWER_VALUE <= value <= MAX_ANSWER_VALUE):
            problems.append(f"{qid}: must be a whole number 0-{MAX_ANSWER_VALUE}, got {value!r}")
            continue
        cleaned[qid] = int(value)

    if problems:
        raise AssessmentValidationError("; ".join(problems))
    return cleaned


# --------------------------------------------------------------------------
# Core scoring (functions below assume validated responses)
# --------------------------------------------------------------------------
def calculate_category_score(responses, category_name):
    question_ids = CATEGORIES[category_name]["questions"]
    total = sum(responses[qid] for qid in question_ids)
    max_possible = len(question_ids) * MAX_ANSWER_VALUE
    return round((total / max_possible) * 100, 2)


def calculate_all_category_scores(responses):
    return {c: calculate_category_score(responses, c) for c in CATEGORIES}


def calculate_overall_score(category_scores):
    total = sum(category_scores[c] * d["weight"] for c, d in CATEGORIES.items())
    return round(total, 2)


def get_maturity_level(overall_score):
    for threshold, label in MATURITY_LEVELS:
        if overall_score <= threshold:
            return label
    return MATURITY_LEVELS[-1][1]


def get_level_number(level_label):
    return LEVEL_NUMBERS.get(level_label, 0)


def identify_gaps(category_scores, threshold=GAP_THRESHOLD, limit=MAX_GAPS):
    """
    Categories scoring below `threshold`, ranked by weighted shortfall
    (weight x points missing) so the fix with the biggest effect on the
    overall score comes first. At most `limit` are returned.
    """
    shortfall = {
        c: CATEGORIES[c]["weight"] * (100 - s)
        for c, s in category_scores.items()
        if s < threshold
    }
    return sorted(shortfall, key=lambda c: (-shortfall[c], c))[:limit]


# --------------------------------------------------------------------------
# Explanation helpers (exact, because the model is linear)
# --------------------------------------------------------------------------
def question_breakdown(responses):
    """Per-question detail incl. how many overall points each answer is costing."""
    rows = []
    for qid in ALL_QUESTION_IDS:
        cat = QUESTION_CATEGORY[qid]
        answer = responses[qid]
        rows.append(
            {
                "id": qid,
                "category": cat,
                "text": QUESTION_TEXT[qid],
                "answer": answer,
                "maxAnswer": MAX_ANSWER_VALUE,
                "pointsLost": round(step_value(cat) * (MAX_ANSWER_VALUE - answer), 2),
            }
        )
    return rows


def quick_wins(breakdown, limit=5):
    """Answers costing the most overall points, each with the gain from one step up."""
    weak = [r for r in breakdown if r["answer"] < MAX_ANSWER_VALUE]
    weak.sort(key=lambda r: (-r["pointsLost"], r["id"]))
    return [
        {**r, "gainPerStep": round(step_value(r["category"]), 2)} for r in weak[:limit]
    ]


def next_level_info(overall_score):
    for i, (threshold, label) in enumerate(MATURITY_LEVELS):
        if overall_score <= threshold:
            if i == len(MATURITY_LEVELS) - 1:
                return None
            nxt = MATURITY_LEVELS[i + 1][1]
            return {
                "level": nxt,
                "levelNumber": i + 2,
                "scoreToExceed": threshold,
                "pointsToExceed": round(max(threshold - overall_score, 0), 2),
            }
    return None


def _overall_from_responses(responses):
    return calculate_overall_score(calculate_all_category_scores(responses))


def plan_to_next_level(responses, max_steps=100):
    """
    Fastest-moving path to the next maturity level: repeatedly raise ONE
    answer by ONE step, choosing the answer worth the most points (ties go to
    the lowest current answer, then question order). Greedy and deterministic.
    It ignores effort/cost, so treat it as "what moves the score fastest".
    """
    current = dict(responses)
    start_score = _overall_from_responses(current)
    start_level = get_level_number(get_maturity_level(start_score))
    if start_level == len(MATURITY_LEVELS):
        return None

    steps = []
    for _ in range(max_steps):
        candidates = [q for q in ALL_QUESTION_IDS if current[q] < MAX_ANSWER_VALUE]
        if not candidates:
            break
        qid = max(
            candidates,
            key=lambda q: (
                step_value(QUESTION_CATEGORY[q]),
                -current[q],
                -ALL_QUESTION_IDS.index(q),
            ),
        )
        before = current[qid]
        current[qid] = before + 1
        score = _overall_from_responses(current)
        steps.append(
            {
                "id": qid,
                "category": QUESTION_CATEGORY[qid],
                "text": QUESTION_TEXT[qid],
                "from": before,
                "to": before + 1,
                "scoreAfter": score,
            }
        )
        if get_level_number(get_maturity_level(score)) > start_level:
            break

    final = _overall_from_responses(current)
    return {
        "steps": steps,
        "resultingScore": final,
        "resultingLevel": get_maturity_level(final),
    }


def what_if(responses, changes):
    """
    Re-score with some answers changed, e.g. what_if(answers, {"data_2": 4}).
    Returns before/after scores so the UI can show the effect of an action.
    """
    base = validate_responses(responses)
    if not isinstance(changes, dict) or not changes:
        raise AssessmentValidationError("changes must be a non-empty dict")
    bad = [k for k in changes if k not in QUESTION_TEXT]
    if bad:
        raise AssessmentValidationError(f"unknown question ids in changes: {', '.join(map(str, bad))}")
    changed = validate_responses({**base, **changes})

    def summary(r):
        cats = calculate_all_category_scores(r)
        overall = calculate_overall_score(cats)
        return {
            "categoryScores": cats,
            "overallScore": overall,
            "maturityLevel": get_maturity_level(overall),
        }

    before, after = summary(base), summary(changed)
    return {
        "before": before,
        "after": after,
        "scoreDelta": round(after["overallScore"] - before["overallScore"], 2),
        "levelChanged": before["maturityLevel"] != after["maturityLevel"],
    }


# --------------------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------------------
def run_full_assessment(responses):
    """
    Pass in a flat dict of all 25 answers (0-4). Raises AssessmentValidationError
    on bad input. Returns the complete result to store in DynamoDB.

    Keys from the original version are unchanged:
        categoryScores, overallScore, maturityLevel, gaps
    Added: levelNumber, questionBreakdown, quickWins, nextLevel, planToNextLevel
    """
    clean = validate_responses(responses)
    category_scores = calculate_all_category_scores(clean)
    overall_score = calculate_overall_score(category_scores)
    maturity_level = get_maturity_level(overall_score)
    breakdown = question_breakdown(clean)

    return {
        "categoryScores": category_scores,
        "overallScore": overall_score,
        "maturityLevel": maturity_level,
        "levelNumber": get_level_number(maturity_level),
        "gaps": identify_gaps(category_scores),
        "questionBreakdown": breakdown,
        "quickWins": quick_wins(breakdown),
        "nextLevel": next_level_info(overall_score),
        "planToNextLevel": plan_to_next_level(clean),
    }
