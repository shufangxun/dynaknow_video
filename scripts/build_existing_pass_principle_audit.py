#!/usr/bin/env python3
"""Audit current pass-only release against the principle-first inventory."""

from __future__ import annotations

import argparse
import csv
import html
import json
import mimetypes
import os
from collections import Counter
from pathlib import Path


FIELDS = [
    "video_id",
    "domain",
    "subdomain",
    "current_knowledge_point",
    "best_principle_id",
    "best_principle",
    "required_dynamic_signature",
    "mapping_status",
    "mapping_score",
    "audit_action",
    "dynamic_evidence",
    "static_insufficient_reason",
    "source_url",
    "license_or_usage_note",
    "local_media",
    "duration_sec",
    "risk_tags",
    "principle_gate_decision",
    "gate_reason",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def rel(path: str, output: Path) -> str:
    return esc(os.path.relpath(path, start=output.parent))


def media_type(path: str) -> str:
    guessed, _ = mimetypes.guess_type(path)
    if guessed:
        return guessed
    if path.endswith(".ogv") or path.endswith(".ogg"):
        return "video/ogg"
    if path.endswith(".webm"):
        return "video/webm"
    if path.endswith(".mp4"):
        return "video/mp4"
    return "video/*"


def render_media(path: str, output: Path) -> str:
    if not path or not Path(path).exists():
        return '<div class="missing">No local media</div>'
    src = rel(path, output)
    return (
        '<video controls preload="metadata">'
        f'<source src="{src}" type="{esc(media_type(path))}">'
        f'<a href="{src}">Open video</a>'
        "</video>"
    )


def build_rows(samples: list[dict], manifest_rows: list[dict[str, str]], mapping_rows: list[dict[str, str]], inventory_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    manifest = {row.get("video_id", ""): row for row in manifest_rows}
    mapping = {row.get("video_id", ""): row for row in mapping_rows}
    inventory = {row.get("principle_id", ""): row for row in inventory_rows}
    rows: list[dict[str, str]] = []
    for sample in samples:
        video_id = sample.get("video_id", "")
        mapped = mapping.get(video_id, {})
        principle = inventory.get(mapped.get("best_principle_id", ""), {})
        mani = manifest.get(video_id, {})
        risk_tags = []
        if mapped.get("mapping_status") == "unmapped":
            risk_tags.append("unmapped_to_principle")
        elif mapped.get("mapping_status") == "weak_candidate":
            risk_tags.append("weak_principle_mapping")
        if sample.get("shortcut_labels", {}).get("single_frame_sufficient") == "yes":
            risk_tags.append("single_frame_shortcut")
        if not mani.get("source_url") and not sample.get("source_url"):
            risk_tags.append("missing_source_url")
        if not principle:
            risk_tags.append("missing_inventory_principle")
        evidence = " | ".join(
            str(span.get("description", "")) for span in sample.get("dynamic_evidence", []) if span.get("description")
        )
        if mapped.get("mapping_status") == "strong_candidate" and principle:
            decision = "audit_candidate_keep"
            reason = "Mapped to a principle inventory row; still requires video/source double-check before final v2 pass."
        else:
            decision = "audit_candidate_replace_or_rewrite"
            reason = "Weak or missing principle mapping under the principle-first mechanism."
        rows.append(
            {
                "video_id": video_id,
                "domain": sample.get("domain", ""),
                "subdomain": sample.get("subdomain", ""),
                "current_knowledge_point": sample.get("knowledge_point", ""),
                "best_principle_id": mapped.get("best_principle_id", ""),
                "best_principle": mapped.get("best_principle", ""),
                "required_dynamic_signature": principle.get("required_dynamic_signature", ""),
                "mapping_status": mapped.get("mapping_status", ""),
                "mapping_score": mapped.get("mapping_score", ""),
                "audit_action": mapped.get("action", ""),
                "dynamic_evidence": evidence,
                "static_insufficient_reason": sample.get("static_insufficient_reason", ""),
                "source_url": mani.get("source_url", sample.get("source_url", "")),
                "license_or_usage_note": mani.get("license_or_usage_note", sample.get("license_or_usage_note", "")),
                "local_media": sample.get("local_media", mani.get("local_media", "")),
                "duration_sec": str(sample.get("duration_sec", mani.get("duration_sec", ""))),
                "risk_tags": ";".join(risk_tags),
                "principle_gate_decision": decision,
                "gate_reason": reason,
            }
        )
    return rows


def build_source_lookup(paths: list[Path]) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for path in paths:
        for row in read_csv(path):
            video_id = row.get("video_id", "")
            source_url = row.get("source_url", "")
            if not video_id or not source_url:
                continue
            current = lookup.get(video_id, {})
            if not current.get("source_url"):
                lookup[video_id] = {
                    "source_url": source_url,
                    "license_or_usage_note": row.get("license_or_usage_note", ""),
                    "source_lookup_path": str(path),
                }
    return lookup


def apply_source_lookup(rows: list[dict[str, str]], source_lookup: dict[str, dict[str, str]]) -> None:
    for row in rows:
        if row.get("source_url"):
            continue
        source = source_lookup.get(row["video_id"], {})
        if not source:
            continue
        row["source_url"] = source.get("source_url", "")
        row["license_or_usage_note"] = row.get("license_or_usage_note") or source.get("license_or_usage_note", "")
        risks = [flag for flag in row["risk_tags"].split(";") if flag and flag != "missing_source_url"]
        risks.append("source_url_recovered_from_prior_manifest")
        row["risk_tags"] = ";".join(risks)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_html(rows: list[dict[str, str]], output: Path, title: str) -> None:
    total = len(rows)
    decisions = Counter(row["principle_gate_decision"] for row in rows)
    mapping = Counter(row["mapping_status"] for row in rows)
    domains = Counter(row["domain"] for row in rows)
    risks = Counter(flag for row in rows for flag in row["risk_tags"].split(";") if flag)
    metric_html = "".join(
        f'<div class="metric"><strong>{count}</strong><span>{esc(name)}</span></div>'
        for name, count in [("total", total), *decisions.items(), *mapping.items()]
    )
    domain_rows = "".join(
        f"<tr><td>{esc(domain.replace('_', ' '))}</td><td>{count}</td></tr>"
        for domain, count in sorted(domains.items())
    )
    risk_rows = "".join(f"<tr><td>{esc(flag)}</td><td>{count}</td></tr>" for flag, count in risks.most_common())
    card_rows = []
    for row in rows:
        card_rows.append(
            f'<article class="card {esc(row["principle_gate_decision"])}">'
            f'<div class="media">{render_media(row["local_media"], output)}</div>'
            '<div class="body">'
            f'<h2>{esc(row["video_id"])} <span>{esc(row["mapping_status"])}</span></h2>'
            f'<p><strong>{esc(row["domain"])}</strong> / {esc(row["subdomain"])}</p>'
            f'<p class="kp">{esc(row["current_knowledge_point"])}</p>'
            f'<p class="principle">{esc(row["best_principle_id"])}: {esc(row["best_principle"])}</p>'
            f'<p><strong>Dynamic signature:</strong> {esc(row["required_dynamic_signature"])}</p>'
            f'<p><strong>Evidence:</strong> {esc(row["dynamic_evidence"])}</p>'
            f'<p><strong>Gate:</strong> {esc(row["principle_gate_decision"])}</p>'
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
h1{{margin:0 0 8px;font-size:24px}} .note{{color:#5f675f;margin:0}}
.metrics{{display:flex;gap:10px;flex-wrap:wrap;padding:16px 24px}}
.metric{{background:white;border:1px solid #d9ddd7;border-radius:8px;padding:12px 14px;min-width:150px}}
.metric strong{{display:block;font-size:24px}} .metric span{{color:#5f675f}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:0 24px}}
.panel{{background:white;border:1px solid #d9ddd7;border-radius:8px;padding:14px;margin-bottom:16px}}
table{{border-collapse:collapse;width:100%}} th,td{{border-bottom:1px solid #e3e6e1;text-align:left;padding:7px 8px;font-size:13px}}
.cards{{display:grid;grid-template-columns:1fr;gap:12px;padding:0 24px 24px}}
.card{{display:grid;grid-template-columns:minmax(260px,430px) 1fr;gap:14px;background:white;border:1px solid #d9ddd7;border-left:5px solid #2f6f9f;border-radius:8px;padding:12px}}
.audit_candidate_replace_or_rewrite{{border-left-color:#b91c1c}}
video{{width:100%;max-height:280px;background:#111;object-fit:contain}}
.missing{{height:160px;display:grid;place-items:center;background:#e5e7eb;color:#52606d}}
h2{{margin:0 0 8px;font-size:17px}} h2 span{{float:right;color:#5f675f;font-weight:400}}
p{{margin:7px 0;font-size:13px;line-height:1.38}} .kp{{font-weight:700}} .principle{{color:#166534}} .flags{{color:#9a3412}}
a{{color:#0645ad}} @media(max-width:900px){{.card,.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header><h1>{esc(title)}</h1><p class="note">Audit only. Existing pass samples are not automatically accepted under the principle-first benchmark.</p></header>
<section class="metrics">{metric_html}</section>
<section class="grid"><div class="panel"><h2>Domains</h2><table><thead><tr><th>Domain</th><th>Rows</th></tr></thead><tbody>{domain_rows}</tbody></table></div><div class="panel"><h2>Risk Tags</h2><table><thead><tr><th>Risk</th><th>Rows</th></tr></thead><tbody>{risk_rows}</tbody></table></div></section>
<section class="cards">{''.join(card_rows)}</section>
</body></html>""",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval", default=Path("release/v1_1_mechanism_principle_pass_only/eval.jsonl"), type=Path)
    parser.add_argument("--manifest", default=Path("release/v1_1_mechanism_principle_pass_only/manifest.csv"), type=Path)
    parser.add_argument("--mapping", default=Path("data/principle_existing_release_mapping_v1.csv"), type=Path)
    parser.add_argument("--inventory", default=Path("data/principle_inventory_v1.csv"), type=Path)
    parser.add_argument("--source-lookup", action="append", type=Path, default=[])
    parser.add_argument("--auto-source-lookup", action="store_true")
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--output-html", required=True, type=Path)
    parser.add_argument("--title", default="Existing Pass Principle-First Audit")
    args = parser.parse_args()
    rows = build_rows(read_jsonl(args.eval), read_csv(args.manifest), read_csv(args.mapping), read_csv(args.inventory))
    source_lookup_paths = list(args.source_lookup)
    if args.auto_source_lookup:
        source_lookup_paths.extend(sorted(Path("release").glob("v*/manifest.csv")))
        source_lookup_paths.extend(sorted(Path("release").glob("v*/dynaknow_video_pilot*_manifest.csv")))
    if source_lookup_paths:
        apply_source_lookup(rows, build_source_lookup(source_lookup_paths))
    write_csv(args.output_csv, rows)
    build_html(rows, args.output_html, args.title)
    print(f"wrote {len(rows)} existing-pass audit rows to {args.output_csv}")
    print(f"wrote existing-pass audit report to {args.output_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
