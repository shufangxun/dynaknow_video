# Dataset Construction

This document summarizes the current VDCR construction logic. Detailed legacy
workflow notes remain in `docs/execution_playbook.md`; this file is the stable
entry point for new contributors.

## Pipeline

```text
concept inventory / taxonomy
-> public source candidate collection
-> media download or local segment creation
-> dynamic-process eligibility review
-> mechanism/concept anchoring
-> leakage and shortcut review
-> source-hidden direct-answer release
-> optional MCQ derivation
```

## Main Artifacts

- `data/`: structured construction records, candidate pools, manifests, manual
  review sheets, frame status files, and pre-release sample JSONL files.
- `reports/`: construction audits, dashboards, model run reports, and score
  summaries.
- `release/v1/`: the clean source-hidden benchmark package exported from the
  construction records.
- `media/`: local videos, segments, extracted frames, and contact sheets. This
  directory is ignored by git but required for media validation and model runs.
- `docs/v2_expansion_plan.md`: planned V2 expansion rules for concept clusters
  and repeated concept videos.

## Gate 1: Coverage And Candidate Source

Candidates are collected against a concept inventory and domain targets rather
than whichever videos are easiest to find. Sources should be public and
license-verifiable, with stable page URLs and reproducible media paths when
possible.

Source URLs, direct media URLs, titles, and license notes are kept in manifests
and review records. They must not be passed to models as part of the evaluation
JSONL.

## Gate 2: Dynamic Eligibility

A candidate must show evidence across time. The visible process should require
motion, progression, interaction, propagation, growth direction, instability, or
state change. A single frame should be insufficient to identify the target
concept.

Reject or keep in review if the clip only supports generic labels such as
`plant growth`, `color change`, `object movement`, or `fire`.

## Gate 3: Mechanism Anchoring

The answer must be a mechanism-bearing concept. The review process should first
describe the visible dynamic process, then list plausible mechanisms, then
select the mechanism with the fewest hidden assumptions.

Allowed source context can refine the mechanism when the video visibly anchors
the process. It cannot be the only reason the concept is identifiable.

## Gate 4: Leakage And Shortcut Review

Reject or trim clips when the answer is recoverable from:

- source page title or file name;
- subtitles, narration, OCR, title cards, labels, or formula text;
- answer-only option cues;
- a single frame;
- sparse frames that remove the need for full temporal viewing.

Valuable clips with answer-leaking openings, endings, or audio should be
converted into local no-audio segments and reviewed as those segments.

## Gate 5: Release Export

The source-hidden release keeps model-facing fields only:

- `video_id`
- `split`
- `domain`
- `subdomain`
- `concept_id`
- `concept`
- `answer`
- `accepted_answers`
- `local_media`
- `duration_sec`
- `question`
- `dynamic_evidence`
- `static_insufficient_reason`
- `quality_gates`

Provenance stays in `release/v1/manifest_v1.csv` and internal construction
records.

## Validation

Use the direct-answer validator for the current release:

```bash
python3 scripts/validate_vdcr_direct_answer.py \
  --input release/v1/dataset_v1.jsonl \
  --release-mode \
  --check-media \
  --min-samples 100 \
  --min-duration-sec 1.0 \
  --min-video-frames 2 \
  --max-domain-imbalance 1
```

Read `docs/annotation_guidelines.md` for annotation rules and
`docs/source_and_leakage_policy.md` for source and leakage policy details.

## V2 Concept Clusters

Current v1 uses one primary sample per concept. V2 may include repeated
concepts when each repeated video provides a meaningfully different visual
realization of the same mechanism.

The intended V2 data model is:

```text
video_concept_sample = one clean video or segment + one grounded dynamic concept
concept_cluster = all samples sharing the same concept_id or canonical answer
```

Repeated concepts are allowed only when they remain specific, mechanism-bearing,
and independently pass all dynamic, leakage, and shortcut gates. Broad concepts
such as `gravity`, `motion`, `growth`, or `chemical reaction` should not be used
to inflate the main benchmark.

See `docs/v2_expansion_plan.md` for the full policy.

## V2 Construction Commands

V2 construction starts from the formal v1 release and then builds a larger
candidate review queue:

```bash
python3 scripts/build_vdcr_v2_construction_assets.py
```

This writes:

- `data/vdcr_v2_seed_samples.jsonl`: the 114 source-backed v1 release samples,
  retagged as V2 seeds for construction.
- `data/vdcr_candidate_videos_combined_v2.csv`: source-deduplicated V1 + V2
  candidate pool.
- `data/vdcr_v2_review_queue.csv`: main-set V2 review queue with domain gap,
  review status, and concept-cluster rank fields.
- `reports/vdcr_v2_construction_status.md`: current construction counts.

Build the local review triage sheet after media/contact-sheet assets are
available:

```bash
python3 scripts/build_vdcr_v2_review_triage.py
```

This writes:

- `data/vdcr_v2_local_review_triage.csv`: V2 candidates that already have local
  media and sparse contact sheets, with blank decision fields for manual review.
- `reports/vdcr_v2_local_review_triage.md`: local-review candidate summary.

After filling `reviewer_decision` and `reviewer_notes`, apply those decisions
back to the V2 review queue:

```bash
python3 scripts/apply_vdcr_v2_triage_decisions.py
```

Only triage rows with `pass_candidate`, `revise`, or `reject` decisions update
`data/vdcr_v2_review_queue.csv`.

Build the V2 expansion backlog after the construction assets:

```bash
python3 scripts/build_vdcr_v2_expansion_backlog.py
```

This writes:

- `data/vdcr_v2_expansion_backlog.csv`: main-eligible, non-action concepts
  whose candidate buffer is below the V2 target.
- `data/vdcr_v2_expansion_queries.csv`: retrieval queries for the highest
  priority backlog concepts.
- `reports/vdcr_v2_expansion_backlog.md`: domain and role summary for V2
  concept/video expansion.

Build the dashboard with:

```bash
python3 scripts/build_vdcr_review_dashboard.py \
  --review-csv data/vdcr_v2_review_queue.csv \
  --samples data/vdcr_v2_seed_samples.jsonl \
  --concepts data/vdcr_concept_inventory_tiered_v1.csv \
  --candidates data/vdcr_candidate_videos_combined_v2.csv \
  --output reports/vdcr_v2_review_dashboard.html
```

The main queue excludes specialized action concepts by default because they are
more likely to test action recognition than VDCR mechanism grounding. Pass
`--include-action-concepts` only when building a separate optional analysis
queue.
