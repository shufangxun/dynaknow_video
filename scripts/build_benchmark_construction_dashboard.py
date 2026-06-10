#!/usr/bin/env python3
"""Build a benchmark construction dashboard from cards and gate audits."""

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

from taxonomy_aliases import normalize_domain_subdomain

DECISION_ORDER = {"pass": 0, "review": 1, "fail": 2, "unknown": 3}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
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


def label(value: str) -> str:
    return value.replace("_", " ")


def pct(value: int, total: int) -> str:
    return "0.0%" if total == 0 else f"{100.0 * value / total:.1f}%"


def canonical_key(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower()).rstrip(".")


def rel(path: str | Path, output: Path, root: Path) -> str:
    source = Path(path)
    if not source.is_absolute():
        source = root / source
    return esc(os.path.relpath(source, start=output.parent))


def media_type(path: str | Path) -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    if guessed:
        return guessed
    suffix = Path(path).suffix.lower()
    if suffix in {".ogv", ".ogg"}:
        return "video/ogg"
    if suffix == ".webm":
        return "video/webm"
    if suffix == ".mp4":
        return "video/mp4"
    return "video/*"


def normalize_card_decision(value: str) -> str:
    if value in {"pass", "review", "fail"}:
        return value
    return {
        "mechanism_keep": "pass",
        "mechanism_review": "review",
        "mechanism_reject_or_rewrite": "fail",
        "accept": "pass",
        "revise": "review",
        "reject": "fail",
    }.get(value, "unknown")


def normalize_gate_decision(value: str) -> str:
    lower = value.lower()
    if lower.startswith(("pass", "accept", "keep")):
        return "pass"
    if lower.startswith(("reject", "fail")):
        return "fail"
    if lower.startswith(("review", "revise")):
        return "review"
    return "unknown"


def split_tags(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value or "").replace(";", ",").split(",") if item.strip()]


def card_reason(card: dict) -> str:
    notes = card.get("critic_notes")
    if isinstance(notes, list):
        notes = "; ".join(str(item) for item in notes if str(item))
    return str(card.get("audit_reason") or notes or "")


def verifier_risk_tags(card: dict) -> list[str]:
    flags = card.get("verifier_flags", {})
    if not isinstance(flags, dict):
        return []
    return [name for name, value in flags.items() if value is False]


def load_card_items(paths: list[Path]) -> list[dict]:
    items: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for path in paths:
        for card in read_jsonl(path):
            item_id = str(card.get("video_id", ""))
            key = (item_id, str(path))
            if not item_id or key in seen:
                continue
            seen.add(key)
            kp = str(card.get("canonical_knowledge_point") or card.get("knowledge_point") or "")
            decision_raw = str(card.get("filter_decision", ""))
            domain, subdomain = normalize_domain_subdomain(
                str(card.get("domain") or "unmapped"),
                str(card.get("subdomain") or "unmapped"),
            )
            items.append(
                {
                    "item_id": item_id,
                    "stage": "knowledge_card",
                    "decision": normalize_card_decision(decision_raw),
                    "raw_decision": decision_raw,
                    "domain": domain,
                    "subdomain": subdomain,
                    "knowledge_point": kp,
                    "canonical_key": canonical_key(kp) if kp else "",
                    "visible_dynamic_process": str(card.get("visible_dynamic_process") or ""),
                    "reason": card_reason(card),
                    "risk_tags": verifier_risk_tags(card),
                    "local_media": str(card.get("local_media") or ""),
                    "frame_contact_sheet": "",
                    "source_url": str(card.get("source_url") or ""),
                    "replacement_video_id": "",
                }
            )
    return items


