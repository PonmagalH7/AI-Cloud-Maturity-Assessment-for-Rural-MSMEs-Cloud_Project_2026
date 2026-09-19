from generate_recommendation import generate_recommendation

result = generate_recommendation(
    business_type="retail",
    category_scores={
        "infrastructure": 60.0,
        "process": 70.0,
        "people": 50.0,
        "data": 65.0,
        "security": 55.0,
    },
    overall_score=60.5,
    maturity_level="Level 4 - Managed",
    gaps=["people", "security"],
)

print("Source:   ", result["source"])
print("Summary:  ", result["summary"])
print("Priorities:")
for p in result["priorities"]:
    print("  -", p)
