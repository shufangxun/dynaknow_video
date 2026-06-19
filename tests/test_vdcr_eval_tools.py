import json
from pathlib import Path

import pytest

from scripts.build_vdcr_mcq_from_direct_answer import build_mcq_rows
from scripts.report_vdcr_dual_eval import build_summary_rows
from scripts.run_qwen3_vl_vdcr import build_task_prompt, prediction_from_response
from scripts.score_vdcr_mcq import extract_choice, score_rows


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
