#!/usr/bin/env python3
"""Build domain/subdomain distribution charts for DynaKnow samples."""

from __future__ import annotations

import argparse
import csv
import html
import json
from collections import Counter, defaultdict
from pathlib import Path

from taxonomy_aliases import normalize_domain_subdomain


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_taxonomy(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = []
        for row in csv.DictReader(handle):
            row["domain"], row["subdomain"] = normalize_domain_subdomain(
                row.get("domain", ""),
                row.get("subdomain", ""),
            )
            rows.append(row)
        return rows


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def pct(value: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{100.0 * value / total:.1f}%"


def css_width(value: int, max_value: int) -> str:
    if max_value <= 0:
        return "0%"
    return f"{max(3.0, 100.0 * value / max_value):.1f}%"


def label(value: str) -> str:
    return value.replace("_", " ")


def bar_rows(counter: Counter, total: int, colors: dict[str, str], key_prefix: str = "") -> str:
    max_value = max(counter.values(), default=0)
    rows = []
    for key, value in counter.most_common():
        color = colors.get(key_prefix + key) or colors.get(key) or "#4f6f8f"
        rows.append(
            "<tr>"
            f"<td>{esc(label(str(key)))}</td>"
            f"<td class=\"count\">{value}</td>"
            f"<td class=\"pct\">{pct(value, total)}</td>"
            "<td class=\"bar-cell\">"
            f"<div class=\"bar\" style=\"width: {css_width(value, max_value)}; background: {esc(color)}\"></div>"
            "</td>"
            "</tr>"
        )
    return "\n".join(rows)


def build_html(samples: list[dict], taxonomy: list[dict[str, str]], output: Path, title: str) -> str:
    knowledge_to_taxonomy = {row["knowledge_point"]: row for row in taxonomy}
    total = len(samples)
    annotated_rows = []
    unmapped = []
    for sample in samples:
        kp = sample.get("knowledge_point", "")
        tax = knowledge_to_taxonomy.get(kp)
        if tax is None:
            domain = sample.get("category", "unmapped")
            subdomain = "unmapped"
            unmapped.append(kp)
        else:
            domain = tax["domain"]
            subdomain = tax["subdomain"]
        domain, subdomain = normalize_domain_subdomain(domain, subdomain)
        annotated_rows.append((sample, domain, subdomain))

    domain_counts = Counter(domain for _, domain, _ in annotated_rows)
    subdomain_counts = Counter((domain, subdomain) for _, domain, subdomain in annotated_rows)
    knowledge_counts = Counter(sample.get("knowledge_point", "") for sample, _, _ in annotated_rows)

    ontology_by_domain: dict[str, set[str]] = defaultdict(set)
    ontology_kp_by_domain: dict[str, set[str]] = defaultdict(set)
    sample_subdomains_by_domain: dict[str, set[str]] = defaultdict(set)
    sample_kp_by_domain: dict[str, set[str]] = defaultdict(set)
    for row in taxonomy:
        ontology_by_domain[row["domain"]].add(row["subdomain"])
        ontology_kp_by_domain[row["domain"]].add(row["knowledge_point"])
    for sample, domain, subdomain in annotated_rows:
        sample_subdomains_by_domain[domain].add(subdomain)
        sample_kp_by_domain[domain].add(sample.get("knowledge_point", ""))

    domain_colors = {
        "physics_physical_systems": "#2f6f9f",
        "chemistry_materials_change": "#8a5a2b",
        "biology_living_systems": "#3d7a49",
        "earth_environmental_systems": "#6a7545",
        "engineering_operational_systems": "#b05247",
    }
    subdomain_colors = {
        f"{domain}|{subdomain}": domain_colors.get(domain, "#4f6f8f")
        for domain, subdomain in subdomain_counts
    }

    subdomain_counter_for_render = Counter(
        {f"{domain}|{subdomain}": value for (domain, subdomain), value in subdomain_counts.items()}
    )
    subdomain_labels = {
        f"{domain}|{subdomain}": f"{label(domain)} / {label(subdomain)}"
        for domain, subdomain in subdomain_counts
    }

    def render_subdomain_rows() -> str:
        max_value = max(subdomain_counter_for_render.values(), default=0)
        rows = []
        for key, value in subdomain_counter_for_render.most_common():
            domain = key.split("|", 1)[0]
            rows.append(
                "<tr>"
                f"<td>{esc(subdomain_labels[key])}</td>"
                f"<td class=\"count\">{value}</td>"
                f"<td class=\"pct\">{pct(value, total)}</td>"
                "<td class=\"bar-cell\">"
                f"<div class=\"bar\" style=\"width: {css_width(value, max_value)}; background: {domain_colors.get(domain, '#4f6f8f')}\"></div>"
                "</td>"
                "</tr>"
            )
        return "\n".join(rows)

    coverage_rows = []
    for domain in sorted(ontology_by_domain):
        sampled_subdomains = sample_subdomains_by_domain.get(domain, set())
        sampled_kp = sample_kp_by_domain.get(domain, set())
        target_subdomains = ontology_by_domain[domain]
        target_kp = ontology_kp_by_domain[domain]
        coverage_rows.append(
            "<tr>"
            f"<td>{esc(label(domain))}</td>"
            f"<td>{len(sampled_subdomains)}/{len(target_subdomains)} ({pct(len(sampled_subdomains), len(target_subdomains))})</td>"
            f"<td>{len(sampled_kp)}/{len(target_kp)} ({pct(len(sampled_kp), len(target_kp))})</td>"
            f"<td>{domain_counts.get(domain, 0)}</td>"
            "</tr>"
        )

    knowledge_rows = []
    for kp, value in knowledge_counts.most_common():
        tax = knowledge_to_taxonomy.get(kp, {})
        knowledge_rows.append(
            "<tr>"
            f"<td>{esc(kp)}</td>"
            f"<td>{esc(label(tax.get('domain', 'unmapped')))}</td>"
            f"<td>{esc(label(tax.get('subdomain', 'unmapped')))}</td>"
            f"<td class=\"count\">{value}</td>"
            f"<td class=\"pct\">{pct(value, total)}</td>"
            "</tr>"
        )

    unmapped_html = ""
    if unmapped:
        items = "".join(f"<li>{esc(item)}</li>" for item in sorted(set(unmapped)))
        unmapped_html = f"<section class=\"panel warn\"><h2>Unmapped Knowledge Points</h2><ul>{items}</ul></section>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    :root {{
      --bg: #f6f6f2;
      --panel: #ffffff;
      --ink: #202124;
      --muted: #646761;
      --line: #d9d7ce;
      --soft: #eef2f3;
      --warn: #fff1cf;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      background: #fff;
    }}
    .wrap {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 20px;
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: 24px;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    .summary {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0;
    }}
    .metric, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .metric strong {{
      display: block;
      font-size: 24px;
      margin-bottom: 2px;
    }}
    .metric span {{
      color: var(--muted);
      font-size: 13px;
    }}
    .panel {{
      margin: 16px 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 8px 6px;
      text-align: left;
      vertical-align: middle;
    }}
    th {{
      color: var(--muted);
      font-weight: 700;
      background: var(--soft);
    }}
    .count, .pct {{
      width: 80px;
      white-space: nowrap;
      text-align: right;
    }}
    .bar-cell {{
      width: 38%;
    }}
    .bar {{
      height: 18px;
      border-radius: 4px;
    }}
    .warn {{
      background: var(--warn);
    }}
    @media (max-width: 760px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .bar-cell {{ width: 26%; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>{esc(title)}</h1>
      <p class="summary">Domain and subdomain distribution for benchmark balance and coverage auditing.</p>
    </div>
  </header>
  <main class="wrap">
    <section class="grid">
      <div class="metric"><strong>{total}</strong><span>samples</span></div>
      <div class="metric"><strong>{len(domain_counts)}</strong><span>sampled domains</span></div>
      <div class="metric"><strong>{len(subdomain_counts)}</strong><span>sampled subdomains</span></div>
    </section>

    <section class="panel">
      <h2>Domain Distribution</h2>
      <table>
        <thead><tr><th>Domain</th><th class="count">Count</th><th class="pct">Share</th><th>Scale</th></tr></thead>
        <tbody>{bar_rows(domain_counts, total, domain_colors)}</tbody>
      </table>
    </section>

    <section class="panel">
      <h2>Subdomain Distribution</h2>
      <table>
        <thead><tr><th>Domain / Subdomain</th><th class="count">Count</th><th class="pct">Share</th><th>Scale</th></tr></thead>
        <tbody>{render_subdomain_rows()}</tbody>
      </table>
    </section>

    <section class="panel">
      <h2>Ontology Coverage</h2>
      <table>
        <thead><tr><th>Domain</th><th>Subdomain coverage</th><th>Knowledge-point coverage</th><th class="count">Samples</th></tr></thead>
        <tbody>{"".join(coverage_rows)}</tbody>
      </table>
    </section>

    <section class="panel">
      <h2>Knowledge Point Distribution</h2>
      <table>
        <thead><tr><th>Knowledge point</th><th>Domain</th><th>Subdomain</th><th class="count">Count</th><th class="pct">Share</th></tr></thead>
        <tbody>{"".join(knowledge_rows)}</tbody>
      </table>
    </section>

    {unmapped_html}
  </main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", required=True, type=Path)
    parser.add_argument("--taxonomy", default=Path("data/domain_taxonomy_v1.csv"), type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", default="DynaKnow-Video Domain Distribution")
    args = parser.parse_args()

    samples = read_jsonl(args.samples)
    taxonomy = read_taxonomy(args.taxonomy)
    html_text = build_html(samples, taxonomy, args.output, args.title)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_text, encoding="utf-8")
    print(f"wrote domain distribution report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
