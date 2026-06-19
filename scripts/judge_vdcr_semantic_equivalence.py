#!/usr/bin/env python3
"""Judge semantic equivalence for VDCR open-vocabulary predictions."""

from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any


VALID_LABELS = {
    "equivalent",
    "too_generic",
    "related_but_wrong",
    "wrong",
    "unclear",
}


SYSTEM_PROMPT = """You are a strict evaluator for a dynamic video concept recognition benchmark.

Your job is to decide whether a model prediction names the same dynamic concept as the gold answer.

Use this strict rubric:
- equivalent: The prediction is the same named concept, a listed alias, a standard synonym, a translation, or a very specific mechanism description that unambiguously denotes the same concept.
- too_generic: The prediction is only a broad parent category, surface event, object, material, or visual description. Examples: "chemical reaction" for "Belousov-Zhabotinsky Reaction"; "surface tension" for "Rayleigh-Plateau Breakup"; "cell division" for a more specific mitotic concept.
- related_but_wrong: The prediction is in the same broad area but refers to a different named mechanism/process.
- wrong: The prediction is unrelated or contradicts the gold answer.
- unclear: The prediction is empty, ambiguous, malformed, or impossible to judge.

Do not give credit merely because the answer is plausible for the video. Judge only equivalence to the gold concept.
Return only compact JSON with keys: equivalent, label, confidence, rationale."""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def load_completed(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    rows = read_jsonl(path)
    return {row["video_id"]: row for row in rows if row.get("video_id") and row.get("judge_status") == "ok"}


def build_prompt(gold: dict[str, Any], pred: dict[str, Any]) -> str:
    concept = gold.get("concept", {}) if isinstance(gold.get("concept"), dict) else {}
    aliases = sorted({str(item) for item in [gold.get("answer", ""), *gold.get("accepted_answers", [])] if str(item).strip()})
    evidence = gold.get("dynamic_evidence", [])
    evidence_text = ""
    if isinstance(evidence, list) and evidence:
        descriptions = [str(item.get("description", "")).strip() for item in evidence if isinstance(item, dict)]
        evidence_text = " | ".join(desc for desc in descriptions if desc)

    payload = {
        "gold_answer": gold.get("answer", ""),
        "accepted_aliases": aliases,
        "gold_concept_en": concept.get("en", ""),
        "gold_concept_zh": concept.get("zh", ""),
        "gold_concept_type": concept.get("type", ""),
        "domain": gold.get("domain", ""),
        "subdomain": gold.get("subdomain", ""),
        "dynamic_evidence_summary": evidence_text,
        "model_prediction": pred.get("predicted_answer", ""),
        "raw_model_response": pred.get("raw_response", ""),
    }
    return (
        "Judge whether model_prediction is semantically equivalent to the gold dynamic concept.\n"
        "Remember: broad parent terms, object names, and visual descriptions are not equivalent to a specific named concept.\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


def normalize_judgment(raw: dict[str, Any], raw_text: str) -> dict[str, Any]:
    label = str(raw.get("label", "")).strip().lower()
    if label not in VALID_LABELS:
        label = "unclear"
    equivalent = bool(raw.get("equivalent", label == "equivalent"))
    if label != "equivalent":
        equivalent = False
    try:
        confidence = float(raw.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))
    rationale = str(raw.get("rationale", "")).strip()
    return {
        "equivalent": equivalent,
        "label": label,
        "confidence": confidence,
        "rationale": rationale,
        "raw_judge_response": raw_text,
    }


class LocalTransformersJudge:
    def __init__(self, model_id: str, dtype: str, device_map: str, max_new_tokens: int, temperature: float):
        import torch
        from transformers import AutoProcessor

        try:
            from transformers import Qwen3VLForConditionalGeneration

            model_cls = Qwen3VLForConditionalGeneration
        except ImportError:
            from transformers import AutoModelForImageTextToText

            model_cls = AutoModelForImageTextToText

        self.torch = torch
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = model_cls.from_pretrained(model_id, dtype=dtype, device_map=device_map)
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature

    def judge(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        )
        inputs.pop("token_type_ids", None)
        inputs = inputs.to(self.model.device)
        kwargs: dict[str, Any] = {"max_new_tokens": self.max_new_tokens}
        if self.temperature > 0:
            kwargs.update({"do_sample": True, "temperature": self.temperature})
        else:
            kwargs["do_sample"] = False
        with self.torch.inference_mode():
            generated_ids = self.model.generate(**inputs, **kwargs)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids, strict=False)
        ]
        return self.processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]


