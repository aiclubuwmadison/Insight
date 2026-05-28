"""Import LeetCode-style CSV rows into Insight's folder-labeled training dataset.

This is optional. It lets you extend data/algorithm_examples with public datasets
that contain solution code plus topic tags.

Example:
    python -m app.models.import_leetcode_csv \
      --csv ~/Downloads/leetcode_solutions.csv \
      --code-column python_code \
      --tags-column tags \
      --title-column title
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

TAG_TO_LABEL = [
    ("binary search", "binary_search"),
    ("breadth-first search", "bfs"),
    ("bfs", "bfs"),
    ("depth-first search", "dfs"),
    ("dfs", "dfs"),
    ("dynamic programming", "dynamic_programming"),
    ("hash table", "hash_map"),
    ("hash map", "hash_map"),
    ("sliding window", "sliding_window"),
    ("sorting", "sorting"),
    ("sort", "sorting"),
    ("stack", "stack"),
    ("two pointers", "two_pointers"),
]


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "example"


def choose_label(tags: str) -> str | None:
    normalized = str(tags).lower()
    for tag, label in TAG_TO_LABEL:
        if tag in normalized:
            return label
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--code-column", required=True)
    parser.add_argument("--tags-column", required=True)
    parser.add_argument("--title-column", default=None)
    parser.add_argument("--output-dir", default="backend/data/algorithm_examples")
    parser.add_argument("--limit-per-label", type=int, default=200)
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    written = 0

    for idx, row in df.iterrows():
        code = row.get(args.code_column)
        tags = row.get(args.tags_column)
        if not isinstance(code, str) or not code.strip():
            continue

        label = choose_label(str(tags))
        if label is None:
            continue

        if counts.get(label, 0) >= args.limit_per_label:
            continue

        title = str(row.get(args.title_column, f"row_{idx}")) if args.title_column else f"row_{idx}"
        label_dir = output_dir / label
        label_dir.mkdir(parents=True, exist_ok=True)
        path = label_dir / f"imported_{slugify(title)}_{counts.get(label, 0):04d}.py"
        path.write_text(code.strip() + "\n", encoding="utf-8")
        counts[label] = counts.get(label, 0) + 1
        written += 1

    print(f"Wrote {written} examples")
    for label, count in sorted(counts.items()):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
