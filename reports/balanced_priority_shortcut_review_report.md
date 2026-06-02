# Balanced Priority Shortcut Review Report

Date: 2026-06-01

## Scope

This review covers the 23 frame-ready samples in:

- `data/draft_samples_balanced_priority_frame_ok.jsonl`
- `data/shortcut_human_review_balanced_priority_frame_ok.csv`

The review uses:

- question and answer options,
- first/middle/last frame contact sheet,
- ordered sparse-frame contact sheets,
- source titles/URLs for leakage risk,
- existing seed shortcut review decisions when available.

This is a conservative first shortcut review. It is not a substitute for a final blinded human full-video annotation pass.

## Decision Summary

- accepted dynamic seed samples: 5
- revise/reject samples: 18

Decision breakdown:

- `accept_dynamic_seed`: 5
- `needs_hard_negative_revision`: 1
- `needs_mechanism_revision`: 1
- `needs_visual_segment_selection`: 1
- `needs_full_video_review`: 1
- `needs_static_shortcut_review`: 1
- `needs_knowledge_point_revision`: 1
- `reject_single_frame_shortcut`: 3
- `reject_static_equipment_or_title_leak`: 1
- `reject_title_or_single_frame_shortcut`: 1
- `reject_title_or_mechanism_confound`: 1
- `reject_specialist_title_leakage`: 3
- `reject_wrong_knowledge_point`: 3

## Accepted v0.1 Pilot Samples

The current accepted v0.1 set is:

- `dynaknow_000001`: Collisions transfer momentum between objects.
- `dynaknow_000002`: Materials can expand unevenly when heated.
- `dynaknow_000003`: Some chemical reactions produce color change.
- `dynaknow_000007`: Surface tension can support or reshape small liquid structures.
- `dynaknow_000010`: A pendulum exchanges gravitational potential energy and kinetic energy.
- `dynaknow_000016`: Unsupported objects accelerate downward under gravity.

Files:

- `data/pilot_samples_accepted_v0_1.jsonl`
- `data/pilot_samples_rejected_or_revise_v0_1.jsonl`
- `data/pilot_manifest_v0_1.csv`

## Main Failure Modes Observed

Static shortcut:

- Several plant, pendulum, and filtration samples can be guessed from a single frame or from static equipment.

Title/source leakage:

- Commons filenames often state the phenomenon directly, e.g. phototropism, pendulum, filtration, magnetic mechanisms.

Wrong knowledge point:

- Some automatically collected plant videos were mapped to seed germination even when the visual process was carnivorous plant motion, apex reorientation, or seasonal tree change.

Specialist visual evidence:

- Several microscopy/magnetic videos technically involve magnetic fields but require specialist context and are unsuitable for basic dynamic knowledge recognition.

Sparse-frame sufficiency:

- Accepted samples pass the single-frame filter, but ordered sparse frames are still usually enough to infer the process. These are v1 dynamic-recognition seeds, not strict full-video-only samples.

## Next Action

Scale should proceed by improving candidate acquisition before downloading more media:

- Add negative rules for title leakage during candidate collection.
- Cap repeated knowledge points earlier, especially pendulum, magnetism, seed germination.
- Improve candidate-to-knowledge mapping for plant videos and microscopy videos.
- Prefer videos where the process is visually obvious only as a temporal change, but the source title does not name the phenomenon.
