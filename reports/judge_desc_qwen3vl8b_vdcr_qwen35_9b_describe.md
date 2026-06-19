# VDCR Description-Understanding Judge Score

- predictions: `runs/vdcr_qwen35_9b_describe_frames_fps1.jsonl`
- judge_model: `Qwen/Qwen3-VL-8B-Instruct`
- predictions judged: 114
- description understanding accuracy: 16/114 (14.0%)

## Labels

- `partial_generic`: 39/114 (34.2%)
- `related_but_wrong`: 3/114 (2.6%)
- `unclear`: 0/114 (0.0%)
- `understands_mechanism`: 16/114 (14.0%)
- `wrong`: 56/114 (49.1%)

## Accuracy By Domain

- `biology_living_systems`: 5/29 (17.2%)
- `chemistry_materials_change`: 5/29 (17.2%)
- `earth_environmental_systems`: 4/28 (14.3%)
- `physics_physical_systems`: 2/28 (7.1%)

## Accuracy By Concept Type

- `专有动态动作概念`: 0/1 (0.0%)
- `实验动态图样`: 4/10 (40.0%)
- `生态行为策略`: 1/2 (50.0%)
- `自然动态机制`: 11/101 (10.9%)
