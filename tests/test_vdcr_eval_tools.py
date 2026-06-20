import json
from pathlib import Path

import pytest

from scripts.build_vdcr_mcq_from_direct_answer import build_mcq_rows
from scripts.build_vdcr_v2_construction_assets import (
    build_concept_map,
    build_v2_assets,
    discover_local_v2_candidate_paths,
    discover_review_assets,
)
from scripts.build_vdcr_v2_expansion_backlog import build_backlog_queries, build_expansion_backlog
from scripts.build_vdcr_v2_gap_queries import build_gap_queries
from scripts.build_vdcr_v2_review_triage import build_triage_rows, decision_counts
from scripts.apply_vdcr_v2_triage_decisions import apply_triage_decisions
from scripts.build_vdcr_v2_draft_samples import build_draft_samples
from scripts.build_vdcr_segments_from_review import build_segment_manifest_rows
from scripts.build_vdcr_review_dashboard import strip_trailing_whitespace
from scripts.report_vdcr_dual_eval import build_summary_rows
from scripts.run_qwen3_vl_vdcr import build_task_prompt, prediction_from_response
from scripts.score_vdcr_mcq import extract_choice, score_rows
from scripts.validate_vdcr_direct_answer import validate_dataset_constraints


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def direct_answer_rows() -> list[dict]:
    return [
        {
            "video_id": "vdcr_000001",
            "domain": "biology",
            "subdomain": "cell",
            "answer": "Endocytosis",
            "accepted_answers": ["胞吞作用"],
            "concept": {"en": "Endocytosis", "zh": "胞吞作用", "type": "mechanism"},
            "question": "Which named dynamic concept is instantiated by the temporally evolving process in this video?",
            "local_media": "media/a.mp4",
        },
        {
            "video_id": "vdcr_000002",
            "domain": "biology",
            "subdomain": "cell",
            "answer": "Exocytosis",
            "accepted_answers": ["胞吐作用"],
            "concept": {"en": "Exocytosis", "zh": "胞吐作用", "type": "mechanism"},
            "question": "Which named dynamic concept is instantiated by the temporally evolving process in this video?",
            "local_media": "media/b.mp4",
        },
        {
            "video_id": "vdcr_000003",
            "domain": "biology",
            "subdomain": "cell",
            "answer": "Mitosis",
            "accepted_answers": ["有丝分裂"],
            "concept": {"en": "Mitosis", "zh": "有丝分裂", "type": "mechanism"},
            "question": "Which named dynamic concept is instantiated by the temporally evolving process in this video?",
            "local_media": "media/c.mp4",
        },
        {
            "video_id": "vdcr_000004",
            "domain": "physics",
            "subdomain": "waves",
            "answer": "Rayleigh-Plateau Instability",
            "accepted_answers": ["瑞利-普拉托不稳定性"],
            "concept": {"en": "Rayleigh-Plateau Instability", "zh": "瑞利-普拉托不稳定性", "type": "mechanism"},
            "question": "Which named dynamic concept is instantiated by the temporally evolving process in this video?",
            "local_media": "media/d.mp4",
        },
    ]


def test_build_mcq_rows_prefers_same_domain_distractors_and_is_reproducible() -> None:
    rows = direct_answer_rows()

    first = build_mcq_rows(rows, seed=7)
    second = build_mcq_rows(rows, seed=7)

    assert first == second
    assert len(first) == 4
    item = first[0]
    assert set(item["choices"]) == {"A", "B", "C", "D"}
    assert item["choices"][item["answer"]] == "Endocytosis"
    distractors = [text for label, text in item["choices"].items() if label != item["answer"]]
    assert "胞吞作用" not in distractors
    assert {"Exocytosis", "Mitosis"}.issubset(set(distractors))
    assert item["mcq_metadata"]["distractor_source_video_ids"][:2] == ["vdcr_000002", "vdcr_000003"]


def test_build_mcq_rows_rejects_dataset_without_three_distractors() -> None:
    with pytest.raises(ValueError, match="needs at least 3 distractors"):
        build_mcq_rows(direct_answer_rows()[:3], seed=1)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("B", "B"),
        ("Answer: c because the vesicles fuse", "C"),
        ('{"answer": "d"}', "D"),
        ("I cannot tell", ""),
    ],
)
def test_extract_choice(text: str, expected: str) -> None:
    assert extract_choice(text) == expected


