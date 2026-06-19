# VDCR Output Comparison: Direct Answer vs Constructed MCQ

## Executive Summary

- **MCQ is much easier because the answer space is collapsed to four curated candidates.** The same model only has to select among hard negatives instead of generating the exact benchmark concept name.
- **Direct-answer scoring is intentionally strict.** Exact scoring accepts only normalized gold aliases; semantic judge accepts synonyms/translations only when they name the same dynamic concept, and rejects broad visual labels like `cell division`, `fluid dynamics`, `color change`, or `avalanche` when the gold is more specific.
- **The gap is therefore expected, but it is informative.** MCQ measures video-conditioned discrimination among plausible concepts; direct-answer measures open-vocabulary naming and is much harsher.

## Aggregate Scores

| model | total | direct exact | direct LLM judge | MCQ | MCQ invalid |
|---|---:|---:|---:|---:|---:|
| Qwen3.5 2B | 114 | 0/114 (0.0%) | 0/114 (0.0%) | 60/114 (52.6%) | 0 |
| Qwen3.5 4B | 114 | 2/114 (1.8%) | 1/114 (0.9%) | 65/114 (57.0%) | 0 |
| Qwen3.5 9B | 114 | 1/114 (0.9%) | 1/114 (0.9%) | 71/114 (62.3%) | 10 |
| Qwen3-VL 2B | 114 | 0/114 (0.0%) | 0/114 (0.0%) | 60/114 (52.6%) | 0 |
| Qwen3-VL 4B | 114 | 1/114 (0.9%) | 3/114 (2.6%) | 72/114 (63.2%) | 0 |
| Qwen3-VL 8B | 114 | 0/114 (0.0%) | 1/114 (0.9%) | 74/114 (64.9%) | 0 |

## Evaluation Standards

**Direct exact.** `scripts/score_vdcr_direct_answer.py` normalizes strings with NFKC/casefolding, whitespace and punctuation cleanup, then checks whether the model output exactly matches `answer`, `accepted_answers`, or concept zh/en aliases.

**Direct LLM judge.** `scripts/judge_vdcr_semantic_equivalence.py` asks Qwen3-VL-8B-Instruct to label each prediction as `equivalent`, `too_generic`, `related_but_wrong`, `wrong`, or `unclear`. Only `equivalent=true` counts. The rubric explicitly rejects broad parent terms, object names, and visual descriptions when they do not name the same dynamic concept.

**Constructed MCQ.** `scripts/build_vdcr_mcq_from_direct_answer.py` builds four choices from the direct-answer gold set. Distractors prefer the same domain, same subdomain, and same concept type, while excluding aliases of the correct answer. `scripts/score_vdcr_mcq.py` only scores the selected option letter A-D; invalid or non-letter outputs are wrong.

## Why MCQ Looks Much Higher

1. **Open vocabulary vs closed set:** direct answer requires producing `Rayleigh-Plateau Breakup`; MCQ only requires choosing it if shown next to three alternatives.
2. **Specificity penalty:** many direct outputs are plausible but too broad, e.g. `fluid dynamics`, `cell division`, `color change`, `avalanche`. MCQ can still be correct if the right specific label is present.
3. **Option contrast helps:** the choices often reveal the intended granularity. For example, seeing `Endocytosis`, `Exocytosis`, `Cytoplasmic Streaming`, `Phagocytosis` tells the model the task is a cell-process distinction, not free naming.

## Examples: MCQ Correct While Direct Is Not

