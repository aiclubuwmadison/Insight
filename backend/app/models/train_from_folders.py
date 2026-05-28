"""Train Insight's local algorithm classifier from folder-labeled Python examples.

Expected data layout, relative to backend/:

    data/algorithm_examples/
        binary_search/*.py
        bfs/*.py
        dfs/*.py
        dynamic_programming/*.py
        hash_map/*.py
        sliding_window/*.py
        sorting/*.py
        stack/*.py
        two_pointers/*.py
        unknown/*.py

Run from backend/:

    python -m app.models.train_from_folders
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from app.core.ast_features import extract_ast_features
from app.core.parser import parse_code

BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data" / "algorithm_examples"
MODEL_PATH = Path(__file__).resolve().parent / "algorithm_classifier.pkl"
METRICS_PATH = Path(__file__).resolve().parent / "algorithm_classifier_metrics.json"

SUPPORTED_LABELS = {
    "binary_search",
    "bfs",
    "dfs",
    "dynamic_programming",
    "hash_map",
    "sliding_window",
    "sorting",
    "stack",
    "two_pointers",
    "unknown",
}


def _load_examples(data_dir: Path = DATA_DIR) -> list[dict[str, Any]]:
    if not data_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {data_dir}")

    rows: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for label_dir in sorted(data_dir.iterdir()):
        if not label_dir.is_dir():
            continue

        label = label_dir.name
        if label not in SUPPORTED_LABELS:
            print(f"Skipping unsupported label folder: {label}")
            continue

        for path in sorted(label_dir.glob("*.py")):
            code = path.read_text(encoding="utf-8")
            try:
                tree = parse_code(code, "python")
                features = extract_ast_features(tree.root_node, code)
            except Exception as exc:  # keep training robust to a bad sample
                skipped.append({"path": str(path), "error": str(exc)})
                continue

            rows.append({
                "label": label,
                "path": str(path.relative_to(BACKEND_DIR)),
                **features,
            })

    if skipped:
        print(f"Skipped {len(skipped)} examples due to parse/feature errors")
        for item in skipped[:10]:
            print(f"  - {item['path']}: {item['error']}")

    if not rows:
        raise RuntimeError(f"No usable examples found in {data_dir}")

    return rows


def train() -> None:
    rows = _load_examples()
    df = pd.DataFrame(rows)

    feature_columns = [
        col for col in df.columns
        if col not in {"label", "path"}
    ]

    X = df[feature_columns]
    y = df["label"]

    label_counts = y.value_counts().sort_index().to_dict()
    min_class_count = min(label_counts.values())
    num_classes = len(label_counts)

    # Stratified split is useful once every class has enough examples.
    # The fallback keeps the script usable for tiny starter datasets too.
    use_split = len(df) >= num_classes * 3 and min_class_count >= 3

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=None,
        min_samples_leaf=1,
        class_weight="balanced",
        random_state=42,
    )

    metrics: dict[str, Any] = {
        "total_examples": int(len(df)),
        "label_counts": {k: int(v) for k, v in label_counts.items()},
        "feature_columns": feature_columns,
    }

    if use_split:
        x_train, x_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)

        metrics["held_out_accuracy"] = float(accuracy_score(y_test, y_pred))
        metrics["classification_report"] = classification_report(
            y_test,
            y_pred,
            output_dict=True,
            zero_division=0,
        )
        metrics["confusion_matrix"] = confusion_matrix(
            y_test,
            y_pred,
            labels=sorted(label_counts),
        ).tolist()
        metrics["confusion_matrix_labels"] = sorted(label_counts)

        print(f"Held-out accuracy: {metrics['held_out_accuracy']:.3f}")

        # Retrain final model on all examples after evaluation.
        model.fit(X, y)
    else:
        model.fit(X, y)
        metrics["held_out_accuracy"] = None
        print("Skipped held-out split because the dataset is too small")

    payload = {
        "model": model,
        "feature_columns": feature_columns,
        "labels": sorted(label_counts),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Trained classifier on {len(df)} examples across {len(label_counts)} classes")
    print("Label counts:")
    for label, count in label_counts.items():
        print(f"  {label}: {count}")
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")


if __name__ == "__main__":
    train()
