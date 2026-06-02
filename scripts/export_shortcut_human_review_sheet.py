#!/usr/bin/env python3
"""Export a human shortcut review sheet for frame-ready samples."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "video_id",
    "category",
    "knowledge_point",
    "answer",
    "source_url",
    "local_media",
    "first_frame",
    "middle_frame",
    "last_frame",
    "sparse_sheet",
    "answer_only_leakage",
    "visible_text_or_overlay",
    "ocr_leakage_status",
    "single_frame_sufficient",
    "sparse_frames_sufficient",
    "dynamic_knowledge_supported",
    "decision",
    "review_notes",
]


def local_media_path(media_dirs: list[Path], video_id: str) -> str:
    for media_dir in media_dirs:
        matches = sorted(media_dir.glob(f"{video_id}.*"))
        if matches:
            return str(matches[0])
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", required=True, type=Path)
    parser.add_argument("--media-dir", required=True, type=Path)
    parser.add_argument("--extra-media-dir", action="append", default=[], type=Path)
    parser.add_argument("--frames-dir", required=True, type=Path)
    parser.add_argument("--sparse-sheet-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = []
    with args.samples.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            sample = json.loads(line)
            video_id = sample["video_id"]
            frame_dir = args.frames_dir / video_id
            sparse_sheet = args.sparse_sheet_dir / f"{video_id}_sparse.jpg"
            rows.append(
                {
                    "video_id": video_id,
                    "category": sample["category"],
                    "knowledge_point": sample["knowledge_point"],
                    "answer": sample["answer"],
                    "source_url": sample["source_url"],
                    "local_media": local_media_path([args.media_dir, *args.extra_media_dir], video_id),
                    "first_frame": str(frame_dir / "first.jpg"),
                    "middle_frame": str(frame_dir / "middle.jpg"),
                    "last_frame": str(frame_dir / "last.jpg"),
                    "sparse_sheet": str(sparse_sheet) if sparse_sheet.exists() else "",
                    "answer_only_leakage": "",
                    "visible_text_or_overlay": "",
                    "ocr_leakage_status": "",
                    "single_frame_sufficient": "",
                    "sparse_frames_sufficient": "",
                    "dynamic_knowledge_supported": "",
                    "decision": "",
                    "review_notes": "",
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} shortcut review rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
