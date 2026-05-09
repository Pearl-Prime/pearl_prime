#!/usr/bin/env python3
"""
Active brand filter for catalog generators
==========================================

Thin caching wrapper around ``scripts.brand.active_brand_classifier`` for
the catalog generators. Mirrors the consumer pattern shipped via PR #982
(``brand_admin.html``): centralize the active/inactive lookup so each
generator stays minimal-change.

Cap: WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01 (Q4 = brand_wizard YAML SSOT).
Spec: docs/specs/ACTIVE_BRAND_SSOT_V1_SPEC.md.

The classifier returns inactive for any brand_id without a committed
``brand-wizard-app/brands/<brand_id>.yaml`` bundle. Generators should
treat ``is_brand_active`` False as "skip with single-line log marker"
and proceed without the row.
"""
from __future__ import annotations

from scripts.brand.active_brand_classifier import (
    default_classifier,
    reset_default_classifier,
)

# Module-level memo so repeated per-row lookups don't re-walk the YAML directory.
_active_ids: frozenset[str] | None = None


def _ensure_loaded() -> frozenset[str]:
    global _active_ids
    if _active_ids is None:
        _active_ids = frozenset(default_classifier().list_active())
    return _active_ids


def get_active_brand_ids() -> set[str]:
    """Snapshot of brand_ids classified as active by the brand_wizard YAML SSOT."""
    return set(_ensure_loaded())


def is_brand_active(brand_id: str) -> bool:
    """True iff ``brand_id`` has a valid ``brand-wizard-app/brands/<brand_id>.yaml`` bundle."""
    return brand_id in _ensure_loaded()


def reset_cache() -> None:
    """Test hook: invalidate the cached active set (and the classifier default)."""
    global _active_ids
    _active_ids = None
    reset_default_classifier()
