#!/usr/bin/env python3
"""Import manually curated public video sources into candidate CSV format."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


INPUT_FIELDS = [
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

OUTPUT_FIELDS = [
    "candidate_id",
    *INPUT_FIELDS,
]


def existing_urls(path: Path | None) -> set[str]:
    if not path or not path.exists():
        return set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row.get("source_url", "") for row in csv.DictReader(handle)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument(
        "--skip-existing",
        action="append",
        default=[],
        type=Path,
        help="Existing candidate CSV to use for source_url deduplication. Can be passed multiple times.",
    )
    args = parser.parse_args()

    skip_urls: set[str] = set()
    for path in args.skip_existing:
        skip_urls.update(existing_urls(path))
    rows = []
    next_id = args.start_index
    with args.input.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            url = row.get("source_url", "")
            if not url or url in skip_urls:
                continue
            rows.append(
                {
                    "candidate_id": f"curated_{next_id:06d}",
                    **{field: row.get(field, "") for field in INPUT_FIELDS},
                }
            )
            skip_urls.add(url)
            next_id += 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} curated candidate rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
