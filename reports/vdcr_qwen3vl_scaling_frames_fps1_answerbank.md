# VDCR Scaling Summary

| run | params_b | correct | total | accuracy | error_rate |
|---|---:|---:|---:|---:|---:|
| qwen3vl_2b | 2 | 23 | 114 | 20.2% | 79.8% |
| qwen3vl_4b | 4 | 30 | 114 | 26.3% | 73.7% |
| qwen3vl_8b | 8 | 32 | 114 | 28.1% | 71.9% |

## Two-Point Error Scaling

- slope from `qwen3vl_2b` to `qwen3vl_8b`: `-0.075` for error_rate vs params_b
- relative error change: `-9.9%`

## Accuracy By Domain

| run | biology_living_systems | chemistry_materials_change | earth_environmental_systems | physics_physical_systems |
|---|---:|---:|---:|---:|
| qwen3vl_2b | 17.2% | 20.7% | 25.0% | 17.9% |
| qwen3vl_4b | 31.0% | 20.7% | 28.6% | 25.0% |
| qwen3vl_8b | 31.0% | 10.3% | 39.3% | 32.1% |