def test_score_rows_scores_predictions_and_reports_invalid_outputs() -> None:
    gold = build_mcq_rows(direct_answer_rows(), seed=7)
    predictions = [
        {"video_id": gold[0]["video_id"], "raw_response": f"Answer: {gold[0]['answer']}"},
        {"video_id": gold[1]["video_id"], "predicted_answer": "A"},
        {"video_id": gold[2]["video_id"], "raw_response": "not sure"},
    ]

    scored, summary = score_rows(gold, predictions)

    assert len(scored) == 3
    assert summary["total"] == 3
    assert summary["invalid"] == 1
    assert summary["correct"] == 1
    assert scored[0]["correct"] is True
    assert scored[2]["parse_status"] == "invalid"


def test_build_summary_rows_combines_exact_semantic_and_mcq_reports(tmp_path: Path) -> None:
    exact = tmp_path / "exact.md"
    semantic = tmp_path / "semantic.md"
    mcq = tmp_path / "mcq.md"
    exact.write_text("- accuracy: 2/4 (50.0%)\n", encoding="utf-8")
    semantic.write_text("- semantic accuracy: 3/4 (75.0%)\n", encoding="utf-8")
    mcq.write_text("- accuracy: 4/4 (100.0%)\n", encoding="utf-8")

    rows = build_summary_rows(
        [
            {
                "run": "qwen3vl_2b",
                "params_b": 2.0,
                "direct_exact": exact,
                "direct_semantic": semantic,
                "mcq": mcq,
            }
        ]
    )

    assert rows == [
        {
            "run": "qwen3vl_2b",
            "params_b": 2.0,
            "direct_exact_accuracy": 0.5,
            "direct_semantic_accuracy": 0.75,
            "mcq_accuracy": 1.0,
            "direct_exact_correct": 2,
            "direct_semantic_correct": 3,
            "mcq_correct": 4,
            "total": 4,
        }
    ]


def test_transformers_runner_builds_per_row_mcq_prompt_and_extracts_letter() -> None:
    row = build_mcq_rows(direct_answer_rows(), seed=7)[0]

    prompt = build_task_prompt(row, task="mcq", default_prompt="unused")

    assert "A." in prompt
    assert "Return only the single best option letter" in prompt
    assert row["choices"]["A"] in prompt
    assert prediction_from_response("Answer: b", task="mcq") == "B"
    assert prediction_from_response("Endocytosis", task="direct") == "Endocytosis"


def test_v2_validation_allows_bounded_repeated_concepts() -> None:
    rows = [
        {"video_id": "vdcr_v2_000001", "answer": "Capillary Rise / Wicking", "domain": "physics_physical_systems"},
        {"video_id": "vdcr_v2_000002", "answer": "Capillary Rise / Wicking", "domain": "physics_physical_systems"},
        {"video_id": "vdcr_v2_000003", "answer": "Phototropism", "domain": "biology_living_systems"},
        {"video_id": "vdcr_v2_000004", "answer": "Iodine Clock Reaction", "domain": "chemistry_materials_change"},
        {"video_id": "vdcr_v2_000005", "answer": "Tidal Bore", "domain": "earth_environmental_systems"},
    ]

    default_errors = validate_dataset_constraints(
        rows,
        min_samples=1,
        max_domain_imbalance=-1,
        allow_duplicate_answers=False,
        max_videos_per_answer=0,
    )
    assert any("answer values must be concept-level unique" in error for error in default_errors)

    v2_errors = validate_dataset_constraints(
        rows,
        min_samples=1,
        max_domain_imbalance=-1,
        allow_duplicate_answers=True,
        max_videos_per_answer=3,
    )
    assert v2_errors == []

    capped_errors = validate_dataset_constraints(
        rows,
        min_samples=1,
        max_domain_imbalance=-1,
        allow_duplicate_answers=True,
        max_videos_per_answer=1,
    )
    assert any("concept cluster exceeds 1 videos" in error for error in capped_errors)


