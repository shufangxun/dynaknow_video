#!/usr/bin/env python3
"""Filter a media manifest by IDs from a review sheet or JSONL samples."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_ids(path: Path, id_field: str) -> list[str]:
    if path.suffix == ".jsonl":
        ids = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    ids.append(json.loads(line).get(id_field, ""))
        return [item_id for item_id in ids if item_id]

    with path.open("r", encoding="utf-8", newline="") as handle:
        return [row.get(id_field, "") for row in csv.DictReader(handle) if row.get(id_field, "")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--ids-from", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--id-field", default="video_id")
    parser.add_argument("--manifest-id-field", default="id")
    parser.add_argument("--missing-output", type=Path)
    parser.add_argument("--exclude-ids-from", type=Path)
    args = parser.parse_args()

    ordered_ids = read_ids(args.ids_from, args.id_field)
    excluded_ids = set(read_ids(args.exclude_ids_from, args.id_field)) if args.exclude_ids_from else set()
    id_order = {item_id: idx for idx, item_id in enumerate(ordered_ids)}

    with args.manifest.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        manifest_rows = list(reader)

    by_id = {row.get(args.manifest_id_field, ""): row for row in manifest_rows}
    selected = [by_id[item_id] for item_id in ordered_ids if item_id in by_id and item_id not in excluded_ids]
    selected.sort(key=lambda row: id_order[row.get(args.manifest_id_field, "")])
    missing = [item_id for item_id in ordered_ids if item_id not in by_id and item_id not in excluded_ids]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(selected)

    if args.missing_output:
        args.missing_output.parent.mkdir(parents=True, exist_ok=True)
        with args.missing_output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=[args.id_field])
            writer.writeheader()
            for item_id in missing:
                writer.writerow({args.id_field: item_id})

    print(f"selected={len(selected)} missing={len(missing)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
