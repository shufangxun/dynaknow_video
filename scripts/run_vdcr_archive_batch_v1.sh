#!/usr/bin/env bash
set -euo pipefail

QUERY_CSV="${1:-data/vdcr_concept_search_queries_v1.csv}"
OUTPUT_CSV="${VDCR_ARCHIVE_OUTPUT:-data/vdcr_candidate_videos_archive_batch_v1.csv}"
SKIPPED_CSV="${VDCR_ARCHIVE_SKIPPED:-${OUTPUT_CSV%.csv}_skipped.csv}"
QUERY_OFFSET="${VDCR_QUERY_OFFSET:-0}"
QUERY_LIMIT="${VDCR_QUERY_LIMIT:-80}"
PER_QUERY="${VDCR_PER_QUERY:-5}"
SKIP_EXISTING="${VDCR_SKIP_EXISTING:-}"
ID_PREFIX="${VDCR_ID_PREFIX:-vdcr_archive_batch}"

mkdir -p data logs

ARGS=(
  --queries "${QUERY_CSV}"
  --output "${OUTPUT_CSV}"
  --skipped-output "${SKIPPED_CSV}"
  --per-query "${PER_QUERY}"
  --query-offset "${QUERY_OFFSET}"
  --query-limit "${QUERY_LIMIT}"
  --id-prefix "${ID_PREFIX}"
  --sleep-sec 0.5
  --timeout-sec 25
  --max-attempts 3
)

if [[ -n "${SKIP_EXISTING}" ]]; then
  ARGS+=(--skip-existing "${SKIP_EXISTING}")
fi

python scripts/search_archive_files.py "${ARGS[@]}"
