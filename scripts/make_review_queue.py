#!/usr/bin/env python3
"""Create a prioritized first-pass review queue from candidate videos."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


INPUT_FIELDS = [
    "candidate_id",
    "source_url",
    "source_platform",
    "license_or_usage_note",
    "raw_duration_sec",
    "suggested_start_sec",
    "suggested_end_sec",
    "initial_category",
    "candidate_knowledge_point",
    "domain_seed",
    "subdomain_seed",
    "why_dynamic",
    "collector_notes",
]

OUTPUT_FIELDS = INPUT_FIELDS + [
    "priority_score",
    "review_flags",
    "first_pass_decision",
    "reviewer_notes",
]

NOISY_TERMS = [
    "broad",
    "noisy",
    "likely narration",
    "weak mapping",
    "possible extension",
    "filter aggressively",
]


def score_row(row: dict[str, str]) -> tuple[int, list[str]]:
    score = 0
    flags: list[str] = []
    try:
        duration = float(row.get("raw_duration_sec", "0") or 0)
    except ValueError:
        duration = 0.0

    if 5 <= duration <= 60:
        score += 4
    elif duration == 0:
        flags.append("missing_duration")
        score -= 1
    elif duration > 60:
        flags.append("needs_trim")
        score += 1
    else:
        flags.append("too_short")
        score -= 1

    notes = (row.get("collector_notes", "") + " " + row.get("why_dynamic", "")).lower()
    if any(term in notes for term in NOISY_TERMS):
        flags.append("noisy_source_or_mapping")
        score -= 2
    if "strong seed" in notes or "high-value" in notes or "good source" in notes:
        score += 2
    if "auto_collected" not in notes:
        score += 1
    if "title may leak" in notes or "caption may leak" in notes:
        flags.append("title_or_caption_leakage_risk")
        score -= 1

    url = row.get("source_url", "")
    if "commons.wikimedia.org/wiki/File:" in url:
        score += 1
    else:
        flags.append("non_commons_or_unusual_url")

    return score, flags


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=80)
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8", newline="") as handle:
        rows = [{key: row.get(key, "") for key in INPUT_FIELDS} for row in csv.DictReader(handle)]

    scored = []
    for row in rows:
        score, flags = score_row(row)
        row["priority_score"] = str(score)
        row["review_flags"] = ";".join(flags)
        row["first_pass_decision"] = ""
        row["reviewer_notes"] = ""
        scored.append(row)

    scored.sort(key=lambda row: (int(row["priority_score"]), row["initial_category"], row["candidate_id"]), reverse=True)
    selected = scored[: args.limit]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(selected)

    print(f"wrote {len(selected)} review rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
