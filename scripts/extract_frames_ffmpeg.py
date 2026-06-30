#!/usr/bin/env python3
"""Extract review frames from downloaded media with ffmpeg/ffprobe."""

from __future__ import annotations

import argparse
import csv
import math
import subprocess
from pathlib import Path
from fractions import Fraction


FIELDNAMES = [
    "id",
    "video_path",
    "duration_sec",
    "first",
    "middle",
    "last",
    "sparse",
    "contact_sheet",
    "error",
]


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        errors="replace",
    )


def duration_sec(path: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe_failed")
    raw_duration = result.stdout.strip()
    try:
        return max(0.0, float(raw_duration or 0.0))
    except ValueError:
        pass

    packet_result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-count_packets",
            "-show_entries",
            "stream=nb_read_packets,r_frame_rate",
            "-of",
            "default=noprint_wrappers=1",
            str(path),
        ]
    )
    if packet_result.returncode != 0:
        raise RuntimeError(packet_result.stderr.strip() or f"invalid_duration:{raw_duration}")
    values = {}
    for line in packet_result.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    try:
        packets = int(values.get("nb_read_packets", "0"))
        frame_rate = float(Fraction(values.get("r_frame_rate", "0/1")))
    except (ValueError, ZeroDivisionError) as exc:
        raise RuntimeError(f"invalid_duration:{raw_duration}") from exc
    if packets <= 0 or frame_rate <= 0:
        raise RuntimeError(f"invalid_duration:{raw_duration}")
    return packets / frame_rate


def extract_one(path: Path, timestamp: float, output: Path) -> bool:
    output.parent.mkdir(parents=True, exist_ok=True)
    result = run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{timestamp:.3f}",
            "-i",
            str(path),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output),
        ]
    )
    return result.returncode == 0 and output.exists() and output.stat().st_size > 0


def make_contact_sheet(frames: list[Path], output: Path) -> bool:
    if not frames:
        return False
    output.parent.mkdir(parents=True, exist_ok=True)
    input_args: list[str] = []
    for frame in frames:
        input_args.extend(["-i", str(frame)])
    cols = min(4, len(frames))
    rows = math.ceil(len(frames) / cols)
    concat_inputs = "".join(f"[{idx}:v]" for idx in range(len(frames)))
    result = run(
        [
            "ffmpeg",
            "-y",
            *input_args,
            "-filter_complex",
            f"{concat_inputs}concat=n={len(frames)}:v=1:a=0,tile={cols}x{rows}",
            "-frames:v",
            "1",
            str(output),
        ]
    )
    return result.returncode == 0 and output.exists() and output.stat().st_size > 0


def find_video(media_dir: Path, item_id: str) -> Path | None:
    matches = sorted(media_dir.glob(f"{item_id}.*"))
    return matches[0] if matches else None


def extract_item(item_id: str, media_dir: Path, frames_dir: Path, sparse_count: int) -> dict[str, str]:
    video_path = find_video(media_dir, item_id)
    row = {
        "id": item_id,
        "video_path": str(video_path or ""),
        "duration_sec": "",
        "first": "missing",
        "middle": "missing",
        "last": "missing",
        "sparse": "0",
        "contact_sheet": "missing",
        "error": "",
    }
    if video_path is None:
        row["error"] = "missing_video"
        return row

    try:
        duration = duration_sec(video_path)
    except Exception as exc:
        row["error"] = f"ffprobe:{exc}"
        return row

    row["duration_sec"] = f"{duration:.3f}"
    if duration <= 0:
        row["error"] = "zero_duration"
        return row

    item_dir = frames_dir / item_id
    first_t = min(max(duration * 0.05, 0.0), max(duration - 0.1, 0.0))
    middle_t = min(max(duration * 0.50, 0.0), max(duration - 0.1, 0.0))
    last_t = min(max(duration * 0.95, 0.0), max(duration - 0.1, 0.0))
    for label, ts in [("first", first_t), ("middle", middle_t), ("last", last_t)]:
        if extract_one(video_path, ts, item_dir / f"{label}.jpg"):
            row[label] = "ok"

    sparse_paths: list[Path] = []
    if sparse_count > 0:
        sparse_dir = item_dir / "sparse"
        for idx in range(sparse_count):
            if sparse_count == 1:
                ts = middle_t
            else:
                ts = first_t + idx * (last_t - first_t) / (sparse_count - 1)
            output = sparse_dir / f"frame_{idx + 1:03d}.jpg"
            if extract_one(video_path, ts, output):
                sparse_paths.append(output)
        row["sparse"] = str(len(sparse_paths))
        if make_contact_sheet(sparse_paths, item_dir / "contact_sheet.jpg"):
            row["contact_sheet"] = "ok"

    if row["first"] != "ok" or row["middle"] != "ok" or row["last"] != "ok":
        row["error"] = "partial_frame_extraction"
    elif sparse_count > 0 and int(row["sparse"]) < sparse_count:
        row["error"] = "partial_sparse_extraction"
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media-manifest", required=True, type=Path)
    parser.add_argument("--media-dir", required=True, type=Path)
    parser.add_argument("--frames-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--sparse-count", type=int, default=6)
    args = parser.parse_args()

    with args.media_manifest.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    results = [extract_item(row["id"], args.media_dir, args.frames_dir, args.sparse_count) for row in rows]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
    ok_count = sum(1 for row in results if not row["error"])
    print(f"processed={len(results)} ok={ok_count} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
