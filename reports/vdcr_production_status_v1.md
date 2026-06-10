# VDCR Production Status v1

Date: 2026-06-06

## Scope

VDCR v1 is using direct-answer evaluation, not multiple choice.

Question:

```text
Which named dynamic concept is instantiated by the temporally evolving process in this video?
```

## Current Assets

| Asset | Path | Count |
|---|---|---:|
| Concept inventory | `data/vdcr_concept_inventory_v1.csv` | 248 concepts |
| Tiered concept inventory | `data/vdcr_concept_inventory_tiered_v1.csv` | 52 core main, 142 strict main candidates, 16 stress-slice, 15 extension, 23 defer/remove |
| Executable concept pool | `data/vdcr_concept_pool_v1.csv` | legacy pool, superseded for sample building by tiered inventory |
| Search query queue | `data/vdcr_concept_search_queries_v1.csv` | 1103 queries |
| Merged Archive candidates | `data/vdcr_candidate_videos_archive_merged_v1.csv` | 372 candidates |
| Combined candidates | `data/vdcr_candidate_videos_combined_v1.csv` | 593 source-deduplicated candidates |
| Candidate review HTML | `reports/vdcr_candidate_review_v1.html` | 372 cards |
| Review dashboard | `reports/vdcr_review_dashboard_v1.html` | 296 review rows, 115 main samples |
| Pilot manual review | `data/vdcr_pilot_manual_review_seed_v1.csv` | 296 reviewed rows |
| Direct-answer pilot samples | `data/vdcr_pilot_samples_direct_answer_v1.jsonl` | 115 main samples |
| Oracle score report | `reports/vdcr_pilot_score_oracle_v1.md` | 115/115 oracle |

## Candidate Distribution

| Domain | Candidate Count |
|---|---:|
| 生命过程机制 | 250 |
| 地球环境过程 | 144 |
| 自然物理规律 | 123 |
| 物质变化机制 | 76 |

| Current Concept Validity Tier | Concept Count |
|---|---:|
| `strict_main_candidate` | 142 |
| `core_main` | 52 |
| `defer_or_remove` | 23 |
| `stress_slice` | 16 |
| `extension` | 15 |

The historical/archive candidates predate the current tiering policy and remain in the merged candidate CSV for traceability. They should not enter final samples unless they pass the current concept-pool and video-gate rules.

## Pilot Review Status

| Status | Count | Meaning |
|---|---:|---|
| pass_candidate | 121 | Usable after current visual review; still needs final license/source audit. |
| revise | 26 | Relevant but requires trimming/cropping or stronger leakage review. |
| review | 26 | Potentially useful, needs closer manual review or extension decision. |
| reject | 123 | Wrong sense, lecture video, source-dependent clip, duplicate concept, or non-VDCR source. |

## Pilot Sample Tier Audit

The sample builder now uses `data/vdcr_concept_inventory_tiered_v1.csv` and only admits `core_main` plus `strict_main_candidate` concepts into the main direct-answer JSONL. Six previously reviewed pass candidates were filtered out of the main set because they are now `extension` or `stress_slice`.

| Concept Validity Tier | Current Main Sample Count | Release Treatment |
|---|---:|---|
| `core_main` | 45 | Main v1 samples |
| `strict_main_candidate` | 70 | Main v1 samples, each requiring explicit video-level gate evidence |
| `extension` | 0 | Not counted in main JSONL |
| `stress_slice` | 0 | Not counted in main JSONL |

Current main sample distribution:

| Domain | Main Sample Count |
|---|---:|
| `chemistry_materials_change` | 29 |
| `biology_living_systems` | 29 |
| `earth_environmental_systems` | 28 |
| `physics_physical_systems` | 29 |

## Round32 Update

Round32 added five reviewed candidates and two pre-filter pass samples. These IDs were historical before the stricter tiered sample builder renumbered the authoritative JSONL:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `pre_tier_round32_000101` | `Boiling Bubble Nucleation and Departure` | `physics_physical_systems` | pass |
| `pre_tier_round32_000102` | `Embryonic Cleavage Division Sequence` | `biology_living_systems` | pass |

Rejected round32 candidates:

- `Gelation Front Propagation` s2: rejected for visible setup/title text and source-dependent hydrogel context.
- `Gelation Front Propagation` s3: rejected because the video shows hydrogel fiber/microspring coiling rather than a decisive gelation-front propagation process.
- `Dune Slip-Face Avalanche`: rejected because the NASA Mars video is an explainer/flyover and does not show clean textless grain avalanche dynamics.

At the end of round32, before the stricter tier filter was applied, the sample distribution was 26 physics, 26 biology, 25 chemistry/materials, and 25 earth/environment.

## Round33 Update

Round33 added five reviewed candidates and one new main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000097` | `Coalescence-Driven Coarsening` | `chemistry_materials_change` | pass |

Rejected or held round33 candidates:

- `Viscoelastic Recoil` pitcher-plant fluid video: rejected because the visible evidence is insect/liquid-surface interaction, not clear stretch-release-recoil dynamics.
- `Viscoelastic Recoil` vitrimer heat-gun video: rejected for title leakage and material-processing context; the video does not independently show a clear recoil cycle.
- `Storm Surge Propagation`: rejected because it is a warning-map/satellite overlay animation, not raw surge/inundation propagation.
- `Wave Refraction`: held as extension because it is a clean teaching/simulation GIF, not a main-quota natural/process video.

After round33 tier filtering, the authoritative main sample count was 97, not 103 pass-candidate review rows.

## Round34 Update

Round34 added seven new reviewed Commons candidates and two new main pass samples:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000098` | `Coupled Pendulum Synchronization` | `physics_physical_systems` | pass |
| `vdcr_000099` | `Bacterial Swarming Motility` | `biology_living_systems` | pass |

Rejected round34 candidates:

- Backup `Coupled Pendulum Synchronization` coupled-pendula experiment: rejected as a duplicate and less visually decisive than the clean metronome segment.
- `Damped Oscillation`: rejected because the torsion-pendulum clip does not make amplitude decay visually decisive.
- `Bacterial Chemotaxis`: rejected because directionality toward a gradient/wound target is not decisive without source context.
- `Aeolian Saltation`: rejected because the downloaded GIF has no usable video duration and behaves like a tiny static/diagrammatic file.
- `Wall Cloud Rotation`: rejected because the source is a generic scenic cloud timelapse, not a localized rotating wall cloud.

After round34, the authoritative main sample count was 99. The next production step prioritized earth/environment first, then physics/biology, while keeping chemistry from over-dominating the current pilot.

## Round35 Update

Round35 added three new reviewed Commons candidates and one new main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000100` | `Wind-Driven Fire-Front Propagation` | `earth_environmental_systems` | pass |

Rejected round35 candidates:

- Backup `Wind-Driven Fire-Front Propagation` Texas wildfire clip: rejected as a duplicate backup because the Ranger Road Fire sample is longer and more visually specific.
- `Lava Dome Collapse`: rejected because the GIF repeats near-identical satellite frames and does not show a decisive dome-collapse, plume, or flow sequence.

After round35, the authoritative main sample count is 100. The next production step should prioritize physics, then biology/earth, while maintaining concept-level deduplication.

## Round36 Update

Round36 added four new reviewed Commons candidates and three new main pass samples:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000101` | `Inertia-Capillarity Droplet Rebound` | `physics_physical_systems` | pass |
| `vdcr_000102` | `Pollen Tube Chemotropic Growth` | `biology_living_systems` | pass |
| `vdcr_000103` | `Root Hair Tip Growth` | `biology_living_systems` | pass |

