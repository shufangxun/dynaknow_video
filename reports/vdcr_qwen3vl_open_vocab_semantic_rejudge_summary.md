# VDCR Qwen3-VL Open-Vocab Semantic Rejudge

- dataset: `release/v1/dataset_v1.jsonl` (114 VDCR v1 samples)
- predictions judged: open-vocab direct-answer outputs from `runs/vdcr_qwen3vl_*_frames_fps1.jsonl`
- visual input used for predictions: ffmpeg frame-list video at `fps=1.0`
- judge: local `Qwen/Qwen3-VL-8B-Instruct` text judge, deterministic decoding (`temperature=0.0`)
- rubric: exact aliases/translations/specific same mechanism are equivalent; broad parent terms and visual descriptions are not equivalent

## Main Results

| model | params_b | exact_match | semantic_judge | too_generic | related_but_wrong | wrong |
|---|---:|---:|---:|---:|---:|---:|
| qwen3vl_2b | 2 | 0/114 (0.0%) | 0/114 (0.0%) | 68 | 5 | 41 |
| qwen3vl_4b | 4 | 1/114 (0.9%) | 3/114 (2.6%) | 57 | 10 | 44 |
| qwen3vl_8b | 8 | 0/114 (0.0%) | 1/114 (0.9%) | 60 | 4 | 49 |

## Interpretation

- Semantic judging raises a few cases over exact match, but most open-vocab outputs remain broad labels rather than the benchmark concept name.
- The dominant failure mode is `too_generic`: models often answer with categories such as chemical reaction, fire, wave, surface tension, cell division, or storm instead of the named mechanism.
- The semantic judge used here is local Qwen3-VL-8B, not a stronger external judge. Treat this as a reproducible local pass; a final paper-quality number should be rerun with a stronger independent judge and sampled human audit.

## Related Artifacts

- semantic scaling: `reports/vdcr_qwen3vl_semantic_scaling_qwen3vl8b_judge.md`
- per-model judge JSONL: `reports/judge_qwen3vl8b_vdcr_qwen3vl_*_frames_fps1.jsonl`
- per-model judge reports: `reports/judge_qwen3vl8b_vdcr_qwen3vl_*_frames_fps1.md`
- judge script: `scripts/judge_vdcr_semantic_equivalence.py`
