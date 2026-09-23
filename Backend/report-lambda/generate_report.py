from report_template import render_report_html


def generate_report(assessment_id, business_name, business_type, scoring_result, recommendation_result):
    """
    Main entry point for Person 2's Lambda (generateReport()).

    assessment_id: str - the assessment's unique ID (used in filename + footer)
    business_name: str - business name from the assessment payload
    business_type: str - e.g. "retail", "logistics"
    scoring_result: dict - output of run_full_assessment() from scoring.py
                    -> {categoryScores, overallScore, maturityLevel, gaps}
    recommendation_result: dict - output of generate_recommendation() from
                    generate_recommendation.py -> {summary, priorities, source}

    Returns a dict: {"html": <string>, "filename": <string>}
    Person 2 uploads the "html" string as an object to S3 using "filename" as the key.
    """
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
    )

    filename = f"reports/{assessment_id}.html"

    return {"html": html, "filename": filename}
