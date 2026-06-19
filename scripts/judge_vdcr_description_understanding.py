#!/usr/bin/env python3
"""Judge whether open descriptive predictions capture the gold VDCR mechanism."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


VALID_LABELS = {
    "understands_mechanism",
    "partial_generic",
    "related_but_wrong",
    "wrong",
    "unclear",
}


SYSTEM_PROMPT = """You are a strict but not terminology-only evaluator for a dynamic video concept benchmark.

Decide whether a model's open response demonstrates understanding of the gold dynamic concept, even if it does not use the canonical concept name.

Use this rubric:
- understands_mechanism: The prediction names the gold concept, gives an accepted alias/translation, or describes the key dynamic mechanism specifically enough to distinguish it from nearby mechanisms.
- partial_generic: The prediction identifies only a broad event, object, material, domain, or high-level phenomenon, but misses the distinguishing mechanism. Examples: "chemical reaction" for "Belousov-Zhabotinsky Reaction"; "avalanche" for "Slab Avalanche Release"; "fluid dynamics" for "Rayleigh-Plateau Breakup".
- related_but_wrong: The prediction describes a specific mechanism in the same broad area, but it is not the gold mechanism.
- wrong: The prediction is unrelated or contradicts the gold dynamic concept.
- unclear: The prediction is empty, malformed, or too ambiguous to judge.

Count mechanism understanding, not exact terminology. However, do not give credit for a broad caption that could fit many concepts.
Return only compact JSON with keys: understands, label, confidence, rationale."""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_completed(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    return {row["video_id"]: row for row in read_jsonl(path) if row.get("judge_status") == "ok" and row.get("video_id")}


def build_prompt(gold: dict[str, Any], pred: dict[str, Any]) -> str:
    concept = gold.get("concept", {}) if isinstance(gold.get("concept"), dict) else {}
    aliases = sorted({str(item) for item in [gold.get("answer", ""), *gold.get("accepted_answers", [])] if str(item).strip()})
    evidence = gold.get("dynamic_evidence", [])
    evidence_text = ""
    if isinstance(evidence, list):
        evidence_text = " | ".join(
            str(item.get("description", "")).strip() for item in evidence if isinstance(item, dict) and item.get("description")
        )

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
        "Judge whether model_prediction demonstrates understanding of the gold dynamic mechanism.\n"
        "Credit a precise mechanism description even without the canonical name. Reject broad captions.\n\n"
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
    understands = bool(raw.get("understands", label == "understands_mechanism"))
    if label != "understands_mechanism":
        understands = False
    try:
        confidence = float(raw.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))
    return {
        "understands": understands,
        "label": label,
        "confidence": confidence,
        "rationale": str(raw.get("rationale", "")).strip(),
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


def pct(num: int, den: int) -> str:
    return "0.0%" if den == 0 else f"{100.0 * num / den:.1f}%"


def write_report(path: Path, rows: list[dict[str, Any]], judge_model: str, prediction_path: Path) -> None:
    total = len(rows)
    correct = sum(1 for row in rows if row.get("understands"))
    labels = Counter(str(row.get("label", "unclear")) for row in rows)
    by_domain_total: Counter[str] = Counter()
    by_domain_correct: Counter[str] = Counter()
    by_type_total: Counter[str] = Counter()
    by_type_correct: Counter[str] = Counter()
    for row in rows:
        domain = str(row.get("domain", ""))
        concept_type = str(row.get("concept_type", ""))
        by_domain_total[domain] += 1
        by_domain_correct[domain] += int(bool(row.get("understands")))
        by_type_total[concept_type] += 1
        by_type_correct[concept_type] += int(bool(row.get("understands")))

    lines = ["# VDCR Description-Understanding Judge Score", ""]
    lines.append(f"- predictions: `{prediction_path}`")
    lines.append(f"- judge_model: `{judge_model}`")
    lines.append(f"- predictions judged: {total}")
    lines.append(f"- description understanding accuracy: {correct}/{total} ({pct(correct, total)})")
    lines.append("")
    lines.append("## Labels")
    lines.append("")
    for label in sorted(VALID_LABELS):
        count = labels.get(label, 0)
        lines.append(f"- `{label}`: {count}/{total} ({pct(count, total)})")
    lines.append("")
    lines.append("## Accuracy By Domain")
    lines.append("")
    for domain in sorted(by_domain_total):
        total_for_domain = by_domain_total[domain]
        correct_for_domain = by_domain_correct[domain]
        lines.append(f"- `{domain}`: {correct_for_domain}/{total_for_domain} ({pct(correct_for_domain, total_for_domain)})")
    lines.append("")
    lines.append("## Accuracy By Concept Type")
    lines.append("")
    for concept_type in sorted(by_type_total):
        total_for_type = by_type_total[concept_type]
        correct_for_type = by_type_correct[concept_type]
        lines.append(f"- `{concept_type}`: {correct_for_type}/{total_for_type} ({pct(correct_for_type, total_for_type)})")
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
    parser.add_argument("--max-new-tokens", type=int, default=192)
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
            try:
                raw_text = judge.judge(build_prompt(gold, pred))
                judgment = normalize_judgment(extract_json(raw_text), raw_text)
                result = {
                    "video_id": video_id,
                    "judge_model": args.judge_model,
                    "prediction_path": str(args.predictions),
                    "gold_answer": gold.get("answer", ""),
                    "predicted_answer": pred.get("predicted_answer", ""),
                    "raw_model_response": pred.get("raw_response", ""),
                    "domain": gold.get("domain", ""),
                    "concept_type": gold.get("concept", {}).get("type", "") if isinstance(gold.get("concept"), dict) else "",
                    "judge_status": "ok",
                    **judgment,
                }
            except Exception as exc:
                if not args.continue_on_error:
                    raise
                result = {
                    "video_id": video_id,
                    "judge_model": args.judge_model,
                    "prediction_path": str(args.predictions),
                    "gold_answer": gold.get("answer", ""),
                    "predicted_answer": pred.get("predicted_answer", ""),
                    "raw_model_response": pred.get("raw_response", ""),
                    "domain": gold.get("domain", ""),
                    "concept_type": gold.get("concept", {}).get("type", "") if isinstance(gold.get("concept"), dict) else "",
                    "judge_status": "error",
                    "understands": False,
                    "label": "unclear",
                    "confidence": 0.0,
                    "rationale": "",
                    "raw_judge_response": "",
                    "error": repr(exc),
                }
            handle.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            judged_rows.append(result)
            print(f"[{idx}/{len(pred_rows)}] {video_id}: {result.get('label')} understands={result.get('understands')}")

    final_rows = [row for row in judged_rows if row.get("judge_status") == "ok"]
    write_report(args.report, final_rows, args.judge_model, args.predictions)
    print(f"wrote description judge rows to {args.output}")
    print(f"wrote description judge report to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
