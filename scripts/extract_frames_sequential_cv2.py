#!/usr/bin/env python3
"""Extract review frames by sequential decoding instead of random seeking.

Some Commons videos report misleading FPS/frame-count metadata. This fallback
decodes the file linearly, counts actual readable frames, then decodes once
more to write first/middle/last/sparse frames.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2


def extension_from_url(url: str) -> str:
    lower = url.lower()
    if lower.endswith(".ogv") or lower.endswith(".ogg"):
        return ".ogv"
    if lower.endswith(".mp4"):
        return ".mp4"
    return ".webm"


def count_frames(video_path: Path) -> tuple[int, float]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return 0, 0.0
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    count = 0
    while True:
        ok, frame = cap.read()
        if not ok or frame is None:
            break
        count += 1
    cap.release()
    return count, fps


def write_selected(video_path: Path, output_dir: Path, indices: dict[int, Path]) -> int:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return 0
    output_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    frame_index = 0
    wanted = set(indices)
    while wanted:
        ok, frame = cap.read()
        if not ok or frame is None:
            break
        if frame_index in wanted:
            path = indices[frame_index]
            path.parent.mkdir(parents=True, exist_ok=True)
            if cv2.imwrite(str(path), frame):
                written += 1
            wanted.remove(frame_index)
        frame_index += 1
    cap.release()
    return written


def extract(video_path: Path, output_dir: Path, sparse_count: int) -> dict[str, str]:
    result = {
        "video_path": str(video_path),
        "frame_count": "0",
        "fps": "0",
        "first": "missing",
        "middle": "missing",
        "last": "missing",
        "sparse": "0",
        "error": "",
    }
    if not video_path.exists():
        result["error"] = "missing_video"
        return result

    frame_count, fps = count_frames(video_path)
    result["frame_count"] = str(frame_count)
    result["fps"] = f"{fps:.3f}"
    if frame_count <= 0:
        result["error"] = "open_or_decode_failed"
        return result

    first = 0
    middle = frame_count // 2
    last = frame_count - 1
    selected: dict[int, Path] = {
        first: output_dir / "first.jpg",
        middle: output_dir / "middle.jpg",
        last: output_dir / "last.jpg",
    }
    sparse_indices: list[int] = []
    if sparse_count > 0:
        if sparse_count == 1:
            sparse_indices = [middle]
        else:
            sparse_indices = [
                round(i * (frame_count - 1) / (sparse_count - 1))
                for i in range(sparse_count)
            ]
        for idx, frame_index in enumerate(sparse_indices, start=1):
            selected[frame_index] = output_dir / "sparse" / f"frame_{idx:03d}.jpg"

    written = write_selected(video_path, output_dir, selected)
    result["first"] = "ok" if (output_dir / "first.jpg").exists() else "missing"
    result["middle"] = "ok" if (output_dir / "middle.jpg").exists() else "missing"
    result["last"] = "ok" if (output_dir / "last.jpg").exists() else "missing"
    result["sparse"] = str(sum(1 for path in (output_dir / "sparse").glob("*.jpg")))
    expected = len(set(selected))
    if written < expected:
        result["error"] = "partial_frame_extraction"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-manifest", required=True, type=Path)
    parser.add_argument("--media-dir", required=True, type=Path)
    parser.add_argument("--frames-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--sparse-count", type=int, default=8)
    args = parser.parse_args()

    rows = list(csv.DictReader(args.media_manifest.open("r", encoding="utf-8", newline="")))
    results = []
    for row in rows:
        item_id = row["id"]
        video_path = args.media_dir / f"{item_id}{extension_from_url(row.get('direct_url', ''))}"
        result = {"id": item_id}
        result.update(extract(video_path, args.frames_dir / item_id, args.sparse_count))
        results.append(result)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["id", "video_path", "frame_count", "fps", "first", "middle", "last", "sparse", "error"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    ok_count = sum(row["error"] == "" for row in results)
    print(f"processed={len(results)} ok={ok_count} output={args.output}")
    return 0 if ok_count == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
