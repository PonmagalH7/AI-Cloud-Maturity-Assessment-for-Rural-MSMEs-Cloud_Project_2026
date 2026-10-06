# What changed in AI-models

## Replace these files (same names)
scoring.py, recommendation_prompt.py, bedrock_client.py, generate_recommendation.py,
fallback_recommendations.py, report_template.py, generate_report.py, sample_report_output.html

## Delete these old files (replaced by tests/)
test_scoring.py, test_report.py, test_recommendation.py   (the ones in AI-models/ root)
Also delete AI-models/__pycache__ from git if it was committed, and add a .gitignore with: __pycache__/ .pytest_cache/

## Add these new files
requirements.txt, tests/, tools/, data/

## Behaviour changes you should know about
* run_full_assessment() now RAISES AssessmentValidationError for missing, unknown, non-integer
  or out-of-range (not 0-4) answers. Your Lambda must catch it and return HTTP 400.
* Gaps: categories below 60, ranked by weighted shortfall, max 3 (before: below 50, sorted by score).
* New result keys: levelNumber, questionBreakdown, quickWins, nextLevel, planToNextLevel.
  Old keys are unchanged. DynamoDB does not accept Python floats - convert with Decimal before put_item.
* generate_recommendation() accepts weak_questions (pass result["questionBreakdown"]) and
  language ("English", "Tamil", "Hindi"). Replies with wrong shape or invented numbers are rejected.
  The result has source ("bedrock"/"fallback") and, for fallbacks, fallback_reason.
* generate_report() rejects assessment_ids that are not letters/digits/-/_.
  All text in the report is HTML-escaped.
* bedrock_client creates the AWS client lazily. NOT VERIFIED: that amazon.nova-micro-v1:0 is
  enabled for your account in ap-south-1 (some regions need an inference-profile ID).
  Run one real call yourself before relying on it. The Bedrock path was only tested with a fake model.
