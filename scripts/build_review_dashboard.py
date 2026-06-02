#!/usr/bin/env python3
"""Build a static HTML review dashboard for DynaKnow pilot data."""

from __future__ import annotations

import argparse
import csv
import html
import json
import os
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def rel(path: Path, base: Path) -> str:
    return html.escape(os.path.relpath(path, start=base.parent))


def esc(value: object) -> str:
    return html.escape(str(value))


def render_sample(sample: dict, root: Path, output: Path) -> str:
    video_id = sample["video_id"]
    review = sample.get("shortcut_human_review", {})
    contact = root / "media" / "contact_sheets" / "seed_first_middle_last.jpg"
    sparse = root / "media" / "contact_sheets" / "sparse" / f"{video_id}_sparse.jpg"
    media_dir = root / "media" / "raw"
    media_files = sorted(media_dir.glob(f"{video_id}.*"))
    media_link = ""
    if media_files:
        media_link = f'<a href="{rel(media_files[0], output)}">local media</a>'
    sparse_img = f'<img src="{rel(sparse, output)}" alt="{video_id} sparse">' if sparse.exists() else "<em>No sparse sheet</em>"
    return f"""
    <section class="card">
      <h3>{esc(video_id)}: {esc(sample["knowledge_point"])}</h3>
      <p><strong>Decision:</strong> {esc(review.get("decision", "pending"))} | {media_link} | <a href="{esc(sample["source_url"])}">source</a></p>
      <p><strong>Question:</strong> {esc(sample["question"])}</p>
      <ol type="A">
        <li>{esc(sample["choices"]["A"])}</li>
        <li>{esc(sample["choices"]["B"])}</li>
        <li>{esc(sample["choices"]["C"])}</li>
        <li>{esc(sample["choices"]["D"])}</li>
      </ol>
      <p><strong>Answer:</strong> {esc(sample["answer"])}</p>
      <p><strong>Review notes:</strong> {esc(review.get("review_notes", ""))}</p>
      <div class="sheet">{sparse_img}</div>
    </section>
    """


def render_queue_table(rows: list[dict[str, str]], limit: int) -> str:
    body = []
    for row in rows[:limit]:
        body.append(
            "<tr>"
            f"<td>{esc(row.get('candidate_id',''))}</td>"
            f"<td>{esc(row.get('priority_score',''))}</td>"
            f"<td>{esc(row.get('initial_category',''))}</td>"
            f"<td>{esc(row.get('candidate_knowledge_point',''))}</td>"
            f"<td>{esc(row.get('raw_duration_sec',''))}</td>"
            f"<td><a href=\"{esc(row.get('source_url',''))}\">source</a></td>"
            f"<td>{esc(row.get('review_flags',''))}</td>"
            "</tr>"
        )
    return "\n".join(body)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--queue-limit", type=int, default=40)
    args = parser.parse_args()

    root = args.root
    accepted = read_jsonl(root / "data" / "pilot_samples_accepted_seed.jsonl")
    rejected = read_jsonl(root / "data" / "pilot_samples_rejected_or_revise_seed.jsonl")
    queue = read_csv(root / "data" / "review_queue_seed.csv")
    shortcut_review = read_csv(root / "data" / "shortcut_human_review_seed.csv")

    accepted_html = "\n".join(render_sample(sample, root, args.output) for sample in accepted)
    rejected_html = "\n".join(render_sample(sample, root, args.output) for sample in rejected)
    queue_table = render_queue_table(queue, args.queue_limit)

    html_text = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>DynaKnow-Video Review Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #222; }}
    h1, h2 {{ margin-bottom: 8px; }}
    .summary {{ display: flex; gap: 16px; margin: 16px 0 24px; }}
    .metric {{ border: 1px solid #ccc; padding: 12px; min-width: 140px; }}
    .card {{ border: 1px solid #ccc; padding: 16px; margin: 16px 0; }}
    img {{ max-width: 100%; border: 1px solid #ddd; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #ddd; padding: 6px; vertical-align: top; }}
    th {{ background: #f5f5f5; }}
  </style>
</head>
<body>
  <h1>DynaKnow-Video Review Dashboard</h1>
  <div class="summary">
    <div class="metric"><strong>Accepted seed</strong><br>{len(accepted)}</div>
    <div class="metric"><strong>Revise/reject</strong><br>{len(rejected)}</div>
    <div class="metric"><strong>Shortcut reviewed</strong><br>{len(shortcut_review)}</div>
    <div class="metric"><strong>Queue rows</strong><br>{len(queue)}</div>
  </div>

  <h2>Accepted Seed Samples</h2>
  {accepted_html}

  <h2>Revise / Reject Samples</h2>
  {rejected_html}

  <h2>Prioritized Review Queue Top {args.queue_limit}</h2>
  <table>
    <thead>
      <tr><th>ID</th><th>Priority</th><th>Category</th><th>Knowledge Point</th><th>Duration</th><th>Source</th><th>Flags</th></tr>
    </thead>
    <tbody>{queue_table}</tbody>
  </table>
</body>
</html>
"""

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_text, encoding="utf-8")
    print(f"wrote dashboard to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
