# v0.5 Evaluation Harness Report

Date: 2026-06-01

## Purpose

This adds a local scoring harness for the v0.5 pilot release so model outputs can be evaluated consistently across full-video and shortcut settings.

## New Scripts

- `scripts/score_predictions.py`
- `scripts/make_baseline_predictions.py`
- `scripts/build_combined_gold.py`
- `scripts/normalize_model_outputs.py`
- `scripts/validate_predictions.py`

## Prediction Format

Each prediction is one JSON object:

```json
{"video_id":"dynaknow_000001","mode":"full_video","predicted_answer":"A"}
```

Supported modes:

- `full_video`
- `answer_only`
- `single_frame_first`
- `single_frame_middle`
- `single_frame_last`
- `sparse_frames_ordered`

## Release Gold

Combined gold file:

- `release/v0_5/combined_gold_v0_5_balanced.jsonl`

Counts:

- full-video rows: 8
- answer-only rows: 8
- frame-shortcut rows: 32
- total scoring rows: 48

## Smoke Test

Smoke-test prediction file:

- `release/v0_5/predictions_smoke_full_oracle_shortcut_always_a.jsonl`

Score report:

- `release/v0_5/score_smoke_full_oracle_shortcut_always_a.md`

Result:

- full-video oracle accuracy: 8/8
- answer-only always-A accuracy: 2/8
- single-frame first always-A accuracy: 2/8
- single-frame middle always-A accuracy: 2/8
- single-frame last always-A accuracy: 2/8
- sparse-frame always-A accuracy: 2/8
- Dynamic Necessity Gap: 0.750

This validates that answer-position balancing and Dynamic Necessity Gap scoring behave as expected.

## Model Output Normalization

Raw model responses can be converted into the scorer format with:

```bash
python /root/public/jasonshu/dynaknow_video/scripts/normalize_model_outputs.py \
  --input /path/to/raw_model_outputs.jsonl \
  --output /path/to/predictions.jsonl \
  --response-field response
```

Expected raw row shape:

```json
{"video_id":"dynaknow_000001","mode":"full_video","response":"Answer: A"}
```

The normalizer extracts `A`, `B`, `C`, or `D` from common response forms and writes:

```json
{"video_id":"dynaknow_000001","mode":"full_video","predicted_answer":"A"}
```

Before scoring, run:

```bash
python /root/public/jasonshu/dynaknow_video/scripts/validate_predictions.py \
  --gold /root/public/jasonshu/dynaknow_video/release/v0_5/combined_gold_v0_5_balanced.jsonl \
  --predictions /path/to/predictions.jsonl
```

If no valid option letter is parsed, the normalized row is written with `predicted_answer="uncertain"`. The validator treats this as invalid so parsing failures are visible before scoring.

The current smoke normalization files are:

- `release/v0_5/raw_model_outputs_smoke.jsonl`
- `release/v0_5/predictions_smoke_normalized.jsonl`
- `release/v0_5/score_smoke_normalized.md`

Validation result for the normalized smoke file:

- gold rows: 48
- prediction rows: 48
- missing rows: 0
- extra rows: 0
- duplicate rows: 0
- invalid answers: 0

The normalized smoke score is an oracle-format parsing check, not a model baseline.

## Next Step

Replace the smoke-test predictions with model predictions using the same JSONL format, then score with:

```bash
python /root/public/jasonshu/dynaknow_video/scripts/score_predictions.py \
  --gold /root/public/jasonshu/dynaknow_video/release/v0_5/combined_gold_v0_5_balanced.jsonl \
  --predictions /path/to/model_predictions.jsonl \
  --output /path/to/model_score.md
```
