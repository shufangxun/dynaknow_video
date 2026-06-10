#!/usr/bin/env python3
"""Report replacement gaps from the principle-first audit."""

from __future__ import annotations

import argparse
import csv
import html
from collections import Counter, defaultdict
from pathlib import Path


FIELDS = [
    "domain",
    "subdomain",
    "target_n",
    "stretch_target_n",
    "current_total",
    "strong_keep_candidates",
    "replace_or_rewrite",
    "missing_source_url",
    "source_recovered",
    "weak_mapping",
    "unmapped",
    "estimated_new_needed",
    "stretch_new_needed",
    "priority",
    "top_risk_tags",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build_rows(audit_rows: list[dict[str, str]], targets: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in audit_rows:
        grouped[(row["domain"], row["subdomain"])].append(row)
    target_min_map = {
        (row["domain"], row["subdomain"]): int(
            row.get("target_n", "")
            or row.get("target_count", "")
            or row.get("min_v1_count", "")
            or 8
        )
        for row in targets
        if row.get("domain") and row.get("subdomain")
    }
    target_stretch_map = {
        (row["domain"], row["subdomain"]): int(
            row.get("target_v1_count", "")
            or row.get("stretch_target_n", "")
            or row.get("target_n", "")
            or row.get("target_count", "")
            or row.get("min_v1_count", "")
            or 8
        )
        for row in targets
        if row.get("domain") and row.get("subdomain")
    }
    keys = sorted(set(grouped) | set(target_min_map))
    output = []
    for domain, subdomain in keys:
        rows = grouped.get((domain, subdomain), [])
        target = target_min_map.get((domain, subdomain), 8)
        stretch_target = target_stretch_map.get((domain, subdomain), target)
        strong = sum(row.get("principle_gate_decision") == "audit_candidate_keep" for row in rows)
        replace = sum(row.get("principle_gate_decision") == "audit_candidate_replace_or_rewrite" for row in rows)
        missing_source = sum("missing_source_url" in row.get("risk_tags", "").split(";") for row in rows)
        source_recovered = sum("source_url_recovered_from_prior_manifest" in row.get("risk_tags", "").split(";") for row in rows)
        weak = sum(row.get("mapping_status") == "weak_candidate" for row in rows)
        unmapped = sum(row.get("mapping_status") == "unmapped" for row in rows)
        min_gap = max(0, target - strong)
        stretch_gap = max(0, stretch_target - strong)
        if strong == 0:
            priority = "urgent_no_strong_keep"
        elif min_gap > 0:
            priority = "needs_new_pass_samples"
        elif replace > 0 or missing_source > 0 or weak > 0 or unmapped > 0:
            priority = "covered_but_replace_weak_rows"
        else:
            priority = "covered_after_audit"
        risks = Counter(flag for row in rows for flag in row.get("risk_tags", "").split(";") if flag)
        output.append(
            {
                "domain": domain,
                "subdomain": subdomain,
                "target_n": str(target),
                "stretch_target_n": str(stretch_target),
                "current_total": str(len(rows)),
                "strong_keep_candidates": str(strong),
                "replace_or_rewrite": str(replace),
                "missing_source_url": str(missing_source),
                "source_recovered": str(source_recovered),
                "weak_mapping": str(weak),
                "unmapped": str(unmapped),
                "estimated_new_needed": str(min_gap),
                "stretch_new_needed": str(stretch_gap),
                "priority": priority,
                "top_risk_tags": ";".join(f"{flag}:{count}" for flag, count in risks.most_common(5)),
            }
        )
    priority_order = {
        "urgent_no_strong_keep": 0,
        "needs_new_pass_samples": 1,
        "covered_but_replace_weak_rows": 2,
        "covered_after_audit": 3,
    }
    output.sort(
        key=lambda row: (
            priority_order.get(row["priority"], 99),
            -int(row["estimated_new_needed"]),
            row["domain"],
            row["subdomain"],
        )
    )
    return output


def build_html(rows: list[dict[str, str]], output: Path, title: str) -> None:
    total_needed = sum(int(row["estimated_new_needed"]) for row in rows)
    total_stretch_needed = sum(int(row["stretch_new_needed"]) for row in rows)
    total_replace = sum(int(row["replace_or_rewrite"]) for row in rows)
    total_strong = sum(int(row["strong_keep_candidates"]) for row in rows)
    priority_counts = Counter(row["priority"] for row in rows)
    domain_rows = []
    by_domain: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_domain[row["domain"]].append(row)
    for domain, domain_items in sorted(by_domain.items()):
        domain_rows.append(
            "<tr>"
            f"<td>{esc(domain.replace('_', ' '))}</td>"
            f"<td class=\"num\">{len(domain_items)}</td>"
            f"<td class=\"num\">{sum(int(row['target_n']) for row in domain_items)}</td>"
            f"<td class=\"num\">{sum(int(row['strong_keep_candidates']) for row in domain_items)}</td>"
            f"<td class=\"num\">{sum(int(row['replace_or_rewrite']) for row in domain_items)}</td>"
            f"<td class=\"num\">{sum(int(row['estimated_new_needed']) for row in domain_items)}</td>"
            f"<td>{esc('; '.join(f'{key}:{value}' for key, value in Counter(row['priority'] for row in domain_items).most_common()))}</td>"
            "</tr>"
        )
    priority_rows = "".join(
        "<tr>"
        f"<td>{esc(priority)}</td>"
        f"<td class=\"num\">{count}</td>"
        "</tr>"
        for priority, count in priority_counts.most_common()
    )
    rows_html = "".join(
        "<tr>"
        f"<td>{esc(row['domain'].replace('_', ' '))}</td>"
        f"<td>{esc(row['subdomain'].replace('_', ' '))}</td>"
        f"<td class=\"num\">{esc(row['target_n'])}</td>"
        f"<td class=\"num\">{esc(row['stretch_target_n'])}</td>"
        f"<td class=\"num\">{esc(row['current_total'])}</td>"
        f"<td class=\"num\">{esc(row['strong_keep_candidates'])}</td>"
        f"<td class=\"num\">{esc(row['replace_or_rewrite'])}</td>"
        f"<td class=\"num\">{esc(row['weak_mapping'])}</td>"
        f"<td class=\"num\">{esc(row['unmapped'])}</td>"
        f"<td class=\"num\">{esc(row['missing_source_url'])}</td>"
        f"<td class=\"num\">{esc(row['estimated_new_needed'])}</td>"
        f"<td class=\"num\">{esc(row['stretch_new_needed'])}</td>"
        f"<td>{esc(row['priority'])}</td>"
        f"<td>{esc(row['top_risk_tags'])}</td>"
        "</tr>"
        for row in rows
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
.metric{{background:white;border:1px solid #d9ddd7;border-radius:8px;padding:12px 14px;min-width:160px}}
.metric strong{{display:block;font-size:24px}} .metric span{{color:#5f675f}}
.panel{{margin:0 24px 24px;background:white;border:1px solid #d9ddd7;border-radius:8px;padding:14px;overflow:auto}}
table{{border-collapse:collapse;width:100%}} th,td{{border-bottom:1px solid #e3e6e1;text-align:left;padding:7px 8px;font-size:13px;vertical-align:top}}
.num{{text-align:right;white-space:nowrap}} a{{color:#0645ad}}
code{{background:#eef3f1;border-radius:4px;padding:1px 4px}}
</style>
</head>
<body>
<header><h1>{esc(title)}</h1><p class="note">Estimated new-needed = v1 minimum target minus strong principle-mapped keep candidates. Strong keep still means <code>audit candidate</code>, not final v2 pass; each row still needs video/source double-check.</p></header>
<section class="metrics"><div class="metric"><strong>{len(rows)}</strong><span>subdomains</span></div><div class="metric"><strong>{total_strong}</strong><span>strong keep candidates</span></div><div class="metric"><strong>{total_needed}</strong><span>min-target new needed</span></div><div class="metric"><strong>{total_stretch_needed}</strong><span>stretch-target new needed</span></div><div class="metric"><strong>{total_replace}</strong><span>replace/rewrite rows</span></div></section>
<section class="panel"><h2>Domain Summary</h2><table><thead><tr><th>Domain</th><th class="num">Subdomains</th><th class="num">Min Target</th><th class="num">Strong Keep</th><th class="num">Replace/Rewrite</th><th class="num">New Needed</th><th>Priorities</th></tr></thead><tbody>{''.join(domain_rows)}</tbody></table></section>
<section class="panel"><h2>Priority Summary</h2><table><thead><tr><th>Priority</th><th class="num">Subdomains</th></tr></thead><tbody>{priority_rows}</tbody></table></section>
<section class="panel"><h2>Subdomain Gap Task List</h2><table><thead><tr><th>Domain</th><th>Subdomain</th><th class="num">Min Target</th><th class="num">Stretch</th><th class="num">Current</th><th class="num">Strong Keep</th><th class="num">Replace/Rewrite</th><th class="num">Weak</th><th class="num">Unmapped</th><th class="num">Missing Source</th><th class="num">New Needed</th><th class="num">Stretch Gap</th><th>Priority</th><th>Top Risks</th></tr></thead><tbody>{rows_html}</tbody></table></section>
</body></html>""",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--targets", default=Path("data/domain_sampling_targets_v1.csv"), type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--output-html", required=True, type=Path)
    parser.add_argument("--title", default="Principle Replacement Gaps")
    args = parser.parse_args()
    rows = build_rows(read_csv(args.audit), read_csv(args.targets))
    write_csv(args.output_csv, rows)
    build_html(rows, args.output_html, args.title)
    print(f"wrote {len(rows)} replacement gap rows to {args.output_csv}")
    print(f"wrote replacement gap report to {args.output_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
