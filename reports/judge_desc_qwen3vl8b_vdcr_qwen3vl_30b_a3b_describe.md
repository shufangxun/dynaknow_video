# VDCR Description-Understanding Judge Score

- predictions: `runs/vdcr_qwen3vl_30b_a3b_describe_frames_fps1.jsonl`
- judge_model: `Qwen/Qwen3-VL-8B-Instruct`
- predictions judged: 114
- description understanding accuracy: 33/114 (28.9%)

## Labels

- `partial_generic`: 23/114 (20.2%)
- `related_but_wrong`: 1/114 (0.9%)
- `unclear`: 0/114 (0.0%)
- `understands_mechanism`: 33/114 (28.9%)
- `wrong`: 57/114 (50.0%)

## Accuracy By Domain

- `biology_living_systems`: 9/29 (31.0%)
- `chemistry_materials_change`: 6/29 (20.7%)
- `earth_environmental_systems`: 8/28 (28.6%)
- `physics_physical_systems`: 10/28 (35.7%)

## Accuracy By Concept Type

- `专有动态动作概念`: 0/1 (0.0%)
- `实验动态图样`: 3/10 (30.0%)
- `生态行为策略`: 2/2 (100.0%)
- `自然动态机制`: 28/101 (27.7%)
