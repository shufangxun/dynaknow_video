#!/usr/bin/env python3
"""Validate prediction coverage against a DynaKnow gold file."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


VALID = {"A", "B", "C", "D"}


def read_keys(path: Path) -> set[tuple[str, str]]:
    keys = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            keys.add((row["video_id"], row.get("mode", "full_video")))
    return keys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    args = parser.parse_args()

    gold_keys = read_keys(args.gold)
    pred_keys = []
    invalid_answers = []
    with args.predictions.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            key = (row.get("video_id", ""), row.get("mode", "full_video"))
            pred_keys.append(key)
            if row.get("predicted_answer") not in VALID:
                invalid_answers.append((line_no, row.get("predicted_answer")))

    pred_counter = Counter(pred_keys)
    pred_set = set(pred_keys)
    missing = sorted(gold_keys - pred_set)
    extra = sorted(pred_set - gold_keys)
    duplicates = sorted(key for key, count in pred_counter.items() if count > 1)

    print(f"gold_rows={len(gold_keys)} prediction_rows={len(pred_keys)}")
    print(f"missing={len(missing)} extra={len(extra)} duplicates={len(duplicates)} invalid_answers={len(invalid_answers)}")
    if missing[:20]:
        print("missing_examples=" + ", ".join(f"{vid}/{mode}" for vid, mode in missing[:20]))
    if extra[:20]:
        print("extra_examples=" + ", ".join(f"{vid}/{mode}" for vid, mode in extra[:20]))
    if duplicates[:20]:
        print("duplicate_examples=" + ", ".join(f"{vid}/{mode}" for vid, mode in duplicates[:20]))
    if invalid_answers[:20]:
        print("invalid_answer_examples=" + ", ".join(f"line {line}: {ans}" for line, ans in invalid_answers[:20]))

    return 0 if not (missing or extra or duplicates or invalid_answers) else 1


if __name__ == "__main__":
    raise SystemExit(main())
