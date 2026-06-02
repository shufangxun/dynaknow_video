#!/usr/bin/env python3
"""Generate DynaKnow draft MCQ samples from reviewed candidate videos."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


CHOICE_KEYS = ["A", "B", "C", "D"]
QUESTION = "Which knowledge point is best demonstrated by the dynamic process in the video?"
STATIC_REASON = (
    "A single frame may show the objects or final state but cannot establish the temporal process "
    "needed to identify this knowledge point."
)
BROAD_KNOWLEDGE_PATTERNS = [
    "some chemical reactions produce color change",
    "some reactions form a precipitate",
    "some mixtures produce gas during chemical reactions",
]


def read_knowledge_points(path: Path) -> tuple[dict[str, dict[str, str]], dict[str, list[str]]]:
    by_point: dict[str, dict[str, str]] = {}
    by_category: dict[str, list[str]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            point = row["knowledge_point"].strip()
            category = row["category"].strip()
            by_point[point] = row
            by_category.setdefault(category, []).append(point)
    return by_point, by_category


def existing_urls_and_ids(path: Path | None) -> tuple[set[str], set[str]]:
    urls: set[str] = set()
    ids: set[str] = set()
    if not path or not path.exists():
        return urls, ids
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            sample = json.loads(line)
            if sample.get("source_url"):
                urls.add(sample["source_url"])
            if sample.get("video_id"):
                ids.add(sample["video_id"])
    return urls, ids


def read_candidates(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_duration(value: str) -> float | None:
    try:
        duration = float(value)
    except (TypeError, ValueError):
        return None
    return duration if duration > 0 else None


def parse_time(value: str, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, parsed)


def has_broad_knowledge_point(point: str) -> bool:
    normalized = point.lower().strip().rstrip(".")
    return any(pattern in normalized for pattern in BROAD_KNOWLEDGE_PATTERNS)


def collect_distractors(
    point: str,
    category: str,
    knowledge_by_point: dict[str, dict[str, str]],
    knowledge_by_category: dict[str, list[str]],
) -> list[str]:
    row = knowledge_by_point.get(point, {})
    raw_negatives = row.get("hard_negative_pool", "")
    distractors: list[str] = []
    for item in raw_negatives.split(";"):
        candidate = item.strip()
        if candidate and candidate != point and candidate not in distractors:
            distractors.append(candidate)

    for candidate in knowledge_by_category.get(category, []):
        if candidate != point and candidate not in distractors:
            distractors.append(candidate)

    for other_point in knowledge_by_point:
        if other_point != point and other_point not in distractors:
            distractors.append(other_point)

    return distractors[:3]


def make_choices(point: str, distractors: list[str], sample_index: int) -> tuple[dict[str, str], str]:
    if len(distractors) < 3:
        raise ValueError(f"not enough distractors for {point}")
    correct_slot = sample_index % 4
    options = distractors[:3]
    options.insert(correct_slot, point)
    choices = {key: option for key, option in zip(CHOICE_KEYS, options, strict=True)}
    return choices, CHOICE_KEYS[correct_slot]


def build_sample(row: dict[str, str], video_id: str, sample_index: int, knowledge_by_point: dict[str, dict[str, str]], knowledge_by_category: dict[str, list[str]]) -> dict | None:
    point = row.get("candidate_knowledge_point", "").strip()
    category = row.get("initial_category", "").strip()
    duration = parse_duration(row.get("raw_duration_sec", ""))
    source_url = row.get("source_url", "").strip()
    if not point or not category or not duration or not source_url:
        return None
    if has_broad_knowledge_point(point):
        return None

    start = parse_time(row.get("suggested_start_sec", ""), 0.0)
    end = parse_time(row.get("suggested_end_sec", ""), duration)
    if end <= start:
        start, end = 0.0, duration
    end = min(end, duration)
    if end <= start:
        return None

    distractors = collect_distractors(point, category, knowledge_by_point, knowledge_by_category)
    if len(distractors) < 3:
        return None
    choices, answer = make_choices(point, distractors, sample_index)

    evidence_description = row.get("why_dynamic", "").strip()
    if len(evidence_description) < 10:
        evidence_description = (
            "The video must be watched over time to observe the process that demonstrates the knowledge point."
        )

    return {
        "video_id": video_id,
        "source_url": source_url,
        "license_or_usage_note": row.get("license_or_usage_note", "").strip() or "license_to_verify",
        "duration_sec": duration,
        "category": category,
        "knowledge_point": point,
        "question": QUESTION,
        "choices": choices,
        "answer": answer,
        "dynamic_evidence": [
            {
                "start_sec": start,
                "end_sec": end,
                "description": evidence_description,
            }
        ],
        "static_insufficient_reason": STATIC_REASON,
        "shortcut_results": {
            "answer_only": "not_run",
            "single_frame": "not_run",
            "sparse_frame": "not_run",
            "subtitle_only": "not_run",
            "static_caption_only": "not_run",
        },
        "review": {
            "human_full_video_correct": False,
            "human_single_frame_status": "not_run",
            "answer_leakage_status": "not_run",
            "subtitle_leakage_status": "not_run",
            "decision": "revise",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--knowledge-points", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--existing", type=Path)
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    knowledge_by_point, knowledge_by_category = read_knowledge_points(args.knowledge_points)
    existing_urls, existing_ids = existing_urls_and_ids(args.existing)
    candidates = read_candidates(args.candidates)

    samples = []
    next_index = args.start_index
    for row in candidates:
        if len(samples) >= args.limit:
            break
        source_url = row.get("source_url", "").strip()
        if source_url in existing_urls:
            continue
        while True:
            video_id = f"dynaknow_{next_index:06d}"
            next_index += 1
            if video_id not in existing_ids:
                break
        sample = build_sample(row, video_id, len(samples), knowledge_by_point, knowledge_by_category)
        if not sample:
            continue
        samples.append(sample)
        existing_urls.add(source_url)
        existing_ids.add(video_id)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(f"wrote {len(samples)} draft samples to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
