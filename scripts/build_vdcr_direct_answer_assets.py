#!/usr/bin/env python3
"""Build VDCR direct-answer concept and retrieval assets from the Markdown inventory."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


QUESTION = "Which named dynamic concept is instantiated by the temporally evolving process in this video?"

DOMAIN_MAP = {
    "自然物理规律": "physics_physical_systems",
    "物质变化机制": "chemistry_materials_change",
    "生命过程机制": "biology_living_systems",
    "地球环境过程": "earth_environmental_systems",
}

CAPABILITY_MAP = {
    "自然动态机制": "dynamic_mechanism_concept",
    "实验动态图样": "experimental_dynamic_pattern",
    "生态行为策略": "ecological_behavior_strategy",
    "专有动态动作概念": "specialized_dynamic_action_concept",
}

CONCEPT_FIELDS = [
    "concept_id",
    "domain",
    "domain_zh",
    "subdomain",
    "subdomain_zh",
    "concept_zh",
    "concept_en",
    "concept_type",
    "capability_label",
    "priority",
    "risk_reason",
    "static_shortcut_risk",
    "video_availability_guess",
    "accepted_answers_json",
    "direct_answer_question",
    "retrieval_query_seed",
]

QUERY_FIELDS = [
    "concept_id",
    "priority",
    "search_term",
    "initial_category",
    "candidate_knowledge_point",
    "domain_seed",
    "subdomain_seed",
    "why_dynamic",
    "default_start_sec",
    "default_end_sec",
    "notes",
]

SUMMARY_FIELDS = ["metric", "value"]

PRIORITY_A_TERMS = {
    "Vortex Shedding / Karman Vortex Street",
    "Cavitation Bubble Growth and Collapse",
    "Kelvin-Helmholtz Instability",
    "Rayleigh-Taylor Instability",
    "Hydraulic Jump",
    "Rayleigh-Plateau Breakup",
    "Liquid Bridge Pinch-Off",
    "Leidenfrost Droplet Motion",
    "Marangoni-Driven Flow",
    "Standing Wave Formation",
    "Faraday Waves",
    "Gyroscopic Precession",
    "Dzhanibekov Effect / Tennis Racket Theorem",
    "Brazil Nut Effect",
    "Crown Splash",
    "Worthington Jet",
    "Vortex Ring Formation",
    "Rayleigh-Benard Convection",
    "Shear Thickening",
    "Weissenberg Rod-Climbing Effect",
    "Dendritic Crystal Growth",
    "Supercooled Liquid Rapid Crystallization",
    "Iodine Clock Reaction",
    "Belousov-Zhabotinsky Reaction",
    "Briggs-Rauscher Reaction",
    "Chemical Garden Growth",
    "Liesegang Ring Formation",
    "Spinodal Decomposition",
    "Thin-Film Dewetting",
    "Electrodeposition Dendrite Growth",
    "C-Start Escape Response",
    "Jet Propulsion Swimming",
    "Metachronal Wave Locomotion",
    "Bubble-Net Feeding",
    "Mud-Ring Feeding",
    "Murmuration",
    "Phototropism",
    "Gravitropism",
    "Thigmonasty",
    "Nyctinasty",
    "Bistable Snap-Trap Closure",
    "Cytoplasmic Streaming",
    "Mitotic Chromosome Segregation",
    "Ciliary Beating",
    "Calcium Wave Propagation",
    "FRAP Recovery",
    "Endocytosis",
    "Exocytosis",
    "Microtubule Dynamic Instability",
    "Gastrulation",
    "Stomatal Opening and Closing",
    "Bacterial Chemotaxis",
    "Supercell Mesocyclone Rotation",
    "Tornadogenesis",
    "Downburst / Microburst Outflow",
    "Meander Neck Cutoff",
    "Sediment Saltation",
    "Pyroclastic Density Current",
    "Pahoehoe Lava Roping",
    "Slab Avalanche Release",
    "Barchan Dune Migration",
    "Tidal Bore",
    "Gully Headcut Retreat",
    "Spain Action",
    "Elevator Screen",
    "Hammer Action",
}

PRIORITY_C_PATTERNS = [
    "Prandtl-Meyer",
    "Shock-Boundary-Layer",
    "Magnetic Reconnection",
    "Plasma Filamentation",
    "Solar Prominence",
    "Coronal Mass",
    "Liquid Crystal",
    "Polymerization Shrinkage",
    "Corrosion Pit",
    "Anodic Oxide",
    "Lithium Dendrite",
    "Fault Rupture",
    "Glacier Creep",
    "Basal Sliding",
    "Longshore Drift",
    "Wave Refraction",
    "Sea-Cliff Retreat",
    "Spit Progradation",
    "Stratified Sediment Gravity Flow",
    "Epithelial-Mesenchymal",
    "Neural Tube",
    "Convergent Extension",
]

STATIC_SHORTCUT_HIGH_PATTERNS = [
    "Droplet Rebound",
    "Ligament-Mediated Atomization",
    "Plunging Breaker",
    "Longshore Drift",
    "Fire Whirl",
    "Eggbeater Kick",
    "Bicycle",
]

VIDEO_AVAILABILITY_LOW_PATTERNS = [
    "Prandtl-Meyer",
    "Shock-Boundary-Layer",
    "Magnetic Reconnection",
    "Plasma Filamentation",
    "Liquid Crystal",
    "Anodic Oxide",
    "Lithium Dendrite",
    "Basal Sliding",
    "Glacier Creep",
]


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_") or "concept"


def split_aliases(concept_en: str, concept_zh: str) -> list[str]:
    aliases = [concept_en, concept_zh]
    for sep in [" / ", " /", "/ ", "/"]:
        if sep in concept_en:
            aliases.extend(part.strip() for part in concept_en.split(sep) if part.strip())
    if "(" in concept_en:
        aliases.append(re.sub(r"\s*\([^)]*\)", "", concept_en).strip())
    seen = set()
    output = []
    for alias in aliases:
        key = alias.casefold()
        if alias and key not in seen:
            seen.add(key)
            output.append(alias)
    return output


def parse_inventory(path: Path) -> list[dict[str, str]]:
    rows = []
    in_table = False
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if line.startswith("## Candidate Concepts"):
                in_table = True
                continue
            if line.startswith("## Explicitly"):
                in_table = False
            if not in_table or not line.startswith("| "):
                continue
            if "---" in line or "一级 Domain" in line:
                continue
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) != 5:
                continue
            rows.append(
                {
                    "domain_zh": parts[0],
                    "subdomain_zh": parts[1],
                    "concept_zh": parts[2],
                    "concept_en": parts[3],
                    "concept_type": parts[4],
                }
            )
    return rows


def priority_for(row: dict[str, str]) -> str:
    concept = row["concept_en"]
    if concept in PRIORITY_A_TERMS:
        return "A"
    if any(pattern in concept for pattern in PRIORITY_C_PATTERNS):
        return "C"
    if row["concept_type"] == "专有动态动作概念":
        return "B"
    return "B"


def risk_reason_for(row: dict[str, str], priority: str) -> str:
    concept = row["concept_en"]
    if priority == "A":
        return "strong_temporal_signature_and_named_dynamic_concept"
    if any(pattern in concept for pattern in PRIORITY_C_PATTERNS):
        return "likely_requires_simulation_instrumentation_or_long_timescale_review"
    if row["concept_type"] == "专有动态动作概念":
        return "specialized_action_requires_nearby_action_contrast_and_clear_sequence"
    return "usable_candidate_requires_video_availability_and_static_shortcut_review"


def static_shortcut_risk_for(row: dict[str, str]) -> str:
    concept = row["concept_en"]
    if any(pattern in concept for pattern in STATIC_SHORTCUT_HIGH_PATTERNS):
        return "high"
    if row["concept_type"] == "专有动态动作概念":
        return "medium"
    return "medium"


def video_availability_for(row: dict[str, str]) -> str:
    concept = row["concept_en"]
    if any(pattern in concept for pattern in VIDEO_AVAILABILITY_LOW_PATTERNS):
        return "low"
    if row["concept_type"] in {"实验动态图样", "专有动态动作概念", "生态行为策略"}:
        return "high"
    return "medium"


def dynamic_reason(row: dict[str, str]) -> str:
    return (
        "Candidate must show the temporal sequence that instantiates "
        f"{row['concept_en']}, not merely an object, scene, or static result."
    )


def query_terms(row: dict[str, str], priority: str) -> list[str]:
    concept = row["concept_en"]
    zh = row["concept_zh"]
    aliases = [alias for alias in split_aliases(concept, zh) if re.search(r"[A-Za-z]", alias)]
    terms = []
    contextualized_ball_term = False
    if row["subdomain_zh"] == "球类专项动作与战术序列":
        contextualized_ball_term = True
        soccer_terms = {
            "Elastico / Flip Flap",
            "Marseille Turn / Roulette",
            "Cruyff Turn",
            "Rainbow Flick",
        }
        basketball_terms = {
            "Spain Action",
            "Elevator Screen",
            "Hammer Action",
            "Floppy Action",
            "Iverson Cut",
            "UCLA Cut",
            "Ram Screen",
            "Spain Back Screen",
        }
        if concept in soccer_terms:
            for alias in aliases[:4]:
                terms.append(f"{alias} soccer skill")
                terms.append(f"{alias} football skill")
                terms.append(f"{alias} soccer technique video")
        elif concept in basketball_terms:
            for alias in aliases[:4]:
                terms.append(f"{alias} basketball play")
                terms.append(f"{alias} basketball offense")
                terms.append(f"{alias} basketball video")
        else:
            for alias in aliases[:4]:
                terms.append(f"{alias} sport technique video")
    if not contextualized_ball_term:
        for alias in aliases[:4]:
            terms.append(alias)
            terms.append(f"{alias} video")
    primary = aliases[0] if aliases else concept
    if not contextualized_ball_term:
        terms.extend(
            [
                f"{primary} slow motion",
                f"{primary} demonstration",
            ]
        )
        if row["concept_type"] == "实验动态图样":
            terms.append(f"{primary} experiment video")
        if row["concept_type"] == "专有动态动作概念":
            terms.append(f"{primary} technique video")
        if row["concept_type"] == "生态行为策略":
            terms.append(f"{primary} wildlife video")
        if priority == "A":
            terms.append(f"{zh} {primary}")
    seen = set()
    output = []
    for term in terms:
        key = term.casefold()
        if key not in seen:
            seen.add(key)
            output.append(term)
    return output


DOMAIN_PREFIX = {
    "physics_physical_systems": "physics",
    "chemistry_materials_change": "materials",
    "biology_living_systems": "biology",
    "earth_environmental_systems": "earth",
}


def subdomain_slugs(raw_rows: list[dict[str, str]]) -> dict[tuple[str, str], str]:
    mapping: dict[tuple[str, str], str] = {}
    counts: dict[str, int] = {}
    for row in raw_rows:
        domain = DOMAIN_MAP.get(row["domain_zh"], slugify(row["domain_zh"]))
        key = (domain, row["subdomain_zh"])
        if key in mapping:
            continue
        counts[domain] = counts.get(domain, 0) + 1
        mapping[key] = f"{DOMAIN_PREFIX.get(domain, 'domain')}_family_{counts[domain]:02d}"
    return mapping


def build_rows(raw_rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    concept_rows = []
    query_rows = []
    subdomain_map = subdomain_slugs(raw_rows)
    for index, row in enumerate(raw_rows, start=1):
        concept_id = f"vdcr_concept_{index:04d}"
        domain = DOMAIN_MAP.get(row["domain_zh"], slugify(row["domain_zh"]))
        subdomain = subdomain_map[(domain, row["subdomain_zh"])]
        priority = priority_for(row)
        aliases = split_aliases(row["concept_en"], row["concept_zh"])
        retrieval_seed = query_terms(row, priority)[0]
        concept_rows.append(
            {
                "concept_id": concept_id,
                "domain": domain,
                "domain_zh": row["domain_zh"],
                "subdomain": subdomain,
                "subdomain_zh": row["subdomain_zh"],
                "concept_zh": row["concept_zh"],
                "concept_en": row["concept_en"],
                "concept_type": row["concept_type"],
                "capability_label": CAPABILITY_MAP.get(row["concept_type"], slugify(row["concept_type"])),
                "priority": priority,
                "risk_reason": risk_reason_for(row, priority),
                "static_shortcut_risk": static_shortcut_risk_for(row),
                "video_availability_guess": video_availability_for(row),
                "accepted_answers_json": json.dumps(aliases, ensure_ascii=False),
                "direct_answer_question": QUESTION,
                "retrieval_query_seed": retrieval_seed,
            }
        )
        for term in query_terms(row, priority):
            query_rows.append(
                {
                    "concept_id": concept_id,
                    "priority": priority,
                    "search_term": term,
                    "initial_category": domain,
                    "candidate_knowledge_point": row["concept_en"],
                    "domain_seed": domain,
                    "subdomain_seed": subdomain,
                    "why_dynamic": dynamic_reason(row),
                    "default_start_sec": "0",
                    "default_end_sec": "30",
                    "notes": (
                        f"vdcr_direct_answer; concept_zh={row['concept_zh']}; "
                        f"concept_type={row['concept_type']}; priority={priority}"
                    ),
                }
            )
    priority_rank = {"A": 0, "B": 1, "C": 2}
    query_rows.sort(key=lambda row: (priority_rank.get(row["priority"], 9), row["concept_id"], row["search_term"]))
    return concept_rows, query_rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_summary(path: Path, concept_rows: list[dict[str, str]], query_rows: list[dict[str, str]]) -> None:
    counts: dict[str, int] = {
        "concept_count": len(concept_rows),
        "query_count": len(query_rows),
    }
    for field in ["domain", "priority", "concept_type", "capability_label"]:
        for row in concept_rows:
            counts[f"{field}:{row[field]}"] = counts.get(f"{field}:{row[field]}", 0) + 1
    rows = [{"metric": key, "value": str(value)} for key, value in sorted(counts.items())]
    write_csv(path, SUMMARY_FIELDS, rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory-md", type=Path, default=Path("docs/vdcr_concept_inventory_v1.md"))
    parser.add_argument("--concept-csv", type=Path, default=Path("data/vdcr_concept_inventory_v1.csv"))
    parser.add_argument("--concept-jsonl", type=Path, default=Path("data/vdcr_concept_inventory_v1.jsonl"))
    parser.add_argument("--query-csv", type=Path, default=Path("data/vdcr_concept_search_queries_v1.csv"))
    parser.add_argument("--summary-csv", type=Path, default=Path("data/vdcr_asset_summary_v1.csv"))
    args = parser.parse_args()

    raw_rows = parse_inventory(args.inventory_md)
    concept_rows, query_rows = build_rows(raw_rows)
    write_csv(args.concept_csv, CONCEPT_FIELDS, concept_rows)
    write_jsonl(args.concept_jsonl, concept_rows)
    write_csv(args.query_csv, QUERY_FIELDS, query_rows)
    write_summary(args.summary_csv, concept_rows, query_rows)
    print(f"concepts={len(concept_rows)} queries={len(query_rows)}")
    print(f"wrote {args.concept_csv}")
    print(f"wrote {args.query_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
