# v0.6 Candidate Expansion Report

Date: 2026-06-01

## Purpose

This round expands the pilot beyond v0.5 by adding a taxonomy-driven candidate acquisition path and a small web-curated Commons batch for immediate review.

## Taxonomy Query Expansion

New script:

- `scripts/make_commons_search_queries_from_taxonomy.py`

Generated file:

- `data/commons_file_search_queries_v0_6.csv`

Result:

- 153 Commons file-search query rows generated from `data/knowledge_points_v1.csv`
- up to 3 search terms per knowledge point

The Commons API search probe currently returns `HTTP Error 403: Too Many Reqs`, so large API shards should be retried later with smaller query batches and longer delays.

## Web-Curated Intake

New curated source file:

- `data/curated_sources_web_v0_6.csv`

Imported candidate file:

- `data/candidate_videos_curated_web_v0_6.csv`

Counts:

- curated source rows: 14
- imported non-duplicate candidate rows: 12
- priority after quality filter: 3
- excluded after quality filter: 9
- manual-review bucket: 0

Priority candidates:

- `dynaknow_000082`: Some reactions form a precipitate.
- `dynaknow_000083`: Some chemical reactions produce color change.
- `dynaknow_000084`: Plant shoots can grow toward a light source.

Excluded candidates were mainly blocked by title leakage, animation/simulation, specialist-content, or long-duration flags.

## Filter Improvements

Updated script:

- `scripts/filter_candidate_quality.py`

Changes:

- added title-leakage keyword rules for friction, melting, crystallization, germination, precipitate, color-change reactions, gyroscope/precession, and angular momentum candidates
- added `ch3nh3pbi3` to specialist-content terms
- made normalized keyword matching catch CamelCase titles such as `FrictionOnBlock`
- applied animation/simulation checks to notes as well as titles

## Draft Samples

New files:

- `data/draft_samples_curated_web_v0_6.jsonl`
- `data/draft_samples_all_v0_6.jsonl`
- `data/answer_only_tasks_curated_web_v0_6.jsonl`

Counts:

- new v0.6 draft samples: 3
- total draft samples after merge: 81
- new answer-only tasks: 3

Validation:

- `scripts/validate_samples.py data/draft_samples_curated_web_v0_6.jsonl`: OK
- `scripts/validate_samples.py data/draft_samples_all_v0_6.jsonl`: OK

## Media And Frames

New files:

- `data/draft_media_manifest_curated_web_v0_6.csv`
- `data/draft_media_manifest_curated_web_v0_6_transcode_360p.csv`
- `data/frame_extraction_status_curated_web_v0_6.csv`
- `data/frame_extraction_status_curated_web_v0_6_transcode_360p.csv`
- `data/frame_extraction_status_curated_web_v0_6_combined.csv`
- `data/frame_shortcut_tasks_curated_web_v0_6.jsonl`
- `data/shortcut_run_manifest_curated_web_v0_6.csv`
- `data/shortcut_human_review_curated_web_v0_6.csv`
- `media/contact_sheets/curated_web_v0_6_first_middle_last.jpg`

Download result:

- `dynaknow_000082`: downloaded original AV1 and 360p transcode
- `dynaknow_000083`: downloaded original AV1 and 360p transcode
- `dynaknow_000084`: downloaded original WebM

Frame extraction result:

- 3/3 samples have first/middle/last frames
- 3/3 samples have 8 sparse frames
- AV1 originals for `dynaknow_000082` and `dynaknow_000083` could not be decoded by local OpenCV, so Commons 360p WebM transcodes were used for frame extraction and human review

New helper script:

- `scripts/make_commons_transcode_manifest.py`

## Next Step

This step has been completed in:

- `reports/v0_6_review_release_report.md`

Outcome:

- accepted: 2
- rejected/revise: 1
- release package: `release/v0_6/`
