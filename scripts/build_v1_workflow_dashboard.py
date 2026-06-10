#!/usr/bin/env python3
"""Build a unified v1 workflow dashboard.

The page combines pass/review/fail audit status, taxonomy coverage, duplicate
knowledge-point groups, filter reasons, and per-video QA review cards.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import mimetypes
import os
import re
from collections import Counter, defaultdict
from pathlib import Path


DECISION_LABELS = {
    "mechanism_keep": "pass",
    "mechanism_review": "review",
    "mechanism_reject_or_rewrite": "fail",
    "accept": "pass",
    "revise": "review",
    "reject": "fail",
}
DECISION_ORDER = {"pass": 0, "review": 1, "fail": 2, "unknown": 3}
CHOICE_KEYS = ["A", "B", "C", "D"]


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def read_csv(path: Path | None) -> list[dict[str, str]]:
    if path is None or not path.exists():
        return []
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


def decision_label(value: str) -> str:
    return DECISION_LABELS.get(value, value or "unknown")


def split_tags(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value or "").replace(";", ",").split(",") if item.strip()]


def rel_url(path: str | Path, output: Path, root: Path) -> str:
    source = Path(path)
    if not source.is_absolute():
        source = root / source
    return esc(os.path.relpath(source, start=output.parent))


def media_type(path: str) -> str:
    guessed, _ = mimetypes.guess_type(path)
    if guessed:
        return guessed
    suffix = Path(path).suffix.lower()
    if suffix == ".ogv":
        return "video/ogg"
    if suffix == ".webm":
        return "video/webm"
    if suffix == ".mp4":
        return "video/mp4"
    return "video/*"


def taxonomy_maps(taxonomy_rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], set[tuple[str, str]]]:
    by_kp = {row["knowledge_point"]: row for row in taxonomy_rows if row.get("knowledge_point")}
    pairs = {(row["domain"], row["subdomain"]) for row in taxonomy_rows if row.get("domain") and row.get("subdomain")}
    return by_kp, pairs


def infer_domain_subdomain(row: dict, taxonomy_by_kp: dict[str, dict[str, str]]) -> tuple[str, str]:
    kp = row.get("knowledge_point", "")
    tax = taxonomy_by_kp.get(kp, {})
    domain = row.get("domain") or tax.get("domain") or row.get("category") or "unmapped"
    subdomain = row.get("subdomain") or tax.get("subdomain") or "unmapped"
    return str(domain), str(subdomain)


def audit_by_id(audit_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["video_id"]: row for row in audit_rows if row.get("video_id")}


def enrich_rows(samples: list[dict], audit_rows: list[dict[str, str]], taxonomy_by_kp: dict[str, dict[str, str]]) -> list[dict]:
    audit = audit_by_id(audit_rows)
    rows: list[dict] = []
    for sample in samples:
        video_id = sample["video_id"]
        audit_row = audit.get(video_id, {})
        kp = audit_row.get("knowledge_point") or sample.get("knowledge_point", "")
        tax = taxonomy_by_kp.get(kp, {})
        domain = tax.get("domain") or sample.get("domain") or sample.get("category") or "unmapped"
        subdomain = tax.get("subdomain") or sample.get("subdomain") or "unmapped"
        raw_decision = audit_row.get("filter_decision") or sample.get("filter_decision") or sample.get("review_status", "")
        decision = decision_label(raw_decision)
        risk_tags = split_tags(audit_row.get("risk_tags") or sample.get("risk_tags", []))
        rows.append(
            {
                "sample": sample,
                "audit": audit_row,
                "video_id": video_id,
                "knowledge_point": kp,
                "canonical_key": canonical_key(kp),
                "domain": domain,
                "subdomain": subdomain,
                "decision": decision,
                "filter_decision": raw_decision,
                "reason": audit_row.get("reason") or sample.get("filter_reason", ""),
                "risk_tags": risk_tags,
                "source_url": audit_row.get("source_url") or sample.get("source_url", ""),
                "local_media": audit_row.get("local_media") or sample.get("local_media", ""),
            }
        )
    return rows


def metric(label_text: str, value: int | str, detail: str = "") -> str:
    return (
        '<div class="metric">'
        f"<strong>{esc(value)}</strong>"
        f"<span>{esc(label_text)}</span>"
        f"{f'<small>{esc(detail)}</small>' if detail else ''}"
        "</div>"
    )


def count_table(counter: Counter[tuple[str, str]], total: int, title: str) -> str:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for (group, decision), value in counter.items():
        grouped[group][decision] = value
    rows = []
    for group in sorted(grouped):
        counts = grouped[group]
        current_total = sum(counts.values())
        rows.append(
            "<tr>"
            f"<td>{esc(label(group))}</td>"
            f'<td class="num">{current_total}</td>'
            f'<td class="num pass">{counts.get("pass", 0)}</td>'
            f'<td class="num review">{counts.get("review", 0)}</td>'
            f'<td class="num fail">{counts.get("fail", 0)}</td>'
            f'<td class="num">{pct(current_total, total)}</td>'
            "</tr>"
        )
    return (
        '<section class="panel">'
        f"<h2>{esc(title)}</h2>"
        "<table>"
        '<thead><tr><th>Category</th><th class="num">Total</th><th class="num">Pass</th><th class="num">Review</th><th class="num">Fail</th><th class="num">Share</th></tr></thead>'
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "</section>"
    )


def target_table(rows: list[dict], targets: list[dict[str, str]]) -> str:
    if not targets:
        return ""
    counts = Counter((row["domain"], row["subdomain"], row["decision"]) for row in rows)
    body = []
    for target in targets:
        domain = target["domain"]
        subdomain = target["subdomain"]
        pass_count = counts.get((domain, subdomain, "pass"), 0)
        review_count = counts.get((domain, subdomain, "review"), 0)
        fail_count = counts.get((domain, subdomain, "fail"), 0)
        min_count = int(target.get("min_v1_count", 0) or 0)
        target_count = int(target.get("target_v1_count", 0) or 0)
        body.append(
            "<tr>"
            f"<td>{esc(label(domain))} / {esc(label(subdomain))}</td>"
            f'<td class="num pass">{pass_count}</td>'
            f'<td class="num review">{review_count}</td>'
            f'<td class="num fail">{fail_count}</td>'
            f'<td class="num">{min_count}</td>'
            f'<td class="num">{max(0, min_count - pass_count)}</td>'
            f'<td class="num">{target_count}</td>'
            f'<td class="num">{max(0, target_count - pass_count)}</td>'
            "</tr>"
        )
    return (
        '<section class="panel">'
        "<h2>Subdomain Targets</h2>"
        "<table>"
        '<thead><tr><th>Domain / Subdomain</th><th class="num">Pass</th><th class="num">Review</th><th class="num">Fail</th><th class="num">Min</th><th class="num">Min Gap</th><th class="num">Target</th><th class="num">Target Gap</th></tr></thead>'
        f"<tbody>{''.join(body)}</tbody>"
        "</table>"
        "</section>"
    )


def dedupe_table(rows: list[dict]) -> str:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["canonical_key"]].append(row)
    body = []
    for _, group_rows in sorted(groups.items(), key=lambda item: (item[1][0]["domain"], item[1][0]["knowledge_point"])):
        counts = Counter(row["decision"] for row in group_rows)
        status = "mixed" if len(counts) > 1 else next(iter(counts), "unknown")
        videos = " ".join(
            f'<span class="mini {esc(row["decision"])}">{esc(row["video_id"])}</span>'
            for row in sorted(group_rows, key=lambda item: item["video_id"])
        )
        first = group_rows[0]
        body.append(
            f'<tr class="status-{esc(status)}">'
            f"<td>{esc(first['knowledge_point'])}</td>"
            f"<td>{esc(label(first['domain']))}</td>"
            f"<td>{esc(label(first['subdomain']))}</td>"
            f'<td class="num pass">{counts.get("pass", 0)}</td>'
            f'<td class="num review">{counts.get("review", 0)}</td>'
            f'<td class="num fail">{counts.get("fail", 0)}</td>'
            f"<td>{videos}</td>"
            "</tr>"
        )
    return (
        '<section class="panel">'
        "<h2>Deduplicated Knowledge Points</h2>"
        "<table>"
        '<thead><tr><th>Canonical knowledge point</th><th>Domain</th><th>Subdomain</th><th class="num">Pass</th><th class="num">Review</th><th class="num">Fail</th><th>Videos</th></tr></thead>'
        f"<tbody>{''.join(body)}</tbody>"
        "</table>"
        "</section>"
    )


def reason_table(rows: list[dict]) -> str:
    reason_counts: Counter[tuple[str, str]] = Counter()
    tag_counts: Counter[tuple[str, str]] = Counter()
    for row in rows:
        reason = row["reason"] or "no_reason_recorded"
        reason_counts[(reason, row["decision"])] += 1
        for tag in row["risk_tags"]:
            tag_counts[(tag, row["decision"])] += 1
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for (reason, decision), count in reason_counts.items():
        grouped[reason][decision] = count
    reason_rows = []
    for reason, counts in sorted(grouped.items(), key=lambda item: -sum(item[1].values())):
        reason_rows.append(
            "<tr>"
            f"<td>{esc(reason)}</td>"
            f'<td class="num">{sum(counts.values())}</td>'
            f'<td class="num pass">{counts.get("pass", 0)}</td>'
            f'<td class="num review">{counts.get("review", 0)}</td>'
            f'<td class="num fail">{counts.get("fail", 0)}</td>'
            "</tr>"
        )

    tag_grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for (tag, decision), count in tag_counts.items():
        tag_grouped[tag][decision] = count
    tag_rows = []
    for tag, counts in sorted(tag_grouped.items(), key=lambda item: -sum(item[1].values())):
        tag_rows.append(
            "<tr>"
            f"<td>{esc(tag)}</td>"
            f'<td class="num">{sum(counts.values())}</td>'
            f'<td class="num pass">{counts.get("pass", 0)}</td>'
            f'<td class="num review">{counts.get("review", 0)}</td>'
            f'<td class="num fail">{counts.get("fail", 0)}</td>'
            "</tr>"
        )
    return (
        '<div class="grid">'
        '<section class="panel"><h2>Filter Reasons</h2><table>'
        '<thead><tr><th>Reason</th><th class="num">Total</th><th class="num">Pass</th><th class="num">Review</th><th class="num">Fail</th></tr></thead>'
        f"<tbody>{''.join(reason_rows)}</tbody></table></section>"
        '<section class="panel"><h2>Risk Tags</h2><table>'
        '<thead><tr><th>Tag</th><th class="num">Total</th><th class="num">Pass</th><th class="num">Review</th><th class="num">Fail</th></tr></thead>'
        f"<tbody>{''.join(tag_rows)}</tbody></table></section>"
        "</div>"
    )


def render_evidence(spans: list[dict]) -> str:
    items = []
    for span in spans:
        items.append(
            "<li>"
            f'<span class="time">{esc(span.get("start_sec", ""))}s-{esc(span.get("end_sec", ""))}s</span>'
            f"{esc(span.get('description', ''))}"
            "</li>"
        )
    return "".join(items)


def render_choices(sample: dict) -> str:
    choices = sample.get("choices", {})
    answer = sample.get("answer", "")
    items = []
    for key in CHOICE_KEYS:
        class_name = "choice correct" if key == answer else "choice"
        items.append(
            f'<li class="{class_name}"><span class="choice-key">{esc(key)}</span><span>{esc(choices.get(key, ""))}</span></li>'
        )
    return "".join(items)


def sample_card(row: dict, output: Path, root: Path) -> str:
    sample = row["sample"]
    local_media = row["local_media"]
    video_id = row["video_id"]
    video_html = '<div class="missing">No local media path found.</div>'
    media_link = ""
    if local_media:
        media_src = rel_url(local_media, output, root)
        poster = root / "media" / "frames" / video_id / "middle.jpg"
        poster_attr = f' poster="{rel_url(poster, output, root)}"' if poster.exists() else ""
        video_html = (
            f"<video controls preload=\"metadata\"{poster_attr}>"
            f'<source src="{media_src}" type="{esc(media_type(local_media))}">'
            f'<a href="{media_src}">Open video file</a>'
            "</video>"
        )
        media_link = f'<a href="{media_src}">local video</a>'
    source_link = f'<a href="{esc(row["source_url"])}">source</a>' if row["source_url"] else ""
    links = " ".join(item for item in [media_link, source_link] if item)
    links_html = f'<p class="links">{links}</p>' if links else ""
    tags = "".join(f"<span>risk: {esc(tag)}</span>" for tag in row["risk_tags"])
    return f"""
    <article class="sample status-{esc(row['decision'])}" data-decision="{esc(row['decision'])}" data-domain="{esc(row['domain'])}" data-subdomain="{esc(row['subdomain'])}">
      <div class="media-panel">
        {video_html}
        {links_html}
      </div>
      <div class="qa-panel">
        <div class="sample-head">
          <div>
            <h3>{esc(video_id)}</h3>
            <p>{esc(label(row['domain']))} / {esc(label(row['subdomain']))}</p>
          </div>
          <span class="badge {esc(row['decision'])}">{esc(row['decision'])}</span>
        </div>
        <p class="knowledge">{esc(row['knowledge_point'])}</p>
        <div class="chips"><span>filter: {esc(row['filter_decision'])}</span>{tags}</div>
        <p class="reason">{esc(row['reason'])}</p>
        <p class="question">{esc(sample.get('question', ''))}</p>
        <ol class="choices">{render_choices(sample)}</ol>
        <section class="detail">
          <h4>Dynamic Evidence</h4>
          <ul>{render_evidence(sample.get('dynamic_evidence', []))}</ul>
        </section>
        <section class="detail">
          <h4>Static Shortcut Check</h4>
          <p>{esc(sample.get('static_insufficient_reason', ''))}</p>
        </section>
      </div>
    </article>
    """


def sample_cards(rows: list[dict], output: Path, root: Path) -> str:
    sorted_rows = sorted(rows, key=lambda row: (DECISION_ORDER.get(row["decision"], 99), row["domain"], row["subdomain"], row["video_id"]))
    cards = "".join(sample_card(row, output, root) for row in sorted_rows)
    return f'<section class="cards"><h2>Video QA Review</h2>{cards}</section>'


def build_html(rows: list[dict], targets: list[dict[str, str]], output: Path, root: Path, title: str) -> str:
    total = len(rows)
    decisions = Counter(row["decision"] for row in rows)
    domain_counter = Counter((row["domain"], row["decision"]) for row in rows)
    subdomain_counter = Counter((f"{row['domain']} / {row['subdomain']}", row["decision"]) for row in rows)
    kp_groups = defaultdict(list)
    for row in rows:
        kp_groups[row["canonical_key"]].append(row)
    duplicate_groups = sum(1 for group in kp_groups.values() if len(group) > 1)
    target_min_total = sum(int(row.get("min_v1_count", 0) or 0) for row in targets)
    target_clean_total = sum(int(row.get("target_v1_count", 0) or 0) for row in targets)
    metric_html = "".join(
        [
            metric("videos", total),
            metric("pass", decisions.get("pass", 0), pct(decisions.get("pass", 0), total)),
            metric("review", decisions.get("review", 0), pct(decisions.get("review", 0), total)),
            metric("fail", decisions.get("fail", 0), pct(decisions.get("fail", 0), total)),
            metric("unique KPs", len(kp_groups)),
            metric("duplicate KP groups", duplicate_groups),
            metric("v1 min clean", target_min_total),
            metric("v1 target clean", target_clean_total),
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
      --bg: #f7f7f4;
      --panel: #fff;
      --ink: #202124;
      --muted: #626660;
      --line: #d8d8d0;
      --pass: #276749;
      --review: #986200;
      --fail: #a23a3a;
      --soft-pass: #e5f3eb;
      --soft-review: #fff0d2;
      --soft-fail: #f8e2e2;
      --soft-mixed: #ece9fa;
      --accent: #17695e;
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
      position: sticky;
      top: 0;
      z-index: 2;
    }}
    .wrap {{
      max-width: 1360px;
      margin: 0 auto;
      padding: 18px 20px;
    }}
    h1 {{ margin: 0 0 5px; font-size: 24px; letter-spacing: 0; }}
    h2 {{ margin: 0 0 12px; font-size: 18px; letter-spacing: 0; }}
    h3 {{ margin: 0 0 3px; font-size: 17px; letter-spacing: 0; }}
    h4 {{ margin: 0 0 8px; font-size: 14px; letter-spacing: 0; }}
    .summary {{ margin: 0; color: var(--muted); font-size: 14px; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(8, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0;
    }}
    .metric, .panel, .sample {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .metric {{ padding: 13px; }}
    .metric strong {{ display: block; font-size: 24px; margin-bottom: 2px; }}
    .metric span, .metric small {{ display: block; color: var(--muted); font-size: 12px; }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-bottom: 14px;
    }}
    .panel {{ padding: 14px; margin-bottom: 14px; overflow: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 8px 7px; text-align: left; vertical-align: top; }}
    th {{ background: #f0f0eb; color: var(--muted); }}
    .num {{ width: 72px; white-space: nowrap; text-align: right; }}
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
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
      margin: 1px 2px 1px 0;
    }}
    .badge.pass, .mini.pass {{ background: var(--soft-pass); color: var(--pass); }}
    .badge.review, .mini.review {{ background: var(--soft-review); color: var(--review); }}
    .badge.fail, .mini.fail {{ background: var(--soft-fail); color: var(--fail); }}
    .cards h2 {{ margin: 8px 0 14px; }}
    .sample {{
      display: grid;
      grid-template-columns: minmax(320px, 42%) minmax(0, 1fr);
      gap: 16px;
      padding: 14px;
      margin-bottom: 16px;
    }}
    video {{ width: 100%; max-height: 420px; background: #111; border-radius: 6px; display: block; }}
    .missing {{ border: 1px dashed var(--line); border-radius: 6px; padding: 24px; color: var(--muted); }}
    .links {{ margin: 8px 0 0; font-size: 13px; }}
    a {{ color: var(--accent); font-weight: 700; }}
    .sample-head {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; margin-bottom: 10px; }}
    .sample-head p {{ margin: 0; color: var(--muted); font-size: 13px; }}
    .knowledge {{ margin: 0 0 10px; font-size: 15px; font-weight: 700; }}
    .question {{ margin: 12px 0 8px; }}
    .reason {{ margin: 8px 0; color: var(--muted); font-size: 13px; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }}
    .chips span {{ background: #f0f0eb; border-radius: 999px; padding: 3px 8px; font-size: 12px; color: var(--muted); }}
    .choices {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 7px; }}
    .choice {{ border: 1px solid var(--line); border-radius: 6px; padding: 8px; display: grid; grid-template-columns: 30px 1fr; gap: 8px; }}
    .choice.correct {{ border-color: var(--pass); background: var(--soft-pass); }}
    .choice-key {{ font-weight: 700; }}
    .detail {{ margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--line); }}
    .detail ul {{ margin: 0; padding-left: 18px; }}
    .detail p {{ margin: 0; }}
    .time {{ display: inline-block; color: var(--muted); font-size: 12px; margin-right: 6px; }}
    @media (max-width: 1000px) {{
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .grid, .sample {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>{esc(title)}</h1>
      <p class="summary">Unified v1 workflow view: audit decisions, domain coverage, deduped knowledge points, filter reasons, and video QA review.</p>
    </div>
  </header>
  <main class="wrap">
    <section class="metrics">{metric_html}</section>
    <section class="grid">
      {count_table(domain_counter, total, "Domain By Decision")}
      {count_table(subdomain_counter, total, "Subdomain By Decision")}
    </section>
    {target_table(rows, targets)}
    {dedupe_table(rows)}
    {reason_table(rows)}
    {sample_cards(rows, output, root)}
  </main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", required=True, type=Path)
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--taxonomy", type=Path, default=Path("data/domain_taxonomy_v1.csv"))
    parser.add_argument("--targets", type=Path, default=Path("data/domain_sampling_targets_v1.csv"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--title", default="DynaKnow-Video v1 Workflow Dashboard")
    args = parser.parse_args()

    samples = read_jsonl(args.samples)
    audit_rows = read_csv(args.audit)
    taxonomy_rows = read_csv(args.taxonomy)
    targets = read_csv(args.targets)
    taxonomy_by_kp, _ = taxonomy_maps(taxonomy_rows)
    rows = enrich_rows(samples, audit_rows, taxonomy_by_kp)
    html_text = build_html(rows, targets, args.output, args.root, args.title)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_text, encoding="utf-8")
    print(f"wrote v1 workflow dashboard to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
