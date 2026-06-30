#!/usr/bin/env python3
"""Build the V1 final MP4 release metadata and dataset files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FINAL_ASSET_FIELDS = [
    "media_asset_id",
    "video_id",
    "source_id",
    "file_path",
    "source_file_path",
    "original_local_media",
    "source_url",
    "direct_url",
    "license_or_usage_note",
    "is_derivative",
    "start_sec",
    "end_sec",
    "transform_note",
    "source_status",
    "mp4_status",
    "release_processing_status",
    "release_ready",
    "release_processing_note",
    "sha256",
    "bytes",
]

METADATA_AUDIO_ONLY_TRANSFORMS = {"metadata_clean", "noaudio"}
VIDEO_ONLY_CLEAN_TRANSFORMS = {
    "biofilm_expansion_clean",
    "electrodeposition_dendrite_01_clean",
    "droplet_spreading_retraction_clean",
    "flame_blowoff_clean",
}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def classify_release_processing_status(row: dict[str, str]) -> dict[str, str]:
    source_status = row.get("source_status", "")
    transform_note = row.get("transform_note", "")
    is_derivative = row.get("is_derivative", "") == "true"

    if source_status == "downloaded_source_fallback":
        if transform_note in METADATA_AUDIO_ONLY_TRANSFORMS:
            return {
                "release_processing_status": "rebuilt_metadata_noaudio_mp4",
                "release_ready": "true",
                "release_processing_note": "metadata/audio cleanup represented by MP4 normalization with no audio and stripped container metadata",
            }
        if transform_note in VIDEO_ONLY_CLEAN_TRANSFORMS:
            return {
                "release_processing_status": "rebuilt_video_only_clean_mp4",
                "release_ready": "true",
                "release_processing_note": "video-only clean transform represented by MP4 normalization, no audio, stripped metadata, and segment-manifest timing when present",
            }
        return {
            "release_processing_status": "source_fallback_unresolved_transform",
            "release_ready": "false",
            "release_processing_note": "source fallback is normalized to MP4, but the processed V1 source file is required to reproduce crop/custom clean transforms exactly",
        }

    if source_status == "rebuilt_segment":
        return {
            "release_processing_status": "rebuilt_segment_mp4",
            "release_ready": "true",
            "release_processing_note": "time segment rebuilt from source media and normalized to MP4/H.264",
        }

    if source_status == "existing_release" and is_derivative:
        return {
            "release_processing_status": "processed_existing_release_mp4",
            "release_ready": "true",
            "release_processing_note": "normalized to MP4/H.264 from existing processed V1 media",
        }

    if source_status == "existing_release":
        return {
            "release_processing_status": "original_existing_release_mp4",
            "release_ready": "true",
            "release_processing_note": "original V1 media normalized to MP4/H.264",
        }

    if source_status == "downloaded":
        return {
            "release_processing_status": "downloaded_original_mp4",
            "release_ready": "true",
            "release_processing_note": "source media required no V1 derivative transform and was normalized to MP4/H.264",
        }

    return {
        "release_processing_status": "unknown",
        "release_ready": "false",
        "release_processing_note": f"unrecognized source_status: {source_status}",
    }


def build_final_asset_rows(asset_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    final_rows: list[dict[str, str]] = []
    for row in asset_rows:
        classified = classify_release_processing_status(row)
        final_rows.append(
            {
                "media_asset_id": row.get("media_asset_id", ""),
                "video_id": row.get("video_id", ""),
                "source_id": row.get("source_id", ""),
                "file_path": row.get("file_path", ""),
                "source_file_path": row.get("source_file_path", ""),
                "original_local_media": row.get("original_local_media", ""),
                "source_url": row.get("source_url", ""),
                "direct_url": row.get("direct_url", ""),
                "license_or_usage_note": row.get("license_or_usage_note", ""),
                "is_derivative": row.get("is_derivative", ""),
                "start_sec": row.get("start_sec", ""),
                "end_sec": row.get("end_sec", ""),
                "transform_note": row.get("transform_note", ""),
                "source_status": row.get("source_status", ""),
                "mp4_status": row.get("status", ""),
                "release_processing_status": classified["release_processing_status"],
                "release_ready": classified["release_ready"],
                "release_processing_note": classified["release_processing_note"],
                "sha256": row.get("sha256", ""),
                "bytes": row.get("bytes", ""),
            }
        )
    return final_rows


def insert_after(fieldnames: list[str], anchor: str, new_fields: list[str]) -> list[str]:
    output = [field for field in fieldnames if field not in new_fields]
    insert_at = output.index(anchor) + 1 if anchor in output else len(output)
    return output[:insert_at] + new_fields + output[insert_at:]


def write_final_release_outputs(
    samples: list[dict],
    manifest_rows: list[dict[str, str]],
    asset_rows: list[dict[str, str]],
    dataset_output: Path,
    manifest_output: Path,
    assets_output: Path,
) -> list[dict[str, str]]:
    final_assets = build_final_asset_rows(asset_rows)
    assets_by_video_id = {row["video_id"]: row for row in final_assets}

    dataset_output.parent.mkdir(parents=True, exist_ok=True)
    with dataset_output.open("w", encoding="utf-8") as handle:
        for sample in samples:
            asset = assets_by_video_id[sample["video_id"]]
            updated = dict(sample)
            updated["media_asset_id"] = asset["media_asset_id"]
            updated["local_media"] = asset["file_path"]
            updated["media_processing_status"] = asset["release_processing_status"]
            updated["media_release_ready"] = asset["release_ready"] == "true"
            handle.write(json.dumps(updated, ensure_ascii=False, sort_keys=True) + "\n")

    manifest_fieldnames = insert_after(
        list(manifest_rows[0].keys()),
        "local_media",
        ["media_asset_id", "media_processing_status", "media_release_ready"],
    )
    out_manifest: list[dict[str, str]] = []
    for row in manifest_rows:
        asset = assets_by_video_id[row["video_id"]]
        updated = dict(row)
        updated["media_asset_id"] = asset["media_asset_id"]
        updated["local_media"] = asset["file_path"]
        updated["media_processing_status"] = asset["release_processing_status"]
        updated["media_release_ready"] = asset["release_ready"]
        out_manifest.append(updated)

    write_csv(manifest_output, manifest_fieldnames, out_manifest)
    write_csv(assets_output, FINAL_ASSET_FIELDS, final_assets)
    return final_assets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-input", type=Path, default=Path("release/v1/dataset_v1.jsonl"))
    parser.add_argument("--manifest-input", type=Path, default=Path("release/v1/manifest_v1.csv"))
    parser.add_argument("--assets-input", type=Path, default=Path("release/media/media_assets_v1_mp4.csv"))
    parser.add_argument("--dataset-output", type=Path, default=Path("release/v1/dataset_v1_final_mp4.jsonl"))
    parser.add_argument("--manifest-output", type=Path, default=Path("release/v1/manifest_v1_final_mp4.csv"))
    parser.add_argument("--assets-output", type=Path, default=Path("release/media/media_assets_v1_final_mp4.csv"))
    parser.add_argument("--strict", action="store_true", help="Return non-zero if any row is not fully release-ready.")
    args = parser.parse_args()

    final_assets = write_final_release_outputs(
        read_jsonl(args.dataset_input),
        read_csv(args.manifest_input),
        read_csv(args.assets_input),
        args.dataset_output,
        args.manifest_output,
        args.assets_output,
    )
    counts: dict[str, int] = {}
    ready_count = 0
    for row in final_assets:
        counts[row["release_processing_status"]] = counts.get(row["release_processing_status"], 0) + 1
        if row["release_ready"] == "true":
            ready_count += 1
    unresolved = len(final_assets) - ready_count
    print(
        f"rows={len(final_assets)} release_ready={ready_count} unresolved={unresolved} "
        f"statuses={counts} dataset={args.dataset_output} assets={args.assets_output}"
    )
    return 1 if args.strict and unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
