"""
Stage 18 — Upload/Publish: extended tests for quota management, scheduling,
credential resolution, and integration smoke tests.

These tests are intentionally self-contained: they do NOT make real HTTP
requests and do NOT touch the filesystem beyond tmp_path fixtures.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch, PropertyMock

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


# ── Minimal in-test QuotaManager ────────────────────────────────────────────
# The production code stores quota tracking inside each uploader instance
# (_daily_upload_count). These tests validate that behaviour plus a thin
# coordinator class mirroring the upload_config.yaml spec.

class QuotaManager:
    """Thin coordinator that mirrors the per-brand-per-platform quota rules
    expressed in upload_config.yaml.  Wraps the per-uploader counters so we
    can test cross-brand and cross-platform aggregation in isolation."""

    def __init__(self, config: dict):
        """
        config shape (mirrors brand_platform_map section of upload_config.yaml):
            {
                "<brand_id>": {
                    "<platform>": <daily_cap: int>,
                    ...
                }
            }
        """
        self._caps: dict[str, dict[str, int]] = config
        self._counts: dict[str, dict[str, int]] = {
            brand: {platform: 0 for platform in platforms}
            for brand, platforms in config.items()
        }

    def can_publish(self, brand_id: str, platform: str) -> bool:
        """Return True when the brand+platform is under its daily cap."""
        cap = self._caps.get(brand_id, {}).get(platform, 0)
        count = self._counts.get(brand_id, {}).get(platform, 0)
        return count < cap

    def record_publish(self, brand_id: str, platform: str) -> None:
        """Increment the counter for brand+platform."""
        if brand_id in self._counts and platform in self._counts[brand_id]:
            self._counts[brand_id][platform] += 1

    def reset_daily_counts(self) -> None:
        """Zero all counters (called at midnight UTC by the scheduler)."""
        for brand in self._counts:
            for platform in self._counts[brand]:
                self._counts[brand][platform] = 0

    def count(self, brand_id: str, platform: str) -> int:
        return self._counts.get(brand_id, {}).get(platform, 0)


# ── 1. Quota manager tests ───────────────────────────────────────────────────

_QUOTA_CFG = {
    "stillness_press": {"youtube": 6, "tiktok": 20},
    "cognitive_clarity": {"youtube": 6, "tiktok": 20},
}


class TestQuotaManagerCanPublish:
    def test_can_publish_when_under_quota(self):
        qm = QuotaManager(_QUOTA_CFG)
        assert qm.can_publish("stillness_press", "youtube") is True

    def test_can_publish_false_when_at_quota(self):
        qm = QuotaManager(_QUOTA_CFG)
        for _ in range(6):
            qm.record_publish("stillness_press", "youtube")
        assert qm.can_publish("stillness_press", "youtube") is False

    def test_can_publish_false_after_exceeding_quota(self):
        qm = QuotaManager({"brand_a": {"youtube": 2}})
        qm.record_publish("brand_a", "youtube")
        qm.record_publish("brand_a", "youtube")
        assert qm.can_publish("brand_a", "youtube") is False

    def test_can_publish_unknown_brand_returns_false(self):
        qm = QuotaManager(_QUOTA_CFG)
        assert qm.can_publish("nonexistent_brand", "youtube") is False

    def test_can_publish_unknown_platform_returns_false(self):
        qm = QuotaManager(_QUOTA_CFG)
        assert qm.can_publish("stillness_press", "webtoon") is False

    def test_different_platforms_independent(self):
        qm = QuotaManager(_QUOTA_CFG)
        for _ in range(6):
            qm.record_publish("stillness_press", "youtube")
        # YouTube is exhausted, TikTok should still be open
        assert qm.can_publish("stillness_press", "youtube") is False
        assert qm.can_publish("stillness_press", "tiktok") is True

    def test_different_brands_independent(self):
        qm = QuotaManager(_QUOTA_CFG)
        for _ in range(6):
            qm.record_publish("stillness_press", "youtube")
        assert qm.can_publish("stillness_press", "youtube") is False
        assert qm.can_publish("cognitive_clarity", "youtube") is True


class TestQuotaManagerRecordPublish:
    def test_record_publish_increments_counter(self):
        qm = QuotaManager(_QUOTA_CFG)
        assert qm.count("stillness_press", "youtube") == 0
        qm.record_publish("stillness_press", "youtube")
        assert qm.count("stillness_press", "youtube") == 1

    def test_record_publish_multiple_increments(self):
        qm = QuotaManager(_QUOTA_CFG)
        for i in range(5):
            qm.record_publish("stillness_press", "tiktok")
        assert qm.count("stillness_press", "tiktok") == 5

    def test_record_publish_does_not_affect_other_brand(self):
        qm = QuotaManager(_QUOTA_CFG)
        qm.record_publish("stillness_press", "youtube")
        assert qm.count("cognitive_clarity", "youtube") == 0

    def test_record_publish_unknown_brand_is_noop(self):
        qm = QuotaManager(_QUOTA_CFG)
        qm.record_publish("ghost_brand", "youtube")  # should not raise
        assert qm.count("stillness_press", "youtube") == 0


class TestQuotaManagerResetDailyCounts:
    def test_reset_daily_counts_clears_all_counters(self):
        qm = QuotaManager(_QUOTA_CFG)
        qm.record_publish("stillness_press", "youtube")
        qm.record_publish("cognitive_clarity", "tiktok")
        qm.reset_daily_counts()
        assert qm.count("stillness_press", "youtube") == 0
        assert qm.count("cognitive_clarity", "tiktok") == 0

    def test_can_publish_true_after_reset(self):
        qm = QuotaManager(_QUOTA_CFG)
        for _ in range(6):
            qm.record_publish("stillness_press", "youtube")
        assert qm.can_publish("stillness_press", "youtube") is False
        qm.reset_daily_counts()
        assert qm.can_publish("stillness_press", "youtube") is True


class TestQuotaManagerLoadFromConfig:
    def test_load_upload_config_yaml(self):
        """Verify upload_config.yaml is parseable and has brand_platform_map."""
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        assert "brand_platform_map" in cfg
        brand_map = cfg["brand_platform_map"]
        assert "stillness_press" in brand_map
        assert "cognitive_clarity" in brand_map

    def test_brand_platform_map_has_credential_suffix(self):
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        sp = cfg["brand_platform_map"]["stillness_press"]
        assert sp.get("credential_suffix") == "_SP"
        cc = cfg["brand_platform_map"]["cognitive_clarity"]
        assert cc.get("credential_suffix") == "_CC"

    def test_scheduling_block_present(self):
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        sched = cfg.get("scheduling", {})
        assert "base_hour_utc" in sched
        assert "stagger_minutes" in sched
        assert "retry_max" in sched


# ── 2. Upload scheduling tests ───────────────────────────────────────────────

class TestStaggerCalculation:
    """Stagger logic lives in upload_config.yaml and would be consumed by
    a scheduler. These tests validate the config values and simulate what a
    scheduler must do with them."""

    def _get_scheduling(self) -> dict:
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        return cfg.get("scheduling", {})

    def test_base_hour_is_valid_utc(self):
        sched = self._get_scheduling()
        base = sched.get("base_hour_utc", -1)
        assert 0 <= base <= 23, f"base_hour_utc={base} is not in [0,23]"

    def test_stagger_minutes_positive(self):
        sched = self._get_scheduling()
        stagger = sched.get("stagger_minutes", 0)
        assert stagger > 0, "stagger_minutes must be positive"

    def test_brand_stagger_between_brands(self):
        """Two distinct brands should receive distinct upload offsets."""
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        sched = cfg.get("scheduling", {})
        brands = list(cfg.get("brand_platform_map", {}).keys())
        # At least 2 brands must exist for this test to be meaningful
        assert len(brands) >= 2, "Need at least 2 brands"
        stagger = sched.get("stagger_minutes", 15)
        offsets = [i * stagger for i in range(len(brands))]
        assert len(set(offsets)) == len(offsets), "Offsets for brands are not unique"

    def test_platform_stagger_within_brand(self):
        """Within a single brand, stagger each platform upload."""
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        sched = cfg.get("scheduling", {})
        stagger = sched.get("stagger_minutes", 15)
        brand_cfg = cfg["brand_platform_map"]["stillness_press"]
        enabled_platforms = [
            k for k, v in brand_cfg.items()
            if isinstance(v, bool) and v
        ]
        offsets = [i * stagger for i in range(len(enabled_platforms))]
        assert len(set(offsets)) == len(offsets)

    def test_stagger_does_not_overflow_window(self):
        """With stagger_minutes applied, the final platform fits in one hour."""
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        sched = cfg.get("scheduling", {})
        stagger = sched.get("stagger_minutes", 15)
        window = sched.get("window_duration_hours", 1) * 60
        brand_cfg = cfg["brand_platform_map"]["stillness_press"]
        platforms = [k for k, v in brand_cfg.items() if isinstance(v, bool) and v]
        max_offset = (len(platforms) - 1) * stagger
        assert max_offset < window, (
            f"stagger overflow: {len(platforms)} platforms × {stagger}min "
            f"= {max_offset}min > {window}min window"
        )


class TestPublishWindowValidation:
    """publish_window: only upload during allowed UTC hours."""

    def _is_in_window(self, current_hour_utc: int, base_hour: int, window_duration_hours: int) -> bool:
        """Helper: return True if current_hour_utc is within [base_hour, base_hour+window)."""
        end_hour = (base_hour + window_duration_hours) % 24
        if base_hour <= end_hour:
            return base_hour <= current_hour_utc < end_hour
        # Window wraps midnight
        return current_hour_utc >= base_hour or current_hour_utc < end_hour

    def test_publish_allowed_at_base_hour(self):
        assert self._is_in_window(6, base_hour=6, window_duration_hours=1) is True

    def test_publish_not_allowed_before_window(self):
        assert self._is_in_window(5, base_hour=6, window_duration_hours=1) is False

    def test_publish_not_allowed_after_window(self):
        assert self._is_in_window(7, base_hour=6, window_duration_hours=1) is False

    def test_publish_allowed_at_start_of_window(self):
        assert self._is_in_window(6, base_hour=6, window_duration_hours=2) is True

    def test_publish_allowed_within_window(self):
        assert self._is_in_window(7, base_hour=6, window_duration_hours=2) is True

    def test_publish_not_allowed_at_boundary(self):
        # End boundary is exclusive
        assert self._is_in_window(8, base_hour=6, window_duration_hours=2) is False

    def test_window_wraps_midnight(self):
        # Window from 23:00 to 01:00
        assert self._is_in_window(0, base_hour=23, window_duration_hours=2) is True
        assert self._is_in_window(23, base_hour=23, window_duration_hours=2) is True
        assert self._is_in_window(1, base_hour=23, window_duration_hours=2) is False

    def test_upload_config_base_hour_is_in_own_window(self):
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        sched = cfg.get("scheduling", {})
        base = sched.get("base_hour_utc", 6)
        window = sched.get("window_duration_hours", 1)
        assert self._is_in_window(base, base_hour=base, window_duration_hours=window)


class TestDryRunMode:
    def test_dry_run_does_not_call_upload_video(self, tmp_path):
        """Dry run must short-circuit before calling _upload_video."""
        config = {"rate_limits": {"max_uploads_per_day": 10}}
        uploader = YouTubeUploader(config, "stillness_press", dry_run=True)
        video_file = tmp_path / "sample.mp4"
        video_file.write_bytes(b"\x00" * 128)

        with patch.object(uploader, "_upload_video") as mock_upload:
            result = uploader.upload(
                video_path=video_file,
                channel_id="ch_001",
                video_id="vid-dry-001",
                variant={"platform": "youtube", "metadata": {"title": "Dry Test"}},
            )
            mock_upload.assert_not_called()

        assert result.success is True
        assert result.metadata.get("dry_run") is True

    def test_dry_run_does_not_call_authenticate(self, tmp_path):
        """Dry run must not call authenticate (no credential check)."""
        config = {"rate_limits": {"max_uploads_per_day": 10}}
        uploader = TikTokUploader(config, "stillness_press", dry_run=True)
        video_file = tmp_path / "sample.mp4"
        video_file.write_bytes(b"\x00" * 128)

        with patch.object(uploader, "authenticate") as mock_auth:
            result = uploader.upload(
                video_path=video_file,
                channel_id="ch_001",
                video_id="vid-dry-002",
                variant={"platform": "tiktok", "metadata": {"title": "TikTok Dry"}},
            )
            mock_auth.assert_not_called()

        assert result.success is True

    def test_dry_run_returns_placeholder_video_id(self, tmp_path):
        config = {"rate_limits": {"max_uploads_per_day": 10}}
        uploader = InstagramReelsUploader(config, "stillness_press", dry_run=True)
        video_file = tmp_path / "sample.mp4"
        video_file.write_bytes(b"\x00" * 128)
        result = uploader.upload(
            video_path=video_file,
            channel_id="ch_001",
            video_id="vid-dry-003",
            variant={"platform": "instagram_reels", "metadata": {"title": "IG Dry"}},
        )
        assert result.platform_video_id == "dry-run-id"

    def test_dry_run_does_not_increment_daily_count(self, tmp_path):
        config = {"rate_limits": {"max_uploads_per_day": 10}}
        uploader = YouTubeUploader(config, "stillness_press", dry_run=True)
        video_file = tmp_path / "sample.mp4"
        video_file.write_bytes(b"\x00" * 128)
        assert uploader._daily_upload_count == 0
        uploader.upload(
            video_path=video_file,
            channel_id="ch_001",
            video_id="vid-dry-004",
            variant={"platform": "youtube", "metadata": {"title": "Counter Test"}},
        )
        # Dry run must NOT increment the counter
        assert uploader._daily_upload_count == 0

    def test_run_upload_dry_run_no_actual_upload(self, tmp_path):
        """Full orchestrator in dry-run must succeed without any real uploader call."""
        from scripts.video.run_upload import run_upload

        variants = {
            "video_id": "vid-orchestrator-dry",
            "variants": [
                {"platform": "youtube", "metadata": {"title": "Orchestrator Dry Test"}},
            ],
        }
        variants_path = tmp_path / "variants.json"
        variants_path.write_text(json.dumps(variants))
        output_path = tmp_path / "out.json"

        with patch("scripts.video.run_upload.load_channel_registry") as mock_reg, \
             patch("scripts.video.run_upload.load_upload_config") as mock_cfg, \
             patch("scripts.video.run_upload.config_snapshot_hash", return_value="testhash"):
            mock_reg.return_value = {"ch_001": {"brand_id": "stillness_press"}}
            mock_cfg.return_value = {
                "platforms": {
                    "youtube": {"enabled": True, "rate_limits": {"max_uploads_per_day": 6}},
                },
                "brand_platform_map": {
                    "stillness_press": {
                        "youtube": True,
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

        assert len(results) == 1
        assert results[0]["success"] is True
        data = json.loads(output_path.read_text())
        assert data["dry_run"] is True
        assert data["uploads_succeeded"] == 1


# ── 3. Credential resolution tests ──────────────────────────────────────────

class TestEnvHelperSuffixResolution:
    def test_env_resolves_brand_suffixed_secret(self, monkeypatch):
        monkeypatch.setenv("YT_CLIENT_ID_SP", "sp-client-id-value")
        uploader = YouTubeUploader({}, "stillness_press", credential_suffix="_SP", dry_run=True)
        assert uploader._env("YT_CLIENT_ID") == "sp-client-id-value"

    def test_env_resolves_cc_suffix(self, monkeypatch):
        monkeypatch.setenv("YT_CLIENT_SECRET_CC", "cc-secret-value")
        uploader = YouTubeUploader({}, "cognitive_clarity", credential_suffix="_CC", dry_run=True)
        assert uploader._env("YT_CLIENT_SECRET") == "cc-secret-value"

    def test_env_resolves_nd_suffix(self, monkeypatch):
        monkeypatch.setenv("TIKTOK_ACCESS_TOKEN_ND", "nd-token-value")
        uploader = TikTokUploader({}, "norcal_dharma", credential_suffix="_ND", dry_run=True)
        assert uploader._env("TIKTOK_ACCESS_TOKEN") == "nd-token-value"

    def test_env_empty_suffix_uses_bare_key(self, monkeypatch):
        monkeypatch.setenv("YT_REFRESH_TOKEN", "bare-token")
        uploader = YouTubeUploader({}, "some_brand", credential_suffix="", dry_run=True)
        assert uploader._env("YT_REFRESH_TOKEN") == "bare-token"

    def test_env_suffixed_key_not_bare(self, monkeypatch):
        """With suffix _SP, bare key must NOT be picked up."""
        monkeypatch.delenv("YT_CLIENT_ID_SP", raising=False)
        monkeypatch.setenv("YT_CLIENT_ID", "bare-id")  # bare key exists
        # In dry_run mode _env returns "" (no raise) for missing suffixed key
        uploader = YouTubeUploader({}, "stillness_press", credential_suffix="_SP", dry_run=True)
        val = uploader._env("YT_CLIENT_ID")
        # Should return "" because "YT_CLIENT_ID_SP" is not set
        assert val == ""

    def test_env_with_suffix_prefers_suffixed(self, monkeypatch):
        """Suffixed key wins over bare key."""
        monkeypatch.setenv("YT_CLIENT_ID", "bare-val")
        monkeypatch.setenv("YT_CLIENT_ID_SP", "suffixed-val")
        uploader = YouTubeUploader({}, "stillness_press", credential_suffix="_SP", dry_run=True)
        assert uploader._env("YT_CLIENT_ID") == "suffixed-val"


class TestMissingCredentialError:
    def test_missing_credential_raises_environment_error_in_live_mode(self, monkeypatch):
        monkeypatch.delenv("YT_CLIENT_ID_SP", raising=False)
        uploader = YouTubeUploader({}, "stillness_press", credential_suffix="_SP", dry_run=False)
        with pytest.raises(EnvironmentError, match="Missing required credential"):
            uploader._env("YT_CLIENT_ID")

    def test_error_message_names_the_missing_key(self, monkeypatch):
        monkeypatch.delenv("TIKTOK_ACCESS_TOKEN_CC", raising=False)
        uploader = TikTokUploader({}, "cognitive_clarity", credential_suffix="_CC", dry_run=False)
        with pytest.raises(EnvironmentError, match="TIKTOK_ACCESS_TOKEN_CC"):
            uploader._env("TIKTOK_ACCESS_TOKEN")

    def test_dry_run_does_not_raise_for_missing_credential(self, monkeypatch):
        monkeypatch.delenv("YT_CLIENT_ID_SP", raising=False)
        uploader = YouTubeUploader({}, "stillness_press", credential_suffix="_SP", dry_run=True)
        val = uploader._env("YT_CLIENT_ID")
        assert val == ""

    def test_bilibili_missing_sessdata_raises(self, monkeypatch):
        monkeypatch.delenv("BILI_SESSDATA_SP", raising=False)
        uploader = BilibiliUploader({}, "stillness_press", credential_suffix="_SP", dry_run=False)
        with pytest.raises(EnvironmentError, match="Missing required credential"):
            uploader._env("BILI_SESSDATA")

    def test_douyin_missing_access_token_raises(self, monkeypatch):
        monkeypatch.delenv("DOUYIN_ACCESS_TOKEN_ND", raising=False)
        uploader = DouyinUploader({}, "norcal_dharma", credential_suffix="_ND", dry_run=False)
        with pytest.raises(EnvironmentError, match="Missing required credential"):
            uploader._env("DOUYIN_ACCESS_TOKEN")


class TestCredentialSuffixMapping:
    """Ensure the suffix constants from upload_config.yaml match expectations."""

    def test_sp_suffix_in_config(self):
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        assert cfg["brand_platform_map"]["stillness_press"]["credential_suffix"] == "_SP"

    def test_cc_suffix_in_config(self):
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        assert cfg["brand_platform_map"]["cognitive_clarity"]["credential_suffix"] == "_CC"

    def test_nd_suffix_in_config(self):
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        assert cfg["brand_platform_map"]["norcal_dharma"]["credential_suffix"] == "_ND"

    def test_suffixes_are_all_unique(self):
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        suffixes = [
            v.get("credential_suffix")
            for v in cfg["brand_platform_map"].values()
        ]
        assert len(suffixes) == len(set(suffixes)), "Duplicate credential suffixes detected"

    def test_all_brands_have_suffix(self):
        from scripts.video._config import load_yaml
        cfg = load_yaml("config/video/upload_config.yaml")
        for brand, brand_cfg in cfg["brand_platform_map"].items():
            suffix = brand_cfg.get("credential_suffix", "")
            assert suffix, f"Brand '{brand}' has no credential_suffix"
            assert suffix.startswith("_"), (
                f"Brand '{brand}' suffix '{suffix}' must start with '_'"
            )


# ── 4. Integration smoke tests (mocked) ─────────────────────────────────────

class TestYouTubeUploaderInit:
    def test_init_with_mocked_credentials(self, monkeypatch):
        """YouTubeUploader should initialise without raising when creds are mocked."""
        monkeypatch.setenv("YT_CLIENT_ID_SP", "mock-client-id")
        monkeypatch.setenv("YT_CLIENT_SECRET_SP", "mock-client-secret")
        monkeypatch.setenv("YT_REFRESH_TOKEN_SP", "mock-refresh-token")

        config = {"rate_limits": {"max_uploads_per_day": 6}}
        uploader = YouTubeUploader(config, "stillness_press", credential_suffix="_SP", dry_run=False)

        assert uploader.brand_id == "stillness_press"
        assert uploader.credential_suffix == "_SP"
        assert uploader._authenticated is False  # not yet authenticated

    def test_authenticate_calls_token_url(self, monkeypatch):
        """authenticate() should POST to the Google token endpoint."""
        monkeypatch.setenv("YT_CLIENT_ID_SP", "mock-client-id")
        monkeypatch.setenv("YT_CLIENT_SECRET_SP", "mock-secret")
        monkeypatch.setenv("YT_REFRESH_TOKEN_SP", "mock-refresh")

        mock_response = MagicMock()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_response.read.return_value = json.dumps({"access_token": "mock-access-token"}).encode()

        config = {}
        uploader = YouTubeUploader(config, "stillness_press", credential_suffix="_SP", dry_run=False)

        with patch("scripts.video.uploaders.youtube.urlopen", return_value=mock_response) as mock_open:
            result = uploader.authenticate()

        assert result is True
        assert uploader._authenticated is True
        assert uploader._access_token == "mock-access-token"
        mock_open.assert_called_once()

    def test_authenticate_returns_false_on_http_error(self, monkeypatch):
        from urllib.error import HTTPError
        monkeypatch.setenv("YT_CLIENT_ID_SP", "mock-client-id")
        monkeypatch.setenv("YT_CLIENT_SECRET_SP", "mock-secret")
        monkeypatch.setenv("YT_REFRESH_TOKEN_SP", "mock-refresh")

        config = {}
        uploader = YouTubeUploader(config, "stillness_press", credential_suffix="_SP", dry_run=False)

        with patch("scripts.video.uploaders.youtube.urlopen",
                   side_effect=HTTPError(None, 401, "Unauthorized", {}, None)):
            result = uploader.authenticate()

        assert result is False
        assert uploader._authenticated is False

    def test_shorts_mode_flag(self):
        config = {"rate_limits": {"max_uploads_per_day": 6}}
        uploader = YouTubeUploader(config, "test_brand", dry_run=True)
        assert uploader._is_shorts is False
        uploader.set_shorts_mode(True)
        assert uploader._is_shorts is True
        uploader.set_shorts_mode(False)
        assert uploader._is_shorts is False

    def test_platform_constant(self):
        assert YouTubeUploader.PLATFORM == "youtube"

    def test_uploaders_registry_has_youtube(self):
        assert "youtube" in UPLOADERS
        assert UPLOADERS["youtube"] is YouTubeUploader


class TestTikTokUploaderInit:
    def test_init_with_mocked_credentials(self, monkeypatch):
        monkeypatch.setenv("TIKTOK_ACCESS_TOKEN_SP", "mock-tt-token")
        config = {"rate_limits": {"max_uploads_per_day": 20}}
        uploader = TikTokUploader(config, "stillness_press", credential_suffix="_SP", dry_run=False)
        assert uploader.brand_id == "stillness_press"
        assert uploader._authenticated is False

    def test_authenticate_with_mocked_token(self, monkeypatch):
        monkeypatch.setenv("TIKTOK_ACCESS_TOKEN_SP", "mock-tt-token")
        config = {}
        uploader = TikTokUploader(config, "stillness_press", credential_suffix="_SP", dry_run=False)
        result = uploader.authenticate()
        assert result is True
        assert uploader._authenticated is True
        assert uploader._access_token == "mock-tt-token"

    def test_authenticate_fails_without_token(self, monkeypatch):
        monkeypatch.delenv("TIKTOK_ACCESS_TOKEN_SP", raising=False)
        config = {}
        uploader = TikTokUploader(config, "stillness_press", credential_suffix="_SP", dry_run=False)
        result = uploader.authenticate()
        assert result is False

    def test_platform_constant(self):
        assert TikTokUploader.PLATFORM == "tiktok"

    def test_uploaders_registry_has_tiktok(self):
        assert "tiktok" in UPLOADERS
        assert UPLOADERS["tiktok"] is TikTokUploader

    def test_dry_run_succeeds_without_token(self, tmp_path):
        config = {"rate_limits": {"max_uploads_per_day": 20}}
        uploader = TikTokUploader(config, "stillness_press", dry_run=True)
        video_file = tmp_path / "vid.mp4"
        video_file.write_bytes(b"\x00" * 64)
        result = uploader.upload(
            video_path=video_file,
            channel_id="ch_002",
            video_id="vid-tt-001",
            variant={"platform": "tiktok", "metadata": {"title": "TikTok Test"}},
        )
        assert result.success is True
        assert result.platform == "tiktok"


class TestRunUploadArgParsing:
    """Test the CLI argument parser for run_upload.py main()."""

    def _make_parser(self) -> argparse.ArgumentParser:
        """Replicate the parser from main() without running main()."""
        parser = argparse.ArgumentParser()
        parser.add_argument("variants_json", type=Path)
        parser.add_argument("--channel-id", type=str)
        parser.add_argument("--batch", action="store_true")
        parser.add_argument("--video-dir", type=Path, default=Path("artifacts/video/rendered"))
        parser.add_argument("--platforms", type=str)
        parser.add_argument("--no-dry-run", action="store_true")
        parser.add_argument("-o", "--output", type=Path)
        return parser

    def test_minimal_args_parse(self, tmp_path):
        parser = self._make_parser()
        variants_file = tmp_path / "variants.json"
        variants_file.write_text("{}")
        args = parser.parse_args([str(variants_file), "--channel-id", "ch_001"])
        assert args.channel_id == "ch_001"
        assert args.batch is False
        assert args.no_dry_run is False  # default: dry-run on

    def test_dry_run_default_is_true(self, tmp_path):
        parser = self._make_parser()
        variants_file = tmp_path / "variants.json"
        variants_file.write_text("{}")
        args = parser.parse_args([str(variants_file), "--channel-id", "ch_001"])
        dry_run = not args.no_dry_run
        assert dry_run is True

    def test_no_dry_run_flag(self, tmp_path):
        parser = self._make_parser()
        variants_file = tmp_path / "variants.json"
        variants_file.write_text("{}")
        args = parser.parse_args([str(variants_file), "--channel-id", "ch_001", "--no-dry-run"])
        dry_run = not args.no_dry_run
        assert dry_run is False

    def test_batch_flag(self, tmp_path):
        parser = self._make_parser()
        variants_file = tmp_path / "variants.json"
        variants_file.write_text("{}")
        args = parser.parse_args([str(variants_file), "--batch"])
        assert args.batch is True

    def test_platforms_filter_parsed(self, tmp_path):
        parser = self._make_parser()
        variants_file = tmp_path / "variants.json"
        variants_file.write_text("{}")
        args = parser.parse_args([str(variants_file), "--channel-id", "ch_001",
                                   "--platforms", "youtube,tiktok"])
        platforms = args.platforms.split(",") if args.platforms else None
        assert platforms == ["youtube", "tiktok"]

    def test_output_path_parsed(self, tmp_path):
        parser = self._make_parser()
        variants_file = tmp_path / "variants.json"
        variants_file.write_text("{}")
        out = tmp_path / "results.json"
        args = parser.parse_args([str(variants_file), "--channel-id", "ch_001",
                                   "-o", str(out)])
        assert args.output == out

    def test_video_dir_default(self, tmp_path):
        parser = self._make_parser()
        variants_file = tmp_path / "variants.json"
        variants_file.write_text("{}")
        args = parser.parse_args([str(variants_file), "--channel-id", "ch_001"])
        assert args.video_dir == Path("artifacts/video/rendered")


class TestRunUploadDryRunIntegration:
    """End-to-end dry-run tests with all external I/O mocked."""

    def _make_variants(self, platforms: list[str]) -> dict:
        return {
            "video_id": "vid-integration-001",
            "variants": [
                {"platform": p, "metadata": {"title": f"Test {p}"}}
                for p in platforms
            ],
        }

    def _base_upload_config(self, platforms: list[str]) -> dict:
        platform_cfgs = {
            p: {"enabled": True, "rate_limits": {"max_uploads_per_day": 20}}
            for p in platforms
        }
        brand_map: dict[str, Any] = {p: True for p in platforms}
        brand_map["credential_suffix"] = "_SP"
        return {
            "platforms": platform_cfgs,
            "brand_platform_map": {"stillness_press": brand_map},
            "scheduling": {"retry_max": 1, "retry_backoff_base_s": 1},
        }

    def test_dry_run_youtube_only(self, tmp_path):
        from scripts.video.run_upload import run_upload
        variants_path = tmp_path / "v.json"
        variants_path.write_text(json.dumps(self._make_variants(["youtube"])))

        with patch("scripts.video.run_upload.load_channel_registry",
                   return_value={"ch_001": {"brand_id": "stillness_press"}}), \
             patch("scripts.video.run_upload.load_upload_config",
                   return_value=self._base_upload_config(["youtube"])), \
             patch("scripts.video.run_upload.config_snapshot_hash", return_value="h"):
            results = run_upload(
                variants_path=variants_path,
                channel_id="ch_001",
                video_dir=tmp_path,
                platforms_filter=None,
                batch_mode=False,
                dry_run=True,
                output_path=None,
            )

        assert len(results) == 1
        assert results[0]["success"] is True
        assert results[0]["platform"] == "youtube"

    def test_dry_run_multi_platform(self, tmp_path):
        from scripts.video.run_upload import run_upload
        platforms = ["youtube", "tiktok", "instagram_reels"]
        variants_path = tmp_path / "v.json"
        variants_path.write_text(json.dumps(self._make_variants(platforms)))
        output_path = tmp_path / "out.json"

        with patch("scripts.video.run_upload.load_channel_registry",
                   return_value={"ch_001": {"brand_id": "stillness_press"}}), \
             patch("scripts.video.run_upload.load_upload_config",
                   return_value=self._base_upload_config(platforms)), \
             patch("scripts.video.run_upload.config_snapshot_hash", return_value="h"):
            results = run_upload(
                variants_path=variants_path,
                channel_id="ch_001",
                video_dir=tmp_path,
                platforms_filter=None,
                batch_mode=False,
                dry_run=True,
                output_path=output_path,
            )

        assert len(results) == len(platforms)
        assert all(r["success"] for r in results)
        data = json.loads(output_path.read_text())
        assert data["uploads_succeeded"] == len(platforms)
        assert data["dry_run"] is True

    def test_dry_run_platform_filter_applied(self, tmp_path):
        from scripts.video.run_upload import run_upload
        platforms = ["youtube", "tiktok"]
        variants_path = tmp_path / "v.json"
        variants_path.write_text(json.dumps(self._make_variants(platforms)))

        with patch("scripts.video.run_upload.load_channel_registry",
                   return_value={"ch_001": {"brand_id": "stillness_press"}}), \
             patch("scripts.video.run_upload.load_upload_config",
                   return_value=self._base_upload_config(platforms)), \
             patch("scripts.video.run_upload.config_snapshot_hash", return_value="h"):
            results = run_upload(
                variants_path=variants_path,
                channel_id="ch_001",
                video_dir=tmp_path,
                platforms_filter=["youtube"],
                batch_mode=False,
                dry_run=True,
                output_path=None,
            )

        assert len(results) == 1
        assert results[0]["platform"] == "youtube"

    def test_dry_run_output_json_schema(self, tmp_path):
        """Output JSON must have the documented top-level keys."""
        from scripts.video.run_upload import run_upload
        variants_path = tmp_path / "v.json"
        variants_path.write_text(json.dumps(self._make_variants(["youtube"])))
        output_path = tmp_path / "out.json"

        with patch("scripts.video.run_upload.load_channel_registry",
                   return_value={"ch_001": {"brand_id": "stillness_press"}}), \
             patch("scripts.video.run_upload.load_upload_config",
                   return_value=self._base_upload_config(["youtube"])), \
             patch("scripts.video.run_upload.config_snapshot_hash", return_value="testhash"):
            run_upload(
                variants_path=variants_path,
                channel_id="ch_001",
                video_dir=tmp_path,
                platforms_filter=None,
                batch_mode=False,
                dry_run=True,
                output_path=output_path,
            )

        data = json.loads(output_path.read_text())
        required_keys = {
            "upload_run_id", "config_hash", "dry_run",
            "channels_processed", "uploads_attempted",
            "uploads_succeeded", "uploads_failed", "results", "completed_at",
        }
        missing = required_keys - set(data.keys())
        assert not missing, f"Output JSON missing keys: {missing}"
        assert data["config_hash"] == "testhash"

    def test_dry_run_unknown_channel_skipped(self, tmp_path):
        from scripts.video.run_upload import run_upload
        variants_path = tmp_path / "v.json"
        variants_path.write_text(json.dumps(self._make_variants(["youtube"])))

        with patch("scripts.video.run_upload.load_channel_registry",
                   return_value={"ch_999": {"brand_id": "some_brand"}}), \
             patch("scripts.video.run_upload.load_upload_config",
                   return_value=self._base_upload_config(["youtube"])), \
             patch("scripts.video.run_upload.config_snapshot_hash", return_value="h"):
            results = run_upload(
                variants_path=variants_path,
                channel_id="ch_001",  # not in registry
                video_dir=tmp_path,
                platforms_filter=None,
                batch_mode=False,
                dry_run=True,
                output_path=None,
            )

        assert results == []
