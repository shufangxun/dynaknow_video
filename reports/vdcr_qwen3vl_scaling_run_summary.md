# VDCR Qwen3-VL Scaling Run

- dataset: `release/v1/dataset_v1.jsonl` (114 VDCR v1 samples)
- visual input: ffmpeg-extracted frame-list video, `fps=1.0`, shared cache `runs/qwen3vl_frame_cache_fps1`
- frame extraction coverage: 114/114 videos, no model-run errors or empty predictions in final runs
- scorer: `scripts/score_vdcr_direct_answer.py` alias-normalized exact match against `answer` and `accepted_answers`

## Open-vocab direct answer

Strict alias exact-match on free-form model output.

| model | params_b | correct | total | accuracy |
|---|---:|---:|---:|---:|
| qwen3vl_2b | 2 | 0 | 114 | 0.0% |
| qwen3vl_4b | 4 | 1 | 114 | 0.9% |
| qwen3vl_8b | 8 | 0 | 114 | 0.0% |

| model | biology | chemistry/materials | earth/environment | physics |
|---|---:|---:|---:|---:|
| qwen3vl_2b | 0/29 (0.0%) | 0/29 (0.0%) | 0/28 (0.0%) | 0/28 (0.0%) |
| qwen3vl_4b | 0/29 (0.0%) | 0/29 (0.0%) | 0/28 (0.0%) | 1/28 (3.6%) |
| qwen3vl_8b | 0/29 (0.0%) | 0/29 (0.0%) | 0/28 (0.0%) | 0/28 (0.0%) |

## Closed-vocab answer bank

Same scorer, but prompt includes all 114 candidate concept names.

| model | params_b | correct | total | accuracy |
|---|---:|---:|---:|---:|
| qwen3vl_2b | 2 | 23 | 114 | 20.2% |
| qwen3vl_4b | 4 | 30 | 114 | 26.3% |
| qwen3vl_8b | 8 | 32 | 114 | 28.1% |

| model | biology | chemistry/materials | earth/environment | physics |
|---|---:|---:|---:|---:|
| qwen3vl_2b | 5/29 (17.2%) | 6/29 (20.7%) | 7/28 (25.0%) | 5/28 (17.9%) |
| qwen3vl_4b | 9/29 (31.0%) | 6/29 (20.7%) | 8/28 (28.6%) | 7/28 (25.0%) |
| qwen3vl_8b | 9/29 (31.0%) | 3/29 (10.3%) | 11/28 (39.3%) | 9/28 (32.1%) |

## Interpretation Notes

- Open-vocab exact-match is mostly measuring whether the model emits the benchmark canonical concept name, so near-zero scores should not be read as pure visual failure.
- The answer-bank condition is a closed-set diagnostic over the same videos and gold scorer; it is better for quick scaling comparison, but it is easier than the released direct-answer task.
- The 2B to 8B answer-bank error rate changes from 79.8% to 71.9%, a relative error reduction of about 9.9%.
