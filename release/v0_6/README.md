# DynaKnow-Video Pilot v0.6

This is the current pilot release for dynamic video knowledge recognition.

Task:

```text
Given a video, identify the knowledge point best demonstrated by its dynamic process.
```

## Files

- `dynaknow_video_pilot_v0_6.jsonl`: clean release JSONL for accepted pilot samples, preserving source option order.
- `dynaknow_video_pilot_v0_6_balanced.jsonl`: recommended evaluation JSONL with answer positions rebalanced.
- `dynaknow_video_pilot_v0_6_manifest.csv`: compact sample/media manifest.
- `answer_only_tasks_v0_6_balanced.jsonl`: recommended answer-only leakage tasks.
- `frame_shortcut_tasks_v0_6_balanced.jsonl`: recommended first/middle/last and sparse-frame shortcut tasks.
- `shortcut_run_manifest_v0_6_balanced.csv`: recommended shortcut task manifest.
- `combined_gold_v0_6_balanced.jsonl`: combined gold file for scoring full-video and shortcut predictions together.
- `stats_v0_6.md`: dataset statistics before answer rebalance.
- `stats_v0_6_balanced.md`: statistics for the recommended balanced release.
- `predictions_smoke_full_oracle_shortcut_always_a.jsonl`: smoke-test predictions.
- `score_smoke_full_oracle_shortcut_always_a.md`: smoke-test score report.

## Scope

- Samples: 10
- This is not the final benchmark scale.
- Accepted samples pass answer-only leakage and single-frame insufficiency review.
- Ordered sparse frames are often sufficient, so this release evaluates v1 dynamic knowledge recognition, not strict dense full-video-only understanding.

## Evaluation

Use the video prompt in:

- `../../prompts/video_knowledge_question.md`

Primary metric:

- full-video multiple-choice accuracy.

Shortcut diagnostics:

- answer-only accuracy,
- single-frame accuracy,
- sparse-frame accuracy,
- Dynamic Necessity Gap: full-video accuracy minus best static/answer-only shortcut accuracy.

Prediction JSONL format:

```json
{"video_id":"dynaknow_000001","mode":"full_video","predicted_answer":"A"}
```

Score predictions:

```bash
python ../../scripts/score_predictions.py \
  --gold combined_gold_v0_6_balanced.jsonl \
  --predictions predictions.jsonl \
  --output score.md
```

Normalize raw model outputs:

```bash
python ../../scripts/normalize_model_outputs.py \
  --input raw_model_outputs.jsonl \
  --output predictions.jsonl \
  --response-field response
```

Validate prediction coverage before scoring:

```bash
python ../../scripts/validate_predictions.py \
  --gold combined_gold_v0_6_balanced.jsonl \
  --predictions predictions.jsonl
```

## Caveats

- Source licenses must be verified on linked source pages before redistribution.
- Local media paths point to files in `../../media/raw/` or `../../media/raw_transcoded/`.
- This is still a construction pilot for validating the benchmark protocol.
