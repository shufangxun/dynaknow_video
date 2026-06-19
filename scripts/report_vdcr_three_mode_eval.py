#!/usr/bin/env python3
"""Summarize VDCR exact naming, description understanding, and MCQ results."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Any


EXACT_RE = re.compile(r"- accuracy: (?P<correct>\d+)/(?P<total>\d+) \((?P<acc>[0-9.]+)%\)")
DESC_RE = re.compile(r"- description understanding accuracy: (?P<correct>\d+)/(?P<total>\d+) \((?P<acc>[0-9.]+)%\)")


def parse_key_value(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"expected NAME=VALUE, got {value!r}")
    key, raw = value.split("=", 1)
    if not key or not raw:
        raise argparse.ArgumentTypeError(f"expected NAME=VALUE, got {value!r}")
    return key, raw


def parse_metric(path: Path, pattern: re.Pattern[str]) -> dict[str, int | float]:
    text = path.read_text(encoding="utf-8")
    match = pattern.search(text)
    if not match:
        raise ValueError(f"could not parse metric from {path}")
    correct = int(match.group("correct"))
    total = int(match.group("total"))
    return {"correct": correct, "total": total, "accuracy": correct / total if total else 0.0}


def format_pct(value: float) -> str:
    return f"{100.0 * value:.1f}%"


def build_rows(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in specs:
        exact = parse_metric(Path(spec["exact"]), EXACT_RE)
        desc = parse_metric(Path(spec["description"]), DESC_RE)
        mcq = parse_metric(Path(spec["mcq"]), EXACT_RE)
        totals = {int(exact["total"]), int(desc["total"]), int(mcq["total"])}
        if len(totals) != 1:
            raise ValueError(f"{spec['run']}: report totals disagree: {sorted(totals)}")
        total = int(exact["total"])
        rows.append(
            {
                "run": spec["run"],
                "params_b": spec.get("params_b"),
                "total": total,
                "exact_correct": int(exact["correct"]),
                "exact_accuracy": float(exact["accuracy"]),
                "description_correct": int(desc["correct"]),
                "description_accuracy": float(desc["accuracy"]),
                "mcq_correct": int(mcq["correct"]),
                "mcq_accuracy": float(mcq["accuracy"]),
            }
        )
    rows.sort(key=lambda row: (float("inf") if row["params_b"] is None else float(row["params_b"]), row["run"]))
    return rows


def write_markdown(path: Path, rows: list[dict[str, Any]], notes: list[str]) -> None:
    lines = ["# VDCR Three-Mode Evaluation Summary", ""]
    lines.append("| run | params_b | total | open exact naming | open description judge | MCQ recognition |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in rows:
        params = "" if row["params_b"] is None else f"{float(row['params_b']):g}"
        total = row["total"]
        lines.append(
            f"| {row['run']} | {params} | {total} | "
            f"{row['exact_correct']}/{total} ({format_pct(row['exact_accuracy'])}) | "
            f"{row['description_correct']}/{total} ({format_pct(row['description_accuracy'])}) | "
            f"{row['mcq_correct']}/{total} ({format_pct(row['mcq_accuracy'])}) |"
        )
    lines.extend(
        [
            "",
            "## Metric Definitions",
            "",
            "- `open exact naming`: open-ended answer must match the canonical concept name or accepted aliases after normalization.",
            "- `open description judge`: open-ended response may be a short mechanism description; an LLM judge gives credit only if the response distinguishes the gold dynamic mechanism, not merely a broad caption.",
            "- `MCQ recognition`: four-choice constructed item scored by selected option letter only.",
        ]
    )
    if notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in notes)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "run",
        "params_b",
        "total",
        "exact_correct",
        "exact_accuracy",
        "description_correct",
        "description_accuracy",
        "mcq_correct",
        "mcq_accuracy",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="append", required=True, type=parse_key_value, help="Run label and params, e.g. qwen35_2b=2")
    parser.add_argument("--exact", action="append", required=True, type=parse_key_value)
    parser.add_argument("--description", action="append", required=True, type=parse_key_value)
    parser.add_argument("--mcq", action="append", required=True, type=parse_key_value)
    parser.add_argument("--note", action="append", default=[])
    parser.add_argument("--output-md", required=True, type=Path)
    parser.add_argument("--output-csv", type=Path, default=None)
    args = parser.parse_args()

    params = {name: float(value) for name, value in args.run}
    exact = dict(args.exact)
    description = dict(args.description)
    mcq = dict(args.mcq)
    specs = []
    for run in params:
        missing = [name for name, source in [("exact", exact), ("description", description), ("mcq", mcq)] if run not in source]
        if missing:
            raise SystemExit(f"{run}: missing {', '.join(missing)} report")
        specs.append(
            {
                "run": run,
                "params_b": params[run],
                "exact": Path(exact[run]),
                "description": Path(description[run]),
                "mcq": Path(mcq[run]),
            }
        )
    rows = build_rows(specs)
    write_markdown(args.output_md, rows, args.note)
    print(f"wrote three-mode summary to {args.output_md}")
    if args.output_csv:
        write_csv(args.output_csv, rows)
        print(f"wrote three-mode csv to {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
