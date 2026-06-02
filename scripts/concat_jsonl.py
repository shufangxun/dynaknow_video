#!/usr/bin/env python3
"""Concatenate JSONL files without deduplicating records."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", required=True, nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with args.output.open("w", encoding="utf-8") as dst:
        for path in args.inputs:
            with path.open("r", encoding="utf-8") as src:
                for line in src:
                    if not line.strip():
                        continue
                    dst.write(line if line.endswith("\n") else line + "\n")
                    written += 1
    print(f"wrote {written} records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
