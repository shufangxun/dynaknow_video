#!/usr/bin/env python3
"""Score DynaKnow prediction JSONL files."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


VALID_ANSWERS = {"A", "B", "C", "D"}


def normalize_answer(value: object) -> str:
    text = str(value or "").strip().upper()
    if text in VALID_ANSWERS:
        return text
    if text.startswith(("A", "B", "C", "D")):
        return text[0]
    return "uncertain"


def read_gold(path: Path, answer_field: str) -> dict[tuple[str, str], str]:
    gold = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            mode = row.get("mode", "full_video")
            gold[(row["video_id"], mode)] = row[answer_field]
    return gold


def read_predictions(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def pct(num: int, den: int) -> str:
    return "0.0%" if den == 0 else f"{100.0 * num / den:.1f}%"


def accuracy(correct: int, total: int) -> float:
    return 0.0 if total == 0 else correct / total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--gold-answer-field", default="answer")
    args = parser.parse_args()

    gold = read_gold(args.gold, args.gold_answer_field)
    predictions = read_predictions(args.predictions)
    by_mode_total: Counter[str] = Counter()
    by_mode_correct: Counter[str] = Counter()
    by_video_modes: dict[str, dict[str, bool]] = defaultdict(dict)
    missing_gold = []

    scored_rows = []
    for row in predictions:
        video_id = row.get("video_id", "")
        mode = row.get("mode", "full_video")
        key = (video_id, mode)
        if key not in gold:
            missing_gold.append({"video_id": video_id, "mode": mode})
            continue
        pred = normalize_answer(row.get("predicted_answer", row.get("answer", "")))
        is_correct = pred == gold[key]
        by_mode_total[mode] += 1
        by_mode_correct[mode] += int(is_correct)
        by_video_modes[video_id][mode] = is_correct
        scored_rows.append(
            {
                "video_id": video_id,
                "mode": mode,
                "gold_answer": gold[key],
                "predicted_answer": pred,
                "correct": is_correct,
            }
        )

    lines = ["# DynaKnow Prediction Score", ""]
    lines.append(f"- predictions scored: {len(scored_rows)}")
    lines.append(f"- predictions missing gold: {len(missing_gold)}")
    lines.append("")
    lines.append("## Accuracy By Mode")
    lines.append("")

    mode_accuracy = {}
    for mode in sorted(by_mode_total):
        correct = by_mode_correct[mode]
        total = by_mode_total[mode]
        mode_accuracy[mode] = accuracy(correct, total)
        lines.append(f"- `{mode}`: {correct}/{total} ({pct(correct, total)})")

    full_video_acc = mode_accuracy.get("full_video")
    if full_video_acc is not None:
        shortcut_modes = [mode for mode in mode_accuracy if mode != "full_video"]
        best_shortcut = max((mode_accuracy[mode] for mode in shortcut_modes), default=0.0)
        lines.append("")
        lines.append("## Dynamic Necessity Gap")
        lines.append("")
        lines.append(f"- full_video_accuracy: {full_video_acc:.3f}")
        lines.append(f"- best_shortcut_accuracy: {best_shortcut:.3f}")
        lines.append(f"- dynamic_necessity_gap: {full_video_acc - best_shortcut:.3f}")

    if missing_gold:
        lines.append("")
        lines.append("## Missing Gold Rows")
        lines.append("")
        for row in missing_gold[:50]:
            lines.append(f"- {row['video_id']} / {row['mode']}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")

    scored_output = args.output.with_suffix(".scored.jsonl")
    with scored_output.open("w", encoding="utf-8") as handle:
        for row in scored_rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(f"wrote score report to {args.output}")
    print(f"wrote scored rows to {scored_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
