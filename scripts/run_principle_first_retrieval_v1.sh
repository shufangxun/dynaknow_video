#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

TAG="${1:-$(date -u +%Y%m%d_%H%M%S)}"
PER_QUERY="${PER_QUERY:-12}"
QUERY_LIMIT="${QUERY_LIMIT:-0}"
QUEUE_LIMIT="${QUEUE_LIMIT:-800}"
DOWNLOAD_LIMIT="${DOWNLOAD_LIMIT:-160}"
MAX_CONTENT_LENGTH_BYTES="${MAX_CONTENT_LENGTH_BYTES:-50000000}"
MAX_DURATION_SEC="${MAX_DURATION_SEC:-180}"
SEARCH_SLEEP_SEC="${SEARCH_SLEEP_SEC:-1.0}"
DOWNLOAD_SLEEP_SEC="${DOWNLOAD_SLEEP_SEC:-1.0}"
WAIT_FOR_COMMONS="${WAIT_FOR_COMMONS:-1}"
COMMONS_PROBE_SLEEP_SEC="${COMMONS_PROBE_SLEEP_SEC:-900}"
COMMONS_WAIT_TIMEOUT_SEC="${COMMONS_WAIT_TIMEOUT_SEC:-0}"

QUERY_CSV="${QUERY_CSV:-data/principle_search_queries_v1.csv}"
SKIP_EXISTING="${SKIP_EXISTING:-data/existing_source_urls_v1_20260603_all.csv}"

RAW_CANDIDATES="data/principle_candidates_v1_${TAG}_commons_raw.csv"
SKIPPED_SEARCH="data/principle_candidates_v1_${TAG}_commons_skipped.csv"
POOL_CSV="data/principle_candidate_pool_v1_${TAG}.csv"
QUEUE_CSV="data/principle_review_queue_v1_${TAG}.csv"
POOL_HTML="reports/principle_first_v1/candidate_pool_${TAG}.html"
MEDIA_MANIFEST="data/principle_media_manifest_v1_${TAG}.csv"
MEDIA_CHECK="data/principle_media_url_check_v1_${TAG}.csv"
DOWNLOAD_MANIFEST="data/principle_media_manifest_v1_${TAG}_download_ok.csv"
DOWNLOAD_REJECTED="data/principle_media_manifest_v1_${TAG}_download_rejected.csv"
DOWNLOAD_STATUS="data/principle_download_status_v1_${TAG}.csv"
MEDIA_DIR="media/principle_retrieval_v1_${TAG}"
FRAMES_DIR="media/principle_frames_v1_${TAG}"
FRAME_STATUS="data/principle_frame_status_v1_${TAG}.csv"
GATE_REVIEW="data/principle_gate_review_v1_${TAG}.csv"
GATE_REVIEW_HTML="reports/principle_first_v1/gate_review_${TAG}.html"
MEDIA_REVIEW_HTML="reports/principle_first_v1/media_review_${TAG}.html"

mkdir -p data reports/principle_first_v1 media logs

echo "tag=${TAG}"
echo "query_csv=${QUERY_CSV}"
echo "per_query=${PER_QUERY} query_limit=${QUERY_LIMIT} queue_limit=${QUEUE_LIMIT} download_limit=${DOWNLOAD_LIMIT}"
echo "max_content_length_bytes=${MAX_CONTENT_LENGTH_BYTES} max_duration_sec=${MAX_DURATION_SEC}"
echo "wait_for_commons=${WAIT_FOR_COMMONS} commons_probe_sleep_sec=${COMMONS_PROBE_SLEEP_SEC} commons_wait_timeout_sec=${COMMONS_WAIT_TIMEOUT_SEC}"

if [[ "${WAIT_FOR_COMMONS}" != "0" ]]; then
  python3 - "${COMMONS_PROBE_SLEEP_SEC}" "${COMMONS_WAIT_TIMEOUT_SEC}" <<'PY'
import json
import sys
import time
import urllib.parse
import urllib.request

sleep_sec = float(sys.argv[1])
timeout_sec = float(sys.argv[2])
started = time.time()
params = {
    "action": "query",
    "format": "json",
    "list": "search",
    "srsearch": "free fall acceleration slow motion",
    "srnamespace": "6",
    "srlimit": "1",
}
url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
headers = {
    "User-Agent": "DynaKnowVideoPilot/0.1 (research metadata collection)",
    "Accept": "application/json",
}

while True:
    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        hits = len(payload.get("query", {}).get("search", []))
        print(f"Commons probe ok hits={hits}", flush=True)
        break
    except Exception as exc:
        elapsed = time.time() - started
        if timeout_sec > 0 and elapsed >= timeout_sec:
            raise RuntimeError(f"Commons probe timed out after {elapsed:.0f}s: {exc}") from exc
        print(f"Commons probe blocked: {exc}; sleeping {sleep_sec:.0f}s", flush=True)
        time.sleep(sleep_sec)
PY
fi

