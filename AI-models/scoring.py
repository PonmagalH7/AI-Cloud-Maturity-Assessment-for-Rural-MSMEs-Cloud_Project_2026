import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "categories.json")) as f:
    CATEGORIES = json.load(f)

with open(os.path.join(BASE_DIR, "questions.json")) as f:
    QUESTIONS = json.load(f)

MAX_ANSWER_VALUE = 4  # scale is 0-4

MATURITY_LEVELS = [
    (20, "Level 1 - Initial"),
    (40, "Level 2 - Developing"),
    (60, "Level 3 - Defined"),
    (80, "Level 4 - Managed"),
    (100, "Level 5 - Optimized"),
]


def calculate_category_score(responses, category_name):
    """
    responses: dict of {question_id: answer_value} for ALL categories, e.g.
        {"infra_1": 3, "infra_2": 2, ..., "security_5": 1}
    category_name: e.g. "infrastructure"
    """
    question_ids = CATEGORIES[category_name]["questions"]
    total = sum(responses.get(qid, 0) for qid in question_ids)
    max_possible = len(question_ids) * MAX_ANSWER_VALUE  # 5 x 4 = 20
    return round((total / max_possible) * 100, 2)


def calculate_all_category_scores(responses):
    return {
        category: calculate_category_score(responses, category)
        for category in CATEGORIES
    }


def calculate_overall_score(category_scores):
    total = 0
    for category, details in CATEGORIES.items():
        weight = details["weight"]
        total += category_scores.get(category, 0) * weight
    return round(total, 2)


def get_maturity_level(overall_score):
    for threshold, label in MATURITY_LEVELS:
        if overall_score <= threshold:
            return label
    return MATURITY_LEVELS[-1][1]


def identify_gaps(category_scores, threshold=50):
    gaps = [c for c, s in category_scores.items() if s < threshold]
    gaps.sort(key=lambda c: category_scores[c])
    return gaps


def run_full_assessment(responses):
    """
    Main entry point. Pass in a flat dict of all 25 answers.
    Returns the complete result Person 2's Lambda should store in DynamoDB.
    """
    category_scores = calculate_all_category_scores(responses)
    overall_score = calculate_overall_score(category_scores)
    maturity_level = get_maturity_level(overall_score)
    gaps = identify_gaps(category_scores)

    return {
        "categoryScores": category_scores,
        "overallScore": overall_score,
        "maturityLevel": maturity_level,
        "gaps": gaps,
    }
