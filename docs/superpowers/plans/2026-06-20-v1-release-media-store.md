# V1 Release Media Store Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a script that materializes the VDCR v1 release videos into a shared `release/media/videos/` store and writes metainfo linking V1 samples to shared media assets.

**Architecture:** Add one focused Python CLI, `scripts/materialize_v1_release_media.py`, with pure helpers for parsing V1 media references, indexing existing manifests, and writing release metadata. The CLI resolves each V1 sample from `release/v1/dataset_v1.jsonl` plus `manifest_v1.csv`, copies an existing local media file when present, otherwise downloads the original source file and rebuilds simple time clips with ffmpeg.

**Tech Stack:** Python standard library, existing JSONL/CSV files, `urllib`, `subprocess` for `ffmpeg`, and pytest.

---

### Task 1: Parse V1 Media References

**Files:**
- Create: `tests/test_v1_release_media_store.py`
- Create: `scripts/materialize_v1_release_media.py`

- [ ] **Step 1: Write failing tests**

Create tests for extracting source ids, segment times, derivative flags, and release asset names from V1 `local_media` paths.

- [ ] **Step 2: Run tests to verify failure**

Run: `python3 -m pytest tests/test_v1_release_media_store.py -q`
Expected: import failure because `scripts.materialize_v1_release_media` does not exist.

- [ ] **Step 3: Implement minimal parsing helpers**

Add dataclass `MediaPlan` and helper `plan_media_asset(video_id, local_media)`.

- [ ] **Step 4: Run tests to verify pass**

Run: `python3 -m pytest tests/test_v1_release_media_store.py -q`
Expected: all tests pass.

### Task 2: Build Manifest Index and Dry-Run Planning

**Files:**
- Modify: `tests/test_v1_release_media_store.py`
- Modify: `scripts/materialize_v1_release_media.py`

- [ ] **Step 1: Write failing tests**

Test that direct URLs are indexed from `data/*media_manifest*.csv` and `data/*download_status*.csv`, and that dry-run rows include `media_asset_id`, `release_media`, `source_url`, `direct_url`, and `is_derivative`.

- [ ] **Step 2: Run tests to verify failure**

Run: `python3 -m pytest tests/test_v1_release_media_store.py -q`
Expected: failure for missing index/planning functions.

- [ ] **Step 3: Implement index and dry-run planning**

Add `build_direct_url_index`, `load_v1_rows`, and `build_asset_rows`.

- [ ] **Step 4: Run tests to verify pass**

Run: `python3 -m pytest tests/test_v1_release_media_store.py -q`
Expected: all tests pass.

### Task 3: Materialize Files and Write Outputs

**Files:**
- Modify: `tests/test_v1_release_media_store.py`
- Modify: `scripts/materialize_v1_release_media.py`

- [ ] **Step 1: Write failing tests**

Test copy behavior using a temporary source video file and output CSV/JSONL rewriting.

- [ ] **Step 2: Run tests to verify failure**

Run: `python3 -m pytest tests/test_v1_release_media_store.py -q`
Expected: failure for missing materialization/output functions.

- [ ] **Step 3: Implement materialization and CLI**

Add copy/download/ffmpeg clip behavior, `--dry-run`, `--limit`, `--allow-download`, `--source-media-root`, and output path arguments.

- [ ] **Step 4: Run tests to verify pass**

Run: `python3 -m pytest tests/test_v1_release_media_store.py -q`
Expected: all tests pass.

### Task 4: Validate on V1 Metadata

**Files:**
- Modify: `release/v1/README.md`

- [ ] **Step 1: Run dry-run over all V1 rows**

Run: `python3 scripts/materialize_v1_release_media.py --dry-run`
Expected: 114 planned rows and no crash.

- [ ] **Step 2: Run full tests**

Run: `python3 -m pytest -q`
Expected: all existing and new tests pass.

- [ ] **Step 3: Document usage**

Add the V1 media materialization command to `release/v1/README.md`.
