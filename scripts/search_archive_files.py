#!/usr/bin/env python3
"""Search Internet Archive movie items for principle-first video candidates."""

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


API_URL = "https://archive.org/advancedsearch.php"
METADATA_URL = "https://archive.org/metadata/"
USER_AGENT = "DynaKnowVideoPilot/0.1 (research metadata collection)"
VIDEO_EXTENSIONS = (".mp4", ".webm", ".ogv", ".ogg", ".mov", ".mkv", ".avi")
GENERIC_QUERY_TERMS = {
    "video",
    "slow",
    "motion",
    "time",
    "lapse",
    "timelapse",
    "experiment",
    "demonstration",
    "demo",
}
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
    "domain_seed",
    "subdomain_seed",
    "why_dynamic",
    "collector_notes",
]

SKIPPED_FIELDS = ["search_term", "initial_category", "candidate_knowledge_point", "error"]


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


def archive_query_clause(search_term: str) -> str:
    tokens = [
        token
        for token in re.findall(r"[A-Za-z0-9]+", search_term.lower())
        if len(token) >= 3 and token not in GENERIC_QUERY_TERMS
    ]
    if not tokens:
        tokens = [token for token in re.findall(r"[A-Za-z0-9]+", search_term.lower()) if len(token) >= 3]
    tokens = tokens[:6]
    return " AND ".join(tokens) if tokens else search_term


def search_items(search_term: str, limit: int, timeout_sec: float, max_attempts: int) -> list[dict[str, Any]]:
    query = f"({archive_query_clause(search_term)}) AND mediatype:movies"
    params = [
        ("q", query),
        ("fl[]", "identifier"),
        ("fl[]", "title"),
        ("fl[]", "description"),
        ("fl[]", "licenseurl"),
        ("fl[]", "downloads"),
        ("rows", str(limit)),
        ("page", "1"),
        ("output", "json"),
        ("sort[]", "downloads desc"),
    ]
    payload = api_get(f"{API_URL}?{urllib.parse.urlencode(params)}", timeout_sec, max_attempts)
    return payload.get("response", {}).get("docs", [])


def metadata(identifier: str, timeout_sec: float, max_attempts: int) -> dict[str, Any]:
    return api_get(METADATA_URL + urllib.parse.quote(identifier, safe=""), timeout_sec, max_attempts)


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


def duration_seconds(file_row: dict[str, Any]) -> float:
    try:
        return float(file_row.get("length", "") or 0)
    except ValueError:
        return 0.0


def existing_urls(path: Path | None) -> set[str]:
    if not path or not path.exists():
        return set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row.get("source_url", "") for row in csv.DictReader(handle)}


