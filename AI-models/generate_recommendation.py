from bedrock_client import call_bedrock
from recommendation_prompt import build_prompt
from fallback_recommendations import get_fallback_recommendation


def generate_recommendation(business_type, category_scores, overall_score, maturity_level, gaps):
    """
    Main entry point for Person 2's Lambda. Tries Bedrock (Nova Micro) first,
    falls back to rules-based recommendations if Bedrock fails for any reason
    (permissions, timeout, malformed response, etc.)
    """
    try:
        prompt = build_prompt(business_type, category_scores, overall_score, maturity_level, gaps)
        result = call_bedrock(prompt)

        # Basic validation - don't trust the model blindly
        if "summary" not in result or "priorities" not in result:
            raise ValueError("Bedrock response missing expected fields")

        result["source"] = "bedrock"
        return result

    except Exception:
        # In production, log the exception to CloudWatch here so you know
        # how often the fallback is triggering.
        fallback = get_fallback_recommendation(overall_score, maturity_level, gaps, business_type)
        fallback["source"] = "fallback"
        return fallback
