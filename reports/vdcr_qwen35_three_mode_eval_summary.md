# VDCR Three-Mode Evaluation Summary

| run | params_b | total | open exact naming | open description judge | MCQ recognition |
|---|---:|---:|---:|---:|---:|
| qwen35_2b | 2 | 114 | 0/114 (0.0%) | 17/114 (14.9%) | 60/114 (52.6%) |
| qwen35_4b | 4 | 114 | 2/114 (1.8%) | 17/114 (14.9%) | 65/114 (57.0%) |
| qwen35_9b | 9 | 114 | 1/114 (0.9%) | 16/114 (14.0%) | 71/114 (62.3%) |

## Metric Definitions

- `open exact naming`: open-ended answer must match the canonical concept name or accepted aliases after normalization.
- `open description judge`: open-ended response may be a short mechanism description; an LLM judge gives credit only if the response distinguishes the gold dynamic mechanism, not merely a broad caption.
- `MCQ recognition`: four-choice constructed item scored by selected option letter only.

## Notes

- Qwen/Qwen3.5-30B does not exist on Hugging Face; 30B video run uses Qwen/Qwen3-VL-30B-A3B-Instruct when available.
