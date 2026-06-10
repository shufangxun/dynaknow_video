# DynaKnow-Video v1 Execution Package

This directory turns the proposal into a pilot-ready workflow for **dynamic video knowledge recognition**.

Core task:

```text
Given a video, identify the knowledge point best demonstrated by its dynamic process.
```

v1 choices:

- Source: public videos only.
- Scale: 250-310 clean samples, collected from an initial 800-1200 candidate/review pool.
- Format: 4-choice MCQ.
- Primary quality bar: full video should beat answer-only, subtitle-only, single-frame, and sparse-frame shortcuts.
- Taxonomy: 5 primary domains and 31 mechanism-family subdomains in `docs/taxonomy_v1.md`.

## Current v1 Workflow Entrypoints

The current workflow is driven by three contracts:

- Retrieval candidates: `schemas/candidate_manifest.schema.json`
- Dynamic knowledge cards: `schemas/dynamic_knowledge_card.schema.json`
- Knowledge annotations: `schemas/annotation_manifest.schema.json`
- Audit/review decisions: `schemas/audit_manifest.schema.json`

Run these commands from the repository root:

```bash
python3 scripts/make_commons_search_queries_from_taxonomy.py \
  --knowledge-points data/domain_sampling_targets_v1.csv \
  --output data/commons_file_search_queries_v1.csv \
  --max-per-point 4

python3 scripts/validate_samples.py \
  data/pilot_samples_source_grounded_v0_15_hardneg_40_review.unbalanced.jsonl \
  --taxonomy data/domain_taxonomy_v1.csv \
  --audit data/mechanism_filter_audit_v0_14.csv \
  --targets data/domain_sampling_targets_v1.csv \
  --require-hard-distractors \
  --check-media

python3 scripts/build_dynamic_knowledge_cards.py \
  --samples data/pilot_samples_source_grounded_v0_15_hardneg_40_review.unbalanced.jsonl \
  --audit data/mechanism_filter_audit_v0_14.csv \
  --taxonomy data/domain_taxonomy_v1.csv \
  --source-audit data/source_grounded_qa_audit_v0_14_40_review.csv \
  --output-jsonl data/dynamic_knowledge_cards_v0_15.jsonl \
  --output-html reports/dynamic_knowledge_cards_v0_15.html

python3 scripts/build_v1_workflow_dashboard.py \
  --samples data/pilot_samples_source_grounded_v0_14_40_review.unbalanced.jsonl \
  --audit data/mechanism_filter_audit_v0_14.csv \
  --taxonomy data/domain_taxonomy_v1.csv \
  --targets data/domain_sampling_targets_v1.csv \
  --output reports/v1_workflow_dashboard_v0_14.html
```

Final release JSONL must be source-hidden. Validate it with:

```bash
python3 scripts/validate_samples.py release/v1/dataset_v1.jsonl \
  --taxonomy data/domain_taxonomy_v1.csv \
  --targets data/domain_sampling_targets_v1.csv \
  --cards data/dynamic_knowledge_cards_v1.jsonl \
  --require-card-pass \
  --require-hard-distractors \
  --release-mode \
  --check-media
```

Media/storage contract:

- Accepted videos live locally under `media/raw/`, `media/raw_transcoded/`, or `media/segments/`.
- Release/evaluation JSONL files expose only `local_media`; source URLs, titles, direct download URLs, and license notes stay in release manifests.
- Source priority is real-world, license-verifiable media: Wikimedia Commons first, then public-institution/government media, university/OER demos, and carefully reviewed open archive/stock clips.
- Main-split videos should have no subtitles/OCR overlays whenever possible. Samples with answer-revealing visible text, title cards, formulas, captions, or source metadata are rejected or trimmed into clean no-audio segments before review.

## Files

