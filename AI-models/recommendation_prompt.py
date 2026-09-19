def build_prompt(business_type, category_scores, overall_score, maturity_level, gaps):
    return f"""You are a cloud advisor for a rural micro/small business in India.
You will be given a cloud maturity assessment result. Do not invent or change
any numbers - use only the scores given. Explain the result in plain,
non-technical language suitable for a small business owner, and suggest
exactly 3 practical, low-cost next steps, prioritizing the weakest categories.

Business type: {business_type}
Overall score: {overall_score}/100 ({maturity_level})
Category scores: {category_scores}
Weakest categories (gaps): {gaps}

Respond ONLY with valid JSON in this exact format, nothing else:
{{
  "summary": "2-3 sentence plain-language explanation of the result",
  "priorities": ["step 1", "step 2", "step 3"]
}}"""
