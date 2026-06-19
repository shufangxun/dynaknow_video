#!/usr/bin/env python3
"""Score VDCR multiple-choice predictions."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


VALID = {"A", "B", "C", "D"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def prediction_text(row: dict[str, Any]) -> str:
    for key in ["predicted_answer", "answer", "prediction", "output", "raw_response"]:
        value = row.get(key)
        if value:
            return str(value)
    return ""


def extract_choice(text: object) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        for key in ["answer", "predicted_answer", "choice"]:
            value = str(parsed.get(key, "")).strip().upper()
            if value in VALID:
                return value

    cleaned = raw.strip().upper()
    if cleaned in VALID:
        return cleaned
    patterns = [
        r"\b(?:ANSWER|CHOICE|OPTION|答案|选项)\s*(?:IS|:|：)?\s*([ABCD])\b",
        r"\b([ABCD])\s*(?:\.|、|\)|）)",
    ]
    for pattern in patterns:
        match = re.search(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return ""


def pct(num: int, den: int) -> str:
    return "0.0%" if den == 0 else f"{100.0 * num / den:.1f}%"


def score_rows(gold_rows: list[dict[str, Any]], pred_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    gold_by_id = {row["video_id"]: row for row in gold_rows}
    scored: list[dict[str, Any]] = []
    missing_gold: list[str] = []
    by_domain_total: Counter[str] = Counter()
    by_domain_correct: Counter[str] = Counter()
    by_type_total: Counter[str] = Counter()
    by_type_correct: Counter[str] = Counter()

    for pred in pred_rows:
        video_id = pred.get("video_id", "")
        gold = gold_by_id.get(video_id)
        if not gold:
            missing_gold.append(str(video_id))
            continue
        predicted = extract_choice(prediction_text(pred))
        correct = predicted == gold.get("answer")
        domain = str(gold.get("domain", ""))
        concept = gold.get("concept", {})
        concept_type = str(concept.get("type", "")) if isinstance(concept, dict) else ""
        by_domain_total[domain] += 1
        by_domain_correct[domain] += int(correct)
        by_type_total[concept_type] += 1
        by_type_correct[concept_type] += int(correct)
        scored.append(
            {
                "video_id": video_id,
                "correct": correct,
                "predicted_answer": predicted,
                "raw_prediction": prediction_text(pred),
                "gold_answer": gold.get("answer", ""),
                "gold_choice_text": gold.get("choices", {}).get(gold.get("answer", ""), ""),
                "choices": gold.get("choices", {}),
                "domain": domain,
                "concept_type": concept_type,
                "parse_status": "ok" if predicted else "invalid",
            }
        )

    correct_total = sum(1 for row in scored if row["correct"])
    invalid = sum(1 for row in scored if row["parse_status"] != "ok")
    return scored, {
        "total": len(scored),
        "correct": correct_total,
        "invalid": invalid,
        "missing_gold": missing_gold,
        "by_domain_total": by_domain_total,
        "by_domain_correct": by_domain_correct,
        "by_type_total": by_type_total,
        "by_type_correct": by_type_correct,
    }


def write_report(path: Path, summary: dict[str, Any]) -> None:
    lines = ["# VDCR MCQ Score", ""]
    lines.append(f"- predictions scored: {summary['total']}")
    lines.append(f"- predictions missing gold: {len(summary['missing_gold'])}")
    lines.append(f"- invalid predictions: {summary['invalid']}")
    lines.append(f"- accuracy: {summary['correct']}/{summary['total']} ({pct(summary['correct'], summary['total'])})")
    lines.append("")
    lines.append("## Accuracy By Domain")
    lines.append("")
    for domain in sorted(summary["by_domain_total"]):
        total = summary["by_domain_total"][domain]
        correct = summary["by_domain_correct"][domain]
        lines.append(f"- `{domain}`: {correct}/{total} ({pct(correct, total)})")
    lines.append("")
    lines.append("## Accuracy By Concept Type")
    lines.append("")
    for concept_type in sorted(summary["by_type_total"]):
        total = summary["by_type_total"][concept_type]
        correct = summary["by_type_correct"][concept_type]
        lines.append(f"- `{concept_type}`: {correct}/{total} ({pct(correct, total)})")
    if summary["missing_gold"]:
        lines.append("")
        lines.append("## Missing Gold")
        lines.extend(f"- `{video_id}`" for video_id in summary["missing_gold"][:50])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    scored, summary = score_rows(read_jsonl(args.gold), read_jsonl(args.predictions))
    write_report(args.output, summary)
    scored_output = args.output.with_suffix(".scored.jsonl")
    with scored_output.open("w", encoding="utf-8") as handle:
        for row in scored:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"wrote score report to {args.output}")
    print(f"wrote scored rows to {scored_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
