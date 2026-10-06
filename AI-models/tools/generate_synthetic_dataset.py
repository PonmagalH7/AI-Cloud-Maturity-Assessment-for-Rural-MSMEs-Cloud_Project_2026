"""
Generates a SYNTHETIC test dataset of MSME assessments.

IMPORTANT: this is made-up data for testing the pipeline only. The archetypes
and their typical answers are assumptions, not findings. Do not use it to
train, validate or report the accuracy of anything. Replace it with real
survey responses for any research claim.

Usage:  python tools/generate_synthetic_dataset.py   (writes data/synthetic_msme_assessments.csv)
"""
import csv
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from scoring import ALL_QUESTION_IDS, CATEGORIES, MAX_ANSWER_VALUE  # noqa: E402

# name -> typical answer (0-4) for each category
ARCHETYPES = {
    "1_paper_only":        {"infrastructure": 0.8, "process": 0.6, "people": 0.8, "data": 0.6, "security": 0.6},
    "2_phone_whatsapp":    {"infrastructure": 1.6, "process": 1.4, "people": 1.5, "data": 1.3, "security": 1.2},
    "3_partly_digital":    {"infrastructure": 2.4, "process": 2.3, "people": 2.2, "data": 2.2, "security": 2.0},
    "4_cloud_adopting":    {"infrastructure": 3.1, "process": 3.0, "people": 2.8, "data": 3.0, "security": 2.8},
    "5_cloud_mature":      {"infrastructure": 3.7, "process": 3.6, "people": 3.4, "data": 3.7, "security": 3.5},
}
SIZE_WEIGHTS = {  # (Micro, Small, Medium) - more mature profiles skew larger
    "1_paper_only": (0.90, 0.10, 0.00),
    "2_phone_whatsapp": (0.75, 0.22, 0.03),
    "3_partly_digital": (0.55, 0.35, 0.10),
    "4_cloud_adopting": (0.35, 0.45, 0.20),
    "5_cloud_mature": (0.20, 0.45, 0.35),
}
SECTORS = ["Retail", "Food processing", "Handloom and textile", "Agri-based", "Services", "Small manufacturing"]
LANGUAGES = ["English", "Tamil", "Hindi"]


def _answer(rng, mean, business_offset):
    value = rng.gauss(mean + business_offset, 0.6)
    return max(0, min(MAX_ANSWER_VALUE, int(round(value))))


def generate(per_archetype=60, seed=2026):
    rng = random.Random(seed)
    rows, n = [], 0
    for archetype, means in ARCHETYPES.items():
        for _ in range(per_archetype):
            n += 1
            offset = rng.gauss(0, 0.4)  # one business is a bit better/worse across the board
            row = {
                "record_id": f"SYN-{n:04d}",
                "archetype": archetype,
                "enterprise_size": rng.choices(["Micro", "Small", "Medium"], SIZE_WEIGHTS[archetype])[0],
                "sector": rng.choice(SECTORS),
                "language": rng.choices(LANGUAGES, [0.4, 0.4, 0.2])[0],
            }
            for cat, details in CATEGORIES.items():
                for qid in details["questions"]:
                    row[qid] = _answer(rng, means[cat], offset)
            rows.append(row)
    return rows


def write_csv(rows, path):
    fields = ["record_id", "archetype", "enterprise_size", "sector", "language", *ALL_QUESTION_IDS]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(HERE), "data", "synthetic_msme_assessments.csv")
    data = generate()
    write_csv(data, out)
    print(f"Wrote {len(data)} synthetic records to {out}")
