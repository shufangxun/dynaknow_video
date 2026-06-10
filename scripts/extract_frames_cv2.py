#!/usr/bin/env python3
"""Extract first/middle/last/sparse frames from downloaded videos with OpenCV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2


def is_dark(frame, threshold: float) -> bool:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return float(gray.mean()) < threshold


def read_frame(video, frame_index: int, fallback_back: int = 0):
    frame = None
    for offset in range(fallback_back + 1):
        video.set(cv2.CAP_PROP_POS_FRAMES, max(frame_index - offset, 0))
        ok, candidate = video.read()
        if ok and candidate is not None:
            frame = candidate
            break
    return frame


def write_frame(video, frame_index: int, output: Path, fallback_back: int = 0) -> bool:
    frame = read_frame(video, frame_index, fallback_back=fallback_back)
    if frame is None:
        return False
    output.parent.mkdir(parents=True, exist_ok=True)
    return bool(cv2.imwrite(str(output), frame))


def find_content_frame(video, frame_count: int, start: int, stop: int, step: int, threshold: float) -> int:
    frame_index = start
    while 0 <= frame_index < frame_count and ((step > 0 and frame_index <= stop) or (step < 0 and frame_index >= stop)):
        frame = read_frame(video, frame_index)
        if frame is not None and not is_dark(frame, threshold):
            return frame_index
        frame_index += step
    return start


def extract(video_path: Path, output_dir: Path, sparse_count: int, skip_dark_edges: bool, dark_threshold: float) -> dict[str, str]:
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

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        result["error"] = "open_failed"
        return result

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    result["frame_count"] = str(frame_count)
    result["fps"] = f"{fps:.3f}"
    if frame_count <= 0:
        result["error"] = "unknown_frame_count"
        cap.release()
        return result

    first_index = 0
    middle_index = frame_count // 2
    last_index = max(frame_count - 1, 0)
    if skip_dark_edges:
        scan = min(max(int(fps * 8), 120), frame_count - 1)
        first_index = find_content_frame(cap, frame_count, 0, scan, 1, dark_threshold)
        last_index = find_content_frame(cap, frame_count, frame_count - 1, max(frame_count - 1 - scan, 0), -1, dark_threshold)

    if write_frame(cap, first_index, output_dir / "first.jpg"):
        result["first"] = "ok"
    if write_frame(cap, middle_index, output_dir / "middle.jpg"):
        result["middle"] = "ok"
    if write_frame(cap, last_index, output_dir / "last.jpg", fallback_back=min(20, frame_count - 1)):
        result["last"] = "ok"
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        last_frame = None
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                break
            last_frame = frame
        if last_frame is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            if cv2.imwrite(str(output_dir / "last.jpg"), last_frame):
                result["last"] = "ok"

    sparse_dir = output_dir / "sparse"
    sparse_dir.mkdir(parents=True, exist_ok=True)
    if sparse_count > 0:
        if sparse_count == 1:
            indices = [middle_index]
        else:
            sparse_start = first_index if skip_dark_edges else 0
            sparse_end = last_index if skip_dark_edges else frame_count - 1
            if sparse_end <= sparse_start:
                sparse_start, sparse_end = 0, frame_count - 1
            indices = [round(sparse_start + i * (sparse_end - sparse_start) / (sparse_count - 1)) for i in range(sparse_count)]
        written = 0
        for idx, frame_index in enumerate(indices, start=1):
            if write_frame(cap, frame_index, sparse_dir / f"frame_{idx:03d}.jpg"):
                written += 1
        result["sparse"] = str(written)

    cap.release()
    expected_sparse = min(sparse_count, frame_count) if sparse_count > 0 else 0
    if (
        result["first"] != "ok"
        or result["middle"] != "ok"
        or result["last"] != "ok"
        or int(result["sparse"]) < expected_sparse
    ):
        result["error"] = "partial_frame_extraction"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-manifest", required=True, type=Path)
    parser.add_argument("--media-dir", required=True, type=Path)
    parser.add_argument("--frames-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--sparse-count", type=int, default=8)
    parser.add_argument("--skip-dark-edges", action="store_true")
    parser.add_argument("--dark-threshold", type=float, default=12.0)
    args = parser.parse_args()

    with args.media_manifest.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    results = []
    for row in rows:
        item_id = row["id"]
        direct_url = row.get("direct_url", "").lower()
        extension = ".webm"
        if direct_url.endswith(".ogv") or direct_url.endswith(".ogg"):
            extension = ".ogv"
        elif direct_url.endswith(".mp4"):
            extension = ".mp4"
        elif direct_url.endswith(".gif"):
            extension = ".gif"
        video_path = args.media_dir / f"{item_id}{extension}"
        result = {"id": item_id}
        result.update(extract(video_path, args.frames_dir / item_id, args.sparse_count, args.skip_dark_edges, args.dark_threshold))
        results.append(result)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["id", "video_path", "frame_count", "fps", "first", "middle", "last", "sparse", "error"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    ok_count = sum(row["error"] == "" for row in results)
    print(f"processed={len(results)} ok={ok_count} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
