# DynaKnow-Video v0.7 Candidate Expansion Report

## Objective

Expand beyond the v0.6 10-sample pilot by collecting another web-curated batch focused on real videos whose knowledge signal depends on temporal change. This pass also stress-tests filters for answer leakage and non-real-video sources.

## Inputs

- Curated source sheet: `data/curated_sources_web_v0_7.csv`
- Imported candidates: `data/candidate_videos_curated_web_v0_7.csv`
- Quality outputs:
  - `data/candidate_quality_priority_curated_web_v0_7.csv`
  - `data/candidate_quality_manual_curated_web_v0_7.csv`
  - `data/candidate_quality_exclude_curated_web_v0_7.csv`

## Filter Result

| Bucket | Count | Notes |
| --- | ---: | --- |
| priority | 3 | Real videos with clear temporal processes from metadata-level screening. |
| manual_review | 2 | Long or weak-mapping videos needing segment/visual confirmation. |
| exclude | 5 | Animation/simulation, game/synthetic context, title leakage, or specialist paper context. |

The updated filter now catches:

- animation or simulation mentions in notes/title
- game or synthetic context
- specialist/paper terms such as `srep`, `pcbi`, and `supplementary`
- target-phenomenon title leakage for magnetic and several chemistry/material categories

## Generated v0.7 Drafts

| video_id | Knowledge Point | Source | Preliminary Visual Status |
| --- | --- | --- | --- |
| `dynaknow_000085` | Some mixtures produce gas during chemical reactions. | `File:Dancing_Raisins.webm` | Strong dynamic foam/bubble evidence, but on-screen captions expose `CO2` and chemical formula text. Do not accept without subtitle/text mitigation. |
| `dynaknow_000086` | Pressure differences can move fluids. | `File:Meca_siphon.webm` | Dynamic liquid transfer is visible, but early frames include an on-screen siphon title. Candidate should be trimmed or reviewed for answer leakage. |
| `dynaknow_000087` | Porous materials absorb liquid through internal spaces. | `File:Pleopeltis_polypodioides_water_absorption_timelapse.webm` | Metadata fits, but sparse frames show weak visible change. Needs full-video review and likely a clearer source. |

Draft and review artifacts:

- Draft samples: `data/draft_samples_curated_web_v0_7.jsonl`
- Merged draft pool: `data/draft_samples_all_v0_7.jsonl`
- Answer-only tasks: `data/answer_only_tasks_curated_web_v0_7.jsonl`
- Frame-shortcut tasks: `data/frame_shortcut_tasks_curated_web_v0_7.jsonl`
- Shortcut run manifest: `data/shortcut_run_manifest_curated_web_v0_7.csv`
- Human shortcut review sheet: `data/shortcut_human_review_curated_web_v0_7.csv`
- Media manifest: `data/draft_media_manifest_curated_web_v0_7.csv`
- First/middle/last sheet: `media/contact_sheets/curated_web_v0_7_first_middle_last.jpg`

## Media Processing

All three priority drafts were downloaded and frame-extracted:

- `media/raw/dynaknow_000085.webm`
- `media/raw/dynaknow_000086.webm`
- `media/raw/dynaknow_000087.webm`
- Frame status: `data/frame_extraction_status_curated_web_v0_7.csv`

OpenCV/ffmpeg emitted an Opus packet warning during extraction, but all three rows completed with `ok` status.

## Lessons For Next Batch

1. Prioritize videos with no embedded explanatory text, captions, classroom title slides, or formula overlays.
2. For otherwise-good demonstrations, store a segment-level start time that excludes title/narration frames, then add a release-time clipping step before acceptance.
3. Add a visual-change check after sparse contact sheet generation. Metadata can say "absorbing" or "reaction" while frames remain too subtle for benchmark use.
4. Treat "dynamic supported" and "answer leakage controlled" as separate gates. `dynaknow_000085` supports the knowledge point but fails leakage hygiene.

## Verification

Commands run:

```bash
python -m py_compile scripts/import_curated_sources.py scripts/filter_candidate_quality.py
python scripts/import_curated_sources.py --input data/curated_sources_web_v0_7.csv --output data/candidate_videos_curated_web_v0_7.csv --start-index 700 --skip-existing data/candidate_videos_merged.csv --skip-existing data/candidate_videos_curated_web_v0_4.csv --skip-existing data/candidate_videos_curated_web_v0_5.csv --skip-existing data/candidate_videos_curated_web_v0_6.csv
python scripts/filter_candidate_quality.py --input data/candidate_videos_curated_web_v0_7.csv --priority-output data/candidate_quality_priority_curated_web_v0_7.csv --review-output data/candidate_quality_manual_curated_web_v0_7.csv --exclude-output data/candidate_quality_exclude_curated_web_v0_7.csv --max-duration 75
python scripts/generate_draft_samples_from_candidates.py --candidates data/candidate_quality_priority_curated_web_v0_7.csv --knowledge-points data/knowledge_points_v1.csv --existing data/draft_samples_all_v0_6.jsonl --output data/draft_samples_curated_web_v0_7.jsonl --start-index 85 --limit 30
python scripts/validate_samples.py data/draft_samples_curated_web_v0_7.jsonl
python scripts/merge_jsonl_unique.py --inputs data/draft_samples_all_v0_6.jsonl data/draft_samples_curated_web_v0_7.jsonl --output data/draft_samples_all_v0_7.jsonl
python scripts/download_media.py --manifest data/draft_media_manifest_curated_web_v0_7.csv --output-dir media/raw --sleep-sec 2
python scripts/extract_frames_cv2.py --media-manifest data/draft_media_manifest_curated_web_v0_7.csv --media-dir media/raw --frames-dir media/frames --output data/frame_extraction_status_curated_web_v0_7.csv --sparse-count 8 --skip-dark-edges --dark-threshold 35
```
