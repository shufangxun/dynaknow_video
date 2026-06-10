#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

QUERY_QUEUE="${QUERY_QUEUE:-data/principle_gap_aware_search_queries_v1_20260605.csv}"
TAG="${1:-$(date -u +%Y%m%d_gap_principle_first)}"

if [[ ! -f "${QUERY_QUEUE}" ]]; then
  python3 scripts/build_gap_aware_principle_queries.py \
    --output-csv "${QUERY_QUEUE}" \
    --output-html reports/principle_first_v1/gap_aware_query_queue_20260605.html \
    --title "Gap-Aware Principle Query Queue 20260605"
fi

QUERY_CSV="${QUERY_QUEUE}" \
  PER_QUERY="${PER_QUERY:-12}" \
  QUERY_LIMIT="${QUERY_LIMIT:-0}" \
  QUEUE_LIMIT="${QUEUE_LIMIT:-800}" \
  DOWNLOAD_LIMIT="${DOWNLOAD_LIMIT:-160}" \
  MAX_CONTENT_LENGTH_BYTES="${MAX_CONTENT_LENGTH_BYTES:-50000000}" \
  MAX_DURATION_SEC="${MAX_DURATION_SEC:-180}" \
  SEARCH_SLEEP_SEC="${SEARCH_SLEEP_SEC:-1.0}" \
  DOWNLOAD_SLEEP_SEC="${DOWNLOAD_SLEEP_SEC:-1.0}" \
  WAIT_FOR_COMMONS="${WAIT_FOR_COMMONS:-1}" \
  COMMONS_PROBE_SLEEP_SEC="${COMMONS_PROBE_SLEEP_SEC:-900}" \
  COMMONS_WAIT_TIMEOUT_SEC="${COMMONS_WAIT_TIMEOUT_SEC:-0}" \
  bash scripts/run_principle_first_retrieval_v1.sh "${TAG}"
