import json
from pathlib import Path

import pytest

from scripts.build_vdcr_mcq_from_direct_answer import build_mcq_rows
from scripts.build_vdcr_v2_construction_assets import build_v2_assets
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
