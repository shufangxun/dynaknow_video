#!/usr/bin/env python3
"""Apply VDCR V2 local triage decisions back to the review queue."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ACTION_BY_DECISION = {
    "pass_candidate": "candidate_ready_for_v2_draft",
    "revise": "revise_or_trim_before_draft",
    "reject": "do_not_use_for_v2",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fields} for row in rows])


def append_triage_note(existing: str, decision: str, reviewer_notes: str) -> str:
    note = f"triage_decision={decision}"
    if reviewer_notes:
        note = f"{note}; triage_notes={reviewer_notes}"
    if not existing:
        return note
    if "triage_decision=" in existing:
        return existing
    return f"{existing} | {note}"


def apply_triage_decisions(
    review_rows: list[dict[str, str]],
    triage_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    decisions = {
        row.get("candidate_id", ""): row
        for row in triage_rows
        if row.get("candidate_id", "") and row.get("reviewer_decision", "") in ACTION_BY_DECISION
    }
    output: list[dict[str, str]] = []
    for row in review_rows:
        updated = dict(row)
        candidate_id = updated.get("candidate_id") or updated.get("id", "")
        triage = decisions.get(candidate_id)
        if triage:
            decision = triage.get("reviewer_decision", "")
            updated["review_status"] = decision
            updated["recommended_action"] = ACTION_BY_DECISION[decision]
            updated["review_notes"] = append_triage_note(
                updated.get("review_notes", ""),
                decision,
                triage.get("reviewer_notes", ""),
            )
        output.append(updated)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-queue", type=Path, default=Path("data/vdcr_v2_review_queue.csv"))
    parser.add_argument("--triage", type=Path, default=Path("data/vdcr_v2_local_review_triage.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/vdcr_v2_review_queue.csv"))
    args = parser.parse_args()

    review_rows = read_csv(args.review_queue)
    fieldnames = list(review_rows[0].keys()) if review_rows else []
    updated = apply_triage_decisions(review_rows, read_csv(args.triage))
    write_csv(args.output, updated, fieldnames)
    changed = sum(1 for before, after in zip(review_rows, updated) if before != after)
    print(f"updated_review_rows={changed} wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
