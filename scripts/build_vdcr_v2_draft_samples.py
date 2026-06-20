#!/usr/bin/env python3
"""Build a source-hidden VDCR V2 draft JSONL from seed release rows and passed candidates."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


QUESTION = "Which named dynamic concept is instantiated by the temporally evolving process in this video?"

SOURCE_FIELDS = {
    "source_url",
    "source_title",
    "source_summary",
    "source_description",
    "direct_media_url",
    "download_url",
    "license_or_usage_note",
    "author",
    "caption",
}

MANIFEST_FIELDS = [
    "video_id",
    "candidate_id",
    "answer",
    "domain",
    "source_url",
    "license_or_usage_note",
    "local_media",
    "review_status",
    "review_notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fields} for row in rows])


def concept_map(concepts: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    mapped: dict[str, dict[str, str]] = {}
    for row in concepts:
        for key in [
            row.get("concept_en", ""),
            row.get("concept_zh", ""),
            row.get("recommended_answer_en", ""),
            row.get("recommended_answer_zh", ""),
        ]:
            if key:
                mapped[key] = row
    return mapped


def parse_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def source_hidden(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key not in SOURCE_FIELDS}


def accepted_answers(concept: dict[str, str], answer: str) -> list[str]:
    try:
        aliases = json.loads(concept.get("accepted_answers_json", "[]") or "[]")
    except json.JSONDecodeError:
        aliases = []
    values = [answer, concept.get("concept_en", ""), concept.get("concept_zh", ""), *aliases]
    return [item for item in dict.fromkeys(str(value) for value in values if str(value).strip())]


def build_sample(
    row: dict[str, str],
    concept: dict[str, str],
    frame_status: dict[str, dict[str, str]],
    index: int,
) -> dict[str, Any]:
    candidate_id = row.get("candidate_id", "")
    answer = concept.get("recommended_answer_en") or concept.get("concept_en") or row.get("candidate_knowledge_point", "")
    answer_zh = concept.get("recommended_answer_zh") or concept.get("concept_zh", "")
    frame = frame_status.get(candidate_id, {})
    duration = parse_float(frame.get("duration_sec") or row.get("suggested_end_sec"), 0.0)
    start = parse_float(row.get("suggested_start_sec"), 0.0)
    end = parse_float(row.get("suggested_end_sec"), duration)
    if duration > 0:
        end = min(end if end > start else duration, duration)
    return {
        "video_id": f"vdcr_v2_{index:06d}",
        "split": "v2_draft",
        "domain": concept.get("domain") or row.get("domain_seed", ""),
        "subdomain": concept.get("subdomain") or row.get("subdomain_seed", ""),
        "concept_id": concept.get("concept_id", ""),
        "concept": {
            "zh": answer_zh,
            "en": answer,
            "original_en": concept.get("concept_en", answer),
            "type": concept.get("concept_type", ""),
            "validity_tier": concept.get("concept_validity_tier", ""),
        },
        "answer": answer,
        "accepted_answers": accepted_answers(concept, answer),
        "local_media": row.get("local_media", ""),
        "duration_sec": duration,
        "question": QUESTION,
        "dynamic_evidence": [
            {
                "start_sec": start,
                "end_sec": end,
                "description": row.get("review_notes", ""),
            }
        ],
        "static_insufficient_reason": (
            "A single frame may show the objects, scene, or intermediate state, but the named concept requires observing the temporal sequence, trajectory, propagation, morphology change, or interaction pattern."
        ),
        "quality_gates": {
            "temporal_necessity": "pass",
            "domain_specificity": "pass",
            "mechanism_bearing_label": "pass",
            "expert_naming_gap": "pass",
            "text_or_audio_leakage": "pass",
            "single_frame_shortcut": "pass",
            "concept_validity_tier": concept.get("concept_validity_tier", ""),
            "production_gate": concept.get("production_gate", ""),
        },
    }


def build_draft_samples(
    seed_rows: list[dict[str, Any]],
    review_rows: list[dict[str, str]],
    concepts_by_name: dict[str, dict[str, str]],
    frame_status: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    output = [source_hidden(row) for row in seed_rows]
    index = 1
    for row in review_rows:
        if row.get("review_status") != "pass_candidate":
            continue
        concept = concepts_by_name.get(row.get("candidate_knowledge_point", ""), {})
        output.append(build_sample(row, concept, frame_status, index))
        index += 1
    return output


def build_manifest_rows(samples: list[dict[str, Any]], review_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    review_by_media = {row.get("local_media", ""): row for row in review_rows if row.get("local_media")}
    rows: list[dict[str, str]] = []
    for sample in samples:
        review = review_by_media.get(str(sample.get("local_media", "")), {})
        rows.append(
            {
                "video_id": str(sample.get("video_id", "")),
                "candidate_id": review.get("candidate_id", ""),
                "answer": str(sample.get("answer", "")),
                "domain": str(sample.get("domain", "")),
                "source_url": review.get("source_url", ""),
                "license_or_usage_note": review.get("license_or_usage_note", ""),
                "local_media": str(sample.get("local_media", "")),
                "review_status": review.get("review_status", "v2_seed"),
                "review_notes": review.get("review_notes", ""),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-samples", type=Path, default=Path("release/v1/dataset_v1.jsonl"))
    parser.add_argument("--review-queue", type=Path, default=Path("data/vdcr_v2_review_queue.csv"))
    parser.add_argument("--concepts", type=Path, default=Path("data/vdcr_concept_inventory_tiered_v1.csv"))
    parser.add_argument("--frame-status", action="append", type=Path, default=[])
    parser.add_argument("--output", type=Path, default=Path("data/vdcr_v2_draft_samples.jsonl"))
    parser.add_argument("--manifest", type=Path, default=Path("data/vdcr_v2_draft_manifest.csv"))
    args = parser.parse_args()

    frame_paths = args.frame_status or sorted(Path("data").glob("vdcr_v2_*frame_status.csv"))
    frame_status = {row["id"]: row for path in frame_paths for row in read_csv(path)}
    review_rows = read_csv(args.review_queue)
    samples = build_draft_samples(
        seed_rows=read_jsonl(args.seed_samples),
        review_rows=review_rows,
        concepts_by_name=concept_map(read_csv(args.concepts)),
        frame_status=frame_status,
    )
    write_jsonl(args.output, samples)
    write_csv(args.manifest, build_manifest_rows(samples, review_rows), MANIFEST_FIELDS)
    print(f"draft_samples={len(samples)} wrote {args.output}")
    print(f"wrote {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
