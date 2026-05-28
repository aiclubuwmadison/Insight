import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any

from app.gemini.gemini_client import get_gemini_explanation
from app.services.analyze import _try_local_algorithm_analysis


BACKEND_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = BACKEND_ROOT / "data" / "algorithm_examples"
RESULTS_PATH = Path(__file__).resolve().parent / "benchmark_results.json"


def read_examples(dataset_dir: Path, limit_per_label: int) -> list[dict[str, str]]:
    examples = []

    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    for label_dir in sorted(dataset_dir.iterdir()):
        if not label_dir.is_dir():
            continue

        label = label_dir.name
        files = sorted(label_dir.glob("*.py"))[:limit_per_label]

        for file_path in files:
            examples.append(
                {
                    "label": label,
                    "path": str(file_path),
                    "code": file_path.read_text(encoding="utf-8"),
                    "language": "python",
                }
            )

    return examples


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None

    sorted_values = sorted(values)
    index = int(round((p / 100) * (len(sorted_values) - 1)))
    return sorted_values[index]


def summarize_latencies(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {
            "count": 0,
            "min_ms": None,
            "median_ms": None,
            "mean_ms": None,
            "p90_ms": None,
            "max_ms": None,
        }

    return {
        "count": len(values),
        "min_ms": round(min(values), 3),
        "median_ms": round(statistics.median(values), 3),
        "mean_ms": round(statistics.mean(values), 3),
        "p90_ms": round(percentile(values, 90), 3),
        "max_ms": round(max(values), 3),
    }


def benchmark_local_classifier(
    examples: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[float]]:
    results = []
    latencies = []

    for example in examples:
        start = time.perf_counter()

        local_result = _try_local_algorithm_analysis(
            code=example["code"],
            language=example["language"],
        )

        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

        if local_result is None:
            predicted_label = None
            confidence = None
            gemini_skipped = False
        else:
            predicted_label = local_result.get("algorithm")
            confidence = local_result.get("confidence")
            gemini_skipped = local_result.get("gemini_used") is False

        results.append(
            {
                "expected_label": example["label"],
                "predicted_label": predicted_label,
                "confidence": confidence,
                "gemini_skipped": gemini_skipped,
                "correct": (
                    predicted_label == example["label"]
                    if example["label"] != "unknown"
                    else local_result is None
                ),
                "latency_ms": round(elapsed_ms, 3),
                "path": example["path"],
            }
        )

    return results, latencies


def benchmark_gemini(
    examples: list[dict[str, str]],
    gemini_limit: int,
) -> tuple[list[dict[str, Any]], list[float]]:
    """
    Optional benchmark.

    This makes real Gemini API calls, so it can be slow and may use quota.
    Keep gemini_limit small.
    """
    results = []
    latencies = []

    for example in examples[:gemini_limit]:
        start = time.perf_counter()

        try:
            response = get_gemini_explanation(
                code=example["code"],
                language=example["language"],
                source="benchmark",
            )
            error = None
        except Exception as exc:
            response = None
            error = str(exc)

        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

        results.append(
            {
                "expected_label": example["label"],
                "latency_ms": round(elapsed_ms, 3),
                "success": response is not None and error is None,
                "error": error,
                "path": example["path"],
            }
        )

    return results, latencies


def build_summary(
    local_results: list[dict[str, Any]],
    local_latencies: list[float],
    gemini_results: list[dict[str, Any]] | None,
    gemini_latencies: list[float] | None,
) -> dict[str, Any]:
    total = len(local_results)

    skipped_count = sum(1 for result in local_results if result["gemini_skipped"])
    fallback_count = total - skipped_count

    correct_predictions = sum(1 for result in local_results if result["correct"])

    known_results = [
        result for result in local_results if result["expected_label"] != "unknown"
    ]
    known_skipped_count = sum(1 for result in known_results if result["gemini_skipped"])

    summary: dict[str, Any] = {
        "total_examples": total,
        "local_classifier": {
            "latency": summarize_latencies(local_latencies),
            "skip_count": skipped_count,
            "fallback_count": fallback_count,
            "skip_rate": round(skipped_count / total, 4) if total else 0,
            "accuracy_against_folder_labels": (
                round(correct_predictions / total, 4) if total else 0
            ),
            "known_algorithm_skip_rate": (
                round(known_skipped_count / len(known_results), 4)
                if known_results
                else 0
            ),
        },
    }

    if gemini_results is not None and gemini_latencies is not None:
        successful_gemini = [result for result in gemini_results if result["success"]]

        summary["gemini_direct"] = {
            "latency": summarize_latencies(gemini_latencies),
            "attempted_calls": len(gemini_results),
            "successful_calls": len(successful_gemini),
        }

        if local_latencies and gemini_latencies:
            local_median = statistics.median(local_latencies)
            gemini_median = statistics.median(gemini_latencies)

            if gemini_median > 0:
                reduction = (gemini_median - local_median) / gemini_median
                summary["estimated_median_latency_reduction_vs_gemini"] = round(
                    reduction,
                    4,
                )

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark Insight's local algorithm classifier."
    )

    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=DATASET_DIR,
        help="Path to backend/data/algorithm_examples",
    )

    parser.add_argument(
        "--limit-per-label",
        type=int,
        default=10,
        help="Number of examples to benchmark per label.",
    )

    parser.add_argument(
        "--include-gemini",
        action="store_true",
        help="Also benchmark direct Gemini calls. This uses real API quota.",
    )

    parser.add_argument(
        "--gemini-limit",
        type=int,
        default=10,
        help="Maximum number of Gemini calls when --include-gemini is enabled.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS_PATH,
        help="Where to save benchmark JSON results.",
    )

    args = parser.parse_args()

    examples = read_examples(args.dataset_dir, args.limit_per_label)

    print(f"Loaded {len(examples)} examples from {args.dataset_dir}")
    print("Benchmarking local classifier...")

    local_results, local_latencies = benchmark_local_classifier(examples)

    gemini_results = None
    gemini_latencies = None

    if args.include_gemini:
        print(
            f"Benchmarking Gemini directly on {args.gemini_limit} examples. "
            "This may use API quota..."
        )
        gemini_results, gemini_latencies = benchmark_gemini(
            examples=examples,
            gemini_limit=args.gemini_limit,
        )

    summary = build_summary(
        local_results=local_results,
        local_latencies=local_latencies,
        gemini_results=gemini_results,
        gemini_latencies=gemini_latencies,
    )

    output_payload = {
        "summary": summary,
        "local_results": local_results,
        "gemini_results": gemini_results or [],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output_payload, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"Saved benchmark results to {args.output}")


if __name__ == "__main__":
    main()
