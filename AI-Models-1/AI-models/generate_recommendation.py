import logging
import re

from fallback_recommendations import get_fallback_recommendation
from recommendation_prompt import SUPPORTED_LANGUAGES, build_prompt

logger = logging.getLogger(__name__)

_NUMBER = re.compile(r"\d+(?:\.\d+)?")


def _allowed_numbers(category_scores, overall_score):
    scores = [overall_score, *category_scores.values()]
    return scores, set(range(0, 6)) | {100}  # score values, plus small counts / "out of 100"


def _check_numbers(text, category_scores, overall_score):
    """Reject the reply if it mentions a number that isn't one of our scores."""
    scores, small = _allowed_numbers(category_scores, overall_score)
    for raw in _NUMBER.findall(text):
        n = float(raw)
        if n in small:
            continue
        if any(abs(n - s) <= 0.5 for s in scores):
            continue
        raise ValueError(f"model mentioned a number we did not give it: {raw}")


def validate_llm_result(result, category_scores, overall_score):
    """Raises ValueError unless the reply is exactly what we asked for."""
    if not isinstance(result, dict):
        raise ValueError("reply is not a JSON object")
    summary = result.get("summary")
    priorities = result.get("priorities")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("summary missing or empty")
    if (
        not isinstance(priorities, list)
        or len(priorities) != 3
        or not all(isinstance(p, str) and p.strip() for p in priorities)
    ):
        raise ValueError("priorities must be a list of exactly 3 non-empty strings")
    _check_numbers(summary, category_scores, overall_score)
    for p in priorities:
        _check_numbers(p, category_scores, overall_score)
    return {"summary": summary.strip(), "priorities": [p.strip() for p in priorities]}


def generate_recommendation(
    business_type,
    category_scores,
    overall_score,
    maturity_level,
    gaps,
    weak_questions=None,
    language="English",
    llm_call=None,
):
    """
    Main entry point for the recommendation Lambda. Tries Bedrock first and
    falls back to rules-based advice if the call fails or the reply fails
    validation. The result always has: summary, priorities (3), source, and
    (when the fallback is used) fallback_reason.

    weak_questions: pass result["questionBreakdown"] from scoring for
    personalised advice. llm_call: inject a fake in tests.
    """
    reason = None
    try:
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"unsupported language: {language}")
        if llm_call is None:
            from bedrock_client import call_bedrock as llm_call
        prompt = build_prompt(
            business_type, category_scores, overall_score, maturity_level, gaps,
            weak_questions=weak_questions, language=language,
        )
        result = validate_llm_result(llm_call(prompt), category_scores, overall_score)
        result["source"] = "bedrock"
        result["language"] = language
        return result
    except Exception as exc:  # deliberately broad: any failure must still produce a report
        reason = f"{type(exc).__name__}: {exc}"
        logger.warning("Bedrock recommendation failed, using fallback (%s)", reason)

    fallback = get_fallback_recommendation(
        overall_score, maturity_level, gaps, business_type, weak_questions=weak_questions
    )
    fallback["source"] = "fallback"
    fallback["language"] = "English"  # fallback tips are English only
    fallback["fallback_reason"] = reason
    return fallback
