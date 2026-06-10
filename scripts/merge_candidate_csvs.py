#!/usr/bin/env python3
"""Merge DynaKnow candidate CSV files and deduplicate by source_url."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = [
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


def read_rows(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    for path in paths:
        with path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                url = row.get("source_url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                rows.append({key: row.get(key, "") for key in FIELDNAMES})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()

    rows = read_rows(args.inputs)
    for idx, row in enumerate(rows, start=1):
        row["candidate_id"] = f"candidate_{idx:06d}"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} deduplicated rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
