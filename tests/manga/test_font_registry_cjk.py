"""Tests for fonts/manga/FONT_REGISTRY.yaml v2 (CJK rebuild).

PR #631 Decision 3: every locale Phoenix Omega ships must have a body
font registered. These tests lock that in.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.manga.check_font_registry import (  # type: ignore
    REGISTRY,
    VALID_LOCALES,
    VALID_STATUSES,
    _load,
    validate_registry,
)


@pytest.fixture(scope="module")
def registry():
    return _load()


# ─── schema sanity ──────────────────────────────────────────────────────────


def test_registry_loads(registry):
    assert "fonts" in registry
    assert isinstance(registry["fonts"], list)
    assert len(registry["fonts"]) >= 8, "expected ≥8 fonts after PR #631 CJK rebuild"


def test_registry_validates(registry):
    errors = validate_registry(registry, strict=False)
    assert not errors, f"registry has validation errors: {errors}"


def test_no_duplicate_ids(registry):
    ids = [f["id"] for f in registry["fonts"]]
    assert len(ids) == len(set(ids)), f"duplicate font ids: {ids}"


def test_no_duplicate_paths(registry):
    paths = [f["path"] for f in registry["fonts"]]
    assert len(paths) == len(set(paths)), f"duplicate font paths: {paths}"


# ─── CJK coverage (the whole point of v2) ──────────────────────────────────


def test_japanese_body_font_registered(registry):
    ids = {f["id"] for f in registry["fonts"]}
    assert "source_han_sans_jp" in ids, "ja_JP body font missing"


def test_traditional_chinese_body_font_registered(registry):
    ids = {f["id"] for f in registry["fonts"]}
    assert "source_han_sans_tc" in ids, "zh_TW body font missing"


def test_simplified_chinese_body_font_registered(registry):
    ids = {f["id"] for f in registry["fonts"]}
    assert "source_han_sans_sc" in ids, "zh_CN body font missing"


def test_korean_body_font_registered(registry):
    """Even though ko_KR is Phase 2, register the font now — Naver connector
    follow-up is in PR #631's roadmap."""
    ids = {f["id"] for f in registry["fonts"]}
    assert "source_han_sans_kr" in ids, "ko_KR body font missing"


def test_japanese_handwritten_font_registered(registry):
    ids = {f["id"] for f in registry["fonts"]}
    assert "klee_one_jp" in ids, "Klee One JP missing — needed for iyashikei"


def test_chinese_handwritten_font_registered(registry):
    ids = {f["id"] for f in registry["fonts"]}
    assert "lxgw_wenkai" in ids, "LXGW WenKai missing — needed for zh handwritten"


# ─── Latin coverage ────────────────────────────────────────────────────────


def test_anime_ace_dialogue_registered(registry):
    ids = {f["id"] for f in registry["fonts"]}
    assert "anime_ace_dialogue" in ids


def test_badaboom_sfx_registered(registry):
    ids = {f["id"] for f in registry["fonts"]}
    assert "badaboom_sfx" in ids


# ─── locale_coverage_required cross-reference ──────────────────────────────


def test_every_catalog_locale_has_body_font(registry):
    coverage = registry["locale_coverage_required"]
    for locale in ("en_US", "ja_JP", "zh_TW", "zh_CN"):
        assert locale in coverage, f"locale_coverage_required missing {locale}"
        assert "body" in coverage[locale], f"{locale} has no body font"


def test_coverage_references_resolve(registry):
    """Every font_id in locale_coverage_required must exist in fonts[]."""
    ids = {f["id"] for f in registry["fonts"]}
    coverage = registry["locale_coverage_required"]
    for locale, roles in coverage.items():
        for role, font_id in roles.items():
            assert font_id in ids, f"{locale}.{role} → unknown font {font_id}"


# ─── status / license sanity ───────────────────────────────────────────────


def test_no_blocked_fonts(registry):
    """If any font ends up with status=blocked, fail loudly — don't ship it."""
    blocked = [f["id"] for f in registry["fonts"] if f.get("status") == "blocked"]
    assert not blocked, f"blocked fonts still in registry: {blocked}"


def test_every_font_has_license(registry):
    for f in registry["fonts"]:
        assert f.get("license"), f"font {f['id']} has no license"


def test_every_font_has_source_url(registry):
    """Every font needs a canonical source URL for compliance + auto-install."""
    # Some legacy entries may lack source_url; warn-but-allow for now
    missing = [f["id"] for f in registry["fonts"] if not f.get("source_url")]
    assert not missing, f"fonts missing source_url: {missing}"
