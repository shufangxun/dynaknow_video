# VDCR V2-300 Direct-Answer MP4 Release

This package is the current source-hidden VDCR release for dynamic video
concept recognition.

Task:

```text
Which named dynamic concept is instantiated by the temporally evolving process in this video?
```

Files:

- `dataset_v2_mp4.jsonl`: evaluation JSONL. It excludes source URLs, titles,
  license notes, and direct download URLs. `local_media` points to MP4/H.264
  files in the shared release media store.
- `manifest_v2_mp4.csv`: internal provenance and review manifest aligned to the
  V2 JSONL. Do not pass this file to models.
- `release/media/media_assets_v2_mp4.csv`: V2 media asset table with hashes,
  processing status, provenance fields, and release readiness.

Shared media store:

- `release/media/videos_mp4/`: MP4/H.264 media reused from the V1 release.
- `release/media/videos_v2_mp4/`: MP4/H.264 media added for V2.

Current status:

- samples: 300
- unique concepts/answers: 181
- V1 reused media: 114
- V2 added media: 186
- max videos per concept cluster: 3
- all model-facing media are MP4/H.264 and no-audio.

Domain distribution:

| Domain | Samples |
|---|---:|
| `biology_living_systems` | 84 |
| `chemistry_materials_change` | 75 |
| `earth_environmental_systems` | 69 |
| `physics_physical_systems` | 72 |

Validation:

```bash
python3 scripts/validate_vdcr_direct_answer.py \
  --input release/v2/dataset_v2_mp4.jsonl \
  --release-mode \
  --check-media \
  --min-samples 300 \
  --allow-duplicate-answers \
  --max-videos-per-answer 3 \
  --min-video-frames 2
```

Media build:

```bash
python3 scripts/build_v2_mp4_release.py
```

The V2 build reuses existing V1 MP4 media for `vdcr_000001` through
`vdcr_000114` and only writes V2-added media into
`release/media/videos_v2_mp4/`.
