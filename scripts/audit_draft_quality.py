#!/usr/bin/env python3
"""Audit DynaKnow draft samples for leakage, mapping, and balance risks."""

from __future__ import annotations

import argparse
import csv
import json
import re
import urllib.parse
from collections import Counter
from pathlib import Path


OUTPUT_FIELDS = [
    "video_id",
    "category",
    "knowledge_point",
    "answer",
    "source_title",
    "source_url",
    "prior_review_decision",
    "knowledge_point_seen_rank",
    "risk_score",
    "risk_flags",
    "recommendation",
    "notes",
]

TITLE_KEYWORDS_BY_KP = {
    "A pendulum exchanges gravitational potential energy and kinetic energy.": [
        "pendulum",
        "pendel",
        "pendule",
        "pendolo",
    ],
    "Magnetic fields can align or attract ferromagnetic materials.": [
        "magnet",
        "magnetic",
        "magneto",
        "magnetotactic",
    ],
    "Plant shoots can grow toward a light source.": [
        "phototropism",
        "phototropic",
    ],
    "Surface tension can support small objects or droplets.": [
        "surface tension",
    ],
    "Surface tension can support or reshape small liquid structures.": [
        "surface tension",
        "capillary",
    ],
    "Filtering separates solids from liquids by particle size.": [
        "filter",
        "filtration",
        "backwashing",
    ],
    "A solid can absorb heat and melt into a liquid.": [
        "melting",
        "melt",
    ],
    "Combustion requires fuel and oxygen.": [
        "combustion",
        "burning",
        "fire",
    ],
    "Elastic materials restore shape after deformation.": [
        "spring",
        "elastic",
    ],
}

SPECIALIST_TITLE_TERMS = [
    "nanoparticle",
    "molecular",
    "foldamer",
    "cell",
    "microscopy",
    "plos",
    "pone",
]

STATIC_EQUIPMENT_TERMS = [
    "pendulum",
    "filter",
    "filtration",
    "magnetic",
    "magnet",
]

ANIMATION_OR_SIMULATION_TERMS = [
    "animation",
    "anim",
    "simulation",
]

WRONG_MAPPING_PATTERNS = [
    (
        "Seed germination involves root and shoot emergence.",
        ["carnivorous", "drosera", "fruit fly", "apex", "reorientation", "365 days tree", "tree"],
        "plant_video_not_seed_germination",
    ),
    (
        "Plant shoots can grow toward a light source.",
        ["flower opening", "sunflower flower opening"],
        "plant_video_not_phototropism",
    ),
    (
        "A solid can absorb heat and melt into a liquid.",
        ["greenland", "arctic sea ice", "iceberg"],
        "remote_sensing_or_macro_ice_not_simple_phase_change",
    ),
    (
        "Pressure differences can move fluids.",
        ["plattenkondensator", "capacitor", "electric field"],
        "electric_field_flame_not_pressure_difference",
    ),
]

REJECT_DECISION_PREFIXES = ("reject_",)
REVISE_DECISION_PREFIXES = ("needs_",)


def source_title(source_url: str) -> str:
    if "/wiki/File:" not in source_url:
        return source_url.rsplit("/", 1)[-1]
    raw = source_url.split("/wiki/File:", 1)[1]
    return urllib.parse.unquote(raw).replace("_", " ")


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def contains_any(text: str, terms: list[str]) -> bool:
    padded = f" {norm(text)} "
    return any(f" {norm(term)} " in padded for term in terms)


def load_reviews(paths: list[Path]) -> dict[str, str]:
    reviews: dict[str, str] = {}
    for path in paths:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                video_id = row.get("video_id", "")
                decision = row.get("decision", "")
                if video_id and decision:
                    reviews[video_id] = decision
    return reviews


def load_media_failures(path: Path | None) -> set[str]:
    if not path or not path.exists():
        return set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row.get("video_id", "") for row in csv.DictReader(handle) if row.get("video_id", "")}


def read_samples(path: Path) -> list[dict]:
    samples = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                samples.append(json.loads(line))
    return samples


