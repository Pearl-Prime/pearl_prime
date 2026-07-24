"""Mocked unit tests for scripts/social/dashscope_free_media.py — no live API."""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.social import dashscope_free_media as dfm  # noqa: E402


class _FakeResp:
    def __init__(self, payload: dict[str, Any] | bytes, status: int = 200):
        self._payload = payload
        self.status = status

    def read(self) -> bytes:
        if isinstance(self._payload, bytes):
            return self._payload
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_beijing_base_refused(monkeypatch):
    monkeypatch.setenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    monkeypatch.delenv("DASHSCOPE_NATIVE_BASE_URL", raising=False)
    with pytest.raises(dfm.DashScopeFreeMediaError, match="Beijing"):
        dfm.native_base()


def test_hard_fail_arrearage():
    with pytest.raises(dfm.DashScopeFreeMediaError, match="Arrearage"):
        dfm._raise_if_hard_fail({"code": "Arrearage", "message": "overdue"})


def test_hard_fail_free_tier_only():
    with pytest.raises(dfm.DashScopeFreeMediaError, match="FreeTierOnly"):
        dfm._raise_if_hard_fail("AllocationQuota.FreeTierOnly exceeded")


def test_submit_image_returns_task_id(monkeypatch):
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")
    monkeypatch.setenv("DASHSCOPE_NATIVE_BASE_URL", "https://dashscope-intl.aliyuncs.com/api/v1")

    def opener(req, timeout=0):
        return _FakeResp({"output": {"task_id": "img-task-1", "task_status": "PENDING"}})

    tid = dfm.submit_image(prompt="calm desk", opener=opener)
    assert tid == "img-task-1"


def test_run_video_poll_download(tmp_path, monkeypatch):
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")
    monkeypatch.setenv("DASHSCOPE_NATIVE_BASE_URL", "https://dashscope-intl.aliyuncs.com/api/v1")
    calls = {"n": 0}
    blob = b"x" * 60_000

    def opener(req, timeout=0):
        url = req.full_url
        calls["n"] += 1
        if "video-synthesis" in url:
            return _FakeResp({"output": {"task_id": "vid-1", "task_status": "PENDING"}})
        if "/tasks/vid-1" in url:
            return _FakeResp(
                {
                    "output": {
                        "task_id": "vid-1",
                        "task_status": "SUCCEEDED",
                        "video_url": "https://example.com/clip.mp4",
                    }
                }
            )
        if "example.com/clip.mp4" in url:
            return _FakeResp(blob)
        raise AssertionError(f"unexpected url {url}")

    result = dfm.run_video(
        prompt="gentle push",
        out_dir=tmp_path,
        model="wan2.7-t2v",
        duration_s=5,
        opener=opener,
        sleeper=lambda _s: None,
    )
    assert result.bytes == 60_000
    assert result.local_path.exists()
    assert result.modality == "video"
    assert result.model == "wan2.7-t2v"


def test_run_image_stub_guard(tmp_path, monkeypatch):
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")
    monkeypatch.setenv("DASHSCOPE_NATIVE_BASE_URL", "https://dashscope-intl.aliyuncs.com/api/v1")

    def opener(req, timeout=0):
        url = req.full_url
        if "image-synthesis" in url:
            return _FakeResp({"output": {"task_id": "img-2"}})
        if "/tasks/img-2" in url:
            return _FakeResp(
                {
                    "output": {
                        "task_status": "SUCCEEDED",
                        "results": [{"url": "https://example.com/tiny.png"}],
                    }
                }
            )
        if "tiny.png" in url:
            return _FakeResp(b"tiny")
        raise AssertionError(url)

    with pytest.raises(dfm.DashScopeFreeMediaError, match="stub-sized"):
        dfm.run_image(
            prompt="x",
            out_dir=tmp_path,
            opener=opener,
            sleeper=lambda _s: None,
        )


def test_cli_dry_run(capsys):
    rc = dfm.main(
        [
            "image",
            "--prompt",
            "test",
            "--out-dir",
            "/tmp/out",
            "--dry-run-submit-body",
        ]
    )
    assert rc == 0
    assert "qwen-image-2.0" in capsys.readouterr().out