def test_build_v2_assets_prioritizes_domain_gaps_and_caps_clusters() -> None:
    v1_samples = [
        {"video_id": "vdcr_000001", "answer": "Phototropism", "domain": "biology_living_systems", "source_url": "https://example.test/v1-a"},
        {"video_id": "vdcr_000002", "answer": "Phototropism", "domain": "biology_living_systems", "source_url": "https://example.test/v1-b"},
        {"video_id": "vdcr_000003", "answer": "Tidal Bore", "domain": "earth_environmental_systems", "source_url": "https://example.test/v1-c"},
    ]
    candidates = [
        {
            "candidate_id": "c1",
            "source_url": "https://example.test/new-physics",
            "source_platform": "internet_archive",
            "license_or_usage_note": "ok",
            "raw_duration_sec": "12",
            "suggested_start_sec": "0",
            "suggested_end_sec": "12",
            "initial_category": "physics_physical_systems",
            "candidate_knowledge_point": "Capillary Rise / Wicking",
            "domain_seed": "physics_physical_systems",
            "subdomain_seed": "physics_family_01",
            "why_dynamic": "visible rise",
            "collector_notes": "title=Capillary Rise Wicking demonstration; description=water wicking upward through paper; priority=A",
            "source_csv": "runs/v2_retrieval/unit/archive_candidates.csv",
        },
        {
            "candidate_id": "c2",
            "source_url": "https://example.test/third-photo",
            "source_platform": "internet_archive",
            "license_or_usage_note": "ok",
            "raw_duration_sec": "12",
            "suggested_start_sec": "0",
            "suggested_end_sec": "12",
            "initial_category": "biology_living_systems",
            "candidate_knowledge_point": "Phototropism",
            "domain_seed": "biology_living_systems",
            "subdomain_seed": "biology_family_01",
            "why_dynamic": "visible bending",
            "collector_notes": "title=Phototropism time lapse; description=plant bends toward light; priority=A",
            "source_csv": "runs/v2_retrieval/unit/archive_candidates.csv",
        },
        {
            "candidate_id": "c3",
            "source_url": "https://example.test/fourth-photo",
            "source_platform": "internet_archive",
            "license_or_usage_note": "ok",
            "raw_duration_sec": "12",
            "suggested_start_sec": "0",
            "suggested_end_sec": "12",
            "initial_category": "biology_living_systems",
            "candidate_knowledge_point": "Phototropism",
            "domain_seed": "biology_living_systems",
            "subdomain_seed": "biology_family_01",
            "why_dynamic": "visible bending",
            "collector_notes": "title=Phototropism second angle; description=seedling bends toward light; priority=A",
            "source_csv": "runs/v2_retrieval/unit/archive_candidates.csv",
        },
        {
            "candidate_id": "c4",
            "source_url": "https://example.test/action",
            "source_platform": "internet_archive",
            "license_or_usage_note": "ok",
            "raw_duration_sec": "12",
            "suggested_start_sec": "0",
            "suggested_end_sec": "12",
            "initial_category": "physics_physical_systems",
            "candidate_knowledge_point": "Rabona",
            "domain_seed": "physics_physical_systems",
            "subdomain_seed": "physics_family_99",
            "why_dynamic": "visible kick",
            "collector_notes": "title=Rabona kick; description=soccer kick; priority=A",
            "source_csv": "runs/v2_retrieval/unit/archive_candidates.csv",
        },
    ]
    concepts = {
        "Phototropism": {"concept_id": "vdcr_concept_1", "domain": "biology_living_systems", "subdomain": "biology_family_01", "priority": "A"},
        "Capillary Rise / Wicking": {"concept_id": "vdcr_concept_2", "domain": "physics_physical_systems", "subdomain": "physics_family_01", "priority": "A"},
        "Rabona": {"concept_id": "vdcr_concept_3", "domain": "physics_physical_systems", "subdomain": "physics_family_99", "priority": "A", "concept_type": "专有动态动作概念"},
    }

    assets = build_v2_assets(
        v1_samples=v1_samples,
        candidate_rows=candidates,
        concept_by_answer=concepts,
        reviewed_status_by_id={"c2": "pass_candidate", "c3": "pass_candidate"},
        target_per_domain=2,
        max_videos_per_concept=3,
        queue_limit=10,
        release_video_ids={"vdcr_000001", "vdcr_000002", "vdcr_000003"},
        include_action_concepts=False,
    )

    assert [row["candidate_id"] for row in assets.review_queue] == ["c1", "c2"]
    assert assets.review_queue[0]["domain_target_gap"] == "2"
    assert assets.review_queue[1]["repeat_concept_rank"] == "3"
    assert assets.stats["seed_samples"] == 3
    assert assets.stats["review_queue_rows"] == 2