Rejected round36 candidate:

- `Standing Wave Formation`: rejected because the source is a long explanatory animation with frequency readouts, wave-symbol labels, formula-like labels, and audio. Cropping away the labels would remove much of the standing-wave/resonance evidence, so it is not release-ready as clean video-native evidence.

Round36 cleaning notes:

- `Droplet Rebound`: cropped away bottom text/time overlays, removed audio and source metadata, retained the impact-deformation-retraction-liftoff sequence.
- `Pollen Tube Chemotropic Growth`: cropped away time labels and scale bars, removed source metadata, retained directional tube navigation into the ovule.
- `Root Hair Tip Growth`: cropped away timestamp overlays, removed source metadata, retained polarized tip extension across frames.

After round36, the authoritative main sample count was 103. The next production step was one earth/environment sample to rebalance toward 26 each, then continued physics-heavy production until the main pool grows toward the 248-sample target.

## Round37 Update

Round37 added one new earth/environment concept and one new main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000104` | `Seismic Wave Propagation` | `earth_environmental_systems` | pass |

Round37 cleaning notes:

- `Seismic Wave Propagation` was added to the concept inventory as a strict-gate earth/environment concept under `地球物理与地震波动力学`.
- The accepted sample uses a cropped, metadata-clean derivative of a USGS/Commons ground-shaking animation. The crop removes the original title, timestamp, intensity legend, audio, and answer-bearing source metadata while preserving the outward propagation of the colored ground-motion field.
- The source page double-checks the earthquake/seismic-wave context, but the review decision relies on the visible temporal propagation in the video itself.

After round37, the authoritative main sample count is 104: 27 biology, 26 chemistry/materials, 26 earth/environment, and 25 physics.

## Round38 Update

Round38 added one new physics concept and one new main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000105` | `Stokes Flow Kinematic Reversibility` | `physics_physical_systems` | pass |

Round38 cleaning notes:

- `Stokes Flow Kinematic Reversibility` was added to the concept inventory as a strict-gate physics concept under `低雷诺数层流与可逆性`.
- The accepted sample uses a cropped, metadata-clean derivative of the Commons/UNM laminar-flow demonstration. The crop removes the bottom title/logo, audio, and source metadata while preserving the forward laminar deformation and reverse recovery sequence.
- The source page double-checks the Re < 1 laminar-flow reversal context; the pass decision relies on the visible forward deformation followed by reverse restoration in the video.

After round38, the authoritative main sample count is 105: 27 biology, 26 physics, 26 chemistry/materials, and 26 earth/environment.

## Round40 Update

Round40 added one new chemistry/materials main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000106` | `Benedict Positive Reducing-Sugar Reaction` | `chemistry_materials_change` | pass |

Round40 cleaning notes:

- The accepted sample uses a cropped, metadata-clean derivative of a new Commons Wikiexperiments Benedict reaction video, distinct from the prior concentration-series Benedict candidates.
- The crop removes the right-side title/label risk area, audio, and source metadata while preserving reagent addition, water-bath heating, and progressive blue-to-red-brown precipitate formation.
- The source page double-checks the Cu2+ to Cu+ reduction and Cu2O precipitate mechanism; the pass decision relies on the visible color/precipitate evolution in the video itself.
- A duplicate/retrieved-again electrodeposition candidate from round39 was deliberately not merged because the same source URL was already present in the combined candidate pool.

After round40, the authoritative main sample count is 106: 27 biology, 27 chemistry/materials, 26 physics, and 26 earth/environment.

## Round41 Update

Round41 added one new earth/environment main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000107` | `Cutbank Erosion / Point-Bar Deposition` | `earth_environmental_systems` | pass |

Round41 cleaning notes:

- The accepted sample uses a cropped, metadata-clean derivative of the Commons/NASA Padma River Landsat time-series.
- The crop removes bottom year labels, audio, and source metadata while preserving river-channel boundary migration, outer-bank retreat, and light-toned bar/accretion growth across the time sequence.
- The source page double-checks the Padma River time-series context; the pass decision relies on visible channel-boundary and bar-morphology evolution in the video itself.

After round41, the authoritative main sample count is 107: 27 biology, 27 chemistry/materials, 27 earth/environment, and 26 physics.

## Round42 Update

Round42 added one new physics main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000108` | `Worthington Jet` | `physics_physical_systems` | pass |

Round42 cleaning notes:

- The accepted sample uses a cropped, metadata-clean derivative from a new Commons slow-motion splash video.
- The segment excludes the raw opening title card and unrelated later impacts, removes source metadata, and keeps only the impact-to-vertical-jet sequence.
- The video evidence shows impact into a liquid surface, cavity/splash disturbance, a vertical liquid jet rising, top droplet formation, and relaxation. A single frame could be confused with a generic splash, pouring stream, or static liquid column.
- The source page only double-checks that the video is a slow-motion splash/impact source; the pass decision relies on visible post-impact jet dynamics in the cleaned segment.

After round42, the authoritative main sample count is 108: 27 biology, 27 chemistry/materials, 27 earth/environment, and 27 physics.

## Round43 Update

Round43 added one new biology main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000109` | `Biofilm Colony Expansion Dynamics` | `biology_living_systems` | pass |

Round43 cleaning notes:

- The accepted sample uses a metadata-clean, video-only derivative from a new NIGMS image-gallery time-lapse.
- The raw source contained audio and container creation metadata; both were removed before the sample was added.
- The video evidence shows red biofilm/colony material expanding through a curved microfluidic channel and progressively occupying/blocking the flow path. A single frame can show colored material inside a channel, but the named concept requires observing collective front expansion and channel-occupancy growth across time.
- A separate NIGMS lamellipodium candidate was downloaded during the round but deliberately not merged because the visible actin-driven mechanism was not sufficiently verifiable from the video alone.

Round43 builder fix:

- `scripts/build_vdcr_pilot_samples_from_review.py` now maps both original `concept_en` and `recommended_answer_en` to the same tiered concept row.
- When `--allowed-concept-tiers` is active, unmapped concepts are now filtered out instead of being silently admitted with an empty tier.

After round43, the authoritative main sample count is 109: 28 biology, 27 chemistry/materials, 27 earth/environment, and 27 physics.

## Round44 Update

Round44 added one new chemistry/materials main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000110` | `Electrodeposition Dendrite Growth` | `chemistry_materials_change` | pass |

Round44 cleaning notes:

- The accepted sample uses a video-only clean derivative from a Scientific Reports/PMC experimental supplementary movie under CC BY 4.0.
- The raw experimental WMV was converted to metadata-stripped MP4; no audio, title card, overlay text, or answer-bearing screen text is present in the accepted derivative.
- The video evidence shows dark electrodeposits initiating at opposing electrode tips, thickening, and growing into branching/fractal dendritic morphology over time. A single frame could show only electrodes or an already formed deposit; the accepted concept requires observing electrode-driven growth fronts and morphology formation across the temporal sequence.
- Nearby candidates were deliberately not merged: a Zenodo spherulitic-growth source was too visually static/source-dependent, PNAS lithium-dendrite downloads were not release-friendly, Scientific Reports modeling videos were not real experimental footage, and the high-frequency experimental clip was more wire-like than dendritic.

After round44, the authoritative main sample count is 110: 28 biology, 28 chemistry/materials, 27 earth/environment, and 27 physics.

## Round45 Update

Round45 added one new earth/environment main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000111` | `Dune Slip-Face Grain Avalanche` | `earth_environmental_systems` | pass |

