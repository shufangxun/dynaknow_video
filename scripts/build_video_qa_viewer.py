#!/usr/bin/env python3
"""Build a static video+QA browser for a DynaKnow-Video release."""

from __future__ import annotations

import argparse
import csv
import html
import json
import mimetypes
import os
from collections import Counter, defaultdict
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_manifest(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None or not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["video_id"]: row for row in csv.DictReader(handle)}


def read_taxonomy(path: Path | None) -> list[dict[str, str]]:
    if path is None or not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def pct(value: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{100.0 * value / total:.1f}%"


def label(value: str) -> str:
    return value.replace("_", " ")


def css_width(value: int, max_value: int) -> str:
    if max_value <= 0:
        return "0%"
    return f"{max(3.0, 100.0 * value / max_value):.1f}%"


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


def render_choice(key: str, text: str, answer: str) -> str:
    status = " correct" if key == answer else ""
    return (
        f'<li class="choice{status}">'
        f'<span class="choice-key">{esc(key)}</span>'
        f'<span>{esc(text)}</span>'
        "</li>"
    )


def render_evidence(spans: list[dict]) -> str:
    items = []
    for span in spans:
        start = span.get("start_sec", "")
        end = span.get("end_sec", "")
        desc = span.get("description", "")
        items.append(
            "<li>"
            f'<span class="time">{esc(start)}s-{esc(end)}s</span>'
            f"{esc(desc)}"
            "</li>"
        )
    return "\n".join(items)


def render_sample(
    sample: dict,
    manifest: dict[str, dict[str, str]],
    taxonomy_by_knowledge: dict[str, dict[str, str]],
    output: Path,
    root: Path,
) -> str:
    video_id = sample["video_id"]
    manifest_row = manifest.get(video_id, {})
    tax_row = taxonomy_by_knowledge.get(sample.get("knowledge_point", ""), {})
    domain = tax_row.get("domain", sample.get("category", ""))
    subdomain = tax_row.get("subdomain", "unmapped" if taxonomy_by_knowledge else "")
    local_media = sample.get("local_media") or manifest_row.get("local_media", "")
    source_url = manifest_row.get("source_url", "")
    source_grounding_note = manifest_row.get("source_grounding_note", "")
    review_status = sample.get("review_status") or manifest_row.get("review_status", "")
    filter_decision = sample.get("filter_decision") or manifest_row.get("filter_decision", "")
    filter_reason = sample.get("filter_reason") or manifest_row.get("filter_reason", "") or manifest_row.get("reason", "")
    risk_value = sample.get("risk_tags") or manifest_row.get("risk_tags", "")
    if isinstance(risk_value, list):
        risk_tags = [str(tag) for tag in risk_value if str(tag)]
    else:
        risk_tags = [tag for tag in str(risk_value).replace(";", ",").split(",") if tag]
    poster = root / "media" / "frames" / video_id / "middle.jpg"
    sparse = root / "media" / "contact_sheets" / "sparse" / f"{video_id}_sparse.jpg"
    poster_attr = f' poster="{rel_url(poster, output, root)}"' if poster.exists() else ""
    sparse_img = ""
    if sparse.exists():
        sparse_img = (
            '<details class="frames">'
            "<summary>Sparse frames</summary>"
            f'<img src="{rel_url(sparse, output, root)}" alt="{esc(video_id)} sparse frame sheet">'
            "</details>"
        )

    media_link = ""
    if local_media:
        media_src = rel_url(local_media, output, root)
        video_html = (
            f"<video controls preload=\"metadata\"{poster_attr}>"
            f'<source src="{media_src}" type="{esc(media_type(local_media))}">'
            f'<a href="{media_src}">Open video file</a>'
            "</video>"
        )
        media_link = f'<a href="{media_src}">local video file</a>'
    else:
        video_html = '<div class="missing">No local media path found.</div>'

    choices = sample.get("choices", {})
    answer = sample.get("answer", "")
    choice_items = "\n".join(render_choice(key, choices.get(key, ""), answer) for key in ["A", "B", "C", "D"])
    shortcut = sample.get("shortcut_labels", {})
    review_chips = []
    if review_status:
        review_chips.append(f"<span>review: {esc(review_status)}</span>")
    if filter_decision:
        review_chips.append(f"<span>filter: {esc(filter_decision)}</span>")
    for tag in risk_tags:
        review_chips.append(f"<span>risk: {esc(tag.strip())}</span>")
    review_html = f'<div class="chips review-chips">{"".join(review_chips)}</div>' if review_chips else ""
    filter_html = ""
    if filter_decision or filter_reason:
        decision_text = f"<strong>{esc(filter_decision)}</strong>" if filter_decision else ""
        reason_text = esc(filter_reason)
        separator = " - " if decision_text and reason_text else ""
        filter_html = (
            '<section class="detail filter-note">'
            "<h3>Mechanism Filter</h3>"
            f"<p>{decision_text}{separator}{reason_text}</p>"
            "</section>"
        )
    evidence = render_evidence(sample.get("dynamic_evidence", []))
    source_link = f'<a href="{esc(source_url)}">source page</a>' if source_url else ""
    link_items = " · ".join(item for item in [media_link, source_link] if item)
    links_html = f'<p class="media-links">{link_items}</p>' if link_items else ""

    return f"""
    <article class="sample" data-category="{esc(domain)}" data-subdomain="{esc(subdomain)}" data-answer="{esc(answer)}">
      <div class="media-panel">
        {video_html}
        {links_html}
        {sparse_img}
      </div>
      <div class="qa-panel">
        <div class="sample-head">
          <div>
            <h2>{esc(video_id)}</h2>
            <p class="meta">{esc(domain)}{f' / {esc(subdomain)}' if subdomain else ''} · {esc(sample.get("duration_sec", ""))}s</p>
          </div>
          <span class="answer">Answer {esc(answer)}</span>
        </div>
        <p class="knowledge">{esc(sample.get("knowledge_point", ""))}</p>
        {review_html}
        <p class="question">{esc(sample.get("question", ""))}</p>
        <ol class="choices">{choice_items}</ol>
        <section class="detail">
          <h3>Dynamic Evidence</h3>
          <ul>{evidence}</ul>
        </section>
        <section class="detail">
          <h3>Static Shortcut Check</h3>
          <p>{esc(sample.get("static_insufficient_reason", ""))}</p>
          <div class="chips">
            <span>answer-only: {esc(shortcut.get("answer_only_leakage", ""))}</span>
            <span>single-frame: {esc(shortcut.get("single_frame_sufficient", ""))}</span>
            <span>sparse-frames: {esc(shortcut.get("sparse_frames_sufficient", ""))}</span>
            <span>OCR: {esc(shortcut.get("ocr_leakage_status", ""))}</span>
          </div>
        </section>
        {filter_html}
        {f'<section class="detail source-grounding"><h3>Source Grounding</h3><p>{esc(source_grounding_note)}</p></section>' if source_grounding_note else ''}
      </div>
    </article>
    """


def render_distribution(samples: list[dict], taxonomy: list[dict[str, str]], targets: list[dict[str, str]]) -> str:
    if not taxonomy:
        return ""

    taxonomy_by_knowledge = {row["knowledge_point"]: row for row in taxonomy}
    total = len(samples)
    annotated = []
    for sample in samples:
        tax_row = taxonomy_by_knowledge.get(sample.get("knowledge_point", ""))
        domain = tax_row.get("domain", sample.get("category", "unmapped")) if tax_row else sample.get("category", "unmapped")
        subdomain = tax_row.get("subdomain", "unmapped") if tax_row else "unmapped"
        annotated.append((sample, domain, subdomain))

    domain_counts = Counter(domain for _, domain, _ in annotated)
    subdomain_counts = Counter((domain, subdomain) for _, domain, subdomain in annotated)
    ontology_subdomains: dict[str, set[str]] = defaultdict(set)
    ontology_knowledge: dict[str, set[str]] = defaultdict(set)
    sampled_subdomains: dict[str, set[str]] = defaultdict(set)
    sampled_knowledge: dict[str, set[str]] = defaultdict(set)
    for row in taxonomy:
        ontology_subdomains[row["domain"]].add(row["subdomain"])
        ontology_knowledge[row["domain"]].add(row["knowledge_point"])
    for row in targets:
        ontology_subdomains[row["domain"]].add(row["subdomain"])
    for sample, domain, subdomain in annotated:
        sampled_subdomains[domain].add(subdomain)
        sampled_knowledge[domain].add(sample.get("knowledge_point", ""))

    domain_colors = {
        "physics_physical_systems": "#2f6f9f",
        "chemistry_materials_change": "#8a5a2b",
        "biology_living_systems": "#3d7a49",
        "earth_environmental_systems": "#6a7545",
        "engineering_operational_systems": "#b05247",
    }

    max_domain = max(domain_counts.values(), default=0)
    domain_rows = []
    for domain, count in domain_counts.most_common():
        domain_rows.append(
            "<tr>"
            f"<td>{esc(label(domain))}</td>"
            f"<td class=\"num\">{count}</td>"
            f"<td class=\"num\">{pct(count, total)}</td>"
            "<td class=\"bar-cell\">"
            f"<div class=\"dist-bar\" style=\"width: {css_width(count, max_domain)}; background: {domain_colors.get(domain, '#4f6f8f')}\"></div>"
            "</td>"
            "</tr>"
        )

    max_subdomain = max(subdomain_counts.values(), default=0)
    subdomain_rows = []
    for (domain, subdomain), count in subdomain_counts.most_common():
        subdomain_rows.append(
            "<tr>"
            f"<td>{esc(label(domain))} / {esc(label(subdomain))}</td>"
            f"<td class=\"num\">{count}</td>"
            f"<td class=\"num\">{pct(count, total)}</td>"
            "<td class=\"bar-cell\">"
            f"<div class=\"dist-bar\" style=\"width: {css_width(count, max_subdomain)}; background: {domain_colors.get(domain, '#4f6f8f')}\"></div>"
            "</td>"
            "</tr>"
        )

    coverage_rows = []
    for domain in sorted(ontology_subdomains):
        sd_total = len(ontology_subdomains[domain])
        kp_total = len(ontology_knowledge[domain])
        sd_count = len(sampled_subdomains.get(domain, set()))
        kp_count = len(sampled_knowledge.get(domain, set()))
        kp_coverage = f"{kp_count}/{kp_total} ({pct(kp_count, kp_total)})" if kp_total else "not seeded"
        coverage_rows.append(
            "<tr>"
            f"<td>{esc(label(domain))}</td>"
            f"<td>{sd_count}/{sd_total} ({pct(sd_count, sd_total)})</td>"
            f"<td>{kp_coverage}</td>"
            f"<td class=\"num\">{domain_counts.get(domain, 0)}</td>"
            "</tr>"
        )

    target_rows = []
    target_summary = ""
    if targets:
        min_total = sum(int(row.get("min_v1_count", 0) or 0) for row in targets)
        target_total = sum(int(row.get("target_v1_count", 0) or 0) for row in targets)
        target_summary = f" · min v1 {min_total} · target v1 {target_total}"
        for row in targets:
            domain = row["domain"]
            subdomain = row["subdomain"]
            current = subdomain_counts.get((domain, subdomain), 0)
            min_count = int(row.get("min_v1_count", 0) or 0)
            target_count = int(row.get("target_v1_count", 0) or 0)
            min_gap = max(0, min_count - current)
            target_gap = max(0, target_count - current)
            target_rows.append(
                "<tr>"
                f"<td>{esc(label(domain))} / {esc(label(subdomain))}</td>"
                f"<td class=\"num\">{current}</td>"
                f"<td class=\"num\">{min_count}</td>"
                f"<td class=\"num\">{min_gap}</td>"
                f"<td class=\"num\">{target_count}</td>"
                f"<td class=\"num\">{target_gap}</td>"
                "</tr>"
            )

    target_html = ""
    if target_rows:
        target_html = f"""
      <section class="stat-panel">
        <h3>Sampling Targets</h3>
        <table>
          <thead><tr><th>Domain / Subdomain</th><th class="num">Current</th><th class="num">Min</th><th class="num">Min gap</th><th class="num">Target</th><th class="num">Target gap</th></tr></thead>
          <tbody>{"".join(target_rows)}</tbody>
        </table>
      </section>
        """

    return f"""
    <section id="distribution" class="distribution">
      <div class="section-head">
        <h2>Domain Distribution</h2>
        <p>{total} samples · {len(domain_counts)} sampled domains · {len(subdomain_counts)} sampled subdomains{target_summary}</p>
      </div>
      <div class="stats-grid">
        <section class="stat-panel">
          <h3>Domains</h3>
          <table>
            <thead><tr><th>Domain</th><th class="num">Count</th><th class="num">Share</th><th>Scale</th></tr></thead>
            <tbody>{"".join(domain_rows)}</tbody>
          </table>
        </section>
        <section class="stat-panel">
          <h3>Subdomains</h3>
          <table>
            <thead><tr><th>Domain / Subdomain</th><th class="num">Count</th><th class="num">Share</th><th>Scale</th></tr></thead>
            <tbody>{"".join(subdomain_rows)}</tbody>
          </table>
        </section>
      </div>
      <section class="stat-panel">
        <h3>Ontology Coverage</h3>
        <table>
          <thead><tr><th>Domain</th><th>Subdomain coverage</th><th>Knowledge-point coverage</th><th class="num">Samples</th></tr></thead>
          <tbody>{"".join(coverage_rows)}</tbody>
        </table>
      </section>
      {target_html}
    </section>
    """


def build_html(
    samples: list[dict],
    manifest: dict[str, dict[str, str]],
    taxonomy: list[dict[str, str]],
    targets: list[dict[str, str]],
    output: Path,
    root: Path,
    title: str,
) -> str:
    taxonomy_by_knowledge = {row["knowledge_point"]: row for row in taxonomy}
    categories = sorted(
        {
            taxonomy_by_knowledge.get(sample.get("knowledge_point", ""), {}).get("domain", sample.get("category", ""))
            for sample in samples
        }
    )
    subdomains = sorted(
        {
            taxonomy_by_knowledge.get(sample.get("knowledge_point", ""), {}).get("subdomain", "unmapped")
            for sample in samples
        }
    ) if taxonomy else []
    answer_counts = {key: 0 for key in ["A", "B", "C", "D"]}
    for sample in samples:
        answer = sample.get("answer")
        if answer in answer_counts:
            answer_counts[answer] += 1
    local_count = sum(1 for sample in samples if sample.get("local_media") or manifest.get(sample["video_id"], {}).get("local_media"))
    cards = "\n".join(render_sample(sample, manifest, taxonomy_by_knowledge, output, root) for sample in samples)
    distribution = render_distribution(samples, taxonomy, targets)
    category_options = "\n".join(f'<option value="{esc(category)}">{esc(category)}</option>' for category in categories)
    subdomain_options = "\n".join(f'<option value="{esc(subdomain)}">{esc(label(subdomain))}</option>' for subdomain in subdomains)
    answer_summary = " / ".join(f"{key}: {value}" for key, value in answer_counts.items())

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f7f4;
      --panel: #ffffff;
      --ink: #202124;
      --muted: #61635f;
      --line: #d9d9d2;
      --accent: #186a5d;
      --accent-soft: #e4f1ed;
      --warn-soft: #fff1d6;
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
      position: sticky;
      top: 0;
      z-index: 2;
      border-bottom: 1px solid var(--line);
      background: rgba(247, 247, 244, 0.96);
      backdrop-filter: blur(10px);
    }}
    .bar {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 16px 20px;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 16px;
      align-items: center;
    }}
    h1 {{
      margin: 0 0 4px;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: 0;
    }}
    .summary {{
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }}
    .controls {{
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}
    input, select {{
      height: 36px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      padding: 0 10px;
      font-size: 14px;
    }}
    main {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 20px;
    }}
    .nav-links {{
      display: flex;
      gap: 10px;
      margin-top: 8px;
      font-size: 13px;
    }}
    .nav-links a {{
      color: var(--accent);
      font-weight: 700;
    }}
    .distribution {{
      margin-bottom: 18px;
    }}
    .section-head {{
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .section-head h2 {{
      margin: 0;
      font-size: 20px;
    }}
    .section-head p {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
    }}
    .stats-grid {{
      display: grid;
      grid-template-columns: 0.9fr 1.1fr;
      gap: 14px;
      margin-bottom: 14px;
    }}
    .stat-panel {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 14px;
    }}
    .stat-panel h3 {{
      margin: 0 0 10px;
      font-size: 15px;
    }}
    .stat-panel table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    .stat-panel th, .stat-panel td {{
      border-bottom: 1px solid var(--line);
      padding: 7px 6px;
      text-align: left;
      vertical-align: middle;
    }}
    .stat-panel th {{
      color: var(--muted);
      background: #f1f1ec;
    }}
    .num {{
      width: 72px;
      text-align: right !important;
      white-space: nowrap;
    }}
    .bar-cell {{
      width: 32%;
    }}
    .dist-bar {{
      height: 16px;
      border-radius: 4px;
    }}
    .sample {{
      display: grid;
      grid-template-columns: minmax(320px, 44%) minmax(0, 1fr);
      gap: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 14px;
      margin-bottom: 18px;
    }}
    video {{
      width: 100%;
      max-height: 430px;
      background: #111;
      border-radius: 6px;
      display: block;
    }}
    .frames {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
    }}
    .media-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 10px 0 0;
      font-size: 14px;
    }}
    .media-links a {{
      color: var(--accent);
      font-weight: 700;
    }}
    .frames summary {{ cursor: pointer; }}
    .frames img {{
      width: 100%;
      margin-top: 8px;
      border: 1px solid var(--line);
      border-radius: 6px;
      display: block;
    }}
    .sample-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
      margin-bottom: 10px;
    }}
    h2 {{
      margin: 0 0 4px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    .meta {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
    }}
    .meta a {{
      color: var(--accent);
      margin-left: 6px;
    }}
    .answer {{
      flex: 0 0 auto;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-weight: 700;
      padding: 5px 10px;
      font-size: 13px;
    }}
    .knowledge {{
      margin: 0 0 10px;
      font-weight: 700;
    }}
    .question {{
      margin: 0 0 10px;
    }}
    .choices {{
      list-style: none;
      padding: 0;
      margin: 0 0 12px;
      display: grid;
      gap: 8px;
    }}
    .choice {{
      display: grid;
      grid-template-columns: 28px minmax(0, 1fr);
      gap: 8px;
      padding: 8px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
    }}
    .choice.correct {{
      border-color: #7db7a7;
      background: var(--accent-soft);
    }}
    .choice-key {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 26px;
      height: 26px;
      border-radius: 50%;
      background: #eeeeea;
      font-weight: 700;
      font-size: 13px;
    }}
    .detail {{
      border-top: 1px solid var(--line);
      padding-top: 10px;
      margin-top: 10px;
    }}
    .detail h3 {{
      margin: 0 0 6px;
      font-size: 13px;
      text-transform: uppercase;
      color: var(--muted);
      letter-spacing: 0;
    }}
    .detail p, .detail ul {{
      margin: 0;
      color: #383936;
      font-size: 14px;
    }}
    .detail ul {{
      padding-left: 18px;
    }}
    .time {{
      display: inline-block;
      margin-right: 8px;
      color: var(--accent);
      font-weight: 700;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }}
    .chips span {{
      background: var(--warn-soft);
      border: 1px solid #ead5a6;
      border-radius: 999px;
      padding: 4px 8px;
      color: #5f4b1f;
      font-size: 12px;
    }}
    .missing {{
      border: 1px dashed var(--line);
      border-radius: 6px;
      padding: 24px;
      color: var(--muted);
      background: #fafafa;
    }}
    @media (max-width: 860px) {{
      .bar {{
        grid-template-columns: 1fr;
      }}
      .controls {{
        justify-content: start;
      }}
      .stats-grid {{
        grid-template-columns: 1fr;
      }}
      .section-head {{
        display: block;
      }}
      .sample {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="bar">
      <div>
        <h1>{esc(title)}</h1>
        <p class="summary">{len(samples)} samples · local media {local_count}/{len(samples)} · answers {esc(answer_summary)}</p>
        <nav class="nav-links"><a href="#distribution">Distribution</a><a href="#samples">Samples</a></nav>
      </div>
      <div class="controls">
        <input id="query" type="search" placeholder="Search ID or knowledge point" aria-label="Search">
        <select id="category" aria-label="Domain">
          <option value="">All domains</option>
          {category_options}
        </select>
        {f'<select id="subdomain" aria-label="Subdomain"><option value="">All subdomains</option>{subdomain_options}</select>' if taxonomy else ''}
      </div>
    </div>
  </header>
  <main>
    {distribution}
    <section id="samples">
    {cards}
    </section>
  </main>
  <script>
    const query = document.getElementById('query');
    const category = document.getElementById('category');
    const subdomain = document.getElementById('subdomain');
    const samples = Array.from(document.querySelectorAll('.sample'));
    function applyFilters() {{
      const q = query.value.trim().toLowerCase();
      const c = category.value;
      const s = subdomain ? subdomain.value : '';
      for (const sample of samples) {{
        const text = sample.textContent.toLowerCase();
        const visible = (!q || text.includes(q)) && (!c || sample.dataset.category === c) && (!s || sample.dataset.subdomain === s);
        sample.style.display = visible ? '' : 'none';
      }}
    }}
    query.addEventListener('input', applyFilters);
    category.addEventListener('change', applyFilters);
    if (subdomain) subdomain.addEventListener('change', applyFilters);
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--taxonomy", type=Path)
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title", default="DynaKnow-Video QA Viewer")
    args = parser.parse_args()

    root = args.root.resolve()
    input_path = args.input if args.input.is_absolute() else root / args.input
    manifest_path = None
    if args.manifest:
        manifest_path = args.manifest if args.manifest.is_absolute() else root / args.manifest
    output = args.output if args.output.is_absolute() else root / args.output

    samples = read_jsonl(input_path)
    manifest = read_manifest(manifest_path)
    taxonomy_path = args.taxonomy if args.taxonomy is None or args.taxonomy.is_absolute() else root / args.taxonomy
    taxonomy = read_taxonomy(taxonomy_path)
    targets_path = args.targets if args.targets is None or args.targets.is_absolute() else root / args.targets
    targets = read_taxonomy(targets_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_html(samples, manifest, taxonomy, targets, output, root, args.title), encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
