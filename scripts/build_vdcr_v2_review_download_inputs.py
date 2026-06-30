#!/usr/bin/env python3
"""Build small resolver input CSVs from the V2 review queue."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FIELDS = [
    "candidate_id",
    "source_url",
    "source_platform",
    "raw_duration_sec",
    "candidate_knowledge_point",
    "domain_seed",
    "review_status",
    "repeat_concept_rank",
    "source_csv",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in FIELDS} for row in rows])


def duration(row: dict[str, str]) -> float:
    try:
        return float(row.get("raw_duration_sec", "") or 0)
    except ValueError:
        return 0.0


def platform_key(row: dict[str, str]) -> str:
    platform = row.get("source_platform", "").casefold().replace(" ", "_")
    if "archive" in platform:
        return "archive"
    if "wikimedia" in platform or "commons" in platform:
        return "commons"
    return platform


def sort_key(row: dict[str, str]) -> tuple[int, int, float, str]:
    status_rank = {"review": 0, "revise": 1, "": 2}
    local_rank = 1 if row.get("local_media") else 0
    return (
        status_rank.get(row.get("review_status", ""), 9),
        local_rank,
        duration(row) if duration(row) > 0 else 9999.0,
        row.get("candidate_id", ""),
    )


def select_rows(rows: list[dict[str, str]], max_duration_sec: float, limit: int) -> list[dict[str, str]]:
    selected = [
        row
        for row in rows
        if row.get("review_status", "") == "review"
        and not row.get("local_media")
        and duration(row) > 0
        and (max_duration_sec <= 0 or duration(row) <= max_duration_sec)
        and platform_key(row) in {"archive", "commons"}
    ]
    selected.sort(key=sort_key)
    if limit > 0:
        selected = selected[:limit]
    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-queue", type=Path, default=Path("data/vdcr_v2_review_queue.csv"))
    parser.add_argument("--output-prefix", type=Path, default=Path("data/vdcr_v2_review_download_input"))
    parser.add_argument("--max-duration-sec", type=float, default=120.0)
    parser.add_argument("--limit", type=int, default=48)
    args = parser.parse_args()

    selected = select_rows(read_csv(args.review_queue), args.max_duration_sec, args.limit)
    groups = {"archive": [], "commons": []}
    for row in selected:
        groups[platform_key(row)].append(row)

    for key, rows in groups.items():
        write_csv(args.output_prefix.with_name(f"{args.output_prefix.name}_{key}.csv"), rows)

    print(f"selected_rows={len(selected)}")
    print("platforms", dict(Counter(platform_key(row) for row in selected)))
    print("domains", dict(Counter(row.get("domain_seed", "") for row in selected)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
