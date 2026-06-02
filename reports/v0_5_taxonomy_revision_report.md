# v0.5 Taxonomy Revision Report

Date: 2026-06-01

## Purpose

v0.4 found that `Brazil_nut_effect_demonstration.webm` was visually useful but mapped to the wrong knowledge point. v0.5 converts that failure into a taxonomy update and regenerates the sample.

## Taxonomy Change

Added:

- `kp_proc_011`
- Category: `procedural_operational_principles`
- Knowledge point: `Vibration can cause granular materials to segregate by particle size.`

Rationale:

- The video shows repeated shaking of granular material.
- Larger pieces migrate upward relative to smaller grains.
- The earlier label, `Settling separates materials by density over time.`, was too imprecise.

Updated file:

- `data/knowledge_points_v1.csv`

## Regenerated Sample

Regenerated:

- `data/draft_samples_curated_web_v0_5.jsonl`
- `data/draft_samples_all_v0_5.jsonl`
- `data/answer_only_tasks_curated_web_v0_5.jsonl`
- `data/frame_shortcut_tasks_curated_web_v0_5.jsonl`
- `data/shortcut_human_review_curated_web_v0_5.csv`

Sample:

- `dynaknow_000081`
- Source: `https://commons.wikimedia.org/wiki/File:Brazil_nut_effect_demonstration.webm`
- Knowledge point: `Vibration can cause granular materials to segregate by particle size.`

Shortcut review:

- answer-only leakage: `low`
- single-frame sufficient: `no`
- sparse frames sufficient: `yes`
- dynamic knowledge supported: `yes`
- decision: `accept_dynamic_seed`

Interpretation:

- Single frames show jar states but do not establish vibration-driven segregation.
- Ordered sparse frames reveal the process, so this is a v1 dynamic-recognition seed, not a strict dense-video-only item.

## v0.5 Pilot State

Files:

- `data/pilot_samples_accepted_v0_5.jsonl`
- `data/pilot_samples_rejected_or_revise_v0_5.jsonl`
- `data/pilot_manifest_v0_5.csv`

Counts:

- accepted: 8
- rejected or revise: 21

Accepted IDs:

- `dynaknow_000001`
- `dynaknow_000002`
- `dynaknow_000003`
- `dynaknow_000007`
- `dynaknow_000010`
- `dynaknow_000016`
- `dynaknow_000047`
- `dynaknow_000081`

Category distribution for accepted v0.5:

- `physics_mechanics`: 4
- `chemistry_material_change`: 2
- `everyday_causal_mechanisms`: 1
- `procedural_operational_principles`: 1

## Lesson

Some rejected samples are not bad videos; they expose missing or overly coarse knowledge points. The benchmark build loop should preserve these as taxonomy-revision candidates instead of only discarding them.
