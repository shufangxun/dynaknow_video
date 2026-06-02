# v0.4 Curated Web Intake Report

Date: 2026-06-01

## Purpose

v0.4 tests the manual/curated intake path using concrete Commons File pages found through web search rather than the throttled Commons API search endpoint.

## Curated Sources

Input:

- `data/curated_sources_web_v0_4.csv`

Imported candidates:

- `data/candidate_videos_curated_web_v0_4.csv`

Candidate-quality filter result:

- priority: 1
- manual review: 1
- exclude: 3

The filter correctly excluded the title-leaking convection files after adding `convection` as a leakage keyword for `Warm air rises and can drive convection.`

## Draft And Media Pipeline

Priority candidate converted to draft:

- `data/draft_samples_curated_web_v0_4.jsonl`
- `data/draft_samples_all_v0_4.jsonl`

Media and frame outputs:

- `data/draft_media_manifest_curated_web_v0_4.csv`
- `media/raw/dynaknow_000081.webm`
- `data/frame_extraction_status_curated_web_v0_4.csv`
- `media/contact_sheets/curated_web_v0_4_first_middle_last.jpg`
- `media/contact_sheets/sparse/dynaknow_000081_sparse.jpg`

Shortcut artifacts:

- `data/answer_only_tasks_curated_web_v0_4.jsonl`
- `data/frame_shortcut_tasks_curated_web_v0_4.jsonl`
- `data/shortcut_human_review_curated_web_v0_4.csv`

## Review Result

`dynaknow_000081` was not accepted.

Decision:

- `needs_knowledge_point_revision`

Reason:

- The video shows Brazil-nut/granular segregation after shaking.
- The current knowledge point, `Settling separates materials by density over time.`, is not precise enough.
- This should either become a taxonomy extension for granular size segregation or remain excluded from v1.

## v0.4 Pilot State

Files:

- `data/pilot_samples_accepted_v0_4.jsonl`
- `data/pilot_samples_rejected_or_revise_v0_4.jsonl`
- `data/pilot_manifest_v0_4.csv`

Counts:

- accepted: 7
- rejected or revise: 22

No new sample was accepted in v0.4.

## Web Sources Used

The curated candidates were found through web search over Wikimedia Commons File pages, including pages for `MakingASplash.webm`, `Rayleigh-Benard convection.webm`, `Formation-of-convection-cells.webm`, `Natural Convection Flow.webm`, and `Brazil nut effect demonstration.webm`.
