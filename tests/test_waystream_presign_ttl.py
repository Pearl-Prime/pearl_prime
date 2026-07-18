"""Regression: Waystream presign TTLs must stay under R2's 1-week ceiling.

Cloudflare R2 rejects presigned GETs with X-Amz-Expires >= 604800 (1 week) with
HTTP 400 "X-Amz-Expires must be less than a week (in seconds)". Confirmed empirically
2026-07-01 during the flip-assemble R2 pilot (PR #4204): a 30-day presign 400'd, a
6-day presign returned HTTP 200.

The DURABLE public download path is the /download/<book>?week=... Cloudflare Pages
Function, which re-signs the R2 object server-side on every request
(brand-wizard-app/functions/download/[book_id].js). These checks guard the legacy
direct-presign code paths from regressing back to a >= 1-week ExpiresIn.
"""
from __future__ import annotations

import importlib.util
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


def test_upload_default_presign_under_one_week(monkeypatch):
    monkeypatch.delenv("WAYSTREAM_R2_PRESIGN_SEC", raising=False)
    mod = _load("scripts/release/upload_waystream_deliveries_r2.py")
    assert mod.R2_MAX_PRESIGN_SEC == R2_WEEK_SECONDS
    assert mod.DEFAULT_PRESIGN_SEC < R2_WEEK_SECONDS
    assert 0 < mod._resolve_presign_sec() < R2_WEEK_SECONDS


@pytest.mark.parametrize("bad", [R2_WEEK_SECONDS, R2_WEEK_SECONDS + 1, 60 * 60 * 24 * 30])
def test_upload_rejects_one_week_or_more(monkeypatch, bad):
    mod = _load("scripts/release/upload_waystream_deliveries_r2.py")
    monkeypatch.setenv("WAYSTREAM_R2_PRESIGN_SEC", str(bad))
    with pytest.raises(SystemExit):
        mod._resolve_presign_sec()


def test_upload_accepts_valid_override(monkeypatch):
    mod = _load("scripts/release/upload_waystream_deliveries_r2.py")
    monkeypatch.setenv("WAYSTREAM_R2_PRESIGN_SEC", str(R2_WEEK_SECONDS - 1))
    assert mod._resolve_presign_sec() == R2_WEEK_SECONDS - 1


def test_upload_rejects_non_positive(monkeypatch):
    mod = _load("scripts/release/upload_waystream_deliveries_r2.py")
    monkeypatch.setenv("WAYSTREAM_R2_PRESIGN_SEC", "0")
    with pytest.raises(SystemExit):
        mod._resolve_presign_sec()


def test_rebuild_feed_cap_under_one_week():
    mod = _load("scripts/marketing/rebuild_waystream_feed_from_r2.py")
    assert mod.MAX_PRESIGN_TTL < R2_WEEK_SECONDS
    # An over-limit request must be capped strictly under a week (not to exactly a week).
    assert mod._effective_presign_ttl(R2_WEEK_SECONDS) < R2_WEEK_SECONDS
    assert mod._effective_presign_ttl(60 * 60 * 24 * 30) < R2_WEEK_SECONDS
