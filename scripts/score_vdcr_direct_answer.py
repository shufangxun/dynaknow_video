#!/usr/bin/env python3
"""Score VDCR direct-answer predictions with alias normalization."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = re.sub(r"[\s_\-/、，,;:()（）]+", " ", text)
    text = re.sub(r"[^0-9a-z\u4e00-\u9fff ]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def gold_answers(row: dict[str, Any]) -> set[str]:
    answers = {row.get("answer", "")}
    answers.update(row.get("accepted_answers", []))
    concept = row.get("concept", {})
    if isinstance(concept, dict):
        answers.add(concept.get("zh", ""))
        answers.add(concept.get("en", ""))
    return {norm for answer in answers if (norm := normalize(answer))}


def prediction_answer(row: dict[str, Any]) -> str:
    for key in ["predicted_answer", "answer", "prediction", "output"]:
        if row.get(key):
            return str(row[key])
    return ""


def pct(num: int, den: int) -> str:
    return "0.0%" if den == 0 else f"{100.0 * num / den:.1f}%"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    gold_rows = read_jsonl(args.gold)
    pred_rows = read_jsonl(args.predictions)
    gold_by_id = {row["video_id"]: row for row in gold_rows}

    scored = []
    missing_gold = []
    by_domain_total: Counter[str] = Counter()
    by_domain_correct: Counter[str] = Counter()
    by_type_total: Counter[str] = Counter()
    by_type_correct: Counter[str] = Counter()

    for pred in pred_rows:
        video_id = pred.get("video_id", "")
        gold = gold_by_id.get(video_id)
        if not gold:
            missing_gold.append(video_id)
            continue
        normalized_prediction = normalize(prediction_answer(pred))
        accepted = gold_answers(gold)
        correct = normalized_prediction in accepted
        domain = gold.get("domain", "")
        concept_type = gold.get("concept", {}).get("type", "")
        by_domain_total[domain] += 1
        by_domain_correct[domain] += int(correct)
        by_type_total[concept_type] += 1
        by_type_correct[concept_type] += int(correct)
        scored.append(
            {
                "video_id": video_id,
                "correct": correct,
                "predicted_answer": prediction_answer(pred),
                "normalized_prediction": normalized_prediction,
                "accepted_answers": sorted(accepted),
                "gold_answer": gold.get("answer", ""),
                "domain": domain,
                "concept_type": concept_type,
            }
        )

    correct_total = sum(1 for row in scored if row["correct"])
    lines = ["# VDCR Direct-Answer Score", ""]
    lines.append(f"- predictions scored: {len(scored)}")
    lines.append(f"- predictions missing gold: {len(missing_gold)}")
    lines.append(f"- accuracy: {correct_total}/{len(scored)} ({pct(correct_total, len(scored))})")
    lines.append("")
    lines.append("## Accuracy By Domain")
    lines.append("")
    for domain in sorted(by_domain_total):
        total = by_domain_total[domain]
        correct = by_domain_correct[domain]
        lines.append(f"- `{domain}`: {correct}/{total} ({pct(correct, total)})")
    lines.append("")
    lines.append("## Accuracy By Concept Type")
    lines.append("")
    for concept_type in sorted(by_type_total):
        total = by_type_total[concept_type]
        correct = by_type_correct[concept_type]
        lines.append(f"- `{concept_type}`: {correct}/{total} ({pct(correct, total)})")
    if missing_gold:
        lines.append("")
        lines.append("## Missing Gold")
        lines.extend(f"- `{video_id}`" for video_id in missing_gold[:50])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    scored_output = args.output.with_suffix(".scored.jsonl")
    with scored_output.open("w", encoding="utf-8") as handle:
        for row in scored:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(f"wrote score report to {args.output}")
    print(f"wrote scored rows to {scored_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
