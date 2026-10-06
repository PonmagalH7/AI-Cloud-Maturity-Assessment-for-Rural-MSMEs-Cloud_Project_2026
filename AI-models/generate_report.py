import re

from report_template import render_report_html

# Keeps S3 keys safe: letters, digits, dash, underscore only.
_SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,100}$")


def generate_report(assessment_id, business_name, business_type, scoring_result, recommendation_result):
    """
    Main entry point for the report Lambda.

    scoring_result: output of run_full_assessment() in scoring.py
    recommendation_result: output of generate_recommendation()

    Returns {"html": <string>, "filename": <string>}; upload "html" to S3 using
    "filename" as the key. Raises ValueError if assessment_id is not key-safe.
    """
    if not isinstance(assessment_id, str) or not _SAFE_ID.match(assessment_id):
        raise ValueError("assessment_id may only contain letters, digits, '-' and '_' (max 100)")

    html = render_report_html(
        business_name=business_name,
        business_type=business_type,
        category_scores=scoring_result["categoryScores"],
        overall_score=scoring_result["overallScore"],
        maturity_level=scoring_result["maturityLevel"],
        gaps=scoring_result["gaps"],
        summary=recommendation_result["summary"],
        priorities=recommendation_result["priorities"],
        assessment_id=assessment_id,
        next_level=scoring_result.get("nextLevel"),
        quick_wins=scoring_result.get("quickWins"),
        source=recommendation_result.get("source"),
    )
    return {"html": html, "filename": f"reports/{assessment_id}.html"}
