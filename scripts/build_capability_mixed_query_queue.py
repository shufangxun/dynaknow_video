#!/usr/bin/env python3
"""Build a mixed DMR/DCR query queue for capability-labeled retrieval."""

from __future__ import annotations

import argparse
import csv
import html
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from taxonomy_aliases import normalize_domain_subdomain  # noqa: E402


DMR_DEFAULT = {
    "capability_label": "DMR",
    "dynamic_concept_id": "",
    "dynamic_concept": "",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def normalize_dmr(row: dict[str, str]) -> dict[str, str]:
    out = dict(row)
    domain, subdomain = normalize_domain_subdomain(out.get("domain_seed", ""), out.get("subdomain_seed", ""))
    out["initial_category"] = domain
    out["domain_seed"] = domain
    out["subdomain_seed"] = subdomain
    for key, value in DMR_DEFAULT.items():
        out.setdefault(key, value)
    notes = out.get("notes", "")
    if "capability_label=" not in notes:
        out["notes"] = f"{notes}; capability_label=DMR".strip("; ")
    collector = out.get("collector_notes", notes)
    if "capability_label=" not in collector:
        out["collector_notes"] = f"{collector}; capability_label=DMR".strip("; ")
    return out


def normalize_dcr(row: dict[str, str]) -> dict[str, str]:
    out = dict(row)
    domain, subdomain = normalize_domain_subdomain(out.get("domain_seed", ""), out.get("subdomain_seed", ""))
    out["initial_category"] = domain
    out["domain_seed"] = domain
    out["subdomain_seed"] = subdomain
    out["capability_label"] = "DCR"
    return out


def interleave(dmr_rows: list[dict[str, str]], dcr_rows: list[dict[str, str]], dmr_per_dcr: int) -> list[dict[str, str]]:
    dmr_by_key: dict[tuple[str, str], deque[dict[str, str]]] = defaultdict(deque)
    dcr_by_key: dict[tuple[str, str], deque[dict[str, str]]] = defaultdict(deque)
    for row in dmr_rows:
        dmr_by_key[(row.get("domain_seed", ""), row.get("subdomain_seed", ""))].append(row)
    for row in dcr_rows:
        dcr_by_key[(row.get("domain_seed", ""), row.get("subdomain_seed", ""))].append(row)
    keys = sorted(set(dmr_by_key) | set(dcr_by_key))
    ordered: list[dict[str, str]] = []
    while any(dmr_by_key.values()) or any(dcr_by_key.values()):
        made_progress = False
        for key in keys:
            for _ in range(max(1, dmr_per_dcr)):
                if dmr_by_key[key]:
                    ordered.append(dmr_by_key[key].popleft())
                    made_progress = True
            if dcr_by_key[key]:
                ordered.append(dcr_by_key[key].popleft())
                made_progress = True
        if not made_progress:
            break
    for index, row in enumerate(ordered, start=1):
        row["capability_queue_rank"] = str(index)
    return ordered


def write_csv(path: Path, rows: list[dict[str, str]], field_order: list[str]) -> None:
    fields = list(dict.fromkeys(field_order + ["capability_label", "dynamic_concept_id", "dynamic_concept", "capability_queue_rank"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_html(path: Path, rows: list[dict[str, str]], title: str) -> None:
    by_capability = Counter(row.get("capability_label", "") for row in rows)
    by_domain = Counter((row.get("capability_label", ""), row.get("domain_seed", "")) for row in rows)
    cap_rows = "".join(
        "<tr>"
        f"<td>{esc(label)}</td>"
        f"<td class=\"num\">{count}</td>"
        "</tr>"
        for label, count in sorted(by_capability.items())
    )
    domain_rows = "".join(
        "<tr>"
        f"<td>{esc(label)}</td>"
        f"<td>{esc(domain.replace('_', ' '))}</td>"
        f"<td class=\"num\">{count}</td>"
        "</tr>"
        for (label, domain), count in sorted(by_domain.items())
    )
    query_rows = "".join(
        "<tr>"
        f"<td class=\"num\">{esc(row.get('capability_queue_rank', ''))}</td>"
        f"<td>{esc(row.get('capability_label', ''))}</td>"
        f"<td>{esc(row.get('domain_seed', '').replace('_', ' '))}</td>"
        f"<td>{esc(row.get('subdomain_seed', '').replace('_', ' '))}</td>"
        f"<td>{esc(row.get('search_term', ''))}</td>"
        f"<td>{esc(row.get('dynamic_concept', ''))}</td>"
        f"<td>{esc(row.get('why_dynamic', ''))}</td>"
        "</tr>"
        for row in rows
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
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
.num{{text-align:right;white-space:nowrap}}
</style>
</head>
<body>
<header><h1>{esc(title)}</h1><p class="note">Mixed retrieval queue: DMR gap-aware mechanism queries plus DCR named dynamic concept queries.</p></header>
<section class="metrics"><div class="metric"><strong>{len(rows)}</strong><span>queries</span></div><div class="metric"><strong>{by_capability.get('DMR', 0)}</strong><span>DMR queries</span></div><div class="metric"><strong>{by_capability.get('DCR', 0)}</strong><span>DCR queries</span></div></section>
<section class="panel"><h2>Capability Counts</h2><table><thead><tr><th>Capability</th><th class="num">Queries</th></tr></thead><tbody>{cap_rows}</tbody></table></section>
<section class="panel"><h2>Domain Counts</h2><table><thead><tr><th>Capability</th><th>Domain</th><th class="num">Queries</th></tr></thead><tbody>{domain_rows}</tbody></table></section>
<section class="panel"><h2>Mixed Query Queue</h2><table><thead><tr><th class="num">Rank</th><th>Capability</th><th>Domain</th><th>Subdomain</th><th>Search Term</th><th>DCR Concept</th><th>Dynamic Signature</th></tr></thead><tbody>{query_rows}</tbody></table></section>
</body></html>""",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dmr-queries", default=Path("data/principle_gap_aware_search_queries_v1_20260605.csv"), type=Path)
    parser.add_argument("--dmr-fallback-queries", default=Path("data/principle_search_queries_v1.csv"), type=Path)
    parser.add_argument("--dcr-queries", default=Path("data/dynamic_concept_search_queries_v1.csv"), type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--output-html", required=True, type=Path)
    parser.add_argument("--dmr-per-dcr", type=int, default=2)
    parser.add_argument("--title", default="Capability-Mixed Query Queue")
    args = parser.parse_args()

    dmr_query_path = args.dmr_queries if args.dmr_queries.exists() else args.dmr_fallback_queries
    dmr_rows = [normalize_dmr(row) for row in read_csv(dmr_query_path)]
    dcr_rows = [normalize_dcr(row) for row in read_csv(args.dcr_queries)]
    rows = interleave(dmr_rows, dcr_rows, args.dmr_per_dcr)
    base_fields = list(read_csv(dmr_query_path)[0].keys()) if dmr_rows else []
    if dcr_rows:
        base_fields.extend(read_csv(args.dcr_queries)[0].keys())
    write_csv(args.output_csv, rows, base_fields)
    write_html(args.output_html, rows, args.title)
    print(f"wrote {len(rows)} mixed capability query rows to {args.output_csv}")
    print(f"wrote mixed capability query report to {args.output_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
