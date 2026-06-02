#!/usr/bin/env python3
"""Create a manifest of shortcut-filter runs to execute."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "run_id",
    "shortcut_type",
    "task_file",
    "num_tasks",
    "required_input",
    "status",
    "notes",
]


def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--answer-only", required=True, type=Path)
    parser.add_argument("--frame-shortcut", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = [
        {
            "run_id": "shortcut_answer_only_seed",
            "shortcut_type": "answer_only",
            "task_file": str(args.answer_only),
            "num_tasks": str(count_jsonl(args.answer_only)),
            "required_input": "question_and_choices_only",
            "status": "ready",
            "notes": "Use a strong text-only model or human; accept sample only if answer is not reliably inferable.",
        },
        {
            "run_id": "shortcut_single_frame_seed",
            "shortcut_type": "single_frame",
            "task_file": str(args.frame_shortcut),
            "num_tasks": str(
                sum(
                    1
                    for line in args.frame_shortcut.open("r", encoding="utf-8")
                    if line.strip() and json.loads(line).get("mode", "").startswith("single_frame")
                )
                if args.frame_shortcut.exists()
                else 0
            ),
            "required_input": "one_still_frame_plus_question_and_choices",
            "status": "ready",
            "notes": "Run first/middle/last separately; flag sample if any single frame is sufficient.",
        },
        {
            "run_id": "shortcut_sparse_frames_seed",
            "shortcut_type": "sparse_frames",
            "task_file": str(args.frame_shortcut),
            "num_tasks": str(
                sum(
                    1
                    for line in args.frame_shortcut.open("r", encoding="utf-8")
                    if line.strip() and json.loads(line).get("mode", "").startswith("sparse")
                )
                if args.frame_shortcut.exists()
                else 0
            ),
            "required_input": "sparse_still_frames_plus_question_and_choices",
            "status": "ready",
            "notes": "This is a stricter shortcut; if sparse frames solve it, the item may still be valid only if full temporal ordering is needed.",
        },
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} shortcut run rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

