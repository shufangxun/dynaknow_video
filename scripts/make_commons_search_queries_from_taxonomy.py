#!/usr/bin/env python3
"""Expand taxonomy seeds into Commons file-search rows.

Two input shapes are supported:

1. Legacy knowledge-point seed CSV:
   knowledge_point, category, search_queries
2. v1 subdomain target CSV:
   domain, subdomain, min_v1_count, target_v1_count, notes

For the v1 target CSV, the script creates retrieval seeds only. The
candidate_knowledge_point field is intentionally set to a construction sentinel
because the retrieval agent should not finalize the mechanism-level knowledge
point.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = [
    "search_term",
    "initial_category",
    "candidate_knowledge_point",
    "domain_seed",
    "subdomain_seed",
    "default_start_sec",
    "default_end_sec",
    "why_dynamic",
    "notes",
]

DEFAULT_START = "0"
DEFAULT_END = "60"


def dynamic_hint(point: str) -> str:
    return f"The video should visibly show the temporal process for: {point}"


def target_queries(domain: str, subdomain: str, notes: str, max_count: int) -> list[str]:
    label = subdomain.replace("_", " ")
    keyword_text = " ".join(word for word in notes.replace(",", " ").split()[:10])
    seeds = [
        f"{label} video",
        f"{label} demonstration",
        f"{label} experiment video",
        f"{label} time lapse",
    ]
    if keyword_text:
        seeds.append(f"{keyword_text} video")
    if domain == "earth_environmental_systems":
        seeds.append(f"{label} natural process video")
    if domain == "engineering_operational_systems":
        seeds.append(f"{label} process demonstration")
    return seeds[:max_count]


def build_rows_from_knowledge_points(reader: csv.DictReader, max_per_point: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen = set()
    for kp in reader:
        point = kp["knowledge_point"].strip()
        category = kp["category"].strip()
        for query in kp.get("search_queries", "").split("|")[:max_per_point]:
            query = query.strip()
            if not query:
                continue
            key = (query.lower(), point)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "search_term": query,
                    "initial_category": category,
                    "candidate_knowledge_point": point,
                    "domain_seed": kp.get("domain", "") or category,
                    "subdomain_seed": kp.get("subdomain", ""),
                    "default_start_sec": DEFAULT_START,
                    "default_end_sec": DEFAULT_END,
                    "why_dynamic": dynamic_hint(point),
                    "notes": "taxonomy_expanded_legacy; requires visual review for dynamic evidence and title leakage.",
                }
            )
    return rows


def build_rows_from_targets(reader: csv.DictReader, max_per_point: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen = set()
    for target in reader:
        domain = target["domain"].strip()
        subdomain = target["subdomain"].strip()
        notes = target.get("notes", "").strip()
        for query in target_queries(domain, subdomain, notes, max_per_point):
            key = (query.lower(), domain, subdomain)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "search_term": query,
                    "initial_category": domain,
                    "candidate_knowledge_point": "__construct_after_dynamic_gate__",
                    "domain_seed": domain,
                    "subdomain_seed": subdomain,
                    "default_start_sec": DEFAULT_START,
                    "default_end_sec": DEFAULT_END,
                    "why_dynamic": (
                        "The video should visibly show a temporal mechanism in "
                        f"{domain}/{subdomain}; the final knowledge point must be constructed after review."
                    ),
                    "notes": (
                        "taxonomy_target_v1; "
                        f"domain={domain}; subdomain={subdomain}; "
                        f"min_v1_count={target.get('min_v1_count', '')}; "
                        f"target_v1_count={target.get('target_v1_count', '')}; {notes}"
                    ),
                }
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--knowledge-points", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-per-point", type=int, default=3)
    args = parser.parse_args()

    with args.knowledge_points.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            rows = []
        elif {"domain", "subdomain"}.issubset(reader.fieldnames) and "knowledge_point" not in reader.fieldnames:
            rows = build_rows_from_targets(reader, args.max_per_point)
        else:
            rows = build_rows_from_knowledge_points(reader, args.max_per_point)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} query rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