def load_gate_items(path: Path | None, stage: str) -> list[dict]:
    items: list[dict] = []
    for row in read_csv(path):
        item_id = row.get("candidate_id") or row.get("video_id") or row.get("id") or ""
        kp = row.get("proposed_knowledge_point") or row.get("knowledge_point") or ""
        if kp == "not_selected":
            kp = ""
        raw_decision = row.get("review_decision") or row.get("gate_decision") or row.get("decision") or ""
        domain, subdomain = normalize_domain_subdomain(
            row.get("domain") or row.get("inferred_domain") or "unmapped",
            row.get("subdomain") or row.get("inferred_subdomain") or "unmapped",
        )
        items.append(
            {
                "item_id": item_id,
                "stage": stage,
                "decision": normalize_gate_decision(raw_decision),
                "raw_decision": raw_decision,
                "domain": domain,
                "subdomain": subdomain,
                "knowledge_point": kp,
                "canonical_key": canonical_key(kp) if kp else "",
                "visible_dynamic_process": row.get("visible_dynamic_process") or "",
                "reason": row.get("gate_reason") or row.get("reason") or row.get("notes") or "",
                "risk_tags": split_tags(row.get("risk_tags") or row.get("review_flags") or ""),
                "local_media": row.get("local_media") or "",
                "frame_contact_sheet": row.get("frame_contact_sheet") or "",
                "source_url": row.get("source_url") or "",
                "replacement_video_id": row.get("replacement_video_id") or "",
            }
        )
    return items


def metric(title: str, value: int | str, detail: str = "") -> str:
    detail_html = f"<small>{esc(detail)}</small>" if detail else ""
    return f'<div class="metric"><strong>{esc(value)}</strong><span>{esc(title)}</span>{detail_html}</div>'


def count_table(counter: Counter[tuple[str, str]], total: int, title: str) -> str:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for (name, decision), value in counter.items():
        grouped[name][decision] = value
    rows = []
    for name in sorted(grouped):
        counts = grouped[name]
        row_total = sum(counts.values())
        rows.append(
            "<tr>"
            f"<td>{esc(label(name))}</td>"
            f'<td class="num">{row_total}</td>'
            f'<td class="num pass">{counts.get("pass", 0)}</td>'
            f'<td class="num review">{counts.get("review", 0)}</td>'
            f'<td class="num fail">{counts.get("fail", 0)}</td>'
            f'<td class="num">{pct(row_total, total)}</td>'
            "</tr>"
        )
    return (
        '<section class="panel">'
        f"<h2>{esc(title)}</h2>"
        "<table><thead><tr><th>Group</th><th class=\"num\">Total</th><th class=\"num\">Pass</th><th class=\"num\">Review</th><th class=\"num\">Fail</th><th class=\"num\">Share</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></section>"
    )


def target_table(items: list[dict], targets: list[dict[str, str]]) -> str:
    if not targets:
        return ""
    pass_counts = Counter(
        (item["domain"], item["subdomain"])
        for item in items
        if item["decision"] == "pass" and item["stage"] == "knowledge_card"
    )
    rows = []
    for target in targets:
        domain, subdomain = normalize_domain_subdomain(target.get("domain", ""), target.get("subdomain", ""))
        current = pass_counts.get((domain, subdomain), 0)
        min_count = int(target.get("min_v1_count", "0") or 0)
        target_count = int(target.get("target_v1_count", "0") or 0)
        rows.append(
            "<tr>"
            f"<td>{esc(label(domain))}</td>"
            f"<td>{esc(label(subdomain))}</td>"
            f'<td class="num pass">{current}</td>'
            f'<td class="num">{min_count}</td>'
            f'<td class="num">{max(0, min_count - current)}</td>'
            f'<td class="num">{target_count}</td>'
            f'<td class="num">{max(0, target_count - current)}</td>'
            "</tr>"
        )
    return (
        '<section class="panel">'
        "<h2>Clean Pass Target Gap</h2>"
        "<table><thead><tr><th>Domain</th><th>Subdomain</th><th class=\"num\">Pass</th><th class=\"num\">Min</th><th class=\"num\">Min Gap</th><th class=\"num\">Target</th><th class=\"num\">Target Gap</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></section>"
    )


