# VDCR V2 Curated Physics Intake

Date: 2026-06-20

## Purpose

This batch adds a source-backed physics expansion slice after Commons API search
was rate-limited. The sources were found through web search and then processed
through the same local review pipeline as earlier V2 curated batches.

## Source Pages

| Concept | Source page | License note | Initial gate |
|---|---|---|---|
| `Hydraulic Jump` | `https://commons.wikimedia.org/wiki/File:Hydraulic_jump.webm` | CC BY-SA 4.0 verify_on_page | must show the flow transition, turbulence, and downstream depth change over time |
| `Leidenfrost Droplet Motion` | `https://commons.wikimedia.org/wiki/File:Effet_Leidenfrost.webm` | CC BY-SA 4.0 verify_on_page | must show droplets skittering or persisting on a hot surface due to vapor cushioning |
| `Capillary-Driven Jet/Thread Breakup` | `https://commons.wikimedia.org/wiki/File:Capillary_breakup.webm` | CC BY-SA 4.0 verify_on_page | must show necking and breakup of a liquid jet/thread |
| `Liquid Bridge Pinch-Off` | `https://commons.wikimedia.org/wiki/File:Pinch-off_in_two-fluid_systems.webm` | CC BY 3.0 verify_on_page | must show bridge/neck thinning and final pinch-off |

## Files

- intake: `data/vdcr_v2_curated_physics_intake.csv`
- imported candidates: `data/vdcr_candidate_videos_curated_physics_v2.csv`
- media manifest: `data/vdcr_v2_curated_physics_media_manifest.csv`
- download status: `data/vdcr_v2_curated_physics_download_status.csv`
- frame status: `data/vdcr_v2_curated_physics_frame_status.csv`
- sparse sheets: `reports/vdcr_v2_curated_physics_sparse_sheets/`

## Import Result

The intake listed 4 source pages. Source URL deduplication imported 1 new row:

| Candidate | Concept | Status |
|---|---|---|
| `curated_004001` | `Hydraulic Jump` | imported, downloaded, reviewed as `pass_candidate` |

The other 3 source pages were already in the V1/V2 seed pool and were not
re-imported:

| Existing ID | Concept | Source |
|---|---|---|
| `vdcr_commons_mr2_000002` | `Leidenfrost Droplet Motion` | `File:Effet_Leidenfrost.webm` |
| `vdcr_commons_mr2_000003` | `Capillary-Driven Jet/Thread Breakup` | `File:Capillary_breakup.webm` |
| `vdcr_commons_mr5_000003` | `Liquid Bridge Pinch-Off` | `File:Pinch-off_in_two-fluid_systems.webm` |

## Gate Status

`curated_004001` passed local sparse-frame review. It adds a second Hydraulic
Jump video under the V2 concept-cluster cap of 3 videos per concept.
