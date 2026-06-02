#!/usr/bin/env python3
"""Merge JSONL files while checking duplicate video IDs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", required=True, nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    seen_ids: set[str] = set()
    written = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as dst:
        for input_path in args.inputs:
            with input_path.open("r", encoding="utf-8") as src:
                for line_no, line in enumerate(src, start=1):
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    video_id = record.get("video_id")
                    if video_id in seen_ids:
                        raise ValueError(f"duplicate video_id {video_id} in {input_path}:{line_no}")
                    seen_ids.add(video_id)
                    dst.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                    written += 1

    print(f"wrote {written} records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