Round45 cleaning notes:

- The accepted sample uses a cropped, metadata-clean derivative from an NPS Great Sand Dunes public video.
- The raw source includes opening park text, `Singing Sand` title text, subtitles, audio, and an end logo. The accepted derivative trims to the middle slip-face segment, crops out bottom captions, removes audio, and strips source metadata.
- The video evidence shows a sand slope/slip face where granular material loses stability and moves downslope as a localized avalanche tongue/fan over time. A single frame could show only a sandy slope or a static erosion scar; the named concept requires observing the granular flow initiate, spread, and relax along the slip face.
- The source page discusses singing sand and dune avalanches; the pass decision relies on the visible time-evolving slip-face grain flow, not the page title.

After round45, the authoritative main sample count is 111: 28 biology, 28 chemistry/materials, 28 earth/environment, and 27 physics.

## Round46 Update

Round46 added one new physics main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000112` | `Capillary Rise / Wicking` | `physics_physical_systems` | pass |

Round46 cleaning notes:

- The accepted sample uses a center-cropped, metadata-clean derivative from a USGS public-domain capillary-action experiment video.
- The raw source is an explainer with narration, setup text, web-page screenshots, USGS logo overlays, and an end card. The accepted derivative keeps only the experiment segment, removes audio and source metadata, and crops away the bottom source logo.
- The video evidence shows water wicking upward through coffee-filter paper and carrying green marker dye as a wetting/color front rises and spreads through the porous sheet over time. A single frame can show a wet filter and green stain, but the target concept requires observing wetting-front progression and dye transport.
- The visible `USGS` letters on the filter are marker dye used in the experiment and do not reveal the answer concept.

After round46, the authoritative main sample count is 112: 28 biology, 28 chemistry/materials, 28 earth/environment, and 28 physics.

## Round47 Update

Round47 added one new biology main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000113` | `Mitotic Chromosome Segregation` | `biology_living_systems` | pass |

Round47 cleaning notes:

- A PMC/Scientific Reports droplet-merging candidate was rejected before merge. The full source had heavy title/condition/annotation text; narrow crops either retained answer-leading labels/boxes or reduced the visual evidence to generic droplet motion rather than decisive coalescence.
- The accepted sample uses a cropped, metadata-clean derivative from a PLOS ONE supplementary microscopy movie under CC BY.
- The raw movie is a 16-hour H2B-GFP HeLa-cell time-lapse with an embedded bottom timestamp band and no audio. The accepted derivative crops out the timestamp band and strips source metadata.
- The video evidence shows fluorescent chromosomes condensing/aligned as bright bars, separating into two groups, and resolving into daughter nuclei/cells over time. A single frame can show nuclei or condensed chromosomes, but the named concept requires observing the temporal chromosome movement and segregation sequence.
- The source page double-checks the HeLa-cell mitosis context; the pass decision relies on visible chromosome dynamics, not page text.

After round47, the authoritative main sample count is 113: 29 biology, 28 chemistry/materials, 28 earth/environment, and 28 physics.

## Round48 Update

