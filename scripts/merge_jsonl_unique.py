#!/usr/bin/env python3
"""Merge JSONL files, keeping the first record for each ID."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", required=True, nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--id-field", default="video_id")
    args = parser.parse_args()

    records: dict[str, dict] = {}
    order: list[str] = []
    duplicates = 0
    for input_path in args.inputs:
        with input_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                item_id = record.get(args.id_field)
                if not item_id:
                    continue
                if item_id in records:
                    duplicates += 1
                    continue
                records[item_id] = record
                order.append(item_id)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for item_id in order:
            handle.write(json.dumps(records[item_id], ensure_ascii=False, separators=(",", ":")) + "\n")

    print(f"wrote {len(order)} unique records to {args.output}; skipped_duplicates={duplicates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
