#!/usr/bin/env python3
"""Resolve Internet Archive details pages to direct media URLs."""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


METADATA_URL = "https://archive.org/metadata/"
USER_AGENT = "DynaKnowVideoPilot/0.1 (research metadata collection)"
VIDEO_EXTENSIONS = (".mp4", ".webm", ".ogv", ".ogg", ".mov", ".mkv", ".avi")
OUTPUT_FIELDS = [
    "id",
    "page_url",
    "title",
    "direct_url",
    "mime",
    "duration_sec",
    "license_short_name",
    "usage_terms",
]


def api_get(url: str, timeout_sec: float, max_attempts: int) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    last_error: Exception | None = None
    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout_sec) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
            time.sleep(2.0 * (attempt + 1))
    if last_error:
        raise last_error
    raise RuntimeError("unreachable archive retry failure")


def identifier_from_url(url: str) -> str:
    match = re.search(r"archive\.org/details/([^/?#]+)", url)
    if not match:
        return ""
    return urllib.parse.unquote(match.group(1))


def read_ids_and_urls(path: Path) -> list[tuple[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        id_field = "video_id" if "video_id" in (reader.fieldnames or []) else "candidate_id"
        return [(row.get(id_field, ""), row.get("source_url", "")) for row in reader]


def is_video_file(file_row: dict[str, Any]) -> bool:
    name = str(file_row.get("name", ""))
    fmt = str(file_row.get("format", "")).lower()
    lower = name.lower()
    if any(lower.endswith(ext) for ext in VIDEO_EXTENSIONS):
        return True
    return "mpeg4" in fmt or "h.264" in fmt or "webm" in fmt or "ogv" in fmt


def choose_video_file(meta: dict[str, Any]) -> dict[str, Any] | None:
    files = [row for row in meta.get("files", []) if is_video_file(row)]
    if not files:
        return None

    def sort_key(row: dict[str, Any]) -> tuple[int, int]:
        name = str(row.get("name", "")).lower()
        preferred = 0 if name.endswith((".mp4", ".webm", ".ogv", ".ogg")) else 1
        try:
            size = int(row.get("size", "0") or 0)
        except ValueError:
            size = 0
        return preferred, size

    files.sort(key=sort_key)
    return files[0]


def direct_url(identifier: str, name: str) -> str:
    return (
        "https://archive.org/download/"
        + urllib.parse.quote(identifier, safe="")
        + "/"
        + urllib.parse.quote(name, safe="()-.!~*'&")
    )


def mime_from_name(name: str) -> str:
    lower = name.lower()
    if lower.endswith(".mp4"):
        return "video/mp4"
    if lower.endswith(".webm"):
        return "video/webm"
    if lower.endswith(".ogv") or lower.endswith(".ogg"):
        return "video/ogg"
    if lower.endswith(".mov"):
        return "video/quicktime"
    return "video/*"


def duration_seconds(file_row: dict[str, Any]) -> str:
    try:
        return f"{float(file_row.get('length', '') or 0):.1f}"
    except ValueError:
        return ""


def write_checkpoint(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout-sec", type=float, default=30.0)
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()

    rows = []
    inputs = read_ids_and_urls(args.input)
    total = len(inputs)
    for index, (item_id, page_url) in enumerate(inputs, start=1):
        print(f"archive_resolve {index}/{total}: {item_id} {page_url}", flush=True)
        identifier = identifier_from_url(page_url)
        meta: dict[str, Any] = {}
        video_file: dict[str, Any] | None = None
        if identifier:
            try:
                meta = api_get(METADATA_URL + urllib.parse.quote(identifier, safe=""), args.timeout_sec, args.max_attempts)
                video_file = choose_video_file(meta)
            except Exception as exc:
                print(f"WARNING: failed archive resolve id={item_id} identifier={identifier}: {exc}")
        metadata = meta.get("metadata", {}) if meta else {}
        name = str(video_file.get("name", "")) if video_file else ""
        rows.append(
            {
                "id": item_id,
                "page_url": page_url,
                "title": str(metadata.get("title", identifier)),
                "direct_url": direct_url(identifier, name) if identifier and name else "",
                "mime": mime_from_name(name) if name else "",
                "duration_sec": duration_seconds(video_file or {}),
                "license_short_name": str(metadata.get("licenseurl", "")),
                "usage_terms": str(metadata.get("rights", "")),
            }
        )
        write_checkpoint(args.output, rows)

    write_checkpoint(args.output, rows)
    print(f"wrote {len(rows)} archive media rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
