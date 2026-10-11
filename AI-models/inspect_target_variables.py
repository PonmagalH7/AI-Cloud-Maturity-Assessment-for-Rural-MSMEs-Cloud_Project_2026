
from pathlib import Path
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "database" / "fat0_raw_data_qje.dta"

df, metadata = pyreadstat.read_dta(DATA_FILE)

targets = [
    "b5a",
    "b4a",
    "db8a2",
    "db8a3",
    "db8a4",
    "db9a5",
    "db14a5",
]

labels = metadata.column_names_to_labels
value_labels = metadata.variable_value_labels

for column in targets:
    if column not in df.columns:
        continue

    print("\n" + "=" * 60)
    print("VARIABLE:", column)
    print("DESCRIPTION:", labels.get(column, "No description"))
    print("VALUE LABELS:", value_labels.get(column, "No value labels"))
    print("MISSING:", int(df[column].isna().sum()))
    print("VALUE COUNTS:")
    print(df[column].value_counts(dropna=False).to_string())
