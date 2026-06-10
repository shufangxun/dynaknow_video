#!/usr/bin/env python3
"""Merge VDCR candidate CSV shards and de-duplicate by source URL."""

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
    "source_csv",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def merge(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    seen_ids: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        for row in read_rows(path):
            url = row.get("source_url", "")
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)
            candidate_id = row.get("candidate_id", "")
            if candidate_id and candidate_id in seen_ids:
                stem = path.stem.replace("vdcr_candidate_videos_", "")
                row["candidate_id"] = f"{candidate_id}_{stem}"
            seen_ids.add(row.get("candidate_id", ""))
            output = {field: row.get(field, "") for field in FIELDNAMES}
            output["source_csv"] = str(path)
            rows.append(output)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = merge(args.inputs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"merged_candidates={len(rows)} wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