- `docs/execution_playbook.md`: end-to-end data collection, filtering, annotation, and evaluation workflow.
- `docs/taxonomy_v1.md`: v1 category and knowledge-point ontology.
- `docs/annotation_guidelines.md`: annotator rules and rejection criteria.
- `docs/curated_sourcing_playbook.md`: sourcing rules for manually curated public video candidates.
- `docs/source_and_leakage_policy.md`: local media storage, source provenance, and subtitle/OCR leakage policy.
- `schemas/dynaknow_sample.schema.json`: source-hidden v1 evaluation JSONL schema.
- `schemas/candidate_manifest.schema.json`: retrieval-agent candidate manifest schema.
- `schemas/dynamic_knowledge_card.schema.json`: card-first dynamic process to knowledge-point schema.
- `schemas/annotation_manifest.schema.json`: knowledge-agent annotation manifest schema.
- `schemas/audit_manifest.schema.json`: deterministic audit manifest schema.
- `templates/candidate_manifest_v1.csv`: retrieval-agent candidate template.
- `templates/dynamic_knowledge_card_v1.jsonl`: card-first dynamic knowledge template.
- `templates/annotation_manifest_v1.jsonl`: knowledge-agent annotation template.
- `templates/audit_manifest_v1.jsonl`: audit manifest template.
- `templates/candidate_videos.csv`: candidate video collection sheet.
- `templates/curated_source_intake.csv`: manual/curated source intake template.
- `data/knowledge_points_v1.csv`: structured seed ontology with search queries and hard-negative pools.
- `data/candidate_videos_seed.csv`: first public-video candidate batch.
- `data/draft_samples_seed.jsonl`: first draft MCQ batch for shortcut and human review.
- `data/draft_samples_batch2.jsonl`: automatically generated second draft MCQ batch from the prioritized review queue.
- `data/draft_samples_batch3.jsonl`: automatically generated third draft MCQ batch from remaining prioritized candidates.
- `data/draft_samples_all.jsonl`: seed + batch2 + batch3 draft samples, currently 77 records.
- `data/candidate_videos_commons_auto.csv`: automatically collected Commons category candidates.
- `data/commons_category_queries_v0_3.csv`: targeted v0.3 Commons category queries for stricter acquisition.
- `data/commons_file_search_queries_v0_3.csv`: targeted v0.3 Commons file-search queries.
- `data/commons_file_search_queries_v0_6.csv`: taxonomy-expanded Commons file-search queries for the next acquisition wave.
- `data/candidate_videos_commons_v0_3_raw.csv`: raw candidates from the v0.3 category collection experiment.
- `data/candidate_quality_priority_existing_v0_3.csv`: existing candidates that pass v0.3 candidate-level quality filters.
- `data/candidate_quality_manual_v0_3.csv`: new v0.3 category candidates requiring manual review.
- `data/candidate_quality_review_pool_v0_3.csv`: 12-row candidate review pool after v0.3 candidate filtering.
- `data/candidate_videos_commons_search_v0_3_shard00_skipped.csv`: Commons file-search shard failure log from API throttling.
- `data/candidate_videos_curated_template_test.csv`: smoke-test import of the curated intake template, not a real candidate batch.
- `data/curated_sources_web_v0_4.csv`: manually curated Commons File candidates found by web search.
- `data/candidate_videos_curated_web_v0_4.csv`: imported v0.4 curated web candidates.
- `data/candidate_quality_priority_curated_web_v0_4.csv`: v0.4 curated candidates passing candidate-level filters.
- `data/draft_samples_curated_web_v0_4.jsonl`: draft sample generated from the v0.4 curated priority candidate.
- `data/draft_samples_all_v0_4.jsonl`: all draft samples plus the v0.4 curated draft sample.
- `data/shortcut_human_review_curated_web_v0_4.csv`: shortcut review for the v0.4 curated frame-ready sample.
- `data/pilot_samples_accepted_v0_4.jsonl`: current accepted v0.4 pilot set, 7 samples.
- `data/pilot_samples_rejected_or_revise_v0_4.jsonl`: current v0.4 revise/reject set, 22 samples.
- `data/pilot_manifest_v0_4.csv`: joined manifest for the current v0.4 accepted and revise/reject sets.
- `data/draft_samples_curated_web_v0_5.jsonl`: regenerated Brazil-nut sample after adding the granular segregation knowledge point.
- `data/draft_samples_all_v0_5.jsonl`: all draft samples plus the v0.5 regenerated curated sample.
- `data/shortcut_human_review_curated_web_v0_5.csv`: shortcut review for the revised v0.5 curated sample.
- `data/pilot_samples_accepted_v0_5.jsonl`: current accepted v0.5 pilot set, 8 samples.
- `data/pilot_samples_rejected_or_revise_v0_5.jsonl`: current v0.5 revise/reject set, 21 samples.
- `data/pilot_manifest_v0_5.csv`: joined manifest for the current v0.5 accepted and revise/reject sets.
- `data/curated_sources_web_v0_6.csv`: web-curated Commons candidate intake for the v0.6 expansion round.
- `data/candidate_videos_curated_web_v0_6.csv`: imported v0.6 curated candidates after duplicate skipping.
- `data/candidate_quality_priority_curated_web_v0_6.csv`: v0.6 curated candidates passing candidate-level quality filters.
- `data/candidate_quality_exclude_curated_web_v0_6.csv`: v0.6 curated candidates excluded by quality filters.
- `data/draft_samples_curated_web_v0_6.jsonl`: draft MCQ samples generated from v0.6 priority candidates.
- `data/draft_samples_all_v0_6.jsonl`: all draft samples plus the v0.6 curated draft samples.
- `data/draft_media_manifest_curated_web_v0_6.csv`: direct Commons media manifest for v0.6 draft samples.
- `data/draft_media_manifest_curated_web_v0_6_transcode_360p.csv`: Commons 360p transcode manifest for AV1 samples needing review-compatible media.
- `data/frame_extraction_status_curated_web_v0_6_combined.csv`: combined frame extraction status after original and transcode fallback extraction.
- `data/frame_shortcut_tasks_curated_web_v0_6.jsonl`: frame shortcut tasks for v0.6 draft samples.
- `data/shortcut_human_review_curated_web_v0_6.csv`: human shortcut review sheet for v0.6 draft samples.
- `data/shortcut_review_decisions_curated_web_v0_6.csv`: compact v0.6 shortcut review decisions.
- `data/pilot_samples_accepted_curated_web_v0_6.jsonl`: v0.6 accepted samples from the curated batch.
- `data/pilot_samples_rejected_or_revise_curated_web_v0_6.jsonl`: v0.6 rejected/revise samples from the curated batch.
- `data/pilot_samples_accepted_v0_6.jsonl`: current accepted v0.6 pilot set, 10 samples.
- `data/pilot_samples_rejected_or_revise_v0_6.jsonl`: current v0.6 revise/reject set, 22 samples.
- `data/pilot_manifest_v0_6.csv`: joined manifest for the current v0.6 accepted and revise/reject sets.
- `data/curated_sources_web_v0_7.csv`: web-curated Commons candidate intake for the v0.7 expansion round.
- `data/candidate_videos_curated_web_v0_7.csv`: imported v0.7 curated candidates after duplicate skipping.
- `data/candidate_quality_priority_curated_web_v0_7.csv`: v0.7 curated candidates passing candidate-level quality filters.
- `data/candidate_quality_manual_curated_web_v0_7.csv`: v0.7 curated candidates requiring segment or visual review.
- `data/candidate_quality_exclude_curated_web_v0_7.csv`: v0.7 curated candidates excluded by quality filters.
- `data/draft_samples_curated_web_v0_7.jsonl`: draft MCQ samples generated from v0.7 priority candidates.
- `data/draft_samples_all_v0_7.jsonl`: all draft samples plus the v0.7 curated draft samples.
- `data/draft_media_manifest_curated_web_v0_7.csv`: direct Commons media manifest for v0.7 draft samples.
- `data/frame_extraction_status_curated_web_v0_7.csv`: frame extraction status for v0.7 draft samples.
- `data/frame_shortcut_tasks_curated_web_v0_7.jsonl`: frame shortcut tasks for v0.7 draft samples.
- `data/shortcut_human_review_curated_web_v0_7.csv`: human shortcut review sheet for v0.7 draft samples.
- `data/media_segments_v0_8.csv`: local segment specification for trimming leakage-prone source videos.
- `data/pilot_samples_accepted_v0_8.jsonl`: current accepted v0.8 pilot set, 12 samples.
- `data/pilot_samples_rejected_or_revise_v0_8.jsonl`: current v0.8 revise/reject set, 23 samples.
- `data/pilot_manifest_v0_8.csv`: joined manifest for the current v0.8 accepted and revise/reject sets.
- `release/v0_8/`: clean v0.8 pilot release package with provenance hidden from recommended evaluation JSONL.
- `data/media_segments_v0_9.csv`: local segment specification for replacing a text-leaky accepted clip.
- `data/shortcut_review_decisions_v0_9_all.csv`: visible-text/OCR review decisions for all v0.9 accepted samples.
- `data/pilot_samples_accepted_v0_9.jsonl`: current accepted v0.9 pilot set, 12 samples with OCR labels filled.
- `data/pilot_samples_rejected_or_revise_v0_9.jsonl`: current v0.9 revise/reject set, including the original text-leaky full clip.
- `data/pilot_manifest_v0_9.csv`: joined manifest for the current v0.9 accepted and revise/reject sets.
- `release/v0_9/`: clean v0.9 pilot release package with all accepted rows marked `ocr_leakage_status=pass`.
- `data/curated_sources_web_v0_10.csv`: clean-source candidate intake for bouncing-ball and Cartesian-diver candidates.
- `data/candidate_quality_priority_curated_web_v0_10.csv`: v0.10 candidates passing candidate-level filters before media download.
- `data/draft_samples_curated_web_v0_10.jsonl`: draft MCQs generated from v0.10 priority candidates.
- `data/media_download_failures_curated_web_v0_10.csv`: v0.10 download failures caused by Wikimedia 429 throttling.
- `data/local_backlog_review_ids_v0_11.csv`: local frame-ready backlog IDs reviewed while Commons downloads were rate-limited.
- `data/shortcut_review_decisions_local_backlog_v0_11.csv`: OCR/shortcut decisions for the local backlog review.
- `data/pilot_samples_accepted_v0_11.jsonl`: current accepted v0.11 pilot set, unchanged at 12 samples.
- `data/pilot_samples_rejected_or_revise_v0_11.jsonl`: current v0.11 revise/reject set after local backlog review.
- `data/pilot_manifest_v0_11.csv`: joined manifest after local backlog review.
- `data/local_orphan_review_ids_v0_12.csv`: local media IDs reviewed after sequential extraction repair.
- `data/shortcut_review_decisions_local_orphans_v0_12.csv`: OCR/shortcut decisions for local orphan media.
- `data/pilot_samples_accepted_v0_12.jsonl`: current accepted v0.12 pilot set, 13 samples.
- `data/pilot_samples_rejected_or_revise_v0_12.jsonl`: current v0.12 revise/reject set.
- `data/pilot_manifest_v0_12.csv`: joined manifest after orphan media review.
- `release/v0_12/`: clean v0.12 pilot release package with 13 source-hidden evaluation samples.
- `release/v0_6/`: clean v0.6 pilot release package with JSONL, balanced evaluation JSONL, manifests, shortcut tasks, stats, and README.
- `release/v0_5/`: clean pilot release package with JSONL, balanced evaluation JSONL, manifests, shortcut tasks, stats, and README.
- `data/candidate_videos_merged.csv`: seed + auto candidates, deduplicated by URL.
- `data/review_queue_seed.csv`: prioritized first-pass review queue.
- `data/answer_only_tasks_seed.jsonl`: answer-only leakage tasks for draft samples.
- `data/answer_only_tasks_all.jsonl`: answer-only leakage tasks for all draft samples.
- `data/draft_media_manifest.csv`: direct Commons media URLs for draft samples.
- `data/draft_media_manifest_all.csv`: direct Commons media URLs for all draft samples.
- `data/draft_media_manifest_balanced_priority.csv`: media manifest for the balanced priority subset, excluding known media failures.
- `data/draft_media_manifest_balanced_priority_downloaded.csv`: balanced priority media rows with local video files available.
- `data/draft_media_manifest_balanced_priority_missing.csv`: balanced priority media rows still waiting for download.
- `data/draft_media_url_check.csv`: HEAD check results for draft media URLs.
- `data/draft_media_url_check_all_partial_429.csv`: interrupted all-draft URL check showing Wikimedia 429 rate-limit responses.
- `data/media_download_failures.csv`: media rows with known download or derived-URL failures.
- `data/sample_review_sheet_all.csv`: 77-row human/model review sheet for all draft samples.
- `data/sample_review_sheet_balanced_priority.csv`: 49-row first-pass review subset capped at 4 samples per knowledge point.
- `data/sample_review_sheet_balanced_leftover.csv`: draft samples held out by the balancing caps.
- `data/frame_extraction_status_balanced_priority.csv`: frame extraction status for downloaded balanced priority media.
- `data/draft_samples_balanced_priority_frame_ok.jsonl`: 23 balanced priority samples with complete first/middle/last/sparse frame extraction.
- `data/answer_only_tasks_balanced_priority_frame_ok.jsonl`: answer-only tasks for the 23 frame-ready samples.
- `data/frame_shortcut_tasks_balanced_priority_frame_ok.jsonl`: single-frame and sparse-frame shortcut tasks for the 23 frame-ready samples.
- `data/shortcut_run_manifest_balanced_priority_frame_ok.csv`: shortcut batch manifest for the 23 frame-ready samples.
- `data/shortcut_human_review_balanced_priority_frame_ok.csv`: human shortcut review sheet for the 23 frame-ready samples.
- `data/frame_extraction_manifest_seed.csv`: ffmpeg command manifest for static-frame and sparse-frame filters.
- `data/first_pass_review_top40.csv`: compact human review sheet for the first 40 prioritized candidates.
- `media/raw/`: local media downloads for draft samples.
- `media/segments/`: local no-audio review clips trimmed from longer or leakage-prone source videos.
- `media/frames/`: extracted first/middle/last/sparse frames when available.
- `media/contact_sheets/seed_first_middle_last.jpg`: quick visual review sheet for extracted draft frames.
- `media/contact_sheets/sparse/`: per-sample sparse-frame contact sheets.
- `data/frame_shortcut_tasks_seed.jsonl`: single-frame and sparse-frame shortcut tasks.
- `data/shortcut_run_manifest_seed.csv`: ready-to-run shortcut baseline manifest.
- `data/shortcut_human_review_seed.csv`: first human/static-frame shortcut review for downloaded seed samples.
- `data/pilot_samples_accepted_seed.jsonl`: accepted dynamic seed samples after first shortcut review.
- `data/pilot_samples_rejected_or_revise_seed.jsonl`: samples rejected or requiring revision after first shortcut review.
- `data/pilot_samples_accepted_v0_1.jsonl`: current accepted v0.1 pilot set, 6 samples.
- `data/pilot_samples_rejected_or_revise_v0_1.jsonl`: current v0.1 revise/reject set from reviewed frame-ready samples.
- `data/pilot_manifest_v0_1.csv`: joined manifest for the current v0.1 accepted and revise/reject sets.
- `data/draft_quality_audit_v0_2.csv`: quality audit for all 77 draft samples.
- `data/draft_quality_new_priority_v0_2.csv`: 9 new candidates that passed v0.2 quality filters for further review.
- `data/draft_quality_exclude_or_revise_v0_2.csv`: candidates excluded or sent to revision by v0.2 quality filters.
- `data/draft_samples_new_priority_v0_2.jsonl`: JSONL for the 9 v0.2 new-priority candidates.
- `data/draft_samples_new_priority_frame_ok_v0_2.jsonl`: 4 v0.2 new-priority samples with complete frame extraction.
- `data/shortcut_human_review_new_priority_frame_ok_v0_2.csv`: shortcut review for the 4 v0.2 frame-ready new-priority samples.
- `data/pilot_samples_accepted_v0_2.jsonl`: current accepted v0.2 pilot set, 7 samples.
- `data/pilot_samples_rejected_or_revise_v0_2.jsonl`: current v0.2 revise/reject set, 21 samples.
- `data/pilot_manifest_v0_2.csv`: joined manifest for the current v0.2 accepted and revise/reject sets.
- `reports/seed_shortcut_review_report.md`: summary of the first human shortcut review.
- `reports/batch2_generation_report.md`: status and next steps for the expanded all-draft batch.
- `reports/priority_download_frame_report.md`: download and frame extraction status for the balanced priority subset.
- `reports/balanced_priority_shortcut_review_report.md`: preliminary shortcut review summary for the 23 frame-ready balanced-priority samples.
- `reports/v0_2_quality_filter_report.md`: v0.2 quality-audit, new-priority download, frame extraction, and shortcut-review summary.
- `reports/v0_3_candidate_collection_report.md`: v0.3 candidate-level filtering and targeted collection experiment summary.
- `reports/v0_4_curated_web_intake_report.md`: v0.4 curated web-source intake and review summary.
- `reports/v0_5_taxonomy_revision_report.md`: taxonomy revision that turns the Brazil-nut effect candidate into an accepted dynamic seed.
- `reports/v0_5_release_report.md`: release package summary and next evaluation step.
- `reports/v0_5_evaluation_harness_report.md`: scoring harness, prediction format, and smoke-test baseline results.
- `reports/v0_6_candidate_expansion_report.md`: v0.6 taxonomy-query expansion, curated intake, quality filtering, media download, and frame extraction summary.
- `reports/v0_6_review_release_report.md`: v0.6 shortcut review decisions and release package summary.
- `reports/v0_7_candidate_expansion_report.md`: v0.7 curated intake, filter stress test, draft generation, media processing, and preliminary visual audit.
- `reports/v0_8_leakage_release_report.md`: v0.8 source/OCR leakage mitigation and release summary.
- `reports/v0_9_ocr_hardening_report.md`: v0.9 accepted-set OCR audit and text-leaky clip replacement summary.
- `reports/v0_10_clean_candidate_intake_report.md`: v0.10 clean candidate intake and Wikimedia throttling status.
- `reports/v0_11_local_backlog_review_report.md`: local frame-ready backlog review completed during Wikimedia throttling.
- `reports/v0_12_orphan_media_review_report.md`: local orphan-media review and sequential extraction repair summary.
- `reports/review_dashboard.html`: static dashboard for accepted samples, rejected samples, and the top review queue.
- `data/pilot_manifest_seed.csv`: joined manifest for accepted/revise samples, local media, frames, and review status.
- `templates/review_sheet.csv`: human review and shortcut validation sheet.
- `templates/samples.example.jsonl`: example final samples.
- `prompts/answer_only_filter.md`: prompt for checking question/option leakage.
- `prompts/video_knowledge_question.md`: model evaluation prompt template.
- `scripts/validate_samples.py`: local JSONL/schema sanity checker.
- `scripts/filter_candidate_quality.py`: candidate-level quality filter used before drafting MCQs or downloading media.
- `scripts/search_commons_files.py`: Commons file-search collector for targeted queries.
- `scripts/import_curated_sources.py`: imports manual/curated source rows into candidate CSV format.
- `scripts/make_commons_search_queries_from_taxonomy.py`: expands taxonomy search queries into Commons file-search rows.
- `scripts/make_commons_transcode_manifest.py`: derives Wikimedia Commons transcode URLs for review-compatible media.
- `scripts/clip_media_cv2.py`: creates no-audio local review clips with OpenCV when ffmpeg is unavailable.
- `scripts/extract_frames_sequential_cv2.py`: sequential frame extraction fallback for videos with broken random-seek metadata.
- `scripts/apply_shortcut_review_decisions.py`: applies compact review decisions to shortcut review sheets.
- `scripts/concat_jsonl.py`: concatenates JSONL prediction files without deduplicating by video ID.
- `scripts/normalize_model_outputs.py`: converts raw model response JSONL into scorer-ready prediction JSONL.
- `scripts/validate_predictions.py`: checks prediction coverage and answer-label validity before scoring.
- `scripts/download_media.py`: downloads media from manifests; supports `--max-retry-after-sec` to fail fast under long Wikimedia throttling.

