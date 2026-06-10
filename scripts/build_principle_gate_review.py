#!/usr/bin/env python3
"""Build principle-gate review rows for principle-first video candidates.

This is a review scaffold, not an automatic pass filter. It joins retrieval
queue rows to the principle inventory so each candidate is evaluated against
the intended transferable mechanism rather than rewritten as a video caption.
"""

from __future__ import annotations

import argparse
import csv
import html
import os
import re
from collections import Counter
from pathlib import Path

from taxonomy_aliases import normalize_domain_subdomain


OUTPUT_FIELDS = [
    "candidate_id",
    "source_url",
    "source_platform",
    "license_or_usage_note",
    "domain",
    "subdomain",
    "capability_label",
    "dynamic_concept_id",
    "dynamic_concept",
    "linked_principle_id",
    "principle_id",
    "principle",
    "required_dynamic_signature",
    "acceptable_video_types",
    "reject_conditions",
    "hard_negative_family",
    "visible_dynamic_process",
    "dynamic_signature_match",
    "source_page_support_level",
    "source_page_mechanism_evidence",
    "source_double_check_decision",
    "source_double_check_reason",
    "source_page_context",
    "review_decision",
    "gate_reason",
    "risk_tags",
    "proposed_knowledge_point",
    "proposed_knowledge_point_type",
    "answerability_notes",
    "distractor_requirements",
    "frame_contact_sheet",
    "local_media",
    "is_new_source",
    "source_reuse_status",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def rel(path: str, output: Path) -> str:
    if not path:
        return ""
    return os.path.relpath(path, start=output.parent)


def parse_principle_id(notes: str) -> str:
    match = re.search(r"(?:^|[;\s])principle_id=([A-Z0-9_]+)", notes or "")
    return match.group(1) if match else ""


def parse_note_value(notes: str, key: str) -> str:
    match = re.search(rf"(?:^|;\s*){re.escape(key)}=([^;]*)", notes or "")
    return match.group(1).strip() if match else ""


def find_local_media(media_dir: Path | None, item_id: str) -> str:
    if media_dir is None:
        return ""
    matches = sorted(media_dir.glob(f"{item_id}.*"))
    return str(matches[0]) if matches else ""


def contact_sheet_path(frames_dir: Path | None, item_id: str, frame_status: dict[str, str]) -> str:
    if frames_dir is None:
        return ""
    path = frames_dir / item_id / "contact_sheet.jpg"
    if path.exists():
        return str(path)
    if frame_status.get("contact_sheet") == "ok":
        return str(path)
    return ""


def source_urls(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    return {row.get("source_url", "") for row in read_csv(path) if row.get("source_url")}


def build_rows(
    queue_rows: list[dict[str, str]],
    inventory_rows: list[dict[str, str]],
    concept_rows: list[dict[str, str]],
    frame_rows: list[dict[str, str]],
    media_dir: Path | None,
    frames_dir: Path | None,
    existing_sources: set[str],
) -> list[dict[str, str]]:
    inventory = {row["principle_id"]: row for row in inventory_rows if row.get("principle_id")}
    concepts = {row["concept_id"]: row for row in concept_rows if row.get("concept_id")}
    frames = {row["id"]: row for row in frame_rows if row.get("id")}
    rows: list[dict[str, str]] = []
    for queue in queue_rows:
        item_id = queue.get("candidate_id", "")
        notes = queue.get("collector_notes", "")
        capability_label = queue.get("capability_label") or parse_note_value(notes, "capability_label") or "DMR"
        dynamic_concept_id = queue.get("dynamic_concept_id") or parse_note_value(notes, "dynamic_concept_id")
        concept = concepts.get(dynamic_concept_id, {})
        principle_id = (
            queue.get("principle_id")
            or parse_principle_id(notes)
            or concept.get("linked_principle_id", "")
        )
        principle = inventory.get(principle_id, {})
        domain, subdomain = normalize_domain_subdomain(
            queue.get("inferred_domain", "") or queue.get("domain_seed", ""),
            queue.get("inferred_subdomain", "") or queue.get("subdomain_seed", ""),
        )
        if concept:
            domain, subdomain = normalize_domain_subdomain(
                concept.get("domain", domain),
                concept.get("subdomain", subdomain),
            )
        source_url = queue.get("source_url", "")
        license_note = queue.get("license_or_usage_note", "")
        source_title = parse_note_value(queue.get("collector_notes", ""), "title")
        source_description = parse_note_value(queue.get("collector_notes", ""), "description")
        source_context = " | ".join(part for part in [source_title, source_description] if part)
        source_seen = source_url in existing_sources
        missing_principle = not principle_id or not principle
        missing_concept = capability_label == "DCR" and (not dynamic_concept_id or not concept)
        frame = frames.get(item_id, {})
        risk_tags = []
        if missing_principle:
            risk_tags.append("missing_principle_join")
        if missing_concept:
            risk_tags.append("missing_dcr_concept_join")
        if queue.get("review_flags"):
            risk_tags.extend(flag for flag in queue["review_flags"].split(";") if flag)
        if frame.get("error"):
            risk_tags.append("frame_extraction_error")
        if source_seen:
            risk_tags.append("existing_source_duplicate")
        license_lower = license_note.lower()
        if "by-nc" in license_lower or "noncommercial" in license_lower:
            risk_tags.append("license_noncommercial")
        if "by-nd" in license_lower or "by-nc-nd" in license_lower or "no derivatives" in license_lower:
            risk_tags.append("license_no_derivatives")
        signature = concept.get("required_dynamic_signature") or principle.get("required_dynamic_signature", queue.get("why_dynamic", ""))
        reject_conditions = concept.get("reject_conditions") or principle.get("reject_conditions", "")
        hard_negatives = concept.get("hard_negative_concepts") or principle.get("hard_negative_family", "")
        proposed_knowledge_point = concept.get("dynamic_concept") or principle.get("principle", "")
        proposed_type = "named_dynamic_concept" if capability_label == "DCR" else "transferable_principle_or_mechanism"
        gate_reason = (
            "Review video first against the named dynamic concept signature; then use source page only if it specifically supports the concept/mechanism."
            if capability_label == "DCR"
            else "Review video first against required_dynamic_signature; then use source page only if it contains specific mechanism evidence."
        )
        rows.append(
            {
                "candidate_id": item_id,
                "source_url": source_url,
                "source_platform": queue.get("source_platform", ""),
                "license_or_usage_note": license_note,
                "domain": domain,
                "subdomain": subdomain,
                "capability_label": capability_label,
                "dynamic_concept_id": dynamic_concept_id,
                "dynamic_concept": concept.get("dynamic_concept", queue.get("dynamic_concept", "")),
                "linked_principle_id": concept.get("linked_principle_id", principle_id),
                "principle_id": principle_id,
                "principle": principle.get("principle", ""),
                "required_dynamic_signature": signature,
                "acceptable_video_types": principle.get("acceptable_video_types", ""),
                "reject_conditions": reject_conditions,
                "hard_negative_family": hard_negatives,
                "visible_dynamic_process": "",
                "dynamic_signature_match": "pending",
                "source_page_support_level": "pending",
                "source_page_mechanism_evidence": "",
                "source_double_check_decision": "pending_source_double_check",
                "source_double_check_reason": "",
                "source_page_context": source_context,
                "review_decision": "pending_dcr_gate" if capability_label == "DCR" else "pending_principle_gate",
                "gate_reason": gate_reason,
                "risk_tags": ";".join(risk_tags),
                "proposed_knowledge_point": proposed_knowledge_point,
                "proposed_knowledge_point_type": proposed_type,
                "answerability_notes": "Question must require the dynamic process; a single frame or source title should not be enough.",
                "distractor_requirements": (
                    "Use hard negatives from same broad visual family, not copied choices from unrelated videos: "
                    + hard_negatives
                ).strip(),
                "frame_contact_sheet": contact_sheet_path(frames_dir, item_id, frame),
                "local_media": find_local_media(media_dir, item_id),
                "is_new_source": str(not source_seen).lower(),
                "source_reuse_status": "existing_source_duplicate" if source_seen else "new_candidate_source",
            }
        )
    return rows


def build_html(rows: list[dict[str, str]], output: Path, title: str) -> None:
    total = len(rows)
    decisions = Counter(row["review_decision"] for row in rows)
    sources = Counter(row["source_reuse_status"] for row in rows)
    domains = Counter(row["domain"] for row in rows)
    capabilities = Counter(row["capability_label"] for row in rows)
    metrics = "".join(
        f'<div class="metric"><strong>{count}</strong><span>{esc(name)}</span></div>'
        for name, count in [("total", total), *capabilities.items(), *decisions.items(), *sources.items()]
    )
    domain_rows = "".join(
        f"<tr><td>{esc(domain.replace('_', ' '))}</td><td>{count}</td></tr>"
        for domain, count in sorted(domains.items())
    )
    cards = []
    for row in rows[:500]:
        sheet = ""
        if row["frame_contact_sheet"]:
            sheet = f'<img class="sheet" src="{esc(rel(row["frame_contact_sheet"], output))}" alt="contact sheet">'
        media = ""
        if row["local_media"]:
            src = esc(rel(row["local_media"], output))
            media = f'<video controls preload="metadata"><source src="{src}"><a href="{src}">Open video</a></video>'
        cards.append(
            '<article class="card">'
            f'<div class="media">{media}{sheet}</div>'
            '<div class="body">'
            f'<h2>{esc(row["candidate_id"])} <span>{esc(row["capability_label"])}</span></h2>'
            f'<p><strong>{esc(row["domain"])}</strong> / {esc(row["subdomain"])} / {esc(row["proposed_knowledge_point_type"])}</p>'
            f'<p><strong>Concept:</strong> {esc(row["dynamic_concept"])} <span class="muted">{esc(row["dynamic_concept_id"])}</span></p>'
            f'<p class="principle"><strong>Principle:</strong> {esc(row["principle"])} <span class="muted">{esc(row["principle_id"])}</span></p>'
            f'<p><strong>Dynamic signature:</strong> {esc(row["required_dynamic_signature"])}</p>'
            f'<p><strong>Reject:</strong> {esc(row["reject_conditions"])}</p>'
            f'<p><strong>Hard negatives:</strong> {esc(row["hard_negative_family"])}</p>'
            f'<p><strong>Source double-check:</strong> {esc(row["source_double_check_decision"])}</p>'
            f'<p><strong>Source context:</strong> {esc(row["source_page_context"])}</p>'
            f'<p class="flags">{esc(row["risk_tags"])}</p>'
            f'<p><a href="{esc(row["source_url"])}">source page</a></p>'
            "</div></article>"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<style>
body{{margin:0;background:#f5f6f4;color:#202124;font-family:Arial,sans-serif}}
header{{background:white;border-bottom:1px solid #d9ddd7;padding:20px 24px}}
h1{{margin:0 0 8px;font-size:24px}}
.note{{color:#5f675f;margin:0}}
.metrics{{display:flex;gap:10px;flex-wrap:wrap;padding:16px 24px}}
.metric{{background:white;border:1px solid #d9ddd7;border-radius:8px;padding:12px 14px;min-width:150px}}
.metric strong{{display:block;font-size:24px}} .metric span{{color:#5f675f}}
.panel{{margin:0 24px 16px;background:white;border:1px solid #d9ddd7;border-radius:8px;padding:14px}}
table{{border-collapse:collapse;width:100%}} th,td{{border-bottom:1px solid #e3e6e1;text-align:left;padding:7px 8px;font-size:13px}}
.cards{{display:grid;grid-template-columns:1fr;gap:12px;padding:0 24px 24px}}
.card{{display:grid;grid-template-columns:minmax(260px,430px) 1fr;gap:14px;background:white;border:1px solid #d9ddd7;border-left:5px solid #2f6f9f;border-radius:8px;padding:12px}}
video,.sheet{{width:100%;max-height:280px;background:#111;object-fit:contain}}
.sheet{{display:block;margin-top:8px;border:1px solid #d9ddd7}}
h2{{margin:0 0 8px;font-size:17px}} h2 span{{float:right;color:#5f675f;font-weight:400}}
p{{margin:7px 0;font-size:13px;line-height:1.38}} .principle{{color:#166534}} .flags{{color:#9a3412}} .muted{{color:#5f675f;font-weight:400}}
a{{color:#0645ad}}
@media(max-width:800px){{.card{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header><h1>{esc(title)}</h1><p class="note">Gate order: video dynamic signature first; source page only supports the mechanism when it is specific, not broad metadata.</p></header>
<section class="metrics">{metrics}</section>
<section class="panel"><h2>Domain Counts</h2><table><thead><tr><th>Domain</th><th>Rows</th></tr></thead><tbody>{domain_rows}</tbody></table></section>
<section class="cards">{''.join(cards)}</section>
</body></html>""",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", required=True, type=Path)
    parser.add_argument("--inventory", default=Path("data/principle_inventory_v1.csv"), type=Path)
    parser.add_argument("--concept-inventory", default=Path("data/dynamic_concept_inventory_v1.csv"), type=Path)
    parser.add_argument("--frame-status", type=Path)
    parser.add_argument("--media-dir", type=Path)
    parser.add_argument("--frames-dir", type=Path)
    parser.add_argument("--existing-sources", type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--output-html", required=True, type=Path)
    parser.add_argument("--title", default="DynaKnow Principle Gate Review")
    args = parser.parse_args()

    rows = build_rows(
        read_csv(args.queue),
        read_csv(args.inventory),
        read_csv(args.concept_inventory),
        read_csv(args.frame_status) if args.frame_status else [],
        args.media_dir,
        args.frames_dir,
        source_urls(args.existing_sources),
    )
    write_csv(args.output_csv, rows)
    build_html(rows, args.output_html, args.title)
    print(f"wrote {len(rows)} principle-gate rows to {args.output_csv}")
    print(f"wrote principle-gate report to {args.output_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
