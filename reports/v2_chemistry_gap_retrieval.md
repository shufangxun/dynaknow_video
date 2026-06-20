# VDCR V2 Chemistry Gap Retrieval

Date: 2026-06-20

## Why This Exists

The current V2 construction queue is large enough overall but chemistry remains
the weakest domain:

- V2 seed samples: 29 chemistry rows.
- V2 main review queue: 20 chemistry rows.
- First-target domain goal: about 60 rows per domain before final balancing.

The chemistry domain therefore needs a larger candidate buffer before manual
review can realistically yield a balanced V2 release.

## Query Asset

Generated query file:

```text
data/vdcr_v2_gap_queries_chemistry.csv
```

It currently contains 156 query rows across 39 undercovered
chemistry/materials concepts after adding the curated chemistry candidates.
Each row keeps the existing retrieval schema used by
`data/vdcr_concept_search_queries_v1.csv`, so it can be passed directly to the
current retrieval shard runner.

Generation command:

```bash
python3 scripts/build_vdcr_v2_gap_queries.py
```

The generator ranks chemistry concepts by current candidate count first, then
priority and expected video availability. It excludes specialized action
concepts and uses four query forms per concept:

```text
<concept>
<concept> demonstration
<concept> experiment video
<concept_zh> <concept>
```

## Active Retrieval Run

Archive-only run launched because Commons recently returned throttling errors:

```bash
VDCR_RUN_ID=v2_gap_chem_archive_20260620T044725Z \
VDCR_SOURCES=archive \
VDCR_QUERY_OFFSET=0 \
VDCR_QUERY_LIMIT=160 \
VDCR_PER_QUERY=5 \
bash scripts/start_v2_retrieval_background.sh data/vdcr_v2_gap_queries_chemistry.csv
```

Run directory:

```text
runs/v2_retrieval/v2_gap_chem_archive_20260620T044725Z
```

Result:

```text
commons_candidates.csv: 0
commons_skipped.csv: 0
archive_candidates.csv: 0
archive_skipped.csv: 0
```

Archive search completed but yielded no new candidates for this gap query set.
This means chemistry expansion should not continue relying on Archive-only
retrieval. The next source path is Commons retry plus curated public-source
intake for chemistry demonstrations.

## Commons Smoke Retry

Commons was retried with a small 40-query smoke shard:

```bash
VDCR_RUN_ID=v2_gap_chem_commons_smoke_20260620T045129Z \
VDCR_SOURCES=commons \
VDCR_QUERY_OFFSET=0 \
VDCR_QUERY_LIMIT=40 \
VDCR_PER_QUERY=5 \
VDCR_COMMONS_SLEEP_SEC=2.0 \
bash scripts/start_v2_retrieval_background.sh data/vdcr_v2_gap_queries_chemistry.csv
```

Result: Commons still returned `HTTP Error 403: Too Many Reqs`, so the smoke
run was stopped early. Do not launch a full Commons gap shard until this
throttling clears.

## Curated Chemistry Intake

Because automatic Archive yielded 0 and Commons remains throttled, V2 now uses a
curated chemistry intake file:

```text
data/vdcr_v2_curated_chemistry_intake.csv
```

Imported candidate file:

```text
data/vdcr_candidate_videos_curated_chemistry_v2.csv
```

Import command:

```bash
python3 scripts/import_curated_sources.py \
  --input data/vdcr_v2_curated_chemistry_intake.csv \
  --output data/vdcr_candidate_videos_curated_chemistry_v2.csv \
  --start-index 2001 \
  --skip-existing data/vdcr_candidate_videos_combined_v1.csv
```

This added 6 source-deduplicated Wikimedia Commons chemistry candidates:

- `curated_002001`: Iodine Clock Reaction
- `curated_002002`: Iodine Clock Reaction
- `curated_002003`: Chemical Garden Growth
- `curated_002004`: Blue Bottle Reaction
- `curated_002005`: Blue Bottle Reaction
- `curated_002006`: Briggs-Rauscher Reaction

After rebuilding construction assets, all 6 curated candidates entered the V2
main review queue. The V2 queue now has 172 rows, including 22 chemistry rows.

## Local Media Review Assets

The 6 curated chemistry candidates were resolved to Commons direct media URLs
and downloaded locally:

```text
data/vdcr_v2_curated_chemistry_media_manifest.csv
data/vdcr_v2_curated_chemistry_download_status.csv
```

Local media cache:

```text
media/vdcr_curated_chemistry_v2/
```

Frame extraction status:

```text
data/vdcr_v2_curated_chemistry_frame_status.csv
```

All 6 rows downloaded successfully and all 6 produced first/middle/last plus 8
sparse review frames. Sparse contact sheets are under:

```text
reports/vdcr_v2_curated_chemistry_sparse_sheets/
```

The V2 construction builder now discovers `data/vdcr_v2_*download_status.csv`
and `reports/vdcr_v2_*sparse_sheets/*_sparse.jpg`, then backfills
`local_media` and `contact_sheet` into `data/vdcr_v2_review_queue.csv`.
Therefore the main dashboard can directly play and inspect the curated
chemistry candidates.

After the run finishes, regenerate V2 construction assets:

```bash
python3 scripts/build_vdcr_v2_construction_assets.py
python3 scripts/build_vdcr_review_dashboard.py \
  --review-csv data/vdcr_v2_review_queue.csv \
  --samples data/vdcr_v2_seed_samples.jsonl \
  --concepts data/vdcr_concept_inventory_v1.csv \
  --candidates data/vdcr_candidate_videos_combined_v2.csv \
  --output reports/vdcr_v2_review_dashboard.html
```
