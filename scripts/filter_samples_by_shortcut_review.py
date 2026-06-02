#!/usr/bin/env python3
"""Filter DynaKnow JSONL samples using human shortcut review decisions."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ACCEPT_DECISIONS = {"accept_dynamic_seed"}


def load_reviews(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["video_id"]: row for row in csv.DictReader(handle)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--accepted-output", required=True, type=Path)
    parser.add_argument("--rejected-output", required=True, type=Path)
    args = parser.parse_args()

    reviews = load_reviews(args.review)
    accepted = 0
    rejected = 0
    args.accepted_output.parent.mkdir(parents=True, exist_ok=True)
    args.rejected_output.parent.mkdir(parents=True, exist_ok=True)
    with args.samples.open("r", encoding="utf-8") as src, args.accepted_output.open("w", encoding="utf-8") as acc, args.rejected_output.open("w", encoding="utf-8") as rej:
        for line in src:
            if not line.strip():
                continue
            sample = json.loads(line)
            video_id = sample["video_id"]
            review = reviews.get(video_id)
            if not review:
                continue
            sample["shortcut_human_review"] = review
            decision = review["decision"]
            text_leakage = review.get("ocr_leakage_status", "").lower()
            if text_leakage in {"fail", "direct_leak", "target_text_present"}:
                sample["review"]["decision"] = "reject"
                sample["review"]["subtitle_leakage_status"] = "fail"
                rej.write(json.dumps(sample, ensure_ascii=False) + "\n")
                rejected += 1
            elif decision in ACCEPT_DECISIONS:
                sample["shortcut_results"]["answer_only"] = "pass" if review["answer_only_leakage"] == "low" else "fail"
                sample["shortcut_results"]["single_frame"] = "pass" if review["single_frame_sufficient"] == "no" else "fail"
                sample["shortcut_results"]["sparse_frame"] = "fail" if review["sparse_frames_sufficient"] == "yes" else "pass"
                sample["review"]["answer_leakage_status"] = sample["shortcut_results"]["answer_only"]
                if text_leakage in {"pass", "none", "low"}:
                    sample["review"]["subtitle_leakage_status"] = "pass"
                sample["review"]["decision"] = "revise"
                acc.write(json.dumps(sample, ensure_ascii=False) + "\n")
                accepted += 1
            else:
                sample["review"]["decision"] = "reject" if decision.startswith("reject") else "revise"
                rej.write(json.dumps(sample, ensure_ascii=False) + "\n")
                rejected += 1
    print(f"accepted={accepted} rejected_or_revise={rejected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
