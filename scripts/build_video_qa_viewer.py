#!/usr/bin/env python3
"""Build a static video+QA browser for a DynaKnow-Video release."""

from __future__ import annotations

import argparse
import csv
import html
import json
import mimetypes
import os
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


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


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


def render_sample(sample: dict, manifest: dict[str, dict[str, str]], output: Path, root: Path) -> str:
    video_id = sample["video_id"]
    manifest_row = manifest.get(video_id, {})
    local_media = sample.get("local_media") or manifest_row.get("local_media", "")
    source_url = manifest_row.get("source_url", "")
    source_grounding_note = manifest_row.get("source_grounding_note", "")
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
    evidence = render_evidence(sample.get("dynamic_evidence", []))
    source_link = f'<a href="{esc(source_url)}">source page</a>' if source_url else ""
    link_items = " · ".join(item for item in [media_link, source_link] if item)
    links_html = f'<p class="media-links">{link_items}</p>' if link_items else ""

    return f"""
    <article class="sample" data-category="{esc(sample.get("category", ""))}" data-answer="{esc(answer)}">
      <div class="media-panel">
        {video_html}
        {links_html}
        {sparse_img}
      </div>
      <div class="qa-panel">
        <div class="sample-head">
          <div>
            <h2>{esc(video_id)}</h2>
            <p class="meta">{esc(sample.get("category", ""))} · {esc(sample.get("duration_sec", ""))}s</p>
          </div>
          <span class="answer">Answer {esc(answer)}</span>
        </div>
        <p class="knowledge">{esc(sample.get("knowledge_point", ""))}</p>
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
        {f'<section class="detail source-grounding"><h3>Source Grounding</h3><p>{esc(source_grounding_note)}</p></section>' if source_grounding_note else ''}
      </div>
    </article>
    """


def build_html(samples: list[dict], manifest: dict[str, dict[str, str]], output: Path, root: Path, title: str) -> str:
    categories = sorted({sample.get("category", "") for sample in samples})
    answer_counts = {key: 0 for key in ["A", "B", "C", "D"]}
    for sample in samples:
        answer = sample.get("answer")
        if answer in answer_counts:
            answer_counts[answer] += 1
    local_count = sum(1 for sample in samples if sample.get("local_media") or manifest.get(sample["video_id"], {}).get("local_media"))
    cards = "\n".join(render_sample(sample, manifest, output, root) for sample in samples)
    category_options = "\n".join(f'<option value="{esc(category)}">{esc(category)}</option>' for category in categories)
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
      </div>
      <div class="controls">
        <input id="query" type="search" placeholder="Search ID or knowledge point" aria-label="Search">
        <select id="category" aria-label="Category">
          <option value="">All categories</option>
          {category_options}
        </select>
      </div>
    </div>
  </header>
  <main id="samples">
    {cards}
  </main>
  <script>
    const query = document.getElementById('query');
    const category = document.getElementById('category');
    const samples = Array.from(document.querySelectorAll('.sample'));
    function applyFilters() {{
      const q = query.value.trim().toLowerCase();
      const c = category.value;
      for (const sample of samples) {{
        const text = sample.textContent.toLowerCase();
        const visible = (!q || text.includes(q)) && (!c || sample.dataset.category === c);
        sample.style.display = visible ? '' : 'none';
      }}
    }}
    query.addEventListener('input', applyFilters);
    category.addEventListener('change', applyFilters);
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
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
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_html(samples, manifest, output, root, args.title), encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
