"""Unit tests for DashScope free media-bank ingest (no live API)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.social import ingest_dashscope_free_media_bank as ingest  # noqa: E402


def test_ingest_video_writes_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest, "REPO", tmp_path)
    monkeypatch.setattr(ingest, "VIDEO_ROOT", tmp_path / "vbank")
    monkeypatch.setattr(ingest, "VIDEO_MANIFEST", tmp_path / "vbank" / "MANIFEST.tsv")
    monkeypatch.setattr(ingest, "VIDEO_PILOTS", tmp_path / "vbank" / "pilots")
    src = tmp_path / "clip.mp4"
    src.write_bytes(b"v" * 60_000)
    row = ingest.ingest_video(src, topic="anxiety", model="wan2.7-t2v", duration_s=5, k_index=0)
    assert row["family"] == "wan_t2v"
    assert row["content_provenance"] == "INTERIM"
    assert "dashscope_free" in row["source_stock_ref"]
    assert ingest.VIDEO_MANIFEST.exists()
    text = ingest.VIDEO_MANIFEST.read_text(encoding="utf-8")
    assert "wan_t2v__anxiety__beat__k00__VERTICAL_9_16" in text


def test_ingest_video_stub_guard(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest, "REPO", tmp_path)
    monkeypatch.setattr(ingest, "VIDEO_ROOT", tmp_path / "vbank")
    monkeypatch.setattr(ingest, "VIDEO_MANIFEST", tmp_path / "vbank" / "MANIFEST.tsv")
    monkeypatch.setattr(ingest, "VIDEO_PILOTS", tmp_path / "vbank" / "pilots")
    src = tmp_path / "tiny.mp4"
    src.write_bytes(b"tiny")
    with pytest.raises(ValueError, match="stub-guard"):
        ingest.ingest_video(src, topic="anxiety", model="wan2.7-t2v", duration_s=5)


def test_ingest_image_pending_look_gate(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest, "REPO", tmp_path)
    monkeypatch.setattr(ingest, "IMAGE_ROOT", tmp_path / "ibank")
    monkeypatch.setattr(ingest, "IMAGE_MANIFEST", tmp_path / "ibank" / "MANIFEST.tsv")
    monkeypatch.setattr(ingest, "IMAGE_PILOTS", tmp_path / "ibank" / "pilots" / "dashscope_free")
    src = tmp_path / "still.png"
    src.write_bytes(b"i" * 12_000)
    row = ingest.ingest_image(
        src, topic="burnout", design_family="object_metaphor", model="qwen-image-2.0"
    )
    assert row["look_gate"] == "PENDING"
    assert row["provider"] == "dashscope_free"
    assert ingest.IMAGE_MANIFEST.exists()