def dedupe_table(items: list[dict]) -> str:
    groups: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        if item["knowledge_point"]:
            groups[item["canonical_key"]].append(item)
    rows = []
    for _, group in sorted(groups.items(), key=lambda item: (item[1][0]["domain"], item[1][0]["knowledge_point"])):
        counts = Counter(row["decision"] for row in group)
        ids = " ".join(f'<span class="mini {esc(row["decision"])}">{esc(row["item_id"])}</span>' for row in group)
        first = group[0]
        rows.append(
            "<tr>"
            f"<td>{esc(first['knowledge_point'])}</td>"
            f"<td>{esc(label(first['domain']))}</td>"
            f"<td>{esc(label(first['subdomain']))}</td>"
            f'<td class="num pass">{counts.get("pass", 0)}</td>'
            f'<td class="num review">{counts.get("review", 0)}</td>'
            f'<td class="num fail">{counts.get("fail", 0)}</td>'
            f"<td>{ids}</td>"
            "</tr>"
        )
    return (
        '<section class="panel">'
        "<h2>Knowledge Point Deduplication</h2>"
        "<table><thead><tr><th>Knowledge Point</th><th>Domain</th><th>Subdomain</th><th class=\"num\">Pass</th><th class=\"num\">Review</th><th class=\"num\">Fail</th><th>Items</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></section>"
    )


def reason_table(items: list[dict]) -> str:
    reasons = Counter((item["reason"] or "no_reason_recorded", item["decision"]) for item in items)
    tags = Counter((tag, item["decision"]) for item in items for tag in item["risk_tags"])

    def render(counter: Counter[tuple[str, str]], title: str) -> str:
        grouped: dict[str, Counter[str]] = defaultdict(Counter)
        for (name, decision), value in counter.items():
            grouped[name][decision] = value
        rows = []
        for name, counts in sorted(grouped.items(), key=lambda item: -sum(item[1].values())):
            rows.append(
                "<tr>"
                f"<td>{esc(name)}</td>"
                f'<td class="num">{sum(counts.values())}</td>'
                f'<td class="num pass">{counts.get("pass", 0)}</td>'
                f'<td class="num review">{counts.get("review", 0)}</td>'
                f'<td class="num fail">{counts.get("fail", 0)}</td>'
                "</tr>"
            )
        return (
            '<section class="panel">'
            f"<h2>{esc(title)}</h2>"
            "<table><thead><tr><th>Name</th><th class=\"num\">Total</th><th class=\"num\">Pass</th><th class=\"num\">Review</th><th class=\"num\">Fail</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table></section>"
        )

    return f'<div class="grid">{render(reasons, "Filter And Gate Reasons")}{render(tags, "Risk Tags")}</div>'


def media_html(item: dict, output: Path, root: Path) -> str:
    parts = []
    local_media = item.get("local_media", "")
    if local_media:
        media_path = root / local_media if not Path(local_media).is_absolute() else Path(local_media)
        if media_path.exists():
            src = rel(media_path, output, root)
            if media_path.suffix.lower() == ".gif":
                parts.append(f'<img class="animated" src="{src}" alt="animated media">')
            else:
                parts.append(
                    f'<video controls preload="metadata"><source src="{src}" type="{esc(media_type(media_path))}"><a href="{src}">Open video</a></video>'
                )
    sheet = item.get("frame_contact_sheet", "")
    if sheet:
        sheet_path = root / sheet if not Path(sheet).is_absolute() else Path(sheet)
        if sheet_path.exists():
            parts.append(f'<img class="sheet" src="{rel(sheet_path, output, root)}" alt="frame contact sheet">')
    if not parts:
        parts.append('<div class="missing">No local visual evidence.</div>')
    return "".join(parts)


