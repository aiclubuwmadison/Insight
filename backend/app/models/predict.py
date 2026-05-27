"""Model loading and inference for Insight's algorithm classifier."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.core.ast_features import FEATURE_KEYS

MODEL_PATH = Path(__file__).with_name("algorithm_classifier.pkl")
DEFAULT_CONFIDENCE_THRESHOLD = 0.75


@lru_cache(maxsize=1)
def _load_model_bundle() -> dict[str, Any] | None:
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def predict_algorithm(features: dict[str, float], threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> dict[str, Any]:
    """
    Return an algorithm prediction. Falls back to unknown when the model is absent
    or confidence is below the threshold.
    """
    bundle = _load_model_bundle()
    if bundle is None:
        return {
            "label": "unknown",
            "confidence": 0.0,
            "model_available": False,
            "reason": "algorithm_classifier.pkl not found; run backend/app/models/train_model.py",
        }

    model = bundle["model"]
    feature_keys = bundle.get("feature_keys", FEATURE_KEYS)
    row = pd.DataFrame([{key: features.get(key, 0.0) for key in feature_keys}])

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(row)[0]
        class_index = int(probabilities.argmax())
        label = str(model.classes_[class_index])
        confidence = float(probabilities[class_index])
    else:
        label = str(model.predict(row)[0])
        confidence = 1.0

    if confidence < threshold:
        return {
            "label": "unknown",
            "raw_label": label,
            "confidence": confidence,
            "model_available": True,
            "reason": f"confidence below threshold {threshold}",
        }

    return {
        "label": label,
        "confidence": confidence,
        "model_available": True,
        "reason": "confident local classification",
    }
