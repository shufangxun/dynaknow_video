#!/usr/bin/env bash
set -euo pipefail

QUERY_CSV="${1:-data/vdcr_concept_search_queries_v1.csv}"
QUERY_LIMIT="${VDCR_QUERY_LIMIT:-80}"
PER_QUERY="${VDCR_PER_QUERY:-4}"

mkdir -p data logs

python scripts/search_commons_files.py \
  --queries "${QUERY_CSV}" \
  --output data/vdcr_candidate_videos_commons_v1.csv \
  --skipped-output data/vdcr_candidate_videos_commons_v1_skipped.csv \
  --per-query "${PER_QUERY}" \
  --query-limit "${QUERY_LIMIT}" \
  --id-prefix vdcr_commons \
  --sleep-sec 1.0 \
  --timeout-sec 25 \
  --max-attempts 3

python scripts/search_archive_files.py \
  --queries "${QUERY_CSV}" \
  --output data/vdcr_candidate_videos_archive_v1.csv \
  --skipped-output data/vdcr_candidate_videos_archive_v1_skipped.csv \
  --per-query "${PER_QUERY}" \
  --query-limit "${QUERY_LIMIT}" \
  --id-prefix vdcr_archive \
  --sleep-sec 0.5 \
  --timeout-sec 25 \
  --max-attempts 3
