#!/usr/bin/env python3
"""Export a clean release JSONL and manifest for accepted DynaKnow samples."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from taxonomy_aliases import normalize_domain_subdomain


RELEASE_FIELDS = [
    "video_id",
    "split",
    "domain",
    "subdomain",
    "knowledge_point",
    "duration_sec",
    "local_media",
    "question",
    "choices",
    "answer",
    "dynamic_evidence",
    "static_insufficient_reason",
    "shortcut_labels",
]

MANIFEST_FIELDS = [
    "video_id",
    "split",
    "domain",
    "subdomain",
    "knowledge_point",
    "answer",
    "source_url",
    "license_or_usage_note",
    "local_media",
    "duration_sec",
    "single_frame_sufficient",
    "sparse_frames_sufficient",
    "source_grounding_note",
]


def local_media_path(media_dirs: list[Path], video_id: str) -> str:
    for media_dir in media_dirs:
        matches = sorted(media_dir.glob(f"{video_id}.*"))
        if matches:
            return str(matches[0])
    return ""


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def read_taxonomy(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None or not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = {}
        for row in csv.DictReader(handle):
            if not row.get("knowledge_point"):
                continue
            row["domain"], row["subdomain"] = normalize_domain_subdomain(
                row.get("domain", ""),
                row.get("subdomain", ""),
            )
            rows[row["knowledge_point"]] = row
        return rows


def infer_domain_subdomain(sample: dict, taxonomy_by_kp: dict[str, dict[str, str]]) -> tuple[str, str]:
    tax = taxonomy_by_kp.get(sample.get("knowledge_point", ""), {})
    domain = sample.get("domain") or tax.get("domain") or sample.get("category", "")
    subdomain = sample.get("subdomain") or tax.get("subdomain", "")
    return normalize_domain_subdomain(domain, subdomain)


def shortcut_labels(sample: dict) -> dict[str, str]:
    shortcut_review = sample.get("shortcut_human_review", {})
    labels = sample.get("shortcut_labels")
    if isinstance(labels, dict):
        return {
            "answer_only_leakage": labels.get("answer_only_leakage", ""),
            "single_frame_sufficient": labels.get("single_frame_sufficient", ""),
            "sparse_frames_sufficient": labels.get("sparse_frames_sufficient", ""),
            "dynamic_knowledge_supported": labels.get("dynamic_knowledge_supported", ""),
            "ocr_leakage_status": labels.get("ocr_leakage_status", ""),
        }
    return {
        "answer_only_leakage": shortcut_review.get("answer_only_leakage", ""),
        "single_frame_sufficient": shortcut_review.get("single_frame_sufficient", ""),
        "sparse_frames_sufficient": shortcut_review.get("sparse_frames_sufficient", ""),
        "dynamic_knowledge_supported": shortcut_review.get("dynamic_knowledge_supported", ""),
        "ocr_leakage_status": shortcut_review.get("ocr_leakage_status", ""),
    }


def release_record(sample: dict, split: str, media_dirs: list[Path], include_provenance: bool, taxonomy_by_kp: dict[str, dict[str, str]]) -> dict:
    domain, subdomain = infer_domain_subdomain(sample, taxonomy_by_kp)
    row = {
        "video_id": sample["video_id"],
        "split": split,
        "domain": domain,
        "subdomain": subdomain,
        "knowledge_point": sample["knowledge_point"],
        "duration_sec": sample["duration_sec"],
        "local_media": sample.get("local_media") or local_media_path(media_dirs, sample["video_id"]),
        "question": sample["question"],
        "choices": sample["choices"],
        "answer": sample["answer"],
        "dynamic_evidence": sample["dynamic_evidence"],
        "static_insufficient_reason": sample["static_insufficient_reason"],
        "shortcut_labels": shortcut_labels(sample),
    }
    if include_provenance:
        row["source_url"] = sample.get("source_url", "")
        row["license_or_usage_note"] = sample.get("license_or_usage_note", "")
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accepted", required=True, type=Path)
    parser.add_argument("--media-dir", required=True, type=Path)
    parser.add_argument("--extra-media-dir", action="append", default=[], type=Path)
    parser.add_argument("--release-output", required=True, type=Path)
    parser.add_argument("--manifest-output", required=True, type=Path)
    parser.add_argument("--split", default="pilot_v0_5")
    parser.add_argument("--taxonomy", type=Path, default=Path("data/domain_taxonomy_v1.csv"))
    parser.add_argument(
        "--include-provenance",
        action="store_true",
        help="Include source_url and license_or_usage_note in the release JSONL. Keep off for evaluation JSONL to avoid source-title leakage.",
    )
    args = parser.parse_args()

    samples = read_jsonl(args.accepted)
    taxonomy_by_kp = read_taxonomy(args.taxonomy)
    media_dirs = [args.media_dir, *args.extra_media_dir]
    release_rows = [release_record(sample, args.split, media_dirs, args.include_provenance, taxonomy_by_kp) for sample in samples]

    args.release_output.parent.mkdir(parents=True, exist_ok=True)
    with args.release_output.open("w", encoding="utf-8") as handle:
        for row in release_rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
    with args.manifest_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        for row in release_rows:
            writer.writerow(
                {
                    "video_id": row["video_id"],
                    "split": row["split"],
                    "domain": row["domain"],
                    "subdomain": row["subdomain"],
                    "knowledge_point": row["knowledge_point"],
                    "answer": row["answer"],
                    "source_url": next((sample.get("source_url", "") for sample in samples if sample["video_id"] == row["video_id"]), ""),
                    "license_or_usage_note": next((sample.get("license_or_usage_note", "") for sample in samples if sample["video_id"] == row["video_id"]), ""),
                    "local_media": row["local_media"],
                    "duration_sec": row["duration_sec"],
                    "single_frame_sufficient": row["shortcut_labels"]["single_frame_sufficient"],
                    "sparse_frames_sufficient": row["shortcut_labels"]["sparse_frames_sufficient"],
                    "source_grounding_note": next(
                        (
                            sample.get("annotation_context", {}).get("source_grounding_note", "")
                            for sample in samples
                            if sample["video_id"] == row["video_id"]
                        ),
                        "",
                    ),
                }
            )

    print(f"wrote {len(release_rows)} release records to {args.release_output}")
    print(f"wrote manifest to {args.manifest_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
