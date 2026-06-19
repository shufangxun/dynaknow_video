# DynaKnow-Video v1 Workflow

## Objective

Build a dynamic video knowledge benchmark where the correct answer depends on
the temporal process in the video. The benchmark should evaluate mechanism
recognition, not static object recognition, source-page memorization, subtitles,
or generic event description.

The core task stays fixed:

```text
Which knowledge point is best demonstrated by the dynamic process in the video?
```

## Target Scale

Use the v1 taxonomy in `docs/taxonomy_v1.md`.

- Primary domains: 5
- Mechanism-family subdomains: 31
- Minimum clean v1: about 250 samples
- Target clean v1: about 310 samples
- Candidate/review pool: about 800-1,200 videos
- Per-subdomain target: 8 clean minimum, 10 clean preferred

The candidate pool is intentionally much larger than the final benchmark because
many videos fail dynamic-evidence, shortcut, leakage, source-grounding, or
knowledge-point-quality checks.

## Workflow Overview

```text
taxonomy targets
-> domain/subdomain query generation
-> retrieval candidate collection
-> media download and frame extraction
-> dynamic-knowledge gate
-> dynamic knowledge card
-> mechanism-level knowledge construction
-> MCQ construction
-> deterministic audit and dedupe
-> human review
-> dashboard and source-hidden release
```

## Agent Split

### Retrieval Agent

The retrieval agent finds and prepares candidates. It must not finalize the
knowledge point.

Required output fields:

```text
video_id
candidate_id
source_url
source_platform
license_or_usage_note
local_media
duration_sec
domain_seed
subdomain_seed
query
visible_dynamic_phenomenon
temporal_evidence
source_summary
retrieval_status
retrieval_notes
```

The retrieval agent records what is visible across time: motion transfer,
delayed endpoint, growth direction, flow, segregation, deformation, state
change, reaction endpoint, or other visible temporal process.

### Knowledge-Construction Agent

The knowledge agent applies the card-first annotation rule in
`docs/annotation_guidelines.md`. It must inspect and record the visible dynamic
process before writing the final knowledge point.

Required output fields:

```text
video_id
domain
subdomain
visible_dynamic_phenomenon
temporal_evidence
candidate_mechanisms
knowledge_point
canonical_knowledge_point
source_grounding_note
question
choices
answer
dynamic_evidence
static_insufficient_reason
risk_tags
review_status
```

The agent may use source summaries only for annotation grounding. Source titles,
descriptions, URLs, author/license text, captions, and other provenance metadata
must not be included in the evaluation JSONL.

### Dynamic Knowledge Card

Every candidate that survives retrieval must become a Dynamic Knowledge Card
before MCQ generation. The card is the handoff object between video review and
QA construction.

Required card fields:

```text
video_id
filter_decision
domain
subdomain
local_media
visible_dynamic_process
temporal_evidence
single_frame_failure
candidate_mechanisms
selected_mechanism
knowledge_point
canonical_knowledge_point
source_grounding
verifier_flags
critic_notes
audit_reason
```

The card order is mandatory:

```text
visible_dynamic_process
-> video_anchor_check
-> source_text_check
-> candidate_mechanisms
-> selected_mechanism
-> knowledge_point
-> QA
```

Do not generate QA from a source page, search query, title, or pre-filled
candidate knowledge point unless the card first establishes a visible dynamic
process and a visually anchored mechanism.

Source text is used as double-check, not as the primary evidence. The required
logic is:

```text
video anchor says: this dynamic process is visible
source text says: this mechanism identity is confirmed, OR source text is not used
release gate says: source text did not supply a hidden mechanism or leak the answer
```

When the video and source disagree, or the source is the only reason the
mechanism can be named, keep the candidate in review or fail.

If the source page only has a broad description, title, author note, rendering
workflow, generic scene summary, or no useful mechanism text, mark:

```text
source_text_check.support_status = descriptive_only_not_used
source_text_check.source_role = not_used_no_knowledge
source_text_check.alignment_status = video_primary_source_not_used
```

In that case, the source page must not be cited as knowledge evidence. The item
can still pass only if the video anchor itself is enough to support the selected
mechanism.

### Deterministic Audit

The audit step is not an LLM judgment. It normalizes and displays decisions.

Required output fields:

```text
video_id
filter_decision
reason
domain
subdomain
canonical_knowledge_point
duplicate_group_id
shortcut_risk_tags
leakage_risk_tags
review_status
```

Allowed v1 decisions:

```text
pass
review
fail
```

Legacy decisions are mapped as:

```text
mechanism_keep -> pass
mechanism_review -> review
mechanism_reject_or_rewrite -> fail
```

## Quality Gates

### Gate 0: Taxonomy Coverage

Every candidate has a fixed `domain_seed` and `subdomain_seed`. Gap filling is
driven by `data/domain_sampling_targets_v1.csv`, not by whichever videos are
easiest to crawl.

### Gate 1: Retrieval And Provenance

Keep only candidates with license-verifiable public source pages and local media
or a reproducible download path. Prefer 5-60 second usable clips. Long videos
must have suggested trim spans.

### Gate 2: Dynamic-Knowledge Eligibility

Accept only when:

- the relevant evidence is visible across at least two time points,
- a single frame cannot establish the mechanism,
- the video shows more than an object, final state, or broad change,
- the visible process can support a named or well-defined mechanism.

This gate writes the first half of the Dynamic Knowledge Card. If the visible
dynamic process cannot be described without naming the final answer, keep the
candidate in review.

Reject or keep in review if the best label is only:

- "a liquid changes color",
- "a plant grows",
- "seeds sprout",
- "a machine operates",
- "objects move",
- "a candle burns".

