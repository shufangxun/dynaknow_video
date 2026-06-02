#!/usr/bin/env python3
"""Build combined gold JSONL for full-video and shortcut tasks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def write_full_video_rows(path: Path, handle) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as src:
        for line in src:
            if not line.strip():
                continue
            row = json.loads(line)
            handle.write(
                json.dumps(
                    {
                        "video_id": row["video_id"],
                        "mode": "full_video",
                        "answer": row["answer"],
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                + "\n"
            )
            count += 1
    return count


def write_task_rows(path: Path, handle) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as src:
        for line in src:
            if not line.strip():
                continue
            row = json.loads(line)
            handle.write(
                json.dumps(
                    {
                        "video_id": row["video_id"],
                        "mode": row["mode"],
                        "answer": row["gold_answer"],
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                + "\n"
            )
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-video", required=True, type=Path)
    parser.add_argument("--answer-only", required=True, type=Path)
    parser.add_argument("--frame-shortcut", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        full_count = write_full_video_rows(args.full_video, handle)
        answer_count = write_task_rows(args.answer_only, handle)
        frame_count = write_task_rows(args.frame_shortcut, handle)

    print(f"wrote combined gold: full={full_count} answer_only={answer_count} frame={frame_count} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
