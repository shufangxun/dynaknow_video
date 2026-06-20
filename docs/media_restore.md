# Media Restore

`media/` is a local video cache. It is ignored by git because video files and
frame artifacts are large, but it is required for `--check-media` validation and
video model evaluation.

Do not remove `media/` as routine cleanup.

## What Belongs In `media/`

Typical subdirectories include:

- raw downloaded videos;
- clean local segments cut from longer videos;
- extracted first/middle/last/sparse frames;
- contact sheets for visual review.

The current release references local media paths through
`release/v1/dataset_v1.jsonl`. Source and provenance information is kept in
`release/v1/manifest_v1.csv` and construction manifests under `data/`.

## Check Whether Media Is Present

Run:

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

Missing `local_media does not exist` errors mean the local cache must be
restored before video evaluation can run.

## Restore Strategy

For a fresh checkout, restore only the current release media first. The current
release uses 114 local media paths, and most can be traced back to construction
manifests in `data/`.

Recommended order:

1. Recreate required raw downloads from relevant `data/*media_manifest*.csv`
   rows and `release/v1/manifest_v1.csv`.
2. Recreate required no-audio segments from `data/*segment_manifest*.csv`.
3. Re-run the release validator with `--check-media`.
4. Only restore historical review media if you need to reproduce old
   construction dashboards or audits.

The broad historical `media/` tree is not required to understand the benchmark.
The current `release/v1/` media is required to run the benchmark.

## Cleanup Rule

Safe cleanup should target caches and generated runtime outputs, not benchmark
media. Before deleting ignored files, dry-run:

```bash
git clean -fdX -n
```

If the dry-run includes `media/`, do not run the destructive command unless you
have an external backup or explicitly want to rebuild the local video cache.
