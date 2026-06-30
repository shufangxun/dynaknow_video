#!/usr/bin/env python3
"""Build repeatable VDCR V2 construction inputs from V1 seeds and candidate pools."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DOMAINS = [
    "biology_living_systems",
    "chemistry_materials_change",
    "earth_environmental_systems",
    "physics_physical_systems",
]
MAIN_TIERS = {"core_main", "strict_main_candidate"}

CANDIDATE_FIELDS = [
    "candidate_id",
    "source_url",
    "source_platform",
    "license_or_usage_note",
    "raw_duration_sec",
    "suggested_start_sec",
    "suggested_end_sec",
    "initial_category",
    "candidate_knowledge_point",
    "domain_seed",
    "subdomain_seed",
    "why_dynamic",
    "collector_notes",
    "source_csv",
]

REVIEW_FIELDS = [
    "id",
    "candidate_id",
    "candidate_knowledge_point",
    "concept_id",
    "concept_cluster_id",
    "domain_seed",
    "subdomain_seed",
    "source_platform",
    "source_url",
    "license_or_usage_note",
    "raw_duration_sec",
    "local_media",
    "contact_sheet",
    "review_status",
    "recommended_action",
    "suggested_start_sec",
    "suggested_end_sec",
    "review_notes",
    "v1_review_status",
    "v1_seed_status",
    "domain_target_gap",
    "repeat_concept_rank",
    "repeat_concept_cap",
    "source_csv",
]

STATUS_RANK = {
    "pass_candidate": 0,
    "revise": 1,
    "review": 2,
    "": 3,
}

GENERIC_TOKENS = {
    "and",
    "the",
    "effect",
    "reaction",
    "formation",
    "motion",
    "propagation",
    "growth",
    "collapse",
    "video",
    "slow",
    "demonstration",
    "demo",
    "experiment",
}


@dataclass
class V2Assets:
    candidate_rows: list[dict[str, str]]
    review_queue: list[dict[str, str]]
    seed_samples: list[dict[str, Any]]
    stats: dict[str, int]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{field: row.get(field, "") for field in fields} for row in rows])


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def write_stats(path: Path, stats: dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# VDCR V2 Construction Status", ""]
    for key in sorted(stats):
        lines.append(f"- {key}: {stats[key]}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def concept_key(text: str) -> str:
    return " ".join((text or "").casefold().replace(" / ", "/").split())


def concept_tokens(concept: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[A-Za-z0-9]+", concept.casefold())
        if len(token) >= 4 and token not in GENERIC_TOKENS
    ]


def note_field(notes: str, field: str) -> str:
    match = re.search(rf"{re.escape(field)}=([^;]+)", notes or "")
    return match.group(1) if match else ""


def normalized_text(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.casefold()))


def has_candidate_text_match(row: dict[str, str]) -> bool:
    concept = row.get("candidate_knowledge_point", "")
    tokens = concept_tokens(concept)
    if not tokens:
        return True
    notes = row.get("collector_notes", "")
    searchable = " ".join(
        [
            row.get("source_url", ""),
            note_field(notes, "title"),
            note_field(notes, "description"),
        ]
    )
    normalized_searchable = normalized_text(searchable)
    normalized_concept = normalized_text(concept)
    if normalized_concept and normalized_concept in normalized_searchable:
        return True
    matched = sum(1 for token in set(tokens) if token in normalized_searchable)
    required = 2 if len(set(tokens)) >= 2 else 1
    if len(set(tokens)) == 1 and len(re.findall(r"[A-Za-z0-9]+", concept)) > 1:
        return False
    return matched >= required


def needs_auto_retrieval_text_filter(row: dict[str, str]) -> bool:
    source_csv = row.get("source_csv", "")
    candidate_id = row.get("candidate_id", "")
    return source_csv.startswith("runs/v2_retrieval/") or candidate_id.startswith(("v2_archive_", "v2_commons_"))


def build_concept_map(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    mapped: dict[str, dict[str, str]] = {}
    for row in rows:
        keys = [
            row.get("concept_en", ""),
            row.get("concept_zh", ""),
            row.get("recommended_answer_en", ""),
            row.get("recommended_answer_zh", ""),
        ]
        try:
            keys.extend(json.loads(row.get("accepted_answers_json", "[]")))
        except json.JSONDecodeError:
            pass
        for key in keys:
            if key:
                mapped[concept_key(key)] = row
    return mapped


def merge_candidates(candidate_groups: list[list[dict[str, str]]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    for group in candidate_groups:
        for row in group:
            source_url = row.get("source_url", "")
            if not source_url or source_url in seen_urls:
                continue
            seen_urls.add(source_url)
            rows.append({field: row.get(field, "") for field in CANDIDATE_FIELDS})
    return rows


def build_review_status(review_rows: list[dict[str, str]]) -> dict[str, str]:
    status_by_id: dict[str, str] = {}
    for row in review_rows:
        review_id = row.get("id", "") or row.get("candidate_id", "")
        status = row.get("review_status", "") or row.get("reviewer_decision", "")
        if not review_id or not status:
            continue
        status_by_id[review_id] = status
    return status_by_id


def sample_source_urls(samples: list[dict[str, Any]]) -> set[str]:
    return {str(row.get("source_url", "")) for row in samples if row.get("source_url")}


def seed_samples_for_v2(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in samples:
        copied = dict(row)
        copied["split"] = "v2_seed"
        output.append(copied)
    return output


def concept_for_candidate(row: dict[str, str], concept_by_answer: dict[str, dict[str, str]]) -> dict[str, str]:
    answer = row.get("candidate_knowledge_point", "")
    return concept_by_answer.get(concept_key(answer)) or concept_by_answer.get(answer, {})


def candidate_domain(row: dict[str, str], concept: dict[str, str]) -> str:
    return concept.get("domain") or row.get("domain_seed") or row.get("initial_category", "")


def candidate_subdomain(row: dict[str, str], concept: dict[str, str]) -> str:
    return concept.get("subdomain") or row.get("subdomain_seed", "")


def priority_rank(
    row: dict[str, str],
    concept: dict[str, str],
    status: str,
    gap: int,
    has_review_assets: bool = False,
) -> tuple[int, bool, int, int, float, str]:
    priority = concept.get("priority") or ("A" if "priority=A" in row.get("collector_notes", "") else "")
    priority_order = {"A": 0, "B": 1, "C": 2, "": 3}
    try:
        duration = float(row.get("raw_duration_sec", "") or 0.0)
    except ValueError:
        duration = 0.0
    return (
        -gap,
        not has_review_assets,
        STATUS_RANK.get(status, 4),
        priority_order.get(priority, 3),
        duration <= 0 or duration > 180,
        row.get("candidate_id", ""),
    )


def build_v2_assets(
    v1_samples: list[dict[str, Any]],
    candidate_rows: list[dict[str, str]],
    concept_by_answer: dict[str, dict[str, str]],
    reviewed_status_by_id: dict[str, str],
    target_per_domain: int,
    max_videos_per_concept: int,
    queue_limit: int,
    release_video_ids: set[str] | None = None,
    include_action_concepts: bool = False,
    review_assets_by_id: dict[str, dict[str, str]] | None = None,
) -> V2Assets:
    if release_video_ids is not None:
        v1_samples = [row for row in v1_samples if row.get("video_id") in release_video_ids]
    seed_samples = seed_samples_for_v2(v1_samples)
    seed_urls = sample_source_urls(v1_samples)
    domain_counts = Counter(str(row.get("domain", "")) for row in v1_samples)
    concept_counts = Counter(str(row.get("answer", "")) for row in v1_samples)

    eligible: list[tuple[tuple[int, int, int, float, str], dict[str, str], dict[str, str], str, str, int, int]] = []
    filtered_auto_text = 0
    filtered_action = 0
    filtered_cluster_cap = 0
    filtered_domain = 0
    filtered_non_main_tier = 0
    filtered_reject = 0
    filtered_seed_url = 0
    for row in candidate_rows:
        if row.get("source_url", "") in seed_urls:
            filtered_seed_url += 1
            continue
        if needs_auto_retrieval_text_filter(row) and not has_candidate_text_match(row):
            filtered_auto_text += 1
            continue
        status = reviewed_status_by_id.get(row.get("candidate_id", ""), "")
        if status == "reject":
            filtered_reject += 1
            continue
        concept = concept_for_candidate(row, concept_by_answer)
        if not include_action_concepts and concept.get("concept_type") == "专有动态动作概念":
            filtered_action += 1
            continue
        tier = concept.get("concept_validity_tier", "")
        if tier and tier not in MAIN_TIERS:
            filtered_non_main_tier += 1
            continue
        domain = candidate_domain(row, concept)
        if domain not in DOMAINS:
            filtered_domain += 1
            continue
        answer = row.get("candidate_knowledge_point", "")
        repeat_rank = concept_counts.get(answer, 0) + 1
        if max_videos_per_concept > 0 and repeat_rank > max_videos_per_concept:
            filtered_cluster_cap += 1
            continue
        gap = max(target_per_domain - domain_counts.get(domain, 0), 0)
        review_assets = (review_assets_by_id or {}).get(row.get("candidate_id", ""), {})
        has_review_assets = bool(review_assets.get("local_media") and review_assets.get("contact_sheet"))
        eligible.append((priority_rank(row, concept, status, gap, has_review_assets), row, concept, status, domain, gap, repeat_rank))

    eligible.sort(key=lambda item: item[0])
    review_queue: list[dict[str, str]] = []
    working_domain_counts = Counter(domain_counts)
    working_concept_counts = Counter(concept_counts)
    for _, row, concept, status, domain, gap, _repeat_rank in eligible:
        answer = row.get("candidate_knowledge_point", "")
        repeat_rank = working_concept_counts.get(answer, 0) + 1
        if max_videos_per_concept > 0 and repeat_rank > max_videos_per_concept:
            continue
        review_assets = (review_assets_by_id or {}).get(row.get("candidate_id", ""), {})
        current_gap = max(target_per_domain - working_domain_counts.get(domain, 0), 0)
        review_queue.append(
            {
                "id": row.get("candidate_id", ""),
                "candidate_id": row.get("candidate_id", ""),
                "candidate_knowledge_point": answer,
                "concept_id": concept.get("concept_id", ""),
                "concept_cluster_id": concept.get("concept_id", "") or concept_key(answer).replace(" ", "_"),
                "domain_seed": domain,
                "subdomain_seed": candidate_subdomain(row, concept),
                "source_platform": row.get("source_platform", ""),
                "source_url": row.get("source_url", ""),
                "license_or_usage_note": row.get("license_or_usage_note", ""),
                "raw_duration_sec": row.get("raw_duration_sec", ""),
                "local_media": review_assets.get("local_media", ""),
                "contact_sheet": review_assets.get("contact_sheet", ""),
                "review_status": "review",
                "recommended_action": "inspect_video",
                "suggested_start_sec": row.get("suggested_start_sec", "0"),
                "suggested_end_sec": row.get("suggested_end_sec", "30"),
                "review_notes": row.get("why_dynamic", ""),
                "v1_review_status": status,
                "v1_seed_status": "new_candidate",
                "domain_target_gap": str(current_gap if current_gap else gap),
                "repeat_concept_rank": str(repeat_rank),
                "repeat_concept_cap": str(max_videos_per_concept),
                "source_csv": row.get("source_csv", ""),
            }
        )
        working_domain_counts[domain] += 1
        working_concept_counts[answer] += 1
        if queue_limit > 0 and len(review_queue) >= queue_limit:
            break

    stats = {
        "seed_samples": len(seed_samples),
        "candidate_rows": len(candidate_rows),
        "review_queue_rows": len(review_queue),
        "seed_unique_concepts": len({row.get("answer", "") for row in v1_samples}),
        "target_per_domain": target_per_domain,
        "max_videos_per_concept": max_videos_per_concept,
        "filtered_auto_retrieval_text_mismatch": filtered_auto_text,
        "filtered_action_concepts": filtered_action,
        "filtered_cluster_cap": filtered_cluster_cap,
        "filtered_domain": filtered_domain,
        "filtered_non_main_tier_concepts": filtered_non_main_tier,
        "filtered_rejected_review_rows": filtered_reject,
        "filtered_seed_source_urls": filtered_seed_url,
    }
    for domain in DOMAINS:
        stats[f"seed_domain_{domain}"] = domain_counts.get(domain, 0)
        stats[f"queued_domain_{domain}"] = sum(1 for row in review_queue if row.get("domain_seed") == domain)

    return V2Assets(candidate_rows=candidate_rows, review_queue=review_queue, seed_samples=seed_samples, stats=stats)


def discover_v2_candidate_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    runs_dir = root / "runs" / "v2_retrieval"
    if not runs_dir.exists():
        return paths
    for path in sorted(runs_dir.glob("*/archive_candidates.csv")) + sorted(runs_dir.glob("*/commons_candidates.csv")):
        if "/test_" in str(path):
            continue
        run_dir = path.parent
        if not (run_dir / "summary.txt").exists():
            continue
        pid_path = run_dir / "pid"
        if pid_path.exists():
            try:
                pid = int(pid_path.read_text(encoding="utf-8").strip())
            except ValueError:
                pid = 0
            if pid > 0 and Path(f"/proc/{pid}").exists():
                continue
        paths.append(path)
    return paths


def discover_local_v2_candidate_paths(root: Path) -> list[Path]:
    data_dir = root / "data"
    if not data_dir.exists():
        return []
    return [
        path
        for path in sorted(data_dir.glob("vdcr_candidate_videos_*_v2.csv"))
        if path.name != "vdcr_candidate_videos_combined_v2.csv"
    ]


def discover_review_assets(root: Path) -> dict[str, dict[str, str]]:
    assets: dict[str, dict[str, str]] = {}
    data_dir = root / "data"
    def exists_in_root(path_text: str) -> bool:
        if not path_text:
            return False
        path = Path(path_text)
        if not path.is_absolute():
            path = root / path
        return path.exists()

    if data_dir.exists():
        review_asset_paths = [
            *sorted(data_dir.glob("vdcr_pilot_manual_review*_v1.csv")),
            data_dir / "vdcr_v2_clean_derivatives_review.csv",
            *sorted(data_dir.glob("vdcr_v2_*manual_review.csv")),
        ]
        for review_path in review_asset_paths:
            for row in read_csv(review_path):
                item_id = row.get("id", "") or row.get("candidate_id", "")
                if not item_id:
                    continue
                if exists_in_root(row.get("local_media", "")):
                    assets.setdefault(item_id, {})["local_media"] = row.get("local_media", "")
                if exists_in_root(row.get("contact_sheet", "")):
                    assets.setdefault(item_id, {})["contact_sheet"] = row.get("contact_sheet", "")
        for status_path in sorted(data_dir.glob("vdcr_v2_*download_status.csv")):
            for row in read_csv(status_path):
                if row.get("ok") != "true" or not row.get("local_media"):
                    continue
                item_id = row.get("id", "")
                if not item_id:
                    continue
                assets.setdefault(item_id, {})["local_media"] = row.get("local_media", "")
    reports_dir = root / "reports"
    if reports_dir.exists():
        for sheet in sorted(reports_dir.glob("vdcr_v2_*sparse_sheets/*_sparse.jpg")):
            item_id = sheet.name.removesuffix("_sparse.jpg")
            assets.setdefault(item_id, {})["contact_sheet"] = str(sheet)
    return assets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-samples", type=Path, default=Path("data/vdcr_pilot_samples_direct_answer_v1.jsonl"))
    parser.add_argument("--v1-release-filter", type=Path, default=Path("release/v1/dataset_v1.jsonl"))
    parser.add_argument("--concepts", type=Path, default=Path("data/vdcr_v2_concept_inventory.csv"))
    parser.add_argument("--candidate-input", action="append", default=[], type=Path)
    parser.add_argument("--review-input", action="append", default=[], type=Path)
    parser.add_argument("--output-candidates", type=Path, default=Path("data/vdcr_candidate_videos_combined_v2.csv"))
    parser.add_argument("--output-review-queue", type=Path, default=Path("data/vdcr_v2_review_queue.csv"))
    parser.add_argument("--output-seed-samples", type=Path, default=Path("data/vdcr_v2_seed_samples.jsonl"))
    parser.add_argument("--output-stats", type=Path, default=Path("reports/vdcr_v2_construction_status.md"))
    parser.add_argument("--target-per-domain", type=int, default=75)
    parser.add_argument("--max-videos-per-concept", type=int, default=3)
    parser.add_argument("--queue-limit", type=int, default=360)
    parser.add_argument("--include-action-concepts", action="store_true")
    parser.add_argument("--discover-runs", action="store_true", help="Include completed ignored runs/v2_retrieval outputs.")
    parser.add_argument("--no-discover-runs", action="store_true")
    args = parser.parse_args()

    candidate_paths = args.candidate_input or [Path("data/vdcr_candidate_videos_combined_v1.csv")]
    if not args.candidate_input:
        candidate_paths.extend(discover_local_v2_candidate_paths(Path(".")))
    if args.discover_runs and not args.no_discover_runs:
        candidate_paths.extend(discover_v2_candidate_paths(Path(".")))
    candidate_groups = []
    for path in candidate_paths:
        rows = read_csv(path)
        for row in rows:
            row.setdefault("source_csv", str(path))
            if not row.get("source_csv"):
                row["source_csv"] = str(path)
        candidate_groups.append(rows)

    review_paths = args.review_input or [
        *sorted(Path("data").glob("vdcr_pilot_manual_review*_v1.csv")),
        Path("data/vdcr_v2_clean_derivatives_review.csv"),
        Path("data/vdcr_v2_local_review_triage.csv"),
        *sorted(Path("data").glob("vdcr_v2_*manual_review.csv")),
    ]
    reviewed_status = build_review_status([row for path in review_paths for row in read_csv(path)])

    release_rows = read_jsonl(args.v1_release_filter)
    release_video_ids = {row.get("video_id", "") for row in release_rows} if release_rows else None
    assets = build_v2_assets(
        v1_samples=read_jsonl(args.v1_samples),
        candidate_rows=merge_candidates(candidate_groups),
        concept_by_answer=build_concept_map(read_csv(args.concepts)),
        reviewed_status_by_id=reviewed_status,
        target_per_domain=args.target_per_domain,
        max_videos_per_concept=args.max_videos_per_concept,
        queue_limit=args.queue_limit,
        release_video_ids=release_video_ids,
        include_action_concepts=args.include_action_concepts,
        review_assets_by_id=discover_review_assets(Path(".")),
    )

    write_csv(args.output_candidates, assets.candidate_rows, CANDIDATE_FIELDS)
    write_csv(args.output_review_queue, assets.review_queue, REVIEW_FIELDS)
    write_jsonl(args.output_seed_samples, assets.seed_samples)
    write_stats(args.output_stats, assets.stats)
    print(f"candidate_rows={len(assets.candidate_rows)} wrote {args.output_candidates}")
    print(f"review_queue_rows={len(assets.review_queue)} wrote {args.output_review_queue}")
    print(f"seed_samples={len(assets.seed_samples)} wrote {args.output_seed_samples}")
    print(f"wrote {args.output_stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
