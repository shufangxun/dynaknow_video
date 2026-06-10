#!/usr/bin/env python3
"""Filter candidate rows by canonicalized source URL duplicates."""

from __future__ import annotations

import argparse
import csv
import json
import re
import urllib.parse
from collections import defaultdict
from pathlib import Path
from typing import Iterable


def canonical_source_key(url: str) -> str:
    """Return a stable key for duplicate detection across URL spellings."""
    value = (url or "").strip()
    if not value:
        return ""
    parsed = urllib.parse.urlsplit(value)
    host = parsed.netloc.lower()
    path = urllib.parse.unquote(parsed.path)
    if host.endswith("commons.wikimedia.org") and "/wiki/" in path:
        title = path.split("/wiki/", 1)[1]
        if title.startswith(("File:", "Image:")):
            _, filename = title.split(":", 1)
            filename = re.sub(r"[_\s]+", " ", filename).strip().lower()
            return f"commons:file:{filename}"
    normalized_path = re.sub(r"/+", "/", path)
    return urllib.parse.urlunsplit((parsed.scheme.lower(), host, normalized_path, "", "")).rstrip("/")


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def row_id(row: dict[str, str]) -> str:
    return row.get("candidate_id") or row.get("video_id") or row.get("id") or ""


def source_url(row: dict[str, str]) -> str:
    return row.get("source_url") or row.get("page_url") or ""


def read_existing(path: Path) -> Iterable[tuple[str, str]]:
    if path.suffix == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                yield str(row.get("video_id") or row.get("candidate_id") or row.get("id") or ""), str(row.get("source_url") or row.get("page_url") or "")
        return
    rows, _ = read_csv_rows(path)
    for row in rows:
        yield row_id(row), source_url(row)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--existing", nargs="+", required=True, type=Path)
    parser.add_argument("--output-new", required=True, type=Path)
    parser.add_argument("--output-duplicates", required=True, type=Path)
    args = parser.parse_args()

    existing_by_key: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for path in args.existing:
        if not path.exists():
            continue
        for item_id, url in read_existing(path):
            key = canonical_source_key(url)
            if key:
                existing_by_key[key].append((item_id, url))

    candidates, fieldnames = read_csv_rows(args.candidates)
    new_rows: list[dict[str, str]] = []
    duplicate_rows: list[dict[str, str]] = []
    seen_candidate_keys: dict[str, str] = {}
    for row in candidates:
        key = canonical_source_key(source_url(row))
        duplicate_matches = existing_by_key.get(key, [])
        repeated_candidate = key in seen_candidate_keys
        if duplicate_matches or repeated_candidate:
            enriched = dict(row)
            enriched["duplicate_key"] = key
            enriched["matched_existing_ids"] = ";".join(item_id for item_id, _ in duplicate_matches)
            enriched["matched_existing_urls"] = ";".join(url for _, url in duplicate_matches)
            enriched["matched_candidate_id"] = seen_candidate_keys.get(key, "")
            duplicate_rows.append(enriched)
        else:
            new_rows.append(row)
            if key:
                seen_candidate_keys[key] = row_id(row)

    args.output_new.parent.mkdir(parents=True, exist_ok=True)
    args.output_duplicates.parent.mkdir(parents=True, exist_ok=True)
    with args.output_new.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_rows)
    dup_fields = fieldnames + ["duplicate_key", "matched_existing_ids", "matched_existing_urls", "matched_candidate_id"]
    with args.output_duplicates.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=dup_fields)
        writer.writeheader()
        writer.writerows(duplicate_rows)

    print(
        f"candidates={len(candidates)} new={len(new_rows)} duplicates={len(duplicate_rows)} "
        f"existing_keys={len(existing_by_key)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
