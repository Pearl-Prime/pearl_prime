"""Stage 18 — Video Upload/Publish: platform-specific uploaders for the VCE pipeline."""

from scripts.video.uploaders.base import BaseUploader, UploadResult
from scripts.video.uploaders.youtube import YouTubeUploader
from scripts.video.uploaders.tiktok import TikTokUploader
from scripts.video.uploaders.instagram import InstagramReelsUploader
from scripts.video.uploaders.bilibili import BilibiliUploader
from scripts.video.uploaders.douyin import DouyinUploader

UPLOADERS: dict[str, type[BaseUploader]] = {
    "youtube": YouTubeUploader,
    "youtube_shorts": YouTubeUploader,
    "tiktok": TikTokUploader,
    "instagram_reels": InstagramReelsUploader,
    "bilibili": BilibiliUploader,
    "douyin": DouyinUploader,
}

__all__ = [
    "BaseUploader",
    "UploadResult",
    "YouTubeUploader",
    "TikTokUploader",
    "InstagramReelsUploader",
    "BilibiliUploader",
    "DouyinUploader",
    "UPLOADERS",
]