def audit_sample(
    sample: dict,
    prior_decision: str,
    seen_rank: int,
    max_per_knowledge: int,
    media_failures: set[str],
) -> dict[str, str]:
    title = source_title(sample["source_url"])
    title_norm = norm(title)
    point = sample["knowledge_point"]
    flags: list[str] = []
    notes: list[str] = []
    score = 0

    if prior_decision == "accept_dynamic_seed":
        flags.append("previously_accepted")
        notes.append("Already accepted in shortcut review.")
        recommendation = "keep_accepted"
        score = -10
    else:
        if prior_decision.startswith(REJECT_DECISION_PREFIXES):
            flags.append("previously_rejected")
            score += 100
            notes.append(f"Prior review decision: {prior_decision}.")
        elif prior_decision.startswith(REVISE_DECISION_PREFIXES):
            flags.append("previously_needs_revision")
            score += 45
            notes.append(f"Prior review decision: {prior_decision}.")

        if sample["video_id"] in media_failures:
            flags.append("known_media_download_failure")
            score += 100
            notes.append("Media download failed with current manifest URL.")

        if seen_rank > max_per_knowledge:
            flags.append("over_knowledge_point_cap")
            score += 50
            notes.append(f"Knowledge point rank {seen_rank} exceeds cap {max_per_knowledge}.")

        keywords = TITLE_KEYWORDS_BY_KP.get(point, [])
        if keywords and contains_any(title, keywords):
            flags.append("title_names_phenomenon")
            score += 55
            notes.append("Source title contains a keyword for the target phenomenon.")

        if contains_any(title, SPECIALIST_TITLE_TERMS):
            flags.append("specialist_context_or_title")
            score += 35
            notes.append("Source title suggests specialist context or paper-derived microscopy.")

        if contains_any(title, STATIC_EQUIPMENT_TERMS):
            flags.append("static_equipment_shortcut_risk")
            score += 15
            notes.append("Source title or object class may reveal the answer from static frames.")

        if contains_any(title, ANIMATION_OR_SIMULATION_TERMS):
            flags.append("animation_or_simulation")
            score += 30
            notes.append("Source title suggests animation/simulation rather than natural video evidence.")

        evidence_text = " ".join(span.get("description", "") for span in sample.get("dynamic_evidence", []))
        if "requires review" in evidence_text.lower():
            flags.append("auto_evidence_requires_review")
            score += 15
            notes.append("Dynamic evidence was auto-filled and requires manual verification.")

        for target_point, terms, flag in WRONG_MAPPING_PATTERNS:
            if point == target_point and contains_any(title_norm, terms):
                flags.append(flag)
                score += 80
                notes.append("Title strongly suggests the candidate was mapped to the wrong knowledge point.")

        if score >= 100:
            recommendation = "exclude"
        elif score >= 45:
            recommendation = "revise_or_manual_review"
        else:
            recommendation = "priority_review"

    return {
        "video_id": sample["video_id"],
        "category": sample["category"],
        "knowledge_point": point,
        "answer": sample["answer"],
        "source_title": title,
        "source_url": sample["source_url"],
        "prior_review_decision": prior_decision,
        "knowledge_point_seen_rank": str(seen_rank),
        "risk_score": str(score),
        "risk_flags": ";".join(flags),
        "recommendation": recommendation,
        "notes": " ".join(notes),
    }


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", required=True, type=Path)
    parser.add_argument("--review", action="append", type=Path, default=[])
    parser.add_argument("--audit-output", required=True, type=Path)
    parser.add_argument("--priority-output", required=True, type=Path)
    parser.add_argument("--new-priority-output", type=Path)
    parser.add_argument("--accepted-output", type=Path)
    parser.add_argument("--exclude-output", required=True, type=Path)
    parser.add_argument("--media-failures", type=Path)
    parser.add_argument("--max-per-knowledge", type=int, default=4)
    args = parser.parse_args()

    samples = read_samples(args.samples)
    reviews = load_reviews(args.review)
    media_failures = load_media_failures(args.media_failures)
    seen_by_knowledge: Counter[str] = Counter()

    audit_rows = []
    for sample in samples:
        seen_by_knowledge[sample["knowledge_point"]] += 1
        audit_rows.append(
            audit_sample(
                sample=sample,
                prior_decision=reviews.get(sample["video_id"], ""),
                seen_rank=seen_by_knowledge[sample["knowledge_point"]],
                max_per_knowledge=args.max_per_knowledge,
                media_failures=media_failures,
            )
        )

    priority_rows = [
        row
        for row in audit_rows
        if row["recommendation"] in {"priority_review", "keep_accepted"}
    ]
    new_priority_rows = [row for row in audit_rows if row["recommendation"] == "priority_review"]
    accepted_rows = [row for row in audit_rows if row["recommendation"] == "keep_accepted"]
    exclude_rows = [
        row
        for row in audit_rows
        if row["recommendation"] in {"exclude", "revise_or_manual_review"}
    ]

    write_rows(args.audit_output, audit_rows)
    write_rows(args.priority_output, priority_rows)
    if args.new_priority_output:
        write_rows(args.new_priority_output, new_priority_rows)
    if args.accepted_output:
        write_rows(args.accepted_output, accepted_rows)
    write_rows(args.exclude_output, exclude_rows)

    summary = Counter(row["recommendation"] for row in audit_rows)
    print(f"audited={len(audit_rows)} summary={dict(summary)}")
    print(f"priority_or_accepted={len(priority_rows)} excluded_or_revise={len(exclude_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
