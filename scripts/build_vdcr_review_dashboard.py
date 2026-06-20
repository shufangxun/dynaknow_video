#!/usr/bin/env python3
"""Build a VDCR direct-answer production review dashboard."""

from __future__ import annotations

import argparse
import csv
import html
import json
import mimetypes
import os
from collections import Counter
from pathlib import Path


STATUS_CLASS = {
    "pass_candidate": "pass",
    "review": "review",
    "revise": "revise",
    "reject": "reject",
}


def read_csv(path: Path) -> list[dict[str, str]]:
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


def media_type(path: str) -> str:
    guessed, _ = mimetypes.guess_type(path)
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


def rel(path: str, output: Path, root: Path) -> str:
    source = Path(path)
    if not source.is_absolute():
        source = root / source
    return esc(os.path.relpath(source, start=output.parent))


def strip_trailing_whitespace(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()) + ("\n" if text.endswith("\n") else "")


def concept_maps(concepts: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    mapped: dict[str, dict[str, str]] = {}
    for row in concepts:
        for key in (
            row.get("concept_en", ""),
            row.get("recommended_answer_en", ""),
            row.get("concept_zh", ""),
            row.get("recommended_answer_zh", ""),
        ):
            if key:
                mapped[key] = row
    return mapped


def candidates_by_id(candidates: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["candidate_id"]: row for row in candidates}


def samples_by_media(samples: list[dict]) -> dict[str, dict]:
    return {sample.get("local_media", ""): sample for sample in samples}


def sample_for_review(review: dict[str, str], samples: list[dict]) -> dict | None:
    local_media = review.get("local_media", "")
    by_media = samples_by_media(samples)
    if local_media in by_media:
        return by_media[local_media]
    answer = review.get("candidate_knowledge_point", "")
    for sample in samples:
        if sample.get("answer") == answer and sample.get("local_media") == local_media:
            return sample
    return None


def source_candidate_id(review_id: str) -> str:
    marker = "_seg_"
    if marker in review_id:
        return review_id.split(marker, 1)[0]
    return review_id


def metric(label: str, value: object, detail: str = "") -> str:
    return (
        '<div class="metric">'
        f"<strong>{esc(value)}</strong>"
        f"<span>{esc(label)}</span>"
        f"{f'<small>{esc(detail)}</small>' if detail else ''}"
        "</div>"
    )


def count_table(title: str, counter: Counter[str]) -> str:
    rows = "".join(f"<tr><td>{esc(k)}</td><td>{v}</td></tr>" for k, v in counter.most_common())
    return f'<section class="panel"><h2>{esc(title)}</h2><table><tbody>{rows}</tbody></table></section>'


def card(
    review: dict[str, str],
    sample: dict | None,
    concept: dict[str, str],
    candidate: dict[str, str],
    output: Path,
    root: Path,
) -> str:
    status = review.get("review_status", "unknown")
    local_media = review.get("local_media", "")
    contact_sheet = review.get("contact_sheet", "")
    video = ""
    if local_media:
        video = (
            f'<video controls preload="metadata" src="{rel(local_media, output, root)}" '
            f'type="{esc(media_type(local_media))}"></video>'
        )
    sheet = ""
    if contact_sheet:
        sheet = f'<a href="{rel(contact_sheet, output, root)}" target="_blank"><img src="{rel(contact_sheet, output, root)}" alt="contact sheet"></a>'
    source_url = (sample or {}).get("source_url") or candidate.get("source_url") or ""
    sample_id = (sample or {}).get("video_id", "")
    domain = concept.get("domain") or candidate.get("domain_seed", "")
    subdomain = concept.get("subdomain") or candidate.get("subdomain_seed", "")
    concept_obj = (sample or {}).get("concept", {})
    quality_gates = (sample or {}).get("quality_gates", {})
    tier = (
        concept_obj.get("validity_tier")
        or quality_gates.get("concept_validity_tier")
        or concept.get("concept_validity_tier", "")
    )
    production_gate = quality_gates.get("production_gate") or concept.get("production_gate", "")
    return f"""
    <article class="card {esc(STATUS_CLASS.get(status, 'unknown'))}" data-status="{esc(status)}" data-domain="{esc(domain)}" data-answer="{esc(review.get('candidate_knowledge_point', ''))}">
      <div class="media">{video}{sheet}</div>
      <div class="body">
        <div class="topline">
          <span class="status">{esc(status)}</span>
          <span class="id">{esc(review.get('id', ''))}</span>
          {f'<span class="sample">{esc(sample_id)}</span>' if sample_id else ''}
        </div>
        <h2>{esc(review.get('candidate_knowledge_point', ''))} <span>{esc(concept.get('concept_zh', ''))}</span></h2>
        <dl>
          <dt>Domain</dt><dd>{esc(domain)} / {esc(subdomain)}</dd>
          <dt>Tier</dt><dd>{esc(tier)}</dd>
          <dt>Action</dt><dd>{esc(review.get('recommended_action', ''))}</dd>
          <dt>Window</dt><dd>{esc(review.get('suggested_start_sec', ''))}s - {esc(review.get('suggested_end_sec', ''))}s</dd>
          <dt>Source</dt><dd>{f'<a href="{esc(source_url)}" target="_blank" rel="noreferrer">{esc(source_url)}</a>' if source_url else ''}</dd>
          <dt>Gate</dt><dd>{esc(production_gate)}</dd>
          <dt>Notes</dt><dd>{esc(review.get('review_notes', ''))}</dd>
        </dl>
      </div>
    </article>
    """


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-csv", type=Path, default=Path("data/vdcr_pilot_manual_review_seed_v1.csv"))
    parser.add_argument("--samples", type=Path, default=Path("data/vdcr_pilot_samples_direct_answer_v1.jsonl"))
    parser.add_argument("--concepts", type=Path, default=Path("data/vdcr_concept_inventory_v1.csv"))
    parser.add_argument("--candidates", type=Path, default=Path("data/vdcr_candidate_videos_combined_v1.csv"))
    parser.add_argument("--output", type=Path, default=Path("reports/vdcr_review_dashboard_v1.html"))
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()

    reviews = read_csv(args.review_csv)
    samples = read_jsonl(args.samples)
    concepts = concept_maps(read_csv(args.concepts))
    candidates = candidates_by_id(read_csv(args.candidates))

    status_counts = Counter(row.get("review_status", "unknown") for row in reviews)
    sample_domain_counts = Counter(sample.get("domain", "") for sample in samples)
    sample_tier_counts = Counter(
        (sample.get("concept", {}) or {}).get("validity_tier")
        or (sample.get("quality_gates", {}) or {}).get("concept_validity_tier", "unknown")
        for sample in samples
    )
    source_platform_counts = Counter(candidates.get(source_candidate_id(row.get("id", "")), {}).get("source_platform", "unknown") for row in reviews)
    answer_counts = Counter(sample.get("answer", "") for sample in samples)
    duplicate_answers = [answer for answer, count in answer_counts.items() if count > 1]

    cards = []
    for review in reviews:
        concept = concepts.get(review.get("candidate_knowledge_point", ""), {})
        candidate = candidates.get(source_candidate_id(review.get("id", "")), {})
        cards.append(card(review, sample_for_review(review, samples), concept, candidate, args.output, args.root))

    html_out = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VDCR Review Dashboard v1</title>
  <style>
    :root {{ --bg:#f7f7f8; --panel:#fff; --text:#17202a; --muted:#667085; --line:#d7dce2; --pass:#0f766e; --review:#b45309; --revise:#4338ca; --reject:#b42318; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Arial, Helvetica, sans-serif; background:var(--bg); color:var(--text); }}
    header, main {{ width:min(1440px, calc(100% - 32px)); margin:0 auto; }}
    header {{ padding:24px 0 14px; }}
    h1 {{ margin:0 0 8px; font-size:28px; letter-spacing:0; }}
    .sub {{ color:var(--muted); }}
    .metrics {{ display:grid; grid-template-columns:repeat(5, minmax(140px,1fr)); gap:12px; margin:16px 0; }}
    .metric, .panel, .card {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; }}
    .metric {{ padding:12px; }}
    .metric strong {{ display:block; font-size:24px; }}
    .metric span, .metric small {{ display:block; color:var(--muted); font-size:13px; }}
    .filters {{ display:grid; grid-template-columns:repeat(3, minmax(180px,1fr)); gap:12px; margin:16px 0; }}
    input, select {{ width:100%; padding:9px 10px; border:1px solid var(--line); border-radius:6px; background:#fff; }}
    .tables {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:16px; }}
    .panel {{ padding:12px; }}
    .panel h2 {{ margin:0 0 8px; font-size:16px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    td {{ border-top:1px solid var(--line); padding:6px 4px; }}
    .card {{ display:grid; grid-template-columns:minmax(360px, 44%) 1fr; gap:16px; margin:14px 0; overflow:hidden; }}
    .media {{ background:#101820; min-height:260px; display:grid; grid-template-columns:1fr; gap:0; align-content:start; }}
    video {{ width:100%; max-height:360px; background:#000; display:block; }}
    img {{ width:100%; display:block; border-top:1px solid #26313b; }}
    .body {{ padding:14px 16px 16px 0; }}
    .topline {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:8px; }}
    .status, .id, .sample {{ font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:12px; padding:3px 6px; border-radius:5px; border:1px solid var(--line); }}
    .pass .status {{ color:var(--pass); border-color:var(--pass); }}
    .review .status {{ color:var(--review); border-color:var(--review); }}
    .revise .status {{ color:var(--revise); border-color:var(--revise); }}
    .reject .status {{ color:var(--reject); border-color:var(--reject); }}
    h2 {{ margin:0 0 10px; font-size:20px; letter-spacing:0; }}
    h2 span {{ color:var(--muted); font-size:15px; font-weight:400; }}
    dl {{ display:grid; grid-template-columns:96px 1fr; gap:7px 12px; margin:0; font-size:14px; }}
    dt {{ color:var(--muted); }}
    dd {{ margin:0; overflow-wrap:anywhere; }}
    a {{ color:#0f5f9a; }}
    .hidden {{ display:none; }}
    @media (max-width:900px) {{ .metrics,.tables,.filters,.card {{ grid-template-columns:1fr; }} .body {{ padding:14px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>VDCR Review Dashboard v1</h1>
    <div class="sub">Direct-answer benchmark production status. Pass candidates are visually reviewed but still require final license/source audit.</div>
    <div class="metrics">
      {metric("Samples", len(samples), "direct-answer JSONL")}
      {metric("Reviewed Rows", len(reviews), "manual review CSV")}
      {metric("Pass Candidates", status_counts.get("pass_candidate", 0))}
      {metric("Unique Answers", len(answer_counts), f"duplicates: {len(duplicate_answers)}")}
      {metric("Question Type", "Direct", "no MCQ options")}
    </div>
    <div class="filters">
      <select id="status"><option value="">All statuses</option>{''.join(f'<option value="{esc(k)}">{esc(k)} ({v})</option>' for k, v in sorted(status_counts.items()))}</select>
      <select id="domain"><option value="">All domains</option>{''.join(f'<option value="{esc(k)}">{esc(k)} ({v})</option>' for k, v in sorted(sample_domain_counts.items()))}</select>
      <input id="search" placeholder="Search answer, id, notes">
    </div>
  </header>
  <main>
    <div class="tables">
      {count_table("Review Status", status_counts)}
      {count_table("Pass Samples By Domain", sample_domain_counts)}
      {count_table("Pass Samples By Tier", sample_tier_counts)}
      {count_table("Reviewed Sources", source_platform_counts)}
    </div>
    <section id="cards">{''.join(cards)}</section>
  </main>
  <script>
    const statusFilter = document.getElementById('status');
    const domainFilter = document.getElementById('domain');
    const searchFilter = document.getElementById('search');
    const cards = Array.from(document.querySelectorAll('.card'));
    function applyFilters() {{
      const status = statusFilter.value;
      const domain = domainFilter.value;
      const q = searchFilter.value.toLowerCase();
      for (const card of cards) {{
        const okStatus = !status || card.dataset.status === status;
        const okDomain = !domain || card.dataset.domain === domain;
        const okSearch = !q || card.innerText.toLowerCase().includes(q);
        card.classList.toggle('hidden', !(okStatus && okDomain && okSearch));
      }}
    }}
    statusFilter.addEventListener('change', applyFilters);
    domainFilter.addEventListener('change', applyFilters);
    searchFilter.addEventListener('input', applyFilters);
  </script>
</body>
</html>
"""
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(strip_trailing_whitespace(html_out), encoding="utf-8")
    print(f"wrote dashboard {args.output} with {len(reviews)} review rows and {len(samples)} samples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
