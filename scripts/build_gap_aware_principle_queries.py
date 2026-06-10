#!/usr/bin/env python3
"""Build a gap-aware principle-first retrieval query queue."""

from __future__ import annotations

import argparse
import csv
import html
import re
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from taxonomy_aliases import normalize_domain_subdomain  # noqa: E402


PRIORITY_SCORE = {"core": 0, "supporting": 1, "edge": 2}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def note_value(notes: str, key: str) -> str:
    match = re.search(rf"(?:^|;\s*){re.escape(key)}=([^;]+)", notes or "")
    return match.group(1).strip() if match else ""


def principle_id(row: dict[str, str]) -> str:
    return note_value(row.get("notes", "") or row.get("collector_notes", ""), "principle_id")


def priority_value(row: dict[str, str], inventory_by_id: dict[str, dict[str, str]]) -> str:
    from_notes = note_value(row.get("notes", "") or row.get("collector_notes", ""), "priority")
    if from_notes:
        return from_notes
    pid = principle_id(row)
    return inventory_by_id.get(pid, {}).get("priority", "")


def build_rows(
    query_rows: list[dict[str, str]],
    gap_rows: list[dict[str, str]],
    inventory_rows: list[dict[str, str]],
    max_queries_per_subdomain: int,
    include_zero_min_gap: bool,
) -> list[dict[str, str]]:
    inventory_by_id = {row["principle_id"]: row for row in inventory_rows}
    gap_by_subdomain = {
        normalize_domain_subdomain(row["domain"], row["subdomain"]): row
        for row in gap_rows
        if include_zero_min_gap
        or int(row.get("estimated_new_needed", "") or 0) > 0
        or int(row.get("stretch_new_needed", "") or 0) > 0
        or int(row.get("replace_or_rewrite", "") or 0) > 0
        or int(row.get("missing_source_url", "") or 0) > 0
    }
    original_index = {id(row): idx for idx, row in enumerate(query_rows)}
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in query_rows:
        key = normalize_domain_subdomain(
            row.get("domain_seed", "") or row.get("initial_category", ""),
            row.get("subdomain_seed", ""),
        )
        if key not in gap_by_subdomain:
            continue
        grouped[key].append(row)

    for key, rows in grouped.items():
        rows.sort(
            key=lambda row: (
                PRIORITY_SCORE.get(priority_value(row, inventory_by_id), 9),
                principle_id(row),
                original_index[id(row)],
            )
        )
        if max_queries_per_subdomain > 0:
            grouped[key] = rows[:max_queries_per_subdomain]

    subdomain_order = sorted(
        grouped,
        key=lambda key: (
            -int(gap_by_subdomain[key].get("estimated_new_needed", "") or 0),
            -int(gap_by_subdomain[key].get("replace_or_rewrite", "") or 0),
            -int(gap_by_subdomain[key].get("stretch_new_needed", "") or 0),
            key[0],
            key[1],
        ),
    )

    queues = {key: deque(grouped[key]) for key in subdomain_order}
    ordered: list[dict[str, str]] = []
    while queues:
        for key in list(subdomain_order):
            queue = queues.get(key)
            if not queue:
                queues.pop(key, None)
                continue
            source = queue.popleft()
            gap = gap_by_subdomain[key]
            pid = principle_id(source)
            inventory = inventory_by_id.get(pid, {})
            row = dict(source)
            row["initial_category"] = key[0]
            row["domain_seed"] = key[0]
            row["subdomain_seed"] = key[1]
            row["gap_rank"] = str(len(ordered) + 1)
            row["principle_id"] = pid
            row["principle"] = inventory.get("principle", "")
            row["principle_priority"] = priority_value(source, inventory_by_id)
            row["target_n"] = gap.get("target_n", "")
            row["stretch_target_n"] = gap.get("stretch_target_n", "")
            row["strong_keep_candidates"] = gap.get("strong_keep_candidates", "")
            row["replace_or_rewrite"] = gap.get("replace_or_rewrite", "")
            row["estimated_new_needed"] = gap.get("estimated_new_needed", "")
            row["stretch_new_needed"] = gap.get("stretch_new_needed", "")
            row["gap_priority"] = gap.get("priority", "")
            extra = (
                f"gap_rank={row['gap_rank']}; gap_new_needed={row['estimated_new_needed']}; "
                f"gap_priority={row['gap_priority']}; strong_keep_candidates={row['strong_keep_candidates']}; "
                f"replace_or_rewrite={row['replace_or_rewrite']}"
            )
            row["notes"] = f"{source.get('notes', '')}; {extra}".strip("; ")
            row["collector_notes"] = f"{source.get('collector_notes', source.get('notes', ''))}; {extra}".strip("; ")
            ordered.append(row)
    return ordered


