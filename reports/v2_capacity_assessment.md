# VDCR V2 Capacity Assessment

Date: 2026-06-20

## Recommendation

Use **240 clean video-concept samples** as the first V2 target, with a stretch
target of **300** after the expansion pipeline proves yield.

Recommended V2 target:

- unique concepts: 160-180
- total videos: 240
- default concept-cluster cap: 3 videos per concept
- domain target: about 60 videos per domain

Stretch target:

- unique concepts: 200-220
- total videos: 300
- domain target: about 75 videos per domain

This keeps the benchmark close to Video-MMMU's video scale while preserving
VDCR's stricter video-to-concept grounding requirement.

## Current Capacity Evidence

Current v1 release:

- 114 clean source-hidden samples
- 114 unique concepts
- four-domain balance: biology 29, chemistry/materials 29, earth/environment
  28, physics 28

Current tiered concept inventory:

- 194 main-eligible concepts (`core_main` + `strict_main_candidate`)
- 114 concepts already used in v1
- 80 remaining main-eligible concepts

Remaining main-eligible concepts by domain:

| Domain | Remaining concepts |
|---|---:|
| physics_physical_systems | 25 |
| biology_living_systems | 20 |
| earth_environmental_systems | 20 |
| chemistry_materials_change | 15 |

Current candidate pool:

- 593 source-deduplicated candidates
- 296 reviewed rows
- 395 currently unreviewed candidates

Unreviewed candidates by domain:

| Domain | Unreviewed candidates |
|---|---:|
| biology_living_systems | 191 |
| earth_environmental_systems | 84 |
| physics_physical_systems | 83 |
| chemistry_materials_change | 37 |

Observed reviewed-pass rates are roughly 18-35% depending on domain, before
final license, leakage, and release filtering. This means the current pool can
likely support a V1.1 expansion, but not a clean 300-video V2 by itself.

## Why 240 First

A strict one-concept-one-video policy is capped by the current 194
main-eligible concepts and will likely land below that after source and leakage
losses.

V2 should therefore scale with concept clusters:

```text
video_concept_sample = one clean video or segment + one grounded dynamic concept
concept_cluster = all samples sharing the same concept_id or canonical answer
```

A realistic 240-video target can look like:

| Cluster type | Concepts | Videos per concept | Videos |
|---|---:|---:|---:|
| singleton | 120 | 1 | 120 |
| paired | 45 | 2 | 90 |
| triple | 10 | 3 | 30 |
| total | 175 | - | 240 |

This keeps concept diversity high while using repeated concepts only where
multiple visually distinct videos are available.

## 300-Video Stretch

A 300-video target should be attempted after the 240-video target proves yield.
One plausible structure:

| Cluster type | Concepts | Videos per concept | Videos |
|---|---:|---:|---:|
| singleton | 140 | 1 | 140 |
| paired | 55 | 2 | 110 |
| triple | 15 | 3 | 45 |
| limited fourth exemplar | 1-2 | 4 | 5 |
| total | about 211 | - | 300 |

The fourth-exemplar bucket should be rare and reserved for unusually strong
concepts with clearly different visual realizations. The default cap remains 3.

## Expansion Strategy

1. Expand the concept inventory from 194 to at least 250-300 main-eligible
   concepts.
2. Prioritize concepts with medium/high public video availability and medium/low
   static shortcut risk.
3. Search multiple sources per concept, with Wikimedia Commons preferred and
   Internet Archive used as a secondary source.
4. Review videos independently; repeated-concept videos must show different
   scenes, materials, organisms, scales, viewpoints, or implementations.
5. Report both video-level and concept-balanced metrics.

## Background Execution

Use `scripts/start_v2_retrieval_background.sh` to launch retrieval shards with
`nohup`. Outputs go to ignored `runs/v2_retrieval/<run_id>/` directories so long
jobs survive shell disconnects and do not pollute tracked `data/` or `logs/`
until reviewed.

When Commons throttles with `403 Too Many Reqs`, use Archive-only shards:

```bash
VDCR_SOURCES=archive VDCR_QUERY_OFFSET=120 VDCR_QUERY_LIMIT=120 VDCR_PER_QUERY=5 \
  bash scripts/start_v2_retrieval_background.sh
```
