#!/usr/bin/env python3
"""Normalize raw model outputs into DynaKnow prediction JSONL."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


VALID = {"A", "B", "C", "D"}
LETTER_PATTERNS = [
    re.compile(r"^\s*([ABCD])\s*$", re.IGNORECASE),
    re.compile(r"^\s*([ABCD])[\).:\-]\s*", re.IGNORECASE),
    re.compile(r"\banswer\s*(?:is|:)?\s*([ABCD])\b", re.IGNORECASE),
    re.compile(r"\boption\s*([ABCD])\b", re.IGNORECASE),
    re.compile(r"\b([ABCD])\b", re.IGNORECASE),
]


def extract_answer(text: object) -> tuple[str, str]:
    raw = str(text or "").strip()
    for pattern in LETTER_PATTERNS:
        match = pattern.search(raw)
        if match:
            answer = match.group(1).upper()
            if answer in VALID:
                return answer, "letter_pattern"
    return "uncertain", "no_valid_letter"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--response-field", default="response")
    parser.add_argument("--default-mode", default="full_video")
    args = parser.parse_args()

    rows = []
    with args.input.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            response = row.get(args.response_field, row.get("model_output", row.get("text", "")))
            answer, parse_status = extract_answer(response)
            rows.append(
                {
                    "video_id": row.get("video_id", ""),
                    "mode": row.get("mode", args.default_mode),
                    "predicted_answer": answer,
                    "parse_status": parse_status,
                    "raw_response": response,
                    "source_line": line_no,
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"wrote {len(rows)} normalized predictions to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
