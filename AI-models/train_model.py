from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------
# 1. Load the dataset
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "synthetic_msme_assessments.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print("Number of records:", len(df))


# --------------------------------------------------
# 2. Select input features and target
# --------------------------------------------------

# We exclude record_id and archetype from the inputs.
# Archetype is the label the model must learn to predict.

question_columns = [
    col for col in df.columns
    if col.startswith((
        "infra_", "process_", "people_", "data_", "security_"
    ))
]

categorical_columns = [
    "enterprise_size", "sector", "language"
]

feature_columns = categorical_columns + question_columns

X = df[feature_columns].copy()
y = df["archetype"].copy()

# Treat business information as categorical data.
X[categorical_columns] = (
    X[categorical_columns].fillna("Unknown").astype(str)
)

# Convert assessment answers to numbers.
X[question_columns] = X[question_columns].apply(
    pd.to_numeric, errors="raise"
)

print("Number of input features:", len(feature_columns))
print("Target classes:", sorted(y.unique()))


# --------------------------------------------------
# 3. Split the data into training and testing sets
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training records:", len(X_train))
print("Testing records:", len(X_test))


# --------------------------------------------------
# 4. Prepare the features
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_columns
        ),
        ("numeric", "passthrough", question_columns)
    ]
)


# --------------------------------------------------
# 5. Create and train the ML model
# --------------------------------------------------

model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            RandomForestClassifier(
                n_estimators=200,
                random_state=42,
                class_weight="balanced"
            )
        )
    ]
)

model.fit(X_train, y_train)

print("\nModel training completed!")


# --------------------------------------------------
# 6. Evaluate the model on unseen test records
# --------------------------------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print(f"\nTest accuracy: {accuracy:.4f}")
print(f"Test accuracy percentage: {accuracy * 100:.2f}%")

print("\nClassification report:")
print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# --------------------------------------------------
# 7. Save the trained model
# --------------------------------------------------

model_path = MODEL_DIR / "archetype_classifier.joblib"

joblib.dump(model, model_path)

print("\nTrained model saved to:")
print(model_path)
