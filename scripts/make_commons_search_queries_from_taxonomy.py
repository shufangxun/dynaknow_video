#!/usr/bin/env python3
"""Expand taxonomy search queries into Commons file-search rows."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = [
    "search_term",
    "initial_category",
    "candidate_knowledge_point",
    "default_start_sec",
    "default_end_sec",
    "why_dynamic",
    "notes",
]

DEFAULT_START = "0"
DEFAULT_END = "60"


def dynamic_hint(point: str) -> str:
    return f"The video should visibly show the temporal process for: {point}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-points", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-per-point", type=int, default=3)
    args = parser.parse_args()

    rows = []
    seen = set()
    with args.knowledge_points.open("r", encoding="utf-8", newline="") as handle:
        for kp in csv.DictReader(handle):
            point = kp["knowledge_point"].strip()
            category = kp["category"].strip()
            for query in kp.get("search_queries", "").split("|")[: args.max_per_point]:
                query = query.strip()
                if not query:
                    continue
                key = (query.lower(), point)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "search_term": query,
                        "initial_category": category,
                        "candidate_knowledge_point": point,
                        "default_start_sec": DEFAULT_START,
                        "default_end_sec": DEFAULT_END,
                        "why_dynamic": dynamic_hint(point),
                        "notes": "taxonomy_expanded_v0_6; requires visual review for dynamic evidence and title leakage.",
                    }
                )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} query rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