## Recommended Pilot Flow

1. Fill `templates/candidate_videos.csv` with 800-1000 candidate public videos.
2. Use `docs/taxonomy_v1.md` to assign a primary category and candidate knowledge point.
3. Apply first-pass rejection using `docs/annotation_guidelines.md`.
4. Write final MCQ samples using `schemas/dynaknow_sample.schema.json`.
5. Run:

```bash
python /root/public/jasonshu/dynaknow_video/scripts/validate_samples.py \
  /root/public/jasonshu/dynaknow_video/templates/samples.example.jsonl

python /root/public/jasonshu/dynaknow_video/scripts/validate_samples.py \
  /root/public/jasonshu/dynaknow_video/data/draft_samples_seed.jsonl

python /root/public/jasonshu/dynaknow_video/scripts/make_review_queue.py \
  --input /root/public/jasonshu/dynaknow_video/data/candidate_videos_merged.csv \
  --output /root/public/jasonshu/dynaknow_video/data/review_queue_seed.csv

python /root/public/jasonshu/dynaknow_video/scripts/export_answer_only_tasks.py \
  --input /root/public/jasonshu/dynaknow_video/data/draft_samples_seed.jsonl \
  --output /root/public/jasonshu/dynaknow_video/data/answer_only_tasks_seed.jsonl

python /root/public/jasonshu/dynaknow_video/scripts/resolve_commons_media.py \
  --no-api \
  --input /root/public/jasonshu/dynaknow_video/data/draft_samples_seed.jsonl \
  --output /root/public/jasonshu/dynaknow_video/data/draft_media_manifest.csv

python /root/public/jasonshu/dynaknow_video/scripts/check_media_urls.py \
  --input /root/public/jasonshu/dynaknow_video/data/draft_media_manifest.csv \
  --output /root/public/jasonshu/dynaknow_video/data/draft_media_url_check.csv

python /root/public/jasonshu/dynaknow_video/scripts/make_frame_extraction_manifest.py \
  --media-manifest /root/public/jasonshu/dynaknow_video/data/draft_media_manifest.csv \
  --media-dir /root/public/jasonshu/dynaknow_video/media/raw \
  --frames-dir /root/public/jasonshu/dynaknow_video/media/frames \
  --output /root/public/jasonshu/dynaknow_video/data/frame_extraction_manifest_seed.csv

python /root/public/jasonshu/dynaknow_video/scripts/make_first_pass_review.py \
  --input /root/public/jasonshu/dynaknow_video/data/review_queue_seed.csv \
  --output /root/public/jasonshu/dynaknow_video/data/first_pass_review_top40.csv \
  --limit 40

python /root/public/jasonshu/dynaknow_video/scripts/download_media.py \
  --manifest /root/public/jasonshu/dynaknow_video/data/draft_media_manifest.csv \
  --output-dir /root/public/jasonshu/dynaknow_video/media/raw

python /root/public/jasonshu/dynaknow_video/scripts/extract_frames_cv2.py \
  --media-manifest /root/public/jasonshu/dynaknow_video/data/draft_media_manifest.csv \
  --media-dir /root/public/jasonshu/dynaknow_video/media/raw \
  --frames-dir /root/public/jasonshu/dynaknow_video/media/frames \
  --output /root/public/jasonshu/dynaknow_video/data/frame_extraction_status_seed.csv

python /root/public/jasonshu/dynaknow_video/scripts/make_contact_sheet.py \
  --status /root/public/jasonshu/dynaknow_video/data/frame_extraction_status_seed.csv \
  --frames-dir /root/public/jasonshu/dynaknow_video/media/frames \
  --output /root/public/jasonshu/dynaknow_video/media/contact_sheets/seed_first_middle_last.jpg

python /root/public/jasonshu/dynaknow_video/scripts/make_sparse_contact_sheets.py \
  --frames-dir /root/public/jasonshu/dynaknow_video/media/frames \
  --output-dir /root/public/jasonshu/dynaknow_video/media/contact_sheets/sparse

python /root/public/jasonshu/dynaknow_video/scripts/export_frame_shortcut_tasks.py \
  --samples /root/public/jasonshu/dynaknow_video/data/draft_samples_seed.jsonl \
  --frames-dir /root/public/jasonshu/dynaknow_video/media/frames \
  --output /root/public/jasonshu/dynaknow_video/data/frame_shortcut_tasks_seed.jsonl

python /root/public/jasonshu/dynaknow_video/scripts/make_shortcut_run_manifest.py \
  --answer-only /root/public/jasonshu/dynaknow_video/data/answer_only_tasks_seed.jsonl \
  --frame-shortcut /root/public/jasonshu/dynaknow_video/data/frame_shortcut_tasks_seed.jsonl \
  --output /root/public/jasonshu/dynaknow_video/data/shortcut_run_manifest_seed.csv

python /root/public/jasonshu/dynaknow_video/scripts/report_shortcut_review.py \
  /root/public/jasonshu/dynaknow_video/data/shortcut_human_review_seed.csv

python /root/public/jasonshu/dynaknow_video/scripts/filter_samples_by_shortcut_review.py \
  --samples /root/public/jasonshu/dynaknow_video/data/draft_samples_seed.jsonl \
  --review /root/public/jasonshu/dynaknow_video/data/shortcut_human_review_seed.csv \
  --accepted-output /root/public/jasonshu/dynaknow_video/data/pilot_samples_accepted_seed.jsonl \
  --rejected-output /root/public/jasonshu/dynaknow_video/data/pilot_samples_rejected_or_revise_seed.jsonl

python /root/public/jasonshu/dynaknow_video/scripts/build_review_dashboard.py \
  --root /root/public/jasonshu/dynaknow_video \
  --output /root/public/jasonshu/dynaknow_video/reports/review_dashboard.html

python /root/public/jasonshu/dynaknow_video/scripts/build_pilot_manifest.py \
  --accepted /root/public/jasonshu/dynaknow_video/data/pilot_samples_accepted_seed.jsonl \
  --rejected /root/public/jasonshu/dynaknow_video/data/pilot_samples_rejected_or_revise_seed.jsonl \
  --media-dir /root/public/jasonshu/dynaknow_video/media/raw \
  --frames-dir /root/public/jasonshu/dynaknow_video/media/frames \
  --sparse-sheet-dir /root/public/jasonshu/dynaknow_video/media/contact_sheets/sparse \
  --output /root/public/jasonshu/dynaknow_video/data/pilot_manifest_seed.csv

python /root/public/jasonshu/dynaknow_video/scripts/generate_draft_samples_from_candidates.py \
  --candidates /root/public/jasonshu/dynaknow_video/data/review_queue_seed.csv \
  --knowledge-points /root/public/jasonshu/dynaknow_video/data/knowledge_points_v1.csv \
  --existing /root/public/jasonshu/dynaknow_video/data/draft_samples_seed.jsonl \
  --output /root/public/jasonshu/dynaknow_video/data/draft_samples_batch2.jsonl \
  --start-index 11 \
  --limit 30

python /root/public/jasonshu/dynaknow_video/scripts/merge_jsonl.py \
  --inputs /root/public/jasonshu/dynaknow_video/data/draft_samples_seed.jsonl \
    /root/public/jasonshu/dynaknow_video/data/draft_samples_batch2.jsonl \
    /root/public/jasonshu/dynaknow_video/data/draft_samples_batch3.jsonl \
  --output /root/public/jasonshu/dynaknow_video/data/draft_samples_all.jsonl

python /root/public/jasonshu/dynaknow_video/scripts/export_sample_review_sheet.py \
  --samples /root/public/jasonshu/dynaknow_video/data/draft_samples_all.jsonl \
  --media-manifest /root/public/jasonshu/dynaknow_video/data/draft_media_manifest_all.csv \
  --output /root/public/jasonshu/dynaknow_video/data/sample_review_sheet_all.csv

python /root/public/jasonshu/dynaknow_video/scripts/make_balanced_review_subset.py \
  --input /root/public/jasonshu/dynaknow_video/data/sample_review_sheet_all.csv \
  --output /root/public/jasonshu/dynaknow_video/data/sample_review_sheet_balanced_priority.csv \
  --leftover-output /root/public/jasonshu/dynaknow_video/data/sample_review_sheet_balanced_leftover.csv \
  --limit 50 \
  --max-per-knowledge 4 \
  --max-per-category 15

python /root/public/jasonshu/dynaknow_video/scripts/filter_media_manifest.py \
  --manifest /root/public/jasonshu/dynaknow_video/data/draft_media_manifest_all.csv \
  --ids-from /root/public/jasonshu/dynaknow_video/data/sample_review_sheet_balanced_priority.csv \
  --exclude-ids-from /root/public/jasonshu/dynaknow_video/data/media_download_failures.csv \
  --output /root/public/jasonshu/dynaknow_video/data/draft_media_manifest_balanced_priority.csv

python /root/public/jasonshu/dynaknow_video/scripts/split_manifest_by_local_media.py \
  --manifest /root/public/jasonshu/dynaknow_video/data/draft_media_manifest_balanced_priority.csv \
  --media-dir /root/public/jasonshu/dynaknow_video/media/raw \
  --downloaded-output /root/public/jasonshu/dynaknow_video/data/draft_media_manifest_balanced_priority_downloaded.csv \
  --missing-output /root/public/jasonshu/dynaknow_video/data/draft_media_manifest_balanced_priority_missing.csv

python /root/public/jasonshu/dynaknow_video/scripts/extract_frames_cv2.py \
  --media-manifest /root/public/jasonshu/dynaknow_video/data/draft_media_manifest_balanced_priority_downloaded.csv \
  --media-dir /root/public/jasonshu/dynaknow_video/media/raw \
  --frames-dir /root/public/jasonshu/dynaknow_video/media/frames \
  --output /root/public/jasonshu/dynaknow_video/data/frame_extraction_status_balanced_priority.csv \
  --sparse-count 8

python /root/public/jasonshu/dynaknow_video/scripts/filter_samples_by_shortcut_review.py \
  --samples /root/public/jasonshu/dynaknow_video/data/draft_samples_balanced_priority_frame_ok.jsonl \
  --review /root/public/jasonshu/dynaknow_video/data/shortcut_human_review_balanced_priority_frame_ok.csv \
  --accepted-output /root/public/jasonshu/dynaknow_video/data/pilot_samples_accepted_balanced_priority_frame_ok.jsonl \
  --rejected-output /root/public/jasonshu/dynaknow_video/data/pilot_samples_rejected_or_revise_balanced_priority_frame_ok.jsonl

python /root/public/jasonshu/dynaknow_video/scripts/merge_jsonl_unique.py \
  --inputs /root/public/jasonshu/dynaknow_video/data/pilot_samples_accepted_seed.jsonl \
    /root/public/jasonshu/dynaknow_video/data/pilot_samples_accepted_balanced_priority_frame_ok.jsonl \
  --output /root/public/jasonshu/dynaknow_video/data/pilot_samples_accepted_v0_1.jsonl
```

6. Run shortcut checks: answer-only, subtitle-only, single-frame, sparse-frame.
7. Keep only samples that satisfy dynamic necessity and leakage checks.

Current seed files:

```bash
python /root/public/jasonshu/dynaknow_video/scripts/summarize_candidates.py \
  /root/public/jasonshu/dynaknow_video/data/candidate_videos_seed.csv

python /root/public/jasonshu/dynaknow_video/scripts/validate_samples.py \
  /root/public/jasonshu/dynaknow_video/templates/samples.example.jsonl
```
