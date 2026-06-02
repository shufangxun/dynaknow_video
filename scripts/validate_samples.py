#!/usr/bin/env python3
"""Validate DynaKnow-Video JSONL samples.

This checker intentionally has no external dependency. It performs schema-like
checks that catch common annotation mistakes before model evaluation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


CATEGORIES = {
    "physics_mechanics",
    "chemistry_material_change",
    "biology_life_processes",
    "everyday_causal_mechanisms",
    "procedural_operational_principles",
}

STATUSES = {"pass", "fail", "not_run"}
ANSWERS = {"A", "B", "C", "D"}


def fail(path: Path, line_no: int, message: str) -> str:
    return f"{path}:{line_no}: {message}"


def require(condition: bool, errors: list[str], path: Path, line_no: int, message: str) -> None:
    if not condition:
        errors.append(fail(path, line_no, message))


def validate_record(record: dict, path: Path, line_no: int) -> list[str]:
    errors: list[str] = []
    required = [
        "video_id",
        "source_url",
        "license_or_usage_note",
        "duration_sec",
        "category",
        "knowledge_point",
        "question",
        "choices",
        "answer",
        "dynamic_evidence",
        "static_insufficient_reason",
        "shortcut_results",
        "review",
    ]
    for key in required:
        require(key in record, errors, path, line_no, f"missing required field: {key}")
    if errors:
        return errors

    require(isinstance(record["video_id"], str) and record["video_id"].startswith("dynaknow_"), errors, path, line_no, "video_id must start with dynaknow_")
    require(isinstance(record["source_url"], str) and record["source_url"], errors, path, line_no, "source_url must be non-empty")
    require(isinstance(record["license_or_usage_note"], str) and record["license_or_usage_note"], errors, path, line_no, "license_or_usage_note must be non-empty")
    require(isinstance(record["duration_sec"], (int, float)) and record["duration_sec"] > 0, errors, path, line_no, "duration_sec must be positive")
    require(record["category"] in CATEGORIES, errors, path, line_no, f"unknown category: {record['category']}")
    require(isinstance(record["knowledge_point"], str) and len(record["knowledge_point"]) >= 10, errors, path, line_no, "knowledge_point is too short")
    require("dynamic process" in record["question"].lower(), errors, path, line_no, "question should use the generic dynamic process wording")

    choices = record["choices"]
    require(isinstance(choices, dict), errors, path, line_no, "choices must be an object")
    if isinstance(choices, dict):
        require(set(choices) == ANSWERS, errors, path, line_no, "choices must contain exactly A, B, C, D")
        for key, value in choices.items():
            require(isinstance(value, str) and len(value) >= 5, errors, path, line_no, f"choice {key} is too short")
    require(record["answer"] in ANSWERS, errors, path, line_no, "answer must be A, B, C, or D")

    evidence = record["dynamic_evidence"]
    require(isinstance(evidence, list) and len(evidence) >= 1, errors, path, line_no, "dynamic_evidence must contain at least one span")
    if isinstance(evidence, list):
        for idx, span in enumerate(evidence):
            require(isinstance(span, dict), errors, path, line_no, f"dynamic_evidence[{idx}] must be an object")
            if not isinstance(span, dict):
                continue
            for key in ["start_sec", "end_sec", "description"]:
                require(key in span, errors, path, line_no, f"dynamic_evidence[{idx}] missing {key}")
            if "start_sec" in span and "end_sec" in span:
                require(isinstance(span["start_sec"], (int, float)), errors, path, line_no, f"dynamic_evidence[{idx}].start_sec must be numeric")
                require(isinstance(span["end_sec"], (int, float)), errors, path, line_no, f"dynamic_evidence[{idx}].end_sec must be numeric")
                if isinstance(span["start_sec"], (int, float)) and isinstance(span["end_sec"], (int, float)):
                    require(span["end_sec"] > span["start_sec"], errors, path, line_no, f"dynamic_evidence[{idx}] end_sec must be greater than start_sec")
            if "description" in span:
                require(isinstance(span["description"], str) and len(span["description"]) >= 10, errors, path, line_no, f"dynamic_evidence[{idx}].description is too short")

    require(isinstance(record["static_insufficient_reason"], str) and len(record["static_insufficient_reason"]) >= 10, errors, path, line_no, "static_insufficient_reason is too short")

    shortcut_results = record["shortcut_results"]
    require(isinstance(shortcut_results, dict), errors, path, line_no, "shortcut_results must be an object")
    if isinstance(shortcut_results, dict):
        for key in ["answer_only", "single_frame", "sparse_frame", "subtitle_only", "static_caption_only"]:
            require(shortcut_results.get(key) in STATUSES, errors, path, line_no, f"shortcut_results.{key} must be pass, fail, or not_run")

    review = record["review"]
    require(isinstance(review, dict), errors, path, line_no, "review must be an object")
    if isinstance(review, dict):
        require(isinstance(review.get("human_full_video_correct"), bool), errors, path, line_no, "review.human_full_video_correct must be boolean")
        require(review.get("human_single_frame_status") in {"wrong", "uncertain", "correct", "not_run"}, errors, path, line_no, "invalid review.human_single_frame_status")
        require(review.get("answer_leakage_status") in STATUSES, errors, path, line_no, "invalid review.answer_leakage_status")
        require(review.get("subtitle_leakage_status") in STATUSES, errors, path, line_no, "invalid review.subtitle_leakage_status")
        require(review.get("decision") in {"accept", "revise", "reject"}, errors, path, line_no, "review.decision must be accept, revise, or reject")

    return errors


def validate_jsonl(path: Path) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(fail(path, line_no, f"invalid JSON: {exc}"))
                continue
            if not isinstance(record, dict):
                errors.append(fail(path, line_no, "line must be a JSON object"))
                continue
            video_id = record.get("video_id")
            if video_id in seen_ids:
                errors.append(fail(path, line_no, f"duplicate video_id: {video_id}"))
            if isinstance(video_id, str):
                seen_ids.add(video_id)
            errors.extend(validate_record(record, path, line_no))
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: validate_samples.py path/to/samples.jsonl", file=sys.stderr)
        return 2
    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2
    errors = validate_jsonl(path)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

