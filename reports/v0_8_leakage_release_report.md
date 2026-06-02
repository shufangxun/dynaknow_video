# DynaKnow-Video v0.8 Leakage And Release Report

## What Changed

v0.8 addresses the source/OCR leakage issue raised during review:

- Local videos remain in `media/raw/`, `media/raw_transcoded/`, and `media/segments/`.
- Source URLs remain in manifests for provenance.
- Recommended evaluation JSONL no longer exposes `source_url` or license/source-title fields.
- Shortcut review sheets now include `visible_text_or_overlay` and `ocr_leakage_status`.
- Filtering rejects samples marked with OCR/text leakage statuses such as `fail`, `direct_leak`, or `target_text_present`.

## New Accepted Samples

| video_id | Source | Local Media | Decision |
| --- | --- | --- | --- |
| `dynaknow_000088` | `File:Meca_siphon.webm` | `media/segments/dynaknow_000088.mp4` | Accepted after trimming opening title frames and dropping audio. |
| `dynaknow_000089` | `File:Siphon.webm` | `media/raw/dynaknow_000089.webm` | Accepted because visible frames show no explanatory OCR/overlay text; source title is hidden from evaluation JSONL. |

Rejected:

- `dynaknow_000090`: no major OCR leak, but single frames make germination obvious.

## Release Artifacts

- Accepted samples: `data/pilot_samples_accepted_v0_8.jsonl`
- Rejected/revise: `data/pilot_samples_rejected_or_revise_v0_8.jsonl`
- Pilot manifest: `data/pilot_manifest_v0_8.csv`
- Release directory: `release/v0_8/`
- Recommended eval JSONL: `release/v0_8/dynaknow_video_pilot_v0_8_balanced.jsonl`
- Provenance manifest: `release/v0_8/dynaknow_video_pilot_v0_8_manifest.csv`

## Verification

- `release/v0_8/dynaknow_video_pilot_v0_8_balanced.jsonl` has 12 samples.
- Answer distribution is balanced: A/B/C/D = 3/3/3/3.
- Evaluation JSONL contains no `source_url` or `license_or_usage_note`.
- Local media is available for all 12 samples.
- Combined gold has 72 rows: 12 full-video, 12 answer-only, and 48 frame-shortcut rows.
- Oracle prediction coverage validation passes with no missing or extra rows.

