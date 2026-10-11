
from pathlib import Path
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "database" / "fat0_raw_data_qje.dta"

df, metadata = pyreadstat.read_dta(DATA_FILE)

print("Dataset shape:", df.shape)

for column in ["country", "a5a", "s7", "base_wt", "formality"]:
    if column not in df.columns:
        print(f"\n{column}: not found")
        continue

    print(f"\n{'=' * 50}")
    print("COLUMN:", column)
    print("DESCRIPTION:",
          metadata.column_names_to_labels.get(column, "No description"))
    print("MISSING:", int(df[column].isna().sum()))
    print("UNIQUE VALUES:", df[column].nunique(dropna=True))

    if column in ["country", "a5a", "formality"]:
        print(df[column].value_counts(dropna=False).head(30).to_string())
    elif column == "base_wt":
        print(df[column].describe().to_string())
