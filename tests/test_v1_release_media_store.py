import csv
import json
from pathlib import Path

from scripts.materialize_v1_release_media import (
    build_asset_rows,
    build_direct_url_index,
    materialize_existing_file,
    plan_media_asset,
    write_release_outputs,
)


def test_plan_media_asset_parses_archive_segment():
    plan = plan_media_asset(
        "vdcr_000003",
        "media/vdcr_segments_pilot_v1/vdcr_archive_only_000025_seg_005000_034000.mp4",
    )

    assert plan.media_asset_id == "vdcr_v1_000003"
    assert plan.source_id == "vdcr_archive_only_000025"
    assert plan.release_media == "release/media/videos/vdcr_v1_000003.mp4"
    assert plan.start_sec == 5.0
    assert plan.end_sec == 34.0
    assert plan.is_derivative is True


def test_plan_media_asset_parses_long_millisecond_segment_tokens():
    plan = plan_media_asset(
        "vdcr_000010",
        "media/vdcr_segments_pilot_v1/vdcr_archive_earth_000008_seg_1825000_1860000.mp4",
    )

    assert plan.source_id == "vdcr_archive_earth_000008"
    assert plan.start_sec == 1825.0
    assert plan.end_sec == 1860.0


def test_plan_media_asset_parses_direct_commons_reference():
    plan = plan_media_asset(
        "vdcr_000036",
        "media/vdcr_commons_manual_round5_v1/vdcr_commons_mr5_000001.webm",
    )

    assert plan.media_asset_id == "vdcr_v1_000036"
    assert plan.source_id == "vdcr_commons_mr5_000001"
    assert plan.release_media == "release/media/videos/vdcr_v1_000036.webm"
    assert plan.start_sec == ""
    assert plan.end_sec == ""
    assert plan.is_derivative is False


def test_plan_media_asset_marks_clean_derivative_without_segment():
    plan = plan_media_asset(
        "vdcr_000101",
        "media/vdcr_segments_pilot_v1/vdcr_commons_mr36_000001_crop_metadata_clean.mp4",
    )

    assert plan.source_id == "vdcr_commons_mr36_000001"
    assert plan.is_derivative is True
    assert plan.transform_note == "crop_metadata_clean"


def test_build_direct_url_index_reads_media_manifest_and_status(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    write_csv(
        data_dir / "example_media_manifest.csv",
        ["id", "page_url", "title", "direct_url", "mime", "duration_sec", "license_short_name", "usage_terms"],
        [
            {
                "id": "vdcr_commons_mr5_000001",
                "page_url": "https://commons.wikimedia.org/wiki/File:Example.webm",
                "title": "Example",
                "direct_url": "https://upload.wikimedia.org/example.webm",
                "mime": "video/webm",
                "duration_sec": "18",
                "license_short_name": "CC-BY-SA-4.0",
                "usage_terms": "",
            }
        ],
    )
    write_csv(
        data_dir / "example_download_status.csv",
        ["id", "ok", "status", "error", "direct_url", "local_media"],
        [
            {
                "id": "vdcr_archive_b02_000010",
                "ok": "true",
                "status": "download_ok",
                "error": "",
                "direct_url": "https://archive.org/download/example/example.mp4",
                "local_media": "media/example.mp4",
            }
        ],
    )

    index = build_direct_url_index(data_dir)

    assert index["vdcr_commons_mr5_000001"] == "https://upload.wikimedia.org/example.webm"
    assert index["vdcr_archive_b02_000010"] == "https://archive.org/download/example/example.mp4"


def test_build_asset_rows_combines_release_manifest_and_direct_url_index():
    samples = [
        {
            "video_id": "vdcr_000036",
            "local_media": "media/vdcr_commons_manual_round5_v1/vdcr_commons_mr5_000001.webm",
            "answer": "Brazil Nut Effect",
        }
    ]
    manifest = {
        "vdcr_000036": {
            "video_id": "vdcr_000036",
            "source_url": "https://commons.wikimedia.org/wiki/File:Example.webm",
            "license_or_usage_note": "CC-BY-SA-4.0",
            "domain": "physics_physical_systems",
            "answer": "Brazil Nut Effect",
        }
    }

    rows = build_asset_rows(samples, manifest, {"vdcr_commons_mr5_000001": "https://upload.wikimedia.org/example.webm"})

    assert rows == [
        {
            "media_asset_id": "vdcr_v1_000036",
            "video_id": "vdcr_000036",
            "source_id": "vdcr_commons_mr5_000001",
            "file_path": "release/media/videos/vdcr_v1_000036.webm",
            "original_local_media": "media/vdcr_commons_manual_round5_v1/vdcr_commons_mr5_000001.webm",
            "source_url": "https://commons.wikimedia.org/wiki/File:Example.webm",
            "direct_url": "https://upload.wikimedia.org/example.webm",
            "license_or_usage_note": "CC-BY-SA-4.0",
            "is_derivative": "false",
            "start_sec": "",
            "end_sec": "",
            "transform_note": "",
            "sha256": "",
            "bytes": "",
            "status": "planned",
            "error": "",
        }
    ]


def test_materialize_existing_file_copies_and_hashes(tmp_path):
    source_root = tmp_path / "repo"
    original = source_root / "media/source/example.webm"
    original.parent.mkdir(parents=True)
    original.write_bytes(b"video-bytes")
    row = {
        "file_path": "release/media/videos/vdcr_v1_000001.webm",
        "original_local_media": "media/source/example.webm",
        "is_derivative": "false",
    }

    result = materialize_existing_file(row, source_root, tmp_path / "out")

    copied = tmp_path / "out/release/media/videos/vdcr_v1_000001.webm"
    assert copied.read_bytes() == b"video-bytes"
    assert result["status"] == "copied"
    assert result["bytes"] == "11"
    assert result["sha256"] == "79fd615a866fe7f9eb4da8d9c41ab57e3bd48056df42fd2c13e4d461a87afbe3"


def test_write_release_outputs_rewrites_dataset_and_manifest_paths(tmp_path):
    sample = {
        "video_id": "vdcr_000036",
        "local_media": "media/old.webm",
        "answer": "Brazil Nut Effect",
    }
    manifest_row = {
        "video_id": "vdcr_000036",
        "local_media": "media/old.webm",
        "source_url": "https://example.test/page",
    }
    asset_row = {
        "video_id": "vdcr_000036",
        "media_asset_id": "vdcr_v1_000036",
        "file_path": "release/media/videos/vdcr_v1_000036.webm",
    }

    write_release_outputs(
        [sample],
        {"vdcr_000036": manifest_row},
        [asset_row],
        tmp_path / "dataset.jsonl",
        tmp_path / "manifest.csv",
    )

    written_sample = json.loads((tmp_path / "dataset.jsonl").read_text(encoding="utf-8"))
    with (tmp_path / "manifest.csv").open(newline="", encoding="utf-8") as handle:
        written_manifest = list(csv.DictReader(handle))

    assert written_sample["local_media"] == "release/media/videos/vdcr_v1_000036.webm"
    assert written_sample["media_asset_id"] == "vdcr_v1_000036"
    assert written_manifest[0]["local_media"] == "release/media/videos/vdcr_v1_000036.webm"
    assert written_manifest[0]["media_asset_id"] == "vdcr_v1_000036"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
