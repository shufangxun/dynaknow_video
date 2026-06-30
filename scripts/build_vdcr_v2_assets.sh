#!/usr/bin/env bash
set -euo pipefail

python3 scripts/build_vdcr_v2_concept_inventory.py
python3 scripts/build_vdcr_v2_construction_assets.py \
  --target-per-domain 75
python3 scripts/build_vdcr_v2_review_triage.py
python3 scripts/apply_vdcr_v2_triage_decisions.py
python3 scripts/build_vdcr_v2_draft_samples.py
python3 scripts/build_vdcr_v2_draft_status.py
python3 scripts/build_vdcr_v2_expansion_backlog.py
python3 scripts/build_vdcr_review_dashboard.py \
  --review-csv data/vdcr_v2_review_queue.csv \
  --samples data/vdcr_v2_seed_samples.jsonl \
  --concepts data/vdcr_v2_concept_inventory.csv \
  --candidates data/vdcr_candidate_videos_combined_v2.csv \
  --output reports/vdcr_v2_review_dashboard.html
