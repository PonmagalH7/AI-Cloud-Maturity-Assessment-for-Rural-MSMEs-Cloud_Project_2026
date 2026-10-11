"""
Train two separate models for the AI Cloud Maturity Assessment project.

1) App-aligned model:
   Predicts the synthetic dataset's archetype from the app's 25 assessment
   answers plus enterprise metadata. This is schema-compatible with the app,
   but its labels are synthetic and must not be presented as real-world proof.

2) Real-survey model:
   Predicts World Bank survey variable db8a3 (adoption of mobile apps/digital
   platforms for business administration) from selected survey features.
   This is a separate research model, NOT a cloud-maturity model and NOT
   directly callable from the app unless the app collects matching features.

Run from the AI-models directory:
    py train_project_models.py

Required packages:
    py -m pip install pandas scikit-learn joblib pyreadstat
"""

from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, classification_report,
    f1_score, precision_score, recall_score
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier

warnings.filterwarnings("ignore", category=FutureWarning)

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
DATA_DIR = HERE / "data"
MODEL_DIR = HERE / "models"
REPORT_DIR = HERE / "data" / "training_results"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42


def make_preprocessor(frame: pd.DataFrame, scale_numeric: bool):
    categorical = frame.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numeric = [c for c in frame.columns if c not in categorical]

    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))
    numeric_pipe = Pipeline(numeric_steps)

    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    transformer = ColumnTransformer([
        ("numeric", numeric_pipe, numeric),
        ("categorical", categorical_pipe, categorical),
    ])
    return transformer


