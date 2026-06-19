#!/usr/bin/env python3
"""Run VDCR direct-answer or MCQ evaluation with vLLM offline inference."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_qwen3_vl_vdcr import DEFAULT_PROMPT, build_message, extract_answer, read_completed_ids, read_jsonl
from scripts.run_qwen3_vl_vdcr import apply_chat_template
from scripts.score_vdcr_mcq import extract_choice


MCQ_PROMPT_TEMPLATE = """{question}

A. {choice_a}
B. {choice_b}
C. {choice_c}
D. {choice_d}

Return only the single best option letter: A, B, C, or D."""


def gpu_count() -> int:
    visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    if visible:
        return len([part for part in visible.split(",") if part.strip()])
    try:
        import torch

        count = torch.cuda.device_count()
    except Exception:
        count = 0
    return max(count, 1)


def mcq_prompt(row: dict[str, Any]) -> str:
    choices = row.get("choices", {})
    if not isinstance(choices, dict):
        choices = {}
    return MCQ_PROMPT_TEMPLATE.format(
        question=row.get("question", "Which named dynamic concept is instantiated by the temporally evolving process in this video?"),
        choice_a=choices.get("A", ""),
        choice_b=choices.get("B", ""),
        choice_c=choices.get("C", ""),
        choice_d=choices.get("D", ""),
    )


def prediction_from_response(raw_response: str, task: str) -> str:
    if task == "mcq":
        return extract_choice(raw_response)
    return extract_answer(raw_response)


def build_vllm_input(
    row: dict[str, Any],
    repo_root: Path,
    prompt: str,
    processor: Any,
    fps: float | None,
    max_pixels: int | None,
    total_pixels: int | None,
    video_source: str,
    frame_cache_dir: Path,
    enable_thinking: bool,
) -> dict[str, Any]:
    from qwen_vl_utils import process_vision_info

    messages = build_message(
        row,
        repo_root,
        prompt,
        fps,
        max_pixels,
        total_pixels,
        video_source,
        frame_cache_dir,
    )
    rendered_prompt = apply_chat_template(processor, messages, enable_thinking=enable_thinking)
    images, videos = process_vision_info(messages)
    mm_data: dict[str, Any] = {}
    if images is not None:
        mm_data["image"] = images
    if videos is not None:
        mm_data["video"] = videos
    payload: dict[str, Any] = {"prompt": rendered_prompt}
    if mm_data:
        payload["multi_modal_data"] = mm_data
    return payload


def make_llm(args: argparse.Namespace, tensor_parallel_size: int) -> Any:
    from vllm import LLM

    kwargs: dict[str, Any] = {
        "model": args.model_id,
        "tensor_parallel_size": tensor_parallel_size,
        "gpu_memory_utilization": args.gpu_memory_utilization,
        "trust_remote_code": True,
        "limit_mm_per_prompt": {"video": 1},
    }
    if args.dtype:
        kwargs["dtype"] = args.dtype
    if args.max_model_len:
        kwargs["max_model_len"] = args.max_model_len
    if args.max_num_seqs:
        kwargs["max_num_seqs"] = args.max_num_seqs
    if args.max_num_batched_tokens:
        kwargs["max_num_batched_tokens"] = args.max_num_batched_tokens
    if args.enforce_eager:
        kwargs["enforce_eager"] = True
    if args.mm_encoder_tp_mode:
        kwargs["mm_encoder_tp_mode"] = args.mm_encoder_tp_mode
    return LLM(**kwargs)


def write_generated_batch(
    llm: Any,
    sampling_params: Any,
    batch_rows: list[dict[str, Any]],
    batch_inputs: list[dict[str, Any]],
    args: argparse.Namespace,
    handle: Any,
    total_rows: int,
) -> None:
    if not batch_inputs:
        return
    try:
        outputs = llm.generate(batch_inputs, sampling_params=sampling_params)
    except Exception as exc:
        if not args.continue_on_error:
            raise
        outputs = [None] * len(batch_inputs)
        batch_error = repr(exc)
    else:
        batch_error = ""

    for meta, output in zip(batch_rows, outputs, strict=True):
        source_row = meta["row"]
        raw_response = "" if output is None else output.outputs[0].text
        status = "error" if output is None else "ok"
        result = {
            "video_id": source_row["video_id"],
            "mode": "full_video_mcq" if args.task == "mcq" else "full_video",
            "model_id": args.model_id,
            "predicted_answer": prediction_from_response(raw_response, args.task),
            "raw_response": raw_response,
            "prompt": meta["prompt"],
            "local_media": source_row.get("local_media", ""),
            "fps": args.fps,
            "max_pixels": args.max_pixels,
            "total_pixels": args.total_pixels,
            "video_source": args.video_source,
            "frame_cache_dir": str(args.frame_cache_dir) if args.video_source == "frames" else "",
            "tensor_parallel_size": meta["tensor_parallel_size"],
            "mm_encoder_tp_mode": args.mm_encoder_tp_mode,
            "latency_sec": round(time.perf_counter() - meta["started"], 3),
            "status": status,
        }
        if batch_error:
            result["error"] = batch_error
        handle.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        print(
            f"[{meta['index']}/{total_rows}] {source_row['video_id']}: "
            f"{result['predicted_answer']!r} ({result['status']})"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("release/v1/dataset_v1.jsonl"))
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--task", choices=["direct", "mcq"], default="direct")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--prompt-file", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--tensor-parallel-size", type=int, default=0, help="0 means use all visible GPUs.")
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.78)
    parser.add_argument("--mm-encoder-tp-mode", choices=["weights", "data", ""], default="data")
    parser.add_argument("--max-model-len", type=int, default=8192)
    parser.add_argument("--max-num-seqs", type=int, default=1)
    parser.add_argument("--max-num-batched-tokens", type=int, default=8192)
    parser.add_argument("--enforce-eager", action="store_true")
    parser.add_argument("--fps", type=float, default=1.0)
    parser.add_argument("--max-pixels", type=int, default=360 * 420)
    parser.add_argument("--total-pixels", type=int, default=None)
    parser.add_argument("--video-source", choices=["file", "frames"], default="frames")
    parser.add_argument("--frame-cache-dir", type=Path, default=Path("runs/qwen3vl_frame_cache_fps1"))
    parser.add_argument("--max-new-tokens", type=int, default=32)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--enable-thinking", action="store_true")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    from transformers import AutoProcessor
    from vllm import SamplingParams

    rows = read_jsonl(args.dataset)
    if args.limit is not None:
        rows = rows[: args.limit]

    prompt = args.prompt_file.read_text(encoding="utf-8") if args.prompt_file else args.prompt
    repo_root = args.repo_root.resolve()
    frame_cache_dir = args.frame_cache_dir.resolve()
    tensor_parallel_size = args.tensor_parallel_size or gpu_count()

    processor = AutoProcessor.from_pretrained(args.model_id, trust_remote_code=True)
    llm = make_llm(args, tensor_parallel_size)
    sampling_params = SamplingParams(
        max_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    completed = set() if args.overwrite else read_completed_ids(args.output)
    mode = "w" if args.overwrite else "a"

    with args.output.open(mode, encoding="utf-8") as handle:
        batch_rows: list[dict[str, Any]] = []
        batch_inputs: list[dict[str, Any]] = []
        for idx, row in enumerate(rows, start=1):
            video_id = row["video_id"]
            if video_id in completed:
                continue
            item_prompt = mcq_prompt(row) if args.task == "mcq" else prompt
            started = time.perf_counter()
            try:
                llm_input = build_vllm_input(
                    row,
                    repo_root,
                    item_prompt,
                    processor,
                    args.fps,
                    args.max_pixels,
                    args.total_pixels,
                    args.video_source,
                    frame_cache_dir,
                    args.enable_thinking,
                )
            except Exception as exc:
                if not args.continue_on_error:
                    raise
                result = {
                    "video_id": video_id,
                    "mode": "full_video_mcq" if args.task == "mcq" else "full_video",
                    "model_id": args.model_id,
                    "predicted_answer": "",
                    "raw_response": "",
                    "prompt": item_prompt,
                    "local_media": row.get("local_media", ""),
                    "latency_sec": round(time.perf_counter() - started, 3),
                    "status": "error",
                    "error": repr(exc),
                }
                handle.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
                handle.flush()
                print(f"[{idx}/{len(rows)}] {video_id}: build_error {exc!r}")
                continue

            batch_rows.append(
                {
                    "row": row,
                    "prompt": item_prompt,
                    "started": started,
                    "index": idx,
                    "tensor_parallel_size": tensor_parallel_size,
                }
            )
            batch_inputs.append(llm_input)
            if len(batch_inputs) < args.batch_size and idx < len(rows):
                continue

            write_generated_batch(llm, sampling_params, batch_rows, batch_inputs, args, handle, len(rows))
            batch_rows = []
            batch_inputs = []
        write_generated_batch(llm, sampling_params, batch_rows, batch_inputs, args, handle, len(rows))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
