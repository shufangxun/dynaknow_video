#!/usr/bin/env python3
"""Report compact statistics for a DynaKnow release JSONL."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def pct(value: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{100.0 * value / total:.1f}%"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = read_jsonl(args.input)
    total = len(rows)
    category = Counter(row["category"] for row in rows)
    answers = Counter(row["answer"] for row in rows)
    knowledge = Counter(row["knowledge_point"] for row in rows)
    single_frame = Counter(row["shortcut_labels"].get("single_frame_sufficient", "") for row in rows)
    sparse_frame = Counter(row["shortcut_labels"].get("sparse_frames_sufficient", "") for row in rows)
    durations = [float(row["duration_sec"]) for row in rows]
    local_media = sum(1 for row in rows if row.get("local_media"))

    dataset_name = args.input.stem.replace("_", " ")
    lines = [
        f"# DynaKnow-Video Statistics: {dataset_name}",
        "",
        f"- samples: {total}",
        f"- local media available: {local_media}/{total} ({pct(local_media, total)})",
        f"- total duration sec: {sum(durations):.1f}",
        f"- mean duration sec: {(sum(durations) / total if total else 0):.1f}",
        f"- min duration sec: {(min(durations) if durations else 0):.1f}",
        f"- max duration sec: {(max(durations) if durations else 0):.1f}",
        "",
        "## Categories",
        "",
    ]
    for key, value in sorted(category.items()):
        lines.append(f"- `{key}`: {value} ({pct(value, total)})")

    lines.extend(["", "## Answer Distribution", ""])
    for key in ["A", "B", "C", "D"]:
        lines.append(f"- `{key}`: {answers.get(key, 0)} ({pct(answers.get(key, 0), total)})")

    lines.extend(["", "## Knowledge Points", ""])
    for key, value in knowledge.most_common():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Shortcut Labels", "", "Single-frame sufficient:"])
    for key, value in sorted(single_frame.items()):
        lines.append(f"- `{key or 'missing'}`: {value}")

    lines.extend(["", "Sparse-frames sufficient:"])
    for key, value in sorted(sparse_frame.items()):
        lines.append(f"- `{key or 'missing'}`: {value}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote stats to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
