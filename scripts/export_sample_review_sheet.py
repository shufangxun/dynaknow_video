#!/usr/bin/env python3
"""Export a CSV review sheet from DynaKnow sample JSONL."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "video_id",
    "source_url",
    "direct_url",
    "media_ok",
    "duration_sec",
    "category",
    "knowledge_point",
    "question",
    "choice_A",
    "choice_B",
    "choice_C",
    "choice_D",
    "answer",
    "dynamic_evidence",
    "static_insufficient_reason",
    "video_available",
    "dynamic_process_visible",
    "knowledge_point_supported",
    "answer_only_leakage",
    "single_frame_sufficient",
    "sparse_frames_sufficient",
    "title_or_subtitle_leakage",
    "review_decision",
    "reviewer_notes",
]


def read_media_status(manifest_path: Path | None, check_path: Path | None) -> tuple[dict[str, str], dict[str, str]]:
    direct_urls: dict[str, str] = {}
    ok_status: dict[str, str] = {}
    if manifest_path and manifest_path.exists():
        with manifest_path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                direct_urls[row.get("id", "")] = row.get("direct_url", "")
    if check_path and check_path.exists():
        with check_path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                ok_status[row.get("id", "")] = row.get("ok", "")
    return direct_urls, ok_status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--media-manifest", type=Path)
    parser.add_argument("--media-check", type=Path)
    args = parser.parse_args()

    direct_urls, ok_status = read_media_status(args.media_manifest, args.media_check)
    rows = []
    with args.samples.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            sample = json.loads(line)
            video_id = sample["video_id"]
            evidence = "; ".join(
                f"{span['start_sec']}-{span['end_sec']}: {span['description']}"
                for span in sample.get("dynamic_evidence", [])
            )
            choices = sample["choices"]
            rows.append(
                {
                    "video_id": video_id,
                    "source_url": sample["source_url"],
                    "direct_url": direct_urls.get(video_id, ""),
                    "media_ok": ok_status.get(video_id, ""),
                    "duration_sec": sample["duration_sec"],
                    "category": sample["category"],
                    "knowledge_point": sample["knowledge_point"],
                    "question": sample["question"],
                    "choice_A": choices["A"],
                    "choice_B": choices["B"],
                    "choice_C": choices["C"],
                    "choice_D": choices["D"],
                    "answer": sample["answer"],
                    "dynamic_evidence": evidence,
                    "static_insufficient_reason": sample["static_insufficient_reason"],
                    "video_available": "",
                    "dynamic_process_visible": "",
                    "knowledge_point_supported": "",
                    "answer_only_leakage": "",
                    "single_frame_sufficient": "",
                    "sparse_frames_sufficient": "",
                    "title_or_subtitle_leakage": "",
                    "review_decision": "",
                    "reviewer_notes": "",
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} sample review rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
