#!/usr/bin/env python3
"""Create frame-extraction command manifest for static/sparse-frame filters.

This does not require ffmpeg at generation time. It writes shell commands that
can be run on a machine with ffmpeg after media files are downloaded.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


OUTPUT_FIELDS = [
    "id",
    "media_path",
    "first_frame_cmd",
    "middle_frame_cmd",
    "last_frame_cmd",
    "sparse_frames_cmd",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-manifest", required=True, type=Path)
    parser.add_argument("--media-dir", required=True, type=Path)
    parser.add_argument("--frames-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with args.media_manifest.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    output_rows = []
    for row in rows:
        item_id = row["id"]
        extension = ".webm"
        direct_url = row.get("direct_url", "").lower()
        if direct_url.endswith(".ogv") or direct_url.endswith(".ogg"):
            extension = ".ogv"
        elif direct_url.endswith(".mp4"):
            extension = ".mp4"
        media_path = args.media_dir / f"{item_id}{extension}"
        frame_dir = args.frames_dir / item_id
        output_rows.append(
            {
                "id": item_id,
                "media_path": str(media_path),
                "first_frame_cmd": f"mkdir -p {frame_dir} && ffmpeg -y -i {media_path} -vf \"select=eq(n\\,0)\" -frames:v 1 {frame_dir}/first.jpg",
                "middle_frame_cmd": f"mkdir -p {frame_dir} && ffmpeg -y -ss 50% -i {media_path} -frames:v 1 {frame_dir}/middle.jpg",
                "last_frame_cmd": f"mkdir -p {frame_dir} && ffmpeg -y -sseof -0.5 -i {media_path} -frames:v 1 {frame_dir}/last.jpg",
                "sparse_frames_cmd": f"mkdir -p {frame_dir}/sparse && ffmpeg -y -i {media_path} -vf fps=1/2 {frame_dir}/sparse/frame_%03d.jpg",
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"wrote {len(output_rows)} frame extraction rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

