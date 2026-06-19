#!/usr/bin/env python3
"""Run Qwen3-VL models on the VDCR direct-answer release."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any


DEFAULT_PROMPT = (
    "Which named dynamic concept is instantiated by the temporally evolving process in this video?\n"
    "Return only the short canonical concept name in English or Chinese. Do not explain."
)

MCQ_PROMPT_TEMPLATE = """{question}

A. {choice_a}
B. {choice_b}
C. {choice_c}
D. {choice_d}

Return only the single best option letter: A, B, C, or D."""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def read_completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    completed: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("status", "ok") == "ok" and row.get("video_id"):
                completed.add(row["video_id"])
    return completed


def extract_answer(raw_response: object) -> str:
    text = str(raw_response or "").strip()
    if not text:
        return ""

    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        for key in ("answer", "predicted_answer", "concept", "name"):
            value = parsed.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    text = re.sub(r"^\s*(?:answer|predicted answer|concept|概念|答案)\s*[:：]\s*", "", text, flags=re.IGNORECASE)
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    first_line = first_line.strip(" \t\r\n`\"'。；;")
    return first_line


def extract_choice(raw_response: object) -> str:
    text = str(raw_response or "").strip()
    if not text:
        return ""
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        for key in ("answer", "predicted_answer", "choice"):
            value = str(parsed.get(key, "")).strip().upper()
            if value in {"A", "B", "C", "D"}:
                return value
    text = text.upper()
    if text in {"A", "B", "C", "D"}:
        return text
    for pattern in [
        r"\b(?:ANSWER|CHOICE|OPTION|答案|选项)\s*(?:IS|:|：)?\s*([ABCD])\b",
        r"\b([ABCD])\s*(?:\.|、|\)|）)",
    ]:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return ""


def build_task_prompt(row: dict[str, Any], task: str, default_prompt: str) -> str:
    if task == "direct":
        return default_prompt
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


def prediction_from_response(raw_response: object, task: str) -> str:
    if task == "mcq":
        return extract_choice(raw_response)
    return extract_answer(raw_response)


def apply_chat_template(processor: Any, messages: list[dict[str, Any]], enable_thinking: bool) -> str:
    try:
        return processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=enable_thinking,
        )
    except TypeError:
        return processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def extract_video_frames(media_path: Path, output_dir: Path, fps: float) -> list[Path]:
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    lock_path = output_dir.with_suffix(".lock")
    with lock_path.open("w", encoding="utf-8") as lock_handle:
        fcntl.flock(lock_handle, fcntl.LOCK_EX)
        marker = output_dir / ".complete"
        if marker.exists():
            frames = sorted(output_dir.glob("frame_*.jpg"))
            if frames:
                return frames

        tmp_dir = output_dir.with_name(f"{output_dir.name}.{os.getpid()}.tmp")
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        fps_text = f"{fps:g}"
        cmd = [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(media_path),
            "-vf",
            f"fps={fps_text}",
            str(tmp_dir / "frame_%06d.jpg"),
        ]
        try:
            subprocess.run(cmd, check=True)
            frames = sorted(tmp_dir.glob("frame_*.jpg"))
            if not frames:
                raise RuntimeError(f"ffmpeg produced no frames for {media_path}")
            if output_dir.exists():
                shutil.rmtree(output_dir)
            tmp_dir.rename(output_dir)
            marker.write_text(json.dumps({"source": str(media_path), "fps": fps}, separators=(",", ":")) + "\n", encoding="utf-8")
            return sorted(output_dir.glob("frame_*.jpg"))
        finally:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)


def build_message(
    row: dict[str, Any],
    repo_root: Path,
    prompt: str,
    fps: float | None,
    max_pixels: int | None,
    total_pixels: int | None,
    video_source: str,
    frame_cache_dir: Path,
) -> list[dict[str, Any]]:
    media_path = (repo_root / row["local_media"]).resolve()
    video_item: dict[str, Any] = {"type": "video"}
    if video_source == "frames":
        if fps is None or fps <= 0:
            raise ValueError("--fps must be positive when --video-source frames")
        frame_dir = frame_cache_dir / row["video_id"]
        frames = extract_video_frames(media_path, frame_dir, fps)
        video_item["video"] = [frame.as_uri() for frame in frames]
        video_item["sample_fps"] = fps
    else:
        video_item["video"] = media_path.as_uri()
    if fps is not None:
        video_item["fps"] = fps
    if max_pixels is not None:
        video_item["max_pixels"] = max_pixels
    if total_pixels is not None:
        video_item["total_pixels"] = total_pixels
    return [
        {
            "role": "user",
            "content": [
                video_item,
                {"type": "text", "text": prompt},
            ],
        }
    ]


def load_model(model_id: str, dtype: str, device_map: str, attn_implementation: str | None):
    from transformers import AutoProcessor

    if "qwen3.5" in model_id.casefold():
        try:
            from transformers import AutoModelForMultimodalLM

            model_cls = AutoModelForMultimodalLM
        except ImportError:
            from transformers import Qwen3_5ForConditionalGeneration

            model_cls = Qwen3_5ForConditionalGeneration
    else:
        try:
            if "qwen3-vl-30b" in model_id.casefold() or "qwen3_vl_moe" in model_id.casefold():
                from transformers import Qwen3VLMoeForConditionalGeneration

                model_cls = Qwen3VLMoeForConditionalGeneration
            else:
                from transformers import Qwen3VLForConditionalGeneration

                model_cls = Qwen3VLForConditionalGeneration
        except ImportError:
            from transformers import AutoModelForImageTextToText

            model_cls = AutoModelForImageTextToText

    kwargs: dict[str, Any] = {"dtype": dtype, "device_map": device_map}
    if attn_implementation:
        kwargs["attn_implementation"] = attn_implementation
    model = model_cls.from_pretrained(model_id, **kwargs)
    processor = AutoProcessor.from_pretrained(model_id)
    return model, processor


def generate_one(
    model: Any,
    processor: Any,
    messages: list[dict[str, Any]],
    max_new_tokens: int,
    temperature: float,
    enable_thinking: bool,
) -> str:
    import torch
    from qwen_vl_utils import process_vision_info

    text = apply_chat_template(processor, messages, enable_thinking=enable_thinking)
    images, videos, video_kwargs = process_vision_info(
        messages,
        image_patch_size=16,
        return_video_kwargs=True,
        return_video_metadata=True,
    )
    if videos is not None:
        videos, video_metadatas = zip(*videos)
        videos = list(videos)
        video_metadatas = list(video_metadatas)
    else:
        video_metadatas = None

    inputs = processor(
        text=text,
        images=images,
        videos=videos,
        video_metadata=video_metadatas,
        return_tensors="pt",
        do_resize=False,
        **video_kwargs,
    )
    inputs = inputs.to(model.device)

    generation_kwargs: dict[str, Any] = {"max_new_tokens": max_new_tokens}
    if temperature > 0:
        generation_kwargs.update({"do_sample": True, "temperature": temperature})
    else:
        generation_kwargs["do_sample"] = False

    with torch.inference_mode():
        generated_ids = model.generate(**inputs, **generation_kwargs)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids, strict=False)
    ]
    return processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]


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
    parser.add_argument("--device-map", default="auto")
    parser.add_argument("--attn-implementation", default=None)
    parser.add_argument("--fps", type=float, default=1.0)
    parser.add_argument("--max-pixels", type=int, default=360 * 420)
    parser.add_argument("--total-pixels", type=int, default=None)
    parser.add_argument("--video-source", choices=["file", "frames"], default="file")
    parser.add_argument("--frame-cache-dir", type=Path, default=Path("runs/qwen3vl_frame_cache_fps1"))
    parser.add_argument("--max-new-tokens", type=int, default=32)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--enable-thinking", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    rows = read_jsonl(args.dataset)
    if args.limit is not None:
        rows = rows[: args.limit]

    prompt = args.prompt_file.read_text(encoding="utf-8") if args.prompt_file else args.prompt

    args.output.parent.mkdir(parents=True, exist_ok=True)
    completed = set() if args.overwrite else read_completed_ids(args.output)
    mode = "w" if args.overwrite else "a"

    model, processor = load_model(args.model_id, args.dtype, args.device_map, args.attn_implementation)
    repo_root = args.repo_root.resolve()

    with args.output.open(mode, encoding="utf-8") as handle:
        for idx, row in enumerate(rows, start=1):
            video_id = row["video_id"]
            if video_id in completed:
                continue
            started = time.perf_counter()
            try:
                item_prompt = build_task_prompt(row, args.task, prompt)
                messages = build_message(
                    row,
                    repo_root,
                    item_prompt,
                    args.fps,
                    args.max_pixels,
                    args.total_pixels,
                    args.video_source,
                    args.frame_cache_dir.resolve(),
                )
                raw_response = generate_one(
                    model,
                    processor,
                    messages,
                    args.max_new_tokens,
                    args.temperature,
                    args.enable_thinking,
                )
                result = {
                    "video_id": video_id,
                    "mode": "full_video_mcq" if args.task == "mcq" else "full_video",
                    "model_id": args.model_id,
                    "predicted_answer": prediction_from_response(raw_response, args.task),
                    "raw_response": raw_response,
                    "prompt": item_prompt,
                    "local_media": row["local_media"],
                    "fps": args.fps,
                    "max_pixels": args.max_pixels,
                    "total_pixels": args.total_pixels,
                    "video_source": args.video_source,
                    "frame_cache_dir": str(args.frame_cache_dir) if args.video_source == "frames" else "",
                    "latency_sec": round(time.perf_counter() - started, 3),
                    "status": "ok",
                }
            except Exception as exc:
                if not args.continue_on_error:
                    raise
                result = {
                    "video_id": video_id,
                    "mode": "full_video_mcq" if args.task == "mcq" else "full_video",
                    "model_id": args.model_id,
                    "predicted_answer": "",
                    "raw_response": "",
                    "prompt": build_task_prompt(row, args.task, prompt),
                    "local_media": row.get("local_media", ""),
                    "fps": args.fps,
                    "max_pixels": args.max_pixels,
                    "total_pixels": args.total_pixels,
                    "video_source": args.video_source,
                    "frame_cache_dir": str(args.frame_cache_dir) if args.video_source == "frames" else "",
                    "latency_sec": round(time.perf_counter() - started, 3),
                    "status": "error",
                    "error": repr(exc),
                }
            handle.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            print(f"[{idx}/{len(rows)}] {video_id}: {result['predicted_answer']!r} ({result['status']})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
