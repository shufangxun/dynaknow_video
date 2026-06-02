#!/usr/bin/env python3
"""Build a compact pilot manifest joining samples, media, frames, and review."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "video_id",
    "split_status",
    "category",
    "knowledge_point",
    "answer",
    "source_url",
    "local_media",
    "first_frame",
    "middle_frame",
    "last_frame",
    "sparse_sheet",
    "shortcut_decision",
    "single_frame_sufficient",
    "sparse_frames_sufficient",
    "review_notes",
]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def local_media_path(media_dirs: list[Path], video_id: str) -> str:
    for media_dir in media_dirs:
        media_files = sorted(media_dir.glob(f"{video_id}.*"))
        if media_files:
            return str(media_files[0])
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accepted", required=True, type=Path)
    parser.add_argument("--rejected", required=True, type=Path)
    parser.add_argument("--media-dir", required=True, type=Path)
    parser.add_argument("--extra-media-dir", action="append", default=[], type=Path)
    parser.add_argument("--frames-dir", required=True, type=Path)
    parser.add_argument("--sparse-sheet-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = []
    for status, path in [("accepted", args.accepted), ("rejected_or_revise", args.rejected)]:
        for sample in read_jsonl(path):
            video_id = sample["video_id"]
            review = sample.get("shortcut_human_review", {})
            frame_dir = args.frames_dir / video_id
            rows.append(
                {
                    "video_id": video_id,
                    "split_status": status,
                    "category": sample["category"],
                    "knowledge_point": sample["knowledge_point"],
                    "answer": sample["answer"],
                    "source_url": sample["source_url"],
                    "local_media": local_media_path([args.media_dir, *args.extra_media_dir], video_id),
                    "first_frame": str(frame_dir / "first.jpg") if (frame_dir / "first.jpg").exists() else "",
                    "middle_frame": str(frame_dir / "middle.jpg") if (frame_dir / "middle.jpg").exists() else "",
                    "last_frame": str(frame_dir / "last.jpg") if (frame_dir / "last.jpg").exists() else "",
                    "sparse_sheet": str(args.sparse_sheet_dir / f"{video_id}_sparse.jpg") if (args.sparse_sheet_dir / f"{video_id}_sparse.jpg").exists() else "",
                    "shortcut_decision": review.get("decision", ""),
                    "single_frame_sufficient": review.get("single_frame_sufficient", ""),
                    "sparse_frames_sufficient": review.get("sparse_frames_sufficient", ""),
                    "review_notes": review.get("review_notes", ""),
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} pilot manifest rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
