# VDCR Dual-Mode Evaluation Summary

| run | params_b | total | direct_exact | direct_llm_judge | mcq |
|---|---:|---:|---:|---:|---:|
| qwen35_2b | 2 | 114 | 0/114 (0.0%) | 0/114 (0.0%) | 60/114 (52.6%) |
| qwen35_4b | 4 | 114 | 2/114 (1.8%) | 1/114 (0.9%) | 65/114 (57.0%) |
| qwen35_9b | 9 | 114 | 1/114 (0.9%) | 1/114 (0.9%) | 71/114 (62.3%) |

## Notes

- `direct_exact` uses alias-normalized exact matching.
- `direct_llm_judge` uses an LLM judge against the reference answer and accepted aliases.
- `mcq` uses constructed four-choice items with hard negatives derived from the direct-answer reference set.
