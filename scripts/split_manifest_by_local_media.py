#!/usr/bin/env python3
"""Split a media manifest into downloaded and missing-local subsets."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def extension_from_url(url: str) -> str:
    lower = url.lower().split("?", 1)[0]
    for ext in [".webm", ".ogv", ".ogg", ".mp4", ".mov", ".mkv", ".avi"]:
        if lower.endswith(ext):
            return ext
    return ".video"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--media-dir", required=True, type=Path)
    parser.add_argument("--downloaded-output", required=True, type=Path)
    parser.add_argument("--missing-output", required=True, type=Path)
    args = parser.parse_args()

    with args.manifest.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    downloaded = []
    missing = []
    for row in rows:
        item_id = row.get("id", "")
        direct_url = row.get("direct_url", "")
        expected_path = args.media_dir / f"{item_id}{extension_from_url(direct_url)}"
        if expected_path.exists() and expected_path.stat().st_size > 0:
            downloaded.append(row)
        else:
            missing.append(row)

    for path, output_rows in [(args.downloaded_output, downloaded), (args.missing_output, missing)]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)

    print(f"downloaded={len(downloaded)} missing={len(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
