#!/usr/bin/env python3
"""Build VDCR direct-answer pilot samples from manually reviewed candidates."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


QUESTION = "Which named dynamic concept is instantiated by the temporally evolving process in this video?"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-csv", type=Path, default=Path("data/vdcr_pilot_manual_review_seed_v1.csv"))
    parser.add_argument("--candidates", type=Path, default=Path("data/vdcr_candidate_videos_archive_merged_v1.csv"))
    parser.add_argument("--concepts", type=Path, default=Path("data/vdcr_concept_inventory_v1.csv"))
    parser.add_argument("--media-manifest", type=Path, default=Path("data/vdcr_archive_media_manifest_v1.csv"))
    parser.add_argument("--segment-manifest", type=Path, default=Path("data/vdcr_segment_manifest_pilot_v1.csv"))
    parser.add_argument("--frame-status", type=Path, default=Path("data/vdcr_frame_status_pilot_v1.csv"))
    parser.add_argument("--segment-frame-status", type=Path, default=Path("data/vdcr_segment_frame_status_pilot_v1.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/vdcr_pilot_samples_direct_answer_v1.jsonl"))
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument(
        "--allowed-concept-tiers",
        default="",
        help="Comma-separated concept_validity_tier values to keep when the concepts CSV provides tiers.",
    )
    args = parser.parse_args()

    reviews = [row for row in read_csv(args.review_csv) if row.get("review_status") == "pass_candidate"]
    candidates = {row["candidate_id"]: row for row in read_csv(args.candidates)}
    concepts = {}
    for row in read_csv(args.concepts):
        for key in [
            row.get("concept_en", ""),
            row.get("recommended_answer_en", ""),
            row.get("concept_zh", ""),
            row.get("recommended_answer_zh", ""),
        ]:
            if key:
                concepts[key] = row
    media = {row["id"]: row for row in read_csv(args.media_manifest)}
    segments = {row["id"]: row for row in read_csv(args.segment_manifest)} if args.segment_manifest.exists() else {}
    frames = {row["id"]: row for row in read_csv(args.frame_status)}
    if args.segment_frame_status.exists():
        frames.update({row["id"]: row for row in read_csv(args.segment_frame_status)})
    allowed_tiers = {item.strip() for item in args.allowed_concept_tiers.split(",") if item.strip()}

    samples = []
    for review in reviews:
        candidate_id = review["id"]
        segment = segments.get(candidate_id, {})
        source_id = segment.get("source_id", candidate_id)
        candidate = candidates.get(source_id, candidates.get(candidate_id, {}))
        concept_key = review.get("candidate_knowledge_point") or candidate.get("candidate_knowledge_point", "")
        concept = concepts.get(concept_key, {})
        concept_tier = concept.get("concept_validity_tier", "")
        if allowed_tiers and (not concept_tier or concept_tier not in allowed_tiers):
            continue
        answer_en = concept.get("recommended_answer_en") or concept.get("concept_en", concept_key)
        answer_zh = concept.get("recommended_answer_zh") or concept.get("concept_zh", "")
        media_row = media.get(source_id, media.get(candidate_id, {}))
        frame_row = frames.get(candidate_id, {})
        duration = as_float(frame_row.get("duration_sec") or media_row.get("duration_sec"), 0.0)
        start_sec = max(0.0, as_float(review.get("suggested_start_sec"), 0.0))
        end_sec = as_float(review.get("suggested_end_sec"), duration)
        if duration > 0:
            end_sec = min(end_sec if end_sec > start_sec else duration, duration)
        accepted_answers = json.loads(concept.get("accepted_answers_json", "[]") or "[]")
        if concept_key and concept_key not in accepted_answers:
            accepted_answers.insert(0, concept_key)
        if answer_en and answer_en not in accepted_answers:
            accepted_answers.insert(0, answer_en)

        samples.append(
            {
                "video_id": f"vdcr_{args.start_index + len(samples):06d}",
                "split": "pilot",
                "domain": concept.get("domain", candidate.get("domain_seed", "")),
                "subdomain": concept.get("subdomain", candidate.get("subdomain_seed", "")),
                "concept_id": concept.get("concept_id", ""),
                "concept": {
                    "zh": answer_zh,
                    "en": answer_en,
                    "original_en": concept.get("concept_en", concept_key),
                    "type": concept.get("concept_type", ""),
                    "validity_tier": concept_tier,
                },
                "answer": answer_en,
                "accepted_answers": list(dict.fromkeys(accepted_answers)),
                "local_media": review.get("local_media", ""),
                "duration_sec": duration,
                "question": QUESTION,
                "dynamic_evidence": [
                    {
                        "start_sec": start_sec,
                        "end_sec": end_sec,
                        "description": review.get("review_notes", "") or f"Temporal microscopy sequence instantiates {concept_key}.",
                    }
                ],
                "static_insufficient_reason": (
                    "A single frame may show the objects, scene, or intermediate state, but the named concept requires observing the temporal sequence, trajectory, propagation, morphology change, or interaction pattern."
                ),
                "source_url": candidate.get("source_url") or media_row.get("page_url", ""),
                "license_or_usage_note": candidate.get("license_or_usage_note") or media_row.get("license_short_name") or "verify_on_source_page",
                "quality_gates": {
                    "temporal_necessity": "pass",
                    "domain_specificity": "pass",
                    "mechanism_bearing_label": "pass",
                    "expert_naming_gap": "pass",
                    "text_or_audio_leakage": "pass",
                    "single_frame_shortcut": "pass",
                    "concept_validity_tier": concept_tier or "not_provided",
                    "production_gate": concept.get("production_gate", ""),
                },
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"pilot_samples={len(samples)} wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
