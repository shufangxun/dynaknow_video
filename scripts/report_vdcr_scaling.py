#!/usr/bin/env python3
"""Summarize VDCR score reports as a small model-scaling table."""

from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path


ACCURACY_RE = re.compile(r"- accuracy: (?P<correct>\d+)/(?P<total>\d+) \((?P<acc>[0-9.]+)%\)")
DOMAIN_RE = re.compile(r"- `(?P<name>[^`]+)`: (?P<correct>\d+)/(?P<total>\d+) \((?P<acc>[0-9.]+)%\)")


def parse_key_value(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(f"expected NAME=VALUE, got {value!r}")
    key, raw = value.split("=", 1)
    if not key or not raw:
        raise argparse.ArgumentTypeError(f"expected NAME=VALUE, got {value!r}")
    return key, raw


def parse_score(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    match = ACCURACY_RE.search(text)
    if not match:
        raise ValueError(f"could not parse accuracy line from {path}")
    domains: dict[str, dict[str, float | int]] = {}
    in_domain_section = False
    for line in text.splitlines():
        if line.strip() == "## Accuracy By Domain":
            in_domain_section = True
            continue
        if in_domain_section and line.startswith("## "):
            break
        if in_domain_section and (domain_match := DOMAIN_RE.match(line)):
            total = int(domain_match.group("total"))
            correct = int(domain_match.group("correct"))
            domains[domain_match.group("name")] = {
                "correct": correct,
                "total": total,
                "accuracy": correct / total if total else 0.0,
            }
    total = int(match.group("total"))
    correct = int(match.group("correct"))
    return {
        "correct": correct,
        "total": total,
        "accuracy": correct / total if total else 0.0,
        "domains": domains,
    }


def format_pct(value: float) -> str:
    return f"{100.0 * value:.1f}%"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="append", required=True, type=parse_key_value, help="Run label and score path, e.g. qwen3vl_2b=reports/score.md")
    parser.add_argument("--params-b", action="append", default=[], type=parse_key_value, help="Run label and parameter count in billions, e.g. qwen3vl_2b=2")
    parser.add_argument("--output-md", required=True, type=Path)
    parser.add_argument("--output-csv", type=Path, default=None)
    args = parser.parse_args()

    params_by_run = {name: float(value) for name, value in args.params_b}
    rows = []
    for run_name, score_path in args.run:
        parsed = parse_score(Path(score_path))
        total = int(parsed["total"])
        correct = int(parsed["correct"])
        accuracy = float(parsed["accuracy"])
        error_rate = 1.0 - accuracy
        rows.append(
            {
                "run": run_name,
                "params_b": params_by_run.get(run_name),
                "score_path": score_path,
                "correct": correct,
                "total": total,
                "accuracy": accuracy,
                "error_rate": error_rate,
                "domains": parsed["domains"],
            }
        )

    rows.sort(key=lambda row: (float("inf") if row["params_b"] is None else row["params_b"], row["run"]))

    lines = ["# VDCR Scaling Summary", ""]
    lines.append("| run | params_b | correct | total | accuracy | error_rate |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in rows:
        params = "" if row["params_b"] is None else f"{row['params_b']:g}"
        lines.append(
            f"| {row['run']} | {params} | {row['correct']} | {row['total']} | "
            f"{format_pct(row['accuracy'])} | {format_pct(row['error_rate'])} |"
        )

    fit_rows = [row for row in rows if row["params_b"] and row["error_rate"] > 0]
    if len(fit_rows) >= 2:
        first = fit_rows[0]
        last = fit_rows[-1]
        slope = math.log(last["error_rate"] / first["error_rate"]) / math.log(last["params_b"] / first["params_b"])
        lines.extend(
            [
                "",
                "## Two-Point Error Scaling",
                "",
                f"- slope from `{first['run']}` to `{last['run']}`: `{slope:.3f}` for error_rate vs params_b",
                f"- relative error change: `{(last['error_rate'] / first['error_rate'] - 1.0) * 100.0:.1f}%`",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Two-Point Error Scaling",
                "",
                "- skipped: at least two runs with non-zero error_rate and known params_b are required.",
            ]
        )

    domain_names = sorted({name for row in rows for name in row["domains"]})
    if domain_names:
        lines.extend(["", "## Accuracy By Domain", ""])
        header = "| run | " + " | ".join(domain_names) + " |"
        lines.append(header)
        lines.append("|---|" + "|".join("---:" for _ in domain_names) + "|")
        for row in rows:
            cells = []
            domains = row["domains"]
            for name in domain_names:
                metric = domains.get(name)
                cells.append("" if metric is None else format_pct(float(metric["accuracy"])))
            lines.append(f"| {row['run']} | " + " | ".join(cells) + " |")

    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if args.output_csv:
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.output_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["run", "params_b", "correct", "total", "accuracy", "error_rate", "score_path"])
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row[key] for key in writer.fieldnames})

    print(f"wrote scaling summary to {args.output_md}")
    if args.output_csv:
        print(f"wrote scaling csv to {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
