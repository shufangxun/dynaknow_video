#!/usr/bin/env python3
"""Reorder choices in a release JSONL to reduce answer-position bias."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


LETTERS = ["A", "B", "C", "D"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = []
    with args.input.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle):
            if not line.strip():
                continue
            row = json.loads(line)
            old_answer = row["answer"]
            correct_text = row["choices"][old_answer]
            distractors = [row["choices"][letter] for letter in LETTERS if letter != old_answer]
            target_idx = idx % 4
            options = distractors[:]
            options.insert(target_idx, correct_text)
            row["choices"] = {letter: options[pos] for pos, letter in enumerate(LETTERS)}
            row["answer"] = LETTERS[target_idx]
            rows.append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"wrote {len(rows)} rebalanced records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
