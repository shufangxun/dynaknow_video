#!/usr/bin/env python3
"""Download media files from a DynaKnow media manifest."""

from __future__ import annotations

import argparse
import csv
import time
import urllib.error
import urllib.request
from pathlib import Path


USER_AGENT = "DynaKnowVideoPilot/0.1 (media download for local review)"


def extension_from_url(url: str) -> str:
    lower = url.lower().split("?", 1)[0]
    for ext in [".webm", ".ogv", ".ogg", ".mp4", ".mov", ".mkv", ".avi"]:
        if lower.endswith(ext):
            return ext
    return ".video"


def download(url: str, output: Path, max_retry_after_sec: float) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response, output.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
            return
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 500, 502, 503, 504}:
                raise
            if output.exists():
                output.unlink()
            retry_after = exc.headers.get("Retry-After")
            wait_s = float(retry_after) if retry_after and retry_after.isdigit() else 5.0 * (attempt + 1)
            if max_retry_after_sec > 0 and wait_s > max_retry_after_sec:
                raise RuntimeError(f"retry_after_too_long:{wait_s:.0f}s")
            time.sleep(wait_s)
        except Exception as exc:
            last_error = exc
            if output.exists():
                output.unlink()
            time.sleep(2.0 * (attempt + 1))
    if last_error:
        raise last_error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--sleep-sec", type=float, default=2.0)
    parser.add_argument(
        "--max-retry-after-sec",
        type=float,
        default=0.0,
        help="Fail fast when an HTTP Retry-After value exceeds this many seconds. Default 0 waits as requested.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with args.manifest.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if args.limit > 0:
        rows = rows[: args.limit]

    downloaded = 0
    skipped = 0
    failed = 0
    for row in rows:
        item_id = row["id"]
        url = row.get("direct_url", "")
        if not url:
            failed += 1
            print(f"FAIL {item_id}: missing direct_url")
            continue
        output = args.output_dir / f"{item_id}{extension_from_url(url)}"
        if output.exists() and output.stat().st_size > 0:
            skipped += 1
            print(f"SKIP {item_id}: {output}")
            continue
        print(f"START {item_id}: {url}")
        try:
            download(url, output, args.max_retry_after_sec)
            downloaded += 1
            print(f"OK {item_id}: {output} ({output.stat().st_size} bytes)")
        except Exception as exc:
            failed += 1
            print(f"FAIL {item_id}: {exc}")
        time.sleep(args.sleep_sec)
    print(f"downloaded={downloaded} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
