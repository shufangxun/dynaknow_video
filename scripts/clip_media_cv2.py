#!/usr/bin/env python3
"""Clip local review videos with OpenCV when ffmpeg is unavailable.

The output intentionally drops audio. For this benchmark's visual shortcut
review, audio is a leakage risk rather than a required signal.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2


INPUT_FIELDS = ["id", "source_id", "input_path", "output_path", "start_sec", "end_sec", "notes"]
OUTPUT_FIELDS = INPUT_FIELDS + ["status", "fps", "frames_written", "duration_sec", "error"]


def parse_float(value: str, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clip_row(row: dict[str, str]) -> dict[str, str]:
    output = {field: row.get(field, "") for field in INPUT_FIELDS}
    output.update({"status": "failed", "fps": "", "frames_written": "0", "duration_sec": "", "error": ""})

    input_path = Path(row.get("input_path", ""))
    output_path = Path(row.get("output_path", ""))
    if not input_path.exists():
        output["error"] = "missing_input"
        return output

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        output["error"] = "open_failed"
        return output

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    if fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
        cap.release()
        output["error"] = "invalid_video_metadata"
        return output

    start_sec = max(0.0, parse_float(row.get("start_sec", ""), 0.0))
    default_end = frame_count / fps
    end_sec = parse_float(row.get("end_sec", ""), default_end)
    end_sec = min(max(start_sec, end_sec), default_end)
    start_frame = min(int(round(start_sec * fps)), frame_count - 1)
    end_frame = min(max(int(round(end_sec * fps)), start_frame + 1), frame_count)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        cap.release()
        output["error"] = "writer_open_failed"
        return output

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    written = 0
    for _ in range(start_frame, end_frame):
        ok, frame = cap.read()
        if not ok or frame is None:
            break
        writer.write(frame)
        written += 1

    writer.release()
    cap.release()

    if written <= 0:
        output["error"] = "no_frames_written"
        return output

    output["status"] = "ok"
    output["fps"] = f"{fps:.3f}"
    output["frames_written"] = str(written)
    output["duration_sec"] = f"{written / fps:.3f}"
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8", newline="") as handle:
        rows = [clip_row(row) for row in csv.DictReader(handle)]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    ok_count = sum(row["status"] == "ok" for row in rows)
    print(f"processed={len(rows)} ok={ok_count} output={args.output}")
    return 0 if ok_count == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
