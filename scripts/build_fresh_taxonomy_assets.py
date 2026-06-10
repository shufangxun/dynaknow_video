#!/usr/bin/env python3
"""Build fresh taxonomy/target CSVs from DMR/DCR inventories."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

TAXONOMY_OUT = DATA / "domain_taxonomy_v1.csv"
TARGETS_OUT = DATA / "domain_sampling_targets_v1.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    principles = read_csv(DATA / "principle_inventory_v1.csv")
    concepts = read_csv(DATA / "dynamic_concept_inventory_v1.csv")
    taxonomy_rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    subdomains: dict[tuple[str, str], set[str]] = defaultdict(set)

    for row in principles:
        key = (row["domain"], row["subdomain"], row["principle"])
        if key not in seen:
            taxonomy_rows.append(
                {
                    "domain": row["domain"],
                    "subdomain": row["subdomain"],
                    "knowledge_point": row["principle"],
                }
            )
            seen.add(key)
        subdomains[(row["domain"], row["subdomain"])].add("DMR")

    for row in concepts:
        key = (row["domain"], row["subdomain"], row["dynamic_concept"])
        if key not in seen:
            taxonomy_rows.append(
                {
                    "domain": row["domain"],
                    "subdomain": row["subdomain"],
                    "knowledge_point": row["dynamic_concept"],
                }
            )
            seen.add(key)
        subdomains[(row["domain"], row["subdomain"])].add("DCR")

    target_rows = [
        {
            "domain": domain,
            "subdomain": subdomain,
            "min_v1_count": "8",
            "target_v1_count": "10",
            "capability_mix": "DMR+DCR" if len(labels) > 1 else next(iter(labels)),
        }
        for (domain, subdomain), labels in sorted(subdomains.items())
    ]

    write_csv(TAXONOMY_OUT, taxonomy_rows, ["domain", "subdomain", "knowledge_point"])
    write_csv(TARGETS_OUT, target_rows, ["domain", "subdomain", "min_v1_count", "target_v1_count", "capability_mix"])
    print(f"wrote {len(taxonomy_rows)} taxonomy rows -> {TAXONOMY_OUT}")
    print(f"wrote {len(target_rows)} target rows -> {TARGETS_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
