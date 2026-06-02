# v0.6 Review And Release Report

Date: 2026-06-01

## Shortcut Review

Review input:

- `data/shortcut_human_review_curated_web_v0_6.csv`
- `data/shortcut_review_decisions_curated_web_v0_6.csv`

Decision helper:

- `scripts/apply_shortcut_review_decisions.py`

Review result:

- reviewed v0.6 draft samples: 3
- accepted: 2
- rejected/revise: 1

Accepted:

- `dynaknow_000083`: Some chemical reactions produce color change.
- `dynaknow_000084`: Plant shoots can grow toward a light source.

Rejected/revise:

- `dynaknow_000082`: Some reactions form a precipitate.

Reason:

- `dynaknow_000082` has visible late still frames showing cloudy products in test tubes, so the precipitate answer can likely be inferred from a single late frame.

## v0.6 Dataset State

Files:

- `data/pilot_samples_accepted_v0_6.jsonl`
- `data/pilot_samples_rejected_or_revise_v0_6.jsonl`
- `data/pilot_manifest_v0_6.csv`

Counts:

- accepted samples: 10
- rejected/revise samples: 22
- manifest rows: 32
- all draft samples: 81

## Release Package

Directory:

- `release/v0_6/`

Recommended evaluation file:

- `release/v0_6/dynaknow_video_pilot_v0_6_balanced.jsonl`

Counts:

- release samples: 10
- answer-only tasks: 10
- frame shortcut tasks: 40
- combined scoring rows: 60
- balanced answer distribution: A/B/C/D = 3/3/2/2

Smoke score:

- full-video oracle accuracy: 10/10
- answer-only always-A accuracy: 3/10
- single-frame first always-A accuracy: 3/10
- single-frame middle always-A accuracy: 3/10
- single-frame last always-A accuracy: 3/10
- sparse-frame always-A accuracy: 3/10
- Dynamic Necessity Gap: 0.700

## Notes

- `scripts/extract_frames_cv2.py` now supports `--skip-dark-edges` to avoid selecting black intro/outro frames as first/last shortcut frames.
- `scripts/build_pilot_manifest.py` and `scripts/export_release_dataset.py` now support `--extra-media-dir` so Commons transcodes can be used when original AV1 media is not locally decodable.
- `scripts/report_dataset_stats.py` now writes a dataset-specific title instead of a fixed v0.5 title.
