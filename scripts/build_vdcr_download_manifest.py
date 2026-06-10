#!/usr/bin/env python3
"""Build a small VDCR media download manifest from resolved Archive URLs."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


FIELDS = [
    "id",
    "direct_url",
    "page_url",
    "title",
    "mime",
    "duration_sec",
    "candidate_knowledge_point",
    "concept_zh",
    "domain_zh",
    "subdomain_zh",
    "priority",
    "source_csv",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def duration(row: dict[str, str]) -> float:
    try:
        return float(row.get("duration_sec", "") or 0)
    except ValueError:
        return 0.0


GENERIC_TOKENS = {
    "and",
    "the",
    "effect",
    "reaction",
    "formation",
    "motion",
    "propagation",
    "growth",
    "collapse",
    "video",
    "slow",
    "demonstration",
}

NEGATIVE_SOURCE_TERMS = {
    "asl",
    "american sign language",
    "sign language",
    "dictionary",
    "definition",
}


def concept_tokens(concept: str) -> list[str]:
    tokens = []
    for token in re.findall(r"[A-Za-z0-9]+", concept.casefold()):
        if len(token) < 4 or token in GENERIC_TOKENS:
            continue
        tokens.append(token)
    return tokens


def note_field(notes: str, field: str) -> str:
    match = re.search(rf"{re.escape(field)}=([^;]+)", notes or "")
    return match.group(1) if match else ""


def has_core_term_match(row: dict[str, str], candidate: dict[str, str]) -> bool:
    tokens = concept_tokens(row["candidate_knowledge_point"])
    if not tokens:
        return True
    searchable_text = " ".join(
        [
            row.get("title", ""),
            row.get("page_url", ""),
            row.get("direct_url", ""),
            note_field(candidate.get("collector_notes", ""), "title"),
            note_field(candidate.get("collector_notes", ""), "description"),
        ]
    ).casefold()
    matched = sum(1 for token in set(tokens) if token in searchable_text)
    required = 2 if len(set(tokens)) >= 2 else 1
    return matched >= required


def has_negative_source_match(row: dict[str, str], candidate: dict[str, str]) -> bool:
    searchable_text = " ".join(
        [
            row.get("title", ""),
            row.get("page_url", ""),
            row.get("direct_url", ""),
            note_field(candidate.get("collector_notes", ""), "title"),
            note_field(candidate.get("collector_notes", ""), "description"),
        ]
    ).casefold()
    return any(term in searchable_text for term in NEGATIVE_SOURCE_TERMS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--media-manifest", required=True, type=Path)
    parser.add_argument("--concepts", type=Path, default=Path("data/vdcr_concept_inventory_v1.csv"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-duration-sec", type=float, default=120.0)
    parser.add_argument("--max-per-concept", type=int, default=1)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--allow-weak-title-match", action="store_true")
    parser.add_argument("--review-csv", type=Path, default=Path("data/vdcr_pilot_manual_review_seed_v1.csv"))
    parser.add_argument("--exclude-reviewed", action="store_true")
    args = parser.parse_args()

    candidates = {row["candidate_id"]: row for row in read_csv(args.candidates)}
    concepts = {row["concept_en"]: row for row in read_csv(args.concepts)}
    media_rows = [row for row in read_csv(args.media_manifest) if row.get("direct_url")]
    rejected_ids: set[str] = set()
    reviewed_ids: set[str] = set()
    if args.review_csv.exists():
        review_rows = read_csv(args.review_csv)
        rejected_ids = {row.get("id", "") for row in review_rows if row.get("review_status") == "reject"}
        reviewed_ids = {row.get("id", "") for row in review_rows if row.get("id", "")}

    enriched: list[dict[str, str]] = []
    for media in media_rows:
        if media["id"] in rejected_ids:
            continue
        if args.exclude_reviewed and media["id"] in reviewed_ids:
            continue
        candidate = candidates.get(media["id"], {})
        concept_key = candidate.get("candidate_knowledge_point", "")
        concept = concepts.get(concept_key, {})
        row = {
            "id": media["id"],
            "direct_url": media.get("direct_url", ""),
            "page_url": media.get("page_url", ""),
            "title": media.get("title", ""),
            "mime": media.get("mime", ""),
            "duration_sec": media.get("duration_sec", ""),
            "candidate_knowledge_point": concept_key,
            "concept_zh": concept.get("concept_zh", ""),
            "domain_zh": concept.get("domain_zh", ""),
            "subdomain_zh": concept.get("subdomain_zh", ""),
            "priority": concept.get("priority", ""),
            "source_csv": candidate.get("source_csv", ""),
        }
        if args.max_duration_sec > 0 and duration(row) > args.max_duration_sec:
            continue
        if has_negative_source_match(row, candidate):
            continue
        if not args.allow_weak_title_match and not has_core_term_match(row, candidate):
            continue
        enriched.append(row)

    priority_rank = {"A": 0, "B": 1, "C": 2, "": 9}
    enriched.sort(
        key=lambda row: (
            priority_rank.get(row["priority"], 9),
            duration(row) <= 0,
            duration(row),
            row["candidate_knowledge_point"],
            row["id"],
        )
    )

    selected: list[dict[str, str]] = []
    per_concept: dict[str, int] = {}
    for row in enriched:
        concept_key = row["candidate_knowledge_point"]
        if args.max_per_concept > 0 and per_concept.get(concept_key, 0) >= args.max_per_concept:
            continue
        selected.append(row)
        per_concept[concept_key] = per_concept.get(concept_key, 0) + 1
        if args.limit > 0 and len(selected) >= args.limit:
            break

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(selected)
    print(f"download_manifest_rows={len(selected)} wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
