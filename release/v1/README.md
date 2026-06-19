# VDCR v1 Direct-Answer Pilot Release

This package is a source-hidden, locally runnable evaluation snapshot for dynamic video concept recognition.

Task:

```text
Which named dynamic concept is instantiated by the temporally evolving process in this video?
```

Files:

- `dataset_v1.jsonl`: evaluation JSONL. It excludes source URLs, titles, and license notes.
- `dataset_v1_mcq_seed20260619.jsonl`: constructed four-choice MCQ variant derived from the direct-answer gold set.
- `manifest_v1.csv`: provenance and license/source audit fields. Do not pass this file to models.
- `stats_v1.md`: sample count, domain distribution, concept type distribution, and duration summary.

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
  --input release/v1/dataset_v1.jsonl \
  --release-mode \
  --check-media \
  --min-samples 100 \
  --min-duration-sec 1.0 \
  --min-video-frames 2 \
  --max-domain-imbalance 1
```
