#!/usr/bin/env python3
"""Apply curated hard-negative choice overrides to DynaKnow JSONL samples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


CHOICE_KEYS = ["A", "B", "C", "D"]


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_overrides(path: Path) -> dict[str, list[str]]:
    overrides: dict[str, list[str]] = {}
    for row in read_jsonl(path):
        video_id = row.get("video_id")
        distractors = row.get("distractors")
        if not isinstance(video_id, str) or not isinstance(distractors, list):
            raise ValueError(f"{path}: every row must contain video_id and distractors")
        cleaned = [str(item).strip() for item in distractors if str(item).strip()]
        if len(cleaned) != 3 or len(set(cleaned)) != 3:
            raise ValueError(f"{path}: {video_id} must have exactly three unique distractors")
        overrides[video_id] = cleaned
    return overrides


def apply_override(row: dict, distractors: list[str]) -> dict:
    answer = row.get("answer", "A")
    if answer not in CHOICE_KEYS:
        raise ValueError(f"{row.get('video_id')}: answer must be one of A/B/C/D")
    point = str(row.get("knowledge_point", "")).strip()
    if not point:
        raise ValueError(f"{row.get('video_id')}: missing knowledge_point")
    if point in distractors:
        raise ValueError(f"{row.get('video_id')}: distractor duplicates the correct answer")

    choices: dict[str, str] = {}
    distractor_iter = iter(distractors)
    for key in CHOICE_KEYS:
        choices[key] = point if key == answer else next(distractor_iter)
    updated = dict(row)
    updated["choices"] = choices
    return updated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--overrides", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    rows = read_jsonl(args.input)
    overrides = load_overrides(args.overrides)
    updated_rows = []
    missing: list[str] = []
    for row in rows:
        video_id = row.get("video_id", "")
        distractors = overrides.get(video_id)
        if not distractors:
            missing.append(str(video_id))
            updated_rows.append(row)
            continue
        updated_rows.append(apply_override(row, distractors))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in updated_rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(f"wrote {len(updated_rows)} rows to {args.output}")
    if missing:
        print(f"kept {len(missing)} rows without overrides: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
