#!/usr/bin/env python3
"""Create a contact sheet for first/middle/last frame review."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


def read_image(path: Path, size: tuple[int, int]) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        image = np.full((size[1], size[0], 3), 245, dtype=np.uint8)
        cv2.putText(image, "missing", (20, size[1] // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return image
    return cv2.resize(image, size)


def label(image: np.ndarray, text: str) -> np.ndarray:
    canvas = image.copy()
    cv2.rectangle(canvas, (0, 0), (canvas.shape[1], 28), (255, 255, 255), -1)
    cv2.putText(canvas, text[:60], (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1)
    return canvas


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", required=True, type=Path)
    parser.add_argument("--frames-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--thumb-width", type=int, default=240)
    parser.add_argument("--thumb-height", type=int, default=160)
    args = parser.parse_args()

    with args.status.open("r", encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if not row.get("error")]

    strips = []
    size = (args.thumb_width, args.thumb_height)
    for row in rows:
        item_id = row["id"]
        frame_dir = args.frames_dir / item_id
        images = [
            label(read_image(frame_dir / "first.jpg", size), f"{item_id} first"),
            label(read_image(frame_dir / "middle.jpg", size), "middle"),
            label(read_image(frame_dir / "last.jpg", size), "last"),
        ]
        strips.append(np.hstack(images))

    if not strips:
        raise SystemExit("no extracted frames found")
    sheet = np.vstack(strips)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.output), sheet)
    print(f"wrote contact sheet to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

