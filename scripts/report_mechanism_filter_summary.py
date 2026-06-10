#!/usr/bin/env python3
"""Build a pass/review/fail mechanism-filter summary page."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


DECISION_LABELS = {
    "mechanism_keep": "pass",
    "mechanism_review": "review",
    "mechanism_reject_or_rewrite": "fail",
}

DECISION_ORDER = ["pass", "review", "fail"]


def read_jsonl(path: Path) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                row = json.loads(line)
                rows[row["video_id"]] = row
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def pct(value: int, total: int) -> str:
    return "0.0%" if total == 0 else f"{100.0 * value / total:.1f}%"


def label(value: str) -> str:
    return value.replace("_", " ")


def canonical_key(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower()).rstrip(".")


def decision_label(filter_decision: str) -> str:
    return DECISION_LABELS.get(filter_decision, filter_decision or "unknown")


def row_status_class(decision: str) -> str:
    return f"status-{decision_label(decision)}"


def metric_card(label_text: str, value: int | str, detail: str = "") -> str:
    return (
        '<div class="metric">'
        f"<strong>{esc(value)}</strong>"
        f"<span>{esc(label_text)}</span>"
        f"{f'<small>{esc(detail)}</small>' if detail else ''}"
        "</div>"
    )


def count_table(counter: Counter[tuple[str, str]], total: int, header: str) -> str:
    rows = []
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for (group, decision), value in counter.items():
        grouped[group][decision] = value
    for group in sorted(grouped):
        counts = grouped[group]
        current_total = sum(counts.values())
        rows.append(
            "<tr>"
            f"<td>{esc(label(group))}</td>"
            f"<td class=\"num\">{current_total}</td>"
            f"<td class=\"num pass\">{counts.get('pass', 0)}</td>"
            f"<td class=\"num review\">{counts.get('review', 0)}</td>"
            f"<td class=\"num fail\">{counts.get('fail', 0)}</td>"
            f"<td class=\"num\">{pct(current_total, total)}</td>"
            "</tr>"
        )
    return (
        '<section class="panel">'
        f"<h2>{esc(header)}</h2>"
        "<table>"
        "<thead><tr><th>Category</th><th class=\"num\">Total</th><th class=\"num\">Pass</th><th class=\"num\">Review</th><th class=\"num\">Fail</th><th class=\"num\">Share</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "</section>"
    )


def build_html(samples: dict[str, dict], audit_rows: list[dict[str, str]], taxonomy: list[dict[str, str]], title: str) -> str:
    tax_by_kp = {row["knowledge_point"]: row for row in taxonomy}
    rows = []
    for audit in audit_rows:
        video_id = audit["video_id"]
        sample = samples.get(video_id, {})
        kp = audit.get("knowledge_point") or sample.get("knowledge_point", "")
        tax = tax_by_kp.get(kp, {})
        domain = tax.get("domain") or sample.get("category", "unmapped")
        subdomain = tax.get("subdomain", "unmapped")
        decision = decision_label(audit.get("filter_decision", ""))
        rows.append(
            {
                "video_id": video_id,
                "decision": decision,
                "filter_decision": audit.get("filter_decision", ""),
                "reason": audit.get("reason", ""),
                "old_review_status": audit.get("old_review_status", ""),
                "risk_tags": audit.get("risk_tags", ""),
                "knowledge_point": kp,
                "canonical_key": canonical_key(kp),
                "domain": domain,
                "subdomain": subdomain,
                "source_url": audit.get("source_url", ""),
                "local_media": audit.get("local_media") or sample.get("local_media", ""),
            }
        )

    total = len(rows)
    by_decision = Counter(row["decision"] for row in rows)
    domain_counter = Counter((row["domain"], row["decision"]) for row in rows)
    subdomain_counter = Counter((f"{row['domain']} / {row['subdomain']}", row["decision"]) for row in rows)

    kp_groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        kp_groups[row["canonical_key"]].append(row)
    unique_kp_total = len(kp_groups)
    unique_by_decision: Counter[str] = Counter()
    for group_rows in kp_groups.values():
        decisions = {row["decision"] for row in group_rows}
        if len(decisions) == 1:
            unique_by_decision[next(iter(decisions))] += 1
        else:
            unique_by_decision["mixed"] += 1

    kp_table_rows = []
    for _, group_rows in sorted(kp_groups.items(), key=lambda item: (item[1][0]["domain"], item[1][0]["knowledge_point"])):
        representative = group_rows[0]
        counts = Counter(row["decision"] for row in group_rows)
        videos = " ".join(
            f'<span class="mini {esc(row["decision"])}">{esc(row["video_id"])}</span>'
            for row in sorted(group_rows, key=lambda row: row["video_id"])
        )
        status = "mixed" if len(counts) > 1 else next(iter(counts))
        kp_table_rows.append(
            f'<tr class="status-{esc(status)}">'
            f"<td>{esc(representative['knowledge_point'])}</td>"
            f"<td>{esc(label(representative['domain']))}</td>"
            f"<td>{esc(label(representative['subdomain']))}</td>"
            f"<td class=\"num pass\">{counts.get('pass', 0)}</td>"
            f"<td class=\"num review\">{counts.get('review', 0)}</td>"
            f"<td class=\"num fail\">{counts.get('fail', 0)}</td>"
            f"<td>{videos}</td>"
            "</tr>"
        )

    sample_rows = []
    for row in sorted(rows, key=lambda item: (DECISION_ORDER.index(item["decision"]) if item["decision"] in DECISION_ORDER else 99, item["domain"], item["video_id"])):
        source_link = f'<a href="{esc(row["source_url"])}">source</a>' if row["source_url"] else ""
        sample_rows.append(
            f'<tr class="{row_status_class(row["filter_decision"])}">'
            f"<td>{esc(row['video_id'])}</td>"
            f"<td><span class=\"badge {esc(row['decision'])}\">{esc(row['decision'])}</span></td>"
            f"<td>{esc(label(row['domain']))}</td>"
            f"<td>{esc(label(row['subdomain']))}</td>"
            f"<td>{esc(row['knowledge_point'])}</td>"
            f"<td>{esc(row['reason'])}</td>"
            f"<td>{esc(row['risk_tags'])}</td>"
            f"<td>{source_link}</td>"
            "</tr>"
        )

    metric_html = "".join(
        [
            metric_card("videos", total),
            metric_card("pass", by_decision.get("pass", 0), pct(by_decision.get("pass", 0), total)),
            metric_card("review", by_decision.get("review", 0), pct(by_decision.get("review", 0), total)),
            metric_card("fail", by_decision.get("fail", 0), pct(by_decision.get("fail", 0), total)),
            metric_card("unique knowledge points", unique_kp_total),
            metric_card("mixed duplicate KPs", unique_by_decision.get("mixed", 0)),
        ]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    :root {{
      --bg: #f6f6f2;
      --panel: #fff;
      --ink: #202124;
      --muted: #626660;
      --line: #d9d7ce;
      --pass: #276749;
      --review: #9a5b00;
      --fail: #a33838;
      --soft-pass: #e4f3ea;
      --soft-review: #fff0d2;
      --soft-fail: #f8e1e1;
      --soft-mixed: #e8e6f7;
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
      background: #fff;
      border-bottom: 1px solid var(--line);
    }}
    .wrap {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 18px 20px;
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: 24px;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 10px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    .summary {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
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
      font-size: 25px;
      margin-bottom: 2px;
    }}
    .metric span, .metric small {{
      display: block;
      color: var(--muted);
      font-size: 12px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-bottom: 14px;
    }}
    .panel {{
      margin-bottom: 14px;
      overflow: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 8px 7px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      background: #f0f0eb;
      font-weight: 700;
    }}
    .num {{
      width: 70px;
      text-align: right;
      white-space: nowrap;
    }}
    .pass {{ color: var(--pass); }}
    .review {{ color: var(--review); }}
    .fail {{ color: var(--fail); }}
    .status-pass {{ background: var(--soft-pass); }}
    .status-review {{ background: var(--soft-review); }}
    .status-fail {{ background: var(--soft-fail); }}
    .status-mixed {{ background: var(--soft-mixed); }}
    .badge, .mini {{
      display: inline-block;
      border-radius: 999px;
      padding: 2px 7px;
      font-weight: 700;
      font-size: 12px;
      white-space: nowrap;
      margin: 1px 2px 1px 0;
    }}
    .badge.pass, .mini.pass {{ background: var(--soft-pass); color: var(--pass); }}
    .badge.review, .mini.review {{ background: var(--soft-review); color: var(--review); }}
    .badge.fail, .mini.fail {{ background: var(--soft-fail); color: var(--fail); }}
    a {{ color: #186a5d; font-weight: 700; }}
    @media (max-width: 900px) {{
      .metrics, .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>{esc(title)}</h1>
      <p class="summary">One-page pass/review/fail summary with domain classification and deduplicated canonical knowledge points.</p>
    </div>
  </header>
  <main class="wrap">
    <section class="metrics">{metric_html}</section>
    <section class="grid">
      {count_table(domain_counter, total, "Domain By Decision")}
      {count_table(subdomain_counter, total, "Subdomain By Decision")}
    </section>
    <section class="panel">
      <h2>Deduplicated Knowledge Points</h2>
      <table>
        <thead><tr><th>Canonical knowledge point</th><th>Domain</th><th>Subdomain</th><th class="num">Pass</th><th class="num">Review</th><th class="num">Fail</th><th>Videos</th></tr></thead>
        <tbody>{''.join(kp_table_rows)}</tbody>
      </table>
    </section>
    <section class="panel">
      <h2>All Videos</h2>
      <table>
        <thead><tr><th>Video</th><th>Decision</th><th>Domain</th><th>Subdomain</th><th>Knowledge point</th><th>Reason</th><th>Risk tags</th><th>Source</th></tr></thead>
        <tbody>{''.join(sample_rows)}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--taxonomy", default=Path("data/domain_taxonomy_v1.csv"), type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", default="DynaKnow-Video Mechanism Filter Summary")
    args = parser.parse_args()

    samples = read_jsonl(args.samples)
    audit_rows = read_csv(args.audit)
    taxonomy = read_csv(args.taxonomy)
    html_text = build_html(samples, audit_rows, taxonomy, args.title)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_text, encoding="utf-8")
    print(f"wrote mechanism filter summary to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