def score_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    correct = sum(1 for row in rows if row.get("equivalent"))
    labels = Counter(str(row.get("label", "unclear")) for row in rows)
    by_domain_total: Counter[str] = Counter()
    by_domain_correct: Counter[str] = Counter()
    by_type_total: Counter[str] = Counter()
    by_type_correct: Counter[str] = Counter()
    for row in rows:
        domain = row.get("domain", "")
        concept_type = row.get("concept_type", "")
        by_domain_total[domain] += 1
        by_domain_correct[domain] += int(bool(row.get("equivalent")))
        by_type_total[concept_type] += 1
        by_type_correct[concept_type] += int(bool(row.get("equivalent")))
    return {
        "total": total,
        "correct": correct,
        "accuracy": correct / total if total else 0.0,
        "labels": labels,
        "by_domain_total": by_domain_total,
        "by_domain_correct": by_domain_correct,
        "by_type_total": by_type_total,
        "by_type_correct": by_type_correct,
    }


def pct(num: int, den: int) -> str:
    return "0.0%" if den == 0 else f"{100.0 * num / den:.1f}%"


def write_report(path: Path, rows: list[dict[str, Any]], judge_model: str, prediction_path: Path) -> None:
    summary = score_summary(rows)
    lines = ["# VDCR Semantic-Judge Score", ""]
    lines.append(f"- predictions: `{prediction_path}`")
    lines.append(f"- judge_model: `{judge_model}`")
    lines.append(f"- predictions judged: {summary['total']}")
    lines.append(f"- semantic accuracy: {summary['correct']}/{summary['total']} ({pct(summary['correct'], summary['total'])})")
    lines.append("")
    lines.append("## Labels")
    lines.append("")
    for label in sorted(VALID_LABELS):
        count = summary["labels"].get(label, 0)
        lines.append(f"- `{label}`: {count}/{summary['total']} ({pct(count, summary['total'])})")
    lines.append("")
    lines.append("## Accuracy By Domain")
    lines.append("")
    for domain in sorted(summary["by_domain_total"]):
        total = summary["by_domain_total"][domain]
        correct = summary["by_domain_correct"][domain]
        lines.append(f"- `{domain}`: {correct}/{total} ({pct(correct, total)})")
    lines.append("")
    lines.append("## Accuracy By Concept Type")
    lines.append("")
    for concept_type in sorted(summary["by_type_total"]):
        total = summary["by_type_total"][concept_type]
        correct = summary["by_type_correct"][concept_type]
        lines.append(f"- `{concept_type}`: {correct}/{total} ({pct(correct, total)})")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--judge-model", default="Qwen/Qwen3-VL-8B-Instruct")
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--device-map", default="auto")
    parser.add_argument("--max-new-tokens", type=int, default=160)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    gold_rows = read_jsonl(args.gold)
    pred_rows = read_jsonl(args.predictions)
    if args.limit is not None:
        pred_rows = pred_rows[: args.limit]
    gold_by_id = {row["video_id"]: row for row in gold_rows}
    completed = {} if args.overwrite else load_completed(args.output)
    judged_rows = [] if args.overwrite else list(completed.values())
    completed_ids = set(completed)

    judge = LocalTransformersJudge(args.judge_model, args.dtype, args.device_map, args.max_new_tokens, args.temperature)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if args.overwrite else "a"
    with args.output.open(mode, encoding="utf-8") as handle:
        for idx, pred in enumerate(pred_rows, start=1):
            video_id = pred.get("video_id", "")
            if video_id in completed_ids:
                continue
            gold = gold_by_id.get(video_id)
            if not gold:
                continue
            started = time.perf_counter()
            base = {
                "video_id": video_id,
                "predicted_answer": pred.get("predicted_answer", ""),
                "gold_answer": gold.get("answer", ""),
                "accepted_answers": gold.get("accepted_answers", []),
                "domain": gold.get("domain", ""),
                "concept_type": gold.get("concept", {}).get("type", "") if isinstance(gold.get("concept"), dict) else "",
                "judge_model": args.judge_model,
            }
            try:
                prompt = build_prompt(gold, pred)
                raw_text = judge.judge(prompt)
                judgment = normalize_judgment(extract_json(raw_text), raw_text)
                result = {
                    **base,
                    **judgment,
                    "judge_status": "ok",
                    "latency_sec": round(time.perf_counter() - started, 3),
                }
            except Exception as exc:
                if not args.continue_on_error:
                    raise
                result = {
                    **base,
                    "equivalent": False,
                    "label": "unclear",
                    "confidence": 0.0,
                    "rationale": "",
                    "raw_judge_response": "",
                    "judge_status": "error",
                    "error": repr(exc),
                    "latency_sec": round(time.perf_counter() - started, 3),
                }
            handle.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            judged_rows.append(result)
            print(f"[{idx}/{len(pred_rows)}] {video_id}: {result['label']} equiv={result['equivalent']} pred={result['predicted_answer']!r}")

    final_rows = read_jsonl(args.output)
    write_report(args.report, final_rows, args.judge_model, args.predictions)
    print(f"wrote judgments to {args.output}")
    print(f"wrote report to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
