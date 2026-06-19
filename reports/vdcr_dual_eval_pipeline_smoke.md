# VDCR Dual-Mode Evaluation Summary

| run | params_b | total | direct_exact | direct_llm_judge | mcq |
|---|---:|---:|---:|---:|---:|
| qwen3vl_2b | 2 | 114 | 0/114 (0.0%) | 0/114 (0.0%) | 114/114 (100.0%) |

## Notes

- `direct_exact` uses alias-normalized exact matching.
- `direct_llm_judge` uses an LLM judge against the reference answer and accepted aliases.
- `mcq` uses constructed four-choice items with hard negatives derived from the direct-answer reference set.
