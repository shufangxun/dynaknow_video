#!/usr/bin/env python3
"""Normalize legacy candidate CSVs into a v1 retrieval review pool."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path

from taxonomy_aliases import normalize_domain_subdomain


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

OUTPUT_FIELDS = [
    *INPUT_FIELDS,
    "inferred_domain",
    "inferred_subdomain",
    "taxonomy_match",
    "retrieval_decision",
    "priority_score",
    "review_flags",
    "review_status",
    "linked_review_video_id",
]

LEGACY_DOMAIN_MAP = {
    "physics_mechanics": "physics_physical_systems",
    "chemistry_material_change": "chemistry_materials_change",
    "biology_life_processes": "biology_living_systems",
    "everyday_causal_mechanisms": "physics_physical_systems",
    "procedural_operational_principles": "engineering_operational_systems",
}

DOMAIN_DEFAULT_SUBDOMAIN = {
    "physics_physical_systems": "motion_forces_and_energy",
    "chemistry_materials_change": "phase_change_and_crystallization",
    "biology_living_systems": "germination_and_development",
    "earth_environmental_systems": "hydrology_and_flow_processes",
    "engineering_operational_systems": "machines_control_and_failure_modes",
}

SUBDOMAIN_HINTS = [
    ("collisions_and_momentum", ["collision", "collisions", "momentum", "billiard", "rebound"]),
    ("oscillation_rotation_and_vibration", ["pendulum", "oscillat", "vibration", "torsion", "coupled"]),
    ("fluids_pressure_and_buoyancy", ["pressure", "buoyancy", "siphon", "fluid flow", "water rises", "ballast"]),
    ("surface_and_capillary_processes", ["surface tension", "capillary", "droplet", "breakup", "wetting"]),
    ("thermal_physical_response", ["thermal expansion", "bimetal", "heated", "convection"]),
    ("electromagnetism_and_fields", ["magnet", "magnetic", "field", "ferromagnetic"]),
    ("phase_change_and_crystallization", ["melt", "melting", "freezing", "crystal", "crystallization", "solidify"]),
    ("redox_and_endpoint_reactions", ["iodine", "clock", "benedict", "redox", "reducing"]),
    ("precipitation_and_solubility", ["precipitate", "precipitation", "solubility", "insoluble"]),
    ("gas_evolution_and_combustion", ["combustion", "burn", "flame", "ignition", "gas", "carbon dioxide"]),
    ("diffusion_mixing_and_transport", ["diffusion", "mixing", "dispersion"]),
    ("plant_growth_and_tropisms", ["phototropism", "gravitropism", "shoot", "growth direction", "reorient"]),
    ("plant_nastic_movements", ["photonasty", "thigmonasty", "leaf position", "carnivorous", "drosera"]),
    ("germination_and_development", ["germination", "sprout", "seed", "emergence"]),
    (
        "plant_water_relations_and_turgor",
        [
            "plant water state",
            "capillary absorption",
            "turgor",
            "plasmolysis",
            "deplasmolysis",
            "wilting",
            "recovery after watering",
            "stomatal aperture",
        ],
    ),
    ("animal_locomotion_and_biomechanics", ["muscle", "joint", "gait", "locomotion"]),
    ("organism_behavior_and_taxis", ["taxis", "phototaxis", "chemotaxis"]),
    ("filtration_and_separation", ["filter", "filtration", "settling", "sorting", "separation", "backwashing"]),
    ("mixing_dispersion_and_wetting", ["mixing", "dispersion", "wetting"]),
    ("pressure_flow_and_process_control", ["pump", "valve", "pressure release", "flow regulation"]),
    ("thermal_process_control", ["heating", "cooling", "thermal shock"]),
    ("tooling_force_and_precision", ["clamp", "cutting", "drilling", "tightening"]),
]

RISK_TITLE_TERMS = [
    "animation",
    "simulation",
    "game",
    "gameplay",
    "speedrun",
    "walkthrough",
    "playthrough",
    "trailer",
    "arcade",
    "half-life",
    "minecraft",
    "grand theft",
    "call of duty",
    "xbox",
    "playstation",
    "nintendo",
    "lecture",
    "lectures",
    "chapter review",
    "chapter reviews",
    "course",
    "seminar",
    "talk",
    "mit8.",
    "mit 8.",
    "mit2.",
    "mit 2.",
    "mitpe.",
    "ocw",
    "engineering dynamics",
    "physics iii",
    "supplementary",
    "molecular",
    "nanoparticle",
    "microscopy",
    "plos",
    "pone",
    "srep",
    "deepstate",
    "goyim",
    "gray state",
    "moon landing hoax",
    "sinbad",
    "artist's diary",
    "workflow compilation",
    "tractor soot",
    "still images",
    "flyover",
    "suit up",
    "fake moon",
    "fangruida",
]

MATCH_STOPWORDS = {
    "video",
    "slow",
    "motion",
    "time",
    "lapse",
    "timelapse",
    "experiment",
    "demonstration",
    "demo",
    "with",
    "from",
    "that",
    "this",
    "after",
    "before",
}


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path | None) -> list[dict]:
    if path is None or not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def read_source_urls(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    if path.suffix == ".jsonl":
        return {
            str(row.get("source_url", "")): str(row.get("video_id", ""))
            for row in read_jsonl(path)
            if row.get("source_url")
        }
    rows = read_csv(path)
    return {
        str(row.get("source_url", "")): str(row.get("video_id", ""))
        for row in rows
        if row.get("source_url")
    }


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def source_title(url: str) -> str:
    if "/wiki/File:" in url:
        raw = url.split("/wiki/File:", 1)[1]
        return urllib.parse.unquote(raw).replace("_", " ")
    return urllib.parse.unquote(url.rsplit("/", 1)[-1])


def parse_float(value: str) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def note_value(notes: str, key: str) -> str:
    match = re.search(rf"(?:^|;\s*){re.escape(key)}=([^;]*)", notes or "")
    return match.group(1).strip() if match else ""


def content_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9]+", text.lower())
        if len(token) >= 4 and token not in MATCH_STOPWORDS
    }


def taxonomy_by_kp(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None or not path.exists():
        return {}
    return {row["knowledge_point"]: row for row in read_csv(path) if row.get("knowledge_point")}


GATE_PLACEHOLDERS = {
    "__construct_after_dynamic_gate__",
    "__construct_after_principle_video_gate__",
    "__construct_after_dcr_video_gate__",
}


def infer_taxonomy(row: dict[str, str], taxonomy: dict[str, dict[str, str]]) -> tuple[str, str, str]:
    point = normalize_space(row.get("candidate_knowledge_point", ""))
    if point in GATE_PLACEHOLDERS:
        domain, subdomain = normalize_domain_subdomain(row.get("domain_seed", ""), row.get("subdomain_seed", ""))
        match_type = "dcr_seed" if point == "__construct_after_dcr_video_gate__" else "principle_seed"
        return domain, subdomain, match_type
    if point in taxonomy:
        tax = taxonomy[point]
        domain, subdomain = normalize_domain_subdomain(tax["domain"], tax["subdomain"])
        return domain, subdomain, "exact_knowledge_point"

    domain = row.get("domain_seed") or LEGACY_DOMAIN_MAP.get(row.get("initial_category", ""), "")
    if not domain:
        domain = "unmapped"
    text = " ".join(
        [
            point,
            row.get("why_dynamic", ""),
            row.get("collector_notes", ""),
            source_title(row.get("source_url", "")),
        ]
    ).lower()
    for subdomain, hints in SUBDOMAIN_HINTS:
        if any(hint in text for hint in hints):
            domain, subdomain = normalize_domain_subdomain(domain, subdomain)
            return domain, subdomain, "heuristic_hint"
    domain, subdomain = normalize_domain_subdomain(
        domain,
        row.get("subdomain_seed") or DOMAIN_DEFAULT_SUBDOMAIN.get(domain, "unmapped"),
    )
    return domain, subdomain, "legacy_default"


def score_row(row: dict[str, str], reviewed_urls: dict[str, str]) -> tuple[str, int, list[str], str]:
    flags: list[str] = []
    score = 0
    url = row.get("source_url", "")
    duration = parse_float(row.get("raw_duration_sec", ""))
    title = source_title(url).lower()
    point = row.get("candidate_knowledge_point", "")

    if url in reviewed_urls:
        flags.append("already_reviewed")
        return "already_reviewed", 0, flags, reviewed_urls[url]

    if point in GATE_PLACEHOLDERS:
        flags.append("needs_dynamic_gate")
        score += 5

    if 5 <= duration <= 75:
        score += 20
    elif duration > 240:
        flags.append("very_long_duration")
        score -= 20
    elif duration > 75:
        flags.append("needs_trim")
        score += 2
    elif duration <= 0:
        flags.append("missing_duration")
        score -= 20
    else:
        flags.append("too_short")
        score -= 20

    if "commons.wikimedia.org/wiki/File:" in url:
        score += 5
    else:
        flags.append("non_commons_source")
        score -= 5

    notes = f"{row.get('collector_notes', '')} {row.get('why_dynamic', '')}".lower()
    if row.get("source_platform") == "internet_archive":
        query_terms = content_tokens(note_value(row.get("collector_notes", ""), "search_term"))
        title_terms = content_tokens(
            " ".join(
                [
                    note_value(row.get("collector_notes", ""), "title"),
                    note_value(row.get("collector_notes", ""), "description"),
                    source_title(url),
                ]
            )
        )
        overlap = query_terms & title_terms
        if len(query_terms) >= 2 and len(overlap) == 0:
            flags.append("weak_archive_title_match")
            score -= 25
        elif len(overlap) == 1:
            flags.append("thin_archive_title_match")
            score -= 8
    if any(term in title or term in notes for term in RISK_TITLE_TERMS):
        flags.append("source_or_specialist_context_risk")
        score -= 25

    if "strong seed" in notes or "high-value" in notes or "good dynamic" in notes:
        score += 10
    if "broad" in notes or "weak mapping" in notes or "noisy" in notes:
        flags.append("weak_mapping_note")
        score -= 10

    if score >= 25:
        decision = "priority_review"
    elif score >= 5:
        decision = "manual_review"
    else:
        decision = "low_priority_or_exclude"
    return decision, score, flags, ""


def build_pool(inputs: list[Path], taxonomy: dict[str, dict[str, str]], reviewed_urls: dict[str, str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    for path in inputs:
        for row in read_csv(path):
            url = row.get("source_url", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            normalized = {field: row.get(field, "") for field in INPUT_FIELDS}
            domain, subdomain, match = infer_taxonomy(normalized, taxonomy)
            decision, score, flags, linked_video_id = score_row(normalized, reviewed_urls)
            normalized.update(
                {
                    "inferred_domain": domain,
                    "inferred_subdomain": subdomain,
                    "taxonomy_match": match,
                    "retrieval_decision": decision,
                    "priority_score": str(score),
                    "review_flags": ";".join(flags),
                    "review_status": "",
                    "linked_review_video_id": linked_video_id,
                }
            )
            rows.append(normalized)
    rows.sort(
        key=lambda row: (
            {"priority_review": 0, "manual_review": 1, "low_priority_or_exclude": 2, "already_reviewed": 3}.get(
                row["retrieval_decision"], 4
            ),
            row["inferred_domain"],
            row["inferred_subdomain"],
            -int(row["priority_score"]),
            row["candidate_id"],
        )
    )
    return rows


def write_csv(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_queue(rows: list[dict[str, str]], output: Path, decisions: set[str], limit: int) -> None:
    selected = [row for row in rows if row["retrieval_decision"] in decisions]
    if limit > 0:
        selected = selected[:limit]
    write_csv(selected, output)


def pct(value: int, total: int) -> str:
    return "0.0%" if total == 0 else f"{100 * value / total:.1f}%"


def build_html(rows: list[dict[str, str]], output: Path, title: str) -> None:
    total = len(rows)
    decisions = Counter(row["retrieval_decision"] for row in rows)
    domains = Counter((row["inferred_domain"], row["retrieval_decision"]) for row in rows)
    flags = Counter(flag for row in rows for flag in row["review_flags"].split(";") if flag)
    metric_html = "".join(
        f'<div class="metric"><strong>{count}</strong><span>{esc(key)}</span><small>{pct(count, total)}</small></div>'
        for key, count in [("total", total), *decisions.most_common()]
    )
    domain_rows = []
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for (domain, decision), count in domains.items():
        grouped[domain][decision] = count
    for domain in sorted(grouped):
        counts = grouped[domain]
        domain_rows.append(
            "<tr>"
            f"<td>{esc(domain.replace('_', ' '))}</td>"
            f"<td>{sum(counts.values())}</td>"
            f"<td>{counts.get('priority_review', 0)}</td>"
            f"<td>{counts.get('manual_review', 0)}</td>"
            f"<td>{counts.get('low_priority_or_exclude', 0)}</td>"
            f"<td>{counts.get('already_reviewed', 0)}</td>"
            "</tr>"
        )
    flag_rows = "".join(f"<tr><td>{esc(flag)}</td><td>{count}</td></tr>" for flag, count in flags.most_common())
    card_rows = []
    for row in rows[:250]:
        card_rows.append(
            f'<article class="card {esc(row["retrieval_decision"])}">'
            f'<h3>{esc(row["candidate_id"])} <span>{esc(row["retrieval_decision"])}</span></h3>'
            f'<p><strong>{esc(row["inferred_domain"])}</strong> / {esc(row["inferred_subdomain"])}</p>'
            f'<p>{esc(row["candidate_knowledge_point"])}</p>'
            f'<p>{esc(row["why_dynamic"])}</p>'
            f'<p class="flags">{esc(row["review_flags"])}</p>'
            f'<p><a href="{esc(row["source_url"])}">source</a></p>'
            "</article>"
        )
    html_text = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<style>
body{{font-family:Arial,sans-serif;margin:0;background:#f6f7f9;color:#1f2933}}
header{{padding:24px 28px;background:#111827;color:white}}
h1{{margin:0 0 8px;font-size:24px}}
.metrics{{display:flex;flex-wrap:wrap;gap:10px;padding:18px 28px}}
.metric{{background:white;border:1px solid #d7dce3;border-radius:8px;padding:12px 14px;min-width:130px}}
.metric strong{{display:block;font-size:24px}} .metric span,.metric small{{display:block;color:#52606d}}
.panel{{margin:0 28px 18px;background:white;border:1px solid #d7dce3;border-radius:8px;padding:14px}}
table{{border-collapse:collapse;width:100%}} th,td{{border-bottom:1px solid #e6e9ee;text-align:left;padding:7px 8px;font-size:13px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px;padding:0 28px 28px}}
.card{{background:white;border-left:5px solid #9aa6b2;border-radius:8px;border-top:1px solid #d7dce3;border-right:1px solid #d7dce3;border-bottom:1px solid #d7dce3;padding:12px}}
.priority_review{{border-left-color:#15803d}} .manual_review{{border-left-color:#b7791f}} .low_priority_or_exclude{{border-left-color:#b91c1c}} .already_reviewed{{border-left-color:#6b7280}}
.card h3{{margin:0 0 8px;font-size:15px}} .card h3 span{{float:right;font-weight:400;color:#52606d}}
.card p{{margin:7px 0;font-size:13px;line-height:1.35}} .flags{{color:#9a3412}}
a{{color:#0645ad}}
</style>
</head>
<body>
<header><h1>{esc(title)}</h1><p>Normalized retrieval candidates for DynaKnow-Video v1. QA is not constructed at this stage.</p></header>
<section class="metrics">{metric_html}</section>
<section class="panel"><h2>Domain Coverage</h2><table><thead><tr><th>Domain</th><th>Total</th><th>Priority</th><th>Manual</th><th>Low/Exclude</th><th>Already reviewed</th></tr></thead><tbody>{''.join(domain_rows)}</tbody></table></section>
<section class="panel"><h2>Review Flags</h2><table><thead><tr><th>Flag</th><th>Count</th></tr></thead><tbody>{flag_rows}</tbody></table></section>
<section class="cards">{''.join(card_rows)}</section>
</body></html>"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--taxonomy", type=Path, default=Path("data/domain_taxonomy_v1.csv"))
    parser.add_argument("--reviewed-source-audit", action="append", type=Path, default=[])
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--output-html", required=True, type=Path)
    parser.add_argument("--queue-csv", type=Path, help="Optional priority/manual review queue CSV.")
    parser.add_argument("--queue-decisions", default="priority_review,manual_review")
    parser.add_argument("--queue-limit", type=int, default=0)
    parser.add_argument("--title", default="DynaKnow-Video v1 Retrieval Candidate Pool")
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()

    taxonomy = taxonomy_by_kp(args.taxonomy)
    reviewed_urls: dict[str, str] = {}
    for path in args.reviewed_source_audit:
        reviewed_urls.update(read_source_urls(path))
    rows = build_pool(args.inputs, taxonomy, reviewed_urls)
    write_csv(rows, args.output_csv)
    if args.queue_csv:
        write_queue(rows, args.queue_csv, {item.strip() for item in args.queue_decisions.split(",") if item.strip()}, args.queue_limit)
    build_html(rows, args.output_html, args.title)
    print(f"wrote {len(rows)} rows to {args.output_csv}")
    if args.queue_csv:
        print(f"wrote review queue to {args.queue_csv}")
    print(f"wrote candidate report to {args.output_html}")
    print("decisions=" + ",".join(f"{k}:{v}" for k, v in Counter(row["retrieval_decision"] for row in rows).items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
