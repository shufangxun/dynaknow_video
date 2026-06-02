#!/usr/bin/env python3
"""Summarize and lightly validate a DynaKnow candidate-video CSV."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path


CATEGORIES = {
    "physics_mechanics",
    "chemistry_material_change",
    "biology_life_processes",
    "everyday_causal_mechanisms",
    "procedural_operational_principles",
}

VIDEO_EXTENSIONS = (".webm", ".ogv", ".ogg", ".mp4", ".mov", ".mkv", ".avi")


def is_likely_video_url(url: str) -> bool:
    base = url.split("?", 1)[0].lower()
    return any(base.endswith(ext) for ext in VIDEO_EXTENSIONS) or "file:" in base and any(ext in base for ext in VIDEO_EXTENSIONS)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: summarize_candidates.py path/to/candidate_videos.csv", file=sys.stderr)
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    errors: list[str] = []
    warnings: list[str] = []
    ids: set[str] = set()
    category_counts: Counter[str] = Counter()
    platform_counts: Counter[str] = Counter()
    likely_rejects = 0

    for idx, row in enumerate(rows, start=2):
        candidate_id = row.get("candidate_id", "")
        if not candidate_id:
            errors.append(f"{path}:{idx}: missing candidate_id")
        elif candidate_id in ids:
            errors.append(f"{path}:{idx}: duplicate candidate_id {candidate_id}")
        ids.add(candidate_id)

        category = row.get("initial_category", "")
        if category not in CATEGORIES:
            errors.append(f"{path}:{idx}: invalid initial_category {category}")
        else:
            category_counts[category] += 1

        platform = row.get("source_platform", "")
        if platform:
            platform_counts[platform] += 1

        source_url = row.get("source_url", "")
        if not source_url.startswith("http"):
            errors.append(f"{path}:{idx}: source_url must start with http")
        if source_url and not is_likely_video_url(source_url):
            warnings.append(f"{path}:{idx}: URL does not look like a direct video file page: {source_url}")

        try:
            duration = float(row.get("raw_duration_sec", ""))
        except ValueError:
            errors.append(f"{path}:{idx}: raw_duration_sec must be numeric")
            continue
        if duration <= 0:
            warnings.append(f"{path}:{idx}: non-positive raw_duration_sec")
            likely_rejects += 1
        elif duration < 5 or duration > 60:
            warnings.append(f"{path}:{idx}: duration outside v1 target range: {duration:g}s")

        try:
            start = float(row.get("suggested_start_sec", ""))
            end = float(row.get("suggested_end_sec", ""))
            if end <= start:
                errors.append(f"{path}:{idx}: suggested_end_sec must be greater than suggested_start_sec")
        except ValueError:
            errors.append(f"{path}:{idx}: suggested start/end must be numeric")

        notes = row.get("collector_notes", "").lower()
        if "reject" in notes or "not a video" in notes:
            likely_rejects += 1

    print(f"rows: {len(rows)}")
    print("by_category:")
    for category in sorted(CATEGORIES):
        print(f"  {category}: {category_counts[category]}")
    print("by_platform:")
    for platform, count in platform_counts.most_common():
        print(f"  {platform}: {count}")
    print(f"likely_rejects_or_fallbacks: {likely_rejects}")
    print(f"warnings: {len(warnings)}")
    for warning in warnings[:20]:
        print(f"WARNING: {warning}")
    if len(warnings) > 20:
        print(f"WARNING: ... {len(warnings) - 20} more")

    if errors:
        print(f"errors: {len(errors)}", file=sys.stderr)
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("errors: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

