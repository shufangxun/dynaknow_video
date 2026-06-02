#!/usr/bin/env python3
"""Generate simple baseline predictions for DynaKnow tasks."""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path


LETTERS = ["A", "B", "C", "D"]


def read_tasks(path: Path, answer_field: str) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                if "mode" not in row:
                    row["mode"] = "full_video"
                if answer_field not in row and "gold_answer" in row:
                    row[answer_field] = row["gold_answer"]
                rows.append(row)
    return rows


def choose_prediction(row: dict, baseline: str, answer_field: str, majority_answer: str, rng: random.Random) -> str:
    if baseline == "oracle":
        return row[answer_field]
    if baseline == "always_a":
        return "A"
    if baseline == "majority":
        return majority_answer
    if baseline == "random":
        return rng.choice(LETTERS)
    raise ValueError(f"unknown baseline: {baseline}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--baseline", choices=["oracle", "always_a", "majority", "random"], default="oracle")
    parser.add_argument("--answer-field", default="answer")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rows = read_tasks(args.tasks, args.answer_field)
    answer_counts = Counter(row[args.answer_field] for row in rows)
    majority_answer = answer_counts.most_common(1)[0][0] if answer_counts else "A"
    rng = random.Random(args.seed)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            prediction = {
                "video_id": row["video_id"],
                "mode": row.get("mode", "full_video"),
                "predicted_answer": choose_prediction(row, args.baseline, args.answer_field, majority_answer, rng),
                "baseline": args.baseline,
            }
            handle.write(json.dumps(prediction, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(f"wrote {len(rows)} {args.baseline} predictions to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
