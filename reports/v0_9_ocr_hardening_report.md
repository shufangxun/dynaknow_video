# DynaKnow-Video v0.9 OCR Hardening Report

## Objective

Apply the no-subtitle/no-OCR preference to every currently accepted pilot sample, not only newly added items.

## Changes

- Reviewed all 12 accepted v0.8 samples using sparse contact sheets.
- Added `data/shortcut_review_decisions_v0_9_all.csv` with explicit `visible_text_or_overlay` and `ocr_leakage_status` for every accepted sample.
- Replaced `dynaknow_000016` with a clean no-audio segment:
  - rejected full clip: `media/raw/dynaknow_000016.webm`
  - replacement clip: `media/segments/dynaknow_000091.mp4`
  - segment spec: `data/media_segments_v0_9.csv`
- Regenerated the accepted set and release as v0.9.

## Current Release

- Accepted: `data/pilot_samples_accepted_v0_9.jsonl`
- Rejected/revise: `data/pilot_samples_rejected_or_revise_v0_9.jsonl`
- Manifest: `data/pilot_manifest_v0_9.csv`
- Release: `release/v0_9/`

## Verification

- `release/v0_9/dynaknow_video_pilot_v0_9_balanced.jsonl` has 12 samples.
- Answer distribution is balanced: A/B/C/D = 3/3/3/3.
- Evaluation JSONL contains no `source_url` or `license_or_usage_note`.
- All accepted rows have `ocr_leakage_status=pass`.
- All local media paths exist.
- `dynaknow_000016` is rejected with `reject_text_leakage`.
- `dynaknow_000091` is accepted and points to `media/segments/dynaknow_000091.mp4`.
- Prediction coverage validation passes for the v0.9 combined gold file.

