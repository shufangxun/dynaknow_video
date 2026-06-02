#!/usr/bin/env python3
"""Create per-video sparse-frame contact sheets."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def read_image(path: Path, size: tuple[int, int]) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        return np.full((size[1], size[0], 3), 245, dtype=np.uint8)
    return cv2.resize(image, size)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--thumb-width", type=int, default=180)
    parser.add_argument("--thumb-height", type=int, default=120)
    parser.add_argument("--cols", type=int, default=4)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    size = (args.thumb_width, args.thumb_height)
    for video_dir in sorted(path for path in args.frames_dir.iterdir() if path.is_dir()):
        sparse_paths = sorted((video_dir / "sparse").glob("*.jpg"))
        if not sparse_paths:
            continue
        images = []
        for idx, path in enumerate(sparse_paths, start=1):
            image = read_image(path, size)
            cv2.rectangle(image, (0, 0), (image.shape[1], 24), (255, 255, 255), -1)
            cv2.putText(image, f"{video_dir.name} #{idx}", (6, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
            images.append(image)
        while len(images) % args.cols:
            images.append(np.full((size[1], size[0], 3), 245, dtype=np.uint8))
        rows = []
        for start in range(0, len(images), args.cols):
            rows.append(np.hstack(images[start : start + args.cols]))
        sheet = np.vstack(rows)
        cv2.imwrite(str(args.output_dir / f"{video_dir.name}_sparse.jpg"), sheet)
        written += 1
    print(f"wrote {written} sparse contact sheets to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

