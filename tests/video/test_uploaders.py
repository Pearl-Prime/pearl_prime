"""Tests for Stage 18 — Upload/Publish uploaders and orchestrator."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video.uploaders.base import BaseUploader, UploadResult
from scripts.video.uploaders.youtube import YouTubeUploader
from scripts.video.uploaders.tiktok import TikTokUploader
from scripts.video.uploaders.instagram import InstagramReelsUploader
from scripts.video.uploaders.bilibili import BilibiliUploader
from scripts.video.uploaders.douyin import DouyinUploader
from scripts.video.uploaders import UPLOADERS


# ── UploadResult tests ──────────────────────────────────────────────────────

class TestUploadResult:
    def test_to_dict_omits_none(self):
        r = UploadResult(
            platform="youtube", channel_id="ch_001", brand_id="stillness_press",
            video_id="vid-001", success=True, platform_video_id="abc123",
        )
        d = r.to_dict()
        assert d["platform"] == "youtube"
        assert d["success"] is True
        assert d["platform_video_id"] == "abc123"
        assert "error" not in d
        assert "retry_after_s" not in d

    def test_to_dict_includes_error(self):
        r = UploadResult(
            platform="tiktok", channel_id="ch_002", brand_id="cognitive_clarity",
            video_id="vid-002", success=False, error="rate_limited",
        )
        d = r.to_dict()
        assert d["success"] is False
        assert d["error"] == "rate_limited"


# ── UPLOADERS registry ──────────────────────────────────────────────────────

class TestUploadersRegistry:
    def test_all_platforms_have_uploaders(self):
        expected = {"youtube", "youtube_shorts", "tiktok", "instagram_reels", "bilibili", "douyin"}
        assert set(UPLOADERS.keys()) == expected

    def test_youtube_shorts_uses_youtube_uploader(self):
        assert UPLOADERS["youtube_shorts"] is YouTubeUploader


# ── Base uploader tests ─────────────────────────────────────────────────────

class TestBaseUploader:
    def test_dry_run_returns_success(self, tmp_path):
        """Dry-run mode should return success without making API calls."""
        config = {"rate_limits": {"max_uploads_per_day": 10}}
        uploader = YouTubeUploader(config, "test_brand", dry_run=True)
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video")

        result = uploader.upload(
            video_path=video_file,
            channel_id="ch_001",
            video_id="vid-001",
            variant={"platform": "youtube", "metadata": {"title": "Test"}},
        )
        assert result.success is True
        assert result.metadata.get("dry_run") is True
        assert result.platform_video_id == "dry-run-id"

    def test_rate_limit_check(self):
        config = {"rate_limits": {"max_uploads_per_day": 2}}
        uploader = YouTubeUploader(config, "test_brand", dry_run=True)
        uploader._daily_upload_count = 2

        result = uploader.upload(
            video_path=Path("/fake.mp4"),
            channel_id="ch_001",
            video_id="vid-001",
            variant={"platform": "youtube", "metadata": {}},
        )
        assert result.success is False
        assert result.error == "daily_rate_limit_exceeded"

    def test_env_with_suffix(self, monkeypatch):
        monkeypatch.setenv("YT_CLIENT_ID_SP", "test-id")
        config = {}
        uploader = YouTubeUploader(config, "stillness_press", credential_suffix="_SP", dry_run=True)
        assert uploader._env("YT_CLIENT_ID") == "test-id"

    def test_env_missing_in_live_mode(self):
        config = {}
        uploader = YouTubeUploader(config, "test_brand", dry_run=False)
        with pytest.raises(EnvironmentError, match="Missing required credential"):
            uploader._env("YT_CLIENT_ID")


# ── YouTube uploader tests ──────────────────────────────────────────────────

class TestYouTubeUploader:
    def test_shorts_mode_adds_hashtag(self, tmp_path):
        config = {"rate_limits": {"max_uploads_per_day": 10}}
        uploader = YouTubeUploader(config, "test_brand", dry_run=True)
        uploader.set_shorts_mode(True)
        assert uploader._is_shorts is True

    def test_authenticate_needs_credentials(self, monkeypatch):
        monkeypatch.delenv("YT_CLIENT_ID", raising=False)
        monkeypatch.delenv("YT_CLIENT_SECRET", raising=False)
        monkeypatch.delenv("YT_REFRESH_TOKEN", raising=False)
        config = {}
        uploader = YouTubeUploader(config, "test_brand", dry_run=False)
        # Auth will fail due to missing env vars
        assert uploader.authenticate() is False


# ── TikTok uploader tests ───────────────────────────────────────────────────

class TestTikTokUploader:
    def test_dry_run(self, tmp_path):
        config = {"rate_limits": {"max_uploads_per_day": 20}}
        uploader = TikTokUploader(config, "test_brand", dry_run=True)
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video")

        result = uploader.upload(
            video_path=video_file,
            channel_id="ch_003",
            video_id="vid-003",
            variant={"platform": "tiktok", "metadata": {"title": "Test TikTok", "hashtags": ["wellness"]}},
        )
        assert result.success is True

    def test_authenticate_needs_token(self, monkeypatch):
        monkeypatch.delenv("TIKTOK_ACCESS_TOKEN", raising=False)
        config = {}
        uploader = TikTokUploader(config, "test_brand", dry_run=False)
        assert uploader.authenticate() is False


# ── Instagram uploader tests ────────────────────────────────────────────────

class TestInstagramReelsUploader:
    def test_dry_run(self, tmp_path):
        config = {"rate_limits": {"max_uploads_per_day": 25}}
        uploader = InstagramReelsUploader(config, "test_brand", dry_run=True)
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video")

        result = uploader.upload(
            video_path=video_file,
            channel_id="ch_005",
            video_id="vid-005",
            variant={"platform": "instagram_reels", "metadata": {"title": "Test Reel"}},
        )
        assert result.success is True


# ── Bilibili uploader tests ─────────────────────────────────────────────────

class TestBilibiliUploader:
    def test_zh_subtitle_check_fails(self):
        config = {"compliance": {"requires_zh_subtitles": True}}
        uploader = BilibiliUploader(config, "test_brand", dry_run=False)
        uploader._authenticated = True
        result = uploader._upload_video(Path("/fake.mp4"), {"zh_subtitle_path": "/nonexistent.srt"})
        assert result.success is False
        assert "zh_subtitles_required" in result.error

    def test_dry_run(self, tmp_path):
        config = {"rate_limits": {"max_uploads_per_day": 20}}
        uploader = BilibiliUploader(config, "test_brand", dry_run=True)
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video")

        result = uploader.upload(
            video_path=video_file,
            channel_id="ch_010",
            video_id="vid-010",
            variant={"platform": "bilibili", "metadata": {"title": "Test Bilibili"}},
        )
        assert result.success is True


# ── Douyin uploader tests ───────────────────────────────────────────────────

class TestDouyinUploader:
    def test_dry_run(self, tmp_path):
        config = {"rate_limits": {"max_uploads_per_day": 20}}
        uploader = DouyinUploader(config, "test_brand", dry_run=True)
        video_file = tmp_path / "test.mp4"
        video_file.write_bytes(b"fake video")

        result = uploader.upload(
            video_path=video_file,
            channel_id="ch_014",
            video_id="vid-014",
            variant={"platform": "douyin", "metadata": {"title": "Test Douyin"}},
        )
        assert result.success is True


# ── Orchestrator tests (run_upload module) ───────────────────────────────────

class TestRunUploadOrchestrator:
    def test_resolve_video_path_specific(self, tmp_path):
        from scripts.video.run_upload import resolve_video_path
        specific = tmp_path / "ch_001_youtube.mp4"
        specific.write_bytes(b"video")
        result = resolve_video_path(tmp_path, "ch_001", "youtube")
        assert result == specific

    def test_resolve_video_path_generic(self, tmp_path):
        from scripts.video.run_upload import resolve_video_path
        generic = tmp_path / "ch_001.mp4"
        generic.write_bytes(b"video")
        result = resolve_video_path(tmp_path, "ch_001", "youtube")
        assert result == generic

    def test_resolve_video_path_not_found(self, tmp_path):
        from scripts.video.run_upload import resolve_video_path
        result = resolve_video_path(tmp_path, "ch_001", "youtube")
        assert result is None

    def test_get_brand_for_channel(self):
        from scripts.video.run_upload import get_brand_for_channel
        channels = {"ch_001": {"brand_id": "stillness_press"}}
        assert get_brand_for_channel("ch_001", channels) == "stillness_press"
        assert get_brand_for_channel("ch_999", channels) == "unknown"

    def test_get_platforms_for_channel(self):
        from scripts.video.run_upload import get_platforms_for_channel
        channels = {"ch_001": {"brand_id": "stillness_press"}}
        upload_config = {
            "platforms": {
                "youtube": {"enabled": True},
                "youtube_shorts": {"inherits": "youtube"},
                "tiktok": {"enabled": True},
                "instagram_reels": {"enabled": True},
                "bilibili": {"enabled": True},
                "webtoon": {"enabled": False},
            },
            "brand_platform_map": {
                "stillness_press": {
                    "youtube": True,
                    "youtube_shorts": True,
                    "tiktok": True,
                    "instagram_reels": True,
                    "bilibili": False,
                    "credential_suffix": "_SP",
                },
            },
        }
        platforms = get_platforms_for_channel("ch_001", channels, upload_config)
        assert "youtube" in platforms
        assert "tiktok" in platforms
        assert "instagram_reels" in platforms
        assert "bilibili" not in platforms

    def test_get_platforms_with_filter(self):
        from scripts.video.run_upload import get_platforms_for_channel
        channels = {"ch_001": {"brand_id": "stillness_press"}}
        upload_config = {
            "platforms": {
                "youtube": {"enabled": True},
                "tiktok": {"enabled": True},
            },
            "brand_platform_map": {
                "stillness_press": {
                    "youtube": True,
                    "tiktok": True,
                    "credential_suffix": "_SP",
                },
            },
        }
        platforms = get_platforms_for_channel("ch_001", channels, upload_config, ["youtube"])
        assert platforms == ["youtube"]

    def test_run_upload_dry_run(self, tmp_path):
        """Full orchestrator dry run with a minimal variants file."""
        from scripts.video.run_upload import run_upload

        variants = {
            "video_id": "vid-test-001",
            "variants": [
                {"platform": "youtube", "metadata": {"title": "Test Video"}},
                {"platform": "tiktok", "metadata": {"title": "Test TikTok"}},
            ],
        }
        variants_path = tmp_path / "platform_variants.json"
        variants_path.write_text(json.dumps(variants))

        output_path = tmp_path / "results.json"

        with patch("scripts.video.run_upload.load_channel_registry") as mock_reg, \
             patch("scripts.video.run_upload.load_upload_config") as mock_cfg:
            mock_reg.return_value = {
                "ch_001": {"brand_id": "stillness_press"},
            }
            mock_cfg.return_value = {
                "platforms": {
                    "youtube": {"enabled": True, "rate_limits": {"max_uploads_per_day": 6}},
                    "tiktok": {"enabled": True, "rate_limits": {"max_uploads_per_day": 20}},
                },
                "brand_platform_map": {
                    "stillness_press": {
                        "youtube": True,
                        "tiktok": True,
                        "credential_suffix": "_SP",
                    },
                },
                "scheduling": {"retry_max": 1, "retry_backoff_base_s": 1},
            }

            results = run_upload(
                variants_path=variants_path,
                channel_id="ch_001",
                video_dir=tmp_path,
                platforms_filter=None,
                batch_mode=False,
                dry_run=True,
                output_path=output_path,
            )

        assert len(results) == 2
        assert all(r["success"] for r in results)
        assert output_path.exists()
        output_data = json.loads(output_path.read_text())
        assert output_data["dry_run"] is True
        assert output_data["uploads_succeeded"] == 2
