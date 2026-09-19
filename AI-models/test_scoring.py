from scoring import run_full_assessment

# This test uses the SAME example numbers your teammate worked out by hand,
# so if this script's output matches, your code is correct:
#   Infrastructure = 60, Process = 70, People = 50, Data = 65, Security = 55
#   Expected overall = 60.5, expected level = Level 3 - Defined

fake_responses = {
    # Infrastructure -> sum must be 12 -> (12/20)*100 = 60
    "infra_1": 3, "infra_2": 2, "infra_3": 3, "infra_4": 2, "infra_5": 2,

    # Process -> sum must be 14 -> (14/20)*100 = 70
    "process_1": 3, "process_2": 3, "process_3": 3, "process_4": 3, "process_5": 2,

    # People -> sum must be 10 -> (10/20)*100 = 50
    "people_1": 2, "people_2": 2, "people_3": 2, "people_4": 2, "people_5": 2,

    # Data -> sum must be 13 -> (13/20)*100 = 65
    "data_1": 3, "data_2": 3, "data_3": 3, "data_4": 2, "data_5": 2,

    # Security -> sum must be 11 -> (11/20)*100 = 55
    "security_1": 3, "security_2": 2, "security_3": 2, "security_4": 2, "security_5": 2,
}

result = run_full_assessment(fake_responses)

print("Category scores:", result["categoryScores"])
print("Overall score:  ", result["overallScore"])
print("Maturity level: ", result["maturityLevel"])
print("Gaps:           ", result["gaps"])

print()
print("Expected: overall=60.5, level='Level 3 - Defined'")
