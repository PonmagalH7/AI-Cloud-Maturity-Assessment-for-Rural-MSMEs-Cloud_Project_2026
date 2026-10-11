
from pathlib import Path
import pandas as pd
import pyreadstat

# Project root is the parent folder of AI-models
ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "database"

files = [
    "fat0_raw_data_qje.dta",
    "isic_data.dta",
]

output_dir = Path(__file__).resolve().parent / "data" / "world_bank_fat"
output_dir.mkdir(parents=True, exist_ok=True)

for filename in files:
    filepath = DATABASE / filename

    print("\n" + "=" * 70)
    print(f"FILE: {filename}")
    print("=" * 70)

    if not filepath.exists():
        print(f"File not found: {filepath}")
        continue

    df, metadata = pyreadstat.read_dta(filepath)

    print("Dataset shape (rows, columns):", df.shape)
    print("\nColumn names and descriptions:")

    labels = metadata.column_names_to_labels
    inventory = pd.DataFrame({
        "column": df.columns,
        "description": [
            labels.get(column, "") for column in df.columns
        ],
        "missing_count": [
            df[column].isna().sum() for column in df.columns
        ],
        "unique_values": [
            df[column].nunique(dropna=True) for column in df.columns
        ],
    })

    print(inventory.head(40).to_string(index=False))

    output_file = output_dir / (
        filename.replace(".dta", "_variable_inventory.csv")
    )
    inventory.to_csv(output_file, index=False)

    print("\nFirst 5 rows:")
    print(df.head().to_string())

    print("\nMissing values — top 15 columns:")
    print(
        df.isna().sum()
        .sort_values(ascending=False)
        .head(15)
        .to_string()
    )

    print(f"\nVariable inventory saved to: {output_file}")
