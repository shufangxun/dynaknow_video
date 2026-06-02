#!/usr/bin/env python3
"""Filter JSONL records by IDs from CSV or JSONL."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_ids(path: Path, id_field: str, require_empty_error: bool) -> list[str]:
    ids = []
    if path.suffix == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                if require_empty_error and record.get("error"):
                    continue
                item_id = record.get(id_field, "")
                if item_id:
                    ids.append(item_id)
        return ids

    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if require_empty_error and row.get("error"):
                continue
            item_id = row.get(id_field, "")
            if item_id:
                ids.append(item_id)
    return ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--ids-from", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--record-id-field", default="video_id")
    parser.add_argument("--ids-field", default="video_id")
    parser.add_argument("--require-empty-error", action="store_true")
    args = parser.parse_args()

    ordered_ids = read_ids(args.ids_from, args.ids_field, args.require_empty_error)
    wanted = set(ordered_ids)
    records = {}
    with args.input.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            item_id = record.get(args.record_id_field, "")
            if item_id in wanted:
                records[item_id] = record

    args.output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with args.output.open("w", encoding="utf-8") as handle:
        for item_id in ordered_ids:
            record = records.get(item_id)
            if not record:
                continue
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            written += 1

    print(f"wrote {written} records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
