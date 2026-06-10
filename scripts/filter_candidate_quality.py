#!/usr/bin/env python3
"""Filter candidate videos before draft-question generation."""

from __future__ import annotations

import argparse
import csv
import re
import urllib.parse
from pathlib import Path


INPUT_FIELDS = [
    "candidate_id",
    "source_url",
    "source_platform",
    "license_or_usage_note",
    "raw_duration_sec",
    "suggested_start_sec",
    "suggested_end_sec",
    "initial_category",
    "candidate_knowledge_point",
    "domain_seed",
    "subdomain_seed",
    "why_dynamic",
    "collector_notes",
]

OUTPUT_FIELDS = INPUT_FIELDS + [
    "quality_score",
    "quality_flags",
    "quality_decision",
]

TITLE_KEYWORDS_BY_KP = {
    "Unsupported objects accelerate downward under gravity.": ["falling", "falls", "freefall", "free fall", "gravity"],
    "A pendulum exchanges gravitational potential energy and kinetic energy.": ["pendulum", "pendel", "pendule", "pendolo"],
    "Objects sliding on rough surfaces slow down due to friction.": ["friction", "sliding"],
    "Magnetic fields can align or attract ferromagnetic materials.": ["magnet", "magnetic", "magneto", "magnetotactic"],
    "A spinning object can maintain angular momentum.": ["gyroscope", "precession", "spinning"],
    "Plant shoots can grow toward a light source.": ["phototropism", "phototropic"],
    "Seed germination involves root and shoot emergence.": ["germination", "emerging"],
    "Filtering separates solids from liquids by particle size.": ["filter", "filtration", "backwashing"],
    "A solid can absorb heat and melt into a liquid.": ["melting", "melt"],
    "Solvent evaporation can leave crystals behind.": ["crystallization", "crystal", "crystals"],
    "Acid-carbonate reactions can release carbon dioxide gas bubbles.": ["baking soda", "vinegar", "carbonate", "carbon dioxide", "effervescence"],
    "Iodine-clock reactions can show a delayed abrupt endpoint color change.": ["iodine clock", "persulfate"],
    "Mixing ions that form an insoluble salt can produce a precipitate.": ["precipitate", "precipitation", "silver nitrate", "sodium chloride"],
    "Benedict's reagent changes color when heated with reducing sugars.": ["benedict", "reducing sugar", "glucose"],
    "Combustion requires fuel and oxygen.": ["combustion", "burning", "fire"],
    "Warm air rises and can drive convection.": ["convection", "convective"],
    "Surface tension can support small objects or droplets.": ["surface tension"],
    "Surface tension can support or reshape small liquid structures.": ["surface tension", "capillary"],
    "Elastic materials restore shape after deformation.": ["spring", "elastic"],
    "Layering fluids can demonstrate density differences.": ["density", "stratified"],
}

SPECIALIST_TERMS = [
    "nanoparticle",
    "molecular",
    "foldamer",
    "cell",
    "microscopy",
    "plos",
    "pone",
    "srep",
    "pcbi",
    "supplementary",
    "ch3nh3pbi3",
]
ANIMATION_TERMS = ["animation", "anim", "simulation", "computer program", "computer generated", "information graphic"]
GAME_TERMS = ["game", "bonk", "video game"]
STATIC_EQUIPMENT_TERMS = ["pendulum", "filter", "filtration", "magnetic", "magnet"]
BAD_NOTES_TERMS = ["broad", "noisy", "weak mapping", "filter aggressively"]
BROAD_KNOWLEDGE_PATTERNS = [
    "some chemical reactions produce color change",
    "some reactions form a precipitate",
    "some mixtures produce gas during chemical reactions",
]


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def contains_any(text: str, terms: list[str]) -> bool:
    normalized_text = norm(text)
    padded = f" {normalized_text} "
    for term in terms:
        normalized_term = norm(term)
        if not normalized_term:
            continue
        if f" {normalized_term} " in padded or normalized_term in normalized_text:
            return True
    return False


