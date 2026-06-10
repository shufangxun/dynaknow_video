#!/usr/bin/env python3
"""Build dynamic-knowledge cards from existing DynaKnow samples.

The card is an intermediate review object:

video -> visible dynamic process -> candidate mechanisms -> selected mechanism
-> knowledge point -> verifier flags -> pass/review/fail critique.

This script does not perform fresh vision inference. It uses the repository's
existing sample annotations, shortcut labels, taxonomy, audit decisions, and
optional source-grounding notes to make the dynamic-knowledge review surface
explicit.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import mimetypes
import os
import re
from collections import Counter, defaultdict
from pathlib import Path


DECISION_LABELS = {
    "mechanism_keep": "pass",
    "mechanism_review": "review",
    "mechanism_reject_or_rewrite": "fail",
    "accept": "pass",
    "revise": "review",
    "reject": "fail",
}
DECISION_ORDER = {"pass": 0, "review": 1, "fail": 2, "unknown": 3}
CHOICE_KEYS = ["A", "B", "C", "D"]

DESCRIPTIVE_PATTERNS = [
    re.compile(r"\bthe .{0,40}(falls?|moves?|changes?|grows?|sprouts?|burns?|operates?)\b", re.IGNORECASE),
    re.compile(r"\bseeds? sprout\b", re.IGNORECASE),
    re.compile(r"\bplants? grows?\b", re.IGNORECASE),
    re.compile(r"\bliquids? changes? colo[u]?r\b", re.IGNORECASE),
    re.compile(r"\bsome (chemical )?reactions?\b", re.IGNORECASE),
    re.compile(r"\bsome mixtures?\b", re.IGNORECASE),
    re.compile(r"\bthis video\b", re.IGNORECASE),
]
WEAK_MECHANISM_PATTERNS = [
    re.compile(r"\bcan cause (a )?(change|movement|effect)\b", re.IGNORECASE),
    re.compile(r"\bchange shape\b", re.IGNORECASE),
    re.compile(r"\bvisible change\b", re.IGNORECASE),
]
MECHANISM_TERMS_BY_DOMAIN = {
    "physics_physical_systems": [
        "gravity",
        "momentum",
        "energy",
        "pressure",
        "buoyancy",
        "surface tension",
        "capillary",
        "thermal expansion",
        "magnetic",
        "electric",
        "field",
        "current",
        "lorentz",
        "eddy",
        "oscillation",
        "elastic",
        "center of mass",
        "torque",
    ],
    "chemistry_materials_change": [
        "reaction",
        "redox",
        "indicator",
        "oxygen",
        "reduce",
        "reduction",
        "oxid",
        "precipitate",
        "crystallization",
        "crystal growth",
        "nucleation",
        "supersaturated",
        "supersaturation",
        "combustion",
        "ignition",
        "gas",
        "bubble",
        "bubbles",
        "decomposition",
        "catalytic",
        "ions",
        "solubility",
        "diffusion",
        "concentration",
        "transport",
        "dye",
        "melting",
        "phase",
        "copper",
        "iodine",
        "deformation",
        "compression",
        "viscoelastic",
        "non-newtonian",
        "elastic",
        "strain",
        "load",
    ],
    "biology_living_systems": [
        "phototaxis",
        "taxis",
        "orientation",
        "light",
        "phototropism",
        "gravitropism",
        "thigmotropism",
        "seismonasty",
        "nastic",
        "thigmonasty",
        "photonasty",
        "pulvinus",
        "pulvini",
        "leaflet",
        "touch",
        "germination",
        "transpiration",
        "capillary",
        "absorption",
        "differential growth",
        "stimulus",
        "emergence",
        "petal",
        "gait",
        "locomotion",
        "trail",
        "contraction",
        "propulsion",
        "anchoring",
        "water uptake",
        "hydration",
        "rehydration",
        "turgor",
        "frond",
    ],
    "earth_environmental_systems": [
        "erosion",
        "deposition",
        "transport",
        "debris",
        "sediment",
        "downslope",
        "lava",
        "volcanic",
        "molten",
        "solidifying",
        "convection",
        "updraft",
        "condensation",
        "wind shear",
        "freeze-thaw",
        "avalanche",
        "snow",
        "mass movement",
        "slope",
        "gravity",
        "hydrology",
        "phenology",
        "atmospheric",
        "flow",
        "wind",
        "tidal",
        "tide",
        "hydraulic",
        "gradient",
        "cloud",
        "runoff",
        "meander",
        "bank",
        "point-bar",
        "glacier",
        "calving",
        "fracture",
        "predator",
        "prey",
        "capture",
        "predation",
        "interaction",
        "contact",
    ],
    "engineering_operational_systems": [
        "filter",
        "filtration",
        "pressure gradient",
        "pressure",
        "percolate",
        "separation",
        "sorting",
        "segregation",
        "settling",
        "control",
        "force",
        "stabilize",
        "backwashing",
        "pump",
        "pumping",
        "laminar",
        "shear",
        "valve",
        "cutting",
        "tool",
        "workpiece",
        "flow",
        "turbulent",
        "hydraulic",
        "jet",
        "torque",
        "spray",
        "mixing",
        "stirring",
        "dispersion",
        "circulation",
        "vortex",
        "hydrophobic",
        "wetting",
        "droplet",
        "adhesion",
        "crank",
        "linkage",
        "actuation",
        "mechanism",
        "escapement",
        "gear",
        "heat",
        "heating",
        "thermal",
        "temperature",
        "plastic",
        "deform",
        "malleability",
        "ductile",
        "ductility",
        "forging",
        "hammer",
        "energy",
    ],
}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def read_csv(path: Path | None) -> list[dict[str, str]]:
    if path is None or not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def label(value: str) -> str:
    return value.replace("_", " ")


def pct(value: int, total: int) -> str:
    return "0.0%" if total == 0 else f"{100.0 * value / total:.1f}%"


def canonical_key(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower()).rstrip(".")


def decision_label(value: str) -> str:
    return DECISION_LABELS.get(value, value or "unknown")


def split_tags(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value or "").replace(";", ",").split(",") if item.strip()]


def rel_url(path: str | Path, output: Path, root: Path) -> str:
    source = Path(path)
    if not source.is_absolute():
        source = root / source
    return esc(os.path.relpath(source, start=output.parent))


def media_type(path: str) -> str:
    guessed, _ = mimetypes.guess_type(path)
    if guessed:
        return guessed
    suffix = Path(path).suffix.lower()
    if suffix == ".ogv":
        return "video/ogg"
    if suffix == ".webm":
        return "video/webm"
    if suffix == ".mp4":
        return "video/mp4"
    return "video/*"


def taxonomy_by_knowledge(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["knowledge_point"]: row for row in rows if row.get("knowledge_point")}


def audit_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["video_id"]: row for row in rows if row.get("video_id")}


def source_audit_by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["video_id"]: row for row in rows if row.get("video_id")}


def first_evidence_text(sample: dict) -> str:
    evidence = sample.get("dynamic_evidence", [])
    if isinstance(evidence, list) and evidence:
        return str(evidence[0].get("description", ""))
    return ""


def has_temporal_span(sample: dict) -> bool:
    for span in sample.get("dynamic_evidence", []):
        start = span.get("start_sec")
        end = span.get("end_sec")
        if isinstance(start, (int, float)) and isinstance(end, (int, float)) and end > start:
            return True
    return False


def selected_choice(sample: dict, knowledge_point: str) -> str:
    choices = sample.get("choices", {})
    answer = sample.get("answer", "")
    if isinstance(choices, dict) and answer in choices:
        return str(choices[answer])
    return knowledge_point


def candidate_mechanisms(sample: dict) -> list[str]:
    choices = sample.get("choices", {})
    if not isinstance(choices, dict):
        return []
    return [str(choices.get(key, "")).strip() for key in CHOICE_KEYS if str(choices.get(key, "")).strip()]


def answer_index(samples: list[dict]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for sample in samples:
        point = str(sample.get("knowledge_point", "")).strip()
        video_id = str(sample.get("video_id", "")).strip()
        if point and video_id:
            index[canonical_key(point)].append(video_id)
    return index


def option_length_cue(correct: str, distractors: list[str]) -> bool:
    if not distractors:
        return True
    correct_words = len(correct.split())
    distractor_words = [len(item.split()) for item in distractors if item]
    if not distractor_words:
        return True
    avg = sum(distractor_words) / len(distractor_words)
    if avg == 0:
        return True
    return correct_words / avg > 1.8 or avg / max(correct_words, 1) > 1.8


def distractor_check(sample: dict, all_answers: dict[str, list[str]]) -> dict[str, object]:
    choices = sample.get("choices", {})
    answer = sample.get("answer", "")
    if not isinstance(choices, dict) or answer not in choices:
        return {
            "hard_negative_status": "fail",
            "copied_from_other_sample_answer": [],
            "answer_only_elimination_risk": True,
            "choice_count": 0,
            "notes": ["missing choices or answer key"],
        }

    correct = str(choices.get(answer, "")).strip()
    distractors: list[tuple[str, str]] = [
        (key, str(choices.get(key, "")).strip())
        for key in CHOICE_KEYS
        if key != answer and str(choices.get(key, "")).strip()
    ]
    copied = []
    weak = []
    for key, text in distractors:
        owners = [owner for owner in all_answers.get(canonical_key(text), []) if owner != sample.get("video_id")]
        if owners:
            copied.append({"choice": key, "copied_from_video_ids": owners, "text": text})
        if descriptive_match(text) or weak_match(text):
            weak.append({"choice": key, "text": text})

    texts = [correct, *[text for _, text in distractors]]
    duplicate_text = len(texts) != len({canonical_key(text) for text in texts})
    length_cue = option_length_cue(correct, [text for _, text in distractors])
    missing_distractors = len(distractors) != 3
    answer_only_risk = bool(copied or weak or duplicate_text or length_cue or missing_distractors)
    if copied or duplicate_text or missing_distractors:
        status = "fail"
    elif weak or length_cue:
        status = "review"
    else:
        status = "pass"

    notes: list[str] = []
    if copied:
        notes.append("one or more distractors exactly copy another sample's correct knowledge point")
    if weak:
        notes.append("one or more distractors are broad, descriptive, or weakly mechanistic")
    if duplicate_text:
        notes.append("choices contain duplicate or near-duplicate text")
    if length_cue:
        notes.append("correct answer length is noticeably different from distractors")
    if missing_distractors:
        notes.append("expected exactly three distractors")
    if not notes:
        notes.append("distractors are target-specific hard negatives under deterministic checks")

    return {
        "hard_negative_status": status,
        "copied_from_other_sample_answer": copied,
        "weak_distractors": weak,
        "answer_only_elimination_risk": answer_only_risk,
        "choice_count": len(texts),
        "notes": notes,
    }


def mechanism_terms(domain: str, text: str) -> list[str]:
    normalized = text.lower()
    matched = []
    for term in MECHANISM_TERMS_BY_DOMAIN.get(domain, []):
        escaped = re.escape(term.lower())
        if term in {"oxid"}:
            found = re.search(rf"\b{escaped}", normalized) is not None
        else:
            found = re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", normalized) is not None
        if found:
            matched.append(term)
    return matched


def descriptive_match(text: str) -> str:
    for pattern in DESCRIPTIVE_PATTERNS:
        if pattern.search(text):
            return pattern.pattern
    return ""


def weak_match(text: str) -> str:
    for pattern in WEAK_MECHANISM_PATTERNS:
        if pattern.search(text):
            return pattern.pattern
    return ""


def infer_domain_subdomain(sample: dict, audit: dict, taxonomy: dict[str, dict[str, str]], knowledge_point: str) -> tuple[str, str]:
    tax = taxonomy.get(knowledge_point, {})
    domain = audit.get("domain") or sample.get("domain") or tax.get("domain") or sample.get("category") or "unmapped"
    subdomain = audit.get("subdomain") or sample.get("subdomain") or tax.get("subdomain") or "unmapped"
    return str(domain), str(subdomain)


def duplicate_groups(samples: list[dict], audits: dict[str, dict[str, str]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for sample in samples:
        video_id = sample["video_id"]
        audit = audits.get(video_id, {})
        kp = audit.get("knowledge_point") or sample.get("knowledge_point", "")
        groups[canonical_key(kp)].append(video_id)
    return groups


def verifier_flags(sample: dict, audit: dict, domain: str, knowledge_point: str, duplicate_count: int) -> dict[str, object]:
    shortcut = sample.get("shortcut_labels", {})
    risk_tags = split_tags(audit.get("risk_tags") or sample.get("risk_tags", []))
    evidence_text = first_evidence_text(sample)
    terms = mechanism_terms(domain, knowledge_point)
    descriptive = descriptive_match(knowledge_point)
    weak = weak_match(knowledge_point)
    source_only_risk = any(
        tag in risk_tags
        for tag in [
            "source_only_mechanism",
            "source_grounding_needed",
            "needs_reagent_review",
            "weak_visual_anchor",
            "weak_mechanism_anchor",
        ]
    )
    hidden_assumption_risk = source_only_risk or any(
        tag in risk_tags
        for tag in [
            "specialist_context",
            "weak_visual_anchor",
            "weak_mechanism_anchor",
            "hidden_stimulus_risk",
            "hidden_charge_mechanism_risk",
        ]
    )
    leakage_risk = any(
        token in tag
        for tag in risk_tags
        for token in ["ocr", "text_leakage", "caption", "subtitle"]
    )
    shortcut_risk = (
        shortcut.get("single_frame_sufficient") not in {"no", "pass"}
        or any("single_frame" in tag or "static" in tag or "final_state" in tag for tag in risk_tags)
    )
    return {
        "visible_temporal_process": has_temporal_span(sample) and len(evidence_text) >= 10,
        "single_frame_blocked": shortcut.get("single_frame_sufficient") in {"no", "pass"},
        "mechanism_level_wording": bool(terms) and not descriptive,
        "not_just_event_description": not descriptive,
        "not_weak_generic_mechanism": not weak,
        "source_grounding_is_bounded": not source_only_risk,
        "no_hidden_assumption_risk": not hidden_assumption_risk,
        "no_leakage_risk": not leakage_risk,
        "no_shortcut_risk": not shortcut_risk,
        "duplicate_group_size": duplicate_count,
        "domain_mechanism_terms": terms,
        "descriptive_pattern": descriptive,
        "weak_pattern": weak,
        "risk_tags": risk_tags,
    }


def source_text_check(source_row: dict[str, str], audit: dict, flags: dict[str, object]) -> dict[str, object]:
    note = source_row.get("source_grounding_note", "")
    risk_tags = set(split_tags(audit.get("risk_tags") or source_row.get("risk_tags", "")))
    note_lower = note.lower()
    explicitly_not_used = any(
        phrase in note_lower
        for phrase in [
            "not used as release evidence",
            "source text is not used",
            "source is not used",
            "keep source out of evaluation input",
        ]
    )
    confirms = any(
        phrase in note_lower
        for phrase in [
            "source identifies",
            "source and video anchor",
            "source filename and visual process identify",
            "source filename and visible process identify",
            "video visibly anchors",
            "passes with source grounding",
            "passes both steps",
        ]
    )
    source_requested = any(
        tag in risk_tags
        for tag in [
            "source_grounded_chemistry",
            "source_grounding_needed",
            "needs_reagent_review",
        ]
    )
    needs_review = any(
        tag in risk_tags
        for tag in [
            "source_grounding_needed",
            "needs_reagent_review",
            "source_title_names_process",
            "source_title_names_mechanism",
            "source_title_names_phenomenon",
            "title_names_phenomenon",
            "caption_names_co2",
        ]
    ) or "needs verification" in note_lower or "needs timing/source review" in note_lower
    source_only = any(
        tag in risk_tags
        for tag in ["specialist_context", "weak_visual_anchor", "weak_mechanism_anchor"]
    )
    leakage = any(
        token in tag
        for tag in risk_tags
        for token in ["caption", "ocr", "text_leakage", "subtitle"]
    )

    if source_only:
        support_status = "source_only_or_hidden"
    elif explicitly_not_used:
        support_status = "descriptive_only_not_used"
    elif needs_review:
        support_status = "needs_review"
    elif confirms:
        support_status = "confirmed"
    elif note:
        support_status = "descriptive_only_not_used"
    else:
        support_status = "not_recorded"

    video_anchor_ok = bool(flags.get("visible_temporal_process")) and bool(flags.get("mechanism_level_wording"))
    if source_only:
        alignment_status = "source_claim_not_visually_anchored"
    elif leakage and source_requested:
        alignment_status = "source_or_text_leakage_risk"
    elif video_anchor_ok and support_status == "confirmed":
        alignment_status = "video_and_source_agree"
    elif video_anchor_ok and support_status in {"descriptive_only_not_used", "not_recorded"}:
        alignment_status = "video_primary_source_not_used"
    else:
        alignment_status = "needs_review"

    if support_status == "confirmed":
        source_role = "confirm_mechanism_identity"
    elif support_status == "needs_review":
        source_role = "needs_human_source_check"
    elif support_status == "source_only_or_hidden":
        source_role = "reject_source_only_mechanism"
    elif support_status == "descriptive_only_not_used":
        source_role = "not_used_no_knowledge"
    else:
        source_role = "not_recorded"

    return {
        "support_status": support_status,
        "alignment_status": alignment_status,
        "source_role": source_role,
        "source_grounding_note": note,
        "source_risk_tags": sorted(risk_tags),
        "requires_human_source_review": support_status in {"needs_review", "source_only_or_hidden"} or leakage,
    }


def source_grounding_summary(source_check: dict[str, object]) -> str:
    status = str(source_check.get("support_status", ""))
    note = str(source_check.get("source_grounding_note", "")).strip()
    if status == "confirmed":
        return note or "Source text confirms the mechanism identity, and the video visibly anchors it."
    if status == "descriptive_only_not_used":
        return "Source page has no usable mechanism text; source is not used as knowledge evidence."
    if status == "needs_review":
        return "Source text needs human double-check before it can be used as mechanism evidence."
    if status == "source_only_or_hidden":
        return "Source text appears to supply a hidden or weakly visible mechanism; source is not release evidence."
    return "No usable source mechanism evidence recorded."


def critic_notes(
    decision: str,
    flags: dict[str, object],
    source_check: dict[str, object],
    qa_check: dict[str, object],
    audit_reason: str,
) -> list[str]:
    notes: list[str] = []
    if not flags["visible_temporal_process"]:
        notes.append("no solid temporal evidence span recorded")
    if not flags["single_frame_blocked"]:
        notes.append("single-frame shortcut is not cleanly blocked")
    if not flags["not_just_event_description"]:
        notes.append("knowledge point reads like an event/phenomenon description")
    if not flags["mechanism_level_wording"]:
        notes.append("knowledge point lacks a strong domain mechanism term")
    if not flags["not_weak_generic_mechanism"]:
        notes.append("knowledge point may be too generic or weakly causal")
    if not flags["source_grounding_is_bounded"]:
        notes.append("source/title grounding may be doing too much work")
    if source_check["support_status"] == "needs_review":
        notes.append("source text needs human double-check")
    if source_check["support_status"] == "source_only_or_hidden":
        notes.append("source text appears to supply hidden mechanism")
    if decision != "pass" and source_check["support_status"] == "descriptive_only_not_used":
        notes.append("source text is broad/descriptive, not used as knowledge evidence")
    if source_check["alignment_status"] == "source_or_text_leakage_risk":
        notes.append("source/title/text may leak the answer")
    if qa_check["hard_negative_status"] == "fail":
        notes.append("distractors fail hard-negative checks")
    elif qa_check["hard_negative_status"] == "review":
        notes.append("distractors need hard-negative review")
    if not flags["no_hidden_assumption_risk"]:
        notes.append("hidden assumption or weak visual-anchor risk")
    if not flags["no_leakage_risk"]:
        notes.append("text/OCR/title/caption leakage risk")
    if not flags["no_shortcut_risk"]:
        notes.append("static/final-state shortcut risk")
    if int(flags["duplicate_group_size"]) > 1:
        notes.append(f"duplicate mechanism group has {flags['duplicate_group_size']} videos")
    if decision == "pass" and notes:
        notes.insert(0, "pass but needs scrutiny")
    if decision == "review" and not notes:
        notes.append("review due to audit policy; no deterministic issue found")
    if decision == "fail" and audit_reason:
        notes.append(f"audit says: {audit_reason}")
    return notes


def build_cards(
    samples: list[dict],
    audit_rows: list[dict[str, str]],
    taxonomy_rows: list[dict[str, str]],
    source_audit_rows: list[dict[str, str]],
) -> list[dict]:
    audits = audit_by_id(audit_rows)
    source_audits = source_audit_by_id(source_audit_rows)
    taxonomy = taxonomy_by_knowledge(taxonomy_rows)
    duplicates = duplicate_groups(samples, audits)
    all_answers = answer_index(samples)
    cards = []
    for sample in samples:
        video_id = sample["video_id"]
        audit = audits.get(video_id, {})
        knowledge_point = audit.get("knowledge_point") or sample.get("knowledge_point", "")
        domain, subdomain = infer_domain_subdomain(sample, audit, taxonomy, knowledge_point)
        decision = decision_label(audit.get("filter_decision") or sample.get("review_status", ""))
        key = canonical_key(knowledge_point)
        flags = verifier_flags(sample, audit, domain, knowledge_point, len(duplicates.get(key, [])))
        source_check = source_text_check(source_audits.get(video_id, {}), audit, flags)
        qa_check = distractor_check(sample, all_answers)
        flags["hard_negative_quality"] = qa_check["hard_negative_status"] == "pass"
        notes = critic_notes(decision, flags, source_check, qa_check, audit.get("reason", ""))
        evidence = sample.get("dynamic_evidence", [])
        card = {
            "video_id": video_id,
            "filter_decision": decision,
            "domain": domain,
            "subdomain": subdomain,
            "local_media": audit.get("local_media") or sample.get("local_media", ""),
            "source_url": audit.get("source_url") or sample.get("source_url", ""),
            "visible_dynamic_process": first_evidence_text(sample),
            "temporal_evidence": evidence,
            "single_frame_failure": sample.get("static_insufficient_reason", ""),
            "video_anchor_check": {
                "visible_temporal_process": flags["visible_temporal_process"],
                "single_frame_blocked": flags["single_frame_blocked"],
                "mechanism_level_wording": flags["mechanism_level_wording"],
                "not_just_event_description": flags["not_just_event_description"],
                "no_shortcut_risk": flags["no_shortcut_risk"],
            },
            "source_text_check": source_check,
            "distractor_check": qa_check,
            "candidate_mechanisms": candidate_mechanisms(sample),
            "selected_mechanism": selected_choice(sample, knowledge_point),
            "knowledge_point": knowledge_point,
            "canonical_knowledge_point": key,
            "source_grounding": source_grounding_summary(source_check),
            "verifier_flags": flags,
            "critic_notes": notes,
            "audit_reason": audit.get("reason", ""),
        }
        cards.append(card)
    return cards


def write_jsonl(cards: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for card in cards:
            handle.write(json.dumps(card, ensure_ascii=False, separators=(",", ":")) + "\n")


def badge(text: str, class_name: str) -> str:
    return f'<span class="badge {esc(class_name)}">{esc(text)}</span>'


def render_video(card: dict, output: Path, root: Path) -> str:
    local_media = card.get("local_media", "")
    if not local_media:
        return '<div class="missing">No local media path.</div>'
    src = rel_url(local_media, output, root)
    poster = root / "media" / "frames" / card["video_id"] / "middle.jpg"
    poster_attr = f' poster="{rel_url(poster, output, root)}"' if poster.exists() else ""
    return (
        f"<video controls preload=\"metadata\"{poster_attr}>"
        f'<source src="{src}" type="{esc(media_type(local_media))}">'
        f'<a href="{src}">Open video</a>'
        "</video>"
    )


def render_list(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def render_flags(flags: dict[str, object]) -> str:
    primary = [
        ("temporal", flags["visible_temporal_process"]),
        ("single-frame blocked", flags["single_frame_blocked"]),
        ("mechanism wording", flags["mechanism_level_wording"]),
        ("not event desc", flags["not_just_event_description"]),
        ("hard negatives", flags.get("hard_negative_quality", False)),
        ("bounded source", flags["source_grounding_is_bounded"]),
        ("no leakage", flags["no_leakage_risk"]),
        ("no shortcut", flags["no_shortcut_risk"]),
    ]
    return "".join(badge(name, "ok" if value else "bad") for name, value in primary)


def render_source_check(check: dict[str, object]) -> str:
    status = str(check.get("support_status", ""))
    alignment = str(check.get("alignment_status", ""))
    role = str(check.get("source_role", ""))
    review = bool(check.get("requires_human_source_review"))
    cls = "bad" if review or "hidden" in status or "leakage" in alignment else "ok"
    note = str(check.get("source_grounding_note", ""))
    summary = source_grounding_summary(check)
    note_label = "Audit note"
    if status == "descriptive_only_not_used":
        note_label = "Audit note, not evidence"
    return (
        '<div class="chips">'
        f'{badge("source: " + status, cls)}'
        f'{badge("alignment: " + alignment, cls)}'
        f'{badge("role: " + role, cls)}'
        "</div>"
        f"<p>{esc(summary)}</p>"
        + (f"<p><strong>{esc(note_label)}:</strong> {esc(note)}</p>" if note else "")
    )


def render_distractor_check(check: dict[str, object]) -> str:
    status = str(check.get("hard_negative_status", ""))
    cls = "ok" if status == "pass" else "bad" if status == "fail" else "risk"
    copied = check.get("copied_from_other_sample_answer", [])
    weak = check.get("weak_distractors", [])
    notes = check.get("notes", [])
    copied_count = len(copied) if isinstance(copied, list) else 0
    weak_count = len(weak) if isinstance(weak, list) else 0
    return (
        '<div class="chips">'
        f'{badge("hard negatives: " + status, cls)}'
        f'{badge("copied answers: " + str(copied_count), "bad" if copied_count else "ok")}'
        f'{badge("weak distractors: " + str(weak_count), "risk" if weak_count else "ok")}'
        "</div>"
        f"{render_list([str(note) for note in notes])}"
    )


def render_card(card: dict, output: Path, root: Path) -> str:
    decision = card["filter_decision"]
    source = card.get("source_url", "")
    source_link = f'<a href="{esc(source)}">source</a>' if source else ""
    risks = split_tags(card["verifier_flags"].get("risk_tags", []))
    risk_html = "".join(badge(f"risk: {risk}", "risk") for risk in risks)
    terms = card["verifier_flags"].get("domain_mechanism_terms", [])
    terms_html = "".join(badge(f"term: {term}", "term") for term in terms)
    return f"""
    <article class="card status-{esc(decision)}">
      <div class="media">
        {render_video(card, output, root)}
        <p>{source_link}</p>
      </div>
      <div class="body">
        <div class="head">
          <div>
            <h2>{esc(card['video_id'])}</h2>
            <p>{esc(label(card['domain']))} / {esc(label(card['subdomain']))}</p>
          </div>
          {badge(decision, decision)}
        </div>
        <section>
          <h3>Visible Dynamic Process</h3>
          <p>{esc(card['visible_dynamic_process'])}</p>
        </section>
        <section>
          <h3>Selected Knowledge Point</h3>
          <p class="kp">{esc(card['knowledge_point'])}</p>
          <div class="chips">{terms_html}{risk_html}</div>
        </section>
        <section>
          <h3>Verifier Flags</h3>
          <div class="chips">{render_flags(card['verifier_flags'])}</div>
        </section>
        <section>
          <h3>Distractor Quality</h3>
          {render_distractor_check(card.get('distractor_check', {}))}
        </section>
        <section>
          <h3>Source Text Double-Check</h3>
          {render_source_check(card.get('source_text_check', {}))}
        </section>
        <section>
          <h3>Candidate Mechanisms</h3>
          {render_list(card['candidate_mechanisms'])}
        </section>
        <section>
          <h3>Critic Notes</h3>
          {render_list(card['critic_notes'])}
        </section>
      </div>
    </article>
    """


def build_html(cards: list[dict], output: Path, root: Path, title: str) -> str:
    total = len(cards)
    decisions = Counter(card["filter_decision"] for card in cards)
    issue_counts = Counter(note for card in cards for note in card["critic_notes"])
    domain_counts = Counter((card["domain"], card["filter_decision"]) for card in cards)
    distractor_counts = Counter(card.get("distractor_check", {}).get("hard_negative_status", "unknown") for card in cards)
    metric_html = "".join(
        [
            f'<div class="metric"><strong>{total}</strong><span>cards</span></div>',
            f'<div class="metric"><strong>{decisions.get("pass", 0)}</strong><span>pass</span><small>{pct(decisions.get("pass", 0), total)}</small></div>',
            f'<div class="metric"><strong>{decisions.get("review", 0)}</strong><span>review</span><small>{pct(decisions.get("review", 0), total)}</small></div>',
            f'<div class="metric"><strong>{decisions.get("fail", 0)}</strong><span>fail</span><small>{pct(decisions.get("fail", 0), total)}</small></div>',
            f'<div class="metric"><strong>{distractor_counts.get("pass", 0)}</strong><span>hard-negative pass</span><small>{pct(distractor_counts.get("pass", 0), total)}</small></div>',
            f'<div class="metric"><strong>{len(issue_counts)}</strong><span>critic issue types</span></div>',
        ]
    )
    issue_rows = "".join(
        f"<tr><td>{esc(issue)}</td><td class=\"num\">{count}</td></tr>"
        for issue, count in issue_counts.most_common()
    )
    domain_rows = []
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for (domain, decision), count in domain_counts.items():
        grouped[domain][decision] = count
    for domain in sorted(grouped):
        counts = grouped[domain]
        domain_rows.append(
            "<tr>"
            f"<td>{esc(label(domain))}</td>"
            f'<td class="num">{sum(counts.values())}</td>'
            f'<td class="num pass">{counts.get("pass", 0)}</td>'
            f'<td class="num review">{counts.get("review", 0)}</td>'
            f'<td class="num fail">{counts.get("fail", 0)}</td>'
            "</tr>"
        )
    sorted_cards = sorted(cards, key=lambda card: (DECISION_ORDER.get(card["filter_decision"], 99), card["domain"], card["video_id"]))
    cards_html = "".join(render_card(card, output, root) for card in sorted_cards)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    :root {{
      --bg: #f7f7f4;
      --panel: #fff;
      --ink: #202124;
      --muted: #626660;
      --line: #d8d8d0;
      --pass: #276749;
      --review: #986200;
      --fail: #a23a3a;
      --soft-pass: #e5f3eb;
      --soft-review: #fff0d2;
      --soft-fail: #f8e2e2;
      --soft-risk: #edf0f4;
      --accent: #17695e;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: Arial, Helvetica, sans-serif; line-height: 1.45; }}
    header {{ background: #fff; border-bottom: 1px solid var(--line); position: sticky; top: 0; z-index: 2; }}
    .wrap {{ max-width: 1360px; margin: 0 auto; padding: 18px 20px; }}
    h1 {{ margin: 0 0 5px; font-size: 24px; letter-spacing: 0; }}
    h2 {{ margin: 0 0 3px; font-size: 18px; letter-spacing: 0; }}
    h3 {{ margin: 0 0 6px; font-size: 14px; letter-spacing: 0; }}
    .summary {{ margin: 0; color: var(--muted); font-size: 14px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin: 18px 0; }}
    .metric, .panel, .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; }}
    .metric {{ padding: 13px; }}
    .metric strong {{ display: block; font-size: 24px; }}
    .metric span, .metric small {{ display: block; color: var(--muted); font-size: 12px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }}
    .panel {{ padding: 14px; overflow: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 8px 7px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); background: #f0f0eb; }}
    .num {{ width: 72px; white-space: nowrap; text-align: right; }}
    .pass {{ color: var(--pass); }}
    .review {{ color: var(--review); }}
    .fail {{ color: var(--fail); }}
    .card {{ display: grid; grid-template-columns: minmax(320px, 42%) minmax(0, 1fr); gap: 16px; padding: 14px; margin-bottom: 16px; }}
    .status-pass {{ border-left: 5px solid var(--pass); }}
    .status-review {{ border-left: 5px solid var(--review); }}
    .status-fail {{ border-left: 5px solid var(--fail); }}
    video {{ width: 100%; max-height: 420px; background: #111; border-radius: 6px; display: block; }}
    .missing {{ border: 1px dashed var(--line); border-radius: 6px; padding: 24px; color: var(--muted); }}
    a {{ color: var(--accent); font-weight: 700; }}
    .head {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; margin-bottom: 10px; }}
    .head p {{ margin: 0; color: var(--muted); font-size: 13px; }}
    section {{ margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--line); }}
    section p {{ margin: 0; }}
    .kp {{ font-weight: 700; }}
    ul {{ margin: 0; padding-left: 18px; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .badge {{ display: inline-block; border-radius: 999px; padding: 3px 8px; font-size: 12px; font-weight: 700; white-space: nowrap; }}
    .badge.pass, .badge.ok {{ background: var(--soft-pass); color: var(--pass); }}
    .badge.review {{ background: var(--soft-review); color: var(--review); }}
    .badge.fail, .badge.bad {{ background: var(--soft-fail); color: var(--fail); }}
    .badge.risk, .badge.term {{ background: var(--soft-risk); color: var(--muted); }}
    @media (max-width: 1000px) {{
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .grid, .card {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>{esc(title)}</h1>
      <p class="summary">Dynamic Knowledge Card: video evidence -> source text double-check -> candidate mechanisms -> selected mechanism -> critic flags.</p>
    </div>
  </header>
  <main class="wrap">
    <section class="metrics">{metric_html}</section>
    <section class="grid">
      <section class="panel"><h2>Domain Decisions</h2><table><thead><tr><th>Domain</th><th class="num">Total</th><th class="num">Pass</th><th class="num">Review</th><th class="num">Fail</th></tr></thead><tbody>{''.join(domain_rows)}</tbody></table></section>
      <section class="panel"><h2>Critic Issue Types</h2><table><thead><tr><th>Issue</th><th class="num">Count</th></tr></thead><tbody>{issue_rows}</tbody></table></section>
    </section>
    {cards_html}
  </main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--taxonomy", type=Path, default=Path("data/domain_taxonomy_v1.csv"))
    parser.add_argument("--source-audit", type=Path, help="CSV with source_grounding_note keyed by video_id.")
    parser.add_argument("--output-jsonl", required=True, type=Path)
    parser.add_argument("--output-html", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--title", default="DynaKnow-Video Dynamic Knowledge Cards")
    args = parser.parse_args()

    samples = read_jsonl(args.samples)
    audit_rows = read_csv(args.audit)
    taxonomy_rows = read_csv(args.taxonomy)
    source_audit_rows = read_csv(args.source_audit)
    cards = build_cards(samples, audit_rows, taxonomy_rows, source_audit_rows)
    write_jsonl(cards, args.output_jsonl)
    args.output_html.parent.mkdir(parents=True, exist_ok=True)
    args.output_html.write_text(build_html(cards, args.output_html, args.root, args.title), encoding="utf-8")
    print(f"wrote {len(cards)} cards to {args.output_jsonl}")
    print(f"wrote card report to {args.output_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