def item_card(item: dict, output: Path, root: Path) -> str:
    tags = "".join(f"<span>{esc(tag)}</span>" for tag in item["risk_tags"])
    replacement = (
        f'<p><strong>Replacement:</strong> {esc(item["replacement_video_id"])}</p>' if item.get("replacement_video_id") else ""
    )
    source = f'<a href="{esc(item["source_url"])}">source</a>' if item.get("source_url") else ""
    kp = item["knowledge_point"] or "No knowledge point selected at gate."
    return f"""
    <article class="item status-{esc(item['decision'])}">
      <div class="media">{media_html(item, output, root)}</div>
      <div class="body">
        <div class="head">
          <div>
            <h3>{esc(item['item_id'])}</h3>
            <p>{esc(item['stage'])} / {esc(label(item['domain']))} / {esc(label(item['subdomain']))}</p>
          </div>
          <span class="badge {esc(item['decision'])}">{esc(item['decision'])}</span>
        </div>
        <p class="kp">{esc(kp)}</p>
        <p><strong>Raw decision:</strong> {esc(item['raw_decision'])}</p>
        <p>{esc(item['visible_dynamic_process'])}</p>
        <p class="reason">{esc(item['reason'])}</p>
        {replacement}
        <div class="chips">{tags}</div>
        <p>{source}</p>
      </div>
    </article>
    """


def build_html(items: list[dict], targets: list[dict[str, str]], output: Path, root: Path, title: str) -> str:
    total = len(items)
    decisions = Counter(item["decision"] for item in items)
    stage_counter = Counter((item["stage"], item["decision"]) for item in items)
    domain_counter = Counter((item["domain"], item["decision"]) for item in items)
    subdomain_counter = Counter((f"{item['domain']} / {item['subdomain']}", item["decision"]) for item in items)
    pass_kps = {item["canonical_key"] for item in items if item["decision"] == "pass" and item["canonical_key"]}
    all_kps = {item["canonical_key"] for item in items if item["canonical_key"]}
    sorted_items = sorted(
        items,
        key=lambda item: (DECISION_ORDER.get(item["decision"], 9), item["stage"], item["domain"], item["subdomain"], item["item_id"]),
    )
    metric_html = "".join(
        [
            metric("construction items", total),
            metric("pass", decisions.get("pass", 0), pct(decisions.get("pass", 0), total)),
            metric("review", decisions.get("review", 0), pct(decisions.get("review", 0), total)),
            metric("fail", decisions.get("fail", 0), pct(decisions.get("fail", 0), total)),
            metric("unique pass KPs", len(pass_kps)),
            metric("unique all KPs", len(all_kps)),
        ]
    )
    cards = "".join(item_card(item, output, root) for item in sorted_items)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>
