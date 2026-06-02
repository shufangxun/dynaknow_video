# Priority Download And Frame Report

Date: 2026-06-01

## Scope

This report covers the balanced priority review subset:

- priority review rows: 49
- known media failures excluded from current download queue: 1
- active priority media manifest rows: 48

## Download Status

Current files:

- `data/draft_media_manifest_balanced_priority.csv`
- `data/draft_media_manifest_balanced_priority_downloaded.csv`
- `data/draft_media_manifest_balanced_priority_missing.csv`
- `data/media_download_failures.csv`

Counts:

- downloaded local media: 29
- still missing local media: 19
- known media failures: 1

Known failure:

- `dynaknow_000021`: derived Commons upload URL returned HTTP 404. A Commons API retry was attempted but blocked by rate limiting, so this row is excluded from the active download queue until the true media URL can be resolved.

## Frame Extraction Status

Frame extraction was run on the 29 downloaded priority videos with 8 sparse frames per video.

Output:

- `data/frame_extraction_status_balanced_priority.csv`
- `media/contact_sheets/balanced_priority_first_middle_last.jpg`
- `media/contact_sheets/sparse/`

Counts:

- processed downloaded videos: 29
- complete frame extraction: 23
- partial frame extraction: 6

Partial frame extraction rows:

- `dynaknow_000001`: first/middle/last OK, sparse frames = 6
- `dynaknow_000013`: middle OK, first/last missing, sparse frames = 3
- `dynaknow_000015`: first/middle/last OK, sparse frames = 7
- `dynaknow_000018`: first/middle/last OK, sparse frames = 7
- `dynaknow_000023`: first/middle/last OK, sparse frames = 7
- `dynaknow_000030`: first/middle/last missing, sparse frames = 0

The extraction script now marks these as `partial_frame_extraction`, so they are not included in the frame-ready shortcut batch.

## Frame-Ready Shortcut Batch

The following files define the current runnable shortcut batch:

- `data/draft_samples_balanced_priority_frame_ok.jsonl`
- `data/answer_only_tasks_balanced_priority_frame_ok.jsonl`
- `data/frame_shortcut_tasks_balanced_priority_frame_ok.jsonl`
- `data/shortcut_run_manifest_balanced_priority_frame_ok.csv`
- `data/shortcut_human_review_balanced_priority_frame_ok.csv`

Counts:

- frame-ready samples: 23
- answer-only tasks: 23
- frame shortcut tasks: 92
- human shortcut review rows: 23

Each frame-ready sample contributes:

- 3 single-frame tasks: first, middle, last
- 1 ordered sparse-frame task

## Next Step

Run answer-only and frame-only shortcut review on `data/shortcut_run_manifest_balanced_priority_frame_ok.csv`. Keep a sample only if:

- answer-only cannot infer the answer,
- no single frame makes the answer obvious,
- sparse frames are materially weaker than full video,
- title/subtitle leakage is absent,
- full video supports the stated dynamic knowledge point.