def test_build_v2_assets_filters_archive_query_term_false_positives() -> None:
    candidates = [
        {
            "candidate_id": "bad_magnus",
            "source_url": "https://archive.org/details/patient-zero",
            "source_platform": "internet_archive",
            "license_or_usage_note": "ok",
            "raw_duration_sec": "120",
            "suggested_start_sec": "0",
            "suggested_end_sec": "30",
            "initial_category": "physics_physical_systems",
            "candidate_knowledge_point": "Magnus Effect",
            "domain_seed": "physics_physical_systems",
            "subdomain_seed": "physics_family_01",
            "why_dynamic": "visible curve",
            "collector_notes": "archive_search_collected; search_term=Magnus Effect; title=Patient Zero; description=Dr. Magnus has developed a drug whose effect lasts 20 minutes.",
            "source_csv": "runs/v2_retrieval/unit/archive_candidates.csv",
        },
        {
            "candidate_id": "good_magnus",
            "source_url": "https://archive.org/details/magnus-demo",
            "source_platform": "internet_archive",
            "license_or_usage_note": "ok",
            "raw_duration_sec": "30",
            "suggested_start_sec": "0",
            "suggested_end_sec": "30",
            "initial_category": "physics_physical_systems",
            "candidate_knowledge_point": "Magnus Effect",
            "domain_seed": "physics_physical_systems",
            "subdomain_seed": "physics_family_01",
            "why_dynamic": "visible curve",
            "collector_notes": "archive_search_collected; search_term=Magnus Effect; title=Magnus Effect demonstration; description=spinning ball curves in airflow.",
            "source_csv": "runs/v2_retrieval/unit/archive_candidates.csv",
        },
    ]
    concepts = {
        "Magnus Effect": {
            "concept_id": "vdcr_concept_0001",
            "domain": "physics_physical_systems",
            "subdomain": "physics_family_01",
            "priority": "B",
            "concept_type": "自然动态机制",
        }
    }

    assets = build_v2_assets(
        v1_samples=[],
        candidate_rows=candidates,
        concept_by_answer=concepts,
        reviewed_status_by_id={},
        target_per_domain=60,
        max_videos_per_concept=3,
        queue_limit=10,
    )

    assert [row["candidate_id"] for row in assets.review_queue] == ["good_magnus"]


def test_build_concept_map_includes_recommended_answer_names() -> None:
    rows = [
        {
            "concept_id": "vdcr_concept_0011",
            "concept_en": "Droplet Coalescence",
            "concept_zh": "液滴并合",
            "recommended_answer_en": "Capillary-Driven Droplet Coalescence",
            "recommended_answer_zh": "毛细驱动液滴并合",
            "accepted_answers_json": '["droplet merging"]',
        }
    ]

    mapped = build_concept_map(rows)

    assert mapped["capillary-driven droplet coalescence"]["concept_id"] == "vdcr_concept_0011"
    assert mapped["毛细驱动液滴并合"]["concept_id"] == "vdcr_concept_0011"


