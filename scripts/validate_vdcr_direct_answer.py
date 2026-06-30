#!/usr/bin/env python3
"""Validate VDCR direct-answer JSONL datasets."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


QUESTION = "Which named dynamic concept is instantiated by the temporally evolving process in this video?"

DOMAINS = {
    "physics_physical_systems",
    "chemistry_materials_change",
    "biology_living_systems",
    "earth_environmental_systems",
}

SOURCE_LEAK_FIELDS = {
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

QUALITY_GATES = {
    "temporal_necessity",
    "domain_specificity",
    "mechanism_bearing_label",
    "expert_naming_gap",
    "text_or_audio_leakage",
    "single_frame_shortcut",
}

ALLOWED_TIERS = {"core_main", "strict_main_candidate"}
CONCEPT_ID_PREFIXES = ("vdcr_concept_", "vdcr_v2_concept_")


def read_jsonl(path: Path) -> list[tuple[int, dict[str, Any]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be a JSON object")
            rows.append((line_no, row))
    return rows


def error(errors: list[str], path: Path, line_no: int, message: str) -> None:
    errors.append(f"{path}:{line_no}: {message}")


def require(errors: list[str], path: Path, line_no: int, condition: bool, message: str) -> None:
    if not condition:
        error(errors, path, line_no, message)


def validate_evidence(errors: list[str], path: Path, line_no: int, row: dict[str, Any]) -> None:
    evidence = row.get("dynamic_evidence")
    require(errors, path, line_no, isinstance(evidence, list) and len(evidence) > 0, "dynamic_evidence must be a non-empty list")
    if not isinstance(evidence, list):
        return
    duration = row.get("duration_sec")
    for idx, span in enumerate(evidence):
        require(errors, path, line_no, isinstance(span, dict), f"dynamic_evidence[{idx}] must be an object")
        if not isinstance(span, dict):
            continue
        start = span.get("start_sec")
        end = span.get("end_sec")
        desc = span.get("description")
        require(errors, path, line_no, isinstance(start, (int, float)), f"dynamic_evidence[{idx}].start_sec must be numeric")
        require(errors, path, line_no, isinstance(end, (int, float)), f"dynamic_evidence[{idx}].end_sec must be numeric")
        require(errors, path, line_no, isinstance(desc, str) and len(desc.strip()) >= 20, f"dynamic_evidence[{idx}].description is too short")
        if isinstance(start, (int, float)) and isinstance(end, (int, float)):
            require(errors, path, line_no, 0 <= start < end, f"dynamic_evidence[{idx}] must satisfy 0 <= start < end")
            if isinstance(duration, (int, float)) and duration > 0:
                require(errors, path, line_no, end <= duration + 0.25, f"dynamic_evidence[{idx}].end_sec exceeds duration_sec")


def validate_quality(errors: list[str], path: Path, line_no: int, row: dict[str, Any]) -> None:
    gates = row.get("quality_gates")
    require(errors, path, line_no, isinstance(gates, dict), "quality_gates must be an object")
    if not isinstance(gates, dict):
        return
    for gate in QUALITY_GATES:
        require(errors, path, line_no, gates.get(gate) == "pass", f"quality_gates.{gate} must be pass")
    tier = row.get("concept", {}).get("validity_tier") if isinstance(row.get("concept"), dict) else ""
    tier = tier or gates.get("concept_validity_tier", "")
    require(errors, path, line_no, tier in ALLOWED_TIERS, "concept validity tier must be core_main or strict_main_candidate")


def probe_video_frames(media_path: Path) -> int | None:
    cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(media_path),
        "-map",
        "v:0",
        "-frames:v",
        "2",
        "-f",
        "framehash",
        "-",
    ]
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return sum(1 for line in result.stdout.splitlines() if line.startswith("0,"))


def validate_row(
    errors: list[str],
    path: Path,
    line_no: int,
    row: dict[str, Any],
    release_mode: bool,
    check_media: bool,
    min_duration_sec: float,
    min_video_frames: int,
) -> None:
    for field in [
        "video_id",
        "split",
        "domain",
        "subdomain",
        "concept_id",
        "concept",
        "answer",
        "accepted_answers",
        "local_media",
        "duration_sec",
        "question",
        "dynamic_evidence",
        "static_insufficient_reason",
        "quality_gates",
    ]:
        require(errors, path, line_no, field in row, f"missing required field: {field}")

    require(errors, path, line_no, isinstance(row.get("video_id"), str) and row["video_id"].startswith("vdcr_"), "video_id must start with vdcr_")
    require(errors, path, line_no, row.get("domain") in DOMAINS, f"domain must be one of {sorted(DOMAINS)}")
    require(errors, path, line_no, isinstance(row.get("subdomain"), str) and bool(row.get("subdomain")), "subdomain must be non-empty")
    require(
        errors,
        path,
        line_no,
        isinstance(row.get("concept_id"), str) and row["concept_id"].startswith(CONCEPT_ID_PREFIXES),
        "concept_id must start with vdcr_concept_ or vdcr_v2_concept_",
    )
    require(errors, path, line_no, row.get("question") == QUESTION, "question does not match VDCR direct-answer prompt")
    require(errors, path, line_no, isinstance(row.get("duration_sec"), (int, float)) and row["duration_sec"] > 0, "duration_sec must be positive")
    if isinstance(row.get("duration_sec"), (int, float)):
        require(errors, path, line_no, row["duration_sec"] >= min_duration_sec, f"duration_sec must be >= {min_duration_sec}")
    require(errors, path, line_no, isinstance(row.get("static_insufficient_reason"), str) and len(row["static_insufficient_reason"].strip()) >= 20, "static_insufficient_reason is too short")

    concept = row.get("concept")
    require(errors, path, line_no, isinstance(concept, dict), "concept must be an object")
    if isinstance(concept, dict):
        for field in ["zh", "en", "type", "validity_tier"]:
            require(errors, path, line_no, isinstance(concept.get(field), str) and bool(concept.get(field)), f"concept.{field} must be non-empty")

    answer = row.get("answer")
    accepted = row.get("accepted_answers")
    require(errors, path, line_no, isinstance(answer, str) and bool(answer.strip()), "answer must be non-empty")
    require(errors, path, line_no, isinstance(accepted, list) and len(accepted) > 0, "accepted_answers must be non-empty")
    if isinstance(accepted, list):
        require(errors, path, line_no, all(isinstance(item, str) and item.strip() for item in accepted), "accepted_answers must contain non-empty strings")
        require(errors, path, line_no, len(accepted) == len(set(accepted)), "accepted_answers must be unique")
        require(errors, path, line_no, answer in accepted, "accepted_answers must include answer")

    if release_mode:
        leaks = sorted(field for field in SOURCE_LEAK_FIELDS if field in row)
        require(errors, path, line_no, not leaks, f"release row contains source/provenance fields: {', '.join(leaks)}")

    media = row.get("local_media")
    require(errors, path, line_no, isinstance(media, str) and bool(media.strip()), "local_media must be non-empty")
    if check_media and isinstance(media, str) and media:
        media_path = Path(media)
        require(errors, path, line_no, media_path.exists(), f"local_media does not exist: {media}")
        if media_path.exists() and min_video_frames > 0:
            frames = probe_video_frames(media_path)
            require(errors, path, line_no, frames is not None, f"could not determine video frame count: {media}")
            if frames is not None:
                require(errors, path, line_no, frames >= min_video_frames, f"video must have at least {min_video_frames} frames, got {frames}: {media}")

    validate_evidence(errors, path, line_no, row)
    validate_quality(errors, path, line_no, row)


def validate_dataset_constraints(
    plain_rows: list[dict[str, Any]],
    min_samples: int,
    max_domain_imbalance: int,
    allow_duplicate_answers: bool,
    max_videos_per_answer: int,
) -> list[str]:
    errors: list[str] = []
    video_ids = [row.get("video_id", "") for row in plain_rows]
    answers = [row.get("answer", "") for row in plain_rows]
    domains = Counter(row.get("domain", "") for row in plain_rows)
    if len(plain_rows) < min_samples:
        errors.append(f"{Path('<dataset>')}:0: dataset has fewer than {min_samples} samples")
    if len(video_ids) != len(set(video_ids)):
        errors.append(f"{Path('<dataset>')}:0: video_id values must be unique")
    if not allow_duplicate_answers and len(answers) != len(set(answers)):
        errors.append(f"{Path('<dataset>')}:0: answer values must be concept-level unique")
    if allow_duplicate_answers and max_videos_per_answer > 0:
        for answer, count in sorted(Counter(answers).items()):
            if count > max_videos_per_answer:
                errors.append(
                    f"{Path('<dataset>')}:0: concept cluster exceeds {max_videos_per_answer} videos: {answer}={count}"
                )
    if set(domains) != DOMAINS:
        errors.append(f"{Path('<dataset>')}:0: dataset must cover exactly the four VDCR main domains")
    if max_domain_imbalance >= 0 and domains:
        if max(domains.values()) - min(domains.values()) > max_domain_imbalance:
            errors.append(
                f"{Path('<dataset>')}:0: domain imbalance exceeds {max_domain_imbalance}: {dict(sorted(domains.items()))}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--release-mode", action="store_true")
    parser.add_argument("--check-media", action="store_true")
    parser.add_argument("--min-samples", type=int, default=1)
    parser.add_argument("--min-duration-sec", type=float, default=0.0)
    parser.add_argument("--min-video-frames", type=int, default=0)
    parser.add_argument("--max-domain-imbalance", type=int, default=-1)
    parser.add_argument(
        "--allow-duplicate-answers",
        action="store_true",
        help="Allow V2-style repeated concept clusters instead of requiring concept-level unique answers.",
    )
    parser.add_argument(
        "--max-videos-per-answer",
        type=int,
        default=0,
        help="When duplicate answers are allowed, fail if one answer appears more than this many times. 0 disables the cap.",
    )
    args = parser.parse_args()

    rows = read_jsonl(args.input)
    errors: list[str] = []
    for line_no, row in rows:
        validate_row(
            errors,
            args.input,
            line_no,
            row,
            args.release_mode,
            args.check_media,
            args.min_duration_sec,
            args.min_video_frames,
        )

    plain_rows = [row for _, row in rows]
    domains = Counter(row.get("domain", "") for row in plain_rows)
    for dataset_error in validate_dataset_constraints(
        plain_rows,
        min_samples=args.min_samples,
        max_domain_imbalance=args.max_domain_imbalance,
        allow_duplicate_answers=args.allow_duplicate_answers,
        max_videos_per_answer=args.max_videos_per_answer,
    ):
        errors.append(dataset_error.replace("<dataset>", str(args.input)))

    if errors:
        for item in errors:
            print(item, file=sys.stderr)
        return 1

    print(f"validated {len(plain_rows)} VDCR direct-answer rows")
    print("domains:", ", ".join(f"{domain}={count}" for domain, count in sorted(domains.items())))
    print(f"unique_answers={len({row.get('answer', '') for row in plain_rows})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
