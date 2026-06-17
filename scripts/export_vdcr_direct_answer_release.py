#!/usr/bin/env python3
"""Export a source-hidden VDCR direct-answer release package."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


RELEASE_FIELDS = {
    "video_id",
    "split",
    "domain",
    "subdomain",
    "concept_id",
    "concept",
    "answer",
    "accepted_answers",
    "local_media",
    "duration_sec",
    "question",
    "dynamic_evidence",
    "static_insufficient_reason",
    "quality_gates",
}

SOURCE_FIELDS = {
    "source_url",
    "license_or_usage_note",
    "source_title",
    "source_summary",
    "source_description",
    "direct_media_url",
    "download_url",
    "author",
    "caption",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def source_hidden_row(row: dict[str, Any], split: str) -> dict[str, Any]:
    output = {key: row[key] for key in RELEASE_FIELDS if key in row}
    output["split"] = split
    return output


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def write_manifest(path: Path, source_rows: list[dict[str, Any]], release_rows: list[dict[str, Any]]) -> None:
    release_by_id = {row["video_id"]: row for row in release_rows}
    fields = [
        "video_id",
        "split",
        "domain",
        "subdomain",
        "concept_id",
        "answer",
        "local_media",
        "duration_sec",
        "source_url",
        "license_or_usage_note",
        "concept_validity_tier",
        "production_gate",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for source in source_rows:
            release = release_by_id[source["video_id"]]
            quality_gates = release.get("quality_gates", {})
            concept = release.get("concept", {})
            writer.writerow(
                {
                    "video_id": release["video_id"],
                    "split": release["split"],
                    "domain": release["domain"],
                    "subdomain": release["subdomain"],
                    "concept_id": release["concept_id"],
                    "answer": release["answer"],
                    "local_media": release["local_media"],
                    "duration_sec": release["duration_sec"],
                    "source_url": source.get("source_url", ""),
                    "license_or_usage_note": source.get("license_or_usage_note", ""),
                    "concept_validity_tier": concept.get("validity_tier", quality_gates.get("concept_validity_tier", "")),
                    "production_gate": quality_gates.get("production_gate", ""),
                }
            )


def pct(value: int, total: int) -> str:
    return "0.0%" if total == 0 else f"{100.0 * value / total:.1f}%"


def write_stats(path: Path, rows: list[dict[str, Any]]) -> None:
    total = len(rows)
    by_domain = Counter(row.get("domain", "") for row in rows)
    by_type = Counter(row.get("concept", {}).get("type", "") for row in rows)
    by_tier = Counter(row.get("concept", {}).get("validity_tier", "") for row in rows)
    durations = [float(row.get("duration_sec", 0.0)) for row in rows]
    lines = [
        "# VDCR v1 Direct-Answer Dataset Stats",
        "",
        f"- samples: {total}",
        f"- unique video ids: {len({row.get('video_id') for row in rows})}",
        f"- unique answers: {len({row.get('answer') for row in rows})}",
        f"- local media references: {sum(1 for row in rows if row.get('local_media'))}/{total} ({pct(sum(1 for row in rows if row.get('local_media')), total)})",
        f"- total duration sec: {sum(durations):.1f}",
        f"- mean duration sec: {(sum(durations) / total if total else 0):.1f}",
        f"- min duration sec: {(min(durations) if durations else 0):.1f}",
        f"- max duration sec: {(max(durations) if durations else 0):.1f}",
        "",
        "## Domain Distribution",
        "",
    ]
    for domain, count in sorted(by_domain.items()):
        lines.append(f"- `{domain}`: {count} ({pct(count, total)})")
    lines.extend(["", "## Concept Type Distribution", ""])
    for concept_type, count in sorted(by_type.items()):
        lines.append(f"- `{concept_type}`: {count} ({pct(count, total)})")
    lines.extend(["", "## Concept Validity Tier", ""])
    for tier, count in sorted(by_tier.items()):
        lines.append(f"- `{tier}`: {count} ({pct(count, total)})")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(path: Path, rows: list[dict[str, Any]]) -> None:
    by_domain = Counter(row.get("domain", "") for row in rows)
    lines = [
        "# VDCR v1 Direct-Answer Pilot Release",
        "",
        "This package is a source-hidden, locally runnable evaluation snapshot for dynamic video concept recognition.",
        "",
        "Task:",
        "",
        "```text",
        "Which named dynamic concept is instantiated by the temporally evolving process in this video?",
        "```",
        "",
        "Files:",
        "",
        "- `dataset_v1.jsonl`: evaluation JSONL. It excludes source URLs, titles, and license notes.",
        "- `manifest_v1.csv`: provenance and license/source audit fields. Do not pass this file to models.",
        "- `stats_v1.md`: sample count, domain distribution, concept type distribution, and duration summary.",
        "",
        "Current status:",
        "",
        f"- samples: {len(rows)}",
        f"- domains: {', '.join(f'{domain}={count}' for domain, count in sorted(by_domain.items()))}",
        "- all rows are direct-answer samples with accepted answer aliases.",
        "- all rows carry temporal evidence spans, static-insufficiency rationale, and passing dynamic quality gates.",
        "",
        "Validation:",
        "",
        "```bash",
        "python3 scripts/validate_vdcr_direct_answer.py \\",
        "  --input release/v1/dataset_v1.jsonl \\",
        "  --release-mode \\",
        "  --check-media \\",
        "  --min-samples 100 \\",
        "  --min-duration-sec 1.0 \\",
        "  --min-video-frames 2 \\",
        "  --max-domain-imbalance 1",
        "```",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/vdcr_pilot_samples_direct_answer_v1.jsonl"))
    parser.add_argument("--dataset-output", type=Path, default=Path("release/v1/dataset_v1.jsonl"))
    parser.add_argument("--manifest-output", type=Path, default=Path("release/v1/manifest_v1.csv"))
    parser.add_argument("--stats-output", type=Path, default=Path("release/v1/stats_v1.md"))
    parser.add_argument("--readme-output", type=Path, default=Path("release/v1/README.md"))
    parser.add_argument("--split", default="pilot")
    parser.add_argument(
        "--exclude-video-id",
        action="append",
        default=[],
        help="Video id to exclude from the release export. May be passed multiple times.",
    )
    args = parser.parse_args()

    excluded = set(args.exclude_video_id)
    source_rows = [row for row in read_jsonl(args.input) if row.get("video_id") not in excluded]
    release_rows = [source_hidden_row(row, args.split) for row in source_rows]
    leaked = sorted({field for row in release_rows for field in SOURCE_FIELDS if field in row})
    if leaked:
        raise SystemExit(f"release rows still contain source fields: {', '.join(leaked)}")

    write_jsonl(args.dataset_output, release_rows)
    write_manifest(args.manifest_output, source_rows, release_rows)
    write_stats(args.stats_output, release_rows)
    write_readme(args.readme_output, release_rows)
    print(f"wrote {len(release_rows)} source-hidden rows to {args.dataset_output}")
    print(f"wrote provenance manifest to {args.manifest_output}")
    print(f"wrote stats to {args.stats_output}")
    print(f"wrote README to {args.readme_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
