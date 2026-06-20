#!/usr/bin/env python3
"""Build domain-targeted VDCR V2 retrieval queries for undercovered concepts."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


QUERY_FIELDS = [
    "concept_id",
    "priority",
    "search_term",
    "initial_category",
    "candidate_knowledge_point",
    "domain_seed",
    "subdomain_seed",
    "why_dynamic",
    "default_start_sec",
    "default_end_sec",
    "notes",
]

AVAILABILITY_RANK = {"high": 0, "medium": 1, "low": 2, "": 3}
PRIORITY_RANK = {"A": 0, "B": 1, "C": 2, "": 3}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=QUERY_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def query_terms(concept_en: str, concept_zh: str) -> list[str]:
    terms = [
        concept_en,
        f"{concept_en} demonstration",
        f"{concept_en} experiment video",
        f"{concept_zh} {concept_en}".strip(),
    ]
    seen: set[str] = set()
    output: list[str] = []
    for term in terms:
        if term and term not in seen:
            seen.add(term)
            output.append(term)
    return output


def build_gap_queries(
    concepts: list[dict[str, str]],
    candidates: list[dict[str, str]],
    domain: str,
    target_candidates_per_concept: int,
) -> list[dict[str, str]]:
    candidate_counts = Counter(row.get("candidate_knowledge_point", "") for row in candidates)
    eligible = [
        row
        for row in concepts
        if row.get("domain") == domain
        and row.get("concept_type") != "专有动态动作概念"
        and candidate_counts.get(row.get("concept_en", ""), 0) < target_candidates_per_concept
    ]
    eligible.sort(
        key=lambda row: (
            candidate_counts.get(row.get("concept_en", ""), 0),
            PRIORITY_RANK.get(row.get("priority", ""), 3),
            AVAILABILITY_RANK.get(row.get("video_availability_guess", ""), 3),
            row.get("concept_en", ""),
        )
    )

    rows: list[dict[str, str]] = []
    for concept in eligible:
        concept_en = concept.get("concept_en", "")
        concept_zh = concept.get("concept_zh", "")
        for term in query_terms(concept_en, concept_zh):
            rows.append(
                {
                    "concept_id": concept.get("concept_id", ""),
                    "priority": concept.get("priority", ""),
                    "search_term": term,
                    "initial_category": domain,
                    "candidate_knowledge_point": concept_en,
                    "domain_seed": domain,
                    "subdomain_seed": concept.get("subdomain", ""),
                    "why_dynamic": (
                        f"Candidate must show the temporal sequence that instantiates {concept_en}, "
                        "not merely an object, scene, or static result."
                    ),
                    "default_start_sec": "0",
                    "default_end_sec": "30",
                    "notes": (
                        f"vdcr_v2_gap_query; concept_zh={concept_zh}; "
                        f"existing_candidates={candidate_counts.get(concept_en, 0)}; "
                        f"target_candidates_per_concept={target_candidates_per_concept}"
                    ),
                }
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--concepts", type=Path, default=Path("data/vdcr_concept_inventory_v1.csv"))
    parser.add_argument("--candidates", type=Path, default=Path("data/vdcr_candidate_videos_combined_v2.csv"))
    parser.add_argument("--domain", default="chemistry_materials_change")
    parser.add_argument("--target-candidates-per-concept", type=int, default=3)
    parser.add_argument("--output", type=Path, default=Path("data/vdcr_v2_gap_queries_chemistry.csv"))
    args = parser.parse_args()

    rows = build_gap_queries(
        read_csv(args.concepts),
        read_csv(args.candidates),
        domain=args.domain,
        target_candidates_per_concept=args.target_candidates_per_concept,
    )
    write_csv(args.output, rows)
    print(f"gap_query_rows={len(rows)} wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