def candidate_models(scale_numeric: bool):
    models = {
        "logistic_regression": LogisticRegression(
            max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "decision_tree": DecisionTreeClassifier(
            class_weight="balanced", min_samples_leaf=3, random_state=RANDOM_STATE
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300, class_weight="balanced_subsample",
            min_samples_leaf=2, n_jobs=-1, random_state=RANDOM_STATE
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=300, class_weight="balanced",
            min_samples_leaf=2, n_jobs=-1, random_state=RANDOM_STATE
        ),
        "gradient_boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }
    if scale_numeric:
        models["svm_rbf"] = SVC(
            kernel="rbf", class_weight="balanced", probability=True,
            random_state=RANDOM_STATE
        )
        models["knn"] = KNeighborsClassifier(n_neighbors=7, weights="distance")
    return models


def train_and_compare(
    *,
    dataset_name: str,
    X: pd.DataFrame,
    y: pd.Series,
    output_prefix: str,
    scale_numeric: bool,
    cv_splits: int,
):
    usable = y.notna()
    X = X.loc[usable].copy()
    y = y.loc[usable].astype(str).copy()

    # Drop rows with no usable predictors at all.
    keep = X.notna().any(axis=1)
    X, y = X.loc[keep], y.loc[keep]

    counts = y.value_counts()
    if len(counts) < 2 or counts.min() < 2:
        raise ValueError(f"{dataset_name}: not enough examples in each class: {counts.to_dict()}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )

    preprocessor = make_preprocessor(X_train, scale_numeric)
    min_class_count = int(y_train.value_counts().min())
    folds = min(cv_splits, min_class_count)
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=RANDOM_STATE)

    rows = []
    fitted = {}

    for name, estimator in candidate_models(scale_numeric).items():
        pipe = Pipeline([
            ("preprocessor", clone(preprocessor)),
            ("model", estimator),
        ])
        try:
            cv_scores = cross_val_score(
                pipe, X_train, y_train, cv=cv, scoring="f1_macro", n_jobs=1
            )
            pipe.fit(X_train, y_train)
            pred = pipe.predict(X_test)

            row = {
                "dataset": dataset_name,
                "model": name,
                "rows_used": len(X),
                "features": X.shape[1],
                "test_accuracy": accuracy_score(y_test, pred),
                "test_balanced_accuracy": balanced_accuracy_score(y_test, pred),
                "test_macro_f1": f1_score(y_test, pred, average="macro", zero_division=0),
                "test_weighted_f1": f1_score(y_test, pred, average="weighted", zero_division=0),
                "test_macro_precision": precision_score(y_test, pred, average="macro", zero_division=0),
                "test_macro_recall": recall_score(y_test, pred, average="macro", zero_division=0),
                "cv_macro_f1_mean": float(np.mean(cv_scores)),
                "cv_macro_f1_std": float(np.std(cv_scores)),
            }
            rows.append(row)
            fitted[name] = (pipe, row, y_test, pred)
            print(
                f"{dataset_name} | {name:20s} "
                f"test macro-F1={row['test_macro_f1']:.3f} "
                f"CV macro-F1={row['cv_macro_f1_mean']:.3f} "
                f"accuracy={row['test_accuracy']:.3f}"
            )
        except Exception as exc:
            print(f"WARNING: {dataset_name} | {name} failed: {exc}")

    if not fitted:
        raise RuntimeError(f"No models trained successfully for {dataset_name}")

    comparison = pd.DataFrame(rows).sort_values(
        ["cv_macro_f1_mean", "test_macro_f1"], ascending=False
    )
    comparison_path = REPORT_DIR / f"{output_prefix}_model_comparison.csv"
    comparison.to_csv(comparison_path, index=False)

    # Select by CV score, not by test score; test set remains final evaluation.
    best_name = comparison.iloc[0]["model"]
    best_pipe, best_row, y_test, pred = fitted[best_name]
    model_path = MODEL_DIR / f"{output_prefix}_best.joblib"
    joblib.dump({
        "pipeline": best_pipe,
        "target_name": output_prefix,
        "feature_columns": X.columns.tolist(),
        "selected_model": best_name,
        "label_classes": sorted(y.unique().tolist()),
        "notes": dataset_name,
    }, model_path)

    report = classification_report(y_test, pred, output_dict=True, zero_division=0)
    report_path = REPORT_DIR / f"{output_prefix}_classification_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    metadata_path = REPORT_DIR / f"{output_prefix}_run_info.json"
    metadata_path.write_text(json.dumps({
        "dataset": dataset_name,
        "rows_used": int(len(X)),
        "feature_columns": X.columns.tolist(),
        "target_classes": sorted(y.unique().tolist()),
        "selected_model_by_cv_macro_f1": best_name,
        "selected_model_cv_macro_f1_mean": float(best_row["cv_macro_f1_mean"]),
        "selected_model_test_macro_f1": float(best_row["test_macro_f1"]),
        "selected_model_test_accuracy": float(best_row["test_accuracy"]),
        "model_file": str(model_path),
        "comparison_file": str(comparison_path),
        "sklearn_version": sklearn.__version__,
    }, indent=2), encoding="utf-8")

    print(f"\nBest model for {dataset_name}: {best_name}")
    print(f"Saved model: {model_path}")
    print(f"Saved comparison: {comparison_path}")
    print(f"Saved classification report: {report_path}\n")
    return comparison


def train_app_aligned_model():
    csv_path = DATA_DIR / "synthetic_msme_assessments.csv"
    if not csv_path.exists():
        print(f"SKIP app-aligned model: file not found: {csv_path}")
        return None

    df = pd.read_csv(csv_path)
    if "archetype" not in df.columns:
        print("SKIP app-aligned model: synthetic dataset has no 'archetype' column.")
        return None

    question_cols = [
        c for c in df.columns
        if c.startswith(("infra_", "process_", "people_", "data_", "security_"))
    ]
    if not question_cols:
        print("SKIP app-aligned model: no assessment question columns found.")
        return None

    # Only use columns the app can plausibly supply at prediction time.
    meta_cols = [c for c in ["enterprise_size", "sector", "language"] if c in df.columns]
    X = df[meta_cols + question_cols].copy()
    y = df["archetype"].copy()

    # Numeric assessment answers; invalid/missing responses become missing and
    # are imputed within each training fold by the sklearn pipeline.
    for col in question_cols:
        X[col] = pd.to_numeric(X[col], errors="coerce")
        X.loc[~X[col].between(0, 4), col] = np.nan

    print("\n=== APP-ALIGNED SYNTHETIC MODEL ===")
    print("Rows:", len(df), "| Question features:", len(question_cols), "| Metadata:", meta_cols)
    print("Archetype counts:\n", y.value_counts().to_string())
    result = train_and_compare(
        dataset_name="Synthetic assessment data (labels are generated archetypes)",
        X=X, y=y, output_prefix="app_archetype_classifier",
        scale_numeric=True, cv_splits=5,
    )
    return result


def train_world_bank_model():
    dta_path = PROJECT_ROOT / "database" / "fat0_raw_data_qje.dta"
    if not dta_path.exists():
        print(f"SKIP World Bank model: file not found: {dta_path}")
        return None

    try:
        import pyreadstat
    except ImportError:
        print("SKIP World Bank model: install pyreadstat with `py -m pip install pyreadstat`.")
        return None

    df, metadata = pyreadstat.read_dta(dta_path)
    target = "db8a3"  # Adopted - Business Administration - Mobile Apps or Digital Platform
    feature_cols = [
        "country", "a5a", "s7", "b5a", "b4a",
        "db8a2", "db8a4", "db9a5", "db14a5",
    ]
    missing_cols = [c for c in [target] + feature_cols if c not in df.columns]
    if missing_cols:
        print("SKIP World Bank model: missing columns:", missing_cols)
        return None

    # Keep the real survey's target separate from synthetic archetype labels.
    # Do not use sampling weights as a predictor. They can be used later for
    # survey-weighted estimates; they are not ordinary business attributes.
    work = df[feature_cols + [target]].copy()
    work[target] = pd.to_numeric(work[target], errors="coerce")
    work = work[work[target].isin([0, 1])].copy()
    y = work[target].astype(int).map({0: "not_adopted", 1: "adopted"})

    # Treat negative survey special codes as missing, not real numeric values.
    for col in ["b4a", "s7", "a5a", "b5a", "db8a2", "db8a4", "db9a5", "db14a5"]:
        work[col] = pd.to_numeric(work[col], errors="coerce")
        work.loc[work[col] < 0, col] = np.nan

    # Categoricals: country, sector and binary/survey-coded responses.
    X = work[feature_cols].copy()
    for col in ["country", "a5a", "b5a", "db8a2", "db8a4", "db9a5", "db14a5"]:
        X[col] = X[col].astype("object").where(X[col].notna(), np.nan).astype(str)
        X.loc[X[col].isin(["nan", "None"]), col] = np.nan

    print("\n=== WORLD BANK REAL-SURVEY MODEL ===")
    print("Target:", target, "-", metadata.column_names_to_labels.get(target, "Adoption target"))
    print("Usable target rows:", len(work))
    print("Target counts:\n", y.value_counts().to_string())
    print("Features:", feature_cols)
    result = train_and_compare(
        dataset_name="World Bank FAT survey; target is db8a3 adoption",
        X=X, y=y, output_prefix="world_bank_db8a3_adoption",
        scale_numeric=True, cv_splits=5,
    )
    return result


def main():
    print("Python ML training run")
    print("scikit-learn:", sklearn.__version__)
    print("Output folder:", MODEL_DIR)
    all_results = []

    for train_func in [train_app_aligned_model, train_world_bank_model]:
        try:
            result = train_func()
            if result is not None:
                all_results.append(result)
        except Exception as exc:
            print(f"\nERROR while running {train_func.__name__}: {exc}")

    if all_results:
        combined = pd.concat(all_results, ignore_index=True)
        combined.to_csv(REPORT_DIR / "all_model_comparisons.csv", index=False)
        print("\n=== DONE ===")
        print("Combined comparison:", REPORT_DIR / "all_model_comparisons.csv")
        print("App model and World Bank model remain separate.")
        print("Do not interpret synthetic-data metrics as real-world validation.")
    else:
        print("\nNo models were trained. Check file paths and dependencies.")


if __name__ == "__main__":
    main()
