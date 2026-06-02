#!/usr/bin/env python3
"""Create a compact first-pass review sheet from the prioritized queue."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


OUTPUT_FIELDS = [
    "candidate_id",
    "source_url",
    "raw_duration_sec",
    "suggested_start_sec",
    "suggested_end_sec",
    "initial_category",
    "candidate_knowledge_point",
    "why_dynamic",
    "priority_score",
    "review_flags",
    "video_available",
    "dynamic_process_visible",
    "knowledge_point_supported",
    "single_frame_likely_sufficient",
    "title_or_subtitle_leakage_risk",
    "first_pass_decision",
    "reviewer_notes",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))[: args.limit]

    output_rows = []
    for row in rows:
        flags = row.get("review_flags", "")
        notes = row.get("collector_notes", "").lower()
        leakage_risk = "yes" if "title may leak" in notes or "caption may leak" in notes else ""
        output_rows.append(
            {
                "candidate_id": row.get("candidate_id", ""),
                "source_url": row.get("source_url", ""),
                "raw_duration_sec": row.get("raw_duration_sec", ""),
                "suggested_start_sec": row.get("suggested_start_sec", ""),
                "suggested_end_sec": row.get("suggested_end_sec", ""),
                "initial_category": row.get("initial_category", ""),
                "candidate_knowledge_point": row.get("candidate_knowledge_point", ""),
                "why_dynamic": row.get("why_dynamic", ""),
                "priority_score": row.get("priority_score", ""),
                "review_flags": flags,
                "video_available": "",
                "dynamic_process_visible": "",
                "knowledge_point_supported": "",
                "single_frame_likely_sufficient": "",
                "title_or_subtitle_leakage_risk": leakage_risk,
                "first_pass_decision": "",
                "reviewer_notes": "",
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"wrote {len(output_rows)} first-pass review rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

