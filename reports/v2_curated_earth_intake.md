# VDCR V2 Curated Earth Intake

Date: 2026-06-20

## Purpose

This batch targets the current lowest-count V2 domain,
`earth_environmental_systems`, using specific Commons file pages found through
web search rather than bulk Commons API search.

## Source Pages

| Concept | Source page | Initial gate |
|---|---|---|
| `Ice Cliff Calving` | `https://commons.wikimedia.org/wiki/File:040_Eqi_glacier_calving_filmed_in_slow_motion_(Greenland)_Video_by_Giles_Laurent.webm` | must show instability, ice detachment, and fall sequence |
| `Pyroclastic Density Current` | `https://commons.wikimedia.org/wiki/File:An_moderately_explosive_eruption_occurred_at_Kanlaon_Volcano_on_May_13,_2025.webm` | must show ground-hugging density currents or column-collapse flow traveling down slopes |

## Files

- intake: `data/vdcr_v2_curated_earth_intake.csv`
- imported candidates: `data/vdcr_candidate_videos_curated_earth_v2.csv`
- media manifest: `data/vdcr_v2_curated_earth_media_manifest.csv`
- download status: `data/vdcr_v2_curated_earth_download_status.csv`
- frame status: `data/vdcr_v2_curated_earth_frame_status.csv`
- sparse sheets: `reports/vdcr_v2_curated_earth_sparse_sheets/`

## Gate Status

Import/review result:

- imported candidates: 2
- downloaded media: 2
- sparse frame/contact-sheet extraction: 2
- accepted into V2 draft: 1
- kept for revision: 1

Review decisions:

| Candidate | Concept | Decision | Rationale |
|---|---|---|---|
| `curated_005001` | `Ice Cliff Calving` | `pass_candidate` | sparse frames show glacier/ice cliff detachment and collapse into water with splash plume; no obvious text leakage |
| `curated_005002` | `Pyroclastic Density Current` | `revise` | night camera/watermark frames show eruption and possible downslope incandescent flow, but sparse frames do not fully prove a ground-hugging pyroclastic density current |
