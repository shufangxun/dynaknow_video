# DynaKnow-Video Pilot v0.8

This pilot release adds two pressure/fluid-flow samples and separates evaluation data from source provenance to reduce source-title leakage.

## Files

- `dynaknow_video_pilot_v0_8.jsonl`: evaluation JSONL, preserving source option order.
- `dynaknow_video_pilot_v0_8_balanced.jsonl`: recommended evaluation JSONL with answer positions balanced.
- `dynaknow_video_pilot_v0_8_manifest.csv`: provenance and local-media manifest, including source URLs.
- `answer_only_tasks_v0_8_balanced.jsonl`: answer-only leakage tasks.
- `frame_shortcut_tasks_v0_8_balanced.jsonl`: first/middle/last and sparse-frame shortcut tasks.
- `combined_gold_v0_8_balanced.jsonl`: combined gold file for scorer validation.
- `stats_v0_8_balanced.md`: balanced-release statistics.
- `score_smoke_oracle.md`: scorer smoke test using oracle predictions.
- `score_smoke_always_a.md`: always-A baseline smoke test.

## Leakage Handling

The recommended evaluation JSONL intentionally omits:

- `source_url`
- `license_or_usage_note`

Source URLs and license notes are retained in the manifest for provenance review only. v0.8 also adds explicit shortcut-review columns for visible text/OCR leakage:

- `visible_text_or_overlay`
- `ocr_leakage_status`

The two newly accepted v0.8 samples were reviewed as `ocr_leakage_status=pass`.

## Scope

- Samples: 12
- Local media: 12/12
- Answer balance: A/B/C/D = 3/3/3/3
- This remains a construction pilot, not the final 200-300 sample benchmark.

