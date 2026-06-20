# V2 Expansion Plan

V2 should scale the benchmark without weakening the core VDCR requirement:
each sample must be a clean video-to-concept binding where the visible temporal
process strongly supports the target dynamic concept.

## Unit Of Data

V2 uses two related units:

- `video_concept_sample`: one clean video or segment bound to one grounded
  dynamic concept.
- `concept_cluster`: all samples that share the same `concept_id` or canonical
  answer.

The main dataset may contain repeated concepts when the repeated videos provide
meaningfully different visual realizations. This acknowledges that one dynamic
concept can appear across materials, scenes, scales, and recording conditions.

## Target Scale

Recommended targets:

- V1.1: 150-180 clean video-concept samples.
- V2 first target: 240 clean video-concept samples.
- V2 stretch target: 300 clean video-concept samples.
- V2 first-target unique concepts: 160-180.
- V2 stretch unique concepts: 200-220.
- Concept inventory before V2 sampling: at least 250-300 main-eligible concepts
  after tiering.
- Default concept-cluster cap: up to 3 main-set videos per concept.

The default cap of 3 is a quality control, not a quota. A concept should have
fewer than 3 videos when clean, distinct, non-leaky examples are unavailable.

## Expansion Order

Expand in this order:

1. Expand and tier the concept inventory.
2. Prioritize concepts with strong temporal visual signatures and realistic
   public-source availability.
3. Search for multiple source videos per prioritized concept.
4. Review each candidate video independently against the construction gates.
5. Admit repeated-concept videos only when they add visual diversity.
6. Report both video-level and concept-balanced evaluation.

This order prevents the dataset from growing only through whichever videos are
easiest to find.

## Repeated Concept Rules

Repeated concepts are allowed when all conditions hold:

- The concept is specific and mechanism-bearing.
- Each video independently passes dynamic eligibility, leakage review, and
  single-frame shortcut review.
- The videos differ meaningfully in scene, material, organism, scale, viewpoint,
  source, or implementation.
- The videos are not minor trims, near-duplicates, or alternate encodes of the
  same source.
- The concept cluster does not dominate a domain or the overall benchmark.

Do not use repeated concepts to inflate broad labels. Concepts such as
`gravity`, `motion`, `growth`, `chemical reaction`, `fluid dynamics`, or
`plant movement` are too broad for repeated expansion in the main benchmark.

Better repeated-concept candidates have distinctive temporal signatures, such
as `Rayleigh-Plateau Breakup`, `Vortex Shedding`, `Capillary Rise / Wicking`,
`Phototropism`, `Ostwald Ripening`, `Bubble-Net Feeding`, or other concepts
whose mechanism can be visually distinguished from nearby alternatives.

## Evaluation Reporting

V2 should report two aggregation views:

```text
video-level score | concept-balanced score
```

Video-level score counts every video-concept sample. It measures whether a
model recognizes the concept across all visual instances.

Concept-balanced score prevents repeated concepts from dominating the result.
Two acceptable policies are:

- sample one video per concept cluster with a fixed seed; or
- average within each concept cluster, then average across clusters.

The report should state the number of unique concepts, total video-concept
samples, and the distribution of videos per concept.

## Practical Capacity Estimate

The current v1 release has 114 unique concepts. The current tiered inventory
contains 194 main-eligible concepts (`core_main` plus `strict_main_candidate`),
so a strict one-concept-one-video expansion can likely reach about 150-190
samples after source and leakage losses.

Reaching 240-300 samples requires both:

- expanding the main-eligible concept inventory; and
- allowing selected concept clusters to contain multiple clean, distinct videos.

This is the recommended path for aligning V2 with Video-MMMU-scale video counts
while preserving VDCR's video-concept grounding standard.

See `reports/v2_capacity_assessment.md` for the current capacity estimate and
target-count rationale.

## Background Retrieval

V2 retrieval can be run in shards that survive shell disconnects:

```bash
VDCR_QUERY_OFFSET=0 VDCR_QUERY_LIMIT=120 VDCR_PER_QUERY=5 \
  bash scripts/start_v2_retrieval_background.sh
```

The launcher uses `nohup` and writes all outputs under
`runs/v2_retrieval/<run_id>/`, which is intentionally ignored by git. Check a
running shard with:

```bash
cat runs/v2_retrieval/<run_id>/pid
tail -f runs/v2_retrieval/<run_id>/retrieval.log
```

If Commons is temporarily throttled, run Archive-only shards:

```bash
VDCR_SOURCES=archive VDCR_QUERY_OFFSET=120 VDCR_QUERY_LIMIT=120 VDCR_PER_QUERY=5 \
  bash scripts/start_v2_retrieval_background.sh
```
