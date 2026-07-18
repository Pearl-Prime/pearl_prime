"""Regression: manga R2 presign TTLs must stay strictly under R2's 1-week ceiling.

Cloudflare R2 rejects presigned GETs with X-Amz-Expires >= 604800 (1 week) with HTTP 400
"X-Amz-Expires must be less than a week (in seconds)" — exactly one week is rejected; it
must be STRICTLY less. Confirmed empirically 2026-07-01 (Waystream flip-assemble R2 pilot,
PR #4204; fixed for Waystream in PR #4213, mirrored for manga here).

The manga weekly/smoke lane emits these presigned URLs straight into digest emails and has
NO durable /download proxy that re-signs per request, so a regression back to a >= 1-week
ExpiresIn would 400 every digest link. These checks guard the manga presign chokepoint and
the three call sites (r2 release default, smoke publish, weekly rollout) + the lane config.
"""
from __future__ import annotations

import importlib.util
import inspect
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
R2_WEEK_SECONDS = 604_800  # hard ceiling — a valid ExpiresIn must be strictly less


def _load(rel: str):
    path = REPO / rel
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def r2mod():
    return _load("scripts/manga/r2_manga_release.py")


def test_constants_under_one_week(r2mod):
    assert r2mod.R2_MAX_PRESIGN_SEC == R2_WEEK_SECONDS
    assert 0 < r2mod.DEFAULT_PRESIGN_SEC < R2_WEEK_SECONDS


def test_default_params_under_one_week(r2mod):
    for fn in (r2mod.presigned_get_url, r2mod.upload_manga_release_dir):
        default = inspect.signature(fn).parameters["expires_in"].default
        assert 0 < default < R2_WEEK_SECONDS, f"{fn.__name__} expires_in default {default} >= 1 week"


@pytest.mark.parametrize("bad", [R2_WEEK_SECONDS, R2_WEEK_SECONDS + 1, 60 * 60 * 24 * 30])
def test_clamp_forces_under_one_week(r2mod, bad):
    assert r2mod.clamp_presign_sec(bad) < R2_WEEK_SECONDS


def test_clamp_passes_valid_through(r2mod):
    assert r2mod.clamp_presign_sec(R2_WEEK_SECONDS - 1) == R2_WEEK_SECONDS - 1
    assert r2mod.clamp_presign_sec(60) == 60


def test_clamp_non_positive_falls_back_safe(r2mod):
    assert 0 < r2mod.clamp_presign_sec(0) < R2_WEEK_SECONDS
    assert 0 < r2mod.clamp_presign_sec(-5) < R2_WEEK_SECONDS


def test_generated_url_expires_in_under_one_week(r2mod):
    """Even if a caller passes exactly a week, the signed ExpiresIn is strictly less."""
    captured: dict[str, int] = {}

    class _FakeClient:
        def generate_presigned_url(self, op, Params, ExpiresIn):  # noqa: N803
            captured["ExpiresIn"] = ExpiresIn
            return f"https://example/{Params['Key']}?X-Amz-Expires={ExpiresIn}"

    r2mod.presigned_get_url(_FakeClient(), bucket="b", key="k", expires_in=R2_WEEK_SECONDS)
    assert captured["ExpiresIn"] < R2_WEEK_SECONDS


def test_weekly_rollout_fallback_not_one_week():
    src = (REPO / "scripts/weekly_manga_rollout.py").read_text(encoding="utf-8")
    assert "or 604800" not in src, "weekly rollout still falls back to a 1-week (604800) presign TTL"


def test_smoke_post_publish_not_hardcoded_one_week():
    src = (REPO / "scripts/manga/smoke_post_publish.py").read_text(encoding="utf-8")
    assert "expires_in=604800" not in src, "smoke_post_publish still passes a 1-week (604800) presign TTL"


def test_rollout_config_expiry_under_one_week():
    cfg = (REPO / "config/weekly_rollout/manga_rollout.yaml").read_text(encoding="utf-8")
    m = re.search(r"signed_url_expiry_seconds:\s*(\d+)", cfg)
    assert m, "signed_url_expiry_seconds missing from manga_rollout.yaml"
    assert int(m.group(1)) < R2_WEEK_SECONDS
