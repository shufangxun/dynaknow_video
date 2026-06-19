#!/usr/bin/env bash
set -euo pipefail

DATASET="${DATASET:-release/v1/dataset_v1.jsonl}"
MCQ_DATASET="${MCQ_DATASET:-release/v1/dataset_v1_mcq_seed20260619.jsonl}"
OUT_DIR="${OUT_DIR:-runs/vdcr_vllm}"
REPORT_DIR="${REPORT_DIR:-reports/vdcr_vllm_dual_eval}"
JUDGE_MODEL="${JUDGE_MODEL:-Qwen/Qwen3-VL-8B-Instruct}"
MCQ_SEED="${MCQ_SEED:-20260619}"
VIDEO_SOURCE="${VIDEO_SOURCE:-frames}"
FPS="${FPS:-1.0}"
MAX_PIXELS="${MAX_PIXELS:-151200}"
BATCH_SIZE="${BATCH_SIZE:-1}"
TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-0}"

# Format: label|hf_model_id|params_b. Override this for Qwen3.5 model ids if needed.
MODEL_SPECS="${MODEL_SPECS:-qwen3vl_2b|Qwen/Qwen3-VL-2B-Instruct|2 qwen3vl_4b|Qwen/Qwen3-VL-4B-Instruct|4 qwen3vl_8b|Qwen/Qwen3-VL-8B-Instruct|8}"

mkdir -p "${OUT_DIR}" "${REPORT_DIR}" "$(dirname "${MCQ_DATASET}")"

python3 scripts/build_vdcr_mcq_from_direct_answer.py \
  --input "${DATASET}" \
  --output "${MCQ_DATASET}" \
  --seed "${MCQ_SEED}"

summary_args=()

for spec in ${MODEL_SPECS}; do
  IFS='|' read -r label model_id params_b <<< "${spec}"
  direct_pred="${OUT_DIR}/${label}_direct.jsonl"
  mcq_pred="${OUT_DIR}/${label}_mcq.jsonl"
  direct_exact_report="${REPORT_DIR}/score_${label}_direct_exact.md"
  direct_semantic_jsonl="${REPORT_DIR}/judge_${label}_direct_semantic.jsonl"
  direct_semantic_report="${REPORT_DIR}/judge_${label}_direct_semantic.md"
  mcq_report="${REPORT_DIR}/score_${label}_mcq.md"

  python3 scripts/run_vdcr_vllm.py \
    --dataset "${DATASET}" \
    --model-id "${model_id}" \
    --output "${direct_pred}" \
    --task direct \
    --video-source "${VIDEO_SOURCE}" \
    --fps "${FPS}" \
    --max-pixels "${MAX_PIXELS}" \
    --batch-size "${BATCH_SIZE}" \
    --tensor-parallel-size "${TENSOR_PARALLEL_SIZE}" \
    --continue-on-error

  python3 scripts/run_vdcr_vllm.py \
    --dataset "${MCQ_DATASET}" \
    --model-id "${model_id}" \
    --output "${mcq_pred}" \
    --task mcq \
    --video-source "${VIDEO_SOURCE}" \
    --fps "${FPS}" \
    --max-pixels "${MAX_PIXELS}" \
    --batch-size "${BATCH_SIZE}" \
    --tensor-parallel-size "${TENSOR_PARALLEL_SIZE}" \
    --continue-on-error

  python3 scripts/score_vdcr_direct_answer.py \
    --gold "${DATASET}" \
    --predictions "${direct_pred}" \
    --output "${direct_exact_report}"

  python3 scripts/judge_vdcr_semantic_equivalence.py \
    --gold "${DATASET}" \
    --predictions "${direct_pred}" \
    --output "${direct_semantic_jsonl}" \
    --report "${direct_semantic_report}" \
    --judge-model "${JUDGE_MODEL}" \
    --continue-on-error

  python3 scripts/score_vdcr_mcq.py \
    --gold "${MCQ_DATASET}" \
    --predictions "${mcq_pred}" \
    --output "${mcq_report}"

  summary_args+=(
    --run "${label}=${params_b}"
    --direct-exact "${label}=${direct_exact_report}"
    --direct-semantic "${label}=${direct_semantic_report}"
    --mcq "${label}=${mcq_report}"
  )
done

python3 scripts/report_vdcr_dual_eval.py \
  "${summary_args[@]}" \
  --output-md "${REPORT_DIR}/vdcr_dual_eval_summary.md" \
  --output-csv "${REPORT_DIR}/vdcr_dual_eval_summary.csv"
