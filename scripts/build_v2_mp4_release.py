#!/usr/bin/env python3
"""Build the VDCR V2 MP4 release package from the draft source-hidden JSONL."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ASSET_FIELDS = [
    "media_asset_id",
    "video_id",
    "candidate_id",
    "answer",
    "domain",
    "file_path",
    "source_file_path",
    "original_local_media",
    "source_url",
    "license_or_usage_note",
    "review_status",
    "review_notes",
    "release_processing_status",
    "release_ready",
    "sha256",
    "bytes",
    "status",
    "error",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def v1_mp4_fallback(video_id: str) -> Path | None:
    if not video_id.startswith("vdcr_") or video_id.startswith("vdcr_v2_"):
        return None
    suffix = video_id.removeprefix("vdcr_")
    if not suffix.isdigit():
        return None
    return Path("release/media/videos_mp4") / f"vdcr_v1_{int(suffix):06d}.mp4"


def resolve_source(local_media: str, video_id: str) -> Path | None:
    source = Path(local_media)
    if source.exists():
        return source
    fallback = v1_mp4_fallback(video_id)
    if fallback and fallback.exists():
        return fallback
    return None


def is_v1_seed_video(video_id: str) -> bool:
    return v1_mp4_fallback(video_id) is not None


def has_audio_stream(path: Path) -> bool:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            str(path),
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return bool(result.stdout.strip())


def ffmpeg_normalize_to_mp4(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp.mp4")
    if tmp.exists():
        tmp.unlink()
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-map",
        "0:v:0",
        "-an",
        "-map_metadata",
        "-1",
        "-vf",
        "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(tmp),
    ]
    result = subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        if tmp.exists():
            tmp.unlink()
        raise RuntimeError(result.stderr.strip() or "ffmpeg_failed")
    if not tmp.exists() or tmp.stat().st_size <= 1024:
        if tmp.exists():
            tmp.unlink()
        raise RuntimeError("ffmpeg produced an empty output")
    tmp.replace(target)


def materialize_release_video(source: Path, target: Path, force: bool) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 1024 and not force:
        return "existing_mp4"
    if source.suffix.lower() == ".mp4" and not has_audio_stream(source):
        if source.resolve() != target.resolve():
            target.write_bytes(source.read_bytes())
        return "copied_noaudio_mp4"
    ffmpeg_normalize_to_mp4(source, target)
    return "normalized_noaudio_mp4"


def build_assets(
    samples: list[dict[str, Any]],
    manifest_rows: list[dict[str, str]],
    media_dir: Path,
    force: bool,
) -> list[dict[str, str]]:
    manifest_by_video_id = {row["video_id"]: row for row in manifest_rows}
    assets: list[dict[str, str]] = []
    for index, sample in enumerate(samples, start=1):
        video_id = str(sample["video_id"])
        manifest = manifest_by_video_id.get(video_id, {})
        source = resolve_source(str(sample["local_media"]), video_id)
        fallback = v1_mp4_fallback(video_id)
        reuse_v1 = is_v1_seed_video(video_id) and fallback is not None and fallback.exists()
        media_asset_id = fallback.stem if reuse_v1 else f"vdcr_v2_{index:06d}"
        file_path = fallback if reuse_v1 else media_dir / f"{media_asset_id}.mp4"
        row = {
            "media_asset_id": media_asset_id,
            "video_id": video_id,
            "candidate_id": manifest.get("candidate_id", ""),
            "answer": str(sample.get("answer", "")),
            "domain": str(sample.get("domain", "")),
            "file_path": file_path.as_posix(),
            "source_file_path": source.as_posix() if source else "",
            "original_local_media": str(sample.get("local_media", "")),
            "source_url": manifest.get("source_url", ""),
            "license_or_usage_note": manifest.get("license_or_usage_note", ""),
            "review_status": manifest.get("review_status", ""),
            "review_notes": manifest.get("review_notes", ""),
            "release_processing_status": "reused_v1_final_mp4" if reuse_v1 else "normalized_v2_mp4_noaudio",
            "release_ready": "false",
            "sha256": "",
            "bytes": "",
            "status": "planned",
            "error": "",
        }
        if source is None:
            row["status"] = "missing_source"
            row["error"] = f"missing source file: {sample.get('local_media', '')}"
            assets.append(row)
            continue
        try:
            if reuse_v1:
                row["status"] = "reused_v1_mp4"
            else:
                row["status"] = materialize_release_video(source, file_path, force=force)
            row["release_ready"] = "true"
            row["bytes"] = str(file_path.stat().st_size)
            row["sha256"] = sha256_file(file_path)
        except Exception as exc:
            row["status"] = "failed"
            row["error"] = str(exc)
        assets.append(row)
    return assets


def write_release_dataset(samples: list[dict[str, Any]], assets: list[dict[str, str]], output: Path) -> None:
    assets_by_video_id = {row["video_id"]: row for row in assets}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for sample in samples:
            asset = assets_by_video_id[sample["video_id"]]
            updated = dict(sample)
            updated["media_asset_id"] = asset["media_asset_id"]
            updated["local_media"] = asset["file_path"]
            updated["media_processing_status"] = asset["release_processing_status"]
            updated["media_release_ready"] = asset["release_ready"] == "true"
            handle.write(json.dumps(updated, ensure_ascii=False, sort_keys=True) + "\n")


def write_release_manifest(manifest_rows: list[dict[str, str]], assets: list[dict[str, str]], output: Path) -> None:
    assets_by_video_id = {row["video_id"]: row for row in assets}
    fieldnames = list(manifest_rows[0].keys())
    for field in ["media_asset_id", "media_processing_status", "media_release_ready"]:
        if field not in fieldnames:
            fieldnames.append(field)
    output_rows: list[dict[str, str]] = []
    for row in manifest_rows:
        asset = assets_by_video_id[row["video_id"]]
        updated = dict(row)
        updated["local_media"] = asset["file_path"]
        updated["media_asset_id"] = asset["media_asset_id"]
        updated["media_processing_status"] = asset["release_processing_status"]
        updated["media_release_ready"] = asset["release_ready"]
        output_rows.append(updated)
    write_csv(output, fieldnames, output_rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-input", type=Path, default=Path("data/vdcr_v2_draft_samples.jsonl"))
    parser.add_argument("--manifest-input", type=Path, default=Path("data/vdcr_v2_draft_manifest.csv"))
    parser.add_argument("--dataset-output", type=Path, default=Path("release/v2/dataset_v2_mp4.jsonl"))
    parser.add_argument("--manifest-output", type=Path, default=Path("release/v2/manifest_v2_mp4.csv"))
    parser.add_argument("--assets-output", type=Path, default=Path("release/media/media_assets_v2_mp4.csv"))
    parser.add_argument("--media-dir", type=Path, default=Path("release/media/videos_v2_mp4"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    samples = read_jsonl(args.dataset_input)
    manifest_rows = read_csv(args.manifest_input)
    assets = build_assets(samples, manifest_rows, args.media_dir, force=args.force)
    write_csv(args.assets_output, ASSET_FIELDS, assets)
    write_release_dataset(samples, assets, args.dataset_output)
    write_release_manifest(manifest_rows, assets, args.manifest_output)

    counts: dict[str, int] = {}
    ready = 0
    for row in assets:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
        if row["release_ready"] == "true":
            ready += 1
    failed = len(assets) - ready
    print(
        f"rows={len(assets)} release_ready={ready} failed={failed} "
        f"statuses={counts} dataset={args.dataset_output} assets={args.assets_output}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
