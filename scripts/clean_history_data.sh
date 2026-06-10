#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ "${CONFIRM_DELETE_HISTORY:-}" != "yes" ]]; then
  echo "Refusing to delete history data."
  echo "Run with: CONFIRM_DELETE_HISTORY=yes bash scripts/clean_history_data.sh"
  exit 2
fi

for session in \
  dynaknow_principle_gap_retrieval_v1 \
  dynaknow_principle_retrieval_v1 \
  dynaknow_principle_archive_v1 \
  dynaknow_principle_first_v1
do
  if tmux has-session -t "${session}" 2>/dev/null; then
    tmux kill-session -t "${session}"
  fi
done

rm -rf data media reports logs release
mkdir -p data media reports logs

echo "Deleted history data directories: data media reports logs release"
echo "Preserved scripts, markdown docs, git metadata, and repository config."
