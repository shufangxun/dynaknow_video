#!/usr/bin/env python3
"""Build a lightweight VDCR candidate review HTML page."""

from __future__ import annotations

import argparse
import csv
import html
import re
from collections import Counter
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def archive_identifier(notes: str) -> str:
    match = re.search(r"archive_identifier=([^;]+)", notes or "")
    return match.group(1).strip() if match else ""


def short_notes(notes: str, max_len: int = 520) -> str:
    notes = re.sub(r"\s+", " ", notes or "").strip()
    if len(notes) <= max_len:
        return notes
    return notes[: max_len - 3].rstrip() + "..."


def pill(label: str, value: str) -> str:
    return f'<span class="pill"><b>{html.escape(label)}</b>{html.escape(value)}</span>'


def dedupe_candidates(candidate_groups: list[tuple[Path, list[dict[str, str]]]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    for path, rows in candidate_groups:
        for row in rows:
            key = row.get("source_url", "")
            if key and key in seen_urls:
                continue
            if key:
                seen_urls.add(key)
            row = dict(row)
            row["review_source_csv"] = str(path)
            output.append(row)
    return output


def build_html(candidates: list[dict[str, str]], concepts: dict[str, dict[str, str]]) -> str:
    rows = []
    domain_counts = Counter()
    priority_counts = Counter()
    concept_counts = Counter()

    for cand in candidates:
        concept = concepts.get(cand.get("candidate_knowledge_point", ""), {})
        domain = concept.get("domain_zh") or cand.get("domain_seed", "")
        subdomain = concept.get("subdomain_zh") or cand.get("subdomain_seed", "")
        priority = concept.get("priority", "")
        risk = concept.get("risk_reason", "")
        static_risk = concept.get("static_shortcut_risk", "")
        availability = concept.get("video_availability_guess", "")
        source_url = cand.get("source_url", "")
        answer = cand.get("candidate_knowledge_point", "")
        concept_zh = concept.get("concept_zh", "")
        identifier = archive_identifier(cand.get("collector_notes", ""))
        iframe = ""
        if identifier:
            iframe = (
                '<iframe loading="lazy" allowfullscreen '
                f'src="https://archive.org/embed/{html.escape(identifier)}"></iframe>'
            )
        else:
            iframe = '<div class="no-preview">No embedded preview</div>'

        domain_counts[domain] += 1
        priority_counts[priority or "unknown"] += 1
        concept_counts[answer] += 1

        gate_items = [
            f"temporal gate: {cand.get('why_dynamic', '')}",
            f"risk rule: {risk}",
            f"static shortcut risk: {static_risk}",
            f"video availability guess: {availability}",
        ]
        gate_text = " | ".join(item for item in gate_items if item and not item.endswith(": "))

        rows.append(
            f"""
            <article class="candidate" data-domain="{html.escape(domain)}" data-priority="{html.escape(priority or 'unknown')}" data-concept="{html.escape(answer)}">
              <div class="media">{iframe}</div>
              <div class="body">
                <div class="topline">
                  <span class="id">{html.escape(cand.get('candidate_id', ''))}</span>
                  {pill("priority", priority or "unknown")}
                  {pill("domain", domain)}
                  {pill("subdomain", subdomain)}
                </div>
                <h2>{html.escape(answer)} <span>{html.escape(concept_zh)}</span></h2>
                <p class="question">Which named dynamic concept is instantiated by the temporally evolving process in this video?</p>
                <dl>
                  <dt>Source page</dt><dd><a href="{html.escape(source_url)}" target="_blank" rel="noreferrer">{html.escape(source_url)}</a></dd>
                  <dt>Source status</dt><dd>newly retrieved from Internet Archive search; csv={html.escape(cand.get('review_source_csv', ''))}</dd>
                  <dt>Pruning status</dt><dd>not pruned; pending manual video review</dd>
                  <dt>Suggested clip</dt><dd>{html.escape(cand.get('suggested_start_sec', ''))}s - {html.escape(cand.get('suggested_end_sec', ''))}s; raw duration {html.escape(cand.get('raw_duration_sec', ''))}s</dd>
                  <dt>Gate reason</dt><dd>{html.escape(gate_text)}</dd>
                  <dt>Collector notes</dt><dd>{html.escape(short_notes(cand.get('collector_notes', '')))}</dd>
                </dl>
              </div>
            </article>
            """
        )

    domain_options = "\n".join(
        f'<option value="{html.escape(name)}">{html.escape(name)} ({count})</option>'
        for name, count in sorted(domain_counts.items())
    )
    priority_options = "\n".join(
        f'<option value="{html.escape(name)}">{html.escape(name)} ({count})</option>'
        for name, count in sorted(priority_counts.items())
    )
    concept_summary = "".join(
        f"<tr><td>{html.escape(name)}</td><td>{count}</td></tr>"
        for name, count in concept_counts.most_common()
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VDCR Candidate Review v1</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --text: #17202a;
      --muted: #657080;
      --line: #d8dde5;
      --panel: #ffffff;
      --accent: #0f766e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }}
    header, main {{
      width: min(1380px, calc(100% - 32px));
      margin: 0 auto;
    }}
    header {{
      padding: 28px 0 18px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      letter-spacing: 0;
    }}
    .meta {{
      color: var(--muted);
      font-size: 14px;
    }}
    .controls {{
      display: grid;
      grid-template-columns: repeat(3, minmax(180px, 1fr));
      gap: 12px;
      margin: 18px 0;
      padding: 14px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    label {{
      display: grid;
      gap: 6px;
      font-size: 13px;
      color: var(--muted);
    }}
    select, input {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 10px;
      font-size: 14px;
      background: #fff;
      color: var(--text);
    }}
    .summary {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 18px;
    }}
    .summary section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .summary h2 {{
      margin: 0 0 10px;
      font-size: 16px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    td {{
      border-top: 1px solid var(--line);
      padding: 6px 4px;
    }}
    .candidate {{
      display: grid;
      grid-template-columns: minmax(360px, 42%) 1fr;
      gap: 16px;
      margin: 16px 0;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    .media {{
      min-height: 300px;
      background: #101820;
    }}
    iframe {{
      width: 100%;
      height: 100%;
      min-height: 300px;
      border: 0;
      display: block;
    }}
    .no-preview {{
      color: #fff;
      height: 300px;
      display: grid;
      place-items: center;
    }}
    .body {{
      padding: 16px 16px 18px 0;
    }}
    .topline {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin-bottom: 10px;
    }}
    .id {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      color: var(--accent);
      font-weight: 700;
    }}
    .pill {{
      display: inline-flex;
      gap: 5px;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 12px;
      color: var(--muted);
      background: #f9fafb;
    }}
    .pill b {{
      color: var(--text);
      font-weight: 700;
    }}
    .body h2 {{
      margin: 0 0 8px;
      font-size: 21px;
      letter-spacing: 0;
    }}
    .body h2 span {{
      color: var(--muted);
      font-weight: 400;
      font-size: 16px;
    }}
    .question {{
      margin: 0 0 12px;
      color: var(--muted);
    }}
    dl {{
      display: grid;
      grid-template-columns: 130px 1fr;
      gap: 8px 12px;
      margin: 0;
      font-size: 14px;
    }}
    dt {{
      color: var(--muted);
    }}
    dd {{
      margin: 0;
      min-width: 0;
      overflow-wrap: anywhere;
    }}
    a {{
      color: var(--accent);
    }}
    .hidden {{
      display: none;
    }}
    @media (max-width: 900px) {{
      header, main {{
        width: min(100% - 20px, 760px);
      }}
      .controls, .summary, .candidate {{
        grid-template-columns: 1fr;
      }}
      .body {{
        padding: 0 14px 16px;
      }}
      dl {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>VDCR Candidate Review v1</h1>
    <div class="meta">Direct-answer candidate pool. Total candidates: <span id="visible-count">{len(candidates)}</span> / {len(candidates)}.</div>
    <div class="controls">
      <label>Domain
        <select id="domain-filter"><option value="">All domains</option>{domain_options}</select>
      </label>
      <label>Priority
        <select id="priority-filter"><option value="">All priorities</option>{priority_options}</select>
      </label>
      <label>Search
        <input id="text-filter" type="search" placeholder="candidate id, concept, notes">
      </label>
    </div>
  </header>
  <main>
    <div class="summary">
      <section>
        <h2>Concept Counts</h2>
        <table>{concept_summary}</table>
      </section>
      <section>
        <h2>Review Rule</h2>
        <p class="meta">Final inclusion still requires manual pass on temporal necessity, domain specificity, static shortcut risk, source/license check, and text leakage.</p>
      </section>
    </div>
    <section id="candidates">
      {''.join(rows)}
    </section>
  </main>
  <script>
    const domainFilter = document.getElementById('domain-filter');
    const priorityFilter = document.getElementById('priority-filter');
    const textFilter = document.getElementById('text-filter');
    const visibleCount = document.getElementById('visible-count');
    const cards = Array.from(document.querySelectorAll('.candidate'));

    function applyFilters() {{
      const domain = domainFilter.value;
      const priority = priorityFilter.value;
      const text = textFilter.value.trim().toLowerCase();
      let visible = 0;
      for (const card of cards) {{
        const domainOk = !domain || card.dataset.domain === domain;
        const priorityOk = !priority || card.dataset.priority === priority;
        const textOk = !text || card.textContent.toLowerCase().includes(text);
        const show = domainOk && priorityOk && textOk;
        card.classList.toggle('hidden', !show);
        if (show) visible += 1;
      }}
      visibleCount.textContent = String(visible);
    }}

    domainFilter.addEventListener('change', applyFilters);
    priorityFilter.addEventListener('change', applyFilters);
    textFilter.addEventListener('input', applyFilters);
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidates",
        type=Path,
        nargs="+",
        default=[Path("data/vdcr_candidate_videos_archive_only_v1.csv")],
    )
    parser.add_argument("--concepts", type=Path, default=Path("data/vdcr_concept_inventory_v1.csv"))
    parser.add_argument("--output", type=Path, default=Path("reports/vdcr_candidate_review_v1.html"))
    args = parser.parse_args()

    candidate_groups = [(path, read_csv(path)) for path in args.candidates if path.exists()]
    candidates = dedupe_candidates(candidate_groups)
    concept_rows = read_csv(args.concepts)
    concepts = {row["concept_en"]: row for row in concept_rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(candidates, concepts), encoding="utf-8")
    print(f"candidates={len(candidates)} wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