def write_candidate_checkpoint(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_skipped_checkpoint(path: Path | None, rows: list[dict[str, str]]) -> None:
    if not path:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SKIPPED_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def source_url(identifier: str) -> str:
    return "https://archive.org/details/" + urllib.parse.quote(identifier, safe="")


def compact_note_text(value: object, limit: int = 240) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    text = text.replace(";", ",")
    if len(text) > limit:
        text = text[: limit - 3].rstrip() + "..."
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--per-query", type=int, default=5)
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument("--skip-existing", type=Path)
    parser.add_argument("--sleep-sec", type=float, default=0.5)
    parser.add_argument("--query-offset", type=int, default=0)
    parser.add_argument("--query-limit", type=int, default=0)
    parser.add_argument("--skipped-output", type=Path)
    parser.add_argument("--id-prefix", default="archive_principle_v1")
    parser.add_argument("--timeout-sec", type=float, default=30.0)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--max-duration-sec", type=float, default=0.0)
    args = parser.parse_args()

    with args.queries.open("r", encoding="utf-8", newline="") as handle:
        query_rows = list(csv.DictReader(handle))
    if args.query_offset:
        query_rows = query_rows[args.query_offset :]
    if args.query_limit > 0:
        query_rows = query_rows[: args.query_limit]

    rows: list[dict[str, str]] = []
    skipped_rows: list[dict[str, str]] = []
    seen_urls = existing_urls(args.skip_existing)
    next_id = args.start_index
    total_queries = len(query_rows)
    for query_index, query in enumerate(query_rows, start=1):
        term = query["search_term"]
        before_count = len(rows)
        print(f"archive_search {query_index}/{total_queries}: {term}", flush=True)
        try:
            docs = search_items(term, args.per_query, args.timeout_sec, args.max_attempts)
        except Exception as exc:
            print(f"WARNING: skipping archive search_term={term!r}: {exc}")
            skipped_rows.append(
                {
                    "search_term": term,
                    "initial_category": query.get("initial_category", ""),
                    "candidate_knowledge_point": query.get("candidate_knowledge_point", ""),
                    "error": str(exc),
                }
            )
            write_candidate_checkpoint(args.output, rows)
            write_skipped_checkpoint(args.skipped_output, skipped_rows)
            time.sleep(args.sleep_sec)
            continue
        for doc in docs:
            identifier = str(doc.get("identifier", ""))
            if not identifier:
                continue
            url = source_url(identifier)
            if url in seen_urls:
                continue
            try:
                meta = metadata(identifier, args.timeout_sec, args.max_attempts)
                video_file = choose_video_file(meta)
            except Exception as exc:
                print(f"WARNING: skipping archive identifier={identifier!r}: {exc}")
                continue
            if not video_file:
                continue
            duration = duration_seconds(video_file)
            if args.max_duration_sec > 0 and duration > args.max_duration_sec:
                continue
            suggested_start = float(query.get("default_start_sec") or 0)
            configured_end = float(query.get("default_end_sec") or 0)
            suggested_end = configured_end
            if duration > 0:
                suggested_end = min(configured_end or duration, duration)
                if suggested_end <= suggested_start:
                    suggested_start = 0.0
                    suggested_end = min(duration, 60.0)
            license_note = str(doc.get("licenseurl", "") or meta.get("metadata", {}).get("licenseurl", "") or "archive_license_verify_on_page")
            rows.append(
                {
                    "candidate_id": f"{args.id_prefix}_{next_id:06d}",
                    "source_url": url,
                    "source_platform": "internet_archive",
                    "license_or_usage_note": license_note,
                    "raw_duration_sec": f"{duration:.1f}",
                    "suggested_start_sec": f"{suggested_start:.1f}",
                    "suggested_end_sec": f"{suggested_end:.1f}",
                    "initial_category": query["initial_category"],
                    "candidate_knowledge_point": query["candidate_knowledge_point"],
                    "domain_seed": query.get("domain_seed", query.get("initial_category", "")),
                    "subdomain_seed": query.get("subdomain_seed", ""),
                    "why_dynamic": query.get("why_dynamic", "Search result requires review for visible temporal evidence."),
                    "collector_notes": (
                        f"archive_search_collected; search_term={term}; archive_identifier={identifier}; "
                        f"archive_file={video_file.get('name', '')}; title={compact_note_text(doc.get('title', ''))}; "
                        f"description={compact_note_text(doc.get('description', ''))}; {query.get('notes', '')}"
                    ),
                }
            )
            seen_urls.add(url)
            next_id += 1
        print(
            f"archive_search_done {query_index}/{total_queries}: hits={len(docs)} added={len(rows) - before_count} total={len(rows)}",
            flush=True,
        )
        write_candidate_checkpoint(args.output, rows)
        write_skipped_checkpoint(args.skipped_output, skipped_rows)
        time.sleep(args.sleep_sec)

    write_candidate_checkpoint(args.output, rows)
    write_skipped_checkpoint(args.skipped_output, skipped_rows)
    print(f"wrote {len(rows)} archive rows to {args.output}")
    if skipped_rows:
        print(f"skipped_archive_search_terms={len(skipped_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
