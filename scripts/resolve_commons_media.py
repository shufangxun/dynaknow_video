#!/usr/bin/env python3
"""Resolve Wikimedia Commons File pages to direct media URLs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_URL = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "DynaKnowVideoPilot/0.1 (research metadata collection)"
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


def api_get(params: dict[str, Any]) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{API_URL}?{query}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {403, 429, 500, 502, 503, 504}:
                raise
            retry_after = exc.headers.get("Retry-After")
            wait_s = float(retry_after) if retry_after and retry_after.isdigit() else 2.0 * (attempt + 1)
            time.sleep(wait_s)
        except urllib.error.URLError as exc:
            last_error = exc
            time.sleep(2.0 * (attempt + 1))
    if last_error:
        raise last_error
    raise RuntimeError("unreachable API retry failure")


def title_from_page_url(url: str) -> str:
    match = re.search(r"/wiki/(File:.+)$", url)
    if not match:
        return ""
    return urllib.parse.unquote(match.group(1)).replace("_", " ")


def filename_from_page_url(url: str) -> str:
    match = re.search(r"/wiki/File:(.+)$", url)
    if not match:
        return ""
    return urllib.parse.unquote(match.group(1))


def derived_commons_direct_url(page_url: str) -> str:
    filename = filename_from_page_url(page_url)
    if not filename:
        return ""
    digest = hashlib.md5(filename.encode("utf-8")).hexdigest()
    quoted = urllib.parse.quote(filename, safe="()-.!~*'&")
    return f"https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{quoted}"


def mime_from_filename(page_url: str) -> str:
    filename = filename_from_page_url(page_url).lower()
    if filename.endswith(".webm"):
        return "video/webm"
    if filename.endswith(".ogv") or filename.endswith(".ogg"):
        return "video/ogg"
    if filename.endswith(".mp4"):
        return "video/mp4"
    return ""


def metadata_value(imageinfo: dict[str, Any], name: str) -> str:
    for item in imageinfo.get("metadata", []):
        if item.get("name") == name:
            return str(item.get("value", ""))
    return ""


def duration_seconds(imageinfo: dict[str, Any]) -> str:
    raw = metadata_value(imageinfo, "length") or metadata_value(imageinfo, "duration")
    try:
        return f"{float(raw):.1f}"
    except ValueError:
        return ""


def resolve_titles(titles: list[str]) -> dict[str, dict[str, str]]:
    resolved: dict[str, dict[str, str]] = {}
    for start in range(0, len(titles), 50):
        chunk = titles[start : start + 50]
        payload = api_get(
            {
                "action": "query",
                "format": "json",
                "prop": "imageinfo",
                "titles": "|".join(chunk),
                "iiprop": "url|mime|metadata|extmetadata",
            }
        )
        for page in payload.get("query", {}).get("pages", {}).values():
            title = page.get("title", "")
            imageinfo = page.get("imageinfo", [{}])[0]
            ext = imageinfo.get("extmetadata", {})
            resolved[title] = {
                "direct_url": imageinfo.get("url", ""),
                "mime": imageinfo.get("mime", ""),
                "duration_sec": duration_seconds(imageinfo),
                "license_short_name": ext.get("LicenseShortName", {}).get("value", ""),
                "usage_terms": ext.get("UsageTerms", {}).get("value", ""),
            }
        time.sleep(0.75)
    return resolved


def read_ids_and_urls(path: Path) -> list[tuple[str, str]]:
    if path.suffix == ".jsonl":
        rows = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                sample = json.loads(line)
                rows.append((sample.get("video_id", ""), sample.get("source_url", "")))
        return rows
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        id_field = "video_id" if "video_id" in (reader.fieldnames or []) else "candidate_id"
        return [(row.get(id_field, ""), row.get("source_url", "")) for row in reader]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--no-api", action="store_true", help="derive Commons upload URLs without calling the API")
    args = parser.parse_args()

    ids_and_urls = read_ids_and_urls(args.input)
    titles = [title_from_page_url(url) for _, url in ids_and_urls]
    if args.no_api:
        title_info = {}
    else:
        try:
            title_info = resolve_titles([title for title in titles if title])
        except Exception as exc:
            print(f"WARNING: failed to resolve Commons API metadata, writing page-only manifest: {exc}")
            title_info = {}

    rows = []
    for item_id, page_url in ids_and_urls:
        title = title_from_page_url(page_url)
        info = title_info.get(title, {})
        derived_url = derived_commons_direct_url(page_url)
        rows.append(
            {
                "id": item_id,
                "page_url": page_url,
                "title": title,
                "direct_url": info.get("direct_url", "") or derived_url,
                "mime": info.get("mime", "") or mime_from_filename(page_url),
                "duration_sec": info.get("duration_sec", ""),
                "license_short_name": info.get("license_short_name", ""),
                "usage_terms": info.get("usage_terms", ""),
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} media rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
