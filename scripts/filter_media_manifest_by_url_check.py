#!/usr/bin/env python3
"""Split a media manifest by URL check results."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_float(value: str) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def parse_int(value: str) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--url-check", required=True, type=Path)
    parser.add_argument("--ok-output", required=True, type=Path)
    parser.add_argument("--failed-output", required=True, type=Path)
    parser.add_argument("--max-content-length-bytes", type=int, default=0)
    parser.add_argument("--max-duration-sec", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    manifest_rows = read_csv(args.manifest)
    with args.manifest.open("r", encoding="utf-8", newline="") as handle:
        manifest_fieldnames = csv.DictReader(handle).fieldnames or []
    check_rows = {row["id"]: row for row in read_csv(args.url_check)}
    ok_rows = []
    failed_rows = []
    for row in manifest_rows:
        check = check_rows.get(row["id"], {})
        merged = {**row, **{f"url_check_{key}": value for key, value in check.items() if key != "id"}}
        filter_reasons = []
        if check.get("ok") != "true":
            filter_reasons.append("url_check_failed")
        content_length = parse_int(check.get("content_length", ""))
        if args.max_content_length_bytes > 0 and content_length > args.max_content_length_bytes:
            filter_reasons.append("content_length_exceeds_limit")
        duration = parse_float(row.get("duration_sec", ""))
        if args.max_duration_sec > 0 and duration > args.max_duration_sec:
            filter_reasons.append("duration_exceeds_limit")
        merged["download_filter_reasons"] = ";".join(filter_reasons)
        if not filter_reasons:
            ok_rows.append(merged)
        else:
            failed_rows.append(merged)
    if args.limit > 0:
        overflow = ok_rows[args.limit :]
        for row in overflow:
            row["download_filter_reasons"] = "download_limit_overflow"
        failed_rows.extend(overflow)
        ok_rows = ok_rows[: args.limit]

    fallback_fields = [*manifest_fieldnames, "download_filter_reasons"]
    fieldnames = list(ok_rows[0].keys() if ok_rows else failed_rows[0].keys() if failed_rows else fallback_fields)
    write_csv(args.ok_output, ok_rows, fieldnames)
    write_csv(args.failed_output, failed_rows, fieldnames)
    print(f"ok={len(ok_rows)} failed={len(failed_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
