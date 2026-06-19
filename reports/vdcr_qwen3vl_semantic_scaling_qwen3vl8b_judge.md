# VDCR Semantic-Judge Scaling Summary

| run | params_b | correct | total | semantic_accuracy | semantic_error_rate |
|---|---:|---:|---:|---:|---:|
| qwen3vl_2b | 2 | 0 | 114 | 0.0% | 100.0% |
| qwen3vl_4b | 4 | 3 | 114 | 2.6% | 97.4% |
| qwen3vl_8b | 8 | 1 | 114 | 0.9% | 99.1% |

## Two-Point Error Scaling

- slope from `qwen3vl_2b` to `qwen3vl_8b`: `-0.006` for semantic_error_rate vs params_b
- relative semantic error change: `-0.9%`

## Accuracy By Domain

| run | biology_living_systems | chemistry_materials_change | earth_environmental_systems | physics_physical_systems |
|---|---:|---:|---:|---:|
| qwen3vl_2b | 0.0% | 0.0% | 0.0% | 0.0% |
| qwen3vl_4b | 0.0% | 0.0% | 7.1% | 3.6% |
| qwen3vl_8b | 0.0% | 0.0% | 0.0% | 3.6% |
