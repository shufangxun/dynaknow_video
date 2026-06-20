#!/usr/bin/env bash
set -euo pipefail

QUERY_CSV="${1:-data/vdcr_concept_search_queries_v1.csv}"
RUN_ID="${VDCR_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_DIR="${VDCR_RUN_DIR:-runs/v2_retrieval/${RUN_ID}}"

mkdir -p "${RUN_DIR}"

export VDCR_RUN_ID="${RUN_ID}"
export VDCR_RUN_DIR="${RUN_DIR}"

if command -v setsid >/dev/null 2>&1; then
  setsid nohup bash scripts/run_v2_retrieval_shard.sh "${QUERY_CSV}" \
    > "${RUN_DIR}/retrieval.log" 2>&1 < /dev/null &
else
  nohup bash scripts/run_v2_retrieval_shard.sh "${QUERY_CSV}" \
    > "${RUN_DIR}/retrieval.log" 2>&1 < /dev/null &
fi

PID="$!"
echo "${PID}" > "${RUN_DIR}/pid"

cat <<EOF
started_v2_retrieval
run_id=${RUN_ID}
pid=${PID}
run_dir=${RUN_DIR}
log=${RUN_DIR}/retrieval.log

status:
  ps -p ${PID} -o pid,etime,cmd
  tail -f ${RUN_DIR}/retrieval.log

outputs:
  ${RUN_DIR}/commons_candidates.csv
  ${RUN_DIR}/archive_candidates.csv
  ${RUN_DIR}/summary.txt

source selection:
  VDCR_SOURCES=both     # default
  VDCR_SOURCES=archive  # skip Commons when throttled
  VDCR_SOURCES=commons  # Commons-only retry
EOF