:root {{
  --bg: #f6f7f5;
  --panel: #fff;
  --ink: #202124;
  --muted: #5f656b;
  --line: #d8dfe3;
  --pass: #1f7a4f;
  --review: #9a6400;
  --fail: #a63838;
  --pass-bg: #e6f4ec;
  --review-bg: #fff1d8;
  --fail-bg: #f8e2e2;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Arial, Helvetica, sans-serif; line-height: 1.45; }}
header {{ background: #fff; border-bottom: 1px solid var(--line); position: sticky; top: 0; z-index: 2; }}
.wrap {{ max-width: 1400px; margin: 0 auto; padding: 18px 22px; }}
h1 {{ margin: 0 0 5px; font-size: 24px; letter-spacing: 0; }}
h2 {{ margin: 0 0 12px; font-size: 18px; letter-spacing: 0; }}
h3 {{ margin: 0 0 4px; font-size: 17px; letter-spacing: 0; }}
.summary {{ margin: 0; color: var(--muted); font-size: 14px; }}
.metrics {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; margin: 18px 0; }}
.metric, .panel, .item {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; }}
.metric {{ padding: 13px; }}
.metric strong {{ display: block; font-size: 25px; }}
.metric span, .metric small {{ display: block; color: var(--muted); font-size: 12px; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }}
.panel {{ padding: 14px; margin-bottom: 14px; overflow: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
th, td {{ border-bottom: 1px solid var(--line); padding: 8px 7px; vertical-align: top; text-align: left; }}
th {{ background: #eef2f3; color: var(--muted); }}
.num {{ text-align: right; white-space: nowrap; width: 72px; }}
.pass {{ color: var(--pass); }}
.review {{ color: var(--review); }}
.fail {{ color: var(--fail); }}
.mini, .badge {{ display: inline-block; border-radius: 999px; padding: 2px 7px; font-size: 12px; font-weight: 700; margin: 1px 2px 1px 0; white-space: nowrap; }}
.mini.pass, .badge.pass {{ background: var(--pass-bg); color: var(--pass); }}
.mini.review, .badge.review {{ background: var(--review-bg); color: var(--review); }}
.mini.fail, .badge.fail {{ background: var(--fail-bg); color: var(--fail); }}
.items h2 {{ margin: 10px 0 14px; }}
.item {{ display: grid; grid-template-columns: minmax(320px, 42%) minmax(0, 1fr); gap: 16px; padding: 14px; margin-bottom: 16px; border-left: 5px solid var(--line); }}
.status-pass {{ border-left-color: var(--pass); }}
.status-review {{ border-left-color: var(--review); }}
.status-fail {{ border-left-color: var(--fail); }}
video, .sheet, .animated {{ width: 100%; max-height: 420px; display: block; background: #111; border-radius: 6px; }}
.animated {{ object-fit: contain; }}
.sheet {{ margin-top: 8px; object-fit: contain; border: 1px solid var(--line); }}
.missing {{ min-height: 180px; display: grid; place-items: center; border: 1px dashed var(--line); border-radius: 6px; color: var(--muted); }}
.head {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; margin-bottom: 10px; }}
.head p {{ margin: 0; color: var(--muted); font-size: 13px; }}
p {{ margin: 8px 0; font-size: 13px; }}
.kp {{ font-size: 15px; font-weight: 700; }}
.reason {{ color: var(--muted); }}
.chips {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }}
.chips span {{ background: #eef2f3; color: var(--muted); border-radius: 999px; padding: 3px 8px; font-size: 12px; }}
a {{ color: #17695e; font-weight: 700; }}
@media (max-width: 960px) {{ .metrics, .grid, .item {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<header><div class="wrap"><h1>{esc(title)}</h1><p class="summary">Cards plus gate audits. Final benchmark release should use pass items only; review/fail rows document filtering and coverage gaps.</p></div></header>
<main class="wrap">
<section class="metrics">{metric_html}</section>
<section class="grid">{count_table(stage_counter, total, "Stage By Decision")}{count_table(domain_counter, total, "Domain By Decision")}</section>
{count_table(subdomain_counter, total, "Subdomain By Decision")}
{target_table(items, targets)}
{dedupe_table(items)}
{reason_table(items)}
<section class="items"><h2>Construction Items</h2>{cards}</section>
</main>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cards", nargs="*", type=Path, default=[])
    parser.add_argument("--retrieval-gate", type=Path)
    parser.add_argument("--local-gate", type=Path)
    parser.add_argument("--targets", type=Path, default=Path("data/domain_sampling_targets_v1.csv"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--title", default="DynaKnow-Video Benchmark Construction Dashboard")
    args = parser.parse_args()

    items = load_card_items(args.cards)
    items.extend(load_gate_items(args.retrieval_gate, "retrieval_gate"))
    items.extend(load_gate_items(args.local_gate, "local_orphan_gate"))
    targets = read_csv(args.targets)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(items, targets, args.output, args.root, args.title), encoding="utf-8")
    decisions = Counter(item["decision"] for item in items)
    print(f"wrote construction dashboard to {args.output}")
    print(f"items={len(items)} pass={decisions.get('pass', 0)} review={decisions.get('review', 0)} fail={decisions.get('fail', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
