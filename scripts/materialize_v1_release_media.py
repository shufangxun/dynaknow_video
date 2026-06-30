#!/usr/bin/env python3
"""Materialize VDCR v1 videos into the shared release media store."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ASSET_FIELDS = [
    "media_asset_id",
    "video_id",
    "source_id",
    "file_path",
    "original_local_media",
    "source_url",
    "direct_url",
    "license_or_usage_note",
    "is_derivative",
    "start_sec",
    "end_sec",
    "transform_note",
    "sha256",
    "bytes",
    "status",
    "error",
]

SOURCE_ID_RE = re.compile(
    r"(vdcr_(?:archive_only_\d{6}|archive_b\d{2}_\d{6}|archive_earth_\d{6}|commons_mr\d+_\d{6}|public_mr\d+_\d{6}))"
)
SEGMENT_RE = re.compile(r"_seg_(\d{5,7})_(\d{5,7})")
DERIVATIVE_MARKERS = ("seg", "clean", "crop", "noaudio", "metadata", "mask", "lowerfoam", "trim")
USER_AGENT = "DynaKnowVideoRelease/0.1"


@dataclass(frozen=True)
class MediaPlan:
    media_asset_id: str
    source_id: str
    release_media: str
    original_local_media: str
    is_derivative: bool
    start_sec: float | str
    end_sec: float | str
    transform_note: str


def parse_millis_token(value: str) -> float:
    return int(value) / 1000.0


def source_id_from_local_media(local_media: str) -> str:
    name = Path(local_media).stem
    match = SOURCE_ID_RE.search(name)
    if not match:
        raise ValueError(f"cannot parse source id from local_media: {local_media}")
    return match.group(1)


def transform_note_from_name(local_media: str, source_id: str) -> str:
    stem = Path(local_media).stem
    suffix = stem.removeprefix(source_id).strip("_")
    suffix = SEGMENT_RE.sub("", suffix).strip("_")
    return suffix


def plan_media_asset(video_id: str, local_media: str) -> MediaPlan:
    source_id = source_id_from_local_media(local_media)
    media_asset_id = video_id.replace("vdcr_", "vdcr_v1_")
    ext = Path(local_media).suffix
    release_media = f"release/media/videos/{media_asset_id}{ext}"
    name_parts = set(Path(local_media).stem.split("_"))
    segment_match = SEGMENT_RE.search(Path(local_media).stem)
    is_derivative = bool(segment_match) or any(marker in name_parts for marker in DERIVATIVE_MARKERS)
    start_sec: float | str = ""
    end_sec: float | str = ""
    if segment_match:
        start_sec = parse_millis_token(segment_match.group(1))
        end_sec = parse_millis_token(segment_match.group(2))
    return MediaPlan(
        media_asset_id=media_asset_id,
        source_id=source_id,
        release_media=release_media,
        original_local_media=local_media,
        is_derivative=is_derivative,
        start_sec=start_sec,
        end_sec=end_sec,
        transform_note=transform_note_from_name(local_media, source_id),
    )


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def read_manifest(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["video_id"]: row for row in csv.DictReader(handle)}


def build_direct_url_index(data_dir: Path) -> dict[str, str]:
    index: dict[str, str] = {}
    for path in sorted(data_dir.glob("*.csv")):
        if "media_manifest" not in path.name and "download_status" not in path.name:
            continue
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or "id" not in reader.fieldnames or "direct_url" not in reader.fieldnames:
                continue
            for row in reader:
                item_id = row.get("id", "")
                direct_url = row.get("direct_url", "")
                if item_id and direct_url and item_id not in index:
                    index[item_id] = direct_url
    return index


def build_asset_rows(
    samples: list[dict],
    manifest_by_video_id: dict[str, dict[str, str]],
    direct_url_index: dict[str, str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for sample in samples:
        video_id = sample["video_id"]
        plan = plan_media_asset(video_id, sample["local_media"])
        manifest = manifest_by_video_id.get(video_id, {})
        rows.append(
            {
                "media_asset_id": plan.media_asset_id,
                "video_id": video_id,
                "source_id": plan.source_id,
                "file_path": plan.release_media,
                "original_local_media": plan.original_local_media,
                "source_url": manifest.get("source_url", ""),
                "direct_url": direct_url_index.get(plan.source_id, ""),
                "license_or_usage_note": manifest.get("license_or_usage_note", ""),
                "is_derivative": str(plan.is_derivative).lower(),
                "start_sec": str(plan.start_sec),
                "end_sec": str(plan.end_sec),
                "transform_note": plan.transform_note,
                "sha256": "",
                "bytes": "",
                "status": "planned",
                "error": "",
            }
        )
    return rows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def commons_transcode_url(page_url: str, suffix: str = "360p.webm") -> str:
    if "/wiki/File:" not in page_url:
        return ""
    filename = urllib.parse.unquote(page_url.split("/wiki/File:", 1)[1].split("#", 1)[0])
    digest = hashlib.md5(filename.encode("utf-8")).hexdigest()
    quoted = urllib.parse.quote(filename, safe="()-.!~*'")
    return (
        "https://upload.wikimedia.org/wikipedia/commons/transcoded/"
        f"{digest[0]}/{digest[:2]}/{quoted}/{quoted}.{suffix}"
    )


def materialize_existing_file(row: dict[str, str], source_root: Path, output_root: Path) -> dict[str, str]:
    result = dict(row)
    source = source_root / row["original_local_media"]
    target = output_root / row["file_path"]
    if not source.exists():
        result["status"] = "missing_existing"
        result["error"] = f"missing source file: {source}"
        return result
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    result["status"] = "copied"
    result["error"] = ""
    result["bytes"] = str(target.stat().st_size)
    result["sha256"] = sha256_file(target)
    return result


def download_file(url: str, output: Path, sleep_sec: float = 0.0) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    output.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            if sleep_sec > 0:
                time.sleep(sleep_sec)
            with urllib.request.urlopen(request, timeout=120) as response, output.open("wb") as handle:
                shutil.copyfileobj(response, handle)
            if output.exists() and output.stat().st_size > 0:
                return
        except urllib.error.HTTPError as exc:
            last_error = exc
            if output.exists():
                output.unlink()
            if exc.code not in {429, 500, 502, 503, 504}:
                raise
            retry_after = exc.headers.get("Retry-After")
            wait_s = float(retry_after) if retry_after and retry_after.isdigit() else min(120.0, 10.0 * (attempt + 1))
            time.sleep(wait_s)
        except Exception as exc:
            last_error = exc
            if output.exists():
                output.unlink()
            time.sleep(min(60.0, 5.0 * (attempt + 1)))
    if last_error:
        raise last_error
    raise RuntimeError("download_failed")


def download_first_available(urls: list[str], output: Path, sleep_sec: float = 0.0) -> str:
    last_error: Exception | None = None
    for url in [url for url in urls if url]:
        try:
            download_file(url, output, sleep_sec=sleep_sec)
            return url
        except Exception as exc:
            last_error = exc
            if output.exists():
                output.unlink()
    if last_error:
        raise last_error
    raise RuntimeError("no_download_url")


def run_ffmpeg_clip(input_path: Path, output_path: Path, start_sec: str, end_sec: str, strip_audio: bool) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y"]
    if start_sec:
        cmd.extend(["-ss", start_sec])
    cmd.extend(["-i", str(input_path)])
    if end_sec:
        duration = max(0.0, float(end_sec) - float(start_sec or 0.0))
        cmd.extend(["-t", f"{duration:.3f}"])
    cmd.extend(["-map_metadata", "-1", "-an"])
    ext = output_path.suffix.lower()
    if ext == ".webm":
        cmd.extend(["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "32"])
    elif ext in {".ogv", ".ogg"}:
        cmd.extend(["-c:v", "libtheora", "-q:v", "7"])
    else:
        cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p"])
    cmd.append(str(output_path))
    completed = subprocess.run(cmd, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        if output_path.exists():
            output_path.unlink()
        raise RuntimeError(completed.stderr.strip() or "ffmpeg_failed")


def materialize_download_or_rebuild(row: dict[str, str], output_root: Path, cache_dir: Path, sleep_sec: float = 0.0) -> dict[str, str]:
    result = dict(row)
    target = output_root / row["file_path"]
    if target.exists() and target.stat().st_size > 1024:
        result["status"] = "existing_release"
        result["bytes"] = str(target.stat().st_size)
        result["sha256"] = sha256_file(target)
        result["error"] = ""
        return result
    if target.exists():
        target.unlink()
    direct_url = row.get("direct_url", "")
    if not direct_url:
        result["status"] = "missing_direct_url"
        result["error"] = "no direct_url found for source_id"
        return result

    try:
        transcode_url = commons_transcode_url(row.get("source_url", ""))
        download_urls = [transcode_url, direct_url] if transcode_url else [direct_url]
        if row["is_derivative"] == "false":
            if transcode_url and target.suffix.lower() != ".webm":
                result["file_path"] = str(Path(row["file_path"]).with_suffix(".webm"))
                target = output_root / result["file_path"]
            used_url = download_first_available(download_urls, target, sleep_sec=sleep_sec)
            result["direct_url"] = used_url
            result["status"] = "downloaded"
        elif row.get("start_sec") and row.get("end_sec"):
            preferred_url = transcode_url or direct_url
            raw_path = cache_dir / f"{row['source_id']}{Path(preferred_url.split('?', 1)[0]).suffix or '.video'}"
            if not raw_path.exists() or raw_path.stat().st_size == 0:
                used_url = download_first_available(download_urls, raw_path, sleep_sec=sleep_sec)
                result["direct_url"] = used_url
            strip_audio = "noaudio" in row.get("transform_note", "") or "clean" in row.get("transform_note", "")
            run_ffmpeg_clip(raw_path, target, row["start_sec"], row["end_sec"], strip_audio)
            result["status"] = "rebuilt_segment"
        else:
            result["status"] = "missing_existing_derivative"
            result["error"] = "derivative has no segment times; original processed file is required"
            return result
    except Exception as exc:
        if target.exists() and target.stat().st_size <= 1024:
            target.unlink()
        result["status"] = "failed"
        result["error"] = str(exc)
        return result

    result["bytes"] = str(target.stat().st_size)
    result["sha256"] = sha256_file(target)
    result["error"] = ""
    return result


def write_asset_rows(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ASSET_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_release_outputs(
    samples: list[dict],
    manifest_by_video_id: dict[str, dict[str, str]],
    asset_rows: list[dict[str, str]],
    dataset_output: Path,
    manifest_output: Path,
) -> None:
    assets_by_video_id = {row["video_id"]: row for row in asset_rows}
    dataset_output.parent.mkdir(parents=True, exist_ok=True)
    with dataset_output.open("w", encoding="utf-8") as handle:
        for sample in samples:
            updated = dict(sample)
            asset = assets_by_video_id[updated["video_id"]]
            updated["media_asset_id"] = asset["media_asset_id"]
            updated["local_media"] = asset["file_path"]
            handle.write(json.dumps(updated, ensure_ascii=False, sort_keys=True) + "\n")

    manifest_rows: list[dict[str, str]] = []
    for video_id, row in manifest_by_video_id.items():
        if video_id not in assets_by_video_id:
            continue
        updated = dict(row)
        asset = assets_by_video_id[video_id]
        updated["media_asset_id"] = asset["media_asset_id"]
        updated["local_media"] = asset["file_path"]
        manifest_rows.append(updated)

    fieldnames = list(next(iter(manifest_by_video_id.values())).keys())
    if "media_asset_id" not in fieldnames:
        insert_at = fieldnames.index("local_media") if "local_media" in fieldnames else len(fieldnames)
        fieldnames.insert(insert_at, "media_asset_id")
    manifest_output.parent.mkdir(parents=True, exist_ok=True)
    with manifest_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest_rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("release/v1/dataset_v1.jsonl"))
    parser.add_argument("--manifest", type=Path, default=Path("release/v1/manifest_v1.csv"))
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--source-media-root", type=Path, default=Path("."))
    parser.add_argument("--output-root", type=Path, default=Path("."))
    parser.add_argument("--assets-output", type=Path, default=Path("release/media/media_assets_v1.csv"))
    parser.add_argument("--dataset-output", type=Path, default=Path("release/v1/dataset_v1_with_media.jsonl"))
    parser.add_argument("--manifest-output", type=Path, default=Path("release/v1/manifest_v1_with_media.csv"))
    parser.add_argument("--cache-dir", type=Path, default=Path("release/media/source_cache_v1"))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-download", action="store_true")
    parser.add_argument("--sleep-sec", type=float, default=3.0)
    args = parser.parse_args()

    samples = read_jsonl(args.dataset)
    if args.limit:
        samples = samples[: args.limit]
    manifest = read_manifest(args.manifest)
    rows = build_asset_rows(samples, manifest, build_direct_url_index(args.data_dir))

    if not args.dry_run:
        materialized: list[dict[str, str]] = []
        for row in rows:
            existing = materialize_existing_file(row, args.source_media_root, args.output_root)
            if existing["status"] == "copied" or not args.allow_download:
                materialized.append(existing)
            else:
                materialized.append(materialize_download_or_rebuild(row, args.output_root, args.output_root / args.cache_dir, args.sleep_sec))
        rows = materialized
        write_release_outputs(samples, manifest, rows, args.dataset_output, args.manifest_output)

    write_asset_rows(rows, args.output_root / args.assets_output)
    status_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    print(f"planned={len(rows)} statuses={status_counts} assets={args.output_root / args.assets_output}")
    return 0 if all(row["status"] not in {"failed"} for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