search_args=(
  --queries "${QUERY_CSV}"
  --output "${RAW_CANDIDATES}"
  --per-query "${PER_QUERY}"
  --start-index 1
  --id-prefix "principle_v1"
  --sleep-sec "${SEARCH_SLEEP_SEC}"
  --timeout-sec 30
  --max-attempts 3
  --skipped-output "${SKIPPED_SEARCH}"
)
if [[ "${QUERY_LIMIT}" != "0" ]]; then
  search_args+=(--query-limit "${QUERY_LIMIT}")
fi
if [[ -f "${SKIP_EXISTING}" ]]; then
  search_args+=(--skip-existing "${SKIP_EXISTING}")
fi
python3 scripts/search_commons_files.py "${search_args[@]}"

reviewed_args=()
if [[ -f "${SKIP_EXISTING}" ]]; then
  reviewed_args+=(--reviewed-source-audit "${SKIP_EXISTING}")
fi
python3 scripts/build_retrieval_candidate_pool.py \
  --taxonomy data/domain_taxonomy_v1.csv \
  "${reviewed_args[@]}" \
  --output-csv "${POOL_CSV}" \
  --output-html "${POOL_HTML}" \
  --queue-csv "${QUEUE_CSV}" \
  --queue-decisions priority_review,manual_review \
  --queue-limit "${QUEUE_LIMIT}" \
  --title "DynaKnow Principle-First Retrieval Candidates ${TAG}" \
  "${RAW_CANDIDATES}"

python3 scripts/resolve_commons_media.py \
  --input "${QUEUE_CSV}" \
  --output "${MEDIA_MANIFEST}"

if ! python3 scripts/check_media_urls.py \
  --input "${MEDIA_MANIFEST}" \
  --output "${MEDIA_CHECK}" \
  --timeout-sec 10 \
  --attempts 2 \
  --sleep-sec 0.4; then
  echo "continuing after URL check failures"
fi

python3 scripts/filter_media_manifest_by_url_check.py \
  --manifest "${MEDIA_MANIFEST}" \
  --url-check "${MEDIA_CHECK}" \
  --ok-output "${DOWNLOAD_MANIFEST}" \
  --failed-output "${DOWNLOAD_REJECTED}" \
  --max-content-length-bytes "${MAX_CONTENT_LENGTH_BYTES}" \
  --max-duration-sec "${MAX_DURATION_SEC}" \
  --limit "${DOWNLOAD_LIMIT}"

if ! python3 scripts/download_media.py \
  --manifest "${DOWNLOAD_MANIFEST}" \
  --output-dir "${MEDIA_DIR}" \
  --status-output "${DOWNLOAD_STATUS}" \
  --sleep-sec "${DOWNLOAD_SLEEP_SEC}" \
  --max-retry-after-sec 90; then
  echo "continuing after media download failures"
fi

python3 scripts/extract_frames_ffmpeg.py \
  --media-manifest "${DOWNLOAD_MANIFEST}" \
  --media-dir "${MEDIA_DIR}" \
  --frames-dir "${FRAMES_DIR}" \
  --output "${FRAME_STATUS}" \
  --sparse-count 6

gate_review_args=(
  --queue "${QUEUE_CSV}"
  --inventory data/principle_inventory_v1.csv
  --frame-status "${FRAME_STATUS}"
  --media-dir "${MEDIA_DIR}"
  --frames-dir "${FRAMES_DIR}"
  --output-csv "${GATE_REVIEW}"
  --output-html "${GATE_REVIEW_HTML}"
  --title "DynaKnow Principle Gate Review ${TAG}"
)
if [[ -f "${SKIP_EXISTING}" ]]; then
  gate_review_args+=(--existing-sources "${SKIP_EXISTING}")
fi
python3 scripts/build_principle_gate_review.py "${gate_review_args[@]}"

python3 scripts/build_retrieval_media_review.py \
  --queue "${QUEUE_CSV}" \
  --media-check "${MEDIA_CHECK}" \
  --dynamic-gate "${GATE_REVIEW}" \
  --media-dir "${MEDIA_DIR}" \
  --output "${MEDIA_REVIEW_HTML}" \
  --title "DynaKnow Principle-First Media Review ${TAG}"

if [[ "$(wc -l < "${DOWNLOAD_MANIFEST}")" -gt 1 ]]; then
  cp "${POOL_HTML}" reports/principle_first_v1/latest_candidate_pool.html
  cp "${GATE_REVIEW_HTML}" reports/principle_first_v1/latest_gate_review.html
  cp "${MEDIA_REVIEW_HTML}" reports/principle_first_v1/latest_media_review.html
else
  echo "download manifest is empty; latest review links were not updated"
fi

echo "raw_candidates=${RAW_CANDIDATES}"
echo "candidate_pool=${POOL_CSV}"
echo "queue=${QUEUE_CSV}"
echo "media_manifest=${MEDIA_MANIFEST}"
echo "media_check=${MEDIA_CHECK}"
echo "download_manifest=${DOWNLOAD_MANIFEST}"
echo "download_status=${DOWNLOAD_STATUS}"
echo "frame_status=${FRAME_STATUS}"
echo "gate_review=${GATE_REVIEW}"
echo "candidate_pool_html=${POOL_HTML}"
echo "gate_review_html=${GATE_REVIEW_HTML}"
echo "media_review_html=${MEDIA_REVIEW_HTML}"
