# VDCR Description-Understanding Judge Score

- predictions: `runs/vdcr_qwen35_2b_describe_frames_fps1.jsonl`
- judge_model: `Qwen/Qwen3-VL-8B-Instruct`
- predictions judged: 114
- description understanding accuracy: 17/114 (14.9%)

## Labels

- `partial_generic`: 34/114 (29.8%)
- `related_but_wrong`: 0/114 (0.0%)
- `unclear`: 0/114 (0.0%)
- `understands_mechanism`: 17/114 (14.9%)
- `wrong`: 63/114 (55.3%)

## Accuracy By Domain

- `biology_living_systems`: 6/29 (20.7%)
- `chemistry_materials_change`: 3/29 (10.3%)
- `earth_environmental_systems`: 5/28 (17.9%)
- `physics_physical_systems`: 3/28 (10.7%)

## Accuracy By Concept Type

- `专有动态动作概念`: 0/1 (0.0%)
- `实验动态图样`: 2/10 (20.0%)
- `生态行为策略`: 2/2 (100.0%)
- `自然动态机制`: 13/101 (12.9%)
