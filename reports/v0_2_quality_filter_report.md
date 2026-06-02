# v0.2 Quality Filter Report

Date: 2026-06-01

## Purpose

The v0.1 review showed that blindly downloading auto-collected candidates wastes effort on title leakage, single-frame shortcuts, wrong knowledge-point mappings, and specialist videos. v0.2 therefore adds an explicit quality-audit pass before more media work.

## Quality Audit Rules

The audit script checks:

- prior shortcut review decisions,
- source-title leakage for known phenomena,
- title hints for static equipment shortcuts,
- specialist or paper-derived microscopy context,
- animation/simulation titles,
- known media download failures,
- repeated knowledge points beyond a cap of 4,
- known wrong-mapping patterns for plants, ice, and electric-field flame videos,
- auto-filled evidence spans that still require manual verification.

Script:

- `scripts/audit_draft_quality.py`

Inputs:

- `data/draft_samples_all.jsonl`
- `data/shortcut_human_review_seed.csv`
- `data/shortcut_human_review_balanced_priority_frame_ok.csv`
- `data/media_download_failures.csv`

Outputs:

- `data/draft_quality_audit_v0_2.csv`
- `data/draft_quality_priority_v0_2.csv`
- `data/draft_quality_new_priority_v0_2.csv`
- `data/draft_quality_accepted_v0_2.csv`
- `data/draft_quality_exclude_or_revise_v0_2.csv`

Audit counts:

- audited draft samples: 77
- already accepted: 6
- new priority candidates: 9
- revise/manual-review candidates: 34
- excluded candidates: 28

## v0.2 New Priority Processing

The 9 new priority candidates were exported to:

- `data/draft_samples_new_priority_v0_2.jsonl`
- `data/draft_media_manifest_new_priority_v0_2.csv`

Download status:

- downloaded: 9
- missing: 0

Frame extraction status:

- processed: 9
- complete frame extraction: 4
- partial frame extraction: 5

Frame-ready files:

- `data/draft_samples_new_priority_frame_ok_v0_2.jsonl`
- `data/answer_only_tasks_new_priority_frame_ok_v0_2.jsonl`
- `data/frame_shortcut_tasks_new_priority_frame_ok_v0_2.jsonl`
- `data/shortcut_run_manifest_new_priority_frame_ok_v0_2.csv`
- `data/shortcut_human_review_new_priority_frame_ok_v0_2.csv`
- `media/contact_sheets/new_priority_v0_2_first_middle_last.jpg`

## v0.2 Shortcut Review Result

Reviewed 4 frame-ready new-priority samples:

- accepted dynamic seed: 1
- revise/reject: 3

Accepted:

- `dynaknow_000047`: Collisions transfer momentum between objects.

Rejected or revise:

- `dynaknow_000057`: reject animation, not natural video knowledge.
- `dynaknow_000061`: needs mechanism revision; combustion/oxygen not visually isolated.
- `dynaknow_000062`: needs mechanism revision; oxygen requirement not directly established.

## Current v0.2 Pilot State

Files:

- `data/pilot_samples_accepted_v0_2.jsonl`
- `data/pilot_samples_rejected_or_revise_v0_2.jsonl`
- `data/pilot_manifest_v0_2.csv`

Counts:

- accepted v0.2 samples: 7
- rejected or revise v0.2 samples: 21

Accepted IDs:

- `dynaknow_000001`
- `dynaknow_000002`
- `dynaknow_000003`
- `dynaknow_000007`
- `dynaknow_000010`
- `dynaknow_000016`
- `dynaknow_000047`

## Next Execution Direction

The filter is now strict enough to expose a candidate-supply problem: only 9 of 77 draft samples remained as new priority after quality filtering, and only 1 of 4 frame-ready new-priority samples was accepted.

Next scale-up should focus on acquiring better source videos, not expanding from the current noisy Commons category set. The collection stage should:

- reject title leakage at collection time,
- avoid specialist microscopy and paper supplementary videos,
- avoid animation/simulation unless explicitly creating a separate synthetic split,
- avoid plant videos unless the exact plant process is mapped correctly,
- cap repeated knowledge points before drafting MCQs,
- prefer clips where the dynamic process is visually necessary but the title does not name the phenomenon.
