# VDCR V2 Legacy Physics Intake

Date: 2026-06-20

## Purpose

This slice restores a previously reviewed V1 candidate that was present in the
candidate pool but missing from V2 local triage because the V2 construction
script only discovered V2 download-status files.

## Source

| Candidate | Concept | Source page | License |
|---|---|---|---|
| `vdcr_commons_mr13_000005` | `Rayleigh-Taylor Instability` | `https://commons.wikimedia.org/wiki/File:HD-Rayleigh-Taylor.gif` | Public domain USGov |

## Files

- media manifest: `data/vdcr_v2_legacy_round13_media_manifest.csv`
- download status: `data/vdcr_v2_legacy_round13_download_status.csv`
- frame status: `data/vdcr_v2_legacy_round13_frame_status.csv`
- sparse sheet: `reports/vdcr_v2_legacy_round13_sparse_sheets/vdcr_commons_mr13_000005_sparse.jpg`

## Gate Status

| Candidate | Decision | Rationale |
|---|---|---|
| `vdcr_commons_mr13_000005` | `reject` | source is a single composite GIF frame showing multiple panels rather than a temporal video sequence; too much single-frame shortcut risk |
