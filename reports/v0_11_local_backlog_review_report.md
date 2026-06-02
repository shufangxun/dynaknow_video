# DynaKnow-Video v0.11 Local Backlog Review Report

## Objective

Continue progress while Wikimedia Commons downloads are rate-limited by reviewing already-downloaded, frame-ready local candidates.

## Reviewed Pool

Input IDs:

- `data/local_backlog_review_ids_v0_11.csv`

Review artifacts:

- `data/draft_samples_local_backlog_v0_11.jsonl`
- `data/shortcut_human_review_local_backlog_v0_11.csv`
- `data/shortcut_review_decisions_local_backlog_v0_11.csv`
- `data/shortcut_human_review_local_backlog_v0_11_reviewed.csv`

## Decisions

| video_id | Decision | Main Reason |
| --- | --- | --- |
| `dynaknow_000015` | reject | Static equipment and visible labels; dynamic filtration mechanism not isolated. |
| `dynaknow_000018` | reject | Candle/flame frames do not visually isolate oxygen requirement. |
| `dynaknow_000023` | reject | Printed background text and single-frame shortcut risk. |
| `dynaknow_000039` | reject | Weak mapping from candle motion to vibration transfer. |
| `dynaknow_000068` | reject | Title/poster OCR and broad edited clip; collision evidence is not clean. |
| `dynaknow_000085` | reject | Burned-in `CO2`/formula captions directly leak the mechanism. |
| `dynaknow_000086` | reject | Opening title says `Le siphon`; already replaced by trimmed `dynaknow_000088`. |
| `dynaknow_000087` | reject | Sparse frames show too little visible change for porous absorption. |

## Current State

- Accepted remains 12 samples, same as v0.9.
- Rejected/revise pool grows to 32 records.
- Current manifest: `data/pilot_manifest_v0_11.csv`
- Current accepted copy: `data/pilot_samples_accepted_v0_11.jsonl`
- Current rejected/revise: `data/pilot_samples_rejected_or_revise_v0_11.jsonl`

## Rationale

This pass intentionally prioritizes precision over sample count. The reviewed items were local and frame-ready, but they violate at least one core benchmark requirement:

- no visible answer-leaking OCR/overlay text,
- dynamic knowledge must be visually supported,
- a single frame should not be sufficient,
- source/title leakage should not be recoverable from the evaluation artifact.

## Next Step

Resume v0.10 media downloading after the Wikimedia `429` throttling window clears, then apply the same OCR/shortcut review gates to the bouncing-ball and Cartesian-diver drafts.

