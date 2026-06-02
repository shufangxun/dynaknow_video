#!/usr/bin/env python3
"""Search Wikimedia Commons file pages for candidate videos."""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_URL = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "DynaKnowVideoPilot/0.1 (research metadata collection)"
VIDEO_EXTENSIONS = (".webm", ".ogv", ".ogg", ".mp4", ".mov", ".mkv", ".avi")
FIELDNAMES = [
    "candidate_id",
    "source_url",
    "source_platform",
    "license_or_usage_note",
    "raw_duration_sec",
    "suggested_start_sec",
    "suggested_end_sec",
    "initial_category",
    "candidate_knowledge_point",
    "why_dynamic",
    "collector_notes",
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


def search_files(search_term: str, limit: int) -> list[str]:
    payload = api_get(
        {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": search_term,
            "srnamespace": 6,
            "srlimit": limit,
        }
    )
    return [row.get("title", "") for row in payload.get("query", {}).get("search", []) if row.get("title", "")]


def file_info(titles: list[str]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for start in range(0, len(titles), 50):
        chunk = titles[start : start + 50]
        if not chunk:
            continue
        payload = api_get(
            {
                "action": "query",
                "format": "json",
                "prop": "imageinfo",
                "titles": "|".join(chunk),
                "iiprop": "url|mime|metadata|extmetadata|size",
            }
        )
        for page in payload.get("query", {}).get("pages", {}).values():
            title = page.get("title", "")
            imageinfo = page.get("imageinfo", [{}])[0]
            output[title] = imageinfo
        time.sleep(0.75)
    return output


def metadata_value(imageinfo: dict[str, Any], name: str) -> str:
    for item in imageinfo.get("metadata", []):
        if item.get("name") == name:
            return str(item.get("value", ""))
    return ""


def duration_seconds(imageinfo: dict[str, Any]) -> float:
    raw = metadata_value(imageinfo, "length") or metadata_value(imageinfo, "duration")
    try:
        return float(raw)
    except ValueError:
        return 0.0


def license_note(imageinfo: dict[str, Any]) -> str:
    ext = imageinfo.get("extmetadata", {})
    short = ext.get("LicenseShortName", {}).get("value", "")
    usage = ext.get("UsageTerms", {}).get("value", "")
    artist = ext.get("Artist", {}).get("value", "")
    bits = [bit for bit in [short, usage] if bit]
    if artist:
        bits.append("artist metadata present")
    return "; ".join(bits) or "wikimedia_commons_license_verify_on_page"


def is_video(title: str, imageinfo: dict[str, Any]) -> bool:
    mime = imageinfo.get("mime", "")
    url = imageinfo.get("url", "")
    title_lower = title.lower()
    url_lower = url.lower()
    return mime.startswith("video/") or any(title_lower.endswith(ext) or url_lower.endswith(ext) for ext in VIDEO_EXTENSIONS)


def page_url(title: str) -> str:
    return "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe=":/_()-.%")


def existing_urls(path: Path | None) -> set[str]:
    if not path or not path.exists():
        return set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row.get("source_url", "") for row in csv.DictReader(handle)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--per-query", type=int, default=10)
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument("--skip-existing", type=Path)
    parser.add_argument("--sleep-sec", type=float, default=1.5)
    parser.add_argument("--query-offset", type=int, default=0)
    parser.add_argument("--query-limit", type=int, default=0)
    parser.add_argument("--skipped-output", type=Path)
    parser.add_argument("--id-prefix", default="commons_search")
    args = parser.parse_args()

    with args.queries.open("r", encoding="utf-8", newline="") as handle:
        query_rows = list(csv.DictReader(handle))
    if args.query_offset:
        query_rows = query_rows[args.query_offset :]
    if args.query_limit > 0:
        query_rows = query_rows[: args.query_limit]

    rows = []
    skipped_rows = []
    seen_urls = existing_urls(args.skip_existing)
    next_id = args.start_index
    for query in query_rows:
        try:
            titles = search_files(query["search_term"], args.per_query)
            infos = file_info(titles)
        except Exception as exc:
            print(f"WARNING: skipping search_term={query['search_term']!r}: {exc}")
            skipped_rows.append(
                {
                    "search_term": query["search_term"],
                    "initial_category": query.get("initial_category", ""),
                    "candidate_knowledge_point": query.get("candidate_knowledge_point", ""),
                    "error": str(exc),
                }
            )
            time.sleep(args.sleep_sec)
            continue
        for title in titles:
            info = infos.get(title, {})
            if not is_video(title, info):
                continue
            url = page_url(title)
            if url in seen_urls:
                continue
            duration = duration_seconds(info)
            suggested_start = float(query.get("default_start_sec") or 0)
            configured_end = float(query.get("default_end_sec") or 0)
            suggested_end = configured_end
            if duration > 0:
                suggested_end = min(configured_end or duration, duration)
                if suggested_end <= suggested_start:
                    suggested_start = 0.0
                    suggested_end = min(duration, 60.0)
            rows.append(
                {
                    "candidate_id": f"{args.id_prefix}_{next_id:06d}",
                    "source_url": url,
                    "source_platform": "wikimedia_commons",
                    "license_or_usage_note": license_note(info),
                    "raw_duration_sec": f"{duration:.1f}",
                    "suggested_start_sec": f"{suggested_start:.1f}",
                    "suggested_end_sec": f"{suggested_end:.1f}",
                    "initial_category": query["initial_category"],
                    "candidate_knowledge_point": query["candidate_knowledge_point"],
                    "why_dynamic": query.get("why_dynamic", "Search result requires review for visible temporal evidence."),
                    "collector_notes": f"search_collected; search_term={query['search_term']}; commons_title={title}; {query.get('notes', '')}",
                }
            )
            seen_urls.add(url)
            next_id += 1
        time.sleep(args.sleep_sec)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    if args.skipped_output:
        args.skipped_output.parent.mkdir(parents=True, exist_ok=True)
        with args.skipped_output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["search_term", "initial_category", "candidate_knowledge_point", "error"],
            )
            writer.writeheader()
            writer.writerows(skipped_rows)
    print(f"wrote {len(rows)} rows to {args.output}")
    if skipped_rows:
        print(f"skipped_search_terms={len(skipped_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
