# DynaKnow-Video v0.10 Clean Candidate Intake Report

## Objective

Continue expanding toward the final 200-300 sample benchmark while enforcing the v0.9 source/OCR leakage rules.

## Candidate Intake

Input sheet:

- `data/curated_sources_web_v0_10.csv`

Imported and filtered candidates:

- `data/candidate_videos_curated_web_v0_10.csv`
- `data/candidate_quality_priority_curated_web_v0_10.csv`
- `data/candidate_quality_exclude_curated_web_v0_10.csv`

Filter result:

| Bucket | Count | Notes |
| --- | ---: | --- |
| priority | 4 | Bouncing-ball and Cartesian-diver candidates for visual review. |
| manual_review | 0 | No rows fell into manual review. |
| exclude | 1 | `Newton's - Balls.webm` excluded due animation/simulation risk. |

## Drafts

Generated:

- `data/draft_samples_curated_web_v0_10.jsonl`
- `data/draft_samples_all_v0_10.jsonl`
- `data/draft_media_manifest_curated_web_v0_10.csv`

Draft IDs:

- `dynaknow_000092`: `Bouncy_ball_240fps.webm`
- `dynaknow_000093`: `Bouncing_Ball.webm`
- `dynaknow_000094`: `Cartesian_diver.ogv`
- `dynaknow_000095`: `Cartesian_Diver.ogv`

## Download Status

Wikimedia Commons returned `HTTP 429` with `Retry-After: 600` seconds during media download. No v0.10 media files were accepted or frame-reviewed in this pass.

Failure log:

- `data/media_download_failures_curated_web_v0_10.csv`

Downloader improvement:

- `scripts/download_media.py` now supports `--max-retry-after-sec`.
- It prints `START <id>` before each download attempt.
- This prevents silent 10-minute sleeps during Wikimedia throttling.

## Next Step

Retry v0.10 media downloads after the Wikimedia rate limit clears:

```bash
python scripts/download_media.py \
  --manifest data/draft_media_manifest_curated_web_v0_10.csv \
  --output-dir media/raw \
  --sleep-sec 2 \
  --max-retry-after-sec 30
```

Only after successful download should these drafts proceed to frame extraction, OCR/overlay review, single-frame review, and acceptance.

