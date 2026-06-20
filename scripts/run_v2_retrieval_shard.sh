#!/usr/bin/env bash
set -euo pipefail

QUERY_CSV="${1:-data/vdcr_concept_search_queries_v1.csv}"
RUN_ID="${VDCR_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_DIR="${VDCR_RUN_DIR:-runs/v2_retrieval/${RUN_ID}}"
QUERY_OFFSET="${VDCR_QUERY_OFFSET:-0}"
QUERY_LIMIT="${VDCR_QUERY_LIMIT:-120}"
PER_QUERY="${VDCR_PER_QUERY:-5}"
SKIP_EXISTING="${VDCR_SKIP_EXISTING:-data/vdcr_candidate_videos_combined_v1.csv}"
TIMEOUT_SEC="${VDCR_TIMEOUT_SEC:-25}"
COMMONS_SLEEP_SEC="${VDCR_COMMONS_SLEEP_SEC:-1.0}"
ARCHIVE_SLEEP_SEC="${VDCR_ARCHIVE_SLEEP_SEC:-0.5}"
SOURCES="${VDCR_SOURCES:-both}"

mkdir -p "${RUN_DIR}"

COMMONS_OUTPUT="${RUN_DIR}/commons_candidates.csv"
COMMONS_SKIPPED="${RUN_DIR}/commons_skipped.csv"
ARCHIVE_OUTPUT="${RUN_DIR}/archive_candidates.csv"
ARCHIVE_SKIPPED="${RUN_DIR}/archive_skipped.csv"

cat > "${RUN_DIR}/run_config.env" <<EOF
QUERY_CSV=${QUERY_CSV}
RUN_ID=${RUN_ID}
RUN_DIR=${RUN_DIR}
VDCR_QUERY_OFFSET=${QUERY_OFFSET}
VDCR_QUERY_LIMIT=${QUERY_LIMIT}
VDCR_PER_QUERY=${PER_QUERY}
VDCR_SKIP_EXISTING=${SKIP_EXISTING}
VDCR_TIMEOUT_SEC=${TIMEOUT_SEC}
VDCR_SOURCES=${SOURCES}
EOF

case ",${SOURCES}," in
  *,commons,*|*,both,*)
    python scripts/search_commons_files.py \
      --queries "${QUERY_CSV}" \
      --output "${COMMONS_OUTPUT}" \
      --skipped-output "${COMMONS_SKIPPED}" \
      --per-query "${PER_QUERY}" \
      --query-offset "${QUERY_OFFSET}" \
      --query-limit "${QUERY_LIMIT}" \
      --skip-existing "${SKIP_EXISTING}" \
      --id-prefix "v2_commons_${QUERY_OFFSET}" \
      --sleep-sec "${COMMONS_SLEEP_SEC}" \
      --timeout-sec "${TIMEOUT_SEC}" \
      --max-attempts 3
    ;;
  *)
    printf 'candidate_id,source_url,source_platform,license_or_usage_note,raw_duration_sec,suggested_start_sec,suggested_end_sec,initial_category,candidate_knowledge_point,domain_seed,subdomain_seed,why_dynamic,collector_notes\n' > "${COMMONS_OUTPUT}"
    printf 'search_term,initial_category,candidate_knowledge_point,error\n' > "${COMMONS_SKIPPED}"
    ;;
esac

case ",${SOURCES}," in
  *,archive,*|*,both,*)
    python scripts/search_archive_files.py \
      --queries "${QUERY_CSV}" \
      --output "${ARCHIVE_OUTPUT}" \
      --skipped-output "${ARCHIVE_SKIPPED}" \
      --per-query "${PER_QUERY}" \
      --query-offset "${QUERY_OFFSET}" \
      --query-limit "${QUERY_LIMIT}" \
      --skip-existing "${SKIP_EXISTING}" \
      --id-prefix "v2_archive_${QUERY_OFFSET}" \
      --sleep-sec "${ARCHIVE_SLEEP_SEC}" \
      --timeout-sec "${TIMEOUT_SEC}" \
      --max-attempts 3
    ;;
  *)
    printf 'candidate_id,source_url,source_platform,license_or_usage_note,raw_duration_sec,suggested_start_sec,suggested_end_sec,initial_category,candidate_knowledge_point,domain_seed,subdomain_seed,why_dynamic,collector_notes\n' > "${ARCHIVE_OUTPUT}"
    printf 'search_term,initial_category,candidate_knowledge_point,error\n' > "${ARCHIVE_SKIPPED}"
    ;;
esac

python - <<'PY' "${RUN_DIR}"
import csv
import sys
from pathlib import Path

run_dir = Path(sys.argv[1])
summary = []
for name in ["commons_candidates.csv", "commons_skipped.csv", "archive_candidates.csv", "archive_skipped.csv"]:
    path = run_dir / name
    if not path.exists():
        summary.append((name, "missing"))
        continue
    with path.open(newline="", encoding="utf-8") as handle:
        count = max(sum(1 for _ in csv.reader(handle)) - 1, 0)
    summary.append((name, str(count)))

(run_dir / "summary.txt").write_text(
    "\n".join(f"{name}: {count}" for name, count in summary) + "\n",
    encoding="utf-8",
)
PY