def test_build_gap_queries_prioritizes_undercovered_chemistry_concepts() -> None:
    concepts = [
        {
            "concept_id": "c1",
            "domain": "chemistry_materials_change",
            "subdomain": "chemistry_family_01",
            "concept_en": "Iodine Clock Reaction",
            "concept_zh": "碘钟反应",
            "priority": "A",
            "video_availability_guess": "high",
            "concept_type": "自然动态机制",
        },
        {
            "concept_id": "c2",
            "domain": "chemistry_materials_change",
            "subdomain": "chemistry_family_02",
            "concept_en": "Spinodal Decomposition",
            "concept_zh": "旋节线分解",
            "priority": "A",
            "video_availability_guess": "medium",
            "concept_type": "自然动态机制",
        },
        {
            "concept_id": "c3",
            "domain": "physics_physical_systems",
            "subdomain": "physics_family_01",
            "concept_en": "Vortex Shedding",
            "concept_zh": "涡脱落",
            "priority": "A",
            "video_availability_guess": "high",
            "concept_type": "自然动态机制",
        },
    ]
    candidates = [
        {"candidate_knowledge_point": "Iodine Clock Reaction"},
        {"candidate_knowledge_point": "Iodine Clock Reaction"},
    ]

    rows = build_gap_queries(concepts, candidates, domain="chemistry_materials_change", target_candidates_per_concept=3)

    assert [row["candidate_knowledge_point"] for row in rows[:4]] == ["Spinodal Decomposition"] * 4
    assert {row["search_term"] for row in rows[:4]} == {
        "Spinodal Decomposition",
        "Spinodal Decomposition demonstration",
        "Spinodal Decomposition experiment video",
        "旋节线分解 Spinodal Decomposition",
    }
    assert all(row["initial_category"] == "chemistry_materials_change" for row in rows)
    assert all(row["candidate_knowledge_point"] != "Vortex Shedding" for row in rows)


def test_build_expansion_backlog_prioritizes_main_eligible_undercovered_concepts() -> None:
    concepts = [
        {
            "concept_id": "c1",
            "domain": "physics_physical_systems",
            "subdomain": "physics_family_01",
            "concept_en": "Capillary Rise / Wicking",
            "concept_zh": "毛细上升/芯吸",
            "priority": "A",
            "video_availability_guess": "high",
            "concept_type": "自然动态机制",
            "concept_validity_tier": "core_main",
            "production_gate": "must show liquid front rising",
        },
        {
            "concept_id": "c2",
            "domain": "chemistry_materials_change",
            "subdomain": "chemistry_family_01",
            "concept_en": "Iodine Clock Reaction",
            "concept_zh": "碘钟反应",
            "priority": "A",
            "video_availability_guess": "high",
            "concept_type": "实验动态图样",
            "concept_validity_tier": "strict_main_candidate",
            "production_gate": "must show delayed color change",
        },
        {
            "concept_id": "c3",
            "domain": "biology_living_systems",
            "subdomain": "biology_family_01",
            "concept_en": "Rabona",
            "concept_zh": "拉波纳",
            "priority": "A",
            "video_availability_guess": "high",
            "concept_type": "专有动态动作概念",
            "concept_validity_tier": "stress_slice",
            "production_gate": "action",
        },
    ]
    seed_samples = [
        {"answer": "Iodine Clock Reaction", "domain": "chemistry_materials_change"},
    ]
    candidates = [
        {"candidate_knowledge_point": "Iodine Clock Reaction"},
        {"candidate_knowledge_point": "Iodine Clock Reaction"},
    ]
    review_queue = [
        {"candidate_knowledge_point": "Iodine Clock Reaction"},
    ]

    rows = build_expansion_backlog(
        concepts=concepts,
        seed_samples=seed_samples,
        candidates=candidates,
        review_queue=review_queue,
        target_candidates_per_concept=3,
    )

    assert [row["concept_en"] for row in rows] == ["Capillary Rise / Wicking", "Iodine Clock Reaction"]
    assert rows[0]["expansion_role"] == "new_concept"
    assert rows[0]["needed_candidates"] == "3"
    assert rows[1]["expansion_role"] == "repeat_concept"
    assert rows[1]["current_candidates"] == "2"
    assert rows[1]["current_review_queue"] == "1"


