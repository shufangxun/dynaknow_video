#!/usr/bin/env python3
"""Summarize human shortcut review CSV."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("review", type=Path)
    args = parser.parse_args()

    with args.review.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    print(f"rows: {len(rows)}")
    for key in ["answer_only_leakage", "single_frame_sufficient", "sparse_frames_sufficient", "decision"]:
        counts = Counter(row[key] for row in rows)
        print(f"{key}:")
        for value, count in counts.most_common():
            print(f"  {value}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

