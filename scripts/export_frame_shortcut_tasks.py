#!/usr/bin/env python3
"""Export single-frame and sparse-frame shortcut tasks from samples and frames."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_samples(path: Path) -> dict[str, dict]:
    samples: dict[str, dict] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            sample = json.loads(line)
            samples[sample["video_id"]] = sample
    return samples


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", required=True, type=Path)
    parser.add_argument("--frames-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    samples = load_samples(args.samples)
    tasks = []
    for video_id, sample in samples.items():
        frame_dir = args.frames_dir / video_id
        for frame_name in ["first", "middle", "last"]:
            image_path = frame_dir / f"{frame_name}.jpg"
            if image_path.exists():
                tasks.append(
                    {
                        "video_id": video_id,
                        "mode": f"single_frame_{frame_name}",
                        "image_paths": [str(image_path)],
                        "question": sample["question"],
                        "choices": sample["choices"],
                        "gold_answer": sample["answer"],
                        "instruction": "Answer using only the provided still frame. If the knowledge point cannot be determined from the frame, return uncertain.",
                    }
                )
        sparse_dir = frame_dir / "sparse"
        sparse_paths = sorted(str(path) for path in sparse_dir.glob("*.jpg"))
        if sparse_paths:
            tasks.append(
                {
                    "video_id": video_id,
                    "mode": "sparse_frames_ordered",
                    "image_paths": sparse_paths,
                    "question": sample["question"],
                    "choices": sample["choices"],
                    "gold_answer": sample["answer"],
                    "instruction": "Answer using only the provided sparse still frames. If the knowledge point cannot be determined from these frames, return uncertain.",
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for task in tasks:
            handle.write(json.dumps(task, ensure_ascii=False) + "\n")
    print(f"wrote {len(tasks)} frame shortcut tasks to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