def test_build_backlog_queries_emits_gate_aware_query_forms() -> None:
    backlog_rows = [
        {
            "concept_id": "c1",
            "domain": "physics_physical_systems",
            "subdomain": "physics_family_01",
            "concept_en": "Capillary Rise / Wicking",
            "concept_zh": "毛细上升/芯吸",
            "priority": "A",
            "video_availability_guess": "high",
            "needed_candidates": "3",
            "production_gate": "must show liquid front rising",
        }
    ]

    rows = build_backlog_queries(backlog_rows, max_concepts=1)

    assert [row["search_term"] for row in rows] == [
        "Capillary Rise / Wicking",
        "Capillary Rise / Wicking demonstration",
        "Capillary Rise / Wicking experiment video",
        "毛细上升/芯吸 Capillary Rise / Wicking",
    ]
    assert all(row["candidate_knowledge_point"] == "Capillary Rise / Wicking" for row in rows)
    assert "must show liquid front rising" in rows[0]["notes"]


def test_build_backlog_queries_round_robins_domains() -> None:
    backlog_rows = [
        {
            "concept_id": "bio",
            "domain": "biology_living_systems",
            "subdomain": "biology_family_01",
            "concept_en": "Phototropism",
            "concept_zh": "向光性",
            "priority": "A",
            "needed_candidates": "3",
        },
        {
            "concept_id": "bio2",
            "domain": "biology_living_systems",
            "subdomain": "biology_family_02",
            "concept_en": "Hydrotropism",
            "concept_zh": "向水性",
            "priority": "B",
            "needed_candidates": "3",
        },
        {
            "concept_id": "chem",
            "domain": "chemistry_materials_change",
            "subdomain": "chemistry_family_01",
            "concept_en": "Iodine Clock Reaction",
            "concept_zh": "碘钟反应",
            "priority": "A",
            "needed_candidates": "3",
        },
        {
            "concept_id": "earth",
            "domain": "earth_environmental_systems",
            "subdomain": "earth_family_01",
            "concept_en": "Tidal Bore",
            "concept_zh": "涌潮",
            "priority": "A",
            "needed_candidates": "3",
        },
        {
            "concept_id": "phys",
            "domain": "physics_physical_systems",
            "subdomain": "physics_family_01",
            "concept_en": "Vortex Shedding",
            "concept_zh": "涡脱落",
            "priority": "A",
            "needed_candidates": "3",
        },
    ]

    rows = build_backlog_queries(backlog_rows, max_concepts=4)

    assert [row["domain_seed"] for row in rows[::4]] == [
        "biology_living_systems",
        "chemistry_materials_change",
        "earth_environmental_systems",
        "physics_physical_systems",
    ]


def test_build_triage_rows_keeps_only_local_reviewable_candidates() -> None:
    review_rows = [
        {
            "candidate_id": "curated_003002",
            "candidate_knowledge_point": "Phototropism",
            "domain_seed": "biology_living_systems",
            "local_media": "media/photo.ogv",
            "contact_sheet": "reports/photo.jpg",
            "review_notes": "visible bending",
        },
        {
            "candidate_id": "remote_only",
            "candidate_knowledge_point": "Tidal Bore",
            "domain_seed": "earth_environmental_systems",
            "local_media": "",
            "contact_sheet": "",
            "review_notes": "remote source only",
        },
    ]

    rows = build_triage_rows(review_rows)

    assert [row["candidate_id"] for row in rows] == ["curated_003002"]
    assert rows[0]["triage_status"] == "ready_for_manual_review"
    assert rows[0]["reviewer_decision"] == ""
    assert rows[0]["visual_gate_focus"] == "visible bending"


def test_build_triage_rows_preserves_existing_reviewer_decisions() -> None:
    review_rows = [
        {
            "candidate_id": "curated_003002",
            "candidate_knowledge_point": "Phototropism",
            "domain_seed": "biology_living_systems",
            "local_media": "media/photo.ogv",
            "contact_sheet": "reports/photo.jpg",
            "review_notes": "visible bending",
        }
    ]
    existing = {
        "curated_003002": {
            "reviewer_decision": "pass_candidate",
            "reviewer_notes": "clear time-lapse bend",
        }
    }

    rows = build_triage_rows(review_rows, existing_decisions=existing)

    assert rows[0]["reviewer_decision"] == "pass_candidate"
    assert rows[0]["reviewer_notes"] == "clear time-lapse bend"


