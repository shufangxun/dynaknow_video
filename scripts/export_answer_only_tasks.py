#!/usr/bin/env python3
"""Export answer-only leakage tasks from DynaKnow sample JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with args.input.open("r", encoding="utf-8") as src, args.output.open("w", encoding="utf-8") as dst:
        for line in src:
            if not line.strip():
                continue
            sample = json.loads(line)
            task = {
                "video_id": sample["video_id"],
                "mode": "answer_only",
                "question": sample["question"],
                "choices": sample["choices"],
                "gold_answer": sample["answer"],
                "instruction": "Answer using only the question and choices. If the answer cannot be inferred without the video, return uncertain.",
            }
            dst.write(json.dumps(task, ensure_ascii=False) + "\n")
            count += 1
    print(f"wrote {count} answer-only tasks to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

