# DynaKnow-Video Pilot v0.9

This release hardens the v0.8 pilot against visible text/OCR leakage.

## Files

- `dynaknow_video_pilot_v0_9_balanced.jsonl`: recommended evaluation JSONL.
- `dynaknow_video_pilot_v0_9_manifest.csv`: source provenance and local-media manifest.
- `answer_only_tasks_v0_9_balanced.jsonl`: answer-only leakage tasks.
- `frame_shortcut_tasks_v0_9_balanced.jsonl`: first/middle/last and sparse-frame shortcut tasks.
- `combined_gold_v0_9_balanced.jsonl`: combined gold for scoring.
- `stats_v0_9_balanced.md`: release statistics.
- `score_smoke_oracle.md`: scorer smoke test.

## Leakage Handling

- Evaluation JSONL does not expose `source_url` or license/source-title fields.
- All 12 accepted samples have `ocr_leakage_status=pass`.
- The original full `dynaknow_000016` clip was moved to rejected/revise because its sparse frames include end-card text.
- `dynaknow_000091` replaces it with a 0-12s no-audio segment stored in `media/segments/dynaknow_000091.mp4`.

## Scope

- Samples: 12
- Local media: 12/12
- Answer balance: A/B/C/D = 3/3/3/3
- This remains a construction pilot toward the final 200-300 sample benchmark.

