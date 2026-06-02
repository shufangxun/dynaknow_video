#!/usr/bin/env python3
"""Create a Wikimedia Commons transcode media manifest from File-page URLs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import urllib.parse
from pathlib import Path


FIELDS = ["id", "page_url", "title", "direct_url", "mime", "duration_sec", "license_short_name", "usage_terms"]


def filename_from_page_url(url: str) -> str:
    if "/wiki/File:" not in url:
        return ""
    return urllib.parse.unquote(url.split("/wiki/File:", 1)[1])


def transcode_url(page_url: str, suffix: str) -> str:
    filename = filename_from_page_url(page_url)
    if not filename:
        return ""
    digest = hashlib.md5(filename.encode("utf-8")).hexdigest()
    quoted = urllib.parse.quote(filename, safe="()-.!~*'")
    return (
        f"https://upload.wikimedia.org/wikipedia/commons/transcoded/"
        f"{digest[0]}/{digest[:2]}/{quoted}/{quoted}.{suffix}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--suffix", default="360p.webm")
    parser.add_argument("--ids", nargs="*", default=[])
    args = parser.parse_args()

    wanted = set(args.ids)
    rows = []
    with args.input.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if wanted and row["id"] not in wanted:
                continue
            out = {field: row.get(field, "") for field in FIELDS}
            out["direct_url"] = transcode_url(row["page_url"], args.suffix)
            out["mime"] = "video/webm"
            rows.append(out)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} transcode media rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
