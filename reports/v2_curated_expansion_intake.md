# VDCR V2 Curated Expansion Intake

Date: 2026-06-20

## Purpose

Archive-only retrieval produced mostly metadata false positives for the V2
expansion backlog. This intake adds a small curated Wikimedia Commons batch for
concepts that are either V1-uncovered or useful repeated-concept candidates.

## Imported Candidates

Imported candidate file:

```text
data/vdcr_candidate_videos_curated_expansion_v2.csv
```

Source intake:

```text
data/vdcr_v2_curated_expansion_intake.csv
```

Import command:

```bash
python3 scripts/import_curated_sources.py \
  --input data/vdcr_v2_curated_expansion_intake.csv \
  --output data/vdcr_candidate_videos_curated_expansion_v2.csv \
  --start-index 3001 \
  --skip-existing data/vdcr_candidate_videos_combined_v2.csv
```

The intake listed 5 candidate URLs. Four were imported; one droplet
precipitation/coalescence movie already existed in the V1/V2 candidate pool as
`vdcr_commons_mr24_000002` and was skipped by source URL deduplication.

| Candidate | Concept | Source | Initial visual note |
|---|---|---|---|
| `curated_003001` | `Tendril Circumnutation` | `File:Cucumber_Climb.webm` | Candidate shows plant/tendril movement but later sparse frames darken; must inspect full video. |
| `curated_003002` | `Phototropism` | `File:Azuki_Bean_phototropism.ogv` | Strong visible plant bending over time. |
| `curated_003003` | `Standing-Wave Mode Formation` | `File:Dipole_xmting_antenna_animation_2_pulses_HD_1080_12_fps.webm` | Shows oscillatory field/current animation; reviewer must decide whether this is acceptable or too diagrammatic. |
| `curated_003004` | `Capillary-Driven Droplet Coalescence` | `File:Spontaneous-assembly-of-chemically-encoded-two-dimensional-coacervate-droplet-arrays-by-acoustic-ncomms13068-s2.ogv` | Shows droplet array growth/coalescence; reviewer must verify capillary coalescence is visually grounded. |

## Local Review Assets

Media manifest:

```text
data/vdcr_v2_curated_expansion_media_manifest.csv
```

Download status:

```text
data/vdcr_v2_curated_expansion_download_status.csv
```

Frame extraction status:

```text
data/vdcr_v2_curated_expansion_frame_status.csv
```

All 4 imported rows downloaded successfully and produced first/middle/last plus
8 sparse frames. Sparse contact sheets are under:

```text
reports/vdcr_v2_curated_expansion_sparse_sheets/
```

The media files and extracted frames live under ignored `media/` paths and are
not tracked in git:

```text
media/vdcr_curated_expansion_v2/
media/vdcr_curated_expansion_v2_frames/
```

## Construction Effect

After rebuilding V2 construction assets:

- `data/vdcr_candidate_videos_combined_v2.csv`: 621 source-deduplicated rows.
- `data/vdcr_v2_review_queue.csv`: 175 rows.
- The 4 `curated_003xxx` rows are in the review queue with `local_media` and
  `contact_sheet` populated.

## Next Review Gate

These rows are candidates, not accepted samples. Before V2 release export they
still need:

- full-video visual inspection;
- answer leakage review;
- single-frame shortcut review;
- concept-cluster diversity review for repeated concepts;
- license page verification.
