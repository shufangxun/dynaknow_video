# v0.3 Candidate Collection Report

Date: 2026-06-01

## Purpose

v0.2 showed that most automatically collected Commons candidates were unusable because of title leakage, static-frame shortcuts, wrong knowledge-point mappings, specialist context, or animation/simulation content. v0.3 moves those filters earlier, before drafting MCQs or downloading media.

## New Scripts

- `scripts/filter_candidate_quality.py`
- `scripts/search_commons_files.py`
- `scripts/merge_csv_unique.py`

## Candidate-Level Quality Filter

The filter checks:

- missing, too-short, or very long duration,
- auto-filled evidence that still needs review,
- noisy collection notes,
- title names the target phenomenon,
- specialist/paper/microscopy context,
- animation or simulation,
- static equipment shortcut risk.

Applied to the existing 141 candidate pool:

- priority: 10
- manual review: 13
- exclude: 118

Output files:

- `data/candidate_quality_priority_existing_v0_3.csv`
- `data/candidate_quality_manual_existing_v0_3.csv`
- `data/candidate_quality_exclude_existing_v0_3.csv`

## v0.3 Category Collection

New targeted category query file:

- `data/commons_category_queries_v0_3.csv`

Collection output:

- `data/candidate_videos_commons_v0_3_raw.csv`

Counts:

- raw candidates: 16
- priority after filter: 0
- manual review after filter: 2
- exclude after filter: 14

The main failure modes were missing duration, broad/noisy category matches, and auto-filled evidence that needs review. `Category:Videos of sound` produced mostly audio/performance-adjacent files rather than visible vibration mechanisms.

## v0.3 File Search

New Commons file-search query file:

- `data/commons_file_search_queries_v0_3.csv`

New file-search script:

- `scripts/search_commons_files.py`

The first file-search run hit Wikimedia Commons API throttling:

```text
HTTP Error 403: Too Many Reqs
```

The script was updated to skip failed search terms and preserve partial results on future runs. Do not re-run it aggressively; use a longer sleep interval.

Recommended retry:

```bash
python /root/public/jasonshu/dynaknow_video/scripts/search_commons_files.py \
  --queries /root/public/jasonshu/dynaknow_video/data/commons_file_search_queries_v0_3.csv \
  --output /root/public/jasonshu/dynaknow_video/data/candidate_videos_commons_search_v0_3_raw.csv \
  --per-query 5 \
  --start-index 500 \
  --sleep-sec 8 \
  --skip-existing /root/public/jasonshu/dynaknow_video/data/candidate_videos_merged.csv
```

The file-search script now also supports shard-level retries:

- `--query-offset`
- `--query-limit`
- `--skipped-output`

A low-rate collision shard was attempted with 3 search terms, `per-query=4`, and `sleep-sec=10`. Commons still returned `HTTP Error 403: Too Many Reqs` for all 3 search terms.

Outputs:

- `data/candidate_videos_commons_search_v0_3_shard00_raw.csv`
- `data/candidate_videos_commons_search_v0_3_shard00_skipped.csv`

## Review Pool

The v0.3 candidate review pool combines:

- old candidates that pass the stricter candidate-level filter,
- new v0.3 category candidates marked manual-review.

Output:

- `data/candidate_quality_review_pool_v0_3.csv`

Count:

- review-pool rows: 12

## Curated Intake Path

Because Commons broad categories are noisy and Commons search is currently throttled, v0.3 adds a manual/curated source path.

New files:

- `templates/curated_source_intake.csv`
- `docs/curated_sourcing_playbook.md`
- `scripts/import_curated_sources.py`

Smoke-test outputs:

- `data/candidate_videos_curated_template_test.csv`
- `data/candidate_quality_priority_curated_template_test.csv`

The smoke-test row is only a template/example row, not a real candidate. It verifies that manually curated rows can be imported and passed through the candidate-quality filter.

## Decision

The current Commons category strategy is not sufficient for scaling to 200-300 final samples. The stricter filter is useful and should remain in the pipeline, but the candidate source strategy needs to shift toward:

- targeted file search with low request rate,
- manually curated public-domain/CC science demo collections,
- collecting candidates where the title names the object/event but not the target knowledge point,
- avoiding broad Commons categories that produce missing-duration, specialist, or audio-only results.
