#!/usr/bin/env python3
"""Validate DynaKnow-Video JSONL samples against the v1 workflow.

The checker is dependency-free and intentionally works with both current
internal review JSONL rows and final source-hidden release JSONL rows. When a
sample does not carry explicit domain/subdomain fields, the checker derives
them from the taxonomy by exact knowledge-point match.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from taxonomy_aliases import normalize_domain_subdomain


DOMAINS = {
    "physics_physical_systems",
    "chemistry_materials_change",
    "biology_living_systems",
    "earth_environmental_systems",
    "engineering_operational_systems",
}
ANSWERS = {"A", "B", "C", "D"}
LEGACY_DECISIONS = {
    "mechanism_keep": "pass",
    "mechanism_review": "review",
    "mechanism_reject_or_rewrite": "fail",
}
DECISIONS = {"pass", "review", "fail", *LEGACY_DECISIONS}
RELEASE_LEAK_FIELDS = {
    "source_url",
    "source_title",
    "source_summary",
    "source_description",
    "source_grounding_note",
    "license_or_usage_note",
    "direct_media_url",
    "download_url",
    "author",
    "caption",
}
BROAD_PATTERNS = [
    re.compile(r"\bsome chemical reactions?\b", re.IGNORECASE),
    re.compile(r"\bsome reactions?\b", re.IGNORECASE),
    re.compile(r"\bsome mixtures?\b", re.IGNORECASE),
    re.compile(r"\bcan cause (a )?(change|movement|effect)\b", re.IGNORECASE),
    re.compile(r"\bproduce color change\b", re.IGNORECASE),
    re.compile(r"\bform a precipitate\b", re.IGNORECASE),
    re.compile(r"\bseeds? sprout\b", re.IGNORECASE),
    re.compile(r"\bplants? grows?\b", re.IGNORECASE),
]
CARD_PASS_FLAGS = [
    "visible_temporal_process",
    "single_frame_blocked",
    "mechanism_level_wording",
    "not_just_event_description",
    "source_grounding_is_bounded",
    "no_hidden_assumption_risk",
    "no_leakage_risk",
    "no_shortcut_risk",
    "hard_negative_quality",
]
CARD_SOURCE_PASS_ALIGNMENTS = {
    "video_and_source_agree",
    "video_primary_source_not_used",
}
CARD_SOURCE_FAIL_STATUSES = {
    "needs_review",
    "source_only_or_hidden",
}


def fail(path: Path, line_no: int, message: str) -> str:
    return f"{path}:{line_no}: {message}"


def require(condition: bool, errors: list[str], path: Path, line_no: int, message: str) -> None:
    if not condition:
        errors.append(fail(path, line_no, message))


def canonical_key(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower()).rstrip(".")


def decision_label(value: str) -> str:
    return LEGACY_DECISIONS.get(value, value)


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: line must be a JSON object")
            rows.append(row)
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_audit(path: Path) -> list[dict[str, str]]:
    if path.suffix == ".jsonl":
        return [dict(row) for row in read_jsonl(path)]
    return read_csv(path)


def load_cards(path: Path | None) -> dict[str, dict]:
    if path is None or not path.exists():
        return {}
    return {row["video_id"]: row for row in read_jsonl(path) if row.get("video_id")}


def load_taxonomy(path: Path | None) -> tuple[dict[str, dict[str, str]], set[tuple[str, str]]]:
    if path is None or not path.exists():
        return {}, set()
    rows = read_csv(path)
    for row in rows:
        row["domain"], row["subdomain"] = normalize_domain_subdomain(row.get("domain", ""), row.get("subdomain", ""))
    by_kp = {row["knowledge_point"]: row for row in rows if row.get("knowledge_point")}
    pairs = {(row["domain"], row["subdomain"]) for row in rows if row.get("domain") and row.get("subdomain")}
    return by_kp, pairs


def load_targets(path: Path | None) -> set[tuple[str, str]]:
    if path is None or not path.exists():
        return set()
    return {normalize_domain_subdomain(row["domain"], row["subdomain"]) for row in read_csv(path)}


def infer_taxonomy(row: dict, taxonomy_by_kp: dict[str, dict[str, str]]) -> tuple[str, str]:
    domain = str(row.get("domain", "") or "")
    subdomain = str(row.get("subdomain", "") or "")
    tax = taxonomy_by_kp.get(str(row.get("knowledge_point", "")), {})
    if not domain:
        domain = tax.get("domain", "") or str(row.get("category", "") or "")
    if not subdomain:
        subdomain = tax.get("subdomain", "")
    return normalize_domain_subdomain(domain, subdomain)


def has_broad_wording(text: str) -> str | None:
    for pattern in BROAD_PATTERNS:
        if pattern.search(text):
            return pattern.pattern
    return None


def validate_choices(record: dict, errors: list[str], path: Path, line_no: int) -> None:
    choices = record.get("choices")
    require(isinstance(choices, dict), errors, path, line_no, "choices must be an object")
    if not isinstance(choices, dict):
        return
    require(set(choices) == ANSWERS, errors, path, line_no, "choices must contain exactly A, B, C, D")
    for key in sorted(ANSWERS):
        value = choices.get(key)
        require(isinstance(value, str) and len(value) >= 5, errors, path, line_no, f"choice {key} is too short")
    if set(choices) == ANSWERS:
        normalized = [canonical_key(str(choices.get(key, ""))) for key in sorted(ANSWERS)]
        require(len(normalized) == len(set(normalized)), errors, path, line_no, "choices must be unique")
    answer = record.get("answer")
    require(answer in ANSWERS, errors, path, line_no, "answer must be A, B, C, or D")
    if answer in choices and isinstance(record.get("knowledge_point"), str):
        require(
            choices[answer] == record["knowledge_point"],
            errors,
            path,
            line_no,
            "correct answer choice must equal knowledge_point",
        )


def validate_evidence(record: dict, errors: list[str], path: Path, line_no: int) -> None:
    evidence = record.get("dynamic_evidence")
    require(isinstance(evidence, list) and len(evidence) >= 1, errors, path, line_no, "dynamic_evidence must contain at least one span")
    if not isinstance(evidence, list):
        return
    for idx, span in enumerate(evidence):
        require(isinstance(span, dict), errors, path, line_no, f"dynamic_evidence[{idx}] must be an object")
        if not isinstance(span, dict):
            continue
        for key in ["start_sec", "end_sec", "description"]:
            require(key in span, errors, path, line_no, f"dynamic_evidence[{idx}] missing {key}")
        start = span.get("start_sec")
        end = span.get("end_sec")
        require(isinstance(start, (int, float)), errors, path, line_no, f"dynamic_evidence[{idx}].start_sec must be numeric")
        require(isinstance(end, (int, float)), errors, path, line_no, f"dynamic_evidence[{idx}].end_sec must be numeric")
        if isinstance(start, (int, float)) and isinstance(end, (int, float)):
            require(end > start, errors, path, line_no, f"dynamic_evidence[{idx}] end_sec must be greater than start_sec")
        require(
            isinstance(span.get("description"), str) and len(span.get("description", "")) >= 10,
            errors,
            path,
            line_no,
            f"dynamic_evidence[{idx}].description is too short",
        )


def validate_shortcuts(record: dict, errors: list[str], path: Path, line_no: int, release_mode: bool) -> None:
    labels = record.get("shortcut_labels")
    legacy = record.get("shortcut_results")
    if release_mode:
        require(isinstance(labels, dict), errors, path, line_no, "release rows must contain shortcut_labels")
    else:
        require(isinstance(labels, dict) or isinstance(legacy, dict), errors, path, line_no, "missing shortcut_labels or shortcut_results")

    if isinstance(labels, dict):
        for key in [
            "answer_only_leakage",
            "single_frame_sufficient",
            "sparse_frames_sufficient",
            "dynamic_knowledge_supported",
            "ocr_leakage_status",
        ]:
            require(key in labels, errors, path, line_no, f"shortcut_labels missing {key}")


def validate_record(
    record: dict,
    path: Path,
    line_no: int,
    taxonomy_by_kp: dict[str, dict[str, str]],
    valid_pairs: set[tuple[str, str]],
    decisions_by_id: dict[str, str],
    cards_by_id: dict[str, dict],
    require_card_pass: bool,
    release_mode: bool,
    check_media: bool,
    root: Path,
) -> list[str]:
    errors: list[str] = []
    required = [
        "video_id",
        "duration_sec",
        "knowledge_point",
        "question",
        "choices",
        "answer",
        "dynamic_evidence",
        "static_insufficient_reason",
    ]
    if release_mode:
        required.extend(["split", "domain", "subdomain", "local_media", "shortcut_labels"])
    for key in required:
        require(key in record, errors, path, line_no, f"missing required field: {key}")
    if errors:
        return errors

    video_id = record.get("video_id")
    require(isinstance(video_id, str) and re.match(r"^dynaknow_[0-9]{6}$", video_id) is not None, errors, path, line_no, "video_id must match dynaknow_000000")
    require(isinstance(record.get("duration_sec"), (int, float)) and record["duration_sec"] > 0, errors, path, line_no, "duration_sec must be positive")
    require(isinstance(record.get("knowledge_point"), str) and len(record["knowledge_point"]) >= 10, errors, path, line_no, "knowledge_point is too short")
    require("dynamic process" in str(record.get("question", "")).lower(), errors, path, line_no, "question should use the generic dynamic process wording")

    domain, subdomain = infer_taxonomy(record, taxonomy_by_kp)
    require(domain in DOMAINS, errors, path, line_no, f"unknown domain/category after taxonomy inference: {domain}")
    if valid_pairs:
        require((domain, subdomain) in valid_pairs, errors, path, line_no, f"unknown domain/subdomain pair: {domain}/{subdomain}")
    else:
        require(bool(subdomain) or not release_mode, errors, path, line_no, "missing subdomain")

    if taxonomy_by_kp:
        require(record["knowledge_point"] in taxonomy_by_kp, errors, path, line_no, "knowledge_point is not mapped in taxonomy")

    broad = has_broad_wording(record["knowledge_point"])
    row_decision = decision_label(decisions_by_id.get(str(video_id), ""))
    allow_failed_pool_broad_wording = bool(broad) and not release_mode and row_decision == "fail"
    require(
        broad is None or allow_failed_pool_broad_wording,
        errors,
        path,
        line_no,
        f"knowledge_point has broad/descriptive wording matched by {broad!r}",
    )

    validate_choices(record, errors, path, line_no)
    validate_evidence(record, errors, path, line_no)
    require(
        isinstance(record.get("static_insufficient_reason"), str) and len(record["static_insufficient_reason"]) >= 10,
        errors,
        path,
        line_no,
        "static_insufficient_reason is too short",
    )
    validate_shortcuts(record, errors, path, line_no, release_mode)

    if release_mode:
        for key in RELEASE_LEAK_FIELDS:
            require(key not in record, errors, path, line_no, f"release row must not expose provenance/leakage field: {key}")

    card = cards_by_id.get(str(video_id))
    if cards_by_id or require_card_pass:
        require(card is not None, errors, path, line_no, f"missing Dynamic Knowledge Card for {video_id}")
    if card:
        require(card.get("knowledge_point") == record["knowledge_point"], errors, path, line_no, "card knowledge_point must match sample knowledge_point")
        if release_mode:
            require(card.get("domain") == domain, errors, path, line_no, "card domain must match release sample domain")
            require(card.get("subdomain") == subdomain, errors, path, line_no, "card subdomain must match release sample subdomain")
        if require_card_pass:
            require(card.get("filter_decision") == "pass", errors, path, line_no, f"card filter_decision must be pass, got {card.get('filter_decision')}")
            flags = card.get("verifier_flags", {})
            require(isinstance(flags, dict), errors, path, line_no, "card verifier_flags must be an object")
            if isinstance(flags, dict):
                for flag in CARD_PASS_FLAGS:
                    require(flags.get(flag) is True, errors, path, line_no, f"card verifier flag must be true: {flag}")
            source_check = card.get("source_text_check", {})
            require(isinstance(source_check, dict), errors, path, line_no, "card source_text_check must be an object")
            if isinstance(source_check, dict):
                require(
                    source_check.get("support_status") not in CARD_SOURCE_FAIL_STATUSES,
                    errors,
                    path,
                    line_no,
                    f"card source support must not need review or be source-only: {source_check.get('support_status')}",
                )
                require(
                    source_check.get("alignment_status") in CARD_SOURCE_PASS_ALIGNMENTS,
                    errors,
                    path,
                    line_no,
                    f"card source/video alignment is not release-clean: {source_check.get('alignment_status')}",
                )
                require(
                    source_check.get("requires_human_source_review") is False,
                    errors,
                    path,
                    line_no,
                    "card source_text_check requires human source review",
                )
            distractor_check = card.get("distractor_check", {})
            require(isinstance(distractor_check, dict), errors, path, line_no, "card distractor_check must be an object")
            if isinstance(distractor_check, dict):
                require(
                    distractor_check.get("hard_negative_status") == "pass",
                    errors,
                    path,
                    line_no,
                    f"card hard-negative status must be pass: {distractor_check.get('hard_negative_status')}",
                )
                require(
                    distractor_check.get("answer_only_elimination_risk") is False,
                    errors,
                    path,
                    line_no,
                    "card distractors create answer-only elimination risk",
                )

    local_media = record.get("local_media")
    if check_media:
        require(isinstance(local_media, str) and local_media, errors, path, line_no, "local_media is required when --check-media is set")
        if isinstance(local_media, str) and local_media:
            media_path = Path(local_media)
            if not media_path.is_absolute():
                media_path = root / media_path
            require(media_path.exists(), errors, path, line_no, f"local_media does not exist: {local_media}")

    return errors


def validate_audit(audit_path: Path, samples: list[dict], taxonomy_by_kp: dict[str, dict[str, str]], valid_pairs: set[tuple[str, str]]) -> list[str]:
    errors: list[str] = []
    sample_ids = {row.get("video_id") for row in samples}
    audit_rows = read_audit(audit_path)
    seen_ids: set[str] = set()
    for idx, row in enumerate(audit_rows, start=2 if audit_path.suffix != ".jsonl" else 1):
        video_id = row.get("video_id", "")
        if video_id in seen_ids:
            errors.append(fail(audit_path, idx, f"duplicate audit video_id: {video_id}"))
        seen_ids.add(video_id)
        if video_id not in sample_ids:
            errors.append(fail(audit_path, idx, f"audit row has no matching sample: {video_id}"))
        decision = row.get("filter_decision", "")
        if decision not in DECISIONS:
            errors.append(fail(audit_path, idx, f"unknown filter_decision: {decision}"))
        kp = row.get("knowledge_point") or row.get("canonical_knowledge_point") or ""
        if kp and taxonomy_by_kp:
            tax = taxonomy_by_kp.get(kp)
            if not tax:
                errors.append(fail(audit_path, idx, f"audit knowledge point is not mapped in taxonomy: {kp}"))
            else:
                tax_domain, tax_subdomain = normalize_domain_subdomain(tax["domain"], tax["subdomain"])
                if valid_pairs and (tax_domain, tax_subdomain) not in valid_pairs:
                    errors.append(fail(audit_path, idx, f"audit taxonomy pair is not in targets: {tax_domain}/{tax_subdomain}"))
    missing = sorted(str(video_id) for video_id in sample_ids - seen_ids if video_id)
    for video_id in missing:
        errors.append(f"{audit_path}: missing audit row for sample {video_id}")
    return errors


def summarize(samples: list[dict], taxonomy_by_kp: dict[str, dict[str, str]], targets: set[tuple[str, str]], audit_path: Path | None) -> str:
    domain_counts: Counter[str] = Counter()
    subdomain_counts: Counter[tuple[str, str]] = Counter()
    kp_groups: defaultdict[str, list[str]] = defaultdict(list)
    for row in samples:
        domain, subdomain = infer_taxonomy(row, taxonomy_by_kp)
        domain_counts[domain] += 1
        subdomain_counts[(domain, subdomain)] += 1
        kp_groups[canonical_key(row.get("knowledge_point", ""))].append(row.get("video_id", ""))

    lines = [
        f"samples={len(samples)}",
        f"domains={len(domain_counts)}",
        f"subdomains={len(subdomain_counts)}",
        f"unique_knowledge_points={len(kp_groups)}",
    ]
    duplicate_groups = sum(1 for ids in kp_groups.values() if len(ids) > 1)
    if duplicate_groups:
        lines.append(f"duplicate_knowledge_point_groups={duplicate_groups}")
    if targets:
        lines.append(f"target_subdomains={len(targets)}")
        lines.append(f"unsampled_target_subdomains={len(targets - set(subdomain_counts))}")
    if audit_path:
        decisions = Counter(decision_label(row.get("filter_decision", "")) for row in read_audit(audit_path))
        lines.append("decisions=" + ",".join(f"{key}:{decisions.get(key, 0)}" for key in ["pass", "review", "fail"]))
    return " ".join(lines)


def validate_jsonl(
    path: Path,
    taxonomy_by_kp: dict[str, dict[str, str]],
    valid_pairs: set[tuple[str, str]],
    decisions_by_id: dict[str, str],
    cards_by_id: dict[str, dict],
    require_card_pass: bool,
    release_mode: bool,
    check_media: bool,
    require_hard_distractors: bool,
    root: Path,
) -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    rows: list[dict] = []
    line_numbers: list[int] = []
    seen_ids: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(fail(path, line_no, f"invalid JSON: {exc}"))
                continue
            if not isinstance(record, dict):
                errors.append(fail(path, line_no, "line must be a JSON object"))
                continue
            video_id = record.get("video_id")
            if video_id in seen_ids:
                errors.append(fail(path, line_no, f"duplicate video_id: {video_id}"))
            if isinstance(video_id, str):
                seen_ids.add(video_id)
            rows.append(record)
            line_numbers.append(line_no)
            errors.extend(
                validate_record(
                    record,
                    path,
                    line_no,
                    taxonomy_by_kp,
                    valid_pairs,
                    decisions_by_id,
                    cards_by_id,
                    require_card_pass,
                    release_mode,
                    check_media,
                    root,
                )
            )
    if require_hard_distractors:
        errors.extend(validate_dataset_distractors(rows, line_numbers, path))
    return rows, errors


def validate_dataset_distractors(rows: list[dict], line_numbers: list[int], path: Path) -> list[str]:
    errors: list[str] = []
    answer_index: defaultdict[str, list[str]] = defaultdict(list)
    for row in rows:
        point = row.get("knowledge_point")
        video_id = row.get("video_id")
        if isinstance(point, str) and isinstance(video_id, str):
            answer_index[canonical_key(point)].append(video_id)

    for row, line_no in zip(rows, line_numbers, strict=True):
        choices = row.get("choices")
        answer = row.get("answer")
        video_id = row.get("video_id")
        if not isinstance(choices, dict) or answer not in ANSWERS:
            continue
        for key, text in choices.items():
            if key == answer or not isinstance(text, str):
                continue
            owners = [owner for owner in answer_index.get(canonical_key(text), []) if owner != video_id]
            require(
                not owners,
                errors,
                path,
                line_no,
                f"choice {key} exactly copies another sample's correct knowledge point: {', '.join(owners)}",
            )
    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("--taxonomy", type=Path, default=Path("data/domain_taxonomy_v1.csv"))
    parser.add_argument("--targets", type=Path, default=Path("data/domain_sampling_targets_v1.csv"))
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--cards", type=Path, help="Dynamic Knowledge Card JSONL to validate against.")
    parser.add_argument("--require-card-pass", action="store_true", help="Require a matching pass card with all release gate flags true.")
    parser.add_argument("--require-hard-distractors", action="store_true", help="Reject choices that exactly copy another sample's correct answer.")
    parser.add_argument("--release-mode", action="store_true", help="Enforce the source-hidden release contract.")
    parser.add_argument("--check-media", action="store_true", help="Require local_media and verify paths exist.")
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv[1:])

    if not args.jsonl.exists():
        print(f"File not found: {args.jsonl}", file=sys.stderr)
        return 2

    taxonomy_by_kp, taxonomy_pairs = load_taxonomy(args.taxonomy)
    target_pairs = load_targets(args.targets)
    valid_pairs = target_pairs or taxonomy_pairs
    audit_rows = read_audit(args.audit) if args.audit else []
    decisions_by_id = {row.get("video_id", ""): row.get("filter_decision", "") for row in audit_rows}
    cards_by_id = load_cards(args.cards)
    samples, errors = validate_jsonl(
        args.jsonl,
        taxonomy_by_kp,
        valid_pairs,
        decisions_by_id,
        cards_by_id,
        args.require_card_pass,
        args.release_mode,
        args.check_media,
        args.require_hard_distractors,
        args.root,
    )
    if args.audit:
        errors.extend(validate_audit(args.audit, samples, taxonomy_by_kp, valid_pairs))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(f"OK: {args.jsonl} {summarize(samples, taxonomy_by_kp, target_pairs, args.audit)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
