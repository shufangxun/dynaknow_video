# VDCR Semantic-Judge Score

- predictions: `runs/vdcr_qwen35_9b_direct_frames_fps1.jsonl`
- judge_model: `Qwen/Qwen3-VL-8B-Instruct`
- predictions judged: 114
- semantic accuracy: 1/114 (0.9%)

## Labels

- `equivalent`: 1/114 (0.9%)
- `related_but_wrong`: 1/114 (0.9%)
- `too_generic`: 66/114 (57.9%)
- `unclear`: 2/114 (1.8%)
- `wrong`: 44/114 (38.6%)

## Accuracy By Domain

- `biology_living_systems`: 1/29 (3.4%)
- `chemistry_materials_change`: 0/29 (0.0%)
- `earth_environmental_systems`: 0/28 (0.0%)
- `physics_physical_systems`: 0/28 (0.0%)

## Accuracy By Concept Type

- `专有动态动作概念`: 0/1 (0.0%)
- `实验动态图样`: 0/10 (0.0%)
- `生态行为策略`: 1/2 (50.0%)
- `自然动态机制`: 0/101 (0.0%)
