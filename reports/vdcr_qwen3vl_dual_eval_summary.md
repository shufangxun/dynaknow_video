# VDCR Dual-Mode Evaluation Summary

| run | params_b | total | direct_exact | direct_llm_judge | mcq |
|---|---:|---:|---:|---:|---:|
| qwen3vl_2b | 2 | 114 | 0/114 (0.0%) | 0/114 (0.0%) | 60/114 (52.6%) |
| qwen3vl_4b | 4 | 114 | 1/114 (0.9%) | 3/114 (2.6%) | 72/114 (63.2%) |
| qwen3vl_8b | 8 | 114 | 0/114 (0.0%) | 1/114 (0.9%) | 74/114 (64.9%) |

## Notes

- `direct_exact` uses alias-normalized exact matching.
- `direct_llm_judge` uses an LLM judge against the reference answer and accepted aliases.
- `mcq` uses constructed four-choice items with hard negatives derived from the direct-answer reference set.
