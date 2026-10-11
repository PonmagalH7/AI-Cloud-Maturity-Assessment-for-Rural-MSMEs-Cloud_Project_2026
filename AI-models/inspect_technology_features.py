
from pathlib import Path
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "database" / "fat0_raw_data_qje.dta"

df, metadata = pyreadstat.read_dta(DATA_FILE)
labels = metadata.column_names_to_labels

# First inspect likely technology-related variables.
keywords = [
    "internet", "computer", "digital", "technology",
    "cloud", "software", "website", "mobile",
    "online", "email", "automation", "ict",
    "years using", "production", "sector",
    "workers", "electrical connection"
]

results = []

for column in df.columns:
    description = str(labels.get(column, ""))
    if any(word in description.lower() for word in keywords):
        results.append({
            "column": column,
            "description": description,
            "missing_count": df[column].isna().sum(),
            "unique_values": df[column].nunique(dropna=True),
            "sample_values": str(
                df[column].dropna().unique()[:10].tolist()
            )
        })

output = pd.DataFrame(results)
output.to_csv(
    Path(__file__).resolve().parent
    / "data" / "world_bank_fat"
    / "technology_features.csv",
    index=False
)

print("Potential technology-related variables:", len(output))
print(output.to_string(index=False))
print("\nSaved to AI-models/data/world_bank_fat/technology_features.csv")
