#!/usr/bin/env python3
"""Check direct media URLs in a DynaKnow media manifest."""

from __future__ import annotations

import argparse
import csv
import time
import urllib.error
import urllib.request
from pathlib import Path


USER_AGENT = "DynaKnowVideoPilot/0.1 (media availability check)"
OUTPUT_FIELDS = [
    "id",
    "direct_url",
    "http_status",
    "content_type",
    "content_length",
    "ok",
    "error",
]


def head(url: str, timeout_sec: float, attempts: int) -> dict[str, str]:
    if not url:
        return {"http_status": "", "content_type": "", "content_length": "", "ok": "false", "error": "missing_url"}
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    last_error = ""
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=timeout_sec) as response:
                status = str(response.status)
                content_type = response.headers.get("Content-Type", "")
                content_length = response.headers.get("Content-Length", "")
                ok_content_type = content_type.startswith("video/") or content_type in {"application/ogg", "application/octet-stream"}
                ok = str(response.status == 200 and ok_content_type).lower()
                return {
                    "http_status": status,
                    "content_type": content_type,
                    "content_length": content_length,
                    "ok": ok,
                    "error": "",
                }
        except urllib.error.HTTPError as exc:
            last_error = str(exc)
            if exc.code not in {429, 500, 502, 503, 504}:
                return {
                    "http_status": str(exc.code),
                    "content_type": "",
                    "content_length": "",
                    "ok": "false",
                    "error": str(exc),
                }
            time.sleep(2.0 * (attempt + 1))
        except Exception as exc:
            last_error = str(exc)
            time.sleep(1.0 * (attempt + 1))
    return {
        "http_status": "",
        "content_type": "",
        "content_length": "",
        "ok": "false",
        "error": last_error,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout-sec", type=float, default=8.0)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--sleep-sec", type=float, default=0.5)
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        checked = []
        for row in rows:
            result = head(row.get("direct_url", ""), args.timeout_sec, args.attempts)
            result["id"] = row.get("id", "")
            result["direct_url"] = row.get("direct_url", "")
            checked.append(result)
            writer.writerow(result)
            handle.flush()
            print(f"{result['id']}: ok={result['ok']} status={result['http_status']} error={result['error']}")
            time.sleep(args.sleep_sec)

    ok_count = sum(row["ok"] == "true" for row in checked)
    print(f"checked {len(checked)} URLs; ok={ok_count}; output={args.output}")
    return 0 if ok_count == len(checked) else 1


if __name__ == "__main__":
    raise SystemExit(main())
