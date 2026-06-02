# v0.13 Source, Storage, And Leakage Policy Update

## What Changed

This update tightens the benchmark execution plan around three requirements:

- Videos must be stored locally inside the benchmark package.
- Source provenance must be preserved for audit, but hidden from model evaluation inputs.
- Main-split videos should avoid subtitles/OCR/overlays as much as possible.

## Storage Contract

Local media locations:

- `media/raw/`: original downloaded videos, named by `video_id`.
- `media/raw_transcoded/`: transcode fallbacks for videos whose original encoding is hard to decode.
- `media/segments/`: clean no-audio clips cut from longer videos when trimming removes leakage-prone openings, endings, title cards, subtitles, or narration.

Frame-review artifacts:

- `media/frames/<video_id>/`
- `media/contact_sheets/`
- `media/contact_sheets/sparse/`

Release/evaluation JSONL should expose only `local_media`, such as `media/raw/dynaknow_000001.webm` or `media/segments/dynaknow_000088.mp4`.

## Source Policy

Preferred source order:

1. Wikimedia Commons real-world videos with stable file pages and license metadata.
2. Government/public-institution public-domain or open-license media.
3. University/OER demonstration videos with explicit reuse terms and direct media access.
4. Open archive/stock platforms only when the clip is real-world, license-clear, non-explanatory, and visually demonstrates the target dynamic knowledge.

The main split should not use lecture, slide, animation, simulation, synthetic, or paper-supplement videos. Those can be kept for a later diagnostic split if useful.

## Leakage Policy

Accepted main-split samples should have no subtitles and minimal visible text. Reject or trim any video with:

- subtitles or burned-in captions that name the target knowledge point;
- title cards, end cards, lower thirds, board text, formulas, or explanatory labels;
- visible terms such as `gravity`, `surface tension`, `siphon`, `density`, `CO2`, or `phototropism` when those terms map to the answer;
- narration required to identify the answer;
- source title or file name leakage in any model-visible evaluation input.

Source URLs, direct URLs, page titles, license notes, and authors stay in manifests for audit, but are omitted from model-facing JSONL.

## Current v0.12 Status

Current release package:

- Evaluation JSONL: `release/v0_12/dynaknow_video_pilot_v0_12_balanced.jsonl`
- Provenance manifest: `release/v0_12/dynaknow_video_pilot_v0_12_manifest.csv`

Current accepted set:

- 13 accepted samples.
- 13/13 have local media paths.
- 13/13 have `ocr_leakage_status=pass`.
- Evaluation JSONL has no `source_url`, `direct_url`, `source_platform`, `license_or_usage_note`, or source title fields.
- Current accepted sources are Wikimedia Commons file pages, with provenance retained in the release manifest.

This update is reflected in:

- `README.md`
- `docs/source_and_leakage_policy.md`
- `docs/curated_sourcing_playbook.md`
- `docs/execution_playbook.md`
- `../dynamic_video_knowledge_benchmark_proposal.md`
