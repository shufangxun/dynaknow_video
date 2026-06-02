# Expanded Draft Generation Report

Date: 2026-06-01

## What Was Executed

- Generated 30 new draft MCQ samples from `data/review_queue_seed.csv`.
- Generated 37 additional draft MCQ samples from the remaining prioritized candidates.
- Reused `data/knowledge_points_v1.csv` hard-negative pools for choices.
- Rotated the correct answer position across A/B/C/D for the generated batch.
- Merged seed, batch2, and batch3 into `data/draft_samples_all.jsonl`.
- Validated batch2, batch3, and all-draft JSONL with `scripts/validate_samples.py`.
- Exported answer-only leakage tasks for all 77 draft samples.
- Resolved direct Commons upload URLs for all 77 draft samples.
- Exported a 77-row review sheet for human/model filtering.

## Current Counts

- Seed draft samples: 10
- Batch2 draft samples: 30
- Batch3 draft samples: 37
- All draft samples: 77
- Answer-only tasks: 77
- Media manifest rows: 77
- Human review sheet rows: 77
- Skipped prioritized candidates: 3, all because `raw_duration_sec=0.0`

Category distribution in `data/draft_samples_all.jsonl`:

- `physics_mechanics`: 23
- `chemistry_material_change`: 17
- `biology_life_processes`: 12
- `everyday_causal_mechanisms`: 21
- `procedural_operational_principles`: 4

Most repeated knowledge points:

- `A pendulum exchanges gravitational potential energy and kinetic energy.`: 14
- `Magnetic fields can align or attract ferromagnetic materials.`: 9
- `Vibration can transfer energy through a medium.`: 8
- `Seed germination involves root and shoot emergence.`: 7
- `Collisions transfer momentum between objects.`: 6
- `Some chemical reactions produce color change.`: 6
- `A solid can absorb heat and melt into a liquid.`: 6

The first-pass accepted set should cap repeated knowledge points before shortcut evaluation, otherwise model scores will overrepresent a few visually similar processes.

## Output Files

- `data/draft_samples_batch2.jsonl`
- `data/draft_samples_batch3.jsonl`
- `data/draft_samples_all.jsonl`
- `data/answer_only_tasks_all.jsonl`
- `data/draft_media_manifest_all.csv`
- `data/sample_review_sheet_all.csv`
- `data/sample_review_sheet_balanced_priority.csv`
- `data/sample_review_sheet_balanced_leftover.csv`

## Balanced Review Subset

The first-pass review subset was generated with:

- limit: 50
- max per knowledge point: 4
- max per category: 15

Result:

- selected for priority review: 49
- held out by balancing caps: 28

Selected category distribution:

- `physics_mechanics`: 11
- `chemistry_material_change`: 13
- `biology_life_processes`: 9
- `everyday_causal_mechanisms`: 12
- `procedural_operational_principles`: 4

## Media Check Status

The all-draft URL HEAD check was interrupted after Wikimedia Commons returned HTTP 429 rate-limit responses. The partial output was saved as:

- `data/draft_media_url_check_all_partial_429.csv`

This file should not be used as evidence that media URLs are invalid. It only records that the current environment hit Wikimedia rate limiting during rapid repeated media checks. The next run should use a longer delay or wait before retrying.

Recommended retry command:

```bash
python /root/public/jasonshu/dynaknow_video/scripts/check_media_urls.py \
  --input /root/public/jasonshu/dynaknow_video/data/draft_media_manifest_all.csv \
  --output /root/public/jasonshu/dynaknow_video/data/draft_media_url_check_all.csv \
  --timeout-sec 8 \
  --attempts 2 \
  --sleep-sec 5
```

## Next Execution Step

Use `data/sample_review_sheet_all.csv` for first-pass review:

- Confirm video is available.
- Confirm dynamic process is visible.
- Confirm the listed knowledge point is actually supported by the visual temporal evidence.
- Mark answer-only leakage.
- Mark title/subtitle leakage risk.
- Reject items where title, final frame, or sparse frames make the knowledge point obvious.

After review, download only rows that pass this first-pass filter, then run frame extraction and single-frame/sparse-frame shortcut checks.
