#!/usr/bin/env python3
"""Create a balanced review subset from a DynaKnow sample review sheet."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


EXTRA_FIELDS = ["balance_rank", "selection_reason"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--leftover-output", type=Path)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--max-per-knowledge", type=int, default=3)
    parser.add_argument("--max-per-category", type=int, default=15)
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    selected = []
    leftovers = []
    category_counts: dict[str, int] = {}
    knowledge_counts: dict[str, int] = {}

    for row in rows:
        if len(selected) >= args.limit:
            leftovers.append((row, "review_subset_limit_reached"))
            continue

        category = row.get("category", "")
        knowledge_point = row.get("knowledge_point", "")
        if knowledge_counts.get(knowledge_point, 0) >= args.max_per_knowledge:
            leftovers.append((row, "knowledge_point_cap"))
            continue
        if category_counts.get(category, 0) >= args.max_per_category:
            leftovers.append((row, "category_cap"))
            continue

        knowledge_counts[knowledge_point] = knowledge_counts.get(knowledge_point, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1
        row = dict(row)
        row["balance_rank"] = str(len(selected) + 1)
        row["selection_reason"] = "selected_for_balanced_first_pass_review"
        selected.append(row)

    output_fields = fieldnames + [field for field in EXTRA_FIELDS if field not in fieldnames]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(selected)

    if args.leftover_output:
        args.leftover_output.parent.mkdir(parents=True, exist_ok=True)
        with args.leftover_output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=output_fields)
            writer.writeheader()
            for row, reason in leftovers:
                out = dict(row)
                out["balance_rank"] = ""
                out["selection_reason"] = reason
                writer.writerow(out)

    print(
        "selected="
        f"{len(selected)} leftover={len(leftovers)} "
        f"categories={dict(sorted(category_counts.items()))} "
        f"max_per_knowledge={args.max_per_knowledge}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
