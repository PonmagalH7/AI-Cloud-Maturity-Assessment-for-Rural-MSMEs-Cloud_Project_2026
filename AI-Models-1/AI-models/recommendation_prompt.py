from scoring import CATEGORY_LABELS, MAX_ANSWER_VALUE

SUPPORTED_LANGUAGES = ("English", "Tamil", "Hindi")


def _weak_question_lines(weak_questions, limit=5):
    """Turn the costliest answers into short lines the model can reason about."""
    rows = sorted(
        (q for q in (weak_questions or []) if q["answer"] < MAX_ANSWER_VALUE),
        key=lambda q: (-q["pointsLost"], q["id"]),
    )[:limit]
    return "\n".join(
        f"- [{CATEGORY_LABELS.get(q['category'], q['category'])}] {q['text']} "
        f"-> answered {q['answer']} out of {MAX_ANSWER_VALUE}"
        for q in rows
    )


def build_prompt(
    business_type,
    category_scores,
    overall_score,
    maturity_level,
    gaps,
    weak_questions=None,
    language="English",
):
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"language must be one of {SUPPORTED_LANGUAGES}, got {language!r}")

    weak_block = _weak_question_lines(weak_questions)
    weak_section = (
        f"\nThe specific answers that cost this business the most points "
        f"(0 = not at all, {MAX_ANSWER_VALUE} = fully in place):\n{weak_block}\n"
        "Base each step on these specific answers, not on generic advice.\n"
        if weak_block
        else ""
    )

    return f"""You are a cloud advisor for a rural MSME (Micro, Small, or Medium
Enterprise) in India. You will be given a cloud maturity assessment result.
Do not invent or change any numbers - use only the scores given. Explain the
result in plain, non-technical language suitable for a small business owner,
and suggest exactly 3 practical next steps, prioritizing the weakest categories.
Each step must be one sentence of at most 25 words.

This business is classified as a {business_type} enterprise under India's
MSME classification. Scale your suggestions to match: a Micro enterprise
typically has very limited budget and staff, so favor free or near-zero-cost
steps and avoid suggesting dedicated IT hires or paid enterprise tools. A
Small enterprise can typically afford small recurring costs (e.g. a paid
backup service, a part-time trainer). A Medium enterprise can typically
absorb moderate investment (e.g. a proper cloud migration project, hiring
part-time IT support). Do not mention the word "budget" or the classification
itself in your output - just make the suggestions naturally appropriate for
a business of this scale.

Overall score: {overall_score}/100 ({maturity_level})
Category scores: {category_scores}
Weakest categories (gaps): {gaps}
{weak_section}
Write the summary and the steps in {language}. Keep the JSON keys in English.

Respond ONLY with valid JSON in this exact format, nothing else:
{{
  "summary": "2-3 sentence plain-language explanation of the result",
  "priorities": ["step 1", "step 2", "step 3"]
}}"""
