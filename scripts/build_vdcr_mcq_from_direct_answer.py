#!/usr/bin/env python3
"""Build hard-negative MCQ items from VDCR direct-answer samples."""

from __future__ import annotations

import argparse
import json
import random
import re
import unicodedata
from pathlib import Path
from typing import Any


LETTERS = ["A", "B", "C", "D"]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def canonical(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = re.sub(r"[\s_\-/、，,;:()（）]+", " ", text)
    text = re.sub(r"[^0-9a-z\u4e00-\u9fff ]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def aliases(row: dict[str, Any]) -> set[str]:
    values = {row.get("answer", "")}
    values.update(row.get("accepted_answers", []))
    concept = row.get("concept", {})
    if isinstance(concept, dict):
        values.add(concept.get("en", ""))
        values.add(concept.get("zh", ""))
        values.add(concept.get("original_en", ""))
    return {key for value in values if (key := canonical(value))}


def concept_type(row: dict[str, Any]) -> str:
    concept = row.get("concept", {})
    if isinstance(concept, dict):
        return str(concept.get("type", ""))
    return ""


def distractor_rank(row: dict[str, Any], candidate: dict[str, Any]) -> tuple[int, int, int]:
    return (
        0 if candidate.get("domain", "") == row.get("domain", "") else 1,
        0 if candidate.get("subdomain", "") == row.get("subdomain", "") else 1,
        0 if concept_type(candidate) == concept_type(row) else 1,
    )


def choose_distractors(rows: list[dict[str, Any]], row: dict[str, Any], seed: int) -> list[dict[str, Any]]:
    gold_aliases = aliases(row)
    seen_answers = set(gold_aliases)
    candidates: list[dict[str, Any]] = []
    for candidate in rows:
        if candidate.get("video_id") == row.get("video_id"):
            continue
        answer = str(candidate.get("answer", "")).strip()
        answer_key = canonical(answer)
        if not answer or not answer_key or answer_key in seen_answers:
            continue
        if aliases(candidate) & gold_aliases:
            continue
        candidates.append(candidate)
        seen_answers.add(answer_key)
    candidates.sort(key=lambda candidate: distractor_rank(row, candidate))
    if len(candidates) < 3:
        raise ValueError(f"{row.get('video_id')}: needs at least 3 distractors, found {len(candidates)}")
    return candidates[:3]


def build_mcq_rows(rows: list[dict[str, Any]], seed: int = 20260619) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        distractors = choose_distractors(rows, row, seed)
        correct = str(row.get("answer", "")).strip()
        options = [correct, *[str(item.get("answer", "")).strip() for item in distractors]]
        rng = random.Random(f"{seed}:{row.get('video_id', '')}")
        rng.shuffle(options)
        answer = LETTERS[options.index(correct)]
        choices = {letter: option for letter, option in zip(LETTERS, options, strict=True)}
        output.append(
            {
                "video_id": row.get("video_id", ""),
                "mode": "full_video_mcq",
                "question": row.get(
                    "question",
                    "Which named dynamic concept is instantiated by the temporally evolving process in this video?",
                ),
                "choices": choices,
                "answer": answer,
                "gold_answer": correct,
                "accepted_answers": row.get("accepted_answers", []),
                "concept": row.get("concept", {}),
                "domain": row.get("domain", ""),
                "subdomain": row.get("subdomain", ""),
                "local_media": row.get("local_media", ""),
                "split": row.get("split", ""),
                "dynamic_evidence": row.get("dynamic_evidence", []),
                "static_insufficient_reason": row.get("static_insufficient_reason", ""),
                "mcq_metadata": {
                    "source": "vdcr_direct_answer",
                    "seed": seed,
                    "distractor_policy": "prefer_same_domain_then_subdomain_then_concept_type",
                    "distractor_source_video_ids": [str(item.get("video_id", "")) for item in distractors],
                    "distractor_gold_answers": [str(item.get("answer", "")) for item in distractors],
                },
            }
        )
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=20260619)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    rows = read_jsonl(args.input)
    if args.limit is not None:
        rows = rows[: args.limit]
    mcq_rows = build_mcq_rows(rows, seed=args.seed)
    write_jsonl(args.output, mcq_rows)
    print(f"wrote {len(mcq_rows)} MCQ rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
