# VDCR v1 Direct-Answer Pilot Release

This package is a source-hidden, locally runnable evaluation snapshot for dynamic video concept recognition.

Task:

```text
Which named dynamic concept is instantiated by the temporally evolving process in this video?
```

Files:

- `dataset_v1.jsonl`: evaluation JSONL. It excludes source URLs, titles, and license notes.
- `dataset_v1_final_mp4.jsonl`: recommended V1 release JSONL for open-source local evaluation. `local_media` points to MP4/H.264 files and each row includes `media_processing_status` plus `media_release_ready`.
- `dataset_v1_mcq_seed20260619.jsonl`: constructed four-choice MCQ variant derived from the direct-answer gold set.
- `manifest_v1.csv`: provenance and license/source audit fields. Do not pass this file to models.
- `manifest_v1_final_mp4.csv`: provenance manifest aligned to `dataset_v1_final_mp4.jsonl`.
- `stats_v1.md`: sample count, domain distribution, concept type distribution, and duration summary.

Shared media store:

- `release/media/videos/`: version-shared release videos. Files are named by media asset id, for example `vdcr_v1_000001.mp4`.
- `release/media/media_assets_v1.csv`: V1 media metainfo, including source id, original source URL, direct download URL, license note, derivative flag, segment bounds when known, file hash, and materialization status.
- `dataset_v1_with_media.jsonl` and `manifest_v1_with_media.csv`: optional generated V1 files whose `local_media` fields point at `../media/videos/...`.
- `release/media/videos_mp4/`: uniform MP4/H.264 copies of the V1 release media. The original files in `release/media/videos/` are retained.
- `release/media/media_assets_v1_mp4.csv`: MP4 media metainfo, including the source file path, source materialization status, MP4 file hash, and conversion status.
- `dataset_v1_mp4.jsonl` and `manifest_v1_mp4.csv`: optional generated V1 files whose `local_media` fields point at `../media/videos_mp4/...`.
- `release/media/media_assets_v1_final_mp4.csv`: final open-source media metainfo. It distinguishes exact existing processed media, rebuilt segments, MP4-normalized metadata/audio-clean rows, original-source rows, and unresolved source fallbacks.

Recommended V1 open-source media entry point:

```text
release/v1/dataset_v1_final_mp4.jsonl
release/media/videos_mp4/
release/media/media_assets_v1_final_mp4.csv
```

`dataset_v1_final_mp4.jsonl` uses MP4/H.264 media and is the file evaluators should load. Rows whose historical V1 derivative was fully represented by existing processed media, time-segment rebuild, or MP4 normalization are marked `media_release_ready=true`. Rows marked `media_release_ready=false` are normalized source fallbacks where the historical filename indicates crop/custom clean transforms but the exact crop/custom parameters are not recoverable from the source URL alone.

Current final MP4 media status:

- total videos: 114
- `media_release_ready=true`: 99
- `media_release_ready=false`: 15
- unresolved rows need the original processed V1 file or exact spatial crop/filter parameters before they can be treated as fully release-ready.

Build or inspect the V1 shared media store:

```bash
python3 scripts/materialize_v1_release_media.py --dry-run
```

To materialize files, first restore any existing processed V1 media cache if available, then run:

```bash
python3 scripts/materialize_v1_release_media.py \
  --source-media-root . \
  --allow-download
```

The script copies exact processed files when present. If a file is missing, it can download direct source media and rebuild simple time-bounded segments with `ffmpeg`. Some V1 derivatives only encode cleanup/crop metadata in the filename and cannot be losslessly rebuilt from the source URL alone; those rows are reported as `missing_existing_derivative` unless the original processed file is present.

To generate the uniform MP4 copies:

```bash
python3 scripts/convert_release_media_to_mp4.py
```

To generate the final MP4 release metadata and dataset:

```bash
python3 scripts/build_v1_final_mp4_release.py
```

Use strict mode to fail if any row still needs the original processed V1 source file:

```bash
python3 scripts/build_v1_final_mp4_release.py --strict
```

Current status:

- samples: 114
- domains: biology_living_systems=29, chemistry_materials_change=29, earth_environmental_systems=28, physics_physical_systems=28
- all rows are direct-answer samples with accepted answer aliases.
- all rows carry temporal evidence spans, static-insufficiency rationale, and passing dynamic quality gates.

Evaluation granularity:

- VDCR should be reported with three separate metrics: open exact naming, open description judge, and MCQ recognition.
- The recommended scoring standard and reviewer-facing interpretation are documented in `docs/vdcr_evaluation_granularity.md`.
- Exact naming measures canonical term recall; description judging measures mechanism-level understanding without requiring the canonical term; MCQ measures closed-set recognition among plausible candidates.

Validation:

```bash
python3 scripts/validate_vdcr_direct_answer.py \
  --input release/v1/dataset_v1_final_mp4.jsonl \
  --release-mode \
  --check-media \
  --min-samples 100 \
  --min-duration-sec 1.0 \
  --min-video-frames 2 \
  --max-domain-imbalance 1
```
