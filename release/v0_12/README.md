# DynaKnow-Video Pilot v0.12

This release adds one locally reviewed buoyancy sample while Wikimedia Commons downloads are rate-limited.

## Files

- `dynaknow_video_pilot_v0_12_balanced.jsonl`: recommended evaluation JSONL.
- `dynaknow_video_pilot_v0_12_manifest.csv`: source provenance and local-media manifest.
- `answer_only_tasks_v0_12_balanced.jsonl`: answer-only leakage tasks.
- `frame_shortcut_tasks_v0_12_balanced.jsonl`: first/middle/last and sparse-frame shortcut tasks.
- `combined_gold_v0_12_balanced.jsonl`: combined gold for scoring.
- `stats_v0_12_balanced.md`: release statistics.
- `score_smoke_oracle.md`: scorer smoke test.

## Leakage Handling

- Evaluation JSONL omits `source_url` and license/source-title fields.
- All 13 accepted samples have `ocr_leakage_status=pass`.
- Source URLs remain in the manifest only.

## Scope

- Samples: 13
- Local media: 13/13
- Answer distribution after rebalance: A/B/C/D = 4/3/3/3
- This remains a construction pilot toward the final 200-300 sample benchmark.

## New Sample

- `dynaknow_000048`: accepted after sequential frame extraction fixed a bad metadata/random-seeking issue. Sparse frames show a floating platform transitioning from horizontal to vertical.