def test_decision_counts_tracks_blank_and_filled_triage_decisions() -> None:
    rows = [
        {"reviewer_decision": "pass_candidate"},
        {"reviewer_decision": "revise"},
        {"reviewer_decision": ""},
    ]

    counts = decision_counts(rows)

    assert counts["pass_candidate"] == 1
    assert counts["revise"] == 1
    assert counts["pending"] == 1


def test_apply_triage_decisions_updates_review_queue_status_and_notes() -> None:
    review_rows = [
        {
            "candidate_id": "curated_003002",
            "review_status": "review",
            "review_notes": "old gate",
            "recommended_action": "inspect_video",
        },
        {
            "candidate_id": "curated_003001",
            "review_status": "review",
            "review_notes": "old gate",
            "recommended_action": "inspect_video",
        },
    ]
    triage_rows = [
        {
            "candidate_id": "curated_003002",
            "reviewer_decision": "pass_candidate",
            "reviewer_notes": "clear bending sequence",
        },
        {
            "candidate_id": "curated_003001",
            "reviewer_decision": "revise",
            "reviewer_notes": "needs tighter segment",
        },
    ]

    updated = apply_triage_decisions(review_rows, triage_rows)

    assert updated[0]["review_status"] == "pass_candidate"
    assert updated[0]["recommended_action"] == "candidate_ready_for_v2_draft"
    assert "triage_decision=pass_candidate" in updated[0]["review_notes"]
    assert "clear bending sequence" in updated[0]["review_notes"]
    assert updated[1]["review_status"] == "revise"
    assert updated[1]["recommended_action"] == "revise_or_trim_before_draft"


def test_build_draft_samples_appends_source_hidden_pass_candidates() -> None:
    seed_rows = [
        {
            "video_id": "vdcr_000001",
            "split": "v2_seed",
            "domain": "biology_living_systems",
            "subdomain": "biology_family_04",
            "concept_id": "vdcr_concept_0143",
            "concept": {"en": "Phototropism", "zh": "向光性", "type": "自然动态机制", "validity_tier": "core_main"},
            "answer": "Phototropism",
            "accepted_answers": ["Phototropism", "向光性"],
            "local_media": "media/seed.mp4",
            "duration_sec": 10,
            "question": "Which named dynamic concept is instantiated by the temporally evolving process in this video?",
            "dynamic_evidence": [{"start_sec": 0, "end_sec": 10, "description": "seed evidence long enough"}],
            "static_insufficient_reason": "A single frame is insufficient because the named dynamic concept requires observing change over time.",
            "quality_gates": {
                "temporal_necessity": "pass",
                "domain_specificity": "pass",
                "mechanism_bearing_label": "pass",
                "expert_naming_gap": "pass",
                "text_or_audio_leakage": "pass",
                "single_frame_shortcut": "pass",
                "concept_validity_tier": "core_main",
            },
            "source_url": "https://example.test/seed",
        }
    ]
    review_rows = [
        {
            "candidate_id": "curated_003002",
            "candidate_knowledge_point": "Phototropism",
            "concept_id": "vdcr_concept_0143",
            "domain_seed": "biology_living_systems",
            "subdomain_seed": "biology_family_04",
            "review_status": "pass_candidate",
            "local_media": "media/photo.ogv",
            "suggested_start_sec": "0",
            "suggested_end_sec": "34",
            "review_notes": "Visible plant bending toward light over time, with no answer text in sparse frames.",
        }
    ]
    concepts = {
        "Phototropism": {
            "concept_id": "vdcr_concept_0143",
            "domain": "biology_living_systems",
            "subdomain": "biology_family_04",
            "concept_en": "Phototropism",
            "concept_zh": "向光性",
            "recommended_answer_en": "",
            "recommended_answer_zh": "",
            "concept_type": "自然动态机制",
            "concept_validity_tier": "core_main",
            "accepted_answers_json": '["Phototropism","向光性"]',
            "production_gate": "must show bending",
        }
    }
    frame_status = {"curated_003002": {"duration_sec": "33.5"}}

    rows = build_draft_samples(seed_rows, review_rows, concepts, frame_status)

    assert len(rows) == 2
    added = rows[1]
    assert added["video_id"] == "vdcr_v2_000001"
    assert added["split"] == "v2_draft"
    assert added["answer"] == "Phototropism"
    assert "source_url" not in added
    assert added["quality_gates"]["text_or_audio_leakage"] == "pass"
    assert added["duration_sec"] == 33.5