def write_csv(path: Path, rows: list[dict[str, str]], base_fields: list[str]) -> None:
    extra_fields = [
        "gap_rank",
        "principle_id",
        "principle",
        "principle_priority",
        "target_n",
        "stretch_target_n",
        "strong_keep_candidates",
        "replace_or_rewrite",
        "estimated_new_needed",
        "stretch_new_needed",
        "gap_priority",
    ]
    fields = list(dict.fromkeys(base_fields + extra_fields))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_html(path: Path, rows: list[dict[str, str]], title: str) -> None:
    by_domain = Counter(row.get("domain_seed", "") for row in rows)
    by_subdomain: Counter[tuple[str, str]] = Counter(
        (row.get("domain_seed", ""), row.get("subdomain_seed", "")) for row in rows
    )
    domain_rows = "".join(
        "<tr>"
        f"<td>{esc(domain.replace('_', ' '))}</td>"
        f"<td class=\"num\">{count}</td>"
        "</tr>"
        for domain, count in sorted(by_domain.items())
    )
    top_subdomains = "".join(
        "<tr>"
        f"<td>{esc(domain.replace('_', ' '))}</td>"
        f"<td>{esc(subdomain.replace('_', ' '))}</td>"
        f"<td class=\"num\">{count}</td>"
        "</tr>"
        for (domain, subdomain), count in by_subdomain.most_common(40)
    )
    query_rows = "".join(
        "<tr>"
        f"<td class=\"num\">{esc(row.get('gap_rank', ''))}</td>"
        f"<td>{esc(row.get('domain_seed', '').replace('_', ' '))}</td>"
        f"<td>{esc(row.get('subdomain_seed', '').replace('_', ' '))}</td>"
        f"<td>{esc(row.get('search_term', ''))}</td>"
        f"<td>{esc(row.get('principle', ''))}</td>"
        f"<td>{esc(row.get('why_dynamic', ''))}</td>"
        f"<td class=\"num\">{esc(row.get('estimated_new_needed', ''))}</td>"
        f"<td>{esc(row.get('gap_priority', ''))}</td>"
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
<header><h1>{esc(title)}</h1><p class="note">Queries are ordered by replacement gaps, but still require video-first dynamic signature review and source double-check.</p></header>
<section class="metrics"><div class="metric"><strong>{len(rows)}</strong><span>queries</span></div><div class="metric"><strong>{len(by_subdomain)}</strong><span>subdomains</span></div><div class="metric"><strong>{len(by_domain)}</strong><span>domains</span></div></section>
<section class="panel"><h2>Domain Query Counts</h2><table><thead><tr><th>Domain</th><th class="num">Queries</th></tr></thead><tbody>{domain_rows}</tbody></table></section>
<section class="panel"><h2>Subdomain Query Counts</h2><table><thead><tr><th>Domain</th><th>Subdomain</th><th class="num">Queries</th></tr></thead><tbody>{top_subdomains}</tbody></table></section>
<section class="panel"><h2>Ordered Query Queue</h2><table><thead><tr><th class="num">Rank</th><th>Domain</th><th>Subdomain</th><th>Search Term</th><th>Principle</th><th>Dynamic Signature</th><th class="num">New Needed</th><th>Gap Priority</th></tr></thead><tbody>{query_rows}</tbody></table></section>
</body></html>""",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", default=Path("data/principle_search_queries_v1.csv"), type=Path)
    parser.add_argument("--gaps", default=Path("data/principle_replacement_gaps_v1_20260605.csv"), type=Path)
    parser.add_argument("--inventory", default=Path("data/principle_inventory_v1.csv"), type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--output-html", required=True, type=Path)
    parser.add_argument("--max-queries-per-subdomain", type=int, default=0)
    parser.add_argument("--include-zero-min-gap", action="store_true")
    parser.add_argument("--title", default="Gap-Aware Principle Query Queue")
    args = parser.parse_args()

    query_rows = read_csv(args.queries)
    rows = build_rows(
        query_rows,
        read_csv(args.gaps),
        read_csv(args.inventory),
        args.max_queries_per_subdomain,
        args.include_zero_min_gap,
    )
    write_csv(args.output_csv, rows, list(query_rows[0].keys()) if query_rows else [])
    write_html(args.output_html, rows, args.title)
    print(f"wrote {len(rows)} gap-aware query rows to {args.output_csv}")
    print(f"wrote gap-aware query report to {args.output_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
