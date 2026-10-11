"""
Optional ML "profile match" for the report.

Loads your trained archetype classifier (the .joblib file) and predicts which
archetype the business's 25 answers most resemble.

RULES
- It NEVER changes the maturity score, level or gaps (scoring.py still does that).
- The model was trained on SYNTHETIC data, so the report labels it "Experimental".
- predict_archetype() never raises. If the model file, scikit-learn, or the
  answers are missing/invalid it returns None and the report is built without it.
- scikit-learn is only imported when a prediction is made.

Check your model from the command line (inside AI-models):
    py ml_insights.py
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Checked in this order. Set ARCHETYPE_MODEL_PATH to use a different file.
MODEL_CANDIDATES = [
    os.environ.get("ARCHETYPE_MODEL_PATH"),
    os.path.join(BASE_DIR, "models", "app_archetype_classifier_best.joblib"),
    os.path.join(BASE_DIR, "models", "archetype_classifier.joblib"),
]

QUESTION_PREFIXES = ("infra_", "process_", "people_", "data_", "security_")

_cache = {"loaded": False, "pipeline": None, "columns": None, "bare": False, "path": None, "cats": None}


def _find_model_path():
    return next((p for p in MODEL_CANDIDATES if p and os.path.exists(p)), None)


def _load():
    """Load the model once. Returns (pipeline, feature_columns) or (None, None)."""
    if _cache["loaded"]:
        return _cache["pipeline"], _cache["columns"]
    _cache["loaded"] = True

    path = _find_model_path()
    if path is None:
        return None, None

    try:
        import joblib

        obj = joblib.load(path)
        # train_project_models.py saves a dict; train_model.py saves a bare Pipeline.
        if isinstance(obj, dict):
            pipeline, columns, bare = obj["pipeline"], list(obj["feature_columns"]), False
        else:
            pipeline, columns, bare = obj, list(getattr(obj, "feature_names_in_", [])), True
        if not columns:
            return None, None
        _cache.update(pipeline=pipeline, columns=columns, bare=bare, path=path)
    except Exception as exc:  # corrupt file, sklearn version mismatch, sklearn missing...
        print("ml_insights: could not load model:", exc)
        return None, None

    return _cache["pipeline"], _cache["columns"]


def _known_categories():
    """{column: [values the model saw in training]} for the text columns."""
    if _cache["cats"] is not None:
        return _cache["cats"]
    cats = {}
    try:
        pre = _cache["pipeline"].named_steps["preprocessor"]
        for _name, trans, cols in pre.transformers_:
            enc = trans if hasattr(trans, "categories_") else getattr(trans, "named_steps", {}).get("onehot")
            if enc is not None and hasattr(enc, "categories_"):
                for col, values in zip(cols, enc.categories_):
                    cats[col] = [str(v) for v in values]
    except Exception:
        pass
    _cache["cats"] = cats
    return cats


def _match_category(column, value):
    """Use the model's own spelling, e.g. 'micro' -> 'Micro' if that is what it learned."""
    if value is None:
        return None
    known = _known_categories().get(column)
    if known:
        for k in known:
            if k.lower() == str(value).strip().lower():
                return k
    return value


def _clean_answer(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if 0 <= number <= 4 else None  # same rule as the training script


def predict_archetype(responses, business_type=None, sector=None, language=None):
    """
    responses: dict like {"infra_1": 3, ..., "security_5": 1}  (all 25 answers)
    Returns {"archetype", "confidence", "alternatives"} or None.
    """
    try:
        if not isinstance(responses, dict):
            return None

        pipeline, columns = _load()
        if pipeline is None:
            return None

        question_cols = [c for c in columns if c.startswith(QUESTION_PREFIXES)]
        answers = {c: _clean_answer(responses.get(c)) for c in question_cols}
        if not question_cols or any(v is None for v in answers.values()):
            return None  # never guess from partial or invalid answers

        import numpy as np
        import pandas as pd

        missing = "Unknown" if _cache["bare"] else np.nan
        meta = {
            "enterprise_size": _match_category("enterprise_size", business_type) or missing,
            "sector": _match_category("sector", sector) or missing,
            "language": _match_category("language", language) or missing,
        }

        row = {c: (answers[c] if c in answers else meta.get(c, missing)) for c in columns}
        frame = pd.DataFrame([row], columns=columns)

        probabilities = pipeline.predict_proba(frame)[0]
        ranked = sorted(zip(list(pipeline.classes_), probabilities), key=lambda x: x[1], reverse=True)

        return {
            "archetype": str(ranked[0][0]),
            "confidence": round(float(ranked[0][1]) * 100, 1),
            "alternatives": [
                {"archetype": str(n), "confidence": round(float(p) * 100, 1)} for n, p in ranked[1:3]
            ],
        }
    except Exception as exc:
        print("ml_insights: prediction skipped:", exc)
        return None


if __name__ == "__main__":
    pipeline, columns = _load()
    if pipeline is None:
        print("No usable model found. Looked for:")
        for p in MODEL_CANDIDATES:
            if p:
                print("  ", p, "->", "exists" if os.path.exists(p) else "missing")
    else:
        print("Model file :", _cache["path"])
        print("Format     :", "bare Pipeline" if _cache["bare"] else "dict (train_project_models.py)")
        print("Inputs     :", len(columns), "columns")
        print("Classes    :", list(pipeline.classes_))
        for col, values in _known_categories().items():
            print(f"Values the model learned for {col}: {values}")
