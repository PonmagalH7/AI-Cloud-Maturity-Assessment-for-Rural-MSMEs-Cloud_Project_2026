from generate_report import generate_report

scoring_result = {
    "categoryScores": {
        "infrastructure": 60.0,
        "process": 70.0,
        "people": 50.0,
        "data": 65.0,
        "security": 55.0,
    },
    "overallScore": 60.5,
    "maturityLevel": "Level 4 - Managed",
    "gaps": ["people", "security"],
}

recommendation_result = {
    "summary": "Your business scored 60.5/100, placing it at Level 4 - Managed. "
                "The areas needing the most attention are: people, security.",
    "priorities": [
        "Run a short internal session to walk staff through the tools you already use",
        "Turn on multi-factor authentication (MFA) for all business accounts",
        "Assign one staff member as the point of contact for basic tech issues",
    ],
    "source": "fallback",
}

result = generate_report(
    assessment_id="test-assessment-001",
    business_name="Sri Lakshmi General Store",
    business_type="Retail",
    scoring_result=scoring_result,
    recommendation_result=recommendation_result,
)

print("Filename:", result["filename"])
print("HTML length:", len(result["html"]), "characters")

# Basic sanity checks - if any of these fail, something's structurally wrong
checks = {
    "has doctype": result["html"].strip().startswith("<!DOCTYPE html>"),
    "has overall score": "60.5" in result["html"],
    "has maturity level": "Level 4 - Managed" in result["html"],
    "has business name": "Sri Lakshmi General Store" in result["html"],
    "has all 5 categories": all(
        label in result["html"]
        for label in [
            "Infrastructure & Technology",
            "Processes & Digital Operations",
            "People & Skills",
            "Data Management",
            "Security & Governance",
        ]
    ),
    "has all 3 priorities": all(p in result["html"] for p in recommendation_result["priorities"]),
    "has assessment id": "test-assessment-001" in result["html"],
    "closes html tag": result["html"].strip().endswith("</html>"),
}

print()
for check, passed in checks.items():
    print(f"  [{'OK' if passed else 'FAIL'}] {check}")

assert all(checks.values()), "One or more checks failed - see above"
print()
print("All checks passed.")

# Save a local copy so you can open it in a browser and actually look at it
with open("sample_report_output.html", "w") as f:
    f.write(result["html"])
print("Saved sample_report_output.html - open this in a browser to see the rendered report")