def test_discover_local_v2_candidate_paths_excludes_combined_output(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    curated = data / "vdcr_candidate_videos_curated_chemistry_v2.csv"
    combined = data / "vdcr_candidate_videos_combined_v2.csv"
    unrelated = data / "vdcr_candidate_videos_archive_batch02_v1.csv"
    curated.write_text("candidate_id,source_url\n", encoding="utf-8")
    combined.write_text("candidate_id,source_url\n", encoding="utf-8")
    unrelated.write_text("candidate_id,source_url\n", encoding="utf-8")

    assert discover_local_v2_candidate_paths(tmp_path) == [curated]


def test_discover_review_assets_uses_download_status_and_sparse_sheet(tmp_path: Path) -> None:
    data = tmp_path / "data"
    reports = tmp_path / "reports" / "vdcr_v2_curated_chemistry_sparse_sheets"
    data.mkdir()
    reports.mkdir(parents=True)
    status = data / "vdcr_v2_curated_chemistry_download_status.csv"
    status.write_text(
        "id,ok,status,error,direct_url,local_media\n"
        "curated_002001,true,download_ok,,https://example.test/a,media/a.webm\n",
        encoding="utf-8",
    )
    sheet = reports / "curated_002001_sparse.jpg"
    sheet.write_text("fake", encoding="utf-8")

    assets = discover_review_assets(tmp_path)

    assert assets["curated_002001"] == {
        "local_media": "media/a.webm",
        "contact_sheet": str(sheet),
    }


def test_build_segment_manifest_rows_cuts_only_valid_revise_rows(tmp_path: Path) -> None:
    source = tmp_path / "source.webm"
    source.write_bytes(b"video")
    output_dir = tmp_path / "segments"
    calls = []

    def fake_cut(src: Path, out: Path, start: float, end: float) -> None:
        calls.append((src, out, start, end))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"segment")

    review_rows = [
        {
            "id": "curated_002004",
            "candidate_knowledge_point": "Blue Bottle Reaction",
            "review_status": "revise",
            "suggested_start_sec": "5",
            "suggested_end_sec": "42.5",
            "local_media": str(source),
        },
        {
            "id": "not_revise",
            "candidate_knowledge_point": "Iodine Clock Reaction",
            "review_status": "review",
            "suggested_start_sec": "0",
            "suggested_end_sec": "10",
            "local_media": str(source),
        },
        {
            "id": "bad_time",
            "candidate_knowledge_point": "Chemical Garden Growth",
            "review_status": "revise",
            "suggested_start_sec": "10",
            "suggested_end_sec": "10",
            "local_media": str(source),
        },
    ]
    media_rows = [
        {
            "id": "curated_002004",
            "direct_url": "https://example.test/blue.webm",
            "page_url": "https://example.test/page",
            "title": "Blue-bottle reaction",
            "mime": "video/webm",
        }
    ]

    rows = build_segment_manifest_rows(review_rows, media_rows, output_dir, cut_segment=fake_cut)

    assert [row["id"] for row in rows] == ["curated_002004_seg_005000_042500"]
    assert rows[0]["source_id"] == "curated_002004"
    assert rows[0]["candidate_knowledge_point"] == "Blue Bottle Reaction"
    assert rows[0]["duration_sec"] == "37.500"
    assert rows[0]["direct_url"] == "https://example.test/blue.webm"
    assert rows[0]["local_media"].endswith("curated_002004_seg_005000_042500.webm")
    assert calls == [
        (source, output_dir / "curated_002004_seg_005000_042500.webm", 5.0, 42.5),
    ]


def test_strip_trailing_whitespace_preserves_line_structure() -> None:
    assert strip_trailing_whitespace("a  \n  \nb\t \n") == "a\n\nb\n"
