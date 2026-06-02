# DynaKnow-Video v0.12 Orphan Media Review Report

## Objective

Continue benchmark construction without waiting for Wikimedia downloads by reviewing local media files that had frames but were not yet in the accepted/rejected pools.

## Tooling Fix

Added:

- `scripts/extract_frames_sequential_cv2.py`

This handles videos with misleading FPS/frame-count metadata by sequentially decoding frames instead of relying on random seeking. It was needed for `dynaknow_000048`, where the original OpenCV metadata reported `fps=1000` and random middle-frame extraction failed.

## Reviewed Orphans

Reviewed IDs:

- `dynaknow_000013`
- `dynaknow_000030`
- `dynaknow_000048`
- `dynaknow_000067`

Decision file:

- `data/shortcut_review_decisions_local_orphans_v0_12.csv`

## Decisions

| video_id | Decision | Reason |
| --- | --- | --- |
| `dynaknow_000013` | reject | Map/date/scale text and source-title melting leakage; map interpretation rather than direct video dynamics. |
| `dynaknow_000030` | reject | Specialist molecular/magnetic paper context. |
| `dynaknow_000048` | accept | No visible OCR; sequential frames show the floating platform transitioning from horizontal to vertical. |
| `dynaknow_000067` | reject | Archival/title context and weak isolated collision evidence. |

## Current State

- Accepted: `data/pilot_samples_accepted_v0_12.jsonl` with 13 samples.
- Rejected/revise: `data/pilot_samples_rejected_or_revise_v0_12.jsonl` with 35 samples.
- Release: `release/v0_12/`

## Verification

- v0.12 evaluation JSONL has 13 samples.
- All accepted rows have `ocr_leakage_status=pass`.
- Evaluation JSONL contains no `source_url` or `license_or_usage_note`.
- Local media exists for all 13 samples.
- Combined gold has 78 rows.
- Oracle prediction coverage validation passes with no missing or extra rows.