Round48 added one new physics main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000114` | `Droplet Spreading and Retraction` | `physics_physical_systems` | pass |

Round48 cleaning notes:

- A Scientific Reports/Commons droplet-impact video was inspected as a possible `Crown Splash` source, but it was rejected for that concept because no crown-shaped splash is visible.
- The same source is accepted for `Droplet Spreading and Retraction`: the cleaned segment shows a droplet descending, contacting a superhydrophobic surface, spreading laterally into a flattened lamella/film with a rippled edge, and retracting into a compact central mass.
- The segment is deliberately cut to 0-2.8s, before clear liftoff, to avoid ambiguity with the already-covered `Inertia-Capillarity Droplet Rebound` concept.
- The raw OGV metadata contains article/title/author information. The accepted derivative removes audio, strips source metadata, and contains no in-frame answer text.
- The source page double-checks that the clip is a CC BY 4.0 Scientific Reports supplementary movie; the pass decision relies on visible impact-spreading-retraction dynamics.

After round48, the authoritative main sample count is 114: 29 biology, 29 physics, 28 chemistry/materials, and 28 earth/environment.

## Round49 Update

Round49 added one new chemistry/materials main pass sample:

| ID | Answer | Domain | Status |
|---|---|---|---|
| `vdcr_000115` | `Flame Blowoff` | `chemistry_materials_change` | pass |

Round49 cleaning notes:

- A Commons/Scientific Reports coffee-ring candidate was inspected and rejected before merge. The full source has title and four-panel PEG/SDS labels; label-cropped single panels become visually weak and mostly static, so the dynamic coffee-ring formation evidence would rely too much on source context.
- The accepted `Flame Blowoff` sample uses a metadata-clean GIF-to-MP4 derivative from a Wikimedia Commons combustor video.
- The clean derivative has no audio, no in-frame answer text, and no source metadata beyond neutral container encoding.
- The video evidence shows a blue premixed swirl-combustor flame changing from a broad stable flame into a narrowed, elongated, unstable downstream flame structure as the sequence progresses toward blowoff. A single frame can show only a blue flame shape; the target concept requires observing loss of stable anchoring and flame-shape degradation over time.
- The source page double-checks that fuel-air-ratio decrease leads toward blow-off; the pass decision relies on visible flame evolution rather than page text.
- License note: the source is CC BY-SA 4.0 on Wikimedia Commons. Final release should preserve source attribution and share-alike obligations.

After round49, the authoritative main sample count is 115: 29 biology, 29 physics, 29 chemistry/materials, and 28 earth/environment.

## Concept-Name Tightening Update

The v10 concept-name review was operationalized in `scripts/build_vdcr_tiered_inventory.py`. The current builder now uses more mechanism-bearing recommended answers for over-broad labels.

Current sample answer renames:

| ID | Previous Answer | Current Answer |
|---|---|---|
| `vdcr_000025` | `Capillary Breakup` | `Capillary-Driven Jet/Thread Breakup` |
| `vdcr_000035` | `Convective Smoke Plume Rise` | `Buoyancy-Driven Smoke Plume Rise` |
| `vdcr_000056` | `Ciliary Beating` | `Coordinated Ciliary Beating Dynamics` |
| `vdcr_000060` | `Flame Front Propagation` | `Reactive Flame-Front Propagation` |
| `vdcr_000073` | `Gel Swelling` | `Osmotic Gel Swelling Dynamics` |
| `vdcr_000082` | `Crystal Nucleation` | `Crystal Nucleation-and-Growth Dynamics` |
| `vdcr_000085` | `Precipitation Front Propagation` | `Reaction-Precipitation Front Propagation` |
| `vdcr_000086` | `Medusan Bell-Contraction Jet Propulsion` | `Medusan Jet Propulsion by Bell Contraction` |
| `vdcr_000096` | `Embryonic Cleavage Division Sequence` | `Early Embryonic Cleavage Sequence` |

Post-tightening validation:

- Direct-answer main samples: 115
- MCQ/choice fields: 0
- Missing local media: 0
- Unique answers: 115
- Main concept tiers: 45 `core_main`, 70 `strict_main_candidate`
- Oracle score: 115/115

## Historical Pilot Samples Snapshot

The table below is a historical snapshot from before the current tiered sample builder. The authoritative current sample list is `data/vdcr_pilot_samples_direct_answer_v1.jsonl`.

| ID | Answer | Domain | Source Type |
|---|---|---|---|
| `vdcr_000001` | Endocytosis | biology_living_systems | Raw microscopy clip |
| `vdcr_000002` | Exocytosis | biology_living_systems | Raw microscopy clip |
| `vdcr_000003` | Dzhanibekov Effect / Tennis Racket Theorem | physics_physical_systems | Trimmed segment |
| `vdcr_000004` | Briggs-Rauscher Reaction | chemistry_materials_change | Trimmed segment |
| `vdcr_000005` | Double Pendulum Chaos | physics_physical_systems | Trimmed segment |
| `vdcr_000006` | Murmuration | biology_living_systems | Raw wildlife clip |
| `vdcr_000007` | Diffusion Flame | chemistry_materials_change | Raw experiment clip |
| `vdcr_000008` | Eskimo Roll / Kayak Roll | biology_living_systems | Raw sport-technique clip |
| `vdcr_000009` | Coronal Mass Ejection | physics_physical_systems | Raw coronagraph time series |
| `vdcr_000010` | Magnetic Reconnection | physics_physical_systems | Raw scientific animation |
| `vdcr_000011` | Solar Prominence Eruption | physics_physical_systems | Trimmed segment |
| `vdcr_000012` | Slab Avalanche Release | earth_environmental_systems | Trimmed historical avalanche segment |
| `vdcr_000013` | Belousov-Zhabotinsky Reaction | chemistry_materials_change | Trimmed reaction-diffusion wave segment |
| `vdcr_000014` | Pahoehoe Lava Roping | earth_environmental_systems | Trimmed ropy lava flow segment |
| `vdcr_000015` | Ice Cliff Calving | earth_environmental_systems | Trimmed glacier calving segment |
| `vdcr_000016` | Iodine Clock Reaction | chemistry_materials_change | Cropped delayed color-transition segment |
| `vdcr_000017` | Cytoplasmic Streaming | biology_living_systems | Trimmed microscopy segment |
| `vdcr_000018` | Thigmonasty | biology_living_systems | Raw Mimosa pudica touch-response clip |
| `vdcr_000019` | Shear Thickening | chemistry_materials_change | Trimmed oobleck shear-response segment |
| `vdcr_000020` | Aa Lava Front Advance | earth_environmental_systems | Trimmed public-domain volcano segment |
| `vdcr_000021` | Fire-Whirl Vortex Formation | earth_environmental_systems | Cropped wildfire whirl segment |
| `vdcr_000022` | Chemical Garden Growth | chemistry_materials_change | Trimmed Commons experiment segment |
| `vdcr_000023` | Blue Bottle Reaction | chemistry_materials_change | Trimmed Commons reaction segment |
| `vdcr_000024` | Phototropism | biology_living_systems | Raw Commons plant time-lapse |
| `vdcr_000025` | Tidal Bore | earth_environmental_systems | Trimmed Commons tidal-bore segment |
| `vdcr_000026` | Hydraulic Jump | physics_physical_systems | Trimmed Commons fluid experiment segment |
| `vdcr_000027` | Vortex Shedding / Karman Vortex Street | physics_physical_systems | Raw Commons water-channel flow visualization |
| `vdcr_000028` | Leidenfrost Droplet Motion | physics_physical_systems | Raw Commons hot-pan droplet-motion clip |
| `vdcr_000029` | Capillary Breakup | physics_physical_systems | Raw Commons capillary-flow breakup clip |
| `vdcr_000030` | Supercell Mesocyclone Rotation | earth_environmental_systems | Raw Commons/NOAA satellite loop |
| `vdcr_000031` | Supercooled Liquid Rapid Crystallization | chemistry_materials_change | Raw Commons sodium-acetate crystallization clip |
| `vdcr_000032` | Liesegang Ring Formation | chemistry_materials_change | Raw Commons precipitation-band experiment |
| `vdcr_000033` | Thin-Film Dewetting | chemistry_materials_change | Raw Commons/PMC dewetting supplementary movie |
| `vdcr_000034` | Bistable Snap-Trap Closure | biology_living_systems | Raw Commons Venus flytrap time-lapse |
| `vdcr_000035` | Gust Front Propagation | earth_environmental_systems | Raw Commons/NOAA satellite loop |
| `vdcr_000036` | Microtubule Dynamic Instability | biology_living_systems | Commons scientific animation |
| `vdcr_000037` | Calcium Wave Propagation | biology_living_systems | Commons/PLOS microscopy supplementary movie |
| `vdcr_000038` | Dust Storm Front Propagation | earth_environmental_systems | Raw Commons ground-view dust-front clip |
| `vdcr_000039` | Convective Smoke Plume Rise | earth_environmental_systems | Raw Commons/NOAA satellite loop |
| `vdcr_000040` | Brazil Nut Effect | physics_physical_systems | Raw Commons granular-convection clip |
| `vdcr_000041` | Liquid Bridge Pinch-Off | physics_physical_systems | Raw Commons two-fluid pinch-off clip |
| `vdcr_000042` | Spinodal Decomposition | chemistry_materials_change | Commons/Nature Communications simulation |
| `vdcr_000043` | Metachronal Wave Locomotion | biology_living_systems | Commons scientific ciliate animation |
| `vdcr_000044` | Pyroclastic Density Current | earth_environmental_systems | Commons/PHIVOLCS no-audio eruption footage |
| `vdcr_000045` | Meander Neck Cutoff | earth_environmental_systems | Commons satellite time-lapse GIF |
| `vdcr_000046` | Kelvin-Helmholtz Instability | physics_physical_systems | Commons public-domain simulation |
| `vdcr_000047` | Vortex Ring Formation | physics_physical_systems | Commons/Nature Communications no-audio segment |
| `vdcr_000048` | Bubble-Net Feeding | biology_living_systems | Commons no-audio ecological behavior clip |
| `vdcr_000049` | Dendritic Crystal Growth | chemistry_materials_change | Commons public-domain animation |
| `vdcr_000050` | Ostwald Ripening | chemistry_materials_change | Commons/Nature Communications no-audio lower-panel crop |
| `vdcr_000051` | Axonal Transport | biology_living_systems | Commons/PLOS microscopy movie |
| `vdcr_000052` | Phagocytosis | biology_living_systems | Commons microscopy movie |
| `vdcr_000053` | Debris-Flow Surge Propagation | earth_environmental_systems | Commons no-audio debris-flow segment |
| `vdcr_000054` | Plunging Breaker | earth_environmental_systems | Commons wave-flume animation |
| `vdcr_000055` | Pyrocumulus Development | earth_environmental_systems | Commons/NOAA no-label satellite loop |
| `vdcr_000056` | Cavitation Bubble Growth and Collapse | physics_physical_systems | Commons transparent gear-pump cavitation video |
| `vdcr_000057` | Chemical Traffic Light Reaction | chemistry_materials_change | Commons reaction time-lapse |
| `vdcr_000058` | Rayleigh-Taylor Instability | physics_physical_systems | Commons public-domain simulation GIF |
| `vdcr_000059` | Electrolysis Bubble Nucleation and Detachment | chemistry_materials_change | Commons/Nature Communications clean no-audio segment |
| `vdcr_000060` | Ciliary Beating | biology_living_systems | Commons/PLOS Genetics clean no-metadata microscopy segment |
| `vdcr_000061` | Gyroscopic Precession | physics_physical_systems | Commons public-domain animation GIF |
| `vdcr_000062` | Turbidity Current Propagation | earth_environmental_systems | SERC clean no-metadata segment; noncommercial license audit required |
| `vdcr_000063` | Nyctinasty | biology_living_systems | Commons cropped clean flower-opening segment |
| `vdcr_000064` | Flame Front Propagation | chemistry_materials_change | Commons clean no-audio flame-front propagation segment |
| `vdcr_000065` | Metal Displacement Dendrite Growth | chemistry_materials_change | Commons clean no-audio silver dendrite-growth segment |
| `vdcr_000066` | Gravitropism | biology_living_systems | Commons schematic root-curvature animation |
| `vdcr_000067` | Tornadogenesis | earth_environmental_systems | Commons clean no-audio tornado-formation time-lapse |
| `vdcr_000068` | Rayleigh-Plateau Breakup | physics_physical_systems | Commons silent water-drop necking and breakup video |
| `vdcr_000069` | Marangoni-Driven Flow | physics_physical_systems | Commons/Scientific Reports interfacial-flow video |
| `vdcr_000070` | Weissenberg Rod-Climbing Effect | chemistry_materials_change | MIT cropped clean rod-climbing segment; source-rights audit required |
| `vdcr_000071` | Plasmolysis and Deplasmolysis | biology_living_systems | Commons onion-cell microscopy time-lapse |
| `vdcr_000072` | River Avulsion | earth_environmental_systems | Google Earth Timelapse no-label Kosi River video |
| `vdcr_000073` | Glacier Surge | earth_environmental_systems | NPS public-domain Muldrow Glacier surge time-lapse |
| `vdcr_000074` | Taylor-Couette Vortices | physics_physical_systems | Commons/Scientific Reports cropped clean Taylor-Couette visualization |
| `vdcr_000075` | Crystallization Front Propagation | chemistry_materials_change | Commons potassium-permanganate crystallization video |
| `vdcr_000076` | Cytokinetic Furrow Ingression | biology_living_systems | Commons/PLOS cropped clean cell-division microscopy segment |
| `vdcr_000077` | Magnus Effect | physics_physical_systems | Commons simulation GIF showing rotation-coupled deflection |
| `vdcr_000078` | Gel Swelling | chemistry_materials_change | Commons/Nature Communications cropped clean hydrogel-swelling segment |
| `vdcr_000079` | Membrane Blebbing | biology_living_systems | Commons/PLOS microscopy video |
| `vdcr_000080` | Headward Erosion | earth_environmental_systems | Commons sand-slope erosion video |
| `vdcr_000081` | Thermocapillary Convection | physics_physical_systems | Commons/Nature Communications cropped metadata-stripped infrared droplet segment |
| `vdcr_000082` | Evaporation-Induced Deposition Front | chemistry_materials_change | Commons/Nature Communications metadata-stripped deposition-front segment |
| `vdcr_000083` | Actin Wave | biology_living_systems | Commons/PLOS metadata-stripped microscopy segment |
| `vdcr_000084` | Braided Channel Migration | earth_environmental_systems | NASA/Commons metadata-stripped satellite time-lapse |
| `vdcr_000085` | Faraday Waves | physics_physical_systems | Commons metadata-stripped singing-bowl liquid-surface wave video |
| `vdcr_000086` | C-Start Escape Response | biology_living_systems | Commons/PLOS clean textless predator-prey escape segment |
| `vdcr_000087` | Crystal Nucleation | chemistry_materials_change | Commons cropped textless MAPbI3 crystal nucleation segment |
| `vdcr_000088` | Internal Wave Propagation | earth_environmental_systems | Commons/Nature Communications metadata-stripped temperature-anomaly propagation animation |
| `vdcr_000089` | Euler's Disk Motion | physics_physical_systems | Commons cropped metadata-stripped rolling-precession disk segment |
| `vdcr_000090` | Precipitation Front Propagation | chemistry_materials_change | Commons cropped metadata-stripped droplet precipitation-front segment |
| `vdcr_000091` | Medusan Bell-Contraction Jet Propulsion | biology_living_systems | Commons no-audio metadata-stripped jellyfish bell-contraction propulsion video |
| `vdcr_000092` | Rip Current Formation | earth_environmental_systems | Commons CC0 textless no-audio segment from rip-current formation video |
| `vdcr_000093` | Rayleigh-Benard Convection | physics_physical_systems | Commons no-audio metadata-stripped Benard-cell convection video |
| `vdcr_000094` | Reaction-Diffusion Wave | chemistry_materials_change | Commons no-audio metadata-stripped scientific visualization GIF derivative |
| `vdcr_000095` | Neutrophil Chemotaxis | biology_living_systems | Commons/PLOS no-audio metadata-stripped microfluidic chemotaxis racecourse video |
| `vdcr_000096` | Downburst / Microburst Outflow | earth_environmental_systems | Commons no-audio metadata-stripped downburst wind/rain outflow video |
| `vdcr_000097` | Saffman-Taylor Viscous Fingering | physics_physical_systems | Commons metadata-stripped viscous-fluid fingering GIF derivative |
| `vdcr_000098` | FRAP Recovery | biology_living_systems | Commons/PLOS metadata-stripped fluorescence recovery time-series video |
| `vdcr_000099` | Gully Headcut Retreat | earth_environmental_systems | Commons metadata-stripped headcut/upward-erosion video |
| `vdcr_000100` | Freeze-Induced Phase Separation | chemistry_materials_change | Commons/PLOS title-trimmed metadata-stripped microscopy video |

## Quality Lessons

- Archive search is useful for candidate discovery but noisy. It produces many long compilation videos, lecture videos, entertainment clips, and wrong-sense matches.
- Query context matters. Sport terms such as `Elastico` must include soccer/football context, otherwise they retrieve unrelated elasticity/flexibility content.
- Biomedical concept terms can retrieve ASL/sign-language dictionary clips; these are now filtered.
- Many relevant videos require trimming because title cards or overlays directly reveal the answer.
- Direct-answer construction is viable: samples contain no MCQ choices and can be scored by normalized exact/alias matching.
- Earth/environment retrieval is especially noisy on Archive: many matches are historical documentaries, news, interviews, games, or wrong-sense title matches. The first usable earth sample came from trimming a long avalanche dynamics film.
- Chemistry/materials retrieval is more productive when the source title directly names a reaction. Still, duplicates should be controlled at the concept level; only one BZ reaction sample is currently admitted.
- For long source videos, pass status applies to the cleaned segment, not the full raw video. The raw source may remain `revise` or `review` if maps, captions, title cards, or unrelated scenes appear elsewhere.
- Targeted earth retrieval produced two additional usable segments: `Pahoehoe Lava Roping` and `Ice Cliff Calving`. The `Ice Cliff Calving` segment was shortened from 42-60s to 42-55s to remove the later title card.
- `Iodine Clock Reaction` became usable only after segmenting the delayed color transition and cropping the bottom subtitle area. The full raw video remains a risky review item because setup labels and captions appear elsewhere.
- `Cytoplasmic Streaming` was admitted only from the clean late microscopy segment. The earlier labeled teaching frames remain excluded because they contain distracting biological labels.
- Round2 downloaded 12 additional source videos; 1 became pass (`Thigmonasty`), 1 became revise (`Shear Thickening`), 4 remain review leads, and 6 were rejected for text leakage, static/non-target footage, or explainer mismatch.
- For duplicate clean source clips, only one sample is admitted per concept. Two additional Mimosa pudica clips remain review-only duplicates because `vdcr_archive_b03_000027` already covers `Thigmonasty`.
- `Shear Thickening` became usable after trimming to the oobleck handling window. The full source is not release-ready because it includes charts, title/text overlays, ad-like scenes, and unrelated ballistic tests.
- Round3 earth Archive search with narrow terms produced only four new candidates; all were too weak or wrong-target, so production pivoted back to already downloaded targeted earth footage.
- `Aa Lava Front Advance` was admitted only from 120-145s of the public-domain `Volcanoes` source. The full film has mixed volcano scenes and credits, so only the clean blocky lava-front segment should be treated as pass.
- Commons API remained blocked by 403 Too Many Reqs during the round4 probe, so no Commons-derived earth samples were added in this step.
- `Fire Whirl` became usable only after cropping the news footage to remove captions, credits, and logos. The pass segment contains the rotating fire column and smoke field without visible answer text.
- `data/vdcr_concept_pool_v1.csv` now operationalizes the v2 concept-name review into `main_pool`, `strict_gate`, `stress_slice`, and `extension` tiers. Production should prioritize `main_pool` plus carefully audited `strict_gate`; human/sport concepts remain capped stress-slice items.
- Archive round1/round2 main-pool searches produced no new candidates after duplicate filtering, confirming that Archive has already been saturated for several common science terms. Production should not keep re-querying the same Archive hits.
- Manual Commons sourcing added six new source videos. Five became pass candidates after trimming or raw review: `Chemical Garden Growth`, `Blue Bottle Reaction`, `Phototropism`, `Tidal Bore`, and `Hydraulic Jump`.
- Commons direct `Special:Redirect/file` downloads were rate-limited, but original `upload.wikimedia.org` media URLs worked. The failed redirect attempt is recorded in `data/vdcr_commons_manual_download_status_round1_v1.csv`; successful direct downloads are recorded in `data/vdcr_commons_manual_download_status_round1_v1_all.csv`.
- `Chemical Garden Growth` required trimming to 8-20s to remove title text and credits. `Blue Bottle Reaction` required trimming to 20-150s to remove the opening whiteboard answer. `Hydraulic Jump` required trimming to 20-55s to remove the Russian title card and later schematic. `Tidal Bore` was trimmed to a propagation window. `Phototropism` was clean as raw time-lapse.
- `Ciliary Beating` was rejected because the Commons/PLOS source describes immotile cilia, so the video does not instantiate the target dynamic concept.
- `reports/vdcr_concept_name_review_v3.md` further tightened the concept-name policy. `data/vdcr_concept_pool_v1.csv` now has 50 main-pool concepts after demoting static-shortcut-prone names such as `Crown Splash`, `Worthington Jet`, `Standing Wave Formation`, `Tidal Bore`, and `Hydraulic Jump` to strict gate.
- Manual Commons round2 added six new source videos. Four became pass candidates: `Vortex Shedding / Karman Vortex Street`, `Leidenfrost Droplet Motion`, `Capillary Breakup`, and `Supercell Mesocyclone Rotation`.
- `Tornadogenesis` was rejected despite a strong source because the visible tornado funnel creates a static shortcut and risks generic tornado recognition. `Pyroclastic Density Current` was rejected because the clip is a lab analogue whose target label depends too heavily on the source page.
- Manual Commons round3 added nine source videos. Five became pass candidates: `Supercooled Liquid Rapid Crystallization`, `Liesegang Ring Formation`, `Thin-Film Dewetting`, `Bistable Snap-Trap Closure`, and `Gust Front Propagation`.
- `Electrodeposition Dendrite Growth` was rejected because the video shows existing copper crystals being handled rather than electrodeposition growth. `Downburst / Microburst Outflow` was rejected because it is visually too close to generic storm footage. `Crystallization Front Propagation` was rejected for explicit in-frame scientific text. `Bubble-Net Feeding` is visually strong but remains review-only until the Commons external-source license review is resolved.
- `reports/vdcr_concept_name_review_v4.md` tightened the concept-name policy again: all ball-sport tactics were moved from stress-slice to extension, leaving only cross-system human specialty movement as a capped stress slice. v1 production should not use ball-sport items to fill sample quotas.
- Manual Commons round4 added ten source videos. Four became pass candidates: `Microtubule Dynamic Instability`, `Calcium Wave Propagation`, `Dust Storm Front Propagation`, and `Convective Smoke Plume Rise`.
- Round4 rejected both chromosome-segregation candidates because the visual evidence did not show a clean alignment-to-separation sequence. It also rejected the second calcium-wave and second dust-storm candidates as lower-quality duplicates. `Ciliary Beating` and `Pyrocumulus Development` remain review-only until visual/source dependence is resolved.
- Manual Commons round5 added three physics source videos. Two became pass candidates: `Brazil Nut Effect` and `Liquid Bridge Pinch-Off`. `Marangoni-Driven Flow` remains revise-only because the opening title card and dish labels leak answer/setup text.
- Manual Commons round6 added three source videos. `Spinodal Decomposition` became a pass candidate. `FRAP Recovery` was rejected as a labeled figure-panel/source-dependent experiment, and `Gravitropism` was rejected because the clip instantiates a source-described competition between gravitropism and phototropism rather than a clean single target.
- Manual Commons round7 added three source videos. `Metachronal Wave Locomotion` became a pass candidate from a clean scientific ciliate animation. `Ciliary Beating` remains review-only because the sparse contact sheet does not make the beating visually strong enough for direct-answer admission without video playback review. `Meander Neck Cutoff` remains revise-only because the GIF contains visible `Oxbow Lake is formed` and `Flooding` text leakage.
- The masked no-text derivative of `OxbowAnimation.gif` was not admitted because the mask removed answer text but also obscured the key meander-neck dynamics. This is recorded as a failed revise attempt rather than a pass.
- Manual Commons round8 added three earth/environment source videos. Two became pass candidates: `Pyroclastic Density Current` from a no-audio PHIVOLCS eruption derivative and `Meander Neck Cutoff` from the Ucayali River satellite time-lapse. The Nature Communications lab analogue for `Pyroclastic Density Current` was rejected because the apparatus makes the target too source-dependent.
- Manual Commons round9 added six non-earth source videos. Three became pass candidates: `Kelvin-Helmholtz Instability`, `Vortex Ring Formation`, and `Bubble-Net Feeding`. `Electrodeposition Dendrite Growth` was rejected because the clip shows existing copper crystals rather than growth, and `Bacterial Swarming Motility` was rejected because it is mostly trajectory overlay rather than a clean swarm visual. `Neutrophil Chemotaxis` remains review-only because the arrow/gradient context makes the current video partly source-dependent.
- `Vortex Ring Formation` was admitted only after cutting a no-audio segment from 3.0-35.5s to remove the opening schematic/text. `Bubble-Net Feeding` was admitted as a no-audio local derivative, but it still needs final Commons external-source license audit before release.
- Manual Commons round10 added five chemistry/materials source videos. Two became pass candidates: `Dendritic Crystal Growth` and `Ostwald Ripening`. `Crystallization Front Propagation` and `Marangoni-Driven Flow` remain revise-only because visible title/setup text remains difficult to remove without weakening the dynamic evidence. `Crystal Nucleation` was rejected because the video is a labeled scientific visualization and too source-dependent.
- `Ostwald Ripening` was admitted only after making a no-audio lower-panel crop from 12-46s, removing interstitial title text while preserving foam coarsening dynamics.
- Manual Commons round11 added four source videos. Two became pass candidates: `Axonal Transport` and `Phagocytosis`. `Downburst / Microburst Outflow` was rejected because the clip remains visually generic storm footage, and `Tornadogenesis` remains review-only because the tornado-funnel static shortcut and label scope need stricter gating.
- Manual Commons round12 added seven earth/environment source videos. Three became pass candidates: `Debris-Flow Surge Propagation`, `Plunging Breaker`, and `Pyrocumulus Development`. `Rip Current Formation` remains review-only because the surf-zone flow direction is not yet visually decisive from the contact sheet. `Seismic Soil Liquefaction` was rejected because the GIF is a generic liquefaction schematic without seismic forcing. `Barchan Dune Migration` was rejected for visible title leakage and static flyover footage.
- Manual Commons round13 added six physics/chemistry source videos. Three became pass candidates: `Cavitation Bubble Growth and Collapse`, `Chemical Traffic Light Reaction`, and `Rayleigh-Taylor Instability`. `Faraday Waves` remains review-only because the bead assembly GIF does not visually expose the liquid wave itself strongly enough. `Electrodeposition Dendrite Growth` was rejected because electrodeposition is visible but branching dendritic growth is not clear. `Compactification` was rejected for explanatory labels and duplicate cavitation answer risk.
- Manual Commons round14 added four source videos. Two became pass candidates: `Electrolysis Bubble Nucleation and Detachment` and `Ciliary Beating`. Both pass samples use clean local derivatives with no audio stream and no answer-bearing source metadata. Two chromosome-segregation candidates were rejected: one was a congression simulation rather than a clean segregation sequence, and one had visible phase/time overlays plus insufficient chromosome-level evidence.
- Manual Commons round15 added five source videos. Three became pass candidates: `Gyroscopic Precession`, `Turbidity Current Propagation`, and `Nyctinasty`. `Turbidity Current Propagation` is visually strong but carries a CC BY-NC-SA license audit risk. `Coffee-Ring Formation` and `FRAP Recovery` were rejected because their clips are figure-like multi-panel videos with labels/metadata and weak clean video-native evidence.
- Manual Commons round16 added two chemistry/materials source videos. `Flame Front Propagation` became a pass candidate only after generating a clean no-audio derivative. `Precipitation Front Propagation` was rejected because the source contains prominent German title/instruction/end text and visually shows generic cloudy precipitation rather than a clean propagating front.
- Manual Commons round17 added seven source videos. Four became pass candidates: `Metal Displacement Dendrite Growth`, `Gravitropism`, `Tornadogenesis`, and `Rayleigh-Plateau Breakup`. `Crown Splash` was rejected because the source was a branded CGI paint ad with visible product text. `Mitotic Chromosome Segregation` was rejected because the microscopy sequence did not clearly show chromosome separation. `Downburst / Microburst Outflow` was rejected because it looked like generic severe rain/wind without decisive outflow structure.
- Round17 has two boundary-risk pass samples that need final sampling attention: `Gravitropism` is a schematic animation with static-diagram shortcut risk, and `Tornadogenesis` has a mature-funnel shortcut risk. They are included as pass candidates because their temporal mechanism is visible, but final release review should decide whether to keep them in the main set or move them to analysis-only.
- Manual Commons/scientific-source round18 added five source videos. Four became pass candidates: `Marangoni-Driven Flow`, `Weissenberg Rod-Climbing Effect`, `Plasmolysis and Deplasmolysis`, and `River Avulsion`. The freezing-soap-bubble backup was rejected because its visual evidence is source-dependent and more naturally reads as freezing/crystallization rather than Marangoni-driven flow.
- `Weissenberg Rod-Climbing Effect` uses a cropped clean derivative to remove bottom lab text; final release must audit MIT source rights before publication.
- `River Avulsion` uses a no-label Google Earth Timelapse clip under CC BY 4.0 and needs attribution to Google Earth Timelapse, Google, Landsat, and Copernicus.
- `Plasmolysis and Deplasmolysis` is a strict-gate microscopy sample: the motion is visible but subtle, so final release review should verify that the shrinkage/recovery sequence is apparent in playback, not only source metadata.
- Manual/public-source round19 added seven source videos. Four became pass candidates: `Glacier Surge`, `Taylor-Couette Vortices`, `Crystallization Front Propagation`, and `Cytokinetic Furrow Ingression`.
- Round19 rejected `Faraday Waves` because the bead-assembly GIF does not visibly expose the surface wave, rejected `Electrodeposition Dendrite Growth` because it shows already-grown crystals being handled rather than growth, and rejected `FRAP Recovery` because the frame contains answer-level `FRAP ROI` text.
- `Taylor-Couette Vortices` and `Cytokinetic Furrow Ingression` use cropped clean no-audio derivatives with answer-bearing panels/time overlays removed and source metadata stripped.
- `Glacier Surge` is a strict long-timescale NPS sample: final review should verify playback-level glacier-front advance, not rely only on the contact sheet.
- `Crystallization Front Propagation` is strict because static crystals create a shortcut risk; the admitted evidence must be the moving/retreating crystallization front and growth sequence.
- Manual Commons/scientific-source round20 added ten source videos. Four became pass candidates: `Magnus Effect`, `Gel Swelling`, `Membrane Blebbing`, and `Headward Erosion`; five were rejected and one remained review-only.
- `Gel Swelling` uses a cropped clean derivative of the hydrogel strip movie to remove visible time/speed text while preserving the swelling-driven bending trajectory.
- `Hydrogel micropump` was rejected for `Gel Swelling` because the visible process is device actuation rather than clear swelling/deswelling. `Crystal Growth` was rejected for `Crystal Nucleation` because no new-nucleus onset is clear. The guard-cell-category video was rejected because it is a whole-plant ozone-exposure timelapse with text, not stomatal opening/closing.
- Both sediment-transport candidates were rejected for `Sediment Saltation` because they show granular creep/bed rearrangement with time/scale overlays rather than decisive hopping grain trajectories.
- Concept-name cleanup after v6 review tightened several answer labels: `Fire Whirl` is now produced as `Fire-Whirl Vortex Formation`; broad animal locomotion labels were narrowed to `Medusan Bell-Contraction Jet Propulsion` and `Anguilliform Undulation`; `Cleavage` was renamed to `Embryonic Cleavage Division Sequence`. `Downburst / Microburst Outflow` and `Tornadogenesis` remain valid but are now strict-gate seeds rather than automatic main-pool fillers.
- Manual Commons round22 added nine source videos. Two became pass candidates: `Faraday Waves` and `C-Start Escape Response`. `Faraday Waves` uses a no-audio metadata-stripped singing-bowl derivative that shows vibration-driven liquid-surface wave emergence. `C-Start Escape Response` uses a 15-20s clean segment that removes title cards and preserves the rapid C-shaped bend-and-escape sequence.
- Round22 rejected seven candidates: the bead Faraday-wave GIF was a duplicate lower-information source; the standing-wave GIF was too classroom-basic; the copper electrodeposition clip did not show visible dendritic growth; the coffee-ring clip had labels and static deposition shortcut risk; the sediment-saltation GIF was a single labeled diagram rather than video evidence; the barchan-dune clip showed camera flyover/static dunes rather than migration; the thunderstorm clip lacked downburst outflow structure and would collapse into generic storm understanding.
- Manual Commons round23 added six source videos. Two became pass candidates: `Crystal Nucleation` and `Internal Wave Propagation`, bringing all four top-level domains to 22 samples each.
- `Crystal Nucleation` uses a heavily cropped no-audio derivative of the MAPbI3 crystal-growth video. The crop removes title/time overlays and preserves the visual onset of a small crystal from solution followed by faceted growth. The full raw video remains unsuitable because its visible text directly describes crystal growth and experimental conditions.
- `Internal Wave Propagation` uses a no-audio metadata-stripped scientific animation of temperature anomalies moving across an ocean-drifter array. It is a strict-gate scientific-visualization sample, not a natural camera clip; final release review should decide whether to count it in the main set or keep it as an instrumented-science subset.
- Round23 rejected four candidates: the nanorod crystallization movie was too source-dependent and overlay-heavy; the Coriolis Platform internal-wave candidate mostly showed apparatus animation; the first rip-current video failed download in this round; the second rip-current video was text-heavy and the current was not decisive without annotations.
- `Slime Mold Aggregation` remains review-only: the video is visually relevant but currently reads more like plasmodial expansion/foraging than aggregation, so the concept label needs tightening before admission.
- Manual Commons/scientific-source round21 added eight source videos plus four clean metadata-stripped derivatives. Four became pass candidates: `Thermocapillary Convection`, `Evaporation-Induced Deposition Front`, `Actin Wave`, and `Braided Channel Migration`.
- Round21 rejected `Electric Arc Formation and Bending` because the clip reads as a generic apparatus arc flash rather than a robust named dynamic process; rejected duplicate deposition-front and actin-wave candidates to preserve concept-level deduplication; and rejected `Mitochondrial Fission-Fusion Dynamics` because individual fission/fusion events were not visually decisive without source metadata.
- All four round21 pass samples use clean local derivatives with answer-bearing source metadata stripped. `Thermocapillary Convection` also uses a crop to remove visible experimental-condition text.
- Manual Commons round24 added five source videos. Two became pass candidates: `Euler's Disk Motion` and `Precipitation Front Propagation`. Both pass samples use cropped no-audio metadata-stripped derivatives: the Euler disk crop removes the bottom rim label while preserving rolling-precession-wobble-collapse dynamics, and the precipitation-front crop removes microscope parameter text while preserving the droplet-internal precipitate spread.
- Round24 rejected three candidates: both mitotic-chromosome-segregation microscopy candidates were too subtle/source-dependent for direct-answer admission, and the rip-current candidate looked like a generic surf scene without a decisive offshore-directed channel.
- Manual Commons round25 added eight source videos. One became a pass candidate: `Medusan Bell-Contraction Jet Propulsion`, using a no-audio metadata-stripped jellyfish video that preserves repeated bell contraction and relaxation. Seven candidates were rejected: three FRAP candidates lacked visually decisive recovery, the stomatal-closure candidate showed source-dependent plant-cell panels rather than clear guard-cell aperture dynamics, the soil-liquefaction GIF was too schematic, the lava-dome-collapse GIF was only a two-frame before/after comparison, and the eruption-column candidate showed generic plume growth with logo/time overlays rather than column collapse.
- Manual Commons round26 added four earth/environment candidates. One became a pass candidate: `Rip Current Formation`, using a clean no-audio 66-78s segment from a CC0 Commons rip-current formation video. The full raw video remains `revise` because it contains title cards, arrows, German explanatory text, and end credits. Three candidates were rejected: the dike-overtopping simulator was an engineering/text-heavy erosion setup rather than clear rill-network expansion, the barchan-dune video was a static Mars flyover rather than migration, and the tornado clip showed a mature funnel without landspout-specific development.
- Manual Commons round27 added six source videos after Commons API search was rate-limited. Two became pass candidates: `Rayleigh-Benard Convection`, using a clean no-audio Benard-cell convection video, and `Reaction-Diffusion Wave`, using a no-audio metadata-stripped scientific visualization derivative. Four candidates were rejected or kept revise-only: one Rayleigh-Benard screen-recording had border/title leakage risk, one longer Rayleigh-Benard clip was lower-priority duplicate/ambiguous, the bacterial motility clip did not establish chemotaxis, and the short slime-mold clip did not show aggregation.
- Manual Commons round28 added five biology/earth candidates. One became a pass candidate: `Neutrophil Chemotaxis`, using a no-audio metadata-stripped microfluidic racecourse video in which fluorescent cells migrate through channels over time. Four candidates were rejected: one neutrophil clip lacked decisive directed migration, the amoeboid crawling clip did not establish chemotaxis without source metadata, the filopodium clip had a static shortcut and weak temporal sequence, and the Dixie Fire map visualization was rejected because it would become map/metadata reading rather than raw video-native earth dynamics.
- Manual Commons round29 added two downburst/microburst candidates. One became a pass candidate: `Downburst / Microburst Outflow`, using a no-audio metadata-stripped Commons downburst video that shows a sudden near-surface lateral wind/rain burst sweeping across buildings and vegetation over time. The second microburst candidate was rejected because visible date/location overlay and generic storm-cloud/rain-shaft evidence made the answer too dependent on the source page.
- Manual Commons round30 added five candidates. Two became pass candidates: `Saffman-Taylor Viscous Fingering`, using a metadata-stripped GIF derivative of finger-like air/liquid invasion in a viscous medium, and `FRAP Recovery`, using a metadata-stripped fluorescence recovery time-series video. Three candidates were rejected: the coffee-ring movie had multi-panel PEG/SDS labels and static deposit shortcut risk, the lithium electrodeposition movie did not show decisive dendritic branching and came from a dendrite-free study, and the wildfire satellite loop was too logo/timestamp/source-context dependent for `Wind-Driven Fire-Front Propagation`.
- Manual Commons round31 added five candidates. Two became pass candidates: `Gully Headcut Retreat`, using a metadata-stripped upward-erosion/headcut-retreat video, and `Freeze-Induced Phase Separation`, using a title-trimmed metadata-stripped microscopy movie. `Benedict Positive Reducing-Sugar Reaction` was rejected because visible experiment labels and reagent context made the answer source-dependent, one Benedict backup failed download, and `Lava Dome Collapse` was rejected because the short satellite/false-color GIF did not show a decisive collapse sequence.
- `Freeze-Induced Phase Separation` was added to the concept inventory as a strict-gate chemistry/materials concept because the accepted video evidence is a dynamic freezing/melting microscopy sequence rather than a static chemical label.
- Current direct-answer sample distribution is 28 physics, 28 chemistry/materials, 28 biology, and 28 earth/environment; all 112 answers are concept-level unique.

## Next Work

1. Continue Commons/manual public-source retrieval only from `core_main` and strong `strict_main_candidate` concepts; do not use `extension` or `stress_slice` to fill main quotas.
2. Continue balanced production across all four main domains, preserving concept-level diversity.
3. Keep concept-level deduplication: one pass sample per answer unless a later release explicitly allows multiple clips per concept.
4. Use `reports/vdcr_review_dashboard_v1.html` for pass/reject/revise/source/gate review; it now includes 296 review rows and 115 samples.
5. Run a final license/source audit before treating `pass_candidate` rows as release-ready.
