import csv
import json
from pathlib import Path

from scripts.build_v1_final_mp4_release import (
    FINAL_ASSET_FIELDS,
    classify_release_processing_status,
    write_final_release_outputs,
)


def test_classify_release_processing_status_marks_exact_processed_media_ready():
    row = {
        "source_status": "existing_release",
        "is_derivative": "true",
        "transform_note": "crop_clean",
    }

    classified = classify_release_processing_status(row)

    assert classified["release_processing_status"] == "processed_existing_release_mp4"
    assert classified["release_ready"] == "true"
    assert classified["release_processing_note"] == "normalized to MP4/H.264 from existing processed V1 media"


def test_classify_release_processing_status_accepts_metadata_clean_fallback_after_mp4_normalization():
    row = {
        "source_status": "downloaded_source_fallback",
        "is_derivative": "true",
        "transform_note": "metadata_clean",
    }

    classified = classify_release_processing_status(row)

    assert classified["release_processing_status"] == "rebuilt_metadata_noaudio_mp4"
    assert classified["release_ready"] == "true"
    assert "metadata/audio cleanup represented" in classified["release_processing_note"]


def test_classify_release_processing_status_flags_unresolved_crop_fallback():
    row = {
        "source_status": "downloaded_source_fallback",
        "is_derivative": "true",
        "transform_note": "crop_metadata_clean",
    }

    classified = classify_release_processing_status(row)

    assert classified["release_processing_status"] == "source_fallback_unresolved_transform"
    assert classified["release_ready"] == "false"
    assert "processed V1 source file is required" in classified["release_processing_note"]


def test_classify_release_processing_status_accepts_video_only_custom_clean_fallback():
    row = {
        "source_status": "downloaded_source_fallback",
        "is_derivative": "true",
        "transform_note": "biofilm_expansion_clean",
    }

    classified = classify_release_processing_status(row)

    assert classified["release_processing_status"] == "rebuilt_video_only_clean_mp4"
    assert classified["release_ready"] == "true"
    assert "video-only clean transform represented" in classified["release_processing_note"]


def test_write_final_release_outputs_adds_mp4_paths_and_processing_fields(tmp_path):
    samples = [
        {"video_id": "vdcr_000001", "local_media": "media/old.mp4", "answer": "A"},
        {"video_id": "vdcr_000002", "local_media": "media/old.webm", "answer": "B"},
    ]
    manifest_rows = [
        {"video_id": "vdcr_000001", "local_media": "media/old.mp4", "source_url": "https://example.test/a"},
        {"video_id": "vdcr_000002", "local_media": "media/old.webm", "source_url": "https://example.test/b"},
    ]
    asset_rows = [
        {
            "media_asset_id": "vdcr_v1_000001",
            "video_id": "vdcr_000001",
            "file_path": "release/media/videos_mp4/vdcr_v1_000001.mp4",
            "source_status": "downloaded",
            "is_derivative": "false",
            "transform_note": "",
            "sha256": "abc",
            "bytes": "100",
            "status": "existing_mp4",
            "source_file_path": "release/media/videos/vdcr_v1_000001.mp4",
        },
        {
            "media_asset_id": "vdcr_v1_000002",
            "video_id": "vdcr_000002",
            "file_path": "release/media/videos_mp4/vdcr_v1_000002.mp4",
            "source_status": "downloaded_source_fallback",
            "is_derivative": "true",
            "transform_note": "crop_clean",
            "sha256": "def",
            "bytes": "200",
            "status": "existing_mp4",
            "source_file_path": "release/media/videos/vdcr_v1_000002.webm",
        },
    ]

    write_final_release_outputs(
        samples,
        manifest_rows,
        asset_rows,
        tmp_path / "dataset.jsonl",
        tmp_path / "manifest.csv",
        tmp_path / "assets.csv",
    )

    written_samples = [json.loads(line) for line in (tmp_path / "dataset.jsonl").read_text(encoding="utf-8").splitlines()]
    with (tmp_path / "manifest.csv").open(newline="", encoding="utf-8") as handle:
        written_manifest = list(csv.DictReader(handle))
    with (tmp_path / "assets.csv").open(newline="", encoding="utf-8") as handle:
        written_assets = list(csv.DictReader(handle))

    assert written_samples[0]["local_media"] == "release/media/videos_mp4/vdcr_v1_000001.mp4"
    assert written_samples[0]["media_release_ready"] is True
    assert written_samples[1]["media_release_ready"] is False
    assert written_samples[1]["media_processing_status"] == "source_fallback_unresolved_transform"
    assert written_manifest[1]["media_release_ready"] == "false"
    assert written_assets[1]["release_ready"] == "false"
    assert written_assets[1]["release_processing_status"] == "source_fallback_unresolved_transform"
    assert list(written_assets[0].keys()) == FINAL_ASSET_FIELDS


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
