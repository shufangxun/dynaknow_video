# Seed Shortcut Review Report

## Summary

This report covers the first 10 downloaded DynaKnow-Video draft samples with extracted first/middle/last/sparse frames.

Review result:

- Accepted as dynamic seed samples: 5
- Needs revision: 3
- Rejected for single-frame shortcut: 2

Important interpretation:

- These accepted samples satisfy the v1 goal of **dynamic knowledge recognition**: a single still frame is not enough to robustly identify the knowledge point.
- They do **not** satisfy a stricter "sparse frames must fail" criterion. In all 6 reviewed cases, ordered sparse frames were sufficient to infer the dynamic process.
- Therefore these are valid v1 seed samples, but not evidence for dense full-video-only understanding.

## Accepted Seed Samples

| video_id | knowledge point | reason |
| --- | --- | --- |
| dynaknow_000001 | Collisions transfer momentum between objects. | Pool-break process requires seeing before/after contact; single frames show billiards but not transfer. |
| dynaknow_000002 | Materials can expand unevenly when heated. | Coil deformation after heating is visible over time; a still frame only shows a coil shape. |
| dynaknow_000003 | Some chemical reactions produce color change. | The answer depends on observing color transition, not a single beaker state. |
| dynaknow_000007 | Surface tension can support or reshape small liquid structures. | Liquid filament breakup is dynamic; taxonomy wording was revised to cover this process. |
| dynaknow_000010 | A pendulum exchanges gravitational potential energy and kinetic energy. | Oscillatory motion shows changing height and speed; still frames do not show the exchange. |

## Revise or Reject

| video_id | decision | reason |
| --- | --- | --- |
| dynaknow_000004 | needs_hard_negative_revision | Melting is dynamic, but a still frame showing ice in water may let models infer the answer from priors. |
| dynaknow_000006 | reject_single_frame_shortcut | Final frame strongly suggests germination/root-shoot emergence, so it fails single-frame insufficiency. |
| dynaknow_000005 | reject_single_frame_shortcut | Plant orientation is visible in single frames and title leaks phototropism. |
| dynaknow_000008 | needs_mechanism_revision | Water rises after candle is covered, but pressure-difference wording may require background explanation not isolated visually. |
| dynaknow_000009 | needs_visual_segment_selection | Filtration setup is visible, but current segment does not strongly show separation. |

## Artifacts

- Accepted pilot JSONL: `data/pilot_samples_accepted_seed.jsonl`
- Revise/reject JSONL: `data/pilot_samples_rejected_or_revise_seed.jsonl`
- Human shortcut review: `data/shortcut_human_review_seed.csv`
- Frame shortcut tasks: `data/frame_shortcut_tasks_seed.jsonl`
- Contact sheet: `media/contact_sheets/seed_first_middle_last.jpg`
- Sparse contact sheets: `media/contact_sheets/sparse/`

## Next Step

Run model-based shortcut baselines on:

- `data/answer_only_tasks_seed.jsonl`
- `data/frame_shortcut_tasks_seed.jsonl`

Use the results to decide whether accepted seed samples remain accepted under model shortcuts.
