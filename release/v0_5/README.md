# DynaKnow-Video Pilot v0.5

This is a small pilot release for dynamic video knowledge recognition.

Task:

```text
Given a video, identify the knowledge point best demonstrated by its dynamic process.
```

## Files

- `dynaknow_video_pilot_v0_5.jsonl`: clean release JSONL for accepted pilot samples, preserving source option order.
- `dynaknow_video_pilot_v0_5_balanced.jsonl`: recommended evaluation JSONL with answer positions rebalanced.
- `dynaknow_video_pilot_v0_5_manifest.csv`: compact sample/media manifest.
- `answer_only_tasks_v0_5_balanced.jsonl`: recommended answer-only leakage tasks.
- `frame_shortcut_tasks_v0_5_balanced.jsonl`: recommended first/middle/last and sparse-frame shortcut tasks.
- `shortcut_run_manifest_v0_5_balanced.csv`: recommended task manifest for shortcut baselines.
- `combined_gold_v0_5_balanced.jsonl`: combined gold file for scoring full-video and shortcut predictions together.
- `stats_v0_5.md`: dataset statistics.
- `stats_v0_5_balanced.md`: statistics for the recommended balanced release.
- `raw_model_outputs_smoke.jsonl`: example raw model-output rows for normalization testing.
- `predictions_smoke_normalized.jsonl`: normalized predictions produced from the smoke raw outputs.
- `score_smoke_normalized.md`: score report for the normalized smoke predictions.

## Scope

- Samples: 8
- This is not the final benchmark scale.
- Accepted samples pass a human single-frame insufficiency screen.
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

Valid `mode` values in this release:

- `full_video`
- `answer_only`
- `single_frame_first`
- `single_frame_middle`
- `single_frame_last`
- `sparse_frames_ordered`

Score predictions:

```bash
python ../../scripts/score_predictions.py \
  --gold combined_gold_v0_5_balanced.jsonl \
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

Raw model output rows should contain at least:

```json
{"video_id":"dynaknow_000001","mode":"full_video","response":"Answer: A"}
```

Validate prediction coverage before scoring:

```bash
python ../../scripts/validate_predictions.py \
  --gold combined_gold_v0_5_balanced.jsonl \
  --predictions predictions.jsonl
```

The validator checks missing rows, extra rows, duplicate `(video_id, mode)` rows, and invalid answer labels before scoring. Normalizer parse failures are written as `uncertain` and will fail validation.

Generate smoke-test baselines:

```bash
python ../../scripts/make_baseline_predictions.py \
  --tasks dynaknow_video_pilot_v0_5_balanced.jsonl \
  --output predictions_full_video_oracle.jsonl \
  --baseline oracle
```

## Caveats

- Source licenses must be verified on the linked source pages before redistribution.
- Local media paths point to files in `../../media/raw/`.
- This release is a pilot for validating the data construction and filtering protocol.
