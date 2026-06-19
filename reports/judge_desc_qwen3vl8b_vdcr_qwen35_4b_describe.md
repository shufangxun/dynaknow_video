# VDCR Description-Understanding Judge Score

- predictions: `runs/vdcr_qwen35_4b_describe_frames_fps1.jsonl`
- judge_model: `Qwen/Qwen3-VL-8B-Instruct`
- predictions judged: 114
- description understanding accuracy: 17/114 (14.9%)

## Labels

- `partial_generic`: 30/114 (26.3%)
- `related_but_wrong`: 1/114 (0.9%)
- `unclear`: 0/114 (0.0%)
- `understands_mechanism`: 17/114 (14.9%)
- `wrong`: 66/114 (57.9%)

## Accuracy By Domain

- `biology_living_systems`: 6/29 (20.7%)
- `chemistry_materials_change`: 6/29 (20.7%)
- `earth_environmental_systems`: 3/28 (10.7%)
- `physics_physical_systems`: 2/28 (7.1%)

## Accuracy By Concept Type

- `专有动态动作概念`: 0/1 (0.0%)
- `实验动态图样`: 4/10 (40.0%)
- `生态行为策略`: 0/2 (0.0%)
- `自然动态机制`: 13/101 (12.9%)
