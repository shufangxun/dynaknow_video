#!/usr/bin/env python3
"""Merge CSV files with compatible headers and deduplicate by a key."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--key", default="source_url")
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()

    rows = []
    seen = set()
    fieldnames: list[str] | None = None
    for path in args.inputs:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if fieldnames is None:
                fieldnames = reader.fieldnames or []
            for row in reader:
                key = row.get(args.key, "")
                if not key or key in seen:
                    continue
                seen.add(key)
                rows.append({field: row.get(field, "") for field in fieldnames})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames or [])
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