### Gate 3: Knowledge-Point Expression

The knowledge point must use this pattern:

```text
named concept/mechanism + cause/condition/process relation + visible dynamic consequence
```

Domain-specific rules:

- Physics: name the force, energy, pressure, momentum, field, surface, or thermal
  mechanism that explains the time change.
- Chemistry: name the reaction/test/process and material transformation. Generic
  color change, bubbling, or precipitate wording is not enough.
- Biology: name the biological process or stimulus response, such as
  phototropism, gravitropism, nastic movement, germination stage, or water
  transport mechanism.
- Earth/environment: name the dynamic process, such as sediment transport,
  freeze-thaw, hydrologic flow, atmospheric motion, or ecosystem interaction.
- Engineering: name the transferable operational principle, not the equipment or
  procedure label.

This gate writes the second half of the Dynamic Knowledge Card. The final
knowledge point must be selected from candidate mechanisms after rejecting
source-only and static-frame explanations.

### Gate 4: QA Construction

Use the fixed generic question. Each item has 4 options:

- one mechanism-level correct answer,
- three hard negatives at the same abstraction level,
- no obviously unrelated distractors,
- no length or specificity cue that identifies the correct answer,
- no distractor that exactly copies another sample's correct knowledge point.

Hard negatives must be target-specific near misses. Prefer same subdomain,
same visible phenomenon family, or same static-frame confusion. If the only
available distractors are copied answers from other videos or broad
cross-domain fillers, keep the item in review rather than constructing QA.

QA construction may run only after a Dynamic Knowledge Card has a selected
mechanism and a mechanism-level knowledge point. The correct answer must equal
the card's `knowledge_point`.

### Gate 5: Shortcut And Leakage Review

Reject if the answer is recoverable from:

- answer text alone,
- title/source metadata,
- subtitles or narration,
- OCR or visible labels,
- a single frame,
- static captions for sampled frames,
- specialist context not visible in the clip.

### Gate 6: Dedupe

Canonicalize knowledge points and group duplicates. The dashboard must show
duplicate groups and whether a group contains pass/review/fail mixtures. A clean
split should keep the best representative when multiple clips demonstrate the
same canonical mechanism.

### Gate 7: Human Review

Human review checks:

- full video supports the answer,
- single-frame shortcut does not solve the item,
- source grounding is justified by visible anchors,
- QA options are balanced,
- final decision is `pass`, `review`, or `fail`.

## Release Contract

The evaluation JSONL exposes only model-facing fields:

```text
video_id
split
domain
subdomain
knowledge_point
local_media
duration_sec
question
choices
answer
dynamic_evidence
static_insufficient_reason
shortcut_labels
```

The evaluation JSONL must not expose `source_url`, source title, source summary,
author/license text, direct media URL, source-page description, or source-derived
caption text.

Provenance stays in internal manifests and review dashboards.

Clean release rows must have a matching Dynamic Knowledge Card with:

```text
filter_decision = pass
visible_temporal_process = true
single_frame_blocked = true
mechanism_level_wording = true
not_just_event_description = true
source_grounding_is_bounded = true
no_hidden_assumption_risk = true
no_leakage_risk = true
no_shortcut_risk = true
source_text_check.requires_human_source_review = false
source_text_check.alignment_status in {video_and_source_agree, video_primary_source_not_used}
source_text_check.support_status not in {needs_review, source_only_or_hidden}
```

## Standard Commands

Generate v1 Commons query seeds from the subdomain targets:

```bash
python3 scripts/make_commons_search_queries_from_taxonomy.py \
  --knowledge-points data/domain_sampling_targets_v1.csv \
  --output data/commons_file_search_queries_v1.csv \
  --max-per-point 4
```

Validate current samples against the v1 taxonomy and audit:

```bash
python3 scripts/validate_samples.py \
  data/pilot_samples_source_grounded_v0_15_hardneg_40_review.unbalanced.jsonl \
  --taxonomy data/domain_taxonomy_v1.csv \
  --audit data/mechanism_filter_audit_v0_14.csv \
  --targets data/domain_sampling_targets_v1.csv \
  --require-hard-distractors \
  --check-media
```

Build the unified review dashboard:

```bash
python3 scripts/build_v1_workflow_dashboard.py \
  --samples data/pilot_samples_source_grounded_v0_15_hardneg_40_review.unbalanced.jsonl \
  --audit data/mechanism_filter_audit_v0_14.csv \
  --taxonomy data/domain_taxonomy_v1.csv \
  --targets data/domain_sampling_targets_v1.csv \
  --output reports/v1_workflow_dashboard_v0_14.html
```

Build Dynamic Knowledge Cards before QA/release review:

```bash
python3 scripts/build_dynamic_knowledge_cards.py \
  --samples data/pilot_samples_source_grounded_v0_15_hardneg_40_review.unbalanced.jsonl \
  --audit data/mechanism_filter_audit_v0_14.csv \
  --taxonomy data/domain_taxonomy_v1.csv \
  --source-audit data/source_grounded_qa_audit_v0_14_40_review.csv \
  --output-jsonl data/dynamic_knowledge_cards_v0_15.jsonl \
  --output-html reports/dynamic_knowledge_cards_v0_15.html
```

For a source-hidden release JSONL, run validation with release mode:

```bash
python3 scripts/validate_samples.py release/v1/dataset_v1.jsonl \
  --taxonomy data/domain_taxonomy_v1.csv \
  --targets data/domain_sampling_targets_v1.csv \
  --cards data/dynamic_knowledge_cards_v1.jsonl \
  --require-card-pass \
  --require-hard-distractors \
  --release-mode \
  --check-media
```
