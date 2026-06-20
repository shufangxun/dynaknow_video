# VDCR V2 Retrieval Status

Date: 2026-06-20

## Current State

No V2 retrieval background process is currently running.

Recent runs wrote outputs under ignored `runs/v2_retrieval/` directories. These
outputs are local working artifacts and should be inspected before any rows are
imported into tracked candidate CSVs.

## Completed Runs

| Run | Query asset | Source mode | Query window | Candidate rows | Notes |
|---|---|---|---:|---:|---|
| `v2_shard_000_120_20260620T040948Z` | `data/vdcr_concept_search_queries_v1.csv` | both | 0-120 | no summary | Commons returned throttling before a complete summary was written. |
| `v2_archive_shard_120_240_20260620T041144Z` | `data/vdcr_concept_search_queries_v1.csv` | archive | 120-240 | 13 | Needs manual quality review before import. |
| `v2_expansion_archive_smoke_20260620T000000Z` | `data/vdcr_v2_expansion_queries.csv` | archive | 0-40 | 1 | Pre-round-robin smoke; yielded an obvious false positive. |
| `v2_expansion_archive_smoke_rr_20260620T000000Z` | `data/vdcr_v2_expansion_queries.csv` | archive | 0-40 | 1 | Domain round-robin smoke; yielded the same obvious false positive. |

The expansion smoke false positive was:

```text
candidate_id=v2_archive_0_000001
concept=Standing-Wave Mode Formation
url=https://archive.org/details/the-complete-history-of-the-super-mario-64-a-button-challenge
```

This row should not be imported; it is a title/metadata false match, not a
standing-wave video.

## Retrieval Implications

Archive-only retrieval has low yield for the current V2 expansion backlog. It
should be used as a secondary source, not the main path for V2 scale-up.

The better next steps are:

1. Retry Commons in small, throttled shards once `403 Too Many Reqs` cools down.
2. Use curated public-source intake for chemistry/materials and high-value
   physics/biology concepts.
3. Inspect the 13 rows from
   `runs/v2_retrieval/v2_archive_shard_120_240_20260620T041144Z/archive_candidates.csv`
   before deciding whether any deserve import.
4. Keep `data/vdcr_v2_expansion_queries.csv` as the main query entry point; it
   now round-robins domains so early shards do not overfocus on one domain.

## Useful Commands

```bash
cat runs/v2_retrieval/v2_archive_shard_120_240_20260620T041144Z/summary.txt
head -20 runs/v2_retrieval/v2_archive_shard_120_240_20260620T041144Z/archive_candidates.csv

VDCR_RUN_ID=v2_expansion_commons_smoke_<timestamp> \
VDCR_SOURCES=commons \
VDCR_QUERY_OFFSET=0 \
VDCR_QUERY_LIMIT=40 \
VDCR_PER_QUERY=5 \
VDCR_COMMONS_SLEEP_SEC=3.0 \
bash scripts/start_v2_retrieval_background.sh data/vdcr_v2_expansion_queries.csv
```
