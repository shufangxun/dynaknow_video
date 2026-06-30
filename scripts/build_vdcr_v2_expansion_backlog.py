#!/usr/bin/env python3
"""Build VDCR V2 concept/video expansion backlog and retrieval queries."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


DOMAINS = [
    "biology_living_systems",
    "chemistry_materials_change",
    "earth_environmental_systems",
    "physics_physical_systems",
]

MAIN_TIERS = {"core_main", "strict_main_candidate"}
AVAILABILITY_RANK = {"high": 0, "medium": 1, "low": 2, "": 3}
PRIORITY_RANK = {"A": 0, "B": 1, "C": 2, "": 3}

BACKLOG_FIELDS = [
    "concept_id",
    "domain",
    "subdomain",
    "concept_en",
    "concept_zh",
    "concept_validity_tier",
    "priority",
    "video_availability_guess",
    "current_seed_samples",
    "current_candidates",
    "current_review_queue",
    "target_candidates_per_concept",
    "needed_candidates",
    "expansion_role",
    "query_priority",
    "production_gate",
]

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


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fields} for row in rows])


def is_main_eligible(row: dict[str, str]) -> bool:
    tier = row.get("concept_validity_tier", "")
    if tier:
        return tier in MAIN_TIERS
    return row.get("priority", "") in {"A", "B"}


def query_terms(concept_en: str, concept_zh: str) -> list[str]:
    terms = [
        concept_en,
        f"{concept_en} demonstration",
        f"{concept_en} experiment video",
        f"{concept_zh} {concept_en}".strip(),
    ]
    output: list[str] = []
    seen: set[str] = set()
    for term in terms:
        if term and term not in seen:
            seen.add(term)
            output.append(term)
    return output


def build_expansion_backlog(
    concepts: list[dict[str, str]],
    seed_samples: list[dict[str, object]],
    candidates: list[dict[str, str]],
    review_queue: list[dict[str, str]],
    target_candidates_per_concept: int,
) -> list[dict[str, str]]:
    seed_counts = Counter(str(row.get("answer", "")) for row in seed_samples)
    candidate_counts = Counter(row.get("candidate_knowledge_point", "") for row in candidates)
    review_counts = Counter(row.get("candidate_knowledge_point", "") for row in review_queue)

    rows: list[dict[str, str]] = []
    for concept in concepts:
        concept_en = concept.get("recommended_answer_en") or concept.get("concept_en", "")
        if not concept_en:
            continue
        if concept.get("domain", "") not in DOMAINS:
            continue
        if concept.get("concept_type") == "专有动态动作概念":
            continue
        if not is_main_eligible(concept):
            continue
        current_candidates = candidate_counts.get(concept_en, 0)
        needed_candidates = max(target_candidates_per_concept - current_candidates, 0)
        if needed_candidates <= 0:
            continue
        current_seed = seed_counts.get(concept_en, 0)
        query_priority = (
            current_seed,
            current_candidates,
            PRIORITY_RANK.get(concept.get("priority", ""), 3),
            AVAILABILITY_RANK.get(concept.get("video_availability_guess", ""), 3),
            concept.get("domain", ""),
            concept_en,
        )
        rows.append(
            {
                "concept_id": concept.get("concept_id", ""),
                "domain": concept.get("domain", ""),
                "subdomain": concept.get("subdomain", ""),
                "concept_en": concept_en,
                "concept_zh": concept.get("recommended_answer_zh") or concept.get("concept_zh", ""),
                "concept_validity_tier": concept.get("concept_validity_tier", ""),
                "priority": concept.get("priority", ""),
                "video_availability_guess": concept.get("video_availability_guess", ""),
                "current_seed_samples": str(current_seed),
                "current_candidates": str(current_candidates),
                "current_review_queue": str(review_counts.get(concept_en, 0)),
                "target_candidates_per_concept": str(target_candidates_per_concept),
                "needed_candidates": str(needed_candidates),
                "expansion_role": "new_concept" if current_seed == 0 else "repeat_concept",
                "query_priority": "|".join(str(part) for part in query_priority),
                "production_gate": concept.get("production_gate", ""),
            }
        )

    rows.sort(key=lambda row: row["query_priority"])
    return rows


def round_robin_by_domain(backlog_rows: list[dict[str, str]], max_concepts: int = 0) -> list[dict[str, str]]:
    by_domain = {domain: [] for domain in DOMAINS}
    for row in backlog_rows:
        by_domain.setdefault(row.get("domain", ""), []).append(row)

    selected: list[dict[str, str]] = []
    while True:
        added = False
        for domain in DOMAINS:
            if by_domain.get(domain):
                selected.append(by_domain[domain].pop(0))
                added = True
                if max_concepts > 0 and len(selected) >= max_concepts:
                    return selected
        if not added:
            return selected


def build_backlog_queries(backlog_rows: list[dict[str, str]], max_concepts: int = 0) -> list[dict[str, str]]:
    selected = round_robin_by_domain(backlog_rows, max_concepts=max_concepts)
    rows: list[dict[str, str]] = []
    for concept in selected:
        concept_en = concept.get("concept_en", "")
        concept_zh = concept.get("concept_zh", "")
        for term in query_terms(concept_en, concept_zh):
            rows.append(
                {
                    "concept_id": concept.get("concept_id", ""),
                    "priority": concept.get("priority", ""),
                    "search_term": term,
                    "initial_category": concept.get("domain", ""),
                    "candidate_knowledge_point": concept_en,
                    "domain_seed": concept.get("domain", ""),
                    "subdomain_seed": concept.get("subdomain", ""),
                    "why_dynamic": (
                        f"Candidate must show the temporal sequence that instantiates {concept_en}, "
                        "not merely an object, scene, or static result."
                    ),
                    "default_start_sec": "0",
                    "default_end_sec": "30",
                    "notes": (
                        "vdcr_v2_expansion_backlog; "
                        f"concept_zh={concept_zh}; "
                        f"needed_candidates={concept.get('needed_candidates', '')}; "
                        f"production_gate={concept.get('production_gate', '')}"
                    ),
                }
            )
    return rows


def write_report(path: Path, backlog_rows: list[dict[str, str]], query_rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_domain = Counter(row["domain"] for row in backlog_rows)
    by_role = Counter(row["expansion_role"] for row in backlog_rows)
    needed_by_domain = Counter()
    for row in backlog_rows:
        needed_by_domain[row["domain"]] += int(row.get("needed_candidates", "0") or 0)

    lines = [
        "# VDCR V2 Expansion Backlog",
        "",
        "Generated by `scripts/build_vdcr_v2_expansion_backlog.py`.",
        "",
        "This backlog identifies main-eligible, non-action concepts whose candidate buffer is below the V2 target.",
        "",
        "`new_concept` means the concept is not covered by the V1 seed samples. It may come from either the tiered V1 inventory or the V2-only expansion table.",
        "",
        "## Summary",
        "",
        f"- backlog concepts: {len(backlog_rows)}",
        f"- retrieval query rows: {len(query_rows)}",
        f"- new-concept backlog: {by_role.get('new_concept', 0)}",
        f"- repeated-concept backlog: {by_role.get('repeat_concept', 0)}",
        "",
        "## Domain Counts",
        "",
        "| Domain | Concepts | Needed candidates |",
        "|---|---:|---:|",
    ]
    for domain in DOMAINS:
        lines.append(f"| `{domain}` | {by_domain.get(domain, 0)} | {needed_by_domain.get(domain, 0)} |")
    lines.extend(
        [
            "",
            "## Top Backlog Concepts",
            "",
            "| Concept | Domain | Role | Current candidates | Needed candidates | Gate |",
            "|---|---|---|---:|---:|---|",
        ]
    )
    for row in backlog_rows[:40]:
        lines.append(
            "| `{concept}` | `{domain}` | `{role}` | {current} | {needed} | {gate} |".format(
                concept=row["concept_en"],
                domain=row["domain"],
                role=row["expansion_role"],
                current=row["current_candidates"],
                needed=row["needed_candidates"],
                gate=row["production_gate"].replace("|", "/"),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--concepts", type=Path, default=Path("data/vdcr_v2_concept_inventory.csv"))
    parser.add_argument("--seed-samples", type=Path, default=Path("data/vdcr_v2_seed_samples.jsonl"))
    parser.add_argument("--candidates", type=Path, default=Path("data/vdcr_candidate_videos_combined_v2.csv"))
    parser.add_argument("--review-queue", type=Path, default=Path("data/vdcr_v2_review_queue.csv"))
    parser.add_argument("--target-candidates-per-concept", type=int, default=3)
    parser.add_argument("--max-query-concepts", type=int, default=120)
    parser.add_argument("--output-backlog", type=Path, default=Path("data/vdcr_v2_expansion_backlog.csv"))
    parser.add_argument("--output-queries", type=Path, default=Path("data/vdcr_v2_expansion_queries.csv"))
    parser.add_argument("--output-report", type=Path, default=Path("reports/vdcr_v2_expansion_backlog.md"))
    args = parser.parse_args()

    backlog_rows = build_expansion_backlog(
        concepts=read_csv(args.concepts),
        seed_samples=read_jsonl(args.seed_samples),
        candidates=read_csv(args.candidates),
        review_queue=read_csv(args.review_queue),
        target_candidates_per_concept=args.target_candidates_per_concept,
    )
    query_rows = build_backlog_queries(backlog_rows, max_concepts=args.max_query_concepts)
    write_csv(args.output_backlog, backlog_rows, BACKLOG_FIELDS)
    write_csv(args.output_queries, query_rows, QUERY_FIELDS)
    write_report(args.output_report, backlog_rows, query_rows)
    print(f"backlog_concepts={len(backlog_rows)} wrote {args.output_backlog}")
    print(f"query_rows={len(query_rows)} wrote {args.output_queries}")
    print(f"wrote {args.output_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
