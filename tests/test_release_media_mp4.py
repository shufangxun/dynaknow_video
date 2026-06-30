import csv
from pathlib import Path

from scripts.convert_release_media_to_mp4 import (
    build_mp4_rows,
    ffmpeg_mp4_command,
    load_segment_index,
    mp4_path_for_asset,
)


def test_mp4_path_for_asset_uses_media_asset_id():
    row = {
        "media_asset_id": "vdcr_v1_000036",
        "file_path": "release/media/videos/vdcr_v1_000036.webm",
    }

    assert mp4_path_for_asset(row) == "release/media/videos_mp4/vdcr_v1_000036.mp4"


def test_build_mp4_rows_preserves_source_metadata_and_updates_paths(tmp_path):
    source = tmp_path / "release/media/videos/vdcr_v1_000036.webm"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"source")
    row = {
        "media_asset_id": "vdcr_v1_000036",
        "video_id": "vdcr_000036",
        "source_id": "vdcr_commons_mr5_000001",
        "file_path": "release/media/videos/vdcr_v1_000036.webm",
        "original_local_media": "media/original.webm",
        "source_url": "https://example.test/page",
        "direct_url": "https://example.test/video.webm",
        "license_or_usage_note": "CC",
        "is_derivative": "false",
        "start_sec": "",
        "end_sec": "",
        "transform_note": "",
        "sha256": "old",
        "bytes": "6",
        "status": "downloaded",
        "error": "",
    }

    rows = build_mp4_rows([row], tmp_path)

    assert rows[0]["file_path"] == "release/media/videos_mp4/vdcr_v1_000036.mp4"
    assert rows[0]["source_file_path"] == "release/media/videos/vdcr_v1_000036.webm"
    assert rows[0]["status"] == "planned"
    assert rows[0]["sha256"] == ""
    assert rows[0]["bytes"] == ""


def test_ffmpeg_mp4_command_pads_odd_dimensions():
    cmd = ffmpeg_mp4_command(Path("source.webm"), Path("target.mp4"), "", "")

    assert "-vf" in cmd
    assert "pad=ceil(iw/2)*2:ceil(ih/2)*2" in cmd
    assert cmd[-1] == "target.mp4"


def test_ffmpeg_mp4_command_trims_when_segment_bounds_are_present():
    cmd = ffmpeg_mp4_command(Path("source.webm"), Path("target.mp4"), "36.000", "45.000")

    assert cmd[:5] == ["ffmpeg", "-y", "-ss", "36.000", "-i"]
    assert "-t" in cmd
    assert cmd[cmd.index("-t") + 1] == "9.000"


def test_load_segment_index_reads_all_segment_manifests(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    write_csv(
        data_dir / "vdcr_segment_manifest_round42_v1.csv",
        ["id", "segment_start_sec", "segment_end_sec", "duration_sec"],
        [
            {
                "id": "vdcr_commons_mr42_000001_worthington_jet_clean",
                "segment_start_sec": "36.000",
                "segment_end_sec": "45.000",
                "duration_sec": "9.000",
            }
        ],
    )

    index = load_segment_index(data_dir)

    assert index["vdcr_commons_mr42_000001_worthington_jet_clean"]["segment_start_sec"] == "36.000"


def test_build_mp4_rows_uses_segment_manifest_for_source_fallback(tmp_path):
    source = tmp_path / "release/media/videos/vdcr_v1_000108.webm"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"source")
    row = {
        "media_asset_id": "vdcr_v1_000108",
        "video_id": "vdcr_000108",
        "source_id": "vdcr_commons_mr42_000001",
        "file_path": "release/media/videos/vdcr_v1_000108.webm",
        "original_local_media": "media/vdcr_segments_pilot_v1/vdcr_commons_mr42_000001_worthington_jet_clean.mp4",
        "source_url": "https://example.test/page",
        "direct_url": "https://example.test/video.webm",
        "license_or_usage_note": "CC",
        "is_derivative": "true",
        "start_sec": "",
        "end_sec": "",
        "transform_note": "worthington_jet_clean",
        "sha256": "old",
        "bytes": "6",
        "status": "downloaded_source_fallback",
        "error": "",
    }
    segment_index = {
        "vdcr_commons_mr42_000001_worthington_jet_clean": {
            "segment_start_sec": "36.000",
            "segment_end_sec": "45.000",
        }
    }

    rows = build_mp4_rows([row], tmp_path, segment_index)

    assert rows[0]["start_sec"] == "36.000"
    assert rows[0]["end_sec"] == "45.000"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
