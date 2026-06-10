#!/usr/bin/env python3
"""Build executable VDCR concept pool tiers from the v1 inventory."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


SINGLE_BALL_TECHNIQUES = {
    "Elastico / Flip Flap",
    "Marseille Turn / Roulette",
    "Cruyff Turn",
    "Rainbow Flick",
}

HUMAN_STRESS_SUBDOMAINS = {
    "人体专项动作与运动技术",
}

BALL_TACTIC_STRESS = {
    "Spain Action",
    "Elevator Screen",
    "Hammer Action",
    "Floppy Action",
    "Iverson Cut",
    "UCLA Cut",
    "Ram Screen",
    "Spain Back Screen",
}

ANIMAL_BROAD_EXTENSION = {
    "Anguilliform Undulation",
}

STRICT_GATE_CONCEPTS = {
    "Hydraulic Jump",
    "Crown Splash",
    "Worthington Jet",
    "Standing Wave Formation",
    "Rayleigh-Benard Convection",
    "Bacterial Chemotaxis",
    "Stomatal Opening and Closing",
    "Tidal Bore",
    "Barchan Dune Migration",
    "Gully Headcut Retreat",
    "Sediment Saltation",
    "Blue Bottle Reaction",
    "Chemical Traffic Light Reaction",
    "Benedict Positive Reducing-Sugar Reaction",
    "Crystal Nucleation",
    "Precipitation Front Propagation",
    "Reaction-Diffusion Wave",
    "Coffee-Ring Formation",
    "Droplet Rebound",
    "Droplet Spreading and Retraction",
    "Damped Oscillation",
    "Elastic Pendulum Motion",
    "Medusan Bell-Contraction Jet Propulsion",
    "Murmuration",
    "Fire-Whirl Vortex Formation",
    "Embryonic Cleavage Division Sequence",
    "Downburst / Microburst Outflow",
    "Tornadogenesis",
    "Ice Cliff Calving",
    "Wall Cloud Rotation",
    "Landspout Development",
    "Rip Current Formation",
}

RENAME_REVIEW_NOTES = {
    "Stomatal Opening and Closing": (
        "Concept name should be tightened during inventory refresh to "
        "Guard-Cell Driven Stomatal Aperture Dynamics."
    ),
    "Medusan Bell-Contraction Jet Propulsion": (
        "Use only when the video shows the bell contraction, water expulsion, and recoil sequence; "
        "do not accept generic jellyfish swimming."
    ),
    "Anguilliform Undulation": (
        "Too close to broad animal locomotion for the v1 main pool; use only in a future controlled locomotion slice with nearby gait contrasts."
    ),
    "Murmuration": (
        "Use only when flock-level dynamic shape waves and coordinated collective motion are visible; reject single-frame flock silhouettes."
    ),
    "Fire-Whirl Vortex Formation": (
        "Use only when the video shows vortex formation or maintained rotating fire-column dynamics, not a static fire column."
    ),
    "Embryonic Cleavage Division Sequence": (
        "Use only for clean time-lapse evidence of repeated early embryo division stages."
    ),
    "Downburst / Microburst Outflow": (
        "Use only when the outflow boundary or ground-level radial spreading is visible; reject generic wind/rain footage."
    ),
    "Tornadogenesis": (
        "Use only for formation sequences from rotating cloud base to funnel/vortex development; reject mature-tornado-only clips."
    ),
    "Sediment Saltation": (
        "Potential duplicate with Aeolian Saltation; keep only one saltation concept per "
        "sample set unless the transport medium is explicitly gated."
    ),
}

EXTENSION_CONCEPTS = {
    "Gastrulation",
    "Neural Tube Closure",
    "Epithelial-Mesenchymal Transition",
    "Convergent Extension",
    "Glacier Creep",
    "Basal Sliding",
    "Sea-Cliff Retreat",
    "Spit Progradation",
    "Wave Refraction",
    "Fault Rupture Propagation",
    "Prandtl-Meyer Expansion Fan",
    "Shock-Boundary-Layer Interaction",
    "Magnetic Reconnection",
    "Plasma Filamentation",
    "Corrosion Pit Growth",
    "Anodic Oxide Film Growth",
    "Lithium Dendrite Growth",
    "Liquid Crystal Domain Evolution",
    "Liquid Crystal Defect Annihilation",
}

OUTPUT_FIELDS = [
    "concept_id",
    "domain",
    "domain_zh",
    "subdomain",
    "subdomain_zh",
    "concept_zh",
    "concept_en",
    "concept_type",
    "priority",
    "pool_tier",
    "use_for_v1_main_target",
    "production_note",
    "retrieval_query_seed",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def tier_for(row: dict[str, str]) -> tuple[str, str, str]:
    concept = row["concept_en"]
    subdomain_zh = row["subdomain_zh"]
    priority = row.get("priority", "")

    if concept in SINGLE_BALL_TECHNIQUES:
        return (
            "extension",
            "no",
            "Named ball-sport technique, but too close to generic sport action recognition for v1 main pool.",
        )
    if concept in BALL_TACTIC_STRESS:
        return (
            "extension",
            "no",
            "Named ball-sport tactic with multi-agent temporal structure, but kept outside v1 production to avoid sport-play-recognition framing.",
        )
    if subdomain_zh in HUMAN_STRESS_SUBDOMAINS:
        return (
            "stress_slice",
            "limited",
            "Allowed only as a capped stress slice; require formal temporal signature and no scene/posture shortcut.",
        )
    if concept in ANIMAL_BROAD_EXTENSION:
        return (
            "extension",
            "no",
            "Named locomotion mode, but too close to generic animal movement unless collected as a controlled locomotion-family contrast set.",
        )
    if concept in EXTENSION_CONCEPTS or priority == "C":
        return (
            "extension",
            "no",
            "Valid concept but likely needs instrumentation, long time scale, simulation, or unusually clean evidence.",
        )
    if concept in STRICT_GATE_CONCEPTS or priority == "B":
        review_note = RENAME_REVIEW_NOTES.get(concept)
        note = "Use only after video-level gate confirms temporal necessity, no text leakage, and nearby negative viability."
        if review_note:
            note = f"{note} {review_note}"
        return (
            "strict_gate",
            "conditional",
            note,
        )
    return (
        "main_pool",
        "yes",
        "Preferred v1 production seed: named mechanism with strong temporal signature.",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--concepts", type=Path, default=Path("data/vdcr_concept_inventory_v1.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/vdcr_concept_pool_v1.csv"))
    args = parser.parse_args()

    rows = []
    for source in read_csv(args.concepts):
        tier, use_target, note = tier_for(source)
        rows.append(
            {
                "concept_id": source["concept_id"],
                "domain": source["domain"],
                "domain_zh": source["domain_zh"],
                "subdomain": source["subdomain"],
                "subdomain_zh": source["subdomain_zh"],
                "concept_zh": source["concept_zh"],
                "concept_en": source["concept_en"],
                "concept_type": source["concept_type"],
                "priority": source["priority"],
                "pool_tier": tier,
                "use_for_v1_main_target": use_target,
                "production_note": note,
                "retrieval_query_seed": source["retrieval_query_seed"],
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} concepts to {args.output}")
    print("pool_tier", dict(Counter(row["pool_tier"] for row in rows)))
    print("use_for_v1_main_target", dict(Counter(row["use_for_v1_main_target"] for row in rows)))
    print("domain_pool")
    for (domain, tier), count in sorted(Counter((row["domain"], row["pool_tier"]) for row in rows).items()):
        print(f"{domain}\t{tier}\t{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
