# VDCR V2 Retrieval Status

Date: 2026-06-20

## Active Background Runs

### Shard 0-120, Commons + Archive

```text
run_id=v2_shard_000_120_20260620T040948Z
pid=168567
run_dir=runs/v2_retrieval/v2_shard_000_120_20260620T040948Z
log=runs/v2_retrieval/v2_shard_000_120_20260620T040948Z/retrieval.log
```

This shard was launched with the default source setting (`VDCR_SOURCES=both`).
Commons is currently returning `403 Too Many Reqs`, so the shard is recording
Commons skipped rows and will continue into Archive search.

### Shard 120-240, Archive Only

```text
run_id=v2_archive_shard_120_240_20260620T041144Z
pid=169847
run_dir=runs/v2_retrieval/v2_archive_shard_120_240_20260620T041144Z
log=runs/v2_retrieval/v2_archive_shard_120_240_20260620T041144Z/retrieval.log
```

This shard was launched with `VDCR_SOURCES=archive` to avoid wasting time while
Commons is throttled. Outputs are written under `runs/`, which is ignored by git.

## Monitoring Commands

```bash
ps -p 168567 -o pid,etime,cmd
ps -p 169847 -o pid,etime,cmd

tail -f runs/v2_retrieval/v2_shard_000_120_20260620T040948Z/retrieval.log
tail -f runs/v2_retrieval/v2_archive_shard_120_240_20260620T041144Z/retrieval.log

cat runs/v2_retrieval/v2_shard_000_120_20260620T040948Z/summary.txt
cat runs/v2_retrieval/v2_archive_shard_120_240_20260620T041144Z/summary.txt
```

## Next Shard Commands

If Archive-only retrieval remains stable, continue with:

```bash
VDCR_SOURCES=archive VDCR_QUERY_OFFSET=240 VDCR_QUERY_LIMIT=120 VDCR_PER_QUERY=5 \
  bash scripts/start_v2_retrieval_background.sh
```

When Commons throttling cools down, retry Commons-only shards:

```bash
VDCR_SOURCES=commons VDCR_QUERY_OFFSET=0 VDCR_QUERY_LIMIT=120 VDCR_PER_QUERY=5 \
  bash scripts/start_v2_retrieval_background.sh
```
