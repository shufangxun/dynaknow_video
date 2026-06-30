#!/usr/bin/env python3
"""Convert release media assets to a uniform MP4 directory."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path


MP4_FIELDS = [
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
    "sha256",
    "bytes",
    "status",
    "error",
]


def mp4_path_for_asset(row: dict[str, str]) -> str:
    return f"release/media/videos_mp4/{row['media_asset_id']}.mp4"


def load_segment_index(data_dir: Path) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for path in sorted(data_dir.glob("vdcr_segment_manifest*_v1.csv")):
        for row in read_csv(path):
            if row.get("id"):
                index[row["id"]] = row
    return index


def apply_segment_manifest(row: dict[str, str], segment_index: dict[str, dict[str, str]]) -> None:
    if row.get("source_status") != "downloaded_source_fallback":
        return
    segment_id = Path(row.get("original_local_media", "")).stem
    segment = segment_index.get(segment_id)
    if not segment:
        return
    row["start_sec"] = segment.get("segment_start_sec", row.get("start_sec", ""))
    row["end_sec"] = segment.get("segment_end_sec", row.get("end_sec", ""))


def build_mp4_rows(source_rows: list[dict[str, str]], repo_root: Path, segment_index: dict[str, dict[str, str]] | None = None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in source_rows:
        source_path = repo_root / row["file_path"]
        out = {field: row.get(field, "") for field in MP4_FIELDS}
        out["file_path"] = mp4_path_for_asset(row)
        out["source_file_path"] = row["file_path"]
        out["source_status"] = row.get("status", "")
        apply_segment_manifest(out, segment_index or {})
        out["sha256"] = ""
        out["bytes"] = ""
        out["status"] = "planned" if source_path.exists() else "missing_source"
        out["error"] = "" if source_path.exists() else f"missing source file: {source_path}"
        rows.append(out)
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


def ffmpeg_mp4_command(source: Path, target: Path, start_sec: str, end_sec: str) -> list[str]:
    cmd = [
        "ffmpeg",
        "-y",
    ]
    if start_sec:
        cmd.extend(["-ss", start_sec])
    cmd.extend(
        [
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
        str(target),
        ]
    )
    if end_sec:
        duration = max(0.001, float(end_sec) - float(start_sec or 0.0))
        cmd[cmd.index("-map") : cmd.index("-map")] = ["-t", f"{duration:.3f}"]
    return cmd


def ffmpeg_convert_to_mp4(source: Path, target: Path, start_sec: str = "", end_sec: str = "") -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp.mp4")
    if tmp.exists():
        tmp.unlink()
    cmd = ffmpeg_mp4_command(source, tmp, start_sec, end_sec)
    result = subprocess.run(
        cmd,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
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


def materialize_mp4_rows(rows: list[dict[str, str]], repo_root: Path, force: bool = False) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for row in rows:
        out = dict(row)
        source = repo_root / row["source_file_path"]
        target = repo_root / row["file_path"]
        if not source.exists() or source.stat().st_size <= 0:
            out["status"] = "missing_source"
            out["error"] = f"missing source file: {source}"
            results.append(out)
            continue
        if target.exists() and target.stat().st_size > 0 and not force:
            out["status"] = "existing_mp4"
        else:
            try:
                start_sec = row.get("start_sec", "") if row.get("source_status") == "downloaded_source_fallback" else ""
                end_sec = row.get("end_sec", "") if row.get("source_status") == "downloaded_source_fallback" else ""
                ffmpeg_convert_to_mp4(source, target, start_sec, end_sec)
                out["status"] = "converted"
                out["error"] = ""
            except Exception as exc:
                out["status"] = "failed"
                out["error"] = str(exc)
                results.append(out)
                continue
        out["bytes"] = str(target.stat().st_size)
        out["sha256"] = sha256_file(target)
        results.append(out)
    return results


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_release_outputs(samples: list[dict], manifest_rows: list[dict[str, str]], mp4_rows: list[dict[str, str]], dataset_output: Path, manifest_output: Path) -> None:
    by_video = {row["video_id"]: row for row in mp4_rows}
    dataset_output.parent.mkdir(parents=True, exist_ok=True)
    with dataset_output.open("w", encoding="utf-8") as handle:
        for sample in samples:
            updated = dict(sample)
            asset = by_video[updated["video_id"]]
            updated["media_asset_id"] = asset["media_asset_id"]
            updated["local_media"] = asset["file_path"]
            handle.write(json.dumps(updated, ensure_ascii=False, sort_keys=True) + "\n")

    fieldnames = list(manifest_rows[0].keys())
    if "media_asset_id" not in fieldnames:
        fieldnames.insert(fieldnames.index("local_media"), "media_asset_id")
    out_rows: list[dict[str, str]] = []
    for row in manifest_rows:
        asset = by_video[row["video_id"]]
        updated = dict(row)
        updated["media_asset_id"] = asset["media_asset_id"]
        updated["local_media"] = asset["file_path"]
        out_rows.append(updated)
    write_csv(manifest_output, fieldnames, out_rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets-input", type=Path, default=Path("release/media/media_assets_v1.csv"))
    parser.add_argument("--assets-output", type=Path, default=Path("release/media/media_assets_v1_mp4.csv"))
    parser.add_argument("--dataset-input", type=Path, default=Path("release/v1/dataset_v1.jsonl"))
    parser.add_argument("--manifest-input", type=Path, default=Path("release/v1/manifest_v1.csv"))
    parser.add_argument("--dataset-output", type=Path, default=Path("release/v1/dataset_v1_mp4.jsonl"))
    parser.add_argument("--manifest-output", type=Path, default=Path("release/v1/manifest_v1_mp4.csv"))
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    source_rows = read_csv(args.assets_input)
    rows = build_mp4_rows(source_rows, Path("."), load_segment_index(args.data_dir))
    if not args.dry_run:
        rows = materialize_mp4_rows(rows, Path("."), force=args.force)
        samples = read_jsonl(args.dataset_input)
        manifest_rows = read_csv(args.manifest_input)
        write_release_outputs(samples, manifest_rows, rows, args.dataset_output, args.manifest_output)
    write_csv(args.assets_output, MP4_FIELDS, rows)
    status_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    print(f"rows={len(rows)} statuses={status_counts} output={args.assets_output}")
    return 0 if all(row["status"] not in {"failed", "missing_source"} for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
