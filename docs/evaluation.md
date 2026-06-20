# Evaluation

VDCR v1 should be reported with three separate metrics:

```text
open exact naming | open description judge | MCQ recognition
```

These metrics should not be averaged into one score. They measure different
levels of model behavior.

## Open Exact Naming

The model receives the video and the open prompt:

```text
Which named dynamic concept is instantiated by the temporally evolving process in this video?
Return only the short canonical concept name in English or Chinese. Do not explain.
```

Scoring uses alias-normalized exact match against `answer`,
`accepted_answers`, and concept names.

```bash
python3 scripts/score_vdcr_direct_answer.py \
  --gold release/v1/dataset_v1.jsonl \
  --predictions path/to/predictions.jsonl \
  --output reports/score_my_model_direct_exact.md
```

## Open Description Judge

The model describes the visible dynamic mechanism in a concise phrase or
sentence. A judge then decides whether the response names the gold concept or
describes the distinguishing temporal mechanism specifically enough.

Correct responses are labeled `understands_mechanism`. Generic captions such as
`chemical reaction`, `plant movement`, or `avalanche` should not receive credit
when they do not distinguish the target concept.

Use `docs/vdcr_evaluation_granularity.md` for the judge rubric.

## MCQ Recognition

The MCQ file is derived from the direct-answer gold set:

```text
release/v1/dataset_v1_mcq_seed20260619.jsonl
```

Distractors prefer the same domain, subdomain, and concept type when possible.
This metric measures closed-set recognition among plausible concepts, not
open-vocabulary concept recall.

Score MCQ predictions with:

```bash
python3 scripts/score_vdcr_mcq.py \
  --gold release/v1/dataset_v1_mcq_seed20260619.jsonl \
  --predictions path/to/mcq_predictions.jsonl \
  --output reports/score_my_model_mcq.md
```

## Interpretation

Expected ordering is usually:

```text
open exact naming <= open description judge <= MCQ recognition
```

Large gaps are diagnostic:

- low exact naming and higher description judge means the model sees the
  mechanism but lacks the canonical term;
- high MCQ and low open scores means the model benefits from the candidate
  answer set;
- low description judge means the model mostly gives broad captions or nearby
  wrong mechanisms.

The full rubric is in `docs/vdcr_evaluation_granularity.md`.

## V2 Concept-Balanced Reporting

If V2 includes multiple videos per concept, report both:

```text
video-level score | concept-balanced score
```

Video-level score counts every video-concept sample. Concept-balanced score
either samples one video per concept cluster with a fixed seed or averages
within each concept cluster before averaging across concepts. This prevents
repeated concepts from dominating the benchmark while still preserving the value
of testing multiple visual realizations of the same mechanism.
