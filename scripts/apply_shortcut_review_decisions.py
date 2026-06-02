#!/usr/bin/env python3
"""Apply compact shortcut-review decisions to a full review sheet."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DECISION_FIELDS = [
    "video_id",
    "answer_only_leakage",
    "visible_text_or_overlay",
    "ocr_leakage_status",
    "single_frame_sufficient",
    "sparse_frames_sufficient",
    "dynamic_knowledge_supported",
    "decision",
    "review_notes",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with args.decisions.open("r", encoding="utf-8", newline="") as handle:
        decisions = {row["video_id"]: row for row in csv.DictReader(handle)}

    with args.review.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        rows = []
        for row in reader:
            decision = decisions.get(row["video_id"])
            if decision:
                for field in DECISION_FIELDS[1:]:
                    row[field] = decision.get(field, row.get(field, ""))
            rows.append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"applied {len(decisions)} decisions to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
