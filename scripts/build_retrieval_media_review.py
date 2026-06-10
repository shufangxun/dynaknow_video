#!/usr/bin/env python3
"""Build an HTML review page for retrieval candidates and downloaded media."""

from __future__ import annotations

import argparse
import csv
import html
import mimetypes
import os
from pathlib import Path

from taxonomy_aliases import normalize_domain_subdomain


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def rel(path: Path, output: Path) -> str:
    return esc(os.path.relpath(path, start=output.parent))


def media_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    if guessed:
        return guessed
    if path.suffix.lower() in {".ogv", ".ogg"}:
        return "video/ogg"
    if path.suffix.lower() == ".webm":
        return "video/webm"
    if path.suffix.lower() == ".mp4":
        return "video/mp4"
    return "video/*"


def find_local_media(media_dir: Path, item_id: str) -> Path | None:
    matches = sorted(media_dir.glob(f"{item_id}.*"))
    return matches[0] if matches else None


def gate_local_media(gate: dict[str, str], media_dir: Path, item_id: str) -> Path | None:
    path = gate.get("local_media", "")
    if path:
        media_path = Path(path)
        if media_path.exists():
            return media_path
    return find_local_media(media_dir, item_id)


def find_gate_frame(path: str, output: Path) -> str:
    if not path:
        return ""
    frame_path = Path(path)
    if not frame_path.exists():
        return ""
    return f'<img class="sheet" src="{rel(frame_path, output)}" alt="contact sheet">'


def render_video(path: Path | None, output: Path) -> str:
    if path is None:
        return '<div class="missing">No local media yet.</div>'
    src = rel(path, output)
    if path.suffix.lower() == ".gif":
        return f'<img class="animated" src="{src}" alt="animated media">'
    return (
        '<video controls preload="metadata">'
        f'<source src="{src}" type="{esc(media_type(path))}">'
        f'<a href="{src}">Open local media</a>'
        "</video>"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", required=True, type=Path)
    parser.add_argument("--media-check", required=True, type=Path)
    parser.add_argument("--dynamic-gate", type=Path)
    parser.add_argument("--media-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", default="DynaKnow-Video Retrieval Media Review")
    args = parser.parse_args()

    queue_rows = read_csv(args.queue)
    checks = {row["id"]: row for row in read_csv(args.media_check)}
    gate_rows = {row["candidate_id"]: row for row in read_csv(args.dynamic_gate)} if args.dynamic_gate else {}
    cards = []
    local_count = 0
    ok_count = 0
    for row in queue_rows:
        item_id = row["candidate_id"]
        check = checks.get(item_id, {})
        gate = gate_rows.get(item_id, {})
        local_media = gate_local_media(gate, args.media_dir, item_id)
        if local_media:
            local_count += 1
        if check.get("ok") == "true":
            ok_count += 1
        flags = row.get("review_flags", "")
        gate_decision = gate.get("review_decision", "not_reviewed")
        domain, subdomain = normalize_domain_subdomain(
            row.get("inferred_domain", "") or gate.get("domain", ""),
            row.get("inferred_subdomain", "") or gate.get("subdomain", ""),
        )
        proposed_html = (
            f'<p class="kp proposed">{esc(gate.get("proposed_knowledge_point", ""))}</p>'
            if gate.get("proposed_knowledge_point")
            else ""
        )
        visible_html = f'<p>{esc(gate.get("visible_dynamic_process", ""))}</p>' if gate.get("visible_dynamic_process") else ""
        reason_html = f'<p class="reason">{esc(gate.get("gate_reason", ""))}</p>' if gate.get("gate_reason") else ""
        gate_flags_html = f'<p class="flags">{esc(gate.get("risk_tags", ""))}</p>' if gate.get("risk_tags") else ""
        cards.append(
            f'<article class="card {esc(row.get("retrieval_decision", ""))} gate-{esc(gate_decision)}">'
            f'<div class="media">{render_video(local_media, args.output)}{find_gate_frame(gate.get("frame_contact_sheet", ""), args.output)}</div>'
            '<div class="body">'
            f'<h2>{esc(item_id)} <span>{esc(row.get("retrieval_decision", ""))}</span></h2>'
            f'<p class="gate"><strong>Dynamic gate:</strong> {esc(gate_decision)}</p>'
            f'<p><strong>{esc(domain)}</strong> / {esc(subdomain)}</p>'
            f'<p class="kp">{esc(row.get("candidate_knowledge_point", ""))}</p>'
            f"{proposed_html}"
            f'<p>{esc(row.get("why_dynamic", ""))}</p>'
            f"{visible_html}"
            f"{reason_html}"
            f'<p class="flags">{esc(flags)}</p>'
            f"{gate_flags_html}"
            f'<p>URL check: {esc(check.get("ok", "not_checked"))} {esc(check.get("http_status", ""))} {esc(check.get("error", ""))}</p>'
            f'<p><a href="{esc(row.get("source_url", ""))}">source page</a></p>'
            "</div></article>"
        )

    total = len(queue_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(args.title)}</title>
<style>
body{{margin:0;background:#f5f7fa;color:#1f2933;font-family:Arial,sans-serif}}
header{{background:#111827;color:white;padding:22px 28px}}
h1{{margin:0 0 8px;font-size:24px}}
.metrics{{display:flex;gap:10px;flex-wrap:wrap;padding:16px 28px}}
.metric{{background:white;border:1px solid #d8dee8;border-radius:8px;padding:12px 14px;min-width:130px}}
.metric strong{{display:block;font-size:24px}} .metric span{{color:#52606d}}
.cards{{display:grid;grid-template-columns:1fr;gap:12px;padding:0 28px 28px}}
.card{{display:grid;grid-template-columns:minmax(260px,440px) 1fr;gap:16px;background:white;border:1px solid #d8dee8;border-left:5px solid #9aa6b2;border-radius:8px;padding:12px}}
.priority_review{{border-left-color:#15803d}} .manual_review{{border-left-color:#b7791f}}
video,.animated{{width:100%;max-height:300px;background:#111;object-fit:contain}}
.sheet{{display:block;width:100%;margin-top:8px;border:1px solid #d8dee8}}
.missing{{height:180px;display:grid;place-items:center;background:#e5e7eb;color:#52606d}}
h2{{margin:0 0 8px;font-size:17px}} h2 span{{float:right;font-weight:400;color:#52606d}}
p{{font-size:13px;line-height:1.35;margin:7px 0}} .kp{{font-weight:700}} .proposed{{color:#166534}} .flags{{color:#9a3412}} .reason{{color:#334155}} .gate{{color:#111827}}
.gate-review_candidate{{border-left-color:#b7791f}} .gate-reject_current_mapping{{border-left-color:#b91c1c}}
a{{color:#0645ad}}
@media (max-width: 800px){{.card{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header><h1>{esc(args.title)}</h1><p>Retrieval candidates only. Use this page for dynamic-process review before constructing knowledge cards or QA.</p></header>
<section class="metrics">
<div class="metric"><strong>{total}</strong><span>queue rows</span></div>
<div class="metric"><strong>{ok_count}</strong><span>URL ok</span></div>
<div class="metric"><strong>{local_count}</strong><span>local media</span></div>
</section>
<section class="cards">{''.join(cards)}</section>
</body></html>""",
        encoding="utf-8",
    )
    print(f"wrote media review page to {args.output}")
    print(f"queue={total} url_ok={ok_count} local_media={local_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
