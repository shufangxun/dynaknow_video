#!/usr/bin/env python3
"""Cut revised VDCR pilot candidates into reviewable media segments."""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path
from typing import Callable


FIELDS = [
    "id",
    "source_id",
    "candidate_knowledge_point",
    "direct_url",
    "page_url",
    "title",
    "mime",
    "duration_sec",
    "local_media",
    "segment_start_sec",
    "segment_end_sec",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def extension(path: str) -> str:
    suffix = Path(path).suffix
    return suffix if suffix else ".mp4"


def run_ffmpeg(source: Path, output: Path, start: float, end: float, reencode: bool) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    duration = max(0.1, end - start)
    cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", str(source), "-t", f"{duration:.3f}"]
    if reencode:
        cmd.extend(["-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p"])
    else:
        cmd.extend(["-an", "-c:v", "copy"])
    cmd.append(str(output))
    result = subprocess.run(cmd, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, errors="replace")
    if result.returncode != 0 or not output.exists() or output.stat().st_size <= 0:
        if not reencode:
            run_ffmpeg(source, output, start, end, reencode=True)
            return
        raise RuntimeError(result.stderr[-1000:] or "ffmpeg segment failed")


def cut_segment(source: Path, output: Path, start: float, end: float) -> None:
    run_ffmpeg(source, output, start, end, reencode=False)


def build_segment_manifest_rows(
    review_rows: list[dict[str, str]],
    media_rows: list[dict[str, str]],
    output_dir: Path,
    cut_segment: Callable[[Path, Path, float, float], None] = cut_segment,
) -> list[dict[str, str]]:
    media = {row["id"]: row for row in media_rows}
    output_rows: list[dict[str, str]] = []
    for review in review_rows:
        if review.get("review_status") != "revise":
            continue
        start = as_float(review.get("suggested_start_sec"), 0.0)
        end = as_float(review.get("suggested_end_sec"), 0.0)
        if end <= start:
            continue
        source = Path(review.get("local_media", ""))
        if not source.exists():
            continue
        source_id = review["id"]
        segment_id = f"{source_id}_seg_{int(start * 1000):06d}_{int(end * 1000):06d}"
        output = output_dir / f"{segment_id}{extension(str(source))}"
        cut_segment(source, output, start, end)
        source_media = media.get(source_id, {})
        output_rows.append(
            {
                "id": segment_id,
                "source_id": source_id,
                "candidate_knowledge_point": review.get("candidate_knowledge_point", ""),
                "direct_url": source_media.get("direct_url", ""),
                "page_url": source_media.get("page_url", ""),
                "title": source_media.get("title", ""),
                "mime": source_media.get("mime", ""),
                "duration_sec": f"{end - start:.3f}",
                "local_media": str(output),
                "segment_start_sec": f"{start:.3f}",
                "segment_end_sec": f"{end:.3f}",
            }
        )
    return output_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-csv", type=Path, default=Path("data/vdcr_pilot_manual_review_seed_v1.csv"))
    parser.add_argument("--media-manifest", type=Path, default=Path("data/vdcr_archive_download_manifest_pilot_v1.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("media/vdcr_segments_pilot_v1"))
    parser.add_argument("--output-manifest", type=Path, default=Path("data/vdcr_segment_manifest_pilot_v1.csv"))
    args = parser.parse_args()

    output_rows = build_segment_manifest_rows(
        read_csv(args.review_csv),
        read_csv(args.media_manifest),
        args.output_dir,
    )

    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.output_manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"segments={len(output_rows)} wrote {args.output_manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
