#!/usr/bin/env python3
"""Build VDCR search queries from executable concept pool tiers."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


OUTPUT_FIELDS = [
    "concept_id",
    "priority",
    "pool_tier",
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


SEARCH_SUFFIXES = ["", "experiment", "demonstration", "slow motion", "video"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_existing_answers(path: Path) -> set[str]:
    if not path.exists():
        return set()
    answers = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            sample = json.loads(line)
            answers.add(sample.get("answer", ""))
            for alias in sample.get("accepted_answers", []):
                if isinstance(alias, str):
                    answers.add(alias)
    return answers


def split_csv_arg(value: str) -> set[str]:
    return {item.strip() for item in value.split(",") if item.strip()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool", type=Path, default=Path("data/vdcr_concept_pool_v1.csv"))
    parser.add_argument("--existing-samples", type=Path, default=Path("data/vdcr_pilot_samples_direct_answer_v1.jsonl"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--tiers", default="main_pool")
    parser.add_argument("--domains", default="")
    parser.add_argument("--concepts", default="", help="Comma-separated concept_en allowlist.")
    parser.add_argument("--max-concepts-per-domain", type=int, default=0)
    parser.add_argument("--exclude-existing-answers", action="store_true")
    parser.add_argument("--query-suffixes", default=",".join(SEARCH_SUFFIXES))
    args = parser.parse_args()

    tiers = split_csv_arg(args.tiers)
    domains = split_csv_arg(args.domains)
    concept_allowlist = split_csv_arg(args.concepts)
    suffixes = [item.strip() for item in args.query_suffixes.split(",")]
    existing = read_existing_answers(args.existing_samples) if args.exclude_existing_answers else set()

    concept_rows = []
    per_domain: dict[str, int] = {}
    for row in read_csv(args.pool):
        if row["pool_tier"] not in tiers:
            continue
        if domains and row["domain"] not in domains:
            continue
        if concept_allowlist and row["concept_en"] not in concept_allowlist:
            continue
        if row["concept_en"] in existing:
            continue
        if args.max_concepts_per_domain > 0 and per_domain.get(row["domain"], 0) >= args.max_concepts_per_domain:
            continue
        concept_rows.append(row)
        per_domain[row["domain"]] = per_domain.get(row["domain"], 0) + 1

    rows = []
    for concept in concept_rows:
        base = concept["retrieval_query_seed"] or concept["concept_en"]
        terms = []
        for suffix in suffixes:
            term = " ".join([base, suffix]).strip()
            if term and term not in terms:
                terms.append(term)
        if concept["concept_zh"]:
            terms.append(f"{concept['concept_zh']} {concept['concept_en']}")

        for term in terms:
            rows.append(
                {
                    "concept_id": concept["concept_id"],
                    "priority": concept["priority"],
                    "pool_tier": concept["pool_tier"],
                    "search_term": term,
                    "initial_category": concept["domain"],
                    "candidate_knowledge_point": concept["concept_en"],
                    "domain_seed": concept["domain"],
                    "subdomain_seed": concept["subdomain"],
                    "why_dynamic": (
                        f"Candidate must show the temporal sequence that instantiates {concept['concept_en']}, "
                        "not merely an object, scene, static result, or generic action."
                    ),
                    "default_start_sec": "0",
                    "default_end_sec": "30",
                    "notes": (
                        "vdcr_direct_answer; "
                        f"concept_zh={concept['concept_zh']}; "
                        f"concept_type={concept['concept_type']}; "
                        f"priority={concept['priority']}; "
                        f"pool_tier={concept['pool_tier']}"
                    ),
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"concepts={len(concept_rows)} query_rows={len(rows)} wrote {args.output}")
    for domain, count in sorted(per_domain.items()):
        print(f"{domain}\t{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
