"""Regression: artifacts R2 sign-url TTLs must stay strictly under R2's 1-week ceiling.

Cloudflare R2 rejects presigned GETs with X-Amz-Expires >= 604800 (1 week) with HTTP 400
"X-Amz-Expires must be less than a week (in seconds)" — exactly one week is rejected; it
must be STRICTLY less. Confirmed empirically 2026-07-01 (Waystream flip-assemble R2 pilot,
PR #4204; fixed for Waystream in PR #4213, for manga in PR #4226, mirrored here for the
shared ``scripts/artifacts/r2_push_helper.py`` sign-url helper).

The helper's default ttl (1h) is already safe, but its CLI exposes ``--ttl`` so a caller can
pass ``--ttl 604800`` or more. These checks guard the ``clamp_presign_sec`` chokepoint that
``sign_url`` flows through so a regression back to an unclamped ExpiresIn can't ship.
"""
from __future__ import annotations

import importlib.util
import inspect
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
    return _load("scripts/artifacts/r2_push_helper.py")


def test_constants_under_one_week(r2mod):
    assert r2mod.R2_MAX_PRESIGN_SEC == R2_WEEK_SECONDS
    assert 0 < r2mod.DEFAULT_TTL_SECONDS < R2_WEEK_SECONDS


def test_default_param_under_one_week(r2mod):
    default = inspect.signature(r2mod.sign_url).parameters["ttl_seconds"].default
    assert 0 < default < R2_WEEK_SECONDS, f"sign_url ttl_seconds default {default} >= 1 week"


@pytest.mark.parametrize("bad", [R2_WEEK_SECONDS, R2_WEEK_SECONDS + 1, 60 * 60 * 24 * 30])
def test_clamp_forces_under_one_week(r2mod, bad):
    assert r2mod.clamp_presign_sec(bad) < R2_WEEK_SECONDS


def test_clamp_passes_valid_through(r2mod):
    assert r2mod.clamp_presign_sec(R2_WEEK_SECONDS - 1) == R2_WEEK_SECONDS - 1
    assert r2mod.clamp_presign_sec(60) == 60


def test_clamp_non_positive_falls_back_safe(r2mod):
    assert 0 < r2mod.clamp_presign_sec(0) < R2_WEEK_SECONDS
    assert 0 < r2mod.clamp_presign_sec(-5) < R2_WEEK_SECONDS


def test_generated_url_expires_in_under_one_week(r2mod, monkeypatch):
    """Even if a caller passes exactly a week (via --ttl), the signed ExpiresIn is strictly less."""
    captured: dict[str, int] = {}

    class _FakeClient:
        def generate_presigned_url(self, op, Params, ExpiresIn):  # noqa: N803
            captured["ExpiresIn"] = ExpiresIn
            return f"https://example/{Params['Key']}?X-Amz-Expires={ExpiresIn}"

    monkeypatch.setattr(r2mod, "_bucket_name", lambda: "b")
    monkeypatch.setattr(r2mod, "_r2_client", lambda: _FakeClient())

    r2mod.sign_url(key="k", ttl_seconds=R2_WEEK_SECONDS)
    assert captured["ExpiresIn"] < R2_WEEK_SECONDS
