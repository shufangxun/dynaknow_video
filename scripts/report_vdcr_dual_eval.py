#!/usr/bin/env python3
"""Summarize VDCR direct-answer judge and MCQ results in one table."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any


ACCURACY_RE = re.compile(r"- accuracy: (?P<correct>\d+)/(?P<total>\d+) \((?P<acc>[0-9.]+)%\)")
SEMANTIC_RE = re.compile(r"- semantic accuracy: (?P<correct>\d+)/(?P<total>\d+) \((?P<acc>[0-9.]+)%\)")


def parse_key_value(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"expected NAME=VALUE, got {value!r}")
    key, raw = value.split("=", 1)
    if not key or not raw:
        raise argparse.ArgumentTypeError(f"expected NAME=VALUE, got {value!r}")
    return key, raw


def parse_metric(path: Path, semantic: bool = False) -> dict[str, int | float]:
    text = path.read_text(encoding="utf-8")
    pattern = SEMANTIC_RE if semantic else ACCURACY_RE
    match = pattern.search(text)
    if not match:
        raise ValueError(f"could not parse accuracy from {path}")
    correct = int(match.group("correct"))
    total = int(match.group("total"))
    return {
        "correct": correct,
        "total": total,
        "accuracy": correct / total if total else 0.0,
    }


def build_summary_rows(run_specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in run_specs:
        exact = parse_metric(Path(spec["direct_exact"]), semantic=False)
        semantic = parse_metric(Path(spec["direct_semantic"]), semantic=True)
        mcq = parse_metric(Path(spec["mcq"]), semantic=False)
        totals = {int(exact["total"]), int(semantic["total"]), int(mcq["total"])}
        if len(totals) != 1:
            raise ValueError(f"{spec['run']}: report totals disagree: {sorted(totals)}")
        rows.append(
            {
                "run": spec["run"],
                "params_b": spec.get("params_b"),
                "direct_exact_accuracy": float(exact["accuracy"]),
                "direct_semantic_accuracy": float(semantic["accuracy"]),
                "mcq_accuracy": float(mcq["accuracy"]),
                "direct_exact_correct": int(exact["correct"]),
                "direct_semantic_correct": int(semantic["correct"]),
                "mcq_correct": int(mcq["correct"]),
                "total": int(exact["total"]),
            }
        )
    rows.sort(key=lambda row: (float("inf") if row["params_b"] is None else float(row["params_b"]), row["run"]))
    return rows


def format_pct(value: float) -> str:
    return f"{100.0 * value:.1f}%"


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = ["# VDCR Dual-Mode Evaluation Summary", ""]
    lines.append("| run | params_b | total | direct_exact | direct_llm_judge | mcq |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in rows:
        params = "" if row["params_b"] is None else f"{float(row['params_b']):g}"
        lines.append(
            f"| {row['run']} | {params} | {row['total']} | "
            f"{row['direct_exact_correct']}/{row['total']} ({format_pct(row['direct_exact_accuracy'])}) | "
            f"{row['direct_semantic_correct']}/{row['total']} ({format_pct(row['direct_semantic_accuracy'])}) | "
            f"{row['mcq_correct']}/{row['total']} ({format_pct(row['mcq_accuracy'])}) |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `direct_exact` uses alias-normalized exact matching.",
            "- `direct_llm_judge` uses an LLM judge against the reference answer and accepted aliases.",
            "- `mcq` uses constructed four-choice items with hard negatives derived from the direct-answer reference set.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "run",
        "params_b",
        "total",
        "direct_exact_correct",
        "direct_exact_accuracy",
        "direct_semantic_correct",
        "direct_semantic_accuracy",
        "mcq_correct",
        "mcq_accuracy",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="append", required=True, type=parse_key_value, help="Run label and params, e.g. qwen3vl_2b=2")
    parser.add_argument("--direct-exact", action="append", required=True, type=parse_key_value)
    parser.add_argument("--direct-semantic", action="append", required=True, type=parse_key_value)
    parser.add_argument("--mcq", action="append", required=True, type=parse_key_value)
    parser.add_argument("--output-md", required=True, type=Path)
    parser.add_argument("--output-csv", type=Path, default=None)
    args = parser.parse_args()

    params = {name: float(value) for name, value in args.run}
    exact = dict(args.direct_exact)
    semantic = dict(args.direct_semantic)
    mcq = dict(args.mcq)
    specs = []
    for run in params:
        missing = [name for name, source in [("direct-exact", exact), ("direct-semantic", semantic), ("mcq", mcq)] if run not in source]
        if missing:
            raise SystemExit(f"{run}: missing {', '.join(missing)} report")
        specs.append(
            {
                "run": run,
                "params_b": params[run],
                "direct_exact": Path(exact[run]),
                "direct_semantic": Path(semantic[run]),
                "mcq": Path(mcq[run]),
            }
        )

    rows = build_summary_rows(specs)
    write_markdown(args.output_md, rows)
    print(f"wrote dual evaluation summary to {args.output_md}")
    if args.output_csv:
        write_csv(args.output_csv, rows)
        print(f"wrote dual evaluation csv to {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
