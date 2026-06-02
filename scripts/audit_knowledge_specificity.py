#!/usr/bin/env python3
"""Audit DynaKnow samples for overly broad knowledge-point wording."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


BROAD_PATTERNS = [
    re.compile(r"\bsome chemical reactions?\b", re.IGNORECASE),
    re.compile(r"\bsome reactions?\b", re.IGNORECASE),
    re.compile(r"\bsome mixtures?\b", re.IGNORECASE),
    re.compile(r"\bcan cause (a )?(change|movement|effect)\b", re.IGNORECASE),
    re.compile(r"\bproduce color change\b", re.IGNORECASE),
    re.compile(r"\bform a precipitate\b", re.IGNORECASE),
]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def find_broad_text(text: str) -> str | None:
    for pattern in BROAD_PATTERNS:
        if pattern.search(text):
            return pattern.pattern
    return None


def audit_row(path: Path, line_no: int, row: dict) -> list[str]:
    errors = []
    video_id = row.get("video_id", f"line_{line_no}")
    fields = [("knowledge_point", row.get("knowledge_point", ""))]
    choices = row.get("choices", {})
    answer = row.get("answer") or row.get("gold_answer")
    if isinstance(choices, dict) and answer in choices:
        fields.append((f"choices.{answer}", choices[answer]))

    for field, value in fields:
        if not isinstance(value, str):
            continue
        matched = find_broad_text(value)
        if matched:
            errors.append(
                f"{path}:{line_no}: {video_id}: broad {field}: {value!r} "
                f"(matched {matched!r})"
            )
    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", type=Path)
    args = parser.parse_args(argv[1:])

    errors: list[str] = []
    with args.jsonl.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            errors.extend(audit_row(args.jsonl, line_no, row))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK: {args.jsonl} passed knowledge-specificity audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