| video_id | gold | correct choice | choices | model | direct output | judge label | MCQ output |
|---|---|---|---|---|---|---|---|
| vdcr_000002 | Exocytosis | C | A=Endocytosis; B=Cytoplasmic Streaming; C=Exocytosis; D=Phagocytosis | Qwen3.5 9B | Cell division | related_but_wrong | C: Exocytosis |
| vdcr_000003 | Dzhanibekov Effect / Tennis Racket Theorem | B | A=Gyroscopic Precession; B=Dzhanibekov Effect / Tennis Racket Theorem; C=Brazil Nut Effect; D=Euler's Disk Motion | Qwen3.5 2B | water | wrong | B: Dzhanibekov Effect / Tennis Racket Theorem |
| vdcr_000005 | Double Pendulum Chaos | B | A=Dzhanibekov Effect / Tennis Racket Theorem; B=Double Pendulum Chaos; C=Coupled Pendulum Synchronization; D=Faraday Waves | Qwen3.5 2B | Chaos | too_generic | B: Double Pendulum Chaos |
| vdcr_000008 | Slab Avalanche Release | A | A=Slab Avalanche Release; B=Aa Lava Front Advance; C=Ice Cliff Calving; D=Pahoehoe Lava Roping | Qwen3.5 2B | 雪崩 | too_generic | A: Slab Avalanche Release |
| vdcr_000009 | Belousov-Zhabotinsky Reaction | B | A=Briggs-Rauscher Reaction; B=Belousov-Zhabotinsky Reaction; C=Iodine Clock Reaction; D=Blue Bottle Reaction | Qwen3.5 2B | 混沌 | too_generic | B: Belousov-Zhabotinsky Reaction |
| vdcr_000010 | Pahoehoe Lava Roping | A | A=Pahoehoe Lava Roping; B=Aa Lava Front Advance; C=Slab Avalanche Release; D=Pyroclastic Density Current | Qwen3.5 9B | giving birth | wrong | A: Pahoehoe Lava Roping |
| vdcr_000011 | Ice Cliff Calving | B | A=Pahoehoe Lava Roping; B=Ice Cliff Calving; C=Slab Avalanche Release; D=Aa Lava Front Advance | Qwen3.5 2B | 冰川崩解 | too_generic | B: Ice Cliff Calving |
| vdcr_000012 | Iodine Clock Reaction | B | A=Blue Bottle Reaction; B=Iodine Clock Reaction; C=Belousov-Zhabotinsky Reaction; D=Briggs-Rauscher Reaction | Qwen3.5 2B | 沉淀 | wrong | B: Iodine Clock Reaction |

## Examples: MCQ Still Wrong

| video_id | gold | correct choice | choices | model | MCQ output | direct output |
|---|---|---|---|---|---|---|
| vdcr_000001 | Endocytosis | A | A=Endocytosis; B=Exocytosis; C=Cytoplasmic Streaming; D=Phagocytosis | Qwen3.5 9B | B: Exocytosis | Cellular respiration |
| vdcr_000002 | Exocytosis | C | A=Endocytosis; B=Cytoplasmic Streaming; C=Exocytosis; D=Phagocytosis | Qwen3-VL 8B | B: Cytoplasmic Streaming | 细胞分裂 |
| vdcr_000010 | Pahoehoe Lava Roping | A | A=Pahoehoe Lava Roping; B=Aa Lava Front Advance; C=Slab Avalanche Release; D=Pyroclastic Density Current | Qwen3-VL 8B | B: Aa Lava Front Advance | 火山喷发 |
| vdcr_000012 | Iodine Clock Reaction | B | A=Blue Bottle Reaction; B=Iodine Clock Reaction; C=Belousov-Zhabotinsky Reaction; D=Briggs-Rauscher Reaction | Qwen3-VL 8B | A: Blue Bottle Reaction | 化学反应 |
| vdcr_000017 | Fire-Whirl Vortex Formation | D | A=Wind-Driven Fire-Front Propagation; B=Pyrocumulus Development; C=Buoyancy-Driven Smoke Plume Rise; D=Fire-Whirl Vortex Formation | Qwen3-VL 8B | C: Buoyancy-Driven Smoke Plume Rise | 火势蔓延 |
| vdcr_000023 | Vortex Shedding / Karman Vortex Street | B | A=Kelvin-Helmholtz Instability; B=Vortex Shedding / Karman Vortex Street; C=Hydraulic Jump; D=Cavitation Bubble Growth and Collapse | Qwen3-VL 8B | A: Kelvin-Helmholtz Instability | 光晕 |

## Audit Artifacts

- Full per-item comparison CSV: `reports/vdcr_per_item_model_output_comparison.csv`
- MCQ dataset: `release/v1/dataset_v1_mcq_seed20260619.jsonl`
- Qwen3.5 summary: `reports/vdcr_qwen35_dual_eval_summary.md`
- Combined Qwen3-VL/Qwen3.5 summary: `reports/vdcr_qwen3vl_qwen35_dual_eval_summary.md`