def source_title(url: str) -> str:
    if "/wiki/File:" not in url:
        return url.rsplit("/", 1)[-1]
    raw = url.split("/wiki/File:", 1)[1]
    return urllib.parse.unquote(raw).replace("_", " ")


def parse_duration(value: str) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def score_row(row: dict[str, str], max_duration: float) -> dict[str, str]:
    title = source_title(row.get("source_url", ""))
    point = row.get("candidate_knowledge_point", "")
    notes = f"{row.get('collector_notes', '')} {row.get('why_dynamic', '')}"
    duration = parse_duration(row.get("raw_duration_sec", ""))
    score = 0
    flags: list[str] = []

    if contains_any(point, BROAD_KNOWLEDGE_PATTERNS):
        flags.append("broad_knowledge_point")
        score -= 80

    if 5 <= duration <= max_duration:
        score += 20
    elif duration <= 0:
        flags.append("missing_duration")
        score -= 50
    elif duration > max_duration:
        flags.append("long_duration_needs_trim")
        score -= 5
    else:
        flags.append("too_short")
        score -= 30

    if "requires review" in notes.lower():
        flags.append("auto_evidence_requires_review")
        score -= 10

    if any(term in notes.lower() for term in BAD_NOTES_TERMS):
        flags.append("noisy_collection_notes")
        score -= 20

    if contains_any(title, TITLE_KEYWORDS_BY_KP.get(point, [])):
        flags.append("title_names_target_phenomenon")
        score -= 60

    if contains_any(title, SPECIALIST_TERMS) or contains_any(notes, SPECIALIST_TERMS):
        flags.append("specialist_or_paper_context")
        score -= 50

    if contains_any(title, ANIMATION_TERMS) or contains_any(notes, ANIMATION_TERMS):
        flags.append("animation_or_simulation")
        score -= 40

    if contains_any(title, GAME_TERMS) or contains_any(notes, GAME_TERMS):
        flags.append("game_or_synthetic_context")
        score -= 40

    if contains_any(title, STATIC_EQUIPMENT_TERMS):
        flags.append("static_equipment_shortcut_risk")
        score -= 15

    if "strong seed" in notes.lower() or "high-value" in notes.lower() or "good dynamic" in notes.lower():
        score += 15

    severe_flags = {
        "missing_duration",
        "too_short",
        "title_names_target_phenomenon",
        "specialist_or_paper_context",
        "animation_or_simulation",
        "game_or_synthetic_context",
        "broad_knowledge_point",
    }
    if any(flag in severe_flags for flag in flags) and score < 0:
        decision = "exclude"
    elif score < 15:
        decision = "manual_review"
    else:
        decision = "priority"

    out = {key: row.get(key, "") for key in INPUT_FIELDS}
    out["quality_score"] = str(score)
    out["quality_flags"] = ";".join(flags)
    out["quality_decision"] = decision
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--priority-output", required=True, type=Path)
    parser.add_argument("--review-output", required=True, type=Path)
    parser.add_argument("--exclude-output", required=True, type=Path)
    parser.add_argument("--max-duration", type=float, default=75.0)
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8", newline="") as handle:
        rows = [score_row(row, args.max_duration) for row in csv.DictReader(handle)]

    rows.sort(key=lambda row: int(row["quality_score"]), reverse=True)
    buckets = {
        "priority": (args.priority_output, [row for row in rows if row["quality_decision"] == "priority"]),
        "manual_review": (args.review_output, [row for row in rows if row["quality_decision"] == "manual_review"]),
        "exclude": (args.exclude_output, [row for row in rows if row["quality_decision"] == "exclude"]),
    }
    for _, (path, output_rows) in buckets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            writer.writerows(output_rows)

    print(
        f"input={len(rows)} priority={len(buckets['priority'][1])} "
        f"manual_review={len(buckets['manual_review'][1])} exclude={len(buckets['exclude'][1])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
